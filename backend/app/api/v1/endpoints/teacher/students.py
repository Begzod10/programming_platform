from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.dependencies import get_db, get_current_instructor
from app.schemas.user import UserRead, UserUpdate, UserCreate
from app.schemas.teacher_progress import (
    TeacherStudentProgress,
    TeacherStudentProgressDetail,
    TeacherStudentProgressList,
    TeacherStudentRankingList,
)
from app.models.user import Student
from app.models.student_achievement import StudentAchievement
from app.services.student_service import StudentService
from app.services.teacher_students import teacher_student_ids_subquery
from app.services.skill_profile_service import build_skill_profile
from app.schemas.team_project import SkillProfile
from app.schemas.dictionary import TeacherDictionaryWord, TeacherStudentDictionary, TeacherWordCheckBody

router = APIRouter()


VALID_PERIODS = ("day", "week", "month", "all")


@router.get("/rankings", response_model=TeacherStudentRankingList)
async def get_students_rankings(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        search: str = Query(None),
        period: str = Query(
            "all",
            description="day | week | month | all — which Ranking bucket to read",
        ),
        group_id: Optional[int] = Query(
            None,
            description="Restrict to one of the teacher's own groups (turon class filter)",
        ),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    if period not in VALID_PERIODS:
        period = "all"
    service = StudentService(db)
    return await service.get_teacher_students_ranking(
        current_teacher.id,
        skip=skip,
        limit=limit,
        search=search,
        period=period,
        group_id=group_id,
    )


async def _student_belongs_to_teacher(
    db: AsyncSession, student_id: int, teacher_id: int
) -> bool:
    """Return True iff `student_id` is reachable by `teacher_id` via a group
    OR a flow they own (see teacher_student_ids_subquery)."""
    res = await db.execute(
        select(Student.id).where(
            Student.id == student_id,
            Student.id.in_(select(teacher_student_ids_subquery(teacher_id).c.student_id)),
        )
        .limit(1)
    )
    return res.scalars().first() is not None


@router.get("/", response_model=List[TeacherStudentProgress])
async def get_all_students(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        search: str = Query(None),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    service = StudentService(db)
    return await service.get_students_by_teacher(current_teacher.id, skip, limit, search)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_student(
        data: UserCreate,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    from app.services.auth_service import register_new_student
    result = await register_new_student(db, data)
    return result["user"]


@router.get("/progress", response_model=TeacherStudentProgressList)
async def get_students_progress(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        search: str = Query(None),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    service = StudentService(db)
    return await service.get_teacher_students_progress(
        current_teacher.id,
        skip=skip,
        limit=limit,
        search=search,
    )


@router.get("/{student_id}/progress", response_model=TeacherStudentProgressDetail)
async def get_student_progress(
        student_id: int,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    service = StudentService(db)
    return await service.get_teacher_student_progress(current_teacher.id, student_id)


@router.get("/{student_id}/skill-profile", response_model=SkillProfile)
async def get_student_skill_profile(
        student_id: int,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """The knowledge/skill snapshot the team-project AI planner (Phase 3)
    builds assignments from — also what StudentProfile.js's teacher view
    surfaces (Phase 7)."""
    if not await _student_belongs_to_teacher(db, student_id, current_teacher.id):
        raise HTTPException(status_code=404, detail="Student not found")
    profile = await build_skill_profile(db, student_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return profile


async def _load_dictionary_words(
        db: AsyncSession, student_id: int, lang: Optional[str] = None, word_id: Optional[int] = None,
) -> List[TeacherDictionaryWord]:
    """A student's saved words with the teacher's oral-check state (latest verdict, when, how many times asked)."""
    from app.models.course import Course
    from app.models.dictionary import DictionaryWordCheck, UserDictionary
    from app.models.lesson import Lesson

    q = (
        select(UserDictionary, Lesson.title, Course.id, Course.title)
        .outerjoin(Lesson, Lesson.id == UserDictionary.lesson_id)
        .outerjoin(Course, Course.id == Lesson.course_id)
        .where(UserDictionary.student_id == student_id)
    )
    if lang:
        q = q.where(UserDictionary.lang == lang.strip().lower())
    if word_id is not None:
        q = q.where(UserDictionary.id == word_id)
    rows = (await db.execute(q.order_by(UserDictionary.created_at.desc(), UserDictionary.id.desc()))).all()

    checks = (await db.execute(
        select(DictionaryWordCheck.word_id, DictionaryWordCheck.knows, DictionaryWordCheck.created_at)
        .where(DictionaryWordCheck.student_id == student_id)
        .order_by(DictionaryWordCheck.created_at, DictionaryWordCheck.id)
    )).all()
    latest: dict = {}
    counts: dict = {}
    for wid, knows, created in checks:                     # ascending: the last write wins
        latest[wid] = (knows, created)
        counts[wid] = counts.get(wid, 0) + 1

    return [
        TeacherDictionaryWord(
            id=w.id, word=w.word, context=w.context, lang=w.lang or "uz", lesson_id=w.lesson_id,
            lesson_title=lesson_title, course_id=course_id, course_title=course_title,
            review_count=w.review_count or 0, correct_count=w.correct_count or 0,
            incorrect_count=w.incorrect_count or 0, last_reviewed_at=w.last_reviewed_at, created_at=w.created_at,
            last_check_knows=latest[w.id][0] if w.id in latest else None,
            last_checked_at=latest[w.id][1] if w.id in latest else None,
            checks_count=counts.get(w.id, 0),
        )
        for w, lesson_title, course_id, course_title in rows
    ]


@router.get("/{student_id}/dictionary", response_model=TeacherStudentDictionary)
async def get_student_dictionary(
        student_id: int,
        lang: Optional[str] = Query(None, description="uz | ru — only words saved in this language"),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """The words a student saved to their dictionary (lug'at), so the teacher can ask them out loud, with the
    teacher's recorded checks. Only for students the teacher reaches through a group or flow of their own."""
    if not await _student_belongs_to_teacher(db, student_id, current_teacher.id):
        raise HTTPException(status_code=404, detail="Student not found")
    words = await _load_dictionary_words(db, student_id, lang)
    known = sum(1 for w in words if w.last_check_knows is True)
    unknown = sum(1 for w in words if w.last_check_knows is False)
    return TeacherStudentDictionary(
        student_id=student_id, total=len(words), known=known, unknown=unknown,
        unchecked=len(words) - known - unknown, words=words,
    )


@router.post("/{student_id}/dictionary/{word_id}/check", response_model=TeacherDictionaryWord)
async def check_student_dictionary_word(
        student_id: int,
        word_id: int,
        body: TeacherWordCheckBody,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Record the result of asking the student a saved word out loud: knows / does not know. Every check is kept;
    the word's state is the latest one. Returns the word with its updated check state."""
    from app.models.dictionary import DictionaryWordCheck, UserDictionary

    if not await _student_belongs_to_teacher(db, student_id, current_teacher.id):
        raise HTTPException(status_code=404, detail="Student not found")
    word = (await db.execute(
        select(UserDictionary.id).where(UserDictionary.id == word_id, UserDictionary.student_id == student_id)
    )).scalar_one_or_none()
    if word is None:
        raise HTTPException(status_code=404, detail="Word not found")
    db.add(DictionaryWordCheck(word_id=word_id, student_id=student_id, teacher_id=current_teacher.id, knows=body.knows))
    await db.commit()
    return (await _load_dictionary_words(db, student_id, word_id=word_id))[0]


@router.delete("/{student_id}")
async def teacher_delete_student(
    student_id: int,
    current_teacher: Student = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Delete a student — only allowed if the student is in a group the
    requesting teacher owns. Without this check any teacher can delete
    any student account on the platform.
    """
    if not await _student_belongs_to_teacher(db, student_id, current_teacher.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu studentni o'chirish huquqi yo'q (sizning guruhingizda emas)",
        )
    service = StudentService(db)
    return await service.delete_student(student_id)


# ── Achievement overview schemas ───────────────────────────────────────────

class AchievementBrief(BaseModel):
    id: int
    name: str
    icon: Optional[str] = "🏆"
    category: Optional[str] = None
    points_reward: int = 0
    earned_at: datetime


class StudentAchievementOverview(BaseModel):
    student_id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    total_points: int = 0
    achievement_count: int = 0
    achievements: List[AchievementBrief] = []


# ── Endpoint ───────────────────────────────────────────────────────────────

@router.get("/achievements/overview", response_model=List[StudentAchievementOverview])
async def get_students_achievements_overview(
    current_teacher: Student = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db),
):
    """All students with the achievements they have earned.

    Returns every student (sorted by achievement count desc) with a flat
    list of their badges — name, icon, category, points, and date earned.
    """
    teacher_student_ids_sq = select(
        teacher_student_ids_subquery(current_teacher.id).c.student_id
    ).scalar_subquery()
    students_res = await db.execute(
        select(Student)
        .where(Student.id.in_(teacher_student_ids_sq))
        .order_by(Student.full_name)
    )
    students = students_res.scalars().all()

    student_ids = [s.id for s in students]
    if not student_ids:
        return []

    sa_res = await db.execute(
        select(StudentAchievement)
        .where(StudentAchievement.student_id.in_(student_ids))
        .options(selectinload(StudentAchievement.achievement))
        .order_by(StudentAchievement.earned_at.desc())
    )
    all_sa = sa_res.scalars().all()

    # Group by student
    by_student: dict[int, list] = {s.id: [] for s in students}
    for sa in all_sa:
        if sa.achievement is None:
            continue
        by_student[sa.student_id].append(AchievementBrief(
            id=sa.achievement_id,
            name=sa.achievement.name,
            icon=sa.achievement.icon or "🏆",
            category=sa.achievement.category,
            points_reward=sa.achievement.points_reward or 0,
            earned_at=sa.earned_at,
        ))

    result = [
        StudentAchievementOverview(
            student_id=s.id,
            username=s.username,
            full_name=s.full_name,
            avatar_url=s.avatar_url,
            total_points=s.total_points or 0,
            achievement_count=len(by_student[s.id]),
            achievements=by_student[s.id],
        )
        for s in students
    ]

    result.sort(key=lambda x: x.achievement_count, reverse=True)
    return result
