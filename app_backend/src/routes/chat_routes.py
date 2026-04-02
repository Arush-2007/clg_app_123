from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.connection_manager import manager
from src.core.database import get_db
from src.core.security import verify_firebase_token
from src.db.entities import ConversationMemberEntity, MessageEntity
from src.models.chat import (
    ConversationDetailResponse,
    ConversationResponse,
    CreateConversationRequest,
    MessageResponse,
    SendMessageRequest,
)
from src.services.chat_service import ChatService

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
_svc = ChatService()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _build_message_response(
    db: Session, msg: MessageEntity
) -> MessageResponse:
    """Build a MessageResponse, populating display_name from profiles."""
    display_name = _svc._get_display_name(db, msg.sender_uid)
    return MessageResponse(
        id=msg.id,
        conversation_id=msg.conversation_id,
        sender_uid=msg.sender_uid,
        display_name=display_name,
        # TODO (migration 0011): read msg.is_anonymous when column exists
        is_anonymous_sender=False,
        content=msg.content,
        message_type=msg.message_type,
        is_deleted=msg.is_deleted,
        created_at=msg.created_at,
    )


def _build_conversation_response(
    db: Session, conv, with_members: bool = False
) -> ConversationResponse | ConversationDetailResponse:
    """
    Build a ConversationResponse (or ConversationDetailResponse if with_members=True).
    Attaches the most recent non-deleted message as last_message.
    """
    last_msg_entity = db.scalar(
        select(MessageEntity)
        .where(
            MessageEntity.conversation_id == conv.id,
            MessageEntity.is_deleted.is_(False),
        )
        .order_by(MessageEntity.created_at.desc())
        .limit(1)
    )
    last_message = (
        _build_message_response(db, last_msg_entity)
        if last_msg_entity
        else None
    )

    base_fields = {
        "id": conv.id,
        "type": conv.type,
        "name": conv.name,
        "avatar_url": conv.avatar_url,
        "club_id": conv.club_id,
        "college_id": conv.college_id,
        "created_by_uid": conv.created_by_uid,
        "last_message": last_message,
        "unread_count": 0,  # TODO: compute from last_read_at once UI sends read receipts
        "created_at": conv.created_at,
    }

    if with_members:
        rows = db.scalars(
            select(ConversationMemberEntity).where(
                ConversationMemberEntity.conversation_id == conv.id
            )
        ).all()
        return ConversationDetailResponse(**base_fields, members=[r.firebase_uid for r in rows])

    return ConversationResponse(**base_fields)


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post(
    "/conversations",
    response_model=ConversationDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    payload: CreateConversationRequest,
    token: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
) -> ConversationDetailResponse:
    conv = _svc.create_conversation(db, creator_uid=token["uid"], payload=payload)
    return _build_conversation_response(db, conv, with_members=True)


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(
    token: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
) -> list[ConversationResponse]:
    conversations = _svc.get_user_conversations(db, firebase_uid=token["uid"])
    return [_build_conversation_response(db, c) for c in conversations]


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
)
def get_conversation(
    conversation_id: int,
    token: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
) -> ConversationDetailResponse:
    conv = _svc.get_conversation(db, conversation_id=conversation_id, firebase_uid=token["uid"])
    return _build_conversation_response(db, conv, with_members=True)


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def get_messages(
    conversation_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    before_id: Optional[int] = Query(default=None),
    token: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
) -> list[MessageResponse]:
    messages = _svc.get_messages(
        db,
        conversation_id=conversation_id,
        firebase_uid=token["uid"],
        limit=limit,
        before_id=before_id,
    )
    # Service returns DESC (newest first); reverse to ASC for chat display
    return [_build_message_response(db, m) for m in reversed(messages)]


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    conversation_id: int,
    payload: SendMessageRequest,
    token: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db),
) -> MessageResponse:
    msg = _svc.send_message(
        db,
        conversation_id=conversation_id,
        sender_uid=token["uid"],
        payload=payload,
    )
    response = _build_message_response(db, msg)
    # Broadcast to all active WebSocket connections in this room.
    # Clients not connected via WS will pick up the message on next REST poll.
    await manager.broadcast(conversation_id, response.model_dump(mode="json"))
    return response
