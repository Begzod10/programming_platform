from typing import Optional

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
from app.db.base_class import Base


class UserDictionary(Base):
    __tablename__ = "user_dictionary"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    word = Column(String, nullable=False)
    context = Column(String, nullable=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="dictionary_words")
    lesson = relationship("Lesson")
    lesson_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True
    )
