"""
Tests for UseCases API endpoints

Integration tests using real database sessions with rollback.
"""

from app.db.repositories import ModelRepository, UseCaseRepository


class TestUseCasesAPI:
    """Tests for /api/v1/use-cases endpoints"""

    async def test_list_use_cases_empty(self, client_with_db):
        """Test listing use cases when none exist"""
        response = await client_with_db.get("/api/v1/use-cases/")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_use_cases_with_data(
        self, client_with_db, test_session, sample_models, sample_use_case
    ):
        """Test listing use cases with existing data"""
        # Create a model first
        model_repo = ModelRepository(test_session)
        model = await model_repo.create(sample_models[0])

        # Create use case linked to model
        sample_use_case.model_id = model.id
        use_case_repo = UseCaseRepository(test_session)
        await use_case_repo.create(sample_use_case)

        response = await client_with_db.get("/api/v1/use-cases/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["use_case"] == sample_use_case.use_case
        assert data[0]["description"] == sample_use_case.description

    async def test_list_use_cases_filter_by_model_id(
        self, client_with_db, test_session, sample_models
    ):
        """Test filtering use cases by model_id"""
        # Create two models
        model_repo = ModelRepository(test_session)
        model1 = await model_repo.create(sample_models[0])
        model2 = await model_repo.create(sample_models[1])

        # Create use cases for each model
        use_case_repo = UseCaseRepository(test_session)
        from app.models.models import UseCase

        use_case1 = UseCase(use_case="Coding", model_id=model1.id)
        use_case2 = UseCase(use_case="Writing", model_id=model2.id)
        await use_case_repo.create(use_case1)
        await use_case_repo.create(use_case2)

        # Filter by model_id
        response = await client_with_db.get(f"/api/v1/use-cases/?model_id={model1.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["use_case"] == "Coding"

    async def test_get_use_case_by_id(
        self, client_with_db, test_session, sample_models, sample_use_case
    ):
        """Test getting a specific use case by ID"""
        # Create model and use case
        model_repo = ModelRepository(test_session)
        model = await model_repo.create(sample_models[0])

        sample_use_case.model_id = model.id
        use_case_repo = UseCaseRepository(test_session)
        created = await use_case_repo.create(sample_use_case)

        response = await client_with_db.get(f"/api/v1/use-cases/{created.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created.id
        assert data["use_case"] == sample_use_case.use_case

    async def test_get_use_case_not_found(self, client_with_db):
        """Test getting a non-existent use case returns 404"""
        response = await client_with_db.get("/api/v1/use-cases/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_create_use_case_success(
        self, client_with_db, test_session, sample_models
    ):
        """Test creating a new use case"""
        # Create model first
        model_repo = ModelRepository(test_session)
        model = await model_repo.create(sample_models[0])

        use_case_data = {
            "use_case": "Data Analysis",
            "description": "Analyzing large datasets and creating visualizations.",
            "mentioned_by": "Tech Blog",
            "model_id": model.id,
        }

        response = await client_with_db.post("/api/v1/use-cases/", json=use_case_data)
        assert response.status_code == 201
        data = response.json()
        assert data["use_case"] == use_case_data["use_case"]
        assert data["description"] == use_case_data["description"]
        assert data["model_id"] == model.id
        assert "id" in data

    async def test_create_use_case_model_not_found(self, client_with_db):
        """Test creating use case with non-existent model returns 404"""
        use_case_data = {
            "use_case": "Some use case",
            "model_id": 99999,
        }

        response = await client_with_db.post("/api/v1/use-cases/", json=use_case_data)
        assert response.status_code == 404
        assert "Model with id 99999 not found" in response.json()["detail"]

    async def test_update_use_case_success(
        self, client_with_db, test_session, sample_models, sample_use_case
    ):
        """Test updating an existing use case"""
        # Create model and use case
        model_repo = ModelRepository(test_session)
        model = await model_repo.create(sample_models[0])

        sample_use_case.model_id = model.id
        use_case_repo = UseCaseRepository(test_session)
        created = await use_case_repo.create(sample_use_case)

        update_data = {
            "use_case": "Updated Use Case",
            "description": "Updated description",
        }

        response = await client_with_db.patch(
            f"/api/v1/use-cases/{created.id}", json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["use_case"] == "Updated Use Case"
        assert data["description"] == "Updated description"

    async def test_update_use_case_not_found(self, client_with_db):
        """Test updating a non-existent use case returns 404"""
        response = await client_with_db.patch(
            "/api/v1/use-cases/99999", json={"use_case": "New name"}
        )
        assert response.status_code == 404

    async def test_delete_use_case_success(
        self, client_with_db, test_session, sample_models, sample_use_case
    ):
        """Test deleting a use case"""
        # Create model and use case
        model_repo = ModelRepository(test_session)
        model = await model_repo.create(sample_models[0])

        sample_use_case.model_id = model.id
        use_case_repo = UseCaseRepository(test_session)
        created = await use_case_repo.create(sample_use_case)

        response = await client_with_db.delete(f"/api/v1/use-cases/{created.id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = await client_with_db.get(f"/api/v1/use-cases/{created.id}")
        assert get_response.status_code == 404

    async def test_delete_use_case_not_found(self, client_with_db):
        """Test deleting a non-existent use case returns 404"""
        response = await client_with_db.delete("/api/v1/use-cases/99999")
        assert response.status_code == 404


class TestModelUseCasesEndpoint:
    """Tests for /api/v1/models/{model_id}/use-cases endpoint"""

    async def test_get_model_use_cases(
        self, client_with_db, test_session, sample_models, sample_use_case
    ):
        """Test getting use cases for a specific model"""
        # Create model and use case
        model_repo = ModelRepository(test_session)
        model = await model_repo.create(sample_models[0])

        sample_use_case.model_id = model.id
        use_case_repo = UseCaseRepository(test_session)
        await use_case_repo.create(sample_use_case)

        response = await client_with_db.get(f"/api/v1/models/{model.id}/use-cases")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["model_id"] == model.id

    async def test_get_model_use_cases_model_not_found(self, client_with_db):
        """Test getting use cases for non-existent model returns 404"""
        response = await client_with_db.get("/api/v1/models/99999/use-cases")
        assert response.status_code == 404
