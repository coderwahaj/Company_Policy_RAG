from ingestion.loader import load_pdfs_from_directory
from processing.chunker import chunk_documents
from embeddings.embedder import Embedder
from vectorstore.faiss_store import FAISSVectorStore
from llm.groq_llm import GroqLLM
from reranker.reranker import Reranker


# =========================
# LOAD DATA
# =========================
policy_docs = load_pdfs_from_directory(
    "data/policy",
    source_name="company_policy",
    domain="policy"
)

all_docs = policy_docs

# =========================
# CHUNKING
# =========================
chunked_docs = chunk_documents(all_docs)

texts = [doc["text"] for doc in chunked_docs]
metadatas = [doc["metadata"] for doc in chunked_docs]

print(f"📄 Total chunks created: {len(texts)}")

# =========================
# EMBEDDINGS
# =========================
embedder = Embedder()
embeddings = embedder.embed_texts(texts)

print("✅ Embeddings created")

# =========================
# VECTOR STORE
# =========================
dimension = len(embeddings[0])
vector_store = FAISSVectorStore(dimension)
vector_store.add_embeddings(embeddings, texts, metadatas)

print("✅ Stored in FAISS")

# =========================
# LLM + RERANKER
# =========================
llm = GroqLLM()
reranker = Reranker()


# =========================
# QUERY CLASSIFIER
# =========================
def is_relevant_query(query):
    q = query.lower()

    keywords = [
        "leave", "policy", "employee", "contract",
        "resign", "salary", "allowance", "communication",
        "employment", "company"
    ]

    return any(word in q for word in keywords)


# =========================
# DOC TYPE DETECTION
# =========================
def detect_doc_type(query):
    q = query.lower()

    if "leave" in q:
        return "leave_policy"
    elif "contract" in q or "employment" in q:
        return "employment_contract"
    elif "communication" in q or "allowance" in q:
        return "communication"

    return None


# =========================
# PRIORITY ORDER
# =========================
PRIORITY = {
    "leave_policy": 1,
    "employment_contract": 2,
    "communication": 3
}


# =========================
# CLI LOOP
# =========================
print("\n Company Policy Assistant Ready!")
print("Type your question (type 'exit' to quit)\n")

while True:
    query = input("🧑 You: ")

    if query.lower() == "exit":
        print("👋 Exiting... Goodbye!")
        break

    if not query.strip():
        print("⚠️ Please enter a valid question.\n")
        continue

    # =========================
    # QUERY FILTER (🔥 NEW)
    # =========================
    if not is_relevant_query(query):
        print("\n🔥 Assistant:\n")
        print("I can only answer questions related to company policies and employment documents.")
        print("\n" + "=" * 60 + "\n")
        continue

    # =========================
    # RETRIEVAL
    # =========================
    query_embedding = embedder.embed_query(query)

    initial_results = vector_store.search(query_embedding, k=15, threshold=1.5)

    # =========================
    # FILTER BY DOC TYPE
    # =========================
    doc_type_filter = detect_doc_type(query)

    if doc_type_filter:
        initial_results = [
            r for r in initial_results
            if r["metadata"]["doc_type"] == doc_type_filter
        ]

    if not initial_results:
        print("\n🔥 Assistant:\n")
        print("I don't know.")
        print("\n" + "=" * 60 + "\n")
        continue

    # =========================
    # RERANK
    # =========================
    docs_for_rerank = [
        {"text": r["text"], "metadata": r["metadata"]}
        for r in initial_results
    ]

    reranked_results = reranker.rerank(query, docs_for_rerank, top_k=5)

    # =========================
    # PRIORITY SORT
    # =========================
    reranked_results = sorted(
        reranked_results,
        key=lambda x: PRIORITY.get(x["metadata"]["doc_type"], 99)
    )

    # =========================
    # CONTEXT
    # =========================
    context = "\n\n".join(
        [f"{r['metadata']['doc_type']}:\n{r['text']}" for r in reranked_results]
    )

    print("\n🔍 Retrieved Context (Preview):\n")
    print(context[:500])

    # =========================
    # GENERATE ANSWER
    # =========================
    answer = llm.generate(query, context)

    print("\n🔥 Assistant:\n")
    print(answer)

    # =========================
    # SHOW SOURCES (🔥 CLEAN)
    # =========================
    if "i don't know" not in answer.lower():
        print("\n📚 Sources:")

        unique_sources = set()
        for r in reranked_results:
            src = f"{r['metadata']['file_name']} (Page {r['metadata']['page']})"
            if src not in unique_sources:
                print(f"- {src}")
                unique_sources.add(src)

    print("\n" + "=" * 60 + "\n")