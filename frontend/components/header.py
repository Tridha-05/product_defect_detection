import streamlit as st


def render_header():
    """Only the project name - no emoji, no description."""
    st.markdown(
        '<div class="hero-title">AI-Based Product <span class="mark">Defect Detection</span> System</div>',
        unsafe_allow_html=True,
    )
