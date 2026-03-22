from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterClub(BaseModel):
    parent_college: str = Field(min_length=2, max_length=120)
    club_name: str = Field(min_length=2, max_length=120)
    club_admin: str = Field(min_length=2, max_length=120)
    club_admin_email: EmailStr
    members: int = Field(ge=0)
    description: str = Field(min_length=10, max_length=5000)


class UpdateClub(BaseModel):
    parent_college: Optional[str] = Field(default=None, min_length=2, max_length=120)
    club_name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    club_admin: Optional[str] = Field(default=None, min_length=2, max_length=120)
    club_admin_email: Optional[EmailStr] = None
    members: Optional[int] = Field(default=None, ge=0)
    description: Optional[str] = Field(default=None, min_length=10, max_length=5000)


class ClubResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    club_id: int
    parent_college: str
    club_name: str
    club_admin: str
    club_admin_email: EmailStr
    members: int
    description: str
    c_id: str
    created_at: datetime
    updated_at: datetime
