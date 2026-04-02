from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.entities import (
    ConversationEntity,
    ConversationMemberEntity,
    MessageEntity,
    ProfileEntity,
)
from src.models.chat import CreateConversationRequest, SendMessageRequest


class ChatService:

    # ── Conversations ──────────────────────────────────────────────────────────

    def create_conversation(
        self,
        db: Session,
        creator_uid: str,
        payload: CreateConversationRequest,
    ) -> ConversationEntity:
        """
        Create a conversation and add all members including the creator.

        Rules:
        - 'direct': exactly 1 UID in member_uids (the other party). If a direct
          conversation between creator_uid and that UID already exists, return it.
        - 'group': name is required; 1+ UIDs in member_uids.
        - 'official': club_id must be provided; name is required.
        - Duplicate UIDs in member_uids are silently de-duplicated.
        """
        # Validate member_uids
        if not payload.member_uids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="member_uids must contain at least one UID",
            )

        # De-duplicate while preserving order, excluding creator (added later)
        seen: set[str] = set()
        unique_members: list[str] = []
        for uid in payload.member_uids:
            if uid not in seen and uid != creator_uid:
                seen.add(uid)
                unique_members.append(uid)

        # Type-specific validation
        if payload.type == "direct":
            if len(unique_members) != 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Direct conversations require exactly 1 member UID (not the creator)",
                )
            other_uid = unique_members[0]
            existing = self._find_direct_conversation(db, creator_uid, other_uid)
            if existing:
                return existing

        if payload.type == "official" and payload.club_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="club_id is required for official conversations",
            )

        # TODO (migration 0011): store payload.is_anonymous on the conversation
        # entity once the column exists.

        conversation = ConversationEntity(
            # Direct conversations intentionally have no name; the Flutter UI
            # renders the other participant's profile name instead.
            type=payload.type,
            name=None if payload.type == "direct" else payload.name,
            avatar_url=payload.avatar_url,
            club_id=payload.club_id,
            created_by_uid=creator_uid,
        )
        db.add(conversation)
        db.flush()  # obtain conversation.id before adding members

        # Add creator as admin
        db.add(ConversationMemberEntity(
            conversation_id=conversation.id,
            firebase_uid=creator_uid,
            role="admin",
        ))

        # Add remaining members
        for uid in unique_members:
            db.add(ConversationMemberEntity(
                conversation_id=conversation.id,
                firebase_uid=uid,
                role="member",
            ))

        db.commit()
        db.refresh(conversation)
        return conversation

    def get_user_conversations(
        self, db: Session, firebase_uid: str
    ) -> list[ConversationEntity]:
        """
        Return all conversations where firebase_uid is a member, ordered by
        the most recently created message DESC (falls back to conversation
        created_at if no messages exist). Soft-deleted messages are excluded
        from the ordering calculation.
        """
        # Subquery: latest non-deleted message timestamp per conversation
        latest_msg_sq = (
            select(
                MessageEntity.conversation_id,
                MessageEntity.created_at.label("latest_at"),
            )
            .where(MessageEntity.is_deleted.is_(False))
            .order_by(
                MessageEntity.conversation_id,
                MessageEntity.created_at.desc(),
            )
            .distinct(MessageEntity.conversation_id)
            .subquery()
        )

        # Conversations the user belongs to, joined with latest message time
        stmt = (
            select(ConversationEntity)
            .join(
                ConversationMemberEntity,
                ConversationMemberEntity.conversation_id == ConversationEntity.id,
            )
            .outerjoin(
                latest_msg_sq,
                latest_msg_sq.c.conversation_id == ConversationEntity.id,
            )
            .where(ConversationMemberEntity.firebase_uid == firebase_uid)
            .order_by(
                # Prefer latest message time; fall back to conversation creation
                latest_msg_sq.c.latest_at.desc().nullslast(),
                ConversationEntity.created_at.desc(),
            )
        )
        return list(db.scalars(stmt).all())

    def get_conversation(
        self,
        db: Session,
        conversation_id: int,
        firebase_uid: str,
    ) -> ConversationEntity:
        """Return the conversation or raise 404/403."""
        conversation = db.scalar(
            select(ConversationEntity).where(ConversationEntity.id == conversation_id)
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found",
            )
        if not self._is_member(db, conversation_id, firebase_uid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this conversation",
            )
        return conversation

    # ── Messages ───────────────────────────────────────────────────────────────

    def get_messages(
        self,
        db: Session,
        conversation_id: int,
        firebase_uid: str,
        limit: int = 50,
        before_id: Optional[int] = None,
    ) -> list[MessageEntity]:
        """
        Return up to `limit` non-deleted messages ordered newest-first.
        Pass `before_id` for cursor-based pagination (returns messages with
        id < before_id so the caller can page backwards through history).
        Raises 403 if the caller is not a member.
        """
        if not self._is_member(db, conversation_id, firebase_uid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this conversation",
            )

        stmt = (
            select(MessageEntity)
            .where(
                MessageEntity.conversation_id == conversation_id,
                MessageEntity.is_deleted.is_(False),
            )
            .order_by(MessageEntity.created_at.desc())
            .limit(limit)
        )
        if before_id is not None:
            stmt = stmt.where(MessageEntity.id < before_id)

        return list(db.scalars(stmt).all())

    def send_message(
        self,
        db: Session,
        conversation_id: int,
        sender_uid: str,
        payload: SendMessageRequest,
    ) -> MessageEntity:
        """
        Persist a new message and return the saved entity.
        Raises 403 if the sender is not a member of the conversation.
        """
        if not self._is_member(db, conversation_id, sender_uid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this conversation",
            )

        # TODO (migration 0011): also store payload.is_anonymous (from
        # SendMessageRequest or per-message flag) once the column exists.

        message = MessageEntity(
            conversation_id=conversation_id,
            sender_uid=sender_uid,
            content=payload.content,
            message_type=payload.message_type,
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _is_member(self, db: Session, conversation_id: int, uid: str) -> bool:
        """Return True if uid is an active member of the conversation."""
        row = db.scalar(
            select(ConversationMemberEntity).where(
                ConversationMemberEntity.conversation_id == conversation_id,
                ConversationMemberEntity.firebase_uid == uid,
            )
        )
        return row is not None

    def _get_display_name(self, db: Session, uid: str) -> Optional[str]:
        """
        Look up the profile name for a UID.
        Returns None if no profile record exists yet.
        Used to populate MessageResponse.display_name in the route layer.
        """
        profile = db.scalar(
            select(ProfileEntity).where(ProfileEntity.firebase_uid == uid)
        )
        return profile.name if profile else None

    def _find_direct_conversation(
        self, db: Session, uid_a: str, uid_b: str
    ) -> Optional[ConversationEntity]:
        """
        Return an existing direct conversation between uid_a and uid_b, or
        None if no such conversation exists.

        The query looks for a conversation of type='direct' where both UIDs
        are members. A direct conversation always has exactly 2 members so we
        join twice to assert both are present.
        """
        member_a = ConversationMemberEntity.__table__.alias("m_a")
        member_b = ConversationMemberEntity.__table__.alias("m_b")

        stmt = (
            select(ConversationEntity)
            .join(member_a, member_a.c.conversation_id == ConversationEntity.id)
            .join(member_b, member_b.c.conversation_id == ConversationEntity.id)
            .where(
                ConversationEntity.type == "direct",
                member_a.c.firebase_uid == uid_a,
                member_b.c.firebase_uid == uid_b,
            )
            .limit(1)
        )
        return db.scalar(stmt)


chat_service = ChatService()
