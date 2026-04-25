from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import io
import os

from app.dependencies import get_db, get_current_student, get_current_instructor
from app.services import achievement_service
from app.utils.certificate import generate_certificate
from app.schemas.achievement import (
    AchievementCreate,
    AchievementUpdate,
    AchievementRead,
    StudentAchievementRead,
    AchievementProgress,
    StudentWithAchievementRead,
    StudentWithoutAchievementRead,
    AchievementStatistics,
    CertificateRead
)

router = APIRouter()


@router.get("/my", response_model=List[StudentAchievementRead])
async def my_achievements(
        current_student=Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    # Avtomatik tekshiruv va berish (Badge va Sertifikat)
    await achievement_service.check_and_award_achievements(db, current_student.id)
    
    results = await achievement_service.get_my_achievements(db, current_student.id)
    return [StudentAchievementRead.from_orm_custom(sa) for sa in results]


@router.get("/my-progress", response_model=List[AchievementProgress])
async def my_achievement_progress(
        current_student=Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Talaba hali olmagan yutuqlari bo'yicha progressni ko'rishi"""
    # Bu yerda ham tekshirib qo'yamiz
    await achievement_service.check_and_award_achievements(db, current_student.id)
    return await achievement_service.get_achievement_progress(db, current_student.id)


@router.get("/my-certificates", response_model=List[CertificateRead])
async def my_certificates(
        current_student=Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Talaba sertifikatlarini ko'rish"""
    # Har safar kirganda tekshiramiz va beramiz (BUG FIX: hamma userlar uchun)
    await achievement_service.check_and_award_achievements(db, current_student.id)
    
    certs = await achievement_service.get_my_certificates(db, current_student.id)
    return [
        CertificateRead(
            id=c.id,
            course_id=c.course_id,
            course_title=c.course.title,
            issued_at=c.issued_at
        ) for c in certs
    ]


@router.post("/check-and-earn-certificate")
async def check_and_earn_certificate(
        course_id: int = Query(...),
        current_student=Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Avtomatik sertifikat berish mantiqi"""
    cert = await achievement_service.award_certificate(db, current_student.id, course_id)
    if not cert:
        # Tekshiramiz: Kurs tugaganmi?
        is_complete = await achievement_service.check_course_completion(db, current_student.id, course_id)
        if not is_complete:
            return {"message": "Siz hali kursni tugatmagansiz", "issued": False}
        return {"message": "Sertifikat allaqachon mavjud", "issued": False}
    return {"message": "Tabriklaymiz! Sertifikat berildi!", "certificate_id": cert.id, "issued": True}


@router.get("/all", response_model=List[AchievementRead])
async def get_all_achievements(
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Barcha mavjud yutuqlar turlari ro'yxati"""
    return await achievement_service.get_all_achievements(db)


@router.post("/create", response_model=AchievementRead, status_code=status.HTTP_201_CREATED)
async def create_achievement(
        data: AchievementCreate,
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Yangi yutuq turi yaratish"""
    return await achievement_service.create_achievement(db, **data.model_dump())


@router.put("/{achievement_id}", response_model=AchievementRead)
async def update_achievement(
        achievement_id: int,
        data: AchievementUpdate,
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Yutuq ma'lumotlarini o'zgartirish"""
    return await achievement_service.update_achievement(db, achievement_id, **data.model_dump(exclude_unset=True))


@router.post("/award")
async def award_achievement_manual(
        student_id: int = Query(...),
        achievement_id: int = Query(...),
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """O'qituvchi tomonidan talabaga yutuqni qo'lda berish"""
    result = await achievement_service.award_achievement(db, student_id, achievement_id)
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Yutuq allaqachon berilgan yoki ma'lumotlarda xatolik bor"
        )
    return {"message": "Yutuq muvaffaqiyatli berildi", "data": result}


@router.delete("/{achievement_id}", status_code=status.HTTP_200_OK)
async def delete_achievement(
        achievement_id: int,
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Yutuqni o'chirish"""
    result = await achievement_service.delete_achievement(db, achievement_id)
    if not result:
        raise HTTPException(status_code=404, detail="Yutuq topilmadi")
    return {"message": "Muvaffaqiyatli o'chirildi"}


@router.get("/{achievement_id}/statistics", response_model=AchievementStatistics)
async def get_achievement_stats(
        achievement_id: int,
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Yutuq statistikasi (Olganlar va olmaganlar soni)"""
    return await achievement_service.get_achievement_statistics(db, achievement_id)


@router.get("/{achievement_id}/students-with", response_model=List[StudentWithAchievementRead])
async def get_earned_students(
        achievement_id: int,
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Frontend 'Получили' tabi uchun"""
    return await achievement_service.get_students_with_achievement(db, achievement_id)


@router.get("/{achievement_id}/students-without", response_model=List[StudentWithoutAchievementRead])
async def get_not_earned_students(
        achievement_id: int,
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Frontend 'Не получили' tabi uchun"""
    return await achievement_service.get_students_without_achievement(db, achievement_id)


@router.get("/{achievement_id}/download")
async def download_achievement_pdf(
        achievement_id: int,
        current_student=Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Yutuqni (Badge) PDF shaklida yuklab olish"""
    pdf_buffer = await achievement_service.generate_certificate_pdf(db, current_student.id, achievement_id)

    if not pdf_buffer or pdf_buffer in ["error", "template_missing"]:
        raise HTTPException(status_code=400, detail="Fayl yaratishda xatolik")

    pdf_buffer.seek(0)
    filename = f"Badge_{current_student.username}_{achievement_id}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/course/{course_id}/download")
async def download_course_certificate(
        course_id: int,
        current_student=Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    cert = await achievement_service.get_course_certificate(db, current_student.id, course_id)
    if not cert:
        # Tekshiramiz: kurs tugatilganmi?
        is_complete = await achievement_service.check_course_completion(db, current_student.id, course_id)
        if not is_complete:
            raise HTTPException(status_code=400, detail="Siz hali kursni tugatmagansiz")
        raise HTTPException(status_code=404, detail="Sertifikat topilmadi")

    student_name = current_student.full_name or current_student.username
    course_name = cert.course.title
    cert_number = cert.id

    pdf_output = generate_certificate(student_name, course_name, cert_number)

    if isinstance(pdf_output, bytes):
        pdf_output = io.BytesIO(pdf_output)

    filename = f"Certificate_{course_id}.pdf"
    return StreamingResponse(
        pdf_output,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.delete("/{achievement_id}/revoke", status_code=status.HTTP_200_OK)
async def revoke_achievement(
        achievement_id: int,
        student_id: int = Query(...),
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """O'qituvchi tomonidan talabadan yutuqni qaytarib olish"""
    result = await achievement_service.revoke_achievement(db, student_id, achievement_id)
    if not result:
        raise HTTPException(status_code=404, detail="Yutuq topilmadi yoki talabada mavjud emas")
    return {"message": "Yutuq muvaffaqiyatli qaytarib olindi"}


@router.delete("/{achievement_id}/revoke", status_code=status.HTTP_200_OK)
async def revoke_achievement_from_student(
        achievement_id: int,
        student_id: int = Query(...),
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """O'qituvchi tomonidan talabadan yutuqni qaytarib olish"""
    result = await achievement_service.revoke_achievement(db, student_id, achievement_id)
    if not result:
        raise HTTPException(status_code=404, detail="Yutuq topilmadi yoki talabada mavjud emas")
    return {"message": "Yutuq muvaffaqiyatli qaytarib olindi"}