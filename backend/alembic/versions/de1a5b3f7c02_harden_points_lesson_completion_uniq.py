"""harden points: enforce unique lesson_completions (student_id, lesson_id)

Revision ID: de1a5b3f7c02
Revises: de1a5b3f7c01
Create Date: 2026-07-16

The model already declared UniqueConstraint("student_id", "lesson_id",
name="uq_student_lesson_completion") but the DB may be missing it (or missing
its migration). This migration dedupes any historical duplicates (keeps the
earliest LessonCompletion per (student, lesson), deletes the rest) and then
creates the constraint if it isn't already there.

The dedupe is safe because a duplicate lesson_completion row could ONLY have
been created via the old race window in the exercise-auto-complete path.
Any lesson-reward points were awarded per-insert, so removing the duplicate
row means the extra reward is drift the recalc script will surface.
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'de1a5b3f7c02'
down_revision: Union[str, None] = 'de1a5b3f7c01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: dedupe. Keep the earliest completed_at per (student, lesson).
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                ROW_NUMBER() OVER (
                    PARTITION BY student_id, lesson_id
                    ORDER BY completed_at ASC, id ASC
                ) AS rn
            FROM lesson_completions
        )
        DELETE FROM lesson_completions
        WHERE id IN (SELECT id FROM ranked WHERE rn > 1);
        """
    )

    # Step 2: create the constraint if it doesn't already exist. Postgres
    # supports IF NOT EXISTS for unique constraints only via a wrapping DO
    # block; SQLite/other dialects don't run this migration in practice.
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_student_lesson_completion'
            ) THEN
                ALTER TABLE lesson_completions
                ADD CONSTRAINT uq_student_lesson_completion
                UNIQUE (student_id, lesson_id);
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    op.drop_constraint(
        'uq_student_lesson_completion',
        'lesson_completions',
        type_='unique',
    )
