"""
Smoke tests — verify the most critical paths respond correctly.
These tests require the database to be reachable (test_readyz included).
"""


def test_healthz(unauthed_client) -> None:
    """Liveness probe should always return 200."""
    res = unauthed_client.get("/healthz")
    assert res.status_code == 200
    assert res.json().get("status") == "ok"


def test_readyz(unauthed_client) -> None:
    """Readiness probe confirms DB connectivity — requires a running DB."""
    res = unauthed_client.get("/readyz")
    assert res.status_code == 200


def test_events_list_no_auth(unauthed_client) -> None:
    """GET /events is a public endpoint and must not require a token."""
    res = unauthed_client.get("/api/v1/events")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_clubs_list_no_auth(unauthed_client) -> None:
    """GET /clubs is a public endpoint and must not require a token."""
    res = unauthed_client.get("/api/v1/clubs")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_profile_requires_auth(unauthed_client) -> None:
    """POST /profiles/me must reject requests with no Authorization header."""
    res = unauthed_client.post(
        "/api/v1/profiles/me",
        json={
            "name": "Ghost User",
            "college": "NIT Agartala",
            "year_of_graduation": "2027",
            "branch": "Computer Science and Engineering",
            "avatar_url": "https://example.com/avatar.png",
        },
    )
    assert res.status_code == 401


def test_chat_conversations_requires_auth(unauthed_client) -> None:
    """GET /chat/conversations must return 401 without a token."""
    res = unauthed_client.get("/api/v1/chat/conversations")
    assert res.status_code == 401


def test_chat_create_conversation_requires_auth(unauthed_client) -> None:
    """POST /chat/conversations must return 401 without a token."""
    res = unauthed_client.post(
        "/api/v1/chat/conversations",
        json={"type": "direct", "member_uids": ["some-uid"]},
    )
    assert res.status_code == 401


def test_chat_send_message_requires_auth(unauthed_client) -> None:
    """POST /chat/conversations/{id}/messages must return 401 without a token."""
    res = unauthed_client.post(
        "/api/v1/chat/conversations/1/messages",
        json={"content": "hello"},
    )
    assert res.status_code == 401
