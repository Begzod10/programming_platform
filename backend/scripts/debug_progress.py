import asyncio
from sqlalchemy import select, func
from app.db.database import AsyncSessionLocal
from app.models.lesson import Lesson, LessonCompletion
from app.models.exercise import Exercise, ExerciseSubmission

async def check_stats(course_id, student_id):
    async with AsyncSessionLocal() as db:
        # Lessons
        total_lessons = await db.scalar(select(func.count(Lesson.id)).where(Lesson.course_id == course_id, Lesson.is_active == True))
        completed_lessons = await db.scalar(
            select(func.count(LessonCompletion.id))
            .join(Lesson, LessonCompletion.lesson_id == Lesson.id)
            .where(Lesson.course_id == course_id, LessonCompletion.student_id == student_id)
        )
        
        # Exercises
        total_ex = await db.scalar(
            select(func.count(Exercise.id))
            .join(Lesson, Exercise.lesson_id == Lesson.id)
            .where(Lesson.course_id == course_id, Exercise.is_active == True)
        )
        completed_ex = await db.scalar(
            select(func.count(ExerciseSubmission.exercise_id.distinct()))
            .select_from(ExerciseSubmission)
            .join(Exercise, Exercise.id == ExerciseSubmission.exercise_id)
            .join(Lesson, Lesson.id == Exercise.lesson_id)
            .where(Lesson.course_id == course_id, ExerciseSubmission.student_id == student_id, ExerciseSubmission.is_correct == True)
        )
        
        print(f"Course ID: {course_id}, Student ID: {student_id}")
        print(f"Lessons: {completed_lessons}/{total_lessons}")
        print(f"Exercises: {completed_ex}/{total_ex}")
        
        total_all = (total_lessons or 0) + (total_ex or 0)
        completed_all = (completed_lessons or 0) + (completed_ex or 0)
        
        if total_all > 0:
            perc = int((completed_all / total_all) * 100)
            print(f"Calculated Progress: {perc}%")
        else:
            print("No lessons or exercises.")

if __name__ == "__main__":
    # Assuming student_id is 81 based on previous logs
    asyncio.run(check_stats(1, 81))
