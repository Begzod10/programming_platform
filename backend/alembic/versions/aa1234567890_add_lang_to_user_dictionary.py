"""add lang to user_dictionary

Revision ID: aa1234567890
Revises: ff2233445566
Create Date: 2026-06-26
"""
from alembic import op
import sqlalchemy as sa

revision = 'aa1234567890'
down_revision = 'ff2233445566'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'user_dictionary',
        sa.Column('lang', sa.String(4), nullable=False, server_default='uz'),
    )


def downgrade():
    op.drop_column('user_dictionary', 'lang')
