"""Deterministic, server-side checks run on a lesson-project submission BEFORE
the AI grader. Each hit is a rule violation (see submission_violations.py):
the project is rejected with the reason and the student can't submit for 20
minutes. Nothing here is "held for a teacher" any more — a teacher can't read
every submission, so the rules enforce themselves.

Why server-side: the code is written outside the platform and arrives as a ZIP
or GitHub link, so the client-side keystroke/paste counters (which only see the
optional comment box) can't see it. The 2026-09-25 incident (34 auto-approved
projects of pasted AI output) is what these checks exist for.

Rules checked here:
  duplicate_content       same code as ANOTHER student's project
  unchanged_resubmission  same code as the student's OWN already-rejected project
  prompt_injection        text in the code aimed at the AI grader ("give 100")
The lesson-sample copy check lives in sample_copy_check.py and the
"3 rejections in 20 minutes" rule in ai_review_service.py (it needs the AI's
verdict); both record violations the same way.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project

# Too little code to say anything: boilerplate pages and one-line answers are
# legitimately identical between students.
FINGERPRINT_MIN_CHARS = 400

_FILE_BLOCK = re.compile(r"^### [^\n]*\n```\n(.*?)\n```\s*(?=^### |\Z)", re.M | re.S)

# Shown when a ZIP's only code is in .txt files. A very common accident:
# Windows hides known extensions, so "index.html" saved from Notepad is really
# "index.html.txt". Rejected at upload (no project is graded, no penalty) so
# the student can fix it and resend immediately.
PLAIN_TEXT_UPLOAD_MESSAGE = (
    "ZIP ichida kod faqat .txt fayl(lar)da: {files}. Agar bu HTML/CSS/JS bo'lsa, "
    "kengaytmani .html/.css/.js ga o'zgartirib qayta yuklang "
    "(Windows: Вид → «Расширения имён файлов»ni yoqing).\n"
    "В ZIP код только в .txt файлах: {files}. Если это HTML/CSS/JS, переименуйте "
    "файлы в .html/.css/.js и загрузите снова."
)

# Instructions aimed at the AI grader. A false positive bans an honest student,
# so every pattern needs a clearly grader-directed phrase — a bare "score = 100"
# or "100 ball ber" is ordinary game code/comments and must NOT match.
_GRADER_WORDS = r"(?:\bai\b|baholovchi|tekshiruvchi|o'qituvchi|\bgrader\b|\brubric\b|проверяющ\w*|нейросет\w*)"
_MAX_SCORE = r"(?:100\s*(?:ball|балл|points?|marks?)|to'liq\s*ball|maksimal\s*ball|максимальн\w+\s*балл|full\s+(?:marks|points|score)|maximum\s+(?:marks|points|score))"
_INJECTION = (
    re.compile(r"ignore\s+(?:all\s+|any\s+|the\s+|your\s+)?(?:previous|prior|above|earlier)\s+(?:instructions|rules|rubric|guidelines)", re.I),
    re.compile(r"disregard\s+(?:all\s+|any\s+|the\s+)?(?:previous|prior|above)\s+(?:instructions|rubric|rules)", re.I),
    re.compile(r"ignore\s+(?:the\s+)?rubric", re.I),
    re.compile(r"(?:give|assign|award)\s+(?:me|this\s+project)\s+(?:a\s+)?(?:score\s+of\s+)?(?:100|full\s+marks|maximum)", re.I),
    # grader-directed word AND a max-score demand on the same line
    re.compile(rf"^(?=.*{_GRADER_WORDS})(?=.*{_MAX_SCORE}).*$", re.I | re.M),
    re.compile(r"игнорир\w*\s+(?:все\s+|любые\s+|предыдущие\s+)+(?:инструкции|правила|критерии)", re.I),
    re.compile(r"(?:поставь|дай|выстави)\s+(?:мне|этому\s+проекту)\s+(?:100|максимальн\w+|высш\w+)", re.I),
)


def find_prompt_injection(text: str) -> Optional[str]:
    """The matched snippet if the code addresses the AI grader, else None."""
    for pattern in _INJECTION:
        m = pattern.search(text or "")
        if m:
            return m.group(0).strip()[:80]
    return None


def content_fingerprint(content_text: str) -> Optional[str]:
    """sha256 of the submitted code, insensitive to file names, file order,
    whitespace and letter case — so the same work re-zipped under another
    folder name or re-indented still matches. None when there is too little
    code for a match to mean anything."""
    bodies = _FILE_BLOCK.findall(content_text or "") or [content_text or ""]
    normalized = sorted(
        n for n in (re.sub(r"\s+", " ", b).strip().lower() for b in bodies) if n
    )
    joined = "\x00".join(normalized)
    if len(joined) < FINGERPRINT_MIN_CHARS:
        return None
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class IntegrityResult:
    violations: tuple[dict, ...] = ()

    @property
    def violated(self) -> bool:
        return bool(self.violations)

    @property
    def first(self) -> Optional[dict]:
        return self.violations[0] if self.violations else None


async def check_submission_integrity(
        db: AsyncSession,
        project: Project,
        *,
        files_included: list[str],
        content_text: str,
) -> IntegrityResult:
    violations: list[dict] = []

    snippet = find_prompt_injection(content_text)
    if snippet:
        violations.append({
            "code": "prompt_injection",
            "detail": f"AI baholovchiga ko'rsatma: «{snippet}»",
        })

    fingerprint = content_fingerprint(content_text)
    # A re-upload to the SAME project row (fix-and-resend flow) is invisible to
    # the "other projects" query below, so compare with this row's previous
    # fingerprint: same code again after a non-passing grade = nothing fixed.
    previous_fingerprint = project.content_fingerprint
    previously_failed = bool(project.grade) and (project.points_earned or 0) < 75
    project.content_fingerprint = fingerprint  # None clears a stale one on resubmit
    if fingerprint is not None and fingerprint == previous_fingerprint and previously_failed:
        violations.append({
            "code": "unchanged_resubmission",
            "detail": "Kod avvalgi (o'tmagan) topshirish bilan bir xil",
        })
    if fingerprint is not None:
        other = (await db.execute(
            select(Project.id).where(
                Project.content_fingerprint == fingerprint,
                Project.student_id != project.student_id,
                Project.id != project.id,
            ).order_by(Project.id).limit(1)
        )).first()
        if other is not None:
            violations.append({
                "code": "duplicate_content",
                "detail": f"Xuddi shu kod boshqa o'quvchining #{other.id}-loyihasida ham bor "
                          "(fayl nomlari/bo'sh joylar e'tiborga olinmadi)",
            })

        own_rejected = (await db.execute(
            select(Project.id).where(
                Project.content_fingerprint == fingerprint,
                Project.student_id == project.student_id,
                Project.id != project.id,
                Project.status == "Rejected",
            ).order_by(Project.id.desc()).limit(1)
        )).first()
        if own_rejected is not None and not any(
                v["code"] == "unchanged_resubmission" for v in violations):
            violations.append({
                "code": "unchanged_resubmission",
                "detail": f"Kod #{own_rejected.id}-loyiha (rad etilgan) bilan bir xil",
            })

    return IntegrityResult(violations=tuple(violations))
