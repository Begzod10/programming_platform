"""add unique constraint to student_question_orders

Revision ID: ee11ff22aa33
Revises: dd44ee55ff66
Create Date: 2026-08-01

"""
from alembic import op

revision = 'ee11ff22aa33'
down_revision = 'dd44ee55ff66'
branch_labels = None
depends_on = None


def upgrade():
    # Two concurrent requests from the same student (double-click, retry after
    # a slow response) could both see "no row yet" and both insert one before
    # this constraint existed, so de-dupe first — keep the lowest id per
    # (session_id, student_id) and drop the rest.
    op.execute("""
        DELETE FROM student_question_orders a
        USING student_question_orders b
        WHERE a.session_id = b.session_id
          AND a.student_id = b.student_id
          AND a.id > b.id
    """)
    op.create_unique_constraint(
        'uq_student_question_order',
        'student_question_orders',
        ['session_id', 'student_id'],
    )


def downgrade():
    op.drop_constraint('uq_student_question_order', 'student_question_orders', type_='unique')
