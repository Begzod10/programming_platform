"""add preview_image_url to lesson_files

Revision ID: aab1234567890
Revises: aa11223344bb
Create Date: 2026-06-19

"""
from alembic import op
import sqlalchemy as sa

revision = 'aab1234567890'
down_revision = 'aa11223344bb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('lesson_files',
        sa.Column('preview_image_url', sa.String(500), nullable=True)
    )


def downgrade():
    op.drop_column('lesson_files', 'preview_image_url')
