from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.dependencies import get_db, get_current_student, get_current_instructor, get_current_student_optional
from app.services.ranking_service import RankingService
from app.schemas.ranking import LeaderboardItem, MyRankingRead, RankingUpdate
from app.models.user import Student, UserRole
from typing import List, Literal, Optional

router = APIRouter()


# ── Project-only leaderboard ──────────────────────────────────────────
# Window applies to projects.reviewed_at (falling back to submitted_at) so
# the rankings reflect the work that landed inside the window — not just
# total lifetime project points.
_PROJECT_WINDOW_SQL = {
    "all":   "",
    "day":   "AND COALESCE(p.reviewed_at, p.submitted_at) >= NOW() - INTERVAL '1 day'",
    "week":  "AND COALESCE(p.reviewed_at, p.submitted_at) >= NOW() - INTERVAL '7 days'",
    "month": "AND COALESCE(p.reviewed_at, p.submitted_at) >= NOW() - INTERVAL '30 days'",
}


@router.get("/project-leaderboard")
async def get_project_leaderboard(
        period: Literal["all", "day", "week", "month"] = Query("all"),
        course_id: Optional[int] = Query(None, description="Restrict ranking to a single course"),
        group_id: Optional[int] = Query(None, description="Restrict ranking to students in a group"),
        search: Optional[str] = Query(None, description="Filter by username or full name (ILIKE)"),
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
        current_user: Optional[Student] = Depends(get_current_student_optional),
):
    """Leaderboard ranked by SUM(projects.points_earned).

    Only counts projects whose status is reviewed (Approved / Submitted /
    Under Review). Draft and Rejected are excluded. Each row also carries
    the student's strongest course in the window so the FE can render the
    same "best_course +N" pill as the points-leaderboard.
    """
    # All three clauses below are injection-safe:
    #   window_clause  — value from a closed dict keyed by Literal["all","day","week","month"];
    #                    FastAPI validates the enum before this function runs.
    #   course_clause  — literal string containing only the :course_id named param.
    #   search_clause  — literal string containing only the :search named param.
    # None of them ever interpolate raw user input into the SQL text.
    assert period in _PROJECT_WINDOW_SQL, f"unexpected period: {period!r}"
    window_clause = _PROJECT_WINDOW_SQL[period]
    course_clause = "AND l.course_id = :course_id" if course_id is not None else ""
    search_clause = (
        "AND (st.username ILIKE :search OR COALESCE(st.full_name, '') ILIKE :search)"
        if search else ""
    )

    # When the caller is a teacher, restrict the ranking to their own students only.
    is_teacher = current_user is not None and current_user.role == UserRole.teacher
    teacher_clause = (
        """AND t.student_id IN (
            SELECT sg.student_id
            FROM student_groups sg
            JOIN groups g ON g.id = sg.group_id
            WHERE g.teacher_id = :teacher_id
        )"""
        if is_teacher else ""
    )
    group_clause = (
        "AND t.student_id IN (SELECT student_id FROM student_groups WHERE group_id = :group_id)"
        if group_id is not None else ""
    )

    params = {"skip": skip, "limit": limit}
    if course_id is not None:
        params["course_id"] = course_id
    if group_id is not None:
        params["group_id"] = group_id
    if search:
        params["search"] = f"%{search.strip()}%"
    if is_teacher:
        params["teacher_id"] = current_user.id

    # totals CTE: per-student aggregate within the window/course filter
    sql = text(f"""
        WITH project_rows AS (
            SELECT
                s.student_id,
                p.points_earned,
                l.course_id,
                c.title AS course_title
            FROM submissions s
            JOIN projects p ON p.id = s.project_id
            JOIN lessons  l ON l.id = s.lesson_id
            JOIN courses  c ON c.id = l.course_id
            WHERE p.status IN ('Approved', 'Submitted', 'Under Review')
              {window_clause}
              {course_clause}
        ),
        totals AS (
            SELECT
                pr.student_id,
                SUM(pr.points_earned)::int           AS project_points,
                COUNT(*)::int                        AS projects_count,
                ROUND(AVG(pr.points_earned)::numeric, 1) AS avg_grade
            FROM project_rows pr
            GROUP BY pr.student_id
        ),
        per_course AS (
            SELECT
                pr.student_id,
                pr.course_id,
                pr.course_title,
                SUM(pr.points_earned)::int AS course_points,
                ROW_NUMBER() OVER (
                    PARTITION BY pr.student_id
                    ORDER BY SUM(pr.points_earned) DESC
                ) AS course_rank
            FROM project_rows pr
            GROUP BY pr.student_id, pr.course_id, pr.course_title
        ),
        ranked AS (
            SELECT
                t.student_id,
                st.username,
                st.full_name,
                st.avatar_url,
                st.current_level,
                t.project_points,
                t.projects_count,
                t.avg_grade,
                pc.course_title AS best_course,
                pc.course_points AS best_course_points,
                RANK() OVER (ORDER BY t.project_points DESC, t.projects_count DESC) AS rank
            FROM totals t
            JOIN students st ON st.id = t.student_id
            LEFT JOIN per_course pc
                   ON pc.student_id = t.student_id AND pc.course_rank = 1
            WHERE 1 = 1
              {search_clause}
              {teacher_clause}
              {group_clause}
        )
        SELECT
            rank, student_id, username, full_name, avatar_url, current_level,
            project_points, projects_count, avg_grade,
            best_course, best_course_points,
            COUNT(*) OVER ()::int AS total_count
        FROM ranked
        ORDER BY rank ASC, project_points DESC
        OFFSET :skip
        LIMIT :limit
    """)

    rows = (await db.execute(sql, params)).mappings().all()
    total = rows[0]["total_count"] if rows else 0
    items = [
        {
            "rank":              r["rank"],
            "student_id":        r["student_id"],
            "username":          r["username"],
            "full_name":         r["full_name"],
            "avatar_url":        r["avatar_url"],
            "current_level":     r["current_level"],
            "project_points":    int(r["project_points"] or 0),
            "projects_count":    int(r["projects_count"] or 0),
            "avg_grade":         float(r["avg_grade"] or 0),
            "best_course":       r["best_course"],
            "best_course_points": int(r["best_course_points"] or 0) if r["best_course_points"] is not None else None,
        }
        for r in rows
    ]
    return {"items": items, "total": total, "period": period, "course_id": course_id, "group_id": group_id}


@router.get("/project-leaderboard/courses")
async def list_courses_for_filter(
        db: AsyncSession = Depends(get_db),
):
    """Lightweight courses list for the leaderboard's course-filter dropdown."""
    sql = text("""
        SELECT c.id, c.title
        FROM courses c
        WHERE EXISTS (
            SELECT 1 FROM lessons l
            JOIN submissions s ON s.lesson_id = l.id
            WHERE l.course_id = c.id
        )
        ORDER BY c.title
    """)
    rows = (await db.execute(sql)).mappings().all()
    return [{"id": r["id"], "title": r["title"]} for r in rows]


@router.get("/groups")
async def list_groups_for_filter(
        db: AsyncSession = Depends(get_db),
):
    """Groups list for the leaderboard's group-filter dropdown."""
    sql = text("""
        SELECT g.id, g.name,
               COUNT(sg.student_id) AS student_count
        FROM groups g
        JOIN student_groups sg ON sg.group_id = g.id
        GROUP BY g.id, g.name
        HAVING COUNT(sg.student_id) > 0
        ORDER BY g.name
    """)
    rows = (await db.execute(sql)).mappings().all()
    return [{"id": r["id"], "name": r["name"], "student_count": r["student_count"]} for r in rows]


# ========== STUDENT ENDPOINTS ==========

@router.get("/leaderboard", response_model=List[LeaderboardItem])
async def get_leaderboard(
        period: Literal["daily", "weekly", "monthly", "all"] = Query("all"),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        level: str = Query(None),
        group_id: Optional[int] = Query(None, description="Restrict to students in a group"),
        db: AsyncSession = Depends(get_db)
):
    """Leaderboard - Tanlangan period bo'yicha dinamik o'rin (rank) bilan."""
    service = RankingService(db)
    rankings = await service.get_leaderboard(
        period=period,
        limit=limit,
        offset=offset,
        level=level,
        group_id=group_id,
    )

    result = []
    for r in rankings:
        # Periodga qarab ochkoni dinamik tanlaymiz
        if period == "all":
            pts = r.total_points
        else:
            pts = getattr(r, f"{period}_points", 0)

        result.append(
            LeaderboardItem(
                rank=r.period_rank,
                student_id=r.student_id,
                username=r.username,
                full_name=r.full_name,
                avatar_url=r.avatar_url,
                points=pts,
                level=r.current_level,
                projects_completed=r.projects_completed
            )
        )
    return result


@router.get("/me", response_model=MyRankingRead)
async def my_ranking(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Foydalanuvchining barcha periodlar bo'yicha shaxsiy o'rinlari"""
    service = RankingService(db)
    r = await service.get_my_ranking(current_student.id)

    if not r:
        # Ranking topilmasa default qiymatlar
        return MyRankingRead(
            global_rank=0,
            daily_rank=0,
            weekly_rank=0,
            monthly_rank=0,
            daily_points=0,
            weekly_points=0,
            monthly_points=0,
            total_points=current_student.total_points,
            projects_completed=0,
            last_calculated_at=None
        )

    # Mapping'dan (dict ko'rinishida) ma'lumotlarni olamiz
    return MyRankingRead(
        global_rank=r['all_rank'],
        daily_rank=r['daily_rank'],
        weekly_rank=r['weekly_rank'],
        monthly_rank=r['monthly_rank'],
        daily_points=r['Ranking'].daily_points,
        weekly_points=r['Ranking'].weekly_points,
        monthly_points=r['Ranking'].monthly_points,
        total_points=r['Ranking'].total_points,
        projects_completed=r['Ranking'].projects_completed,
        last_calculated_at=r['Ranking'].last_calculated_at
    )


@router.get("/my-streak")
async def my_streak(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db),
):
    """Daily-activity streak summary for the sidebar flame widget.

    Returns the lazily-evaluated current streak (drops to 0 if the
    student missed yesterday), longest-ever streak, and whether today
    has already been credited.
    """
    from app.services.streak_service import get_streak
    return await get_streak(db, current_student.id)


@router.get("/my-stats")
async def get_my_stats(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Dashboard tepadagi widget (yulduzcha va global rank) uchun"""
    service = RankingService(db)
    ranking_data = await service.get_my_ranking(current_student.id)

    if not ranking_data:
        return {
            "total_points": current_student.total_points,
            "global_rank": "-",
            "projects_completed": 0
        }

    # ranking_data['Ranking'] -> Model obyektiga
    # ranking_data['all_rank'] -> Hisoblangan global o'ringa murojaat
    return {
        "total_points": current_student.total_points,
        "global_rank": f"#{ranking_data['all_rank']}" if ranking_data['all_rank'] > 0 else "-",
        "projects_completed": ranking_data['Ranking'].projects_completed
    }


# ========== INSTRUCTOR (TEACHER) ENDPOINTS ==========

@router.post("/", status_code=201)
async def create_ranking(
        student_id: int = Query(..., description="Student ID"),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Yangi ranking yaratish"""
    service = RankingService(db)
    result = await service.create_ranking(student_id)

    if not result:
        raise HTTPException(
            status_code=400,
            detail="Ranking allaqachon mavjud yoki foydalanuvchi student emas"
        )

    return {"message": "Ranking yaratildi!", "id": result.id, "student_id": result.student_id}


@router.put("/{ranking_id}")
async def update_ranking(
        ranking_id: int,
        data: RankingUpdate,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Ranking ochkolarini va statistikasini qo'lda yangilash"""
    service = RankingService(db)
    result = await service.update_ranking(ranking_id, **data.dict(exclude_unset=True))

    if not result:
        raise HTTPException(status_code=404, detail="Ranking topilmadi")

    return {
        "message": "Ranking yangilandi!",
        "id": result.id,
        "total_points": result.student.total_points
    }


@router.delete("/{ranking_id}", status_code=204)
async def delete_ranking(
        ranking_id: int,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Rankingni o'chirish"""
    service = RankingService(db)
    success = await service.delete_ranking(ranking_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ranking topilmadi")
    return None


@router.post("/add-points")
async def add_points(
        student_id: int = Query(...),
        points: int = Query(..., ge=1),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Studentga ball qo'shish"""
    service = RankingService(db)
    result = await service.add_points_to_student(student_id, points)
    if not result:
        raise HTTPException(status_code=404, detail="Student topilmadi")
    return {"message": f"{points} ball qo'shildi!", "total_points": result.total_points}


@router.post("/subtract-points")
async def subtract_points(
        student_id: int = Query(...),
        points: int = Query(..., ge=1),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Studentdan ball ayirish"""
    service = RankingService(db)
    result = await service.subtract_points_from_student(student_id, points)
    if not result:
        raise HTTPException(status_code=404, detail="Student topilmadi")
    return {"message": f"{points} ball ayirildi!", "total_points": result.total_points}


@router.post("/recalculate")
async def recalculate_rankings(
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Barcha reytinglarni qayta hisoblash"""
    service = RankingService(db)
    await service.calculate_and_update_rankings()
    return {"message": "Reytinglar qayta hisoblandi!"}


@router.post("/reset-daily")
async def reset_daily(current_teacher: Student = Depends(get_current_instructor), db: AsyncSession = Depends(get_db)):
    service = RankingService(db)
    await service.reset_daily_points()
    return {"message": "Kunlik ballar nolga tushirildi!"}


@router.post("/reset-weekly")
async def reset_weekly(current_teacher: Student = Depends(get_current_instructor), db: AsyncSession = Depends(get_db)):
    service = RankingService(db)
    await service.reset_weekly_points()
    return {"message": "Haftalik ballar nolga tushirildi!"}


@router.post("/reset-monthly")
async def reset_monthly(current_teacher: Student = Depends(get_current_instructor), db: AsyncSession = Depends(get_db)):
    service = RankingService(db)
    await service.reset_monthly_points()
    return {"message": "Oylik ballar nolga tushirildi!"}


@router.get("/all", response_model=List[MyRankingRead])
async def get_all_rankings(
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Barcha rankinglarni ko'rish (Teacher uchun)"""
    service = RankingService(db)
    rankings = await service.get_all_rankings(skip, limit)
    return [
        MyRankingRead(
            global_rank=r.global_rank,
            daily_rank=r.daily_rank,
            weekly_rank=r.weekly_rank,
            monthly_rank=r.monthly_rank,
            daily_points=r.daily_points,
            weekly_points=r.weekly_points,
            monthly_points=r.monthly_points,
            total_points=r.total_points,
            projects_completed=r.projects_completed,
            last_calculated_at=r.last_calculated_at
        )
        for r in rankings
    ]
