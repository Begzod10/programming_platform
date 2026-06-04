"""add_student_groups_table

Revision ID: 49b0f8df8fb9
Revises: 55b0b520983a
Create Date: 2026-05-12 15:09:20.647236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49b0f8df8fb9'
down_revision: Union[str, None] = '55b0b520983a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'student_groups',
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('student_id', 'group_id')
    )

def downgrade():
    op.drop_table('student_groups')