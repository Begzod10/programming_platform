from fastapi import APIRouter

from app.api.v1.endpoints import (
    students,
    projects,
    rankings,
    degrees,
    achievements,
    courses,
    auth
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(students.router, prefix="/student", tags=["Student"])
api_router.include_router(projects.router, prefix="/project", tags=["Project"])
# api_router.include_router(rankings.router, prefix="/ranking", tags=["Ranking"])
# api_router.include_router(degrees.router, prefix="/degree", tags=["Degree"])
# api_router.include_router(achievements.router, prefix="/achievements", tags=["Achievements"])
# api_router.include_router(courses.router, prefix="/course", tags=["Course"])
# api_router.include_router(auth.router, prefix="/student_Achievment", tags=["Auth"])
