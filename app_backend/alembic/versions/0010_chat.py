"""conversations, conversation_members, messages

Revision ID: 0010_chat
Revises: 0009_profile_extensions
Create Date: 2026-03-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010_chat"
down_revision: str | None = "0009_profile_extensions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create conversations table
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("name", sa.String(200), nullable=True),
        sa.Column("avatar_url", sa.String(512), nullable=True),
        sa.Column(
            "college_id",
            sa.Integer(),
            sa.ForeignKey("colleges.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "club_id",
            sa.Integer(),
            sa.ForeignKey("clubs.club_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_by_uid", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_conversations_type", "conversations", ["type"]
    )
    op.create_index(
        "ix_conversations_college_id", "conversations", ["college_id"]
    )
    op.create_index(
        "ix_conversations_club_id", "conversations", ["club_id"]
    )
    op.create_index(
        "ix_conversations_created_by_uid",
        "conversations",
        ["created_by_uid"],
    )

    # 2. Create conversation_members table
    op.create_table(
        "conversation_members",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "conversation_id",
            sa.Integer(),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("firebase_uid", sa.String(128), nullable=False),
        sa.Column(
            "role",
            sa.String(20),
            server_default="member",
            nullable=False,
        ),
        sa.Column("last_read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "conversation_id",
            "firebase_uid",
            name="uq_conversation_member",
        ),
    )
    op.create_index(
        "ix_conversation_members_conversation_id",
        "conversation_members",
        ["conversation_id"],
    )
    op.create_index(
        "ix_conversation_members_firebase_uid",
        "conversation_members",
        ["firebase_uid"],
    )

    # 3. Create messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "conversation_id",
            sa.Integer(),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sender_uid", sa.String(128), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "message_type",
            sa.String(20),
            server_default="text",
            nullable=False,
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_messages_conversation_id", "messages", ["conversation_id"]
    )
    op.create_index(
        "ix_messages_sender_uid", "messages", ["sender_uid"]
    )
    op.create_index(
        "ix_messages_created_at", "messages", ["created_at"]
    )


def downgrade() -> None:
    op.drop_table("messages")
    op.drop_table("conversation_members")
    op.drop_table("conversations")
