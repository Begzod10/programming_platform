"""Teacher endpoints for PC Guard (lab PC control)."""
from datetime import datetime, timedelta, timezone
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_teacher
from app.models.group import Group
from app.models.pc_control import PcCommand, PcDevice, PcSession
from app.models.user import Student
from app.services import pc_allowlist_service, pc_push_service
from app.services.pc_lock_service import compute_state
from app.ws.manager import pc_ws_manager

router = APIRouter()


class AllowlistEntry(BaseModel):
    exe: str
    publisher: Optional[str] = None


class AllowlistBody(BaseModel):
    entries: List[AllowlistEntry]


@router.get("/allowlist")
async def get_allowlist(
    group_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    """`entries` = the list stored for this scope; `effective` = global + group, merged."""
    return {
        "entries": await pc_allowlist_service.get_own_entries(db, group_id),
        "effective": await pc_allowlist_service.effective_allowlist(db, group_id),
    }


@router.put("/allowlist")
async def put_allowlist(
    body: AllowlistBody,
    group_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    if group_id is not None and await db.get(Group, group_id) is None:
        raise HTTPException(status_code=404, detail="Group not found")
    try:
        entries = await pc_allowlist_service.set_entries(
            db, group_id, [e.model_dump() for e in body.entries], teacher.id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    await pc_push_service.push_state_to_devices(db, group_id)
    return {
        "entries": entries,
        "effective": await pc_allowlist_service.effective_allowlist(db, group_id),
    }


ONLINE_WINDOW = timedelta(seconds=90)
MAX_MESSAGE_LEN = 500


def _aware(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@router.get("/devices")
async def list_devices(
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    devices = (await db.execute(select(PcDevice).order_by(PcDevice.id))).scalars().all()
    now = datetime.now(timezone.utc)
    out = []
    for d in devices:
        # Per-device compute_state: one query batch per device; fine at lab scale (a few dozen).
        state = await compute_state(db, d)
        seen = _aware(d.last_seen_at)
        out.append({
            "id": d.id,
            "hostname": d.hostname,
            "group_id": d.group_id,
            "online": seen is not None and now - seen <= ONLINE_WINDOW,
            "student": state["student"],
            "locked": state["locked"],
            "reason": state["reason"],
            "last_app": d.last_app,
            "last_seen_at": seen.isoformat() if seen else None,
        })
    await db.commit()  # compute_state may have created today's quota rows
    return out


class DevicePatch(BaseModel):
    group_id: Optional[int] = None


@router.patch("/devices/{device_id}")
async def patch_device(
    device_id: int,
    body: DevicePatch,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    device = await db.get(PcDevice, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    if body.group_id is not None and await db.get(Group, body.group_id) is None:
        raise HTTPException(status_code=404, detail="Group not found")
    device.group_id = body.group_id
    await db.commit()
    await pc_push_service.push_state_to_device(db, device_id)
    await db.commit()
    return {"id": device.id, "group_id": device.group_id}


class CommandIn(BaseModel):
    scope_type: Literal["device", "group", "all"]
    scope_id: Optional[int] = None
    type: Literal["lock", "unlock", "clear", "message"]
    payload: Optional[dict] = None


@router.post("/commands")
async def create_command(
    body: CommandIn,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    if body.scope_type == "all":
        if body.scope_id is not None:
            raise HTTPException(status_code=422, detail="scope_id must be null for scope 'all'")
    else:
        if body.scope_id is None:
            raise HTTPException(status_code=422, detail="scope_id is required")
        model = PcDevice if body.scope_type == "device" else Group
        if await db.get(model, body.scope_id) is None:
            raise HTTPException(status_code=404, detail=f"{body.scope_type.capitalize()} not found")

    payload = None
    if body.type == "message":
        text = (body.payload or {}).get("text")
        if not isinstance(text, str) or not text.strip():
            raise HTTPException(status_code=422, detail="payload.text is required")
        if len(text) > MAX_MESSAGE_LEN:
            raise HTTPException(status_code=422, detail=f"payload.text exceeds {MAX_MESSAGE_LEN} characters")
        payload = {"text": text}

    cmd = PcCommand(scope_type=body.scope_type, scope_id=body.scope_id, type=body.type,
                    payload=payload, created_by=teacher.id)
    db.add(cmd)
    await db.commit()
    await db.refresh(cmd)

    if body.type == "message":
        if body.scope_type == "device":
            device_ids = [body.scope_id]
        else:
            q = (select(PcSession.device_id)
                 .join(PcDevice, PcDevice.id == PcSession.device_id)
                 .where(PcSession.signed_out_at.is_(None)))
            if body.scope_type == "group":
                q = q.where(PcDevice.group_id == body.scope_id)
            device_ids = (await db.execute(q.distinct())).scalars().all()
        for did in device_ids:
            await pc_ws_manager.broadcast(did, {"type": "message", "text": payload["text"]})
    elif body.scope_type == "device":
        await pc_push_service.push_state_to_device(db, body.scope_id)
    else:
        await pc_push_service.push_state_to_devices(
            db, body.scope_id if body.scope_type == "group" else None)
    await db.commit()
    return {"id": cmd.id, "scope_type": cmd.scope_type, "scope_id": cmd.scope_id,
            "type": cmd.type, "payload": cmd.payload}
