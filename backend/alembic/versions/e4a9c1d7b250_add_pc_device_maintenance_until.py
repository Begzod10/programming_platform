"""add pc_devices.maintenance_until

Revision ID: e4a9c1d7b250
Revises: c5e8a2d71f39
Create Date: 2026-11-04
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'e4a9c1d7b250'
down_revision: Union[str, None] = 'c5e8a2d71f39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pc_devices', sa.Column('maintenance_until', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('pc_devices', 'maintenance_until')
