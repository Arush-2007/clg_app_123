from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr


class UpsertUserRequest(BaseModel):
    email: EmailStr
    source: Literal["email-password", "google-signin"]


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    firebase_uid: str
    email: EmailStr
    source: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
