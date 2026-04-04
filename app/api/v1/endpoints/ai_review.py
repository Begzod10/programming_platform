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


@router.post("/projects/{project_id}/ai-review", response_model=AIReviewResponse)
async def ai_review_project(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_student: Student = Depends(get_current_student)
):
    """
    O'quvchi proektini Grok AI yordamida tahlil qiladi va baho beradi.
    Faqat proekt egasi yoki admin chaqira oladi.
    """
    # Proektni olish
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Proekt topilmadi")

    if project.student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Bu proektni baholashga ruxsat yo'q")

    # Texnologiyalarni parse qilish
    technologies = []
    if project.technologies_used:
        try:
            technologies = json.loads(project.technologies_used)
        except Exception:
            technologies = [t.strip() for t in project.technologies_used.split(",") if t.strip()]

    # Grok AI ga yuborish
    try:
        ai_result = await analyze_project_with_grok(
            title=project.title,
            description=project.description,
            github_url=project.github_url or "",
            technologies=technologies,
            difficulty_level=project.difficulty_level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI tahlil xatosi: {str(e)}")

    # Natijani bazaga saqlash
    project.grade = ai_result.get("grade", "C")
    project.points_earned = ai_result.get("points", 60)
    project.instructor_feedback = ai_result.get("feedback", "")
    project.status = "Approved"

    await db.commit()
    await db.refresh(project)

    return AIReviewResponse(
        project_id=project_id,
        ai_review=AIReviewResult(**ai_result),
        message="AI tahlil muvaffaqiyatli bajarildi"
    )