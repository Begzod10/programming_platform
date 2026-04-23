from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.ranking import Ranking
from app.models.user import Student, UserRole
from datetime import datetime
from typing import List, Literal, Optional
from sqlalchemy import over

class RankingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ========== CREATE ==========

    async def create_ranking(self, student_id: int) -> Optional[Ranking]:
        result = await self.db.execute(select(Ranking).where(Ranking.student_id == student_id))
        if result.scalar_one_or_none():
            return None

        student_res = await self.db.execute(
            select(Student).where(Student.id == student_id, Student.role == UserRole.student)
        )
        student = student_res.scalar_one_or_none()
        if not student:
            return None

        new_ranking = Ranking(
            student_id=student_id,
            daily_points=0, weekly_points=0, monthly_points=0,
            total_points=student.total_points,
            global_rank=0, daily_rank=0, weekly_rank=0, monthly_rank=0,
            level_rank=0, projects_completed=0, average_grade=0.0,
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

    # app/services/ranking_service.py

    async def get_my_ranking(self, student_id: int):
        """Foydalanuvchining har bir perioddagi dinamik o'rnini (7-o'rin bo'lsa 7) hisoblash"""

        def get_rank_subquery(column):
            # Mening ballimni aniqlaymiz (Agar ye'q bo'lsa 0)
            my_val_query = select(func.coalesce(column, 0)).where(Ranking.student_id == student_id)
            my_val = my_val_query.scalar_subquery()

            # O'zimdan ko'p balli bo'lganlar SONI +
            # Balli teng bo'lib, lekin IDsi mendan kichik bo'lganlar SONI
            count_query = select(func.count(Ranking.id)).where(
                (column > my_val) |
                ((column == my_val) & (Ranking.student_id < student_id))
            )
            return count_query.scalar_subquery()

        # Ranking mavjudligini tekshiramiz
        check_res = await self.db.execute(select(Ranking).where(Ranking.student_id == student_id))
        if not check_res.scalar_one_or_none():
            # Agar yo'q bo'lsa, yaratishga harakat qilamiz yoki default qaytaramiz
            await self.create_ranking(student_id)

        query = select(
            Ranking,
            (get_rank_subquery(Ranking.daily_points) + 1).label("daily_rank"),
            (get_rank_subquery(Ranking.weekly_points) + 1).label("weekly_rank"),
            (get_rank_subquery(Ranking.monthly_points) + 1).label("monthly_rank"),
            (get_rank_subquery(Ranking.total_points) + 1).label("all_rank")
        ).where(Ranking.student_id == student_id).options(selectinload(Ranking.student))

        result = await self.db.execute(query)
        return result.mappings().one_or_none()

    async def get_all_rankings(self, skip: int = 0, limit: int = 50) -> List[Ranking]:
        result = await self.db.execute(
            select(Ranking).order_by(Ranking.global_rank.asc())
            .offset(skip).limit(limit)
            .options(selectinload(Ranking.student))
        )
        return result.scalars().all()

    # app/services/ranking_service.py ichida

    async def get_leaderboard(
            self,
            period: str = "all",
            limit: int = 10,
            offset: int = 0,
            level: str = None
    ):
        # 1. Periodga qarab saralash ustunini aniqlaymiz
        sort_column_map = {
            "daily": Ranking.daily_points,
            "weekly": Ranking.weekly_points,
            "monthly": Ranking.monthly_points,
            "all": Ranking.total_points
        }
        target_col = sort_column_map.get(period, Ranking.total_points)

        # 2. Asosiy so'rov
        query = (
            select(
                Ranking.student_id,
                Ranking.daily_points,
                Ranking.weekly_points,
                Ranking.monthly_points,
                Ranking.total_points,
                Ranking.projects_completed,
                Student.username,
                Student.full_name,
                Student.avatar_url,
                Student.current_level,
                # MUHIM: rank() o'rniga row_number() ishlating
                func.row_number().over(
                    order_by=(target_col.desc(), Ranking.student_id.asc())
                ).label("period_rank")
            )
            .join(Student, Ranking.student_id == Student.id)
            .where(Student.is_active == True)
        )

        # 3. Agar level bo'yicha filtr bo'lsa
        if level:
            query = query.where(Student.current_level == level)

        # 4. Saralash va limit
        query = query.order_by(target_col.desc()).limit(limit).offset(offset)

        # 5. Natijani mapping ko'rinishida olish (r.period_rank deb ishlatish uchun)
        res = await self.db.execute(query)
        return res.mappings().all()

    async def add_points_to_student(self, student_id: int, points: int) -> Optional[Student]:
        """Studentga ball qo'shish (Yagona nuqta)"""
        res = await self.db.execute(select(Student).where(Student.id == student_id))
        student = res.scalar_one_or_none()
        if not student:
            return None

        # 1. Student modelini yangilaymiz
        student.total_points += points

        # 2. Ranking modelini yangilaymiz
        result = await self.db.execute(select(Ranking).where(Ranking.student_id == student_id))
        ranking = result.scalar_one_or_none()

        if ranking:
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
                last_calculated_at=datetime.utcnow(),
                last_daily_reset=datetime.utcnow(),
                last_weekly_reset=datetime.utcnow(),
                last_monthly_reset=datetime.utcnow()
            )
            self.db.add(ranking)

        await self.db.flush()
        # Ranklarni qayta hisoblash
        await self.calculate_and_update_rankings()
        await self.db.refresh(student)
        return student

    async def subtract_points_from_student(self, student_id: int, points: int) -> Optional[Student]:
        """Studentdan ball ayirish"""
        res = await self.db.execute(select(Student).where(Student.id == student_id))
        student = res.scalar_one_or_none()
        if not student:
            return None

        student.total_points = max(0, student.total_points - points)

        result = await self.db.execute(select(Ranking).where(Ranking.student_id == student_id))
        ranking = result.scalar_one_or_none()

        if ranking:
            ranking.daily_points = max(0, ranking.daily_points - points)
            ranking.weekly_points = max(0, ranking.weekly_points - points)
            ranking.monthly_points = max(0, ranking.monthly_points - points)
            ranking.total_points = student.total_points
            ranking.last_calculated_at = datetime.utcnow()

        await self.db.flush()
        await self.calculate_and_update_rankings()
        await self.db.refresh(student)
        return student

    # ========== RESET (NO CASCADE - simplified) ==========

    async def reset_daily_points(self):
        """Kun tugadi: daily = 0 (Weekly o'zi dolzarb qoladi)"""
        result = await self.db.execute(select(Ranking))
        rankings = result.scalars().all()
        for r in rankings:
            r.daily_points = 0
            r.last_daily_reset = datetime.utcnow()
        await self.db.commit()
        await self.calculate_and_update_rankings()

    async def reset_weekly_points(self):
        """Hafta tugadi: weekly = 0"""
        result = await self.db.execute(select(Ranking))
        rankings = result.scalars().all()
        for r in rankings:
            r.weekly_points = 0
            r.last_weekly_reset = datetime.utcnow()
        await self.db.commit()
        await self.calculate_and_update_rankings()

    async def reset_monthly_points(self):
        """Oy tugadi: monthly = 0"""
        result = await self.db.execute(select(Ranking))
        rankings = result.scalars().all()
        for r in rankings:
            r.monthly_points = 0
            r.last_monthly_reset = datetime.utcnow()
        await self.db.commit()
        await self.calculate_and_update_rankings()

    async def sync_all_student_points(self):
        """Barcha studentlar ballarini Ranking jadvali bilan sinxronizatsiya qilish"""
        # Barcha studentlarni olamiz
        student_res = await self.db.execute(
            select(Student).where(Student.role == UserRole.student)
        )
        students = student_res.scalars().all()

        for student in students:
            # Ranking mavjudligini tekshiramiz
            rank_res = await self.db.execute(
                select(Ranking).where(Ranking.student_id == student.id)
            )
            ranking = rank_res.scalar_one_or_none()

            if ranking:
                # Agar bor bo'lsa, total_points ni yangilaymiz
                # Daily/Weekly/Monthly larni tegmaymiz (ular o'zi reset bo'ladi)
                ranking.total_points = student.total_points
            else:
                # Agar yo'q bo'lsa, yangi yaratamiz
                new_ranking = Ranking(
                    student_id=student.id,
                    daily_points=0,
                    weekly_points=0,
                    monthly_points=0,
                    total_points=student.total_points,
                    last_daily_reset=datetime.utcnow(),
                    last_weekly_reset=datetime.utcnow(),
                    last_monthly_reset=datetime.utcnow()
                )
                self.db.add(new_ranking)
        
        await self.db.commit()
        await self.calculate_and_update_rankings()
        return len(students)

    # ========== RECALCULATE ==========

    async def calculate_and_update_rankings(self):
        """✅ Har period uchun alohida rank hisoblanadi"""
        ranking_res = await self.db.execute(
            select(Ranking).options(selectinload(Ranking.student))
        )
        all_rankings = ranking_res.scalars().all()

        # Faqat aktiv studentlar
        all_rankings = [
            r for r in all_rankings
            if r.student and r.student.is_active and r.student.role == UserRole.student
        ]

        # ✅ Har period uchun alohida sort → rank berish
        period_config = [
            ("total_points", "global_rank"),
            ("daily_points", "daily_rank"),
            ("weekly_points", "weekly_rank"),
            ("monthly_points", "monthly_rank"),
        ]

        for points_attr, rank_attr in period_config:
            sorted_r = sorted(all_rankings, key=lambda r: getattr(r, points_attr), reverse=True)
            for rank, ranking in enumerate(sorted_r, start=1):
                setattr(ranking, rank_attr, rank)
                if rank_attr == "global_rank":
                    # total_points ni Student bilan sinxronlashtirish
                    ranking.total_points = ranking.student.total_points
                    ranking.student.global_rank = rank
                ranking.last_calculated_at = datetime.utcnow()

        await self.db.commit()

    # ========== DELETE & UPDATE ==========

    async def delete_ranking(self, ranking_id: int) -> bool:
        result = await self.db.execute(select(Ranking).where(Ranking.id == ranking_id))
        ranking = result.scalar_one_or_none()
        if not ranking:
            return False
        await self.db.delete(ranking)
        await self.db.commit()
        return True

    async def update_ranking(self, ranking_id: int, **kwargs) -> Optional[Ranking]:
        result = await self.db.execute(
            select(Ranking).where(Ranking.id == ranking_id)
            .options(selectinload(Ranking.student))
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

        await self.db.flush()
        self.db.expire_all()
        await self.calculate_and_update_rankings()
        await self.db.refresh(ranking)
        return ranking

    async def get_my_ranking_with_periods(self, student_id: int):
        """Foydalanuvchining barcha davrlar bo'yicha o'rinlarini hisoblab beradi"""

        def get_rank_query(col):
            return select(func.count(Ranking.id)).where(
                col > select(col).where(Ranking.student_id == student_id).scalar_subquery())

        # Har bir davr uchun o'zidan tepada nechta odam borligini sanaymiz
        query = select(
            Ranking,
            (get_rank_query(Ranking.daily_points) + 1).label("daily_rank"),
            (get_rank_query(Ranking.weekly_points) + 1).label("weekly_rank"),
            (get_rank_query(Ranking.monthly_points) + 1).label("monthly_rank"),
            Ranking.global_rank.label("all_rank")
        ).where(Ranking.student_id == student_id).options(selectinload(Ranking.student))

        result = await self.db.execute(query)
        return result.mappings().one_or_none()

    async def get_my_ranking_with_all_ranks(self, student_id: int):
        """Foydalanuvchining har bir perioddagi rankini SQL orqali hisoblash"""

        # Har bir period uchun alohida subquery (o'rinni aniqlash uchun)
        def get_rank_subquery(column):
            return select(func.count(Ranking.id)).where(
                column > select(column).where(Ranking.student_id == student_id).scalar_subquery()
            ).scalar_subquery()

        query = select(
            Ranking,
            (get_rank_subquery(Ranking.daily_points) + 1).label("daily_rank"),
            (get_rank_subquery(Ranking.weekly_points) + 1).label("weekly_rank"),
            (get_rank_subquery(Ranking.monthly_points) + 1).label("monthly_rank"),
            Ranking.global_rank.label("all_rank")
        ).where(Ranking.student_id == student_id).options(selectinload(Ranking.student))

        result = await self.db.execute(query)
        return result.mappings().one_or_none()
