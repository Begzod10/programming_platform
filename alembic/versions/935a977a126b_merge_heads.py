"""Merge heads

Revision ID: 935a977a126b
Revises: 45c5ad51cc6a, 7f193745b4ba
Create Date: 2026-03-09 15:29:10.564828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '935a977a126b'
down_revision: Union[str, None] = ('45c5ad51cc6a', '7f193745b4ba')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
