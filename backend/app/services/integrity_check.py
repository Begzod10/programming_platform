"""Holds a lesson-project submission for a teacher instead of letting the AI
grader auto-approve it, when the submission pattern says the code almost
certainly wasn't written by the student.

Why this exists (2026-09-25 incident): one student had 34 lesson projects
auto-approved (A/B) by the AI grader, including 13 in 24 minutes and 9 in
16 minutes — 5-21 KB of polished HTML/CSS each, every one a single
TextEdit-default file ("текст.txt", "текст 2.txt", ...) created 1-3 minutes
before upload. The AI grader only answers "does this code fulfil the task",
so pasted AI output passes it perfectly; and the client-side
keystroke/paste counters can't help because the code is never typed on the
platform (ZIP / GitHub upload). Both signals below are server-side and
deterministic.

Like sample_copy_check, this never *rejects* anything — a held project just
stays "Submitted" for a teacher to grade by hand (POST /project/{id}/review),
so a false positive costs a teacher a minute, not the student their grade.
The reasons go into instructor_feedback (no schema change), where the
teacher sees them on the pending project; their own review overwrites it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.utils.datetime_utils import utcnow

# A 3rd lesson project inside 20 minutes is held. Genuine students do
# occasionally submit two in a row (finishing one, then a short one), but
# the incident above was 13-in-24-minutes; nobody writes and checks three
# multi-KB pages in 20 minutes.
BURST_WINDOW = timedelta(minutes=20)
BURST_MIN_OTHERS = 2

# "/* ===== НАВИГАЦИЯ ===== */"-style section banners — a strong house style
# of AI assistants' generated HTML/CSS. Informational only (never holds a
# project on its own): some teachers write this way too.
_BANNER = re.compile(r"(?:/\*|<!--)\s*={3,}")
BANNER_NOTE_MIN = 5

STUDENT_MESSAGE = (
    "Loyihangiz qabul qilindi va o'qituvchi tomonidan tekshiriladi. "
    "Natija tez orada chiqadi."
)


@dataclass(frozen=True)
class IntegrityResult:
    triggers: tuple[dict, ...] = ()
    notes: tuple[dict, ...] = field(default_factory=tuple)

    @property
    def held(self) -> bool:
        return bool(self.triggers)

    def feedback(self) -> Optional[str]:
        if not self.held:
            return None
        lines = [STUDENT_MESSAGE, "", "O'qituvchi uchun (avto-tekshiruv):"]
        lines += [f"- {f['detail']}" for f in self.triggers + self.notes]
        return "\n".join(lines)


def _only_plain_text_files(files_included: list[str]) -> bool:
    return bool(files_included) and all(
        f.lower().endswith(".txt") for f in files_included
    )


async def check_submission_integrity(
        db: AsyncSession,
        project: Project,
        *,
        files_included: list[str],
        content_text: str,
) -> IntegrityResult:
    triggers: list[dict] = []
    notes: list[dict] = []

    since = utcnow() - BURST_WINDOW
    recent = (await db.execute(
        select(func.count(Project.id)).where(
            Project.student_id == project.student_id,
            Project.id != project.id,
            Project.submitted_at.is_not(None),
            Project.submitted_at >= since,
        )
    )).scalar_one()
    if recent >= BURST_MIN_OTHERS:
        triggers.append({
            "code": "burst",
            "detail": f"Oxirgi {int(BURST_WINDOW.total_seconds() // 60)} daqiqada "
                      f"yana {recent} ta loyiha topshirilgan",
        })

    if _only_plain_text_files(files_included):
        triggers.append({
            "code": "plain_text_only",
            "detail": "Kod .html/.css/.js emas, faqat .txt faylda: "
                      + ", ".join(files_included[:5]),
        })

    banners = len(_BANNER.findall(content_text or ""))
    if banners >= BANNER_NOTE_MIN:
        notes.append({
            "code": "ai_style_banners",
            "detail": f"{banners} ta '/* ===== ... ===== */' bo'lim sarlavhasi "
                      "(AI yordamchilariga xos uslub)",
        })

    return IntegrityResult(triggers=tuple(triggers), notes=tuple(notes))
