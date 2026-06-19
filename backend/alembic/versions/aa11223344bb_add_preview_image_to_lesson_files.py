"""add preview_image_url to lesson_files

Revision ID: aa11223344bb
Revises: ff2233445566
Create Date: 2026-06-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'aa11223344bb'
down_revision: Union[str, None] = 'aa1122334455'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('lesson_files', sa.Column('preview_image_url', sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column('lesson_files', 'preview_image_url')
