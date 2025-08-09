from utils.prisma import db
from prisma.errors import UniqueViolationError  # correct import path
from src.models.positions import Position, Position_Holder, Update_Position
from services.clubs_service import clubs_service


class ClubDoesNotExistError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"Club with c_id '{self.value}' doesn't exist")

class HierarchyNotEnough(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"User does not have enough hierarchy in club '{self.value}")



class PositionService:

    # async def registering_club_registrars(self):


    async def register_club_positions(self, position: Position):
        position_data = position.model_dump()
        p_c_id = f"{position_data['parent_college']}_{position_data['club_name']}"

        p_club = await db.club.find_first(where={"c_id": p_c_id})
        if not p_club:
            raise ClubDoesNotExistError(p_c_id)
        
        if position_data.get("hierarchy") != 1:
            raise HierarchyNotEnough(position_data["hierarchy"])

        return await db.positions.create(data={
            "Hierarchy": position.hierarchy,
            "Hierarchy_Holders": position.hierarchy_holders,
            "c_id": p_c_id
        })
    
    async def update_club_positions(self, previous_position: Position, updated_position : Update_Position):
        position_data = previous_position.model_dump()
        p_c_id = f"{position_data['parent_college']}_{position_data['club_name']}"

        p_club = await db.club.find_first(where={"c_id": p_c_id})
        if not p_club:
            raise ClubDoesNotExistError(p_c_id)

        if position_data.get("hierarchy") != 1:
            raise HierarchyNotEnough(position_data["hierarchy"])
        
        updated_position_data = updated_position.model_dump(exclude_unset=True, exclude_none=True)

        return await db.positions.update(data=updated_position_data, where = {"c_id":p_c_id})

