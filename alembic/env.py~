import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Model va MetaData ni import qilish
from app.db.base import Base
from app.models.user import Student
from app.models.course import Course
from app.models.project import Project
from app.models.achievement import Achievement
from app.models.student_achievement import StudentAchievement
from app.models.student_degree import StudentDegree
from app.models.degree import Degree
from app.models.submission import Submission
from app.models.ranking import Ranking


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Oflayn rejimda migratsiyalarni ishga tushirish."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Migratsiyani sinxron kontekstda bajarish."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Onlayn rejimda (asinxron) migratsiyalarni ishga tushirish."""

    # Bu qism asinxron engineni yaratadi
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # run_sync yordamida asinxron ulanish ichida sinxron funksiyani chaqiramiz
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Asinxron funksiyani ishga tushirish
    asyncio.run(run_migrations_online())
