from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db, get_current_student, get_current_instructor
from app.schemas.user import UserRead, UserUpdate
from app.schemas.project import ProjectRead
from app.services.project_service import ProjectService
from app.services.student_service import StudentService
from app.models.user import Student

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_me(current_student: Student = Depends(get_current_student)):
    """Joriy foydalanuvchi (o'zi) haqida ma'lumot olish"""
    return current_student


@router.put("/me", response_model=UserRead)
async def update_my_profile(
        data: UserUpdate,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """O'z profilini tahrirlash"""
    service = StudentService(db)
    return await service.update_student(current_student.id, data)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Student o'z akkauntini o'chirishi (ID talab qilinmaydi)"""
    service = StudentService(db)
    await service.delete_student(current_student.id)
    return None


@router.get("/me/projects", response_model=List[ProjectRead])
async def get_my_projects(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Faqat o'ziga tegishli loyihalarni olish"""
    service = ProjectService(db)
    return await service.get_projects_by_student(student_id=current_student.id)


# --- UMUMIY VA MA'MURIY (ADMIN/TEACHER) SECTION ---

@router.get("/", response_model=List[UserRead])
async def get_students(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        search: str = Query(None),
        db: AsyncSession = Depends(get_db)
):
    """Barcha studentlarni ro'yxatini olish"""
    service = StudentService(db)
    return await service.get_all_students(skip=skip, limit=limit, search=search)


@router.get("/{student_id}", response_model=UserRead)
async def get_student_by_id(
        student_id: int,
        db: AsyncSession = Depends(get_db)
):
    """ID orqali istalgan student ma'lumotini ko'rish"""
    service = StudentService(db)
    student = await service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student topilmadi")
    return student


@router.put("/{student_id}", response_model=UserRead)
async def update_specific_student(
        student_id: int,
        data: UserUpdate,
        current_user: Student = Depends(get_current_student),  # Bu yerda role tekshiruvi muhim
        db: AsyncSession = Depends(get_db)
):
    """
    Ma'lum bir ID dagi studentni yangilash.
    Agar student bo'lsa - faqat o'zini. Agar Admin bo'lsa - hamma studentni.
    """
    # Xavfsizlik filtri: Agar user student bo'lsa va birovni ID sini yuborsa - rad etish
    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sizda boshqa student ma'lumotlarini o'zgartirish huquqi yo'q"
        )

    service = StudentService(db)
    student = await service.update_student(student_id, data)
    if not student:
        raise HTTPException(status_code=404, detail="Student topilmadi")
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_specific_student(
        student_id: int,
        current_user: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Studentni o'chirish (Faqat o'zi yoki Admin uchun)"""
    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sizda bu akkauntni o'chirish huquqi yo'q"
        )

    service = StudentService(db)
    success = await service.delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student topilmadi")
    return None


@router.post("/refresh-all-student-levels")
async def refresh_all_student_levels(
        db: AsyncSession = Depends(get_db),
        current_teacher=Depends(get_current_instructor)  # Faqat admin/teacher qila olsin
):
    """Bazadagi barcha studentlarning darajasini ballariga qarab to'g'rilab chiqish"""
    result = await db.execute(select(Student))
    students = result.scalars().all()

    updated_count = 0
    for student in students:
        old_level = student.current_level
        student.update_level_based_on_points()

        if old_level != student.current_level:
            updated_count += 1

    await db.commit()
    return {
        "status": "success",
        "total_students": len(students),
        "updated_levels_count": updated_count
    }
