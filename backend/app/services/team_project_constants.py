"""Curated pools for random team-project theme/tech-stack assignment.

Static Python data, not DB tables — teachers aren't asking to edit this
list yet (see team_project_service.py for how these get sampled per team).
"""

THEMES = [
    {"key": "crm", "label": "CRM tizimi", "label_ru": "Система CRM"},
    {"key": "dashboard", "label": "Admin dashboard", "label_ru": "Админ-панель"},
    {"key": "task_tracker", "label": "Vazifalarni boshqarish tizimi", "label_ru": "Трекер задач"},
    {"key": "online_shop", "label": "Onlayn do'kon", "label_ru": "Интернет-магазин"},
    {"key": "social_feed", "label": "Ijtimoiy tarmoq lentasi", "label_ru": "Лента соцсети"},
    {"key": "booking", "label": "Bandlash tizimi", "label_ru": "Система бронирования"},
    {"key": "blog", "label": "Blog platformasi", "label_ru": "Блог-платформа"},
    {"key": "survey", "label": "So'rovnoma tizimi", "label_ru": "Система опросов"},
    {"key": "quiz", "label": "Test (viktorina) platformasi", "label_ru": "Платформа тестов (викторин)"},
    {"key": "library", "label": "Kutubxona tizimi", "label_ru": "Система библиотеки"},
    {"key": "finance", "label": "Shaxsiy moliya hisobi", "label_ru": "Учёт личных финансов"},
    {"key": "bot_panel", "label": "Telegram bot boshqaruv paneli", "label_ru": "Панель управления Telegram-ботом"},
    {"key": "recipes", "label": "Retsept kitobi", "label_ru": "Книга рецептов"},
    {"key": "events", "label": "Tadbirlar va ro'yxatdan o'tish", "label_ru": "События и регистрация"},
    {"key": "jobs", "label": "Vakansiyalar taxtasi", "label_ru": "Доска вакансий"},
    {"key": "attendance", "label": "Davomat tizimi", "label_ru": "Система посещаемости"},
    {"key": "habits", "label": "Odatlar kuzatuvchisi", "label_ru": "Трекер привычек"},
    {"key": "classifieds", "label": "E'lonlar taxtasi", "label_ru": "Доска объявлений"},
]

# `needs`: a regex over a member's skill summary (course titles, lesson
# languages, project technologies). A stack with a frontend framework is only
# offered to a team where at least half of the members have seen that
# framework — nobody on this platform learns React/Vue/Next.js by default, so a
# random pick used to hand teams a framework none of them had studied. "vanilla"
# needs nothing, so every team always has at least one eligible stack.
TECH_STACKS = [
    {"key": "react", "label": "React", "frontend": "React", "backend": "FastAPI", "needs": r"\breact\b",
     "requires": {"frontend": "react", "backend": ["python", "flask"]}},
    {"key": "vue", "label": "Vue", "frontend": "Vue", "backend": "Flask", "needs": r"\bvue\b",
     "requires": {"frontend": "vue", "backend": ["python", "flask"]}},   # no Vue area/course exists: never fits
    {"key": "next", "label": "Next.js", "frontend": "Next.js", "backend": "Django", "needs": r"\b(?:next\.?js|react)\b",
     "requires": {"frontend": "react", "backend": ["python"]}},
    {"key": "express", "label": "Node/Express", "frontend": "React", "backend": "Node/Express", "needs": r"\breact\b",
     "requires": {"frontend": "react", "backend": ["node"]}},
    {"key": "vanilla", "label": "Vanilla JS", "frontend": "Vanilla JS", "backend": "Flask", "needs": None,
     "requires": {"frontend": "javascript", "backend": ["flask", "python"]}},
]

# ── skill areas (see team_project_skills.py) ───────────────────────────────
# A student's level in an area comes from how much of the matching COURSES they
# finished — not from the points-based `current_level`, which says nothing about
# whether they have ever seen React or Flask. Courses are matched by TITLE so the
# map survives course ids changing between environments.
import re as _re

SKILL_AREAS = ("html_css", "javascript", "python", "flask", "node", "react", "sql")
AREA_COURSE_PATTERNS = {
    "html_css": _re.compile(r"\b(html|css)\b", _re.I),
    "javascript": _re.compile(r"\b(javascript|js)\b", _re.I),
    "python": _re.compile(r"\bpython\b", _re.I),
    "flask": _re.compile(r"\bflask\b", _re.I),
    "node": _re.compile(r"\b(node|express)", _re.I),
    "react": _re.compile(r"\breact\b", _re.I),
    "sql": _re.compile(r"\b(sql|postgres\w*)\b", _re.I),
}

THEMES_BY_KEY = {t["key"]: t for t in THEMES}
TECH_STACKS_BY_KEY = {s["key"]: s for s in TECH_STACKS}

# Shared between team_project_service.py (lead picking) and
# team_project_planner.py (plan validation) — both need to compare
# StudentLevel values by seniority, not by string equality.
LEVEL_RANK = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}
