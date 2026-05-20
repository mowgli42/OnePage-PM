"""File attachments for plans and todos."""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from storage import StorageError, load_json, save_json

logger = logging.getLogger("oppm.attachments")

MAX_ATTACHMENT_BYTES = int(os.environ.get("MAX_ATTACHMENT_BYTES", str(10 * 1024 * 1024)))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_name(name: str) -> str:
    base = re.sub(r"[^\w.\-]", "_", Path(name).name)[:120]
    return base or "file"


class AttachmentStore:
    def __init__(self, attachments_dir: Path, index_path: Path):
        self.attachments_dir = attachments_dir
        self.index_path = index_path
        self.attachments_dir.mkdir(parents=True, exist_ok=True)

    def _load_index(self) -> list[dict]:
        return load_json(self.index_path, [], normalize=lambda d: d if isinstance(d, list) else [])

    def _save_index(self, items: list[dict]) -> None:
        save_json(self.index_path, items, max_backups=2)

    def list_for(self, *, plan_id: str | None = None, todo_id: str | None = None) -> list[dict]:
        items = self._load_index()
        if plan_id:
            return [i for i in items if i.get("plan_id") == plan_id]
        if todo_id:
            return [i for i in items if i.get("todo_id") == todo_id]
        return items

    def add(
        self,
        filename: str,
        content: bytes,
        *,
        plan_id: str | None = None,
        todo_id: str | None = None,
        user: str = "system",
    ) -> dict:
        if len(content) > MAX_ATTACHMENT_BYTES:
            raise ValueError(f"File too large (max {MAX_ATTACHMENT_BYTES} bytes)")
        att_id = str(uuid4())
        safe = _safe_name(filename)
        stored_name = f"{att_id}_{safe}"
        path = self.attachments_dir / stored_name
        path.write_bytes(content)
        record = {
            "id": att_id,
            "filename": filename,
            "stored_name": stored_name,
            "size": len(content),
            "plan_id": plan_id,
            "todo_id": todo_id,
            "uploaded_by": user,
            "created_at": _now(),
        }
        items = self._load_index()
        items.append(record)
        self._save_index(items)
        return record

    def get_path(self, att_id: str) -> Path:
        for item in self._load_index():
            if item.get("id") == att_id:
                path = self.attachments_dir / item["stored_name"]
                if path.exists():
                    return path
        raise FileNotFoundError(att_id)

    def get_meta(self, att_id: str) -> dict:
        for item in self._load_index():
            if item.get("id") == att_id:
                return item
        raise FileNotFoundError(att_id)

    def delete(self, att_id: str) -> None:
        items = self._load_index()
        kept = []
        removed = None
        for item in items:
            if item.get("id") == att_id:
                removed = item
            else:
                kept.append(item)
        if not removed:
            raise FileNotFoundError(att_id)
        path = self.attachments_dir / removed["stored_name"]
        path.unlink(missing_ok=True)
        self._save_index(kept)
