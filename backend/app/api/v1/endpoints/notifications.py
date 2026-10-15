from typing import Optional

from fastapi import (
    APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect,
)
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.dependencies import get_db, get_current_student
from app.models.notification import Notification
from app.models.user import Student
from app.schemas.notification import NotificationList, NotificationRead, UnreadCount
from app.services import notification_service
from app.ws.manager import notif_ws_manager

router = APIRouter()


@router.websocket("/ws")
async def notifications_ws(
    websocket: WebSocket,
    token: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Realtime notification stream for the signed-in student.

    Auth is via ``?token=`` because browsers can't set an Authorization header on
    a WebSocket handshake (same approach as the team-game socket). The channel is
    server→client only: on connect it pushes a ``{type:'unread'}`` frame, then a
    ``{type:'notification'}`` frame each time one is emitted for this student.
    Client may send ``"ping"`` to keep the connection warm (answered ``"pong"``).
    """
    user_id = decode_access_token(token) if token else None
    if user_id is None:
        await websocket.close(code=4001)
        return

    student = (await db.execute(
        select(Student).where(Student.id == user_id)
    )).scalar_one_or_none()
    if not student or not student.is_active:
        await websocket.close(code=4001)
        return

    await notif_ws_manager.connect(student.id, websocket)
    try:
        unread = (await db.execute(
            select(func.count(Notification.id)).where(
                Notification.student_id == student.id,
                Notification.is_read == False,  # noqa: E712
            )
        )).scalar() or 0
        await websocket.send_json({"type": "unread", "unread_count": unread})

        # We only push server→client, but must keep reading so a disconnect is
        # noticed promptly and heartbeat pings are answered.
        while True:
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        pass
    except Exception:  # noqa: BLE001 — never let a socket error bubble out
        pass
    finally:
        notif_ws_manager.disconnect(student.id, websocket)


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
    # Re-sync the bell on the student's other open tabs/devices.
    await notification_service.broadcast_unread(db, current_student.id)
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
    await notification_service.broadcast_unread(db, current_student.id)
    return UnreadCount(unread_count=0)
