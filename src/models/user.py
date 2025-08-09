from typing import Optional
from pydantic import BaseModel, SecretStr, field_validator, EmailStr
from pydantic_core import PydanticCustomError
import re

class UserBase(BaseModel):
    @classmethod
    def validate_password_logic(cls, password: str) -> None:
        """Shared password validation logic"""
        if len(password) < 6:
            raise PydanticCustomError(
                'password_too_short',
                'Password must be at least 6 characters long',
                {}
            )
        
        if not re.search(r"[A-Z]", password):
            raise PydanticCustomError(
                'password_missing_uppercase',
                'Password must contain at least one uppercase letter',
                {}
            )
        
        if not re.search(r"[a-z]", password):
            raise PydanticCustomError(
                'password_missing_lowercase', 
                'Password must contain at least one lowercase letter',
                {}
            )
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise PydanticCustomError(
                'password_missing_special',
                'Password must contain at least one special character',
                {}
            )

class CreateUser(UserBase):
    email: EmailStr
    password: SecretStr

    @field_validator("password")
    @classmethod
    def password_validator(cls, v: SecretStr) -> SecretStr:
        cls.validate_password_logic(v.get_secret_value())
        return v

class UpdateUser(UserBase):
    email: Optional[EmailStr] = None
    password: Optional[SecretStr] = None

    @field_validator("password")
    @classmethod
    def password_validator(cls, v: Optional[SecretStr]) -> Optional[SecretStr]:
        if v is None:
            return v
        cls.validate_password_logic(v.get_secret_value())
        return v


class Set_Up_Profile (BaseModel):
    name :str
    college :str
    branch : str
    year : str

class Update_Profile (BaseModel):
    name :Optional[str] = None
    college :Optional[str] = None
    branch : Optional[str] = None
    year : Optional[str] = None