from fastapi import APIRouter, Depends, status, Query, HTTPException, Body
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from app.models.project import Project

from app.dependencies import get_db, get_current_student, get_current_instructor
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead
from app.models.user import Student
from app.services.ranking_service import RankingService
router = APIRouter()


def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


# ✅ STUDENT ENDPOINT'LAR

@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
        payload: ProjectCreate,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Yangi proyekt yaratish"""
    return await service.create_project(student_id=current_student.id, data=payload)


@router.get("/", response_model=List[ProjectRead])
async def get_projects(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        service: ProjectService = Depends(get_project_service),
):
    """Barcha proyektlar (public)"""
    return await service.get_all_projects(skip=skip, limit=limit)


@router.get("/my", response_model=List[ProjectRead])
async def get_my_projects(
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Mening proyektlarim"""
    return await service.get_all_projects_by_student(student_id=current_student.id)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
        project_id: int,
        service: ProjectService = Depends(get_project_service),
):
    """Proyektni ko'rish (public)"""
    project = await service.get_project(project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")
    return project


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
        project_id: int,
        payload: ProjectUpdate,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Proyektni yangilash (faqat egasi)"""
    return await service.update_project(
        project_id=project_id,
        student_id=current_student.id,
        data=payload
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Proyektni o'chirish (faqat egasi)"""
    await service.delete_project(project_id=project_id, student_id=current_student.id)


@router.post("/{project_id}/submit", response_model=ProjectRead)
async def submit_project(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Proyektni taqdim qilish (faqat egasi)"""
    return await service.submit_project(
        project_id=project_id,
        student_id=current_student.id
    )


@router.post("/{project_id}/like", response_model=ProjectRead)
async def like_project(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Proyektni like qilish"""
    return await service.like_project(
        project_id=project_id,
        student_id=current_student.id  # ✅ Student ID qo'shildi
    )


# ✅ TEACHER ENDPOINT'LAR (FAQAT INSTRUCTOR)

class ReviewProjectRequest(BaseModel):
    feedback: str
    grade: str
    points: int


@router.post("/{project_id}/review")
async def review_project(
        project_id: int,
        data: ReviewProjectRequest, # ReviewProjectRequest schema ishlatilsin
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    # 1. Loyihani topish
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")

    if project.status == "Approved":
         raise HTTPException(status_code=400, detail="Bu loyiha allaqachon tasdiqlangan")

    # 2. RankingService orqali ballarni va proyekt sonini yangilash
    service = RankingService(db)
    await service.add_points_to_student(project.student_id, data.points)

    # 3. Loyiha holatini yangilash
    project.status = "Approved"
    project.feedback = data.feedback
    project.grade = data.grade
    project.points_earned = data.points

    await db.commit()
    return {"message": "Loyiha tasdiqlandi, ballar va proyekt soni yangilandi"}

@router.patch("/{project_id}/status")
async def update_status(
        project_id: int,
        new_status: str = Body(..., embed=True),
        current_teacher: Student = Depends(get_current_instructor),
        service: ProjectService = Depends(get_project_service),
):
    """Status o'zgartirish (faqat teacher)"""
    return await service.update_status(project_id=project_id, status=new_status)


@router.patch("/{project_id}/grade")
async def update_grade(
        project_id: int,
        grade: str = Body(..., embed=True),
        current_teacher: Student = Depends(get_current_instructor),
        service: ProjectService = Depends(get_project_service),
):
    """Baho berish (faqat teacher)"""
    return await service.update_grade(project_id=project_id, grade=grade)


@router.patch("/{project_id}/difficulty")
async def update_difficulty(
        project_id: int,
        difficulty: str = Body(..., embed=True),
        current_teacher: Student = Depends(get_current_instructor),
        service: ProjectService = Depends(get_project_service),
):
    """Qiyinlik darajasini o'zgartirish (faqat teacher)"""
    return await service.update_difficulty(project_id=project_id, difficulty=difficulty)


# ✅ OPTIONAL ENDPOINT'LAR (student yoki teacher)

@router.patch("/{project_id}/comment")
async def update_comment(
        project_id: int,
        comment: str = Body(..., embed=True),
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Izoh qo'shish"""
    return await service.update_comment(project_id=project_id, comment=comment)


@router.patch("/{project_id}/file")
async def update_file(
        project_id: int,
        file_url: str = Body(..., embed=True),
        current_student: Student = Depends(get_current_student),
        service: ProjectService = Depends(get_project_service),
):
    """Fayl urlini yangilash"""
    return await service.update_file(project_id=project_id, file_url=file_url)


@router.post("/{project_id}/review")
async def review_project(
        project_id: int,
        feedback: str,
        grade: str,
        points: int,
        db: AsyncSession = Depends(get_db)
):
    # 1. Avval loyihani bazadan qidirib topamiz
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")

    # 2. ENDI BIZDA student_id BOR (project ob'ekti ichida)
    student_id = project.student_id  # <--- MANA SHU QATORNI QO'SHING

    # 3. Ballarni qo'shish
    service = RankingService(db)
    await service.add_points_to_student(student_id, points)

    # 4. Loyiha holatini yangilash
    project.status = "Approved"
    project.feedback = feedback
    project.grade = grade
    project.points_earned = points

    await db.commit()
    return {"message": "Loyiha tekshirildi va ballar qo'shildi"}