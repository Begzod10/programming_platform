import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

from app.config import settings
from app.services.course_service import CourseService
from app.dependencies import get_db, get_current_student, get_current_teacher
from app.models.lesson import Lesson, LessonCompletion
from app.models.course import Course
from app.models.user import Student
from app.schemas.course import (
    CourseRead,
    CourseCreate,
    CourseUpdate,
    CourseReadWithStudents,
    CourseImageUploadResponse,
    CourseReorderRequest,
)

router = APIRouter()

UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "courses"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def _get_id_from_auth(request: Request) -> Optional[int]:
    """Tokenni dekod qilib, student ID sini qaytaradi (Xavfsiz variant)"""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None

    try:
        from app.core.security import decode_access_token
        token = auth.split(" ")[1]
        payload = decode_access_token(token)

        # Turli xil payload ko'rinishlarini tekshiramiz
        if isinstance(payload, int):
            return payload
        if isinstance(payload, str) and payload.isdigit():
            return int(payload)
        if isinstance(payload, dict):
            user_id = payload.get("sub") or payload.get("id") or payload.get("student_id")
            return int(user_id) if user_id else None
        return None
    except Exception:
        return None


def _translate_course_dto(dto, course, lang: Optional[str]) -> None:
    """Apply in-memory translations for title + description. No DB or AI calls."""
    if not lang:
        return
    src_lang = getattr(course, "source_lang", None) or "uz"
    if lang == src_lang:
        return
    from app.services import translation_store as ts
    for field_name in ("title", "description"):
        tr = ts.get("course", course.id, lang, field_name)
        if tr:
            setattr(dto, field_name, tr)


@router.get("/", response_model=List[CourseRead])
async def get_courses(
        request: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        category_id: Optional[int] = Query(None),
        lang: Optional[str] = Query(None),
        db: AsyncSession = Depends(get_db)
):
    student_id = await _get_id_from_auth(request)

    query = (
        select(Course)
        .options(selectinload(Course.instructor), selectinload(Course.category))
        .where(Course.is_active == True)
        .order_by(Course.display_order.asc(), Course.id.asc())
        .offset(skip).limit(limit)
    )
    if category_id is not None:
        query = query.where(Course.category_id == category_id)

    result = await db.execute(query)
    courses = result.scalars().all()

    dtos = [await CourseService.build_dto(db, c, student_id) for c in courses]

    # Parallel translation across the catalogue + a hard timeout. The old
    # version awaited each course's translation sequentially — 12 courses
    # × multi-second AI calls put the request well past Nginx's 30s window
    # and returned 504. asyncio.gather + a single wait_for keeps the total
    # latency bounded by the slowest single call.
    if lang:
        for c, dto in zip(courses, dtos):
            _translate_course_dto(dto, c, lang)
    return dtos


@router.get("/my", response_model=List[CourseRead])
async def get_my_courses(
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    """O'qituvchining o'ziga tegishli kurslari (422 xatosi oldi olindi)"""
    query = (
        select(Course)
        .options(
            selectinload(Course.instructor),
            selectinload(Course.lessons),
            selectinload(Course.students),
            selectinload(Course.category),
        )
        .where(Course.instructor_id == current_teacher.id)
        .order_by(Course.display_order.asc(), Course.id.asc())
    )
    result = await db.execute(query)
    courses = result.scalars().all()

    return [await CourseService.build_dto(db, c, current_teacher.id) for c in courses]


@router.put("/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_courses(
        payload: CourseReorderRequest,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db),
):
    """Bulk-update display_order for the teacher's own courses.

    The frontend sends the full new ordering after a drag-and-drop drop:
    [{"id": 3, "display_order": 0}, {"id": 1, "display_order": 1}, ...].
    Courses not owned by the caller are rejected (403) — the request is
    all-or-nothing so partial reorders never leak through.
    """
    ids = [item.id for item in payload.items]
    if len(ids) != len(set(ids)):
        raise HTTPException(status_code=400, detail="Duplicate course id in payload")

    rows = (
        await db.execute(
            select(Course).where(Course.id.in_(ids))
        )
    ).scalars().all()

    if len(rows) != len(ids):
        raise HTTPException(status_code=404, detail="One or more courses not found")
    for c in rows:
        if c.instructor_id != current_teacher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Faqat o'z kurslaringizning tartibini o'zgartirishingiz mumkin",
            )

    new_order_by_id = {item.id: item.display_order for item in payload.items}
    for c in rows:
        c.display_order = new_order_by_id[c.id]

    await db.commit()


@router.get("/{course_id}", response_model=CourseReadWithStudents)
async def get_course(
        course_id: int,
        request: Request,
        lang: Optional[str] = Query(None),
        db: AsyncSession = Depends(get_db),
):
    """Bitta kurs haqida to'liq ma'lumot"""
    student_id = await _get_id_from_auth(request)

    query = (
        select(Course)
        .options(
            selectinload(Course.instructor),
            selectinload(Course.lessons),
            selectinload(Course.students)
        )
        .where(Course.id == course_id)
    )

    result = await db.execute(query)
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")

    dto = await CourseService.build_dto(db, course, student_id)
    _translate_course_dto(dto, course, lang)
    return dto


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
async def create_course(
        payload: CourseCreate,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db),
):
    """Yangi kurs yaratish"""
    course_service = CourseService(db)
    new_course = await course_service.create_course(payload, current_teacher.id)

    # To'liq ma'lumot yuklash va DTO qurish
    summary = await CourseService.build_dto(db, new_course, current_teacher.id)
    return summary


@router.put("/{course_id}", response_model=CourseRead)
async def update_course(
        course_id: int,
        payload: CourseUpdate,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db),
):
    """Kursni tahrirlash (Service layer orqali)"""
    course_service = CourseService(db)
    updated_course = await course_service.update_course(course_id, payload, current_teacher.id)

    if not updated_course:
        raise HTTPException(404, "Kurs topilmadi")

    # DTO qurib qaytarish
    return await CourseService.build_dto(db, updated_course, current_teacher.id)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
        course_id: int,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db),
):
    """Kursni o'chirish"""
    course_service = CourseService(db)
    deleted = await course_service.delete_course(course_id, current_teacher.id)
    if not deleted:
        raise HTTPException(404, "Kurs topilmadi yoki sizga tegishli emas")
    return None


@router.post("/{course_id}/enroll")
async def enroll_course(
        course_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db),
):
    """Self-enrollment is disabled — a teacher must assign access."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Kursga yozilish o'qituvchi tomonidan amalga oshiriladi.",
    )


@router.post("/{course_id}/upload-image", response_model=CourseImageUploadResponse)
async def upload_course_image(
        course_id: int,
        file: UploadFile = File(...),
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    """Kurs rasmini yuklash"""
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(404, "Kurs topilmadi")
    if course.instructor_id != current_teacher.id:
        raise HTTPException(403, "Ruxsat berilmadi")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(400, "Faqat rasm formatlari ruxsat etiladi (.jpg/.png/.webp)")

    # Read with a hard cap so a teacher can't OOM the server by uploading
    # a multi-GB file. settings.MAX_FILE_SIZE defaults to 10 MB.
    max_bytes = settings.MAX_FILE_SIZE
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Fayl hajmi {max_bytes // (1024 * 1024)} MB dan oshmasligi kerak",
        )

    # Old image cleanup. Resolve to absolute path inside UPLOAD_DIR and
    # guard against path-traversal (the stored value should always be a
    # /uploads/courses/<file> path written by this same endpoint).
    if course.image_url:
        try:
            old_name = Path(course.image_url).name
            old_full = UPLOAD_DIR / old_name
            if old_full.is_file() and old_full.parent == UPLOAD_DIR:
                old_full.unlink()
        except OSError:
            pass  # best-effort cleanup; not fatal

    filename = f"course_{uuid.uuid4().hex}{ext}"
    full_path = UPLOAD_DIR / filename

    with open(full_path, "wb") as f:
        f.write(content)

    course.image_url = f"/uploads/courses/{filename}"
    await db.commit()

    return {"message": "Rasm yuklandi", "image_url": course.image_url}
