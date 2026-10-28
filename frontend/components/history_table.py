import pandas as pd
import streamlit as st

from config import GREEN, RED
from services import api_client


def _colour(value: str) -> str:
    colour = RED if value == "defective" else GREEN
    return f"background-color: {colour}; color: white; font-weight: bold"


def render_history():
    rows = api_client.get_history(limit=200)
    if not rows:
        st.info("No inspections yet. Go to the Inspect tab and upload an image.")
        return

    df = pd.DataFrame(rows)
    df["confidence"] = (df["confidence"] * 100).round(1)
    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d %b %Y, %H:%M")
    table = df[["id", "filename", "prediction", "confidence", "created_at"]].rename(
        columns={"confidence": "confidence %", "created_at": "date"}
    )
    st.dataframe(table.style.map(_colour, subset=["prediction"]), use_container_width=True, hide_index=True)

    st.write("")
    st.subheader("Look at a past result")
    chosen = st.selectbox("Choose inspection ID", df["id"].tolist())
    row = df[df["id"] == chosen].iloc[0]

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="img-label">Original</div>', unsafe_allow_html=True)
        st.image(api_client.get_image(int(chosen), "original"), use_container_width=True)
    with c2:
        st.markdown('<div class="img-label">Grad-CAM</div>', unsafe_allow_html=True)
        st.image(api_client.get_image(int(chosen), "heatmap"), use_container_width=True)

    badge = "badge-defective" if row["prediction"] == "defective" else "badge-normal"
    st.markdown(
        f'<span class="badge {badge}">{row["prediction"].upper()}</span> &nbsp; '
        f'confidence {row["confidence"]}% &nbsp;&middot;&nbsp; <code>{row["filename"]}</code>',
        unsafe_allow_html=True,
    )

    st.write("")
    if st.button("Delete this record"):
        api_client.delete_inspection(int(chosen))
        st.rerun()
