from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
import enum
from sqlalchemy.orm import validates
from sqlalchemy import (
    String, Integer, Boolean, DateTime, Enum, Text, func, ForeignKey
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
    total_points: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    global_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Status fields
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

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
        back_populates="students"
    )

    ranking: Mapped[Optional["Ranking"]] = relationship(
        "Ranking",
        back_populates="student",
        uselist=False,
        cascade="all, delete-orphan"
    )

    group: Mapped[Optional["Group"]] = relationship(
        "Group",
        back_populates="students"
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

    @validates('total_points')
    def sync_level_with_points(self, key, value):
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
