"""Streamlit frontend.  Run (inside the frontend folder):  streamlit run app.py"""
import streamlit as st

from components.header import render_header
from components.history_table import render_history
from components.result_card import render_result_card
from components.sidebar import render_sidebar
from components.stats_panel import render_stats
from components.upload_panel import render_upload_panel
from services import api_client
from styles import inject_styles

st.set_page_config(page_title="AI Defect Detection", layout="wide")
inject_styles()
render_header()
render_sidebar()

tab_inspect, tab_history, tab_stats = st.tabs(["Inspect", "History", "Dashboard"])

with tab_inspect:
    submission = render_upload_panel()
    if submission:
        filename, data, content_type = submission
        with st.spinner("Analysing image..."):
            try:
                result = api_client.predict_image(filename, data, content_type)
                st.session_state["last_result"] = (result, data)
            except api_client.APIError as err:
                st.session_state.pop("last_result", None)
                st.error(str(err))

    if "last_result" in st.session_state:
        result, original = st.session_state["last_result"]
        st.divider()
        render_result_card(result, original)

with tab_history:
    try:
        render_history()
    except api_client.APIError as err:
        st.error(str(err))

with tab_stats:
    try:
        render_stats()
    except api_client.APIError as err:
        st.error(str(err))
