"""add lesson_questions bank table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-02 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'lesson_questions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('lesson_id', sa.Integer(), sa.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('options', postgresql.JSON(), nullable=False),
        sa.Column('correct_option', sa.Integer(), nullable=False),
        sa.Column('time_limit', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('points', sa.Integer(), nullable=False, server_default='1000'),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_lesson_questions_lesson_id', 'lesson_questions', ['lesson_id'])


def downgrade() -> None:
    op.drop_table('lesson_questions')
