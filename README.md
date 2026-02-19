# Project Management App

A simple full-stack one-page project management app built with **Svelte** (frontend), **FastAPI** (backend), and a **vibe coding workflow** using **OpenSpec** and **Beads**.

---

## Project Structure

```
.
├── openspec.md           # Single source-of-truth: architecture, endpoints, data models
├── .beads/
│   └── beads.toml        # Beads task tracker (dependencies, status)
├── scripts/
│   └── bd-ready.sh       # List unblocked tasks (bd ready)
├── backend/
│   ├── main.py           # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.svelte
│   │   ├── stores/todos.js
│   │   └── components/
│   │       ├── TodoForm.svelte
│   │       └── TodoList.svelte
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
└── README.md
```

---

## Setup Instructions

### Prerequisites

- Node.js 18+
- Python 3.10+
- (Optional) Rust toolchain for Beads via cargo

### 1. Backend

```bash
cd backend
python3 -m venv .venv       # or: python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

If venv is unavailable (`ensurepip` missing), use: `pip3 install -r requirements.txt --user` and run `python3 -m uvicorn main:app --reload --port 8000`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### 3. OpenSpec (optional)

OpenSpec is used here as a **markdown spec** (`openspec.md`). No extra install required.

For OpenSpec CLI/tooling (if available in your ecosystem):

```bash
npm install -g openspec   # If the package exists
```

Otherwise, treat `openspec.md` as the spec. Propose changes there before implementing.

### 4. Beads (progress tracker)

**Option A: Via Cargo (Rust)**

```bash
cargo install beads-cli   # If beads-cli is published
```

**Option B: Pre-built binary**

Download from [Beads releases](https://github.com/beads-dev/beads/releases) (if applicable) and add to PATH.

**Option C: Use the included scripts (no install)**

```bash
chmod +x scripts/bd-ready.sh scripts/bd
./scripts/bd-ready.sh   # Lists unblocked tasks
./scripts/bd ready      # Same, via bd wrapper
```

---

## Running the App

1. **Terminal 1 – Backend**

   ```bash
   cd backend && source .venv/bin/activate && uvicorn main:app --reload --port 8000
   ```

2. **Terminal 2 – Frontend**

   ```bash
   cd frontend && npm run dev
   ```

3. Open **http://localhost:5173** – the app loads mock todos and lets you add/toggle/delete.

---

## Vibe Coding Workflow

### 1. OpenSpec (spec-driven development)

- Edit `openspec.md` to define or change:
  - System architecture
  - Endpoints (method, path, description)
  - Data models (JSON schemas)
  - Validation rules
- Keep it lightweight; avoid over-specifying.

### 2. Beads (progress & dependencies)

- **Query unblocked tasks:** `./scripts/bd-ready.sh` or `bd ready`
- **Update status:** edit `.beads/beads.toml`, set `status = "done"` for completed beads.
- **Add tasks:** append new `[[beads]]` blocks with `id`, `title`, `status`, `deps`.

Example dependency: `frontend-integration` depends on `define-api-routes` and `init-frontend`, so it only becomes ready when both are done.

### 3. Implementation loop

1. **Propose** – change `openspec.md`
2. **Apply** – implement in backend/frontend
3. **Update Beads** – mark beads `status = "done"` as you complete them

---

## AI Agent Usage of Beads

For an AI coding agent:

- **Session memory:** At session start, run `bd ready` to see what’s unblocked.
- **Task selection:** Pick work from the ready list; avoid starting tasks whose dependencies aren’t done.
- **After finishing work:** Update `.beads/beads.toml` – set `status = "done"` for completed beads.
- **New tasks:** Add `[[beads]]` entries with correct `deps` so the graph stays valid.

---

## API Overview

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/todos` | List all todos |
| GET | `/todos/{id}` | Get one todo |
| POST | `/todos` | Create todo |
| PATCH | `/todos/{id}` | Update todo |
| DELETE | `/todos/{id}` | Delete todo |

See `openspec.md` for full contracts and examples.

---

## Mock Data

The backend starts with 3 sample todos:

- "Ship the app" (pending)
- "Write OpenSpec" (done)
- "Set up Beads tracker" (done)

Data is in-memory; it resets on server restart.
