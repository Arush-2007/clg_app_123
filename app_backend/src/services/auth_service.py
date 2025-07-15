from src.models import User
from models.user import CreateUser, UpdateUser
from utils.prisma import db
from prisma_client.errors import UniqueViolationError

class UserAlreadyExistError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"User with email {self.value} already exist")


class AuthService:
    def __init__(self):
        pass

    async def create_user(self, user_id: str, user: CreateUser):
        try:
            return await db.user.create(data={
                "user_id": user_id,
                "email": user.email,
                "password": user.password
            })
        except UniqueViolationError as e:
            raise UserAlreadyExistError(user.email)
    
    async def update_user(self, user_id: str, update_data: UpdateUser) -> User | None:
        final_data = update_data.model_dump(exclude_unset=True, exclude_none=True)
        return await db.user.update(data=final_data, where={
            "user_id": user_id
        })
    
    async def delete_user(self, user_id: str) -> None:
        await db.user.delete(where={
            "user_id": user_id
        })

    async def get_user_by_id(self, user_id: str) :
        return await db.user.find_unique(where={
            "user_id": user_id
        })
    
    async def get_user_by_email(self, email: str) :
        return await db.user.find_unique(where={
            "email": email
        })
    

auth_service = AuthService()
