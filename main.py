"""
main.py — CLI entrypoint for the Company Policy RAG Assistant.
Run: python main.py
"""
import numpy as np
from rag.processing.reranker import Reranker
from rag.llm import get_llm
from rag.vectorstore.faiss_store import FAISSVectorStore
from rag.embeddings.embedder import Embedder
from rag.processing.chunker import chunk_documents
from rag.ingestion.loader import load_pdfs_from_directory
import warnings
warnings.filterwarnings("ignore", message=r"Accessing __path__ from .*")


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


def build_pipeline(data_dir="data/policy"):
    """Create embedder, vector store, llm, reranker pipeline objects."""
    docs = load_pdfs_from_directory(
        data_dir, source_name="company_policy", domain="policy")
    if not docs:
        print(f"Warning: no PDFs found in {data_dir}")

    chunked = chunk_documents(docs)
    texts = [d["text"] for d in chunked]
    metadatas = [d["metadata"] for d in chunked]

    embedder = Embedder()
    embeddings = embedder.embed_texts(texts) if texts else []

    if embeddings:
        dimension = len(embeddings[0])
    else:
        # fallback dimension (SentenceTransformer default 768)
        dimension = 768

    vs = FAISSVectorStore(dimension)
    if embeddings:
        vs.add_embeddings(embeddings, texts, metadatas)

    llm = get_llm()
    reranker = Reranker()

    return embedder, vs, llm, reranker


def main():
    print("Initializing pipeline — this may take a minute...")
    embedder, vs, llm, reranker = build_pipeline()

    print("Pipeline ready. Enter a question (or 'exit' to quit):")
    try:
        while True:
            q = input("? ").strip()
            if not q:
                continue
            if q.lower() in ("exit", "quit"):
                break

            answer, sources, context, status = run_rag(
                q, embedder, vs, llm, reranker)
            print("\nAnswer:\n", answer)
            if sources:
                print("\nSources:")
                for s in sources:
                    print(" - ", s)
            print("\n---\n")
    except KeyboardInterrupt:
        print("\nExiting")


if __name__ == "__main__":
    main()
