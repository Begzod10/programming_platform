"""partial unique index on students.gennis_id / students.turon_id

Revision ID: 52c3bf31cfc4
Revises: a3f7c9e1b204
Create Date: 2026-09-14

Documentation/local-dev parity only — this repo's actual deploy path does
not run `alembic upgrade` (see app/db/database.py::_reconcile_indexes,
which is what applies this to prod on every startup). Keeping this file so
`alembic upgrade head` on a fresh local DB still matches prod's real
schema.

Partial (WHERE ... IS NOT NULL) to keep the index smaller — Postgres
already treats NULL as distinct from NULL in a plain unique index, so this
isn't required for correctness on a nullable column, just for index size.

Prompted by a live incident (2026-09-14): two Student rows both had
turon_id=19042 — nothing enforced uniqueness, so a corrupt roster-sync
lookup (`scalar_one_or_none()` on a column that could legitimately have
duplicates) crashed login for every teacher with that student in a group
or flow. See gennis_service.py::_sync_container_student for both the
oldest-row-wins fix for a pre-existing duplicate and the IntegrityError
recovery this constraint's own possible race now needs.
"""
from typing import Sequence, Union

from alembic import op

revision: str = '52c3bf31cfc4'
down_revision: Union[str, None] = 'a3f7c9e1b204'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        'ux_students_turon_id', 'students', ['turon_id'],
        unique=True, postgresql_where='turon_id IS NOT NULL',
    )
    op.create_index(
        'ux_students_gennis_id', 'students', ['gennis_id'],
        unique=True, postgresql_where='gennis_id IS NOT NULL',
    )


def downgrade() -> None:
    op.drop_index('ux_students_gennis_id', table_name='students')
    op.drop_index('ux_students_turon_id', table_name='students')
