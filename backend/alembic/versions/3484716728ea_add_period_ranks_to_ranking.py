"""add period ranks to ranking

Revision ID: 3484716728ea
Revises: 3210e760c2fb
Create Date: 2026-04-07 14:52:16.646979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3484716728ea'
down_revision: Union[str, None] = '3210e760c2fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Ustunlarni nullable=True (bo'sh qolishi mumkin) qilib qo'shamiz
    op.add_column('rankings', sa.Column('daily_rank', sa.Integer(), nullable=True))
    op.add_column('rankings', sa.Column('weekly_rank', sa.Integer(), nullable=True))
    op.add_column('rankings', sa.Column('monthly_rank', sa.Integer(), nullable=True))

    # 2. Mavjud qatorlardagi NULL qiymatlarni 0 bilan to'ldiramiz
    op.execute("UPDATE rankings SET daily_rank = 0, weekly_rank = 0, monthly_rank = 0")

    # 3. Endi ustunlarni NOT NULL holatiga o'tkazamiz
    op.alter_column('rankings', 'daily_rank', nullable=False)
    op.alter_column('rankings', 'weekly_rank', nullable=False)
    op.alter_column('rankings', 'monthly_rank', nullable=False)


def downgrade() -> None:
    op.drop_column('rankings', 'monthly_rank')
    op.drop_column('rankings', 'weekly_rank')
    op.drop_column('rankings', 'daily_rank')