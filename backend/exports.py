"""Export plans as iCalendar or printable HTML."""
from __future__ import annotations

import html
from datetime import datetime, timedelta, timezone


def _escape_ical(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _parse_date(value: str) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%b %d, %Y", "%d %b %Y"):
        try:
            return datetime.strptime(value.strip()[:20], fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def plan_to_ical(plan: dict, plan_id: str) -> str:
    title = (plan.get("header") or {}).get("projectTitle") or plan_id
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//OnePage PM//EN",
        "CALSCALE:GREGORIAN",
        f"X-WR-CALNAME:{_escape_ical(title)}",
    ]
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for task in plan.get("tasks") or []:
        uid = f"{plan_id}-{task.get('id', 'task')}@onepage-pm"
        summary = _escape_ical(task.get("title") or task.get("id") or "Task")
        start = _parse_date(task.get("startDate") or "")
        end = _parse_date(task.get("endDate") or "") or (start + timedelta(days=1) if start else None)
        if not start:
            start = datetime.now(timezone.utc)
        if not end:
            end = start + timedelta(days=1)
        dtstart = start.strftime("%Y%m%d")
        dtend = end.strftime("%Y%m%d")
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now}",
            f"DTSTART;VALUE=DATE:{dtstart}",
            f"DTEND;VALUE=DATE:{dtend}",
            f"SUMMARY:{summary}",
            "END:VEVENT",
        ])
    if not (plan.get("tasks") or []):
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{plan_id}-overview@onepage-pm",
            f"DTSTAMP:{now}",
            f"SUMMARY:{_escape_ical(title)}",
            "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def plan_to_print_html(plan: dict, plan_id: str) -> str:
    header = plan.get("header") or {}
    title = html.escape(header.get("projectTitle") or plan_id)
    status = plan.get("status") or {}
    objectives = plan.get("objectives") or []
    quarters = plan.get("quarters") or []
    matrix = plan.get("matrix") or []
    rows = []
    for i, obj in enumerate(objectives):
        cells = matrix[i] if i < len(matrix) else []
        cell_html = "".join(
            f"<td>{html.escape((cells[j] or {}).get('symbol', ''))} {html.escape((cells[j] or {}).get('label', ''))}</td>"
            for j in range(len(quarters))
        )
        rows.append(
            f"<tr><th>{html.escape(obj.get('id', ''))}</th>"
            f"<td>{html.escape(obj.get('title', ''))}</td>{cell_html}</tr>"
        )
    qheads = "".join(f"<th>{html.escape(q)}</th>" for q in quarters)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<title>{title} — OPPM Export</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 1.5rem; color: #111; }}
h1 {{ margin-bottom: 0.25rem; }}
.meta {{ color: #555; margin-bottom: 1rem; }}
table {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
th, td {{ border: 1px solid #ccc; padding: 4px 6px; }}
th {{ background: #f3f4f6; }}
.status {{ padding: 0.5rem; background: #fef3c7; margin-bottom: 1rem; }}
@media print {{ @page {{ size: A4 landscape; margin: 12mm; }} }}
</style></head><body>
<h1>{title}</h1>
<p class="meta">Sponsor: {html.escape(header.get('sponsor', ''))} · PM: {html.escape(header.get('projectManager', ''))}</p>
<div class="status"><strong>{html.escape((status.get('level') or '').upper())}</strong> — {html.escape(status.get('text', ''))}</div>
<table><thead><tr><th>ID</th><th>Objective</th>{qheads}</tr></thead><tbody>{''.join(rows)}</tbody></table>
<p class="meta">Exported {html.escape(plan_id)} · Print this page to PDF (Ctrl+P)</p>
</body></html>"""
