"""Optional outbound notifications via ntfy or SMTP (stdlib only)."""
from __future__ import annotations

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage
from urllib import error, request

logger = logging.getLogger("oppm.notifications")

NTFY_URL = os.environ.get("NTFY_URL", "").rstrip("/")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM = os.environ.get("SMTP_FROM", SMTP_USER)
SMTP_TO = os.environ.get("SMTP_TO", "")
NOTIFY_ON_CHANGES = os.environ.get("NOTIFY_ON_CHANGES", "false").lower() in ("1", "true", "yes")


def notifications_enabled() -> bool:
    return NOTIFY_ON_CHANGES and (bool(NTFY_TOPIC) or bool(SMTP_HOST))


def notify(event: str, message: str, *, user: str = "system") -> None:
    if not NOTIFY_ON_CHANGES:
        return
    title = f"OPPM: {event}"
    body = f"{message}\n(by {user})"
    _send_ntfy(title, body)
    _send_smtp(title, body)


def _send_ntfy(title: str, body: str) -> None:
    if not NTFY_TOPIC:
        return
    base = NTFY_URL or "https://ntfy.sh"
    url = f"{base}/{NTFY_TOPIC}"
    req = request.Request(url, data=body.encode("utf-8"), method="POST", headers={"Title": title})
    try:
        with request.urlopen(req, timeout=10):
            logger.debug("ntfy sent: %s", title)
    except (error.URLError, TimeoutError) as e:
        logger.warning("ntfy failed: %s", e)


def _send_smtp(subject: str, body: str) -> None:
    if not SMTP_HOST or not SMTP_TO:
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM or SMTP_USER or "oppm@localhost"
    msg["To"] = SMTP_TO
    msg.set_content(body)
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls(context=context)
            if SMTP_USER:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logger.debug("smtp sent: %s", subject)
    except OSError as e:
        logger.warning("smtp failed: %s", e)
