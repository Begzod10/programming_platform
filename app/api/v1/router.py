from fastapi import APIRouter
from app.api.v1.endpoints import (
    students,
    projects,
    auth,
    rankings,
    degrees,
    achievements,
    courses
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

# Studentlar uchun (test_students.py /students/ kutyapti)
api_router.include_router(students.router, prefix="/students", tags=["Students"])

# Loyihalar uchun IKKALA prefixni qo'shamiz:
# 1. test_projects.py uchun (birlikda)
api_router.include_router(projects.router, prefix="/project", tags=["Projects"])
# 2. test_students.py uchun (ko'plikda)
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])

# Qolganlar
api_router.include_router(courses.router, prefix="/courses", tags=["Course"])
api_router.include_router(rankings.router, prefix="/rankings", tags=["Ranking"])
api_router.include_router(degrees.router, prefix="/degrees", tags=["Degree"])
api_router.include_router(achievements.router, prefix="/achievements", tags=["Achievements"])