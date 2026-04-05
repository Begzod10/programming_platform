from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json

from app.dependencies import get_db, get_current_student
from app.models.project import Project
from app.models.user import Student
from app.services.grok_service import analyze_project_with_grok
from app.schemas.ai_review import AIReviewResponse, AIReviewResult

router = APIRouter()


@router.post("/{project_id}/ai-review")
async def ai_review(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """AI orqali loyihani baholash"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")
    if project.student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    if not project.github_url:
        raise HTTPException(status_code=400, detail="AI baholash uchun GitHub URL kerak")

    technologies = project.technologies_used.split(",") if project.technologies_used else []

    review = await analyze_project_with_grok(
        title=project.title,
        description=project.description or "",
        github_url=project.github_url,
        technologies=technologies,
        difficulty_level=str(project.difficulty_level or "Easy")
    )

    new_points = review.get("points", 60)
    old_points = project.points_earned or 0

    # Eski ballni ayirib, yangi ball qo'shamiz
    ranking_service = RankingService(db)
    if old_points > 0:
        await ranking_service.subtract_points_from_student(project.student_id, old_points)
    await ranking_service.add_points_to_student(project.student_id, new_points)

    project.instructor_feedback = review.get("feedback", "")
    project.grade = review.get("grade", "C")
    project.points_earned = new_points
    project.status = "Approved"
    project.reviewed_at = datetime.utcnow()

    await db.commit()

    return {
        "message": "AI baholash yakunlandi!",
        "project_id": project_id,
        "old_points": old_points,
        "new_points": new_points,
        **review
    }