# OnePage-PM

One-page project management: Svelte UI + FastAPI for in-memory todos and JSON-file OPPM plans (no DB). Live: https://one-page-pm.vercel.app
Stack: Svelte 4 + Vite (5173) + FastAPI (8000) + JSON plans in backend/data/plans/. Posture: ponytail (repo >30 days).
Shared health pack in `.cursor/skills/` and `.cursor/rules/` — follow for [Health] work.

## Commands

- Backend: `cd backend && source .venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- Frontend: `cd frontend && npm run dev`
- Backend tests: `cd backend && pytest tests/ -v`
- E2E: `cd frontend && npx playwright test` (backend must be up)
- Seed plans: `python3 backend/scripts/seed_plans.py`
- Screenshots: `cd frontend && npm run screenshot`
- Secrets: `bash scripts/scan-secrets.sh .`
- Beads: `./scripts/bd ready` or `bd ready`

## Hard prohibitions

- Do not commit private keys, `*-key.pem`, `*.key`, `.env` secrets, or `BEGIN … PRIVATE KEY`. Generate locally; gitignore keys. Public certs OK.
- Do not treat JSON plan files or in-memory todos as a shared DB on Vercel production without a persistent volume. Do this instead: keep file-based for local/shared-volume deploys, or document the limitation.
- Do not invent routes, env vars (`PLANS_DIR`, `PLAN_JSON_PATH`, `ALLOWED_ORIGINS`), or matrix symbols (○ ● △) that are not in openspec.md or code.
- Do not rewrite OpenSpec / Gherkin / Beads to match a hoped-for future. Update them only when code already changed.

## Verify by change type

| Change | Check |
| --- | --- |
| UI / Svelte (OPPMPage, todos) | `npm run dev` + load / or ?view=oppm; check screenshots if UI changes |
| API / FastAPI | `pytest tests/` or curl `/health`, `/todos`, `/plans`, `/plan?plan_id=` |
| Spec | matching `features/*.feature` + openspec.md capability still true |
| Deploy | https://one-page-pm.vercel.app returns 200; primary flows (todos + OPPM load) work |
| Secrets / TLS | `bash scripts/scan-secrets.sh .` passes |

## Source of truth

- Behavior: openspec.md + features/*.feature
- Remaining work: .beads/beads.toml + GitHub issues
- Demo evidence: docs/screenshots/ + README walkthrough
- Health bar: do not duplicate SUCCESS_CRITERIA.md here

## House vocabulary

- OPPM — One Page Project Manager (NASS-style). Do not write "project plan page" or "one-pager".
- Matrix symbols: ○ planned, ● completed, △ risk/decision. Do not invent other glyphs.
- projectId (UUID) / projectNumber (int) — server-assigned identifiers for sharing. Do not use filename as sole ID.
- plan_id query param — selects which JSON plan. Do not assume single plan.json.

## Good / bad (from this repo)

Bad: Hand-edit backend/data/plans/*.json and expect UI to pick it up without GET /plans refresh.
Good: PUT /plan?plan_id=… then reload; or run seed_plans.py then restart backend.

## Borrowed patterns

- Hard prohibitions + verification matrix + single-source + house vocabulary from ossrules.md patterns (common across portfolio reviews; cited from https://ossrules.md/).
