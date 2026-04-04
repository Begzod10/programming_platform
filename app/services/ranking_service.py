from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload
from app.models.ranking import Ranking
from app.models.user import Student, UserRole
from app.models.project import Project
from datetime import datetime
from typing import List, Literal, Optional


class RankingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ========== CREATE ==========

    async def create_ranking(self, student_id: int) -> Optional[Ranking]:
        """Yangi ranking yaratish"""
        result = await self.db.execute(
            select(Ranking).where(Ranking.student_id == student_id)
        )
        if result.scalar_one_or_none():
            return None

        student_res = await self.db.execute(
            select(Student).where(
                Student.id == student_id,
                Student.role == UserRole.student
            )
        )
        student = student_res.scalar_one_or_none()
        if not student:
            return None

        new_ranking = Ranking(
            student_id=student_id,
            daily_points=0,
            weekly_points=0,
            monthly_points=0,
            total_points=student.total_points,
            global_rank=0,
            level_rank=0,
            projects_completed=0,
            average_grade=0.0,
            last_daily_reset=datetime.utcnow(),
            last_weekly_reset=datetime.utcnow(),
            last_monthly_reset=datetime.utcnow()
        )
        self.db.add(new_ranking)
        await self.db.commit()
        await self.db.refresh(new_ranking)
        await self.calculate_and_update_rankings()
        return new_ranking

    # ========== READ ==========

    async def get_my_ranking(self, student_id: int) -> Optional[Ranking]:
        result = await self.db.execute(
            select(Ranking)
            .where(Ranking.student_id == student_id)
            .options(selectinload(Ranking.student))
        )
        return result.scalar_one_or_none()

    async def get_all_rankings(self, skip: int = 0, limit: int = 50) -> List[Ranking]:
        result = await self.db.execute(
            select(Ranking)
            .order_by(Ranking.global_rank.asc())
            .offset(skip)
            .limit(limit)
            .options(selectinload(Ranking.student))
        )
        return result.scalars().all()

    async def get_leaderboard(
            self,
            period: Literal["daily", "weekly", "monthly", "all"] = "all",
            limit: int = 10,
            offset: int = 0,
            level: str = None
    ) -> List[Ranking]:
        sort_column_map = {
            "daily": Ranking.daily_points,
            "weekly": Ranking.weekly_points,
            "monthly": Ranking.monthly_points,
            "all": Ranking.total_points
        }
        order_by = sort_column_map.get(period, Ranking.total_points).desc()

        query = (
            select(Ranking)
            .join(Student)
            .where(Student.is_active == True, Student.role == UserRole.student)
            .order_by(order_by)
            .limit(limit)
            .offset(offset)
            .options(selectinload(Ranking.student))
        )
        if level:
            query = query.where(Student.current_level == level)

        result = await self.db.execute(query)
        return result.scalars().all()

    # ========== ADD / SUBTRACT POINTS ==========

    async def add_points_to_student(self, student_id: int, points: int) -> Optional[Student]:
        """Studentga ball qo'shish - barcha period'larga"""
        res = await self.db.execute(select(Student).where(Student.id == student_id))
        student = res.scalar_one_or_none()
        if not student:
            return None

        student.total_points += points

        result = await self.db.execute(
            select(Ranking).where(Ranking.student_id == student_id)
        )
        ranking = result.scalar_one_or_none()

        if ranking:
            # ✅ Barcha period'larga qo'shish
            ranking.daily_points += points
            ranking.weekly_points += points
            ranking.monthly_points += points
            ranking.total_points = student.total_points
            ranking.last_calculated_at = datetime.utcnow()
        else:
            ranking = Ranking(
                student_id=student_id,
                daily_points=points,
                weekly_points=points,
                monthly_points=points,
                total_points=student.total_points,
                projects_completed=0,
                global_rank=0,
                level_rank=0,
                last_calculated_at=datetime.utcnow(),
                last_daily_reset=datetime.utcnow(),
                last_weekly_reset=datetime.utcnow(),
                last_monthly_reset=datetime.utcnow()
            )
            self.db.add(ranking)

        await self.db.commit()
        await self.calculate_and_update_rankings()
        return student

    async def subtract_points_from_student(self, student_id: int, points: int) -> Optional[Student]:
        """Studentdan ball ayirish"""
        res = await self.db.execute(select(Student).where(Student.id == student_id))
        student = res.scalar_one_or_none()
        if not student:
            return None

        student.total_points = max(0, student.total_points - points)

        result = await self.db.execute(
            select(Ranking).where(Ranking.student_id == student_id)
        )
        ranking = result.scalar_one_or_none()

        if ranking:
            ranking.daily_points = max(0, ranking.daily_points - points)
            ranking.weekly_points = max(0, ranking.weekly_points - points)
            ranking.monthly_points = max(0, ranking.monthly_points - points)
            ranking.total_points = student.total_points
            ranking.last_calculated_at = datetime.utcnow()

        await self.db.commit()
        await self.calculate_and_update_rankings()
        return student

    # ========== RESET OPERATIONS (CASCADE) ==========

    async def reset_daily_points(self):
        """
        Har kecha 00:00 da chaqiriladi (scheduler).
        ✅ Kunlik ballarni haftalikka QO'SHIB, keyin 0 ga tushiradi.
        """
        # Barcha ranking'larni olish
        result = await self.db.execute(select(Ranking))
        rankings = result.scalars().all()

        for ranking in rankings:
            # ✅ daily_points ni weekly_points ga QO'SHISH (agar 0 dan katta bo'lsa)
            if ranking.daily_points > 0:
                ranking.weekly_points += ranking.daily_points
                ranking.monthly_points += ranking.daily_points

            # Kunlik ballarni reset qilish
            ranking.daily_points = 0
            ranking.last_daily_reset = datetime.utcnow()

        await self.db.commit()

    async def reset_weekly_points(self):
        """
        Har dushanba 00:00 da chaqiriladi (scheduler).
        ✅ Haftalik ballarni oylikka QO'SHIB, keyin 0 ga tushiradi.
        """
        result = await self.db.execute(select(Ranking))
        rankings = result.scalars().all()

        for ranking in rankings:
            # ✅ weekly_points ni monthly_points ga QO'SHISH
            if ranking.weekly_points > 0:
                ranking.monthly_points += ranking.weekly_points

            # Haftalik ballarni reset qilish
            ranking.weekly_points = 0
            ranking.last_weekly_reset = datetime.utcnow()

        await self.db.commit()

    async def reset_monthly_points(self):
        """
        Har oy 1-si 00:00 da chaqiriladi (scheduler).
        ✅ Oylik ballarni total_points ga QO'SHIB, keyin 0 ga tushiradi.
        """
        result = await self.db.execute(select(Ranking))
        rankings = result.scalars().all()

        for ranking in rankings:
            # ✅ monthly_points ni total_points ga QO'SHISH
            if ranking.monthly_points > 0:
                ranking.total_points += ranking.monthly_points

                # Student'ning total_points'ini ham yangilash
                student_res = await self.db.execute(
                    select(Student).where(Student.id == ranking.student_id)
                )
                student = student_res.scalar_one_or_none()
                if student:
                    student.total_points = ranking.total_points

            # Oylik ballarni reset qilish
            ranking.monthly_points = 0
            ranking.last_monthly_reset = datetime.utcnow()

        await self.db.commit()

    # ========== RECALCULATE ==========

    async def calculate_and_update_rankings(self):
        """Global rank va level rank ni qayta hisoblash"""
        result = await self.db.execute(
            select(Student)
            .where(Student.is_active == True, Student.role == UserRole.student)
            .order_by(Student.total_points.desc())
        )
        students = result.scalars().all()

        ranking_res = await self.db.execute(select(Ranking))
        existing_rankings = {r.student_id: r for r in ranking_res.scalars().all()}

        for global_rank, student in enumerate(students, start=1):
            stats_res = await self.db.execute(
                select(
                    func.count(Project.id).label("count"),
                    func.coalesce(func.avg(Project.points_earned), 0).label("avg")
                ).where(
                    Project.student_id == student.id,
                    Project.status == "Approved"
                )
            )
            stats = stats_res.one()

            level_res = await self.db.execute(
                select(Student.id).where(
                    Student.current_level == student.current_level,
                    Student.is_active == True,
                    Student.role == UserRole.student
                ).order_by(Student.total_points.desc())
            )
            level_ids = level_res.scalars().all()
            level_rank = level_ids.index(student.id) + 1 if student.id in level_ids else 1

            ranking = existing_rankings.get(student.id)
            if ranking:
                ranking.total_points = student.total_points
                ranking.global_rank = global_rank
                ranking.level_rank = level_rank
                ranking.projects_completed = stats.count or 0
                ranking.average_grade = float(stats.avg or 0)
                ranking.last_calculated_at = datetime.utcnow()

            student.global_rank = global_rank

        await self.db.commit()

    # ========== DELETE & UPDATE ==========

    async def delete_ranking(self, ranking_id: int) -> bool:
        result = await self.db.execute(
            select(Ranking).where(Ranking.id == ranking_id)
        )
        ranking = result.scalar_one_or_none()
        if not ranking:
            return False
        await self.db.delete(ranking)
        await self.db.commit()
        return True

    async def update_ranking(self, ranking_id: int, **kwargs) -> Optional[Ranking]:
        result = await self.db.execute(
            select(Ranking).where(Ranking.id == ranking_id)
        )
        ranking = result.scalar_one_or_none()
        if not ranking:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(ranking, key):
                setattr(ranking, key, value)

        if kwargs.get('total_points') is not None:
            student_res = await self.db.execute(
                select(Student).where(Student.id == ranking.student_id)
            )
            student = student_res.scalar_one_or_none()
            if student:
                student.total_points = kwargs['total_points']

        await self.db.commit()
        await self.db.refresh(ranking)
        await self.calculate_and_update_rankings()
        return ranking

