from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CreateEvent(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    image_url: HttpUrl
    status: Literal["ongoing", "upcoming"]
    starts_at: Optional[datetime] = None
    event_type: Literal["online", "offline"] = "offline"
    registration_url: Optional[HttpUrl] = None
    max_registrations: Optional[int] = Field(default=None, gt=0)


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: int
    title: str
    image_url: str
    status: str
    starts_at: Optional[datetime] = None
    creator_uid: Optional[str] = None
    event_type: str = "offline"
    registration_url: Optional[str] = None
    max_registrations: Optional[int] = None
    college_id: Optional[int] = None
    created_at: datetime
