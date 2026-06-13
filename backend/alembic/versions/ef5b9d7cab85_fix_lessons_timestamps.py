"""Fix lessons timestamps

Revision ID: ef5b9d7cab85
Revises: 57588c22097c
Create Date: 2026-03-15 14:19:53.679869

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef5b9d7cab85'
down_revision: Union[str, None] = '57588c22097c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # created_at uchun default qo'yish
    op.execute("""
        ALTER TABLE lessons 
        ALTER COLUMN created_at SET DEFAULT NOW()
    """)

    # updated_at uchun default qo'yish
    op.execute("""
        ALTER TABLE lessons 
        ALTER COLUMN updated_at SET DEFAULT NOW()
    """)

    # Mavjud NULL qiymatlarni yangilash
    op.execute("""
        UPDATE lessons 
        SET created_at = NOW() 
        WHERE created_at IS NULL
    """)

    op.execute("""
        UPDATE lessons 
        SET updated_at = NOW() 
        WHERE updated_at IS NULL
    """)


def downgrade() -> None:
    # Default'larni o'chirish
    op.execute("ALTER TABLE lessons ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE lessons ALTER COLUMN updated_at DROP DEFAULT")