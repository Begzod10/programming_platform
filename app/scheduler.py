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
from app.db.session import AsyncSessionLocal
from app.services.ranking_service import RankingService
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

    scheduler.start()
    logger.info("📅 Scheduler ishga tushdi!")
    logger.info("   - Kunlik reset: har kecha 00:00")
    logger.info("   - Haftalik reset: har dushanba 00:00")
    logger.info("   - Oylik reset: har oy 1-si 00:00")