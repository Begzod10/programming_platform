"""add bug-hunt kind to game_questions

Revision ID: ff33aa44bb55
Revises: ee11ff22aa33
Create Date: 2026-08-01

"""
from alembic import op
import sqlalchemy as sa

revision = 'ff33aa44bb55'
down_revision = 'ee11ff22aa33'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('game_questions', sa.Column(
        'question_kind', sa.String(20), nullable=False, server_default='quiz'
    ))
    op.add_column('game_questions', sa.Column('code_snippet', sa.Text(), nullable=True))
    op.add_column('game_questions', sa.Column('code_language', sa.String(20), nullable=True))
    op.add_column('game_questions', sa.Column('bug_line', sa.Integer(), nullable=True))
    op.add_column('game_questions', sa.Column('bug_explanation', sa.Text(), nullable=True))
    op.add_column('game_questions', sa.Column('bug_explanation_ru', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('game_questions', 'bug_explanation_ru')
    op.drop_column('game_questions', 'bug_explanation')
    op.drop_column('game_questions', 'bug_line')
    op.drop_column('game_questions', 'code_language')
    op.drop_column('game_questions', 'code_snippet')
    op.drop_column('game_questions', 'question_kind')
