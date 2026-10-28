import streamlit as st

from config import API_URL
from services import api_client


def _row(state: str, text: str):
    """One status line with a coloured dot. state = ok | bad | warn"""
    st.markdown(
        f'<div class="status-row"><span class="dot dot-{state}"></span>{text}</div>',
        unsafe_allow_html=True,
    )


def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="side-title">System status</div>', unsafe_allow_html=True)
        health = api_client.get_health()

        if health is None:
            _row("bad", "Backend offline")
            st.markdown(
                f'<div class="side-note">Could not reach {API_URL}.<br>Start it inside the backend folder with '
                f'<code>uvicorn app.main:app --reload</code></div>',
                unsafe_allow_html=True,
            )
            return

        _row("ok", "Backend online")
        if health["model_loaded"]:
            _row("ok", f"ResNet50 loaded ({health['device']})")
        else:
            _row("warn", "Model not trained yet")
        _row("ok" if health["database"] == "connected" else "bad", f"Database {health['database']}")
