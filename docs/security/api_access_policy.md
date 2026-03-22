# API Access Policy

This policy documents which API groups are public vs authenticated.

## Public Endpoints

- `GET /healthz`
- `GET /readyz`
- `GET /api/v1/clubs`
- `GET /api/v1/clubs/{club_id}`
- `GET /api/v1/positions`
- `GET /api/v1/positions/{position_id}`
- `GET /api/v1/events`

## Authenticated Endpoints (Firebase ID token required)

- `POST/PATCH/DELETE /api/v1/clubs/*`
- `POST/PATCH/DELETE /api/v1/positions/*`
- `POST /api/v1/events`
- `POST /api/v1/users`
- `GET /api/v1/users/me`
- `POST /api/v1/profiles/me`
- `GET /api/v1/profiles/me`
- `POST /api/v1/media/upload`

## Operational Endpoints

- `GET /metrics` is protected when `PROTECT_METRICS=true`.
- When protected, include header `X-Metrics-Token: <METRICS_TOKEN>`.
