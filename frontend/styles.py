"""Look and feel of the whole app.

To change the colours, edit ONLY the values inside  :root { ... }  below.
Pastel background ideas (replace --bg and --bg-soft):
    Peach (default) : #FBEFE3  /  #F6E3D1
    Mint            : #E8F5EC  /  #D8EDE0
    Sky             : #E6F1FA  /  #D5E6F4
    Lavender        : #EFEAFA  /  #E2DAF3
    Butter          : #FBF5DC  /  #F3EBC4
"""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=DM+Sans:wght@400;500;600;700&display=swap');

:root {
    --bg: #FBEFE3;
    --bg-soft: #F6E3D1;
    --card: #FFFFFF;
    --ink: #2A2622;
    --muted: #7B6F65;
    --line: #EAD8C4;
    --highlight: #FFCF8F;
    --green: #16a34a;
    --red: #dc2626;
    --amber: #d97706;
    --serif: 'Fraunces', Georgia, 'Times New Roman', serif;
    --sans: 'DM Sans', 'Segoe UI', system-ui, sans-serif;
}

/* ---------- page ---------- */
.stApp { background: var(--bg); color: var(--ink); font-family: var(--sans); }
header[data-testid="stHeader"] { background: transparent; }
footer { visibility: hidden; }
.block-container { padding-top: 2.4rem; max-width: 1100px; }

.stApp h2, .stApp h3 {
    font-family: var(--serif); font-weight: 600; letter-spacing: -0.01em; color: var(--ink);
}

/* ---------- title ---------- */
.hero-title {
    font-family: var(--serif); font-weight: 700; color: var(--ink);
    font-size: 2.9rem; line-height: 1.18; letter-spacing: -0.02em;
    margin: 0.2rem 0 1.6rem 0;
}
.hero-title .mark {
    background: linear-gradient(transparent 60%, var(--highlight) 60%, var(--highlight) 94%, transparent 94%);
    padding: 0 0.12em;
    -webkit-box-decoration-break: clone; box-decoration-break: clone;
}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] { background: var(--bg-soft); border-right: 1px solid var(--line); }
.side-title {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--muted); margin: 0.4rem 0 0.9rem 0;
}
.status-row {
    display: flex; align-items: center; gap: 0.6rem; padding: 0.7rem 0.9rem; margin-bottom: 0.5rem;
    background: var(--card); border: 1px solid var(--line); border-radius: 12px;
    font-size: 0.92rem; font-weight: 500;
}
.dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.dot-ok { background: var(--green); } .dot-bad { background: var(--red); } .dot-warn { background: var(--amber); }
.side-note { font-size: 0.8rem; color: var(--muted); margin-top: 0.6rem; line-height: 1.5; }
.side-note code { background: var(--card); padding: 1px 6px; border-radius: 6px; }

/* ---------- tabs (pill style) ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; border-bottom: none; background: transparent; margin-bottom: 0.8rem; }
.stTabs [data-baseweb="tab"] {
    height: auto; padding: 0.5rem 1.35rem; border-radius: 999px; background: transparent;
    border: 1px solid var(--line);
}
.stTabs [data-baseweb="tab"] p { color: var(--muted); font-weight: 600; font-size: 0.95rem; }
.stTabs [aria-selected="true"] { background: var(--ink); border-color: var(--ink); }
.stTabs [aria-selected="true"] p { color: #FFFFFF; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* ---------- uploader ---------- */
[data-testid="stFileUploaderDropzone"] {
    background: var(--card); border: 2px dashed #E3C9AA; border-radius: 18px; padding: 2rem 1.5rem;
}
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--ink); }

/* ---------- buttons ---------- */
.stButton > button {
    border-radius: 12px; font-weight: 600; padding: 0.65rem 1.3rem;
    background: transparent; border: 1.5px solid var(--ink); color: var(--ink);
    transition: transform .12s ease, box-shadow .12s ease;
}
.stButton > button p { color: inherit; font-weight: 600; }
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 8px 18px rgba(42, 38, 34, .14); border-color: var(--ink); color: var(--ink); }
.stButton > button[kind="primary"] { background: var(--ink); color: #FFFFFF; }
.stButton > button[kind="primary"] p { color: #FFFFFF; }
.stButton > button[kind="primary"]:hover { color: #FFFFFF; }

/* ---------- images / tables / alerts ---------- */
[data-testid="stImage"] img { border-radius: 16px; border: 1px solid var(--line); }
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }
[data-testid="stAlert"] { border-radius: 14px; }

.file-meta { padding: 0.2rem 0 1.1rem 0; }
.file-name { font-family: var(--serif); font-size: 1.25rem; font-weight: 600; word-break: break-all; }
.file-size { color: var(--muted); font-size: 0.9rem; margin-top: 0.2rem; }
.img-label {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--muted); margin: 0.4rem 0 0.5rem 0;
}

/* ---------- result ---------- */
.result-banner {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.6rem 2rem; border-radius: 20px; color: #FFFFFF; margin: 0.4rem 0 1.4rem 0;
}
.result-normal { background: var(--green); }
.result-defective { background: var(--red); }
.result-banner .eyebrow { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; opacity: .85; }
.result-banner .title { font-family: var(--serif); font-size: 2.4rem; font-weight: 700; line-height: 1.1; margin: 0.15rem 0 0.3rem 0; }
.result-banner .sub { opacity: .92; font-size: 0.98rem; }
.result-banner .conf { font-family: var(--serif); font-size: 3.2rem; font-weight: 700; line-height: 1; text-align: right; }
.result-banner .conf small { display: block; font-family: var(--sans); font-size: 0.72rem; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; opacity: .85; margin-top: 0.3rem; }

.prob-label { display: flex; justify-content: space-between; font-weight: 600; margin-top: 0.7rem; font-size: 0.95rem; }
.prob-track { background: var(--line); border-radius: 999px; height: 12px; overflow: hidden; margin-top: 0.3rem; }
.prob-fill-green { background: var(--green); height: 100%; border-radius: 999px; }
.prob-fill-red { background: var(--red); height: 100%; border-radius: 999px; }

.badge { padding: 4px 14px; border-radius: 999px; color: #FFFFFF; font-weight: 700; font-size: 0.8rem; letter-spacing: .04em; }
.badge-normal { background: var(--green); } .badge-defective { background: var(--red); }

/* ---------- dashboard ---------- */
.stat-card { border-radius: 18px; padding: 1.2rem 1.4rem; background: var(--card); border: 1px solid var(--line); }
.stat-card .num { font-family: var(--serif); font-size: 2.3rem; font-weight: 700; line-height: 1.1; }
.stat-card .lbl { color: var(--muted); font-size: 0.9rem; margin-top: 0.2rem; }
.stat-green .num { color: var(--green); } .stat-red .num { color: var(--red); }

.split-bar { display: flex; height: 22px; border-radius: 999px; overflow: hidden; background: var(--line); }
.split-bar .g { background: var(--green); } .split-bar .r { background: var(--red); }
</style>
"""


def inject_styles():
    st.markdown(CSS, unsafe_allow_html=True)
