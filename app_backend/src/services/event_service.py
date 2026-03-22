from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.entities import EventEntity
from src.models.events import CreateEvent


class EventService:
    def create_event(self, db: Session, payload: CreateEvent) -> EventEntity:
        entity = EventEntity(
            title=payload.title,
            image_url=str(payload.image_url),
            status=payload.status,
            starts_at=payload.starts_at,
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def list_events(self, db: Session, status: str | None = None, skip: int = 0, limit: int = 20) -> list[EventEntity]:
        stmt = select(EventEntity)
        if status:
            stmt = stmt.where(EventEntity.status == status)
        stmt = stmt.offset(skip).limit(limit)
        return list(db.scalars(stmt).all())


event_service = EventService()
