import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.dependencies import get_db
from app.models.user import Student
from app.models.student_achievement import StudentAchievement

logger = logging.getLogger(__name__)
router = APIRouter()

GENNIS_BOT_BASE = f"{settings.GENNIS_API_URL}/bot"


async def _get_children_from_gennis(parent_gennis_id: int, client: httpx.AsyncClient) -> list[dict]:
    url = f"{GENNIS_BOT_BASE}/parents/students/{parent_gennis_id}"
    try:
        resp = await client.get(url)
        if resp.status_code == 200:
            return resp.json().get("children", [])
    except Exception as e:
        logger.error("Gennis children fetch failed for parent %s: %s", parent_gennis_id, e)
    return []


async def _resolve_children(
    parent_gennis_id: int,
    children_param: Optional[str],
    client: httpx.AsyncClient,
) -> list[dict]:
    """
    Returns children list. Uses URL-provided IDs when available (avoids Gennis API call).
    Falls back to Gennis API if not provided.
    """
    if children_param:
        ids = [i.strip() for i in children_param.split(",") if i.strip().isdigit()]
        return [{"id": int(i)} for i in ids]
    return await _get_children_from_gennis(parent_gennis_id, client)


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
            selectinload(Student.projects),
            selectinload(Student.student_achievements).selectinload(StudentAchievement.achievement),
            selectinload(Student.ranking),
        )
    )
    row = await db.execute(stmt)
    return row.scalar_one_or_none()


def _build_child_progress(student: Student, child: dict) -> dict:
    child_name = f"{child.get('name', '')} {child.get('surname', '')}".strip()
    if not child_name:
        child_name = student.full_name or "—"

    cert_course_ids = {c.course_id for c in student.certificates}
    active_courses = [
        {"title": c.title}
        for c in student.enrolled_courses
        if c.id not in cert_course_ids
    ]
    completed_courses = [
        {"title": c.title}
        for c in student.enrolled_courses
        if c.id in cert_course_ids
    ]
    gennis_group = next(
        (g.name for g in student.groups if g.gennis_id is not None),
        child.get("group_name", ""),
    )

    # Projects
    projects = [
        {
            "title": p.title,
            "status": p.status,
            "grade": p.grade,
        }
        for p in student.projects
    ]
    graded = [p for p in student.projects if p.grade]
    avg_grade = (
        round(sum(int(p.grade) for p in graded if p.grade and p.grade.isdigit()) / len(graded), 1)
        if graded else None
    )

    # Achievements
    achievements = []
    for sa in student.student_achievements:
        if sa.achievement:
            achievements.append({"name": sa.achievement.name})

    # Ranking
    ranking = None
    if student.ranking:
        r = student.ranking
        ranking = {
            "global_rank": r.global_rank,
            "weekly_points": r.weekly_points,
            "monthly_points": r.monthly_points,
            "projects_completed": r.projects_completed,
            "average_grade": r.average_grade,
        }

    return {
        "name": student.full_name or child_name,
        "gennis_id": student.gennis_id,
        "level": student.current_level.value,
        "points": student.total_points,
        "streak": student.current_streak,
        "longest_streak": student.longest_streak,
        "gennis_group": gennis_group,
        "active_courses": active_courses,
        "completed_courses": completed_courses,
        "projects": projects,
        "projects_count": len(projects),
        "avg_grade": avg_grade,
        "achievements": achievements,
        "achievements_count": len(achievements),
        "certificates_count": len(student.certificates),
        "ranking": ranking,
        "found_in_platform": True,
    }


@router.get("/progress/{parent_gennis_id}")
async def get_parent_progress(
    parent_gennis_id: int,
    children: Optional[str] = Query(None, description="Comma-separated child Gennis IDs"),
    db: AsyncSession = Depends(get_db),
):
    async with httpx.AsyncClient(timeout=10.0) as client:
        raw_children = await _resolve_children(parent_gennis_id, children, client)

    if not raw_children:
        return {"children": []}

    result = []
    for child in raw_children:
        child_gennis_id = child.get("id")
        if not child_gennis_id:
            continue

        student = await _load_student(db, child_gennis_id)
        if student:
            result.append(_build_child_progress(student, child))
        else:
            child_name = f"{child.get('name', '')} {child.get('surname', '')}".strip()
            result.append({
                "name": child_name or f"O'quvchi #{child_gennis_id}",
                "gennis_id": child_gennis_id,
                "level": "Beginner",
                "points": 0,
                "streak": 0,
                "longest_streak": 0,
                "gennis_group": child.get("group_name", ""),
                "active_courses": [],
                "completed_courses": [],
                "projects": [],
                "projects_count": 0,
                "avg_grade": None,
                "achievements": [],
                "achievements_count": 0,
                "certificates_count": 0,
                "ranking": None,
                "found_in_platform": False,
            })

    return {"children": result}


@router.get("/payments/{parent_gennis_id}")
async def get_parent_payments(
    parent_gennis_id: int,
    children: Optional[str] = Query(None),
):
    async with httpx.AsyncClient(timeout=10.0) as client:
        raw_children = await _resolve_children(parent_gennis_id, children, client)

        if not raw_children:
            return {"children": []}

        result = []
        for child in raw_children:
            child_id = child.get("id")
            child_name = f"{child.get('name', '')} {child.get('surname', '')}".strip()
            payments: list[dict] = []

            try:
                resp = await client.get(f"{GENNIS_BOT_BASE}/students/payments/{child_id}")
                if resp.status_code == 200:
                    payments = resp.json().get("payments", [])
            except Exception as e:
                logger.warning("Payments fetch failed for child %s: %s", child_id, e)

            result.append({
                "name": child_name or f"O'quvchi #{child_id}",
                "balance": child.get("balance", 0),
                "payments": payments,
            })

    return {"children": result}


@router.get("/attendance/{parent_gennis_id}")
async def get_parent_attendance(
    parent_gennis_id: int,
    children: Optional[str] = Query(None),
):
    async with httpx.AsyncClient(timeout=10.0) as client:
        raw_children = await _resolve_children(parent_gennis_id, children, client)

        if not raw_children:
            return {"children": []}

        result = []
        for child in raw_children:
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

            result.append({
                "name": child_name or f"O'quvchi #{child_id}",
                "attendance": attendance,
            })

    return {"children": result}
