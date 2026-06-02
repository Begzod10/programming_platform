from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_student, get_db
from app.models.project import Project
from app.models.user import Student
from app.services.ai_review_service import run_ai_review_for_project

router = APIRouter()


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
