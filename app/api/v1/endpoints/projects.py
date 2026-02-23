from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.services.project_service import get_current_student, get_current_instructor
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
    ProjectReadWithStudent,
    ProjectListResponse,
    ProjectReview,
    ProjectStatus,
    DifficultyLevel,
)
from app.services.project_service import ProjectService
from app.models.user import Student

router = APIRouter(prefix="/projects", tags=["Projects"])


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
