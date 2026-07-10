"""widen phone column to 50

Revision ID: aa11bb22cc33
Revises: aabb11223344
Create Date: 2026-07-10

Phone numbers coming from the Gennis API can exceed the old 20-char limit,
causing a StringDataRightTruncationError on login.
"""
from alembic import op
import sqlalchemy as sa

revision = 'ff0011223344'
down_revision = 'aabb11223344'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'students', 'phone',
        existing_type=sa.String(20),
        type_=sa.String(50),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'students', 'phone',
        existing_type=sa.String(50),
        type_=sa.String(20),
        existing_nullable=True,
    )
