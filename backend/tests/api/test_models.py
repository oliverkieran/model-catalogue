"""
Models API Endpoint Tests

Combines unit tests (mocked repositories) and integration tests (real database)
using pytest markers to distinguish between them.

Unit Tests (70%):
- Test HTTP layer concerns without database
- Fast execution with mocked dependencies
- Focus on routing, validation, serialization

Integration Tests (30%):
- Test end-to-end flows with real database
- Verify FastAPI → Repository → Database wiring
- Validate constraints and relationships

Run specific test types:
    pytest -m unit          # Only unit tests
    pytest -m integration   # Only integration tests
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.models.models import Model
from app.db.repositories import ModelRepository


@pytest.mark.unit
class TestModelsEndpointsUnit:
    """Unit tests for /api/v1/models endpoints with mocked repository"""

    @patch("app.api.v1.models.ModelRepository")
    def test_list_models_empty(self, MockRepo: AsyncMock, client: TestClient):
        """Test listing models when database is empty"""
        # Setup mock
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_all.return_value = []
        MockRepo.return_value = mock_repo_instance

        response = client.get("/api/v1/models/")

        assert response.status_code == 200
        assert response.json() == []
        mock_repo_instance.get_all.assert_awaited_once_with(skip=0, limit=10)

    @patch("app.api.v1.models.ModelRepository")
    def test_list_models_with_data(
        self, MockRepo: AsyncMock, client: TestClient, sample_models_list: list[Model]
    ):
        """Test listing models when database has data"""
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_all.return_value = sample_models_list
        MockRepo.return_value = mock_repo_instance

        response = client.get("/api/v1/models/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["name"] == "gpt-test"
        assert data[0]["id"] == 1
        mock_repo_instance.get_all.assert_awaited_once_with(skip=0, limit=10)

    @patch("app.api.v1.models.ModelRepository")
    def test_list_models_pagination(
        self, MockRepo: AsyncMock, client: TestClient, sample_models_list: list[Model]
    ):
        """Test pagination parameters are passed to repository"""
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_all.return_value = sample_models_list[:2]
        MockRepo.return_value = mock_repo_instance

        response = client.get("/api/v1/models/?skip=1&limit=2")

        assert response.status_code == 200
        assert len(response.json()) == 2
        mock_repo_instance.get_all.assert_awaited_once_with(skip=1, limit=2)

    def test_list_models_pagination_invalid_params(self, client: TestClient):
        """Test pagination with invalid parameters returns 422"""
        # Negative skip should fail
        response = client.get("/api/v1/models/?skip=-1")
        assert response.status_code == 422

        # Limit too large should fail
        response = client.get("/api/v1/models/?limit=2000")
        assert response.status_code == 422

    @patch("app.api.v1.models.ModelRepository")
    def test_get_model_by_id(
        self, MockRepo: AsyncMock, client: TestClient, sample_model_data: Model
    ):
        """Test getting a specific model by ID"""
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_id.return_value = sample_model_data
        MockRepo.return_value = mock_repo_instance

        response = client.get(f"/api/v1/models/{sample_model_data.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_model_data.id
        assert data["name"] == sample_model_data.name
        mock_repo_instance.get_by_id.assert_awaited_once_with(sample_model_data.id)

    @patch("app.api.v1.models.ModelRepository")
    def test_get_model_by_id_not_found(self, MockRepo: AsyncMock, client: TestClient):
        """Test getting non-existent model returns 404"""
        # Setup mock to return None (not found)
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_id.return_value = None
        MockRepo.return_value = mock_repo_instance

        response = client.get("/api/v1/models/9999")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    @patch("app.api.v1.models.ModelRepository")
    def test_get_model_by_name(
        self, MockRepo: AsyncMock, client: TestClient, sample_model_data: Model
    ):
        """Test getting a model by its unique name"""
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_name.return_value = sample_model_data
        MockRepo.return_value = mock_repo_instance

        response = client.get(f"/api/v1/models/name/{sample_model_data.name}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_model_data.id
        assert data["name"] == sample_model_data.name
        mock_repo_instance.get_by_name.assert_awaited_once_with(sample_model_data.name)

    @patch("app.api.v1.models.ModelRepository")
    def test_get_model_by_name_not_found(self, MockRepo: AsyncMock, client: TestClient):
        """Test getting non-existent model by name returns 404"""
        # Setup mock to return None (not found)
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_name.return_value = None
        MockRepo.return_value = mock_repo_instance

        response = client.get("/api/v1/models/name/nonexistent-model")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


@pytest.mark.integration
class TestModelsEndpointsIntegration:
    """Integration tests for /api/v1/models endpoints with real database"""

    async def test_list_models_with_real_data(
        self,
        client_with_db: AsyncClient,
        test_session: async_sessionmaker[AsyncSession],
        sample_models: list[Model],
    ):
        """Test listing models with real database data"""
        model_repo = ModelRepository(test_session)
        for model in sample_models:
            await model_repo.create(model)

        response = await client_with_db.get("/api/v1/models/")

        assert response.status_code == 200
        data = response.json()

        # Verify that all our test models are in the response
        # (there might be additional models from production database)
        returned_names = {model["name"] for model in data}
        expected_names = {model.name for model in sample_models}
        assert expected_names.issubset(returned_names), (
            f"Expected models {expected_names} not found in response. "
            f"Got: {returned_names}"
        )

    async def test_pagination_with_real_data(
        self,
        client_with_db: AsyncClient,
        test_session: async_sessionmaker[AsyncSession],
        sample_models: list[Model],
    ):
        """Test that pagination works correctly with real database"""
        # Create test models for pagination testing
        model_repo = ModelRepository(test_session)
        created_models = []
        for model in sample_models:
            created_model = await model_repo.create(model)
            created_models.append(created_model)

        # Test first page (skip=0, limit=2)
        response = await client_with_db.get("/api/v1/models/?skip=0&limit=2")
        assert response.status_code == 200
        page1 = response.json()
        assert len(page1) == 2

        # Test second page (skip=2, limit=1)
        response = await client_with_db.get("/api/v1/models/?skip=2&limit=1")
        assert response.status_code == 200
        page2 = response.json()
        assert len(page2) == 1

        # Verify that page1 and page2 don't overlap
        page1_ids = {model["id"] for model in page1}
        page2_ids = {model["id"] for model in page2}
        assert page1_ids.isdisjoint(
            page2_ids
        ), "Pages should not have overlapping models"

    async def test_get_model_by_id_integration(
        self,
        client_with_db: AsyncClient,
        test_session: async_sessionmaker[AsyncSession],
        sample_models: list[Model],
    ):
        """Test retrieving a specific model by ID with real database"""
        # Create a test model using sample data
        model_repo = ModelRepository(test_session)
        test_model = sample_models[0]  # Use first model from fixture
        created_model = await model_repo.create(test_model)

        # Retrieve the model via API
        response = await client_with_db.get(f"/api/v1/models/{created_model.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_model.id
        assert data["name"] == created_model.name
        assert data["created_at"] is not None

    async def test_get_model_by_name_integration(
        self,
        client_with_db: AsyncClient,
        test_session: async_sessionmaker[AsyncSession],
        sample_models: list[Model],
    ):
        """Test retrieving a model by its unique name with real database"""
        # Create a test model using sample data
        model_repo = ModelRepository(test_session)
        test_model = sample_models[1]  # Use second model from fixture
        created_model = await model_repo.create(test_model)

        # Retrieve the model by name via API
        response = await client_with_db.get(f"/api/v1/models/name/{created_model.name}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_model.id
        assert data["name"] == created_model.name

    async def test_get_nonexistent_model_integration(
        self,
        client_with_db: AsyncClient,
    ):
        """Test that requesting a nonexistent model returns 404"""
        # Use a very large ID that shouldn't exist
        nonexistent_id = 999999999

        response = await client_with_db.get(f"/api/v1/models/{nonexistent_id}")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
        assert str(nonexistent_id) in data["detail"]
