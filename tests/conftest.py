import pytest
import tempfile
import numpy as np
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# SAMPLE DATA FIXTURES

@pytest.fixture
def sample_texts():
    """Sample texts for testing"""
    return [
        "Leave policy states that employees get 20 annual leave days",
        "The notice period for resignation is 30 days",
        "Communication allowance is Rs. 5000 per month",
        "Employees can carry forward up to 10 unused leave days",
    ]


@pytest.fixture
def sample_documents():
    """Sample documents with metadata"""
    return [
        {
            "text": "Employees are entitled to 20 leave days per year. This includes annual leave.",
            "metadata": {
                "source": "company_policy",
                "domain": "policy",
                "doc_type": "leave_policy",
                "file_name": "leave_policy.pdf",
                "page": 1,
            },
        },
        {
            "text": "The notice period for resignation is 30 days from the date of submission.",
            "metadata": {
                "source": "company_policy",
                "domain": "policy",
                "doc_type": "employment_contract",
                "file_name": "employment_contract.pdf",
                "page": 2,
            },
        },
        {
            "text": "All employees receive a communication allowance of Rs. 5000 per month.",
            "metadata": {
                "source": "company_policy",
                "domain": "policy",
                "doc_type": "communication",
                "file_name": "communication.pdf",
                "page": 1,
            },
        },
    ]


@pytest.fixture
def sample_embeddings():
    """Generate sample embeddings (384-dimensional for bge-large)"""
    # Simulate 4 embeddings of dimension 384
    np.random.seed(42)
    return np.random.randn(4, 384).astype("float32")


@pytest.fixture
def temp_vector_store_dir():
    """Create temporary directory for vector store files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_pdf_dir():
    """Create temporary directory for test PDFs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir
@pytest.fixture
def mock_embedder():
    """Mock embedder for testing"""
    embedder = Mock()
    embedder.embed_texts = Mock(return_value=np.random.randn(4,1024).astype("float32"))
    embedder.embed_query = Mock(return_value=np.random.randn(1024).astype("float32"))
    return embedder


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing"""
    vector_store = Mock()
    vector_store.search = Mock(return_value=[
        {
            "text": "Employees get 20 leave days per year",
            "metadata": {"file_name": "leave_policy.pdf", "page": 1, "doc_type": "leave_policy"},
            "score": 0.95
        },
        {
            "text": "Notice period is 30 days",
            "metadata": {"file_name": "employment_contract.pdf", "page": 2, "doc_type": "employment_contract"},
            "score": 0.87
        }
    ])
    vector_store.add_embeddings = Mock()
    vector_store.save = Mock()
    vector_store.load = Mock()
    return vector_store


@pytest.fixture
def mock_reranker():
    """Mock reranker for testing"""
    reranker = Mock()
    reranker.rerank = Mock(return_value=[
        {
            "text": "Employees get 20 leave days per year",
            "metadata": {"file_name": "leave_policy.pdf", "page": 1, "doc_type": "leave_policy"},
            "score": 0.95
        }
    ])
    return reranker


@pytest.fixture
def mock_bm25():
    """Mock BM25 retriever for testing"""
    bm25 = Mock()
    bm25.search = Mock(return_value=[
        {"text": "Leave policy information", "score": 0.9},
        {"text": "Notice period details", "score": 0.85}
    ])
    return bm25


@pytest.fixture
def mock_llm():
    """Mock LLM for testing"""
    llm = Mock()
    llm.generate = Mock(return_value="Based on the company policy, employees get 20 annual leave days.")
    llm.generate_raw = Mock(return_value="policy")
    llm.generate_stream = Mock(return_value=iter([
        "Based on ",
        "the company ",
        "policy, employees ",
        "get 20 annual ",
        "leave days."
    ]))
    return llm


@pytest.fixture
def sample_chat_request():
    """Sample chat request payload"""
    return {
        "query": "How many leave days do I get?",
        "provider": "groq",
        "history": []
    }


@pytest.fixture
def sample_chat_request_with_history():
    """Sample chat request with conversation history"""
    return {
        "query": "What about notice period?",
        "provider": "groq",
        "history": [
            {"role": "user", "content": "How many leave days do I get?"},
            {"role": "assistant", "content": "You get 20 annual leave days."}
        ]
    }


@pytest.fixture
def sample_pipeline_request():
    """Sample pipeline request payload"""
    return {
        "provider": "groq"
    }


@pytest.fixture
def mock_get_pipeline():
    """Mock get_pipeline function"""
    with patch("backend.app.core.pipeline.get_pipeline") as mock:
        mock.return_value = (
            Mock(),  # embedder
            Mock(),  # vector_store
            Mock(),  # llm
            Mock(),  # reranker
            Mock(),  # bm25
            42       # chunk_count
        )
        yield mock


@pytest.fixture
def mock_pipeline_functions():
    """Mock all pipeline-related functions"""
    with patch("backend.app.core.pipeline.reset_pipeline") as mock_reset, \
         patch("backend.app.core.pipeline.pipeline_status") as mock_status:
        mock_status.return_value = {"ready": True, "chunk_count": 42}
        yield {
            "reset_pipeline": mock_reset,
            "pipeline_status": mock_status
        }


@pytest.fixture
def mock_run_rag():
    """Mock run_rag function"""
    with patch("backend.app.core.rag_service.run_rag") as mock:
        mock.return_value = (
            "Based on company policy, employees get 20 annual leave days.",
            ["leave_policy.pdf — Page 1"],
            "Employees are entitled to 20 leave days per year.",
            "ok"
        )
        yield mock


@pytest.fixture
def mock_run_rag_stream():
    """Mock run_rag_stream function"""
    def stream_generator():
        yield ("token", {"delta": "Based on "})
        yield ("token", {"delta": "the company "})
        yield ("token", {"delta": "policy..."})
        yield ("done", {
            "answer": "Based on the company policy...",
            "sources": ["leave_policy.pdf — Page 1"],
            "context": "Employees are entitled to 20 leave days per year.",
            "status": "ok"
        })
    
    with patch("backend.app.core.rag_service.run_rag_stream") as mock:
        mock.return_value = stream_generator()
        yield mock