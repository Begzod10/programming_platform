import os
import uuid
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy import select, func, text as sa_text, case
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pathlib import Path

from app.config import settings
from app.dependencies import get_db, get_current_student, get_current_instructor
from app.schemas.user import UserRead, UserUpdate, PasswordChange
from app.core.security import verify_password, get_password_hash
from app.schemas.project import ProjectRead
from app.schemas.public_profile import (
    PublicProfile,
    PublicAchievement,
    PublicCertificate,
    PublicTeamProject,
)
from app.services import profile_sync
from app.services.gennis_service import GennisService
from app.services.project_service import ProjectService
from app.services.student_service import StudentService
from app.models.user import Student

router = APIRouter()

UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "avatars"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/public/{username}", response_model=PublicProfile)
async def get_public_profile(
        username: str,
        db: AsyncSession = Depends(get_db),
):
    """Public student profile — no auth required.

    The response is shaped by PublicProfile in schemas/public_profile.py;
    every field there is intentionally public-safe. Email, phone, balance,
    and Gennis-issued tokens are excluded by construction (not by filter)
    so a future change to UserRead can't accidentally widen this surface.
    """
    from sqlalchemy import func
    from sqlalchemy.orm import selectinload
    from app.models.project import Project
    from app.models.student_achievement import (
        StudentAchievement,
        CourseCertificate,
    )

    res = await db.execute(
        select(Student).where(
            func.lower(Student.username) == username.lower(),
            Student.is_active == True,
        )
    )
    student = res.scalar_one_or_none()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    proj_res = await db.execute(
        select(func.count(Project.id)).where(
            Project.student_id == student.id,
            Project.status == "Approved",
        )
    )
    projects_approved = proj_res.scalar() or 0

    cert_res = await db.execute(
        select(CourseCertificate)
        .where(CourseCertificate.student_id == student.id)
        .options(selectinload(CourseCertificate.course))
        .order_by(CourseCertificate.issued_at.desc())
    )
    certificates = [
        PublicCertificate(
            course_title=c.course.title if c.course else "",
            issued_at=c.issued_at,
        )
        for c in cert_res.scalars().all()
        if c.course is not None
    ]

    ach_res = await db.execute(
        select(StudentAchievement)
        .where(StudentAchievement.student_id == student.id)
        .options(selectinload(StudentAchievement.achievement))
        .order_by(StudentAchievement.earned_at.desc())
    )
    achievements = [
        PublicAchievement(
            name=sa.achievement.name if sa.achievement else "—",
            description=(sa.achievement.description if sa.achievement else None),
            badge_image_url=(sa.achievement.badge_image_url if sa.achievement else None),
            icon=(sa.achievement.icon if sa.achievement else "🏆"),
            category=(sa.achievement.category if sa.achievement else None),
            points_reward=(sa.achievement.points_reward if sa.achievement else 0),
            earned_at=sa.earned_at,
        )
        for sa in ach_res.scalars().all()
        if sa.achievement is not None
    ]

    from app.models.team_project import TeamProjectTeam, TeamProjectMember, TeamStatus
    from app.models.project import Project as ProjectModel

    tp_res = await db.execute(
        select(
            TeamProjectTeam.project_title,
            TeamProjectMember.role,
            ProjectModel.grade,
            TeamProjectTeam.submitted_at,
        )
        .join(TeamProjectMember, TeamProjectMember.team_id == TeamProjectTeam.id)
        .outerjoin(ProjectModel, ProjectModel.id == TeamProjectTeam.final_project_id)
        .where(
            TeamProjectMember.student_id == student.id,
            TeamProjectTeam.status == TeamStatus.reviewed,
        )
        .order_by(TeamProjectTeam.submitted_at.desc())
    )
    team_projects = [
        PublicTeamProject(
            project_title=title,
            was_lead=(role.value if hasattr(role, "value") else role) == "lead",
            team_bonus_earned=grade in ("A", "B"),
            reviewed_at=submitted_at,
        )
        for title, role, grade, submitted_at in tp_res.all()
    ]

    return PublicProfile(
        username=student.username,
        full_name=student.full_name,
        avatar_url=student.avatar_url,
        current_level=(getattr(student.current_level, "value", student.current_level) or "Beginner"),
        total_points=student.total_points or 0,
        current_streak=student.current_streak or 0,
        longest_streak=student.longest_streak or 0,
        joined_at=student.created_at,
        projects_approved=projects_approved,
        certificates=certificates,
        achievements=achievements,
        team_projects=team_projects,
    )


@router.get("/me", response_model=UserRead)
async def get_me(current_student: Student = Depends(get_current_student)):
    return current_student


@router.put("/me", response_model=UserRead)
async def update_my_profile(
        data: UserUpdate,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    service = StudentService(db)
    return await service.update_own_profile(current_student, data)


@router.put("/me/password")
async def change_my_password(
        data: PasswordChange,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Change the logged-in student's password. Requires the current
    password to match before setting the new one."""
    if data.current_password == data.new_password:
        raise HTTPException(status_code=400, detail="Yangi parol joriy paroldan farq qilishi kerak")

    # A gennis/turon student's password lives in management (the DB gennis-v2 and
    # turon-v2 authenticate against); here only a placeholder is kept. So the
    # current password is checked by logging in there, and the new one is written
    # there — a failure leaves both sides unchanged.
    if profile_sync.external_identities(current_student) and not current_student.is_demo:
        if not await GennisService.login(current_student.username, data.current_password):
            raise HTTPException(status_code=400, detail="Joriy parol noto'g'ri")
        if not await profile_sync.push_profile(current_student, password=data.new_password):
            raise HTTPException(status_code=502, detail=profile_sync.UNREACHABLE)
        return {"message": "Parol muvaffaqiyatli yangilandi"}

    if not verify_password(data.current_password, current_student.hashed_password):
        raise HTTPException(status_code=400, detail="Joriy parol noto'g'ri")
    current_student.hashed_password = get_password_hash(data.new_password)
    await db.commit()
    return {"message": "Parol muvaffaqiyatli yangilandi"}


def _ensure_photo_editable(student: Student) -> None:
    """A gennis/turon student's photo comes from turon-v2 / gennis-v2 and cannot be changed here."""
    if student.identity_managed:
        raise HTTPException(
            status_code=403,
            detail="Profil rasmi Gennis/Turon tizimidan olinadi va bu yerda o'zgartirilmaydi.",
        )


@router.patch("/me/avatar")
async def upload_my_avatar(
        file: UploadFile = File(...),
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    _ensure_photo_editable(current_student)
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Faqat JPEG, PNG, WEBP!")

    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fayl 5MB dan katta!")

    # Eski avatarni o'chirish
    if current_student.avatar_url:
        old_path = UPLOAD_DIR / Path(current_student.avatar_url).name
        if old_path.exists():
            old_path.unlink()

    # Yangi fayl saqlash
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as f:
        f.write(contents)

    avatar_url = f"/uploads/avatars/{filename}"

    service = StudentService(db)
    await service.update_student(
        current_student.id,
        UserUpdate(avatar_url=avatar_url)
    )

    return {
        "avatar_url": avatar_url,
        "message": "Avatar muvaffaqiyatli yangilandi!"
    }


@router.delete("/me/avatar")
async def delete_my_avatar(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    _ensure_photo_editable(current_student)
    if not current_student.avatar_url:
        raise HTTPException(status_code=404, detail="Avatar mavjud emas!")

    # ✅ To'g'ri path
    old_path = UPLOAD_DIR / Path(current_student.avatar_url).name
    if old_path.exists():
        old_path.unlink()

    service = StudentService(db)
    await service.update_student(
        current_student.id,
        UserUpdate(avatar_url=None)
    )
    return {"message": "Avatar o'chirildi!"}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    if current_student.avatar_url:
        old_path = UPLOAD_DIR / Path(current_student.avatar_url).name
        if old_path.exists():
            old_path.unlink()

    service = StudentService(db)
    await service.delete_student(current_student.id)
    return None


@router.get("/me/projects", response_model=List[ProjectRead])
async def get_my_projects(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    service = ProjectService(db)
    return await service.get_all_projects_by_student(student_id=current_student.id)


@router.get("/", response_model=List[UserRead])
async def get_students(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        search: str = Query(None),
        current_user: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    service = StudentService(db)
    return await service.get_all_students(skip=skip, limit=limit, search=search)


@router.get("/{student_id}", response_model=UserRead)
async def get_student_by_id(
        student_id: int,
        current_user: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    service = StudentService(db)
    student = await service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student topilmadi")
    return student


@router.put("/{student_id}", response_model=UserRead)
async def update_specific_student(
        student_id: int,
        data: UserUpdate,
        current_user: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sizda boshqa student ma'lumotlarini o'zgartirish huquqi yo'q"
        )
    service = StudentService(db)
    student = await service.update_student(student_id, data)
    if not student:
        raise HTTPException(status_code=404, detail="Student topilmadi")
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_specific_student(
        student_id: int,
        current_user: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sizda bu akkauntni o'chirish huquqi yo'q"
        )
    service = StudentService(db)
    success = await service.delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student topilmadi")
    return None


@router.post("/refresh-all-student-levels")
async def refresh_all_student_levels(
        db: AsyncSession = Depends(get_db),
        current_teacher=Depends(get_current_instructor)
):
    result = await db.execute(select(Student))
    students = result.scalars().all()

    updated_count = 0
    for student in students:
        old_level = student.current_level
        student.total_points = student.total_points

        if old_level != student.current_level:
            updated_count += 1

    await db.commit()
    return {
        "status": "success",
        "total_students": len(students),
        "updated_levels_count": updated_count
    }


@router.get("/me/course-stats")
async def get_my_course_stats(
        db: AsyncSession = Depends(get_db),
        current_student: Student = Depends(get_current_student),
):
    sid = current_student.id

    # 1. Enrolled course IDs
    enrolled_rows = (await db.execute(
        sa_text("SELECT course_id FROM student_courses WHERE student_id = :sid"),
        {"sid": sid},
    )).all()
    course_ids = [r[0] for r in enrolled_rows]

    # 2. Course details
    courses_info = {}
    if course_ids:
        rows = (await db.execute(
            sa_text(
                "SELECT id, title, image_url, color_accent, difficulty_level "
                "FROM courses WHERE id = ANY(:ids)"
            ),
            {"ids": course_ids},
        )).all()
        for r in rows:
            courses_info[r.id] = {
                "id": r.id,
                "title": r.title,
                "image_url": r.image_url,
                "color_accent": r.color_accent or "#6c5ce7",
                "difficulty_level": r.difficulty_level,
            }

    # 3. Exercise stats per course (correct answers, counted once per exercise)
    ex_stats: dict[int, dict] = {}
    if course_ids:
        rows = (await db.execute(
            sa_text("""
                SELECT
                    l.course_id,
                    COUNT(DISTINCT e.id)                                                           AS total,
                    COUNT(DISTINCT CASE WHEN es.is_correct = TRUE THEN e.id END)                   AS correct
                FROM lessons l
                JOIN exercises e ON e.lesson_id = l.id AND e.is_active = TRUE
                LEFT JOIN exercise_submissions es
                       ON es.exercise_id = e.id AND es.student_id = :sid AND es.is_correct = TRUE
                WHERE l.course_id = ANY(:ids)
                GROUP BY l.course_id
            """),
            {"sid": sid, "ids": course_ids},
        )).all()
        for r in rows:
            total = r.total or 0
            correct = r.correct or 0
            ex_stats[r.course_id] = {
                "exercises_total": total,
                "exercises_correct": correct,
                "exercises_pct": round((correct / total * 100) if total > 0 else 0),
            }

    # 4. Submission stats per course
    sub_stats: dict[int, dict] = {}
    if course_ids:
        rows = (await db.execute(
            sa_text("""
                SELECT
                    l.course_id,
                    COUNT(sub.id)                                                                           AS total,
                    COUNT(CASE WHEN sub.status IN ('Approved', 'Reviewed') THEN 1 END)                     AS approved,
                    COUNT(CASE WHEN sub.status = 'Submitted' THEN 1 END)                                   AS pending,
                    COUNT(CASE WHEN sub.status IN ('Rejected') THEN 1 END)                                 AS rejected,
                    COALESCE(SUM(sub.points_earned), 0)                                                    AS points
                FROM submissions sub
                JOIN lessons l ON l.id = sub.lesson_id
                WHERE sub.student_id = :sid AND l.course_id = ANY(:ids)
                GROUP BY l.course_id
            """),
            {"sid": sid, "ids": course_ids},
        )).all()
        for r in rows:
            sub_stats[r.course_id] = {
                "submissions_total": r.total or 0,
                "submissions_approved": r.approved or 0,
                "submissions_pending": r.pending or 0,
                "submissions_rejected": r.rejected or 0,
                "points_from_submissions": r.points or 0,
            }

    # 5. Overall exercise totals (all courses, not just enrolled)
    ov_ex = (await db.execute(
        sa_text("""
            SELECT
                COUNT(DISTINCT e.id)                                                   AS total,
                COUNT(DISTINCT CASE WHEN es.is_correct = TRUE THEN e.id END)           AS correct
            FROM exercise_submissions es
            JOIN exercises e ON e.id = es.exercise_id
            WHERE es.student_id = :sid
        """),
        {"sid": sid},
    )).one()

    # 6. Overall project stats
    ov_proj = (await db.execute(
        sa_text("""
            SELECT
                COUNT(*)                                                                AS total,
                COUNT(CASE WHEN status IN ('Approved','Reviewed') THEN 1 END)          AS approved,
                COUNT(CASE WHEN status = 'Submitted' THEN 1 END)                       AS submitted,
                COUNT(CASE WHEN status = 'Rejected' THEN 1 END)                        AS rejected,
                COALESCE(SUM(CASE WHEN status IN ('Approved','Reviewed')
                                   THEN points_earned ELSE 0 END), 0)                  AS points
            FROM projects
            WHERE student_id = :sid
        """),
        {"sid": sid},
    )).one()

    # 7. Build per-course list
    courses_out = []
    for cid in course_ids:
        info = courses_info.get(cid, {"id": cid, "title": f"Course #{cid}", "image_url": None, "color_accent": "#6c5ce7", "difficulty_level": ""})
        ex  = ex_stats.get(cid,  {"exercises_total": 0, "exercises_correct": 0, "exercises_pct": 0})
        sub = sub_stats.get(cid, {"submissions_total": 0, "submissions_approved": 0, "submissions_pending": 0, "submissions_rejected": 0, "points_from_submissions": 0})
        courses_out.append({**info, **ex, **sub})

    # Sort: most exercises first, then alphabetical
    courses_out.sort(key=lambda c: (-c["exercises_total"], c["title"]))

    return {
        "profile": {
            "total_points": current_student.total_points,
            "global_rank": current_student.global_rank,
            "current_streak": current_student.current_streak,
            "longest_streak": current_student.longest_streak,
            "level": current_student.current_level.value if current_student.current_level else "Beginner",
        },
        "overall": {
            "exercises_total": ov_ex.total or 0,
            "exercises_correct": ov_ex.correct or 0,
            "exercises_pct": round((ov_ex.correct / ov_ex.total * 100) if (ov_ex.total or 0) > 0 else 0),
            "projects_total": ov_proj.total or 0,
            "projects_approved": ov_proj.approved or 0,
            "projects_submitted": ov_proj.submitted or 0,
            "projects_rejected": ov_proj.rejected or 0,
            "total_points_from_projects": ov_proj.points or 0,
        },
        "courses": courses_out,
    }


@router.get("/me/activity")
async def get_my_activity(
        db: AsyncSession = Depends(get_db),
        weeks: int = Query(26, ge=1, le=53),
        current_student: Student = Depends(get_current_student),
):
    """Daily activity heatmap (GitHub-style contribution matrix).

    Counts, per calendar day, every learning action the student took:
    exercise submissions, project-submission reviews, and project creations.
    The three sources are merged with UNION ALL and bucketed by day so the
    frontend just renders a fixed grid. Returns a dense array covering the
    whole window (days with no activity included as count 0) so the client
    doesn't have to fill gaps itself.
    """
    sid = current_student.id
    # Grid is week-aligned: start on the Monday on/before (today - weeks*7).
    today = date.today()
    raw_start = today - timedelta(days=weeks * 7 - 1)
    start = raw_start - timedelta(days=raw_start.weekday())  # back up to Monday

    rows = (await db.execute(
        sa_text("""
            SELECT d::date AS day, COUNT(*) AS cnt
            FROM (
                SELECT submitted_at AS ts FROM exercise_submissions
                    WHERE student_id = :sid AND submitted_at >= :start
                UNION ALL
                SELECT submitted_at AS ts FROM submissions
                    WHERE student_id = :sid AND submitted_at >= :start
                UNION ALL
                SELECT created_at AS ts FROM projects
                    WHERE student_id = :sid AND created_at >= :start
            ) t
            CROSS JOIN LATERAL (SELECT date_trunc('day', t.ts) AS d) x
            GROUP BY d
            ORDER BY d
        """),
        {"sid": sid, "start": start},
    )).all()

    counts: dict[date, int] = {r.day: int(r.cnt or 0) for r in rows}

    days = []
    total = 0
    active_days = 0
    streak = 0
    longest_streak = 0
    cur = start
    while cur <= today:
        c = counts.get(cur, 0)
        days.append({"date": cur.isoformat(), "count": c})
        total += c
        if c > 0:
            active_days += 1
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0
        cur += timedelta(days=1)

    # current streak = trailing run of active days ending today
    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    return {
        "start": start.isoformat(),
        "end": today.isoformat(),
        "days": days,
        "total": total,
        "active_days": active_days,
        "longest_streak": longest_streak,
        "current_streak": current_streak,
    }
