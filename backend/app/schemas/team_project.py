from datetime import date
from typing import List, Optional, Dict

from pydantic import BaseModel, ConfigDict

from app.models.user import StudentLevel


class SkillProfileCompletedCourse(BaseModel):
    course_id: int
    title: str
    category: Optional[str] = None


class SkillProfilePastProject(BaseModel):
    title: str
    technologies_used: List[str] = []
    grade: Optional[str] = None
    ai_strengths: Optional[str] = None
    ai_improvements: Optional[str] = None


class SkillProfile(BaseModel):
    """A student's knowledge/skill snapshot — the input the team-project AI
    planner uses to assign pieces and pick a lead. Deliberately NOT the same
    thing as Student.current_level, which only tracks lifetime_points (an
    activity measure, not a knowledge map) — see skill_profile_service.py.
    """
    student_id: int
    full_name: str
    current_level: StudentLevel
    lifetime_points: int

    completed_courses: List[SkillProfileCompletedCourse] = []
    completed_lessons_by_course: Dict[int, int] = {}
    # Accuracy topics come from two different groupings merged into one flat
    # dict (see skill_profile_service.py's module docstring for why): course
    # category names (e.g. "Web Asoslari") and exercise types (e.g.
    # "multiple_choice"). Only included where attempts >= 5.
    exercise_accuracy_by_topic: Dict[str, float] = {}
    past_projects: List[SkillProfilePastProject] = []
    technologies_seen: List[str] = []

    streak: int
    last_activity_date: Optional[date] = None

    summary: str

    model_config = ConfigDict(from_attributes=True)
