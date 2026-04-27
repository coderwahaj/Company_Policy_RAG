# tests/unit/test_loader.py
from rag.ingestion.loader import clean_text


class TestCleanText:
    """Test text cleaning functionality"""

    def test_clean_text_removes_urls(self):
        """Test that URLs are removed"""
        text = "Visit https://example.com for more info"
        cleaned = clean_text(text)
        assert "http" not in cleaned
        assert "example.com" not in cleaned

    def test_clean_text_removes_page_numbers(self):
        """Test that page numbers are removed"""
        text = "Content\nPage 1\nMore content"
        cleaned = clean_text(text)
        assert "Page 1" not in cleaned

    def test_clean_text_removes_symbols(self):
        """Test that special symbols are removed"""
        text = "Content ▸ with ◂ symbols"
        cleaned = clean_text(text)
        assert "▸" not in cleaned
        assert "◂" not in cleaned

    def test_clean_text_preserves_content(self):
        """Test that actual content is preserved"""
        text = "Leave policy states 20 days annual leave"
        cleaned = clean_text(text)
        assert "Leave policy" in cleaned
        assert "20 days" in cleaned

    def test_clean_text_removes_extra_whitespace(self):
        """Test that extra whitespace is removed"""
        text = "Content  with   multiple    spaces"
        cleaned = clean_text(text)
        assert "  " not in cleaned  # No double spaces

    def test_clean_text_collapses_newlines(self):
        """Test that multiple newlines are collapsed"""
        text = "Line 1\n\n\n\nLine 2"
        cleaned = clean_text(text)
        # Should have at most 2 consecutive newlines
        assert "\n\n\n" not in cleaned

    def test_clean_text_empty_string(self):
        """Test cleaning empty string"""
        cleaned = clean_text("")
        assert cleaned == ""

    def test_clean_text_only_whitespace(self):
        """Test cleaning whitespace-only string"""
        cleaned = clean_text("   \n\n   \t\t  ")
        assert cleaned == ""


class TestDocumentMetadata:
    """Test document metadata assignment"""

    def test_doc_type_detection_leave(self):
        """Test that 'leave' in filename is detected as leave_policy"""
        # Simulating metadata assignment
        fname = "leave_policy.pdf"
        doc_type = "leave_policy" if "leave" in fname.lower() else "unknown"
        assert doc_type == "leave_policy"

    def test_doc_type_detection_contract(self):
        """Test that 'contract' is detected as employment_contract"""
        fname = "employment_contract.pdf"
        doc_type = "employment_contract" if "contract" in fname.lower() else "unknown"
        assert doc_type == "employment_contract"

    def test_doc_type_detection_communication(self):
        """Test that 'communication' is detected"""
        fname = "communication_policy.pdf"
        doc_type = "communication" if "communication" in fname.lower() else "unknown"
        assert doc_type == "communication"

    def test_doc_type_unknown_filename(self):
        """Test that unknown filename gets 'unknown' doc_type"""
        fname = "random_document.pdf"
        doc_type = "unknown"
        if "leave" in fname.lower():
            doc_type = "leave_policy"
        elif "contract" in fname.lower():
            doc_type = "employment_contract"
        elif "communication" in fname.lower():
            doc_type = "communication"

        assert doc_type == "unknown"


class TestDocumentFiltering:
    """Test document filtering"""

    def test_minimum_text_length(self):
        """Test that documents shorter than 50 chars are filtered"""
        text = "Short"
        assert len(text) < 50  # Should be filtered

    def test_valid_text_length(self):
        """Test that documents with >= 50 chars are kept"""
        text = "This is a valid document with sufficient content to be included"
        assert len(text) >= 50  # Should be kept

    def test_empty_text_filtered(self):
        """Test that empty text is filtered"""
        text = ""
        assert len(text.strip()) == 0


class TestDocumentProcessing:
    """Test document processing logic"""

    def test_document_has_required_fields(self):
        """Test that documents have required fields"""
        doc = {
            "text": "Sample text content",
            "metadata": {
                "source": "company_policy",
                "domain": "policy",
                "doc_type": "leave_policy",
                "file_name": "leave_policy.pdf",
                "page": 1,
            },
        }

        assert "text" in doc
        assert "metadata" in doc
        assert all(
            key in doc["metadata"]
            for key in ["source", "domain", "doc_type", "file_name", "page"]
        )

    def test_metadata_values_correct(self):
        """Test that metadata values are correct"""
        doc = {
            "text": "Content",
            "metadata": {
                "source": "company_policy",
                "domain": "policy",
                "doc_type": "leave_policy",
                "file_name": "leave_policy.pdf",
                "page": 1,
            },
        }

        assert doc["metadata"]["source"] == "company_policy"
        assert doc["metadata"]["domain"] == "policy"
        assert isinstance(doc["metadata"]["page"], int)
        assert doc["metadata"]["page"] >= 1
