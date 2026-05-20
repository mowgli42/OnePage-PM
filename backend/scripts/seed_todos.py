#!/usr/bin/env python3
"""
Seed TODOS_JSON_PATH with default mock todos for local/dev use.
Run from repo root: python backend/scripts/seed_todos.py
Or: TODOS_JSON_PATH=backend/data/todos.json python backend/scripts/seed_todos.py
"""
import json
import os
import sys
from pathlib import Path

# Reproducible seed data (matches backend/main.py DEFAULT_TODOS)
DEFAULT_TODOS = [
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


def main() -> int:
    backend_dir = Path(__file__).resolve().parent.parent
    todos_path = Path(os.environ.get("TODOS_JSON_PATH", backend_dir / "data" / "todos.json"))
    todos_path.parent.mkdir(parents=True, exist_ok=True)
    with open(todos_path, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_TODOS, f, indent=2)
        f.write("\n")
    print(f"Wrote {len(DEFAULT_TODOS)} todos to {todos_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
