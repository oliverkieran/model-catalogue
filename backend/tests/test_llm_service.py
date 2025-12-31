import pytest
from datetime import date
from unittest.mock import AsyncMock, Mock, patch
from anthropic import RateLimitError, BadRequestError
from anthropic.types import (
    Message,
    Usage
)

from app.services.llm_service import (
    LLMService,
    ExtractedModel,
    ExtractionResult,
    SYSTEM_PROMPT
)

from app.config import settings

@pytest.fixture
def llm_service_mock():
    """Create LLMService with test API key"""
    return LLMService(api_key="test-key-123")


@pytest.fixture
def mock_claude_response():
    """
    Mock Claude API response for successful extraction with structured outputs.

    Simulates the response structure from Claude's beta.messages.parse() API
    including parsed_output and token usage.
    """
    def _create_response(extracted_data: dict):
        """Create a mock response with parsed output"""

        # Create usage stats
        usage = Mock(spec=Usage)
        usage.input_tokens = 500
        usage.output_tokens = 150
        usage.cache_creation_input_tokens = 0
        usage.cache_read_input_tokens = 0

        # Create mock response with parsed_output attribute
        response = Mock()
        response.parsed_output = ExtractedModel(**extracted_data)
        response.usage = usage

        return response

    return _create_response


class TestLLMServiceInitialization:
    """Test service initialization and configuration"""

    def test_init_with_api_key(self):
        """Service initializes with provided API key"""
        service = LLMService(api_key="test-key")
        assert service.api_key == "test-key"
        assert service.model == "claude-sonnet-4-5"

    def test_init_without_api_key_raises_error(self):
        """Service raises error if no API key configured"""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.anthropic_api_key = ""

            with pytest.raises(ValueError, match="API key not configured"):
                LLMService()


class TestModelExtraction:
    """Test model data extraction from text"""

    async def test_extract_complete_model_data(
        self, llm_service_mock, mock_claude_response
    ):
        """Successfully extract complete model information"""

        # Mock API response with complete data
        extracted = {
            "model_name": "gpt-4",
            "organization": "OpenAI",
            "release_date": "2023-03-01",
            "description": "A large multimodal model",
            "license": "Proprietary",
        }

        with patch.object(
            llm_service_mock, "_call_claude_with_retry",
            return_value=mock_claude_response(extracted)
        ):
            result = await llm_service_mock.extract_model_data(
                "GPT-4 was released by OpenAI in March 2023..."
            )

        assert isinstance(result, ExtractionResult)
        assert result.data is not None
        assert result.data.model_name == "gpt-4"
        assert result.data.organization == "OpenAI"
        assert result.data.release_date == date(2023, 3, 1)
        assert result.data.description == "A large multimodal model"
        assert result.data.license == "Proprietary"
        assert result.tokens_used == 650  # 500 + 150
        assert result.model_used == "claude-sonnet-4-5"

    
    async def test_extract_partial_model_data(
        self, llm_service_mock, mock_claude_response
    ):
        """Extract model with only some fields available"""

        # Mock API response with partial data
        extracted = {
            "model_name": "claude-sonnet-3",
            "organization": "Anthropic",
            "release_date": None,
            "description": "Claude Sonnet 3 model by Anthropic",
            "license": None,
        }

        with patch.object(
            llm_service_mock, "_call_claude_with_retry",
            return_value=mock_claude_response(extracted)
        ):
            result = await llm_service_mock.extract_model_data(
                "Claude 3 Sonnet by Anthropic"
            )

        assert result.data is not None
        assert result.data.model_name == "claude-sonnet-3"
        assert result.data.organization == "Anthropic"
        assert result.data.release_date is None


    async def test_extract_empty_text_raises_error(self, llm_service_mock):
        """Empty text raises ValueError"""
        error_message = "Input text for extraction cannot be empty"

        with pytest.raises(ValueError, match=error_message):
            await llm_service_mock.extract_model_data("")

        with pytest.raises(ValueError, match=error_message):
            await llm_service_mock.extract_model_data("   ")


class TestRetryLogic:
    """Test API retry behavior with exponential backoff"""

    async def test_successful_call_no_retry(self, llm_service_mock):
        """Successful API call doesn't trigger retry"""

        mock_response = Mock()
        llm_service_mock.client.messages.create = AsyncMock(return_value=mock_response)

        result = await llm_service_mock._call_claude_with_retry(
            system=[{"type": "text", "text": "test"}],
            messages=[{"role": "user", "content": "test"}]
        )

        assert result == mock_response
        assert llm_service_mock.client.messages.create.call_count == 1


    async def test_rate_limit_retry_success(self, llm_service_mock):
        """Rate limit error triggers retry and succeeds"""
        mock_response = Mock()

        # First call raises RateLimitError, second succeeds
        llm_service_mock.client.messages.create = AsyncMock(
            side_effect=[
                RateLimitError("Rate limit exceeded", response=Mock(), body=None),
                mock_response
            ]
        )

        result = await llm_service_mock._call_claude_with_retry(
            system=[{"type": "text", "text": "test"}],
            messages=[{"role": "user", "content": "test"}],
            initial_delay=0.01  # Fast retry for tests
        )

        assert result == mock_response
        assert llm_service_mock.client.messages.create.call_count == 2

    
    async def test_max_retries_exceeded(self, llm_service_mock):
        """Exhausting all retries raises the error"""
        # All calls raise RateLimitError
        error = RateLimitError("Rate limit exceeded", response=Mock(), body=None)
        llm_service_mock.client.messages.create = AsyncMock(side_effect=error)

        with pytest.raises(RateLimitError):
            await llm_service_mock._call_claude_with_retry(
                system=[{"type": "text", "text": "test"}],
                messages=[{"role": "user", "content": "test"}],
                max_retries=2,
                initial_delay=0.01
            )

        # Called 3 times: initial + 2 retries
        assert llm_service_mock.client.messages.create.call_count == 3

    
    async def test_non_retryable_error_no_retry(self, llm_service_mock):
        """Non-retryable errors (400, 401) don't trigger retry"""
        error = BadRequestError("Invalid request", response=Mock(), body=None)
        llm_service_mock.client.messages.create = AsyncMock(side_effect=error)

        with pytest.raises(BadRequestError):
            await llm_service_mock._call_claude_with_retry(
                system=[{"type": "text", "text": "test"}],
                messages=[{"role": "user", "content": "test"}]
            )

        # Only called once - no retry
        assert llm_service_mock.client.messages.create.call_count == 1
        

@pytest.mark.slow
class TestRealAPIIntegration:
    @pytest.fixture
    def real_llm_service(self):
        """Create LLMService with real API key from settings"""
        from app.config import settings

        if not settings.anthropic_api_key:
            pytest.skip("ANTHROPIC_API_KEY not configured")

        return LLMService()

    async def test_extract_gpt4_announcement(self, real_llm_service):
        """Extract data from GPT-4 announcement text"""

        text = """
        OpenAI announced GPT-4 on March 14, 2023. GPT-4 is a large multimodal
        model that can accept image and text inputs and produce text outputs.
        It exhibits human-level performance on various professional and academic
        benchmarks. GPT-4 is available via API with a proprietary license.
        """

        result = await real_llm_service.extract_model_data(text)

        # Verify extraction
        assert result.data is not None
        assert result.data.model_name == "gpt-4"
        assert result.data.organization == "OpenAI"
        assert result.data.release_date == date(2023, 3, 14)
        assert "multimodal" in result.data.description.lower()
        assert result.data.license == "Proprietary"
