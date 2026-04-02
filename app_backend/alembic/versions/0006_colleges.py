"""colleges and college_admins tables, college_id FKs

Revision ID: 0006_colleges
Revises: 0005_club_account_manager
Create Date: 2026-03-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_colleges"
down_revision: str | None = "0005_club_account_manager"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create colleges table
    op.create_table(
        "colleges",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(200), nullable=False, unique=True),
        sa.Column("college_code", sa.String(50), nullable=False, unique=True),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 2-3. Indexes on colleges
    op.create_index("ix_colleges_name", "colleges", ["name"])
    op.create_index("ix_colleges_college_code", "colleges", ["college_code"])

    # 4. Create college_admins table
    op.create_table(
        "college_admins",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "college_id",
            sa.Integer(),
            sa.ForeignKey("colleges.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("firebase_uid", sa.String(128), nullable=False),
        sa.Column("added_by_uid", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "college_id", "firebase_uid", name="uq_college_admin"
        ),
    )

    # 5-6. Indexes on college_admins
    op.create_index(
        "ix_college_admins_college_id", "college_admins", ["college_id"]
    )
    op.create_index(
        "ix_college_admins_firebase_uid", "college_admins", ["firebase_uid"]
    )

    # 7. Add college_id to profiles
    op.add_column(
        "profiles",
        sa.Column(
            "college_id",
            sa.Integer(),
            sa.ForeignKey("colleges.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_profiles_college_id", "profiles", ["college_id"])

    # 8. Add college_id to clubs
    op.add_column(
        "clubs",
        sa.Column(
            "college_id",
            sa.Integer(),
            sa.ForeignKey("colleges.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_clubs_college_id", "clubs", ["college_id"])

    # 9. Add college_id to events
    op.add_column(
        "events",
        sa.Column(
            "college_id",
            sa.Integer(),
            sa.ForeignKey("colleges.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_events_college_id", "events", ["college_id"])

    # 10. Seed NIT Agartala
    op.execute("""
        INSERT INTO colleges
            (name, college_code, city, state, is_active, created_at)
        VALUES
            ('NIT Agartala', 'NITA', 'Agartala', 'Tripura', true, NOW())
    """)


def downgrade() -> None:
    op.drop_index("ix_events_college_id", table_name="events")
    op.drop_column("events", "college_id")

    op.drop_index("ix_clubs_college_id", table_name="clubs")
    op.drop_column("clubs", "college_id")

    op.drop_index("ix_profiles_college_id", table_name="profiles")
    op.drop_column("profiles", "college_id")

    op.drop_table("college_admins")
    op.drop_table("colleges")
