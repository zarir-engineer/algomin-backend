import pytest
from fastapi.testclient import TestClient
from src.algomin.api.routes import app  # or however you expose your FastAPI/Flask app

@pytest.fixture
def client():
    return TestClient(app)

def test_root_endpoint(client):
    resp = client.get("/health")  # adjust to a known route
    assert resp.status_code == 200
