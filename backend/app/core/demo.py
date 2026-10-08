"""Demo accounts.

A prospective student who has not yet been enrolled in gennis can try the
platform by typing only a first and last name. The visitor:

  * is a normal `students` row flagged `is_demo` (role stays "student" so the
    student UI and lesson flow work unchanged), with an unguessable password
    and a short-lived token — there is nothing to log in with afterwards;
  * is enrolled in one course and may open only its first two lessons;
  * can read and answer the lessons' exercises but can NOT submit a project;
  * earns no points, has no ranking row and is excluded from every ranking,
    teacher/admin statistic and student count (see the `is_demo` filters);
  * is deleted automatically after `DEMO_RETENTION` (scheduler), so demo
    sign-ups never pile up and never count as deleted students.

The gate is a plain allow-list (`demo_allows`): anything not listed is refused
for a demo account, so a new endpoint is closed to demo users by default.
"""
from __future__ import annotations

import re
import secrets
from datetime import timedelta

# The demo course ("HTML CSS"): lesson 1 is the intro, lesson 2 ends in a
# project — which a demo visitor can read about but never submit.
DEMO_COURSE_ID = 9
DEMO_LESSON_IDS = frozenset({4, 5})

DEMO_TOKEN_LIFETIME = timedelta(days=3)
DEMO_RETENTION = timedelta(days=14)

DEMO_RESTRICTED_DETAIL = (
    "Demo rejimida bu imkoniyat yopiq. To'liq o'qishni boshlash uchun "
    "administratorga murojaat qiling."
)

_L = "|".join(str(i) for i in sorted(DEMO_LESSON_IDS))
_C = str(DEMO_COURSE_ID)

# (method, regex of the path below /api/v1)
_ALLOWED = [
    ("GET", r"/auth/me"),
    ("GET", r"/student/me"),
    ("GET", r"/student/me/course-stats"),
    ("GET", r"/ai/quota"),
    ("GET", r"/notifications/unread-count"),
    ("GET", r"/categories/?"),
    ("GET", r"/courses/?"),
    ("GET", rf"/courses/{_C}"),
    ("GET", rf"/courses/{_C}/progress"),
    ("GET", rf"/courses/{_C}/lessons"),
    ("GET", rf"/courses/{_C}/lessons/(?:{_L})"),
    ("GET", rf"/courses/{_C}/lessons/(?:{_L})/(?:download|submission|vocabulary)"),
    ("GET", rf"/courses/{_C}/lessons/(?:{_L})/exercises(?:/progress|/\d+|/\d+/my-submissions)?"),
    ("POST", rf"/courses/{_C}/lessons/(?:{_L})/exercises/\d+/submit"),
    ("POST", rf"/courses/{_C}/lessons/(?:{_L})/sections/[^/]+/watch"),
    ("GET", rf"/lessons/(?:{_L})/(?:my-exercise-submissions|is-completed|sample)"),
    ("GET", rf"/lessons/(?:{_L})/feedback/my"),
    ("GET", rf"/lessons/(?:{_L})/files(?:/\d+(?:/download)?)?"),
    ("POST", rf"/lessons/(?:{_L})/complete"),
]
_ALLOWED_RE = [(m, re.compile(rf"^{p}$")) for m, p in _ALLOWED]

_API_PREFIX = "/api/v1"


def demo_allows(method: str, path: str) -> bool:
    """May a demo account call `method path`? `path` includes /api/v1."""
    if path.startswith(_API_PREFIX):
        path = path[len(_API_PREFIX):]
    path = path.rstrip("/") if path != "/" else path
    # "/courses/" and "/categories/" are listed with an optional slash; the
    # rstrip above already normalised both, so match on the stripped form.
    return any(m == method.upper() and rx.match(path or "/") for m, rx in _ALLOWED_RE)


def new_demo_credentials() -> dict:
    """Throw-away identity for a demo account. Nobody ever logs in with these."""
    suffix = secrets.token_hex(5)
    return {
        "username": f"demo_{suffix}",
        "email": f"demo_{suffix}@demo.invalid",
        "password": secrets.token_urlsafe(32),
    }
