"""High-level functions used by the UI and tests."""

from typing import Iterator

from .config import validate_config, RETRIEVAL_K
from .ingestion import fetch_transcript
from .processing import snippets_to_documents
from .indexing import build_index, load_index, save_manifest
from .retrieval import retrieve_documents
from .generation import answer_question, stream_answer
from .insights import generate_insights


SUMMARY_KEYWORDS = (
    "summary", "summarize", "summarise", "overview",
    "what is this video about", "what's this video about",
    "main points", "key points", "key topics", "important topics",
    "what is discussed", "what's discussed", "tldr", "tl;dr",
    "what does this video cover", "what is covered",
)


def is_summary_question(question: str) -> bool:
    ql = (question or "").lower()
    return any(kw in ql for kw in SUMMARY_KEYWORDS)


def get_all_chunks_for_video(vector_store, video_id: str, max_chunks: int = 1000):
    if not video_id:
        return []
    try:
        docs = vector_store.similarity_search(
            query="transcript", k=max_chunks, filter={"video_id": video_id},
        )
    except Exception:
        try:
            docs = vector_store.similarity_search("transcript", k=max_chunks)
            docs = [d for d in docs if str(d.metadata.get("video_id", "")) == str(video_id)]
        except Exception:
            return []

    def _start(doc):
        meta = getattr(doc, "metadata", {}) or {}
        v = meta.get("start_seconds", meta.get("start", meta.get("timestamp", 0)))
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    return sorted(docs, key=_start)


def _sources_from_docs(docs):
    sources = []
    for doc in docs:
        meta = getattr(doc, "metadata", {}) or {}
        start = meta.get("start_seconds", meta.get("start", meta.get("timestamp", 0)))
        try:
            start_int = int(float(start))
        except (TypeError, ValueError):
            start_int = 0
        sources.append({
            "text": getattr(doc, "page_content", ""),
            "video_id": meta.get("video_id", ""),
            "start_seconds": start_int,
            "url": meta.get("source", ""),
        })
    return sources


def _select_documents(vector_store, question, k, documents, video_id):
    if documents is not None:
        return list(documents)
    if video_id and is_summary_question(question):
        docs = get_all_chunks_for_video(vector_store, video_id, max_chunks=1000)
        if not docs:
            docs = retrieve_documents(vector_store, question, k=k)
        return docs
    if is_summary_question(question):
        return retrieve_documents(vector_store, question, k=max(k, 8))
    return retrieve_documents(vector_store, question, k=k)


# -----------------------------------------------------------------------------
# Indexing
# -----------------------------------------------------------------------------
def index_video(url_or_id: str):
    validate_config()
    transcript_data = fetch_transcript(url_or_id)
    docs = snippets_to_documents(transcript_data["snippets"], transcript_data["video_id"])
    vector_store = build_index(docs)
    save_manifest(transcript_data["video_id"], len(docs))
    return {
        "video_id": transcript_data["video_id"],
        "chunk_count": len(docs),
        "vector_store": vector_store,
        "title": transcript_data.get("title", ""),
        "duration_seconds": transcript_data.get("duration_seconds", 0),
        "thumbnail_url": f"https://i.ytimg.com/vi/{transcript_data['video_id']}/hqdefault.jpg",
        "transcript_language": transcript_data.get("language", ""),
    }


def load_video_index():
    validate_config()
    return load_index()


# -----------------------------------------------------------------------------
# Non-streaming Q&A
# -----------------------------------------------------------------------------
def ask_question(vector_store, question: str, k: int = RETRIEVAL_K,
                 documents=None, video_id: str = None):
    docs = _select_documents(vector_store, question, k, documents, video_id)
    if not docs:
        return {
            "answer": "I couldn't find relevant transcript evidence to answer that question.",
            "sources": [],
        }
    answer = answer_question(question, docs)
    return {"answer": answer, "sources": _sources_from_docs(docs)}


# -----------------------------------------------------------------------------
# Streaming Q&A
# -----------------------------------------------------------------------------
def stream_ask_question(vector_store, question: str, k: int = RETRIEVAL_K,
                        documents=None, video_id: str = None) -> Iterator[dict]:
    docs = _select_documents(vector_store, question, k, documents, video_id)
    if not docs:
        yield {"type": "token",
               "text": "I couldn't find relevant transcript evidence to answer that question."}
        yield {"type": "sources", "sources": []}
        return

    for token in stream_answer(question, docs):
        yield {"type": "token", "text": token}

    yield {"type": "sources", "sources": _sources_from_docs(docs)}


# -----------------------------------------------------------------------------
# Insights — new
# -----------------------------------------------------------------------------
def generate_insights_for_video(vector_store, video_id: str) -> dict:
    """Run the insight generator over the entire transcript for this video."""
    docs = get_all_chunks_for_video(vector_store, video_id, max_chunks=1000)
    return generate_insights(docs)