#!/usr/bin/env bash
# Parse .beads/beads.toml and show unblocked (ready) tasks
# Usage: ./scripts/bd-ready.sh  or  bd ready
# Works with Python 3.6+ (no extra deps)

cd "$(dirname "$0")/.." || true
BEADS_FILE="${BEADS_FILE:-.beads/beads.toml}"
[[ -f "$BEADS_FILE" ]] || { echo "No beads file at $BEADS_FILE"; exit 1; }

python3 << 'PY'
import re, json

with open(".beads/beads.toml") as f:
    raw = f.read()

beads = []
current = {}
for line in raw.split("\n"):
    line = line.rstrip()
    if line.strip() == "[[beads]]":
        if current.get("id"):
            beads.append(current)
        current = {"id": "", "title": "", "status": "pending", "deps": []}
        continue
    m = re.match(r'(\w+)\s*=\s*(.+)', line)
    if m and current is not None:
        k, v = m.group(1), m.group(2).strip().strip('"').strip("'")
        if k == "deps":
            inner = re.search(r'\[(.*?)\]', v)
            current["deps"] = [x.strip().strip('"') for x in (inner.group(1).split(",") if inner and inner.group(1) else [])]
        else:
            current[k] = v
if current.get("id"):
    beads.append(current)

done = {b["id"] for b in beads if b.get("status") == "done"}
pending = [b for b in beads if b.get("status") == "pending"]
ready = [b for b in pending if all(d in done for d in b.get("deps", []))]

print("Ready (unblocked) tasks:")
print("-" * 40)
for b in ready:
    print(f"  [{b.get('id', '?')}] {b.get('title', '')}")
if not ready:
    print("  (none)")
PY
