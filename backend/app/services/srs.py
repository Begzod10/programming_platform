"""Spaced-repetition scheduler (SM-2 variant).

Ported from life_tracker's `app/services/srs.py`. Pure functions: no ORM
imports here. Callers pass the SQLAlchemy mapped class as the `Word`
argument so the module stays unit-testable.

Cards diverge by individual difficulty:
  - ease_factor   per-card growth multiplier (default 2.5, floor 1.3)
  - reps          consecutive-success counter, resets on lapse
  - lapses        lifetime forget count, feeds leech + weak detection

`apply_result` accepts a 3-level grade (0/1/2) but also accepts the
legacy binary `was_correct` for flashcard / MCQ flows.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy import case, func, or_, select


# ─── Tunables ────────────────────────────────────────────────────────────────
DEFAULT_EASE = 2.5
MIN_EASE = 1.3
EASE_LAPSE_PENALTY = 0.20   # subtracted when a learned card is forgotten
EASE_HARD_PENALTY = 0.15    # subtracted on a "hard" (close-but-not-exact) pass
FIRST_INTERVAL = 1          # days, after the 1st success
SECOND_INTERVAL = 3         # days, after the 2nd success (gentle for new learners)
HARD_MULTIPLIER = 1.2       # growth for a "hard" pass (vs ease_factor for "good")
FUZZ_RATIO = 0.10           # +/- jitter on intervals >= 2 days
WEAK_EASE = 2.0             # below this ease, a card is "fragile"
FRAGILE_LAPSES = 2          # at or above this lapse count, "fragile"
LEARNING_MAX_INT = 7        # days — upper bound of "learning" bucket
SOLID_MAX_INT = 21          # days — upper bound of "solid" bucket
LEECH_LAPSES = 5            # surface as a leech after this many lapses


# ─── Core scheduler ──────────────────────────────────────────────────────────

def _fuzz(interval_days: int) -> int:
    """Spread due dates so a big cohort doesn't all land on the same day."""
    if interval_days < 2:
        return interval_days
    delta = max(1, round(interval_days * FUZZ_RATIO))
    return interval_days + random.randint(-delta, delta)


def schedule_after_review(
    *,
    reps: int,
    lapses: int,
    ease_factor: float,
    interval_days: int,
    grade: int,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Given a card's SR state + a grade, return the next state.

    grade: 0 = wrong/forgot, 1 = hard (close), 2 = good (exact/correct).
    """
    now = now or datetime.utcnow()
    ef = ease_factor or DEFAULT_EASE

    if grade == 0:
        # Lapse: penalise ease, reset progress, requeue immediately so the
        # word reappears in the very next session. The priority sort in
        # pool_priority_order depends on this invariant.
        lapses += 1
        reps = 0
        ef = max(MIN_EASE, ef - EASE_LAPSE_PENALTY)
        return {
            "reps": reps,
            "lapses": lapses,
            "ease_factor": round(ef, 2),
            "interval_days": 0,
            "next_review_at": now,
            "is_leech": lapses >= LEECH_LAPSES,
        }

    if reps == 0:
        new_interval = FIRST_INTERVAL
    elif reps == 1:
        new_interval = SECOND_INTERVAL
    else:
        mult = HARD_MULTIPLIER if grade == 1 else ef
        # Never let a successful pass shrink or stall the interval.
        new_interval = max(interval_days + 1, round(interval_days * mult))

    if grade == 1:
        ef = max(MIN_EASE, ef - EASE_HARD_PENALTY)

    reps += 1
    new_interval = _fuzz(new_interval)
    return {
        "reps": reps,
        "lapses": lapses,
        "ease_factor": round(ef, 2),
        "interval_days": new_interval,
        "next_review_at": now + timedelta(days=new_interval),
        "is_leech": lapses >= LEECH_LAPSES,
    }


# ─── Grade mapping ───────────────────────────────────────────────────────────

def grade_from_close_match(result: dict) -> int:
    """Map a typed-answer close-match dict ({ok, exact}) to a 3-level grade.

    exact          -> 2 (good)
    close (1-2 ed) -> 1 (hard)  — smaller interval bump + ease penalty
    wrong          -> 0 (lapse)
    """
    if not result.get("ok"):
        return 0
    return 2 if result.get("exact") else 1


# ─── apply_result: orchestrates an ORM word + a graded answer ────────────────

def apply_result(
    word: Any,
    *,
    grade: Optional[int] = None,
    was_correct: Optional[bool] = None,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Update a UserDictionary row in place with the next SR state.

    Backward compatible: callers can pass either `grade` (preferred) or the
    legacy `was_correct`. Returns the scheduler dict so the response can
    surface `is_leech` for client-side flagging.
    """
    now = now or datetime.utcnow()
    if grade is None:
        grade = 2 if was_correct else 0

    word.review_count = (word.review_count or 0) + 1
    if grade != 0:
        word.correct_count = (word.correct_count or 0) + 1
    else:
        word.incorrect_count = (word.incorrect_count or 0) + 1
    word.last_reviewed_at = now

    sched = schedule_after_review(
        reps=word.reps or 0,
        lapses=word.lapses or 0,
        ease_factor=word.ease_factor or DEFAULT_EASE,
        interval_days=word.interval_days or 0,
        grade=grade,
        now=now,
    )
    word.reps = sched["reps"]
    word.lapses = sched["lapses"]
    word.ease_factor = sched["ease_factor"]
    word.interval_days = sched["interval_days"]
    word.next_review_at = sched["next_review_at"]
    return sched


# ─── Retention buckets + shared "fragile" predicate ──────────────────────────

def is_fragile(Word):
    """Struggle signal, independent of interval. Shared by the stats
    "fragile" bucket and the practice weak_only filter so the two never
    drift apart.

    A card is fragile when either:
      - lapses >= FRAGILE_LAPSES  (forgotten more than once), or
      - ease_factor < WEAK_EASE   (chronically hard, leech-ish).

    Note: never-reviewed cards do NOT match — they're not fragile, they're
    untouched. They land in "learning" via bucket_expr below.
    """
    return or_(Word.lapses >= FRAGILE_LAPSES, Word.ease_factor < WEAK_EASE)


def bucket_expr(Word):
    """SQLAlchemy CASE mapping a word's current state to one of four
    learner-meaningful buckets. First match wins.

    Fragile is checked FIRST so a long-interval word the learner keeps
    relapsing on is classed fragile, not mastered.
    """
    return case(
        (is_fragile(Word), "fragile"),
        (Word.interval_days <= LEARNING_MAX_INT, "learning"),
        (Word.interval_days <= SOLID_MAX_INT, "solid"),
        else_="mastered",
    )


def weak_condition(Word):
    """Practice /words?weak_only=true filter."""
    return is_fragile(Word)


# ─── Default /practice/words priority ────────────────────────────────────────

def pool_priority_order(Word, now: datetime):
    """Coverage-aware, ease-weighted ordering for the default practice pool.

        bucket 0: due now / just-missed   (next_review_at <= now or null)
        bucket 1: never reviewed          (oldest first)
        then    : hardest first (low ease), then shortest interval
    """
    pri = case(
        (or_(Word.next_review_at.is_(None), Word.next_review_at <= now), 0),
        (Word.review_count == 0, 1),
        else_=2,
    )
    return [
        pri.asc(),
        Word.ease_factor.asc(),
        Word.interval_days.asc(),
        Word.created_at.asc(),
    ]
