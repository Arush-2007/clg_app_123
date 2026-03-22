# College Application

This repository contains:

- `app_backend`: FastAPI backend (SQLAlchemy + Alembic + Firebase token verification)
- `app_frontend_app`: Flutter mobile/web app (Firebase Auth)

## Local Development

### Backend

1. Copy `app_backend/.env.example` to `app_backend/.env`.
2. Install dependencies:
   - `pip install -r app_backend/requirements.txt`
3. Run migrations:
   - `cd app_backend && alembic upgrade head`
4. Start server:
   - `cd app_backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`

Notes:
- Keep `AUTO_CREATE_SCHEMA=false` in non-dev environments.
- Keep `PROTECT_METRICS=true` in non-dev environments.

### Frontend

1. Install dependencies:
   - `cd app_frontend_app && flutter pub get`
2. Run app (example Android emulator):
   - `flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000`

For physical devices, set `API_BASE_URL` to your machine IP.

## CI Quality Gates

- Backend: `ruff`, Alembic migration smoke test, `pytest` with coverage.
- Frontend: `dart format --set-exit-if-changed`, `flutter analyze`, `flutter test`.

## Security and Operations

- Secret management and key rotation: `docs/security/secrets_and_rotation.md`
- Operations runbook: `docs/operations/runbook.md`
- Release checklist and soak plan: `docs/release/production_rollout_checklist.md`
- API auth policy: `docs/security/api_access_policy.md`
