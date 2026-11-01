"""Teacher endpoints for PC Guard (lab PC control)."""
from datetime import date, datetime, timedelta, timezone
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_teacher
from app.models.group import Group
from app.models.pc_control import PcCommand, PcDevice, PcSession
from app.models.user import Student
from app.services import pc_allowlist_service, pc_push_service, pc_report_service
from app.services.pc_lock_service import compute_state
from app.services.teacher_students import teacher_student_ids_subquery
from app.ws.manager import pc_ws_manager

router = APIRouter()


async def _require_own_group(db: AsyncSession, group_id: int, teacher: Student) -> Group:
    """404 for an unknown group, 403 when it is not one of the calling teacher's groups."""
    group = await db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="Bu guruh sizga tegishli emas")
    return group


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
    if group_id is not None:
        await _require_own_group(db, group_id, teacher)
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
    if group_id is not None:
        await _require_own_group(db, group_id, teacher)
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
    # Lab PCs are shared hardware, so every device is listed; a signed-in student's
    # identity is shown only to a teacher who teaches that student.
    in_scope = set((await db.execute(
        select(teacher_student_ids_subquery(teacher.id).c.student_id))).scalars().all())
    now = datetime.now(timezone.utc)
    out = []
    for d in devices:
        # Per-device compute_state: one query batch per device; fine at lab scale (a few dozen).
        state = await compute_state(db, d)
        seen = _aware(d.last_seen_at)
        student = state["student"]
        if student is not None and student["id"] not in in_scope:
            student = {"id": None, "full_name": None}
        out.append({
            "id": d.id,
            "hostname": d.hostname,
            "group_id": d.group_id,
            "online": seen is not None and now - seen <= ONLINE_WINDOW,
            "student": student,
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
    if "group_id" in body.model_fields_set:  # absent = no change; explicit null clears
        if body.group_id is not None:
            await _require_own_group(db, body.group_id, teacher)
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
        if body.scope_type == "group":
            await _require_own_group(db, body.scope_id, teacher)
        elif await db.get(PcDevice, body.scope_id) is None:
            raise HTTPException(status_code=404, detail="Device not found")

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


MAX_REPORT_DAYS = 31


@router.get("/report")
async def report(
    date_from: date = Query(alias="from"),
    date_to: date = Query(alias="to"),
    group_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    if date_to < date_from:
        raise HTTPException(status_code=422, detail="'to' must not be before 'from'")
    if (date_to - date_from).days + 1 > MAX_REPORT_DAYS:
        raise HTTPException(status_code=422, detail=f"Range is limited to {MAX_REPORT_DAYS} days")
    if group_id is not None:
        owns = (await db.execute(select(Group.id).where(
            Group.id == group_id, Group.teacher_id == teacher.id))).first()
        if owns is None:  # unknown and foreign groups look the same here
            raise HTTPException(status_code=403, detail="Bu guruh sizga tegishli emas")
    return await pc_report_service.build_report(db, date_from, date_to, group_id, teacher.id)
