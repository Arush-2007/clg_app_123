from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import text

from src.core.config import get_settings
from src.core.database import SessionLocal
from src.core.telemetry import metrics_store

router = APIRouter(tags=["system"])

_started_at = datetime.now(timezone.utc)
settings = get_settings()


@router.get("/healthz")
def healthz():
    return {"status": "ok", "started_at": _started_at.isoformat()}


@router.get("/readyz")
def readyz():
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database is not ready") from exc


@router.get("/metrics")
def metrics(x_metrics_token: str | None = Header(default=None)):
    if settings.protect_metrics and x_metrics_token != settings.metrics_token:
        raise HTTPException(status_code=403, detail="Metrics endpoint is protected")
    uptime_seconds = (datetime.now(timezone.utc) - _started_at).total_seconds()
    snapshot = metrics_store.snapshot()
    return {
        "app_uptime_seconds": uptime_seconds,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "requests": snapshot,
    }
