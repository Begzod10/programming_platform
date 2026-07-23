from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.db.base_class import Base


class LessonSample(Base):
    __tablename__ = "lesson_samples"

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, unique=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    sample_type = Column(String(32), nullable=False, default="web")  # web, python, sql, code
    html_code = Column(Text, nullable=True)
    css_code = Column(Text, nullable=True)
    js_code = Column(Text, nullable=True)
    # For sample_type="code": JSON array of {filename, language, code}. Used
    # for lessons whose real syntax can't run in the web/python/sql iframe
    # preview (React/TS/anything needing a build step) — renders as a
    # read-only tabbed source viewer instead of executing anything, so the
    # namuna can show the ACTUAL taught API instead of a same-looking
    # substitute in a different language.
    code_files_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
