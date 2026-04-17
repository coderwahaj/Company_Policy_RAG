import os
import json
import threading
from retriever.bm25_retriever import BM25Retriever
from reranker.reranker import Reranker
from llm import get_llm
from vectorstore.faiss_store import FAISSVectorStore
from embeddings.embedder import Embedder
from processing.chunker import chunk_documents
from ingestion.loader import load_pdfs_from_directory

PIPELINE_INDEX_FILE = "vector_store/faiss.index"
PIPELINE_DOCSTORE_FILE = "vector_store/docstore.pkl"
PIPELINE_MANIFEST = "vector_store/manifest.json"

_PIPELINE_LOCK = threading.Lock()
_PIPELINE_CACHE = {}

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
    dimension = len(embeddings[0]) if embeddings else 768
    vs = FAISSVectorStore(dimension)
    if embeddings:
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