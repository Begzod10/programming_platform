"""harden points: partial unique index on exercise_submissions (scoring rows)

Revision ID: de1a5b3f7c01
Revises: cc1122334455
Create Date: 2026-07-16

Adds a partial unique index on `exercise_submissions (student_id, exercise_id)`
scoped to rows where `score > 0`. This turns the app-level "already solved"
guard in exercise_service.submit_exercise into a hard DB invariant: two racing
correct submissions can no longer both award points.

Non-scoring resubmissions (score = 0 or NULL) remain unrestricted so students
can keep practicing.

Pre-existing duplicate scoring rows are deduped BEFORE creating the index —
the earliest scoring row per (student, exercise) is preserved, later ones are
zeroed out (score = 0, is_correct kept as-is). This is safe: the invariant
we're enforcing is "credit at most once", and total_points has already been
credited once for each preserved row; we do NOT reverse points here (the
recalc script in scripts/recalc_points.py will surface the drift so a human
can decide whether to normalize).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'de1a5b3f7c01'
down_revision: Union[str, None] = 'cc1122334455'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: dedupe. Keep the earliest scoring row per (student, exercise),
    # zero out the rest. Works on Postgres (uses a window function via CTE
    # on the UPDATE ... FROM). Alembic runs this as raw SQL.
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                ROW_NUMBER() OVER (
                    PARTITION BY student_id, exercise_id
                    ORDER BY submitted_at ASC, id ASC
                ) AS rn
            FROM exercise_submissions
            WHERE score > 0
        )
        UPDATE exercise_submissions es
        SET score = 0
        FROM ranked r
        WHERE es.id = r.id AND r.rn > 1;
        """
    )

    # Step 2: create the partial unique index.
    op.create_index(
        'uq_exercise_submissions_scoring',
        'exercise_submissions',
        ['student_id', 'exercise_id'],
        unique=True,
        postgresql_where=sa.text('score > 0'),
    )


def downgrade() -> None:
    op.drop_index(
        'uq_exercise_submissions_scoring',
        table_name='exercise_submissions',
    )
    # No data unwind — zeroed-out scores are safer than fabricated duplicates.
