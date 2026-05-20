"""Tests for extended plan CRUD endpoints."""


def test_create_and_delete_plan(client):
    r = client.post("/plan", json={"title": "CRUD Test Project", "id": "crud-test"})
    assert r.status_code == 201
    plan_id = r.json()["id"]
    assert plan_id == "crud-test"

    r2 = client.get(f"/plan?plan_id={plan_id}")
    assert r2.status_code == 200
    assert r2.json()["header"]["projectTitle"] == "CRUD Test Project"

    r3 = client.delete(f"/plan?plan_id={plan_id}")
    assert r3.status_code == 204


def test_duplicate_plan(client):
    body = {"title": "Dup Source", "id": "dup-src"}
    client.post("/plan", json=body)
    r = client.post("/plan/duplicate?plan_id=dup-src")
    assert r.status_code == 201
    new_id = r.json()["id"]
    assert new_id != "dup-src"
    assert "copy" in r.json()["plan"]["header"]["projectTitle"].lower()


def test_health_includes_storage(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "storage" in data
