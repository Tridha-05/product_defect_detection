import streamlit as st

from services import api_client


def _card(number, label, css=""):
    st.markdown(
        f'<div class="stat-card {css}"><div class="num">{number}</div><div class="lbl">{label}</div></div>',
        unsafe_allow_html=True,
    )


def render_stats():
    stats = api_client.get_stats()
    if stats["total"] == 0:
        st.info("No data yet. Inspect a few images first.")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _card(stats["total"], "Total inspections")
    with c2:
        _card(stats["normal"], "Normal", "stat-green")
    with c3:
        _card(stats["defective"], "Defective", "stat-red")
    with c4:
        _card(f"{stats['avg_confidence'] * 100:.1f}%", "Average confidence")

    st.write("")
    st.subheader("Normal vs defective")
    normal_pct = 100 - stats["defect_rate"] * 100
    st.markdown(
        f'<div class="split-bar"><div class="g" style="width:{normal_pct:.1f}%"></div>'
        f'<div class="r" style="width:{stats["defect_rate"] * 100:.1f}%"></div></div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Defect rate: {stats['defect_rate'] * 100:.1f}%")
