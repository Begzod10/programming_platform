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
    {"key": "flashcards", "label": "So'z kartochkalari", "label_ru": "Карточки для слов"},
    {"key": "inventory", "label": "Ombor hisobi", "label_ru": "Складской учёт"},
    {"key": "tickets", "label": "Yordam so'rovlari tizimi", "label_ru": "Система заявок в поддержку"},
    {"key": "clinic_queue", "label": "Poliklinika navbati", "label_ru": "Очередь в поликлинику"},
    {"key": "tournament", "label": "Turnir jadvali", "label_ru": "Турнирная таблица"},
    {"key": "rental", "label": "Ijara tizimi", "label_ru": "Система аренды"},
]

# `needs`: a regex over a member's skill summary (course titles, lesson
# languages, project technologies). A stack with a frontend framework is only
# offered to a team where at least half of the members have seen that
# framework — nobody on this platform learns React/Vue/Next.js by default, so a
# random pick used to hand teams a framework none of them had studied. "vanilla"
# needs nothing, so every team always has at least one eligible stack.
TECH_STACKS = [
    # Every stack has a blueprint family (flask / express / django) and plain-JS pages — what is
    # written here is what a team is actually given. (React/Vue/Next/FastAPI stacks were removed: no
    # blueprint exists for them; FastAPI is back since "FastAPI Asoslari" and its blueprint family exist.)
    {"key": "vanilla", "label": "Vanilla JS + Flask", "frontend": "Vanilla JS", "backend": "Flask",
     "requires": {"frontend": "javascript", "backend": ["flask", "python"]}},
    {"key": "express", "label": "Vanilla JS + Node/Express", "frontend": "Vanilla JS", "backend": "Node/Express",
     "requires": {"frontend": "javascript", "backend": ["node"]}},
    {"key": "django", "label": "Vanilla JS + Django", "frontend": "Vanilla JS", "backend": "Django",
     "requires": {"frontend": "javascript", "backend": ["django"]}},
    {"key": "fastapi", "label": "Vanilla JS + FastAPI", "frontend": "Vanilla JS", "backend": "FastAPI",
     "requires": {"frontend": "javascript", "backend": ["fastapi"]}},
]

# ── skill areas (see team_project_skills.py) ───────────────────────────────
# A student's level in an area comes from how much of the matching COURSES they finished — not
# from the points-based `current_level`. The map is EXPLICIT (exact course titles), not a regex over
# titles: a regex mapped "Next.js" to JavaScript and kids' courses to the adult areas. Kids' courses
# and mixed capstones are deliberately absent. tests/test_team_project_skills.py checks every title
# below against the real course list.
SKILL_AREAS = ("html_css", "css_frameworks", "javascript", "typescript", "python", "flask", "django", "fastapi",
               "node", "react", "sql", "telegram", "ai", "git", "docker", "linux", "api")

# Flask/Django courses (and the API short courses built on them) count for the python area too;
# the mixed capstones do not.
_FLASK_PYTHON_COURSES = ("Python Flask", "Python Flask — O'rta daraja", "Flask: Token autentifikatsiya va CORS (API)")
_FLASK_COURSES = _FLASK_PYTHON_COURSES + ("Capstone 3: Flask + JavaScript + Telegram Bot",)
_DJANGO_PYTHON_COURSES = ("Python: Django Asoslari", "Django: JSON API (DRF asoslari)")
_DJANGO_COURSES = _DJANGO_PYTHON_COURSES + ("Capstone 2: Django + React + Telegram Bot",)
AREA_COURSES = {
    "html_css": ("HTML CSS", "HTML/CSS Mini-Projects", "HTML/CSS: Keyingi Bosqich", "HTML/CSS: Professional Bosqich",
                 "HTML/CSS: Real Loyihalar", "HTML/CSS: Intervyu Tayyorgarligi"),
    "css_frameworks": ("SASS/SCSS Asoslari", "Bootstrap 5 Asoslari", "Tailwind CSS Asoslari"),
    "javascript": ("Javascript", "JavaScript: Keyingi Bosqich", "JavaScript Mini-Projects", "JavaScript: Ilg'or Mavzular",
                   "JavaScript: Brauzer API va Web", "JavaScript: Algoritmlar va Ma'lumotlar Tuzilmasi", "JavaScript: Testlash"),
    "typescript": ("TypeScript Asoslari", "Capstone 4: TypeScript Full-Stack"),
    # Flask, Django and FastAPI are Python: finishing them counts for the python area too.
    "python": ("Python Asoslari", "Python: Keyingi Bosqich", "Python: Testlash", "Python: Algoritmlar va Ma'lumotlar Tuzilmasi",
               "Python: Ilg'or Mavzular", "FastAPI Asoslari") + _FLASK_PYTHON_COURSES + _DJANGO_PYTHON_COURSES,
    "flask": _FLASK_COURSES,
    "django": _DJANGO_COURSES,
    "fastapi": ("FastAPI Asoslari",),
    "node": ("Node.js/Express Asoslari", "Express: API testlash (Jest va supertest)"),
    "react": ("React Asoslari", "React: Redux Toolkit, TypeScript va Testlash", "React: Next.js va Server-Side Rendering",
              "React: Performance va Optimizatsiya"),
    "sql": ("SQL va PostgreSQL Asoslari", "SQL: Ma'lumotlar Bazasi Dizayni", "SQL: Ilg'or So'rovlar va Performance",
            "SQL + Python ORM va Migratsiyalar"),
    "telegram": ("Telegram Bot aiogram", "Telegram Bot: Ilg'or Mavzular", "Telethon: Telegram Userbot va MTProto",
                 "Pyrogram: Zamonaviy Telegram Client Kutubxonasi"),
    "ai": ("AI API'larni Loyihalarga Ulash", "RAG va Vektor Qidiruv: Hujjatlar Asosida AI"),
    "git": ("Git va GitHub", "Git: Ichki Tuzilishi va Ilg'or Workflow", "GitHub Actions va CI/CD Chuqur",
            "Jamoaviy Ish Madaniyati: Code Review va Versiyalash"),
    # docker / linux / api are tracked like git/sql/telegram: no stack or blueprint need uses them yet
    # (team projects run without Docker, and their API contract is not described in OpenAPI).
    "docker": ("Docker asoslari",),
    "linux": ("Linux va terminal asoslari",),
    # HTTP, Postman, OpenAPI: language-independent, so it does not count for python/flask/node.
    "api": ("API asoslari: Postman va OpenAPI",),
}


def normalize_title(title: str) -> str:
    return (title or "").replace("\u2019", "'").replace("\u02bb", "'").replace("`", "'").strip().casefold()


_AREA_TITLE_SETS = {a: frozenset(normalize_title(t) for t in titles) for a, titles in AREA_COURSES.items()}


def course_in_area(course_title: str, area: str) -> bool:
    return normalize_title(course_title) in _AREA_TITLE_SETS.get(area, frozenset())


THEMES_BY_KEY = {t["key"]: t for t in THEMES}
TECH_STACKS_BY_KEY = {s["key"]: s for s in TECH_STACKS}

# Shared between team_project_service.py (lead picking) and
# team_project_planner.py (plan validation) — both need to compare
# StudentLevel values by seniority, not by string equality.
LEVEL_RANK = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}
