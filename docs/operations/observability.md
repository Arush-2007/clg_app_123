# Observability Baseline

## Logging

- Structured request logs include:
  - request id
  - method/path
  - status code
  - duration
- Response header `X-Request-ID` allows cross-system tracing.

## Metrics

- Expose lightweight app metrics via `GET /metrics`.
- Track at minimum:
  - request latency p95
  - error rate
  - auth failures
  - saturation indicators (CPU/memory)

## Alerts

- Trigger alerts on:
  - sustained 5xx rate above threshold
  - readiness failures
  - abnormal auth failure spikes
  - latency SLO breach

## Dashboards

- Separate dashboards for:
  - API health
  - auth and user onboarding
  - event/profile API throughput and errors
