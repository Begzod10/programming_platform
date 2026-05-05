import json
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.project import Project
from app.models.user import Student
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, student_id: int, data: ProjectCreate) -> Project:
        data_dict = data.dict()
        if data_dict.get("technologies_used"):
            if isinstance(data_dict["technologies_used"], list):
                data_dict["technologies_used"] = ",".join(data_dict["technologies_used"])
        new_project = Project(**data_dict, student_id=student_id)
        self.db.add(new_project)
        await self.db.commit()
        await self.db.refresh(new_project)
        return new_project

    async def get_project(self, project_id: int) -> Optional[Project]:
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.student))
            .where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_all_projects(self, skip: int = 0, limit: int = 10):
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.student))
            .order_by(Project.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_all_projects_by_student(self, student_id: int):
        result = await self.db.execute(
            select(Project).where(Project.student_id == student_id)
        )
        return result.scalars().all()

    async def update_project(self, project_id: int, student_id: int, data: ProjectUpdate) -> Project:
        project = await self.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")
        if project.student_id != student_id:
            raise HTTPException(status_code=403, detail="Ruxsat yo'q")
        update_data = data.dict(exclude_unset=True)
        if "technologies_used" in update_data and isinstance(update_data["technologies_used"], list):
            update_data["technologies_used"] = ",".join(update_data["technologies_used"])
        for key, value in update_data.items():
            setattr(project, key, value)
        project.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete_project(self, project_id: int, student_id: int) -> None:
        project = await self.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")
        if project.student_id != student_id:
            raise HTTPException(status_code=403, detail="Ruxsat yo'q")
        await self.db.delete(project)
        await self.db.commit()

    async def submit_project(self, project_id: int, student_id: int):
        project = await self.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")
        if project.student_id != student_id:
            raise HTTPException(status_code=403, detail="Ruxsat yo'q")
        project.status = "Submitted"
        project.submitted_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def review_project(self, project_id: int, feedback: str, grade: str, points: int) -> Project:
        project = await self.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")

        project.instructor_feedback = feedback
        project.grade = grade
        project.points_earned = points
        project.status = "Approved"
        project.reviewed_at = datetime.utcnow()

        # Studentga ball qo'shish
        student_result = await self.db.execute(
            select(Student).where(Student.id == project.student_id)
        )
        student = student_result.scalar_one_or_none()
        if student and points > 0:
            from app.services.ranking_service import RankingService
            ranking_service = RankingService(self.db)
            await ranking_service.add_points_to_student(student.id, points)

        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_status(self, project_id: int, status: str) -> Project:
        allowed = ["Draft", "Submitted", "Under Review", "Approved", "Rejected"]
        if status not in allowed:
            raise HTTPException(status_code=400, detail=f"Status must be one of: {allowed}")
        project = await self.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")
        project.status = status
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_grade(self, project_id: int, grade: str) -> Project:
        allowed = ["A", "B", "C", "D", "F"]
        if grade not in allowed:
            raise HTTPException(status_code=400, detail=f"Grade must be one of: {allowed}")
        project = await self.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")
        project.grade = grade
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_comment(self, project_id: int, comment: str) -> Project:
        project = await self.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")
        project.instructor_feedback = comment
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_difficulty(self, project_id: int, difficulty: str) -> Project:
        allowed = ["Easy", "Medium", "Hard"]
        if difficulty not in allowed:
            raise HTTPException(status_code=400, detail=f"Difficulty must be one of: {allowed}")
        project = await self.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")
        project.difficulty_level = difficulty
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_file(self, project_id: int, file_url: str) -> Project:
        project = await self.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")
        project.project_files = file_url
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def like_project(self, project_id: int, student_id: int = None) -> Project:
        project = await self.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")
        project.likes_count += 1
        await self.db.commit()
        await self.db.refresh(project)
        return project
