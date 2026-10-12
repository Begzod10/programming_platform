"""Ready-made API contracts ("blueprints") for team projects, one per (theme, backend family).

The AI planner used to invent the contract between a team's pieces, and invented it badly:
the backend task said "clients", the frontend tasks called "/api/customers". A blueprint is
fixed, hand-written data — endpoints, JSON shapes, token key, file layout, run commands —
that the planner may SPLIT among members but never change. See
docs/superpowers/specs/2026-10-12-team-project-planning-design.md §4.3.

Themes are described once (`_THEMES`) and expanded per backend family (`flask`, `express`) so the
two stay in step; only file names and run commands differ between families.
"""
import copy
from typing import Optional

BASE_URL = "http://127.0.0.1:5000"
TOKEN_KEY = "auth_token"
_AUTH = {"header": "Authorization: Bearer <token>", "token_key": TOKEN_KEY}


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
}

# backend family -> (backend files, skeleton files, run commands)
_FAMILIES = {
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
    return "express" if stack_key == "express" else "flask"


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
