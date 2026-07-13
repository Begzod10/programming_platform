"""add auto_mode and student_question_orders

Revision ID: cc1122334455
Revises: ff2233445566
Create Date: 2026-07-13

"""
from alembic import op
import sqlalchemy as sa

revision = 'cc1122334455'
down_revision = 'ff2233445566'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('game_sessions', sa.Column('auto_mode', sa.Boolean(), nullable=False, server_default='false'))

    op.create_table(
        'student_question_orders',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('question_ids', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id', 'student_id', name='uq_student_question_order'),
    )
    op.create_index('ix_student_question_orders_session_student', 'student_question_orders', ['session_id', 'student_id'])


def downgrade():
    op.drop_index('ix_student_question_orders_session_student', table_name='student_question_orders')
    op.drop_table('student_question_orders')
    op.drop_column('game_sessions', 'auto_mode')
