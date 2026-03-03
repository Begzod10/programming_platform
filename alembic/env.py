from logging.config import fileConfig
<<<<<<< HEAD
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from app.db.base_all import Base
from app.models.user import Student
from app.models.project import Project
from app.models.submission import Submission
from app.models.ranking import Ranking
from app.models.student_degree import StudentDegree
from app.models.achievement import Achievement
from app.models.student_achievement import StudentAchievement
from app.models.course import Course
from app.models.degree import Degree


config = context.config
=======
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.base import Base
from app.config import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("+asyncpg", ""))
>>>>>>> 157149ac3bd4f7cda1e91430880ec5cab240cb47

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


<<<<<<< HEAD
def run_migrations_offline() -> None:
=======
def run_migrations_offline():
>>>>>>> 157149ac3bd4f7cda1e91430880ec5cab240cb47
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
<<<<<<< HEAD

=======
>>>>>>> 157149ac3bd4f7cda1e91430880ec5cab240cb47
    with context.begin_transaction():
        context.run_migrations()


<<<<<<< HEAD
def run_migrations_online() -> None:
    url = config.get_main_option("sqlalchemy.url")
    url = url.replace("postgresql+asyncpg", "postgresql+psycopg2")

=======
def run_migrations_online():
>>>>>>> 157149ac3bd4f7cda1e91430880ec5cab240cb47
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
<<<<<<< HEAD
        url=url,
    )

=======
    )
>>>>>>> 157149ac3bd4f7cda1e91430880ec5cab240cb47
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
<<<<<<< HEAD
    run_migrations_online()
=======
    run_migrations_online()
>>>>>>> 157149ac3bd4f7cda1e91430880ec5cab240cb47
