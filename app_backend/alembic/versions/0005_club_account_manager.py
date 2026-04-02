"""clubs: add account_manager_uid column

Revision ID: 0005_club_account_manager
Revises: 0004_admins
Create Date: 2026-03-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_club_account_manager"
down_revision: str | None = "0004_admins"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "clubs",
        sa.Column("account_manager_uid", sa.String(128), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("clubs", "account_manager_uid")
