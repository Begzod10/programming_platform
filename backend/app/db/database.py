import logging
from urllib.parse import urlparse, urlunparse

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from app.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=True,
)


def _safe_db_url() -> str:
    """Render DATABASE_URL without the password — safe to log."""
    try:
        parsed = urlparse(settings.DATABASE_URL)
        if parsed.password:
            netloc = parsed.netloc.replace(f":{parsed.password}@", ":***@")
            parsed = parsed._replace(netloc=netloc)
        return urlunparse(parsed)
    except Exception:
        return "<db url>"


async def init_db():
    """Verify DB connectivity and create any missing tables.

    create_all is idempotent — it only creates tables that don't exist. This is
    a defensive bootstrap so fresh deploys work even if the alembic chain is
    broken. Production should still rely on alembic for schema changes; this
    just prevents a 500 storm when an unmigrated table is queried.
    """
    from app.db import base  # noqa: F401  ensure all models are registered
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            await conn.run_sync(base.Base.metadata.create_all)
        logger.info("Database ready (%s)", _safe_db_url())
        print(" Database connection successful.")
    except Exception:
        logger.exception("Database connection failed for %s", _safe_db_url())
        print(" Database connection failed (see logs for details).")
        raise
