"""Simple token-based auth with file-backed users and login throttling."""
from __future__ import annotations

import hashlib
import json
import logging
import os
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from storage import StorageError, load_json, save_json

logger = logging.getLogger("oppm.auth")

AUTH_ENABLED = os.environ.get("AUTH_ENABLED", "false").lower() in ("1", "true", "yes")
AUTH_ALLOW_GUEST_READ = os.environ.get("AUTH_ALLOW_GUEST_READ", "true").lower() in ("1", "true", "yes")
TOKEN_TTL_SECONDS = int(os.environ.get("AUTH_TOKEN_TTL", "86400"))
MAX_LOGIN_ATTEMPTS = int(os.environ.get("AUTH_MAX_LOGIN_ATTEMPTS", "5"))
LOGIN_WINDOW_SECONDS = int(os.environ.get("AUTH_LOGIN_WINDOW", "60"))

_bearer = HTTPBearer(auto_error=False)

# token -> {username, role, expires_at}
_sessions: dict[str, dict[str, Any]] = {}
# client_key -> [timestamps]
_login_attempts: dict[str, list[float]] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$", 1)
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return secrets.compare_digest(check, digest)


def _default_users() -> list[dict]:
    admin_pass = os.environ.get("ADMIN_PASSWORD", "admin")
    return [
        {
            "username": os.environ.get("ADMIN_USERNAME", "admin"),
            "password_hash": hash_password(admin_pass),
            "role": "admin",
        },
        {
            "username": "guest",
            "password_hash": hash_password(os.environ.get("GUEST_PASSWORD", "guest")),
            "role": "guest",
        },
    ]


def load_users(users_path: Path) -> list[dict]:
    users = load_json(users_path, _default_users(), normalize=lambda d: d if isinstance(d, list) else _default_users())
    if not users_path.exists():
        try:
            save_json(users_path, users, max_backups=1)
        except StorageError as e:
            logger.warning("could not seed users file: %s", e)
    return users


def save_users(users_path: Path, users: list[dict]) -> None:
    save_json(users_path, users, max_backups=2)


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def check_login_allowed(request: Request) -> None:
    key = _client_key(request)
    now = time.time()
    attempts = [t for t in _login_attempts.get(key, []) if now - t < LOGIN_WINDOW_SECONDS]
    if len(attempts) >= MAX_LOGIN_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Too many login attempts; try again later")
    attempts.append(now)
    _login_attempts[key] = attempts


def login(username: str, password: str, users_path: Path) -> dict:
    users = load_users(users_path)
    for u in users:
        if u.get("username") == username and verify_password(password, u.get("password_hash", "")):
            token = secrets.token_urlsafe(32)
            _sessions[token] = {
                "username": username,
                "role": u.get("role", "guest"),
                "expires_at": time.time() + TOKEN_TTL_SECONDS,
            }
            return {"token": token, "username": username, "role": u["role"], "expires_in": TOKEN_TTL_SECONDS}
    raise HTTPException(status_code=401, detail="Invalid credentials")


def resolve_session(token: str | None) -> dict | None:
    if not token:
        return None
    sess = _sessions.get(token)
    if not sess:
        return None
    if sess["expires_at"] < time.time():
        _sessions.pop(token, None)
        return None
    return sess


def require_auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    *,
    write: bool = False,
) -> dict | None:
    if not AUTH_ENABLED:
        return {"username": "system", "role": "admin"}
    token = credentials.credentials if credentials and credentials.scheme.lower() == "bearer" else None
    sess = resolve_session(token)
    if sess:
        if write and sess["role"] != "admin":
            raise HTTPException(status_code=403, detail="Admin role required")
        return sess
    if not write and AUTH_ALLOW_GUEST_READ:
        return {"username": "anonymous", "role": "guest"}
    raise HTTPException(status_code=401, detail="Authentication required")


def require_admin(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    return require_auth(request, credentials, write=True)  # type: ignore[return-value]


def require_read(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict | None:
    return require_auth(request, credentials, write=False)
