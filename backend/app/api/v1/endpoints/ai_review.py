from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_current_student, get_db
from app.models.project import Project
from app.models.user import Student
from app.services.ai_review_service import (
    count_reviews_today,
    run_ai_review_for_project,
)

router = APIRouter()


@router.get("/quota")
async def ai_quota(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db),
):
    """Today's AI-review budget for the current student.

    The lesson page reads this to disable the project-submit button once
    the daily cap is reached, so a student never submits into a dead-end
    (the auto-review would otherwise be skipped and the project left
    pending — see run_ai_review_for_project). Uses the same
    count_reviews_today the review pipeline enforces, so the button and
    the server agree on when submission is allowed.
    """
    used = await count_reviews_today(db, current_student.id)
    limit = settings.MAX_AI_REVIEWS_PER_DAY
    remaining = max(0, limit - used)
    return {
        "used_today": used,
        "limit": limit,
        "remaining": remaining,
        "can_submit": remaining > 0,
    }


@router.post("/{project_id}/ai-review")
async def ai_review(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db),
):
    """Manual AI review trigger from the MyProjects page.

    The same logic also runs automatically when a student submits a
    project from the lesson page (see project_service.submit_project) —
    both paths go through run_ai_review_for_project to keep behavior
    consistent. This endpoint exists so students can re-trigger if the
    auto-review was skipped or they uploaded a ZIP after submission.
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")
    if project.student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    # raise_on_error=True → bad URL / quota / AI failure surface as
    # HTTPException with the right status code (400 / 429 / 502).
    review = await run_ai_review_for_project(db, project, raise_on_error=True)
    return {"message": "AI baholash yakunlandi!", **review}
