# Backend Guide

## Stack

- FastAPI
- SQLAlchemy ORM
- Alembic migrations
- Firebase Admin token verification

## Setup

1. `cp .env.example .env`
2. `pip install -r requirements.txt`
3. `alembic upgrade head`
4. `uvicorn src.main:app --reload`

## Important Runtime Flags

- `AUTO_CREATE_SCHEMA=false` for staging/production.
- `AUTO_CREATE_SCHEMA=true` only for local bootstrap convenience.
- `PROTECT_METRICS=true` in shared environments.
- `METRICS_TOKEN=<secure-random-value>` and pass it as `X-Metrics-Token` header.

## Migrations

- Create migration: `alembic revision -m "description" --autogenerate`
- Apply migration: `alembic upgrade head`
- Rollback one step: `alembic downgrade -1`
