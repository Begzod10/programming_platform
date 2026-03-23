import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db, get_current_student, get_current_instructor
from app.models.course import Course
from app.models.user import Student
from app.schemas.course import (
    CourseRead,
    CourseCreate,
    CourseUpdate,
    CourseReadWithStudents,
    CourseImageUploadResponse,
)

router = APIRouter()

UPLOAD_DIR = Path("uploads/courses")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def add_computed_fields(course) -> dict:
    """Hisoblangan fieldlarni qo'shish helper"""
    return {
        **course.__dict__,
        "lessons_count": len(course.lessons) if hasattr(course, 'lessons') else 0,
        "students_count": len(course.students) if hasattr(course, 'students') else 0
    }


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
async def create_course(
        payload: CourseCreate,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db),
):
    """Yangi kurs yaratish (faqat teacher)"""
    course_data = payload.model_dump()
    course_data["instructor_id"] = current_teacher.id

    new_course = Course(**course_data)
    db.add(new_course)
    await db.commit()
    await db.refresh(new_course)

    # ✅ Hisoblangan fieldlar bilan qaytarish
    return CourseRead(
        **new_course.__dict__,
        lessons_count=0,
        students_count=0
    )


@router.get("/", response_model=List[CourseRead])
async def get_courses(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        search: Optional[str] = Query(None),
        difficulty_level: Optional[str] = Query(None),
        is_active: Optional[bool] = Query(None),
        db: AsyncSession = Depends(get_db)
):
    """Barcha kurslar (public)"""
    # ✅ Lessons va students'ni ham yuklaymiz
    query = select(Course).options(
        selectinload(Course.lessons),
        selectinload(Course.students)
    )

    if search:
        query = query.where(or_(
            Course.title.ilike(f"%{search}%"),
            Course.description.ilike(f"%{search}%")
        ))

    if difficulty_level:
        query = query.where(Course.difficulty_level == difficulty_level)

    if is_active is not None:
        query = query.where(Course.is_active == is_active)

    query = query.order_by(Course.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    courses = result.scalars().all()

    # ✅ Hisoblangan fieldlar bilan qaytarish
    return [CourseRead(**add_computed_fields(c)) for c in courses]


@router.get("/my", response_model=List[CourseRead])
async def get_my_courses(
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db),
):
    """O'z kurslarim (faqat teacher)"""
    query = (
        select(Course)
        .options(selectinload(Course.lessons), selectinload(Course.students))
        .where(Course.instructor_id == current_teacher.id)
    )
    result = await db.execute(query)
    courses = result.scalars().all()

    return [CourseRead(**add_computed_fields(c)) for c in courses]


@router.get("/{course_id}", response_model=CourseReadWithStudents)
async def get_course(
        course_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Kurs haqida to'liq ma'lumot"""
    query = (
        select(Course)
        .options(selectinload(Course.students), selectinload(Course.lessons))
        .where(Course.id == course_id)
    )
    result = await db.execute(query)
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")

    return CourseReadWithStudents(**add_computed_fields(course))


@router.put("/{course_id}", response_model=CourseRead)
async def update_course(
        course_id: int,
        payload: CourseUpdate,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db),
):
    """Kursni yangilash (faqat egasi)"""
    query = (
        select(Course)
        .options(selectinload(Course.lessons), selectinload(Course.students))
        .where(Course.id == course_id)
    )
    result = await db.execute(query)
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")

    if course.instructor_id != current_teacher.id:
        raise HTTPException(
            status_code=403,
            detail="Faqat o'z kursingizni tahrirlashingiz mumkin"
        )

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(course, key, value)

    course.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(course)

    return CourseRead(**add_computed_fields(course))


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
        course_id: int,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Kursni o'chirish (faqat egasi)"""
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")

    if course.instructor_id != current_teacher.id:
        raise HTTPException(
            status_code=403,
            detail="Faqat o'z kursingizni o'chirishingiz mumkin"
        )

    await db.delete(course)
    await db.commit()

    return None


@router.post("/{course_id}/enroll")
async def enroll_course(
        course_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db),
):
    """Kursga yozilish"""
    course_result = await db.execute(select(Course).where(Course.id == course_id))
    course = course_result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")

    if not course.is_active:
        raise HTTPException(status_code=400, detail="Kurs faol emas")

    student_result = await db.execute(
        select(Student)
        .options(selectinload(Student.enrolled_courses))
        .where(Student.id == current_student.id)
    )
    student = student_result.scalar_one()

    if course in student.enrolled_courses:
        raise HTTPException(
            status_code=400,
            detail="Siz allaqachon bu kursga yozilgansiz"
        )

    student.enrolled_courses.append(course)
    await db.commit()

    return {
        "message": f"'{course.title}' kursiga muvaffaqiyatli yozildingiz",
        "course_id": course.id,
        "course_title": course.title
    }


@router.delete("/{course_id}/unenroll")
async def unenroll_course(
        course_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db),
):
    """Kursdan chiqish"""
    course_result = await db.execute(select(Course).where(Course.id == course_id))
    course = course_result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")

    student_result = await db.execute(
        select(Student)
        .options(selectinload(Student.enrolled_courses))
        .where(Student.id == current_student.id)
    )
    student = student_result.scalar_one()

    if course not in student.enrolled_courses:
        raise HTTPException(
            status_code=400,
            detail="Siz bu kursga yozilmagansiz"
        )

    student.enrolled_courses.remove(course)
    await db.commit()

    return {"message": f"'{course.title}' kursidan chiqildingiz"}


@router.post("/{course_id}/upload-cover", response_model=CourseImageUploadResponse)
async def upload_course_cover(
        course_id: int,
        file: UploadFile = File(...),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Kurs cover rasmini yuklash (faqat egasi)"""
    query = (
        select(Course)
        .options(selectinload(Course.lessons), selectinload(Course.students))
        .where(Course.id == course_id)
    )
    result = await db.execute(query)
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")

    if course.instructor_id != current_teacher.id:
        raise HTTPException(
            status_code=403,
            detail="Faqat o'z kursingizni tahrirlashingiz mumkin"
        )

    # Fayl formatini tekshirish
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Faqat rasm yuklash mumkin: {', '.join(allowed_extensions)}"
        )

    # Fayl hajmini tekshirish (5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Fayl hajmi 5MB dan oshmasligi kerak"
        )

    # Unique fayl nomi
    unique_filename = f"cover_{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    # Eski faylni o'chirish
    if course.cover_image_url:
        old_file = Path(".") / course.cover_image_url.lstrip("/")
        if old_file.exists():
            os.remove(old_file)

    # Yangi faylni saqlash
    with open(file_path, "wb") as f:
        f.write(contents)

    # ✅ Ikkalasini ham yangilash (React va Backend uchun)
    cover_url = f"/uploads/courses/{unique_filename}"
    course.cover_image_url = cover_url
    course.image_url = cover_url  # React uchun
    course.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(course)

    return {
        "message": "Cover rasm muvaffaqiyatli yuklandi",
        "image_url": cover_url,
        "course": CourseRead(**add_computed_fields(course))
    }


@router.delete("/{course_id}/cover")
async def delete_course_cover(
        course_id: int,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Kurs cover rasmini o'chirish (faqat egasi)"""
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")

    if course.instructor_id != current_teacher.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    # Eski faylni o'chirish
    if course.cover_image_url:
        old_file = Path(".") / course.cover_image_url.lstrip("/")
        if old_file.exists():
            os.remove(old_file)

    # ✅ Ikkalasini ham NULL qilish
    course.cover_image_url = None
    course.image_url = None
    course.updated_at = datetime.utcnow()

    await db.commit()

    return {"message": "Cover rasm o'chirildi"}