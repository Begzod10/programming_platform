from fastapi import APIRouter, Depends, status, Query, HTTPException, Body
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.project import Project
from app.models.lesson import Lesson
from app.models.submission import Submission

from app.dependencies import get_db, get_current_student, get_current_instructor
from app.services.project_service import ProjectService
from app.services import achievement_service
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead
from app.models.user import Student
from app.services.ranking_service import RankingService
from fastapi.responses import FileResponse
from app.services.grok_service import analyze_project_with_grok

import uuid
from pathlib import Path
from fastapi import UploadFile, File
from app.config import settings

PROJECTS_UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "projects"
PROJECTS_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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


@router.post("/upload-zip")
async def upload_project_zip(
        file: UploadFile = File(...),
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db),
        service: ProjectService = Depends(get_project_service),
):
    import zipfile, io

    allowed_types = [
        "application/zip",
        "application/x-zip-compressed",
        "application/octet-stream"
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Faqat ZIP fayl!")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="ZIP fayl bo'sh!")

    if len(contents) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="ZIP fayl 15MB dan katta!")

    # ZIP tekshirish va kod o'qish
    code_content = ""
    try:
        with zipfile.ZipFile(io.BytesIO(contents)) as zf:
            real_files = [n for n in zf.namelist() if not n.endswith("/")]
            if not real_files:
                raise HTTPException(status_code=400, detail="ZIP ichida fayl yo'q!")
            code_extensions = [".html", ".css", ".js", ".py", ".ts", ".jsx", ".tsx", ".vue", ".java", ".php"]
            for name in real_files[:10]:
                if any(name.endswith(ext) for ext in code_extensions):
                    try:
                        with zf.open(name) as f:
                            code = f.read().decode("utf-8", errors="ignore")
                            code_content += f"\n\n=== {name} ===\n{code[:2000]}"
                    except Exception:
                        pass
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Noto'g'ri ZIP fayl!")

    # Faylni saqlash
    filename = f"{uuid.uuid4()}.zip"
    filepath = PROJECTS_UPLOAD_DIR / filename
    with open(filepath, "wb") as f:
        f.write(contents)
    file_url = f"/uploads/projects/{filename}"

    # Avtomatik project yaratish
    new_project = Project(
        student_id=current_student.id,
        title="Loyiha",
        description="",
        github_url=None,
        live_demo_url=None,
        difficulty_level="Easy",
        status="Submitted",
        project_files=file_url,
    )
    db.add(new_project)
    await db.flush()

    # AI tekshirish
    ai_result = {}
    try:
        ai_result = await analyze_project_with_grok(
            title=new_project.title,
            description=new_project.description + (f"\n\nKod fayllari:\n{code_content}" if code_content else ""),
            github_url="ZIP fayl orqali yuklandi",
            technologies=[],
            difficulty_level="Easy",
            previous_points=0
        )
        if ai_result:
            new_project.grade = ai_result.get("grade")
            new_project.points_earned = ai_result.get("points", 0)
            new_project.instructor_feedback = ai_result.get("feedback", "")
            new_project.status = "Under Review"
    except Exception:
        pass

    await db.commit()
    await db.refresh(new_project)

    return {
        "project_id": new_project.id,
        "file_url": file_url,
        "message": "ZIP fayl yuklandi!",
        "ai_review": {
            "grade": ai_result.get("grade") if ai_result else None,
            "points": ai_result.get("points") if ai_result else None,
            "feedback": ai_result.get("feedback") if ai_result else None,
        }
    }


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


# ============================================================
# TEACHER ENDPOINTS
# ============================================================

class ReviewProjectRequest(BaseModel):
    feedback: str
    grade: str
    points: int = Field(..., ge=0, le=100, description="Ball 0 dan 100 gacha")


@router.post("/{project_id}/review")
async def review_project(
        project_id: int,
        data: ReviewProjectRequest,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")

    if project.status == "Approved":
        raise HTTPException(status_code=400, detail="Bu loyiha allaqachon tasdiqlangan")

    ranking_service = RankingService(db)
    await ranking_service.add_points_to_student(project.student_id, data.points)

    project.status = "Approved"
    project.instructor_feedback = data.feedback
    project.grade = data.grade
    project.points_earned = data.points
    project.reviewed_at = datetime.utcnow()

    await db.commit()

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
    return await service.update_status(project_id=project_id, status=new_status)


@router.patch("/{project_id}/grade")
async def update_grade(
        project_id: int,
        grade: str = Body(..., embed=True),
        current_teacher: Student = Depends(get_current_instructor),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_grade(project_id=project_id, grade=grade)


@router.patch("/{project_id}/difficulty")
async def update_difficulty(
        project_id: int,
        difficulty: str = Body(..., embed=True),
        current_teacher: Student = Depends(get_current_instructor),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_difficulty(project_id=project_id, difficulty=difficulty)


@router.patch("/{project_id}/comment")
async def update_comment(
        project_id: int,
        comment: str = Body(..., embed=True),
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_comment(
        project_id=project_id,
        student_id=current_student.id,
        comment=comment,
    )


@router.patch("/{project_id}/file")
async def update_file(
        project_id: int,
        file_url: str = Body(..., embed=True),
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_file(
        project_id=project_id,
        student_id=current_student.id,
        file_url=file_url,
    )


@router.post("/{project_id}/upload-zip")
async def upload_project_zip_by_id(
        project_id: int,
        file: UploadFile = File(...),
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db),
        service: ProjectService = Depends(get_project_service),
):
    import zipfile, io

    allowed_types = [
        "application/zip",
        "application/x-zip-compressed",
        "application/octet-stream"
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Faqat ZIP fayl!")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="ZIP fayl bo'sh!")

    if len(contents) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="ZIP fayl 15MB dan katta!")

    code_content = ""
    try:
        with zipfile.ZipFile(io.BytesIO(contents)) as zf:
            real_files = [n for n in zf.namelist() if not n.endswith("/")]
            if not real_files:
                raise HTTPException(status_code=400, detail="ZIP ichida fayl yo'q!")
            code_extensions = [".html", ".css", ".js", ".py", ".ts", ".jsx", ".tsx", ".vue", ".java", ".php"]
            for name in real_files[:10]:
                if any(name.endswith(ext) for ext in code_extensions):
                    try:
                        with zf.open(name) as f:
                            code = f.read().decode("utf-8", errors="ignore")
                            code_content += f"\n\n=== {name} ===\n{code[:2000]}"
                    except Exception:
                        pass
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Noto'g'ri ZIP fayl!")

    project = await service.get_project(project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi!")
    if project.student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Bu loyiha sizniki emas!")

    if project.project_files:
        old_path = PROJECTS_UPLOAD_DIR / Path(project.project_files).name
        if old_path.exists():
            old_path.unlink()

    filename = f"{uuid.uuid4()}.zip"
    filepath = PROJECTS_UPLOAD_DIR / filename
    with open(filepath, "wb") as f:
        f.write(contents)
    file_url = f"/uploads/projects/{filename}"

    await service.update_file(
        project_id=project_id,
        student_id=current_student.id,
        file_url=file_url,
    )

    ai_result = {}
    try:
        technologies = []
        if project.technologies_used:
            if isinstance(project.technologies_used, list):
                technologies = project.technologies_used
            else:
                technologies = [project.technologies_used]

        ai_result = await analyze_project_with_grok(
            title=project.title,
            description=project.description + (f"\n\nKod fayllari:\n{code_content}" if code_content else ""),
            github_url=project.github_url or "ZIP fayl orqali yuklandi",
            technologies=technologies,
            difficulty_level=project.difficulty_level,
            previous_points=project.points_earned or 0
        )
        if ai_result:
            project_result = await db.execute(select(Project).where(Project.id == project_id))
            db_project = project_result.scalar_one_or_none()
            if db_project:
                db_project.grade = ai_result.get("grade")
                db_project.points_earned = ai_result.get("points", 0)
                db_project.instructor_feedback = ai_result.get("feedback", "")
                db_project.status = "Under Review"
                await db.commit()
    except Exception:
        pass

    return {
        "file_url": file_url,
        "message": "ZIP fayl yuklandi va AI tekshirdi!",
        "ai_review": {
            "grade": ai_result.get("grade") if ai_result else None,
            "points": ai_result.get("points") if ai_result else None,
            "feedback": ai_result.get("feedback") if ai_result else None,
        }
    }


@router.get("/{project_id}/download-zip")
async def download_project_zip(
        project_id: int,
        current_teacher: Student = Depends(get_current_instructor),
        service: ProjectService = Depends(get_project_service),
):
    project = await service.get_project(project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi!")
    if not project.project_files:
        raise HTTPException(status_code=404, detail="Bu loyihada ZIP fayl yo'q!")

    filename = Path(project.project_files).name
    filepath = PROJECTS_UPLOAD_DIR / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Fayl serverda topilmadi!")

    return FileResponse(
        path=str(filepath),
        filename=f"project_{project_id}_{filename}",
        media_type="application/zip"
    )
