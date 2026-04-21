from backend.app.core.pipeline import get_pipeline
from backend.app.core.rag_service import run_rag, truncate_context
import streamlit as st
from huggingface_hub import login
from dotenv import load_dotenv
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("PIL").setLevel(logging.ERROR)

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "0"

load_dotenv()

hf_token = os.getenv("HF_API_KEY")
if hf_token:
    try:
        login(token=hf_token, add_to_git_credential=False)
        logger.info("Hugging Face authenticated successfully")
    except Exception as e:
        logger.warning("HF authentication warning: %s", e)
else:
    logger.warning("HF_TOKEN not found in .env file")

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


load_css("styles.css")


@st.cache_resource(show_spinner=False)
def init_pipeline(provider):
    return get_pipeline(provider)


# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pipeline_ready" not in st.session_state:
    st.session_state.pipeline_ready = False
if "pipeline_objects" not in st.session_state:
    st.session_state.pipeline_objects = None
if "selected_llm" not in st.session_state:
    st.session_state.selected_llm = "groq"

# Sidebar
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
            st.session_state["_suggestion"] = s
            st.rerun()

# Main chat area
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

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if (
            msg["role"] == "assistant"
            and msg.get("context")
            and msg.get("status") == "ok"
        ):
            with st.expander("📄 Retrieved context", expanded=False):
                st.markdown(f"```\n{msg['context']}\n```")

        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander(f"🔗 Sources ({len(msg['sources'])})", expanded=False):
                for src in msg["sources"]:
                    st.markdown(f"- `{src}`")

# Suggestion click handling
if "_suggestion" in st.session_state:
    query = st.session_state.pop("_suggestion")
    if not st.session_state.pipeline_ready:
        st.warning(" Please load the pipeline first from the sidebar.")
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
                    query,
                    embedder,
                    vector_store,
                    llm,
                    reranker,
                    bm25,
                    history=st.session_state.messages,
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

# Chat input
query = st.chat_input(
    "Ask about company policy…",
    disabled=not st.session_state.pipeline_ready,
)

if query:
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
                    query,
                    embedder,
                    vector_store,
                    llm,
                    reranker,
                    bm25,
                    history=st.session_state.messages,
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