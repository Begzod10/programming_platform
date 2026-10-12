"""Team-project deadlines that follow the work instead of one flat number.

A flat 5-day deadline for tasks of 6-20 hours, with the frontend waiting on the backend, is why
pieces were never integrated. Recommended length = critical path / 2.5 hours a day + 3 days to
integrate, between 7 and 21 days; the backend piece is due early (40%) so frontends can integrate
against the real thing, frontends at 75%, and the lead's integration (the whole `days`) comes last.
"""
import math
from datetime import datetime, timedelta

MIN_DAYS = 7
MAX_DAYS = 21
HOURS_PER_DAY = 2.5          # what a student realistically gives a team project per day
INTEGRATION_DAYS = 3
BACKEND_STAGE = 0.40
FRONTEND_STAGE = 0.75
# A plan does not exist yet when the teacher creates the assignment, so the creation-time
# warning uses a typical backend-then-frontend chain (see blueprints: ~8h + ~8h).
TYPICAL_CRITICAL_PATH_HOURS = 16


def critical_path_hours(tasks: list[dict]) -> float:
    """Longest chain of `depends_on` by estimated hours. Tolerates dangling references and cycles
    (the plan validator rejects them, but a deadline calculation must never hang or crash)."""
    n = len(tasks)
    hours = [float(t.get("estimated_hours") or 0) for t in tasks]
    memo: dict[int, float] = {}

    def longest(i: int, seen: frozenset) -> float:
        if i in memo:
            return memo[i]
        deps = [d for d in (tasks[i].get("depends_on") or []) if isinstance(d, int) and 0 <= d < n and d != i and d not in seen]
        best = hours[i] + max((longest(d, seen | {i}) for d in deps), default=0.0)
        if not seen:
            memo[i] = best
        return best

    return max((longest(i, frozenset()) for i in range(n)), default=0.0)


def recommended_days(critical_hours: float) -> int:
    return max(MIN_DAYS, min(MAX_DAYS, math.ceil(critical_hours / HOURS_PER_DAY) + INTEGRATION_DAYS))


def _is_backend(task: dict) -> bool:
    files = (task.get("interface_contract") or {}).get("files") or []
    return any(isinstance(f, str) and f.startswith("backend/") for f in files)


def stage_deadlines(tasks: list[dict], start: datetime, days: int) -> dict[int, datetime]:
    """{task index: deadline}. Backend-containing tasks at 40% of `days`, everything else at 75%."""
    return {
        i: start + timedelta(days=max(days * (BACKEND_STAGE if _is_backend(t) else FRONTEND_STAGE), 0.5))
        for i, t in enumerate(tasks)
    }
