"""Lesson file management endpoints (upload, download, preview)."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.dependencies import get_db, get_current_student, get_current_student_optional, get_current_instructor
from app.models.lesson import Lesson
from app.models.lesson_file import LessonFile
from app.models.user import Student

from .lesson_helpers import ALLOWED_CODE_EXTENSIONS, LESSONS_FILES_DIR, LESSON_PREVIEWS_DIR, _ensure_enrolled

router = APIRouter()


@router.get("/courses/{course_id}/lessons/{lesson_id}/download")
async def download_lesson_file_for_student(
        course_id: int,
        lesson_id: int,
        file_name: str,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db),
):
    lesson_res = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id)
    )
    lesson = lesson_res.scalar_one_or_none()
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    await _ensure_enrolled(db, current_student.id, course_id)

    file_row = (
        await db.execute(
            select(LessonFile)
            .where(
                LessonFile.lesson_id == lesson_id,
                LessonFile.original_name == file_name,
            )
            .order_by(LessonFile.created_at.desc())
        )
    ).scalars().first()
    if not file_row:
        raise HTTPException(status_code=404, detail="Fayl topilmadi")

    filepath = LESSONS_FILES_DIR / file_row.saved_name
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Fayl serverda topilmadi")

    return FileResponse(
        path=str(filepath),
        filename=file_row.original_name,
        media_type="application/octet-stream",
    )


@router.post("/{lesson_id}/files", status_code=status.HTTP_201_CREATED)
async def upload_lesson_file(
        lesson_id: int,
        file: UploadFile = File(...),
        label: str = Form(default=""),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """O'qituvchi darsga kod fayl yuklaydi — kodi o'qilib qaytariladi"""

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_CODE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Faqat kod fayllari qabul qilinadi: {', '.join(ALLOWED_CODE_EXTENSIONS)}"
        )

    contents = await file.read()

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Fayl bo'sh!")

    if len(contents) > 1 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fayl 1MB dan katta!")

    try:
        code_text = contents.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Fayl UTF-8 formatida emas!")

    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi!")

    filename = f"{uuid.uuid4()}{ext}"
    filepath = LESSONS_FILES_DIR / filename
    with open(filepath, "wb") as f:
        f.write(contents)

    lesson_file = LessonFile(
        lesson_id=lesson_id,
        original_name=file.filename,
        saved_name=filename,
        file_url=f"/uploads/lesson_files/{filename}",
        extension=ext,
        label=label,
        code_content=code_text,
        file_size=len(contents)
    )
    db.add(lesson_file)
    await db.commit()
    await db.refresh(lesson_file)

    return {
        "id": lesson_file.id,
        "lesson_id": lesson_id,
        "original_name": file.filename,
        "file_url": lesson_file.file_url,
        "extension": ext,
        "label": label,
        "code_content": code_text,
        "file_size": len(contents),
        "created_at": lesson_file.created_at
    }


@router.get("/{lesson_id}/files")
async def get_lesson_files(
        lesson_id: int,
        current_user: Optional[Student] = Depends(get_current_student_optional),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(LessonFile)
        .where(LessonFile.lesson_id == lesson_id)
        .order_by(LessonFile.created_at)
    )
    db_files = result.scalars().all()

    files = [
        {
            "id": f.id,
            "lesson_id": f.lesson_id,
            "original_name": f.original_name,
            "file_url": f.file_url,
            "extension": f.extension,
            "label": f.label,
            "code_content": f.code_content,
            "file_size": f.file_size,
            "preview_image_url": f.preview_image_url,
            "created_at": f.created_at
        }
        for f in db_files
    ]

    if not files:
        lesson_res = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
        lesson = lesson_res.scalar_one_or_none()
        if lesson and lesson.sections_json:
            try:
                sections = json.loads(lesson.sections_json)
                for section in sections:
                    for pf in section.get("projectFiles", []):
                        files.append({
                            "id": pf.get("_localId"),
                            "lesson_id": lesson_id,
                            "original_name": pf.get("filename") or pf.get("name"),
                            "file_url": None,
                            "extension": "." + pf.get("filename", "").split(".")[-1],
                            "label": pf.get("label", ""),
                            "code_content": pf.get("content") or pf.get("code"),
                            "file_size": pf.get("size"),
                            "created_at": None
                        })
            except Exception:
                pass

    return files


@router.get("/{lesson_id}/files/{file_id}")
async def get_lesson_file(
        lesson_id: int,
        file_id: int,
        current_user: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(LessonFile).where(
            LessonFile.id == file_id,
            LessonFile.lesson_id == lesson_id
        )
    )
    lesson_file = result.scalar_one_or_none()
    if not lesson_file:
        raise HTTPException(status_code=404, detail="Fayl topilmadi!")
    return {
        "id": lesson_file.id,
        "original_name": lesson_file.original_name,
        "file_url": lesson_file.file_url,
        "extension": lesson_file.extension,
        "label": lesson_file.label,
        "code_content": lesson_file.code_content,
        "file_size": lesson_file.file_size,
        "preview_image_url": lesson_file.preview_image_url,
        "created_at": lesson_file.created_at
    }


@router.post("/{lesson_id}/files/{file_id}/preview", status_code=status.HTTP_200_OK)
async def upload_lesson_file_preview(
        lesson_id: int,
        file_id: int,
        image: UploadFile = File(...),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Teacher uploads a preview screenshot for a lesson file."""
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if image.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Faqat rasm fayllari (JPEG, PNG, WebP, GIF)")

    result = await db.execute(
        select(LessonFile).where(LessonFile.id == file_id, LessonFile.lesson_id == lesson_id)
    )
    lesson_file = result.scalar_one_or_none()
    if not lesson_file:
        raise HTTPException(status_code=404, detail="Fayl topilmadi!")

    contents = await image.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Rasm 5MB dan katta bo'lmasin")

    if lesson_file.preview_image_url:
        old_name = Path(lesson_file.preview_image_url).name
        old_path = LESSON_PREVIEWS_DIR / old_name
        if old_path.exists():
            old_path.unlink()

    ext = Path(image.filename).suffix.lower() if image.filename else ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = LESSON_PREVIEWS_DIR / filename
    with open(filepath, "wb") as f:
        f.write(contents)

    lesson_file.preview_image_url = f"/uploads/lesson_previews/{filename}"
    await db.commit()
    await db.refresh(lesson_file)

    return {"preview_image_url": lesson_file.preview_image_url}


@router.delete("/{lesson_id}/files/{file_id}/preview", status_code=status.HTTP_200_OK)
async def delete_lesson_file_preview(
        lesson_id: int,
        file_id: int,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(LessonFile).where(LessonFile.id == file_id, LessonFile.lesson_id == lesson_id)
    )
    lesson_file = result.scalar_one_or_none()
    if not lesson_file:
        raise HTTPException(status_code=404, detail="Fayl topilmadi!")

    if lesson_file.preview_image_url:
        old_path = LESSON_PREVIEWS_DIR / Path(lesson_file.preview_image_url).name
        if old_path.exists():
            old_path.unlink()
        lesson_file.preview_image_url = None
        await db.commit()

    return {"ok": True}


@router.put("/{lesson_id}/files/{file_id}")
async def update_lesson_file(
        lesson_id: int,
        file_id: int,
        label: str = Body(default=None, embed=True),
        code_content: str = Body(default=None, embed=True),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Fayl label yoki kodni yangilash"""

    result = await db.execute(
        select(LessonFile).where(
            LessonFile.id == file_id,
            LessonFile.lesson_id == lesson_id
        )
    )
    lesson_file = result.scalar_one_or_none()
    if not lesson_file:
        raise HTTPException(status_code=404, detail="Fayl topilmadi!")

    if label is not None:
        lesson_file.label = label

    if code_content is not None:
        lesson_file.code_content = code_content
        filepath = LESSONS_FILES_DIR / lesson_file.saved_name
        if filepath.exists():
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code_content)

    await db.commit()
    await db.refresh(lesson_file)

    return {
        "id": lesson_file.id,
        "label": lesson_file.label,
        "code_content": lesson_file.code_content,
        "message": "Fayl yangilandi!"
    }


@router.delete("/{lesson_id}/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson_file(
        lesson_id: int,
        file_id: int,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Faylni o'chirish"""

    result = await db.execute(
        select(LessonFile).where(
            LessonFile.id == file_id,
            LessonFile.lesson_id == lesson_id
        )
    )
    lesson_file = result.scalar_one_or_none()
    if not lesson_file:
        raise HTTPException(status_code=404, detail="Fayl topilmadi!")

    filepath = LESSONS_FILES_DIR / lesson_file.saved_name
    if filepath.exists():
        filepath.unlink()

    await db.delete(lesson_file)
    await db.commit()
    return None


@router.get("/{lesson_id}/files/{file_id}/download")
async def download_lesson_file(
        lesson_id: int,
        file_id: int,
        current_user: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(LessonFile).where(
            LessonFile.id == file_id,
            LessonFile.lesson_id == lesson_id
        )
    )
    lesson_file = result.scalar_one_or_none()
    if not lesson_file:
        raise HTTPException(status_code=404, detail="Fayl topilmadi!")

    filepath = LESSONS_FILES_DIR / lesson_file.saved_name
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Fayl serverda topilmadi!")

    return FileResponse(
        path=str(filepath),
        filename=lesson_file.original_name,
        media_type="application/octet-stream"
    )
