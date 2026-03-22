# Secrets and Rotation Guide

## Secret Storage Rules

- Never commit `.env` files or service-account credentials.
- Store production secrets in a managed secrets provider.
- Inject secrets into runtime via environment variables.

## Required Backend Secrets

- `DATABASE_URL`
- `FIREBASE_CREDENTIALS_JSON` (or workload identity on cloud)

## Rotation Policy

- Rotate credentials on schedule (every 90 days minimum).
- Rotate immediately after accidental exposure or suspicious activity.
- Invalidate old credentials only after new credential validation.

## Firebase Key Hygiene

- Treat Firebase client keys as public identifiers, not secrets.
- Restrict API keys by platform/app and API scope in Firebase/Google Cloud.
- Enable Firebase App Check for abuse protection.

## Incident Steps (Key Leak)

1. Identify exposed key and affected services.
2. Issue replacement key/credential.
3. Deploy updated secret/config.
4. Revoke old key.
5. Audit access logs and alert on anomalies.
