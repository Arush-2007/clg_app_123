from pydantic import BaseModel, EmailStr
from typing import Optional

class CreateUser(BaseModel):
    email: EmailStr
    password: str

class UpdateUser(BaseModel):
    email: EmailStr = None
    password: Optional[str] = None

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