"""Generate structured insights from a full transcript."""

import json
from typing import Optional

from langchain_openai import ChatOpenAI

from . import config
from .retrieval import format_documents


INSIGHT_PROMPT = """You are an analyst who reads full YouTube video transcripts and produces structured insights.
Return ONLY valid JSON, no prose, no markdown fences.

The JSON must match this exact schema:
{
  "executive_summary": "2-3 sentence overview of what the video is about",
  "key_takeaways": ["5 to 7 short bullet points, each 1 sentence"],
  "important_topics": ["4 to 8 short topic labels, each 1-3 words"],
  "action_items": ["3 to 5 concrete actions a viewer could take after watching"],
  "technical_terms": [
    {"term": "term name", "explanation": "1 sentence plain-English explanation"}
  ]
}

Rules:
- Always write in English, even if the transcript is in Hindi/Hinglish.
- If a section has no good evidence, return an empty list [] for it (do not invent).
- Keep each item concise.
- technical_terms: 3 to 6 items max, only terms a general viewer would need explained.
"""


def _safe_json_load(text: str) -> dict:
    """Parse the model output into a dict, tolerating ```json fences."""
    text = (text or "").strip()
    if text.startswith("```"):
        # strip first fence line and trailing fence
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except Exception:
        # last resort: find first { and last }
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except Exception:
                return {}
        return {}


def generate_insights(documents) -> dict:
    """
    Return dict with keys:
      executive_summary, key_takeaways, important_topics,
      action_items, technical_terms
    Never raises — returns safe empty defaults on failure.
    """
    empty = {
        "executive_summary": "",
        "key_takeaways": [],
        "important_topics": [],
        "action_items": [],
        "technical_terms": [],
    }
    if not documents:
        return empty

    context = format_documents(documents)
    if not context.strip():
        return empty

    llm = ChatOpenAI(
        model=config.CHAT_MODEL,
        temperature=0.2,
        model_kwargs={"response_format": {"type": "json_object"}},
    )

    user_msg = (
        "Here is the full transcript context (multiple [Source N] blocks).\n\n"
        f"<context>\n{context}\n</context>\n\n"
        "Produce the JSON described in the system prompt."
    )

    try:
        resp = llm.invoke([
            ("system", INSIGHT_PROMPT),
            ("human", user_msg),
        ])
        raw = resp.content if isinstance(resp.content, str) else str(resp.content)
        data = _safe_json_load(raw)

        # Normalize / defend against odd shapes
        def _list(v):
            return v if isinstance(v, list) else []

        terms = _list(data.get("technical_terms"))
        cleaned_terms = []
        for t in terms:
            if isinstance(t, dict) and t.get("term") and t.get("explanation"):
                cleaned_terms.append({
                    "term": str(t["term"]).strip(),
                    "explanation": str(t["explanation"]).strip(),
                })

        return {
            "executive_summary": str(data.get("executive_summary", "") or "").strip(),
            "key_takeaways": [str(x).strip() for x in _list(data.get("key_takeaways")) if str(x).strip()],
            "important_topics": [str(x).strip() for x in _list(data.get("important_topics")) if str(x).strip()],
            "action_items": [str(x).strip() for x in _list(data.get("action_items")) if str(x).strip()],
            "technical_terms": cleaned_terms,
        }
    except Exception:
        return empty