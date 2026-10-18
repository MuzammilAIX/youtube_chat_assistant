"""Create and persist the FAISS vector index."""
import json
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from . import config

def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=config.EMBEDDING_MODEL)

def build_index(documents, index_dir: Path | None = None) -> FAISS:
    """Create an index and save it to disk."""
    if not documents:
        raise ValueError("Cannot build an index without documents.")
    target = index_dir or config.INDEX_DIR
    target.mkdir(parents=True, exist_ok=True)
    vector_store = FAISS.from_documents(documents, get_embeddings())
    vector_store.save_local(str(target))
    return vector_store

def load_index(index_dir: Path | None = None) -> FAISS:
    """Load a previously saved local FAISS index."""
    target = index_dir or config.INDEX_DIR
    if not (target / "index.faiss").exists() or not (target / "index.pkl").exists():
        raise FileNotFoundError("No saved index found. Enter a YouTube URL and index it first.")
    # Only load an index.pkl that your own application created and that you trust.
    return FAISS.load_local(
        str(target), get_embeddings(), allow_dangerous_deserialization=True
    )

def save_manifest(video_id: str, document_count: int, manifest_path: Path | None = None) -> None:
    path = manifest_path or config.MANIFEST_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "video_id": video_id,
        "document_count": document_count,
        "embedding_model": config.EMBEDDING_MODEL,
        "chunk_size": config.CHUNK_SIZE,
        "chunk_overlap": config.CHUNK_OVERLAP,
    }
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

def read_manifest(manifest_path: Path | None = None) -> dict:
    path = manifest_path or config.MANIFEST_PATH
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
