"""Pluggable persistence: JSON files (default) or SQLite."""
from __future__ import annotations

import json
import logging
import os
import sqlite3
from pathlib import Path
from typing import Callable

from storage import StorageError, load_json, save_json

logger = logging.getLogger("oppm.datastore")

STORAGE_BACKEND = os.environ.get("STORAGE_BACKEND", "json").lower()


class JsonDatastore:
    def __init__(
        self,
        *,
        todos_path: Path,
        plans_dir: Path,
        plan_json_path: Path,
        archive_dir: Path,
        max_todo_backups: int,
        max_plan_backups: int,
        normalize_todos: Callable,
        normalize_plan: Callable,
        default_todos: list[dict],
        default_plan: dict,
    ):
        self.todos_path = todos_path
        self.plans_dir = plans_dir
        self.plan_json_path = plan_json_path
        self.archive_dir = archive_dir
        self.max_todo_backups = max_todo_backups
        self.max_plan_backups = max_plan_backups
        self.normalize_todos = normalize_todos
        self.normalize_plan = normalize_plan
        self.default_todos = default_todos
        self.default_plan = default_plan

    def load_todos(self) -> list[dict]:
        return load_json(
            self.todos_path,
            [t.copy() for t in self.default_todos],
            normalize=self.normalize_todos,
        )

    def save_todos(self, todos: list[dict]) -> None:
        save_json(self.todos_path, todos, max_backups=self.max_todo_backups)

    def init_todos(self) -> list[dict]:
        todos = self.load_todos()
        if not self.todos_path.exists():
            self.save_todos(todos)
        return todos

    def plan_path(self, plan_id: str) -> Path:
        safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in plan_id).strip() or "default"
        return self.plans_dir / f"{safe_id}.json"

    def plan_exists(self, plan_id: str) -> bool:
        return self.plan_path(plan_id).exists()

    def load_plan_file(self, path: Path) -> dict:
        return load_json(path, self.default_plan.copy(), normalize=self.normalize_plan)

    def load_plan(self, plan_id: str | None) -> dict:
        if plan_id:
            path = self.plan_path(plan_id)
            if plan_id == "default" and not path.exists() and self.plan_json_path.exists():
                return self.load_plan_file(self.plan_json_path)
            return self.load_plan_file(path)
        return self.load_plan_file(self.plan_json_path)

    def save_plan(self, plan: dict, plan_id: str | None) -> None:
        if plan_id:
            save_json(self.plan_path(plan_id), plan, max_backups=self.max_plan_backups)
        else:
            save_json(self.plan_json_path, plan, max_backups=self.max_plan_backups)

    def delete_plan(self, plan_id: str) -> None:
        path = self.plan_path(plan_id)
        if not path.exists():
            raise FileNotFoundError(plan_id)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        path.replace(self.archive_dir / path.name)

    def list_plans(self, include_archived: bool, search: str) -> list[dict]:
        out = []
        q = search.strip().lower()
        for p in sorted(self.plans_dir.glob("*.json")):
            pid = p.stem
            data = self.load_plan_file(p)
            if data.get("archived") and not include_archived:
                continue
            title = (data.get("header") or {}).get("projectTitle") or pid
            if q and q not in title.lower() and q not in pid.lower():
                continue
            out.append({
                "id": pid,
                "title": title,
                "projectId": data.get("projectId"),
                "projectNumber": data.get("projectNumber"),
                "archived": bool(data.get("archived")),
            })
        if not out and self.plan_json_path.exists():
            data = self.load_plan_file(self.plan_json_path)
            title = (data.get("header") or {}).get("projectTitle") or "Default"
            out.append({
                "id": "default",
                "title": title,
                "projectId": data.get("projectId"),
                "projectNumber": data.get("projectNumber"),
                "archived": bool(data.get("archived")),
            })
        return out

    def next_project_number(self) -> int:
        nums = []
        for p in self.plans_dir.glob("*.json"):
            data = self.load_plan_file(p)
            n = data.get("projectNumber")
            if isinstance(n, (int, float)):
                nums.append(int(n))
        return max(nums, default=1000) + 1

    def migrate_from_json(self) -> None:
        pass


class SqliteDatastore(JsonDatastore):
    """SQLite backend with one-shot import from JSON files."""

    def __init__(self, db_path: Path, **kwargs):
        super().__init__(**kwargs)
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
        if not self._has_data():
            self.migrate_from_json()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS todos_store (
                  id INTEGER PRIMARY KEY CHECK (id = 1),
                  data TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS plans (
                  plan_id TEXT PRIMARY KEY,
                  data TEXT NOT NULL,
                  archived INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS meta (
                  key TEXT PRIMARY KEY,
                  value TEXT NOT NULL
                );
                """
            )

    def _has_data(self) -> bool:
        with self._connect() as conn:
            n = conn.execute("SELECT COUNT(*) FROM plans").fetchone()[0]
            t = conn.execute("SELECT COUNT(*) FROM todos_store").fetchone()[0]
            return n > 0 or t > 0

    def migrate_from_json(self) -> None:
        todos = super().load_todos()
        self.save_todos(todos)
        for p in self.plans_dir.glob("*.json"):
            data = super().load_plan_file(p)
            self.save_plan(data, p.stem)
        if self.plan_json_path.exists() and not self.plan_exists("default"):
            self.save_plan(super().load_plan_file(self.plan_json_path), "default")
        logger.info("migrated JSON data into SQLite %s", self.db_path)

    def load_todos(self) -> list[dict]:
        with self._connect() as conn:
            row = conn.execute("SELECT data FROM todos_store WHERE id = 1").fetchone()
        if not row:
            return [t.copy() for t in self.default_todos]
        return self.normalize_todos(json.loads(row["data"]))

    def save_todos(self, todos: list[dict]) -> None:
        payload = json.dumps(todos)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO todos_store (id, data) VALUES (1, ?) "
                "ON CONFLICT(id) DO UPDATE SET data = excluded.data",
                (payload,),
            )

    def init_todos(self) -> list[dict]:
        return self.load_todos()

    def plan_exists(self, plan_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT 1 FROM plans WHERE plan_id = ?", (plan_id,)).fetchone()
        return row is not None

    def load_plan(self, plan_id: str | None) -> dict:
        if not plan_id:
            plan_id = "default"
        with self._connect() as conn:
            row = conn.execute("SELECT data FROM plans WHERE plan_id = ?", (plan_id,)).fetchone()
        if row:
            return self.normalize_plan(json.loads(row["data"]))
        if plan_id == "default" and self.plan_json_path.exists():
            return super().load_plan_file(self.plan_json_path)
        return self.default_plan.copy()

    def save_plan(self, plan: dict, plan_id: str | None) -> None:
        pid = plan_id or "default"
        archived = 1 if plan.get("archived") else 0
        payload = json.dumps(plan)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO plans (plan_id, data, archived) VALUES (?, ?, ?) "
                "ON CONFLICT(plan_id) DO UPDATE SET data = excluded.data, archived = excluded.archived",
                (pid, payload, archived),
            )

    def delete_plan(self, plan_id: str) -> None:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM plans WHERE plan_id = ?", (plan_id,))
        if cur.rowcount == 0:
            raise FileNotFoundError(plan_id)

    def list_plans(self, include_archived: bool, search: str) -> list[dict]:
        out = []
        q = search.strip().lower()
        with self._connect() as conn:
            rows = conn.execute("SELECT plan_id, data, archived FROM plans ORDER BY plan_id").fetchall()
        for row in rows:
            if row["archived"] and not include_archived:
                continue
            data = self.normalize_plan(json.loads(row["data"]))
            pid = row["plan_id"]
            title = (data.get("header") or {}).get("projectTitle") or pid
            if q and q not in title.lower() and q not in pid.lower():
                continue
            out.append({
                "id": pid,
                "title": title,
                "projectId": data.get("projectId"),
                "projectNumber": data.get("projectNumber"),
                "archived": bool(data.get("archived")),
            })
        return out

    def next_project_number(self) -> int:
        nums = []
        with self._connect() as conn:
            rows = conn.execute("SELECT data FROM plans").fetchall()
        for row in rows:
            data = json.loads(row["data"])
            n = data.get("projectNumber")
            if isinstance(n, (int, float)):
                nums.append(int(n))
        return max(nums, default=1000) + 1


def create_datastore(
    *,
    data_dir: Path,
    todos_path: Path,
    plans_dir: Path,
    plan_json_path: Path,
    archive_dir: Path,
    max_todo_backups: int,
    max_plan_backups: int,
    normalize_todos: Callable,
    normalize_plan: Callable,
    default_todos: list[dict],
    default_plan: dict,
) -> JsonDatastore:
    kwargs = dict(
        todos_path=todos_path,
        plans_dir=plans_dir,
        plan_json_path=plan_json_path,
        archive_dir=archive_dir,
        max_todo_backups=max_todo_backups,
        max_plan_backups=max_plan_backups,
        normalize_todos=normalize_todos,
        normalize_plan=normalize_plan,
        default_todos=default_todos,
        default_plan=default_plan,
    )
    if STORAGE_BACKEND == "sqlite":
        db_path = Path(os.environ.get("SQLITE_PATH", data_dir / "oppm.db"))
        return SqliteDatastore(db_path, **kwargs)
    return JsonDatastore(**kwargs)
