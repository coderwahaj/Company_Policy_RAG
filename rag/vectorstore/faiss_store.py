import faiss
import numpy as np
import pickle
import os


class FAISSVectorStore:
    def __init__(self, dimension):
        # Use normalized embeddings → cosine similarity
        self.index = faiss.IndexFlatIP(dimension)
        self.texts = []
        self.metadata = []

    def add_embeddings(self, embeddings, texts, metadatas):
        embeddings = np.array(embeddings).astype("float32")
        self.index.add(embeddings)
        self.texts.extend(texts)
        self.metadata.extend(metadatas)

    def search(self, query_embedding, k=10, threshold=0.45):
        query_embedding = np.array([query_embedding]).astype("float32")
        distances, indices = self.index.search(query_embedding, k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue
            if distances[0][i] < threshold:  # filter low similarity
                continue
            results.append({"text": self.texts[idx], "metadata": self.metadata[idx]})
        return results

    def save(self, index_path: str, docstore_path: str):
        os.makedirs(os.path.dirname(index_path) or "./", exist_ok=True)
        # persist faiss index
        faiss.write_index(self.index, index_path)
        # persist texts + metadata
        with open(docstore_path, "wb") as f:
            pickle.dump({"texts": self.texts, "metadata": self.metadata}, f)

    @classmethod
    def load(cls, index_path: str, docstore_path: str):
        # load faiss index
        index = faiss.read_index(index_path)
        # load docstore
        with open(docstore_path, "rb") as f:
            data = pickle.load(f)

        # create instance with proper dimension
        try:
            dimension = index.d
        except Exception:
            # fallback: try to infer from index.ntotal and index.reconstruct
            dimension = 0

        instance = cls(dimension) if dimension > 0 else cls(1)
        instance.index = index
        instance.texts = data.get("texts", [])
        instance.metadata = data.get("metadata", [])
        return instance
