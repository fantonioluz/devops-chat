import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["status"] == "running"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_endpoint_structure():
    # Test if endpoint exists and accepts proper structure
    response = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "O que é DevOps?"}
            ]
        }
    )
    # Can be 200 or 500 depending on API key, but endpoint should exist
    assert response.status_code in [200, 500]


def test_chat_invalid_payload():
    response = client.post(
        "/chat",
        json={}
    )
    assert response.status_code == 422  # Validation error
