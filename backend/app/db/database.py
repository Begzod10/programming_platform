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

    After create_all, we also reconcile a small set of indexes/constraints
    that were added to models *after* their tables were first created in
    prod (create_all does NOT touch existing tables). Each statement is
    idempotent so this is safe to run on every startup.
    """
    from app.db import base  # noqa: F401  ensure all models are registered
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            await conn.run_sync(base.Base.metadata.create_all)
            await _reconcile_indexes(conn)
        logger.info("Database ready (%s)", _safe_db_url())
        print(" Database connection successful.")
    except Exception:
        logger.exception("Database connection failed for %s", _safe_db_url())
        print(" Database connection failed (see logs for details).")
        raise


async def _reconcile_indexes(conn) -> None:
    """Idempotently add post-hoc indexes to tables that already exist.

    Add a new entry here when a model gains a UniqueConstraint or Index
    after the table has shipped to prod. Each statement must use
    IF NOT EXISTS so re-running on a clean DB is a no-op.
    """
    statements = [
        # 2026-06-01: submissions(student_id, lesson_id) partial unique
        # to close the submit_lesson_project TOCTOU. Partial because
        # standalone (lesson_id IS NULL) projects can repeat.
        text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_submission_student_lesson "
            "ON submissions (student_id, lesson_id) "
            "WHERE lesson_id IS NOT NULL"
        ),
        # 2026-06-03: Increase lesson limits to 500
        text(
            "DO $$ BEGIN "
            "IF (SELECT character_maximum_length FROM information_schema.columns "
            "WHERE table_name = 'lessons' AND column_name = 'title') < 500 THEN "
            "ALTER TABLE lessons ALTER COLUMN title TYPE VARCHAR(500); "
            "END IF; "
            "IF (SELECT character_maximum_length FROM information_schema.columns "
            "WHERE table_name = 'lessons' AND column_name = 'chapter') < 500 THEN "
            "ALTER TABLE lessons ALTER COLUMN chapter TYPE VARCHAR(500); "
            "END IF; "
            "IF (SELECT character_maximum_length FROM information_schema.columns "
            "WHERE table_name = 'lessons' AND column_name = 'task_title') < 500 THEN "
            "ALTER TABLE lessons ALTER COLUMN task_title TYPE VARCHAR(500); "
            "END IF; "
            "END $$;"
        ),
        # 2026-07-20: split spendable balance (total_points) from career
        # total (lifetime_points). Existing prod rows are backfilled from
        # total_points so no student's rank/level moves at cutover.
        text(
            "ALTER TABLE students "
            "ADD COLUMN IF NOT EXISTS lifetime_points INTEGER NOT NULL DEFAULT 0"
        ),
        text(
            "UPDATE students SET lifetime_points = total_points "
            "WHERE lifetime_points = 0 AND total_points > 0"
        ),
        # 2026-08-01: bug-hunt question kind on game_questions. Additive —
        # existing rows default to 'quiz' so the quiz path is byte-identical.
        text(
            "ALTER TABLE game_questions "
            "ADD COLUMN IF NOT EXISTS question_kind VARCHAR(20) NOT NULL DEFAULT 'quiz'"
        ),
        text("ALTER TABLE game_questions ADD COLUMN IF NOT EXISTS code_snippet TEXT"),
        text("ALTER TABLE game_questions ADD COLUMN IF NOT EXISTS code_language VARCHAR(20)"),
        text("ALTER TABLE game_questions ADD COLUMN IF NOT EXISTS bug_line INTEGER"),
        text("ALTER TABLE game_questions ADD COLUMN IF NOT EXISTS bug_explanation TEXT"),
        text("ALTER TABLE game_questions ADD COLUMN IF NOT EXISTS bug_explanation_ru TEXT"),
        # 2026-08-02: bug-hunt kind on lesson_questions (the reusable per-lesson
        # bank, mirrors game_questions above) + relax quiz-only NOT NULLs so
        # bug_hunt rows can leave options/correct_option empty.
        text("ALTER TABLE lesson_questions ALTER COLUMN options DROP NOT NULL"),
        text("ALTER TABLE lesson_questions ALTER COLUMN correct_option DROP NOT NULL"),
        text(
            "ALTER TABLE lesson_questions "
            "ADD COLUMN IF NOT EXISTS question_kind VARCHAR(20) NOT NULL DEFAULT 'quiz'"
        ),
        text("ALTER TABLE lesson_questions ADD COLUMN IF NOT EXISTS code_snippet TEXT"),
        text("ALTER TABLE lesson_questions ADD COLUMN IF NOT EXISTS code_language VARCHAR(20)"),
        text("ALTER TABLE lesson_questions ADD COLUMN IF NOT EXISTS bug_line INTEGER"),
        text("ALTER TABLE lesson_questions ADD COLUMN IF NOT EXISTS distractor_lines JSON"),
        text("ALTER TABLE lesson_questions ADD COLUMN IF NOT EXISTS bug_explanation TEXT"),
        text("ALTER TABLE lesson_questions ADD COLUMN IF NOT EXISTS bug_explanation_ru TEXT"),
        # 2026-09-05: birth_date synced from gennis/turon (see
        # gennis_service.py) — student_platform never collected this
        # itself, so it's purely a mirror of upstream data, nullable.
        text("ALTER TABLE students ADD COLUMN IF NOT EXISTS birth_date DATE"),
    ]
    for stmt in statements:
        await conn.execute(stmt)
