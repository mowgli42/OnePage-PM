# Project Management App — OpenSpec

> Single source-of-truth for architecture, API contracts, and data models.  
> Workflow: Propose changes here → Apply → Update Beads.

---

## 1. System Architecture

```
┌─────────────────────┐     JSON over HTTP      ┌─────────────────────┐
│  Svelte Frontend    │ ◄─────────────────────► │  FastAPI Backend    │
│  - Minimal stores   │  GET/PUT /plan,         │  - JSON file store  │
│  - One-page OPPM    │  GET/POST /todos        │  - Port 8000        │
└─────────────────────┘                         └─────────────────────┘
        Port 5173 (Vite)                                  │
                                                          │
                                                   ┌──────▼──────┐
                                                   │  Mock JSON  │
                                                   │  (no DB)    │
                                                   └─────────────┘
```

- **Frontend**: Svelte + Vite, runs on `http://localhost:5173`
- **Backend**: FastAPI, runs on `http://localhost:8000`
- **Data**: JSON only. No database—todos and plans persist as JSON files under `backend/data/` (configurable via env).

---

## 2. Endpoints

### Todos

| Method | Path | Description |
|--------|------|-------------|
| GET | `/todos` | List all todos |
| GET | `/todos/{id}` | Get one todo by id |
| POST | `/todos` | Create todo (body: `{ title, completed? }`) |
| PATCH | `/todos/{id}` | Update todo (body: partial) |
| DELETE | `/todos/{id}` | Delete todo |

Storage: single file via `TODOS_JSON_PATH` (default `backend/data/todos.json`). Atomic writes with rotating backups (`todos.json.bak.1`, …). On first run with no file, seeds from built-in defaults (same as former in-memory mock data).

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check `{ "status": "ok" }` |

### Plan (OPPM)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/plans` | List available plans: `[{ "id", "title", "projectId", "projectNumber" }, ...]` from PLANS_DIR (or legacy single file as one entry). |
| GET | `/plan` | Get one plan. Query `plan_id` (optional): load from PLANS_DIR or legacy file. |
| PUT | `/plan` | Save the full project plan. Query `plan_id` (optional). Body: plan JSON. |

Storage: multiple plans in directory (env `PLANS_DIR`, default `backend/data/plans/`) as `<id>.json`; or single file via `PLAN_JSON_PATH` (legacy). See [docs/Project-Plan-Persistence-Proposal.md](docs/Project-Plan-Persistence-Proposal.md).

### Error responses

| Status | When | Body |
|--------|------|------|
| 404 | Todo not found (GET/PATCH/DELETE `/todos/{id}`) | `{ "detail": "Todo not found" }` |
| 422 | Validation error (e.g. POST/PATCH body invalid) | `{ "detail": [...] }` (FastAPI validation errors) |

---

## 3. Data Models (JSON Schema)

### Todo

```json
{
  "id": "uuid-string",
  "title": "string (required, min 1, max 200)",
  "completed": "boolean (default false)",
  "created_at": "ISO8601 string"
}
```

### Validation Rules

- `title`: required, 1–200 chars
- `completed`: optional, defaults to `false`
- `id`, `created_at`: server-generated

### Plan (OPPM)

One JSON document with: **`projectId`** (UUID string, unique across projects; set by server on first save if missing), **`projectNumber`** (optional integer, e.g. 1001, for display/reference; server assigns next available if missing), `header`, `quarters`, `objectives`, `matrix`, `owners`, `budget`, `risks`, `kpis`, `status`. PUT merges with server default so partial payloads do not drop sections. Project identifiers support sharing and importing projects across instances.

---

## 4. Display Items (UI)

UI elements derived from the API and data models for the frontend facelift:

| Area | Display items |
|------|----------------|
| **App shell** | App title, subtitle, view switcher (Todos \| OPPM), backend error banner |
| **Todos view** | Add-todo form (input + Add button), todo list (checkbox, title, completed state, delete), empty/loading states |
| **OPPM view** | Action bar (Print one page, Edit plan / Save / Cancel, hint); error/loading messages; edit panel (Header, Status, Budget, Schedule: periods, objectives, matrix); read-only: header block (project, sponsor, PM, dates, period, version); objectives × quarters matrix (symbol + label per cell); owners legend; bottom band: Budget (total, spent, bar, categories), Risks & KPIs, Status & legend (○●△) |

Design system (v2.0): typography (display + body pair), color palette (base, surface, accent), spacing, focus states, print-preserving layout.

---

## 5. Example Payloads

**POST /todos**

```json
{ "title": "Ship the app", "completed": false }
```

**Response (201)**

```json
{
  "id": "a1b2c3d4-...",
  "title": "Ship the app",
  "completed": false,
  "created_at": "2026-02-19T12:00:00Z"
}
```

**GET /todos**

```json
[
  { "id": "...", "title": "Ship the app", "completed": false, "created_at": "..." },
  { "id": "...", "title": "Write OpenSpec", "completed": true, "created_at": "..." }
]
```

---

## 6. Revision Log

| Date | Change |
|------|--------|
| 2026-02-19 | Initial spec: todos CRUD, health, mock data |
| 2026-02-22 | Document error responses (404, 422) |
| 2026-02-22 | Plan (OPPM): GET/PUT /plan, JSON file persistence; proposal for editing and SQLite option |
| 2026-02-22 | Architecture diagram: add GET/PUT /plan; frontend print: one-page landscape, bottom band in two columns (Budget, Risks+Status) |
| 2026-02-22 | Display items (UI): section 4 listing app shell, Todos view, OPPM view; design system v2.0 reference |
| 2026-02-22 | Frontend 2.0 facelift: design system (Fraunces + Source Sans 3, slate/cream/amber), app shell tabs, TodoForm/TodoList/OPPM styling, a11y (focus, aria) |
| 2026-02-22 | Plan: projectId (UUID) and projectNumber; GET /plans returns both; PUT ensures projectId/projectNumber for sharing; README workflow and mock data (4 projects) |
| 2026-05-20 | Todos: persistent JSON file (`TODOS_JSON_PATH`), atomic save, backups, first-run migration from defaults |
