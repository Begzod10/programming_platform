"""add lesson_samples table

Revision ID: aa11bb22cc33
Revises: ff2233445566
Create Date: 2026-06-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'aa11bb22cc33'
down_revision: Union[str, None] = 'b4005434acba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'lesson_samples',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sample_type', sa.String(32), nullable=False, server_default='web'),
        sa.Column('html_code', sa.Text(), nullable=True),
        sa.Column('css_code', sa.Text(), nullable=True),
        sa.Column('js_code', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('lesson_id', name='uq_lesson_samples_lesson_id'),
    )


def downgrade() -> None:
    op.drop_table('lesson_samples')
