from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.debug_log import debug_log
from src.core.security import verify_firebase_token
from src.models.profile import ProfileResponse, UpsertProfileRequest
from src.services.profile_service import profile_service

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("/me", response_model=ProfileResponse)
def upsert_profile(
    payload: UpsertProfileRequest,
    token_claims: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
):
    # region agent log
    debug_log(
        run_id="run1",
        hypothesis_id="H4",
        location="profile_routes.py:upsert_profile",
        message="profile upsert request received",
        data={"token_uid_present": bool(token_claims.get("uid")), "has_college": bool(payload.college)},
    )
    # endregion
    firebase_uid = token_claims.get("uid")
    if not firebase_uid:
        raise HTTPException(status_code=401, detail="Invalid token claims")
    return profile_service.upsert_profile(db, firebase_uid, payload)


@router.get("/me", response_model=ProfileResponse)
def get_profile(
    token_claims: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
):
    # region agent log
    debug_log(
        run_id="run1",
        hypothesis_id="H4",
        location="profile_routes.py:get_profile",
        message="profile get request received",
        data={"token_uid_present": bool(token_claims.get("uid"))},
    )
    # endregion
    firebase_uid = token_claims.get("uid")
    if not firebase_uid:
        raise HTTPException(status_code=401, detail="Invalid token claims")
    profile = profile_service.get_profile(db, firebase_uid)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
