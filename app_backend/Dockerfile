# ── Stage 1: builder ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
# Copying requirements first maximises Docker layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install only runtime system deps (libpq for psycopg2, curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Create non-root user — Cloud Run security requirement
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home --shell /bin/false appuser

# Copy application source
COPY --chown=appuser:appgroup . .

RUN mkdir -p /app/uploads && chown -R appuser:appgroup /app/uploads

# Switch to non-root user
USER appuser

# Cloud Run injects PORT env var — default 8080
ENV PORT=8080

# Healthcheck — Cloud Run calls /healthz to verify container is ready
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT}/healthz || exit 1

# Run migrations then start uvicorn on Cloud Run's injected PORT
# --workers 1 because Cloud Run scales via instances, not workers
# --no-access-log reduces log noise (Cloud Run captures stdout anyway)
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port ${PORT} --workers 1 --no-access-log"]
