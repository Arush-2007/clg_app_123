"""admins table

Revision ID: 0004_admins
Revises: 0003_club_registration
Create Date: 2026-03-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_admins"
down_revision: str | None = "0003_club_registration"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "firebase_uid",
            sa.String(128),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("added_by_uid", sa.String(128), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("admins")
