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
from sqlalchemy import and_, or_, select
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


# Feedback texts that mean "no real review happened yet" (see the sweep below).
TRANSIENT_REVIEW_MARKERS = (
    "AI baholash vaqtincha ishlamayapti",
    "o'qituvchi tomonidan tekshiriladi",
)
TRANSIENT_RETRY_WINDOW = timedelta(days=3)


async def job_expire_code_checks():
    """Code-check quizzes nobody took (or abandoned) become 'expired' and join the teacher's queue."""
    from app.services.code_check_service import expire_old_checks
    async with AsyncSessionLocal() as db:
        n = await expire_old_checks(db)
        if n:
            logger.info("📝 %d ta kod tekshiruvi muddati o'tdi (o'qituvchiga yuborildi)", n)


async def job_purge_expired_demo_accounts():
    """Delete demo accounts (core/demo.py) older than DEMO_RETENTION.

    They are flagged, excluded from every statistic and never enrolled, so
    removing them changes no admin number — and a visitor who never became a
    student never leaves a "deleted student" behind.
    """
    from app.models.user import Student
    from app.core.demo import DEMO_RETENTION

    cutoff = datetime.now(timezone.utc) - DEMO_RETENTION
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(
            select(Student).where(Student.is_demo.is_(True), Student.created_at < cutoff)
        )).scalars().all()
        removed = 0
        for student in rows:
            try:
                await db.delete(student)
                await db.commit()
                removed += 1
            except Exception as e:      # one stubborn row must not stop the rest
                await db.rollback()
                logger.warning("[demo-purge] student=%s not deleted: %s", student.id, e)
        if removed:
            logger.info("🧹 %d ta muddati o'tgan demo akkaunt o'chirildi", removed)


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

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=20)
    # A project parked with a *transient* placeholder ("AI is down, teacher will
    # grade", or the old "held for teacher" notice) is also waiting on a review
    # that never came: on 2026-09-25 two such projects sat unreviewed for 12
    # days, since the AI came back but nothing re-ran them. Retried only inside
    # a window, so one that keeps failing isn't hammered forever; a project that
    # failed for a real reason (unreadable ZIP, rule violation) has different
    # feedback text and is left alone.
    transient_feedback = or_(*(
        Project.instructor_feedback.ilike(f"%{marker}%")
        for marker in TRANSIENT_REVIEW_MARKERS
    ))
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Project).where(
                Project.status == "Submitted",
                Project.reviewed_at.is_(None),
                Project.submitted_at < cutoff,
                or_(
                    Project.instructor_feedback.is_(None),
                    Project.instructor_feedback == "",
                    and_(transient_feedback,
                         Project.submitted_at > now - TRANSIENT_RETRY_WINDOW),
                ),
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

async def job_process_quota_eod():
    """00:05 Asia/Tashkent — process the day that just ended for the daily
    learning quota: penalize missed lessons (floored at 0), carry the debt
    forward, update the quota streak + 0.1% yield, and seed tomorrow's row.

    Commits PER STUDENT so one student's failure can't roll back the rest, and
    so the job is safe to re-run after a restart (each day-row is idempotent
    via its `processed` flag).
    """
    from zoneinfo import ZoneInfo
    from app.services import daily_quota_service as dq
    from app.services.ranking_service import RankingService
    from app.models.user import Student

    tz = ZoneInfo("Asia/Tashkent")
    day = (datetime.now(tz) - timedelta(minutes=10)).date()  # the day that just closed
    processed = 0
    async with AsyncSessionLocal() as db:
        rs = RankingService(db)
        students = (await db.execute(
            select(Student).where(Student.is_active.is_(True), Student.is_demo.is_(False))
        )).scalars().all()
        for student in students:
            try:
                await dq.process_eod_for_student(db, rs, student, day)
                await db.commit()
                processed += 1
            except Exception as e:  # noqa: BLE001
                logger.warning("quota EOD failed for student %s: %s", student.id, e)
                try:
                    await db.rollback()
                except Exception:
                    pass
    logger.info("✅ Kunlik kvota EOD qayta ishlandi: %s ta student (%s)", processed, day)


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

    # Har kecha 00:05 da kunlik kvota EOD (kunlik reset'dan keyin)
    scheduler.add_job(
        job_process_quota_eod,
        trigger=CronTrigger(hour=0, minute=5),  # 00:05 — after the 00:00 daily reset
        id="quota_eod",
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

    scheduler.add_job(
        job_expire_code_checks,
        trigger=IntervalTrigger(minutes=30),
        id="expire_code_checks",
        replace_existing=True,
    )
    scheduler.add_job(
        job_purge_expired_demo_accounts,
        trigger=CronTrigger(hour=4, minute=15),
        id="purge_expired_demo_accounts",
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