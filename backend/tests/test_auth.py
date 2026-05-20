"""Auth tests when AUTH_ENABLED=true (patches module flag, no reload)."""
import pytest

import auth


@pytest.fixture
def auth_enabled(monkeypatch):
    monkeypatch.setattr(auth, "AUTH_ENABLED", True)
    auth._sessions.clear()
    auth._login_attempts.clear()
    yield
    monkeypatch.setattr(auth, "AUTH_ENABLED", False)
    auth._sessions.clear()


def test_login_and_write(client, auth_enabled):
    r = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert r.status_code == 200
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    r2 = client.post("/todos", json={"title": "Auth todo", "completed": False}, headers=headers)
    assert r2.status_code == 201


def test_write_requires_auth_when_enabled(client, auth_enabled):
    r = client.post("/todos", json={"title": "No auth", "completed": False})
    assert r.status_code == 401
