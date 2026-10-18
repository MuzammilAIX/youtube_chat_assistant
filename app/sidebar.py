"""Professional sidebar for TubeMind AI."""

import streamlit as st


# =============================================================================
# RED YOUTUBE LOGO (pure CSS, no SVG, no network dependency)
# =============================================================================
_YOUTUBE_LOGO_HTML = (
    '<span style="display:inline-block;width:{w}px;height:{h}px;'
    'background:#FF0000;border-radius:{r}px;position:relative;'
    'flex-shrink:0;vertical-align:middle;">'
    '<span style="position:absolute;top:50%;left:50%;'
    'transform:translate(-40%,-50%);width:0;height:0;'
    'border-left:{pw}px solid white;'
    'border-top:{ph}px solid transparent;'
    'border-bottom:{ph}px solid transparent;"></span>'
    '</span>'
)


def youtube_logo(width: int = 28, height: int = 20) -> str:
    """Return HTML for a red YouTube-style logo at the given size."""
    radius = max(3, round(height * 0.22))
    play_w = max(6, round(width * 0.28))
    play_h = max(4, round(height * 0.27))
    return _YOUTUBE_LOGO_HTML.format(
        w=width, h=height, r=radius, pw=play_w, ph=play_h,
    )


def _brand():
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;padding:6px 0 14px 0;">
            {youtube_logo(28, 20)}
            <span style="font-size:1.15rem;font-weight:700;
                         background:linear-gradient(90deg,#a5b4fc,#6366f1);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                TubeMind AI
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _section(label: str):
    st.markdown(
        f'<div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;'
        f'color:#8a8f98;font-weight:600;margin:14px 0 6px 0;">{label}</div>',
        unsafe_allow_html=True,
    )


def render_sidebar(
    *,
    state: dict,
    on_new_chat,
    on_select_conversation,
    on_select_video,
    on_clear_all,
) -> dict:
    """
    Render the sidebar and return any changed settings:
      {"model": str, "retrieval_k": int}
    """
    settings = {
        "model": state.get("model", "gpt-4o-mini"),
        "retrieval_k": state.get("retrieval_k", 4),
    }

    with st.sidebar:
        _brand()

        # ---- New Chat button ----
        if st.button("＋  New chat", type="primary", use_container_width=True):
            on_new_chat()

        # ---- Chat history ----
        _section("Recent chats")
        conversations = state.get("conversations", []) or []
        if not conversations:
            st.caption("No conversations yet.")
        else:
            for convo in conversations[:10]:
                vid = convo.get("video_id", "")
                title = convo.get("title") or vid or "Untitled"
                active = "• " if vid == state.get("video_id") else "  "
                if st.button(
                    f"{active}{title[:36]}{'…' if len(title) > 36 else ''}",
                    key=f"convo_{vid}",
                    use_container_width=True,
                ):
                    on_select_conversation(vid)

        # ---- Saved videos ----
        _section("Saved videos")
        saved = state.get("saved_videos", []) or []
        if not saved:
            st.caption("Videos you index appear here.")
        else:
            for vid_meta in saved[:10]:
                vid = vid_meta.get("video_id", "")
                title = vid_meta.get("title") or vid or "Untitled"
                if st.button(
                    f"▶ {title[:34]}{'…' if len(title) > 34 else ''}",
                    key=f"saved_{vid}",
                    use_container_width=True,
                ):
                    on_select_video(vid)

        # ---- Settings ----
        _section("Settings")
        model_options = ["gpt-4o-mini", "gpt-4o", "gpt-4.1"]
        current_model = settings["model"] if settings["model"] in model_options else "gpt-4o-mini"
        model = st.selectbox(
            "Model",
            options=model_options,
            index=model_options.index(current_model),
            key="sidebar_model",
        )
        retrieval_k = st.slider(
            "Chunks per retrieval",
            min_value=1, max_value=10,
            value=settings["retrieval_k"],
            key="sidebar_retrieval_k",
        )
        settings["model"] = model
        settings["retrieval_k"] = retrieval_k

        # ---- Danger zone ----
        if st.button("🗑️ Clear all conversations", use_container_width=True):
            on_clear_all()

        # ---- API status ----
        _section("API status")
        try:
            from youtube_rag import config as _cfg
            has_key = bool(getattr(_cfg, "OPENAI_API_KEY", None))
        except Exception:
            has_key = False

        dot = "🟢" if has_key else "🔴"
        label = "OpenAI connected" if has_key else "OpenAI key missing"
        st.markdown(
            f'<div style="font-size:0.82rem;color:#8a8f98;">{dot} {label}</div>',
            unsafe_allow_html=True,
        )

        st.caption("v1.0 · TubeMind AI")

    return settings