"""club registration: status, members, accounts tables

Revision ID: 0003_club_registration
Revises: 0002_hardening
Create Date: 2026-03-29
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_club_registration"
down_revision: str | None = "0002_hardening"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add new columns to clubs table
    op.add_column("clubs", sa.Column("status", sa.String(20),
        server_default="pending", nullable=False))
    op.add_column("clubs", sa.Column("document_url",
        sa.String(512), nullable=True))
    op.add_column("clubs", sa.Column("rejection_reason",
        sa.Text(), nullable=True))
    op.add_column("clubs", sa.Column("verified_at",
        sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_clubs_status", "clubs", ["status"])

    # Create club_members table
    op.create_table(
        "club_members",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "club_id",
            sa.Integer(),
            sa.ForeignKey("clubs.club_id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("firebase_uid", sa.String(128), nullable=False, index=True),
        sa.Column(
            "position_name",
            sa.String(120),
            server_default="Member",
            nullable=False,
        ),
        sa.Column("hierarchy", sa.Integer(), server_default="99", nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("club_id", "firebase_uid", name="uq_club_member"),
    )

    # Create club_accounts table
    op.create_table(
        "club_accounts",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "club_id",
            sa.Integer(),
            sa.ForeignKey("clubs.club_id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("managed_by_uid", sa.String(128), nullable=False, index=True),
        sa.Column("club_avatar_url", sa.String(512), nullable=True),
        sa.Column("club_bio", sa.Text(), nullable=True),
        sa.Column(
            "is_verified",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("club_accounts")
    op.drop_table("club_members")
    op.drop_index("ix_clubs_status", table_name="clubs")
    op.drop_column("clubs", "verified_at")
    op.drop_column("clubs", "rejection_reason")
    op.drop_column("clubs", "document_url")
    op.drop_column("clubs", "status")
