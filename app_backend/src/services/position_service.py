from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.debug_log import debug_log
from src.db.entities import ClubEntity, PositionEntity
from src.models.positions import Position, Update_Position


class ClubDoesNotExistError(Exception):
    pass


class PositionDoesNotExistError(Exception):
    pass


class PositionAlreadyExistsError(Exception):
    pass


class PositionService:
    @staticmethod
    def _build_cid(parent_college: str, club_name: str) -> str:
        return f"{club_name.strip().lower()}_{parent_college.strip().lower()}"

    def register_club_positions(self, db: Session, position: Position) -> PositionEntity:
        p_c_id = self._build_cid(position.parent_college, position.club_name)
        p_club = db.scalar(select(ClubEntity).where(ClubEntity.c_id == p_c_id))
        # region agent log
        debug_log(
            run_id="run1",
            hypothesis_id="H2",
            location="position_service.py:register_club_positions",
            message="position c_id lookup result",
            data={"p_c_id": p_c_id, "club_found": p_club is not None},
        )
        # endregion
        if not p_club:
            raise ClubDoesNotExistError(f"Club with c_id '{p_c_id}' doesn't exist")

        entity = PositionEntity(
            c_id=p_c_id,
            hierarchy=position.hierarchy,
            hierarchy_holders=position.hierarchy_holders,
            position_name=position.position_name,
        )
        db.add(entity)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise PositionAlreadyExistsError("Hierarchy already exists for this club") from exc
        db.refresh(entity)
        return entity

    def update_club_positions(self, db: Session, position_id: int, updated_position: Update_Position) -> PositionEntity:
        entity = self.get_position_by_id(db, position_id)
        updates = updated_position.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in updates.items():
            setattr(entity, key, value)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise PositionAlreadyExistsError("Hierarchy already exists for this club") from exc
        db.refresh(entity)
        return entity

    def delete_position(self, db: Session, position_id: int) -> None:
        entity = self.get_position_by_id(db, position_id)
        db.delete(entity)
        db.commit()

    def get_position_by_id(self, db: Session, position_id: int) -> PositionEntity:
        entity = db.get(PositionEntity, position_id)
        if not entity:
            raise PositionDoesNotExistError(f"Position with id '{position_id}' does not exist")
        return entity

    def list_positions(self, db: Session, c_id: str | None = None, skip: int = 0, limit: int = 20) -> list[PositionEntity]:
        stmt = select(PositionEntity)
        if c_id:
            stmt = stmt.where(PositionEntity.c_id == c_id)
        stmt = stmt.offset(skip).limit(limit)
        return list(db.scalars(stmt).all())


position_service = PositionService()

