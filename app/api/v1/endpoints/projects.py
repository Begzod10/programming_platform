import os
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, status, Query, HTTPException, Body, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.dependencies import get_db, get_current_student, get_current_instructor
from app.models.project import Project
from app.models.user import Student
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead
from app.services.project_service import ProjectService
from app.services.ranking_service import RankingService
from app.services.grok_service import analyze_project_with_grok
from app.config import settings

router = APIRouter()


def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


# ============ STUDENT ENDPOINTS ============

@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
        payload: ProjectCreate,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Yangi proyekt yaratish"""
    return await service.create_project(student_id=current_student.id, data=payload)


@router.get("/", response_model=List[ProjectRead])
async def get_projects(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        service: ProjectService = Depends(get_project_service),
):
    """Barcha proyektlar"""
    return await service.get_all_projects(skip=skip, limit=limit)


@router.get("/my", response_model=List[ProjectRead])
async def get_my_projects(
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Mening proyektlarim"""
    return await service.get_all_projects_by_student(student_id=current_student.id)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
        project_id: int,
        service: ProjectService = Depends(get_project_service),
):
    """Proyektni ko'rish"""
    project = await service.get_project(project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")
    return project


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
        project_id: int,
        payload: ProjectUpdate,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Proyektni yangilash"""
    return await service.update_project(
        project_id=project_id,
        student_id=current_student.id,
        data=payload
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Proyektni o'chirish"""
    await service.delete_project(project_id=project_id, student_id=current_student.id)


@router.post("/{project_id}/submit", response_model=ProjectRead)
async def submit_project(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Proyektni topshirish"""
    return await service.submit_project(
        project_id=project_id,
        student_id=current_student.id
    )


@router.post("/{project_id}/upload-zip")
async def upload_project_zip(
        project_id: int,
        file: UploadFile = File(...),
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Zip fayl yuklash (max 15MB)"""
    ext = os.path.splitext(file.filename or "")[-1].lower()
    if ext != ".zip":
        raise HTTPException(status_code=400, detail="Faqat .zip fayl qabul qilinadi")

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")
    if project.student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    contents = await file.read()
    if len(contents) > 15 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"Fayl 15MB dan oshmasligi kerak. Hozir: {len(contents) / 1024 / 1024:.1f}MB"
        )

    upload_dir = os.path.join(settings.UPLOAD_DIR, "projects", str(project_id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"project_{project_id}.zip")
    with open(file_path, "wb") as f:
        f.write(contents)

    file_url = f"/uploads/projects/{project_id}/project_{project_id}.zip"
    project.project_files = file_url
    await db.commit()

    return {
        "message": "Zip fayl yuklandi!",
        "file_url": file_url,
        "file_size_mb": round(len(contents) / 1024 / 1024, 2)
    }


@router.post("/{project_id}/ai-review")
async def ai_review(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """AI orqali loyihani baholash (github yoki zip)"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")
    if project.student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    if not project.github_url:
        raise HTTPException(status_code=400, detail="AI baholash uchun GitHub URL kerak")

    technologies = project.technologies_used.split(",") if project.technologies_used else []
    old_points = project.points_earned if project.points_earned else 0
    review = await analyze_project_with_grok(
        title=project.title,
        description=project.description or "",
        github_url=project.github_url,
        technologies=technologies,
        difficulty_level=str(project.difficulty_level or "Easy"),
        previous_points=old_points  # ✅ qo'shildi
    )
    new_points = review.get("points", 60)

    old_points = project.points_earned if project.points_earned else 0
    print(f"DEBUG: project_id={project_id}, old_points={old_points}, new_points biz hali bilmaymiz")
    print(f"DEBUG: project_id={project_id}, old_points={old_points}, new_points={new_points}")

    ranking_service = RankingService(db)

    if old_points > 0:
        await ranking_service.subtract_points_from_student(project.student_id, old_points)
        await ranking_service.add_points_to_student(project.student_id, new_points)
        diff = new_points - old_points
        if diff > 0:
            message = f"Ball oshdi! {old_points} → {new_points} (+{diff})"
        elif diff < 0:
            message = f"Ball kamaydi! {old_points} → {new_points} ({diff})"
        else:
            message = f"Ball o'zgarmadi: {new_points}"
    else:
        await ranking_service.add_points_to_student(project.student_id, new_points)
        message = f"Birinchi baholash! Ball: {new_points}"
    project.points_earned = new_points
    project.grade = review.get("grade", "C")
    project.instructor_feedback = review.get("feedback", "")
    project.status = "Approved"
    project.reviewed_at = datetime.utcnow()

    await db.commit()

    return {
        "message": message,
        "project_id": project_id,
        "old_points": old_points,
        "new_points": new_points,
        **review
    }


# ============ TEACHER ENDPOINTS ============

class ReviewProjectRequest(BaseModel):
    feedback: str
    grade: str
    points: int


@router.post("/{project_id}/review")
async def review_project(
        project_id: int,
        data: ReviewProjectRequest,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Loyihani tekshirish (faqat teacher)"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")
    if project.status == "Approved":
        raise HTTPException(status_code=400, detail="Bu loyiha allaqachon tasdiqlangan")

    old_points = project.points_earned if project.points_earned else 0
    ranking_service = RankingService(db)

    if old_points > 0:
        await ranking_service.subtract_points_from_student(project.student_id, old_points)

    await ranking_service.add_points_to_student(project.student_id, data.points)

    project.status = "Approved"
    project.instructor_feedback = data.feedback
    project.grade = data.grade
    project.points_earned = data.points
    project.reviewed_at = datetime.utcnow()

    await db.commit()
    return {"message": "Loyiha tasdiqlandi!", "points": data.points}


@router.patch("/{project_id}/status")
async def update_status(
        project_id: int,
        new_status: str = Body(..., embed=True),
        current_teacher: Student = Depends(get_current_instructor),
        service: ProjectService = Depends(get_project_service),
):
    """Status o'zgartirish (faqat teacher)"""
    return await service.update_status(project_id=project_id, status=new_status)


@router.patch("/{project_id}/grade")
async def update_grade(
        project_id: int,
        grade: str = Body(..., embed=True),
        current_teacher: Student = Depends(get_current_instructor),
        service: ProjectService = Depends(get_project_service),
):
    """Baho berish (faqat teacher)"""
    return await service.update_grade(project_id=project_id, grade=grade)


@router.patch("/{project_id}/difficulty")
async def update_difficulty(
        project_id: int,
        difficulty: str = Body(..., embed=True),
        current_teacher: Student = Depends(get_current_instructor),
        service: ProjectService = Depends(get_project_service),
):
    """Qiyinlik darajasini o'zgartirish (faqat teacher)"""
    return await service.update_difficulty(project_id=project_id, difficulty=difficulty)


@router.patch("/{project_id}/comment")
async def update_comment(
        project_id: int,
        comment: str = Body(..., embed=True),
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Izoh qo'shish"""
    return await service.update_comment(project_id=project_id, comment=comment)


@router.patch("/{project_id}/file")
async def update_file(
        project_id: int,
        file_url: str = Body(..., embed=True),
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Fayl urlini yangilash"""
    return await service.update_file(project_id=project_id, file_url=file_url)
