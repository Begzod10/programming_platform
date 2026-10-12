"""Skill levels come from finished courses, not from points."""
import uuid

import pytest
from sqlalchemy import select

from app.models.course import Course
from app.models.lesson import Lesson, LessonCompletion
from app.models.project import Project
from app.services.team_project_skills import AreaSkill, build_skill_levels, level_for


@pytest.mark.parametrize("ratio,verified,expected", [
    (0.0, False, "Beginner"), (0.29, True, "Beginner"),
    (0.3, False, "Intermediate"), (0.79, True, "Intermediate"),
    (0.8, True, "Advanced"), (1.0, True, "Advanced"),
    (0.8, False, "Intermediate"),            # no approved project -> not Advanced
])
def test_level_for_thresholds(ratio, verified, expected):
    assert level_for(ratio, verified) == expected


def test_has_means_not_beginner():
    assert AreaSkill("Beginner", 0).has is False
    assert AreaSkill("Intermediate", 0.5).has is True
    assert AreaSkill("Advanced", 1).has is True


async def _student(async_client):
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post("/api/v1/auth/register", json={
        "username": f"sk_{uid}", "email": f"sk_{uid}@example.com", "password": "pass12345"})
    assert reg.status_code == 201
    return reg.json()["user"]["id"]


async def _course(db, title, n_lessons, instructor_id):
    c = Course(title=title, description="d", instructor_id=instructor_id, difficulty_level="Beginner",
               duration_weeks=1, max_points=10, is_active=True, is_published=True)
    db.add(c)
    await db.flush()
    lessons = [Lesson(course_id=c.id, title=f"L{i}", order=i, is_active=True, is_published=True) for i in range(n_lessons)]
    db.add_all(lessons)
    await db.flush()
    return c, lessons


async def test_levels_from_finished_courses_and_a_verified_project(async_client, db_session):
    sid = await _student(async_client)
    u = uuid.uuid4().hex[:6]
    _html, html_lessons = await _course(db_session, f"HTML CSS {u}", 4, sid)
    _js, js_lessons = await _course(db_session, f"Javascript {u}", 6, sid)
    _misc, _ = await _course(db_session, f"Dizayn asoslari {u}", 3, sid)       # matches no area
    _empty, _ = await _course(db_session, f"React {u}", 0, sid)                 # 0 lessons: no division by zero
    for l in html_lessons:
        db_session.add(LessonCompletion(student_id=sid, lesson_id=l.id))
    for l in js_lessons[:2]:                                                    # 2/6 = 0.33
        db_session.add(LessonCompletion(student_id=sid, lesson_id=l.id))
    db_session.add(Project(student_id=sid, title="p", description="d", difficulty_level="Beginner",
                           status="Approved", points_earned=80))
    await db_session.commit()

    skills = (await build_skill_levels(db_session, [sid]))[sid]
    assert skills["html_css"].level == "Advanced" and skills["html_css"].ratio == 1.0
    assert skills["javascript"].level == "Intermediate"
    assert skills["react"].level == "Beginner" and skills["flask"].level == "Beginner"
    assert set(skills) == {"html_css", "javascript", "python", "flask", "node", "react", "sql"}


async def test_empty_input_and_unknown_student_are_safe(async_client, db_session):
    assert await build_skill_levels(db_session, []) == {}
    sid = await _student(async_client)
    skills = (await build_skill_levels(db_session, [sid]))[sid]
    assert all(s.level == "Beginner" for s in skills.values())
