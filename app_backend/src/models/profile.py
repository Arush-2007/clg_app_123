from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class UpsertProfileRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    college: str = Field(min_length=2, max_length=120)
    year_of_graduation: str = Field(min_length=4, max_length=10)
    branch: str = Field(min_length=2, max_length=120)
    avatar_url: HttpUrl
    latitude: str = "Not specified"
    longitude: str = "Not specified"
    bio: Optional[str] = Field(default=None, max_length=500)
    skills: Optional[list[str]] = None
    social_links: Optional[dict[str, str]] = None
    is_alumni: bool = False


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile_id: int
    firebase_uid: str
    name: str
    college: str
    year_of_graduation: str
    branch: str
    avatar_url: str
    latitude: str
    longitude: str
    bio: Optional[str] = None
    skills: Optional[str] = None
    social_links: Optional[str] = None
    is_premium: bool = False
    is_alumni: bool = False
    college_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
