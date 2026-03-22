from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.entities import ProfileEntity
from src.models.profile import UpsertProfileRequest


class ProfileService:
    def upsert_profile(self, db: Session, firebase_uid: str, payload: UpsertProfileRequest) -> ProfileEntity:
        entity = db.scalar(select(ProfileEntity).where(ProfileEntity.firebase_uid == firebase_uid))
        if entity:
            for key, value in payload.model_dump().items():
                setattr(entity, key, value)
        else:
            entity = ProfileEntity(firebase_uid=firebase_uid, **payload.model_dump())
            db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def get_profile(self, db: Session, firebase_uid: str) -> ProfileEntity | None:
        return db.scalar(select(ProfileEntity).where(ProfileEntity.firebase_uid == firebase_uid))


profile_service = ProfileService()
