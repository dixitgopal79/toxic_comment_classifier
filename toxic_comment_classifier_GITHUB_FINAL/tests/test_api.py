from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert "model_loaded" in body
    assert "database_connected" in body

def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200
