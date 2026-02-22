# Project Plan Editing & Persistence — Proposal

**Version:** 1.0  
**Date:** 2026-02-22

---

## 1. Goal

- Allow **editing** the one-page project plan (OPPM): header, objectives, schedule matrix, budget, risks, status.
- **Save** the plan so it can be **updated in the future** (persist across sessions and edits).

---

## 2. Editing a Project

**In scope:**

- **Header:** Project title, sponsor, project manager, start/end dates, reporting period, version, date updated.
- **Objectives:** List of objectives (id, title, metric, owner).
- **Schedule matrix:** Per-objective, per-period cells (symbol: ○/●/△, label).
- **Owners:** Initials and roles.
- **Budget:** Total, spent, categories (name, planned, spent).
- **Risks:** List of risk text, owner, mitigation.
- **KPIs:** Label, value, target (met or not).
- **Status:** Level (green/yellow/red), one-line text.

**UI approach:** An “Edit plan” mode or inline editable fields on the OPPM view, with a **Save** action that persists the current plan.

---

**Schedule tracking (implemented):**
- **Time periods (quarters):** Add, edit, remove column labels. Each column is one period in the timeline (e.g. Q1 2026, Q2 2026). Adding/removing a period updates the matrix columns.
- **Objectives:** Add, edit, remove rows. Each objective has id, title, metric, owner. Adding/removing an objective adds/removes the corresponding matrix row.
- **Matrix cells:** Per objective × period, set symbol (○ Planned, ● Done, △ Risk, or —) and short label. The schedule table in Edit plan shows a compact grid of symbol + label inputs; the main OPPM view shows the same data read-only.

---

## 3. Persistence Options

### Option A: JSON file (recommended for v1)

- **How:** Single file (e.g. `data/plan.json` or `backend/plan.json`) holding the full plan as one JSON document.
- **Pros:** Simple, no extra dependencies; file is human-readable and versionable (git); easy backup and portability.
- **Cons:** Single plan per file (or one file per project if we name by id); no concurrent write safety beyond “last write wins”.
- **API:** `GET /plan` returns the stored plan (or default). `PUT /plan` replaces the stored plan with the request body and writes to the file.

### Option B: SQLite database

- **How:** SQLite DB (e.g. `data/plans.db`) with a table such as `plans (id, name, data JSON, updated_at)`. One row per project plan.
- **Pros:** Multiple plans; simple queries; one file per DB; good for future “list projects” and linking with tools like Project-Artifact-Tracker.
- **Cons:** Slightly more setup (schema, migrations if we change structure); less trivial to “just edit the file” by hand.
- **API:** `GET /plans` list; `GET /plans/{id}` and `PUT /plans/{id}` for one plan; or keep `GET /plan` / `PUT /plan` for “default” plan and add `GET /plans?default=1` later.

### Recommendation

- **Phase 1:** Implement **JSON file** persistence: one plan per app instance, `GET /plan` and `PUT /plan`, file path configurable (e.g. env `PLAN_JSON_PATH`).
- **Phase 2 (future):** Add **SQLite** for multiple projects: e.g. `plans` table, optional `GET /plans`, `GET /plans/{id}`, `PUT /plans/{id}`, and use the same JSON shape for the `data` column so the frontend can stay the same.

---

## 4. Data Shape (single plan)

One JSON document with the same structure as the current OPPM mock:

- `header`: { projectTitle, sponsor, projectManager, startDate, endDate, reportingPeriod, version, dateUpdated }
- `quarters`: string[]
- `objectives`: [{ id, title, metric, owner }]
- `matrix`: 2D array of { symbol, label } (indexed by objective then period)
- `owners`: [{ initials, role }]
- `budget`: { total, spent, categories: [{ name, planned, spent }] }
- `risks`: [{ text, owner, mitigation }]
- `kpis`: [{ label, value, target }]
- `status`: { level, text }

Backend validates required top-level keys and types where needed; frontend sends this shape on Save.

---

## 5. Summary

| Item | Choice |
|------|--------|
| Editing | Editable OPPM (header, objectives, matrix, budget, risks, status, etc.) with Save |
| Save method (v1) | JSON file; GET/PUT `/plan` |
| Save method (future) | Optional SQLite for multiple plans |
| Update in future | Re-open app, load saved plan, edit, Save again |
| Schedule tracking | Time periods (add/edit/remove), Objectives (add/edit/remove), Matrix (symbol + label per cell) |
