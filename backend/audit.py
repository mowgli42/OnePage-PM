"""Append-only audit log for changes."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from storage import append_jsonl, read_jsonl


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_action(audit_path: Path, *, user: str, action: str, resource: str, detail: dict | None = None) -> None:
    append_jsonl(
        audit_path,
        {
            "at": _ts(),
            "user": user,
            "action": action,
            "resource": resource,
            "detail": detail or {},
        },
    )


def list_activity(audit_path: Path, limit: int = 50) -> list[dict]:
    return read_jsonl(audit_path, limit=limit)
