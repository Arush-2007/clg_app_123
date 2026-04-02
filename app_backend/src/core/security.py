from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path

import firebase_admin
from fastapi import Depends, Header, HTTPException, status
from firebase_admin import auth, credentials
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.database import get_db
from src.core.debug_log import debug_log

logger = logging.getLogger(__name__)


@lru_cache
def _init_firebase() -> bool:
    settings = get_settings()
    if firebase_admin._apps:
        return True

    app_options = {"projectId": settings.firebase_project_id} if settings.firebase_project_id else None

    if settings.firebase_credentials_json:
        cred_raw = settings.firebase_credentials_json.strip()
        # Support either inline JSON content or a local file path.
        if cred_raw.startswith("{"):
            cred_info = json.loads(cred_raw)
        else:
            cred_path = Path(cred_raw)
            if not cred_path.is_absolute():
                cred_path = (Path(__file__).resolve().parents[2] / cred_path).resolve()
            cred_info = json.loads(cred_path.read_text(encoding="utf-8"))
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred, app_options)
        return True

    if settings.google_application_credentials:
        cred_path = Path(settings.google_application_credentials)
        if not cred_path.is_absolute():
            cred_path = (Path(__file__).resolve().parents[2] / cred_path).resolve()
        cred = credentials.Certificate(str(cred_path))
        firebase_admin.initialize_app(cred, app_options)
        return True

    try:
        firebase_admin.initialize_app(options=app_options)
        return True
    except Exception:
        return False


def verify_firebase_token(authorization: str | None = Header(default=None)) -> dict:
    settings = get_settings()
    firebase_ok = _init_firebase()
    logger.info("Firebase init status: %s, APP_ENV: %s", firebase_ok, settings.app_env)

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    if not firebase_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth provider not configured",
        )

    token = authorization.split(" ", 1)[1]
    check_revoked = settings.app_env == "production"
    try:
        return auth.verify_id_token(token, check_revoked=check_revoked)
    except Exception as exc:
        logger.error("Token verification failed: %s: %s", type(exc).__name__, exc)
        debug_log(
            run_id="run1",
            hypothesis_id="H6",
            location="security.py:verify_firebase_token",
            message="firebase token verification failed",
            data={
                "error_type": exc.__class__.__name__,
                "error": str(exc),
                "check_revoked": check_revoked,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def verify_admin(
    token: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
) -> dict:
    from src.db.entities import AdminEntity  # local import avoids circular dep

    uid = token["uid"]
    admin = db.query(AdminEntity).filter(
        AdminEntity.firebase_uid == uid
    ).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return token
