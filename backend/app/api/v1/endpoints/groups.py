from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.dependencies import get_db, get_current_teacher
from app.schemas.group import GroupCreate, GroupRead, GroupUpdate
from app.services.group_service import GroupService
from app.models.user import Student
from app.models.group import Group

router = APIRouter()


@router.post("/", response_model=GroupRead)
async def create_new_group(
        payload: GroupCreate,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    """Yangi guruh yaratish (faqat teacher)"""
    service = GroupService(db)
    return await service.create_group(payload)


@router.get("/", response_model=List[GroupRead])
async def get_groups(db: AsyncSession = Depends(get_db)):
    """Barcha guruhlar"""
    service = GroupService(db)
    return await service.get_all_groups()


@router.get("/{group_id}", response_model=GroupRead)
async def get_group(group_id: int, db: AsyncSession = Depends(get_db)):
    """Guruhni ko'rish"""
    service = GroupService(db)
    groups = await service.get_all_groups()
    group = next((g for g in groups if g.id == group_id), None)
    if not group:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")
    return group


@router.patch("/{group_id}/add-student/{student_id}")
async def add_student_to_group(
        group_id: int,
        student_id: int,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    """Studentni guruhga qo'shish (faqat teacher)"""
    group_result = await db.execute(select(Group).where(Group.id == group_id))
    group = group_result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")

    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Talaba topilmadi")

    if student.group_id == group_id:
        raise HTTPException(status_code=400, detail="Talaba allaqachon bu guruhda")

    student.group_id = group_id
    await db.commit()
    return {"message": f"Talaba '{student.full_name or student.username}' '{group.name}' guruhiga qo'shildi"}


@router.patch("/{group_id}/remove-student/{student_id}")
async def remove_student_from_group(
        group_id: int,
        student_id: int,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    """Studentni guruhdan chiqarish (faqat teacher)"""
    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Talaba topilmadi")
    if student.group_id != group_id:
        raise HTTPException(status_code=400, detail="Talaba bu guruhda emas")

    student.group_id = None
    await db.commit()
    return {"message": f"Talaba '{student.full_name or student.username}' guruhdan chiqarildi"}


@router.put("/{group_id}", response_model=GroupRead)
async def update_group(
        group_id: int,
        payload: GroupUpdate,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    """Guruhni yangilash (faqat teacher)"""
    service = GroupService(db)
    updated_group = await service.update_group(group_id, payload)
    if not updated_group:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")
    return updated_group


@router.delete("/{group_id}")
async def delete_group(
        group_id: int,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    """Guruhni o'chirish (faqat teacher)"""
    service = GroupService(db)
    success = await service.delete_group(group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")
    return {"message": "Guruh muvaffaqiyatli o'chirildi"}