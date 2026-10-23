"""PC Guard: server-side lock decision for lab PCs."""
from datetime import datetime, time, timezone
from typing import Optional

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.pc_control import PcDevice, PcSession, PcCommand
from app.models.user import Student
from app.services import daily_quota_service, pc_allowlist_service


def decide_lock(*, has_student: bool, override: Optional[str], quota_unlocked: bool) -> tuple[bool, str]:
    if not has_student:
        return True, "no_student"
    if override == "lock":
        return True, "teacher_lock"
    if override == "unlock":
        return False, "teacher_unlock"
    if quota_unlocked:
        return False, "quota_met"
    return True, "quota_pending"


def _utc(dt: datetime) -> datetime:
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


async def _open_session(db: AsyncSession, device_id: int) -> Optional[PcSession]:
    return (await db.execute(
        select(PcSession)
        .where(PcSession.device_id == device_id, PcSession.signed_out_at.is_(None))
        .order_by(PcSession.id.desc())
        .limit(1)
    )).scalars().first()


async def resolve_override(db: AsyncSession, device: PcDevice,
                           session: Optional[PcSession] = None) -> Optional[str]:
    """Newest applicable lock/unlock/clear command wins, whatever its scope.

    A command applies only if it was created on the current Tashkent calendar day, and a
    device-scope command only if it was created during the device's current session (it
    targets the person at that PC and must not carry over to the next student)."""
    if session is None:
        session = await _open_session(db, device.id)
    day_start = datetime.combine(
        daily_quota_service.today_local(), time.min, tzinfo=daily_quota_service.TZ
    ).astimezone(timezone.utc)

    scope_match = or_(
        and_(PcCommand.scope_type == "device", PcCommand.scope_id == device.id),
        PcCommand.scope_type == "all",
    )
    if device.group_id is not None:
        scope_match = or_(
            scope_match,
            and_(PcCommand.scope_type == "group", PcCommand.scope_id == device.group_id),
        )
    rows = (await db.execute(
        select(PcCommand)
        .where(PcCommand.type.in_(("lock", "unlock", "clear")), scope_match,
               PcCommand.created_at >= day_start)
        .order_by(PcCommand.id.desc())
    )).scalars().all()
    for c in rows:
        if (c.scope_type == "device" and session is not None
                and _utc(c.created_at) < _utc(session.signed_in_at)):
            continue
        return None if c.type == "clear" else c.type
    return None


def _browser_hosts() -> list[str]:
    return [h.strip() for h in (settings.PC_PLATFORM_HOSTS or "").split(",") if h.strip()]


async def compute_state(db: AsyncSession, device: PcDevice,
                        session: Optional[PcSession] = None) -> dict:
    """State for `device`. `session` pins the person (the WS handler passes its own
    token's session); default is the device's newest open session."""
    sess = session if session is not None else await _open_session(db, device.id)
    student = None
    if sess is not None:
        student = await db.get(Student, sess.student_id)

    remaining = completed = required = 0
    quota_unlocked = False
    if student is not None:
        q = await daily_quota_service.get_today(db, student.id)
        remaining, completed, required = q.remaining, q.completed, q.required
        quota_unlocked = q.unlocked

    override = await resolve_override(db, device, sess)
    locked, reason = decide_lock(
        has_student=student is not None, override=override, quota_unlocked=quota_unlocked)
    return {
        "locked": locked,
        "reason": reason,
        "remaining": remaining,
        "completed": completed,
        "required": required,
        "student": {"id": student.id, "full_name": student.full_name} if student else None,
        "allowlist": await pc_allowlist_service.effective_allowlist(db, device.group_id),
        "browser_hosts": _browser_hosts(),
        "server_time": datetime.now(timezone.utc).isoformat(),
    }
