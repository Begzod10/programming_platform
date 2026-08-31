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
            total_points=student.lifetime_points,
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
            level: str = None,
            group_id: int = None,
            peer_student_id: int = None,
    ):
        """Leaderboard query.

        LEFT JOINs Ranking onto Student (not the other way round) — a
        student who hasn't earned any points yet, or simply hasn't opened
        their own dashboard yet (Ranking rows are created lazily on first
        view), still shows up here with 0 points. Otherwise a freshly
        synced class is invisible to itself: their teacher's login just
        populated the group correctly, but nobody in it appears on the
        leaderboard until each of them individually triggers Ranking-row
        creation. Missing values are coalesced to 0 throughout.

        peer_student_id: when set, restrict the ranking to students who share
        at least one teacher with the given student (i.e. the caller's peers
        under any of their teachers). Used to scope the student-facing
        leaderboard so it doesn't leak platform-wide totals.
        """
        from app.models.group import Group, student_groups
        daily = func.coalesce(Ranking.daily_points, 0)
        weekly = func.coalesce(Ranking.weekly_points, 0)
        monthly = func.coalesce(Ranking.monthly_points, 0)
        total = func.coalesce(Ranking.total_points, 0)
        sort_column_map = {
            "daily": daily,
            "weekly": weekly + daily,
            "monthly": monthly + daily,
            "all": total,
        }
        target_col = sort_column_map.get(period, total)

        query = (
            select(
                Student.id.label("student_id"),
                daily.label("daily_points"),
                weekly.label("weekly_points"),
                monthly.label("monthly_points"),
                total.label("total_points"),
                func.coalesce(Ranking.projects_completed, 0).label("projects_completed"),
                Student.username,
                Student.full_name,
                Student.avatar_url,
                Student.current_level,
                func.row_number().over(
                    order_by=(target_col.desc(), Student.id.asc())
                ).label("period_rank")
            )
            .select_from(Student)
            .outerjoin(Ranking, Ranking.student_id == Student.id)
            .where(Student.is_active == True, Student.role == UserRole.student)
        )

        if level:
            query = query.where(Student.current_level == level)

        if group_id is not None:
            query = query.where(
                Student.id.in_(
                    select(student_groups.c.student_id).where(student_groups.c.group_id == group_id)
                )
            )

        if peer_student_id is not None:
            my_teachers_subq = (
                select(Group.teacher_id)
                .join(student_groups, student_groups.c.group_id == Group.id)
                .where(student_groups.c.student_id == peer_student_id)
            )
            peer_ids_subq = (
                select(student_groups.c.student_id)
                .join(Group, Group.id == student_groups.c.group_id)
                .where(Group.teacher_id.in_(my_teachers_subq))
            )
            query = query.where(Student.id.in_(peer_ids_subq))

        query = query.order_by(target_col.desc()).limit(limit).offset(offset)

        res = await self.db.execute(query)
        return res.mappings().all()

    async def add_points_to_student(self, student_id: int, points: int) -> Optional[Student]:
        """Studentga ball qo'shish (Yagona nuqta).

        Bumps both wallets:
          * `total_points`   — spendable balance (used by the store)
          * `lifetime_points` — monotonic career total (drives level + rank)

        The leaderboard reads `Ranking.total_points`, which we keep in sync
        with the student's `lifetime_points` — so spending in the store
        never drops a student down the leaderboard or demotes their level.
        """
        res = await self.db.execute(select(Student).where(Student.id == student_id))
        student = res.scalar_one_or_none()
        if not student:
            return None

        student.total_points += points
        student.lifetime_points += points

        result = await self.db.execute(select(Ranking).where(Ranking.student_id == student_id))
        ranking = result.scalar_one_or_none()

        if ranking:
            ranking.daily_points += points
            ranking.total_points = student.lifetime_points
            ranking.last_calculated_at = datetime.utcnow()
        else:
            ranking = Ranking(
                student_id=student_id,
                daily_points=points,
                weekly_points=0,
                monthly_points=0,
                total_points=student.lifetime_points,
                last_calculated_at=datetime.utcnow(),
                last_daily_reset=datetime.utcnow(),
                last_weekly_reset=datetime.utcnow(),
                last_monthly_reset=datetime.utcnow()
            )
            self.db.add(ranking)

        await self.db.flush()
        await self.calculate_and_update_rankings()
        await self.db.refresh(student)
        return student

    async def subtract_points_from_student(self, student_id: int, points: int) -> Optional[Student]:
        """Studentdan spendable balansdan ayirish.

        Only `total_points` (the spendable balance) is reduced. `lifetime_points`
        and the leaderboard-facing `Ranking.total_points` are left alone, so a
        purchase never lowers the student's level or global rank. Callers who
        want to *revoke earned points* (e.g. reversing a bad submission) must
        use `revoke_earned_points` instead — do not repurpose this method.
        """
        res = await self.db.execute(select(Student).where(Student.id == student_id))
        student = res.scalar_one_or_none()
        if not student:
            return None

        student.total_points = max(0, student.total_points - points)
        await self.db.flush()
        await self.db.refresh(student)
        return student

    async def revoke_earned_points(self, student_id: int, points: int) -> Optional[Student]:
        """Reverse points that were previously granted via `add_points_to_student`.

        Use this — never `subtract_points_from_student` — when undoing a
        prior *earn* (e.g. a project is re-reviewed/re-graded and the old
        score must be backed out before the new one is applied, or a
        teacher revokes an achievement). `add_points_to_student` bumps both
        `total_points` (spendable) and `lifetime_points` (career total that
        drives the leaderboard/level); this method mirrors that by reducing
        both, so a reversed award can never leave `lifetime_points`/
        `Ranking.total_points` permanently inflated the way a bare
        `subtract_points_from_student` call would (that method intentionally
        only touches the spendable wallet, for store purchases).
        """
        res = await self.db.execute(select(Student).where(Student.id == student_id))
        student = res.scalar_one_or_none()
        if not student:
            return None

        student.total_points = max(0, student.total_points - points)
        student.lifetime_points = max(0, student.lifetime_points - points)

        await self.db.flush()
        await self.calculate_and_update_rankings()
        await self.db.refresh(student)
        return student

    # ========== RESET (NO CASCADE - simplified) ==========

    async def reset_daily_points(self):
        """
        Kun tugadi: daily_points haftalikka va oylikka QO'SHILADI.
        Keyin daily_points 0 qilinadi.
        """
        result = await self.db.execute(select(Ranking))
        rankings = result.scalars().all()
        for r in rankings:
            # Foydalanuvchi xohlaganidek: haftalik va oylikka avtomatik qo'shiladi
            r.weekly_points += r.daily_points
            r.monthly_points += r.daily_points
            r.daily_points = 0
            r.last_daily_reset = datetime.utcnow()
        await self.db.commit()
        await self.calculate_and_update_rankings()

    async def reset_weekly_points(self):
        """Hafta tugadi: haftalik ballar nolga tushadi"""
        result = await self.db.execute(select(Ranking))
        rankings = result.scalars().all()
        for r in rankings:
            r.weekly_points = 0
            r.last_weekly_reset = datetime.utcnow()
        await self.db.commit()
        await self.calculate_and_update_rankings()

    async def reset_monthly_points(self):
        """Oy tugadi: oylik ballar nolga tushadi"""
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
                # Mirror career total (lifetime_points), not the spendable
                # wallet — see add_points_to_student for the rationale.
                ranking.total_points = student.lifetime_points
            else:
                new_ranking = Ranking(
                    student_id=student.id,
                    daily_points=0,
                    weekly_points=0,
                    monthly_points=0,
                    total_points=student.lifetime_points,
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
            # Sortlashda real-time summani hisobga olamiz
            if points_attr == "weekly_points":
                key_func = lambda r: r.weekly_points + r.daily_points
            elif points_attr == "monthly_points":
                key_func = lambda r: r.monthly_points + r.daily_points
            else:
                key_func = lambda r: getattr(r, points_attr)

            sorted_r = sorted(all_rankings, key=key_func, reverse=True)
            for rank, ranking in enumerate(sorted_r, start=1):
                setattr(ranking, rank_attr, rank)
                if rank_attr == "global_rank":
                    # Mirror lifetime_points (career earned total) — NOT
                    # total_points (spendable). Otherwise buying a theme
                    # would drop the student down the leaderboard.
                    ranking.total_points = ranking.student.lifetime_points
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
        # Real-time summalarni hisobga olamiz
        def get_rank_subquery(column, is_cumulative=False):
            if is_cumulative:
                my_val = select(column + Ranking.daily_points).where(Ranking.student_id == student_id).scalar_subquery()
                return select(func.count(Ranking.id)).where(
                    (column + Ranking.daily_points) > my_val
                ).scalar_subquery()
            else:
                return select(func.count(Ranking.id)).where(
                    column > select(column).where(Ranking.student_id == student_id).scalar_subquery()
                ).scalar_subquery()

        query = select(
            Ranking,
            (get_rank_subquery(Ranking.daily_points) + 1).label("daily_rank"),
            (get_rank_subquery(Ranking.weekly_points, True) + 1).label("weekly_rank"),
            (get_rank_subquery(Ranking.monthly_points, True) + 1).label("monthly_rank"),
            Ranking.global_rank.label("all_rank")
        ).where(Ranking.student_id == student_id).options(selectinload(Ranking.student))

        result = await self.db.execute(query)
        return result.mappings().one_or_none()
