from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db, get_current_student  # ✅ bir joydan
from app.schemas.user import UserRead, UserUpdate
from app.schemas.project import ProjectRead  # Qo'shildi
from app.services import student_service
<<<<<<< HEAD
from app.services.project_service import get_current_student, ProjectService  # ProjectService qo'shildi
=======
>>>>>>> origin/branch-shoh
from app.models.user import Student

router = APIRouter()


@router.get("/", response_model=List[UserRead])
async def get_students(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        search: str = Query(None),
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    return await student_service.get_all_students(db, skip, limit, search)


@router.get("/projects/", response_model=List[ProjectRead])
async def get_student_projects(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Studentning o'ziga tegishli loyihalarni qaytaradi"""
    service = ProjectService(db)
    return await service.get_projects_by_student(student_id=current_student.id)


@router.get("/me", response_model=UserRead)
async def get_me(current_student: Student = Depends(get_current_student)):
    return current_student


@router.get("/{student_id}", response_model=UserRead)
async def get_student(student_id: int, db: AsyncSession = Depends(get_db)):
    student = await student_service.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student topilmadi")
    return student


@router.put("/{student_id}", response_model=UserRead)
async def update_student(
        student_id: int,
        data: UserUpdate,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    if current_student.id != student_id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    return await student_service.update_student(db, student_id, data)


@router.delete("/{student_id}")
async def delete_student(
        student_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    if current_student.id != student_id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    return await student_service.delete_student(db, student_id)
