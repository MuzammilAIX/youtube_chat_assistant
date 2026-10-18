"""Video workspace: preview, metadata, and Analyze action."""

import streamlit as st
import streamlit.components.v1 as components


def _fmt_duration(seconds: int) -> str:
    try:
        seconds = int(seconds or 0)
    except (TypeError, ValueError):
        seconds = 0
    if seconds <= 0:
        return "—"
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _crisp_video(video_id: str, height_px: int = 520):
    """Embed YouTube at 16:9 with forced HD quality."""
    if not video_id:
        return
    embed = (
        f'<div style="width:100%;max-width:1100px;margin:0 auto;">'
        f'<div style="position:relative;width:100%;padding-bottom:56.25%;height:0;'
        f'border-radius:12px;overflow:hidden;border:1px solid rgba(128,128,128,0.2);background:#000;">'
        f'<iframe src="https://www.youtube.com/embed/{video_id}?rel=0&vq=hd1080&modestbranding=1" '
        f'style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" '
        f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen" '
        f'allowfullscreen></iframe>'
        f'</div></div>'
    )
    components.html(embed, height=height_px, scrolling=False)


def render_video_workspace(
    *,
    video_id: str,
    title: str,
    chunk_count: int,
    duration_seconds: int,
    transcript_language: str,
    on_analyze,
):
    """Render the video workspace (preview + metadata + actions)."""
    if not video_id:
        st.markdown(
            """
            <div style="padding:34px 20px;border:1px dashed rgba(128,128,128,0.35);
                        border-radius:14px;text-align:center;color:#8a8f98;">
                <div style="font-size:2rem;margin-bottom:6px;">🎬</div>
                <div style="font-size:0.95rem;">No video loaded</div>
                <div style="font-size:0.82rem;margin-top:4px;">
                    Paste a YouTube URL below and click <b>Analyze video</b>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        url = st.text_input(
            "YouTube URL",
            placeholder="Paste a YouTube link…",
            label_visibility="collapsed",
            key="workspace_url",
        )
        if st.button("Analyze video →", type="primary", use_container_width=True):
            on_analyze(url)
        return

    # ---- Video preview ----
    _crisp_video(video_id, height_px=520)

    # ---- Metadata card ----
    st.markdown("")
    pills = [
        f'<span class="pill">📼 {chunk_count} chunks</span>',
        f'<span class="pill">⏱ {_fmt_duration(duration_seconds)}</span>',
    ]
    if transcript_language:
        pills.append(f'<span class="pill">🌐 {transcript_language}</span>')
    pills.append('<span class="pill">✅ transcript ready</span>')

    st.markdown(
        f'<div style="margin-bottom:6px;"><b>{title or video_id}</b></div>'
        + f'<div>{"".join(pills)}</div>',
        unsafe_allow_html=True,
    )

    # ---- Re-analyze ----
    if st.button("🔄 Re-analyze video", use_container_width=False):
        on_analyze(video_id)