"""Per-technology skill levels, from the courses a student actually finished.

The old signal (`Student.current_level`) is points-based: someone with 20 000 points who
never opened the React course is "Advanced" and was still handed React work. A level here
means "how much of the best matching course did they complete" — see level_for.
"""
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.lesson import Lesson, LessonCompletion
from app.models.project import Project
from app.services.team_project_constants import AREA_COURSE_PATTERNS, SKILL_AREAS

INTERMEDIATE_FROM = 0.3
ADVANCED_FROM = 0.8
VERIFIED_PROJECT_POINTS = 75


@dataclass(frozen=True)
class AreaSkill:
    level: str
    ratio: float = 0.0

    @property
    def has(self) -> bool:
        return self.level != "Beginner"


def level_for(ratio: float, has_verified_project: bool) -> str:
    """Advanced needs BOTH most of a course and one approved project — finishing lessons
    alone is not enough to be trusted with the hardest part of a team project."""
    if ratio >= ADVANCED_FROM and has_verified_project:
        return "Advanced"
    if ratio >= INTERMEDIATE_FROM:
        return "Intermediate"
    return "Beginner"


async def build_skill_levels(db: AsyncSession, student_ids: List[int]) -> Dict[int, Dict[str, AreaSkill]]:
    """{student_id: {area: AreaSkill}} for every area in SKILL_AREAS (Beginner when unseen).
    Three grouped queries regardless of how many students."""
    if not student_ids:
        return {}

    courses = (await db.execute(select(Course.id, Course.title))).all()
    area_courses: Dict[str, List[int]] = {
        area: [cid for cid, title in courses if AREA_COURSE_PATTERNS[area].search(title or "")]
        for area in SKILL_AREAS
    }
    lesson_totals = dict((await db.execute(
        select(Lesson.course_id, func.count(Lesson.id)).where(Lesson.is_active == True).group_by(Lesson.course_id)  # noqa: E712
    )).all())
    done: Dict[int, Dict[int, int]] = defaultdict(dict)
    for sid, cid, n in (await db.execute(
        select(LessonCompletion.student_id, Lesson.course_id, func.count(LessonCompletion.id))
        .join(Lesson, Lesson.id == LessonCompletion.lesson_id)
        .where(LessonCompletion.student_id.in_(student_ids), Lesson.is_active == True)  # noqa: E712
        .group_by(LessonCompletion.student_id, Lesson.course_id)
    )).all():
        done[sid][cid] = n
    verified = set((await db.execute(
        select(Project.student_id).where(
            Project.student_id.in_(student_ids), Project.status == "Approved",
            Project.points_earned >= VERIFIED_PROJECT_POINTS,
        ).distinct()
    )).scalars().all())

    out: Dict[int, Dict[str, AreaSkill]] = {}
    for sid in student_ids:
        skills = {}
        for area in SKILL_AREAS:
            best = 0.0
            for cid in area_courses[area]:
                total = lesson_totals.get(cid, 0)
                if total:
                    best = max(best, done[sid].get(cid, 0) / total)
            skills[area] = AreaSkill(level_for(best, sid in verified), round(best, 3))
        out[sid] = skills
    return out
