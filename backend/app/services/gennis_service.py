import httpx
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.user import Student, UserRole
from app.models.group import Group

logger = logging.getLogger(__name__)

class GennisService:
    BASE_URL = settings.GENNIS_API_URL # https://admin.gennis.uz/api

    @classmethod
    async def login(cls, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Gennis tizimiga login qilish va ma'lumotlarni olish"""
        url = f"{cls.BASE_URL}/base/login"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json={"username": username, "password": password})
                print(f"Gennis login response status: {resp.status_code}")
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"Gennis login success: {data.get('user', {}).get('username')}")
                    return data
                print(f"Gennis login failed text: {resp.text}")
                logger.error(f"Gennis login failed: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"Gennis login error: {e}")
        return None

    @classmethod
    async def fetch_group_students(cls, group_id: int, token: str) -> List[Dict[str, Any]]:
        """Guruhdagi talabalarni olish"""
        # Tajribadan ma'lumki, endpoint /group/students/{id} bo'lishi mumkin
        url = f"{cls.BASE_URL}/group/students/{group_id}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    # Ba'zan data['students'] ko'rinishida keladi
                    if isinstance(data, dict):
                        return data.get("students", [])
                    return data
                logger.error(f"Failed to fetch students for group {group_id}: {resp.status_code}")
        except Exception as e:
            logger.error(f"Error fetching students: {e}")
        return []

    @classmethod
    async def sync_teacher_data(cls, db: AsyncSession, teacher: Student, login_data: Dict[str, Any]):
        """O'qituvchi ma'lumotlarini va uning guruhlarini/talabalarini sinxronlash"""
        token = login_data.get("access_token")
        if not token:
            return

        user_info = login_data.get("user", {})
        teacher_info = user_info.get("teacher", {})
        groups_data = teacher_info.get("group", []) # API structure shows 'group' list inside 'teacher'

        # 1. O'qituvchi ma'lumotlarini yangilash
        teacher.gennis_token = token
        teacher.surname = user_info.get("surname", teacher.surname)
        name = user_info.get("name", "")
        surname = user_info.get("surname", "")
        if name or surname:
            teacher.full_name = f"{name} {surname}".strip()
        
        # Phone handling
        phones = user_info.get("phone", [])
        if phones and isinstance(phones, list):
            teacher.phone = phones[0].get("phone")

        await db.commit()

        # 2. Guruhlarni sinxronlash
        for g_data in groups_data:
            group = await cls._sync_group(db, g_data, teacher.id)
            
            # 3. Talabalarni sinxronlash (O'qituvchi guruhidagi hamma talabalarni tortib kelamiz)
            students_list = await cls.fetch_group_students(group.gennis_id, token)
            for s_data in students_list:
                await cls._sync_student(db, s_data, group.id)

        logger.info(f"Sync completed for teacher {teacher.username}")

    @classmethod
    async def sync_student_data(cls, db: AsyncSession, student: Student, login_data: Dict[str, Any]):
        """Talaba ma'lumotlarini va uning guruhlarini sinxronlash"""
        token = login_data.get("access_token")
        if not token:
            return

        user_info = login_data.get("user", {})
        student_info = user_info.get("student", {})
        groups_data = student_info.get("group", []) # API structure shows 'group' list inside 'student'

        # 1. Talaba ma'lumotlarini yangilash
        student.gennis_token = token
        student.surname = user_info.get("surname", student.surname)
        
        name = user_info.get("name", "")
        surname = user_info.get("surname", "")
        if name or surname:
            student.full_name = f"{name} {surname}".strip()

        # Phone handling
        phones = user_info.get("phone", [])
        if phones and isinstance(phones, list):
            student.phone = phones[0].get("phone")

        # Balance/Debt handling
        if "balance" in user_info:
            student.balance = user_info["balance"]
        elif "combined_debt" in student_info:
            student.balance = student_info["combined_debt"]
        
        await db.commit()

        # 2. Guruhlarni sinxronlash
        for g_data in groups_data:
            group = await cls._sync_group(db, g_data)
            # Talabani shu guruhga biriktirish
            student.group_id = group.id
        
        await db.commit()
        logger.info(f"Sync completed for student {student.username}")

    @classmethod
    async def _sync_group(cls, db: AsyncSession, g_data: Dict[str, Any], teacher_id: Optional[int] = None) -> Group:
        """Guruhni sinxronlash helper funksiyasi"""
        g_id = g_data.get("id")
        g_name = g_data.get("name")
        g_price = g_data.get("price", 0)

        stmt = select(Group).where(Group.gennis_id == g_id)
        result = await db.execute(stmt)
        group = result.scalar_one_or_none()

        if not group:
            group = Group(
                name=g_name,
                gennis_id=g_id,
                price=g_price,
                teacher_id=teacher_id
            )
            db.add(group)
            await db.commit()
            await db.refresh(group)
        else:
            group.name = g_name
            group.price = g_price
            if teacher_id:
                group.teacher_id = teacher_id
            await db.commit()
        return group

    @classmethod
    async def _sync_student(cls, db: AsyncSession, s_data: Dict[str, Any], group_id: int) -> Student:
        """Talabani sinxronlash helper funksiyasi"""
        s_id = s_data.get("id")
        s_name = s_data.get("name")
        s_surname = s_data.get("surname")
        s_phone = s_data.get("phone")
        s_balance = s_data.get("balance", 0)
        
        s_username = f"gennis_{s_id}"
        
        stmt = select(Student).where(Student.username == s_username)
        result = await db.execute(stmt)
        student = result.scalar_one_or_none()

        if not student:
            student = Student(
                username=s_username,
                email=f"{s_username}@gennis.uz",
                full_name=f"{s_name} {s_surname}",
                hashed_password="external_auth",
                role=UserRole.student,
                phone=s_phone,
                balance=s_balance,
                surname=s_surname,
                group_id=group_id
            )
            db.add(student)
        else:
            student.full_name = f"{s_name} {s_surname}"
            student.phone = s_phone
            student.balance = s_balance
            student.surname = s_surname
            student.group_id = group_id
        
        await db.commit()
        return student
