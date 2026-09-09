"""Read/delete every unhandled 500 the app has hit — see
app/core/exceptions.py's unhandled_exception_handler, the only writer.

Deliberately gated to two specific accounts, not the general teacher role —
a traceback can contain another student's request path/params, and this is
operational visibility into the WHOLE platform's crashes, not a
per-classroom teacher feature. Compare app/api/v1/endpoints/teacher/
statistics.py, which is real per-teacher data and only needs
get_current_instructor."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_instructor, get_db
from app.models.error_log import AppErrorLog
from app.models.user import Student
from app.schemas.error_log import ErrorLogOut

router = APIRouter()

# Only these two accounts can see raw tracebacks. Add a username here (not
# a new role) to grant someone else access — a role would need every other
# teacher-role endpoint re-audited for "does this also leak to error-log
# viewers", which is more than this small allowlist is worth.
_ALLOWED_USERNAMES = {"rimefara_teach", "rimefara_teach_turon"}


def _require_error_log_access(
    current_teacher: Student = Depends(get_current_instructor),
) -> Student:
    if current_teacher.username not in _ALLOWED_USERNAMES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu bo'limni faqat administrator ko'ra oladi",
        )
    return current_teacher


@router.get("", response_model=ErrorLogOut)
async def list_error_logs(
    db: AsyncSession = Depends(get_db),
    _teacher: Student = Depends(_require_error_log_access),
    limit: int = Query(100, ge=1, le=500),
    role: str | None = Query(None, description="Filter by actor_role (student/teacher)"),
):
    q = select(AppErrorLog).order_by(AppErrorLog.created_at.desc())
    if role is not None:
        q = q.where(AppErrorLog.actor_role == role)
    q = q.limit(limit)
    rows = (await db.execute(q)).scalars().all()
    return ErrorLogOut(items=rows)


@router.delete("/{entry_id}")
async def delete_error_log(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    _teacher: Student = Depends(_require_error_log_access),
):
    await db.execute(delete(AppErrorLog).where(AppErrorLog.id == entry_id))
    await db.commit()
    return {"msg": "deleted"}


@router.delete("")
async def clear_error_logs(
    db: AsyncSession = Depends(get_db),
    _teacher: Student = Depends(_require_error_log_access),
):
    await db.execute(delete(AppErrorLog))
    await db.commit()
    return {"msg": "cleared"}
