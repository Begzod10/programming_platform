"""add game_session_snapshots table

Revision ID: ee66aa11bb22
Revises: dd44ee55ff66
Create Date: 2026-07-17

Immutable per-session summary written once when a teacher clicks
Завершить. Payload is the full snapshot (leaderboard, questions with
per-option counts, per-student per-question breakdown) so the summary
view, CSV export, and parent bot notification all read from one row.
"""
from alembic import op
import sqlalchemy as sa

revision = 'ee66aa11bb22'
# Chained onto cc1122334455 (the current alembic_version on prod) rather
# than dd44ee55ff66 (which only exists locally — the options_ru column
# it adds is already present on prod, so skipping it is a functional
# no-op). This keeps the migration linear against the DB's actual state.
down_revision = 'cc1122334455'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'game_session_snapshots',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column(
            'completed_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column('completed_by', sa.Integer(), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ['session_id'], ['game_sessions.id'], ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['completed_by'], ['students.id'], ondelete='SET NULL',
        ),
        sa.UniqueConstraint('session_id', name='uq_game_session_snapshot_session'),
    )
    op.create_index(
        'ix_game_session_snapshots_completed_at',
        'game_session_snapshots',
        ['completed_at'],
    )


def downgrade():
    op.drop_index('ix_game_session_snapshots_completed_at', table_name='game_session_snapshots')
    op.drop_table('game_session_snapshots')
