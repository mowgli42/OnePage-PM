"""
Tests for the plan (OPPM) workflow using mock data for different projects.
Verifies: GET /plan (default or saved), PUT /plan (save), persistence across requests.
"""
import pytest


def test_health(client):
    """Health check responds OK."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_get_plan_returns_default_when_no_file(client):
    """GET /plan returns default plan when no plan file exists."""
    r = client.get("/plan")
    assert r.status_code == 200
    data = r.json()
    assert "header" in data
    assert data["header"]["projectTitle"] == "Regional Data Collection Pilot"
    assert "quarters" in data
    assert "objectives" in data
    assert "matrix" in data
    assert len(data["objectives"]) >= 1
    assert len(data["quarters"]) >= 1


def test_put_plan_then_get_returns_saved_project_a(client, mock_plan_project_a):
    """PUT /plan with Project A (Regional Pilot), then GET returns same plan."""
    r = client.put("/plan", json=mock_plan_project_a)
    assert r.status_code == 200
    saved = r.json()
    assert saved["header"]["projectTitle"] == "Regional Data Collection Pilot"
    assert saved["header"]["sponsor"] == "NASS Field Operations"
    assert len(saved["objectives"]) == 2
    assert len(saved["quarters"]) == 4

    r2 = client.get("/plan")
    assert r2.status_code == 200
    loaded = r2.json()
    assert loaded["header"]["projectTitle"] == saved["header"]["projectTitle"]
    assert loaded["header"]["sponsor"] == saved["header"]["sponsor"]
    assert len(loaded["objectives"]) == len(saved["objectives"])
    assert loaded["objectives"][0]["id"] == "O1"
    assert loaded["objectives"][0]["title"] == "Launch pilot in 3 regions"


def test_put_plan_then_get_returns_saved_project_b(client, mock_plan_project_b):
    """PUT /plan with Project B (IT Migration), then GET returns same plan."""
    r = client.put("/plan", json=mock_plan_project_b)
    assert r.status_code == 200
    saved = r.json()
    assert saved["header"]["projectTitle"] == "IT Migration Project"
    assert saved["header"]["projectManager"] == "Alex Chen"
    assert len(saved["objectives"]) == 2
    assert saved["quarters"] == ["Q1 2026", "Q2 2026", "Q3 2026"]

    r2 = client.get("/plan")
    assert r2.status_code == 200
    loaded = r2.json()
    assert loaded["header"]["projectTitle"] == "IT Migration Project"
    assert loaded["status"]["level"] == "green"
    assert loaded["status"]["text"] == "On schedule."


def test_put_plan_then_get_returns_saved_project_c(client, mock_plan_project_c):
    """PUT /plan with Project C (Grant Proposal), then GET returns same plan."""
    r = client.put("/plan", json=mock_plan_project_c)
    assert r.status_code == 200
    saved = r.json()
    assert saved["header"]["projectTitle"] == "Grant Proposal – Research Pilot"
    assert len(saved["objectives"]) == 1
    assert saved["objectives"][0]["title"] == "Submit proposal"
    assert len(saved["quarters"]) == 2

    r2 = client.get("/plan")
    assert r2.status_code == 200
    loaded = r2.json()
    assert loaded["header"]["projectTitle"] == saved["header"]["projectTitle"]
    assert loaded["budget"]["total"] == 75000
    assert loaded["budget"]["spent"] == 0


def test_plan_workflow_switch_projects(client, mock_plan_project_a, mock_plan_project_b):
    """Save Project A, GET returns A; then save Project B, GET returns B."""
    client.put("/plan", json=mock_plan_project_a)
    r = client.get("/plan")
    assert r.json()["header"]["projectTitle"] == "Regional Data Collection Pilot"

    client.put("/plan", json=mock_plan_project_b)
    r = client.get("/plan")
    assert r.json()["header"]["projectTitle"] == "IT Migration Project"


def test_put_plan_merges_with_default(client, mock_plan_project_a):
    """PUT with partial plan merges with default so missing sections are preserved."""
    # Send only header and status
    partial = {
        "header": {"projectTitle": "Minimal Project", "sponsor": "X", "projectManager": "Y", "startDate": "2026-01-01", "endDate": "2026-12-31", "reportingPeriod": "Q1", "version": "v1", "dateUpdated": "today"},
        "status": {"level": "green", "text": "OK"},
    }
    r = client.put("/plan", json=partial)
    assert r.status_code == 200
    data = r.json()
    assert data["header"]["projectTitle"] == "Minimal Project"
    # Backend merges with DEFAULT_PLAN so quarters/objectives/matrix etc. exist
    assert "quarters" in data
    assert "objectives" in data
    assert "matrix" in data
    assert "budget" in data
