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

# `needs`: a regex over a member's skill summary (course titles, lesson
# languages, project technologies). A stack with a frontend framework is only
# offered to a team where at least half of the members have seen that
# framework — nobody on this platform learns React/Vue/Next.js by default, so a
# random pick used to hand teams a framework none of them had studied. "vanilla"
# needs nothing, so every team always has at least one eligible stack.
TECH_STACKS = [
    {"key": "react", "label": "React", "frontend": "React", "backend": "FastAPI", "needs": r"\breact\b"},
    {"key": "vue", "label": "Vue", "frontend": "Vue", "backend": "Flask", "needs": r"\bvue\b"},
    {"key": "next", "label": "Next.js", "frontend": "Next.js", "backend": "Django", "needs": r"\b(?:next\.?js|react)\b"},
    {"key": "express", "label": "Node/Express", "frontend": "React", "backend": "Node/Express", "needs": r"\breact\b"},
    {"key": "vanilla", "label": "Vanilla JS", "frontend": "Vanilla JS", "backend": "Flask", "needs": None},
]

THEMES_BY_KEY = {t["key"]: t for t in THEMES}
TECH_STACKS_BY_KEY = {s["key"]: s for s in TECH_STACKS}

# Shared between team_project_service.py (lead picking) and
# team_project_planner.py (plan validation) — both need to compare
# StudentLevel values by seniority, not by string equality.
LEVEL_RANK = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}
