"""
FastAPI backend for Project Management App.
Spec: openspec.md
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Project Management API", version="0.1.0")

# Plan persistence: single file (legacy) or plans directory for multiple plans
_BACKEND_DIR = Path(__file__).resolve().parent
PLAN_JSON_PATH = Path(os.environ.get("PLAN_JSON_PATH", _BACKEND_DIR / "data" / "plan.json"))
PLANS_DIR = Path(os.environ.get("PLANS_DIR", _BACKEND_DIR / "data" / "plans"))
PLAN_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
PLANS_DIR.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store with sample mock data
TODOS = [
    {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "title": "Ship the app",
        "completed": False,
        "created_at": "2026-02-19T10:00:00Z",
    },
    {
        "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
        "title": "Write OpenSpec",
        "completed": True,
        "created_at": "2026-02-19T09:00:00Z",
    },
    {
        "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
        "title": "Set up Beads tracker",
        "completed": True,
        "created_at": "2026-02-19T08:30:00Z",
    },
]

# Default OPPM plan (same shape as frontend)
# projectId: unique UUID for sharing/import; projectNumber: optional human-readable id (e.g. 1001)
DEFAULT_PLAN = {
    "projectId": None,  # Set on first save if missing
    "projectNumber": None,  # Optional display number (integer)
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
        {"id": "O1", "title": "Launch pilot in 3 regions", "metric": "3/3 regions operational", "owner": "MS"},
        {"id": "O2", "title": "Complete baseline report", "metric": "Report approved", "owner": "JP"},
        {"id": "O3", "title": "Establish QA process (95% pass)", "metric": "95% pass rate", "owner": "RK"},
        {"id": "O4", "title": "Train 20 field staff", "metric": "20 certified", "owner": "MS"},
        {"id": "O5", "title": "Integrate data into national system", "metric": "API live", "owner": "TL"},
        {"id": "O6", "title": "Publish lessons learned", "metric": "Document released", "owner": "JS"},
    ],
    "matrix": [
        [{"symbol": "○", "label": "Kickoff"}, {"symbol": "●", "label": "Pilot start"}, {"symbol": "●", "label": "3 regions"}, {"symbol": "○", "label": "Handoff"}],
        [{"symbol": "○", "label": "Scoping"}, {"symbol": "○", "label": "Analysis"}, {"symbol": "●", "label": "Draft"}, {"symbol": "●", "label": "Approved"}],
        [{"symbol": "△", "label": "Design QA"}, {"symbol": "○", "label": "Build"}, {"symbol": "○", "label": "Test"}, {"symbol": "●", "label": "95% pass"}],
        [{"symbol": "○", "label": "Curriculum"}, {"symbol": "●", "label": "Week 1–2"}, {"symbol": "●", "label": "Week 3–4"}, {"symbol": "○", "label": "Certify"}],
        [{"symbol": "○", "label": "Specs"}, {"symbol": "○", "label": "Dev"}, {"symbol": "△", "label": "UAT"}, {"symbol": "●", "label": "Live"}],
        [{"symbol": "", "label": ""}, {"symbol": "", "label": ""}, {"symbol": "○", "label": "Draft"}, {"symbol": "●", "label": "Release"}],
    ],
    "owners": [
        {"initials": "JS", "role": "Project Manager"},
        {"initials": "JP", "role": "Lead Analyst"},
        {"initials": "MS", "role": "Field Coordinator"},
        {"initials": "RK", "role": "QA Lead"},
        {"initials": "TL", "role": "Systems Integrator"},
    ],
    "budget": {
        "total": 170000,
        "spent": 38300,
        "categories": [
            {"name": "Personnel", "planned": 120000, "spent": 35000},
            {"name": "Travel", "planned": 15000, "spent": 2100},
            {"name": "Contracts", "planned": 25000, "spent": 0},
            {"name": "Other", "planned": 10000, "spent": 1200},
        ],
    },
    "risks": [
        {"text": "Region 3 staffing gap", "owner": "MS", "mitigation": "Backup contractor identified"},
        {"text": "Data integration delay", "owner": "TL", "mitigation": "Early API testing in Q2"},
        {"text": "Budget overrun risk", "owner": "JS", "mitigation": "10% contingency held"},
    ],
    "kpis": [
        {"label": "Surveys completed", "value": "250 / 400", "target": True},
        {"label": "Data quality pass rate", "value": "92%", "target": False},
        {"label": "Staff trained", "value": "18 / 20", "target": True},
        {"label": "Deliverables on time", "value": "4 / 5", "target": True},
    ],
    "status": {"level": "yellow", "text": "Region 3 data collection delayed 2 weeks; mitigation in progress."},
}


def _plan_path(plan_id: str) -> Path:
    """Path to a plan JSON file in PLANS_DIR. Id is sanitized to filename-safe stem."""
    safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in plan_id).strip() or "default"
    return PLANS_DIR / f"{safe_id}.json"


def _load_plan_file(path: Path) -> dict:
    if not path.exists():
        return DEFAULT_PLAN.copy()
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return DEFAULT_PLAN.copy()


def _load_plan(plan_id: str | None = None) -> dict:
    """Load plan: by id from PLANS_DIR, or fallback to legacy PLAN_JSON_PATH when no id or default missing."""
    if plan_id:
        path = _plan_path(plan_id)
        if plan_id == "default" and not path.exists() and PLAN_JSON_PATH.exists():
            return _load_plan_file(PLAN_JSON_PATH)
        return _load_plan_file(path)
    return _load_plan_file(PLAN_JSON_PATH)


def _save_plan(plan: dict, plan_id: str | None = None) -> None:
    if plan_id:
        path = _plan_path(plan_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2)
        return
    with open(PLAN_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)


def _next_project_number() -> int:
    """Next available projectNumber (max existing + 1, or 1001 if none)."""
    nums = []
    for p in PLANS_DIR.glob("*.json"):
        data = _load_plan_file(p)
        n = data.get("projectNumber")
        if isinstance(n, (int, float)):
            nums.append(int(n))
    return max(nums, default=1000) + 1


def _list_plans() -> list[dict]:
    """List plans from PLANS_DIR (id, title, projectId, projectNumber). If empty, seed default and/or include legacy file."""
    out = []
    for p in sorted(PLANS_DIR.glob("*.json")):
        plan_id = p.stem
        data = _load_plan_file(p)
        title = (data.get("header") or {}).get("projectTitle") or plan_id
        out.append({
            "id": plan_id,
            "title": title,
            "projectId": data.get("projectId"),
            "projectNumber": data.get("projectNumber"),
        })
    if not out and PLAN_JSON_PATH.exists():
        data = _load_plan_file(PLAN_JSON_PATH)
        title = (data.get("header") or {}).get("projectTitle") or "Default"
        out.append({
            "id": "default",
            "title": title,
            "projectId": data.get("projectId"),
            "projectNumber": data.get("projectNumber"),
        })
    if not out:
        # Seed default plan
        _save_plan({**DEFAULT_PLAN}, "default")
        out.append({
            "id": "default",
            "title": (DEFAULT_PLAN.get("header") or {}).get("projectTitle") or "Default",
            "projectId": None,
            "projectNumber": None,
        })
    return out


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    completed: bool = False


class TodoUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    completed: bool | None = None


class TodoResponse(BaseModel):
    id: str
    title: str
    completed: bool
    created_at: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/todos", response_model=list[TodoResponse])
def list_todos():
    return TODOS


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: str):
    for t in TODOS:
        if t["id"] == todo_id:
            return t
    raise HTTPException(status_code=404, detail="Todo not found")


@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(body: TodoCreate):
    todo = {
        "id": str(uuid4()),
        "title": body.title,
        "completed": body.completed,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    TODOS.append(todo)
    return todo


@app.patch("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: str, body: TodoUpdate):
    for i, t in enumerate(TODOS):
        if t["id"] == todo_id:
            if body.title is not None:
                TODOS[i]["title"] = body.title
            if body.completed is not None:
                TODOS[i]["completed"] = body.completed
            return TODOS[i]
    raise HTTPException(status_code=404, detail="Todo not found")


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: str):
    for i, t in enumerate(TODOS):
        if t["id"] == todo_id:
            TODOS.pop(i)
            return
    raise HTTPException(status_code=404, detail="Todo not found")


# --- Plan (OPPM) persistence ---

@app.get("/plans")
def list_plans():
    """List available plans (id and title). From PLANS_DIR; includes legacy single file if no dir entries."""
    return _list_plans()


@app.get("/plan")
def get_plan(plan_id: str | None = None):
    """Return a project plan. Optional query: plan_id (when using multiple plans)."""
    return _load_plan(plan_id)


@app.put("/plan")
def put_plan(plan: dict, plan_id: str | None = None):
    """Save the full project plan. Optional query: plan_id (when using multiple plans).
    Ensures projectId (UUID) and optional projectNumber are set for sharing/identifying projects."""
    if not isinstance(plan, dict):
        raise HTTPException(status_code=422, detail="Body must be a JSON object")
    merged = {**DEFAULT_PLAN, **plan}
    for key in DEFAULT_PLAN:
        if key not in merged or merged[key] is None:
            merged[key] = DEFAULT_PLAN[key]
    # Unique project identifier: UUID so projects are globally identifiable when shared
    if not merged.get("projectId"):
        merged["projectId"] = str(uuid4())
    # Optional human-readable project number (e.g. 1001, 1002) for display/reference; only assign if missing
    if merged.get("projectNumber") is None:
        merged["projectNumber"] = _next_project_number()
    _save_plan(merged, plan_id)
    return merged


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
