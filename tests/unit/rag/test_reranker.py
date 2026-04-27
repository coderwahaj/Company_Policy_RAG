from rag.processing.reranker import Reranker


class TestRerankerInitialization:
    """Test reranker initialization"""

    def test_reranker_initializes(self):
        """Test that reranker initializes"""
        reranker = Reranker()
        assert reranker is not None
        assert reranker.model is not None


class TestReranking:
    """Test reranking functionality"""

    def test_rerank_returns_list(self):
        """Test that rerank returns a list"""
        reranker = Reranker()
        query = "leave days"
        documents = [
            {"text": "Leave policy gives 20 days", "metadata": {}},
            {"text": "Weather is sunny", "metadata": {}},
            {"text": "Annual leave policy", "metadata": {}},
        ]

        results = reranker.rerank(query, documents, top_k=2)
        assert isinstance(results, list)

    def test_rerank_respects_top_k(self):
        """Test that rerank returns at most top_k results"""
        reranker = Reranker()
        query = "leave"
        documents = [
            {"text": f"Document {i} about leave", "metadata": {"id": i}}
            for i in range(10)
        ]

        for k in [1, 3, 5]:
            results = reranker.rerank(query, documents, top_k=k)
            assert len(results) == min(k, len(documents))

    def test_rerank_adds_scores(self):
        """Test that rerank adds scores to documents"""
        reranker = Reranker()
        query = "leave days"
        documents = [
            {"text": "Leave policy gives 20 days", "metadata": {}},
            {"text": "Weather information", "metadata": {}},
        ]

        results = reranker.rerank(query, documents, top_k=2)

        for result in results:
            assert "score" in result
            assert isinstance(result["score"], float)

    def test_rerank_sorted_by_score(self):
        """Test that results are sorted by score"""
        reranker = Reranker()
        query = "leave days"
        documents = [
            {"text": "Leave policy gives 20 days", "metadata": {}},
            {"text": "Weather is sunny", "metadata": {}},
            {"text": "Annual leave policy", "metadata": {}},
        ]

        results = reranker.rerank(query, documents, top_k=3)

        if len(results) > 1:
            scores = [r["score"] for r in results]
            assert scores == sorted(scores, reverse=True)
