"""Video insights panel."""

import streamlit as st


def _section_title(text: str):
    st.markdown(
        f'<div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;'
        f'color:#8a8f98;font-weight:600;margin:14px 0 6px 0;">{text}</div>',
        unsafe_allow_html=True,
    )


def render_insights_panel(insights: dict):
    """Render the 5 insight sections. Safe with empty data."""
    if not insights:
        st.info("No insights yet. Index a video to generate them.")
        return

    summary = insights.get("executive_summary") or ""
    takeaways = insights.get("key_takeaways") or []
    topics = insights.get("important_topics") or []
    actions = insights.get("action_items") or []
    terms = insights.get("technical_terms") or []

    # ---- Executive summary ----
    _section_title("Executive summary")
    if summary:
        st.markdown(summary)
    else:
        st.caption("Not available.")

    # ---- Key takeaways ----
    _section_title("Key takeaways")
    if takeaways:
        for item in takeaways:
            st.markdown(f"- {item}")
    else:
        st.caption("Not available.")

    # ---- Important topics ----
    _section_title("Important topics")
    if topics:
        pills = "".join(f'<span class="pill">{t}</span>' for t in topics)
        st.markdown(pills, unsafe_allow_html=True)
    else:
        st.caption("Not available.")

    # ---- Action items ----
    _section_title("Action items")
    if actions:
        for item in actions:
            st.markdown(f"- {item}")
    else:
        st.caption("Not available.")

    # ---- Technical terms ----
    _section_title("Technical terms")
    if terms:
        for t in terms:
            st.markdown(f"**{t.get('term','')}** — {t.get('explanation','')}")
    else:
        st.caption("Not available.")