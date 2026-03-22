from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.debug_log import debug_log
from src.core.security import verify_firebase_token
from src.models.events import CreateEvent, EventResponse
from src.services.event_service import event_service

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: CreateEvent,
    _: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
):
    # region agent log
    debug_log(
        run_id="run1",
        hypothesis_id="H5",
        location="events_routes.py:create_event",
        message="create event request received",
        data={"status": payload.status, "title_len": len(payload.title)},
    )
    # endregion
    return event_service.create_event(db, payload)


@router.get("", response_model=list[EventResponse])
def list_events(
    status_filter: Literal["ongoing", "upcoming"] | None = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return event_service.list_events(db, status=status_filter, skip=skip, limit=limit)
