from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CreateEvent(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    image_url: HttpUrl
    status: Literal["ongoing", "upcoming"]
    starts_at: Optional[datetime] = None


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: int
    title: str
    image_url: str
    status: str
    starts_at: Optional[datetime]
    created_at: datetime
