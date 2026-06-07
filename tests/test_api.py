"""Testes básicos da API (não requerem áudio nem LLM)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Audio Summarizer" in response.text
    assert "text/html" in response.headers["content-type"]


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
    assert "whisper_model" in data


def test_summarize_rejects_missing_file():
    response = client.post("/api/v1/summarize")
    assert response.status_code == 422


def test_summarize_rejects_invalid_format():
    response = client.post(
        "/api/v1/summarize",
        files={"audio": ("test.txt", b"not audio", "text/plain")},
    )
    assert response.status_code == 400
