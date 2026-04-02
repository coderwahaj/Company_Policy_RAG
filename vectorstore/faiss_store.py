import faiss
import numpy as np


class FAISSVectorStore:
    def __init__(self, dimension):
        self.index = faiss.IndexFlatL2(dimension)
        self.texts = []
        self.metadata = []

    def add_embeddings(self, embeddings, texts, metadatas):
        self.index.add(np.array(embeddings).astype("float32"))
        self.texts.extend(texts)
        self.metadata.extend(metadatas)

    def search(self, query_embedding, k=5, threshold=1.5):
        distances, indices = self.index.search(
            np.array([query_embedding]).astype("float32"), k
        )

        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue

            # ✅ FILTER LOW QUALITY MATCHES
            if distances[0][i] > threshold:
                continue

            results.append({
                "text": self.texts[idx],
                "metadata": self.metadata[idx]
            })

        return results