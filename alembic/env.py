from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# 1. Proekt yo'lini tizimga qo'shish
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 2. Modellarni jamlangan joydan import qilish (MUHIM!)
from app.db.base import Base  # Yuqorida to'g'irlagan faylimiz
from app.config import settings

config = context.config

# 3. Database URL-ni sozlash (Alembic asyncpg-ni tushunmaydi, shuning uchun o'zgartiramiz)
db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 4. Metadata - Alembic endi barcha modellarni ko'radi
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    # Online migratsiya uchun ulanish
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

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
    run_migrations_online()