import pytest
from fastapi.testclient import TestClient

from src.core.security import verify_firebase_token
from src.main import app

MOCK_TOKEN = {"uid": "test-uid-123", "email": "test@nitagartala.ac.in"}


@pytest.fixture
def client():
    """TestClient with Firebase token verification bypassed via dependency override."""
    app.dependency_overrides[verify_firebase_token] = lambda: MOCK_TOKEN
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(verify_firebase_token, None)


@pytest.fixture
def unauthed_client():
    """Plain TestClient with no overrides — real 401 behaviour is preserved."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer mock-token-for-testing"}
