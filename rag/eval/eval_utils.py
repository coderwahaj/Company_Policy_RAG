"""
eval_utils.py — Evaluation script for Company Policy RAG Assistant
Run: python eval_utils.py
"""

import sys, os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # for ingestion, processing etc
sys.path.insert(
    0, os.path.dirname(os.path.abspath(__file__))
)  # for dataset.py in eval/
# =========================
# IMPORTS
# =========================

from rag.ingestion.loader import load_pdfs_from_directory
from rag.processing.chunker import chunk_documents
from rag.embeddings.embedder import Embedder
from rag.vectorstore.faiss_store import FAISSVectorStore
from rag.llm import get_llm
from rag.reranker.reranker import Reranker
from main import run_rag
import os

# =========================
# EVALUATION FUNCTIONS
# =========================


def evaluate_retrieval(vector_store, embedder, dataset, k=5):
    """
    Measures retrieval accuracy based on expected document type.
    Prints each query, expected document, and top retrieved documents.
    """
    correct = 0

    for item in dataset:
        query = item["question"]
        expected_doc = item["expected_doc"]

        query_embedding = embedder.embed_query(query)
        retrieved = vector_store.search(query_embedding, k=k)

        retrieved_docs = [r["metadata"]["doc_type"] for r in retrieved]

        if expected_doc in retrieved_docs:
            correct += 1

        print("\nQuery:", query)
        print("Expected:", expected_doc)
        print("Retrieved (top 3):", retrieved_docs[:3])

    accuracy = correct / len(dataset)
    print(f"\n✅ Retrieval Accuracy: {accuracy:.2f}")
    return accuracy


def evaluate_rag_full(run_rag_fn, dataset):
    """
    Evaluates the full RAG pipeline using run_rag function.
    Prints query, status, answer preview, and sources.
    """
    results = []

    for item in dataset:
        query = item["question"]
        answer, sources, context, status = run_rag_fn(query)

        print("\n========================")
        print("Q:", query)
        print("Status:", status)
        print("Answer (preview):", answer[:200])
        print("Sources:", sources)

        results.append(
            {"query": query, "answer": answer, "status": status, "sources": sources}
        )

    return results


# =========================
# MAIN EXECUTION
# =========================
if __name__ == "__main__":
    print("🚀 Starting Evaluation...\n")

    # -------------------------
    # 1️⃣ Load and preprocess policy documents
    # -------------------------
    policy_docs = load_pdfs_from_directory(
        "data/policy", source_name="company_policy", domain="policy"
    )
    chunked_docs = chunk_documents(policy_docs)

    texts = [d["text"] for d in chunked_docs]
    metadatas = [d["metadata"] for d in chunked_docs]

    # -------------------------
    # 2️⃣ Initialize embedding and vector store
    # -------------------------
    embedder = Embedder()
    embeddings = embedder.embed_texts(texts)
    dimension = len(embeddings[0])
    vector_store = FAISSVectorStore(dimension)
    vector_store.add_embeddings(embeddings, texts, metadatas)

    # -------------------------
    # 3️⃣ Initialize LLM and reranker
    # -------------------------
    llm = get_llm()
    reranker = Reranker()

    # -------------------------
    # 4️⃣ Load your modular dataset
    # -------------------------
    # Assuming you have a Python file like "dataset.py" with "DATASET" variable
    try:
        from rag.eval.dataset import DATASET as dataset
    except ImportError:
        print(
            "❌ Could not import dataset.py. Make sure your dataset is in dataset.py as DATASET list."
        )
        exit(1)

    # -------------------------
    # 5️⃣ Run Retrieval Evaluation
    # -------------------------
    print("\n📊 RETRIEVAL EVALUATION")
    evaluate_retrieval(vector_store, embedder, dataset, k=5)

    # -------------------------
    # 6️⃣ Run RAG Evaluation
    # -------------------------
    print("\n🧠 RAG EVALUATION")
    results = evaluate_rag_full(
        lambda q: run_rag(q, embedder, vector_store, llm, reranker), dataset
    )

    print("\n✅ Evaluation Completed")
