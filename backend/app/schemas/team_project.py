from datetime import date, datetime
from typing import List, Optional, Dict

from pydantic import BaseModel, ConfigDict, Field

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


# ── Team Projects API shapes ───────────────────────────────────────────────

class TeamProjectCreate(BaseModel):
    group_id: int
    course_id: Optional[int] = None
    team_size: int = 4
    deadline_days: int = 14


class TaskRead(BaseModel):
    id: int
    order: int
    title: str
    title_ru: str
    description: str
    description_ru: str
    required_level: str
    interface_contract: dict
    acceptance_criteria: List[str]
    depends_on: List[int]
    estimated_hours: int
    status: str
    assigned_student_id: Optional[int] = None
    assigned_student_name: Optional[str] = None
    submission_url: Optional[str] = None
    ai_score: Optional[int] = None
    ai_feedback: Optional[dict] = None
    deadline_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MemberRead(BaseModel):
    student_id: int
    full_name: str
    role: str
    level_at_assignment: str


class TeamRead(BaseModel):
    id: int
    name: str
    status: str
    theme: Optional[str] = None
    theme_label: Optional[str] = None
    tech_stack: Optional[str] = None
    tech_stack_label: Optional[str] = None
    project_title: Optional[str] = None
    project_description: Optional[str] = None
    lead_student_id: Optional[int] = None
    final_project_id: Optional[int] = None
    generation_attempts: int = 0
    members: List[MemberRead] = []
    tasks: List[TaskRead] = []


class TeamProjectRead(BaseModel):
    id: int
    group_id: int
    course_id: Optional[int] = None
    status: str
    team_size: int
    deadline_days: int
    created_at: datetime
    teams: List[TeamRead] = []


class MyTeamProjectRead(BaseModel):
    team_project: TeamProjectRead
    my_team: TeamRead
    my_role: str


class TaskSubmitBody(BaseModel):
    submission_url: Optional[str] = None
    submission_files: Optional[str] = None


class ReassignBody(BaseModel):
    student_id: int


class FinalizeBody(BaseModel):
    github_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    description: Optional[str] = None


class PeerRatingItem(BaseModel):
    rated_student_id: int
    score: int = Field(ge=1, le=5)
    comment: Optional[str] = None
