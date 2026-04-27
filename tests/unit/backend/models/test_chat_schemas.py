import pytest
from pydantic import ValidationError
from backend.app.models.chat_schemas import Message, ChatRequest, ChatResponse

class TestMessage:
    """Test Message schema validation"""

    def test_message_valid_user(self):
        """Test valid user Message"""
        msg = Message(role="user", content="Hello, what is the leave policy?")
        assert msg.role == "user"
        assert msg.content == "Hello, what is the leave policy?"

    def test_message_valid_assistant(self):
        """Test valid assistant Message"""
        msg = Message(role="assistant", content="Based on company policy, you get 20 leave days.")
        assert msg.role == "assistant"
        assert msg.content == "Based on company policy, you get 20 leave days."

    def test_message_missing_role(self):
        """Test Message fails without role"""
        with pytest.raises(ValidationError):
            Message(content="Hello")

    def test_message_missing_content(self):
        """Test Message fails without content"""
        with pytest.raises(ValidationError):
            Message(role="user")

    def test_message_none_role(self):
        """Test Message fails with None role"""
        with pytest.raises(ValidationError):
            Message(role=None, content="Hello")

    def test_message_none_content(self):
        """Test Message fails with None content"""
        with pytest.raises(ValidationError):
            Message(role="user", content=None)

    def test_message_empty_content(self):
        """Test Message allows empty content"""
        msg = Message(role="user", content="")
        assert msg.content == ""

    def test_message_model_dump(self):
        """Test Message serialization"""
        msg = Message(role="user", content="What is the policy?")
        dumped = msg.model_dump()
        assert dumped == {"role": "user", "content": "What is the policy?"}


class TestChatRequest:
    """Test ChatRequest schema validation"""

    def test_chat_request_required_query_only(self):
        """Test ChatRequest with only required query field"""
        req = ChatRequest(query="How many leave days do I get?")
        assert req.query == "How many leave days do I get?"
        assert req.history is None
        assert req.provider is None

    def test_chat_request_query_required(self):
        """Test ChatRequest fails without query"""
        with pytest.raises(ValidationError):
            ChatRequest(history=[], provider="groq")

    def test_chat_request_query_cannot_be_none(self):
        """Test ChatRequest query cannot be None"""
        with pytest.raises(ValidationError):
            ChatRequest(query=None)

    def test_chat_request_with_history(self):
        """Test ChatRequest with history"""
        history = [
            Message(role="user", content="First question?"),
            Message(role="assistant", content="First answer."),
            Message(role="user", content="Follow up?"),
        ]
        req = ChatRequest(query="Next question?", history=history)
        assert req.query == "Next question?"
        assert len(req.history) == 3
        assert req.history[0].role == "user"

    def test_chat_request_history_as_dict(self):
        """Test ChatRequest accepts history as list of dicts"""
        req = ChatRequest(
            query="Test",
            history=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi"}
            ]
        )
        assert len(req.history) == 2
        assert isinstance(req.history[0], Message)

    def test_chat_request_with_provider(self):
        """Test ChatRequest with specified provider"""
        req = ChatRequest(query="Test", provider="groq")
        assert req.provider == "groq"

    def test_chat_request_all_fields(self):
        """Test ChatRequest with all fields specified"""
        history = [Message(role="user", content="Hi")]
        req = ChatRequest(
            query="What is leave policy?",
            history=history,
            provider="groq"
        )
        assert req.query == "What is leave policy?"
        assert len(req.history) == 1
        assert req.provider == "groq"

    def test_chat_request_query_type_validation(self):
        """Test ChatRequest query must be string"""
        with pytest.raises(ValidationError):
            ChatRequest(query=12345)

    def test_chat_request_history_invalid_type(self):
        """Test ChatRequest history must be list"""
        with pytest.raises(ValidationError):
            ChatRequest(query="Test", history="not a list")

    def test_chat_request_history_invalid_item(self):
        """Test ChatRequest history items must be valid Messages"""
        with pytest.raises(ValidationError):
            ChatRequest(
                query="Test",
                history=[{"role": "user"}]  # Missing content
            )

    def test_chat_request_model_dump(self):
        """Test ChatRequest serialization"""
        req = ChatRequest(
            query="Test query",
            history=[Message(role="user", content="Hi")],
            provider="groq"
        )
        dumped = req.model_dump()
        assert dumped["query"] == "Test query"
        assert dumped["provider"] == "groq"


class TestChatResponse:
    """Test ChatResponse schema validation"""

    def test_chat_response_all_required_fields(self):
        """Test ChatResponse with all required fields"""
        response = ChatResponse(
            answer="Employees get 20 leave days per year.",
            sources=["leave_policy.pdf — Page 1", "employee_handbook.pdf — Page 5"],
            context="Leave policy: Employees are entitled to 20 annual leave days.",
            status="ok"
        )
        assert response.answer == "Employees get 20 leave days per year."
        assert len(response.sources) == 2
        assert response.status == "ok"

    def test_chat_response_missing_answer(self):
        """Test ChatResponse fails without answer"""
        with pytest.raises(ValidationError):
            ChatResponse(
                sources=["file.pdf"],
                context="Context",
                status="ok"
            )

    def test_chat_response_missing_sources(self):
        """Test ChatResponse fails without sources"""
        with pytest.raises(ValidationError):
            ChatResponse(
                answer="Answer",
                context="Context",
                status="ok"
            )

    def test_chat_response_missing_context(self):
        """Test ChatResponse fails without context"""
        with pytest.raises(ValidationError):
            ChatResponse(
                answer="Answer",
                sources=[],
                status="ok"
            )

    def test_chat_response_missing_status(self):
        """Test ChatResponse fails without status"""
        with pytest.raises(ValidationError):
            ChatResponse(
                answer="Answer",
                sources=[],
                context="Context"
            )

    def test_chat_response_empty_sources(self):
        """Test ChatResponse with empty sources list"""
        response = ChatResponse(
            answer="I don't know.",
            sources=[],
            context="",
            status="out_of_context"
        )
        assert response.sources == []

    def test_chat_response_empty_strings(self):
        """Test ChatResponse allows empty strings"""
        response = ChatResponse(
            answer="",
            sources=[],
            context="",
            status="error"
        )
        assert response.answer == ""
        assert response.context == ""

    def test_chat_response_status_variations(self):
        """Test ChatResponse with various status values"""
        for status in ["ok", "casual", "identity", "out_of_context"]:
            response = ChatResponse(
                answer="Answer",
                sources=[],
                context="",
                status=status
            )
            assert response.status == status

    def test_chat_response_none_values(self):
        """Test ChatResponse fails with None values"""
        with pytest.raises(ValidationError):
            ChatResponse(answer=None, sources=[], context="", status="ok")
        
        with pytest.raises(ValidationError):
            ChatResponse(answer="Answer", sources=None, context="", status="ok")
        
        with pytest.raises(ValidationError):
            ChatResponse(answer="Answer", sources=[], context=None, status="ok")
        
        with pytest.raises(ValidationError):
            ChatResponse(answer="Answer", sources=[], context="", status=None)

    def test_chat_response_type_validation(self):
        """Test ChatResponse type validation"""
        with pytest.raises(ValidationError):
            ChatResponse(answer=123, sources=[], context="", status="ok")
        
        with pytest.raises(ValidationError):
            ChatResponse(answer="Answer", sources="not_a_list", context="", status="ok")
        
        with pytest.raises(ValidationError):
            ChatResponse(answer="Answer", sources=["file.pdf", 123], context="", status="ok")
        
        with pytest.raises(ValidationError):
            ChatResponse(answer="Answer", sources=[], context=123, status="ok")

    def test_chat_response_multiple_sources(self):
        """Test ChatResponse with multiple sources"""
        sources = [
            "leave_policy.pdf — Page 1",
            "employment_contract.pdf — Page 2",
            "benefits_guide.pdf — Page 5"
        ]
        response = ChatResponse(
            answer="Answer",
            sources=sources,
            context="Context",
            status="ok"
        )
        assert len(response.sources) == 3

    def test_chat_response_model_dump(self):
        """Test ChatResponse serialization"""
        response = ChatResponse(
            answer="Test answer",
            sources=["file.pdf — Page 1"],
            context="Test context",
            status="ok"
        )
        dumped = response.model_dump()
        assert dumped["answer"] == "Test answer"
        assert dumped["status"] == "ok"
        assert len(dumped["sources"]) == 1