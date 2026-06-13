"""add lesson_feedback table

Revision ID: a7b3c8d12f01
Revises: 25711768993a
Create Date: 2026-06-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7b3c8d12f01"
down_revision: Union[str, None] = "25711768993a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lesson_feedback",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["student_id"], ["students.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"], ["lessons.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint(
            "student_id", "lesson_id", name="uq_lesson_feedback_student_lesson"
        ),
        sa.CheckConstraint(
            "rating BETWEEN 1 AND 5", name="ck_lesson_feedback_rating_range"
        ),
    )
    op.create_index(
        "ix_lesson_feedback_student_id", "lesson_feedback", ["student_id"]
    )
    op.create_index(
        "ix_lesson_feedback_lesson_id", "lesson_feedback", ["lesson_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_lesson_feedback_lesson_id", table_name="lesson_feedback")
    op.drop_index("ix_lesson_feedback_student_id", table_name="lesson_feedback")
    op.drop_table("lesson_feedback")
