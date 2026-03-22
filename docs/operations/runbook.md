# Operations Runbook

## Health Endpoints

- Liveness: `GET /healthz`
- Readiness: `GET /readyz`
- Metrics snapshot: `GET /metrics`
- If metrics protection is enabled, send `X-Metrics-Token`.

## Common Checks

1. Confirm readiness is healthy.
2. Inspect application logs for error spikes.
3. Verify DB connection and migration state (`alembic current`).

## Incident Response

1. Acknowledge alert and classify severity.
2. Mitigate user impact (rollback/scale/restart).
3. Capture timeline and root-cause evidence.
4. Apply fix, validate with smoke tests.
5. Publish postmortem with action items.

## Backup and Restore Drill

- Schedule periodic DB backups and restoration tests.
- Validate restore can boot app and pass smoke tests.

## Rollback

- Keep previous deploy artifact available.
- Roll back backend and frontend independently when possible.
- Verify `/readyz` and critical flows after rollback.
