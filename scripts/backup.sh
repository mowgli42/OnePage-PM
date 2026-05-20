#!/usr/bin/env bash
# Backup JSON data directory to a timestamped tarball.
set -euo pipefail
DATA_DIR="${DATA_DIR:-backend/data}"
OUT_DIR="${1:-.}"
STAMP=$(date +%Y%m%d-%H%M%S)
ARCHIVE="$OUT_DIR/oppm-backup-$STAMP.tar.gz"
mkdir -p "$OUT_DIR"
tar -czf "$ARCHIVE" -C "$(dirname "$DATA_DIR")" "$(basename "$DATA_DIR")"
echo "Created $ARCHIVE"
