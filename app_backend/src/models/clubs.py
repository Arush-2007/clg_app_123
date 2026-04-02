from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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
    club_admin_email: Optional[str] = None
    members: int
    description: str
    c_id: str
    status: str
    document_url: str | None = None
    rejection_reason: str | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("club_admin_email", mode="before")
    @classmethod
    def coerce_empty_email_to_none(cls, v: object) -> object:
        if isinstance(v, str) and not v.strip():
            return None
        return v


class ClubMemberInput(BaseModel):
    firebase_uid: str
    position_name: str = "Member"
    hierarchy: int = 99


class ClubRegistrationRequest(BaseModel):
    """Used when a student submits a club registration request."""

    parent_college: str = Field(min_length=2, max_length=120)
    club_name: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=10, max_length=5000)
    members: List[ClubMemberInput]
    # firebase_uid of the member who will manage the club account
    account_manager_uid: str
    # document_url is set after the document image is uploaded via
    # POST /media/upload — frontend uploads first, then sends URL here
    document_url: str


class ClubRegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    club_id: int
    club_name: str
    parent_college: str
    description: str
    status: str
    document_url: str | None
    created_at: datetime


class ClubVerificationRequest(BaseModel):
    """Used by admin to approve or reject a club."""

    action: str  # "approve" | "reject"
    rejection_reason: str | None = None


class ClubStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    club_id: int
    club_name: str
    status: str
    verified_at: datetime | None
    rejection_reason: str | None


class ClubMemberOut(BaseModel):
    """Response for GET /clubs/{club_id}/members (ORM serialization)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    club_id: int
    firebase_uid: str
    position_name: str
    hierarchy: int
    joined_at: datetime
