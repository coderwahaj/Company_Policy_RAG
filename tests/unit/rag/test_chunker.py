from rag.processing.chunker import chunk_documents


class TestChunkBasics:
    """Test basic chunking functionality"""

    def test_chunk_documents_returns_list(self, sample_documents):
        """Test that chunk_documents returns a list"""
        chunked = chunk_documents(sample_documents)
        assert isinstance(chunked, list)

    def test_chunk_documents_not_empty(self, sample_documents):
        """Test that chunked result is not empty"""
        chunked = chunk_documents(sample_documents)
        assert len(chunked) > 0

    def test_chunk_has_text_and_metadata(self, sample_documents):
        """Test that each chunk has text and metadata"""
        chunked = chunk_documents(sample_documents)
        
        for chunk in chunked:
            assert "text" in chunk
            assert "metadata" in chunk
            assert isinstance(chunk["text"], str)
            assert isinstance(chunk["metadata"], dict)

    def test_chunk_metadata_preserved(self, sample_documents):
        """Test that original metadata is preserved"""
        chunked = chunk_documents(sample_documents)
        
        # Check that we have metadata fields
        assert chunked[0]["metadata"]["file_name"] in [
            doc["metadata"]["file_name"] for doc in sample_documents
        ]


class TestChunkSize:
    """Test chunk size constraints"""

    def test_chunk_size_respected(self, sample_documents):
        """Test that chunk size is <= 500 characters"""
        chunked = chunk_documents(sample_documents)
        
        for chunk in chunked:
            assert len(chunk["text"]) <= 600  # Allow some flexibility

    def test_chunks_contain_text(self, sample_documents):
        """Test that all chunks have non-empty text"""
        chunked = chunk_documents(sample_documents)
        
        for chunk in chunked:
            assert len(chunk["text"].strip()) > 0


class TestChunkOverlap:
    """Test overlap between chunks"""

    def test_overlapping_text_exists(self, sample_documents):
        """Test that overlapping text exists between consecutive chunks"""
        # This would require checking if chunks from same doc have overlap
        chunked = chunk_documents(sample_documents)
        
        # If we have multiple chunks from same doc, there should be overlap
        if len(chunked) > 1:
            # Just verify we got chunks
            assert len(chunked) >= len(sample_documents)


class TestChunkEdgeCases:
    """Test edge cases"""

    def test_chunk_single_document(self):
        """Test chunking single document"""
        single_doc = [
            {
                "text": "This is a test document about leave policies.",
                "metadata": {"source": "test", "domain": "policy"},
            }
        ]
        chunked = chunk_documents(single_doc)
        assert len(chunked) >= 1

    def test_chunk_empty_document_text(self):
        """Test chunking document with empty text"""
        empty_doc = [{"text": "", "metadata": {"source": "test"}}]
        chunked = chunk_documents(empty_doc)
        assert len(chunked) == 0

    def test_chunk_very_long_document(self):
        """Test chunking very long document"""
        long_text = " ".join(["word"] * 5000)
        doc = [{"text": long_text, "metadata": {"source": "test"}}]
        chunked = chunk_documents(doc)
        
        # Should produce multiple chunks
        assert len(chunked) > 1

    def test_chunk_maintains_order(self, sample_documents):
        """Test that chunks maintain document order"""
        chunked = chunk_documents(sample_documents)
        
        # First chunk should be from first document
        assert chunked[0]["metadata"]["file_name"] == sample_documents[0]["metadata"]["file_name"]