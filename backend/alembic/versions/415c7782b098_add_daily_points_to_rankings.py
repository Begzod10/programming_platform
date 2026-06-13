"""Add daily points to rankings

Revision ID: 415c7782b098
Revises: 098fc3fa77cc
Create Date: ...
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '415c7782b098'
down_revision: Union[str, None] = '098fc3fa77cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ✅ Avval nullable qilib qo'shamiz
    op.add_column('rankings', sa.Column('daily_points', sa.Integer(), nullable=True))
    op.add_column('rankings', sa.Column('last_daily_reset', sa.DateTime(), nullable=True))
    op.add_column('rankings', sa.Column('last_weekly_reset', sa.DateTime(), nullable=True))
    op.add_column('rankings', sa.Column('last_monthly_reset', sa.DateTime(), nullable=True))

    # Timestamp type'larini yangilash
    op.alter_column('rankings', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)

    op.alter_column('rankings', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)

    # ✅ Mavjud qatorlarni yangilash
    op.execute("UPDATE rankings SET daily_points = 0 WHERE daily_points IS NULL")
    op.execute("UPDATE rankings SET last_daily_reset = NOW() WHERE last_daily_reset IS NULL")
    op.execute("UPDATE rankings SET last_weekly_reset = NOW() WHERE last_weekly_reset IS NULL")
    op.execute("UPDATE rankings SET last_monthly_reset = NOW() WHERE last_monthly_reset IS NULL")

    # ✅ Keyin NOT NULL qilamiz
    op.alter_column('rankings', 'daily_points', nullable=False)
    op.alter_column('rankings', 'last_daily_reset', nullable=False)
    op.alter_column('rankings', 'last_weekly_reset', nullable=False)
    op.alter_column('rankings', 'last_monthly_reset', nullable=False)


def downgrade() -> None:
    op.alter_column('rankings', 'updated_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)

    op.alter_column('rankings', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)

    op.drop_column('rankings', 'last_monthly_reset')
    op.drop_column('rankings', 'last_weekly_reset')
    op.drop_column('rankings', 'last_daily_reset')
    op.drop_column('rankings', 'daily_points')