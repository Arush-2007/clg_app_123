from uuid import uuid4

from fastapi.testclient import TestClient

from src.core.security import verify_firebase_token
from src.main import app

app.dependency_overrides[verify_firebase_token] = lambda: {"uid": "test-user"}
client = TestClient(app)


def test_create_and_list_events() -> None:
    suffix = uuid4().hex[:6]
    payload = {
        "title": f"TechFest {suffix}",
        "image_url": "https://example.com/event.png",
        "status": "upcoming",
    }
    created = client.post("/api/v1/events", json=payload)
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["title"] == payload["title"]
    assert body["status"] == payload["status"]

    listed = client.get("/api/v1/events?status=upcoming")
    assert listed.status_code == 200
    assert isinstance(listed.json(), list)
