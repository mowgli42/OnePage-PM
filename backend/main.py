"""
FastAPI backend for Project Management App.
Spec: openspec.md
"""
from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field, field_validator

from attachments import AttachmentStore
from audit import list_activity, log_action
from auth import (
    AUTH_ENABLED,
    check_login_allowed,
    load_users,
    login,
    require_admin,
    require_read,
)
from datastore import STORAGE_BACKEND, create_datastore
from exports import plan_to_ical, plan_to_print_html
from notifications import notifications_enabled, notify
from storage import StorageError, dir_disk_usage

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("oppm")

app = FastAPI(title="Project Management API", version="0.2.0")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR", _BACKEND_DIR / "data"))
PLAN_JSON_PATH = Path(os.environ.get("PLAN_JSON_PATH", DATA_DIR / "plan.json"))
PLANS_DIR = Path(os.environ.get("PLANS_DIR", DATA_DIR / "plans"))
ARCHIVE_DIR = Path(os.environ.get("ARCHIVE_DIR", DATA_DIR / "plans_archive"))
TODOS_JSON_PATH = Path(os.environ.get("TODOS_JSON_PATH", DATA_DIR / "todos.json"))
USERS_JSON_PATH = Path(os.environ.get("USERS_JSON_PATH", DATA_DIR / "users.json"))
AUDIT_JSONL_PATH = Path(os.environ.get("AUDIT_JSONL_PATH", DATA_DIR / "audit.jsonl"))
ATTACHMENTS_DIR = Path(os.environ.get("ATTACHMENTS_DIR", DATA_DIR / "attachments"))
ATTACHMENTS_INDEX = ATTACHMENTS_DIR / "index.json"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

for d in (DATA_DIR, PLANS_DIR, ARCHIVE_DIR, ATTACHMENTS_DIR):
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError:
        DATA_DIR = Path("/tmp/oppm_data")
        PLAN_JSON_PATH = DATA_DIR / "plan.json"
        PLANS_DIR = DATA_DIR / "plans"
        ARCHIVE_DIR = DATA_DIR / "plans_archive"
        TODOS_JSON_PATH = DATA_DIR / "todos.json"
        USERS_JSON_PATH = DATA_DIR / "users.json"
        AUDIT_JSONL_PATH = DATA_DIR / "audit.jsonl"
        for d2 in (DATA_DIR, PLANS_DIR, ARCHIVE_DIR):
            d2.mkdir(parents=True, exist_ok=True)
        break

MAX_TODOS = int(os.environ.get("MAX_TODOS", "200"))
MAX_TODO_BACKUPS = int(os.environ.get("MAX_TODO_BACKUPS", "3"))
MAX_PLAN_BACKUPS = int(os.environ.get("MAX_PLAN_BACKUPS", "3"))
MAX_REQUEST_BODY = int(os.environ.get("MAX_REQUEST_BODY", str(1_000_000)))

_default_origins = "http://localhost:5173,http://127.0.0.1:5173"
ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", _default_origins).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.middleware("http")
async def limit_request_body(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_BODY:
        return JSONResponse(status_code=413, content={"detail": "Request body too large"})
    return await call_next(request)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = datetime.now(timezone.utc)
    response = await call_next(request)
    ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
    logger.info("%s %s -> %s (%.0fms)", request.method, request.url.path, response.status_code, ms)
    return response


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_TODOS = [
    {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "title": "Ship the app",
        "completed": False,
        "created_at": "2026-02-19T10:00:00Z",
        "comments": [],
    },
    {
        "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
        "title": "Write OpenSpec",
        "completed": True,
        "created_at": "2026-02-19T09:00:00Z",
        "comments": [],
    },
    {
        "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
        "title": "Set up Beads tracker",
        "completed": True,
        "created_at": "2026-02-19T08:30:00Z",
        "comments": [],
    },
]

DEFAULT_PLAN = {
    "projectId": None,
    "projectNumber": None,
    "archived": False,
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
    "tasks": [],
    "comments": [],
}


# ---------------------------------------------------------------------------
# Datastore (JSON or SQLite)
# ---------------------------------------------------------------------------
def _is_valid_todo(item: object) -> bool:
    return isinstance(item, dict) and all(k in item for k in ("id", "title", "completed", "created_at"))


def _normalize_todos(data: object) -> list[dict]:
    if not isinstance(data, list):
        return [t.copy() for t in DEFAULT_TODOS]
    valid = []
    for t in data:
        if not _is_valid_todo(t):
            continue
        row = dict(t)
        row.setdefault("comments", [])
        valid.append(row)
    return valid if valid else [t.copy() for t in DEFAULT_TODOS]


def _normalize_plan(raw: object) -> dict:
    if not isinstance(raw, dict):
        return DEFAULT_PLAN.copy()
    plan = {**DEFAULT_PLAN, **raw}
    plan.setdefault("archived", False)
    plan.setdefault("tasks", [])
    plan.setdefault("comments", [])
    return plan


STORE = create_datastore(
    data_dir=DATA_DIR,
    todos_path=TODOS_JSON_PATH,
    plans_dir=PLANS_DIR,
    plan_json_path=PLAN_JSON_PATH,
    archive_dir=ARCHIVE_DIR,
    max_todo_backups=MAX_TODO_BACKUPS,
    max_plan_backups=MAX_PLAN_BACKUPS,
    normalize_todos=_normalize_todos,
    normalize_plan=_normalize_plan,
    default_todos=DEFAULT_TODOS,
    default_plan=DEFAULT_PLAN,
)

ATTACHMENTS = AttachmentStore(ATTACHMENTS_DIR, ATTACHMENTS_INDEX)


def _load_todos() -> list[dict]:
    return STORE.load_todos()


def _save_todos(todos: list[dict], user: str = "system") -> None:
    try:
        STORE.save_todos(todos)
        log_action(AUDIT_JSONL_PATH, user=user, action="save", resource="todos")
        notify("todos updated", f"{len(todos)} todos saved", user=user)
    except (StorageError, OSError) as e:
        logger.exception("todo save failed")
        raise HTTPException(status_code=507, detail=str(e)) from e


def reload_todos_from_disk() -> list[dict]:
    global TODOS
    TODOS = _load_todos()
    return TODOS


TODOS = STORE.init_todos()


def _load_plan(plan_id: str | None = None) -> dict:
    return STORE.load_plan(plan_id)


def _save_plan(plan: dict, plan_id: str | None = None, user: str = "system") -> None:
    try:
        STORE.save_plan(plan, plan_id)
        log_action(AUDIT_JSONL_PATH, user=user, action="save", resource=f"plan:{plan_id or 'default'}")
        title = (plan.get("header") or {}).get("projectTitle") or plan_id or "plan"
        notify("plan saved", title, user=user)
    except (StorageError, OSError) as e:
        logger.exception("plan save failed")
        raise HTTPException(status_code=507, detail=str(e)) from e


def _next_project_number() -> int:
    return STORE.next_project_number()


def _list_plans(include_archived: bool = False, search: str = "") -> list[dict]:
    q = search.strip().lower()
    out = STORE.list_plans(include_archived, search)
    if not out and not q:
        _save_plan({**DEFAULT_PLAN}, "default")
        out.append({
            "id": "default",
            "title": (DEFAULT_PLAN.get("header") or {}).get("projectTitle") or "Default",
            "projectId": None,
            "projectNumber": None,
            "archived": False,
        })
    return out


def _sanitize_plan_id(raw: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in raw).strip("-_") or "project"
    return safe[:80]


def _validate_task_dependencies(tasks: list[dict]) -> list[str]:
    warnings: list[str] = []
    ids = {t.get("id") for t in tasks if t.get("id")}
    for t in tasks:
        tid = t.get("id")
        for dep in t.get("dependsOn") or []:
            if dep not in ids:
                warnings.append(f"Task {tid}: missing dependency {dep}")
    # cycle detection (DFS)
    graph: dict[str, list[str]] = {t["id"]: list(t.get("dependsOn") or []) for t in tasks if t.get("id")}
    visiting: set[str] = set()
    done: set[str] = set()

    def visit(n: str) -> bool:
        if n in done:
            return False
        if n in visiting:
            warnings.append(f"Dependency cycle involving task {n}")
            return True
        visiting.add(n)
        for d in graph.get(n, []):
            if d in graph and visit(d):
                pass
        visiting.remove(n)
        done.add(n)
        return False

    for node in graph:
        visit(node)
    return warnings


def _merge_plan(plan_data: dict) -> dict:
    merged = {**DEFAULT_PLAN, **plan_data}
    for key in DEFAULT_PLAN:
        if key not in merged or merged[key] is None:
            merged[key] = DEFAULT_PLAN[key]
    if not merged.get("projectId"):
        merged["projectId"] = str(uuid4())
    if merged.get("projectNumber") is None:
        merged["projectNumber"] = _next_project_number()
    merged.setdefault("archived", False)
    merged.setdefault("tasks", [])
    merged.setdefault("comments", [])
    return merged


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class LoginInput(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=200)


class CommentInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


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
    comments: list[dict] = Field(default_factory=list)


class PlanCreateInput(BaseModel):
    id: str | None = Field(None, max_length=80)
    title: str = Field("New Project", max_length=300)


class PlanMetaPatch(BaseModel):
    title: str | None = Field(None, max_length=300)
    archived: bool | None = None


class TaskInput(BaseModel):
    model_config = {"extra": "ignore"}
    id: str = Field(max_length=50)
    title: str = Field(max_length=300)
    startDate: str = Field("", max_length=50)
    endDate: str = Field("", max_length=50)
    dependsOn: list[str] = Field(default_factory=list, max_length=20)
    progress: int = Field(0, ge=0, le=100)


class PlanHeaderInput(BaseModel):
    model_config = {"extra": "ignore"}
    projectTitle: str = Field("", max_length=300)
    sponsor: str = Field("", max_length=300)
    projectManager: str = Field("", max_length=300)
    startDate: str = Field("", max_length=100)
    endDate: str = Field("", max_length=100)
    reportingPeriod: str = Field("", max_length=100)
    version: str = Field("", max_length=50)
    dateUpdated: str = Field("", max_length=100)


class MatrixCellInput(BaseModel):
    model_config = {"extra": "ignore"}
    symbol: str = Field("", max_length=10)
    label: str = Field("", max_length=200)


class ObjectiveInput(BaseModel):
    model_config = {"extra": "ignore"}
    id: str = Field(max_length=50)
    title: str = Field(max_length=500)
    metric: str = Field("", max_length=300)
    owner: str = Field("", max_length=50)


class OwnerInput(BaseModel):
    model_config = {"extra": "ignore"}
    initials: str = Field(max_length=20)
    role: str = Field("", max_length=200)


class BudgetCategoryInput(BaseModel):
    model_config = {"extra": "ignore"}
    name: str = Field(max_length=200)
    planned: float = Field(0, ge=0, le=1e12)
    spent: float = Field(0, ge=0, le=1e12)


class BudgetInput(BaseModel):
    model_config = {"extra": "ignore"}
    total: float = Field(0, ge=0, le=1e12)
    spent: float = Field(0, ge=0, le=1e12)
    categories: list[BudgetCategoryInput] = Field(default_factory=list, max_length=30)


class RiskInput(BaseModel):
    model_config = {"extra": "ignore"}
    text: str = Field(max_length=500)
    owner: str = Field("", max_length=100)
    mitigation: str = Field("", max_length=500)


class KPIInput(BaseModel):
    model_config = {"extra": "ignore"}
    label: str = Field(max_length=300)
    value: str = Field("", max_length=200)
    target: bool = False


class StatusInput(BaseModel):
    model_config = {"extra": "ignore"}
    level: str = Field("green", max_length=20)
    text: str = Field("", max_length=1000)

    @field_validator("level")
    @classmethod
    def level_values(cls, v: str) -> str:
        if v not in ("green", "yellow", "red"):
            raise ValueError("level must be green, yellow, or red")
        return v


class PlanInput(BaseModel):
    model_config = {"extra": "ignore"}
    projectId: str | None = Field(None, max_length=100)
    projectNumber: int | None = Field(None, ge=0, le=999999)
    archived: bool | None = None
    header: PlanHeaderInput = Field(default_factory=PlanHeaderInput)
    quarters: list[str] = Field(default_factory=list, max_length=24)
    objectives: list[ObjectiveInput] = Field(default_factory=list, max_length=50)
    matrix: list[list[MatrixCellInput]] = Field(default_factory=list, max_length=50)
    owners: list[OwnerInput] = Field(default_factory=list, max_length=50)
    budget: BudgetInput = Field(default_factory=BudgetInput)
    risks: list[RiskInput] = Field(default_factory=list, max_length=30)
    kpis: list[KPIInput] = Field(default_factory=list, max_length=30)
    status: StatusInput = Field(default_factory=StatusInput)
    tasks: list[TaskInput] = Field(default_factory=list, max_length=100)

    @field_validator("quarters")
    @classmethod
    def validate_quarter_labels(cls, v):
        for q in v:
            if len(q) > 100:
                raise ValueError("Time period label too long (max 100 characters)")
        return v

    @field_validator("matrix")
    @classmethod
    def validate_matrix_rows(cls, v):
        for row in v:
            if len(row) > 24:
                raise ValueError("Matrix row too wide (max 24 columns)")
        return v


# ---------------------------------------------------------------------------
# Routes — Auth & health
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    storage = {
        "data": dir_disk_usage(DATA_DIR),
        "plans": dir_disk_usage(PLANS_DIR),
        "todos": dir_disk_usage(TODOS_JSON_PATH.parent),
    }
    return {
        "status": "ok",
        "auth_enabled": AUTH_ENABLED,
        "storage_backend": STORAGE_BACKEND,
        "notifications_enabled": notifications_enabled(),
        "storage": storage,
    }


@app.post("/auth/login")
def auth_login(body: LoginInput, request: Request):
    check_login_allowed(request)
    result = login(body.username, body.password, USERS_JSON_PATH)
    log_action(AUDIT_JSONL_PATH, user=body.username, action="login", resource="auth")
    return result


@app.get("/auth/me")
def auth_me(request: Request, session=Depends(require_read)):
    if not AUTH_ENABLED:
        return {"username": "system", "role": "admin", "auth_enabled": False}
    return {"username": session["username"], "role": session["role"], "auth_enabled": True}


@app.get("/activity")
def activity(limit: int = Query(50, ge=1, le=200), _=Depends(require_read)):
    return list_activity(AUDIT_JSONL_PATH, limit=limit)


# ---------------------------------------------------------------------------
# Routes — Todos
# ---------------------------------------------------------------------------
@app.get("/todos", response_model=list[TodoResponse])
def list_todos(_=Depends(require_read)):
    return TODOS


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: str, _=Depends(require_read)):
    for t in TODOS:
        if t["id"] == todo_id:
            return t
    raise HTTPException(status_code=404, detail="Todo not found")


@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(body: TodoCreate, session=Depends(require_admin)):
    if len(TODOS) >= MAX_TODOS:
        raise HTTPException(status_code=429, detail=f"Todo limit reached ({MAX_TODOS})")
    todo = {
        "id": str(uuid4()),
        "title": body.title,
        "completed": body.completed,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "comments": [],
    }
    TODOS.append(todo)
    _save_todos(TODOS, user=session["username"])
    return todo


@app.patch("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: str, body: TodoUpdate, session=Depends(require_admin)):
    for i, t in enumerate(TODOS):
        if t["id"] == todo_id:
            if body.title is not None:
                TODOS[i]["title"] = body.title
            if body.completed is not None:
                TODOS[i]["completed"] = body.completed
            _save_todos(TODOS, user=session["username"])
            return TODOS[i]
    raise HTTPException(status_code=404, detail="Todo not found")


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: str, session=Depends(require_admin)):
    for i, t in enumerate(TODOS):
        if t["id"] == todo_id:
            TODOS.pop(i)
            _save_todos(TODOS, user=session["username"])
            return
    raise HTTPException(status_code=404, detail="Todo not found")


@app.post("/todos/{todo_id}/comments", status_code=201)
def add_todo_comment(todo_id: str, body: CommentInput, session=Depends(require_admin)):
    for t in TODOS:
        if t["id"] == todo_id:
            comment = {
                "id": str(uuid4()),
                "author": session["username"],
                "text": body.text,
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            t.setdefault("comments", []).append(comment)
            _save_todos(TODOS, user=session["username"])
            return comment
    raise HTTPException(status_code=404, detail="Todo not found")


# ---------------------------------------------------------------------------
# Routes — Plans
# ---------------------------------------------------------------------------
@app.get("/plans")
def list_plans(
    search: str = "",
    include_archived: bool = False,
    _=Depends(require_read),
):
    return _list_plans(include_archived=include_archived, search=search)


@app.get("/plan")
def get_plan(plan_id: str | None = None, _=Depends(require_read)):
    return _load_plan(plan_id)


@app.post("/plan", status_code=201)
def create_plan(body: PlanCreateInput, session=Depends(require_admin)):
    plan_id = _sanitize_plan_id(body.id or body.title or f"project-{uuid4().hex[:8]}")
    if STORE.plan_exists(plan_id):
        raise HTTPException(status_code=409, detail="Plan already exists")
    plan = _merge_plan({
        **DEFAULT_PLAN,
        "header": {**DEFAULT_PLAN["header"], "projectTitle": body.title},
    })
    _save_plan(plan, plan_id, user=session["username"])
    return {"id": plan_id, "plan": plan}


@app.put("/plan")
def put_plan(
    plan: PlanInput,
    plan_id: str | None = None,
    session=Depends(require_admin),
):
    plan_data = plan.model_dump(exclude_unset=True)
    merged = _merge_plan(plan_data)
    warnings = _validate_task_dependencies(merged.get("tasks") or [])
    if warnings:
        logger.warning("plan %s dependency warnings: %s", plan_id, warnings)
    _save_plan(merged, plan_id, user=session["username"])
    return merged


@app.patch("/plan")
def patch_plan_meta(
    body: PlanMetaPatch,
    plan_id: str | None = None,
    session=Depends(require_admin),
):
    if not plan_id:
        raise HTTPException(status_code=400, detail="plan_id query parameter required")
    plan = _load_plan(plan_id)
    if body.title is not None:
        plan.setdefault("header", {})["projectTitle"] = body.title
    if body.archived is not None:
        plan["archived"] = body.archived
    _save_plan(plan, plan_id, user=session["username"])
    return plan


@app.delete("/plan", status_code=204)
def delete_plan(plan_id: str | None = None, session=Depends(require_admin)):
    if not plan_id:
        raise HTTPException(status_code=400, detail="plan_id query parameter required")
    if plan_id == "default":
        raise HTTPException(status_code=400, detail="Cannot delete default plan")
    try:
        STORE.delete_plan(plan_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Plan not found") from None
    log_action(AUDIT_JSONL_PATH, user=session["username"], action="delete", resource=f"plan:{plan_id}")
    return None


@app.post("/plan/duplicate", status_code=201)
def duplicate_plan(
    plan_id: str | None = None,
    new_id: str | None = None,
    session=Depends(require_admin),
):
    if not plan_id:
        raise HTTPException(status_code=400, detail="plan_id query parameter required")
    source = _load_plan(plan_id)
    target_id = _sanitize_plan_id(new_id or f"{plan_id}-copy")
    if STORE.plan_exists(target_id):
        raise HTTPException(status_code=409, detail="Target plan id already exists")
    copy = json.loads(json.dumps(source))
    copy["projectId"] = str(uuid4())
    copy["projectNumber"] = _next_project_number()
    title = (copy.get("header") or {}).get("projectTitle") or target_id
    copy.setdefault("header", {})["projectTitle"] = f"{title} (copy)"
    copy["archived"] = False
    _save_plan(copy, target_id, user=session["username"])
    return {"id": target_id, "plan": copy}


@app.post("/plan/comments", status_code=201)
def add_plan_comment(
    body: CommentInput,
    plan_id: str | None = None,
    session=Depends(require_admin),
):
    if not plan_id:
        raise HTTPException(status_code=400, detail="plan_id query parameter required")
    plan = _load_plan(plan_id)
    comment = {
        "id": str(uuid4()),
        "author": session["username"],
        "text": body.text,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    plan.setdefault("comments", []).append(comment)
    _save_plan(plan, plan_id, user=session["username"])
    return comment


# ---------------------------------------------------------------------------
# Routes — Templates, exports, attachments
# ---------------------------------------------------------------------------
@app.get("/templates")
def list_templates(_=Depends(require_read)):
    out = []
    if TEMPLATES_DIR.exists():
        for p in sorted(TEMPLATES_DIR.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                title = (data.get("header") or {}).get("projectTitle") or p.stem
            except (json.JSONDecodeError, OSError):
                title = p.stem
            out.append({"id": p.stem, "title": title})
    return out


class PlanFromTemplateInput(BaseModel):
    plan_id: str | None = Field(None, max_length=80)
    title: str | None = Field(None, max_length=300)


@app.post("/plan/from-template", status_code=201)
def create_plan_from_template(
    template_id: str = Query(...),
    body: PlanFromTemplateInput | None = None,
    session=Depends(require_admin),
):
    path = TEMPLATES_DIR / f"{_sanitize_plan_id(template_id)}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Template not found")
    try:
        template_data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise HTTPException(status_code=500, detail="Invalid template file") from e
    body = body or PlanFromTemplateInput()
    plan_id = _sanitize_plan_id(body.plan_id or template_id)
    if STORE.plan_exists(plan_id):
        raise HTTPException(status_code=409, detail="Plan already exists")
    merged = _merge_plan(template_data)
    if body.title:
        merged.setdefault("header", {})["projectTitle"] = body.title
    _save_plan(merged, plan_id, user=session["username"])
    return {"id": plan_id, "plan": merged}


@app.get("/plan/export/ical")
def export_plan_ical(plan_id: str | None = None, _=Depends(require_read)):
    pid = plan_id or "default"
    plan = _load_plan(pid)
    content = plan_to_ical(plan, pid)
    return PlainTextResponse(
        content,
        media_type="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="{pid}.ics"'},
    )


@app.get("/plan/export/html")
def export_plan_html(plan_id: str | None = None, _=Depends(require_read)):
    pid = plan_id or "default"
    plan = _load_plan(pid)
    return HTMLResponse(plan_to_print_html(plan, pid))


@app.get("/attachments")
def list_attachments(
    plan_id: str | None = None,
    todo_id: str | None = None,
    _=Depends(require_read),
):
    return ATTACHMENTS.list_for(plan_id=plan_id, todo_id=todo_id)


@app.post("/attachments", status_code=201)
async def upload_attachment(
    file: UploadFile = File(...),
    plan_id: str | None = None,
    todo_id: str | None = None,
    session=Depends(require_admin),
):
    if not plan_id and not todo_id:
        raise HTTPException(status_code=400, detail="plan_id or todo_id required")
    content = await file.read()
    try:
        record = ATTACHMENTS.add(
            file.filename or "upload",
            content,
            plan_id=plan_id,
            todo_id=todo_id,
            user=session["username"],
        )
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e)) from e
    except StorageError as e:
        raise HTTPException(status_code=507, detail=str(e)) from e
    log_action(AUDIT_JSONL_PATH, user=session["username"], action="upload", resource=f"attachment:{record['id']}")
    return record


@app.get("/attachments/{attachment_id}")
def download_attachment(attachment_id: str, _=Depends(require_read)):
    try:
        meta = ATTACHMENTS.get_meta(attachment_id)
        path = ATTACHMENTS.get_path(attachment_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Attachment not found") from None
    return FileResponse(path, filename=meta.get("filename") or path.name)


@app.delete("/attachments/{attachment_id}", status_code=204)
def delete_attachment(attachment_id: str, session=Depends(require_admin)):
    try:
        ATTACHMENTS.delete(attachment_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Attachment not found") from None
    log_action(AUDIT_JSONL_PATH, user=session["username"], action="delete", resource=f"attachment:{attachment_id}")
    return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
