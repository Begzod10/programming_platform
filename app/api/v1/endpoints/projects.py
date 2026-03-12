from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

<<<<<<< HEAD
from app.db.session import get_db
<<<<<<< Updated upstream
from app.services.project_service import get_current_student, ProjectService
=======
from app.dependencies import get_db, get_current_student  # ✅ bir joydan
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead
>>>>>>> origin/branch-shoh
=======
from app.services.project_service import ProjectService
>>>>>>> Stashed changes
from app.models.user import Student
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
    ProjectReadWithStudent,
    ProjectListResponse,
)
from app.services.auth_service import get_current_student

router = APIRouter()


def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED, summary="Yangi loyiha yaratish")
async def create_project(
        payload: ProjectCreate,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.create_project(student_id=current_student.id, data=payload)


@router.get("/", response_model=ProjectListResponse, summary="Barcha loyihalarni olish")
async def get_projects(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        service: ProjectService = Depends(get_project_service),
):
    return await service.get_projects(page=page, page_size=page_size)


@router.get("/my", response_model=ProjectListResponse, summary="Mening loyihalarim")
async def get_my_projects(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.get_student_projects(
        student_id=current_student.id,
        page=page,
        page_size=page_size
    )


@router.get("/{project_id}", response_model=ProjectReadWithStudent, summary="Loyihani ID bo'yicha olish")
async def get_project(
        project_id: int,
        service: ProjectService = Depends(get_project_service),
):
    project = await service.get_project(project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")
    return project


@router.put("/{project_id}", response_model=ProjectRead, summary="Loyihani tahrirlash")
async def update_project(
        project_id: int,
        payload: ProjectUpdate,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")
    if project.student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    return await service.update_project(project_id=project_id, data=payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Loyihani o'chirish")
async def delete_project(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")
    if project.student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    await service.delete_project(project_id=project_id)


@router.post("/{project_id}/submit", response_model=ProjectRead, summary="Loyihani ko'rib chiqishga yuborish")
async def submit_project(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
<<<<<<< Updated upstream
<<<<<<< HEAD
    return await service.review_project(project_id=project_id, data=payload)
=======
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")
    if project.student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    return await service.submit_project(project_id=project_id)
>>>>>>> Stashed changes


@router.post("/{project_id}/like", response_model=ProjectRead, summary="Loyihani like qilish")
async def like_project(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
<<<<<<< Updated upstream
    return await service.update_project_status(project_id=project_id, data=payload)


@router.post("/{project_id}/difficulty", response_model=ProjectRead)
async def update_project_difficulty(
        project_id: int,
        payload: ProjectDifficultyUpdate,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project_difficulty(project_id=project_id, data=payload)


@router.post("/{project_id}/grade", response_model=ProjectRead)
async def update_project_grade(
        project_id: int,
        payload: ProjectGrade,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project_grade(project_id=project_id, data=payload)


@router.post("/{project_id}/comment", response_model=ProjectRead)
async def update_project_comment(
        project_id: int,
        payload: ProjectComment,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project_comment(project_id=project_id, data=payload)


# --- MEDIA VA FAYLLAR ---

@router.post("/{project_id}/file", response_model=ProjectRead)
async def update_project_file(
        project_id: int,
        file: UploadFile = File(...),
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project_file(project_id=project_id, file=file)


@router.post("/{project_id}/image", response_model=ProjectRead)
async def update_project_image(
        project_id: int,
        file: UploadFile = File(...),
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project_image(project_id=project_id, file=file)


@router.post("/{project_id}/video", response_model=ProjectRead)
async def update_project_video(
        project_id: int,
        file: UploadFile = File(...),
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project_video(project_id=project_id, file=file)


@router.post("/{project_id}/code", response_model=ProjectRead)
async def update_project_code(
        project_id: int,
        file: UploadFile = File(...),
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project_code(project_id=project_id, file=file)
=======
    return await service.submit_project(project_id=project_id, student_id=current_student.id)


@router.post("/{project_id}/review")
async def review_project(
        project_id: int,
        feedback: str = Query(...),
        grade: str = Query(...),
        points: int = Query(...),
        # TODO: bu endpoint faqat instructor/admin uchun bo'lishi kerak
        # current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.review_project(project_id=project_id, feedback=feedback, grade=grade, points=points)


@router.post("/{project_id}/status")
async def update_status(
        project_id: int,
        status: str = Query(...),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_status(project_id=project_id, status=status)


@router.post("/{project_id}/grade")
async def update_grade(
        project_id: int,
        grade: str = Query(...),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_grade(project_id=project_id, grade=grade)


@router.post("/{project_id}/comment")
async def update_comment(
        project_id: int,
        comment: str = Query(...),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_comment(project_id=project_id, comment=comment)


@router.post("/{project_id}/difficulty")
async def update_difficulty(
        project_id: int,
        difficulty: str = Query(...),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_difficulty(project_id=project_id, difficulty=difficulty)


@router.post("/{project_id}/file")
async def update_file(
        project_id: int,
        file_url: str = Query(...),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_file(project_id=project_id, file_url=file_url)
>>>>>>> origin/branch-shoh
=======
    return await service.like_project(project_id=project_id)
>>>>>>> Stashed changes
