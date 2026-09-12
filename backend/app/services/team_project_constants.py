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
]

TECH_STACKS = [
    {"key": "react", "label": "React", "frontend": "React", "backend": "FastAPI"},
    {"key": "vue", "label": "Vue", "frontend": "Vue", "backend": "Flask"},
    {"key": "next", "label": "Next.js", "frontend": "Next.js", "backend": "Django"},
    {"key": "express", "label": "Node/Express", "frontend": "React", "backend": "Node/Express"},
    {"key": "vanilla", "label": "Vanilla JS", "frontend": "Vanilla JS", "backend": "Flask"},
]

THEMES_BY_KEY = {t["key"]: t for t in THEMES}
TECH_STACKS_BY_KEY = {s["key"]: s for s in TECH_STACKS}
