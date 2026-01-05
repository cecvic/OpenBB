import pytest
from fastapi.testclient import TestClient

from archon.api.app import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


class TestAPIEndpoints:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Archon"
        assert "version" in data

    def test_health(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "archon"

    def test_docs_available(self, client):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_available(self, client):
        response = client.get("/redoc")
        assert response.status_code == 200
