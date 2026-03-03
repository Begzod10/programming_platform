from fastapi import APIRouter, Depends, status, Query, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.services.project_service import get_current_student, ProjectService
from app.models.user import Student
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
    ProjectReadWithStudent,
    ProjectListResponse,
    ProjectReview,
    ProjectStatusUpdate,
    ProjectDifficultyUpdate,
    ProjectGrade,
    ProjectComment,
)

router = APIRouter()


# Service dependency
def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


# --- ASOSIY CRUD ENDPOINTLARI ---

@router.post(
    "/",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Yangi loyiha yaratish",
)
async def create_project(
        payload: ProjectCreate,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.create_project(student_id=current_student.id, data=payload)


@router.get(
    "/",
    response_model=ProjectListResponse,
    summary="Barcha loyihalarni olish",
)
async def get_projects(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.get_projects(page=page, page_size=page_size)


@router.get(
    "/{project_id}",
    response_model=ProjectReadWithStudent,
    summary="Loyihani ID bo'yicha olish",
)
async def get_project(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    project = await service.get_project(project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")
    return project


@router.put(
    "/{project_id}",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
    summary="Loyihani tahrirlash",
)
async def update_project(
        project_id: int,
        payload: ProjectUpdate,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project(project_id=project_id, data=payload)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    summary="Loyihani o'chirish",
)
async def delete_project(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.delete_project(project_id=project_id)


# --- LOYIHANI BAHOLASH VA STATUSLAR ---

@router.post("/{project_id}/review", response_model=ProjectRead)
async def review_project(
        project_id: int,
        payload: ProjectReview,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.review_project(project_id=project_id, data=payload)


@router.post("/{project_id}/status", response_model=ProjectRead)
async def update_project_status(
        project_id: int,
        payload: ProjectStatusUpdate,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
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
