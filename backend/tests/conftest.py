"""
Pytest configuration and shared fixtures
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application
    """
    return TestClient(app)


@pytest.fixture
def sample_model_data():
    """
    Sample model data for testing
    """
    return {
        "name": "gpt-5",
        "organization": "OpenAI",
        "release_date": "2025-08-07",
        "description": "Large multimodal model",
    }
