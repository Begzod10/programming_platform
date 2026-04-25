import os
import shutil
from fastapi import APIRouter, Depends, status, Query, HTTPException, Body, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from app.models.project import Project
from app.models.lesson import Lesson
from app.models.submission import Submission

from app.dependencies import get_db, get_current_student, get_current_instructor
from app.services.project_service import ProjectService
from app.services import achievement_service
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead
from app.models.user import Student
from app.services.ranking_service import RankingService

router = APIRouter()


def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


# ============================================================
# STUDENT ENDPOINTS
# ============================================================

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
    """Barcha proyektlar (public)"""
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
    """Proyektni ko'rish (public)"""
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
    """Proyektni yangilash (faqat egasi)"""
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
    """Proyektni o'chirish (faqat egasi)"""
    await service.delete_project(project_id=project_id, student_id=current_student.id)


@router.post("/{project_id}/submit", response_model=ProjectRead)
async def submit_project(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Proyektni taqdim qilish (faqat egasi)"""
    return await service.submit_project(
        project_id=project_id,
        student_id=current_student.id
    )


@router.post("/{project_id}/like", response_model=ProjectRead)
async def like_project(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Proyektni like qilish"""
    return await service.like_project(
        project_id=project_id,
        student_id=current_student.id
    )


@router.post("/{project_id}/upload-zip")
async def upload_project_zip(
        project_id: int,
        file: UploadFile = File(...),
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db),
):
    """ZIP fayl yuklash va loyihaga bog'lash"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")
    if project.student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Bu loyiha sizga tegishli emas")

    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Faqat ZIP format qabul qilinadi")

    MAX_SIZE = 15 * 1024 * 1024
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Fayl hajmi 15MB dan oshmasligi kerak")

    upload_dir = os.path.join("uploads", "projects", str(project_id))
    os.makedirs(upload_dir, exist_ok=True)

    safe_filename = f"project_{project_id}.zip"
    file_path = os.path.join(upload_dir, safe_filename)
    with open(file_path, "wb") as f:
        f.write(content)

    project.project_files = f"/uploads/projects/{project_id}/{safe_filename}"
    await db.commit()
    await db.refresh(project)
    return project


@router.post("/{project_id}/ai-review")
async def ai_review_project(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db),
):
    """Loyihani avtomatik baholash"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")

    score = 0
    feedback_lines = []

    if project.title and len(project.title) > 5:
        score += 10
        feedback_lines.append("✅ Sarlavha mavjud")
    else:
        feedback_lines.append("⚠️ Sarlavhani to'ldiring")

    if project.description and len(project.description) > 50:
        score += 20
        feedback_lines.append("✅ Tavsif yaxshi yozilgan")
    else:
        feedback_lines.append("⚠️ Tavsifni batafsil yozing (kamida 50 belgi)")

    if project.github_url:
        score += 25
        feedback_lines.append("✅ GitHub havolasi mavjud")
    else:
        feedback_lines.append("⚠️ GitHub havolasini qo'shing")

    if project.live_demo_url:
        score += 20
        feedback_lines.append("✅ Live demo havolasi mavjud")
    else:
        feedback_lines.append("⚠️ Live demo havolasini qo'shish tavsiya etiladi")

    if project.technologies_used:
        score += 15
        feedback_lines.append("✅ Texnologiyalar ko'rsatilgan")
    else:
        feedback_lines.append("⚠️ Ishlatilgan texnologiyalarni ko'rsating")

    if project.project_files:
        score += 10
        feedback_lines.append("✅ ZIP fayl yuklangan")
    else:
        feedback_lines.append("⚠️ Loyiha ZIP faylini yuklang")

    if score >= 80:
        verdict = "🌟 A'lo"
    elif score >= 60:
        verdict = "👍 Yaxshi"
    elif score >= 40:
        verdict = "📝 O'rtacha"
    else:
        verdict = "❌ Yaxshilash kerak"

    review = (
        f"📊 AI Baholash: {score}/100 — {verdict}\n\n"
        + "\n".join(feedback_lines)
    )
    return review


# ============================================================
# TEACHER ENDPOINTS
# ============================================================

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
    """
    O'qituvchi loyihani tasdiqlaydi.
    Tasdiqlangandan keyin avtomatik:
      - Ballar qo'shiladi
      - Kurs tugagan bo'lsa sertifikat beriladi
      - Achievementlar tekshiriladi
    """
    # 1. Loyihani topish
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")

    if project.status == "Approved":
        raise HTTPException(status_code=400, detail="Bu loyiha allaqachon tasdiqlangan")

    # 2. Ballarni qo'shish
    ranking_service = RankingService(db)
    await ranking_service.add_points_to_student(project.student_id, data.points)

    # 3. Loyiha holatini yangilash
    project.status = "Approved"
    project.feedback = data.feedback
    project.grade = data.grade
    project.points_earned = data.points

    await db.commit()

    # 4. ✅ Submission orqali course_id ni topib sertifikat berish
    sub_result = await db.execute(
        select(Submission).where(Submission.project_id == project_id)
    )
    submission = sub_result.scalar_one_or_none()

    certificate_issued = False
    certificate_id = None

    if submission and submission.lesson_id:
        lesson_res = await db.execute(
            select(Lesson).where(Lesson.id == submission.lesson_id)
        )
        lesson = lesson_res.scalar_one_or_none()
        if lesson:
            cert = await achievement_service.award_certificate(
                db, project.student_id, lesson.course_id
            )
            if cert:
                certificate_issued = True
                certificate_id = cert.id

    # 5. ✅ Achievementlarni tekshirish
    await achievement_service.check_and_award_achievements(db, project.student_id)

    return {
        "message": "Loyiha tasdiqlandi, ballar va proyekt soni yangilandi",
        "certificate_issued": certificate_issued,
        "certificate_id": certificate_id
    }


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