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

    def test_message_any_role_string(self):
        """Test Message accepts any role string (no enum validation)"""
        msg = Message(role="custom_role", content="Some content")
        assert msg.role == "custom_role"

    def test_message_empty_content(self):
        """Test Message with empty content"""
        msg = Message(role="user", content="")
        assert msg.content == ""

    def test_message_missing_role(self):
        """Test Message fails without role"""
        with pytest.raises(ValidationError) as exc_info:
            Message(content="Hello")
        assert "role" in str(exc_info.value)

    def test_message_missing_content(self):
        """Test Message fails without content"""
        with pytest.raises(ValidationError) as exc_info:
            Message(role="user")
        assert "content" in str(exc_info.value)

    def test_message_none_role(self):
        """Test Message fails with None role"""
        with pytest.raises(ValidationError):
            Message(role=None, content="Hello")

    def test_message_none_content(self):
        """Test Message fails with None content"""
        with pytest.raises(ValidationError):
            Message(role="user", content=None)

    def test_message_role_type_coercion(self):
        """Test Message converts role to string if possible"""
        # Pydantic should convert to string
        msg = Message(role="user", content="test")
        assert isinstance(msg.role, str)

    def test_message_content_type_coercion(self):
        """Test Message converts content to string if possible"""
        msg = Message(role="user", content="test")
        assert isinstance(msg.content, str)

    def test_message_whitespace_handling(self):
        """Test Message preserves whitespace in content"""
        content = "   leading and trailing spaces   "
        msg = Message(role="user", content=content)
        assert msg.content == content

    def test_message_unicode_content(self):
        """Test Message handles unicode content"""
        msg = Message(role="user", content="क्या छुट्टी की नीति है? 你好 مرحبا")
        assert "क्या" in msg.content
        assert "你好" in msg.content
        assert "مرحبا" in msg.content

    def test_message_special_characters(self):
        """Test Message handles special characters"""
        msg = Message(role="user", content="!@#$%^&*()_+-=[]{}|;:',.<>?/")
        assert msg.content == "!@#$%^&*()_+-=[]{}|;:',.<>?/"

    def test_message_long_content(self):
        """Test Message handles long content"""
        long_content = "a" * 10000
        msg = Message(role="user", content=long_content)
        assert len(msg.content) == 10000

    def test_message_newlines_in_content(self):
        """Test Message preserves newlines in content"""
        content = "Line 1\nLine 2\nLine 3"
        msg = Message(role="user", content=content)
        assert "\n" in msg.content

    def test_message_model_dump(self):
        """Test Message serialization with model_dump"""
        msg = Message(role="user", content="What is the policy?")
        dumped = msg.model_dump()
        assert dumped == {"role": "user", "content": "What is the policy?"}

    def test_message_model_dump_json(self):
        """Test Message serialization to JSON"""
        msg = Message(role="user", content="What is the policy?")
        json_str = msg.model_dump_json()
        assert "user" in json_str
        assert "What is the policy?" in json_str


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
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(history=[], provider="groq")
        assert "query" in str(exc_info.value)

    def test_chat_request_query_cannot_be_none(self):
        """Test ChatRequest query cannot be None"""
        with pytest.raises(ValidationError):
            ChatRequest(query=None)

    def test_chat_request_query_cannot_be_empty(self):
        """Test ChatRequest allows empty query string"""
        # Pydantic allows empty strings unless specifically validated
        req = ChatRequest(query="")
        assert req.query == ""

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

    def test_chat_request_empty_history(self):
        """Test ChatRequest with empty history list"""
        req = ChatRequest(query="Test", history=[])
        assert req.history == []

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
        assert req.history[0].role == "user"

    def test_chat_request_provider_optional(self):
        """Test ChatRequest provider is optional"""
        req = ChatRequest(query="Test")
        assert req.provider is None

    def test_chat_request_provider_specified(self):
        """Test ChatRequest with specified provider"""
        for provider in ["groq", "gemini", "qwen"]:
            req = ChatRequest(query="Test", provider=provider)
            assert req.provider == provider

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

    def test_chat_request_provider_type_validation(self):
        """Test ChatRequest provider type coercion"""
        # Pydantic coerces to string
        req = ChatRequest(query="Test", provider="groq")
        assert isinstance(req.provider, str)

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
        assert len(dumped["history"]) == 1

    def test_chat_request_model_dump_json(self):
        """Test ChatRequest JSON serialization"""
        req = ChatRequest(query="Test", provider="groq")
        json_str = req.model_dump_json()
        assert "Test" in json_str
        assert "groq" in json_str

    def test_chat_request_unicode_query(self):
        """Test ChatRequest with unicode query"""
        req = ChatRequest(query="क्या छुट्टी की नीति है? 你好 مرحبا")
        assert "क्या" in req.query

    def test_chat_request_long_query(self):
        """Test ChatRequest with very long query"""
        long_query = "a" * 10000
        req = ChatRequest(query=long_query)
        assert len(req.query) == 10000

    def test_chat_request_special_chars_in_query(self):
        """Test ChatRequest with special characters in query"""
        req = ChatRequest(query="What is <script>alert('xss')</script>?")
        assert "<script>" in req.query

    def test_chat_request_multiline_query(self):
        """Test ChatRequest with multiline query"""
        query = "Line 1\nLine 2\nLine 3"
        req = ChatRequest(query=query)
        assert "\n" in req.query

    def test_chat_request_history_order_preserved(self):
        """Test ChatRequest preserves history order"""
        history = [
            Message(role="user", content="First"),
            Message(role="assistant", content="Reply"),
            Message(role="user", content="Second"),
        ]
        req = ChatRequest(query="Third", history=history)
        assert req.history[0].content == "First"
        assert req.history[1].content == "Reply"
        assert req.history[2].content == "Second"

    def test_chat_request_large_history(self):
        """Test ChatRequest with large history"""
        history = [
            Message(role="user" if i % 2 == 0 else "assistant", content=f"Message {i}")
            for i in range(100)
        ]
        req = ChatRequest(query="New message", history=history)
        assert len(req.history) == 100


class TestChatResponse:
    """Test ChatResponse schema validation"""

    def test_chat_response_all_required_fields(self):
        """Test ChatResponse requires all fields"""
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
        with pytest.raises(ValidationError) as exc_info:
            ChatResponse(
                sources=["file.pdf"],
                context="Context",
                status="ok"
            )
        assert "answer" in str(exc_info.value)

    def test_chat_response_missing_sources(self):
        """Test ChatResponse fails without sources"""
        with pytest.raises(ValidationError) as exc_info:
            ChatResponse(
                answer="Answer",
                context="Context",
                status="ok"
            )
        assert "sources" in str(exc_info.value)

    def test_chat_response_missing_context(self):
        """Test ChatResponse fails without context"""
        with pytest.raises(ValidationError) as exc_info:
            ChatResponse(
                answer="Answer",
                sources=[],
                status="ok"
            )
        assert "context" in str(exc_info.value)

    def test_chat_response_missing_status(self):
        """Test ChatResponse fails without status"""
        with pytest.raises(ValidationError) as exc_info:
            ChatResponse(
                answer="Answer",
                sources=[],
                context="Context"
            )
        assert "status" in str(exc_info.value)

    def test_chat_response_empty_sources(self):
        """Test ChatResponse with empty sources list"""
        response = ChatResponse(
            answer="I don't know.",
            sources=[],
            context="",
            status="out_of_context"
        )
        assert response.sources == []
        assert response.status == "out_of_context"

    def test_chat_response_single_source(self):
        """Test ChatResponse with single source"""
        response = ChatResponse(
            answer="Answer",
            sources=["leave_policy.pdf — Page 1"],
            context="Context",
            status="ok"
        )
        assert len(response.sources) == 1

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

    def test_chat_response_empty_answer(self):
        """Test ChatResponse with empty answer"""
        response = ChatResponse(
            answer="",
            sources=[],
            context="",
            status="error"
        )
        assert response.answer == ""

    def test_chat_response_empty_context(self):
        """Test ChatResponse with empty context"""
        response = ChatResponse(
            answer="Answer",
            sources=[],
            context="",
            status="ok"
        )
        assert response.context == ""

    def test_chat_response_status_ok(self):
        """Test ChatResponse with status='ok'"""
        response = ChatResponse(
            answer="Answer",
            sources=["source.pdf"],
            context="Context",
            status="ok"
        )
        assert response.status == "ok"

    def test_chat_response_status_casual(self):
        """Test ChatResponse with status='casual'"""
        response = ChatResponse(
            answer="Hello!",
            sources=[],
            context="",
            status="casual"
        )
        assert response.status == "casual"

    def test_chat_response_status_identity(self):
        """Test ChatResponse with status='identity'"""
        response = ChatResponse(
            answer="I'm the Wamo Labs assistant.",
            sources=[],
            context="",
            status="identity"
        )
        assert response.status == "identity"

    def test_chat_response_status_out_of_context(self):
        """Test ChatResponse with status='out_of_context'"""
        response = ChatResponse(
            answer="I don't have information about that.",
            sources=[],
            context="",
            status="out_of_context"
        )
        assert response.status == "out_of_context"

    def test_chat_response_any_status_string(self):
        """Test ChatResponse accepts any status string"""
        response = ChatResponse(
            answer="Answer",
            sources=[],
            context="",
            status="custom_status"
        )
        assert response.status == "custom_status"

    def test_chat_response_none_answer(self):
        """Test ChatResponse fails with None answer"""
        with pytest.raises(ValidationError):
            ChatResponse(
                answer=None,
                sources=[],
                context="",
                status="ok"
            )

    def test_chat_response_none_sources(self):
        """Test ChatResponse fails with None sources"""
        with pytest.raises(ValidationError):
            ChatResponse(
                answer="Answer",
                sources=None,
                context="",
                status="ok"
            )

    def test_chat_response_none_context(self):
        """Test ChatResponse fails with None context"""
        with pytest.raises(ValidationError):
            ChatResponse(
                answer="Answer",
                sources=[],
                context=None,
                status="ok"
            )

    def test_chat_response_none_status(self):
        """Test ChatResponse fails with None status"""
        with pytest.raises(ValidationError):
            ChatResponse(
                answer="Answer",
                sources=[],
                context="",
                status=None
            )

    def test_chat_response_answer_type_validation(self):
        """Test ChatResponse answer must be string"""
        with pytest.raises(ValidationError):
            ChatResponse(
                answer=123,
                sources=[],
                context="",
                status="ok"
            )

    def test_chat_response_sources_type_validation(self):
        """Test ChatResponse sources must be list"""
        with pytest.raises(ValidationError):
            ChatResponse(
                answer="Answer",
                sources="not_a_list",
                context="",
                status="ok"
            )

    def test_chat_response_sources_item_type_validation(self):
        """Test ChatResponse source items must be strings"""
        with pytest.raises(ValidationError):
            ChatResponse(
                answer="Answer",
                sources=["file.pdf", 123],  # Invalid item
                context="",
                status="ok"
            )

    def test_chat_response_context_type_validation(self):
        """Test ChatResponse context must be string"""
        with pytest.raises(ValidationError):
            ChatResponse(
                answer="Answer",
                sources=[],
                context=123,
                status="ok"
            )

    def test_chat_response_status_type_validation(self):
        """Test ChatResponse status must be string"""
        with pytest.raises(ValidationError):
            ChatResponse(
                answer="Answer",
                sources=[],
                context="",
                status=123
            )

    def test_chat_response_long_answer(self):
        """Test ChatResponse with very long answer"""
        long_answer = "a" * 10000
        response = ChatResponse(
            answer=long_answer,
            sources=[],
            context="",
            status="ok"
        )
        assert len(response.answer) == 10000

    def test_chat_response_long_context(self):
        """Test ChatResponse with very long context"""
        long_context = "x" * 50000
        response = ChatResponse(
            answer="Answer",
            sources=[],
            context=long_context,
            status="ok"
        )
        assert len(response.context) == 50000

    def test_chat_response_unicode_answer(self):
        """Test ChatResponse with unicode answer"""
        response = ChatResponse(
            answer="क्या छुट्टी की नीति है? 你好 مرحبا",
            sources=[],
            context="",
            status="ok"
        )
        assert "क्या" in response.answer

    def test_chat_response_unicode_source(self):
        """Test ChatResponse with unicode source"""
        response = ChatResponse(
            answer="Answer",
            sources=["नीति.pdf — Page 1", "政策.pdf — Page 2"],
            context="",
            status="ok"
        )
        assert "नीति" in response.sources[0]

    def test_chat_response_unicode_context(self):
        """Test ChatResponse with unicode context"""
        response = ChatResponse(
            answer="Answer",
            sources=[],
            context="कंपनी नीति में बताया गया है कि",
            status="ok"
        )
        assert "कंपनी" in response.context

    def test_chat_response_special_chars_answer(self):
        """Test ChatResponse with special characters"""
        response = ChatResponse(
            answer="Answer with !@#$%^&*() special chars",
            sources=[],
            context="",
            status="ok"
        )
        assert "!@#$%" in response.answer

    def test_chat_response_newlines_in_answer(self):
        """Test ChatResponse preserves newlines"""
        answer = "Line 1\nLine 2\nLine 3"
        response = ChatResponse(
            answer=answer,
            sources=[],
            context="",
            status="ok"
        )
        assert "\n" in response.answer

    def test_chat_response_newlines_in_context(self):
        """Test ChatResponse preserves newlines in context"""
        context = "Context line 1\nContext line 2\nContext line 3"
        response = ChatResponse(
            answer="Answer",
            sources=[],
            context=context,
            status="ok"
        )
        assert "\n" in response.context

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

    def test_chat_response_model_dump_json(self):
        """Test ChatResponse JSON serialization"""
        response = ChatResponse(
            answer="Test answer",
            sources=["file.pdf"],
            context="Test context",
            status="ok"
        )
        json_str = response.model_dump_json()
        assert "Test answer" in json_str
        assert "file.pdf" in json_str

    def test_chat_response_sources_with_page_info(self):
        """Test ChatResponse sources with page information format"""
        sources = [
            "leave_policy.pdf — Page 1",
            "employment_contract.pdf — Page 2-3",
            "benefits_guide.pdf — All Pages"
        ]
        response = ChatResponse(
            answer="Answer",
            sources=sources,
            context="",
            status="ok"
        )
        assert "— Page" in response.sources[0]
        assert "— Page 2-3" in response.sources[1]

    def test_chat_response_large_sources_list(self):
        """Test ChatResponse with many sources"""
        sources = [f"file_{i}.pdf — Page {i}" for i in range(100)]
        response = ChatResponse(
            answer="Answer",
            sources=sources,
            context="",
            status="ok"
        )
        assert len(response.sources) == 100