"""PC Guard device endpoints: the lab-PC agent signs a student in, polls state, signs out.

Device tokens are scoped (typ="pc") and rejected by every student API."""
import hashlib
import json
import logging
from typing import Optional
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import rate_limit
from app.core.security import create_pc_token, decode_pc_token
from app.db.session import get_db
from app.models.pc_control import PcDevice, PcSession, PcUsageEvent
from app.models.user import Student, UserRole
from app.services import auth_service
from app.services.pc_lock_service import compute_state
from app.ws.manager import pc_ws_manager

logger = logging.getLogger(__name__)

router = APIRouter()

_pc_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/pc/login")


class PcLoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=255)
    hostname: str = Field(min_length=1, max_length=255)
    machine_key: str = Field(min_length=8, max_length=512)


MAX_USAGE_EVENTS = 500
MAX_EVENT_DURATION = timedelta(hours=12)
MAX_FUTURE_SKEW = timedelta(minutes=5)
USAGE_GRACE = timedelta(hours=24)  # buffered usage may be uploaded this long after sign-out


class UsageEventIn(BaseModel):
    app_name: str = Field(min_length=1, max_length=255)
    started_at: datetime
    ended_at: datetime
    was_locked: bool = False

    @field_validator("started_at", "ended_at")
    @classmethod
    def _tz_aware(cls, v: datetime) -> datetime:
        return v if v.tzinfo is not None else v.replace(tzinfo=timezone.utc)

    @field_validator("ended_at")
    @classmethod
    def _sane_range(cls, v: datetime, info) -> datetime:
        started = info.data.get("started_at")
        if started is not None:
            if v <= started:
                raise ValueError("ended_at must be after started_at")
            if v - started > MAX_EVENT_DURATION:
                raise ValueError("event lasts longer than 12 hours")
        if v > datetime.now(timezone.utc) + MAX_FUTURE_SKEW:
            raise ValueError("ended_at is in the future")
        return v


class UsageIn(BaseModel):
    events: list[UsageEventIn] = Field(max_length=MAX_USAGE_EVENTS)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token noto'g'ri yoki muddati o'tgan",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_pc_device(
        token: str = Depends(_pc_scheme),
        db: AsyncSession = Depends(get_db),
) -> tuple[PcDevice, PcSession]:
    claims = decode_pc_token(token)
    if claims is None:
        raise _unauthorized()
    sess = await db.get(PcSession, claims["ses"])
    if (sess is None or sess.signed_out_at is not None
            or sess.student_id != claims["stu"]
            or claims["sub"] != f"pc:{sess.device_id}"):
        raise _unauthorized()
    device = await db.get(PcDevice, sess.device_id)
    if device is None:
        raise _unauthorized()
    return device, sess


async def get_pc_usage_session(
        token: str = Depends(_pc_scheme),
        db: AsyncSession = Depends(get_db),
) -> PcSession:
    """Like get_pc_device, but the session may be closed up to USAGE_GRACE ago: the agent
    buffers usage offline and uploads it after logout / re-login. Events are always
    attributed to the token's own session, never to a newer one."""
    claims = decode_pc_token(token)
    if claims is None:
        raise _unauthorized()
    sess = await db.get(PcSession, claims["ses"])
    if (sess is None or sess.student_id != claims["stu"]
            or claims["sub"] != f"pc:{sess.device_id}"):
        raise _unauthorized()
    if sess.signed_out_at is not None:
        out = sess.signed_out_at
        if out.tzinfo is None:
            out = out.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - out > USAGE_GRACE:
            raise _unauthorized()
    return sess


@router.post("/login")
async def pc_login(
        body: PcLoginIn,
        db: AsyncSession = Depends(get_db),
        # rate_limit() keys by client IP only and lab PCs share one NAT IP, so allow a class to sign in together.
        _rl: None = Depends(rate_limit(max_calls=120, window_seconds=60)),
):
    result = await auth_service.login(db, body.username, body.password)
    user = result["user"]
    student = await db.get(Student, user.id if hasattr(user, "id") else user["id"])
    if student is None or student.role != UserRole.student:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Faqat o'quvchilar kompyuterga kira oladi")

    key_hash = hashlib.sha256(body.machine_key.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc)
    device = (await db.execute(
        select(PcDevice).where(PcDevice.machine_key_hash == key_hash))).scalars().first()
    if device is None:
        device = PcDevice(hostname=body.hostname, machine_key_hash=key_hash, last_seen_at=now)
        db.add(device)
        await db.flush()
    else:
        device.hostname = body.hostname
        device.last_seen_at = now

    open_sessions = (await db.execute(
        select(PcSession).where(PcSession.device_id == device.id, PcSession.signed_out_at.is_(None))
    )).scalars().all()
    for s in open_sessions:
        s.signed_out_at = now
    sess = PcSession(device_id=device.id, student_id=student.id)
    db.add(sess)
    await db.commit()
    await db.refresh(device)
    await db.refresh(sess)
    # A socket opened with a previous session's token must not outlive that session.
    await pc_ws_manager.close_all(device.id, code=4001)

    return {
        "token": create_pc_token(device.id, student.id, sess.id),
        "state": await compute_state(db, device),
    }


@router.post("/logout")
async def pc_logout(
        ctx: tuple[PcDevice, PcSession] = Depends(get_pc_device),
        db: AsyncSession = Depends(get_db),
):
    _, sess = ctx
    device_id = sess.device_id
    sess.signed_out_at = datetime.now(timezone.utc)
    await db.commit()
    await pc_ws_manager.close_all(device_id, code=4001)
    return {"ok": True}


@router.get("/state")
async def pc_state(
        ctx: tuple[PcDevice, PcSession] = Depends(get_pc_device),
        db: AsyncSession = Depends(get_db),
):
    device, _ = ctx
    device.last_seen_at = datetime.now(timezone.utc)
    await db.commit()
    return await compute_state(db, device)


@router.post("/usage")
async def pc_usage(
        body: UsageIn,
        sess: PcSession = Depends(get_pc_usage_session),
        db: AsyncSession = Depends(get_db),
):
    """All-or-nothing: any invalid event (or >500 events) is rejected with 422 by validation."""
    for e in body.events:
        db.add(PcUsageEvent(session_id=sess.id, app_name=e.app_name,
                            started_at=e.started_at, ended_at=e.ended_at,
                            was_locked=e.was_locked))
    await db.commit()
    return {"stored": len(body.events)}


def _state_key(state: dict) -> tuple:
    """The parts of a state frame whose change must reach the agent."""
    return (state["locked"], state["reason"], state["remaining"],
            json.dumps(state["allowlist"], sort_keys=True), (state["student"] or {}).get("id"),
            tuple(state.get("browser_hosts") or ()))


@router.websocket("/ws")
async def pc_ws(
        websocket: WebSocket,
        token: Optional[str] = Query(default=None),
        db: AsyncSession = Depends(get_db),
):
    """Realtime channel for a lab-PC agent. Auth via ``?token=`` (PC token), like notifications_ws.

    On connect: ``{type:'state',...}``. Device sends ``{type:'hb', app}`` every ~30 s;
    server stores last_seen_at/last_app, answers ``{type:'pong'}`` and, if the recomputed
    state differs from the last one sent on this socket, a ``state`` frame. Server pushes
    ``state`` and ``message`` frames through pc_ws_manager."""
    claims = decode_pc_token(token) if token else None
    if claims is None:
        await websocket.close(code=4001)
        return
    sess = await db.get(PcSession, claims["ses"])
    if (sess is None or sess.signed_out_at is not None
            or sess.student_id != claims["stu"]
            or claims["sub"] != f"pc:{sess.device_id}"):
        await websocket.close(code=4001)
        return
    device = await db.get(PcDevice, sess.device_id)
    if device is None:
        await websocket.close(code=4001)
        return
    device_id = device.id
    ses_id = sess.id

    await pc_ws_manager.connect(device_id, websocket)
    try:
        # Race guard: a newer login may have closed this token's session between the
        # validation above and registering the socket. Never answer with another
        # student's state: compute for THIS socket's session, or close.
        sess = await db.get(PcSession, ses_id)
        if sess is None or sess.signed_out_at is not None:
            await websocket.close(code=4001)
            return
        state = await compute_state(db, device, sess)
        # compute_state may have inserted today's quota row; commit so this long-lived
        # session does not sit on an open (write-locking) transaction for the whole connection.
        await db.commit()
        last_sent = _state_key(state)
        await websocket.send_json({"type": "state", **state})
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except ValueError:
                continue
            if not isinstance(msg, dict) or msg.get("type") != "hb":
                continue
            # Re-check on every heartbeat that this token's session is still open
            # (logout / a newer login on the device ends it), as GET /pc/state does.
            signed_out = (await db.execute(
                select(PcSession.signed_out_at, PcSession.id).where(PcSession.id == ses_id)
            )).first()
            await db.rollback()  # end the read txn; also drops any stale identity-map state
            if signed_out is None or signed_out[0] is not None:
                await websocket.close(code=4001)
                break
            app_name = msg.get("app")
            device = await db.get(PcDevice, device_id)
            if device is None:
                await websocket.close(code=4001)
                break
            device.last_seen_at = datetime.now(timezone.utc)
            device.last_app = app_name[:255] if isinstance(app_name, str) and app_name else None
            sess = await db.get(PcSession, ses_id)
            # Heartbeat doubles as the periodic refresh: quota met, midnight rollover, config
            # changes are never pushed, so recompute and send a state frame if it moved.
            state = await compute_state(db, device, sess)
            await db.commit()  # also persists any quota row compute_state inserted
            await websocket.send_json({"type": "pong"})
            key = _state_key(state)
            if key != last_sent:
                last_sent = key
                await websocket.send_json({"type": "state", **state})
    except WebSocketDisconnect:
        pass
    except Exception as e:  # noqa: BLE001 — never let a socket error bubble out
        logger.warning("pc ws closed on error (device=%s): %s", device_id, e, exc_info=True)
    finally:
        pc_ws_manager.disconnect(device_id, websocket)
