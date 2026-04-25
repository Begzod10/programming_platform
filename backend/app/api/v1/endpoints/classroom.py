from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db, get_current_teacher
from app.schemas.group import GroupRead
from app.services.group_service import GroupService
from app.models.user import Student

router = APIRouter()


@router.get("/groups", response_model=List[GroupRead])
async def get_classroom_groups(
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db),
):
    """Barcha guruhlar va ulardagi talabalar (teacher only)"""
    service = GroupService(db)
    return await service.get_all_groups()


@router.post("/sync")
async def sync_classroom(
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db),
):
    """Sinf ma'lumotlarini yangilash"""
    service = GroupService(db)
    groups = await service.get_all_groups()
    total_students = sum(len(g.students) for g in groups)
    return {
        "message": "Sinf muvaffaqiyatli sinxronlashtirildi",
        "groups_count": len(groups),
        "students_count": total_students,
    }
