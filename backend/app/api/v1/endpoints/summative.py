"""End-of-quarter "summative" test built from the lessons a student finished.

Flow: GET /available (how big a test can I get?) -> POST /start (server picks
the questions, shuffles every question's options and balances where the
correct answer lands, stores it all) -> client plays it fullscreen ->
POST /{id}/violation each time the student leaves fullscreen / the tab ->
POST /{id}/submit (graded here). The correct answers never leave the server
until the attempt is finished.

Question sources, all limited to lessons the student has COMPLETED:
  1. LessonQuestion bank (quiz kind) — the main source, in the student's language
  2. LessonVocabulary — "which term matches this definition?"
  3. Quiz/Question rows of the courses those lessons belong to
"""
import random
import re
from datetime import timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import rate_limit
from app.dependencies import get_current_student, get_db
from app.models.lesson import Lesson, LessonCompletion, LessonVocabulary
from app.models.lesson_question import LessonQuestion
from app.models.quiz import Question, Quiz
from app.models.summative import SummativeAttempt
from app.models.user import Student
from app.utils.datetime_utils import utcnow

router = APIRouter()

SMALL_TEST, BIG_TEST = 25, 50
BIG_TEST_MIN_LESSONS = 20   # a quarter with this many finished lessons gets the 50-question test
MIN_QUESTIONS = 10          # below this a "summative" isn't meaningful
TEST_SECONDS = 30 * 60      # fixed 30 minutes, whether it has 25 or 50 questions
GRACE_SECONDS = 20          # network slack on the deadline
MAX_VIOLATIONS = 3          # leaving fullscreen/the tab this often ends the test
QUARTER_DAYS = 92
VOCAB_MAX_SHARE = 0.3

_CYR = re.compile(r"[А-Яа-яЁё]")


def _lang_of(text: str) -> str:
    return "ru" if _CYR.search(text or "") else "uz"


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


# ── question pool ───────────────────────────────────────────────────────────

async def _completed_lessons(db: AsyncSession, student_id: int) -> List[int]:
    """Lessons finished in the current quarter (the last ~3 months)."""
    stmt = select(LessonCompletion.lesson_id).where(
        LessonCompletion.student_id == student_id,
        LessonCompletion.completed_at >= utcnow() - timedelta(days=QUARTER_DAYS),
    )
    return list((await db.execute(stmt)).scalars().all())


async def _build_pool(db: AsyncSession, lesson_ids: List[int], lang: str) -> List[dict]:
    """Raw questions {text, options, correct(index), kind, explanation} with
    the answer still in its ORIGINAL position (shuffled later)."""
    if not lesson_ids:
        return []
    pool: List[dict] = []
    seen = set()

    def add(text, options, correct, kind, explanation=None, lesson_id=None):
        key = _norm(text)
        options = [str(o) for o in options if o is not None and str(o).strip()]
        if (
            not key or key in seen or correct is None or not (0 <= correct < len(options))
            or len(options) < 2 or len(set(map(_norm, options))) != len(options)
        ):
            return
        seen.add(key)
        pool.append({"text": text, "options": options, "correct": correct, "kind": kind,
                     "explanation": explanation, "lesson_id": lesson_id})

    # 1) lesson question bank — uz and ru rows are paired translations, so use
    #    the student's language and only fall back to the other if none exist.
    bank = (await db.execute(
        select(LessonQuestion).where(
            LessonQuestion.lesson_id.in_(lesson_ids), LessonQuestion.question_kind == "quiz",
        )
    )).scalars().all()
    mine = [q for q in bank if _lang_of(q.question_text) == lang]
    for q in (mine or bank):
        if q.options:
            add(q.question_text, q.options, q.correct_option, "bank", lesson_id=q.lesson_id)

    # 2) course quizzes of the courses these lessons belong to
    course_ids = list((await db.execute(
        select(Lesson.course_id).where(Lesson.id.in_(lesson_ids)).distinct()
    )).scalars().all())
    if course_ids:
        rows = (await db.execute(
            select(Question).join(Quiz, Quiz.id == Question.quiz_id)
            .where(Quiz.course_id.in_(course_ids), Quiz.is_active.is_(True))
        )).scalars().all()
        for r in rows:
            opts = [r.option_a, r.option_b, r.option_c, r.option_d]
            letters = ["A", "B", "C", "D"]
            kept = [(letters[i], o) for i, o in enumerate(opts) if o and str(o).strip()]
            labels = [k for k, _ in kept]
            if r.correct_answer in labels:
                add(r.text, [o for _, o in kept], labels.index(r.correct_answer), "quiz", r.explanation)

    # 3) vocabulary: definition -> term (distractors are other finished terms)
    vocab = (await db.execute(
        select(LessonVocabulary).where(LessonVocabulary.lesson_id.in_(lesson_ids))
    )).scalars().all()
    words = list({v.word for v in vocab})
    if len(words) >= 4:
        vocab_qs = []
        for v in vocab:
            others = [w for w in words if _norm(w) != _norm(v.word)]
            if len(others) < 3:
                continue
            opts = [v.word] + random.sample(others, 3)
            vocab_qs.append((v.definition, opts, 0, v.lesson_id))
        random.shuffle(vocab_qs)
        cap = max(0, int((len(pool) + len(vocab_qs)) * VOCAB_MAX_SHARE))
        for text, opts, correct, lid in vocab_qs[:cap if pool else len(vocab_qs)]:
            add(text, opts, correct, "vocab", lesson_id=lid)
    return pool


def _pick_balanced(pool: List[dict], count: int) -> List[dict]:
    """Take `count` questions spread evenly over the finished lessons (round
    robin), so every lesson of the quarter is represented instead of a few
    lessons with big question banks crowding the rest out."""
    groups = {}
    for q in pool:
        groups.setdefault(q.get("lesson_id"), []).append(q)
    buckets = list(groups.values())
    for b in buckets:
        random.shuffle(b)
    random.shuffle(buckets)
    picked: List[dict] = []
    while len(picked) < count and any(buckets):
        for b in buckets:
            if b and len(picked) < count:
                picked.append(b.pop())
    return picked


def _plan_count(lessons: int, questions: int) -> int:
    want = BIG_TEST if lessons >= BIG_TEST_MIN_LESSONS else SMALL_TEST
    return min(want, questions)


def _place_answers(questions: List[dict]) -> List[dict]:
    """Shuffle every question's options and spread the correct answer evenly
    across A/B/C/D, so it never clusters on one letter (e.g. always "B").
    Each question gets a target slot from a shuffled round-robin; the rest of
    the options fill the other slots in random order. True/false style
    2-option questions use slots 0-1 only."""
    slots_by_len = {}
    out = []
    for q in questions:
        n = len(q["options"])
        bucket = slots_by_len.setdefault(n, [])
        if not bucket:
            bucket.extend(random.sample(range(n), n))
        target = bucket.pop()
        correct_opt = q["options"][q["correct"]]
        rest = [o for i, o in enumerate(q["options"]) if i != q["correct"]]
        random.shuffle(rest)
        options = rest[:target] + [correct_opt] + rest[target:]
        out.append({**q, "options": options, "correct": target})
    random.shuffle(out)
    return out


# ── helpers ─────────────────────────────────────────────────────────────────

def _public_questions(att: SummativeAttempt) -> List[dict]:
    return [{"text": q["text"], "options": q["options"]} for q in att.questions]


def _deadline(att: SummativeAttempt):
    return att.started_at + timedelta(seconds=att.time_limit_seconds)


def _grade(att: SummativeAttempt, answers: Optional[List[Optional[int]]], reason: str) -> None:
    answers = list(answers or [])
    answers += [None] * (len(att.questions) - len(answers))
    answers = answers[: len(att.questions)]
    att.answers = [a if isinstance(a, int) and not isinstance(a, bool) else None for a in answers]
    att.correct = sum(1 for q, a in zip(att.questions, att.answers) if a == q["correct"])
    att.total = len(att.questions)
    att.score = round(100 * att.correct / att.total) if att.total else 0
    att.status = "finished"
    att.finish_reason = reason
    att.finished_at = utcnow()


def _summary(att: SummativeAttempt) -> dict:
    return {
        "id": att.id, "status": att.status, "finish_reason": att.finish_reason, "total": att.total,
        "correct": att.correct, "score": att.score, "violations": att.violations,
        "started_at": att.started_at, "finished_at": att.finished_at, "scope": att.scope,
        "time_limit_seconds": att.time_limit_seconds,
    }


def _review(att: SummativeAttempt) -> List[dict]:
    return [
        {"text": q["text"], "options": q["options"], "correct": q["correct"], "chosen": a,
         "explanation": q.get("explanation")}
        for q, a in zip(att.questions, att.answers or [None] * len(att.questions))
    ]


async def _mine(db: AsyncSession, attempt_id: int, student: Student) -> SummativeAttempt:
    att = (await db.execute(
        select(SummativeAttempt).where(SummativeAttempt.id == attempt_id, SummativeAttempt.student_id == student.id)
    )).scalar_one_or_none()
    if att is None:
        raise HTTPException(status_code=404, detail="Test topilmadi")
    return att


async def _expire_if_late(db: AsyncSession, att: SummativeAttempt) -> None:
    """An abandoned attempt past its deadline is graded as-is (unanswered = wrong)."""
    if att.status == "in_progress" and utcnow() > _deadline(att) + timedelta(seconds=GRACE_SECONDS):
        _grade(att, None, "time")
        await db.commit()


# ── endpoints ───────────────────────────────────────────────────────────────

@router.get("/available")
async def available(
        lang: str = "uz",
        db: AsyncSession = Depends(get_db),
        student: Student = Depends(get_current_student),
):
    lessons = await _completed_lessons(db, student.id)
    pool = await _build_pool(db, lessons, "ru" if lang == "ru" else "uz")
    last = (await db.execute(
        select(SummativeAttempt).where(SummativeAttempt.student_id == student.id)
        .order_by(SummativeAttempt.id.desc()).limit(1)
    )).scalar_one_or_none()
    if last:
        await _expire_if_late(db, last)
    return {
        "lessons": len(lessons), "questions": len(pool), "planned": _plan_count(len(lessons), len(pool)),
        "minutes": TEST_SECONDS // 60, "min_questions": MIN_QUESTIONS,
        "in_progress": last.id if last and last.status == "in_progress" else None,
    }


class StartBody(BaseModel):
    lang: str = "uz"


@router.post("/start")
async def start(
        body: StartBody,
        db: AsyncSession = Depends(get_db),
        student: Student = Depends(get_current_student),
        _rl: None = Depends(rate_limit(max_calls=6, window_seconds=60)),
):
    lang = "ru" if body.lang == "ru" else "uz"

    # Resume an unfinished attempt instead of letting a student re-roll
    # questions until they get an easy set.
    open_att = (await db.execute(
        select(SummativeAttempt).where(
            SummativeAttempt.student_id == student.id, SummativeAttempt.status == "in_progress")
        .order_by(SummativeAttempt.id.desc()).limit(1)
    )).scalar_one_or_none()
    if open_att:
        await _expire_if_late(db, open_att)
        if open_att.status == "in_progress":
            return _start_payload(open_att)

    lessons = await _completed_lessons(db, student.id)
    pool = await _build_pool(db, lessons, lang)
    if len(pool) < MIN_QUESTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Test uchun savol yetarli emas ({len(pool)} ta). Avval ko'proq dars tugating.",
        )
    chosen = _place_answers(_pick_balanced(pool, _plan_count(len(lessons), len(pool))))
    att = SummativeAttempt(
        student_id=student.id, scope="quarter", lang=lang, total=len(chosen), questions=chosen,
        time_limit_seconds=TEST_SECONDS,
    )
    db.add(att)
    await db.commit()
    await db.refresh(att)
    return _start_payload(att)


def _start_payload(att: SummativeAttempt) -> dict:
    remaining = max(0, int((_deadline(att) - utcnow()).total_seconds()))
    return {
        "id": att.id, "total": att.total, "remaining_seconds": remaining,
        "violations": att.violations, "max_violations": MAX_VIOLATIONS,
        "questions": _public_questions(att),
    }


@router.get("/history")
async def history(
        db: AsyncSession = Depends(get_db),
        student: Student = Depends(get_current_student),
):
    rows = (await db.execute(
        select(SummativeAttempt).where(SummativeAttempt.student_id == student.id)
        .order_by(SummativeAttempt.id.desc()).limit(20)
    )).scalars().all()
    for r in rows:
        await _expire_if_late(db, r)
    return [_summary(r) for r in rows]


@router.get("/{attempt_id}")
async def get_attempt(
        attempt_id: int,
        db: AsyncSession = Depends(get_db),
        student: Student = Depends(get_current_student),
):
    att = await _mine(db, attempt_id, student)
    await _expire_if_late(db, att)
    if att.status == "in_progress":
        return _start_payload(att)
    return {**_summary(att), "review": _review(att)}


class ViolationBody(BaseModel):
    reason: str = ""


@router.post("/{attempt_id}/violation")
async def violation(
        attempt_id: int,
        body: ViolationBody,
        db: AsyncSession = Depends(get_db),
        student: Student = Depends(get_current_student),
):
    att = await _mine(db, attempt_id, student)
    if att.status != "in_progress":
        return {"status": att.status, "violations": att.violations}
    att.violations += 1
    ended = att.violations >= MAX_VIOLATIONS
    if ended:
        # Too many exits: grade with what's been saved so far (see /answers).
        _grade(att, att.answers, "violations")
    await db.commit()
    return {"status": att.status, "violations": att.violations, "max_violations": MAX_VIOLATIONS}


class SaveBody(BaseModel):
    answers: List[Optional[int]]


@router.post("/{attempt_id}/save")
async def save_progress(
        attempt_id: int,
        body: SaveBody,
        db: AsyncSession = Depends(get_db),
        student: Student = Depends(get_current_student),
):
    """Autosave of the answers so far — used if the test is ended by the
    server (too many exits / time) before the student presses finish."""
    att = await _mine(db, attempt_id, student)
    if att.status == "in_progress":
        att.answers = body.answers[: len(att.questions)]
        await db.commit()
    return {"ok": True}


@router.post("/{attempt_id}/submit")
async def submit(
        attempt_id: int,
        body: SaveBody,
        db: AsyncSession = Depends(get_db),
        student: Student = Depends(get_current_student),
):
    att = await _mine(db, attempt_id, student)
    if att.status == "in_progress":
        late = utcnow() > _deadline(att) + timedelta(seconds=GRACE_SECONDS)
        # Past the deadline only what was autosaved counts.
        _grade(att, att.answers if late else body.answers, "time" if late else "submitted")
        await db.commit()
    return {**_summary(att), "review": _review(att)}
