"""feed items, likes, reports, event extensions and registrations

Revision ID: 0008_feed
Revises: 0007_connections_tags
Create Date: 2026-03-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008_feed"
down_revision: str | None = "0007_connections_tags"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create feed_items table
    op.create_table(
        "feed_items",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("creator_uid", sa.String(128), nullable=False),
        sa.Column("creator_type", sa.String(20), nullable=False),
        sa.Column("content_type", sa.String(20), nullable=False),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("media_url", sa.String(512), nullable=True),
        sa.Column("media_type", sa.String(20), nullable=True),
        sa.Column(
            "college_id",
            sa.Integer(),
            sa.ForeignKey("colleges.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "likes_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "comments_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "is_flagged",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_feed_items_creator_uid", "feed_items", ["creator_uid"]
    )
    op.create_index(
        "ix_feed_items_creator_type", "feed_items", ["creator_type"]
    )
    op.create_index(
        "ix_feed_items_content_type", "feed_items", ["content_type"]
    )
    op.create_index(
        "ix_feed_items_college_id", "feed_items", ["college_id"]
    )
    op.create_index(
        "ix_feed_items_created_at", "feed_items", ["created_at"]
    )
    op.create_index(
        "ix_feed_items_is_flagged", "feed_items", ["is_flagged"]
    )

    # 2. Create feed_likes table
    op.create_table(
        "feed_likes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "feed_item_id",
            sa.Integer(),
            sa.ForeignKey("feed_items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("firebase_uid", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "feed_item_id", "firebase_uid", name="uq_feed_like"
        ),
    )
    op.create_index(
        "ix_feed_likes_feed_item_id", "feed_likes", ["feed_item_id"]
    )
    op.create_index(
        "ix_feed_likes_firebase_uid", "feed_likes", ["firebase_uid"]
    )

    # 3. Create feed_reports table
    op.create_table(
        "feed_reports",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "feed_item_id",
            sa.Integer(),
            sa.ForeignKey("feed_items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("reported_by_uid", sa.String(128), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_feed_reports_feed_item_id", "feed_reports", ["feed_item_id"]
    )
    op.create_index(
        "ix_feed_reports_reported_by_uid",
        "feed_reports",
        ["reported_by_uid"],
    )

    # 4. Extend events table
    op.add_column(
        "events",
        sa.Column("creator_uid", sa.String(128), nullable=True),
    )
    op.create_index("ix_events_creator_uid", "events", ["creator_uid"])
    op.add_column(
        "events",
        sa.Column(
            "event_type",
            sa.String(20),
            server_default="offline",
            nullable=True,
        ),
    )
    op.add_column(
        "events",
        sa.Column("registration_url", sa.String(512), nullable=True),
    )
    op.add_column(
        "events",
        sa.Column("max_registrations", sa.Integer(), nullable=True),
    )

    # 5. Create event_registrations table
    op.create_table(
        "event_registrations",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "event_id",
            sa.Integer(),
            sa.ForeignKey("events.event_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("firebase_uid", sa.String(128), nullable=False),
        sa.Column(
            "registered_at", sa.DateTime(timezone=True), nullable=False
        ),
        sa.UniqueConstraint(
            "event_id", "firebase_uid", name="uq_event_registration"
        ),
    )
    op.create_index(
        "ix_event_registrations_event_id",
        "event_registrations",
        ["event_id"],
    )
    op.create_index(
        "ix_event_registrations_firebase_uid",
        "event_registrations",
        ["firebase_uid"],
    )


def downgrade() -> None:
    op.drop_table("event_registrations")

    op.drop_column("events", "max_registrations")
    op.drop_column("events", "registration_url")
    op.drop_column("events", "event_type")
    op.drop_index("ix_events_creator_uid", table_name="events")
    op.drop_column("events", "creator_uid")

    op.drop_table("feed_reports")
    op.drop_table("feed_likes")
    op.drop_table("feed_items")
