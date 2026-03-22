from src.models import User
from models.user import CreateUser, UpdateUser
from utils.prisma import db
from prisma_client.errors import UniqueViolationError
from utils.email_validator import EmailValidator
import bcrypt

class UserAlreadyExistError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"User with email {self.value} already exist")

class DifferentPasswordNeeded(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"Password {self.value} is already in use")

class UserNotFoundError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"User with {self.value} dosen't exist")
                
class InvalidCredentialsError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"Password {self.value} is not valid")

class AuthService:
    # def __init__(self):
    #     pass

    def __init__(self, verify_email_existence: bool = False):
        self.verify_email_existence = verify_email_existence

    @staticmethod
    def hash_password(password: str) -> str:
        """ADD: Password hashing method"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """ADD: Password verification method"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))    
    
    async def create_user(self, user_id: str, user: CreateUser):
        if self.verify_email_existence:
            if not EmailValidator.check_domain_mx(user.email):
                raise ValueError("Email domain cannot receive emails")
            
        try:
            hashed_password = self.hash_password(user.password.get_secret_value())

            return await db.user.create(data={
                "user_id": user_id,
                "email": user.email,
                "password": hashed_password
            })
        except UniqueViolationError as e:
            raise UserAlreadyExistError(user.email)
        
    async def login_user_detailed(self, user: CreateUser) -> User:
        
        user_log = await self.get_user_by_email(user.email)
        
        
        if not user_log:
            raise UserNotFoundError(user.email)
        
        
        if not self.verify_password(user.password, user_log.password):
            raise InvalidCredentialsError()
        
        return True    
    
    async def update_user(self, user_id: str, update_data: UpdateUser) -> User | None:

        updated_hashed_password = self.hash_password(update_data.password.get_secret_value())

        return await db.user.update(where = {"user_id" : user_id},data={
                "password": updated_hashed_password
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