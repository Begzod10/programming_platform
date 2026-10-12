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


# ── lesson-level requirements (blueprint `requires`) ────────────────────────

import re  # noqa: E402  (kept next to its only users below)

_PATTERNS: dict[str, "re.Pattern"] = {}


def _rx(pattern: str) -> "re.Pattern":
    if pattern not in _PATTERNS:
        _PATTERNS[pattern] = re.compile(pattern, re.I)
    return _PATTERNS[pattern]


async def completed_lessons_by_student(db: AsyncSession, student_ids: List[int]) -> Dict[int, List[tuple]]:
    """{student_id: [(course title, lesson title), ...]} of every lesson they finished."""
    if not student_ids:
        return {}
    out: Dict[int, List[tuple]] = defaultdict(list)
    for sid, course_title, lesson_title in (await db.execute(
        select(LessonCompletion.student_id, Course.title, Lesson.title)
        .join(Lesson, Lesson.id == LessonCompletion.lesson_id)
        .join(Course, Course.id == Lesson.course_id)
        .where(LessonCompletion.student_id.in_(student_ids))
    )).all():
        out[sid].append((course_title or "", lesson_title or ""))
    return out


def need_met(completed: List[tuple], need: dict) -> bool:
    course, lesson = _rx(need["course"]), _rx(need["lesson"])
    return any(course.search(ct) and lesson.search(lt) for ct, lt in completed)


def unmet_needs(requires: dict, member_completed: List[List[tuple]]) -> List[str]:
    """Labels of the needs the team does not cover: a frontend need must be met by at least half of
    the members, a backend need by at least one."""
    unmet: List[str] = []
    size = len(member_completed)
    for need in requires.get("frontend", []):
        met = sum(1 for c in member_completed if need_met(c, need))
        if met == 0 or met * 2 < size:
            unmet.append(need["label"])
    for need in requires.get("backend", []):
        if not any(need_met(c, need) for c in member_completed):
            unmet.append(need["label"])
    return unmet
