import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import hashlib


class TestComputeDataFingerprint:
    """Test compute_data_fingerprint function"""

    def test_fingerprint_nonexistent_directory(self):
        """Test fingerprint for non-existent directory returns None"""
        from backend.app.core.pipeline import compute_data_fingerprint
        
        fingerprint = compute_data_fingerprint("/nonexistent/path/12345")
        assert fingerprint is None

    def test_fingerprint_empty_directory(self):
        """Test fingerprint for empty directory"""
        from backend.app.core.pipeline import compute_data_fingerprint
        
        with tempfile.TemporaryDirectory() as tmpdir:
            fingerprint = compute_data_fingerprint(tmpdir)
            assert fingerprint is not None
            assert isinstance(fingerprint, str)
            assert len(fingerprint) == 40  # SHA1 hex length

    def test_fingerprint_with_files(self):
        """Test fingerprint changes with different files"""
        from backend.app.core.pipeline import compute_data_fingerprint
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create first file
            file1 = os.path.join(tmpdir, "file1.txt")
            with open(file1, "w") as f:
                f.write("content1")
            fp1 = compute_data_fingerprint(tmpdir)
            
            # Add second file
            file2 = os.path.join(tmpdir, "file2.txt")
            with open(file2, "w") as f:
                f.write("content2")
            fp2 = compute_data_fingerprint(tmpdir)
            
            # Fingerprints should be different
            assert fp1 != fp2

    def test_fingerprint_consistency(self):
        """Test fingerprint is consistent for same directory"""
        from backend.app.core.pipeline import compute_data_fingerprint
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = os.path.join(tmpdir, "file.txt")
            with open(file1, "w") as f:
                f.write("content")
            
            fp1 = compute_data_fingerprint(tmpdir)
            fp2 = compute_data_fingerprint(tmpdir)
            
            assert fp1 == fp2


class TestSavePipeline:
    """Test save_pipeline function"""

    @patch("backend.app.core.pipeline.os.makedirs")
    def test_save_pipeline_creates_directory(self, mock_makedirs):
        """Test save_pipeline creates vector_store directory"""
        from backend.app.core.pipeline import save_pipeline
        
        vs = Mock()
        vs.save = Mock()
        
        save_pipeline(vs, 42, "fingerprint123")
        mock_makedirs.assert_called_once_with("vector_store", exist_ok=True)

    @patch("backend.app.core.pipeline.os.makedirs")
    def test_save_pipeline_saves_vector_store(self, mock_makedirs):
        """Test save_pipeline calls vector store save"""
        from backend.app.core.pipeline import save_pipeline
        
        vs = Mock()
        vs.save = Mock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("backend.app.core.pipeline.PIPELINE_INDEX_FILE", 
                      os.path.join(tmpdir, "faiss.index")):
                with patch("backend.app.core.pipeline.PIPELINE_DOCSTORE_FILE",
                          os.path.join(tmpdir, "docstore.pkl")):
                    with patch("backend.app.core.pipeline.PIPELINE_MANIFEST",
                              os.path.join(tmpdir, "manifest.json")):
                        save_pipeline(vs, 42, "fingerprint123")
                        vs.save.assert_called_once()

    @patch("backend.app.core.pipeline.os.makedirs")
    def test_save_pipeline_manifest_content(self, mock_makedirs):
        """Test save_pipeline creates valid manifest"""
        from backend.app.core.pipeline import save_pipeline
        
        vs = Mock()
        vs.save = Mock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_file = os.path.join(tmpdir, "manifest.json")
            
            with patch("backend.app.core.pipeline.PIPELINE_INDEX_FILE", "test.index"):
                with patch("backend.app.core.pipeline.PIPELINE_DOCSTORE_FILE", "test.pkl"):
                    with patch("backend.app.core.pipeline.PIPELINE_MANIFEST", manifest_file):
                        save_pipeline(vs, 42, "fp123")
                        
                        # Verify manifest file was created
                        assert os.path.exists(manifest_file)
                        
                        with open(manifest_file, "r") as f:
                            manifest = json.load(f)
                        
                        assert manifest["fingerprint"] == "fp123"
                        assert manifest["chunk_count"] == 42


class TestLoadPipeline:
    """Test load_pipeline function"""

    def test_load_pipeline_no_manifest(self):
        """Test load_pipeline returns None when manifest doesn't exist"""
        from backend.app.core.pipeline import load_pipeline
        
        with patch("backend.app.core.pipeline.os.path.exists", return_value=False):
            result = load_pipeline("/data/policy")
            assert result is None

    @patch("backend.app.core.pipeline.compute_data_fingerprint")
    def test_load_pipeline_fingerprint_mismatch(self, mock_fingerprint):
        """Test load_pipeline returns None on fingerprint mismatch"""
        from backend.app.core.pipeline import load_pipeline
        
        mock_fingerprint.return_value = "new_fingerprint"
        
        manifest_content = {
            "fingerprint": "old_fingerprint",
            "chunk_count": 42,
            "index_file": "test.index",
            "docstore_file": "test.pkl"
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_file = os.path.join(tmpdir, "manifest.json")
            with open(manifest_file, "w") as f:
                json.dump(manifest_content, f)
            
            with patch("backend.app.core.pipeline.PIPELINE_MANIFEST", manifest_file):
                result = load_pipeline("/data/policy")
                assert result is None

    @patch("backend.app.core.pipeline.FAISSVectorStore")
    @patch("backend.app.core.pipeline.BM25Retriever")
    @patch("backend.app.core.pipeline.compute_data_fingerprint")
    def test_load_pipeline_success(self, mock_fingerprint, mock_bm25, mock_faiss):
        """Test load_pipeline successfully loads saved pipeline"""
        from backend.app.core.pipeline import load_pipeline
        
        mock_fingerprint.return_value = "correct_fingerprint"
        mock_vs = Mock()
        mock_vs.texts = ["text1", "text2"]
        mock_faiss.load.return_value = mock_vs
        
        manifest_content = {
            "fingerprint": "correct_fingerprint",
            "chunk_count": 2,
            "index_file": "test.index",
            "docstore_file": "test.pkl"
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dummy files
            index_file = os.path.join(tmpdir, "test.index")
            docstore_file = os.path.join(tmpdir, "test.pkl")
            manifest_file = os.path.join(tmpdir, "manifest.json")
            
            open(index_file, "w").close()
            open(docstore_file, "w").close()
            
            with open(manifest_file, "w") as f:
                json.dump(manifest_content, f)
            
            with patch("backend.app.core.pipeline.PIPELINE_MANIFEST", manifest_file):
                with patch("backend.app.core.pipeline.os.path.exists", return_value=True):
                    result = load_pipeline("/data/policy")
                    assert result is not None
                    assert result["chunk_count"] == 2


class TestGetPipeline:
    """Test get_pipeline function"""

    @patch("backend.app.core.pipeline._build_pipeline")
    def test_get_pipeline_returns_tuple(self, mock_build):
        """Test get_pipeline returns correct tuple structure"""
        from backend.app.core.pipeline import get_pipeline, _PIPELINE_CACHE
        
        _PIPELINE_CACHE.clear()
        
        mock_embedder = Mock()
        mock_vs = Mock()
        mock_llm = Mock()
        mock_reranker = Mock()
        mock_bm25 = Mock()
        
        mock_build.return_value = (mock_embedder, mock_vs, mock_llm, mock_reranker, mock_bm25, 42)
        
        result = get_pipeline("groq", "/data/policy")
        
        assert isinstance(result, tuple)
        assert len(result) == 6

    @patch("backend.app.core.pipeline.compute_data_fingerprint")
    @patch("backend.app.core.pipeline._build_pipeline")
    def test_get_pipeline_caching(self, mock_build, mock_fingerprint):
        """Test get_pipeline caches results"""
        from backend.app.core.pipeline import get_pipeline, _PIPELINE_CACHE
        
        _PIPELINE_CACHE.clear()
        mock_fingerprint.return_value = "fp123"
        
        mock_pipeline = Mock()
        mock_build.return_value = mock_pipeline
        
        # First call
        result1 = get_pipeline("groq", "/data/policy")
        
        # Second call - should use cache
        result2 = get_pipeline("groq", "/data/policy")
        
        assert result1 == result2
        assert mock_build.call_count == 1  # Only called once

    @patch("backend.app.core.pipeline.compute_data_fingerprint")
    @patch("backend.app.core.pipeline._build_pipeline")
    def test_get_pipeline_different_providers(self, mock_build, mock_fingerprint):
        """Test get_pipeline creates separate cache for different providers"""
        from backend.app.core.pipeline import get_pipeline, _PIPELINE_CACHE
        
        _PIPELINE_CACHE.clear()
        mock_fingerprint.return_value = "fp123"
        mock_build.return_value = Mock()
        
        get_pipeline("groq", "/data/policy")
        get_pipeline("gemini", "/data/policy")
        
        # Should be called twice for different providers
        assert mock_build.call_count == 2


class TestResetPipeline:
    """Test reset_pipeline function"""

    @patch("backend.app.core.pipeline.compute_data_fingerprint")
    def test_reset_pipeline_removes_cache(self, mock_fingerprint):
        """Test reset_pipeline removes cached pipeline"""
        from backend.app.core.pipeline import reset_pipeline, _PIPELINE_CACHE
        
        mock_fingerprint.return_value = "fp123"
        _PIPELINE_CACHE[("groq", "fp123")] = Mock()
        
        reset_pipeline("groq", "/data/policy")
        
        assert ("groq", "fp123") not in _PIPELINE_CACHE

    @patch("backend.app.core.pipeline.compute_data_fingerprint")
    def test_reset_pipeline_no_error_if_not_cached(self, mock_fingerprint):
        """Test reset_pipeline doesn't error if not cached"""
        from backend.app.core.pipeline import reset_pipeline, _PIPELINE_CACHE
        
        mock_fingerprint.return_value = "fp123"
        _PIPELINE_CACHE.clear()
        
        # Should not raise error
        reset_pipeline("groq", "/data/policy")


class TestPipelineStatus:
    """Test pipeline_status function"""

    @patch("backend.app.core.pipeline.compute_data_fingerprint")
    def test_pipeline_status_from_cache(self, mock_fingerprint):
        """Test pipeline_status returns status from cache"""
        from backend.app.core.pipeline import pipeline_status, _PIPELINE_CACHE
        
        mock_fingerprint.return_value = "fp123"
        _PIPELINE_CACHE.clear()
        
        # Add mock pipeline to cache
        _PIPELINE_CACHE[("groq", "fp123")] = (Mock(), Mock(), Mock(), Mock(), Mock(), 42)
        
        status = pipeline_status("groq", "/data/policy")
        
        assert status["ready"] is True
        assert status["chunk_count"] == 42

    @patch("backend.app.core.pipeline.load_pipeline")
    @patch("backend.app.core.pipeline.compute_data_fingerprint")
    def test_pipeline_status_from_manifest(self, mock_fingerprint, mock_load):
        """Test pipeline_status returns status from persisted manifest"""
        from backend.app.core.pipeline import pipeline_status, _PIPELINE_CACHE
        
        mock_fingerprint.return_value = "fp123"
        _PIPELINE_CACHE.clear()
        mock_load.return_value = {"ready": True, "chunk_count": 50}
        
        status = pipeline_status("groq", "/data/policy")
        
        assert status["ready"] is True
        assert status["chunk_count"] == 50

    @patch("backend.app.core.pipeline.load_pipeline")
    @patch("backend.app.core.pipeline.compute_data_fingerprint")
    def test_pipeline_status_not_ready(self, mock_fingerprint, mock_load):
        """Test pipeline_status returns not ready when nothing found"""
        from backend.app.core.pipeline import pipeline_status, _PIPELINE_CACHE
        
        mock_fingerprint.return_value = "fp123"
        _PIPELINE_CACHE.clear()
        mock_load.return_value = None
        
        status = pipeline_status("groq", "/data/policy")
        
        assert status["ready"] is False
        assert status["chunk_count"] == 0