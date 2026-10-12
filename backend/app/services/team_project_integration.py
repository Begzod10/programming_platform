"""The integration step of a team project.

Every piece is approved on its own, but nothing joins them: each ends up as a separate
repo or ZIP, so a "finished" team has no runnable project. When the last piece is
approved the team's integration is unlocked (`integration_unlocked_at`), the team gets
an event, and the lead is told to assemble everything in ONE repo and submit that link.
"""
import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team_project import (
    TaskStatus, TeamProjectEvent, TeamProjectTask, TeamProjectTeam,
)
from app.utils.datetime_utils import utcnow

logger = logging.getLogger(__name__)

LEAD_MESSAGE = (
    "Barcha vazifalar tasdiqlandi. Endi hamma qismlarni BITTA repoga birlashtiring "
    "(backend + frontend, README'da ishga tushirish yo'l-yo'rig'i bilan), qismlar bir-biriga "
    "ulanishini tekshiring va shu repo havolasini yuborib yakuniy topshiring."
)


async def unlock_integration_if_ready(db: AsyncSession, team_id: int) -> bool:
    """Idempotent, best-effort: never raises. Returns True only on the call that unlocks."""
    try:
        team = (await db.execute(
            select(TeamProjectTeam).where(TeamProjectTeam.id == team_id).with_for_update()
        )).scalar_one_or_none()
        if team is None or team.integration_unlocked_at is not None:
            return False
        statuses = (await db.execute(
            select(TeamProjectTask.status).where(TeamProjectTask.team_id == team_id)
        )).scalars().all()
        if not statuses or any(s != TaskStatus.approved for s in statuses):
            return False
        team.integration_unlocked_at = utcnow()
        db.add(TeamProjectEvent(
            team_project_id=team.team_project_id, team_id=team_id,
            event_type="integration_unlocked", payload_json=json.dumps({"tasks": len(statuses)}),
        ))
        await db.commit()
        if team.lead_student_id:
            from app.services.notification_service import _emit
            await _emit(
                db, team.lead_student_id, type="team_integration_ready", tone="ok",
                title="Jamoaviy loyiha: birlashtirish vaqti 🧩", body=LEAD_MESSAGE,
                link="/student/team-projects",
            )
        return True
    except Exception:  # noqa: BLE001 — a notification/bookkeeping step must never fail a review
        logger.exception("[integration] unlock failed for team %s", team_id)
        try:
            await db.rollback()
        except Exception:
            pass
        return False
