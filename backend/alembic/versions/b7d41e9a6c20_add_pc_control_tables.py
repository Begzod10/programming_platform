"""add pc control tables

Revision ID: b7d41e9a6c20
Revises: 52c3bf31cfc4
Create Date: 2026-10-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'b7d41e9a6c20'
down_revision: Union[str, None] = '52c3bf31cfc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'pc_devices',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('hostname', sa.String(255), nullable=False),
        sa.Column('machine_key_hash', sa.String(128), nullable=False, unique=True),
        sa.Column('group_id', sa.Integer(), sa.ForeignKey('groups.id', ondelete='SET NULL'), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_app', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        'pc_allowlists',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('group_id', sa.Integer(), sa.ForeignKey('groups.id', ondelete='CASCADE'), nullable=True, unique=True),
        sa.Column('entries', sa.JSON(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        'pc_sessions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('pc_devices.id', ondelete='CASCADE'), nullable=False),
        sa.Column('student_id', sa.Integer(), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
        sa.Column('signed_in_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('signed_out_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_pc_sessions_device_signed_out', 'pc_sessions', ['device_id', 'signed_out_at'])
    op.create_table(
        'pc_usage_events',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('pc_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('app_name', sa.String(255), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('was_locked', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index('ix_pc_usage_events_session_id', 'pc_usage_events', ['session_id'])
    op.create_table(
        'pc_commands',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('scope_type', sa.String(10), nullable=False),
        sa.Column('scope_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.String(10), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('pc_commands')
    op.drop_index('ix_pc_usage_events_session_id', table_name='pc_usage_events')
    op.drop_table('pc_usage_events')
    op.drop_index('ix_pc_sessions_device_signed_out', table_name='pc_sessions')
    op.drop_table('pc_sessions')
    op.drop_table('pc_allowlists')
    op.drop_table('pc_devices')
