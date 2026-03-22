# Production Rollout Checklist

## Pre-Release

- [ ] CI green on backend and frontend.
- [ ] `alembic upgrade head` successful in staging.
- [ ] `AUTO_CREATE_SCHEMA=false` in staging/prod environment.
- [ ] `PROTECT_METRICS=true` and `METRICS_TOKEN` configured.
- [ ] Security review completed for auth and API validation.
- [ ] Secrets verified in environment manager.
- [ ] Backward compatibility validated for API consumers.

## Staging Soak (minimum 7 days)

- [ ] Run core user journeys daily:
  - signup/login
  - profile upload
  - events list/create
  - clubs/positions CRUD
- [ ] Monitor error rate and latency trends.
- [ ] Validate alerting and on-call handoff.

## Production Deployment

- [ ] Deploy backend migration and app.
- [ ] Deploy frontend with correct `API_BASE_URL`.
- [ ] Verify `/readyz`, `/healthz`, and smoke tests.
- [ ] Monitor first hour with heightened alertness.

## Post-Deploy

- [ ] Confirm no regression in onboarding flow.
- [ ] Confirm error budget remains healthy.
- [ ] Record release notes and known issues.
