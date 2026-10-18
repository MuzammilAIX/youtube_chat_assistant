"""Clean transcript snippets and create timestamp-aware LangChain documents."""
import re
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import CHUNK_OVERLAP, CHUNK_SIZE

def clean_text(text: str) -> str:
    """Normalize whitespace without changing the words."""
    return re.sub(r"\s+", " ", text).strip()

def snippets_to_documents(snippets: list[dict], video_id: str,
                          chunk_size: int = CHUNK_SIZE,
                          chunk_overlap: int = CHUNK_OVERLAP) -> list[Document]:
    """Create chunks while retaining the approximate source timestamp."""
    if not snippets:
        raise ValueError("Transcript contains no snippets.")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True
    )
    running_text = ""
    segment_starts: list[tuple[int, float]] = []
    for snippet in snippets:
        text = clean_text(str(snippet.get("text", "")))
        if not text:
            continue
        if running_text:
            running_text += " "
        segment_starts.append((len(running_text), float(snippet.get("start", 0.0))))
        running_text += text
    if not running_text:
        raise ValueError("Transcript contains no readable text.")

    documents = []
    for doc in splitter.create_documents([running_text]):
        start_index = int(doc.metadata.get("start_index", 0))
        source_time = 0.0
        for char_pos, timestamp in segment_starts:
            if char_pos <= start_index:
                source_time = timestamp
            else:
                break
        doc.metadata.update({
            "video_id": video_id,
            "start_seconds": source_time,
            "source": f"https://www.youtube.com/watch?v={video_id}&t={int(source_time)}s",
        })
        documents.append(doc)
    return documents
