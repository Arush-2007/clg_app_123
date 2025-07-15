from src.models import User
from models.user import Set_Up_Profile, Update_Profile
from utils.prisma import db

class UserService:
    def __init__(self):
        pass

    async def create_profile(self, user_id: str, User_Profile: Set_Up_Profile):
        return await db.user.update(data={
            "name": User_Profile.name,
            "college": User_Profile.college,
            "year": User_Profile.year,
            "branch": User_Profile.branch
        }, where={"user_id": user_id})

    async def update_profile(self, user_id: str, User_Profile: Update_Profile):
        finalised_profile = User_Profile.model_dump(exclude_unset=True, exclude_none=True)
        return await db.user.update(data=finalised_profile, where={"user_id": user_id})

    async def delete_profile(self, user_id: str):
        return await db.user.update(data={
            "name": None,
            "college": None,
            "year": None,
            "branch": None
        }, where={"user_id": user_id})
    

    async def upload_profile_picture(self, user_id: str, image_url: str):
        return await db.user.update(
           data={"image_url": image_url},
           where={"user_id": user_id}
    )


user_service = UserService()
