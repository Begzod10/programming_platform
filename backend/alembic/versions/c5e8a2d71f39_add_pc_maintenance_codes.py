"""add pc maintenance codes

Revision ID: c5e8a2d71f39
Revises: b7d41e9a6c20
Create Date: 2026-11-04
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'c5e8a2d71f39'
down_revision: Union[str, None] = 'b7d41e9a6c20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'pc_maintenance_codes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('pc_devices.id', ondelete='CASCADE'), nullable=False),
        sa.Column('code_hash', sa.String(64), nullable=False),
        sa.Column('salt', sa.String(64), nullable=False),
        sa.Column('minutes', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_attempts', sa.Integer(), nullable=False, server_default='0'),
    )
    op.create_index('ix_pc_maintenance_codes_device_created', 'pc_maintenance_codes',
                    ['device_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('ix_pc_maintenance_codes_device_created', table_name='pc_maintenance_codes')
    op.drop_table('pc_maintenance_codes')
