#!/bin/bash
set -e
if [ "$APP_ENV" = "production" ]; then
  echo "ERROR: Never run this in production."
  exit 1
fi
echo "[dev] Resetting database..."
cd "$(dirname "$0")/.."
alembic downgrade base
alembic upgrade head
echo "[dev] Done."
