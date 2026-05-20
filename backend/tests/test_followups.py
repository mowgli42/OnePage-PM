"""Tests for follow-up features: templates, exports, attachments, SQLite."""
import json
import os

import pytest


def test_list_templates(client):
    r = client.get("/templates")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert any(t["id"] == "product-launch" for t in data)


def test_create_plan_from_template(client):
    r = client.post("/plan/from-template?template_id=grant-proposal", json={"plan_id": "from-tpl-test"})
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == "from-tpl-test"
    r2 = client.get("/plan?plan_id=from-tpl-test")
    assert "Grant" in r2.json()["header"]["projectTitle"]


def test_export_ical(client):
    client.post("/plan", json={"title": "iCal Test", "id": "ical-test"})
    r = client.get("/plan/export/ical?plan_id=ical-test")
    assert r.status_code == 200
    assert "BEGIN:VCALENDAR" in r.text


def test_export_html(client):
    r = client.get("/plan/export/html?plan_id=default")
    assert r.status_code == 200
    assert "<html" in r.text.lower()


def test_attachment_upload_list_delete(client):
    r = client.post(
        "/attachments",
        params={"plan_id": "default"},
        files={"file": ("notes.txt", b"hello attachment", "text/plain")},
    )
    assert r.status_code == 201
    att_id = r.json()["id"]
    r2 = client.get("/attachments", params={"plan_id": "default"})
    assert any(a["id"] == att_id for a in r2.json())
    r3 = client.get(f"/attachments/{att_id}")
    assert r3.status_code == 200
    r4 = client.delete(f"/attachments/{att_id}")
    assert r4.status_code == 204


def test_sqlite_datastore_roundtrip(tmp_path):
    from datastore import SqliteDatastore
    from main import DEFAULT_PLAN, DEFAULT_TODOS, _normalize_plan, _normalize_todos

    store = SqliteDatastore(
        tmp_path / "oppm.db",
        todos_path=tmp_path / "todos.json",
        plans_dir=tmp_path / "plans",
        plan_json_path=tmp_path / "plan.json",
        archive_dir=tmp_path / "archive",
        max_todo_backups=1,
        max_plan_backups=1,
        normalize_todos=_normalize_todos,
        normalize_plan=_normalize_plan,
        default_todos=DEFAULT_TODOS,
        default_plan=DEFAULT_PLAN,
    )
    store.save_todos([{"id": "1", "title": "A", "completed": False, "created_at": "2026-01-01T00:00:00Z", "comments": []}])
    assert len(store.load_todos()) == 1
    store.save_plan(_normalize_plan({**DEFAULT_PLAN, "header": {**DEFAULT_PLAN["header"], "projectTitle": "SQLite Plan"}}), "sqlite-plan")
    loaded = store.load_plan("sqlite-plan")
    assert loaded["header"]["projectTitle"] == "SQLite Plan"
