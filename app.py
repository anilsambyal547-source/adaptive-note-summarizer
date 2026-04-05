# app.py — Adaptive Note Summarizer (Production Version)
# All 14 improvements integrated: OCR/Vision, chunking, RAG, dynamic models,
# API key management, error handling, caching, progress, batch, security, accessibility.

import streamlit as st

# ========== PAGE CONFIG (must be first Streamlit call) ==========
st.set_page_config(
    page_title="Adaptive Note Summarizer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========== GLOBAL CSS ==========
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Base reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Page background ── */
.stApp {
    background: linear-gradient(135deg, #0f1117 0%, #13151f 50%, #0f1117 100%);
    min-height: 100vh;
}

/* ── Custom scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #1a1d27; }
::-webkit-scrollbar-thumb { background: #6c63ff; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #a78bfa; }

/* ── Fade-in animation ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}
@keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position:  200% 0; }
}
@keyframes gradientShift {
    0%   { background-position: 0%   50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0%   50%; }
}

/* ── Section fade-in ── */
.main .block-container {
    animation: fadeInUp 0.5s ease both;
    padding-top: 1rem !important;
    max-width: 1200px;
}

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1a1d27 0%, #1e1b33 50%, #1a1d27 100%);
    border: 1px solid rgba(108, 99, 255, 0.3);
    border-radius: 20px;
    padding: 2.5rem 2.8rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg,
        rgba(108,99,255,0.08) 0%,
        rgba(167,139,250,0.06) 50%,
        rgba(108,99,255,0.08) 100%);
    background-size: 200% 100%;
    animation: shimmer 4s linear infinite;
    pointer-events: none;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa 0%, #6c63ff 50%, #c4b5fd 100%);
    background-size: 200% 200%;
    animation: gradientShift 5s ease infinite;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.5rem 0;
    line-height: 1.15;
}
.hero-sub {
    color: #94a3b8;
    font-size: 1.05rem;
    font-weight: 400;
    margin: 0 0 1.2rem 0;
}
.hero-badges { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.badge {
    display: inline-flex; align-items: center; gap: 0.35rem;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    font-size: 0.78rem; font-weight: 600;
    border: 1px solid;
    animation: fadeInUp 0.6s ease both;
}
.badge-ai    { background: rgba(108,99,255,.15); border-color: rgba(108,99,255,.4); color: #a78bfa; }
.badge-ocr   { background: rgba(52,211,153,.1);  border-color: rgba(52,211,153,.35); color: #6ee7b7; }
.badge-rag   { background: rgba(251,191,36,.1);   border-color: rgba(251,191,36,.35); color: #fde68a; }
.badge-smart { background: rgba(236,72,153,.1);   border-color: rgba(236,72,153,.35); color: #f9a8d4; }

/* ── Glass card ── */
.glass-card {
    background: rgba(26, 29, 39, 0.75);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(108,99,255,0.18);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    transition: border-color .25s, box-shadow .25s;
}
.glass-card:hover {
    border-color: rgba(108,99,255,0.45);
    box-shadow: 0 0 24px rgba(108,99,255,0.12);
}

/* ── Section header ── */
.section-header {
    display: flex; align-items: center; gap: 0.7rem;
    margin: 1.6rem 0 1rem 0;
}
.section-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #6c63ff, #a78bfa);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}
.section-title {
    font-size: 1.2rem; font-weight: 700; color: #e2e8f0; margin: 0;
}

/* ── Metric cards ── */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.4rem;
}
@media (max-width: 900px) { .metrics-grid { grid-template-columns: repeat(2,1fr); } }
.metric-card {
    background: rgba(26,29,39,0.8);
    border: 1px solid rgba(108,99,255,0.2);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    border-top: 3px solid;
    transition: transform .2s, box-shadow .2s;
}
.metric-card:hover { transform: translateY(-3px); box-shadow: 0 8px 28px rgba(0,0,0,.3); }
.metric-label { font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: .07em; color: #64748b; margin-bottom: .35rem; }
.metric-value { font-size: 1.9rem; font-weight: 800; color: #e2e8f0; line-height: 1; margin-bottom: .2rem; }
.metric-icon  { font-size: 1.3rem; margin-bottom: .4rem; }

/* ── Upload zone ── */
.upload-toggle {
    display: flex; border: 1px solid rgba(108,99,255,.3); border-radius: 10px;
    overflow: hidden; margin-bottom: 1rem; width: fit-content;
}
.upload-tab {
    padding: .45rem 1.2rem; font-size: .85rem; font-weight: 600; cursor: pointer;
    color: #94a3b8; transition: all .2s;
}
.upload-tab.active {
    background: linear-gradient(135deg, #6c63ff, #a78bfa);
    color: #fff;
}

/* ── Streamlit button overrides ── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all .2s ease !important;
    border: 1px solid rgba(108,99,255,.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(108,99,255,.3) !important;
    border-color: rgba(108,99,255,.7) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6c63ff 0%, #a78bfa 100%) !important;
    border: none !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #7c74ff 0%, #b89bfa 100%) !important;
    box-shadow: 0 8px 24px rgba(108,99,255,.5) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1px solid rgba(108,99,255,.3) !important;
    background: rgba(26,29,39,.9) !important;
}

/* ── Text input / textarea ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 10px !important;
    border: 1px solid rgba(108,99,255,.3) !important;
    background: rgba(26,29,39,.85) !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6c63ff !important;
    box-shadow: 0 0 0 3px rgba(108,99,255,.2) !important;
}

/* ── File uploader ── */
.stFileUploader > div {
    border: 2px dashed rgba(108,99,255,.4) !important;
    border-radius: 14px !important;
    background: rgba(108,99,255,.04) !important;
    transition: border-color .2s, background .2s !important;
}
.stFileUploader > div:hover {
    border-color: rgba(108,99,255,.7) !important;
    background: rgba(108,99,255,.08) !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #6c63ff, #a78bfa) !important;
    border-radius: 4px !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius: 14px !important;
    border: 1px solid rgba(108,99,255,.15) !important;
    backdrop-filter: blur(8px) !important;
    margin-bottom: .6rem !important;
}
[data-testid="stChatMessage"][data-testid*="user"] {
    background: rgba(108,99,255,.12) !important;
    border-color: rgba(108,99,255,.3) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    border-radius: 10px !important;
    border: 1px solid rgba(108,99,255,.2) !important;
    background: rgba(26,29,39,.7) !important;
    font-weight: 600 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #13151f 0%, #0f1117 100%) !important;
    border-right: 1px solid rgba(108,99,255,.15) !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: rgba(108,99,255,.08) !important;
    border-color: rgba(108,99,255,.25) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(108,99,255,.18) !important;
}

/* ── Status dot ── */
.status-dot {
    display: inline-block; width: 9px; height: 9px;
    border-radius: 50%; margin-right: 6px; vertical-align: middle;
}
.status-dot.online  { background: #22c55e; animation: pulse 1.8s infinite; }
.status-dot.offline { background: #ef4444; }

/* ── Sidebar logo area ── */
.sidebar-logo {
    background: linear-gradient(135deg, rgba(108,99,255,.15), rgba(167,139,250,.08));
    border: 1px solid rgba(108,99,255,.25);
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    margin-bottom: 1.2rem;
    text-align: center;
}
.sidebar-app-name {
    font-size: 1rem; font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #6c63ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: .35rem 0 0 0;
}
.sidebar-tagline { font-size: .72rem; color: #64748b; margin: 0; }

/* ── Info / success / warning / error overrides ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-left: 4px solid !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(108,99,255,.35), transparent) !important;
    margin: 1.4rem 0 !important;
}

/* ── Analysis result card ── */
.result-card {
    background: rgba(26,29,39,.75);
    border: 1px solid rgba(108,99,255,.25);
    border-left: 4px solid #6c63ff;
    border-radius: 0 14px 14px 0;
    padding: 1.5rem 1.8rem;
    margin-top: 1rem;
    animation: fadeInUp .4s ease both;
}
.result-card h3 {
    font-size: 1rem; font-weight: 700; color: #a78bfa;
    margin: 0 0 .9rem 0; letter-spacing: .02em;
}

/* ── Quick Q chips ── */
.quick-chip {
    display: inline-block;
    padding: .38rem .9rem;
    border: 1px solid rgba(108,99,255,.35);
    border-radius: 999px;
    font-size: .8rem; font-weight: 500; color: #a78bfa;
    background: rgba(108,99,255,.07);
    cursor: pointer; transition: all .2s;
    margin: .25rem;
}
.quick-chip:hover { background: rgba(108,99,255,.2); border-color: rgba(108,99,255,.65); }

/* ── Footer ── */
.app-footer {
    text-align: center;
    padding: 1.5rem 0 .5rem 0;
    color: #475569;
    font-size: .78rem;
    border-top: 1px solid rgba(108,99,255,.15);
    margin-top: 2.5rem;
}
.app-footer span { color: #6c63ff; font-weight: 600; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(108,99,255,.2) !important;
}

/* ── Hide default streamlit branding ── */
#MainMenu { visibility: hidden; }
footer     { visibility: hidden; }
header     { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

import io
import os
import tempfile
import time
import logging

import PyPDF2
import docx

from utils.api_key_manager import APIKeyManager
from utils.model_manager import ModelManager
from utils.classifier import DomainClassifier
from utils.chunker import semantic_chunk, map_reduce_summarize
from utils.rag_engine import RAGEngine
from utils.ocr_processor import (
    extract_text_from_image,
    extract_text_from_scanned_pdf,
)

logger = logging.getLogger(__name__)

# ========== CONSTANTS ==========
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp")
ACCEPTED_TYPES = ["pdf", "txt", "docx", "png", "jpg", "jpeg", "tiff", "bmp", "webp"]

# ========== SESSION STATE DEFAULTS ==========
_DEFAULTS = {
    "doc_text": "",
    "doc_name": "",
    "doc_type": "General",
    "chat_history": [],
    "processing_mode": "",
    "rag_engine": None,
    "batch_results": [],
}

for _key, _val in _DEFAULTS.items():
    if _key not in st.session_state:
        st.session_state[_key] = _val


# ========== CACHED DOCUMENT PARSING ==========
@st.cache_data(show_spinner=False)
def parse_txt(raw_bytes: bytes) -> str:
    return raw_bytes.decode("utf-8", errors="replace")


@st.cache_data(show_spinner=False)
def parse_pdf(raw_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(raw_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


@st.cache_data(show_spinner=False)
def parse_docx(raw_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(raw_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


# ========== INITIALISE AI ==========
key_mgr = APIKeyManager()

if not key_mgr.current_key:
    st.error(
        "🔑 **API Key Required**\n\n"
        "Add your Gemini API key in **Settings → Secrets** on Streamlit Cloud, "
        "or set the `GEMINI_API_KEY` environment variable locally."
    )
    st.stop()

model_mgr = ModelManager(api_key=key_mgr.current_key)

if not model_mgr.is_active:
    with st.status("🔌 Connecting to Gemini AI…", expanded=True) as status:
        st.write("Discovering available models…")
        name = model_mgr.discover_and_init()
        if name:
            status.update(label=f"✅ Connected — {name}", state="complete")
        else:
            status.update(label="❌ Connection failed", state="error")
            new_key = key_mgr.rotate_key()
            if new_key and new_key != key_mgr.current_key:
                model_mgr = ModelManager(api_key=new_key)
                name = model_mgr.discover_and_init()
                if name:
                    status.update(label=f"✅ Connected (key rotated) — {name}", state="complete")


# ========== SIDEBAR ==========
with st.sidebar:
    # Logo / app identity
    ai_status_dot = "online" if model_mgr.is_active else "offline"
    ai_status_label = model_mgr.model_name if model_mgr.is_active else "Offline"
    st.markdown(f"""
    <div class="sidebar-logo">
        <div style="font-size:2rem">📚</div>
        <p class="sidebar-app-name">Adaptive Note Summarizer</p>
        <p class="sidebar-tagline">Powered by Google Gemini</p>
    </div>
    """, unsafe_allow_html=True)

    # AI Status
    st.markdown(f"""
    <div class="glass-card" style="padding:.9rem 1.1rem; margin-bottom:.7rem;">
        <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#64748b;margin-bottom:.5rem;">AI ENGINE</div>
        <div style="display:flex;align-items:center;gap:.5rem;">
            <span class="status-dot {ai_status_dot}"></span>
            <span style="font-weight:600;color:#e2e8f0;font-size:.88rem;">
                {"✅ Active" if model_mgr.is_active else "❌ Offline"}
            </span>
        </div>
        {"<div style='margin-top:.4rem;font-size:.75rem;color:#6c63ff;font-weight:500;word-break:break-all;'>"+model_mgr.model_name+"</div>" if model_mgr.is_active else ""}
        {"<div style='margin-top:.35rem;font-size:.72rem;color:#ef4444;'>"+model_mgr.error+"</div>" if not model_mgr.is_active and model_mgr.error else ""}
    </div>
    """, unsafe_allow_html=True)

    # API usage
    usage = key_mgr.get_usage_info()
    st.markdown(f"""
    <div style="font-size:.72rem;color:#475569;margin-bottom:.5rem;padding:0 .2rem;">
        Key {usage['key_index'] + 1}/{usage['total_keys']} &nbsp;·&nbsp; {usage['requests_used']} requests used
        {"&nbsp;<span style='color:#f59e0b;'>⚠ Near quota</span>" if usage['near_quota'] else ""}
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Reconnect AI", key="sidebar_reconnect", use_container_width=True):
        model_mgr.reset()
        st.rerun()

    if st.session_state.processing_mode:
        st.caption(f"Mode: `{st.session_state.processing_mode}`")

    st.divider()

    # Quick samples
    st.markdown("""
    <div style="font-size:.8rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#64748b;margin-bottom:.7rem;">
        📁 Quick Samples
    </div>
    """, unsafe_allow_html=True)

    SAMPLES = {
        "🔢 Math": (
            "CALCULUS NOTES\n\nDerivatives:\n"
            "The derivative measures change: f'(x) = lim(h→0) [f(x+h) - f(x)]/h\n\n"
            "Example: Derivative of x² is 2x\n\n"
            "Integration:\n∫ x² dx = (x³/3) + C\n\n"
            "Theorem: Fundamental Theorem of Calculus",
            "Mathematics",
        ),
        "📖 Lit": (
            "ROMEO AND JULIET\n\nCharacters:\n- Romeo: Young Montague\n"
            "- Juliet: Young Capulet\n- Tybalt: Juliet's cousin\n\n"
            "Themes:\n1. Love vs Family\n2. Fate and Free Will\n"
            "3. Youth and Impulsivity\n\n"
            'Famous Quote:\n"What\'s in a name? That which we call a rose\n'
            'By any other name would smell as sweet"',
            "Literature",
        ),
        "📄 Gen": (
            "BUSINESS REPORT — Q4 2024\n\nExecutive Summary:\n"
            "18% revenue growth, 25% customer satisfaction increase.\n\n"
            "Key Achievements:\n1. Launched AI features\n"
            "2. Expanded to 3 markets\n3. Reduced costs by 15%\n\n"
            "Recommendations:\n1. Invest in machine learning\n"
            "2. Hire engineering staff\n3. Expand to Asian markets",
            "General",
        ),
    }

    cols = st.columns(3)
    for i, (label, (text, dtype)) in enumerate(SAMPLES.items()):
        with cols[i]:
            if st.button(label, key=f"sample_{label}", use_container_width=True):
                st.session_state.doc_text = text
                st.session_state.doc_name = f"{label} Sample"
                st.session_state.doc_type = dtype
                st.session_state.rag_engine = None
                st.rerun()

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑 Clear Doc", key="clear_doc", use_container_width=True):
            st.session_state.doc_text = ""
            st.session_state.doc_name = ""
            st.session_state.rag_engine = None
            st.session_state.batch_results = []
            st.rerun()
    with c2:
        if st.button("🗑 Clear Chat", key="clear_chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    st.divider()

    # Debug status
    st.markdown("""
    <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#475569;margin-bottom:.5rem;">
        Status
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:.8rem;color:#94a3b8;line-height:1.9;">
        <b>AI:</b> {"✅" if model_mgr.is_active else "❌"}<br>
        <b>Doc:</b> {st.session_state.doc_name or "—"}<br>
        <b>Chat:</b> {len(st.session_state.chat_history)} msgs
    </div>
    """, unsafe_allow_html=True)


# ========== HERO HEADER ==========
st.markdown(f"""
<div class="hero-banner">
    <h1 class="hero-title">📚 Adaptive Note Summarizer</h1>
    <p class="hero-sub">AI-powered document analysis &amp; Q&amp;A — upload, ask, understand.</p>
    <div class="hero-badges">
        <span class="badge badge-ai">⚡ Google Gemini</span>
        <span class="badge badge-ocr">👁 Vision OCR</span>
        <span class="badge badge-rag">🔍 RAG Engine</span>
        <span class="badge badge-smart">🧠 Smart Chunking</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ========== FILE PROCESSING HELPERS ==========
def _process_single_file(file_obj) -> tuple[str, str, str]:
    """
    Process a single uploaded file.
    Returns (content, doc_type, processing_mode).
    Raises ValueError on failure.
    """
    name = file_obj.name.lower()
    raw = file_obj.read()

    if len(raw) > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"File exceeds {MAX_FILE_SIZE_MB} MB limit ({len(raw) / 1024 / 1024:.1f} MB)."
        )

    processing_mode = "text"

    with tempfile.NamedTemporaryFile(delete=True, suffix=os.path.splitext(name)[1]) as tmp:
        tmp.write(raw)
        tmp.flush()

        if name.endswith(".txt"):
            content = parse_txt(raw)
        elif name.endswith(".pdf"):
            content = parse_pdf(raw)
            if len(content.strip()) < 50:
                processing_mode = "ocr_scanned_pdf"
                result = extract_text_from_scanned_pdf(raw, model=model_mgr.model)
                if result.success:
                    content = result.text
                    processing_mode = f"ocr:{result.method}"
                else:
                    warnings = "; ".join(result.warnings) if result.warnings else "Unknown error"
                    raise ValueError(
                        f"Could not extract text from scanned PDF. {warnings}\n\n"
                        "💡 Try uploading a clearer scan or a text-based PDF."
                    )
        elif name.endswith(".docx"):
            content = parse_docx(raw)
        elif any(name.endswith(ext) for ext in IMAGE_EXTENSIONS):
            processing_mode = "ocr_image"
            result = extract_text_from_image(raw, model=model_mgr.model)
            if result.success:
                content = result.text
                processing_mode = f"ocr:{result.method}"
            else:
                warnings = "; ".join(result.warnings) if result.warnings else "Unknown error"
                raise ValueError(
                    f"Could not extract text from image. {warnings}\n\n"
                    "💡 Try uploading a higher-resolution image with clear text."
                )
        else:
            content = raw.decode("utf-8", errors="replace")

    doc_type = DomainClassifier.classify(content)
    return content, doc_type, processing_mode


# ========== UPLOAD SECTION ==========
st.markdown("""
<div class="section-header">
    <div class="section-icon">📤</div>
    <p class="section-title">Upload Document</p>
</div>
""", unsafe_allow_html=True)

upload_mode = st.radio(
    "Upload mode:",
    ["Single file", "Batch (multiple files)"],
    horizontal=True,
    key="upload_mode",
    label_visibility="collapsed",
)

if upload_mode == "Single file":
    uploaded = st.file_uploader(
        "Drop your file here — PDF, TXT, DOCX, or Image",
        type=ACCEPTED_TYPES,
        help=f"Max {MAX_FILE_SIZE_MB} MB · Supports scanned PDFs & images via OCR",
        key="single_upload",
    )

    if uploaded:
        with st.status("📄 Processing document…", expanded=True) as status:
            try:
                st.write(f"Reading **{uploaded.name}**…")
                content, doc_type, mode = _process_single_file(uploaded)

                st.session_state.doc_text = content
                st.session_state.doc_name = uploaded.name
                st.session_state.doc_type = doc_type
                st.session_state.processing_mode = mode
                st.session_state.rag_engine = None

                st.write(f"✅ Extracted **{len(content.split()):,}** words")
                st.write(f"📎 Classified as **{doc_type}** · Mode: `{mode}`")
                status.update(label="✅ Document ready", state="complete")

            except ValueError as exc:
                status.update(label="❌ Processing failed", state="error")
                st.error(str(exc))
            except Exception as exc:
                status.update(label="❌ Unexpected error", state="error")
                st.error(f"File processing error: {exc}")

else:
    uploaded_files = st.file_uploader(
        "Drop multiple files here",
        type=ACCEPTED_TYPES,
        accept_multiple_files=True,
        help=f"Max {MAX_FILE_SIZE_MB} MB each",
        key="batch_upload",
    )

    if uploaded_files:
        if st.button("🚀 Process All Files", type="primary", key="batch_process"):
            results = []
            progress = st.progress(0, text="Processing batch…")
            total = len(uploaded_files)

            for i, f in enumerate(uploaded_files):
                progress.progress(i / total, text=f"Processing {f.name}…")
                try:
                    content, doc_type, mode = _process_single_file(f)
                    results.append({
                        "File": f.name,
                        "Words": len(content.split()),
                        "Type": doc_type,
                        "Mode": mode,
                        "Status": "✅",
                        "_content": content,
                    })
                except Exception as exc:
                    results.append({
                        "File": f.name,
                        "Words": 0,
                        "Type": "—",
                        "Mode": "—",
                        "Status": f"❌ {exc}",
                        "_content": "",
                    })

            progress.progress(1.0, text="Done!")
            st.session_state.batch_results = results

            display = [{k: v for k, v in r.items() if k != "_content"} for r in results]
            st.dataframe(display, use_container_width=True)

            for r in results:
                if r["_content"]:
                    st.session_state.doc_text = r["_content"]
                    st.session_state.doc_name = r["File"]
                    st.session_state.doc_type = r["Type"]
                    st.session_state.rag_engine = None
                    st.info(f"📄 Loaded **{r['File']}** for analysis.")
                    break


# ========== TEXT INPUT ==========
st.markdown("""
<div class="section-header" style="margin-top:1.8rem;">
    <div class="section-icon">📝</div>
    <p class="section-title">Or Paste Text Directly</p>
</div>
""", unsafe_allow_html=True)

text_input = st.text_area(
    "Paste your document:",
    height=180,
    value=st.session_state.doc_text,
    placeholder="Paste any text, notes, article, or document here…",
    key="text_input_area",
    label_visibility="collapsed",
)

if text_input and text_input != st.session_state.doc_text:
    st.session_state.doc_text = text_input
    st.session_state.doc_type = DomainClassifier.classify(text_input)
    st.session_state.rag_engine = None
    if not st.session_state.doc_name:
        st.session_state.doc_name = "Pasted Text"


# ========== AI HELPER FUNCTIONS ==========
def _ensure_rag_indexed():
    """Build RAG index for current document if not already done."""
    if st.session_state.rag_engine is not None:
        return st.session_state.rag_engine

    text = st.session_state.doc_text
    if not text:
        return None

    chunks = semantic_chunk(text)
    engine = RAGEngine()

    with st.status("🔍 Indexing document for retrieval…", expanded=False) as status:
        st.write(f"Chunked into {len(chunks)} segments")
        indexed = engine.index(chunks)
        if indexed:
            st.write("✅ FAISS index built")
            status.update(label="✅ Document indexed", state="complete")
        else:
            st.write("ℹ️ Using full-text fallback (FAISS unavailable)")
            status.update(label="ℹ️ Indexed (fallback)", state="complete")

    st.session_state.rag_engine = engine
    return engine


def ask_gemini(question: str, context: str) -> str:
    """Ask Gemini about the document using RAG-retrieved context."""
    if not model_mgr.is_active or not model_mgr.model:
        return "⚠️ AI is offline. Click **Reconnect AI** in the sidebar."

    engine = _ensure_rag_indexed()
    if engine:
        rag_context = engine.build_context(question, top_k=5, max_chars=6000)
    else:
        rag_context = context[:4000]

    prompt = f"""DOCUMENT CONTEXT:
{rag_context}

QUESTION: {question}

Answer based ONLY on the document context above. If the answer is not found, say so clearly."""

    try:
        key_mgr.record_usage()
        response = model_mgr.model.generate_content(prompt)
        return response.text if response and response.text else "No response generated."
    except Exception as exc:
        if "429" in str(exc) or "quota" in str(exc).lower():
            new_key = key_mgr.rotate_key()
            if new_key:
                model_mgr_new = ModelManager(api_key=new_key)
                model_mgr_new.discover_and_init()
        return f"**AI Error:** {exc}"


def summarize_document(context: str, doc_type: str) -> str:
    """Summarize using chunked map-reduce for long documents."""
    if not model_mgr.is_active or not model_mgr.model:
        return "⚠️ AI is offline. Click **Reconnect AI** in the sidebar."

    chunks = semantic_chunk(context)

    if len(chunks) <= 1:
        prompt = f"""Summarize this {doc_type} document:

{context}

Provide a comprehensive summary with key points. Use markdown formatting."""
        try:
            key_mgr.record_usage()
            response = model_mgr.model.generate_content(prompt)
            return response.text if response and response.text else "Summary failed."
        except Exception as exc:
            return f"**Summary Error:** {exc}"

    progress = st.progress(0, text="Summarizing…")
    total_steps = len(chunks) + 1

    def progress_cb(current, total, phase):
        if phase == "map":
            pct = current / total_steps
            progress.progress(pct, text=f"Summarizing section {current + 1}/{total}…")
        else:
            progress.progress((total_steps - 1) / total_steps, text="Combining summaries…")

    key_mgr.record_usage()
    result = map_reduce_summarize(chunks, model_mgr.model, doc_type, progress_callback=progress_cb)
    progress.progress(1.0, text="✅ Summary complete")
    return result


# ========== DOCUMENT ANALYSIS ==========
if st.session_state.doc_text:
    st.divider()

    # Domain colours for metric card borders
    domain_info = DomainClassifier.get_domain_info(st.session_state.doc_type)
    domain_color = domain_info["color"]
    domain_icon  = domain_info["icon"]
    words_count  = len(st.session_state.doc_text.split())
    chars_count  = len(st.session_state.doc_text)
    chunks_count = len(semantic_chunk(st.session_state.doc_text))

    # ── Metric cards ──
    st.markdown(f"""
    <div class="metrics-grid">
        <div class="metric-card" style="border-top-color:#6c63ff;">
            <div class="metric-icon">✍️</div>
            <div class="metric-label">Words</div>
            <div class="metric-value">{words_count:,}</div>
        </div>
        <div class="metric-card" style="border-top-color:#a78bfa;">
            <div class="metric-icon">🔤</div>
            <div class="metric-label">Characters</div>
            <div class="metric-value">{chars_count:,}</div>
        </div>
        <div class="metric-card" style="border-top-color:{domain_color};">
            <div class="metric-icon">{domain_icon}</div>
            <div class="metric-label">Document type</div>
            <div class="metric-value" style="font-size:1.35rem;">{st.session_state.doc_type}</div>
        </div>
        <div class="metric-card" style="border-top-color:#22d3ee;">
            <div class="metric-icon">🧩</div>
            <div class="metric-label">Chunks</div>
            <div class="metric-value">{chunks_count}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── AI Analysis ──
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">🤖</div>
        <p class="section-title">AI Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    if not model_mgr.is_active:
        st.warning("🔄 **AI Connecting…** Please wait or click Reconnect AI in the sidebar.")

    analysis_type = st.selectbox(
        "Analysis type:",
        ["Summary", "Key Points", "Deep Analysis", "Q&A"],
        key="analysis_select",
        label_visibility="collapsed",
    )

    if analysis_type == "Summary":
        if st.button("✨ Generate Summary", type="primary", key="btn_summary"):
            with st.spinner("Generating summary…"):
                summary = summarize_document(st.session_state.doc_text, st.session_state.doc_type)
            st.markdown(f"""
            <div class="result-card">
                <h3>📋 Summary</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(summary)

    elif analysis_type == "Key Points":
        if st.button("🔑 Extract Key Points", type="primary", key="btn_keypoints"):
            with st.spinner("Extracting key points…"):
                response = ask_gemini(
                    "What are the key points of this document? List them clearly.",
                    st.session_state.doc_text,
                )
            st.markdown(f"""
            <div class="result-card">
                <h3>🔑 Key Points</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(response)

    elif analysis_type == "Deep Analysis":
        if st.button("🧠 Perform Deep Analysis", type="primary", key="btn_deep"):
            with st.spinner("Analyzing deeply…"):
                response = ask_gemini(
                    "Provide a thorough, in-depth analysis of this document including "
                    "structure, themes, methodology, strengths, and limitations.",
                    st.session_state.doc_text,
                )
            st.markdown(f"""
            <div class="result-card">
                <h3>🧠 Deep Analysis</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(response)

    elif analysis_type == "Q&A":
        st.markdown("""
        <div class="section-header" style="margin-top:.8rem;">
            <div class="section-icon" style="font-size:.9rem;">💬</div>
            <p class="section-title" style="font-size:1rem;">Ask Questions</p>
        </div>
        """, unsafe_allow_html=True)

        # Chat history
        if st.session_state.chat_history:
            seen = set()
            unique = []
            for msg in st.session_state.chat_history[-20:]:
                key = f"{msg['role']}:{msg['content'][:80]}"
                if key not in seen:
                    seen.add(key)
                    unique.append(msg)
            for msg in unique:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Question form
        with st.form(key="qa_form", clear_on_submit=True):
            question = st.text_input(
                "Your question:",
                placeholder="Ask anything about the document…",
                key="question_input",
                label_visibility="collapsed",
            )
            cols = st.columns([1, 5])
            with cols[0]:
                submitted = st.form_submit_button("🚀 Ask", type="primary", use_container_width=True)
            with cols[1]:
                clear = st.form_submit_button("🗑 Clear Chat", use_container_width=True)

        if submitted and question:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("Thinking…"):
                answer = ask_gemini(question, st.session_state.doc_text)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()

        if clear:
            st.session_state.chat_history = []
            st.rerun()

        # Quick questions
        quick_qs = {
            "Mathematics": ["What are the main formulas?", "Explain the key theorem", "What examples are given?"],
            "Literature":  ["Who are the main characters?", "What are the themes?", "Analyze the writing style"],
            "General":     ["What is this about?", "What are the key points?", "Summarize the conclusions"],
        }
        questions = quick_qs.get(st.session_state.doc_type, quick_qs["General"])

        st.markdown("""
        <div style="font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:#64748b;margin:.9rem 0 .5rem 0;">
            💡 Suggested Questions
        </div>
        """, unsafe_allow_html=True)

        qcols = st.columns(3)
        for i, q in enumerate(questions[:3]):
            with qcols[i]:
                if st.button(f"❓ {q}", key=f"quick_q_{i}", use_container_width=True):
                    st.session_state.chat_history.append({"role": "user", "content": q})
                    with st.spinner("…"):
                        answer = ask_gemini(q, st.session_state.doc_text)
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    st.rerun()

    # ── Document preview ──
    st.divider()
    with st.expander("📄 View Document Content", expanded=False):
        preview_limit = min(len(st.session_state.doc_text), 5000)
        st.text_area(
            "Content preview",
            st.session_state.doc_text[:preview_limit],
            height=200,
            disabled=True,
            key="doc_preview",
        )
        if len(st.session_state.doc_text) > preview_limit:
            st.caption(f"Showing first {preview_limit:,} of {len(st.session_state.doc_text):,} characters")

else:
    # Empty state
    st.markdown("""
    <div class="glass-card" style="text-align:center;padding:3rem 2rem;margin-top:.5rem;">
        <div style="font-size:3.5rem;margin-bottom:1rem;">📂</div>
        <h2 style="font-size:1.3rem;font-weight:700;color:#e2e8f0;margin:0 0 .5rem 0;">
            No document loaded
        </h2>
        <p style="color:#64748b;font-size:.9rem;margin:0;">
            Upload a file above, paste text, or choose a sample from the sidebar to get started.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ========== FOOTER ==========
st.markdown("""
<div class="app-footer">
    🚀 <span>Adaptive Note Summarizer</span> &nbsp;·&nbsp; Powered by Google Gemini
    &nbsp;·&nbsp; OCR · RAG · Smart Chunking
</div>
""", unsafe_allow_html=True)