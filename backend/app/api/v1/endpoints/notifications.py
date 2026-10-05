from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_student
from app.models.notification import Notification
from app.models.user import Student
from app.schemas.notification import NotificationList, NotificationRead, UnreadCount

router = APIRouter()


@router.get("/", response_model=NotificationList)
async def list_notifications(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """Recent notifications (newest first) plus the live unread count."""
    sid = current_student.id

    rows = (await db.execute(
        select(Notification)
        .where(Notification.student_id == sid)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .limit(limit)
    )).scalars().all()

    unread = (await db.execute(
        select(func.count(Notification.id)).where(
            Notification.student_id == sid,
            Notification.is_read == False,  # noqa: E712
        )
    )).scalar() or 0

    return NotificationList(
        items=[NotificationRead.model_validate(r) for r in rows],
        unread_count=unread,
    )


@router.get("/unread-count", response_model=UnreadCount)
async def unread_count(
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """Lightweight endpoint the header bell polls on an interval."""
    unread = (await db.execute(
        select(func.count(Notification.id)).where(
            Notification.student_id == current_student.id,
            Notification.is_read == False,  # noqa: E712
        )
    )).scalar() or 0
    return UnreadCount(unread_count=unread)


@router.post("/{notification_id}/read", response_model=UnreadCount)
async def mark_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    note = (await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.student_id == current_student.id,
        )
    )).scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Bildirishnoma topilmadi")
    if not note.is_read:
        note.is_read = True
        await db.commit()

    unread = (await db.execute(
        select(func.count(Notification.id)).where(
            Notification.student_id == current_student.id,
            Notification.is_read == False,  # noqa: E712
        )
    )).scalar() or 0
    return UnreadCount(unread_count=unread)


@router.post("/read-all", response_model=UnreadCount)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    await db.execute(
        update(Notification)
        .where(
            Notification.student_id == current_student.id,
            Notification.is_read == False,  # noqa: E712
        )
        .values(is_read=True)
    )
    await db.commit()
    return UnreadCount(unread_count=0)
