"""add project_likes table for per-student like dedup

Revision ID: cc44dd55ee66
Revises: bb44cc55dd66
Create Date: 2026-09-11

`Project.likes_count` used to be a bare counter bumped on every POST
/like with no per-student dedup at all (only self-likes were blocked) —
the same other student could like a project unlimited times and inflate
the count. This table is the real dedup mechanism: a unique constraint
on (student_id, project_id) makes a repeat like a clean no-op at the DB
level. `likes_count` stays on `projects` as a denormalized counter, kept
in sync by the service layer (recomputed from this table on every
like/unlike — see app/services/project_service.py).

Chained onto bb44cc55dd66, the most recently added file still tracked in
backend/alembic/versions/ (versions/ is gitignored going forward per
932e9d6 — see PROJECT_KNOWLEDGE.md §3.1 for why the older links in this
chain are broken/unresolvable and must not be trusted blindly).
"""
from alembic import op
import sqlalchemy as sa

revision = 'cc44dd55ee66'
down_revision = 'bb44cc55dd66'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'project_likes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ['student_id'], ['students.id'], ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['project_id'], ['projects.id'], ondelete='CASCADE',
        ),
        sa.UniqueConstraint(
            'student_id', 'project_id', name='uq_project_like_student_project',
        ),
    )
    op.create_index(
        'ix_project_likes_project_id', 'project_likes', ['project_id'],
    )


def downgrade():
    op.drop_index('ix_project_likes_project_id', table_name='project_likes')
    op.drop_table('project_likes')
