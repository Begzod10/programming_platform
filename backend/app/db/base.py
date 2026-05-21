# app/db/base.py
# Centralizes model imports so Base.metadata sees every table — required for
# Base.metadata.create_all() and for Alembic autogeneration to work correctly.

from app.db.base_class import Base

from app.models.user import Student
from app.models.course import Course
from app.models.project import Project
from app.models.submission import Submission
from app.models.ranking import Ranking
from app.models.degree import Degree
from app.models.student_degree import StudentDegree
from app.models.achievement import Achievement
from app.models.student_achievement import StudentAchievement, CourseCertificate
from app.models.lesson import Lesson, LessonCompletion
from app.models.group import Group
from app.models.exercise import Exercise, ExerciseSubmission
from app.models.quiz import Quiz, Question, StudentQuizResult
from app.models.video_watch import VideoWatch

__all__ = [
    "Base",
    "Student",
    "Course",
    "Project",
    "Submission",
    "Ranking",
    "Degree",
    "StudentDegree",
    "Achievement",
    "StudentAchievement",
    "CourseCertificate",
    "Exercise",
    "ExerciseSubmission",
    "Lesson",
    "LessonCompletion",
    "Group",
    "Quiz",
    "Question",
    "StudentQuizResult",
    "VideoWatch",
]
