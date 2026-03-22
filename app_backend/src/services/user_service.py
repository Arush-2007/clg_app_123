from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.entities import UserEntity
from src.models.users import UpsertUserRequest


class UserService:
    def upsert_user(self, db: Session, firebase_uid: str, payload: UpsertUserRequest) -> UserEntity:
        entity = db.scalar(select(UserEntity).where(UserEntity.firebase_uid == firebase_uid))
        if not entity:
            entity = db.scalar(select(UserEntity).where(UserEntity.email == payload.email))

        if entity:
            entity.email = str(payload.email)
            entity.source = payload.source
            entity.firebase_uid = firebase_uid
        else:
            entity = UserEntity(
                firebase_uid=firebase_uid,
                email=str(payload.email),
                source=payload.source,
            )
            db.add(entity)

        db.commit()
        db.refresh(entity)
        return entity

    def get_user_by_uid(self, db: Session, firebase_uid: str) -> UserEntity | None:
        return db.scalar(select(UserEntity).where(UserEntity.firebase_uid == firebase_uid))


user_service = UserService()
