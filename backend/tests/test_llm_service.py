import pytest
from datetime import date

from app.services.llm_service import LLMService
from app.config import settings


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
