"""postgres hardening: timezone-aware datetimes and performance indexes

Revision ID: 0002_hardening
Revises: 0001_initial
Create Date: 2026-03-25
"""
from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "0002_hardening"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Timezone-aware DateTime columns ──────────────────────────
    # Generate one op.alter_column per DateTime column found in entities.py
    # Use this exact format for each:
    #
    # op.alter_column(
    #     'table_name', 'column_name',
    #     existing_type=sa.DateTime(),
    #     type_=sa.DateTime(timezone=True),
    #     existing_nullable=True,  # match entity definition
    #     postgresql_using='column_name AT TIME ZONE \'UTC\''
    # )
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "users",
        "updated_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "clubs",
        "created_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "clubs",
        "updated_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "positions",
        "created_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "positions",
        "updated_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "events",
        "starts_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="starts_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "events",
        "created_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "profiles",
        "created_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "profiles",
        "updated_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
    )

    # ── Performance indexes ───────────────────────────────────────
    op.create_index('ix_events_starts_at', 'events', ['starts_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_events_starts_at', table_name='events')

    # Revert DateTime columns back to timezone-naive
    # Generate one op.alter_column per DateTime column, reversing the upgrade
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "users",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "clubs",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "clubs",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "positions",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "positions",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "events",
        "starts_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="starts_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "events",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "profiles",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "profiles",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
    )
