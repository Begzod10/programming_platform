"""Blueprints carry the lessons a team must have studied; theme choice puts readiness first."""
import random
import uuid

import pytest

from app.models.course import Course
from app.models.lesson import Lesson, LessonCompletion
from app.services.team_project_blueprints import get_blueprint, lesson_needs
from app.services.team_project_constants import THEMES
from app.services.team_project_service import choose_themes_for_teams
from app.services.team_project_skills import completed_lessons_by_student, need_met, unmet_needs

# Real course/lesson titles (copied from production, 2026-10-12) — the need regexes are checked against them
# so a typo cannot silently make a project impossible to prepare for.
CATALOG = {
    "Javascript": ["Javascript asoslari", "5-Dars: Massivlar (Arrays) — Ma'lumotlar", "7-Dars: Obyektlar (Objects)",
                   "8-Dars: DOM bilan ishlash", "9-Dars: HTML elementlarini dinamik yaratish", "10-Dars: LocalStorage"],
    "JavaScript: Keyingi Bosqich": ["2-Massiv iteratorlari (map, filter, reduce)", "8-async/await", "9-fetch va REST API"],
    "HTML CSS": ["6-dars Div tegi", "7-dars Display Flex", "8-dars Table"],
    "Python Flask": ["2-Routing va URL", "7-Database (SQLAlchemy)", "8-CRUD operatsiyalar", "10-JSON API"],
    "Python Flask — O'rta daraja": ["4-Modellar orasidagi munosabatlar", "5-So'rovlar, filterlar, sahifalash",
                                    "7-Parol hashing (werkzeug.security)"],
    "Python: Django Asoslari": ["2-URL routing va views", "4-Models va ORM asoslari", "7-ORM chuqurroq: querysets va bog'lanishlar",
                                "8-Autentifikatsiya"],
    "Node.js/Express Asoslari": ["2-Routing va middleware", "5-PostgreSQL ulanish (pg)", "6-CRUD operatsiyalar",
                                 "8-JWT autentifikatsiya", "10-CORS va React bilan ulash"],
    # the new API courses (published 2026-10-13)
    "Flask: Token autentifikatsiya va CORS (API)": ["1-Token nima va nega kerak", "2-Flask-JWT-Extended: register va login",
                                                    "3-Himoyalangan route'lar va rollar", "4-CORS: frontend bilan ulash"],
    "Django: JSON API (DRF asoslari)": ["1-JsonResponse bilan oddiy API", "2-DRF: serializer va @api_view",
                                        "4-JWT autentifikatsiya va faqat o'z yozuvlari", "5-CORS, API testlari va Postman"],
}
OLD_CATALOG_ONLY = {c: ls for c, ls in CATALOG.items() if "Token" not in c and "JSON API (DRF" not in c}
EVERYTHING = [(c, l) for c, ls in CATALOG.items() for l in ls]
THEME_KEYS = [t["key"] for t in THEMES]


@pytest.mark.parametrize("theme", THEME_KEYS)
@pytest.mark.parametrize("family", ["flask", "express", "django"])
def test_every_need_matches_a_real_lesson(theme, family):
    needs = lesson_needs(theme, family)
    assert needs["frontend"] and needs["backend"]
    for part in ("frontend", "backend"):
        for need in needs[part]:
            assert need_met(EVERYTHING, need), f"{theme}/{family}: no lesson matches {need['label']}"
    assert unmet_needs(needs, [EVERYTHING]) == []


def test_blueprints_expose_their_requirements():
    bp = get_blueprint("crm", "vanilla")
    assert bp["requires"]["frontend"] and bp["requires"]["backend"]
    assert get_blueprint("crm", "express")["requires"]["backend"] != bp["requires"]["backend"]   # per family


def test_a_need_is_met_only_by_the_right_course_and_lesson():
    need = {"course": "javascript", "lesson": r"fetch va REST API", "label": "x"}
    assert need_met([("JavaScript: Keyingi Bosqich", "9-fetch va REST API")], need)
    assert not need_met([("Python Flask", "9-fetch va REST API")], need)           # right lesson, wrong course
    assert not need_met([("Javascript", "8-Dars: DOM bilan ishlash")], need)
    assert not need_met([], need)


def test_frontend_needs_need_half_the_team_backend_needs_one_member():
    needs = lesson_needs("task_tracker", "flask")
    js = [("Javascript", "8-Dars: DOM bilan ishlash"), ("JavaScript: Keyingi Bosqich", "9-fetch va REST API"),
          ("Javascript", "9-Dars: HTML elementlarini dinamik yaratish"),
          ("JavaScript: Keyingi Bosqich", "2-Massiv iteratorlari (map, filter, reduce)")]
    flask = [(c, l) for c, ls in CATALOG.items() if "Flask" in c for l in ls]
    team = [js, js + flask, [], []]                                               # 2 of 4 know the frontend, 1 the backend
    assert unmet_needs(needs, team) == []
    assert any("fetch" in m for m in unmet_needs(needs, [js[:1], [], [], []]))    # 1 of 4 is below half
    assert any("Flask" in m for m in unmet_needs(needs, [js, js, js, js]))        # nobody did the backend


def test_a_ready_theme_beats_an_unbuilt_but_unready_one():
    unmet = {"crm": 3, "booking": 0, "online_shop": 4, "dashboard": 5, "task_tracker": 2, "social_feed": 1}
    for seed in range(40):
        pick = choose_themes_for_teams([[1, 2]], {2: {"booking"}}, rng=random.Random(seed),
                                       unmet=lambda i, key: unmet.get(key, 9))[0]
        assert pick["key"] == "booking"       # readiness first — even though a member built it before


def test_among_equally_ready_themes_history_still_decides():
    for seed in range(40):
        pick = choose_themes_for_teams([[1]], {1: {"crm"}}, rng=random.Random(seed), unmet=lambda i, key: 0)[0]
        assert pick["key"] != "crm"


async def test_completed_lessons_by_student_returns_course_and_lesson_titles(async_client, db_session):
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post("/api/v1/auth/register", json={
        "username": f"ln_{uid}", "email": f"ln_{uid}@example.com", "password": "pass12345"})
    sid = reg.json()["user"]["id"]
    course = Course(title=f"Javascript {uid}", description="d", instructor_id=sid, difficulty_level="Beginner",
                    duration_weeks=1, max_points=10, is_active=True, is_published=True)
    db_session.add(course)
    await db_session.flush()
    done, todo = (Lesson(course_id=course.id, title=t, order=i, is_active=True, is_published=True)
                  for i, t in enumerate(["8-Dars: DOM bilan ishlash", "10-Dars: LocalStorage"]))
    db_session.add_all([done, todo])
    await db_session.flush()
    db_session.add(LessonCompletion(student_id=sid, lesson_id=done.id))
    await db_session.commit()

    got = await completed_lessons_by_student(db_session, [sid])
    assert got[sid] == [(f"Javascript {uid}", "8-Dars: DOM bilan ishlash")]
    assert await completed_lessons_by_student(db_session, []) == {}


def test_token_lessons_of_the_new_courses_are_required_for_flask_and_django_backends():
    old_lessons = [(c, l) for c, ls in OLD_CATALOG_ONLY.items() for l in ls]
    flask_gaps = unmet_needs(lesson_needs("task_tracker", "flask"), [old_lessons])
    assert "Flask: JWT bilan register va login" in flask_gaps and "Flask: himoyalangan route'lar va rollar" in flask_gaps
    django_gaps = unmet_needs(lesson_needs("task_tracker", "django"), [old_lessons])
    assert {"Django: JSON API (JsonResponse)", "Django: JWT autentifikatsiya", "Django: CORS (django-cors-headers)"} <= set(django_gaps)
    # the session-auth lessons of the old courses do not satisfy the token needs, and Express is unchanged
    assert not need_met([("Python Flask — O'rta daraja", "8-Flask-Login bilan autentifikatsiya")],
                        {"course": "flask", "lesson": r"register va login", "label": "x"})
    assert unmet_needs(lesson_needs("task_tracker", "express"), [old_lessons]) == []
