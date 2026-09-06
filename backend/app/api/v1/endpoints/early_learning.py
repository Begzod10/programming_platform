"""Early-learning (age 5-8) modules & activities — read-only content plus a
single "submit completion" write action. See app/models/early_learning.py
for the model design rationale (star-based, ungraded, deliberately separate
from the points/achievements system) and
backend/scripts/_seed_early_learning.py for how content gets in.
"""
import json
from datetime import date
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db, get_current_student
from app.models.early_learning import EarlyActivity, EarlyActivityCompletion, EarlyModule
from app.models.user import Student, UserRole
from app.schemas.early_learning import (
    EarlyActivityCompleteIn,
    EarlyActivityCompleteOut,
    EarlyActivityOut,
    EarlyLeaderboardEntry,
    EarlyLeaderboardOut,
    EarlyModuleDetail,
    EarlyModuleListItem,
)
from app.services.teacher_students import classmate_ids_subquery

router = APIRouter()

# The whole feature is authored in Uzbek first (EarlyModule/EarlyActivity's
# own source_lang) with an optional Russian rendering stored alongside each
# translatable field (title_ru / description_ru / instruction_text_ru, plus
# label_ru inside a mode="select" activity's content_json — see
# _seed_early_learning.py). ?lang picks which one comes back; a field with
# no ru translation yet falls back to uz rather than going blank or 404ing,
# same fallback rule already used for age-gating's "unknown data → allow".
_LangQuery = Query("uz", pattern="^(uz|ru)$")


def _localized(uz_value: str | None, ru_value: str | None, lang: str) -> str | None:
    if lang == "ru" and ru_value:
        return ru_value
    return uz_value


def _localize_items(items: list | None, lang: str) -> list | None:
    """Translate a list of {label, label_ru, ...} item dicts — shared by both
    of the content shapes below (mode="select"'s correct/distractor_items,
    mode="build"'s slots/distractor_items), same per-occurrence label_ru
    authoring convention either way (see _seed_early_learning.py)."""
    if not items:
        return items
    return [
        {**item, "label": item["label_ru"]} if item.get("label_ru") else item
        for item in items
    ]


_LOCALIZED_ITEM_KEYS = {
    "select": ("correct_items", "distractor_items"),
    "build": ("slots", "distractor_items"),
    "trace": ("targets",),
    # maze has no per-cell labels to translate — an empty tuple still routes
    # through the mode not None check below, so the character (translated
    # unconditionally, right after) still gets its ru rendering.
    "maze": (),
}


def _localize_content(content: dict, lang: str) -> dict:
    """Only mode="select" (tap-to-match), mode="build" (drag-to-assemble),
    mode="trace" (trace-the-outline) and mode="maze" (arrow pathfinding)
    carry translations today — any other content shape (the draft literacy/
    math/creative modules) just renders in uz regardless of `lang` until it
    gets its own translation pass; that's a content gap, not a bug.
    """
    mode = content.get("mode")
    item_keys = _LOCALIZED_ITEM_KEYS.get(mode)
    if lang != "ru" or item_keys is None:
        return content
    character = content.get("character")
    if character and character.get("label_ru"):
        content = {**content, "character": {**character, "label": character["label_ru"]}}
    for key in item_keys:
        content = {**content, key: _localize_items(content.get(key), lang)}
    return content


async def _completions_by_activity(
    db: AsyncSession, student_id: int, activity_ids: List[int]
) -> Dict[int, EarlyActivityCompletion]:
    if not activity_ids:
        return {}
    rows = (
        await db.execute(
            select(EarlyActivityCompletion).where(
                EarlyActivityCompletion.student_id == student_id,
                EarlyActivityCompletion.activity_id.in_(activity_ids),
            )
        )
    ).scalars().all()
    return {row.activity_id: row for row in rows}


def _visible_activities(module: EarlyModule) -> List[EarlyActivity]:
    return [a for a in module.activities if a.is_active and a.is_published]


# Grace band around a module's own age_min/age_max — this was always meant
# to be a soft, advisory range (see EarlyModule's docstring), not a razor
# cutoff that excludes a real kid a few months either side of it.
_AGE_GRACE_YEARS = 2


def _age_from_birth_date(birth_date: date) -> int:
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def _is_age_eligible(student: Student, module: EarlyModule) -> bool:
    """Whether `student` should see `module` at all.

    Most accounts have no birth_date yet (every gennis-synced student, plus
    turon students who haven't logged in/been rostered since the sync
    started carrying it — see gennis_service.py), so this can only ever
    exclude a CONFIRMED mismatch, never require proof of eligibility —
    doing the latter would lock out nearly everyone, including the actual
    5-8 year olds this is for. Teachers always pass, matching the existing
    teacher-preview access to this whole feature (see EarlyLearning.js /
    TeacherSidebar.js) — the point of gating is keeping the feature scoped
    to young kids among *students*, not hiding it from staff previewing it.
    """
    if student.role != UserRole.student:
        return True
    if student.birth_date is None:
        return True
    age = _age_from_birth_date(student.birth_date)
    return (module.age_min - _AGE_GRACE_YEARS) <= age <= (module.age_max + _AGE_GRACE_YEARS)


def _list_item(
    module: EarlyModule, completions: Dict[int, EarlyActivityCompletion], lang: str = "uz"
) -> EarlyModuleListItem:
    activities = _visible_activities(module)
    earned = sum(completions[a.id].stars_earned for a in activities if a.id in completions)
    return EarlyModuleListItem(
        id=module.id,
        title=_localized(module.title, module.title_ru, lang),
        description=_localized(module.description, module.description_ru, lang),
        subject=module.subject,
        icon_emoji=module.icon_emoji,
        color_accent=module.color_accent,
        display_order=module.display_order,
        activities_count=len(activities),
        earned_stars=earned,
        max_stars=sum(a.max_stars for a in activities),
    )


def _activity_out(
    activity: EarlyActivity, completion: EarlyActivityCompletion | None, lang: str = "uz"
) -> EarlyActivityOut:
    try:
        content = json.loads(activity.content_json)
    except (TypeError, ValueError):
        content = {}
    return EarlyActivityOut(
        id=activity.id,
        title=_localized(activity.title, activity.title_ru, lang),
        order=activity.order,
        activity_type=activity.activity_type,
        instruction_text=_localized(activity.instruction_text, activity.instruction_text_ru, lang),
        content=_localize_content(content, lang),
        max_stars=activity.max_stars,
        best_stars=completion.stars_earned if completion else 0,
        attempts=completion.attempts if completion else 0,
    )


@router.get("/modules", response_model=List[EarlyModuleListItem])
async def list_early_modules(
    lang: str = _LangQuery,
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> List[EarlyModuleListItem]:
    """Published, active modules for the module-picker grid, ordered for
    display, each carrying the current student's star progress."""
    modules = (
        await db.execute(
            select(EarlyModule)
            .where(EarlyModule.is_published.is_(True), EarlyModule.is_active.is_(True))
            .options(selectinload(EarlyModule.activities))
            .order_by(EarlyModule.display_order)
        )
    ).scalars().all()
    modules = [m for m in modules if _is_age_eligible(current_student, m)]

    activity_ids = [a.id for m in modules for a in _visible_activities(m)]
    completions = await _completions_by_activity(db, current_student.id, activity_ids)
    return [_list_item(m, completions, lang) for m in modules]


@router.get("/modules/{module_id}", response_model=EarlyModuleDetail)
async def get_early_module(
    module_id: int,
    lang: str = _LangQuery,
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> EarlyModuleDetail:
    """One module's activities, each carrying the student's best-attempt
    stars so the grid can show filled/empty stars without a second call."""
    module = (
        await db.execute(
            select(EarlyModule)
            .where(EarlyModule.id == module_id)
            .options(selectinload(EarlyModule.activities))
        )
    ).scalar_one_or_none()
    if (
        module is None
        or not module.is_published
        or not module.is_active
        or not _is_age_eligible(current_student, module)
    ):
        raise HTTPException(status_code=404, detail="Modul topilmadi")

    activities = sorted(_visible_activities(module), key=lambda a: a.order)
    completions = await _completions_by_activity(db, current_student.id, [a.id for a in activities])

    base = _list_item(module, completions, lang)
    return EarlyModuleDetail(
        **base.model_dump(),
        activities=[_activity_out(a, completions.get(a.id), lang) for a in activities],
    )


@router.post("/activities/{activity_id}/complete", response_model=EarlyActivityCompleteOut)
async def complete_early_activity(
    activity_id: int,
    payload: EarlyActivityCompleteIn,
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> EarlyActivityCompleteOut:
    """Record one play-through. Retryable and ungraded (see
    EarlyActivityCompletion's docstring), so this is an upsert keyed on
    (student, activity) — attempts always increments, stars_earned only
    ever moves up, matching how a kid replaying a round to improve their
    score should work.
    """
    activity = (
        await db.execute(
            select(EarlyActivity)
            .where(EarlyActivity.id == activity_id)
            .options(selectinload(EarlyActivity.module))
        )
    ).scalar_one_or_none()
    if (
        activity is None
        or not activity.is_active
        or not activity.is_published
        or not activity.module.is_active
        or not activity.module.is_published
        or not _is_age_eligible(current_student, activity.module)
    ):
        raise HTTPException(status_code=404, detail="Faoliyat topilmadi")

    existing = (
        await db.execute(
            select(EarlyActivityCompletion).where(
                EarlyActivityCompletion.student_id == current_student.id,
                EarlyActivityCompletion.activity_id == activity_id,
            )
        )
    ).scalar_one_or_none()

    if existing is None:
        existing = EarlyActivityCompletion(
            student_id=current_student.id,
            activity_id=activity_id,
            stars_earned=payload.stars,
            attempts=1,
        )
        db.add(existing)
    else:
        existing.attempts += 1
        existing.stars_earned = max(existing.stars_earned, payload.stars)

    await db.commit()
    await db.refresh(existing)
    return EarlyActivityCompleteOut.model_validate(existing)


@router.get("/leaderboard", response_model=EarlyLeaderboardOut)
async def get_early_learning_leaderboard(
    limit: int = 20,
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> EarlyLeaderboardOut:
    """Rank the current student against their own classmates (anyone who
    shares a teacher-owned Group or Flow with them — see
    classmate_ids_subquery) by total stars earned across every published
    early-learning activity. Deliberately not platform-wide: a 6-year-old
    doesn't know or care about a stranger three schools over, and turning
    this into a global ranking would just be discouraging noise for most
    kids. A student with no Group/Flow membership at all gets
    has_class=False instead of a lonely one-row leaderboard.
    """
    limit = max(1, min(limit, 100))
    classmate_ids = (
        await db.execute(select(classmate_ids_subquery(current_student.id).c.student_id))
    ).scalars().all()
    has_class = len(classmate_ids) > 0
    if not has_class:
        classmate_ids = [current_student.id]

    stars_rows = (
        await db.execute(
            select(
                EarlyActivityCompletion.student_id,
                func.sum(EarlyActivityCompletion.stars_earned).label("total_stars"),
            )
            .join(EarlyActivity, EarlyActivity.id == EarlyActivityCompletion.activity_id)
            .where(
                EarlyActivityCompletion.student_id.in_(classmate_ids),
                EarlyActivity.is_published.is_(True),
                EarlyActivity.is_active.is_(True),
            )
            .group_by(EarlyActivityCompletion.student_id)
        )
    ).all()
    stars_by_student = {row.student_id: row.total_stars for row in stars_rows}

    classmates = (
        await db.execute(
            select(Student.id, Student.full_name, Student.username, Student.avatar_url)
            .where(Student.id.in_(classmate_ids))
        )
    ).all()

    ranked = sorted(
        classmates,
        key=lambda s: stars_by_student.get(s.id, 0),
        reverse=True,
    )[:limit]

    entries = [
        EarlyLeaderboardEntry(
            student_id=s.id,
            name=s.full_name or s.username,
            avatar_url=s.avatar_url,
            total_stars=stars_by_student.get(s.id, 0),
            rank=i + 1,
            is_me=(s.id == current_student.id),
        )
        for i, s in enumerate(ranked)
    ]
    return EarlyLeaderboardOut(has_class=has_class, entries=entries)
