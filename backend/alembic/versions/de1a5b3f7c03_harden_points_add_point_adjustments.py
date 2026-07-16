"""harden points: create point_adjustments audit ledger

Revision ID: de1a5b3f7c03
Revises: de1a5b3f7c02
Create Date: 2026-07-16

Adds the audit ledger table that /rankings/add-points and
/rankings/subtract-points now write to. Existing pre-ledger adjustments
are NOT backfilled — they'll show as drift in the recalc script, which is
the desired behavior (a human can classify them and decide whether to
insert a compensating row).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'de1a5b3f7c03'
down_revision: Union[str, None] = 'de1a5b3f7c02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'point_adjustments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('delta', sa.Integer(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('reason', sa.String(length=500), nullable=False),
        sa.Column('related_entity_type', sa.String(length=64), nullable=True),
        sa.Column('related_entity_id', sa.Integer(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['actor_id'], ['students.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_point_adjustments_student_id',
        'point_adjustments',
        ['student_id'],
    )


def downgrade() -> None:
    op.drop_index('ix_point_adjustments_student_id', table_name='point_adjustments')
    op.drop_table('point_adjustments')
