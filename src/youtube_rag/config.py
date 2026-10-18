"""Application configuration loaded from environment variables."""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
DATA_DIR = Path(os.getenv("DATA_DIR", str(PROJECT_ROOT / "data")))
INDEX_DIR = DATA_DIR / "faiss_index"
MANIFEST_PATH = DATA_DIR / "manifest.json"
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "4"))

def validate_config() -> None:
    """Fail early with a helpful message if required settings are missing."""
    if not OPENAI_API_KEY or OPENAI_API_KEY == "put_your_openai_api_key_here":
        raise ValueError("OPENAI_API_KEY is missing. Copy .env.example to .env and add your API key.")
    if CHUNK_SIZE <= 0:
        raise ValueError("CHUNK_SIZE must be greater than zero.")
    if CHUNK_OVERLAP < 0 or CHUNK_OVERLAP >= CHUNK_SIZE:
        raise ValueError("CHUNK_OVERLAP must be >= 0 and smaller than CHUNK_SIZE.")
    if RETRIEVAL_K <= 0:
        raise ValueError("RETRIEVAL_K must be greater than zero.")
