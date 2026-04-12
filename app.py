# ============================================
# SUPPRESS WARNINGS & LOAD ENV VARIABLES
# ============================================
import warnings
warnings.filterwarnings("ignore", message=r"Accessing __path__ from .*")

import os
import logging


# CRITICAL: Filter warnings BEFORE importing transformers
warnings.filterwarnings('ignore', message='.*__path__.*')
warnings.filterwarnings('ignore', message='.*unauthenticated requests.*')
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=PendingDeprecationWarning)

# Suppress library logging
import logging
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("PIL").setLevel(logging.ERROR)

# Optional: Suppress Streamlit logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '0'

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# ============================================
# AUTHENTICATE WITH HUGGING FACE
# ============================================
from huggingface_hub import login

hf_token = os.getenv("HF_TOKEN")
if hf_token:
    try:
        login(token=hf_token, add_to_git_credential=False)
        print("✅ Hugging Face authenticated successfully")
    except Exception as e:
        print(f"⚠️  HF authentication warning: {e}")
else:
    print("⚠️  HF_TOKEN not found in .env file")

# ============================================
# NOW IMPORT STREAMLIT AND OTHER LIBRARIES
# ============================================
import streamlit as st
from ingestion.loader import load_pdfs_from_directory
from processing.chunker import chunk_documents
from embeddings.embedder import Embedder
from vectorstore.faiss_store import FAISSVectorStore
from llm import get_llm
from reranker.reranker import Reranker
from retriever.bm25_retriever import BM25Retriever

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Company Policy Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# CUSTOM CSS
# =========================
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    #MainMenu, footer, header { visibility: hidden; }

    .stApp { background: #0f1117; }

    [data-testid="stSidebar"] {
        background: #161b27;
        border-right: 1px solid #1e2535;
    }
    [data-testid="stSidebar"] * { color: #c9d1e0 !important; }

    .app-header {
        background: linear-gradient(135deg, #1a2235 0%, #0f1117 60%, #1a1f2e 100%);
        border: 1px solid #1e2d4a;
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
    }
    .app-header::before {
        content: '';
        position: absolute;
        top: -40px; right: -40px;
        width: 180px; height: 180px;
        background: radial-gradient(circle, rgba(56,139,255,0.12) 0%, transparent 70%);
        border-radius: 50%;
    }
    .app-header h1 { color: #e8edf5; font-size: 1.8rem; font-weight: 600; margin: 0 0 6px 0; letter-spacing: -0.3px; }
    .app-header p  { color: #6b7a99; font-size: 0.9rem; margin: 0; }
    .badge {
        display: inline-block;
        background: rgba(56,139,255,0.15);
        border: 1px solid rgba(56,139,255,0.3);
        color: #5b9cf6;
        font-size: 0.72rem; font-weight: 500;
        padding: 3px 10px; border-radius: 20px;
        margin-right: 6px; letter-spacing: 0.4px;
        text-transform: uppercase;
    }

    .msg-row        { display: flex; gap: 14px; align-items: flex-start; margin-bottom: 18px; }
    .msg-row.user   { flex-direction: row-reverse; }
    .avatar         { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0; }
    .avatar.bot     { background: #1e2d4a; border: 1px solid #2a3d5e; }
    .avatar.user    { background: #1a2e1a; border: 1px solid #2a4a2a; }
    .bubble         { max-width: 78%; padding: 14px 18px; border-radius: 14px; font-size: 0.9rem; line-height: 1.65; color: #dce3f0; }
    .bubble.bot     { background: #161b27; border: 1px solid #1e2535; border-top-left-radius: 4px; }
    .bubble.user    { background: #1a2e3d; border: 1px solid #1e3a52; border-top-right-radius: 4px; text-align: right; }

    .sources-card   { margin-top: 10px; background: #0d1520; border: 1px solid #1e2535; border-radius: 10px; padding: 10px 14px; font-size: 0.78rem; color: #5b7aaa; font-family: 'DM Mono', monospace; }
    .sources-card .src-title { color: #3d6494; font-weight: 500; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.6px; font-size: 0.72rem; }
    .sources-card .src-item  { color: #4a6a96; margin: 2px 0; }

    .context-box    { background: #0a0f1a; border: 1px dashed #1e2535; border-radius: 8px; padding: 12px 16px; font-family: 'DM Mono', monospace; font-size: 0.76rem; color: #3d5278; line-height: 1.6; white-space: pre-wrap; margin-top: 8px; }

    .stTextInput > div > div > input {
        background: #161b27 !important; border: 1px solid #1e2d4a !important;
        border-radius: 10px !important; color: #dce3f0 !important;
        font-family: 'DM Sans', sans-serif !important;
        padding: 14px 18px !important; font-size: 0.92rem !important;
    }
    .stTextInput > div > div > input:focus { border-color: #3a6abf !important; box-shadow: 0 0 0 3px rgba(58,106,191,0.12) !important; }
    .stTextInput > div > div > input::placeholder { color: #3d4d68 !important; }

    .stButton > button { background: #1e3a6e; border: 1px solid #2a5499; color: #89b4f7; border-radius: 10px; font-family: 'DM Sans', sans-serif; font-weight: 500; font-size: 0.88rem; padding: 10px 22px; transition: all 0.2s; }
    .stButton > button:hover { background: #254880; border-color: #3a6abf; color: #aac8ff; }

    .guard-msg { background: #1a1500; border: 1px solid #3d3000; border-left: 3px solid #c8960a; border-radius: 8px; padding: 12px 16px; color: #b8860a; font-size: 0.88rem; margin: 4px 0; }
    .empty-msg { background: #1a1520; border: 1px solid #2a1e40; border-left: 3px solid #7a4abf; border-radius: 8px; padding: 12px 16px; color: #8a6abf; font-size: 0.88rem; }

    .stat-card  { background: #0f1520; border: 1px solid #1e2535; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px; text-align: center; }
    .stat-num   { font-size: 1.5rem; font-weight: 600; color: #5b9cf6; }
    .stat-lbl   { font-size: 0.75rem; color: #4a5a78; margin-top: 2px; }

    hr { border-color: #1e2535 !important; }

    .welcome-state       { text-align: center; padding: 60px 20px; color: #3d4d68; }
    .welcome-state .icon { font-size: 3rem; margin-bottom: 16px; }
    .welcome-state h3    { color: #4a5a78; font-weight: 500; margin-bottom: 8px; }
    .welcome-state p     { font-size: 0.88rem; line-height: 1.7; }
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# PIPELINE HELPERS
# =========================
def classify_query(query, llm):
    prompt = f"""
Classify the query into:
1. casual
2. policy
3. unknown

Query: {query}
Answer (one word):
"""
    result = llm.generate_raw(prompt).lower()
    if "casual" in result:
        return "casual"
    elif "policy" in result:
        return "policy"
    return "unknown"


def rewrite_query(query, llm):
    prompt = f"""
Rewrite the query using company policy terminology.

Example:
commission → allowance
salary → compensation

Query: {query}
Rewritten:
"""
    return llm.generate_raw(prompt)


@st.cache_resource(show_spinner=False)
def init_pipeline(provider):
    policy_docs = load_pdfs_from_directory(
        "data/policy", source_name="company_policy", domain="policy"
    )
    chunked_docs = chunk_documents(policy_docs)
    texts = [d["text"] for d in chunked_docs]
    metadatas = [d["metadata"] for d in chunked_docs]
    embedder = Embedder()
    embeddings = embedder.embed_texts(texts)
    dimension = len(embeddings[0])
    vs = FAISSVectorStore(dimension)
    vs.add_embeddings(embeddings, texts, metadatas)
    bm25 = BM25Retriever(texts)  # ✅ initialize here
    llm = get_llm(provider)
    return embedder, vs, llm, Reranker(), bm25, len(texts)


def run_rag(query, embedder, vector_store, llm, reranker, bm25):
    q_type = classify_query(query, llm)

    if q_type == "casual":
        return llm.generate(query, casual=True), [], "", "casual"

    rewritten_query = rewrite_query(query, llm)
    qe = embedder.embed_query(rewritten_query)
    # results = vector_store.search(qe, k=20, threshold=0.45)
    dense_results = vector_store.search(qe, k=20, threshold=0.45)
    sparse_results = bm25.search(query, k=15)
    sparse_results_formatted = [
        {
            "text": r["text"],
            "score": r["score"],
            "metadata": {"file_name": "unknown", "page": "N/A", "doc_type": "unknown"},
        }
        for r in sparse_results
    ]
    # Merge + deduplicate
    combined = dense_results + sparse_results_formatted
    if not combined:
        return llm.generate(query, fallback=True), [], "", "empty"

    docs = [{"text": r["text"], "metadata": r["metadata"]} for r in combined]
    reranked = reranker.rerank(query, docs, top_k=5)
    context = "\n\n".join([r["text"] for r in reranked])
    answer = llm.generate(query, context)

    sources, seen = [], set()
    if "i don't know" not in answer.lower():
        for r in reranked:
            src = f"{r['metadata']['file_name']} — Page {r['metadata']['page']}"
            if src not in seen:
                sources.append(src)
                seen.add(src)

    return answer, sources, context[:800], "ok"


# =========================
# SESSION STATE INIT
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pipeline_ready" not in st.session_state:
    st.session_state.pipeline_ready = False
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None
if "pipeline_objects" not in st.session_state:
    st.session_state.pipeline_objects = None

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("### 🏢 Policy Assistant")
    st.markdown("---")
    st.markdown("### 🤖 LLM Provider")
    selected_llm = st.selectbox(
        "Choose model",
        ["groq", "openai"],
        index=0
    )
    if st.button("🔄 Reset Pipeline"):
        st.cache_resource.clear()
        st.session_state.pipeline_ready = False
        st.session_state.pipeline_objects = None
        st.rerun()

    if not st.session_state.pipeline_ready:
        if st.button("⚡ Load Pipeline", key="load_pipeline", use_container_width=True):
            with st.spinner("Indexing documents…"):
                st.session_state.pipeline_objects = init_pipeline(selected_llm)
                st.session_state.selected_llm = selected_llm
                st.session_state.pipeline_ready = True
                st.session_state.chunk_count = st.session_state.pipeline_objects[5]
            st.rerun()
    else:
        st.success("Pipeline ready", icon="✅")
        st.info(f"Using LLM: {st.session_state.selected_llm.upper()}")
        st.markdown(
            f'<div class="stat-card"><div class="stat-num">{st.session_state.get("chunk_count","—")}</div>'
            f'<div class="stat-lbl">Indexed Chunks</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="stat-card"><div class="stat-num">{len(st.session_state.messages)}</div>'
            f'<div class="stat-lbl">Messages</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("**Documents indexed**")
    for idx, d in enumerate(
        ["📄 communication.pdf", "📄 employment_contract.pdf", "📄 leave_policy.pdf"]
    ):
        st.markdown(f"<small style='color:#4a5a78'>{d}</small>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Try asking:**")
    suggestions = [
        "How many leave days do I get?",
        "What is the resignation notice period?",
        "What is the communication allowance?",
    ]
    for s in suggestions:
        if st.button(s, key=f"sug_{s}", use_container_width=True):
            st.session_state.pending_query = s

    st.markdown("---")
    if st.button("🗑 Clear Chat", key="clear_chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_query = None

# =========================
# CHAT HISTORY + INPUT
# =========================
st.markdown("<br>", unsafe_allow_html=True)


def submit_query():
    query = st.session_state.chat_input.strip()
    if query:
        st.session_state.pending_query = query
        st.session_state.chat_input = ""


col1, col2 = st.columns([6, 1])
with col1:
    st.text_input(
        "question",
        value="",
        placeholder="Ask about company policy...",
        label_visibility="collapsed",
        key="chat_input",
        on_change=submit_query,
    )
with col2:
    st.button("Send ➤", key="send_btn", use_container_width=True, on_click=submit_query)


# =========================
# PROCESS QUERY
# =========================
import re


def truncate_context(context, max_chars=600):
    """Truncate context intelligently at sentence boundaries."""
    if not context:
        return ""
    if len(context) <= max_chars:
        return context
    sentences = re.split(r"(?<=[.!?]) +", context)
    truncated = ""
    for s in sentences:
        if len(truncated) + len(s) > max_chars:
            break
        truncated += s + " "
    return truncated.strip()


if st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None

    if not st.session_state.pipeline_ready:
        st.warning("Please load the pipeline first using the sidebar button.")
    else:
        # Append user message
        st.session_state.messages.append({"role": "user", "content": query})

        # Retrieve pipeline objects
        embedder, vector_store, llm, reranker, bm25, _ = (
            st.session_state.pipeline_objects
        )

        with st.spinner("Thinking…"):
            answer, sources, context_full, status = run_rag(
                query, embedder, vector_store, llm, reranker, bm25
            )
            context_preview = truncate_context(context_full, 600)

        # Define small-talk triggers
        small_talk_triggers = [
            "hi",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
            "how are you",
            "how's your day",
            "goodbye",
            "bye",
        ]

        # Determine response text
        if status in ["guard", "empty"]:
            response_text = llm.generate(query, fallback=True)
        elif status == "casual":
            if any(trigger in query.lower() for trigger in small_talk_triggers):
                # Friendly small-talk
                response_text = llm.generate(query, casual=True)
            else:
                # General casual question outside company policy
                response_text = (
                    "As a Company Policy Assistant, I must inform you that your question "
                    "is not included in the company policy. "
                    "However, here is a general answer:\n\n"
                    + llm.generate(query, casual=True)
                )
        else:
            # Policy-related answer
            response_text = answer

        # Append assistant message
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response_text,
                "sources": sources,
                "context": context_preview,
                "status": status,
            }
        )


# =========================
# DISPLAY CHAT
# =========================
for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "bot"
    bubble_class = "bubble user" if msg["role"] == "user" else "bubble bot"

    st.markdown(
        f"""
        <div class="msg-row {role_class}">
            <div class="avatar {role_class}">{msg['role'][0].upper()}</div>
            <div class="{bubble_class}">{msg['content']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Only show context for policy-related answers
    if msg["role"] == "assistant" and msg.get("context") and msg.get("status") == "ok":
        st.markdown(
            f"""
            <div class="context-box">
                <strong>Context:</strong><br>
                {msg['context']}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Optionally show sources
    if msg["role"] == "assistant" and msg.get("sources"):
        st.markdown(
            "<div class='sources-card'>"
            + "<strong>Sources:</strong><br>"
            + "<br>".join(msg["sources"])
            + "</div>",
            unsafe_allow_html=True,
        )
