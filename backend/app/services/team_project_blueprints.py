"""Ready-made API contracts ("blueprints") for team projects, one per (theme, backend family).

The AI planner used to invent the contract between a team's pieces, and invented it badly:
the backend task said "clients", the frontend tasks called "/api/customers". A blueprint is
fixed, hand-written data — endpoints, JSON shapes, token key, file layout, run commands —
that the planner may SPLIT among members but never change. See
docs/superpowers/specs/2026-10-12-team-project-planning-design.md §4.3.

Themes are described once (`_THEMES`) and expanded per backend family (`flask`, `express`, `django`, `fastapi`) so the
two stay in step; only file names and run commands differ between families.
"""
import copy
from typing import Optional

BASE_URL = "http://127.0.0.1:5000"
TOKEN_KEY = "auth_token"
_AUTH = {"header": "Authorization: Bearer <token>", "token_key": TOKEN_KEY}


# ── lesson requirements ─────────────────────────────────────────────────────
# What a team must have STUDIED for the project to be fair. A need is satisfied by a student who
# finished a lesson whose title matches `lesson` in a course whose title matches `course` (regexes,
# case-insensitive, so they survive renumbering). The frontend needs hold for at least half of the
# team, the backend needs for at least one member (same split as the stack rule).
def _need(course: str, lesson: str, label: str) -> dict:
    return {"course": course, "lesson": lesson, "label": label}


_JS = "javascript"          # `course` of a need is a skill AREA (team_project_constants.AREA_COURSES)
_FLASK = "flask"
_NODE = "node"
_DJANGO = "django"
_FASTAPI = "fastapi"
_DOM = _need(_JS, r"DOM bilan ishlash", "JavaScript: DOM bilan ishlash")
_FETCH = _need(_JS, r"fetch va REST API", "JavaScript: fetch va REST API")
_DYNAMIC = _need(_JS, r"dinamik", "JavaScript: HTML elementlarini dinamik yaratish")
_STORAGE = _need(_JS, r"LocalStorage", "JavaScript: LocalStorage")
_ITER = _need(_JS, r"Massiv iteratorlari", "JavaScript: massiv iteratorlari (map, filter)")
_TABLE = _need("html_css", r"Table", "HTML/CSS: Table")
_FLEX = _need("html_css", r"Display Flex", "HTML/CSS: Display Flex")

_FLASK_BASE = [
    _need(_FLASK, r"Routing va URL", "Flask: Routing va URL"),
    _need(_FLASK, r"JSON API", "Flask: JSON API"),
    _need(_FLASK, r"Database \(SQLAlchemy\)", "Flask: Database (SQLAlchemy)"),
    _need(_FLASK, r"CRUD operatsiyalar", "Flask: CRUD operatsiyalar"),
    _need(_FLASK, r"Parol hashing", "Flask: Parol hashing"),
    # The contract is token auth (register/login -> Bearer token). The older Flask courses only teach
    # session auth (Flask-Login), so these two lessons come from "Flask: Token autentifikatsiya va CORS".
    _need(_FLASK, r"register va login", "Flask: JWT bilan register va login"),
    _need(_FLASK, r"Himoyalangan route", "Flask: himoyalangan route'lar va rollar"),
]
_DJANGO_BASE = [
    _need(_DJANGO, r"URL routing va views", "Django: URL routing va views"),
    _need(_DJANGO, r"Models va ORM asoslari", "Django: Models va ORM asoslari"),
    _need(_DJANGO, r"ORM chuqurroq", "Django: ORM chuqurroq (querysets, bog'lanishlar)"),
    _need(_DJANGO, r"Autentifikatsiya", "Django: Autentifikatsiya"),
    # JSON + token API and CORS come from "Django: JSON API (DRF asoslari)"; the older courses are HTML/session based.
    _need(_DJANGO, r"JsonResponse", "Django: JSON API (JsonResponse)"),
    _need(_DJANGO, r"JWT autentifikatsiya", "Django: JWT autentifikatsiya"),
    _need(_DJANGO, r"CORS", "Django: CORS (django-cors-headers)"),
]
# FastAPI: the contract is JSON + token auth + CORS; every need is a lesson of "FastAPI Asoslari".
_FASTAPI_BASE = [
    _need(_FASTAPI, r"birinchi endpoint", "FastAPI: birinchi endpoint (path va query parametrlari)"),
    _need(_FASTAPI, r"Pydantic", "FastAPI: Pydantic modellari va validatsiya"),
    _need(_FASTAPI, r"SQLAlchemy va Depends", "FastAPI: SQLAlchemy va Depends"),
    _need(_FASTAPI, r"JWT autentifikatsiya", "FastAPI: JWT autentifikatsiya"),
    _need(_FASTAPI, r"CORS", "FastAPI: CORS (CORSMiddleware)"),
]
_RELATIONS = _need(_FLASK, r"Modellar orasidagi munosabatlar", "Flask: modellar orasidagi munosabatlar")
_EXPRESS_BASE = [
    _need(_NODE, r"Routing va middleware", "Node/Express: Routing va middleware"),
    _need(_NODE, r"PostgreSQL ulanish", "Node/Express: PostgreSQL ulanish"),
    _need(_NODE, r"CRUD operatsiyalar", "Node/Express: CRUD operatsiyalar"),
    _need(_NODE, r"JWT autentifikatsiya", "Node/Express: JWT autentifikatsiya"),
    _need(_NODE, r"CORS va React", "Node/Express: CORS va frontend bilan ulash"),
]

_THEME_NEEDS = {
    "online_shop":  {"frontend": [_DOM, _FETCH, _STORAGE, _FLEX], "flask": [_RELATIONS], "express": []},
    "social_feed":  {"frontend": [_DOM, _FETCH, _DYNAMIC],         "flask": [_RELATIONS], "express": []},
    "crm":          {"frontend": [_DOM, _FETCH, _DYNAMIC, _TABLE], "flask": [_RELATIONS], "express": []},
    "booking":      {"frontend": [_DOM, _FETCH, _DYNAMIC, _STORAGE], "flask": [_RELATIONS], "express": []},
    "dashboard":    {"frontend": [_DOM, _FETCH, _DYNAMIC, _TABLE, _ITER],
                     "flask": [_need(_FLASK, r"So'rovlar, filterlar", "Flask: so'rovlar, filterlar, sahifalash")],
                     "express": []},
    "task_tracker": {"frontend": [_DOM, _FETCH, _DYNAMIC, _ITER], "flask": [], "express": []},
    "blog":         {"frontend": [_DOM, _FETCH, _DYNAMIC], "flask": [_RELATIONS], "express": []},
    "survey":       {"frontend": [_DOM, _FETCH, _DYNAMIC, _ITER], "flask": [_RELATIONS], "express": []},
    "quiz":         {"frontend": [_DOM, _FETCH, _DYNAMIC, _ITER], "flask": [_RELATIONS], "express": []},
    "library":      {"frontend": [_DOM, _FETCH, _DYNAMIC], "flask": [_RELATIONS], "express": []},
    "finance":      {"frontend": [_DOM, _FETCH, _DYNAMIC, _TABLE, _ITER],
                     "flask": [_need(_FLASK, r"So'rovlar, filterlar", "Flask: so'rovlar, filterlar, sahifalash")],
                     "express": []},
    "bot_panel":    {"frontend": [_DOM, _FETCH, _DYNAMIC, _TABLE], "flask": [], "express": []},
    "recipes":      {"frontend": [_DOM, _FETCH, _DYNAMIC], "flask": [_RELATIONS], "express": []},
    "events":       {"frontend": [_DOM, _FETCH, _DYNAMIC], "flask": [_RELATIONS], "express": []},
    "jobs":         {"frontend": [_DOM, _FETCH, _DYNAMIC, _FLEX], "flask": [_RELATIONS], "express": []},
    "attendance":   {"frontend": [_DOM, _FETCH, _DYNAMIC, _TABLE], "flask": [_RELATIONS], "express": []},
    "habits":       {"frontend": [_DOM, _FETCH, _DYNAMIC, _STORAGE], "flask": [_RELATIONS], "express": []},
    "classifieds":  {"frontend": [_DOM, _FETCH, _DYNAMIC, _ITER],
                     "flask": [_need(_FLASK, r"So'rovlar, filterlar", "Flask: so'rovlar, filterlar, sahifalash")],
                     "express": []},
    "flashcards":   {"frontend": [_DOM, _FETCH, _DYNAMIC, _STORAGE], "flask": [_RELATIONS], "express": []},
    "inventory":    {"frontend": [_DOM, _FETCH, _DYNAMIC, _TABLE], "flask": [_RELATIONS], "express": []},
    "tickets":      {"frontend": [_DOM, _FETCH, _DYNAMIC], "flask": [_RELATIONS], "express": []},
    "clinic_queue": {"frontend": [_DOM, _FETCH, _DYNAMIC, _FLEX], "flask": [_RELATIONS], "express": []},
    "tournament":   {"frontend": [_DOM, _FETCH, _DYNAMIC, _TABLE, _ITER], "flask": [_RELATIONS], "express": []},
    "rental":       {"frontend": [_DOM, _FETCH, _DYNAMIC, _FLEX], "flask": [_RELATIONS], "express": []},
}


def lesson_needs(theme: str, family: str) -> dict:
    """{"frontend": [needs], "backend": [needs]} for a theme and backend family."""
    t = _THEME_NEEDS[theme]
    base = {"flask": _FLASK_BASE, "express": _EXPRESS_BASE, "django": _DJANGO_BASE, "fastapi": _FASTAPI_BASE}[family]
    return {"frontend": list(t["frontend"]), "backend": list(base) + list(t.get(family, []))}


class BlueprintMissing(Exception):
    """No blueprint for this (theme, backend family)."""


def _ep(id_, method, path, *, auth=False, request=None, response=None):
    return {"id": id_, "method": method, "path": path, "auth": auth, "request": request, "response": response}


_REGISTER = _ep("auth.register", "POST", "/api/register", request={"username": "str", "password": "str(>=6)"},
                response={"message": "str"})
_LOGIN = _ep("auth.login", "POST", "/api/login", request={"username": "str", "password": "str"},
             response={"token": "str", "username": "str"})


def _crud(name, path, shape, *, public_read=False, write_auth=True, update=True, delete=True):
    eps = [_ep(f"{name}.list", "GET", path, auth=not public_read, response=[shape])]
    eps.append(_ep(f"{name}.get", "GET", f"{path}/<id>", auth=not public_read, response=shape))
    eps.append(_ep(f"{name}.create", "POST", path, auth=write_auth, request={k: v for k, v in shape.items() if k != "id"},
                   response=shape))
    if update:
        eps.append(_ep(f"{name}.update", "PUT", f"{path}/<id>", auth=write_auth,
                       request={k: v for k, v in shape.items() if k != "id"}, response=shape))
    if delete:
        eps.append(_ep(f"{name}.delete", "DELETE", f"{path}/<id>", auth=write_auth, response={"message": "str"}))
    return eps


# theme -> (entities, endpoints, frontend files)
_THEMES = {
    "online_shop": {
        "entities": {"product": {"id": "int", "name": "str", "price": "int (so'm)"},
                     "cart_item": {"id": "int (productId)", "name": "str", "price": "int", "quantity": "int"}},
        "endpoints": [
            *_crud("products", "/api/products", {"id": "int", "name": "str", "price": "int"},
                   public_read=True, update=False, delete=False),
            _ep("cart.get", "GET", "/api/cart", auth=True,
                response={"items": [{"id": "int", "name": "str", "price": "int", "quantity": "int"}], "total": "int"}),
            _ep("cart.add", "POST", "/api/cart", auth=True, request={"productId": "int", "quantity": "int(>=1)"},
                response={"items": ["cart_item"], "total": "int"}),
            _ep("cart.remove", "DELETE", "/api/cart/<productId>", auth=True, response={"items": ["cart_item"], "total": "int"}),
            _ep("orders.create", "POST", "/api/orders", auth=True, response={"orderId": "int", "total": "int", "items": ["cart_item"]}),
        ],
        "frontend": ["frontend/index.html", "frontend/js/products.js", "frontend/cart.html", "frontend/js/cart.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "social_feed": {
        "entities": {"post": {"id": "int", "title": "str", "content": "str", "author_id": "int"},
                     "comment": {"id": "int", "content": "str", "author_id": "int"}},
        "endpoints": [
            *_crud("posts", "/api/posts", {"id": "int", "title": "str", "content": "str", "author_id": "int"},
                   public_read=True, update=True, delete=True),
            _ep("comments.create", "POST", "/api/posts/<id>/comments", auth=True, request={"content": "str"},
                response={"message": "str"}),
            _ep("comments.list", "GET", "/api/posts/<id>/comments", response=[{"id": "int", "content": "str", "author_id": "int"}]),
        ],
        "frontend": ["frontend/index.html", "frontend/js/feed.js", "frontend/post.html", "frontend/js/post.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "crm": {
        "entities": {"customer": {"id": "int", "name": "str", "phone": "str", "email": "str", "address": "str"},
                     "deal": {"id": "int", "customer_id": "int", "title": "str", "stage": "new|won|lost", "amount": "int"}},
        "endpoints": [
            *_crud("customers", "/api/customers", {"id": "int", "name": "str", "phone": "str", "email": "str", "address": "str"}),
            _ep("deals.list", "GET", "/api/customers/<id>/deals", auth=True,
                response=[{"id": "int", "customer_id": "int", "title": "str", "stage": "str", "amount": "int"}]),
            _ep("deals.create", "POST", "/api/customers/<id>/deals", auth=True,
                request={"title": "str", "amount": "int"}, response={"id": "int", "stage": "new"}),
            _ep("deals.update_stage", "PUT", "/api/deals/<id>", auth=True, request={"stage": "new|won|lost"},
                response={"id": "int", "stage": "str"}),
        ],
        "frontend": ["frontend/index.html", "frontend/js/customers.js", "frontend/customer.html", "frontend/js/customer.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "booking": {
        "entities": {"slot": {"id": "int", "time": "str (HH:MM)", "date": "str (YYYY-MM-DD)", "free": "bool"},
                     "booking": {"id": "int", "slot_id": "int", "name": "str", "time": "str", "date": "str"}},
        "endpoints": [
            _ep("slots.list", "GET", "/api/slots", response=[{"id": "int", "time": "str", "date": "str", "free": "bool"}]),
            _ep("bookings.create", "POST", "/api/bookings", auth=True, request={"slot_id": "int", "name": "str"},
                response={"id": "int", "slot_id": "int", "name": "str", "time": "str", "date": "str"}),
            _ep("bookings.list", "GET", "/api/bookings", auth=True,
                response=[{"id": "int", "slot_id": "int", "name": "str", "time": "str", "date": "str"}]),
            _ep("bookings.cancel", "DELETE", "/api/bookings/<id>", auth=True, response={"message": "str"}),
        ],
        "frontend": ["frontend/index.html", "frontend/js/booking_form.js", "frontend/bookings.html", "frontend/js/bookings_list.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "dashboard": {
        "entities": {"record": {"id": "int", "title": "str", "category": "str", "amount": "int", "date": "str"},
                     "stats": {"total": "int", "count": "int", "by_category": {"<category>": "int"}}},
        "endpoints": [
            *_crud("records", "/api/records", {"id": "int", "title": "str", "category": "str", "amount": "int", "date": "str"}),
            _ep("stats.get", "GET", "/api/stats", auth=True,
                response={"total": "int", "count": "int", "by_category": {"<category>": "int"}}),
        ],
        "frontend": ["frontend/index.html", "frontend/js/dashboard.js", "frontend/records.html", "frontend/js/records.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "task_tracker": {
        "entities": {"task": {"id": "int", "title": "str", "description": "str", "status": "todo|doing|done", "owner_id": "int"}},
        "endpoints": [
            *_crud("tasks", "/api/tasks", {"id": "int", "title": "str", "description": "str", "status": "todo|doing|done", "owner_id": "int"}),
            _ep("tasks.set_status", "PUT", "/api/tasks/<id>/status", auth=True, request={"status": "todo|doing|done"},
                response={"id": "int", "status": "str"}),
        ],
        "frontend": ["frontend/index.html", "frontend/js/board.js", "frontend/task.html", "frontend/js/task.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },

    "blog": {
        "entities": {"article": {"id": "int", "title": "str", "content": "str", "tag": "str", "author_id": "int"}},
        "endpoints": [
            *_crud("articles", "/api/articles", {"id": "int", "title": "str", "content": "str", "tag": "str", "author_id": "int"},
                   public_read=True),
            _ep("tags.list", "GET", "/api/tags", response=["str"]),
        ],
        "frontend": ["frontend/index.html", "frontend/js/articles.js", "frontend/article.html", "frontend/js/article.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "survey": {
        "entities": {"survey": {"id": "int", "title": "str", "questions": [{"id": "int", "text": "str", "options": ["str"]}]}},
        "endpoints": [
            _ep("surveys.list", "GET", "/api/surveys", response=[{"id": "int", "title": "str"}]),
            _ep("surveys.get", "GET", "/api/surveys/<id>",
                response={"id": "int", "title": "str", "questions": [{"id": "int", "text": "str", "options": ["str"]}]}),
            _ep("surveys.create", "POST", "/api/surveys", auth=True,
                request={"title": "str", "questions": [{"text": "str", "options": ["str"]}]}, response={"id": "int"}),
            _ep("responses.submit", "POST", "/api/surveys/<id>/responses", auth=True,
                request={"answers": [{"question_id": "int", "option": "str"}]}, response={"message": "str"}),
            _ep("results.get", "GET", "/api/surveys/<id>/results", auth=True,
                response={"total": "int", "questions": [{"question_id": "int", "counts": {"<option>": "int"}}]}),
        ],
        "frontend": ["frontend/index.html", "frontend/js/surveys.js", "frontend/survey.html", "frontend/js/survey.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "quiz": {
        "entities": {"quiz": {"id": "int", "title": "str", "questions": [{"id": "int", "text": "str", "options": ["str"]}]},
                     "attempt": {"id": "int", "quiz_id": "int", "score": "int", "total": "int"}},
        "endpoints": [
            _ep("quizzes.list", "GET", "/api/quizzes", response=[{"id": "int", "title": "str"}]),
            _ep("quizzes.get", "GET", "/api/quizzes/<id>",
                response={"id": "int", "title": "str", "questions": [{"id": "int", "text": "str", "options": ["str"]}]}),
            _ep("attempts.submit", "POST", "/api/quizzes/<id>/attempts", auth=True,
                request={"answers": [{"question_id": "int", "option_index": "int"}]},
                response={"id": "int", "score": "int", "total": "int"}),
            _ep("attempts.mine", "GET", "/api/attempts", auth=True,
                response=[{"id": "int", "quiz_id": "int", "score": "int", "total": "int"}]),
        ],
        "frontend": ["frontend/index.html", "frontend/js/quizzes.js", "frontend/quiz.html", "frontend/js/quiz.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "library": {
        "entities": {"book": {"id": "int", "title": "str", "author": "str", "available": "bool"},
                     "loan": {"id": "int", "book_id": "int", "returned": "bool"}},
        "endpoints": [
            *_crud("books", "/api/books", {"id": "int", "title": "str", "author": "str", "available": "bool"},
                   public_read=True, update=False),
            _ep("loans.borrow", "POST", "/api/loans", auth=True, request={"book_id": "int"},
                response={"id": "int", "book_id": "int", "returned": "bool"}),
            _ep("loans.mine", "GET", "/api/loans", auth=True, response=[{"id": "int", "book_id": "int", "returned": "bool"}]),
            _ep("loans.return", "PUT", "/api/loans/<id>/return", auth=True, response={"id": "int", "returned": "bool"}),
        ],
        "frontend": ["frontend/index.html", "frontend/js/books.js", "frontend/loans.html", "frontend/js/loans.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "finance": {
        "entities": {"transaction": {"id": "int", "title": "str", "amount": "int", "kind": "income|expense",
                                     "category": "str", "date": "str"}},
        "endpoints": [
            *_crud("transactions", "/api/transactions",
                   {"id": "int", "title": "str", "amount": "int", "kind": "income|expense", "category": "str", "date": "str"}),
            _ep("categories.list", "GET", "/api/categories", auth=True, response=["str"]),
            _ep("summary.get", "GET", "/api/summary", auth=True,
                response={"balance": "int", "income": "int", "expense": "int", "by_category": {"<category>": "int"}}),
        ],
        "frontend": ["frontend/index.html", "frontend/js/summary.js", "frontend/transactions.html", "frontend/js/transactions.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "bot_panel": {
        "entities": {"bot_user": {"id": "int", "telegram_id": "int", "name": "str", "joined": "str"},
                     "message": {"id": "int", "text": "str", "sent_to": "int", "created": "str"}},
        "endpoints": [
            _ep("users.list", "GET", "/api/bot-users", auth=True,
                response=[{"id": "int", "telegram_id": "int", "name": "str", "joined": "str"}]),
            _ep("broadcasts.create", "POST", "/api/broadcasts", auth=True, request={"text": "str"},
                response={"id": "int", "sent_to": "int"}),
            _ep("broadcasts.list", "GET", "/api/broadcasts", auth=True,
                response=[{"id": "int", "text": "str", "sent_to": "int", "created": "str"}]),
            _ep("stats.get", "GET", "/api/bot-stats", auth=True, response={"users": "int", "messages": "int", "today": "int"}),
        ],
        "frontend": ["frontend/index.html", "frontend/js/stats.js", "frontend/broadcasts.html", "frontend/js/broadcasts.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },

    "recipes": {
        "entities": {"recipe": {"id": "int", "title": "str", "ingredients": ["str"], "steps": "str", "minutes": "int", "author_id": "int"}},
        "endpoints": [
            *_crud("recipes", "/api/recipes",
                   {"id": "int", "title": "str", "ingredients": ["str"], "steps": "str", "minutes": "int", "author_id": "int"},
                   public_read=True),
            _ep("favorites.add", "POST", "/api/recipes/<id>/favorite", auth=True, response={"message": "str"}),
            _ep("favorites.list", "GET", "/api/favorites", auth=True,
                response=[{"id": "int", "title": "str", "minutes": "int"}]),
        ],
        "frontend": ["frontend/index.html", "frontend/js/recipes.js", "frontend/recipe.html", "frontend/js/recipe.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "events": {
        "entities": {"event": {"id": "int", "title": "str", "date": "str", "place": "str", "seats": "int", "taken": "int"},
                     "registration": {"id": "int", "event_id": "int"}},
        "endpoints": [
            *_crud("events", "/api/events", {"id": "int", "title": "str", "date": "str", "place": "str", "seats": "int", "taken": "int"},
                   public_read=True, update=False),
            _ep("registrations.create", "POST", "/api/events/<id>/register", auth=True,
                response={"id": "int", "event_id": "int"}),
            _ep("registrations.mine", "GET", "/api/registrations", auth=True,
                response=[{"id": "int", "event_id": "int", "title": "str", "date": "str"}]),
            _ep("registrations.cancel", "DELETE", "/api/registrations/<id>", auth=True, response={"message": "str"}),
        ],
        "frontend": ["frontend/index.html", "frontend/js/events.js", "frontend/registrations.html", "frontend/js/registrations.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "jobs": {
        "entities": {"job": {"id": "int", "title": "str", "company": "str", "salary": "int", "description": "str"},
                     "application": {"id": "int", "job_id": "int", "message": "str"}},
        "endpoints": [
            *_crud("jobs", "/api/jobs", {"id": "int", "title": "str", "company": "str", "salary": "int", "description": "str"},
                   public_read=True),
            _ep("applications.create", "POST", "/api/jobs/<id>/apply", auth=True, request={"message": "str"},
                response={"id": "int", "job_id": "int"}),
            _ep("applications.mine", "GET", "/api/applications", auth=True,
                response=[{"id": "int", "job_id": "int", "title": "str", "message": "str"}]),
        ],
        "frontend": ["frontend/index.html", "frontend/js/jobs.js", "frontend/job.html", "frontend/js/job.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "attendance": {
        "entities": {"student": {"id": "int", "name": "str"},
                     "mark": {"id": "int", "student_id": "int", "date": "str", "present": "bool"}},
        "endpoints": [
            *_crud("students", "/api/students", {"id": "int", "name": "str"}, update=False),
            _ep("marks.set", "POST", "/api/marks", auth=True, request={"student_id": "int", "date": "str", "present": "bool"},
                response={"id": "int", "student_id": "int", "date": "str", "present": "bool"}),
            _ep("marks.by_date", "GET", "/api/marks", auth=True,
                response=[{"student_id": "int", "name": "str", "present": "bool"}]),
            _ep("report.get", "GET", "/api/students/<id>/attendance", auth=True,
                response={"present": "int", "absent": "int", "percent": "int"}),
        ],
        "frontend": ["frontend/index.html", "frontend/js/attendance.js", "frontend/report.html", "frontend/js/report.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "habits": {
        "entities": {"habit": {"id": "int", "title": "str", "streak": "int"},
                     "checkin": {"id": "int", "habit_id": "int", "date": "str"}},
        "endpoints": [
            *_crud("habits", "/api/habits", {"id": "int", "title": "str", "streak": "int"}, update=False),
            _ep("checkins.create", "POST", "/api/habits/<id>/checkins", auth=True,
                request={"date": "str"}, response={"id": "int", "habit_id": "int", "date": "str", "streak": "int"}),
            _ep("checkins.list", "GET", "/api/habits/<id>/checkins", auth=True,
                response=[{"id": "int", "date": "str"}]),
        ],
        "frontend": ["frontend/index.html", "frontend/js/habits.js", "frontend/habit.html", "frontend/js/habit.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "classifieds": {
        "entities": {"ad": {"id": "int", "title": "str", "category": "str", "price": "int", "description": "str", "owner_id": "int"}},
        "endpoints": [
            *_crud("ads", "/api/ads",
                   {"id": "int", "title": "str", "category": "str", "price": "int", "description": "str", "owner_id": "int"},
                   public_read=True),
            _ep("categories.list", "GET", "/api/categories", response=["str"]),
            _ep("ads.mine", "GET", "/api/my-ads", auth=True,
                response=[{"id": "int", "title": "str", "category": "str", "price": "int"}]),
        ],
        "frontend": ["frontend/index.html", "frontend/js/ads.js", "frontend/ad.html", "frontend/js/ad.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },

    "flashcards": {
        "entities": {"deck": {"id": "int", "title": "str"},
                     "card": {"id": "int", "deck_id": "int", "front": "str", "back": "str", "known": "bool"}},
        "endpoints": [
            *_crud("decks", "/api/decks", {"id": "int", "title": "str"}, update=False),
            _ep("cards.list", "GET", "/api/decks/<id>/cards", auth=True,
                response=[{"id": "int", "front": "str", "back": "str", "known": "bool"}]),
            _ep("cards.create", "POST", "/api/decks/<id>/cards", auth=True, request={"front": "str", "back": "str"},
                response={"id": "int", "front": "str", "back": "str", "known": "bool"}),
            _ep("cards.mark", "PUT", "/api/cards/<id>", auth=True, request={"known": "bool"},
                response={"id": "int", "known": "bool"}),
        ],
        "frontend": ["frontend/index.html", "frontend/js/decks.js", "frontend/study.html", "frontend/js/study.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "inventory": {
        "entities": {"item": {"id": "int", "name": "str", "sku": "str", "quantity": "int", "min_quantity": "int"},
                     "movement": {"id": "int", "item_id": "int", "change": "int", "note": "str"}},
        "endpoints": [
            *_crud("items", "/api/items", {"id": "int", "name": "str", "sku": "str", "quantity": "int", "min_quantity": "int"}),
            _ep("movements.create", "POST", "/api/items/<id>/movements", auth=True,
                request={"change": "int", "note": "str"}, response={"id": "int", "item_id": "int", "quantity": "int"}),
            _ep("movements.list", "GET", "/api/items/<id>/movements", auth=True,
                response=[{"id": "int", "change": "int", "note": "str"}]),
            _ep("items.low", "GET", "/api/low-stock", auth=True, response=[{"id": "int", "name": "str", "quantity": "int"}]),
        ],
        "frontend": ["frontend/index.html", "frontend/js/items.js", "frontend/movements.html", "frontend/js/movements.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "tickets": {
        "entities": {"ticket": {"id": "int", "title": "str", "body": "str", "status": "open|in_progress|closed", "owner_id": "int"},
                     "reply": {"id": "int", "ticket_id": "int", "text": "str", "author_id": "int"}},
        "endpoints": [
            _ep("tickets.create", "POST", "/api/tickets", auth=True, request={"title": "str", "body": "str"},
                response={"id": "int", "status": "open"}),
            _ep("tickets.list", "GET", "/api/tickets", auth=True,
                response=[{"id": "int", "title": "str", "status": "str"}]),
            _ep("tickets.get", "GET", "/api/tickets/<id>", auth=True,
                response={"id": "int", "title": "str", "body": "str", "status": "str", "replies": [{"id": "int", "text": "str"}]}),
            _ep("replies.create", "POST", "/api/tickets/<id>/replies", auth=True, request={"text": "str"},
                response={"id": "int"}),
            _ep("tickets.set_status", "PUT", "/api/tickets/<id>/status", auth=True,
                request={"status": "open|in_progress|closed"}, response={"id": "int", "status": "str"}),
        ],
        "frontend": ["frontend/index.html", "frontend/js/tickets.js", "frontend/ticket.html", "frontend/js/ticket.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "clinic_queue": {
        "entities": {"doctor": {"id": "int", "name": "str", "specialty": "str"},
                     "visit": {"id": "int", "doctor_id": "int", "date": "str", "time": "str", "number": "int"}},
        "endpoints": [
            _ep("doctors.list", "GET", "/api/doctors", response=[{"id": "int", "name": "str", "specialty": "str"}]),
            _ep("visits.create", "POST", "/api/visits", auth=True, request={"doctor_id": "int", "date": "str", "time": "str"},
                response={"id": "int", "number": "int"}),
            _ep("visits.mine", "GET", "/api/visits", auth=True,
                response=[{"id": "int", "doctor": "str", "date": "str", "time": "str", "number": "int"}]),
            _ep("visits.cancel", "DELETE", "/api/visits/<id>", auth=True, response={"message": "str"}),
            _ep("queue.today", "GET", "/api/doctors/<id>/queue", auth=True,
                response=[{"number": "int", "time": "str", "patient": "str"}]),
        ],
        "frontend": ["frontend/index.html", "frontend/js/doctors.js", "frontend/visits.html", "frontend/js/visits.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "tournament": {
        "entities": {"team": {"id": "int", "name": "str"},
                     "match": {"id": "int", "home_id": "int", "away_id": "int", "home_score": "int", "away_score": "int"}},
        "endpoints": [
            *_crud("teams", "/api/teams", {"id": "int", "name": "str"}, public_read=True, update=False),
            _ep("matches.create", "POST", "/api/matches", auth=True,
                request={"home_id": "int", "away_id": "int", "home_score": "int", "away_score": "int"},
                response={"id": "int"}),
            _ep("matches.list", "GET", "/api/matches", response=[{"id": "int", "home": "str", "away": "str", "score": "str"}]),
            _ep("table.get", "GET", "/api/table", response=[{"team": "str", "played": "int", "wins": "int", "points": "int"}]),
        ],
        "frontend": ["frontend/index.html", "frontend/js/table.js", "frontend/matches.html", "frontend/js/matches.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
    "rental": {
        "entities": {"item": {"id": "int", "name": "str", "price_per_day": "int", "available": "bool"},
                     "booking": {"id": "int", "item_id": "int", "from": "str", "to": "str", "total": "int"}},
        "endpoints": [
            *_crud("items", "/api/rentals", {"id": "int", "name": "str", "price_per_day": "int", "available": "bool"},
                   public_read=True, update=False),
            _ep("bookings.create", "POST", "/api/rentals/<id>/book", auth=True, request={"from": "str", "to": "str"},
                response={"id": "int", "total": "int"}),
            _ep("bookings.mine", "GET", "/api/rental-bookings", auth=True,
                response=[{"id": "int", "item": "str", "from": "str", "to": "str", "total": "int"}]),
            _ep("bookings.cancel", "DELETE", "/api/rental-bookings/<id>", auth=True, response={"message": "str"}),
        ],
        "frontend": ["frontend/index.html", "frontend/js/rentals.js", "frontend/bookings.html", "frontend/js/bookings.js",
                     "frontend/login.html", "frontend/js/auth.js", "frontend/js/api.js", "frontend/css/styles.css"],
    },
}

# backend family -> (backend files, skeleton files, run commands)
_FAMILIES = {
    "django": {
        "backend": ["backend/api/models.py", "backend/api/views.py", "backend/api/urls.py"],
        "skeleton": ["README.md", "backend/requirements.txt", "backend/manage.py", "backend/config/settings.py"],
        "run": {"backend": "cd backend && pip install -r requirements.txt && python manage.py migrate && python manage.py runserver 5000",
                "frontend": "cd frontend && python -m http.server 8080  (backend: django-cors-headers allows it)"},
    },
    "fastapi": {
        "backend": ["backend/models.py", "backend/schemas.py", "backend/routes.py", "backend/security.py"],
        "skeleton": ["README.md", "backend/requirements.txt", "backend/main.py", "backend/database.py"],
        "run": {"backend": "cd backend && pip install -r requirements.txt && uvicorn main:app --port 5000",
                "frontend": "cd frontend && python -m http.server 8080  (backend: CORSMiddleware allows it)"},
    },
    "flask": {
        "backend": ["backend/models.py", "backend/routes.py"],
        "skeleton": ["README.md", "backend/requirements.txt", "backend/app.py"],
        "run": {"backend": "cd backend && pip install -r requirements.txt && python app.py",
                "frontend": "backend serves frontend/ at http://127.0.0.1:5000/"},
    },
    "express": {
        "backend": ["backend/routes/index.js", "backend/controllers/index.js"],
        "skeleton": ["README.md", "backend/package.json", "backend/server.js"],
        "run": {"backend": "cd backend && npm install && node server.js",
                "frontend": "server.js serves frontend/ at http://127.0.0.1:5000/"},
    },
}


def backend_family(stack_key: str) -> str:
    return stack_key if stack_key in ("express", "django", "fastapi") else "flask"


def _build(theme: str, family: str) -> dict:
    t, f = _THEMES[theme], _FAMILIES[family]
    auth_eps = [copy.deepcopy(_REGISTER), copy.deepcopy(_LOGIN)]
    return {
        "theme": theme, "backend_family": family,
        "base_url": BASE_URL, "cors": True, "auth": dict(_AUTH),
        "entities": copy.deepcopy(t["entities"]),
        "endpoints": auth_eps + copy.deepcopy(t["endpoints"]),
        "files": {"skeleton": list(f["skeleton"]), "backend": list(f["backend"]), "frontend": list(t["frontend"])},
        "run": dict(f["run"]),
        "requires": lesson_needs(theme, family),
    }


BLUEPRINTS = {(theme, fam): _build(theme, fam) for theme in _THEMES for fam in _FAMILIES}


def get_blueprint(theme: str, stack_key: str) -> dict:
    """A fresh copy (callers may serialize or annotate it). Raises BlueprintMissing."""
    try:
        return copy.deepcopy(BLUEPRINTS[(theme, backend_family(stack_key))])
    except KeyError:
        raise BlueprintMissing(f"{theme}/{backend_family(stack_key)}")


def endpoint_ids(blueprint: dict) -> list[str]:
    return [e["id"] for e in blueprint["endpoints"]]


def all_files(blueprint: dict) -> list[str]:
    return [f for group in ("skeleton", "backend", "frontend") for f in blueprint["files"][group]]


def endpoint_label(endpoint: dict) -> str:
    return f"{endpoint['method']} {endpoint['path']}"
