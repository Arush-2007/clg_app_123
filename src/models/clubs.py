from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterClub(BaseModel):
    parent_college : str
    club_name : str
    club_admin : str
    club_admin_email :EmailStr
    members  :  int
    description :  str

class UpdateClub(BaseModel):
    parent_college : Optional[str]
    club_name : Optional[str]
    club_admin : Optional[str]
    club_admin_email :Optional[EmailStr]
    members  :  Optional[int]
    description : Optional[str]