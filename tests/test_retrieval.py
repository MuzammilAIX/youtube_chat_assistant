from langchain_core.documents import Document
from youtube_rag.retrieval import format_documents

def test_format_documents_includes_source_and_timestamp():
    docs = [Document(page_content="AI is discussed here.", metadata={
        "video_id": "LPZh9BOjkQs", "start_seconds": 125,
        "source": "https://www.youtube.com/watch?v=LPZh9BOjkQs&t=125s",
    })]
    output = format_documents(docs)
    assert "AI is discussed here." in output
    assert "timestamp=125s" in output
    assert "[Source 1" in output
