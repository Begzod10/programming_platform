import logging

from fastapi import APIRouter, Depends, status, Query, HTTPException, Body
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.project import Project
from app.models.lesson import Lesson, LessonCompletion
from app.models.submission import Submission
from app.models.course import Course

from app.dependencies import get_db, get_current_student, get_current_instructor
from app.services.project_service import ProjectService
from app.services import achievement_service
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead, ProjectReadWithStudent
from app.models.user import Student
from app.services.ranking_service import RankingService
from fastapi.responses import FileResponse
from app.services.grok_service import analyze_project_with_grok
from app.services.lesson_context_resolver import load_lesson_context_for_project
from app.services.ai_review_service import run_ai_review_for_project
from app.services.github_repo_service import zip_bytes_have_code_file

import uuid
from pathlib import Path
from fastapi import UploadFile, File, Form
from app.config import settings

PROJECTS_UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "projects"
PROJECTS_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

router = APIRouter()


async def _run_ai_review_and_persist_failure(db: AsyncSession, project: Project) -> dict:
    """Run the AI pipeline for a ZIP upload and make sure a failure is never
    silent. run_ai_review_for_project(raise_on_error=False) already avoids
    raising for expected failures (transient AI outage, quota, etc), but the
    upload-zip endpoints used to just drop that reason into the HTTP
    response and never write it to the project row -- once the upload
    dialog closed, the project sat blank ("Submitted", no grade, no
    feedback) with no trace of why, and no way for the student or teacher
    to know a retry ( POST /{project_id}/ai-review ) could fix it.
    An unhandled exception is also caught here so it can't 500 the
    request after the project row has already been committed.
    """
    try:
        ai_result = await run_ai_review_for_project(db, project, raise_on_error=False)
    except Exception as e:
        logger.warning("[ai-zip] project=%d unhandled error: %s", project.id, e)
        ai_result = {"success": False, "reason": "AI baholash vaqtincha ishlamayapti. "
                                                   "O'qituvchi loyihangizni tez orada baholaydi.",
                     "http_status": 0}

    if not ai_result.get("success") and project.reviewed_at is None:
        project.instructor_feedback = ai_result.get("reason", "AI tekshirish muvaffaqiyatsiz")
        await db.commit()
        await db.refresh(project)

    return ai_result


def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


# Backwards-compat alias — earlier in this branch the helper lived here.
# Kept so any in-flight branches that imported the private name still resolve;
# delete after one release cycle.
_load_lesson_context_for_project = load_lesson_context_for_project


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


@router.get("/", response_model=List[ProjectReadWithStudent])
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
        lesson_id: Optional[int] = Form(None),
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

    # Reject uploads that would only ever fail AI review later (e.g. a ZIP
    # that just wraps a nested .rar/.png). Without this, the project gets
    # created as "Submitted" and stays stuck there forever, since the AI
    # pipeline runs with raise_on_error=False and never surfaces why.
    if not zip_bytes_have_code_file(contents):
        raise HTTPException(
            status_code=400,
            detail="ZIP'da o'qiladigan kod fayli yo'q (faqat rasm/binar yoki "
                   "arxiv fayllar bor). Haqiqiy loyiha fayllaringizni "
                   "(.html, .css, .js va h.k.) to'g'ridan-to'g'ri ZIP qiling.",
        )

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

    # Tie project → lesson via Submission so the AI grader can resolve
    # course/lesson context, and so the regrade pipeline (which looks up
    # submissions.project_id → lesson_id) finds this submission later.
    if lesson_id is not None:
        db.add(Submission(
            project_id=new_project.id,
            student_id=current_student.id,
            lesson_id=lesson_id,
            status="Submitted",
        ))
        await db.flush()

    await db.commit()
    await db.refresh(new_project)

    # Run full AI grading pipeline (same path as the submit button).
    # On success sets status "Approved"/"Rejected", awards points, and
    # creates LessonCompletion. On failure leaves status "Submitted" and
    # persists why, so the teacher can grade manually and the student can
    # see the reason instead of a permanently blank review.
    ai_result = await _run_ai_review_and_persist_failure(db, new_project)
    await db.refresh(new_project)

    return {
        "project_id": new_project.id,
        "file_url": file_url,
        "message": "ZIP fayl yuklandi!",
        "ai_review": {
            "grade": ai_result.get("grade") if ai_result.get("success") else None,
            "points": ai_result.get("new_points") if ai_result.get("success") else None,
            "feedback": ai_result.get("feedback") if ai_result.get("success") else None,
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

    ranking_service = RankingService(db)
    old_points = project.points_earned or 0
    old_status = project.status
    # Only subtract previously-awarded points. Points are only added when a
    # project is Approved — Rejected projects store the AI score in
    # points_earned but never add it to total_points, so subtracting it here
    # would deduct points that were never granted.
    if old_points > 0 and old_status == "Approved":
        await ranking_service.add_points_to_student(project.student_id, -old_points)
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
            # Create LessonCompletion on passing score so the next lesson
            # unlocks. Points reward is only awarded here — not on submission.
            if data.points >= 75:
                existing_comp = await db.execute(
                    select(LessonCompletion).where(
                        LessonCompletion.student_id == project.student_id,
                        LessonCompletion.lesson_id == submission.lesson_id,
                    )
                )
                if not existing_comp.scalar_one_or_none():
                    db.add(LessonCompletion(
                        student_id=project.student_id,
                        lesson_id=submission.lesson_id,
                    ))
                    points_reward = getattr(lesson, "points_reward", 0) or 0
                    if points_reward > 0:
                        await ranking_service.add_points_to_student(
                            project.student_id, points_reward)
                    await db.commit()

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


@router.post("/{project_id}/regrade")
async def regrade_project(
        project_id: int,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db),
        service: ProjectService = Depends(get_project_service),
):
    """Loyihani qayta tekshirish — lesson/course konteksti bilan AI prompt'ni
    qayta yuborib, eski "Python/Flask" hardkod tufayli noto'g'ri ball olgan
    loyihalarni qayta baholaydi. Faqat instructor.
    """
    import zipfile
    import io

    project = await service.get_project(project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi!")
    if not project.project_files:
        raise HTTPException(status_code=400, detail="Loyihada fayl yo'q!")

    zip_path = PROJECTS_UPLOAD_DIR / Path(project.project_files).name
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="ZIP fayl mavjud emas!")

    code_content = ""
    code_extensions = [
        ".html", ".css", ".js", ".py",
        ".ts", ".jsx", ".tsx", ".vue",
        ".java", ".php", ".cpp", ".c",
    ]
    try:
        with zipfile.ZipFile(zip_path) as zf:
            real_files = [n for n in zf.namelist() if not n.endswith("/")]
            for name in real_files[:10]:
                if any(name.endswith(ext) for ext in code_extensions):
                    try:
                        with zf.open(name) as f:
                            code = f.read().decode("utf-8", errors="ignore")
                            code_content += f"\n\n=== {name} ===\n{code[:2000]}"
                    except Exception:
                        pass
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Buzilgan ZIP fayl!")

    technologies: list[str] = []
    if project.technologies_used:
        if isinstance(project.technologies_used, list):
            technologies = project.technologies_used
        else:
            technologies = [project.technologies_used]

    from app.services.ai_review_service import run_ai_review_for_project

    db_project = (await db.execute(
        select(Project).where(Project.id == project_id)
    )).scalar_one_or_none()
    if not db_project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi!")

    # See upload_project_zip_by_id for why this must happen before the
    # status reset: once status flips to "Submitted", run_ai_review_for_project
    # can no longer tell the old grade was ever "Approved", so its own
    # revoke-before-reaward guard would never fire for the points already
    # earned by the grade being replaced.
    if db_project.status == "Approved" and (db_project.points_earned or 0) > 0:
        await RankingService(db).revoke_earned_points(
            db_project.student_id, db_project.points_earned)
    db_project.reviewed_at = None
    db_project.status = "Submitted"
    await db.commit()
    await db.refresh(db_project)

    ai_result = await run_ai_review_for_project(db, db_project, raise_on_error=False)

    lesson_context_used = bool(await _load_lesson_context_for_project(db, project_id=project_id))

    return {
        "message": "Loyiha qayta baholandi",
        "lesson_context_used": lesson_context_used,
        "ai_review": {
            "grade": ai_result.get("grade"),
            "points": ai_result.get("new_points"),
            "summary": ai_result.get("summary"),
            "feedback": ai_result.get("feedback"),
            "strengths": ai_result.get("strengths", []),
            "improvements": ai_result.get("improvements", []),
            "bugs": ai_result.get("bugs", []),
            "error": None if ai_result.get("success") else ai_result.get("reason"),
        },
    }


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


@router.patch("/{project_id}/explanation")
async def save_code_explanation(
        project_id: int,
        explanation: str = Body(..., embed=True),
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project or project.student_id != current_student.id:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")
    project.code_explanation = explanation
    await db.commit()
    return {"ok": True}


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

    # Same fail-fast gate as upload_project_zip — reject a ZIP with no
    # readable code file immediately instead of letting it get stuck in
    # "Submitted" after a silent AI-review failure.
    if not zip_bytes_have_code_file(contents):
        raise HTTPException(
            status_code=400,
            detail="ZIP'da o'qiladigan kod fayli yo'q (faqat rasm/binar yoki "
                   "arxiv fayllar bor). Haqiqiy loyiha fayllaringizni "
                   "(.html, .css, .js va h.k.) to'g'ridan-to'g'ri ZIP qiling.",
        )

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

    # Re-fetch after file update so run_ai_review_for_project sees the
    # new project_files path. Also reset reviewed_at so the AI pipeline
    # doesn't think this was already graded.
    project_result = await db.execute(select(Project).where(Project.id == project_id))
    db_project = project_result.scalar_one_or_none()
    if db_project:
        # This reset makes run_ai_review_for_project see old_status=="Submitted"
        # (never "Approved"), so its own revoke-before-reaward guard never
        # fires for the *previous* grade on this project. Without revoking
        # here first, points already earned by an earlier Approved review
        # are orphaned forever if the resubmission fails/scores low, or
        # silently doubled if it re-passes.
        if db_project.status == "Approved" and (db_project.points_earned or 0) > 0:
            await RankingService(db).revoke_earned_points(
                db_project.student_id, db_project.points_earned)
        db_project.reviewed_at = None
        db_project.status = "Submitted"
        db_project.submitted_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_project)

        ai_result = await _run_ai_review_and_persist_failure(db, db_project)
        await db.refresh(db_project)
    else:
        ai_result = {}

    return {
        "file_url": file_url,
        "message": "ZIP fayl yuklandi va AI tekshirdi!",
        "ai_review": {
            "grade": ai_result.get("grade") if ai_result.get("success") else None,
            "points": ai_result.get("new_points") if ai_result.get("success") else None,
            "feedback": ai_result.get("feedback") if ai_result.get("success") else None,
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
