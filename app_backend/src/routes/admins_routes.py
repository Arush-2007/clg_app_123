import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import verify_admin
from src.db.entities import AdminEntity

router = APIRouter(prefix="/admins", tags=["admins"])


# ── Request bodies ────────────────────────────────────────────────────────────

class SeedRequest(BaseModel):
    firebase_uid: str
    secret: str


class AddAdminRequest(BaseModel):
    firebase_uid: str


# ── Response schema (plain dict is fine, but explicit is cleaner) ─────────────

class AdminOut(BaseModel):
    id: int
    firebase_uid: str
    added_by_uid: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_admin(body: SeedRequest, db: Session = Depends(get_db)):
    """
    Bootstrap endpoint — no auth required. Guarded by ADMIN_SEED_SECRET.
    Use once to add your own UID as the first admin.
    """
    from src.core.config import settings
    expected = settings.admin_seed_secret
    if not expected or body.secret != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid seed secret",
        )

    existing = db.query(AdminEntity).filter(
        AdminEntity.firebase_uid == body.firebase_uid
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already an admin",
        )

    admin = AdminEntity(
        firebase_uid=body.firebase_uid,
        added_by_uid=None,
        created_at=datetime.now(timezone.utc),
    )
    db.add(admin)
    db.commit()
    return {"message": "Admin created", "firebase_uid": body.firebase_uid}


@router.post("/add", status_code=status.HTTP_201_CREATED)
def add_admin(
    body: AddAdminRequest,
    token: dict = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Add another admin. Caller must already be an admin."""
    existing = db.query(AdminEntity).filter(
        AdminEntity.firebase_uid == body.firebase_uid
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already an admin",
        )

    admin = AdminEntity(
        firebase_uid=body.firebase_uid,
        added_by_uid=token["uid"],
        created_at=datetime.now(timezone.utc),
    )
    db.add(admin)
    db.commit()
    return {"message": "Admin created", "firebase_uid": body.firebase_uid}


@router.get("", response_model=list[AdminOut])
def list_admins(
    _: dict = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """List all admins. Admin-only."""
    return db.query(AdminEntity).order_by(AdminEntity.created_at).all()
