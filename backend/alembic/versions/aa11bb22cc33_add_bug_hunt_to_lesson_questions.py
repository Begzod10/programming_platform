"""add bug-hunt kind to lesson_questions, make quiz fields nullable

Revision ID: aa11bb22cc33
Revises: ff33aa44bb55
Create Date: 2026-08-02

"""
from alembic import op
import sqlalchemy as sa

revision = 'aa11bb22cc33'
down_revision = 'ff33aa44bb55'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('lesson_questions', 'options', existing_type=sa.JSON(), nullable=True)
    op.alter_column('lesson_questions', 'correct_option', existing_type=sa.Integer(), nullable=True)
    op.add_column('lesson_questions', sa.Column(
        'question_kind', sa.String(20), nullable=False, server_default='quiz'
    ))
    op.add_column('lesson_questions', sa.Column('code_snippet', sa.Text(), nullable=True))
    op.add_column('lesson_questions', sa.Column('code_language', sa.String(20), nullable=True))
    op.add_column('lesson_questions', sa.Column('bug_line', sa.Integer(), nullable=True))
    op.add_column('lesson_questions', sa.Column('distractor_lines', sa.JSON(), nullable=True))
    op.add_column('lesson_questions', sa.Column('bug_explanation', sa.Text(), nullable=True))
    op.add_column('lesson_questions', sa.Column('bug_explanation_ru', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('lesson_questions', 'bug_explanation_ru')
    op.drop_column('lesson_questions', 'bug_explanation')
    op.drop_column('lesson_questions', 'distractor_lines')
    op.drop_column('lesson_questions', 'bug_line')
    op.drop_column('lesson_questions', 'code_language')
    op.drop_column('lesson_questions', 'code_snippet')
    op.drop_column('lesson_questions', 'question_kind')
    op.alter_column('lesson_questions', 'correct_option', existing_type=sa.Integer(), nullable=False)
    op.alter_column('lesson_questions', 'options', existing_type=sa.JSON(), nullable=False)
