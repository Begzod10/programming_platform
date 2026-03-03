from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.services.project_service import get_current_student, ProjectService
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead
from app.models.user import Student

router = APIRouter()


def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
        payload: ProjectCreate,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.create_project(student_id=current_student.id, data=payload)


@router.get("/", response_model=List[ProjectRead])
async def get_all_projects(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        service: ProjectService = Depends(get_project_service),
):
    return await service.get_all_projects(skip=skip, limit=limit)


@router.get("/my", response_model=List[ProjectRead])
async def get_my_projects(
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.get_all_projects_by_student(student_id=current_student.id)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
        project_id: int,
        service: ProjectService = Depends(get_project_service),
):
    return await service.get_project(project_id)


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
        project_id: int,
        payload: ProjectUpdate,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.update_project(project_id=project_id, student_id=current_student.id, data=payload)


@router.delete("/{project_id}")
async def delete_project(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.delete_project(project_id=project_id, student_id=current_student.id)


@router.post("/{project_id}/submit")
async def submit_project(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    return await service.submit_project(project_id=project_id, student_id=current_student.id)