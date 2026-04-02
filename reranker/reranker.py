from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self):
        # Lightweight but strong model
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def rerank(self, query, documents, top_k=3):
        """
        documents: list of dicts -> [{"text": ..., "metadata": ...}, ...]
        """

        pairs = [(query, doc["text"]) for doc in documents]

        scores = self.model.predict(pairs)

        # Attach scores to docs
        for doc, score in zip(documents, scores):
            doc["score"] = float(score)

        # Sort by score descending
        ranked_docs = sorted(documents, key=lambda x: x["score"], reverse=True)

        return ranked_docs[:top_k]