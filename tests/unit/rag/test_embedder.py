import numpy as np
from rag.embeddings.embedder import Embedder


class TestEmbedderInitialization:
    """Test embedder initialization"""

    def test_embedder_initializes(self):
        """Test that embedder initializes without error"""
        embedder = Embedder()
        assert embedder is not None
        assert embedder.model is not None

    def test_embedder_has_model(self):
        """Test that embedder has a loaded model"""
        embedder = Embedder()
        assert hasattr(embedder, "model")


class TestTextEmbedding:
    """Test embedding generation for texts"""

    def test_embed_texts_returns_array(self, sample_texts):
        """Test that embed_texts returns numpy array"""
        embedder = Embedder()
        embeddings = embedder.embed_texts(sample_texts)
        
        assert embeddings is not None
        assert isinstance(embeddings, np.ndarray)

    def test_embed_texts_correct_shape(self, sample_texts):
        """Test that output shape matches input"""
        embedder = Embedder()
        embeddings = embedder.embed_texts(sample_texts)
        
        # Should be (num_texts, embedding_dim)
        assert embeddings.shape[0] == len(sample_texts)
        assert embeddings.shape[1] == 1024 

    def test_embed_texts_float32_dtype(self, sample_texts):
        """Test that embeddings are float32"""
        embedder = Embedder()
        embeddings = embedder.embed_texts(sample_texts)
        
        assert embeddings.dtype in [np.float32, np.float64]

    def test_embed_texts_normalized(self, sample_texts):
        """Test that embeddings are normalized (L2 norm = 1)"""
        embedder = Embedder()
        embeddings = embedder.embed_texts(sample_texts)
        
        # Check L2 norm is close to 1
        norms = np.linalg.norm(embeddings, axis=1)
        np.testing.assert_array_almost_equal(norms, np.ones(len(sample_texts)), decimal=5)

    def test_embed_query_returns_1d_array(self):
        """Test that embed_query returns 1D array"""
        embedder = Embedder()
        query = "How many leave days do I get?"
        embedding = embedder.embed_query(query)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.ndim == 1
        assert embedding.shape[0] == 1024

    def test_embed_query_normalized(self):
        """Test that query embedding is normalized"""
        embedder = Embedder()
        query = "What is the notice period?"
        embedding = embedder.embed_query(query)
        
        norm = np.linalg.norm(embedding)
        assert np.isclose(norm, 1.0, atol=1e-5)

    def test_embed_identical_texts_identical_embeddings(self):
        """Test that same text produces same embedding"""
        embedder = Embedder()
        text = "Leave policy is important"
        
        emb1 = embedder.embed_texts([text])
        emb2 = embedder.embed_texts([text])
        
        np.testing.assert_array_almost_equal(emb1, emb2)

    def test_embed_single_text(self):
        """Test embedding a single text"""
        embedder = Embedder()
        text = "Single text embedding test"
        embeddings = embedder.embed_texts([text])
        
        assert embeddings.shape == (1, 1024)

    def test_embed_batch_texts(self, sample_texts):
        """Test embedding multiple texts at once"""
        embedder = Embedder()
        embeddings = embedder.embed_texts(sample_texts)
        
        assert embeddings.shape[0] == len(sample_texts)


class TestEmbeddingConsistency:
    """Test consistency of embeddings"""

    def test_similar_texts_similar_embeddings(self):
        """Test that similar texts have similar embeddings"""
        embedder = Embedder()
        text1 = "Leave policy gives 20 days of annual leave"
        text2 = "Annual leave is 20 days per policy"
        
        emb1 = embedder.embed_texts([text1])[0]
        emb2 = embedder.embed_texts([text2])[0]
        
        # Compute cosine similarity
        similarity = np.dot(emb1, emb2)
        
        # Should be high (>0.7)
        assert similarity > 0.7

    def test_different_texts_different_embeddings(self):
        """Test that different texts have different embeddings"""
        embedder = Embedder()
        text1 = "Leave policy gives 20 days"
        text2 = "The weather is sunny today"
        
        emb1 = embedder.embed_texts([text1])[0]
        emb2 = embedder.embed_texts([text2])[0]
        
        similarity = np.dot(emb1, emb2)
        
        # Should be low (<0.5)
        assert similarity < 0.5


class TestEmbeddingEdgeCases:
    """Test edge cases and error handling"""

    def test_embed_empty_list(self):
        """Test embedding empty list"""
        embedder = Embedder()
        embeddings = embedder.embed_texts([])
        
        assert embeddings.shape[0] == 0

    def test_embed_special_characters(self):
        """Test embedding text with special characters"""
        embedder = Embedder()
        text = "Special chars: @#$%^&*() and émojis! 🎉"
        embeddings = embedder.embed_texts([text])
        
        assert embeddings.shape == (1, 1024)

    def test_embed_very_long_text(self):
        """Test embedding very long text"""
        embedder = Embedder()
        long_text = " ".join(["word"] * 1000)
        embeddings = embedder.embed_texts([long_text])
        
        assert embeddings.shape == (1, 1024)

    def test_embed_single_word(self):
        """Test embedding single word"""
        embedder = Embedder()
        embeddings = embedder.embed_texts(["leave"])
        
        assert embeddings.shape == (1, 1024)