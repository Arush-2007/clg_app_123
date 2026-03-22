from __future__ import annotations

import json
from functools import lru_cache

import firebase_admin
from fastapi import Header, HTTPException, status
from firebase_admin import auth, credentials

from src.core.config import get_settings


@lru_cache
def _init_firebase() -> bool:
    settings = get_settings()
    if firebase_admin._apps:
        return True

    if settings.firebase_credentials_json:
        cred_info = json.loads(settings.firebase_credentials_json)
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred)
        return True

    try:
        firebase_admin.initialize_app()
        return True
    except Exception:
        return False


def verify_firebase_token(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    if not _init_firebase():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth provider not configured",
        )

    token = authorization.split(" ", 1)[1]
    try:
        return auth.verify_id_token(token, check_revoked=True)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc
