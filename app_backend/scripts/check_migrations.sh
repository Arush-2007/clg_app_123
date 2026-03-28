#!/bin/bash
set -e
cd "$(dirname "$0")/.."
CURRENT=$(alembic current 2>&1)
echo "Current: $CURRENT"
if echo "$CURRENT" | grep -q "(head)"; then
  echo "[OK] Database is up to date."
else
  echo "[FAIL] Unapplied migrations. Run: alembic upgrade head"
  exit 1
fi
