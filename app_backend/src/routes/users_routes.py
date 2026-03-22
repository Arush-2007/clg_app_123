from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.debug_log import debug_log
from src.core.security import verify_firebase_token
from src.models.users import UpsertUserRequest, UserResponse
from src.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_200_OK)
def upsert_user(
    payload: UpsertUserRequest,
    token_claims: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
):
    # region agent log
    debug_log(
        run_id="run1",
        hypothesis_id="H3",
        location="users_routes.py:upsert_user",
        message="upsert user request received",
        data={"token_uid_present": bool(token_claims.get("uid")), "source": payload.source},
    )
    # endregion
    firebase_uid = token_claims.get("uid")
    if not firebase_uid:
        raise HTTPException(status_code=401, detail="Invalid token claims")
    return user_service.upsert_user(db, firebase_uid, payload)


@router.get("/me", response_model=UserResponse)
def get_current_user(
    token_claims: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
):
    firebase_uid = token_claims.get("uid")
    if not firebase_uid:
        raise HTTPException(status_code=401, detail="Invalid token claims")
    entity = user_service.get_user_by_uid(db, firebase_uid)
    if not entity:
        raise HTTPException(status_code=404, detail="User not found")
    return entity
