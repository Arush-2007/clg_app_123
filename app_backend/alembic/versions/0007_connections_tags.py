"""profile extensions, follows, connections, tags, user_tags

Revision ID: 0007_connections_tags
Revises: 0006_colleges
Create Date: 2026-03-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_connections_tags"
down_revision: str | None = "0006_colleges"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Add new columns to profiles
    op.add_column("profiles", sa.Column("bio", sa.Text(), nullable=True))
    op.add_column("profiles", sa.Column("skills", sa.Text(), nullable=True))
    op.add_column(
        "profiles", sa.Column("social_links", sa.Text(), nullable=True)
    )
    op.add_column(
        "profiles",
        sa.Column(
            "is_premium",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.add_column(
        "profiles",
        sa.Column(
            "is_alumni",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )

    # 2. Create follows table
    op.create_table(
        "follows",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("follower_uid", sa.String(128), nullable=False),
        sa.Column("followee_id", sa.Integer(), nullable=False),
        sa.Column("followee_type", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "follower_uid",
            "followee_id",
            "followee_type",
            name="uq_follow",
        ),
    )
    op.create_index("ix_follows_follower_uid", "follows", ["follower_uid"])
    op.create_index("ix_follows_followee_id", "follows", ["followee_id"])
    op.create_index(
        "ix_follows_followee_type", "follows", ["followee_type"]
    )

    # 3. Create connections table
    op.create_table(
        "connections",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("requester_uid", sa.String(128), nullable=False),
        sa.Column("receiver_uid", sa.String(128), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "requester_uid", "receiver_uid", name="uq_connection"
        ),
    )
    op.create_index(
        "ix_connections_requester_uid", "connections", ["requester_uid"]
    )
    op.create_index(
        "ix_connections_receiver_uid", "connections", ["receiver_uid"]
    )
    op.create_index("ix_connections_status", "connections", ["status"])

    # 4. Create tags table
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("tag_type", sa.String(50), nullable=False),
        sa.Column(
            "college_id",
            sa.Integer(),
            sa.ForeignKey("colleges.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tags_name", "tags", ["name"])
    op.create_index("ix_tags_tag_type", "tags", ["tag_type"])
    op.create_index("ix_tags_college_id", "tags", ["college_id"])

    # 5. Create user_tags table
    op.create_table(
        "user_tags",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("firebase_uid", sa.String(128), nullable=False),
        sa.Column(
            "tag_id",
            sa.Integer(),
            sa.ForeignKey("tags.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("granted_by_uid", sa.String(128), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("firebase_uid", "tag_id", name="uq_user_tag"),
    )
    op.create_index(
        "ix_user_tags_firebase_uid", "user_tags", ["firebase_uid"]
    )
    op.create_index("ix_user_tags_tag_id", "user_tags", ["tag_id"])


def downgrade() -> None:
    op.drop_table("user_tags")
    op.drop_table("tags")
    op.drop_table("connections")
    op.drop_table("follows")

    op.drop_column("profiles", "is_alumni")
    op.drop_column("profiles", "is_premium")
    op.drop_column("profiles", "social_links")
    op.drop_column("profiles", "skills")
    op.drop_column("profiles", "bio")
