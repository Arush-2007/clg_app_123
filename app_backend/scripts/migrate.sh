#!/bin/bash
set -e
echo "[migrate] Running Alembic migrations..."
cd "$(dirname "$0")/.."
alembic upgrade head
echo "[migrate] Migration complete."
