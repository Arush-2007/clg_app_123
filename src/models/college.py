from pydantic import BaseModel
from typing import Optional

class College_Register(BaseModel):
    college_name   : str
    clubs_recognized : int


class College_Club_Update(BaseModel):
    clubs_recognized : Optional[int]