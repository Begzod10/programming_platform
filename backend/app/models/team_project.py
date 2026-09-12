"""Team Projects — AI-planned collaborative projects.

A student in a group is placed into a team. The AI generates a project
idea, splits it into pieces with explicit interface contracts, and assigns
each piece to the member whose skills fit (see
app/services/skill_profile_service.py for the input signal and
app/services/team_project_planner.py, Phase 3, for the planner itself).
Members submit their pieces; each gets an AI review. The strongest member
is the lead/integrator: once every piece is approved, they assemble the
final repo and submit it, reusing the existing Project + AI review
pipeline. Points are awarded per piece plus a team bonus.

Status machines:
  TeamProjectStatus: planning -> pending_approval -> active -> integrating
                      -> submitted -> reviewed  (or -> cancelled at any point)
  TeamStatus:         forming -> working -> integrating -> submitted -> reviewed
  TaskStatus:         assigned -> submitted -> approved
                                            \\-> changes_requested -> submitted (resubmit loop)
                       assigned -> blocked (deadline passed, still unsubmitted)
                       assigned -> reassigned (teacher moved it to someone else)

All `*_json` columns are Text holding a json.dumps() string, not a native
JSON column type — matches the existing convention for structured content
elsewhere (Lesson.sections_json, Exercise.drag_items/correct_order), not
team_game.py's GameQuestion.options (which does use a native JSON column) —
picked Text here to match the majority convention for this kind of
"AI-authored, audit-worthy, rarely queried by field" content.
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import (
    String, Integer, Text, DateTime, ForeignKey, Enum, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.user import StudentLevel
from app.utils.datetime_utils import utcnow


class TeamProjectStatus(str, PyEnum):
    planning = "planning"
    pending_approval = "pending_approval"
    active = "active"
    integrating = "integrating"
    submitted = "submitted"
    reviewed = "reviewed"
    cancelled = "cancelled"


class TeamStatus(str, PyEnum):
    forming = "forming"
    working = "working"
    integrating = "integrating"
    submitted = "submitted"
    reviewed = "reviewed"


class TeamRole(str, PyEnum):
    member = "member"
    lead = "lead"


class TaskStatus(str, PyEnum):
    assigned = "assigned"
    submitted = "submitted"
    changes_requested = "changes_requested"
    approved = "approved"
    blocked = "blocked"
    reassigned = "reassigned"


class TeamProject(Base):
    __tablename__ = "team_projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False,
    )
    # Scope hint for the planner's course-context lookup (Phase 3) — when
    # null, the planner falls back to every course the group's students
    # have >= 50% completion in. Losing the course shouldn't destroy the
    # project's history, so SET NULL rather than CASCADE.
    course_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("courses.id", ondelete="SET NULL"), nullable=True,
    )
    teacher_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("students.id", ondelete="SET NULL"), nullable=True,
    )

    # Nullable until the AI plan is generated and applied per-team.
    title: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[TeamProjectStatus] = mapped_column(
        Enum(TeamProjectStatus), default=TeamProjectStatus.planning, nullable=False,
    )
    team_size: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    deadline_days: Mapped[int] = mapped_column(Integer, default=14, nullable=False)

    # Whole-project lifecycle gates — genuinely project-wide: the scheduler
    # activates every team of a project together once auto_activate_at
    # passes AND every team has a valid plan (Phase 4).
    auto_activate_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # ai_plan_json / plan_generated_at / generation_attempts are on
    # TeamProjectTeam below, NOT here, despite the feature spec's schema
    # listing them under this table — see this phase's final report for
    # why: Phase 4's regenerate endpoint is team-scoped
    # (POST .../teams/{team_id}/regenerate) and caps generation_attempts
    # at 3 per that same endpoint description. A single project-level
    # counter/plan would mean regenerating team A's plan also burns team
    # B's and C's attempt budget and overwrites what should be team B's
    # own plan JSON with team A's — reusing the project-level field as
    # specified doesn't hold up once a project has more than one team,
    # which it always will for anything but a single-team pilot.

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    group: Mapped["Group"] = relationship("Group", foreign_keys=[group_id])
    course: Mapped[Optional["Course"]] = relationship("Course", foreign_keys=[course_id])
    teacher: Mapped[Optional["Student"]] = relationship("Student", foreign_keys=[teacher_id])
    teams: Mapped[List["TeamProjectTeam"]] = relationship(
        "TeamProjectTeam", back_populates="team_project", cascade="all, delete-orphan",
    )
    events: Mapped[List["TeamProjectEvent"]] = relationship(
        "TeamProjectEvent", back_populates="team_project", cascade="all, delete-orphan",
        order_by="TeamProjectEvent.created_at",
    )


class TeamProjectTeam(Base):
    __tablename__ = "team_project_teams"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    team_project_id: Mapped[int] = mapped_column(
        ForeignKey("team_projects.id", ondelete="CASCADE"), nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    lead_student_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("students.id", ondelete="SET NULL"), nullable=True,
    )
    # The lead's final submission reuses Project so the existing AI-review
    # pipeline (run_ai_review_for_project) works unmodified — see Phase 4.
    # SET NULL (not CASCADE): if the Project row is ever deleted, this team
    # loses its link to the final submission but is not itself destroyed —
    # the team/task/audit history is worth keeping regardless.
    final_project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"), nullable=True,
    )

    status: Mapped[TeamStatus] = mapped_column(
        Enum(TeamStatus), default=TeamStatus.forming, nullable=False,
    )
    integration_unlocked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Randomly assigned per-team at formation time (team_project_service.
    # create_team_project) — each team gets its own independent theme/stack
    # even within the same TeamProject, so two teams in one assignment can
    # build different ideas on different stacks. Keys into
    # team_project_constants.THEMES / TECH_STACKS.
    theme: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tech_stack: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # AI-generated concrete idea (e.g. "Kichik do'kon uchun CRM"), denormalized
    # out of ai_plan_json below so list views can show it without parsing JSON.
    project_title: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    project_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Per-team plan tracking — see the note on TeamProject above for why
    # these live here rather than on the parent project.
    ai_plan_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    plan_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    generation_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    team_project: Mapped["TeamProject"] = relationship("TeamProject", back_populates="teams")
    lead: Mapped[Optional["Student"]] = relationship("Student", foreign_keys=[lead_student_id])
    final_project: Mapped[Optional["Project"]] = relationship("Project", foreign_keys=[final_project_id])
    members: Mapped[List["TeamProjectMember"]] = relationship(
        "TeamProjectMember", back_populates="team", cascade="all, delete-orphan",
    )
    tasks: Mapped[List["TeamProjectTask"]] = relationship(
        "TeamProjectTask", back_populates="team", cascade="all, delete-orphan",
        order_by="TeamProjectTask.order",
    )
    peer_ratings: Mapped[List["TeamProjectPeerRating"]] = relationship(
        "TeamProjectPeerRating", back_populates="team", cascade="all, delete-orphan",
    )
    events: Mapped[List["TeamProjectEvent"]] = relationship(
        "TeamProjectEvent", back_populates="team", cascade="all, delete-orphan",
    )


class TeamProjectMember(Base):
    __tablename__ = "team_project_members"
    __table_args__ = (UniqueConstraint("team_id", "student_id", name="uq_team_project_member"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("team_project_teams.id", ondelete="CASCADE"), nullable=False,
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False,
    )
    role: Mapped[TeamRole] = mapped_column(Enum(TeamRole), default=TeamRole.member, nullable=False)

    # Snapshots taken at assignment time — a student's level/skills moving
    # on afterward must not retroactively change what the plan was built
    # against, or the interface contracts stop matching the reasoning that
    # produced them.
    # String, not a native Enum(StudentLevel) column: that would reuse the
    # 'studentlevel' Postgres type Student.current_level already created —
    # SQLAlchemy's create_type=False doesn't reliably suppress a duplicate
    # CREATE TYPE when Alembic's op.create_table() runs with checkfirst=False
    # (confirmed while writing this migration; a real SQLAlchemy/Alembic
    # interaction gotcha, not a design choice). Matches the existing
    # String-backed-pseudo-enum convention already used elsewhere in this
    # codebase (e.g. Exercise.exercise_type) for the same reason.
    level_at_assignment: Mapped[StudentLevel] = mapped_column(String(20), nullable=False)
    skill_summary_at_assignment: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    team: Mapped["TeamProjectTeam"] = relationship("TeamProjectTeam", back_populates="members")
    student: Mapped["Student"] = relationship("Student", foreign_keys=[student_id])


class TeamProjectTask(Base):
    __tablename__ = "team_project_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("team_project_teams.id", ondelete="CASCADE"), nullable=False,
    )
    # Nullable during planning, before assign_tasks() resolves each piece's
    # assign_to_member_index into an actual student_id (Phase 3).
    assigned_student_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("students.id", ondelete="SET NULL"), nullable=True,
    )

    order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    title_ru: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_ru: Mapped[str] = mapped_column(Text, nullable=False)

    # String, not native Enum — see the identical note on
    # TeamProjectMember.level_at_assignment above.
    required_level: Mapped[StudentLevel] = mapped_column(String(20), nullable=False)

    # {"files": [...], "produces": [...], "consumes": [...]}
    interface_contract_json: Mapped[str] = mapped_column(Text, nullable=False)
    # list[str]
    acceptance_criteria_json: Mapped[str] = mapped_column(Text, nullable=False)
    # list[int] — other tasks' `order` values this one depends on.
    depends_on_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    estimated_hours: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.assigned, nullable=False)

    # Same semantics as Project.github_url / project_files — a piece can be
    # submitted as a repo URL or an uploaded ZIP.
    submission_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    submission_files: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    ai_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # {"criteria_results": [...], "contract_violations": [...], "feedback": "...", "feedback_ru": "..."}
    ai_feedback_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lead_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    points_awarded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    deadline_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    team: Mapped["TeamProjectTeam"] = relationship("TeamProjectTeam", back_populates="tasks")
    assigned_student: Mapped[Optional["Student"]] = relationship("Student", foreign_keys=[assigned_student_id])


class TeamProjectPeerRating(Base):
    __tablename__ = "team_project_peer_ratings"
    __table_args__ = (
        UniqueConstraint(
            "team_id", "rater_student_id", "rated_student_id",
            name="uq_team_project_peer_rating",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("team_project_teams.id", ondelete="CASCADE"), nullable=False,
    )
    rater_student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False,
    )
    rated_student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False,
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    team: Mapped["TeamProjectTeam"] = relationship("TeamProjectTeam", back_populates="peer_ratings")
    rater: Mapped["Student"] = relationship("Student", foreign_keys=[rater_student_id])
    rated: Mapped["Student"] = relationship("Student", foreign_keys=[rated_student_id])


class TeamProjectEvent(Base):
    """Append-only audit log. Every state change in this feature writes a
    row here — see the guardrails section of the feature spec."""
    __tablename__ = "team_project_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    team_project_id: Mapped[int] = mapped_column(
        ForeignKey("team_projects.id", ondelete="CASCADE"), nullable=False,
    )
    team_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("team_project_teams.id", ondelete="SET NULL"), nullable=True,
    )
    # Null = system/AI-originated event (plan generation, auto-activate,
    # the deadline-sweep job), not a specific student's action.
    actor_student_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("students.id", ondelete="SET NULL"), nullable=True,
    )

    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Free-form JSON payload, shape depends on event_type — e.g.
    # {"errors": [...]} for a failed plan_generated, {"reason": "..."} for
    # lead_changed, {"by": "auto"|"teacher"} for plan_activated.
    payload_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    team_project: Mapped["TeamProject"] = relationship("TeamProject", back_populates="events")
    team: Mapped[Optional["TeamProjectTeam"]] = relationship("TeamProjectTeam", back_populates="events")
    actor: Mapped[Optional["Student"]] = relationship("Student", foreign_keys=[actor_student_id])
