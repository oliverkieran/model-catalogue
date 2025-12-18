"""
Tests for main application endpoints
"""

import pytest


def test_root_endpoint(client):
    """Test the root endpoint returns expected response"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


@pytest.mark.slow
def test_placeholder_slow():
    """Example of a slow test (like LLM API calls)"""
    pass
