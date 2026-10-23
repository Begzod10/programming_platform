"""Teacher endpoints for PC Guard (lab PC control)."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_teacher
from app.models.group import Group
from app.models.user import Student
from app.services import pc_allowlist_service, pc_push_service

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
