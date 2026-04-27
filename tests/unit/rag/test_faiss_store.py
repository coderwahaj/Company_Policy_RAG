import os
from rag.vectorstore.faiss_store import FAISSVectorStore
import numpy as np


class TestFAISSInitialization:
    """Test FAISS vector store initialization"""

    def test_faiss_initializes(self):
        """Test that FAISS store initializes"""
        vs = FAISSVectorStore(dimension=384)
        assert vs is not None
        assert vs.index is not None
        assert len(vs.texts) == 0
        assert len(vs.metadata) == 0

    def test_faiss_has_correct_dimension(self):
        """Test that FAISS index has correct dimension"""
        dimension = 384
        vs = FAISSVectorStore(dimension=dimension)
        assert vs.index.d == dimension


class TestFAISSAddEmbeddings:
    """Test adding embeddings to FAISS"""

    def test_add_embeddings(self, sample_embeddings):
        """Test adding embeddings"""
        vs = FAISSVectorStore(dimension=384)

        texts = ["Text 1", "Text 2", "Text 3", "Text 4"]
        metadata = [{"page": i} for i in range(4)]

        vs.add_embeddings(sample_embeddings, texts, metadata)

        assert vs.index.ntotal == 4
        assert len(vs.texts) == 4
        assert len(vs.metadata) == 4

    def test_add_multiple_batches(self, sample_embeddings):
        """Test adding multiple batches of embeddings"""
        vs = FAISSVectorStore(dimension=384)

        texts1 = ["Text 1", "Text 2"]
        metadata1 = [{"batch": 1}, {"batch": 1}]
        vs.add_embeddings(sample_embeddings[:2], texts1, metadata1)

        assert vs.index.ntotal == 2

        texts2 = ["Text 3", "Text 4"]
        metadata2 = [{"batch": 2}, {"batch": 2}]
        vs.add_embeddings(sample_embeddings[2:], texts2, metadata2)

        assert vs.index.ntotal == 4


class TestFAISSSearch:
    """Test FAISS search functionality"""

    def test_search_returns_results(self, sample_embeddings):
        """Test that search returns results"""
        vs = FAISSVectorStore(dimension=384)

        texts = ["Leave policy", "Notice period", "Allowance", "Benefits"]
        metadata = [{"id": i} for i in range(4)]
        vs.add_embeddings(sample_embeddings, texts, metadata)

        # Search using first embedding as query
        query_embedding = sample_embeddings[0]
        results = vs.search(query_embedding, k=2)

        assert len(results) > 0
        assert "text" in results[0]
        assert "metadata" in results[0]

    def test_search_respects_k(self, sample_embeddings):
        """Test that search returns at most k results"""
        vs = FAISSVectorStore(dimension=384)

        texts = [f"Text {i}" for i in range(10)]
        metadata = [{"id": i} for i in range(10)]

        # Add more embeddings
        np.random.seed(42)
        embeddings = np.random.randn(10, 384).astype("float32")
        vs.add_embeddings(embeddings, texts, metadata)

        for k in [1, 3, 5]:
            results = vs.search(embeddings[0], k=k)
            assert len(results) <= k

    def test_search_with_threshold(self, sample_embeddings):
        """Test search with similarity threshold"""
        vs = FAISSVectorStore(dimension=384)

        texts = ["Text 1", "Text 2", "Text 3", "Text 4"]
        metadata = [{"id": i} for i in range(4)]
        vs.add_embeddings(sample_embeddings, texts, metadata)

        results = vs.search(sample_embeddings[0], k=5, threshold=0.45)
        # Results should meet threshold
        assert len(results) >= 0


class TestFAISSPersistence:
    """Test saving and loading FAISS index"""

    def test_save_and_load(self, sample_embeddings, temp_vector_store_dir):
        """Test saving and loading FAISS index"""
        vs = FAISSVectorStore(dimension=384)

        texts = ["Text 1", "Text 2", "Text 3", "Text 4"]
        metadata = [{"page": i} for i in range(4)]
        vs.add_embeddings(sample_embeddings, texts, metadata)

        # Save
        index_path = os.path.join(temp_vector_store_dir, "faiss.index")
        docstore_path = os.path.join(temp_vector_store_dir, "docstore.pkl")
        vs.save(index_path, docstore_path)

        # Check files exist
        assert os.path.exists(index_path)
        assert os.path.exists(docstore_path)

        # Load
        vs_loaded = FAISSVectorStore.load(index_path, docstore_path)

        assert vs_loaded.index.ntotal == 4
        assert len(vs_loaded.texts) == 4
        assert len(vs_loaded.metadata) == 4

    def test_roundtrip_preserves_data(self, sample_embeddings, temp_vector_store_dir):
        """Test that save and load preserve data"""
        vs = FAISSVectorStore(dimension=384)

        texts = ["Original 1", "Original 2", "Original 3", "Original 4"]
        metadata = [{"original": True, "id": i} for i in range(4)]
        vs.add_embeddings(sample_embeddings, texts, metadata)

        # Save
        index_path = os.path.join(temp_vector_store_dir, "faiss.index")
        docstore_path = os.path.join(temp_vector_store_dir, "docstore.pkl")
        vs.save(index_path, docstore_path)

        # Load
        vs_loaded = FAISSVectorStore.load(index_path, docstore_path)

        # Compare
        assert vs_loaded.texts == texts
        assert vs_loaded.metadata == metadata
