import json
import os
import shutil
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
<<<<<<< HEAD
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status, UploadFile

from app.models.project import Project
from app.models.user import Student
from app.schemas.project import ProjectCreate, ProjectUpdate

UPLOAD_DIR = "uploads"


<<<<<<< Updated upstream
async def get_current_student(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> Student:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token noto'g'ri yoki muddati o'tgan"
        )
    result = await db.execute(select(Student).where(Student.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return user
=======
from fastapi import HTTPException
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from datetime import datetime
>>>>>>> origin/branch-shoh


=======
>>>>>>> Stashed changes
class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # project_service.py - create_project
    async def create_project(self, student_id: int, data: ProjectCreate) -> Project:
<<<<<<< Updated upstream
<<<<<<< HEAD
=======
        """Yangi loyiha yaratish"""
>>>>>>> Stashed changes
        data_dict = data.model_dump()

        # Technologies listni JSON stringga o'zgartirish
        if data_dict.get("technologies_used") is not None:
=======
        data_dict = data.dict()
        # technologies_used listni JSON string ga aylantiramiz
        if data_dict.get("technologies_used"):
            import json
>>>>>>> origin/branch-shoh
            data_dict["technologies_used"] = json.dumps(data_dict["technologies_used"])

        new_project = Project(**data_dict, student_id=student_id)
        self.db.add(new_project)
        await self.db.commit()
        await self.db.refresh(new_project)
        return await self._load_with_student(new_project.id)

    async def get_project(self, project_id: int) -> Optional[Project]:
        """Bitta loyihani olish"""
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.student))
            .where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        if project:
            project = self._parse_technologies(project)
        return project

    async def get_projects(self, page: int = 1, page_size: int = 10) -> dict:
        """Barcha loyihalarni olish"""
        offset = (page - 1) * page_size

        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.student))
            .order_by(Project.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        projects = result.scalars().all()
        projects = [self._parse_technologies(p) for p in projects]

<<<<<<< Updated upstream
<<<<<<< HEAD
=======
        # Jami loyihalar soni
>>>>>>> Stashed changes
        count_result = await self.db.execute(select(func.count(Project.id)))
        total = count_result.scalar()

        return {
            "projects": projects,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def get_student_projects(self, student_id: int, page: int = 1, page_size: int = 10) -> dict:
        """Ma'lum bir studentning loyihalari"""
        offset = (page - 1) * page_size

        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.student))
            .where(Project.student_id == student_id)
            .order_by(Project.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        projects = result.scalars().all()
        projects = [self._parse_technologies(p) for p in projects]

        # Jami loyihalar soni
        count_result = await self.db.execute(
            select(func.count(Project.id)).where(Project.student_id == student_id)
        )
        total = count_result.scalar()

        return {
            "projects": projects,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def update_project(self, project_id: int, data: ProjectUpdate) -> Project:
<<<<<<< Updated upstream
=======
    async def get_all_projects_by_student(self, student_id: int):
        result = await self.db.execute(
            select(Project).where(Project.student_id == student_id)
        )
        return result.scalars().all()

    async def update_project(self, project_id: int, student_id: int, data: ProjectUpdate) -> Project:
>>>>>>> origin/branch-shoh
        project = await self.get_project(project_id)
=======
        """Loyihani yangilash"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")

>>>>>>> Stashed changes
        update_data = data.model_dump(exclude_unset=True)

        if "technologies_used" in update_data and update_data["technologies_used"] is not None:
            update_data["technologies_used"] = json.dumps(update_data["technologies_used"])

        for key, value in update_data.items():
            setattr(project, key, value)

        project.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(project)
        return await self._load_with_student(project.id)

    async def delete_project(self, project_id: int) -> None:
        """Loyihani o'chirish"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")

        await self.db.delete(project)
        await self.db.commit()

<<<<<<< Updated upstream
<<<<<<< HEAD
    async def review_project(self, project_id: int, data: ProjectReview) -> Project:
        project = await self.get_project(project_id)
        project.status = data.status.value
        project.grade = data.grade.value
        project.points_earned = data.points_earned
        project.instructor_feedback = data.instructor_feedback
        project.reviewed_at = datetime.utcnow()
        self._serialize_project(project)
=======
    async def submit_project(self, project_id: int, student_id: int):
        project = await self.get_project(project_id)
        if project.student_id != student_id:
            raise HTTPException(status_code=403, detail="Ruxsat yo'q")
        if project.status != "Draft":
            raise HTTPException(status_code=400, detail="Proyekt allaqachon yuborilgan")
        project.status = "Submitted"
        project.submitted_at = datetime.utcnow()
>>>>>>> origin/branch-shoh
=======
    async def submit_project(self, project_id: int) -> Project:
        """Loyihani submit qilish"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")

        project.status = "Submitted"
        project.submitted_at = datetime.utcnow()

>>>>>>> Stashed changes
        await self.db.commit()
        await self.db.refresh(project)
        return await self._load_with_student(project.id)

    async def like_project(self, project_id: int) -> Project:
        """Loyihani like qilish"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")

        project.likes_count += 1

        await self.db.commit()
        await self.db.refresh(project)
        return await self._load_with_student(project.id)

    # ─── Helper metodlar ───────────────────────────────────────────────────────

    async def _load_with_student(self, project_id: int) -> Project:
        """Loyihani student bilan birga yuklash"""
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.student))
            .where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        if project:
            project = self._parse_technologies(project)
        return project

    @staticmethod
    def _parse_technologies(project: Project) -> Project:
        """JSON stringni listga o'zgartirish"""
        if project and isinstance(project.technologies_used, str):
            try:
                project.__dict__['technologies_used'] = json.loads(project.technologies_used)
            except (json.JSONDecodeError, TypeError):
                project.__dict__['technologies_used'] = []
        return project

    async def review_project(self, project_id: int, feedback: str, grade: str, points: int) -> Project:
        project = await self.get_project(project_id)
        project.instructor_feedback = feedback
        project.grade = grade
        project.points_earned = points
        project.status = "Approved"
        project.reviewed_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_status(self, project_id: int, status: str) -> Project:
        allowed = ["Draft", "Submitted", "Under Review", "Approved", "Rejected"]
        if status not in allowed:
            raise HTTPException(status_code=400, detail=f"Status must be one of: {allowed}")
        project = await self.get_project(project_id)
        project.status = status
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_grade(self, project_id: int, grade: str) -> Project:
        allowed = ["A", "B", "C", "D", "F"]
        if grade not in allowed:
            raise HTTPException(status_code=400, detail=f"Grade must be one of: {allowed}")
        project = await self.get_project(project_id)
        project.grade = grade
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_comment(self, project_id: int, comment: str) -> Project:
        project = await self.get_project(project_id)
        project.instructor_feedback = comment
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_difficulty(self, project_id: int, difficulty: str) -> Project:
        allowed = ["Easy", "Medium", "Hard"]
        if difficulty not in allowed:
            raise HTTPException(status_code=400, detail=f"Difficulty must be one of: {allowed}")
        project = await self.get_project(project_id)
        project.difficulty_level = difficulty
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_file(self, project_id: int, file_url: str) -> Project:
        project = await self.get_project(project_id)
        project.project_files = file_url
        await self.db.commit()
        await self.db.refresh(project)
        return project
