from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Position(BaseModel):
    parent_college: str = Field(min_length=2, max_length=120)
    club_name: str = Field(min_length=2, max_length=120)
    hierarchy: int = Field(ge=1, le=10)
    hierarchy_holders: int = Field(ge=1, le=100)
    position_name: str = Field(default="Member", min_length=2, max_length=120)


class Update_Position(BaseModel):
    hierarchy: Optional[int] = Field(default=None, ge=1, le=10)
    hierarchy_holders: Optional[int] = Field(default=None, ge=1, le=100)
    position_name: Optional[str] = Field(default=None, min_length=2, max_length=120)


class Position_Holder(BaseModel):
    holder_hierarchy: int
    position_name: str
    holder_email: EmailStr


class PositionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    position_id: int
    c_id: str
    hierarchy: int
    hierarchy_holders: int
    position_name: str
    created_at: datetime
    updated_at: datetime
