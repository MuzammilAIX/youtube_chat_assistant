"""Reusable Streamlit components."""

import streamlit as st


def _fmt_time(seconds: int) -> str:
    seconds = int(seconds or 0)
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"


def render_sources(sources):
    """Render a list of source dicts with clickable YouTube timestamps."""
    if not sources:
        return

    with st.expander(f"📚 View transcript sources ({len(sources)})", expanded=False):
        for i, src in enumerate(sources, start=1):
            video_id = str(src.get("video_id", "") or "")
            start = int(src.get("start_seconds", 0) or 0)
            text = (src.get("text", "") or "").strip()

            header_cols = st.columns([1, 3])
            with header_cols[0]:
                if video_id:
                    url = f"https://youtu.be/{video_id}?t={start}"
                    st.markdown(f"**[Source {i}]** [▶ {_fmt_time(start)}]({url})")
                else:
                    st.markdown(f"**[Source {i}]** · {_fmt_time(start)}")

            with header_cols[1]:
                preview = text[:400] + ("…" if len(text) > 400 else "")
                st.markdown(preview)

            if i < len(sources):
                st.divider()