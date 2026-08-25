from datetime import datetime, date
from typing import List, Optional, TYPE_CHECKING
import enum
from sqlalchemy.orm import validates
from sqlalchemy import (
    String, Integer, Boolean, DateTime, Date, Enum, Text, func, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.course import student_courses

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.project import Project
    from app.models.student_achievement import StudentAchievement
    from app.models.student_degree import StudentDegree
    from app.models.ranking import Ranking
    from app.models.group import Group
    from app.models.flow import Flow
    from app.models.certificate import CourseCertificate


class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"


class StudentLevel(str, enum.Enum):
    Beginner = "Beginner"
    Intermediate = "Intermediate"
    Advanced = "Advanced"


class Student(Base):
    __tablename__ = "students"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Auth fields
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile fields
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512))
    bio: Mapped[Optional[str]] = mapped_column(Text)

    # Role
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.student,
        server_default="student",
        nullable=False
    )

    # Student fields
    enrollment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    current_level: Mapped[StudentLevel] = mapped_column(
        Enum(StudentLevel),
        default=StudentLevel.Beginner,
        server_default="Beginner",
        nullable=False
    )
    # Spendable balance. Goes up on earn, down when the student buys from the
    # store. Named `total_points` for historical reasons; think of it as the
    # student's coin wallet. Do NOT read this for level or leaderboard rank —
    # those read `lifetime_points` so buying cosmetics never lowers status.
    total_points: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Monotonic career total — every earn increments it; spending never
    # decreases it. This is what drives `current_level` (via the validator
    # below) and what `ranking_service` writes into `rankings.total_points`
    # for the leaderboard. Split from `total_points` so the store economy
    # can deduct coins without also demoting the student and dropping them
    # in the rankings.
    lifetime_points: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    global_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Daily-activity streak. Bumped by streak_service.bump_streak() whenever
    # the student does meaningful work (exercise submit, lesson complete,
    # project submit, dictionary quiz). Read-heavy field — denormalized on
    # the row so the FE streak widget renders without a join.
    current_streak: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    last_activity_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Status fields
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # Gennis specific fields
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    balance: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    surname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gennis_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gennis_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    # Turon and gennis mint ids independently, so the same integer can refer to
    # two different real people — this MUST stay a separate column from
    # gennis_id, never a shared "external_id". See auth_service.login's
    # `source` branch.
    turon_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Foreign keys
    group_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("groups.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    groups: Mapped[List["Group"]] = relationship(
        "Group",
        secondary="student_groups",
        back_populates="students",
        lazy="selectin"
    )

    # Turon-only — see app/models/flow.py. Gennis has no equivalent concept.
    flows: Mapped[List["Flow"]] = relationship(
        "Flow",
        secondary="student_flows",
        back_populates="students",
        lazy="selectin"
    )

    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    student_achievements: Mapped[List["StudentAchievement"]] = relationship(
        "StudentAchievement",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    student_degrees: Mapped[List["StudentDegree"]] = relationship(
        "StudentDegree",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    enrolled_courses: Mapped[List["Course"]] = relationship(
        "Course",
        secondary="student_courses",
        back_populates="students",
        lazy="selectin"
    )

    ranking: Mapped[Optional["Ranking"]] = relationship(
        "Ranking",
        back_populates="student",
        uselist=False,
        cascade="all, delete-orphan"
    )

    group: Mapped[Optional["Group"]] = relationship(
        "Group",
        back_populates="students",
        foreign_keys="Student.group_id",
        overlaps="groups"  # Added overlaps to avoid warning
    )

    lesson_completions: Mapped[List["LessonCompletion"]] = relationship(
        "LessonCompletion",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    taught_courses: Mapped[List["Course"]] = relationship(
        "Course",
        back_populates="instructor"
    )

    certificates: Mapped[List["CourseCertificate"]] = relationship(
        "CourseCertificate",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    managed_groups: Mapped[List["Group"]] = relationship(
        "Group",
        back_populates="teacher",
        foreign_keys="Group.teacher_id"
    )

    dictionary_words = relationship("UserDictionary", back_populates="student")

    @validates('lifetime_points')
    def sync_level_with_points(self, key, value):
        # Level tracks lifetime (earned) points, not the spendable balance.
        # This way buying a theme can lower `total_points` without demoting
        # the student.
        points = value if value is not None else 0

        if points >= 5000:
            self.current_level = StudentLevel.Advanced
        elif points >= 1000:
            self.current_level = StudentLevel.Intermediate
        else:
            self.current_level = StudentLevel.Beginner

        return points

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, username={self.username}, role={self.role})>"
