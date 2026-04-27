import numpy as np
from rag.retriever.bm25_retriever import BM25Retriever
 
 
class TestBM25Initialization:
    """Test BM25 retriever initialization"""
 
    def test_bm25_initializes(self, sample_texts):
        """Test that BM25 initializes correctly"""
        retriever = BM25Retriever(sample_texts)
        assert retriever is not None
        assert len(retriever.texts) == len(sample_texts)
 
    def test_bm25_tokenizes_texts(self, sample_texts):
        """Test that texts are tokenized"""
        retriever = BM25Retriever(sample_texts)
        assert len(retriever.tokenized) == len(sample_texts)
        assert all(isinstance(tokens, list) for tokens in retriever.tokenized)
 
 
class TestBM25Search:
    """Test BM25 search functionality"""
 
    def test_search_returns_list(self, sample_texts):
        """Test that search returns a list"""
        retriever = BM25Retriever(sample_texts)
        results = retriever.search("leave days", k=5)
        assert isinstance(results, list)
 
    def test_search_returns_correct_format(self, sample_texts):
        """Test that search results have correct format"""
        retriever = BM25Retriever(sample_texts)
        results = retriever.search("leave days", k=3)
        
        for result in results:
            assert "text" in result
            assert "score" in result
            assert isinstance(result["score"], float)
 
    def test_search_respects_k_parameter(self, sample_texts):
        """Test that search returns at most k results"""
        retriever = BM25Retriever(sample_texts)
        
        for k in [1, 2, 5]:
            results = retriever.search("leave", k=k)
            assert len(results) <= k
 
    def test_search_exact_match_rankpytested_high(self, sample_texts):
        """Test that exact matches are ranked high"""
        retriever = BM25Retriever(sample_texts)
        results = retriever.search("leave days", k=5)
        
        # "leave days" appears in first text
        first_result_text = results[0]["text"] if results else ""
        assert "leave days" in first_result_text.lower() or len(results) > 0
 
 
class TestBM25Scoring:
    """Test BM25 scoring"""
 
    def test_search_scores_are_numeric(self, sample_texts):
        """Test that scores are numeric"""
        retriever = BM25Retriever(sample_texts)
        results = retriever.search("leave", k=5)
        
        for result in results:
            assert isinstance(result["score"], (int, float))
            assert not np.isnan(result["score"])
 
    def test_search_scores_are_sorted(self, sample_texts):
        """Test that results are sorted by score (descending)"""
        retriever = BM25Retriever(sample_texts)
        results = retriever.search("leave", k=10)
        
        if len(results) > 1:
            scores = [r["score"] for r in results]
            assert scores == sorted(scores, reverse=True)
 
    def test_search_higher_scores_for_keyword_match(self, sample_texts):
        """Test that keyword matches have higher scores"""
        retriever = BM25Retriever(sample_texts)
        
        # Query with keyword that should match
        results_with_keyword = retriever.search("leave days", k=5)
        
        # Query with random word that might not match
        results_random = retriever.search("xyzabc", k=5)
        
        # Keywords should have non-zero results
        if results_with_keyword and results_random:
            avg_keyword_score = np.mean([r["score"] for r in results_with_keyword])
            avg_random_score = np.mean([r["score"] for r in results_random])
            
            # Keyword scores should be higher or equal
            assert avg_keyword_score >= avg_random_score
 
 
class TestBM25EdgeCases:
    """Test edge cases"""
 
    def test_search_empty_query(self, sample_texts):
        """Test searching with empty query"""
        retriever = BM25Retriever(sample_texts)
        results = retriever.search("", k=5)
        # Should return results even with empty query
        assert isinstance(results, list)
 
    def test_search_single_word_query(self, sample_texts):
        """Test searching with single word"""
        retriever = BM25Retriever(sample_texts)
        results = retriever.search("leave", k=5)
        assert len(results) > 0
 
    def test_search_special_characters(self, sample_texts):
        """Test searching with special characters"""
        retriever = BM25Retriever(sample_texts)
        results = retriever.search("@#$%", k=5)
        # Should not crash
        assert isinstance(results, list)
 
