from sentence_transformers import SentenceTransformer
import numpy as np


class Embedder:
    def __init__(self, model_name="BAAI/bge-large-en-v1.5"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts):
        return self.model.encode(
            texts, normalize_embeddings=True, show_progress_bar=True
        )

    def embed_query(self, query):
        return self.model.encode([query], normalize_embeddings=True)[0]
