from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
import enum

if TYPE_CHECKING:
    from app.models.lesson import Lesson
    from app.models.user import Student


class ExerciseType(str, enum.Enum):
    fill_in_blank = "fill_in_blank"  # Bo'sh joy to'ldirish
    drag_and_drop = "drag_and_drop"  # Sudrab tashlash
    multiple_choice = "multiple_choice"  # Ko'p tanlov
    text_input = "text_input"  # Matn kiritish


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    # DEAD COLUMN: nothing in the serving code reads title_ru/description_ru/
    # hint_ru/explanation_ru/expected_answer_ru below. Live translation for
    # exercises goes exclusively through translation_cache, read via
    # app/services/translation_store.py and applied in
    # app/api/v1/endpoints/exercises.py::_translate_exercise_dto. Writing a
    # RU translation into one of these columns has NO effect on what a
    # Russian-language student sees — use
    # backend/scripts/write_ru_translations.py::translate_exercises()
    # instead, and verify with backend/scripts/check_ru_coverage.py.
    title_ru: Mapped[Optional[str]] = mapped_column(String(400), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Mashq turi
    exercise_type: Mapped[str] = mapped_column(
        String(50), default=ExerciseType.text_input, nullable=False
    )

    # Fill in blank uchun
    # description da ___ bilan bo'sh joy belgilanadi
    # correct_answers da to'g'ri javoblar vergul bilan yoziladi: "javob1,javob2"
    correct_answers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Drag and drop uchun
    # items — sudraladigan elementlar (JSON string): ["item1","item2","item3"]
    # correct_order — to'g'ri tartib (JSON string): ["item2","item1","item3"]
    drag_items: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    correct_order: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Multiple choice uchun
    # options — variantlar (JSON string): ["A","B","C","D"]
    # correct_answers — to'g'ri javob(lar): "A" yoki "A,C"
    options: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_multiple_select: Mapped[bool] = mapped_column(Boolean, default=False)  # bir yoki ko'p tanlov

    # Text input uchun
    expected_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_answer_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Umumiy
    hint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hint_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    explanation_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty_level: Mapped[str] = mapped_column(String(20), default="Easy")
    points: Mapped[int] = mapped_column(Integer, default=10)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now())

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="exercises")
    submissions: Mapped[List["ExerciseSubmission"]] = relationship(
        "ExerciseSubmission", back_populates="exercise", cascade="all, delete-orphan"
    )


class ExerciseSubmission(Base):
    __tablename__ = "exercise_submissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exercise_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    student_answer: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ai_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    time_spent_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="submissions")
    student: Mapped["Student"] = relationship("Student")
