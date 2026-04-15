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


def load_css(css_path: str):
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found: {css_path}")


# ============================================
# CUSTOM CSS (keep your existing CSS)
# =========================================
load_css("styles.css")


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
    """Classify query type with improved out-of-context detection."""
    query_lower = (query or "").lower().strip()

    identity_phrases = [
        "who are you",
        "what are you",
        "your name",
        "tell me about yourself",
        "who is this",
        "introduce yourself",
        "what is this",
    ]

    # policy_keywords = [
    #     "policy", "leave", "employment", "contract", "resign", "resignation",
    #     "notice period", "salary", "compensation", "commission", "allowance",
    #     "communication", "wallet", "slab", "withdrawal", "year 1", "year 2", "year 3",
    #     "benefits", "pf", "esi", "bonus", "incentive", "deduction", "payroll"
    # ]
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
        "benefits",
        "pf",
        "esi",
        "bonus",
        "incentive",
        "deduction",
        "wamo labs",
        "wamo",
        "company",
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
        "ok",
        "okay",
        "sure",
    ]

    # 🎯 IDENTITY CHECK FIRST
    if any(p in query_lower for p in identity_phrases):
        return "identity"

    # 🎯 POLICY CHECK - should win
    if any(k in query_lower for k in policy_keywords):
        return "policy"

    # 🎯 CASUAL CHECK - only exact matches or starts with
    if any(
        t == query_lower or query_lower.startswith(t + " ") for t in casual_triggers
    ):
        return "casual"

    # 🎯 UNKNOWN - Let LLM classify with strict instructions
    prompt = f"""Classify STRICTLY into: policy, casual, or unknown.
    
⚠️ RULE: If question is NOT about company policy (leave, contracts, salary, benefits, etc.), answer "unknown"
    
Examples:
- "What is Python?" → unknown
- "How many leave days?" → policy
- "Hi there" → casual
- "Tell me about machine learning" → unknown

Query: {query}
Answer (one word only):"""

    try:
        result = (llm.generate_raw(prompt) or "").lower().strip()
        if "policy" in result:
            return "policy"
        if "casual" in result:
            return "casual"
    except Exception:
        pass

    return "unknown"  # ✅ Default to unknown for safety


def is_generic_out_of_context(answer: str) -> bool:
    if not answer:
        return True
    answer_lower = answer.lower()
    generic_phrases = [
        "don't have information",
        "do not have information",
        "i don't have information",
        "i don't know",
        "out of context",
        "not in the company policy documents",
        "not available in the company policy documents",
    ]
    return any(p in answer_lower for p in generic_phrases)


def answer_from_context(query: str, context: str, llm):
    prompt = f"""You are a Wamo Labs Company Policy Assistant.
Use ONLY the retrieved policy text below to answer the user's question.
Do not refuse if the answer appears in the provided text.
Do not hallucinate or invent new information.

Question: {query}

Relevant policy text:
{context}

Answer directly from the retrieved policy text:"""
    return llm.generate_raw(prompt)


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

    # ✅ IDENTITY: Return confident identity response
    if q_type == "identity":
        return (
            "I'm the **Wamo Labs Company Policy Assistant** 🏢\n\n"
            "I help employees understand company policies, leave policies, employment contracts, compensation, and benefits. "
            "Feel free to ask me anything related to company policies and guidelines!",
            [],
            "",
            "identity",
        )

    # ✅ CASUAL: Only handle pure greetings
    if q_type == "casual":
        answer = llm.generate(query, context=conversation_text, casual=True) or ""
        return answer, [], "", "casual"

    # ✅ POLICY or UNKNOWN: Try retrieval
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
    docs = [{"text": r["text"], "metadata": r["metadata"]} for r in combined]
    reranked = reranker.rerank(query, docs, top_k=5)

    # ✅ NO CONTEXT FOUND: Return out-of-context response FIRST
    if not reranked:
        return (
            "I'm the **Wamo Labs Company Policy Assistant** 🏢\n\n"
            "I don't have information about that question in the company policy documents. "
            "I'm trained specifically to help with:\n"
            "- Leave policies\n"
            "- Employment contracts\n"
            "- Compensation & allowances\n"
            "- Communication guidelines\n\n"
            "Feel free to ask me anything related to company policies!",
            [],
            "",
            "out_of_context",
        )

    # ✅ CONTEXT FOUND: Use RAG with policy prompt
    context = "\n\n".join([r["text"] for r in reranked])
    full_context = (conversation_text + "\n\n" + context).strip()
    answer = llm.generate(query, full_context)

    if answer is None:
        answer = ""
    if not isinstance(answer, str):
        answer = str(answer)

    sources, seen = [], set()
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
        <h2>🏢Wamo Labs Policy Assistant</h2>
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
