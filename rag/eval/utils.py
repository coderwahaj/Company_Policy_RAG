"""
eval_utils.py — Evaluation script for Company Policy RAG Assistant
Run: python eval_utils.py
"""

import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag.ingestion.loader import load_pdfs_from_directory
from rag.processing.chunker import chunk_documents
from rag.embeddings.embedder import Embedder
from rag.vectorstore.faiss_store import FAISSVectorStore
from rag.llm import get_llm
from rag.reranker.reranker import Reranker
from main import run_rag

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def evaluate_retrieval(vector_store, embedder, dataset, k=5):
    correct = 0

    for item in dataset:
        query = item["question"]
        expected_doc = item["expected_doc"]

        query_embedding = embedder.embed_query(query)
        retrieved = vector_store.search(query_embedding, k=k)

        retrieved_docs = [r["metadata"]["doc_type"] for r in retrieved]

        if expected_doc in retrieved_docs:
            correct += 1

        logger.info("Query: %s", query)
        logger.info("Expected: %s", expected_doc)
        logger.info("Retrieved (top 3): %s", retrieved_docs[:3])

    accuracy = correct / len(dataset)
    logger.info("Retrieval Accuracy: %.2f", accuracy)
    return accuracy


def evaluate_rag_full(run_rag_fn, dataset):
    results = []

    for item in dataset:
        query = item["question"]
        answer, sources, context, status = run_rag_fn(query)

        logger.info("========================")
        logger.info("Q: %s", query)
        logger.info("Status: %s", status)
        logger.info("Answer (preview): %s", answer[:200])
        logger.info("Sources: %s", sources)

        results.append(
            {"query": query, "answer": answer, "status": status, "sources": sources}
        )

    return results


if __name__ == "__main__":
    logger.info("Starting evaluation...")

    policy_docs = load_pdfs_from_directory(
        "data/policy", source_name="company_policy", domain="policy"
    )
    chunked_docs = chunk_documents(policy_docs)

    texts = [d["text"] for d in chunked_docs]
    metadatas = [d["metadata"] for d in chunked_docs]

    embedder = Embedder()
    embeddings = embedder.embed_texts(texts)
    dimension = len(embeddings[0])
    vector_store = FAISSVectorStore(dimension)
    vector_store.add_embeddings(embeddings, texts, metadatas)

    llm = get_llm()
    reranker = Reranker()

    try:
        from rag.eval.dataset import DATASET as dataset
    except ImportError:
        logger.error(
            "Could not import dataset.py. Ensure DATASET list exists in rag/eval/dataset.py."
        )
        raise SystemExit(1)

    logger.info("Retrieval evaluation")
    evaluate_retrieval(vector_store, embedder, dataset, k=5)

    logger.info("RAG evaluation")
    results = evaluate_rag_full(
        lambda q: run_rag(q, embedder, vector_store, llm, reranker), dataset
    )

    logger.info("Evaluation completed")
