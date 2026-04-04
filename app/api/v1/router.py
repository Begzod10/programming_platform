from fastapi import APIRouter
from app.api.v1.endpoints import (
    students,
    projects,
    auth,
    rankings,
    degrees,
    achievements,
    courses,
    quizzes,
    lessons,
    groups,
    exercises,
    ai_review
)
from app.api.v1.endpoints.teacher import students as teacher_students

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(students.router, prefix="/student", tags=["Students"])
api_router.include_router(projects.router, prefix="/project", tags=["Projects"])
api_router.include_router(courses.router, prefix="/courses", tags=["Course"])
api_router.include_router(rankings.router, prefix="/rankings", tags=["Ranking"])
api_router.include_router(degrees.router, prefix="/degrees", tags=["Degree"])
api_router.include_router(achievements.router, prefix="/achievements", tags=["Achievements"])
api_router.include_router(lessons.router, prefix="", tags=["Lessons"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["Quizzes"])
api_router.include_router(groups.router, prefix="/groups", tags=["Groups"])
api_router.include_router(exercises.router, prefix="/courses/{course_id}/lessons", tags=["Exercises"])
api_router.include_router(ai_review.router, prefix="/ai", tags=["AI Review"])
api_router.include_router(teacher_students.router, prefix="/teacher/students", tags=["Teacher - Students"])