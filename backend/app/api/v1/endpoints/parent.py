import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.dependencies import get_db
from app.models.user import Student

logger = logging.getLogger(__name__)
router = APIRouter()

GENNIS_BOT_BASE = f"{settings.GENNIS_API_URL}/bot"


async def _get_children(parent_gennis_id: int, client: httpx.AsyncClient) -> list[dict]:
    url = f"{GENNIS_BOT_BASE}/parents/students/{parent_gennis_id}"
    try:
        resp = await client.get(url)
        if resp.status_code == 200:
            return resp.json().get("children", [])
    except Exception as e:
        logger.error("Gennis children fetch failed for parent %s: %s", parent_gennis_id, e)
    return []


async def _load_student(db: AsyncSession, gennis_id: int) -> Optional[Student]:
    stmt = (
        select(Student)
        .where(
            (Student.gennis_id == gennis_id) |
            (Student.username == f"gennis_{gennis_id}")
        )
        .options(
            selectinload(Student.enrolled_courses),
            selectinload(Student.certificates),
            selectinload(Student.groups),
        )
    )
    row = await db.execute(stmt)
    return row.scalar_one_or_none()


@router.get("/progress/{parent_gennis_id}")
async def get_parent_progress(
    parent_gennis_id: int,
    db: AsyncSession = Depends(get_db),
):
    async with httpx.AsyncClient(timeout=10.0) as client:
        children = await _get_children(parent_gennis_id, client)

    if not children:
        return {"children": []}

    result = []
    for child in children:
        child_gennis_id = child.get("id")
        child_name = f"{child.get('name', '')} {child.get('surname', '')}".strip()

        student = await _load_student(db, child_gennis_id)

        if student:
            completed_course_ids = {c.course_id for c in student.certificates}
            active = [
                {"title": c.title}
                for c in student.enrolled_courses
                if c.id not in completed_course_ids
            ]
            completed = [
                {"title": c.title}
                for c in student.enrolled_courses
                if c.id in completed_course_ids
            ]
            gennis_group = next(
                (g.name for g in student.groups if g.gennis_id is not None),
                child.get("group_name", ""),
            )
            result.append({
                "name": student.full_name or child_name,
                "level": student.current_level.value,
                "points": student.total_points,
                "streak": student.current_streak,
                "active_courses": active,
                "completed_courses": completed,
                "gennis_group": gennis_group,
            })
        else:
            result.append({
                "name": child_name,
                "level": "Beginner",
                "points": 0,
                "streak": 0,
                "active_courses": [],
                "completed_courses": [],
                "gennis_group": child.get("group_name", ""),
            })

    return {"children": result}


@router.get("/payments/{parent_gennis_id}")
async def get_parent_payments(parent_gennis_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        children = await _get_children(parent_gennis_id, client)

        if not children:
            return {"children": []}

        result = []
        for child in children:
            child_id = child.get("id")
            child_name = f"{child.get('name', '')} {child.get('surname', '')}".strip()
            payments: list[dict] = []

            try:
                resp = await client.get(
                    f"{GENNIS_BOT_BASE}/students/payments/{child_id}"
                )
                if resp.status_code == 200:
                    payments = resp.json().get("payments", [])
            except Exception as e:
                logger.warning("Payments fetch failed for child %s: %s", child_id, e)

            result.append({
                "name": child_name,
                "balance": child.get("balance", 0),
                "payments": payments,
            })

    return {"children": result}


@router.get("/attendance/{parent_gennis_id}")
async def get_parent_attendance(parent_gennis_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        children = await _get_children(parent_gennis_id, client)

        if not children:
            return {"children": []}

        result = []
        for child in children:
            child_id = child.get("id")
            child_name = f"{child.get('name', '')} {child.get('surname', '')}".strip()
            attendance: dict = {}

            try:
                dates_resp = await client.get(
                    f"{GENNIS_BOT_BASE}/students/attendance/dates/{child_id}"
                )
                if dates_resp.status_code == 200:
                    dates_data = dates_resp.json().get("data", {})
                    years = dates_data.get("years", [])
                    if years:
                        year = years[-1]
                        months = dates_data.get(year, [])
                        if months:
                            month = months[-1]
                            att_resp = await client.get(
                                f"{GENNIS_BOT_BASE}/students/attendances/{child_id}/{year}/{month}"
                            )
                            if att_resp.status_code == 200:
                                attendance = {
                                    "year": year,
                                    "month": month,
                                    "tables": att_resp.json().get("attendances", []),
                                }
            except Exception as e:
                logger.warning("Attendance fetch failed for child %s: %s", child_id, e)

            result.append({"name": child_name, "attendance": attendance})

    return {"children": result}
