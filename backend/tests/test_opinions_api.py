"""
Tests for Opinions API endpoints

Integration tests using real database sessions with rollback.
"""

from app.db.repositories import ModelRepository, OpinionRepository


class TestOpinionsAPI:
    """Tests for /api/v1/opinions endpoints"""

    async def test_list_opinions_empty(self, client_with_db):
        """Test listing opinions when none exist"""
        response = await client_with_db.get("/api/v1/opinions/")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_opinions_with_data(
        self, client_with_db, test_session, sample_models, sample_opinion
    ):
        """Test listing opinions with existing data"""
        # Create a model first
        model_repo = ModelRepository(test_session)
        model = await model_repo.create(sample_models[0])

        # Create opinion linked to model
        sample_opinion.model_id = model.id
        opinion_repo = OpinionRepository(test_session)
        await opinion_repo.create(sample_opinion)

        response = await client_with_db.get("/api/v1/opinions/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["content"] == sample_opinion.content
        assert data[0]["sentiment"] == "positive"

    async def test_list_opinions_filter_by_model_id(
        self, client_with_db, test_session, sample_models
    ):
        """Test filtering opinions by model_id"""
        # Create two models
        model_repo = ModelRepository(test_session)
        model1 = await model_repo.create(sample_models[0])
        model2 = await model_repo.create(sample_models[1])

        # Create opinions for each model
        opinion_repo = OpinionRepository(test_session)
        from app.models.models import Opinion

        opinion1 = Opinion(
            content="Opinion for model 1", model_id=model1.id, sentiment="positive"
        )
        opinion2 = Opinion(
            content="Opinion for model 2", model_id=model2.id, sentiment="negative"
        )
        await opinion_repo.create(opinion1)
        await opinion_repo.create(opinion2)

        # Filter by model_id
        response = await client_with_db.get(f"/api/v1/opinions/?model_id={model1.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["content"] == "Opinion for model 1"

    async def test_list_opinions_filter_by_sentiment(
        self, client_with_db, test_session, sample_models
    ):
        """Test filtering opinions by sentiment"""
        # Create model
        model_repo = ModelRepository(test_session)
        model = await model_repo.create(sample_models[0])

        # Create opinions with different sentiments
        opinion_repo = OpinionRepository(test_session)
        from app.models.models import Opinion

        opinion1 = Opinion(
            content="Great model!", model_id=model.id, sentiment="positive"
        )
        opinion2 = Opinion(
            content="Not impressed", model_id=model.id, sentiment="negative"
        )
        await opinion_repo.create(opinion1)
        await opinion_repo.create(opinion2)

        # Filter by sentiment
        response = await client_with_db.get("/api/v1/opinions/?sentiment=positive")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["sentiment"] == "positive"

    async def test_get_opinion_by_id(
        self, client_with_db, test_session, sample_models, sample_opinion
    ):
        """Test getting a specific opinion by ID"""
        # Create model and opinion
        model_repo = ModelRepository(test_session)
        model = await model_repo.create(sample_models[0])

        sample_opinion.model_id = model.id
        opinion_repo = OpinionRepository(test_session)
        created = await opinion_repo.create(sample_opinion)

        response = await client_with_db.get(f"/api/v1/opinions/{created.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created.id
        assert data["content"] == sample_opinion.content

    async def test_get_opinion_not_found(self, client_with_db):
        """Test getting a non-existent opinion returns 404"""
        response = await client_with_db.get("/api/v1/opinions/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_create_opinion_success(
        self, client_with_db, test_session, sample_models
    ):
        """Test creating a new opinion"""
        # Create model first
        model_repo = ModelRepository(test_session)
        model = await model_repo.create(sample_models[0])

        opinion_data = {
            "content": "This is a great model for coding tasks!",
            "sentiment": "positive",
            "source": "Twitter",
            "author": "dev_user",
            "date_published": "2025-01-15",
            "model_id": model.id,
            "tags": ["coding", "productivity"],
        }

        response = await client_with_db.post("/api/v1/opinions/", json=opinion_data)
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == opinion_data["content"]
        assert data["sentiment"] == "positive"
        assert data["model_id"] == model.id
        assert data["tags"] == ["coding", "productivity"]
        assert "id" in data

    async def test_create_opinion_model_not_found(self, client_with_db):
        """Test creating opinion with non-existent model returns 404"""
        opinion_data = {
            "content": "Some opinion",
            "model_id": 99999,
        }

        response = await client_with_db.post("/api/v1/opinions/", json=opinion_data)
        assert response.status_code == 404
        assert "Model with id 99999 not found" in response.json()["detail"]

    async def test_update_opinion_success(
        self, client_with_db, test_session, sample_models, sample_opinion
    ):
        """Test updating an existing opinion"""
        # Create model and opinion
        model_repo = ModelRepository(test_session)
        model = await model_repo.create(sample_models[0])

        sample_opinion.model_id = model.id
        opinion_repo = OpinionRepository(test_session)
        created = await opinion_repo.create(sample_opinion)

        update_data = {"sentiment": "neutral", "content": "Updated content"}

        response = await client_with_db.patch(
            f"/api/v1/opinions/{created.id}", json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] == "neutral"
        assert data["content"] == "Updated content"

    async def test_update_opinion_not_found(self, client_with_db):
        """Test updating a non-existent opinion returns 404"""
        response = await client_with_db.patch(
            "/api/v1/opinions/99999", json={"sentiment": "negative"}
        )
        assert response.status_code == 404

    async def test_delete_opinion_success(
        self, client_with_db, test_session, sample_models, sample_opinion
    ):
        """Test deleting an opinion"""
        # Create model and opinion
        model_repo = ModelRepository(test_session)
        model = await model_repo.create(sample_models[0])

        sample_opinion.model_id = model.id
        opinion_repo = OpinionRepository(test_session)
        created = await opinion_repo.create(sample_opinion)

        response = await client_with_db.delete(f"/api/v1/opinions/{created.id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = await client_with_db.get(f"/api/v1/opinions/{created.id}")
        assert get_response.status_code == 404

    async def test_delete_opinion_not_found(self, client_with_db):
        """Test deleting a non-existent opinion returns 404"""
        response = await client_with_db.delete("/api/v1/opinions/99999")
        assert response.status_code == 404

    async def test_search_opinions(self, client_with_db, test_session, sample_models):
        """Test searching opinions by content"""
        # Create model
        model_repo = ModelRepository(test_session)
        model = await model_repo.create(sample_models[0])

        # Create opinions
        opinion_repo = OpinionRepository(test_session)
        from app.models.models import Opinion

        opinion1 = Opinion(content="Excellent for coding tasks", model_id=model.id)
        opinion2 = Opinion(content="Great for writing essays", model_id=model.id)
        await opinion_repo.create(opinion1)
        await opinion_repo.create(opinion2)

        # Search
        response = await client_with_db.get("/api/v1/opinions/search/?q=coding")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "coding" in data[0]["content"].lower()


class TestModelOpinionsEndpoint:
    """Tests for /api/v1/models/{model_id}/opinions endpoint"""

    async def test_get_model_opinions(
        self, client_with_db, test_session, sample_models, sample_opinion
    ):
        """Test getting opinions for a specific model"""
        # Create model and opinion
        model_repo = ModelRepository(test_session)
        model = await model_repo.create(sample_models[0])

        sample_opinion.model_id = model.id
        opinion_repo = OpinionRepository(test_session)
        await opinion_repo.create(sample_opinion)

        response = await client_with_db.get(f"/api/v1/models/{model.id}/opinions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["model_id"] == model.id

    async def test_get_model_opinions_model_not_found(self, client_with_db):
        """Test getting opinions for non-existent model returns 404"""
        response = await client_with_db.get("/api/v1/models/99999/opinions")
        assert response.status_code == 404
