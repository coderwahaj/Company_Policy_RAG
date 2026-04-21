import os
import json
import threading
from rag.retriever.bm25_retriever import BM25Retriever
from rag.reranker.reranker import Reranker
from rag.llm import get_llm
from rag.vectorstore.faiss_store import FAISSVectorStore
from rag.embeddings.embedder import Embedder
from rag.processing.chunker import chunk_documents
from rag.ingestion.loader import load_pdfs_from_directory

PIPELINE_INDEX_FILE = "vector_store/faiss.index"
PIPELINE_DOCSTORE_FILE = "vector_store/docstore.pkl"
PIPELINE_MANIFEST = "vector_store/manifest.json"

_PIPELINE_LOCK = threading.Lock()
_PIPELINE_CACHE = {}


def compute_data_fingerprint(root_dir: str):
    import hashlib

    hash = hashlib.sha1()
    if not os.path.exists(root_dir):
        return None

    for dirpath, _, filenames in os.walk(root_dir):
        for fn in sorted(filenames):
            fp = os.path.join(dirpath, fn)
            try:
                s = os.stat(fp)
            except OSError:
                continue
            hash.update(fp.replace("\\", "/").encode())
            hash.update(str(s.st_size).encode())
            hash.update(str(int(s.st_mtime)).encode())

    return hash.hexdigest()


def save_pipeline(vs, chunk_count, data_fingerprint: str):
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


def _build_pipeline(provider: str, data_root="data/policy"):
    saved = load_pipeline(data_root)
    if saved:
        embedder = Embedder()
        vs = saved["vector_store"]
        bm25 = saved["bm25"]
        chunk_count = saved["chunk_count"]
        llm = get_llm(provider)
        return embedder, vs, llm, Reranker(), bm25, chunk_count

    policy_docs = load_pdfs_from_directory(
        data_root, source_name="company_policy", domain="policy"
    )
    chunked_docs = chunk_documents(policy_docs)
    texts = [d["text"] for d in chunked_docs]
    metadatas = [d["metadata"] for d in chunked_docs]

    embedder = Embedder()
    embeddings = embedder.embed_texts(texts)

    has_rows = embeddings is not None and (
        (hasattr(embeddings, "shape") and embeddings.shape[0] > 0)
        or (not hasattr(embeddings, "shape") and len(embeddings) > 0)
    )

    dimension = (
        int(embeddings.shape[1])
        if hasattr(embeddings, "shape") and embeddings.shape[0] > 0
        else (len(embeddings[0]) if has_rows else 768)
    )

    vs = FAISSVectorStore(dimension)
    if has_rows:
        vs.add_embeddings(embeddings, texts, metadatas)

    bm25 = BM25Retriever(texts)
    fp = compute_data_fingerprint(data_root)
    save_pipeline(vs, texts, bm25, len(texts), fp)

    llm = get_llm(provider)
    return embedder, vs, llm, Reranker(), bm25, len(texts)


def get_pipeline(provider: str = "groq", data_root="data/policy"):
    """Thread-safe cached pipeline."""
    key = (provider, compute_data_fingerprint(data_root))
    with _PIPELINE_LOCK:
        if key in _PIPELINE_CACHE:
            return _PIPELINE_CACHE[key]

        pipeline = _build_pipeline(provider, data_root)
        _PIPELINE_CACHE[key] = pipeline
        return pipeline


# Added helpers for API routes

def reset_pipeline(provider: str = "groq", data_root="data/policy"):
    """
    Remove cached pipeline for current provider + current data fingerprint.
    Keeps persisted FAISS files on disk.
    """
    fp = compute_data_fingerprint(data_root)
    key = (provider, fp)

    with _PIPELINE_LOCK:
        _PIPELINE_CACHE.pop(key, None)


def pipeline_status(provider: str = "groq", data_root="data/policy"):
    """
    Return readiness and chunk_count.
      1) in-memory cache
      2) persisted manifest (if fingerprint matches)
    """
    fp = compute_data_fingerprint(data_root)
    key = (provider, fp)

    with _PIPELINE_LOCK:
        cached = _PIPELINE_CACHE.get(key)
        if cached:
            chunk_count = 0
            if isinstance(cached, (tuple, list)) and len(cached) >= 6:
                try:
                    chunk_count = int(cached[5])
                except Exception:
                    chunk_count = 0
            return {"ready": True, "chunk_count": chunk_count}

    # fallback: persisted manifest
    saved = load_pipeline(data_root)
    if saved:
        return {"ready": True, "chunk_count": int(saved.get("chunk_count", 0))}

    return {"ready": False, "chunk_count": 0}
