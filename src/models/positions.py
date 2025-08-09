from pydantic import BaseModel, EmailStr
from typing import Optional

class Position(BaseModel):
    parent_college : str
    club_name :str
    hierarchy : int
    hierarchy_holders : int

class Update_Position(BaseModel):
    parent_college : Optional[str]
    club_name :Optional[str]
    hierarchy : Optional[int]
    hierarchy_holders : Optional[int]




class Position_Holder(BaseModel):
    holder_hierarchy : int
    position_name : str
    holder_email : EmailStr