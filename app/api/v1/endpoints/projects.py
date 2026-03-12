from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db, get_current_student  # ✅ bir joydan
from app.services.project_service import ProjectService
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