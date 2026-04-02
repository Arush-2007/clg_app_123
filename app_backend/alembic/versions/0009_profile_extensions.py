"""profile certificates and work experiences

Revision ID: 0009_profile_extensions
Revises: 0008_feed
Create Date: 2026-03-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009_profile_extensions"
down_revision: str | None = "0008_feed"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create profile_certificates table
    op.create_table(
        "profile_certificates",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("firebase_uid", sa.String(128), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("issued_by", sa.String(200), nullable=True),
        sa.Column("file_url", sa.String(512), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_profile_certificates_firebase_uid",
        "profile_certificates",
        ["firebase_uid"],
    )

    # 2. Create work_experiences table
    op.create_table(
        "work_experiences",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("firebase_uid", sa.String(128), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("company", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "is_current",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_work_experiences_firebase_uid",
        "work_experiences",
        ["firebase_uid"],
    )


def downgrade() -> None:
    op.drop_table("work_experiences")
    op.drop_table("profile_certificates")
