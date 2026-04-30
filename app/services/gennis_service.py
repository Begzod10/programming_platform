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
                if resp.status_code == 200:
                    return resp.json()
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

        user_data = login_data.get("data", {}).get("user", {})
        teacher_info = user_data.get("teacher", {})
        groups_data = teacher_info.get("groups", [])

        print(f"  - 1. Syncing teacher {teacher.username} info...")
        # 1. O'qituvchining Gennis tokenini saqlash
        teacher.gennis_token = token
        # Agar familiyasi bo'lsa
        if "surname" in user_data:
            teacher.surname = user_data["surname"]
        
        await db.commit()

        # 2. Guruhlarni sinxronlash
        print(f"  - 2. Syncing {len(groups_data)} groups...")
        for g_data in groups_data:
            g_id = g_data.get("id")
            g_name = g_data.get("name")
            g_price = g_data.get("price", 0)
            print(f"    - Processing group: {g_name} (ID: {g_id})")

            # Guruh mavjudligini tekshirish
            stmt = select(Group).where(Group.gennis_id == g_id)
            result = await db.execute(stmt)
            group = result.scalar_one_or_none()

            if not group:
                print(f"      - Creating new group: {g_name}")
                group = Group(
                    name=g_name,
                    gennis_id=g_id,
                    price=g_price
                )
                db.add(group)
                await db.commit()
                await db.refresh(group)
            else:
                print(f"      - Updating existing group: {g_name}")
                group.name = g_name
                group.price = g_price
                await db.commit()

            # 3. Talabalarni sinxronlash
            print(f"    - 3. Fetching students for group {g_id}...")
            students_list = await cls.fetch_group_students(g_id, token)
            print(f"      - Found {len(students_list)} students in Gennis.")
            for s_data in students_list:
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
                    print(f"      - Creating new student: {s_name} {s_surname} ({s_username})")
                    student = Student(
                        username=s_username,
                        email=f"{s_username}@gennis.uz",
                        full_name=f"{s_name} {s_surname}",
                        hashed_password="external_auth", # Parol shart emas
                        role=UserRole.student,
                        phone=s_phone,
                        balance=s_balance,
                        surname=s_surname,
                        group_id=group.id
                    )
                    db.add(student)
                else:
                    print(f"      - Updating student: {s_name} {s_surname}")
                    student.full_name = f"{s_name} {s_surname}"
                    student.phone = s_phone
                    student.balance = s_balance
                    student.surname = s_surname
                    student.group_id = group.id
                
            await db.commit()

        print(f"✅ Sync completed for teacher {teacher.username}")
