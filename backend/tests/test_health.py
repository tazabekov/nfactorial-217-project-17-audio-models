from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "asr_provider" in body
    assert "tts_provider" in body


def test_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
