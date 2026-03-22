from uuid import uuid4

from fastapi.testclient import TestClient

from src.core.security import verify_firebase_token
from src.main import app

app.dependency_overrides[verify_firebase_token] = lambda: {"uid": "test-user"}
client = TestClient(app)


def test_health_ready_endpoints() -> None:
    health = client.get("/healthz")
    ready = client.get("/readyz")
    assert health.status_code == 200
    assert ready.status_code == 200


def test_create_and_get_club() -> None:
    suffix = uuid4().hex[:8]
    payload = {
        "parent_college": "NIT Agartala",
        "club_name": f"Dev Club {suffix}",
        "club_admin": "Arav",
        "club_admin_email": "admin@example.com",
        "members": 12,
        "description": "Campus development and hackathons community.",
    }

    created = client.post("/api/v1/clubs", json=payload)
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["club_name"] == payload["club_name"]

    fetched = client.get(f"/api/v1/clubs/{body['club_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["c_id"] == body["c_id"]
