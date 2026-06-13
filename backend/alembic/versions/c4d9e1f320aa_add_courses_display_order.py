"""add courses.display_order

Revision ID: c4d9e1f320aa
Revises: a7b3c8d12f01
Create Date: 2026-06-05 13:30:00.000000

Adds an integer `display_order` column so teachers can drag-and-drop
their courses into a custom order. Lower values appear first; ties
break by id. Backfills every existing row with its current id so the
initial order matches what teachers already see.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4d9e1f320aa"
down_revision: Union[str, None] = "a7b3c8d12f01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "courses",
        sa.Column(
            "display_order",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    # Backfill: seed display_order with id so the initial sort matches
    # what teachers already see in the UI (oldest first or however id
    # happens to lay out — at least it's deterministic).
    op.execute("UPDATE courses SET display_order = id")

    op.create_index(
        "ix_courses_display_order", "courses", ["display_order"]
    )


def downgrade() -> None:
    op.drop_index("ix_courses_display_order", table_name="courses")
    op.drop_column("courses", "display_order")
