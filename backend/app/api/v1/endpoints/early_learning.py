"""Early-learning (age 5-8) modules & activities — read-only content plus a
single "submit completion" write action. See app/models/early_learning.py
for the model design rationale (star-based, ungraded, deliberately separate
from the points/achievements system) and
backend/scripts/_seed_early_learning.py for how content gets in.
"""
import json
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db, get_current_student
from app.models.early_learning import EarlyActivity, EarlyActivityCompletion, EarlyModule
from app.models.user import Student
from app.schemas.early_learning import (
    EarlyActivityCompleteIn,
    EarlyActivityCompleteOut,
    EarlyActivityOut,
    EarlyModuleDetail,
    EarlyModuleListItem,
)

router = APIRouter()


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


def _list_item(module: EarlyModule, completions: Dict[int, EarlyActivityCompletion]) -> EarlyModuleListItem:
    activities = _visible_activities(module)
    earned = sum(completions[a.id].stars_earned for a in activities if a.id in completions)
    return EarlyModuleListItem(
        id=module.id,
        title=module.title,
        description=module.description,
        subject=module.subject,
        icon_emoji=module.icon_emoji,
        color_accent=module.color_accent,
        display_order=module.display_order,
        activities_count=len(activities),
        earned_stars=earned,
        max_stars=sum(a.max_stars for a in activities),
    )


def _activity_out(activity: EarlyActivity, completion: EarlyActivityCompletion | None) -> EarlyActivityOut:
    try:
        content = json.loads(activity.content_json)
    except (TypeError, ValueError):
        content = {}
    return EarlyActivityOut(
        id=activity.id,
        title=activity.title,
        order=activity.order,
        activity_type=activity.activity_type,
        instruction_text=activity.instruction_text,
        content=content,
        max_stars=activity.max_stars,
        best_stars=completion.stars_earned if completion else 0,
        attempts=completion.attempts if completion else 0,
    )


@router.get("/modules", response_model=List[EarlyModuleListItem])
async def list_early_modules(
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

    activity_ids = [a.id for m in modules for a in _visible_activities(m)]
    completions = await _completions_by_activity(db, current_student.id, activity_ids)
    return [_list_item(m, completions) for m in modules]


@router.get("/modules/{module_id}", response_model=EarlyModuleDetail)
async def get_early_module(
    module_id: int,
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
    if module is None or not module.is_published or not module.is_active:
        raise HTTPException(status_code=404, detail="Modul topilmadi")

    activities = sorted(_visible_activities(module), key=lambda a: a.order)
    completions = await _completions_by_activity(db, current_student.id, [a.id for a in activities])

    base = _list_item(module, completions)
    return EarlyModuleDetail(
        **base.model_dump(),
        activities=[_activity_out(a, completions.get(a.id)) for a in activities],
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
