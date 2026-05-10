import httpx
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.models.user import Student, UserRole
from app.models.group import Group

logger = logging.getLogger(__name__)

class GennisService:
    BASE_URL = settings.GENNIS_API_URL

    @classmethod
    async def login(cls, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Gennis tizimiga login qilish"""
        url = f"{cls.BASE_URL}/base/login"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json={"username": username, "password": password})
                if resp.status_code == 200:
                    return resp.json()
                logger.error(f"Gennis login muvaffaqiyatsiz: {resp.status_code}")
        except Exception as e:
            logger.error(f"Gennis login xatosi: {e}")
        return None

    @classmethod
    async def fetch_group_students(cls, group_id: int, token: str) -> List[Dict[str, Any]]:
        """Guruhdagi barcha talabalarni Gennis API dan tortib olish"""
        url = f"{cls.BASE_URL}/group/students/{group_id}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("students", []) if isinstance(data, dict) else data
        except Exception as e:
            logger.error(f"Talabalarni olishda xato: {e}")
        return []

    @classmethod
    async def sync_teacher_data(cls, db: AsyncSession, teacher: Student, login_data: Dict[str, Any]):
        """O'qituvchi va uning barcha guruh/talabalarni sinxronlash"""
        token = login_data.get("access_token")
        user_info = login_data.get("user", {})
        teacher_info = user_info.get("teacher", {})
        groups_data = teacher_info.get("group", [])

        # O'qituvchi profilini yangilash
        teacher.gennis_token = token
        teacher.full_name = f"{user_info.get('name', '')} {user_info.get('surname', '')}".strip()
        
        phones = user_info.get("phone", [])
        if phones:
            teacher.phone = str(phones[0].get("phone"))[:50]

        await db.flush()

        for g_data in groups_data:
            group = await cls._sync_group(db, g_data, teacher.id)
            
            # Guruh talabalarini yangilash
            students_list = await cls.fetch_group_students(group.gennis_id, token)
            for s_data in students_list:
                await cls._sync_student(db, s_data, group.id)

        await db.commit()
        logger.info(f"O'qituvchi {teacher.username} sinxronizatsiyasi yakunlandi.")

    @classmethod
    async def sync_student_data(cls, db: AsyncSession, student: Student, login_data: Dict[str, Any]):
        """Talaba ma'lumotlarini va ism-familiyasini sinxronlash"""
        token = login_data.get("access_token")
        user_info = login_data.get("user", {})
        student_info = user_info.get("student", {})
        groups_data = student_info.get("group", [])

        # Ismlarni yangilash
        student.gennis_token = token
        student.full_name = f"{user_info.get('name', '')} {user_info.get('surname', '')}".strip()
        student.surname = user_info.get("surname", "")
        student.balance = user_info.get("balance", student_info.get("combined_debt", 0))
        
        phones = user_info.get("phone", [])
        if phones:
            student.phone = str(phones[0].get("phone"))[:50]

        await db.flush()

        # Talabani guruhlari bilan qayta yuklash
        result = await db.execute(
            select(Student).filter(Student.id == student.id).options(selectinload(Student.groups))
        )
        student = result.scalar_one()

        for g_data in groups_data:
            group = await cls._sync_group(db, g_data)
            
            # Xavfsiz bog'lash: ON CONFLICT DO NOTHING
            query = text("""
                INSERT INTO student_groups (student_id, group_id)
                VALUES (:s_id, :g_id)
                ON CONFLICT (student_id, group_id) DO NOTHING
            """)
            await db.execute(query, {"s_id": student.id, "g_id": group.id})
            student.group_id = group.id

        await db.commit()
        logger.info(f"Talaba {student.username} ma'lumotlari yangilandi.")

    @classmethod
    async def _sync_group(cls, db: AsyncSession, g_data: Dict[str, Any], teacher_id: Optional[int] = None) -> Group:
        """Guruhni bazada yaratish yoki yangilash"""
        g_id = g_data.get("id")
        result = await db.execute(select(Group).where(Group.gennis_id == g_id))
        group = result.scalar_one_or_none()

        if not group:
            group = Group(
                name=g_data.get("name"),
                gennis_id=g_id,
                price=g_data.get("price", 0),
                teacher_id=teacher_id
            )
            db.add(group)
        else:
            group.name = g_data.get("name")
            group.price = g_data.get("price", 0)
            if teacher_id:
                group.teacher_id = teacher_id
        
        await db.flush()
        return group

    @classmethod
    async def _sync_student(cls, db: AsyncSession, s_data: Dict[str, Any], group_id: int) -> Student:
        """Talabani ism-familiyasi bilan birga sinxronlash (O'qituvchi logini uchun)"""
        s_id = s_data.get("id")
        s_username = f"gennis_{s_id}"
        
        # Ismlarni tayyorlash
        first_name = s_data.get("name", "")
        last_name = s_data.get("surname", "")
        full_name = f"{first_name} {last_name}".strip()
        if not full_name:
            full_name = s_username # Agar ism kelmasa username qo'yiladi

        result = await db.execute(select(Student).where(Student.username == s_username))
        student = result.scalar_one_or_none()

        if not student:
            student = Student(
                username=s_username,
                email=f"{s_username}@gennis.uz",
                full_name=full_name,
                hashed_password="external_auth",
                role=UserRole.student,
                phone=str(s_data.get("phone"))[:50],
                balance=s_data.get("balance", 0),
                surname=last_name,
                group_id=group_id
            )
            db.add(student)
            await db.flush()
        else:
            # Mavjud talaba ismini yangilash
            student.full_name = full_name
            student.surname = last_name
            student.phone = str(s_data.get("phone"))[:50]
            student.balance = s_data.get("balance", 0)
            student.group_id = group_id

        # Bog'liqlikni bazada yangilash (Xato bermasligi uchun ON CONFLICT)
        query = text("""
            INSERT INTO student_groups (student_id, group_id)
            VALUES (:s_id, :g_id)
            ON CONFLICT (student_id, group_id) DO NOTHING
        """)
        await db.execute(query, {"s_id": student.id, "g_id": group_id})
        
        await db.flush()
        return student