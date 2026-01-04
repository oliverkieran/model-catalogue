"""
Extraction API Endpoint Tests

Tests the LLM-powered extraction pipeline following the established testing patterns:
- Unit tests with mocked LLM service
- Integration tests with real database
- Helper function tests
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.models import Model
from app.db.repositories import ModelRepository
from app.services.llm_service import ExtractionResult, ExtractedModel


@pytest.fixture
def mock_extraction_result():
    """Mock successful LLM extraction result"""
    extracted = ExtractedModel(
        model_name="gpt-4",
        organization="OpenAI",
        release_date=date(2023, 3, 14),
        description="A large multimodal model",
        license="Proprietary",
    )

    return ExtractionResult(
        data=extracted,
        tokens_used=650,
        model_used="claude-sonnet-4-5",
    )


@pytest.mark.unit
class TestExtractionEndpointUnit:
    """Unit tests for /api/v1/extract endpoint with mocked dependencies"""

    @patch("app.api.v1.models.ModelRepository")
    def test_successful_extraction(
        self,
        MockRepo: AsyncMock,
        client: TestClient,
        mock_extraction_result,
        sample_model_data: Model,
    ):
        """Test successful extraction and model creation"""
        from app.main import app
        from app.services.llm_service import LLMService

        # Mock LLM service
        mock_llm_instance = AsyncMock()
        mock_llm_instance.extract_model_data.return_value = mock_extraction_result

        # Override LLMService dependency
        app.dependency_overrides[LLMService] = lambda: mock_llm_instance

        # Mock repository (to avoid database access)
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_name.return_value = None  # No duplicate
        mock_repo_instance.create.return_value = sample_model_data
        MockRepo.return_value = mock_repo_instance

        try:
            # Make request
            response = client.post(
                "/api/v1/extract",
                json={"text": "GPT-4 was released by OpenAI in March 2023..."},
            )

            # Verify response
            assert response.status_code == 201
            data = response.json()
            assert data["model"]["name"] == sample_model_data.name
            assert data["model"]["organization"] == sample_model_data.organization
            assert data["tokens_used"] == 650
            assert data["llm_model"] == "claude-sonnet-4-5"

            # Verify mocks were called
            mock_llm_instance.extract_model_data.assert_awaited_once()
            mock_repo_instance.get_by_name.assert_awaited_once()
            mock_repo_instance.create.assert_awaited_once()
        finally:
            # Clean up dependency overrides
            app.dependency_overrides.clear()

    def test_extraction_no_data_found(self, client: TestClient):
        """Test extraction when no model information is found"""
        from app.main import app
        from app.services.llm_service import LLMService

        # Mock LLM returning None
        mock_llm_instance = AsyncMock()
        mock_llm_instance.extract_model_data.return_value = ExtractionResult(
            data=None,  # No model found
            tokens_used=200,
            model_used="claude-sonnet-4-5",
        )

        # Override LLMService dependency
        app.dependency_overrides[LLMService] = lambda: mock_llm_instance

        try:
            response = client.post(
                "/api/v1/extract",
                json={"text": "This text has no model information"},
            )

            assert response.status_code == 400
            data = response.json()
            assert "No model information could be extracted" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_extraction_empty_text_validation(self, client: TestClient):
        """Test that empty text fails Pydantic validation"""
        response = client.post(
            "/api/v1/extract",
            json={"text": ""},  # Too short (min_length=10)
        )

        assert response.status_code == 422

    def test_extraction_llm_error(self, client: TestClient):
        """Test extraction when LLM service fails"""
        from app.main import app
        from app.services.llm_service import LLMService

        # Mock LLM raising an exception
        mock_llm_instance = AsyncMock()
        mock_llm_instance.extract_model_data.side_effect = Exception(
            "Claude API timeout"
        )

        # Override LLMService dependency
        app.dependency_overrides[LLMService] = lambda: mock_llm_instance

        try:
            response = client.post(
                "/api/v1/extract",
                json={"text": "GPT-4 by OpenAI..."},
            )

            assert response.status_code == 500
            data = response.json()
            assert "Failed to extract" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    @patch("app.api.v1.models.ModelRepository")
    def test_extraction_duplicate_model(
        self,
        MockRepo: AsyncMock,
        client: TestClient,
        mock_extraction_result,
        sample_model_data: Model,
    ):
        """Test that duplicate model detection works in unit test"""
        from app.main import app
        from app.services.llm_service import LLMService

        # Mock LLM service
        mock_llm_instance = AsyncMock()
        mock_llm_instance.extract_model_data.return_value = mock_extraction_result

        # Override LLMService dependency
        app.dependency_overrides[LLMService] = lambda: mock_llm_instance

        # Mock repository to return existing model (duplicate)
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_name.return_value = sample_model_data
        MockRepo.return_value = mock_repo_instance

        try:
            response = client.post(
                "/api/v1/extract",
                json={"text": "GPT-4 by OpenAI..."},
            )

            assert response.status_code == 409
            data = response.json()
            assert "already exists" in data["detail"].lower()
            mock_repo_instance.get_by_name.assert_awaited_once()
            # create should NOT be called for duplicates
            mock_repo_instance.create.assert_not_awaited()
        finally:
            app.dependency_overrides.clear()


@pytest.mark.slow
@pytest.mark.integration
class TestRealExtractionIntegration:
    """Integration test with real Claude API (marked as slow)"""

    async def test_extract_with_real_llm_api(
        self,
        client_with_db: AsyncClient,
        test_session: async_sessionmaker[AsyncSession],
    ):
        """End-to-end test with real LLM API (costs ~$0.01)"""
        from app.config import settings

        if not settings.anthropic_api_key:
            pytest.skip("ANTHROPIC_API_KEY not configured")

        text = """
        GPT-4 is a large multimodal model developed by OpenAI.
        It was released on March 14, 2023, and represents a significant
        advancement in AI capabilities. The model accepts both text and
        image inputs and produces text outputs. GPT-4 is available under
        a proprietary license via OpenAI's API.
        """

        response = await client_with_db.post(
            "/api/v1/extract",
            json={"text": text},
        )

        assert response.status_code == 201
        data = response.json()

        # Verify extraction accuracy
        assert data["model"]["name"] == "gpt-4"
        assert data["model"]["organization"] == "OpenAI"
        assert data["model"]["release_date"] == "2023-03-14"
        assert "multimodal" in data["model"]["description"].lower()
        assert data["tokens_used"] > 0

        # Clean up - delete created model
        repo = ModelRepository(test_session)
        await repo.delete(data["model"]["id"])
