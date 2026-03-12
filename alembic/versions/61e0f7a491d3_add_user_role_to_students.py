"""Add user role to students

Revision ID: 61e0f7a491d3
Revises: 31270fafaa20
Create Date: 2026-03-10 14:41:08.927484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61e0f7a491d3'
down_revision: Union[str, None] = '31270fafaa20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. ENUM type yaratish
    op.execute("CREATE TYPE userrole AS ENUM ('student', 'instructor', 'admin')")

    # 2. Column qo'shish
    op.add_column('students',
                  sa.Column('role',
                            sa.Enum('student', 'instructor', 'admin', name='userrole'),
                            server_default='student',
                            nullable=False))


def downgrade() -> None:
    # 1. Column o'chirish
    op.drop_column('students', 'role')

    # 2. ENUM type o'chirish
    op.execute('DROP TYPE IF EXISTS userrole')