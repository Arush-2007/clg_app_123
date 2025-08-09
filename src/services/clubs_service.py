from utils.prisma import db
from prisma_client.errors import UniqueViolationError
from src.models.clubs import RegisterClub, UpdateClub


class ClubAlreadyExistError(Exception):
    def __init__(self, value : str):
        self.value = value
        super().__init__(f"Club with name {self.value} already exist")

class ClubDoseNotExistError(Exception):
    def __init__(self, value : str):
        self.value = value
        super().__init__(f"Club with name {self.value} dose not exist")        

class ClubService:
    async def __init__(self):
        pass

    async def register_club(self, club : RegisterClub):
        c_id = f"{club.club_name}_{club.parent_college}"
        try:
            return await db.club.create(data = {
                "parent_college" : club.parent_college,
                "club_name" : club.club_name,
                "club_admin" : club.club_admin,
                "club_admin_email" : club.club_admin_email,
                "members"  :  club.members,
                "description" :  club.description,
                "c_id" : c_id
            })
        except UniqueViolationError as e:
            raise ClubAlreadyExistError(c_id)
        
    async def update_club_details(self,club_id :str,club : UpdateClub):
        finalised_club_details = club.model_dump(exclude_unset=True, exclude_none=True)
        return await db.club.update(data = finalised_club_details, where = {"club_id" : club_id})
    
    async def delete_club(self, club_id: str) -> None:
        await db.club.delete(where={
            "club_id": club_id
        })

    async def get_club_by_id(self, club_id: str) :
        return await db.club.find_unique(where={
            "club_id": club_id
        })    
    
clubs_service = ClubService()