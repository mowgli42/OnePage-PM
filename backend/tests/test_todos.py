"""Tests for todos API (workflow: list, create, update, delete)."""
import pytest


def test_list_todos(client):
    """GET /todos returns list of todos."""
    r = client.get("/todos")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    for t in data:
        assert "id" in t
        assert "title" in t
        assert "completed" in t
        assert "created_at" in t


def test_create_todo(client):
    """POST /todos creates a todo and returns it."""
    r = client.post("/todos", json={"title": "Test task from workflow", "completed": False})
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Test task from workflow"
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data

    r2 = client.get("/todos")
    titles = [t["title"] for t in r2.json()]
    assert "Test task from workflow" in titles


def test_get_todo_by_id(client):
    """GET /todos/{id} returns one todo."""
    r = client.get("/todos")
    todo = r.json()[0]
    r2 = client.get(f"/todos/{todo['id']}")
    assert r2.status_code == 200
    assert r2.json()["id"] == todo["id"]


def test_patch_todo(client):
    """PATCH /todos/{id} updates todo."""
    r = client.get("/todos")
    todo = r.json()[0]
    r2 = client.patch(f"/todos/{todo['id']}", json={"completed": True})
    assert r2.status_code == 200
    assert r2.json()["completed"] is True


def test_delete_todo(client):
    """DELETE /todos/{id} removes todo."""
    r = client.post("/todos", json={"title": "To delete", "completed": False})
    created = r.json()
    r2 = client.delete(f"/todos/{created['id']}")
    assert r2.status_code == 204
    r3 = client.get("/todos")
    ids = [t["id"] for t in r3.json()]
    assert created["id"] not in ids
