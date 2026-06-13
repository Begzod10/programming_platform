"""Add image fields to courses

Revision ID: 8a13d9279eab
Revises: ef5b9d7cab85
Create Date: 2026-03-15 14:26:33.689783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8a13d9279eab'
down_revision: Union[str, None] = 'ef5b9d7cab85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new image columns
    op.add_column('courses', sa.Column('cover_image_url', sa.String(length=500), nullable=True))
    op.add_column('courses', sa.Column('thumbnail_url', sa.String(length=500), nullable=True))
    op.add_column('courses', sa.Column('video_intro_url', sa.String(length=500), nullable=True))
    op.add_column('courses', sa.Column('syllabus_url', sa.String(length=500), nullable=True))

    # Change description type
    op.alter_column('courses', 'description',
               existing_type=sa.VARCHAR(length=500),
               type_=sa.Text(),
               existing_nullable=False)

    # Change timestamp types
    op.alter_column('courses', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)

    op.alter_column('courses', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)

    # ✅ Fix timestamps default values
    op.execute("ALTER TABLE courses ALTER COLUMN created_at SET DEFAULT NOW()")
    op.execute("ALTER TABLE courses ALTER COLUMN updated_at SET DEFAULT NOW()")

    # Update existing NULL values
    op.execute("UPDATE courses SET created_at = NOW() WHERE created_at IS NULL")
    op.execute("UPDATE courses SET updated_at = NOW() WHERE updated_at IS NULL")


def downgrade() -> None:
    # Remove defaults
    op.execute("ALTER TABLE courses ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE courses ALTER COLUMN updated_at DROP DEFAULT")

    # Revert timestamp types
    op.alter_column('courses', 'updated_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)

    op.alter_column('courses', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)

    # Revert description type
    op.alter_column('courses', 'description',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=500),
               existing_nullable=False)

    # Drop new columns
    op.drop_column('courses', 'syllabus_url')
    op.drop_column('courses', 'video_intro_url')
    op.drop_column('courses', 'thumbnail_url')
    op.drop_column('courses', 'cover_image_url')