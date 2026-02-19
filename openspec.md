# Project Management App — OpenSpec

> Single source-of-truth for architecture, API contracts, and data models.  
> Workflow: Propose changes here → Apply → Update Beads.

---

## 1. System Architecture

```
┌─────────────────────┐     JSON over HTTP      ┌─────────────────────┐
│  Svelte Frontend    │ ◄─────────────────────► │  FastAPI Backend    │
│  - Minimal stores   │    GET/POST /todos       │  - In-memory store  │
│  - One-page app     │                         │  - Port 8000        │
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
- **Data**: JSON only. No database—in-memory + optional JSON file for mock data.

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

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check `{ "status": "ok" }` |

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

---

## 4. Example Payloads

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

## 5. Revision Log

| Date | Change |
|------|--------|
| 2026-02-19 | Initial spec: todos CRUD, health, mock data |
