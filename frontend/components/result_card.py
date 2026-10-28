import streamlit as st


def probability_bar(label: str, value: float, color: str):
    pct = value * 100
    st.markdown(
        f"""
        <div class="prob-label"><span>{label}</span><span>{pct:.1f}%</span></div>
        <div class="prob-track"><div class="prob-fill-{color}" style="width:{pct:.1f}%"></div></div>
        """,
        unsafe_allow_html=True,
    )


def render_result_card(result: dict, original_bytes: bytes):
    is_defective = result["prediction"] == "defective"
    css_class = "result-defective" if is_defective else "result-normal"
    title = "Defective" if is_defective else "Normal"
    sub = "Potential defect detected. Manual check recommended." if is_defective else "No defect detected."

    st.markdown(
        f"""
        <div class="result-banner {css_class}">
            <div>
                <div class="eyebrow">Verdict</div>
                <div class="title">{title}</div>
                <div class="sub">{sub}</div>
            </div>
            <div class="conf">{result['confidence'] * 100:.1f}%<small>Confidence</small></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    probability_bar("Normal", result["normal_prob"], "green")
    probability_bar("Defective", result["defective_prob"], "red")
    st.write("")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown('<div class="img-label">Original image</div>', unsafe_allow_html=True)
        st.image(original_bytes, use_container_width=True)
    with col2:
        st.markdown('<div class="img-label">Grad-CAM explanation</div>', unsafe_allow_html=True)
        st.image(result["heatmap_bytes"], use_container_width=True)
        st.caption("Warm areas (red / yellow) influenced the model's decision most.")
    st.caption(f"Saved to history as inspection #{result['id']}")
