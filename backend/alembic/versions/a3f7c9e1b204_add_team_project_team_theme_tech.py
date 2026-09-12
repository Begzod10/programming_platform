"""add theme/tech_stack/project_title/project_description to team_project_teams

Revision ID: a3f7c9e1b204
Revises: d13ba7f94af9
Create Date: 2026-09-12

Purely additive, all nullable — no backfill needed (table has no rows in
prod at the time of this migration, per Phase 2's own note about deploy
timing). See app/services/team_project_constants.py for the theme/stack
key vocabularies these columns store.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'a3f7c9e1b204'
down_revision: Union[str, None] = 'd13ba7f94af9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('team_project_teams', sa.Column('theme', sa.String(length=100), nullable=True))
    op.add_column('team_project_teams', sa.Column('tech_stack', sa.String(length=100), nullable=True))
    op.add_column('team_project_teams', sa.Column('project_title', sa.String(length=300), nullable=True))
    op.add_column('team_project_teams', sa.Column('project_description', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('team_project_teams', 'project_description')
    op.drop_column('team_project_teams', 'project_title')
    op.drop_column('team_project_teams', 'tech_stack')
    op.drop_column('team_project_teams', 'theme')
