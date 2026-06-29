from fastapi import APIRouter
from app.api.v1.endpoints import (
    students,
    projects,
    auth,
    rankings,
    degrees,
    achievements,
    categories,
    courses,
    quizzes,
    lessons,
    groups,
    exercises,
    ai_review,
    lesson_feedback,
)
from app.api.v1.endpoints.teacher import students as teacher_students
from app.api.v1.endpoints.teacher import statistics as teacher_statistics
from app.api.v1.endpoints.teacher import course_access as teacher_course_access
from app.api.v1.endpoints.teacher import activity_analytics
from app.api.v1.endpoints import dictionary
from app.api.v1.endpoints import practice as dict_practice
from app.api.v1.endpoints import team_game
from app.api.v1.endpoints import parent
from app.api.v1.endpoints import bot_stats
api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(students.router, prefix="/student", tags=["Students"])
api_router.include_router(projects.router, prefix="/project", tags=["Projects"])
api_router.include_router(courses.router, prefix="/courses", tags=["Course"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(rankings.router, prefix="/rankings", tags=["Ranking"])
api_router.include_router(degrees.router, prefix="/degrees", tags=["Degree"])
api_router.include_router(achievements.router, prefix="/achievements", tags=["Achievements"])
api_router.include_router(lessons.router, prefix="", tags=["Lessons"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["Quizzes"])
api_router.include_router(groups.router, prefix="/groups", tags=["Groups"])
api_router.include_router(exercises.router, prefix="/courses/{course_id}/lessons", tags=["Exercises"])
api_router.include_router(ai_review.router, prefix="/ai", tags=["AI Review"])
api_router.include_router(teacher_students.router, prefix="/teacher/students", tags=["Teacher - Students"])
api_router.include_router(teacher_statistics.router, prefix="/teacher", tags=["Teacher - Statistics"])
api_router.include_router(teacher_course_access.router, prefix="/teacher/courses", tags=["Teacher - Course Access"])
api_router.include_router(dictionary.router, prefix="/dictionary", tags=["dictionary"])
api_router.include_router(dict_practice.router, prefix="/dictionary/practice", tags=["dictionary-practice"])
api_router.include_router(lesson_feedback.router, prefix="", tags=["Lesson Feedback"])
api_router.include_router(team_game.router, prefix="/game-sessions", tags=["Team Game"])
api_router.include_router(parent.router, prefix="/parent", tags=["Parent MiniApp"])
api_router.include_router(activity_analytics.router, prefix="/teacher/activity", tags=["Teacher Activity"])
api_router.include_router(bot_stats.router, prefix="/bot", tags=["Bot Stats"])
