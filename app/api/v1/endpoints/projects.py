from fastapi import APIRouter, Depends, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.project_service import get_current_student
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
    ProjectReadWithStudent,
    ProjectListResponse,
    ProjectReview,
    ProjectStatusUpdate,  # ✅ enum emas, schema
    ProjectDifficultyUpdate,  # ✅ enum emas, schema
    ProjectGrade,
    ProjectComment,
)
from app.services.project_service import ProjectService
from app.models.user import Student

router = APIRouter()


def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


@router.post(
    "/",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
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
    summary="Get all projects",
)
async def get_projects(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        service: ProjectService = Depends(get_project_service),
):
    return await service.get_projects(page=page, page_size=page_size)


@router.get(
    "/{project_id}",
    response_model=ProjectReadWithStudent,
    summary="Get a project by ID",
)
async def get_project(
        project_id: int,
        service: ProjectService = Depends(get_project_service),
):
    return await service.get_project(project_id=project_id)


@router.put(
    "/{project_id}",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
    summary="Update a project by ID",
)
async def update_project(
        project_id: int,
        payload: ProjectUpdate,
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project(project_id=project_id, data=payload)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a project by ID",
)
async def delete_project(
        project_id: int,
        service: ProjectService = Depends(get_project_service),
):
    return await service.delete_project(project_id=project_id)


@router.post(
    "/{project_id}/review",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
    summary="Review a project by ID",
)
async def review_project(
        project_id: int,
        payload: ProjectReview,
        service: ProjectService = Depends(get_project_service),
):
    return await service.review_project(project_id=project_id, data=payload)


@router.post(
    "/{project_id}/status",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
    summary="Update project status by ID",
)
async def update_project_status(
        project_id: int,
        payload: ProjectStatusUpdate,
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project_status(project_id=project_id, data=payload)


@router.post(
    "/{project_id}/difficulty",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
    summary="Update project difficulty by ID",
)
async def update_project_difficulty(
        project_id: int,
        payload: ProjectDifficultyUpdate,
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project_difficulty(project_id=project_id, data=payload)


@router.post(
    "/{project_id}/grade",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
    summary="Update project grade by ID",
)
async def update_project_grade(
        project_id: int,
        payload: ProjectGrade,
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project_grade(project_id=project_id, data=payload)


@router.post(
    "/{project_id}/comment",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
    summary="Update project comment by ID",
)
async def update_project_comment(
        project_id: int,
        payload: ProjectComment,
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project_comment(project_id=project_id, data=payload)


@router.post(
    "/{project_id}/file",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
    summary="Update project file by ID",
)
async def update_project_file(
        project_id: int,
        file: UploadFile = File(...),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project_file(project_id=project_id, file=file)


@router.post(
    "/{project_id}/image",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
    summary="Update project image by ID",
)
async def update_project_image(
        project_id: int,
        file: UploadFile = File(...),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project_image(project_id=project_id, file=file)


@router.post(
    "/{project_id}/video",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
    summary="Update project video by ID",
)
async def update_project_video(
        project_id: int,
        file: UploadFile = File(...),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project_video(project_id=project_id, file=file)


@router.post(
    "/{project_id}/code",
    response_model=ProjectRead,
    status_code=status.HTTP_200_OK,
    summary="Update project code by ID",
)
async def update_project_code(
        project_id: int,
        file: UploadFile = File(...),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project_code(project_id=project_id, file=file)
