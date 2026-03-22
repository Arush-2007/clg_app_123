from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.debug_log import debug_log
from src.core.security import verify_firebase_token
from src.models.positions import Position, PositionResponse, Update_Position
from src.services.position_service import (
    ClubDoesNotExistError,
    PositionAlreadyExistsError,
    PositionDoesNotExistError,
    position_service,
)

router = APIRouter(prefix="/positions", tags=["positions"])


@router.post("", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
def create_position(
    position: Position,
    _: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
):
    # region agent log
    debug_log(
        run_id="run1",
        hypothesis_id="H2",
        location="positions_routes.py:create_position",
        message="create position request received",
        data={
            "club_name": position.club_name,
            "parent_college": position.parent_college,
            "hierarchy": position.hierarchy,
        },
    )
    # endregion
    try:
        return position_service.register_club_positions(db, position)
    except ClubDoesNotExistError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PositionAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("", response_model=list[PositionResponse])
def list_positions(
    c_id: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return position_service.list_positions(db, c_id=c_id, skip=skip, limit=limit)


@router.get("/{position_id}", response_model=PositionResponse)
def get_position(position_id: int, db: Session = Depends(get_db)):
    try:
        return position_service.get_position_by_id(db, position_id)
    except PositionDoesNotExistError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{position_id}", response_model=PositionResponse)
def update_position(
    position_id: int,
    payload: Update_Position,
    _: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
):
    try:
        return position_service.update_club_positions(db, position_id, payload)
    except PositionDoesNotExistError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PositionAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.delete("/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_position(
    position_id: int,
    _: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
):
    try:
        position_service.delete_position(db, position_id)
    except PositionDoesNotExistError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
