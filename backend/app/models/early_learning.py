from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
import enum

from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, func,
    UniqueConstraint, CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import Student


class EarlySubject(str, enum.Enum):
    literacy = "literacy"      # letters, phonics, sight words
    math = "math"               # counting, shapes, comparison
    logic = "logic"             # sequencing, patterns, mazes
    creative = "creative"       # drawing, music/rhythm
    motor = "motor"             # tracing, cutting-practice style taps


class EarlyActivityType(str, enum.Enum):
    trace = "trace"              # finger/stylus tracing a letter or shape
    match = "match"               # tap-to-match pairs
    sequence = "sequence"         # drag steps into correct order
    count = "count"               # tap-to-count objects
    sort = "sort"                 # sort by size/color/shape into buckets
    maze = "maze"                 # arrow-based pathfinding
    coloring = "coloring"         # free digital coloring
    audio_story = "audio_story"   # narrated read-along


class EarlyModule(Base):
    """A themed set of activities for one subject (e.g. 'Harflar sayohati').

    Parallel to Course, but deliberately not a Course subtype — no AI
    grading, no submissions, no code content. age_min/age_max are advisory
    only: Student has no birth_date, so there is no enforced per-student age
    gate yet (see project_student_platform memory for the open decision).
    """
    __tablename__ = "early_modules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Russian translation of title/description — source_lang below stays "uz"
    # (that's still where the content is authored first), these are just a
    # second rendering picked by the API when ?lang=ru is requested. Nullable
    # so an untranslated module falls back to the uz text instead of 404ing.
    #
    # Deliberately NOT routed through app/services/translation_service.py's
    # translate_fields/translate_json_blob (the generic AI-translate-and-cache
    # path lessons/courses/exercises use) — this whole catalog is a small,
    # fixed, hand-authored vocabulary (professions, seasons, colors...) where
    # a wrong AI guess on a kids' game term is worse than the cost of typing
    # the ~40 module/activity strings by hand once in the seed script. Content
    # that grows or gets teacher-authored later is the signal to switch this
    # over to the shared translation_cache path instead.
    title_ru: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    description_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    subject: Mapped[EarlySubject] = mapped_column(Enum(EarlySubject), nullable=False, index=True)

    age_min: Mapped[int] = mapped_column(Integer, nullable=False, default=4, server_default="4")
    age_max: Mapped[int] = mapped_column(Integer, nullable=False, default=6, server_default="6")

    icon_emoji: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    color_accent: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    instructor_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )

    source_lang: Mapped[str] = mapped_column(String(8), nullable=False, default="uz", server_default="uz")
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("age_min <= age_max", name="ck_early_module_age_range"),
    )

    instructor: Mapped["Student"] = relationship("Student", foreign_keys=[instructor_id])
    activities: Mapped[List["EarlyActivity"]] = relationship(
        "EarlyActivity", back_populates="module", cascade="all, delete-orphan",
        order_by="EarlyActivity.order",
    )

    @property
    def activities_count(self) -> int:
        return len(self.activities) if self.activities else 0


class EarlyActivity(Base):
    """One screen/game unit within a module. Parallel to Lesson, but the
    'content' is a single JSON blob whose shape depends on activity_type —
    deliberately not normalized into per-type tables (no concrete need yet
    to query inside it).
    """
    __tablename__ = "early_activities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    module_id: Mapped[int] = mapped_column(
        ForeignKey("early_modules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    # Russian translations — see EarlyModule.title_ru for the fallback rule
    # (null renders as the uz text, never a 404).
    title_ru: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    activity_type: Mapped[EarlyActivityType] = mapped_column(Enum(EarlyActivityType), nullable=False)

    # Narration is mandatory-in-spirit at this age — most kids can't read
    # instructions yet. Kept nullable at the DB level so content authors can
    # save drafts before recording, but the publish flow should validate it.
    instruction_audio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    instruction_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # captions / translation source
    instruction_text_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Shape depends on activity_type, validated at the Pydantic/schema layer,
    # e.g. {"items": [...], "targets": [...], "image_url": "..."} for match;
    # {"path": [...], "start": ..., "end": ...} for maze.
    content_json: Mapped[str] = mapped_column(Text, nullable=False)

    estimated_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=90, server_default="90")
    max_stars: Mapped[int] = mapped_column(Integer, nullable=False, default=3, server_default="3")

    source_lang: Mapped[str] = mapped_column(String(8), nullable=False, default="uz", server_default="uz")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    module: Mapped["EarlyModule"] = relationship("EarlyModule", back_populates="activities")
    completions: Mapped[List["EarlyActivityCompletion"]] = relationship(
        "EarlyActivityCompletion", back_populates="activity", cascade="all, delete-orphan"
    )


class EarlyActivityCompletion(Base):
    """Best-attempt record per (student, activity) — mirrors LessonCompletion's
    one-row-per-pair convention, but tracks a star score + attempt count
    instead of a bare timestamp, since these activities are retryable and
    ungraded (no AI review, no submission).
    """
    __tablename__ = "early_activity_completions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    activity_id: Mapped[int] = mapped_column(ForeignKey("early_activities.id", ondelete="CASCADE"), nullable=False)

    stars_earned: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    first_completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_attempt_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    student: Mapped["Student"] = relationship("Student")
    activity: Mapped["EarlyActivity"] = relationship("EarlyActivity", back_populates="completions")

    __table_args__ = (
        UniqueConstraint("student_id", "activity_id", name="uq_student_early_activity"),
    )
