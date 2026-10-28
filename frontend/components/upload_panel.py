import html

import streamlit as st


def render_upload_panel():
    """Shows the uploader + preview. Returns (filename, bytes, content_type) when 'Inspect' is clicked."""
    uploaded = st.file_uploader(
        "Drop a product image here, or browse",
        type=["png", "jpg", "jpeg", "bmp", "webp"],
        help="PNG or JPG, up to 10 MB",
    )
    if uploaded is None:
        st.info("Upload an image to begin.")
        return None

    col_preview, col_action = st.columns([3, 2], gap="large")
    with col_preview:
        st.image(uploaded, use_container_width=True)
    with col_action:
        size_kb = len(uploaded.getvalue()) / 1024
        st.markdown(
            f'<div class="file-meta"><div class="file-name">{html.escape(uploaded.name)}</div>'
            f'<div class="file-size">{size_kb:,.0f} KB</div></div>',
            unsafe_allow_html=True,
        )
        clicked = st.button("Inspect image", type="primary", use_container_width=True)

    if clicked:
        return uploaded.name, uploaded.getvalue(), uploaded.type
    return None
