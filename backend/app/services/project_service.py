import json
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.project import Project
from app.models.submission import Submission
from app.models.user import Student
from app.schemas.project import ProjectCreate, ProjectUpdate

logger = logging.getLogger(__name__)


# Minimum project score (0-100) to consider a submission "passing".
# Mirrors PROJECT_PASS_THRESHOLD in app/api/v1/endpoints/lessons.py.
PROJECT_PASS_THRESHOLD = 75


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, student_id: int, data: ProjectCreate) -> Project:
        data_dict = data.dict()
        lesson_id = data_dict.pop("lesson_id", None)

        techs = data_dict.get("technologies_used")
        if techs is not None:
            if isinstance(techs, list):
                data_dict["technologies_used"] = ",".join(techs)

        if "difficulty_level" in data_dict and hasattr(data_dict["difficulty_level"], "value"):
            data_dict["difficulty_level"] = data_dict["difficulty_level"].value

        # Lesson-scoped path: enforce re-submission rules. Pending and passing
        # submissions are locked; failed/rejected ones are replaced.
        existing_sub = None
        if lesson_id is not None:
            sub_res = await self.db.execute(
                select(Submission).where(
                    Submission.lesson_id == lesson_id,
                    Submission.student_id == student_id,
                )
            )
            existing_sub = sub_res.scalar_one_or_none()
            if existing_sub is not None:
                old_proj_res = await self.db.execute(
                    select(Project).where(Project.id == existing_sub.project_id)
                )
                old_project = old_proj_res.scalar_one_or_none()
                old_status = old_project.status if old_project else existing_sub.status
                old_points = old_project.points_earned if old_project else 0

                if old_status == "Submitted":
                    raise HTTPException(
                        status_code=400,
                        detail="Loyihangiz hali tekshirilmoqda — natijani kuting",
                    )
                if old_status == "Approved" and old_points >= PROJECT_PASS_THRESHOLD:
                    raise HTTPException(
                        status_code=400,
                        detail="Bu dars allaqachon muvaffaqiyatli topshirilgan",
                    )

                # Resubmit: reverse the previously awarded points before
                # replacing the project so the next review doesn't double-count.
                if old_points > 0:
                    from app.services.ranking_service import RankingService
                    await RankingService(self.db).subtract_points_from_student(
                        student_id, old_points
                    )

                # Drop the old submission first (its FK points at the old
                # project, which we're about to delete).
                await self.db.delete(existing_sub)
                if old_project is not None:
                    await self.db.delete(old_project)
                await self.db.flush()

        new_project = Project(**data_dict, student_id=student_id)
        self.db.add(new_project)
        await self.db.flush()

        if lesson_id is not None:
            self.db.add(Submission(
                lesson_id=lesson_id,
                student_id=student_id,
                project_id=new_project.id,
                status=new_project.status,
                github_url=new_project.github_url,
                live_demo_url=new_project.live_demo_url,
                description=new_project.description,
                submitted_at=datetime.utcnow(),
                created_at=datetime.utcnow(),  # ← qo'shing
                updated_at=datetime.utcnow(),  # ← qo'shing
            ))

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

        # Auto-trigger AI review when student submits from the lesson page.
        # raise_on_error=False so a failed/missing AI never blocks the
        # submission itself — the project is already marked Submitted and
        # the student can manually retry from MyProjects later. On success,
        # the AI writes status=Approved + grade + points back to the same
        # Project row, so the refreshed project below carries the grade.
        # Local import avoids circular dependency (ai_review_service imports
        # RankingService which lives elsewhere; cleaner to defer).
        from app.services.ai_review_service import run_ai_review_for_project
        try:
            ai_result = await run_ai_review_for_project(
                self.db, project, raise_on_error=False,
            )
            if ai_result.get("success"):
                logger.info(
                    "[ai-auto] project=%d graded %s/%d via %s",
                    project.id, ai_result.get("grade"),
                    ai_result.get("new_points"), ai_result.get("provider"),
                )
            elif not ai_result.get("success"):
                # AI failed (invalid URL, repo not found, provider error, etc.).
                # Reset to "Rejected" so the student can fix and re-submit.
                # "Submitted" would block re-submission permanently.
                reason = ai_result.get("reason", "AI tekshirish muvaffaqiyatsiz")
                project.status = "Rejected"
                project.instructor_feedback = reason
                await self.db.commit()
                logger.warning(
                    "[ai-auto] project=%d failed, set Rejected: %s", project.id, reason
                )
            await self.db.refresh(project)
        except Exception as e:
            # Defense in depth — any unhandled exception in the AI path
            # gets logged but never propagates. The submission stands.
            logger.warning("[ai-auto] project=%d unhandled error: %s",
                           project.id, e)

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

    async def update_comment(self, project_id: int, student_id: int, comment: str) -> Project:
        project = await self.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")
        if project.student_id != student_id:
            raise HTTPException(status_code=403, detail="Ruxsat yo'q")
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

    async def update_file(self, project_id: int, student_id: int, file_url: str) -> Project:
        project = await self.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")
        if project.student_id != student_id:
            raise HTTPException(status_code=403, detail="Ruxsat yo'q")
        project.project_files = file_url
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def like_project(self, project_id: int, student_id: int = None) -> Project:
        """Like a project.

        Self-likes are blocked. Per-user dedup is not enforced yet (needs a
        dedicated project_likes join table — see TODO in the bug report).
        """
        project = await self.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Loyiha topilmadi")
        if student_id is not None and project.student_id == student_id:
            raise HTTPException(status_code=400, detail="O'z loyihangizga like bosa olmaysiz")
        project.likes_count += 1
        await self.db.commit()
        await self.db.refresh(project)
        return project
