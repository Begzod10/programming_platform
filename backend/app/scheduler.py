"""
app/scheduler.py

Avtomatik reset scheduler.

O'rnatish:
    pip install apscheduler

main.py ga qo'shish:
    from app.scheduler import start_scheduler

    @app.on_event("startup")
    async def startup_event():
        start_scheduler()
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.services.ranking_service import RankingService
from app.services.translation_backfill import backfill_course_translations
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")  # O'zbekiston vaqti


# ============================================================
# RESET FUNKSIYALARI
# ============================================================

async def job_reset_daily():
    """
    Har kecha 00:00 da ishlaydi.
    Kunlik ballarni 0 ga tushiradi.
    Haftalik va oylik ballar SAQLANIB qoladi.
    """
    async with AsyncSessionLocal() as db:
        service = RankingService(db)
        await service.reset_daily_points()
        logger.info("✅ Kunlik ballar reset qilindi")


async def job_reset_weekly():
    """
    Har dushanba kuni 00:00 da ishlaydi.
    Haftalik ballarni 0 ga tushiradi.
    """
    async with AsyncSessionLocal() as db:
        service = RankingService(db)
        await service.reset_weekly_points()
        logger.info("✅ Haftalik ballar reset qilindi")


async def job_reset_monthly():
    """
    Har oyning 1-kuni 00:00 da ishlaydi.
    Oylik ballarni 0 ga tushiradi.
    """
    async with AsyncSessionLocal() as db:
        service = RankingService(db)
        await service.reset_monthly_points()
        logger.info("✅ Oylik ballar reset qilindi")


async def job_retry_stuck_project_reviews():
    """Safety net for a real incident found live: a student's ZIP upload
    (project id 4926, 2026-09-11) got permanently stuck at status
    "Submitted" with reviewed_at=None and NO instructor_feedback at all —
    6 days with zero trace of why. Root cause traced to an ~11-minute
    complete backend stall (same worker PID, zero requests served
    platform-wide) that overlapped the AI review call for that exact
    submission — most likely the in-flight request got cancelled
    (asyncio.CancelledError, a BaseException, not an Exception) once the
    client gave up waiting, which _run_ai_review_and_persist_failure's
    `except Exception` can't catch, so its own failure-persist step never
    ran. Rather than chase every possible way a request can die mid-flight
    without leaving a trace, this sweeps for the *symptom* instead — a
    project stuck with genuinely NO record of an attempt at all — every 15
    minutes and retries it.

    Deliberately narrow to avoid retry-looping a project that's legitimately
    still under normal review, or one that already failed for a real reason:
      - reviewed_at IS NULL AND instructor_feedback empty — the "no trace of
        an attempt" signature; a project that failed normally already has
        instructor_feedback set (via _run_ai_review_and_persist_failure /
        submit_project's own failure path) and is left alone here, same as
        one still genuinely mid-review.
      - submitted_at older than 20 minutes — comfortably past how long a
        real synchronous AI review ever takes, so this never fires on one
        that's simply still in flight.
    """
    from app.models.project import Project
    from app.api.v1.endpoints.projects import _run_ai_review_and_persist_failure

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=20)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Project).where(
                Project.status == "Submitted",
                Project.reviewed_at.is_(None),
                (Project.instructor_feedback.is_(None)) | (Project.instructor_feedback == ""),
                Project.submitted_at < cutoff,
            )
        )
        stuck = result.scalars().all()
        if not stuck:
            return

        logger.warning(
            "⚠️  %d loyiha AI tekshiruvsiz qolib ketgan (qayta urinilmoqda): %s",
            len(stuck), [p.id for p in stuck],
        )
        for project in stuck:
            try:
                await _run_ai_review_and_persist_failure(db, project)
            except Exception as e:
                # One project's retry must never take the rest of the sweep
                # down with it — exactly the isolation
                # _run_ai_review_and_persist_failure itself already applies
                # to a single request; this is the same guarantee one level up.
                logger.warning("[sweep-stuck-review] project=%d retry failed: %s", project.id, e)


async def job_retry_stuck_team_task_reviews():
    """Same safety net as job_retry_stuck_project_reviews above, for
    team-project task submissions instead of regular projects — see that
    function's docstring for the full incident writeup this pattern guards
    against (an unbounded AI call cancelled mid-flight via
    asyncio.CancelledError, a BaseException, skips `except Exception` and
    leaves nothing stuck-but-invisible behind).

    team_project_task_review.py's review_task_submission now has its own
    asyncio.wait_for timeout guard (the root-cause fix), so a hang can only
    ever end in an ordinary asyncio.TimeoutError there. This sweep is the
    same second layer of defense as the project one: unlike a project,
    TeamProjectTask has no separate "we tried and here's why it failed"
    field to distinguish a legitimately-failed review from one still
    in-flight or one that never got attempted at all, so this sweeps purely
    on "submitted a while ago, still no reviewed_at" — retrying a task that
    already failed for a mundane reason (e.g. an unreadable repo) is
    harmless; it just fails the same way again.
    """
    from app.models.team_project import TeamProjectTask, TaskStatus
    from app.services.team_project_task_review import review_task_submission

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=20)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(TeamProjectTask).where(
                TeamProjectTask.status == TaskStatus.submitted,
                TeamProjectTask.reviewed_at.is_(None),
                TeamProjectTask.submitted_at < cutoff,
            )
        )
        stuck = result.scalars().all()
        if not stuck:
            return

        logger.warning(
            "⚠️  %d jamoaviy loyiha vazifasi AI tekshiruvsiz qolib ketgan (qayta urinilmoqda): %s",
            len(stuck), [t.id for t in stuck],
        )
        for task in stuck:
            try:
                await review_task_submission(db, task.id)
            except Exception as e:
                # One task's retry must never take the rest of the sweep
                # down with it — same isolation guarantee as the project
                # sweep above.
                logger.warning("[sweep-stuck-task-review] task=%d retry failed: %s", task.id, e)


# ============================================================
# SCHEDULER ISHGA TUSHIRISH
# ============================================================

def start_scheduler():
    """
    main.py da startup_event ichida chaqiring:

        @app.on_event("startup")
        async def startup_event():
            start_scheduler()
    """

    # Har kecha 00:00 da kunlik reset
    scheduler.add_job(
        job_reset_daily,
        trigger=CronTrigger(hour=0, minute=0),  # 00:00 har kuni
        id="reset_daily",
        replace_existing=True
    )

    # Har dushanba 00:00 da haftalik reset
    scheduler.add_job(
        job_reset_weekly,
        trigger=CronTrigger(day_of_week="mon", hour=0, minute=0),  # Dushanba 00:00
        id="reset_weekly",
        replace_existing=True
    )

    # Har oy 1-si 00:00 da oylik reset
    scheduler.add_job(
        job_reset_monthly,
        trigger=CronTrigger(day=1, hour=0, minute=0),  # Har oy 1-si 00:00
        id="reset_monthly",
        replace_existing=True
    )

    # Course title/description RU-translation backfill — moved out of
    # main.py's lifespan() so a slow/unavailable OpenAI never delays server
    # startup (see translation_backfill.py). Runs once ~30s after startup
    # (DateTrigger — gives init_db()/the scheduler itself time to settle
    # first) and then daily at 03:00, well clear of the midnight reset jobs
    # above.
    scheduler.add_job(
        backfill_course_translations,
        trigger=DateTrigger(run_date=datetime.now(timezone.utc) + timedelta(seconds=30)),
        id="translation_backfill_startup",
        replace_existing=True,
    )
    scheduler.add_job(
        backfill_course_translations,
        trigger=CronTrigger(hour=3, minute=0),
        id="translation_backfill_daily",
        replace_existing=True,
    )

    # Stuck-AI-review sweep — see job_retry_stuck_project_reviews's docstring
    # for the live incident this guards against.
    scheduler.add_job(
        job_retry_stuck_project_reviews,
        trigger=IntervalTrigger(minutes=15),
        id="retry_stuck_project_reviews",
        replace_existing=True,
    )

    # Same sweep, for team-project task submissions — see
    # job_retry_stuck_team_task_reviews's docstring.
    scheduler.add_job(
        job_retry_stuck_team_task_reviews,
        trigger=IntervalTrigger(minutes=15),
        id="retry_stuck_team_task_reviews",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("📅 Scheduler ishga tushdi!")
    logger.info("   - Kunlik reset: har kecha 00:00")
    logger.info("   - Haftalik reset: har dushanba 00:00")
    logger.info("   - Oylik reset: har oy 1-si 00:00")
    logger.info("   - Kurs RU tarjima backfill: ishga tushgandan 30s keyin, keyin har kuni 03:00")
    logger.info("   - Tekshirilmagan loyihalarni qayta urinish: har 15 daqiqada")