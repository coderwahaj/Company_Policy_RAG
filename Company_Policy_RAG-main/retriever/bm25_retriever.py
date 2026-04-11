# retrieval/bm25_retriever.py
from rank_bm25 import BM25Okapi

class BM25Retriever:
    def __init__(self, texts):
        self.texts = texts
        self.tokenized = [t.split() for t in texts]
        self.bm25 = BM25Okapi(self.tokenized)

    def search(self, query, k=10):
        scores = self.bm25.get_scores(query.split())
        top_k_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

        return [
            {"text": self.texts[i], "score": scores[i]}
            for i in top_k_idx
        ]