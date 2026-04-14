# ============================================
# SUPPRESS WARNINGS & LOAD ENV VARIABLES
# ============================================
import pickle
import re
from retriever.bm25_retriever import BM25Retriever
from reranker.reranker import Reranker
from llm import get_llm
from vectorstore.faiss_store import FAISSVectorStore
from embeddings.embedder import Embedder
from processing.chunker import chunk_documents
from ingestion.loader import load_pdfs_from_directory
import streamlit as st
import streamlit.components.v1 as components
from huggingface_hub import login
from dotenv import load_dotenv
import logging
import os
import warnings
from datetime import datetime

warnings.filterwarnings("ignore", message=r"Accessing __path__ from .*")

INDEX_PATH = "vector_store/faiss_index"
DOCSTORE_PATH = "vector_store/docstore.pkl"

warnings.filterwarnings("ignore", message=".*__path__.*")
warnings.filterwarnings("ignore", message=".*unauthenticated requests.*")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("PIL").setLevel(logging.ERROR)

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "0"

load_dotenv()

# ============================================
# AUTHENTICATE WITH HUGGING FACE
# ============================================
hf_token = os.getenv("HF_API_KEY")
if hf_token:
    try:
        login(token=hf_token, add_to_git_credential=False)
        print("✅ Hugging Face authenticated successfully")
    except Exception as e:
        print(f"⚠️  HF authentication warning: {e}")
else:
    print("⚠️  HF_TOKEN not found in .env file")

# =========================
# PAGE CONFIG  (must be first Streamlit call)
# =========================
st.set_page_config(
    page_title="Company Policy Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Company Policy Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================
# CUSTOM CSS (keep your existing CSS)
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── App background ── */
.stApp {
    background: #0d1117 !important;
    color: #e6edf3;
}

/* ── MAIN CONTENT AREA ── */
[data-testid="stAppViewContainer"] {
    background: #0d1117 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #30363d;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    color: #c9d1d9 !important;
    border-radius: 8px !important;
    transition: background 0.15s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #30363d !important;
}

/* ── SELECTBOX / DROPDOWN STYLING ── */
[data-testid="stSidebar"] [data-testid="stSelectbox"] {
    background: #21262d !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] [role="button"],
[data-testid="stSidebar"] [data-testid="stSelectbox"] div {
    background: #21262d !important;
    border-color: #30363d !important;
    color: #c9d1d9 !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] input {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    color: #c9d1d9 !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {
    color: #c9d1d9 !important;
}

/* ── CHAT INPUT CONTAINER ── */
[data-testid="stChatInputContainer"] {
    background: #161b22 !important;
    border-top: 1px solid #30363d !important;
    padding: 12px 16px !important;
}

/* ── Chat input wrapper ── */
[data-testid="stChatInputContainer"] > div {
    background: #161b22 !important;
}

/* ── Chat input field (textarea) ── */
[data-testid="stChatInputContainer"] textarea {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
    color: #e6edf3 !important;
    font-size: 0.95rem !important;
    padding: 10px 14px !important;
    caret-color: #e6edf3 !important;
    min-height: 44px !important;
    max-height: 120px !important;
}

[data-testid="stChatInputContainer"] textarea::placeholder {
    color: #8b949e !important;
    opacity: 1 !important;
}

[data-testid="stChatInputContainer"] textarea:focus {
    border-color: #388bfd !important;
    box-shadow: 0 0 0 2px rgba(56,139,253,0.15) !important;
    background: #21262d !important;
    outline: none !important;
}

/* ── Chat input button ── */
[data-testid="stChatInputContainer"] button {
    background: #1f6feb !important;
    border-radius: 8px !important;
    border: none !important;
    color: white !important;
    height: 44px !important;
}

[data-testid="stChatInputContainer"] button:hover {
    background: #388bfd !important;
}

[data-testid="stChatInputContainer"] button:active {
    background: #1f6feb !important;
}

/* ── Native chat messages styling ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.25rem 0 !important;
}

/* User bubble */
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stMarkdownContainer"] p,
.stChatMessage:has([aria-label="user avatar"]) [data-testid="stMarkdownContainer"] p {
    background: #1c2d3a;
    border: 1px solid #264f6b;
    border-radius: 14px 14px 4px 14px;
    padding: 10px 14px;
    display: inline-block;
    max-width: 80%;
    float: right;
}

/* ── Source / context expanders ── */
.stExpander {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    margin-top: 4px;
}
.stExpander summary { color: #8b949e !important; font-size: 0.8rem; }
.stExpander [data-testid="stMarkdownContainer"] {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #8b949e;
}

/* ── Welcome card ── */
.welcome-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 24px 28px;
    margin: 40px auto;
    max-width: 560px;
    text-align: center;
}
.welcome-card h2 { color: #e6edf3; font-size: 1.3rem; margin-bottom: 6px; }
.welcome-card p  { color: #8b949e; font-size: 0.9rem; margin: 0; }

/* ── Stat pill ── */
.stat-pill {
    display: inline-block;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.78rem;
    color: #8b949e;
    margin: 2px;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }

/* ── ADDITIONAL FIXES FOR STREAMLIT COMPONENTS ── */
[data-testid="stMainBlockContainer"] {
    background: #0d1117 !important;
    color: #e6edf3 !important;
}

.stMarkdown {
    color: #e6edf3 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# PIPELINE HELPERS
# ============================================
PIPELINE_INDEX_FILE = "vector_store/faiss.index"
PIPELINE_DOCSTORE_FILE = "vector_store/docstore.pkl"
PIPELINE_MANIFEST = "vector_store/manifest.json"


def compute_data_fingerprint(root_dir: str):
    import hashlib

    h = hashlib.sha1()
    if not os.path.exists(root_dir):
        return None
    for dirpath, _, filenames in os.walk(root_dir):
        for fn in sorted(filenames):
            fp = os.path.join(dirpath, fn)
            try:
                s = os.stat(fp)
            except OSError:
                continue
            h.update(fp.replace("\\", "/").encode())
            h.update(str(s.st_size).encode())
            h.update(str(int(s.st_mtime)).encode())
    return h.hexdigest()


def save_pipeline(vs, texts, bm25, chunk_count, data_fingerprint: str):
    import json

    os.makedirs("vector_store", exist_ok=True)
    vs.save(PIPELINE_INDEX_FILE, PIPELINE_DOCSTORE_FILE)
    manifest = {
        "fingerprint": data_fingerprint,
        "chunk_count": chunk_count,
        "index_file": PIPELINE_INDEX_FILE,
        "docstore_file": PIPELINE_DOCSTORE_FILE,
    }
    with open(PIPELINE_MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f)


def load_pipeline(data_root="data/policy"):
    import json

    if not os.path.exists(PIPELINE_MANIFEST):
        return None
    with open(PIPELINE_MANIFEST, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    current_fp = compute_data_fingerprint(data_root)
    if manifest.get("fingerprint") != current_fp:
        return None
    if not os.path.exists(manifest.get("index_file", "")) or not os.path.exists(
        manifest.get("docstore_file", "")
    ):
        return None
    vs = FAISSVectorStore.load(manifest["index_file"], manifest["docstore_file"])
    texts = vs.texts
    bm25 = BM25Retriever(texts)
    return {
        "vector_store": vs,
        "bm25": bm25,
        "chunk_count": manifest.get("chunk_count", len(texts)),
    }


@st.cache_resource(show_spinner=False)
def init_pipeline(provider):
    saved = load_pipeline("data/policy")
    if saved:
        print("✅ Loaded pipeline from disk")
        embedder = Embedder()
        vs = saved["vector_store"]
        bm25 = saved["bm25"]
        chunk_count = saved["chunk_count"]
        llm = get_llm(provider)
        return embedder, vs, llm, Reranker(), bm25, chunk_count

    print("⚡ Building pipeline from scratch...")
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
    bm25 = BM25Retriever(texts)
    fp = compute_data_fingerprint("data/policy")
    save_pipeline(vs, texts, bm25, len(texts), fp)
    llm = get_llm(provider)
    return embedder, vs, llm, Reranker(), bm25, len(texts)


def classify_query(query, llm):
    query_lower = (query or "").lower().strip()

    identity_phrases = [
        "who are you",
        "what are you",
        "your name",
        "tell me about yourself",
    ]

    policy_keywords = [
        "policy",
        "leave",
        "employment",
        "contract",
        "resign",
        "resignation",
        "notice period",
        "salary",
        "compensation",
        "commission",
        "allowance",
        "communication",
        "wallet",
        "slab",
        "withdrawal",
        "year 1",
        "year 2",
        "year 3",
    ]

    casual_triggers = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "how are you",
        "how's your day",
        "have a good day",
        "bye",
        "goodbye",
        "thanks",
        "thank you",
    ]

    if any(p in query_lower for p in identity_phrases):
        return "identity"

    # policy should win before casual
    if any(k in query_lower for k in policy_keywords):
        return "policy"

    # keep casual only for pure greetings/small talk
    if any(
        t == query_lower or query_lower.startswith(t + " ") for t in casual_triggers
    ):
        return "casual"

    # IMPORTANT: do NOT map "what is/how does" to casual
    # let LLM classify unknowns
    prompt = f"""Classify the query into: casual, policy, or unknown.
Query: {query}
Answer (one word):"""
    try:
        result = (llm.generate_raw(prompt) or "").lower().strip()
    except Exception:
        return "unknown"

    if "policy" in result:
        return "policy"
    if "casual" in result:
        return "casual"
    return "unknown"


def rewrite_query(query, llm):
    prompt = f"""Rewrite the query using company policy terminology.\nExample: commission → allowance, salary → compensation\nQuery: {query}\nRewritten:"""
    return llm.generate_raw(prompt)


def truncate_context(context, max_chars=600):
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


def run_rag(query, embedder, vector_store, llm, reranker, bm25):
    msgs = st.session_state.get("messages", [])
    recent = msgs[-8:] if msgs else []
    conversation_text = "\n".join(
        [f"{m['role'].capitalize()}: {m['content']}" for m in recent]
    )

    q_type = classify_query(query, llm)
    if q_type in ("policy", "unknown"):
        pass  # continue with retrieval
    if q_type == "identity":
        return (
            "I'm the **Wamo Labs Company Policy Assistant** 🏢\n\n"
            "I help you understand company policies, benefits, and guidelines. Feel free to ask me anything!",
            [],
            "",
            "identity",
        )

    if q_type == "casual":
        answer = llm.generate(query, context=conversation_text, casual=True) or ""
        return answer, [], "", "casual"

    rewritten_query = rewrite_query(query, llm)
    qe = embedder.embed_query(rewritten_query)
    dense_results = vector_store.search(qe, k=20, threshold=0.2)
    sparse_results = bm25.search(query, k=15)
    sparse_results_formatted = [
        {
            "text": r["text"],
            "score": r["score"],
            "metadata": {"file_name": "unknown", "page": "N/A", "doc_type": "unknown"},
        }
        for r in sparse_results
    ]
    combined = dense_results + sparse_results_formatted

    if not combined:
        answer = llm.generate(query, context=conversation_text, fallback=True) or ""
        return answer, [], "", "empty"

    docs = [{"text": r["text"], "metadata": r["metadata"]} for r in combined]
    reranked = reranker.rerank(query, docs, top_k=5)
    context = "\n\n".join([r["text"] for r in reranked])
    full_context = (conversation_text + "\n\n" + context).strip()
    answer = llm.generate(query, full_context)

    if answer is None:
        answer = ""
    if not isinstance(answer, str):
        answer = str(answer)

    sources, seen = [], set()
    if "i don't know" not in answer.lower():
        for r in reranked:
            src = f"{r['metadata']['file_name']} — Page {r['metadata']['page']}"
            if src not in seen:
                sources.append(src)
                seen.add(src)

    return answer, sources, context[:800], "ok"


# ============================================
# SESSION STATE
# ============================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pipeline_ready" not in st.session_state:
    st.session_state.pipeline_ready = False
if "pipeline_objects" not in st.session_state:
    st.session_state.pipeline_objects = None
if "selected_llm" not in st.session_state:
    st.session_state.selected_llm = "groq"

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("## 🏢 Policy Assistant")
    st.markdown("---")

    st.markdown("### 🤖 Model")
    selected_llm = st.selectbox(
        "LLM Provider", ["groq", "gemini"], index=0, label_visibility="collapsed"
    )

    st.markdown("---")

    import shutil

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 Reset", use_container_width=True):
            st.cache_resource.clear()
            if os.path.exists("vector_store"):
                shutil.rmtree("vector_store")
            st.session_state.pipeline_ready = False
            st.session_state.pipeline_objects = None
            st.rerun()
    with col_b:
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")

    if not st.session_state.pipeline_ready:
        if st.button("⚡ Load Pipeline", use_container_width=True, type="primary"):
            with st.spinner("Indexing documents…"):
                st.session_state.pipeline_objects = init_pipeline(selected_llm)
                st.session_state.selected_llm = selected_llm
                st.session_state.pipeline_ready = True
                st.session_state.chunk_count = st.session_state.pipeline_objects[5]
            st.rerun()
    else:
        st.success("Pipeline ready ✅")
        st.markdown(
            f'<span class="stat-pill">🤖 {st.session_state.selected_llm.upper()}</span>'
            f'<span class="stat-pill">📦 {st.session_state.get("chunk_count","—")} chunks</span>'
            f'<span class="stat-pill">💬 {len(st.session_state.messages)} msgs</span>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("**📁 Indexed documents**")
    for doc in ["communication.pdf", "employment_contract.pdf", "leave_policy.pdf"]:
        st.markdown(
            f"<small style='color:#8b949e'>📄 {doc}</small>", unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("**💡 Try asking:**")
    suggestions = [
        "How many leave days do I get?",
        "What is the resignation notice period?",
        "What is the communication allowance?",
    ]
    for s in suggestions:
        if st.button(s, key=f"sug_{s}", use_container_width=True):
            # inject as a pending query via session state trick
            st.session_state["_suggestion"] = s
            st.rerun()


# ============================================
# MAIN CHAT AREA
# ============================================

# Show welcome screen when no messages yet
if not st.session_state.messages:
    st.markdown(
        """
    <div class="welcome-card">
        <h2>🏢 Company Policy Assistant</h2>
        <p>Ask me anything about company policies, leave, contracts, and benefits.<br>
        Load the pipeline from the sidebar to get started.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ── Render all past messages using native Streamlit chat UI ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Show context expander for policy answers
        if (
            msg["role"] == "assistant"
            and msg.get("context")
            and msg.get("status") == "ok"
        ):
            with st.expander("📄 Retrieved context", expanded=False):
                st.markdown(f"```\n{msg['context']}\n```")

        # Show sources
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander(f"🔗 Sources ({len(msg['sources'])})", expanded=False):
                for src in msg["sources"]:
                    st.markdown(f"- `{src}`")


# ── Handle suggestion button clicks ──
if "_suggestion" in st.session_state:
    query = st.session_state.pop("_suggestion")
    # Process it as if it came from the input box
    if not st.session_state.pipeline_ready:
        st.warning("⚠️ Please load the pipeline first from the sidebar.")
    else:
        with st.chat_message("user"):
            st.markdown(query)
        st.session_state.messages.append(
            {
                "role": "user",
                "content": query,
                "time": datetime.now().strftime("%H:%M"),
            }
        )
        embedder, vector_store, llm, reranker, bm25, _ = (
            st.session_state.pipeline_objects
        )
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                answer, sources, context_full, status = run_rag(
                    query, embedder, vector_store, llm, reranker, bm25
                )
                context_preview = truncate_context(context_full, 600)
            st.markdown(answer)
            if context_preview and status == "ok":
                with st.expander("📄 Retrieved context", expanded=False):
                    st.markdown(f"```\n{context_preview}\n```")
            if sources:
                with st.expander(f"🔗 Sources ({len(sources)})", expanded=False):
                    for src in sources:
                        st.markdown(f"- `{src}`")
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "context": context_preview,
                "status": status,
                "time": datetime.now().strftime("%H:%M"),
            }
        )


# ── Native bottom-pinned chat input ──
# st.chat_input() is ALWAYS rendered at the bottom of the page by Streamlit
query = st.chat_input(
    "Ask about company policy…",
    disabled=not st.session_state.pipeline_ready,
)

if query:
    if not st.session_state.pipeline_ready:
        st.warning("⚠️ Please load the pipeline first from the sidebar.")
    else:
        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(query)
        st.session_state.messages.append(
            {
                "role": "user",
                "content": query,
                "time": datetime.now().strftime("%H:%M"),
            }
        )

        # Run RAG and stream assistant response
        embedder, vector_store, llm, reranker, bm25, _ = (
            st.session_state.pipeline_objects
        )
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                answer, sources, context_full, status = run_rag(
                    query, embedder, vector_store, llm, reranker, bm25
                )
                context_preview = truncate_context(context_full, 600)
            st.markdown(answer)
            if context_preview and status == "ok":
                with st.expander("📄 Retrieved context", expanded=False):
                    st.markdown(f"```\n{context_preview}\n```")
            if sources:
                with st.expander(f"🔗 Sources ({len(sources)})", expanded=False):
                    for src in sources:
                        st.markdown(f"- `{src}`")

        # Save to session state
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "context": context_preview,
                "status": status,
                "time": datetime.now().strftime("%H:%M"),
            }
        )
