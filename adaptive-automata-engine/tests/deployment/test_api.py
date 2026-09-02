"""
Tests for FastAPI HTTP endpoints.
"""

from fastapi.testclient import TestClient
from api.app import app

def test_api_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "healthy"


def test_api_status_endpoint():
    with TestClient(app) as client:
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert "active_model_version" in data
        assert "metrics" in data


def test_api_models_endpoint():
    with TestClient(app) as client:
        response = client.get("/models")
        assert response.status_code == 200
        data = response.json()
        assert "versions" in data
