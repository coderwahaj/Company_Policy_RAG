import faiss
import numpy as np


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
