import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pathlib import Path

from app.config import settings
from app.dependencies import get_db, get_current_student, get_current_instructor
from app.schemas.user import UserRead, UserUpdate
from app.schemas.project import ProjectRead
from app.services.project_service import ProjectService
from app.services.student_service import StudentService
from app.models.user import Student

router = APIRouter()

UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "avatars"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/me", response_model=UserRead)
async def get_me(current_student: Student = Depends(get_current_student)):
    return current_student


@router.put("/me", response_model=UserRead)
async def update_my_profile(
        data: UserUpdate,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    service = StudentService(db)
    return await service.update_student(current_student.id, data)


@router.patch("/me/avatar")
async def upload_my_avatar(
        file: UploadFile = File(...),
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Faqat JPEG, PNG, WEBP!")

    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fayl 5MB dan katta!")

    # Eski avatarni o'chirish
    if current_student.avatar_url:
        old_path = UPLOAD_DIR / Path(current_student.avatar_url).name
        if old_path.exists():
            old_path.unlink()

    # Yangi fayl saqlash
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as f:
        f.write(contents)

    avatar_url = f"/uploads/avatars/{filename}"

    service = StudentService(db)
    await service.update_student(
        current_student.id,
        UserUpdate(avatar_url=avatar_url)
    )

    return {
        "avatar_url": avatar_url,
        "message": "Avatar muvaffaqiyatli yangilandi!"
    }


@router.delete("/me/avatar")
async def delete_my_avatar(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    if not current_student.avatar_url:
        raise HTTPException(status_code=404, detail="Avatar mavjud emas!")

    # ✅ To'g'ri path
    old_path = UPLOAD_DIR / Path(current_student.avatar_url).name
    if old_path.exists():
        old_path.unlink()

    service = StudentService(db)
    await service.update_student(
        current_student.id,
        UserUpdate(avatar_url=None)
    )
    return {"message": "Avatar o'chirildi!"}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    if current_student.avatar_url:
        old_path = UPLOAD_DIR / Path(current_student.avatar_url).name
        if old_path.exists():
            old_path.unlink()

    service = StudentService(db)
    await service.delete_student(current_student.id)
    return None


@router.get("/me/projects", response_model=List[ProjectRead])
async def get_my_projects(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    service = ProjectService(db)
    return await service.get_all_projects_by_student(student_id=current_student.id)


@router.get("/", response_model=List[UserRead])
async def get_students(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        search: str = Query(None),
        current_user: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    service = StudentService(db)
    return await service.get_all_students(skip=skip, limit=limit, search=search)


@router.get("/{student_id}", response_model=UserRead)
async def get_student_by_id(
        student_id: int,
        current_user: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    service = StudentService(db)
    student = await service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student topilmadi")
    return student


@router.put("/{student_id}", response_model=UserRead)
async def update_specific_student(
        student_id: int,
        data: UserUpdate,
        current_user: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
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
        current_teacher=Depends(get_current_instructor)
):
    result = await db.execute(select(Student))
    students = result.scalars().all()

    updated_count = 0
    for student in students:
        old_level = student.current_level
        student.total_points = student.total_points

        if old_level != student.current_level:
            updated_count += 1

    await db.commit()
    return {
        "status": "success",
        "total_students": len(students),
        "updated_levels_count": updated_count
    }
