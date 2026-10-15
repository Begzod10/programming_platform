"""Curated pools for random team-project theme/tech-stack assignment.

Static Python data, not DB tables — teachers aren't asking to edit this
list yet (see team_project_service.py for how these get sampled per team).
"""

THEMES = [
    {"key": "crm", "label": "CRM tizimi", "label_ru": "Система CRM", "kind": "web"},
    {"key": "dashboard", "label": "Admin dashboard", "label_ru": "Админ-панель", "kind": "web"},
    {"key": "task_tracker", "label": "Vazifalarni boshqarish tizimi", "label_ru": "Трекер задач", "kind": "web"},
    {"key": "online_shop", "label": "Onlayn do'kon", "label_ru": "Интернет-магазин", "kind": "web"},
    {"key": "social_feed", "label": "Ijtimoiy tarmoq lentasi", "label_ru": "Лента соцсети", "kind": "web"},
    {"key": "booking", "label": "Bandlash tizimi", "label_ru": "Система бронирования", "kind": "web"},
    {"key": "blog", "label": "Blog platformasi", "label_ru": "Блог-платформа", "kind": "web"},
    {"key": "survey", "label": "So'rovnoma tizimi", "label_ru": "Система опросов", "kind": "web"},
    {"key": "quiz", "label": "Test (viktorina) platformasi", "label_ru": "Платформа тестов (викторин)", "kind": "web"},
    {"key": "library", "label": "Kutubxona tizimi", "label_ru": "Система библиотеки", "kind": "web"},
    {"key": "finance", "label": "Shaxsiy moliya hisobi", "label_ru": "Учёт личных финансов", "kind": "web"},
    {"key": "bot_panel", "label": "Telegram bot boshqaruv paneli", "label_ru": "Панель управления Telegram-ботом", "kind": "web"},
    {"key": "recipes", "label": "Retsept kitobi", "label_ru": "Книга рецептов", "kind": "web"},
    {"key": "events", "label": "Tadbirlar va ro'yxatdan o'tish", "label_ru": "События и регистрация", "kind": "web"},
    {"key": "jobs", "label": "Vakansiyalar taxtasi", "label_ru": "Доска вакансий", "kind": "web"},
    {"key": "attendance", "label": "Davomat tizimi", "label_ru": "Система посещаемости", "kind": "web"},
    {"key": "habits", "label": "Odatlar kuzatuvchisi", "label_ru": "Трекер привычек", "kind": "web"},
    {"key": "classifieds", "label": "E'lonlar taxtasi", "label_ru": "Доска объявлений", "kind": "web"},
    {"key": "flashcards", "label": "So'z kartochkalari", "label_ru": "Карточки для слов", "kind": "web"},
    {"key": "inventory", "label": "Ombor hisobi", "label_ru": "Складской учёт", "kind": "web"},
    {"key": "tickets", "label": "Yordam so'rovlari tizimi", "label_ru": "Система заявок в поддержку", "kind": "web"},
    {"key": "clinic_queue", "label": "Poliklinika navbati", "label_ru": "Очередь в поликлинику", "kind": "web"},
    {"key": "tournament", "label": "Turnir jadvali", "label_ru": "Турнирная таблица", "kind": "web"},
    {"key": "rental", "label": "Ijara tizimi", "label_ru": "Система аренды", "kind": "web"},
    # Telegram bots (aiogram): no frontend, no HTTP endpoints — the contract is commands, buttons and FSM flows.
    {"key": "delivery_bot", "label": "Yetkazib berish boti", "label_ru": "Бот доставки", "kind": "bot"},
    {"key": "quiz_bot", "label": "Viktorina boti", "label_ru": "Бот-викторина", "kind": "bot"},
    {"key": "queue_bot", "label": "Navbat boti", "label_ru": "Бот очереди", "kind": "bot"},
    {"key": "expense_bot", "label": "Xarajat hisobi boti", "label_ru": "Бот учёта расходов", "kind": "bot"},
    {"key": "flashcards_bot", "label": "So'z kartochkalari boti", "label_ru": "Бот карточек для слов", "kind": "bot"},
    {"key": "events_bot", "label": "Tadbirlar boti", "label_ru": "Бот мероприятий", "kind": "bot"},
    {"key": "support_bot", "label": "Yordam so'rovlari boti", "label_ru": "Бот заявок в поддержку", "kind": "bot"},
    {"key": "habits_bot", "label": "Odatlar kuzatuvchi boti", "label_ru": "Бот-трекер привычек", "kind": "bot"},
    {"key": "library_bot", "label": "Kutubxona boti", "label_ru": "Бот библиотеки", "kind": "bot"},
    {"key": "survey_bot", "label": "So'rovnoma boti", "label_ru": "Бот опросов", "kind": "bot"},
    {"key": "booking_bot", "label": "Bandlash boti", "label_ru": "Бот бронирования", "kind": "bot"},
    {"key": "notes_bot", "label": "Eslatmalar boti", "label_ru": "Бот заметок", "kind": "bot"},
]

WEB_THEMES = [t for t in THEMES if t["kind"] == "web"]
BOT_THEMES = [t for t in THEMES if t["kind"] == "bot"]


def themes_for_kind(kind: str) -> list:
    """The theme pool of a stack kind: 'web' (frontend + backend) or 'bot' (Telegram bot)."""
    return BOT_THEMES if kind == "bot" else WEB_THEMES


# `needs`: a regex over a member's skill summary (course titles, lesson
# languages, project technologies). A stack with a frontend framework is only
# offered to a team where at least half of the members have seen that
# framework — nobody on this platform learns React/Vue/Next.js by default, so a
# random pick used to hand teams a framework none of them had studied. "vanilla"
# needs nothing, so every team always has at least one eligible stack.
TECH_STACKS = [
    # Every stack has a blueprint family (flask / express / django / fastapi / aiogram) and plain-JS pages (bot: none) — what is
    # written here is what a team is actually given. (React/Vue/Next/FastAPI stacks were removed: no
    # blueprint exists for them; FastAPI is back since "FastAPI Asoslari" and its blueprint family exist.)
    {"key": "vanilla", "kind": "web", "label": "Vanilla JS + Flask", "frontend": "Vanilla JS", "backend": "Flask",
     "requires": {"frontend": "javascript", "backend": ["flask", "python"]}},
    {"key": "express", "kind": "web", "label": "Vanilla JS + Node/Express", "frontend": "Vanilla JS", "backend": "Node/Express",
     "requires": {"frontend": "javascript", "backend": ["node"]}},
    {"key": "django", "kind": "web", "label": "Vanilla JS + Django", "frontend": "Vanilla JS", "backend": "Django",
     "requires": {"frontend": "javascript", "backend": ["django"]}},
    {"key": "fastapi", "kind": "web", "label": "Vanilla JS + FastAPI", "frontend": "Vanilla JS", "backend": "FastAPI",
     "requires": {"frontend": "javascript", "backend": ["fastapi"]}},
    # A Telegram bot has no frontend: `requires.frontend` is None, the backend skill is the aiogram course
    # (not the whole `telegram` area, which also holds the Telethon/Pyrogram userbot courses).
    {"key": "aiogram", "kind": "bot", "label": "Telegram bot (aiogram)", "frontend": "—", "backend": "aiogram",
     "requires": {"frontend": None, "backend": ["aiogram"]}},
]

# ── skill areas (see team_project_skills.py) ───────────────────────────────
# A student's level in an area comes from how much of the matching COURSES they finished — not
# from the points-based `current_level`. The map is EXPLICIT (exact course titles), not a regex over
# titles: a regex mapped "Next.js" to JavaScript and kids' courses to the adult areas. Kids' courses
# and mixed capstones are deliberately absent. tests/test_team_project_skills.py checks every title
# below against the real course list.
SKILL_AREAS = ("html_css", "css_frameworks", "javascript", "typescript", "python", "flask", "django", "fastapi", "aiogram",
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
    "aiogram": ("Telegram Bot aiogram", "Telegram Bot: Ilg'or Mavzular"),
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
