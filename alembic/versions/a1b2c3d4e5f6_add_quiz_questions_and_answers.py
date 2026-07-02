"""add quiz questions and answers tables

Revision ID: a1b2c3d4e5f6
Revises: f3cbc27d9853
Create Date: 2026-07-02 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f3cbc27d9853'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add current_question_id to game_sessions
    op.add_column('game_sessions', sa.Column('current_question_id', sa.Integer(), nullable=True))

    # Create question status enum
    question_status = postgresql.ENUM('pending', 'active', 'revealed', name='questionstatus')
    question_status.create(op.get_bind(), checkfirst=True)

    # Create game_questions table
    op.create_table(
        'game_questions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('game_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('options', postgresql.JSON(), nullable=False),
        sa.Column('correct_option', sa.Integer(), nullable=False),
        sa.Column('time_limit', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('points', sa.Integer(), nullable=False, server_default='1000'),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.Enum('pending', 'active', 'revealed', name='questionstatus'), nullable=False, server_default='pending'),
        sa.Column('activated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_game_questions_session_id', 'game_questions', ['session_id'])

    # Create game_answers table
    op.create_table(
        'game_answers',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('question_id', sa.Integer(), sa.ForeignKey('game_questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('student_id', sa.Integer(), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
        sa.Column('team_id', sa.Integer(), sa.ForeignKey('game_teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chosen_option', sa.Integer(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('points_earned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('answered_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('question_id', 'student_id', name='uq_game_answer'),
    )
    op.create_index('ix_game_answers_question_id', 'game_answers', ['question_id'])


def downgrade() -> None:
    op.drop_table('game_answers')
    op.drop_table('game_questions')
    op.drop_column('game_sessions', 'current_question_id')
    op.execute("DROP TYPE IF EXISTS questionstatus")
