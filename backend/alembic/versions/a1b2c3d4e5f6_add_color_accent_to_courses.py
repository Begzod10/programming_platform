"""add color_accent to courses

Revision ID: a1b2c3d4e5f6
Revises: f97620dc4f54
Create Date: 2026-06-13

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = 'f97620dc4f54'
branch_labels = None
depends_on = None

# Default palette per course id — assigned once, can be changed via teacher UI.
_DEFAULTS = {
    9:  '#e34f26',  # HTML CSS       — HTML orange
    21: '#3776ab',  # Python Flask   — Python blue
    22: '#f0db4f',  # Javascript     — JS yellow
    28: '#3776ab',  # Python Flask mid
    30: '#3776ab',  # Python Asoslari
    33: '#7c3aed',  # Dasturlash kirish — purple
    37: '#3776ab',  # Python Keyingi
    39: '#f0db4f',  # JavaScript Keyingi
    41: '#336791',  # SQL/PostgreSQL — PG blue
    43: '#61dafb',  # React          — React cyan
    45: '#f05032',  # Git/GitHub     — Git orange
    48: '#2ca5e0',  # Telegram Bot   — Telegram blue
}


def upgrade() -> None:
    op.add_column('courses', sa.Column('color_accent', sa.String(7), nullable=True))
    for course_id, color in _DEFAULTS.items():
        op.execute(
            f"UPDATE courses SET color_accent = '{color}' WHERE id = {course_id}"
        )


def downgrade() -> None:
    op.drop_column('courses', 'color_accent')
