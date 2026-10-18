
"""Fetch a YouTube transcript and preserve snippet timestamps."""

import re
from typing import Any
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)


YOUTUBE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


class TranscriptIngestionError(RuntimeError):
    """Raised when a usable transcript cannot be retrieved."""


def extract_video_id(url_or_id: str) -> str:
    """Extract an 11-character YouTube video ID from a URL or raw ID."""

    if not isinstance(url_or_id, str) or not url_or_id.strip():
        raise ValueError(
            "Please enter a YouTube URL or 11-character video ID."
        )

    value = url_or_id.strip()

    # Case 1: User entered only the video ID.
    if YOUTUBE_ID_PATTERN.fullmatch(value):
        return value

    # Case 2: Parse a YouTube URL.
    if not value.startswith(("https://", "http://")):
        value = "https://" + value

    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    video_id = None

    if host in {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
    }:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]

        elif parsed.path.startswith(("/embed/", "/shorts/", "/live/")):
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2:
                video_id = parts[1]

    elif host in {"youtu.be", "www.youtu.be"}:
        parts = parsed.path.strip("/").split("/")
        if parts:
            video_id = parts[0]

    if video_id and YOUTUBE_ID_PATTERN.fullmatch(video_id):
        return video_id

    raise ValueError(
        "Enter a valid YouTube URL or 11-character video ID."
    )


def fetch_transcript(
    url_or_id: str,
    languages: list[str] | None = None,
) -> dict[str, Any]:
    """
    Fetch transcript snippets.

    Returns:
        {
            "video_id": str,
            "snippets": [
                {
                    "text": str,
                    "start": float,
                    "duration": float
                }
            ]
        }
    """

    video_id = extract_video_id(url_or_id)
    languages = languages or ["en"]
    try:
        # Compatible with current youtube-transcript-api versions.
        transcript = YouTubeTranscriptApi().fetch(
            video_id,
            languages=languages,
        )

        snippets = []

        for item in transcript:
            text = getattr(item, "text", "").strip()

            if not text:
                continue

            snippets.append(
                {
                    "text": text,
                    "start": float(getattr(item, "start", 0.0)),
                    "duration": float(
                        getattr(item, "duration", 0.0)
                    ),
                }
            )

        if not snippets:
            raise TranscriptIngestionError(
                "The transcript was empty."
            )

        return {
            "video_id": video_id,
            "snippets": snippets,
        }

    except (TranscriptsDisabled, NoTranscriptFound) as exc:
        raise TranscriptIngestionError(
            "No transcript was found in the requested language. "
            "Try another video or language."
        ) from exc

    except VideoUnavailable as exc:
        raise TranscriptIngestionError(
            "This YouTube video is unavailable."
        ) from exc

    except TranscriptIngestionError:
        raise

    except Exception as exc:
        raise TranscriptIngestionError(
            "Could not fetch the transcript. Check your internet "
            "connection, YouTube access, and installed API version. "
            f"Details: {exc}"
        ) from exc
