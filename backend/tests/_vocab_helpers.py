"""Shared setup for the lesson-vocabulary suites: a teacher who owns a course with one lesson, and an enrolled
student. Other suites assume low, fixed course/lesson ids, so everything made here is removed again."""
import uuid

from sqlalchemy import delete, select

from app.core.security import create_access_token
from app.db.database import AsyncSessionLocal
from app.models.course import Course, student_courses
from app.models.dictionary import UserDictionary
from app.models.exercise import Exercise, ExerciseSubmission
from app.models.lesson import Lesson, LessonCompletion, LessonVocabulary
from app.models.project import Project
from app.models.ranking import Ranking
from app.models.submission import Submission
from app.models.user import Student, UserRole

LONG_TEXT = ("CSS selektorlari HTML elementlarini tanlash uchun ishlatiladi. Klass selektori nuqta bilan, id selektori "
             "panjara belgisi bilan yoziladi. Psevdo-element ::before va ::after element oldiga yoki ortiga kontent "
             "qo'shadi, buning uchun content xossasi majburiy. Spetsifiklik qaysi qoida ustun kelishini belgilaydi.")

_made: dict = {"students": [], "courses": []}


def h(user_id: int) -> dict:
    return {"Authorization": f"Bearer {create_access_token(subject=user_id)}"}


async def make_user(*, teacher=False, demo=False) -> int:
    uid = uuid.uuid4().hex[:8]
    async with AsyncSessionLocal() as db:
        s = Student(username=f"lv_{uid}", email=f"lv_{uid}@example.com", hashed_password="x",
                    full_name=f"User {uid}", role=UserRole.teacher if teacher else UserRole.student, is_demo=demo)
        db.add(s)
        await db.commit()
        _made["students"].append(s.id)
        return s.id


async def make_course(teacher_id: int, *, text: str = LONG_TEXT, lessons: int = 1, **lesson_fields) -> tuple:
    """(course_id, [lesson_ids])"""
    async with AsyncSessionLocal() as db:
        c = Course(title="HTML CSS", description="d", instructor_id=teacher_id, difficulty_level="Beginner",
                   duration_weeks=1, max_points=10, is_published=True)
        db.add(c)
        await db.flush()
        ls = [Lesson(course_id=c.id, title=f"Selektorlar {i}", order=i, text_content=text, **lesson_fields)
              for i in range(lessons)]
        db.add_all(ls)
        await db.commit()
        _made["courses"].append(c.id)
        return c.id, [l.id for l in ls]


async def enroll(student_id: int, course_id: int) -> None:
    async with AsyncSessionLocal() as db:
        await db.execute(student_courses.insert().values(student_id=student_id, course_id=course_id))
        await db.commit()


async def add_word(lesson_id: int, word: str, definition: str, definition_ru=None, source="manual", order=0) -> int:
    async with AsyncSessionLocal() as db:
        v = LessonVocabulary(lesson_id=lesson_id, word=word, definition=definition, definition_ru=definition_ru,
                             source=source, order=order)
        db.add(v)
        await db.commit()
        return v.id


async def words(lesson_id: int) -> list:
    async with AsyncSessionLocal() as db:
        return list((await db.execute(
            select(LessonVocabulary).where(LessonVocabulary.lesson_id == lesson_id)
            .order_by(LessonVocabulary.order, LessonVocabulary.id))).scalars().all())


async def dict_rows(student_id: int) -> list:
    async with AsyncSessionLocal() as db:
        return list((await db.execute(
            select(UserDictionary).where(UserDictionary.student_id == student_id)
            .order_by(UserDictionary.word, UserDictionary.lang))).scalars().all())


async def cleanup() -> None:
    async with AsyncSessionLocal() as db:
        sids, cids = _made["students"], _made["courses"]
        lesson_ids = (await db.execute(select(Lesson.id).where(Lesson.course_id.in_(cids)))).scalars().all()
        ex_ids = (await db.execute(select(Exercise.id).where(Exercise.lesson_id.in_(lesson_ids)))).scalars().all()
        await db.execute(delete(UserDictionary).where(UserDictionary.student_id.in_(sids)))
        await db.execute(delete(Submission).where(Submission.student_id.in_(sids)))
        await db.execute(delete(Project).where(Project.student_id.in_(sids)))
        await db.execute(delete(ExerciseSubmission).where(ExerciseSubmission.exercise_id.in_(ex_ids)))
        await db.execute(delete(Exercise).where(Exercise.id.in_(ex_ids)))
        await db.execute(delete(LessonCompletion).where(LessonCompletion.lesson_id.in_(lesson_ids)))
        await db.execute(delete(LessonVocabulary).where(LessonVocabulary.lesson_id.in_(lesson_ids)))
        await db.execute(delete(Lesson).where(Lesson.id.in_(lesson_ids)))
        await db.execute(delete(student_courses).where(student_courses.c.course_id.in_(cids)))
        await db.execute(delete(Course).where(Course.id.in_(cids)))
        await db.execute(delete(Ranking).where(Ranking.student_id.in_(sids)))
        await db.execute(delete(Student).where(Student.id.in_(sids)))
        await db.commit()
    _made["students"].clear()
    _made["courses"].clear()
