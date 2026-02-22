"""
Pytest configuration and fixtures. Uses a temp plan file so tests don't touch real data.
Set PLAN_JSON_PATH before main is imported so the app uses the test file.
"""
import os
import tempfile
from pathlib import Path

import pytest

# Set env before any test (or main) imports the app
_TEST_PLAN_DIR = Path(tempfile.mkdtemp(prefix="oppm_test_"))
_TEST_PLAN_PATH = _TEST_PLAN_DIR / "plan.json"
os.environ["PLAN_JSON_PATH"] = str(_TEST_PLAN_PATH)


@pytest.fixture
def plan_file():
    """Path to the test plan file."""
    return _TEST_PLAN_PATH


@pytest.fixture(autouse=True)
def reset_plan_file(plan_file):
    """Remove plan file before each test so GET /plan returns default unless we PUT."""
    if plan_file.exists():
        plan_file.unlink()
    yield
    if plan_file.exists():
        plan_file.unlink(missing_ok=True)


@pytest.fixture
def client(reset_plan_file):
    """FastAPI test client. Import app after env is set."""
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


@pytest.fixture
def mock_plan_project_a():
    """Mock plan: Regional Data Collection Pilot (default-style)."""
    return {
        "header": {
            "projectTitle": "Regional Data Collection Pilot",
            "sponsor": "NASS Field Operations",
            "projectManager": "Jane Smith",
            "startDate": "Jan 1, 2026",
            "endDate": "Dec 31, 2026",
            "reportingPeriod": "FY Q2 2026",
            "version": "v1.0",
            "dateUpdated": "Feb 19, 2026",
        },
        "quarters": ["Q1 2026", "Q2 2026", "Q3 2026", "Q4 2026"],
        "objectives": [
            {"id": "O1", "title": "Launch pilot in 3 regions", "metric": "3/3 operational", "owner": "MS"},
            {"id": "O2", "title": "Complete baseline report", "metric": "Report approved", "owner": "JP"},
        ],
        "matrix": [
            [{"symbol": "○", "label": "Kickoff"}, {"symbol": "●", "label": "Live"}, {"symbol": "", "label": ""}, {"symbol": "", "label": ""}],
            [{"symbol": "○", "label": "Scoping"}, {"symbol": "○", "label": "Draft"}, {"symbol": "●", "label": "Approved"}, {"symbol": "", "label": ""}],
        ],
        "owners": [{"initials": "JS", "role": "PM"}, {"initials": "MS", "role": "Field"}],
        "budget": {"total": 100000, "spent": 25000, "categories": [{"name": "Personnel", "planned": 80000, "spent": 20000}, {"name": "Other", "planned": 20000, "spent": 5000}]},
        "risks": [{"text": "Staffing gap", "owner": "MS", "mitigation": "Backup identified"}],
        "kpis": [{"label": "Surveys done", "value": "100/200", "target": False}],
        "status": {"level": "yellow", "text": "On track with minor delay."},
    }


@pytest.fixture
def mock_plan_project_b():
    """Mock plan: IT Migration Project (different project)."""
    return {
        "header": {
            "projectTitle": "IT Migration Project",
            "sponsor": "IT Operations",
            "projectManager": "Alex Chen",
            "startDate": "Mar 1, 2026",
            "endDate": "Aug 31, 2026",
            "reportingPeriod": "Q2 2026",
            "version": "v0.2",
            "dateUpdated": "Feb 22, 2026",
        },
        "quarters": ["Q1 2026", "Q2 2026", "Q3 2026"],
        "objectives": [
            {"id": "O1", "title": "Migrate core systems", "metric": "Zero downtime", "owner": "AC"},
            {"id": "O2", "title": "User acceptance testing", "metric": "UAT sign-off", "owner": "BD"},
        ],
        "matrix": [
            [{"symbol": "●", "label": "Done"}, {"symbol": "○", "label": "In progress"}, {"symbol": "", "label": ""}],
            [{"symbol": "", "label": ""}, {"symbol": "○", "label": "UAT start"}, {"symbol": "○", "label": "Sign-off"}],
        ],
        "owners": [{"initials": "AC", "role": "Tech Lead"}, {"initials": "BD", "role": "QA"}],
        "budget": {"total": 50000, "spent": 12000, "categories": [{"name": "Infrastructure", "planned": 30000, "spent": 10000}]},
        "risks": [],
        "kpis": [{"label": "Systems migrated", "value": "2/5", "target": True}],
        "status": {"level": "green", "text": "On schedule."},
    }


@pytest.fixture
def mock_plan_project_c():
    """Mock plan: Grant Proposal (minimal schedule)."""
    return {
        "header": {
            "projectTitle": "Grant Proposal – Research Pilot",
            "sponsor": "Funding Office",
            "projectManager": "Dr. Lee",
            "startDate": "Apr 1, 2026",
            "endDate": "Sep 30, 2026",
            "reportingPeriod": "Q2 2026",
            "version": "v0.1",
            "dateUpdated": "Feb 20, 2026",
        },
        "quarters": ["Q2 2026", "Q3 2026"],
        "objectives": [{"id": "O1", "title": "Submit proposal", "metric": "Submitted", "owner": "DL"}],
        "matrix": [[{"symbol": "●", "label": "Submitted"}, {"symbol": "○", "label": "Review"}]],
        "owners": [{"initials": "DL", "role": "PI"}],
        "budget": {"total": 75000, "spent": 0, "categories": [{"name": "Research", "planned": 75000, "spent": 0}]},
        "risks": [{"text": "Deadline", "owner": "DL", "mitigation": "Draft ready"}],
        "kpis": [],
        "status": {"level": "green", "text": "Proposal drafted."},
    }
