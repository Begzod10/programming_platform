"""setup_course_enrollments

Revision ID: b62001aee2a6
Revises: 995a9c4bf89b
Create Date: 2026-03-19 13:48:24.835144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b62001aee2a6'
down_revision: Union[str, None] = '995a9c4bf89b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # course_enrollments jadvalini yaratish
    op.create_table(
        'course_enrollments',
        sa.Column('student_id', sa.Integer(), sa.ForeignKey('students.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('course_id', sa.Integer(), sa.ForeignKey('courses.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('progress_percent', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('is_completed', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('enrolled_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )

def downgrade() -> None:
    op.drop_table('course_enrollments')
