import pytest
from youtube_rag.ingestion import extract_video_id

def test_extract_video_id_from_id():
    assert extract_video_id("LPZh9BOjkQs") == "LPZh9BOjkQs"

def test_extract_video_id_from_watch_url():
    assert extract_video_id("https://www.youtube.com/watch?v=LPZh9BOjkQs") == "LPZh9BOjkQs"

def test_extract_video_id_from_short_url():
    assert extract_video_id("https://youtu.be/LPZh9BOjkQs") == "LPZh9BOjkQs"

def test_invalid_video_id_raises():
    with pytest.raises(ValueError):
        extract_video_id("not a video")
