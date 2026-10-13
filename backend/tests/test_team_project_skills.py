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
    _html, html_lessons = await _course(db_session, "HTML CSS", 4, sid)
    _js, js_lessons = await _course(db_session, "Javascript", 6, sid)
    _misc, _ = await _course(db_session, f"Dizayn asoslari {u}", 3, sid)       # matches no area
    _empty, _ = await _course(db_session, "React Asoslari", 0, sid)                 # 0 lessons: no division by zero
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
    from app.services.team_project_constants import SKILL_AREAS
    assert set(skills) == set(SKILL_AREAS) and "django" in skills and "telegram" in skills


async def test_empty_input_and_unknown_student_are_safe(async_client, db_session):
    assert await build_skill_levels(db_session, []) == {}
    sid = await _student(async_client)
    skills = (await build_skill_levels(db_session, [sid]))[sid]
    assert all(s.level == "Beginner" for s in skills.values())


# ── the explicit course -> area map ─────────────────────────────────────────

from app.services.team_project_constants import AREA_COURSES, SKILL_AREAS, course_in_area

# All 66 active course titles on production (2026-10-13, incl. the 4 new API courses). Every mapped title must exist here, so a
# typo or a renamed course cannot silently drop students out of an area.
PRODUCTION_TITLES = {
    "HTML CSS", "Python Flask", "Javascript", "Python Flask — O'rta daraja", "Python Asoslari", "Dasturlash dunyosiga kirish",
    "Python: Keyingi Bosqich", "JavaScript: Keyingi Bosqich", "SQL va PostgreSQL Asoslari", "React Asoslari", "Git va GitHub",
    "Telegram Bot aiogram", "JavaScript Mini-Projects", "HTML/CSS Mini-Projects", "HTML/CSS: Keyingi Bosqich",
    "HTML/CSS: Professional Bosqich", "HTML/CSS: Real Loyihalar", "SASS/SCSS Asoslari", "Bootstrap 5 Asoslari",
    "Veb Accessibility (a11y)", "Tailwind CSS Asoslari", "HTML/CSS: Intervyu Tayyorgarligi", "JavaScript: Ilg'or Mavzular",
    "JavaScript: Brauzer API va Web", "JavaScript: Algoritmlar va Ma'lumotlar Tuzilmasi", "JavaScript: Testlash",
    "React: Redux Toolkit, TypeScript va Testlash", "Node.js/Express Asoslari", "Python: Testlash",
    "Python: Algoritmlar va Ma'lumotlar Tuzilmasi", "TypeScript Asoslari", "Python: Django Asoslari", "Python: Ilg'or Mavzular",
    "Capstone: To'liq Stack Loyiha", "Capstone 2: Django + React + Telegram Bot", "Capstone 3: Flask + JavaScript + Telegram Bot",
    "Capstone 4: TypeScript Full-Stack", "Capstone 5: Testlash va Algoritmlar", "Capstone 6: Accessibility va Brauzer API",
    "SQL: Ma'lumotlar Bazasi Dizayni", "SQL: Ilg'or So'rovlar va Performance", "SQL + Python ORM va Migratsiyalar",
    "Git: Ichki Tuzilishi va Ilg'or Workflow", "GitHub Actions va CI/CD Chuqur",
    "Jamoaviy Ish Madaniyati: Code Review va Versiyalash", "Telegram Bot: Ilg'or Mavzular",
    "Telethon: Telegram Userbot va MTProto", "Pyrogram: Zamonaviy Telegram Client Kutubxonasi", "AI API'larni Loyihalarga Ulash",
    "RAG va Vektor Qidiruv: Hujjatlar Asosida AI", "React: Next.js va Server-Side Rendering", "React: Performance va Optimizatsiya",
    "Scratch bilan dasturlash (bolalar uchun)", "Python turtle bilan chizamiz (bolalar uchun)",
    "HTML bilan birinchi vebsahifa (bolalar uchun)", "Scratch 2: O'yin yaratish (bolalar uchun)",
    "CSS bilan sahifani bezash (bolalar uchun)", "Python bilan o'yinlar (bolalar uchun)",
    "JavaScript bilan interaktivlik (bolalar uchun)", "Scratch 3: Ilg'or Scratch (bolalar uchun)",
    "Raqamli xavfsizlik va internet odobi (bolalar uchun)", "Kompyuter qanday ishlaydi (bolalar uchun)",
    "Flask: Token autentifikatsiya va CORS (API)", "Django: JSON API (DRF asoslari)",
    "Express: API testlash (Jest va supertest)", "FastAPI Asoslari",
}


def test_every_mapped_title_is_a_real_course():
    mapped = {t for titles in AREA_COURSES.values() for t in titles}
    assert mapped <= PRODUCTION_TITLES, mapped - PRODUCTION_TITLES
    assert set(AREA_COURSES) == set(SKILL_AREAS)


def test_kids_courses_and_mixed_capstones_map_to_no_area():
    for title in PRODUCTION_TITLES:
        if "bolalar uchun" in title or title in {"Capstone: To'liq Stack Loyiha", "Capstone 5: Testlash va Algoritmlar",
                                                  "Capstone 6: Accessibility va Brauzer API", "Veb Accessibility (a11y)",
                                                  "Dasturlash dunyosiga kirish"}:
            assert not any(course_in_area(title, a) for a in SKILL_AREAS), title


def test_the_old_regex_mistakes_are_gone():
    assert not course_in_area("React: Next.js va Server-Side Rendering", "javascript")      # "Next.js" matched "js"
    assert course_in_area("React: Next.js va Server-Side Rendering", "react")
    assert course_in_area("Tailwind CSS Asoslari", "css_frameworks") and not course_in_area("Tailwind CSS Asoslari", "html_css")
    assert course_in_area("Python: Django Asoslari", "django") and course_in_area("Python: Django Asoslari", "python")
    assert not course_in_area("Capstone 2: Django + React + Telegram Bot", "react")
    assert course_in_area("Telegram Bot aiogram", "telegram") and course_in_area("Git va GitHub", "git")
    assert course_in_area("Node.js/Express Asoslari", "node") and not course_in_area("Node.js/Express Asoslari", "javascript")


def test_title_matching_is_case_and_apostrophe_insensitive():
    assert course_in_area("python flask — o’rta daraja", "flask")
    assert not course_in_area("", "flask") and not course_in_area("Python Flask", "no_such_area")


def test_the_new_api_courses_are_mapped_to_their_areas():
    assert course_in_area("Flask: Token autentifikatsiya va CORS (API)", "flask")
    assert course_in_area("Flask: Token autentifikatsiya va CORS (API)", "python")
    assert course_in_area("Django: JSON API (DRF asoslari)", "django")
    assert course_in_area("Django: JSON API (DRF asoslari)", "python")
    assert course_in_area("Express: API testlash (Jest va supertest)", "node")
    assert not course_in_area("Express: API testlash (Jest va supertest)", "javascript")
    assert course_in_area("FastAPI Asoslari", "python") and course_in_area("FastAPI Asoslari", "fastapi")
    assert not course_in_area("FastAPI Asoslari", "flask") and not course_in_area("FastAPI Asoslari", "django")
