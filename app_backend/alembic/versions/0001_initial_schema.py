"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-03-22
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("firebase_uid", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False, server_default="email-password"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_firebase_uid", "users", ["firebase_uid"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "clubs",
        sa.Column("club_id", sa.Integer(), primary_key=True),
        sa.Column("parent_college", sa.String(length=120), nullable=False),
        sa.Column("club_name", sa.String(length=120), nullable=False),
        sa.Column("club_admin", sa.String(length=120), nullable=False),
        sa.Column("club_admin_email", sa.String(length=320), nullable=False),
        sa.Column("members", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("c_id", sa.String(length=256), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("parent_college", "club_name", name="uq_college_club"),
    )
    op.create_index("ix_clubs_club_id", "clubs", ["club_id"], unique=False)
    op.create_index("ix_clubs_parent_college", "clubs", ["parent_college"], unique=False)
    op.create_index("ix_clubs_club_name", "clubs", ["club_name"], unique=False)
    op.create_index("ix_clubs_c_id", "clubs", ["c_id"], unique=True)

    op.create_table(
        "events",
        sa.Column("event_id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("image_url", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_events_event_id", "events", ["event_id"], unique=False)
    op.create_index("ix_events_title", "events", ["title"], unique=False)
    op.create_index("ix_events_status", "events", ["status"], unique=False)

    op.create_table(
        "profiles",
        sa.Column("profile_id", sa.Integer(), primary_key=True),
        sa.Column("firebase_uid", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("college", sa.String(length=120), nullable=False),
        sa.Column("year_of_graduation", sa.String(length=10), nullable=False),
        sa.Column("branch", sa.String(length=120), nullable=False),
        sa.Column("avatar_url", sa.String(length=512), nullable=False),
        sa.Column("latitude", sa.String(length=64), nullable=False, server_default="Not specified"),
        sa.Column("longitude", sa.String(length=64), nullable=False, server_default="Not specified"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_profiles_profile_id", "profiles", ["profile_id"], unique=False)
    op.create_index("ix_profiles_firebase_uid", "profiles", ["firebase_uid"], unique=True)

    op.create_table(
        "positions",
        sa.Column("position_id", sa.Integer(), primary_key=True),
        sa.Column("c_id", sa.String(length=256), nullable=False),
        sa.Column("hierarchy", sa.Integer(), nullable=False),
        sa.Column("hierarchy_holders", sa.Integer(), nullable=False),
        sa.Column("position_name", sa.String(length=120), nullable=False, server_default="Member"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["c_id"], ["clubs.c_id"], ondelete="CASCADE"),
        sa.UniqueConstraint("c_id", "hierarchy", name="uq_club_hierarchy"),
    )
    op.create_index("ix_positions_position_id", "positions", ["position_id"], unique=False)
    op.create_index("ix_positions_c_id", "positions", ["c_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_positions_c_id", table_name="positions")
    op.drop_index("ix_positions_position_id", table_name="positions")
    op.drop_table("positions")

    op.drop_index("ix_profiles_firebase_uid", table_name="profiles")
    op.drop_index("ix_profiles_profile_id", table_name="profiles")
    op.drop_table("profiles")

    op.drop_index("ix_events_status", table_name="events")
    op.drop_index("ix_events_title", table_name="events")
    op.drop_index("ix_events_event_id", table_name="events")
    op.drop_table("events")

    op.drop_index("ix_clubs_c_id", table_name="clubs")
    op.drop_index("ix_clubs_club_name", table_name="clubs")
    op.drop_index("ix_clubs_parent_college", table_name="clubs")
    op.drop_index("ix_clubs_club_id", table_name="clubs")
    op.drop_table("clubs")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_firebase_uid", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
