"""add question_text_ru to lesson_questions (bug-hunt prompts were never bilingual)

Revision ID: bb44cc55dd66
Revises: aa11bb22cc33
Create Date: 2026-08-05

bug_hunt lesson_questions already had bug_explanation_ru (the post-answer
reveal text) but question_text_ru never existed at all, unlike quiz kind
which achieves a bilingual prompt by pairing two separate LessonQuestion
rows (one uz, one ru) at import time. Bug-hunt rows are single-row, so the
prompt itself needs its own ru column — see import_questions_from_lesson
in team_game_questions.py for the read side of this fix.
"""
from alembic import op
import sqlalchemy as sa

revision = 'bb44cc55dd66'
down_revision = 'aa11bb22cc33'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('lesson_questions', sa.Column('question_text_ru', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('lesson_questions', 'question_text_ru')
