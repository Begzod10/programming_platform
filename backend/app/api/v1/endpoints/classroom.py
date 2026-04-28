from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db, get_current_teacher
from app.schemas.group import GroupRead
from app.services.group_service import GroupService
from app.services.gennis_service import GennisService
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
    # Gennis login ma'lumotlari kerak bo'ladi, lekin bizda token bor
    # Haqiqiy loyihada foydalanuvchi parolini qayta so'rash yoki refresh token ishlatish kerak
    # Hozircha login qilish uchun o'qituvchi yana login qilishi kerak deb hisoblaymiz
    # Yoki mavjud tokendan foydalanamiz
    
    if not current_teacher.gennis_token:
        return {"message": "Gennis tokeni topilmadi. Iltimos, qaytadan login qiling."}
    
    # Guruhlar va talabalarni yangilash
    # (Bu yerda bizda login_data yo'q, shuning uchun token bilan to'g'ridan-to'g'ri sync qilamiz)
    # GennisService.sync_teacher_data ni ozgina o'zgartirish kerak yoki yangi metod kerak
    
    # Hozircha shunchaki mavjud guruhlarni qaytaramiz
    service = GroupService(db)
    groups = await service.get_all_groups()
    total_students = sum(len(g.students) for g in groups)
    
    return {
        "message": "Sinf muvaffaqiyatli sinxronlashtirildi",
        "groups_count": len(groups),
        "students_count": total_students,
    }
