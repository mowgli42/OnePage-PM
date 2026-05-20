"""JSON file persistence with atomic writes, backups, retries, and disk stats."""
from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, TypeVar

logger = logging.getLogger("oppm.storage")

T = TypeVar("T")


class StorageError(Exception):
    """Raised when JSON persistence fails after retries."""

    def __init__(self, message: str, path: Path | None = None):
        super().__init__(message)
        self.path = path


def rotate_backups(path: Path, max_backups: int) -> None:
    if max_backups < 1 or not path.exists():
        return
    for i in range(max_backups, 1, -1):
        src = path.parent / f"{path.name}.bak.{i - 1}"
        dst = path.parent / f"{path.name}.bak.{i}"
        if src.exists():
            if dst.exists():
                dst.unlink()
            shutil.copy2(src, dst)
    bak1 = path.parent / f"{path.name}.bak.1"
    if bak1.exists():
        bak1.unlink()
    shutil.copy2(path, bak1)


def atomic_write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.stem}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def save_json(
    path: Path,
    data: object,
    *,
    max_backups: int = 3,
    retries: int = 3,
    retry_delay: float = 0.05,
) -> None:
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            rotate_backups(path, max_backups)
            atomic_write_json(path, data)
            logger.debug("saved %s", path)
            return
        except OSError as e:
            last_err = e
            logger.warning("save attempt %s failed for %s: %s", attempt + 1, path, e)
            time.sleep(retry_delay * (attempt + 1))
    raise StorageError(f"Failed to save {path}: {last_err}", path)


def load_json(
    path: Path,
    default: T,
    *,
    retries: int = 3,
    retry_delay: float = 0.05,
    normalize: Callable[[Any], T] | None = None,
) -> T:
    if not path.exists():
        return default
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
            if normalize is not None:
                return normalize(raw)
            return raw  # type: ignore[return-value]
        except (json.JSONDecodeError, OSError) as e:
            last_err = e
            logger.warning("load attempt %s failed for %s: %s", attempt + 1, path, e)
            time.sleep(retry_delay * (attempt + 1))
    logger.error("using default for %s after load failure: %s", path, last_err)
    return default


def append_jsonl(path: Path, record: dict, *, max_bytes: int = 5_000_000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > max_bytes:
        rotate_backups(path, 3)
        path.unlink(missing_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def read_jsonl(path: Path, limit: int = 50) -> list[dict]:
    if not path.exists():
        return []
    lines: list[str] = []
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return []
    out: list[dict] = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return list(reversed(out))


def dir_disk_usage(path: Path) -> dict:
    total = 0
    files = 0
    if path.exists():
        for p in path.rglob("*"):
            if p.is_file():
                files += 1
                try:
                    total += p.stat().st_size
                except OSError:
                    pass
    writable = os.access(path, os.W_OK) if path.exists() else True
    try:
        path.mkdir(parents=True, exist_ok=True)
        writable = os.access(path, os.W_OK)
    except OSError:
        writable = False
    return {"path": str(path), "bytes": total, "files": files, "writable": writable}
