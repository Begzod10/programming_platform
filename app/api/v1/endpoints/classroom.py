from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.dependencies import get_db, get_current_teacher
from app.models.user import Student, UserRole
from app.services.ranking_service import RankingService
from app.core.security import get_password_hash

router = APIRouter()

ADMIN_API = "https://admin.gennis.uz/api"
ADMIN_USERNAME = "rimefara_teach"
ADMIN_PASSWORD = "22100122"
PLATFORM_GROUP_IDS = [458, 506, 610, 757]


async def get_admin_token() -> str:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            f"{ADMIN_API}/base/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("access_token", "")
    return ""


async def get_group_profile(token: str, group_id: int) -> dict:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{ADMIN_API}/group/group_profile/{group_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
    return {}


async def get_all_admin_students(token: str) -> dict:
    """Admin dan barcha studentlarni username bo'yicha dict qaytaradi"""
    all_students = {}
    for group_id in PLATFORM_GROUP_IDS:
        profile = await get_group_profile(token, group_id)
        students_raw = profile.get("data", {}).get("students", [])
        for s in students_raw:
            username = s.get("username", "").strip().replace(" ", "_")
            if username:
                all_students[username] = s
    return all_students


def parse_students(students_raw: list) -> list:
    result = []
    for s in students_raw:
        result.append({
            "id": s.get("id"),
            "name": s.get("name"),
            "surname": s.get("surname"),
            "username": s.get("username"),
            "phone": s.get("phone"),
            "balance": s.get("money", 0),
            "moneyType": s.get("moneyType"),
            "is_debtor": s.get("money", 0) < 0,
            "age": s.get("age"),
        })
    return result


@router.get("/groups")
async def get_classroom_groups(
        current_teacher: Student = Depends(get_current_teacher)
):
    """Admin.gennis.uz dan barcha guruhlar va o'quvchilarni olish"""
    try:
        token = await get_admin_token()
        if not token:
            raise HTTPException(status_code=401, detail="Admin API ga ulanib bo'lmadi")

        result = []
        for group_id in PLATFORM_GROUP_IDS:
            profile = await get_group_profile(token, group_id)
            if not profile:
                continue
            students_raw = profile.get("data", {}).get("students", [])
            result.append({
                "id": group_id,
                "name": profile.get("groupName"),
                "subject": profile.get("groupSubject"),
                "teacher_id": profile.get("teacher_id"),
                "students_count": len(students_raw),
                "students": parse_students(students_raw)
            })

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xato: {str(e)}")


@router.get("/groups/{group_id}")
async def get_classroom_group(
        group_id: int,
        current_teacher: Student = Depends(get_current_teacher)
):
    """Bitta guruh ma'lumotlari"""
    try:
        token = await get_admin_token()
        if not token:
            raise HTTPException(status_code=401, detail="Admin API ga ulanib bo'lmadi")

        profile = await get_group_profile(token, group_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Guruh topilmadi")

        students_raw = profile.get("data", {}).get("students", [])
        return {
            "id": group_id,
            "name": profile.get("groupName"),
            "subject": profile.get("groupSubject"),
            "teacher_id": profile.get("teacher_id"),
            "students_count": len(students_raw),
            "students": parse_students(students_raw)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xato: {str(e)}")


@router.post("/sync")
async def sync_students(
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    """Admin.gennis.uz dan studentlarni bazaga sync qilish"""
    try:
        token = await get_admin_token()
        if not token:
            raise HTTPException(status_code=401, detail="Admin API ga ulanib bo'lmadi")

        # Admin dan barcha studentlar
        admin_students = await get_all_admin_students(token)
        admin_usernames = set(admin_students.keys())

        created = 0
        updated = 0
        deactivated = 0
        errors = []

        # 1. Yangi studentlarni qo'shish, mavjudlarini yangilash
        for username, s in admin_students.items():
            try:
                existing = await db.execute(
                    select(Student).where(Student.username == username)
                )
                student = existing.scalar_one_or_none()

                if student:
                    # Mavjud — yangilash
                    student.full_name = f"{s.get('name', '')} {s.get('surname', '')}".strip()
                    student.is_active = True  # Qaytib kelgan bo'lsa aktivlashtirish
                    updated += 1
                else:
                    # Yangi — yaratish
                    new_student = Student(
                        username=username,
                        email=f"{username}@gennis.uz",
                        hashed_password=get_password_hash("12345678"),
                        full_name=f"{s.get('name', '')} {s.get('surname', '')}".strip(),
                        role=UserRole.student,
                        is_active=True,
                    )
                    db.add(new_student)
                    await db.flush()

                    ranking_service = RankingService(db)
                    await ranking_service.create_ranking(new_student.id)
                    created += 1

            except Exception as e:
                errors.append(f"{username}: {str(e)}")

        # 2. Admin da yo'q studentlarni deaktivlashtirish
        all_our_students = await db.execute(
            select(Student).where(
                Student.role == UserRole.student,
                Student.is_active == True,
                Student.email.like("%@gennis.uz")  # Faqat classroom dan kelganlar
            )
        )
        our_students = all_our_students.scalars().all()

        for student in our_students:
            if student.username not in admin_usernames:
                student.is_active = False
                deactivated += 1

        await db.commit()

        return {
            "message": "Sync muvaffaqiyatli bajarildi!",
            "created": created,
            "updated": updated,
            "deactivated": deactivated,
            "errors": errors[:10]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync xatosi: {str(e)}")


async def sync_students_internal(db: AsyncSession):
    """Ichki sync — login da chaqiriladi"""
    try:
        token = await get_admin_token()
        if not token:
            return

        admin_students = await get_all_admin_students(token)
        admin_usernames = set(admin_students.keys())

        for username, s in admin_students.items():
            try:
                existing = await db.execute(
                    select(Student).where(Student.username == username)
                )
                student = existing.scalar_one_or_none()

                if student:
                    student.is_active = True
                else:
                    new_student = Student(
                        username=username,
                        email=f"{username}@gennis.uz",
                        hashed_password=get_password_hash("12345678"),
                        full_name=f"{s.get('name', '')} {s.get('surname', '')}".strip(),
                        role=UserRole.student,
                        is_active=True,
                    )
                    db.add(new_student)
                    await db.flush()

                    ranking_service = RankingService(db)
                    await ranking_service.create_ranking(new_student.id)

            except Exception:
                continue

        # Admin da yo'q studentlarni deaktivlashtirish
        all_our_students = await db.execute(
            select(Student).where(
                Student.role == UserRole.student,
                Student.is_active == True,
                Student.email.like("%@gennis.uz")
            )
        )
        our_students = all_our_students.scalars().all()

        for student in our_students:
            if student.username not in admin_usernames:
                student.is_active = False

        await db.commit()

    except Exception as e:
        print(f"Sync internal xato: {e}")