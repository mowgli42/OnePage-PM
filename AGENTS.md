# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Full-stack project management app: Svelte 4 + Vite frontend (port 5173) and FastAPI backend (port 8000). No database — uses in-memory storage for todos and JSON files for OPPM plans. See `README.md` for complete setup and API docs.

### Running services

- **Backend:** `cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- **Frontend:** `cd frontend && npm run dev`
- Both must be running for E2E tests and manual testing.
- The Vite dev server proxies `/_/backend/*` requests to the backend at `localhost:8000`, so the frontend uses relative `/_/backend` paths in both dev and production (Vercel).

### Testing

- **Backend unit tests:** `cd backend && pytest tests/ -v` (no running server needed; uses Starlette TestClient which requires `httpx`)
- **E2E tests (Playwright):** `cd frontend && npx playwright test` — requires backend running on port 8000; Playwright auto-starts the frontend dev server in non-CI mode.
- **Playwright browsers:** `npx playwright install --with-deps chromium` (one-time; already installed in snapshot).

### Known issues

- 3 of 4 Playwright E2E tests have pre-existing failures: the tests expect project title text inside `.oppm-header`, but the component renders the title in a separate element above the header. Only the "Todos view loads" test passes.

### Vercel deployment

- `vercel.json` uses `experimentalServices` with two services: `frontend` (Vite at `/`) and `backend` (FastAPI at `/_/backend`).
- The frontend stores call `/_/backend/*` for all API requests. In dev, Vite proxies `/_/backend/*` to `localhost:8000` (stripping the prefix). On Vercel, the route prefix handles this automatically.
- Security headers are configured in `vercel.json` for all routes.

### Gotchas

- `pip install` places binaries in `~/.local/bin` — ensure this is on `PATH` (already added in `.bashrc`).
- No linting tools (ESLint, Ruff, etc.) are configured in this project.
- `httpx` is required for backend tests (Starlette TestClient dependency) but is not listed in `requirements-dev.txt`. The update script installs it explicitly.
- Frontend uses `npm` (has `package-lock.json`).
- CORS origins are env-configurable via `ALLOWED_ORIGINS` (comma-separated); defaults to localhost dev origins.

## Local setup

Run from the repository root:

```bash
(cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt)
(cd frontend && npm ci)
(cd frontend && npx playwright install chromium)
```

## Smoke test

```bash
(cd backend && .venv/bin/python -c "import main") && (cd frontend && npm run build)
```

## Agent notes

- Keep backend and frontend changes scoped to their directories.
- Do not commit generated test output such as `frontend/test-results/`.
- Preserve existing local user changes; stage only files you intentionally modify.

## Issue Tracking

This project uses **bd (beads)** for issue tracking. Run `bd prime` for workflow context, or install hooks with `bd hooks install` for automatic context injection.

Quick reference:

- `bd ready` - find unblocked work
- `bd create "Title" --type task --priority 2` - create an issue
- `bd close <id>` - close completed work
- `bd dolt push` - push Beads data when using a shared Beads remote

For full workflow details, run `bd prime`.
