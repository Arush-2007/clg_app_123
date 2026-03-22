from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.debug_log import debug_log
from src.core.security import verify_firebase_token
from src.models.clubs import ClubResponse, RegisterClub, UpdateClub
from src.services.clubs_service import (
    ClubAlreadyExistError,
    ClubDoesNotExistError,
    clubs_service,
)

router = APIRouter(prefix="/clubs", tags=["clubs"])


@router.post("", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
def create_club(
    club: RegisterClub,
    _: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
):
    # region agent log
    debug_log(
        run_id="run1",
        hypothesis_id="H1",
        location="clubs_routes.py:create_club",
        message="create club request received",
        data={"club_name": club.club_name, "parent_college": club.parent_college},
    )
    # endregion
    try:
        return clubs_service.register_club(db, club)
    except ClubAlreadyExistError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("", response_model=list[ClubResponse])
def list_clubs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return clubs_service.list_clubs(db, skip=skip, limit=limit)


@router.get("/{club_id}", response_model=ClubResponse)
def get_club(club_id: int, db: Session = Depends(get_db)):
    try:
        return clubs_service.get_club_by_id(db, club_id)
    except ClubDoesNotExistError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{club_id}", response_model=ClubResponse)
def update_club(
    club_id: int,
    club: UpdateClub,
    _: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
):
    try:
        return clubs_service.update_club_details(db, club_id, club)
    except ClubDoesNotExistError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ClubAlreadyExistError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.delete("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_club(
    club_id: int,
    _: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
):
    try:
        clubs_service.delete_club(db, club_id)
    except ClubDoesNotExistError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
