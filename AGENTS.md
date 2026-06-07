# AGENTS.md - guide for AI coding agents

## Project context

OnePage-PM is a project management app with a Python backend and Node frontend.
Start with `README.md`, then inspect `backend/` and `frontend/` before editing.

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
