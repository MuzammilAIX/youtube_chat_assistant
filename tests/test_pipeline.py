import pytest
from youtube_rag.processing import snippets_to_documents

def test_snippets_become_timestamped_documents():
    docs = snippets_to_documents([
        {"text": "First part of a transcript.", "start": 0, "duration": 3},
        {"text": "Second part of a transcript.", "start": 10, "duration": 3},
    ], video_id="LPZh9BOjkQs", chunk_size=25, chunk_overlap=0)
    assert docs
    assert all(doc.metadata["video_id"] == "LPZh9BOjkQs" for doc in docs)
    assert all("start_seconds" in doc.metadata for doc in docs)

def test_empty_transcript_raises():
    with pytest.raises(ValueError):
        snippets_to_documents([], video_id="LPZh9BOjkQs")
