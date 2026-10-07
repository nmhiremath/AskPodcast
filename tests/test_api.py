"""API integration tests."""
from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_health_endpoint():
    """Verify health probe returns status 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "AskPodcast"}


def test_ask_validation_rejects_empty_payload():
    """Verify input validation rejects questions shorter than 3 characters."""
    response = client.post("/ask", json={"question": "hi"})
    assert response.status_code == 422


def test_stream_validation_rejects_empty_payload():
    """Verify streaming endpoint rejects invalid input."""
    response = client.post("/ask/stream", json={"question": "no"})
    assert response.status_code == 422
