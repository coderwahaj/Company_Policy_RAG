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
