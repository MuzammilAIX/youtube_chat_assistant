"""TubeMind AI — Streamlit interface for the YouTube RAG Assistant."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import streamlit as st
import streamlit.components.v1 as components

from youtube_rag.rag_pipeline import (
    index_video,
    load_video_index,
    ask_question,
    stream_ask_question,
    get_all_chunks_for_video,
    generate_insights_for_video,
)
from youtube_rag.generation import is_summary_question

# App-level helpers live next to this file (app/)
from components import render_sources
from sidebar import render_sidebar
from video_workspace import render_video_workspace
from insights_panel import render_insights_panel


# =============================================================================
# PAGE CONFIG — must be first Streamlit call
# =============================================================================
st.set_page_config(
    page_title="TubeMind AI",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# RED YOUTUBE LOGO (pure CSS)
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


def youtube_logo(width: int = 32, height: int = 22) -> str:
    radius = max(3, round(height * 0.22))
    play_w = max(6, round(width * 0.28))
    play_h = max(4, round(height * 0.27))
    return _YOUTUBE_LOGO_HTML.format(
        w=width, h=height, r=radius, pw=play_w, ph=play_h,
    )


# =============================================================================
# CSS
# =============================================================================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1280px;
    }
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    /* Hero */
    .hero-wrap { padding: 30px 0 10px 0; text-align: center; }
    .hero-brand { display: inline-flex; align-items: center; gap: 10px; margin-bottom: 8px; }
    .hero-brand .mark { font-size: 1.7rem; line-height: 1; }
    .hero-brand .name {
        font-size: 1.35rem; font-weight: 700; letter-spacing: -0.01em;
        background: linear-gradient(90deg, #a5b4fc, #6366f1);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero-brand .badge {
        font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.12em;
        color: #8a8f98; border: 1px solid rgba(128,128,128,0.3);
        padding: 2px 8px; border-radius: 999px; margin-left: 6px;
    }
    .hero-title {
        font-size: 2.6rem; font-weight: 800; line-height: 1.15;
        margin: 12px 0 10px 0; letter-spacing: -0.02em;
    }
    .hero-title .accent {
        background: linear-gradient(90deg, #a5b4fc, #818cf8);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero-sub {
        font-size: 1.05rem; color: #9aa0a6; max-width: 640px;
        margin: 0 auto 26px auto; line-height: 1.55;
    }

    /* Input */
    .input-label {
        font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.12em;
        color: #8a8f98; font-weight: 600; margin-bottom: 8px; display: block;
    }
    div[data-testid="stTextInput"] > div > div > input {
        height: 54px !important; font-size: 1rem !important;
        border-radius: 12px !important;
        border: 1px solid rgba(128, 128, 128, 0.3) !important;
        padding: 0 16px !important;
        background: rgba(128, 128, 128, 0.06) !important;
    }
    div[data-testid="stTextInput"] > div > div > input:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }
    div.stButton > button[kind="primary"] {
        height: 54px; border-radius: 12px; font-size: 0.98rem; font-weight: 600;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        border: none; color: white; transition: all 0.15s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.35);
    }

    /* Feature cards */
    .feature-grid {
        display: grid; grid-template-columns: repeat(3, 1fr);
        gap: 16px; margin: 36px 0 24px 0;
    }
    @media (max-width: 720px) { .feature-grid { grid-template-columns: 1fr; } }
    .feature-card {
        padding: 22px 20px; border-radius: 16px;
        border: 1px solid rgba(128, 128, 128, 0.18);
        background: rgba(128, 128, 128, 0.04);
        transition: all 0.2s ease; height: 100%;
    }
    .feature-card:hover {
        border-color: rgba(99, 102, 241, 0.45);
        background: rgba(99, 102, 241, 0.06);
        transform: translateY(-2px);
    }
    .feature-icon { font-size: 1.6rem; margin-bottom: 10px; }
    .feature-title { font-size: 1rem; font-weight: 600; margin-bottom: 6px; color: inherit; }
    .feature-desc { font-size: 0.87rem; color: #8a8f98; line-height: 1.5; }

    /* Pills */
    .pill {
        display: inline-block; padding: 3px 10px; border-radius: 999px;
        background: rgba(99, 102, 241, 0.16); color: #a5b4fc;
        font-size: 0.72rem; font-weight: 500;
        margin: 2px 6px 2px 0; white-space: nowrap;
    }

    /* Chat */
    [data-testid="stChatMessage"] {
        border-radius: 14px; padding: 14px 18px; margin-bottom: 10px;
        border: 1px solid rgba(128, 128, 128, 0.15);
        background: rgba(128, 128, 128, 0.05);
    }
    [data-testid="stChatInput"] {
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.3);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid rgba(128,128,128,0.15);
        margin-bottom: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 36px;
        padding: 0 14px;
        border-radius: 8px 8px 0 0;
        font-size: 0.88rem;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.12);
        color: #a5b4fc !important;
    }

    /* Copy popover button — tighter styling */
    div[data-testid="stPopover"] > button {
        background: rgba(99, 102, 241, 0.12) !important;
        color: #a5b4fc !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 8px !important;
        padding: 4px 10px !important;
        font-size: 0.8rem !important;
        height: auto !important;
    }
    div[data-testid="stPopover"] > button:hover {
        background: rgba(99, 102, 241, 0.22) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# SESSION STATE
# =============================================================================
DEFAULTS = {
    "messages": [],
    "vector_store": None,
    "video_id": None,
    "video_title": "",
    "chunk_count": 0,
    "duration_seconds": 0,
    "transcript_language": "",
    "all_chunks": [],
    "mode": "landing",
    "insights": None,
    "insights_video_id": None,
    "conversations": [],
    "saved_videos": [],
    "model": "gpt-4o-mini",
    "retrieval_k": 4,
}
for _k, _v in DEFAULTS.items():
    st.session_state.setdefault(_k, _v)


# =============================================================================
# PERSISTENCE
# =============================================================================
DATA_DIR = PROJECT_ROOT / "data"
CHATS_DIR = DATA_DIR / "chats"
CHATS_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_FILE = DATA_DIR / "videos.json"


def _chat_file(video_id):
    return CHATS_DIR / f"{video_id or 'default'}.json"


def save_chat(video_id, messages):
    try:
        _chat_file(video_id).write_text(
            json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8",
        )
    except Exception:
        pass


def load_chat(video_id):
    path = _chat_file(video_id)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def delete_chat(video_id):
    try:
        _chat_file(video_id).unlink(missing_ok=True)
    except Exception:
        pass


def load_saved_videos():
    if not VIDEOS_FILE.exists():
        return []
    try:
        return json.loads(VIDEOS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_saved_videos(videos):
    try:
        VIDEOS_FILE.write_text(
            json.dumps(videos, ensure_ascii=False, indent=2), encoding="utf-8",
        )
    except Exception:
        pass


def upsert_saved_video(meta):
    videos = load_saved_videos()
    by_id = {v.get("video_id"): v for v in videos if isinstance(v, dict)}
    by_id[meta["video_id"]] = meta
    save_saved_videos(list(by_id.values()))
    return load_saved_videos()


def refresh_conversations():
    convos = []
    for f in sorted(CHATS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        vid = f.stem
        if vid == "default":
            continue
        msgs = load_chat(vid)
        if not msgs:
            continue
        title = None
        for v in st.session_state.saved_videos:
            if v.get("video_id") == vid:
                title = v.get("title") or vid
                break
        convos.append({"video_id": vid, "title": title or vid, "count": len(msgs)})
    st.session_state.conversations = convos


def fetch_all_chunks(store, video_id):
    if not video_id:
        return []
    try:
        return get_all_chunks_for_video(store, video_id, max_chunks=1000)
    except Exception:
        return []


# =============================================================================
# SMALL HELPERS
# =============================================================================
def _fmt_duration(seconds) -> str:
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


def _render_video_preview_inline(height_px: int = 320):
    vid = st.session_state.video_id
    if not vid:
        return
    embed = (
        f'<div style="width:100%;">'
        f'<div style="position:relative;width:100%;padding-bottom:56.25%;height:0;'
        f'border-radius:12px;overflow:hidden;border:1px solid rgba(128,128,128,0.2);background:#000;">'
        f'<iframe src="https://www.youtube.com/embed/{vid}?rel=0&vq=hd1080&modestbranding=1" '
        f'style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" '
        f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen" '
        f'allowfullscreen></iframe>'
        f'</div></div>'
    )
    components.html(embed, height=height_px, scrolling=False)


def _empty_insights():
    return {
        "executive_summary": "",
        "key_takeaways": [],
        "important_topics": [],
        "action_items": [],
        "technical_terms": [],
    }


# =============================================================================
# SIDEBAR CALLBACKS
# =============================================================================
def cb_new_chat():
    st.session_state.messages = []
    st.session_state.mode = "landing"
    st.session_state.video_id = None
    st.session_state.vector_store = None
    st.session_state.insights = None
    st.session_state.insights_video_id = None


def cb_select_conversation(video_id):
    st.session_state.messages = load_chat(video_id)
    st.session_state.video_id = video_id
    st.session_state.mode = "chat"
    st.rerun()


def cb_select_video(video_id):
    try:
        store = load_video_index()
        st.session_state.vector_store = store
        st.session_state.video_id = video_id
        st.session_state.messages = load_chat(video_id)
        st.session_state.all_chunks = fetch_all_chunks(store, video_id)
        st.session_state.chunk_count = len(st.session_state.all_chunks)
        st.session_state.insights = None
        st.session_state.insights_video_id = None
        st.session_state.mode = "chat"
        st.rerun()
    except Exception as exc:
        st.error(f"Could not load index: {exc}")


def cb_clear_all():
    for f in CHATS_DIR.glob("*.json"):
        try:
            f.unlink()
        except Exception:
            pass
    st.session_state.messages = []
    st.session_state.conversations = []
    st.rerun()


# =============================================================================
# SIDEBAR
# =============================================================================
st.session_state.saved_videos = load_saved_videos()
refresh_conversations()

try:
    _settings = render_sidebar(
        state={
            "video_id": st.session_state.video_id,
            "conversations": st.session_state.conversations,
            "saved_videos": st.session_state.saved_videos,
            "model": st.session_state.model,
            "retrieval_k": st.session_state.retrieval_k,
        },
        on_new_chat=cb_new_chat,
        on_select_conversation=cb_select_conversation,
        on_select_video=cb_select_video,
        on_clear_all=cb_clear_all,
    )
    st.session_state.model = _settings.get("model", st.session_state.model)
    st.session_state.retrieval_k = _settings.get("retrieval_k", st.session_state.retrieval_k)
except Exception as _exc:
    st.sidebar.error(f"Sidebar error: {_exc}")


# =============================================================================
# INDEXING
# =============================================================================
def do_index(url: str):
    if not url or not url.strip():
        st.warning("Paste a YouTube URL first.")
        return
    with st.status("Analyzing video…", expanded=True) as status:
        st.write("⏬ Downloading transcript…")
        try:
            result = index_video(url)
            st.write(f"✅ Indexed {result.get('chunk_count', 0)} chunks.")
            st.write("📚 Caching chunks…")
            cached = fetch_all_chunks(result.get("vector_store"), result.get("video_id"))
            st.write(f"✅ Cached {len(cached)} chunks.")
            status.update(label="Ready 🎉", state="complete", expanded=False)

            st.session_state.vector_store = result.get("vector_store")
            st.session_state.video_id = result.get("video_id")
            st.session_state.video_title = result.get("title", "") or ""
            st.session_state.chunk_count = result.get("chunk_count", 0)
            st.session_state.duration_seconds = result.get("duration_seconds", 0) or 0
            st.session_state.transcript_language = result.get("transcript_language", "") or ""
            st.session_state.all_chunks = cached
            st.session_state.messages = load_chat(result.get("video_id"))
            st.session_state.insights = None
            st.session_state.insights_video_id = None
            st.session_state.mode = "chat"

            if result.get("video_id"):
                upsert_saved_video({
                    "video_id": result["video_id"],
                    "title": st.session_state.video_title,
                    "duration_seconds": st.session_state.duration_seconds,
                    "chunk_count": st.session_state.chunk_count,
                    "thumbnail_url": result.get("thumbnail_url", ""),
                })
                st.session_state.saved_videos = load_saved_videos()
            refresh_conversations()
            st.rerun()
        except Exception as exc:
            status.update(label="Failed", state="error", expanded=True)
            st.error(f"Analyze failed: {exc}")


# =============================================================================
# LANDING
# =============================================================================
def render_landing():
    st.markdown(
        f"""
        <div class="hero-wrap">
            <div class="hero-brand">
                {youtube_logo(32, 22)}
                <span class="name">TubeMind AI</span>
                <span class="badge">Beta</span>
            </div>
            <div class="hero-title">Turn any video into <span class="accent">knowledge.</span></div>
            <div class="hero-sub">
                Summarize videos, ask questions, and explore important insights
                with timestamped sources.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<span class="input-label">YouTube video URL</span>', unsafe_allow_html=True)
    col_input, col_btn = st.columns([4, 1], gap="small")
    with col_input:
        video_url = st.text_input(
            "YouTube URL",
            placeholder="Paste a YouTube link…",
            label_visibility="collapsed",
            key="landing_url_input",
        )
    with col_btn:
        analyze_clicked = st.button(
            "Analyze video →",
            type="primary",
            use_container_width=True,
            key="landing_analyze_btn",
        )

    st.markdown(
        """
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">✨</div>
                <div class="feature-title">Smart summaries</div>
                <div class="feature-desc">Get the key takeaways from any video in seconds.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💬</div>
                <div class="feature-title">Ask anything</div>
                <div class="feature-desc">Answers grounded in the video content with cited sources.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⏱️</div>
                <div class="feature-title">Timestamped evidence</div>
                <div class="feature-desc">Jump to the exact moment in the video behind every answer.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📂 Load previous session", use_container_width=True):
            try:
                store = load_video_index()
                st.session_state.vector_store = store
                st.session_state.all_chunks = fetch_all_chunks(store, st.session_state.video_id)
                st.session_state.messages = load_chat(st.session_state.video_id)
                st.session_state.mode = "chat"
                st.rerun()
            except Exception as exc:
                st.error(f"No saved index found. ({exc})")
    with col_b:
        st.caption("Index data lives in `data/`.")

    if analyze_clicked:
        do_index(video_url)


# =============================================================================
# CHAT — three-part workspace layout
# =============================================================================
def render_chat():
    # ---- Top bar ----
    left, right = st.columns([5, 1])
    with left:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">'
            f'{youtube_logo(26, 18)}'
            f'<span style="font-size:1.15rem;font-weight:700;'
            f'background:linear-gradient(90deg,#a5b4fc,#6366f1);'
            f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;">'
            f'TubeMind AI</span></div>',
            unsafe_allow_html=True,
        )
    with right:
        if st.button("← New video", use_container_width=True, key="new_video_btn"):
            st.session_state.mode = "landing"
            st.rerun()

    # ---- Auto-generate insights once per video ----
    current_vid = st.session_state.video_id
    if current_vid and (
        st.session_state.insights is None
        or st.session_state.insights_video_id != current_vid
    ):
        with st.spinner("Reading transcript and preparing insights…"):
            try:
                st.session_state.insights = generate_insights_for_video(
                    st.session_state.vector_store, current_vid,
                )
            except Exception:
                st.session_state.insights = _empty_insights()
            st.session_state.insights_video_id = current_vid

    # ---- 40% video / 60% chat ----
    video_col, chat_col = st.columns([2, 3], gap="large")

    # =========================================================================
    # LEFT: video panel
    # =========================================================================
    with video_col:
        _render_video_preview_inline(height_px=320)

        pills = [
            f'<span class="pill">📼 {st.session_state.chunk_count} chunks</span>',
            f'<span class="pill">⏱ {_fmt_duration(st.session_state.duration_seconds)}</span>',
        ]
        if st.session_state.transcript_language:
            pills.append(f'<span class="pill">🌐 {st.session_state.transcript_language}</span>')
        pills.append('<span class="pill">✅ transcript ready</span>')

        st.markdown(
            f'<div style="margin:8px 0 12px 0;font-size:0.9rem;color:#c7c7c7;">'
            f'<b>{st.session_state.video_title or st.session_state.video_id or ""}</b></div>'
            + f'<div>{"".join(pills)}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown(
            '<div style="font-size:0.72rem;text-transform:uppercase;'
            'letter-spacing:0.1em;color:#8a8f98;font-weight:600;margin-bottom:8px;">'
            '📋 Video summary</div>',
            unsafe_allow_html=True,
        )
        try:
            render_insights_panel(st.session_state.insights or _empty_insights())
        except Exception as exc:
            st.caption(f"Insights unavailable: {exc}")

    # =========================================================================
    # RIGHT: chat panel
    # =========================================================================
    with chat_col:
        tab_chat, tab_sources = st.tabs(["💬 Chat", "📚 Sources"])

        # ---------------- Chat tab ----------------
        with tab_chat:
            if not st.session_state.messages:
                st.caption(
                    "Ask anything about this video. Try: "
                    "*“Summarize in 5 bullets”*, "
                    "*“What does he say about AI?”*, "
                    "*“List the tools he mentions.”*"
                )

            for msg_idx, msg in enumerate(st.session_state.messages):
                is_user = msg["role"] == "user"
                with st.chat_message(msg["role"], avatar="🧑" if is_user else "🎬"):
                    st.markdown(msg.get("content", ""))

                    # ---- Copy button (assistant messages only) ----
                    if not is_user:
                        content = msg.get("content", "") or ""
                        if content.strip():
                            copy_col, _ = st.columns([1, 8])
                            with copy_col:
                                with st.popover("📋 Copy"):
                                    st.code(content, language=None)

                    # ---- Sources expander ----
                    if not is_user and msg.get("sources"):
                        with st.expander(f"📚 Sources ({len(msg['sources'])})", expanded=False):
                            try:
                                render_sources(msg["sources"])
                            except Exception:
                                for s in msg["sources"]:
                                    st.caption(s.get("text", "")[:300])

            # ---- Chat input ----
            question = st.chat_input("Message the video…")
            if question:
                st.session_state.messages.append({"role": "user", "content": question})
                with st.chat_message("user", avatar="🧑"):
                    st.markdown(question)

                with st.chat_message("assistant", avatar="🎬"):
                    placeholder = st.empty()
                    buffer = ""
                    sources = []
                    try:
                        if is_summary_question(question) and not st.session_state.all_chunks:
                            st.session_state.all_chunks = fetch_all_chunks(
                                st.session_state.vector_store,
                                st.session_state.video_id,
                            )
                        docs = (
                            st.session_state.all_chunks
                            if is_summary_question(question) else None
                        )

                        for ev in stream_ask_question(
                            st.session_state.vector_store,
                            question,
                            k=st.session_state.retrieval_k,
                            documents=docs,
                            video_id=st.session_state.video_id,
                        ):
                            if ev["type"] == "token":
                                buffer += ev["text"]
                                placeholder.markdown(buffer + "▌")
                            elif ev["type"] == "sources":
                                sources = ev["sources"]
                        placeholder.markdown(buffer)

                        # ---- Copy button for the fresh answer ----
                        if buffer.strip():
                            copy_col, _ = st.columns([1, 8])
                            with copy_col:
                                with st.popover("📋 Copy"):
                                    st.code(buffer, language=None)

                        # ---- Sources ----
                        if sources:
                            with st.expander(f"📚 Sources ({len(sources)})", expanded=False):
                                try:
                                    render_sources(sources)
                                except Exception:
                                    for s in sources:
                                        st.caption(s.get("text", "")[:300])

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": buffer,
                            "sources": sources,
                        })
                        save_chat(st.session_state.video_id, st.session_state.messages)
                        refresh_conversations()
                    except Exception as exc:
                        err = f"⚠️ Sorry, I couldn't complete the request: {exc}"
                        st.error(err)
                        st.session_state.messages.append({
                            "role": "assistant", "content": err, "sources": [],
                        })
                        save_chat(st.session_state.video_id, st.session_state.messages)
                st.rerun()

        # ---------------- Sources tab ----------------
        with tab_sources:
            all_sources = []
            for msg in st.session_state.messages:
                if msg.get("sources"):
                    all_sources.extend(msg["sources"])
            if not all_sources:
                st.caption("No sources yet. Ask a question to see timestamped evidence.")
            else:
                st.caption(f"{len(all_sources)} sources across this conversation")

                # ---- Copy all sources button ----
                full_text = "\n\n".join(
                    f"[Source {i+1}] {s.get('text', '')}"
                    for i, s in enumerate(all_sources)
                )
                copy_col, _ = st.columns([1, 8])
                with copy_col:
                    with st.popover("📋 Copy all"):
                        st.code(full_text, language=None)

                try:
                    render_sources(all_sources)
                except Exception:
                    for s in all_sources:
                        st.caption(s.get("text", "")[:300])


# =============================================================================
# ROUTER
# =============================================================================
try:
    if st.session_state.mode == "chat" and st.session_state.vector_store is not None:
        render_chat()
    else:
        render_landing()
except Exception as _exc:
    st.error(f"App error: {_exc}")
    st.exception(_exc)