# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Full-stack project management app: Svelte 4 + Vite frontend (port 5173) and FastAPI backend (port 8000). No database — uses in-memory storage for todos and JSON files for OPPM plans. See `README.md` for complete setup and API docs.

### Running services

- **Backend:** `cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- **Frontend:** `cd frontend && npm run dev`
- Both must be running for E2E tests and manual testing.
- The Vite dev server proxies `/api/*` requests to the backend at `localhost:8000`, so the frontend uses relative `/api` paths in both dev and production (Vercel).

### Testing

- **Backend unit tests:** `cd backend && pytest tests/ -v` (no running server needed; uses Starlette TestClient which requires `httpx`)
- **E2E tests (Playwright):** `cd frontend && npx playwright test` — requires backend running on port 8000; Playwright auto-starts the frontend dev server in non-CI mode.
- **Playwright browsers:** `npx playwright install --with-deps chromium` (one-time; already installed in snapshot).

### Known issues

- 3 of 4 Playwright E2E tests have pre-existing failures: the tests expect project title text inside `.oppm-header`, but the component renders the title in a separate element above the header. Only the "Todos view loads" test passes.

### Vercel deployment

- `vercel.json` at repo root configures build (frontend), rewrites (`/api/*` → serverless function), and security headers.
- `api/index.py` is the serverless entry point — mounts the FastAPI backend app at `/api`.
- Root `requirements.txt` lists Python deps for Vercel's runtime (just `fastapi`; uvicorn not needed in serverless).
- On Vercel, data in `/tmp` is ephemeral — todos reset on cold start, plans may be lost between deployments.

### Gotchas

- `pip install` places binaries in `~/.local/bin` — ensure this is on `PATH` (already added in `.bashrc`).
- No linting tools (ESLint, Ruff, etc.) are configured in this project.
- `httpx` is required for backend tests (Starlette TestClient dependency) but is not listed in `requirements-dev.txt`. The update script installs it explicitly.
- Frontend uses `npm` (has `package-lock.json`).
- CORS origins are env-configurable via `ALLOWED_ORIGINS` (comma-separated); defaults to localhost dev origins.
