"""Retrieve transcript chunks relevant to a question."""
from langchain_community.vectorstores import FAISS
from .config import RETRIEVAL_K

def retrieve_documents(vector_store: FAISS, question: str, k: int = RETRIEVAL_K):
    """Return the k most similar chunks."""
    question = question.strip()
    if not question:
        raise ValueError("Question cannot be empty.")
    return vector_store.similarity_search(question, k=k)

def format_documents(documents) -> str:
    """Format chunks with source labels for the answer prompt."""
    sections = []
    for i, doc in enumerate(documents, start=1):
        video_id = doc.metadata.get("video_id", "unknown")
        seconds = int(doc.metadata.get("start_seconds", 0))
        url = doc.metadata.get("source", f"https://www.youtube.com/watch?v={video_id}&t={seconds}s")
        sections.append(
            f"[Source {i} | video_id={video_id} | timestamp={seconds}s | url={url}]\n"
            f"{doc.page_content}"
        )
    return "\n\n".join(sections)
