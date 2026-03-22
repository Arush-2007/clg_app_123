from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.debug_log import debug_log
from src.db.entities import ClubEntity
from src.models.clubs import RegisterClub, UpdateClub


class ClubAlreadyExistError(Exception):
    pass


class ClubDoesNotExistError(Exception):
    pass


class ClubService:
    @staticmethod
    def _build_cid(parent_college: str, club_name: str) -> str:
        return f"{club_name.strip().lower()}_{parent_college.strip().lower()}"

    def register_club(self, db: Session, club: RegisterClub) -> ClubEntity:
        c_id = self._build_cid(club.parent_college, club.club_name)
        # region agent log
        debug_log(
            run_id="run1",
            hypothesis_id="H1",
            location="clubs_service.py:register_club",
            message="register club computed c_id",
            data={"c_id": c_id},
        )
        # endregion
        payload = club.model_dump()
        entity = ClubEntity(**payload, c_id=c_id)
        db.add(entity)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise ClubAlreadyExistError(f"Club with c_id '{c_id}' already exists") from exc
        db.refresh(entity)
        return entity

    def update_club_details(self, db: Session, club_id: int, club: UpdateClub) -> ClubEntity:
        entity = self.get_club_by_id(db, club_id)
        updates = club.model_dump(exclude_unset=True, exclude_none=True)
        if "club_name" in updates or "parent_college" in updates:
            new_name = updates.get("club_name", entity.club_name)
            new_college = updates.get("parent_college", entity.parent_college)
            entity.c_id = self._build_cid(new_college, new_name)
        for key, value in updates.items():
            setattr(entity, key, value)

        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise ClubAlreadyExistError("A club with same college and name already exists") from exc
        db.refresh(entity)
        return entity

    def delete_club(self, db: Session, club_id: int) -> None:
        entity = self.get_club_by_id(db, club_id)
        db.delete(entity)
        db.commit()

    def get_club_by_id(self, db: Session, club_id: int) -> ClubEntity:
        entity = db.get(ClubEntity, club_id)
        if not entity:
            raise ClubDoesNotExistError(f"Club with id '{club_id}' does not exist")
        return entity

    def list_clubs(self, db: Session, skip: int = 0, limit: int = 20) -> list[ClubEntity]:
        stmt = select(ClubEntity).offset(skip).limit(limit)
        return list(db.scalars(stmt).all())


clubs_service = ClubService()
