# from ingestion.loader import load_pdfs_from_directory
# from processing.chunker import chunk_documents
# from embeddings.embedder import Embedder
# from vectorstore.faiss_store import FAISSVectorStore
# from llm.groq_llm import GroqLLM
# from reranker.reranker import Reranker


# # =========================
# # LOAD DATA
# # =========================
# policy_docs = load_pdfs_from_directory(
#     "data/policy",
#     source_name="company_policy",
#     domain="policy"
# )

# all_docs = policy_docs

# # =========================
# # CHUNKING
# # =========================
# chunked_docs = chunk_documents(all_docs)

# texts = [doc["text"] for doc in chunked_docs]
# metadatas = [doc["metadata"] for doc in chunked_docs]

# print(f"📄 Total chunks created: {len(texts)}")

# # =========================
# # EMBEDDINGS
# # =========================
# embedder = Embedder()
# embeddings = embedder.embed_texts(texts)

# print("✅ Embeddings created")

# # =========================
# # VECTOR STORE
# # =========================
# dimension = len(embeddings[0])
# vector_store = FAISSVectorStore(dimension)
# vector_store.add_embeddings(embeddings, texts, metadatas)

# print("✅ Stored in FAISS")

# # =========================
# # LLM + RERANKER
# # =========================
# llm = GroqLLM()
# reranker = Reranker()


# # =========================
# # QUERY CLASSIFIER
# # =========================
# def is_relevant_query(query):
#     q = query.lower()

#     keywords = [
#         "leave", "policy", "employee", "contract",
#         "resign", "salary", "allowance", "communication",
#         "employment", "company"
#     ]

#     return any(word in q for word in keywords)


# # =========================
# # DOC TYPE DETECTION
# # =========================
# def detect_doc_type(query):
#     q = query.lower()

#     if "leave" in q:
#         return "leave_policy"
#     elif "contract" in q or "employment" in q:
#         return "employment_contract"
#     elif "communication" in q or "allowance" in q:
#         return "communication"

#     return None


# # =========================
# # PRIORITY ORDER
# # =========================
# PRIORITY = {
#     "leave_policy": 1,
#     "employment_contract": 2,
#     "communication": 3
# }


# # =========================
# # CLI LOOP
# # =========================
# print("\n Company Policy Assistant Ready!")
# print("Type your question (type 'exit' to quit)\n")

# while True:
#     query = input("🧑 You: ")

#     if query.lower() == "exit":
#         print("👋 Exiting... Goodbye!")
#         break

#     if not query.strip():
#         print("⚠️ Please enter a valid question.\n")
#         continue

#     # =========================
#     # QUERY FILTER (🔥 NEW)
#     # =========================
#     if not is_relevant_query(query):
#         print("\n🔥 Assistant:\n")
#         print("I can only answer questions related to company policies and employment documents.")
#         print("\n" + "=" * 60 + "\n")
#         continue

#     # =========================
#     # RETRIEVAL
#     # =========================
#     query_embedding = embedder.embed_query(query)

#     initial_results = vector_store.search(query_embedding, k=15, threshold=1.5)

#     # =========================
#     # FILTER BY DOC TYPE
#     # =========================
#     doc_type_filter = detect_doc_type(query)

#     if doc_type_filter:
#         initial_results = [
#             r for r in initial_results
#             if r["metadata"]["doc_type"] == doc_type_filter
#         ]

#     if not initial_results:
#         print("\n🔥 Assistant:\n")
#         print("I don't know.")
#         print("\n" + "=" * 60 + "\n")
#         continue

#     # =========================
#     # RERANK
#     # =========================
#     docs_for_rerank = [
#         {"text": r["text"], "metadata": r["metadata"]}
#         for r in initial_results
#     ]

#     reranked_results = reranker.rerank(query, docs_for_rerank, top_k=5)

#     # =========================
#     # PRIORITY SORT
#     # =========================
#     reranked_results = sorted(
#         reranked_results,
#         key=lambda x: PRIORITY.get(x["metadata"]["doc_type"], 99)
#     )

#     # =========================
#     # CONTEXT
#     # =========================
#     context = "\n\n".join(
#         [f"{r['metadata']['doc_type']}:\n{r['text']}" for r in reranked_results]
#     )

#     print("\n🔍 Retrieved Context (Preview):\n")
#     print(context[:500])

#     # =========================
#     # GENERATE ANSWER
#     # =========================
#     answer = llm.generate(query, context)

#     print("\n🔥 Assistant:\n")
#     print(answer)

#     # =========================
#     # SHOW SOURCES (🔥 CLEAN)
#     # =========================
#     if "i don't know" not in answer.lower():
#         print("\n📚 Sources:")

#         unique_sources = set()
#         for r in reranked_results:
#             src = f"{r['metadata']['file_name']} (Page {r['metadata']['page']})"
#             if src not in unique_sources:
#                 print(f"- {src}")
#                 unique_sources.add(src)

#     print("\n" + "=" * 60 + "\n")

"""
main.py — CLI entrypoint for the Company Policy RAG Assistant.
Run: python main.py
"""

from ingestion.loader import load_pdfs_from_directory
from processing.chunker import chunk_documents
from embeddings.embedder import Embedder
from vectorstore.faiss_store import FAISSVectorStore
from llm.groq_llm import GroqLLM
from reranker.reranker import Reranker
import spacy
import numpy as np
# =========================
# NEW: QUERY CLASSIFIER
# =========================
def classify_query(query, llm):
    prompt = f"""
Classify the query into one of:
1. casual
2. policy
3. unknown

Query: {query}
Answer (one word only):
"""
    result = llm.generate_raw(prompt).lower()

    if "casual" in result:
        return "casual"
    elif "policy" in result:
        return "policy"
    else:
        return "unknown"


# =========================
# NEW: QUERY REWRITER
# =========================
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


# =========================
#  RAG FUNCTION
# =========================
def run_rag(query, embedder, vector_store, llm, reranker):
    # 1. Classify query
    q_type = classify_query(query, llm)

    # 2. Casual query → use casual mode
    if q_type == "casual":
        return llm.generate(query, casual=True), [], "", "casual"

    # 3. Rewrite query to policy terms
    rewritten_query = rewrite_query(query, llm)

    # 4. Retrieve relevant docs
    qe = embedder.embed_query(rewritten_query)
    results = vector_store.search(qe, k=20, threshold=0.45)

    # 5. No results → fallback
    if not results:
        return llm.generate(query, fallback=True), [], "", "fallback"

    # 6. Rerank top documents
    docs = [{"text": r["text"], "metadata": r["metadata"]} for r in results]
    reranked = reranker.rerank(query, docs, top_k=5)

    # 7. Build context for LLM
    context = "\n\n".join([r["text"] for r in reranked])

    # 8. Generate final answer
    answer = llm.generate(query, context=context)

    # 9. Collect sources
    sources, seen = [], set()
    if "i don't know" not in answer.lower():
        for r in reranked:
            src = f"{r['metadata']['file_name']} — Page {r['metadata']['page']}"
            if src not in seen:
                sources.append(src)
                seen.add(src)

    return answer, sources, context[:800], "ok"