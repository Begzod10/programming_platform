"""Reject project 1837 (student_id=33, lesson_id=10 "6-dars Div tegi",
course "HTML CSS"): the uploaded ZIP contains only a nested `2.rar` archive,
not real source files, so AI grading can never succeed on it. Sets
status=Rejected with feedback explaining the problem so the student can
re-upload properly, and keeps the linked Submission row in sync (matching
the pattern used elsewhere for status consistency between the two tables).
"""
from __future__ import annotations
import asyncio, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.project import Project  # noqa: E402
from app.models.submission import Submission  # noqa: E402

PROJECT_ID = 1837

FEEDBACK = (
    "Yuklangan ZIP fayl ichida faqat bitta arxiv (2.rar) topildi — haqiqiy "
    "HTML/CSS fayllaringiz yo'q edi. Iltimos, loyihangizni ZIP qilishda "
    "to'g'ridan-to'g'ri .html va .css fayllarni tanlang (ichma-ich yana bir "
    "arxiv — .rar yoki .zip — solmasdan), so'ng qaytadan yuklang."
)


async def main():
    async with AsyncSessionLocal() as db:
        project = (await db.execute(select(Project).where(Project.id == PROJECT_ID))).scalar_one()
        project.status = "Rejected"
        project.instructor_feedback = FEEDBACK
        project.reviewed_at = datetime.now(timezone.utc)

        sub = (await db.execute(
            select(Submission).where(Submission.project_id == PROJECT_ID)
        )).scalar_one_or_none()
        if sub is not None:
            sub.status = "Rejected"

        await db.commit()
        print(f"Project {PROJECT_ID}: set Rejected with feedback"
              + (f", submission {sub.id} synced" if sub else ", no linked submission found"))


if __name__ == "__main__":
    asyncio.run(main())
