"""PC Guard: server-side lock decision for lab PCs."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.pc_control import PcDevice, PcSession, PcCommand
from app.models.user import Student
from app.services import daily_quota_service

_SCOPE_RANK = {"device": 3, "group": 2, "all": 1}


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


async def resolve_override(db: AsyncSession, device: PcDevice) -> Optional[str]:
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
        .where(PcCommand.type.in_(("lock", "unlock", "clear")), scope_match)
    )).scalars().all()
    if not rows:
        return None
    best = max(rows, key=lambda c: (_SCOPE_RANK.get(c.scope_type, 0), c.id))
    return None if best.type == "clear" else best.type


def _default_allowlist() -> list[dict]:
    # TODO(task5): replace with pc_allowlist_service.effective_allowlist
    exes = ["code.exe", "windowsterminal.exe", "cmd.exe", "powershell.exe",
            "python.exe", "node.exe", "chrome.exe", "msedge.exe"]
    return [{"exe": e, "publisher": None} for e in exes]


def _browser_hosts() -> list[str]:
    return [h.strip() for h in (settings.PC_PLATFORM_HOSTS or "").split(",") if h.strip()]


async def compute_state(db: AsyncSession, device: PcDevice) -> dict:
    sess = (await db.execute(
        select(PcSession)
        .where(PcSession.device_id == device.id, PcSession.signed_out_at.is_(None))
        .order_by(PcSession.id.desc())
        .limit(1)
    )).scalars().first()
    student = None
    if sess is not None:
        student = await db.get(Student, sess.student_id)

    remaining = completed = required = 0
    quota_unlocked = False
    if student is not None:
        q = await daily_quota_service.get_today(db, student.id)
        remaining, completed, required = q.remaining, q.completed, q.required
        quota_unlocked = q.unlocked

    override = await resolve_override(db, device)
    locked, reason = decide_lock(
        has_student=student is not None, override=override, quota_unlocked=quota_unlocked)
    return {
        "locked": locked,
        "reason": reason,
        "remaining": remaining,
        "completed": completed,
        "required": required,
        "student": {"id": student.id, "full_name": student.full_name} if student else None,
        "allowlist": _default_allowlist(),
        "browser_hosts": _browser_hosts(),
        "server_time": datetime.now(timezone.utc).isoformat(),
    }
