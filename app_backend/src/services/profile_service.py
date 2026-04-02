import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.entities import ProfileEntity
from src.models.profile import UpsertProfileRequest


class ProfileService:
    def upsert_profile(self, db: Session, firebase_uid: str, payload: UpsertProfileRequest) -> ProfileEntity:
        entity = db.scalar(select(ProfileEntity).where(ProfileEntity.firebase_uid == firebase_uid))
        data = payload.model_dump(mode="json")
        if data.get("skills") is not None:
            data["skills"] = json.dumps(data["skills"])
        if data.get("social_links") is not None:
            data["social_links"] = json.dumps(data["social_links"])
        if entity:
            for key, value in data.items():
                setattr(entity, key, value)
        else:
            entity = ProfileEntity(firebase_uid=firebase_uid, **data)
            db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def get_profile(self, db: Session, firebase_uid: str) -> ProfileEntity | None:
        return db.scalar(select(ProfileEntity).where(ProfileEntity.firebase_uid == firebase_uid))


profile_service = ProfileService()
