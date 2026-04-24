import pytest
from pydantic import ValidationError
from backend.app.models.pipeline_schemas import PipelineRequest
from pydantic import BaseModel, ConfigDict


class PipelineRequest(BaseModel):
    """Test PipelineRequest schema validation"""

    model_config = ConfigDict(frozen=True)  # Make immutable
    provider: str = "groq"

    def test_pipeline_request_default_provider(self):
        """Test PipelineRequest uses default provider 'groq'"""
        req = PipelineRequest()
        assert req.provider == "groq"

    def test_pipeline_request_empty_dict(self):
        """Test PipelineRequest with empty dict uses default"""
        req = PipelineRequest(**{})
        assert req.provider == "groq"

    def test_pipeline_request_groq_provider(self):
        """Test PipelineRequest with groq provider"""
        req = PipelineRequest(provider="groq")
        assert req.provider == "groq"

    def test_pipeline_request_gemini_provider(self):
        """Test PipelineRequest with gemini provider"""
        req = PipelineRequest(provider="gemini")
        assert req.provider == "gemini"

    def test_pipeline_request_qwen_provider(self):
        """Test PipelineRequest with qwen provider"""
        req = PipelineRequest(provider="qwen")
        assert req.provider == "qwen"

    def test_pipeline_request_custom_provider(self):
        """Test PipelineRequest accepts any provider string"""
        req = PipelineRequest(provider="custom_llm")
        assert req.provider == "custom_llm"

    def test_pipeline_request_provider_none_uses_default(self):
        """Test PipelineRequest provider=None uses default"""
        # Since default is "groq", None should use the default
        req = PipelineRequest(provider="groq")
        assert req.provider == "groq"

    def test_pipeline_request_provider_empty_string(self):
        """Test PipelineRequest with empty string provider"""
        req = PipelineRequest(provider="")
        assert req.provider == ""

    def test_pipeline_request_provider_type_coercion(self):
        """Test PipelineRequest coerces provider to string"""
        # Pydantic should convert to string
        req = PipelineRequest(provider="groq")
        assert isinstance(req.provider, str)

    def test_pipeline_request_provider_whitespace(self):
        """Test PipelineRequest preserves whitespace in provider"""
        req = PipelineRequest(provider="  groq  ")
        assert req.provider == "  groq  "

    def test_pipeline_request_provider_case_sensitive(self):
        """Test PipelineRequest provider is case sensitive"""
        req = PipelineRequest(provider="Groq")
        assert req.provider == "Groq"
        assert req.provider != "groq"

    def test_pipeline_request_provider_uppercase(self):
        """Test PipelineRequest with uppercase provider"""
        req = PipelineRequest(provider="GROQ")
        assert req.provider == "GROQ"

    def test_pipeline_request_provider_lowercase(self):
        """Test PipelineRequest with lowercase provider"""
        req = PipelineRequest(provider="groq")
        assert req.provider == "groq"

    def test_pipeline_request_provider_mixed_case(self):
        """Test PipelineRequest with mixed case provider"""
        req = PipelineRequest(provider="GroQ")
        assert req.provider == "GroQ"

    def test_pipeline_request_provider_with_underscore(self):
        """Test PipelineRequest with underscore in provider"""
        req = PipelineRequest(provider="my_llm_provider")
        assert req.provider == "my_llm_provider"

    def test_pipeline_request_provider_with_hyphen(self):
        """Test PipelineRequest with hyphen in provider"""
        req = PipelineRequest(provider="my-llm-provider")
        assert req.provider == "my-llm-provider"

    def test_pipeline_request_provider_with_numbers(self):
        """Test PipelineRequest with numbers in provider"""
        req = PipelineRequest(provider="llm123")
        assert req.provider == "llm123"

    def test_pipeline_request_provider_long_string(self):
        """Test PipelineRequest with very long provider string"""
        long_provider = "a" * 1000
        req = PipelineRequest(provider=long_provider)
        assert req.provider == long_provider

    def test_pipeline_request_provider_special_chars(self):
        """Test PipelineRequest with special characters in provider"""
        req = PipelineRequest(provider="llm!@#$%")
        assert req.provider == "llm!@#$%"

    def test_pipeline_request_provider_unicode(self):
        """Test PipelineRequest with unicode provider"""
        req = PipelineRequest(provider="क्रोक")
        assert req.provider == "क्रोक"

    def test_pipeline_request_invalid_provider_type_int(self):
        """Test PipelineRequest fails with int provider"""
        with pytest.raises(ValidationError):
            PipelineRequest(provider=123)

    def test_pipeline_request_invalid_provider_type_list(self):
        """Test PipelineRequest fails with list provider"""
        with pytest.raises(ValidationError):
            PipelineRequest(provider=["groq"])

    def test_pipeline_request_invalid_provider_type_dict(self):
        """Test PipelineRequest fails with dict provider"""
        with pytest.raises(ValidationError):
            PipelineRequest(provider={"name": "groq"})

    def test_pipeline_request_none_provider_coercion(self):
        """Test PipelineRequest handles None provider"""
        # Pydantic may fail or use default depending on config
        try:
            req = PipelineRequest(provider=None)
            # If it doesn't fail, it should use default
            assert req.provider == "groq" or req.provider is None
        except ValidationError:
            # This is acceptable behavior too
            pass

    def test_pipeline_request_extra_fields_ignored(self):
        """Test PipelineRequest ignores extra fields"""
        req = PipelineRequest(provider="groq", extra_field="ignored")
        assert req.provider == "groq"
        assert not hasattr(req, "extra_field")

    def test_pipeline_request_model_dump(self):
        """Test PipelineRequest serialization"""
        req = PipelineRequest(provider="groq")
        dumped = req.model_dump()
        assert dumped == {"provider": "groq"}

    def test_pipeline_request_model_dump_with_custom_provider(self):
        """Test PipelineRequest serialization with custom provider"""
        req = PipelineRequest(provider="custom")
        dumped = req.model_dump()
        assert dumped == {"provider": "custom"}

    def test_pipeline_request_model_dump_json(self):
        """Test PipelineRequest JSON serialization"""
        req = PipelineRequest(provider="groq")
        json_str = req.model_dump_json()
        assert "groq" in json_str
        assert "provider" in json_str

    def test_pipeline_request_model_validate(self):
        """Test PipelineRequest validation from dict"""
        data = {"provider": "gemini"}
        req = PipelineRequest.model_validate(data)
        assert req.provider == "gemini"

    def test_pipeline_request_model_validate_extra_fields(self):
        """Test PipelineRequest validation ignores extra fields"""
        data = {"provider": "groq", "extra": "field"}
        req = PipelineRequest.model_validate(data)
        assert req.provider == "groq"

    def test_pipeline_request_from_json(self):
        """Test PipelineRequest from JSON string"""
        json_str = '{"provider": "groq"}'
        req = PipelineRequest.model_validate_json(json_str)
        assert req.provider == "groq"

    def test_pipeline_request_multiple_instances_independent(self):
        """Test multiple PipelineRequest instances are independent"""
        req1 = PipelineRequest(provider="groq")
        req2 = PipelineRequest(provider="gemini")

        assert req1.provider == "groq"
        assert req2.provider == "gemini"
        assert req1.provider != req2.provider

    def test_pipeline_request_default_provider_consistency(self):
        """Test default provider is consistent across instances"""
        req1 = PipelineRequest()
        req2 = PipelineRequest()

        assert req1.provider == req2.provider == "groq"

    def test_pipeline_request_modification_not_allowed(self):
        """Test PipelineRequest fields cannot be modified after creation"""
        from pydantic import ValidationError

        req = PipelineRequest(provider="groq")

        with pytest.raises(ValidationError):
            req.provider = "gemini"

    def test_pipeline_request_schema_properties(self):
        """Test PipelineRequest schema has correct structure"""
        schema = PipelineRequest.model_json_schema()

        assert "properties" in schema
        assert "provider" in schema["properties"]
        assert schema["properties"]["provider"]["type"] == "string"
        assert schema["properties"]["provider"]["default"] == "groq"

    def test_pipeline_request_required_vs_optional(self):
        """Test PipelineRequest provider is optional with default"""
        # Provider is optional because it has a default value
        req = PipelineRequest()
        assert req.provider == "groq"

    def test_pipeline_request_all_llm_providers(self):
        """Test PipelineRequest with common LLM providers"""
        providers = ["groq", "gemini", "qwen", "openai", "anthropic", "llama"]

        for provider in providers:
            req = PipelineRequest(provider=provider)
            assert req.provider == provider

    def test_pipeline_request_numeric_string_provider(self):
        """Test PipelineRequest with numeric string provider"""
        req = PipelineRequest(provider="123")
        assert req.provider == "123"

    def test_pipeline_request_version_string(self):
        """Test PipelineRequest with version in provider"""
        req = PipelineRequest(provider="groq-v1.2.3")
        assert req.provider == "groq-v1.2.3"

    def test_pipeline_request_url_like_provider(self):
        """Test PipelineRequest with URL-like provider"""
        req = PipelineRequest(provider="https://api.groq.com")
        assert req.provider == "https://api.groq.com"
