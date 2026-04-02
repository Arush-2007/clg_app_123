# SCHEMA NOTE (migration pending):
# MessageEntity (table `messages`) does NOT currently have an `is_anonymous`
# column. The `is_anonymous_sender` field in MessageResponse and the
# `is_anonymous` field in CreateConversationRequest are modelled here in
# anticipation of a future migration (e.g. 0011_chat_anonymous) that adds:
#   - messages.is_anonymous  BOOLEAN NOT NULL DEFAULT false
# Do NOT create that migration until the chat routes are ready to use it.

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Request models ─────────────────────────────────────────────────────────────

class CreateConversationRequest(BaseModel):
    type: Literal["direct", "group", "official"]
    name: Optional[str] = Field(default=None, max_length=120)
    avatar_url: Optional[str] = None
    # firebase UIDs of members to add (must include at least one)
    member_uids: list[str] = Field(min_length=1)
    # only relevant when type == "official"
    club_id: Optional[int] = None
    # True enables Reddit-style anonymous Q&A threads
    is_anonymous: bool = False


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    message_type: Literal["text", "image", "reel_share"] = "text"


# ── Response models ────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    sender_uid: str
    # Populated from the profiles table at the service layer; not a DB column.
    display_name: Optional[str] = None
    # True if the sender chose to post anonymously (requires DB migration 0011).
    is_anonymous_sender: bool = False
    content: str
    message_type: str
    is_deleted: bool
    created_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    club_id: Optional[int] = None
    college_id: Optional[int] = None
    created_by_uid: str
    # Populated by the service layer — not a direct ORM column.
    last_message: Optional[MessageResponse] = None
    unread_count: int = 0
    created_at: datetime


class ConversationDetailResponse(ConversationResponse):
    # List of firebase_uid strings for all current members.
    members: list[str] = []
