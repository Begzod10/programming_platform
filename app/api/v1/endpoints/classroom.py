from fastapi import APIRouter, HTTPException, Depends
from app.dependencies import get_current_teacher
from app.models.user import Student
import httpx

router = APIRouter()

CLASSROOM_API = "https://classroom.gennis.uz/api"
CLASSROOM_USERNAME = "rimefara_teach"
CLASSROOM_PASSWORD = "22100122"

_cached_token = None


async def get_classroom_token() -> str:
    """Classroom dan token olish"""
    global _cached_token
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.post(
                f"{CLASSROOM_API}/login/",
                json={
                    "username": CLASSROOM_USERNAME,
                    "password": CLASSROOM_PASSWORD
                },
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                token = data.get("data", {}).get("access_token", "")
                _cached_token = token
                return token
    except Exception as e:
        print(f"Token olishda xato: {e}")
    return ""

async def classroom_get(url: str) -> dict:
    """Classroom API ga GET so'rov"""
    token = await get_classroom_token()
    if not token:
        raise HTTPException(status_code=500, detail="Classroom token olishda xato")

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Classroom autentifikatsiya xatosi")
        response.raise_for_status()
        return response.json()


@router.get("/groups")
async def get_classroom_groups(
        current_teacher: Student = Depends(get_current_teacher)
):
    """Classroom dan barcha guruhlarni olish"""
    try:
        groups = await classroom_get(f"{CLASSROOM_API}/group/get_groups")
        result = []
        for group in groups:
            students = []
            for student in group.get("students", []):
                students.append({
                    "id": student.get("id"),
                    "name": student.get("name"),
                    "parent_phone": student.get("parent_phone"),
                    "balance": student.get("balance"),
                    "color": student.get("color"),
                })
            result.append({
                "id": group.get("id"),
                "name": group.get("name"),
                "price": group.get("price"),
                "students_num": group.get("students_num"),
                "teacher": group.get("teacher"),
                "subject": group.get("subject"),
                "students": students
            })
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classroom API xatosi: {str(e)}")


@router.get("/groups/{group_id}")
async def get_classroom_group(
        group_id: int,
        current_teacher: Student = Depends(get_current_teacher)
):
    """Classroom dan bitta guruhni olish"""
    try:
        groups = await classroom_get(f"{CLASSROOM_API}/group/get_groups")
        group = next((g for g in groups if g.get("id") == group_id), None)
        if not group:
            raise HTTPException(status_code=404, detail="Guruh topilmadi")

        students = []
        for student in group.get("students", []):
            students.append({
                "id": student.get("id"),
                "name": student.get("name"),
                "parent_phone": student.get("parent_phone"),
                "balance": student.get("balance"),
                "color": student.get("color"),
                "is_debtor": student.get("balance", 0) < 0
            })

        return {
            "id": group.get("id"),
            "name": group.get("name"),
            "price": group.get("price"),
            "students_num": group.get("students_num"),
            "teacher": group.get("teacher"),
            "subject": group.get("subject"),
            "students": students
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classroom API xatosi: {str(e)}")