# app/db/base.py

from app.db.base_class import Base  # Sizning deklarativ bazangiz

# Barcha modellarni shu yerda import qilish shart!
from app.models.user import Student
from app.models.course import Course, CourseEnrollment
from app.models.project import Project
from app.models.submission import Submission
from app.models.ranking import Ranking
from app.models.degree import Degree
from app.models.student_degree import StudentDegree
from app.models.achievement import Achievement
from app.models.student_achievement import StudentAchievement
from app.models.lesson import Lesson
from app.models.group import Group  # <-- BU ALBATTA BO'LISHI SHART
__all__ = [
    "Base",
    "Student",
    "Course",
    "CourseEnrollment",
    "Project",
    "Submission",
    "Ranking",
    "Degree",
    "StudentDegree",
    "Achievement",
    "StudentAchievement",
    "Lesson",
    "Group"
]