"""
TranslationCache — on-demand AI translations for lesson/course/exercise text.

When a student opens a lesson in a language different from the row's source
language, the relevant endpoint asks the translation service for each
natural-language field. The service returns the cached row if present,
otherwise calls Groq, stores the result here, and returns it.

The cache key is (entity_type, entity_id, lang, field_name). The source
hash is recorded so a teacher edit of the original invalidates downstream
translations on the next read (without us having to write an explicit
delete path everywhere).
"""

from datetime import datetime, timezone
from sqlalchemy import (
    String, Integer, Text, DateTime, UniqueConstraint, Index,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TranslationCache(Base):
    __tablename__ = "translation_cache"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 'lesson' | 'course' | 'exercise' — small enough to keep open-text
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id:   Mapped[int] = mapped_column(Integer, nullable=False)

    # ISO 639-1 code ('uz', 'ru'). Future expansion to 'en' / 'kk' is a
    # row-add, no schema change.
    lang: Mapped[str] = mapped_column(String(8), nullable=False)

    # The logical field being translated (e.g. 'title', 'text_content',
    # 'task_description', or 'sections_json'). The service decides what
    # fields exist per entity_type.
    field_name: Mapped[str] = mapped_column(String(64), nullable=False)

    # Translated payload. For sections_json this is the translated JSON
    # serialised as text. For plain fields it's the translated string.
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)

    # SHA-256 of the source text at translation time. Recorded so a read
    # path can invalidate stale rows when the teacher edits the source.
    source_text_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # Where the translation came from — for now always 'groq' but kept
    # for future provider swaps + audit ("regenerate everything from
    # provider X").
    provider: Mapped[str] = mapped_column(String(16), nullable=False, default="groq")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow,
    )

    __table_args__ = (
        UniqueConstraint(
            "entity_type", "entity_id", "lang", "field_name",
            name="uq_translation_cache_key",
        ),
        # Hot lookup index — every read hits this composite
        Index(
            "ix_translation_cache_lookup",
            "entity_type", "entity_id", "lang",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<TranslationCache(type={self.entity_type}, "
            f"id={self.entity_id}, lang={self.lang}, field={self.field_name})>"
        )
