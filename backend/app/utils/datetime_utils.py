"""Single source of truth for "now" in UTC, timezone-aware.

`datetime.utcnow()` is deprecated (Python 3.12+) and returns a NAIVE
datetime that silently misbehaves when compared against/assigned to a
`DateTime(timezone=True)` column (most of this codebase's timestamp
columns — see app/models/*.py). `utcnow()` here always returns an aware
UTC datetime; use it everywhere instead of `datetime.utcnow()`.

Several models (project.py, team_game.py, lesson_file.py,
lesson_question.py, translation_cache.py) previously each defined their
own identical local `utcnow()`/`_utcnow()` helper — consolidated here so
the policy lives in one place; those files now import from here instead.

For the rare column that's genuinely naive (no `timezone=True`) and must
stay that way, call `utcnow().replace(tzinfo=None)` at the call site with
a comment explaining why, rather than reaching for `datetime.utcnow()`.
"""
from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
