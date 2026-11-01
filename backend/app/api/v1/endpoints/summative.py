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
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import rate_limit
from app.dependencies import get_current_instructor, get_current_student, get_db
from app.models.group import Group, student_groups
from app.models.lesson import Lesson, LessonCompletion, LessonVocabulary
from app.models.lesson_question import LessonQuestion
from app.models.quiz import Question, Quiz
from app.models.summative import SummativeAttempt, SummativeSet
from app.models.user import Student
from app.services.ranking_service import RankingService
from app.utils.datetime_utils import utcnow

router = APIRouter()

TEST_QUESTIONS = 30         # every test has 30 questions (fewer only if the student has fewer to draw from)
# SMALL_TEST, BIG_TEST = 25, 50   (disabled: fixed 30 now)
# BIG_TEST_MIN_LESSONS = 20
RETAKE_PENALTY_PCT = 30     # every attempt after the first costs this % of the student's points
MAX_HINTS = 3               # 💡 per test
MIN_QUESTIONS = 10          # below this a "summative" isn't meaningful
TEST_SECONDS = 30 * 60      # fixed 30 minutes
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

# DISABLED — school-quarter filter (used by teacher-built tests)
# # School quarters (month ranges, inclusive): the academic year starts 1 September.
# _QUARTER_MONTHS = {1: (9, 10), 2: (11, 12), 3: (1, 3), 4: (4, 5)}
#
#
# def _quarter_range(quarter: int, anchor: datetime):
#     """[start, end) of a school quarter in the academic year `anchor` falls in."""
#     if quarter not in _QUARTER_MONTHS:
#         return None
#     year = anchor.year if anchor.month >= 9 else anchor.year - 1  # academic year's September
#     m1, m2 = _QUARTER_MONTHS[quarter]
#     y1 = year if m1 >= 9 else year + 1
#     y2 = year if m2 >= 9 else year + 1
#     start = datetime(y1, m1, 1, tzinfo=timezone.utc)
#     end = datetime(y2 + (1 if m2 == 12 else 0), 1 if m2 == 12 else m2 + 1, 1, tzinfo=timezone.utc)
#     return start, end
#
#
# async def _completed_lessons(db: AsyncSession, student_id: int, tset: Optional[SummativeSet] = None) -> List[int]:
#     """Lessons finished in the test's period: the teacher's chosen school
#     quarter, or (no set / quarter 0) the last ~3 months."""
#     rng = _quarter_range(tset.quarter, tset.created_at) if tset is not None and tset.quarter else None
#     stmt = select(LessonCompletion.lesson_id).where(LessonCompletion.student_id == student_id)
#     if rng:
#         stmt = stmt.where(LessonCompletion.completed_at >= rng[0], LessonCompletion.completed_at < rng[1])
#     else:
#         stmt = stmt.where(LessonCompletion.completed_at >= utcnow() - timedelta(days=QUARTER_DAYS))
#     return list((await db.execute(stmt)).scalars().all())
#
#
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
    # Always TEST_QUESTIONS (30) — fewer only if the student's pool is smaller.
    # (Old rule, 25 or 50 by finished lessons: want = BIG_TEST if lessons >= BIG_TEST_MIN_LESSONS else SMALL_TEST)
    return min(TEST_QUESTIONS, questions)

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


# DISABLED — teacher-made sets helpers
# # ── teacher-made sets (student side) ────────────────────────────────────────
#
# async def _active_set(db: AsyncSession, student: Student) -> Optional[SummativeSet]:
#     """The newest active set assigned to any group the student is in."""
#     group_ids = list((await db.execute(
#         select(student_groups.c.group_id).where(student_groups.c.student_id == student.id)
#     )).scalars().all())
#     if not group_ids:
#         return None
#     return (await db.execute(
#         select(SummativeSet).where(SummativeSet.group_id.in_(group_ids), SummativeSet.is_active.is_(True))
#         .order_by(SummativeSet.id.desc()).limit(1)
#     )).scalar_one_or_none()
#
#
# async def _set_attempt(db: AsyncSession, set_id: int, student_id: int) -> Optional[SummativeAttempt]:
#     return (await db.execute(
#         select(SummativeAttempt).where(SummativeAttempt.set_id == set_id, SummativeAttempt.student_id == student_id)
#         .order_by(SummativeAttempt.id.desc()).limit(1)
#     )).scalar_one_or_none()
#
#
# def _set_count(tset: SummativeSet) -> int:
#     return tset.question_count or len(tset.question_ids or []) or 25
#
#
async def _attempt_count(db: AsyncSession, student_id: int) -> int:
    return (await db.execute(
        select(func.count(SummativeAttempt.id)).where(SummativeAttempt.student_id == student_id)
    )).scalar() or 0


def _penalty_for(student: Student, previous_attempts: int) -> int:
    """30% of the points the student has now, from the second attempt on."""
    if previous_attempts <= 0:
        return 0
    return int((student.total_points or 0) * RETAKE_PENALTY_PCT / 100)


# ── endpoints ───────────────────────────────────────────────────────────────

@router.get("/available")
async def available(
        lang: str = "uz",
        db: AsyncSession = Depends(get_db),
        student: Student = Depends(get_current_student),
):
# DISABLED — teacher-set branch of available()
#     tset = await _active_set(db, student)
#     if tset:
#         att = await _set_attempt(db, tset.id, student.id)
#         if att:
#             await _expire_if_late(db, att)
#         lessons = await _completed_lessons(db, student.id, tset)
#         pool = await _build_pool(db, lessons, "ru" if lang == "ru" else "uz")
#         planned = min(_set_count(tset), len(pool))
#         return {
#             "teacher_set": {
#                 "id": tset.id, "title": tset.title, "count": planned, "minutes": tset.minutes,
#                 "done": bool(att and att.status == "finished"),
#                 "score": att.score if att and att.status == "finished" else None,
#             },
#             "lessons": len(lessons), "questions": len(pool), "planned": planned,
#             "minutes": tset.minutes, "min_questions": 1,
#             "in_progress": att.id if att and att.status == "in_progress" else None,
#         }
#
    lessons = await _completed_lessons(db, student.id)
    pool = await _build_pool(db, lessons, "ru" if lang == "ru" else "uz")
    last = (await db.execute(
        select(SummativeAttempt).where(SummativeAttempt.student_id == student.id)
        .order_by(SummativeAttempt.id.desc()).limit(1)
    )).scalar_one_or_none()
    if last:
        await _expire_if_late(db, last)
    prev = await _attempt_count(db, student.id)
    resuming = bool(last and last.status == "in_progress")
    return {
        "lessons": len(lessons), "questions": len(pool), "planned": _plan_count(len(lessons), len(pool)),
        "minutes": TEST_SECONDS // 60, "min_questions": MIN_QUESTIONS,
        "in_progress": last.id if resuming else None,
        # 2nd+ attempt: costs a share of the student's points (not charged when resuming)
        "retake": prev > 0 and not resuming, "penalty_pct": RETAKE_PENALTY_PCT,
        "penalty": _penalty_for(student, prev) if not resuming else 0,
        "points": student.total_points or 0, "max_hints": MAX_HINTS,
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

# DISABLED — teacher-set branch of start()
#     tset = await _active_set(db, student)
#     if tset:
#         if await _set_attempt(db, tset.id, student.id):
#             raise HTTPException(status_code=409, detail="Siz bu testni allaqachon topshirgansiz")
#         lessons = await _completed_lessons(db, student.id, tset)
#         pool = await _build_pool(db, lessons, lang)
#         if not pool:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Test uchun savol topilmadi. Shu chorakda tugatgan darslaringiz yo'q.",
#             )
#         chosen = _place_answers(_pick_balanced(pool, min(_set_count(tset), len(pool))))
#         att = SummativeAttempt(
#             student_id=student.id, scope="teacher", lang=lang, total=len(chosen), questions=chosen,
#             time_limit_seconds=tset.minutes * 60, set_id=tset.id,
#         )
#         db.add(att)
#         await db.commit()
#         await db.refresh(att)
#         return _start_payload(att)
#
    lessons = await _completed_lessons(db, student.id)
    pool = await _build_pool(db, lessons, lang)
    if len(pool) < MIN_QUESTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Test uchun savol yetarli emas ({len(pool)} ta). Avval ko'proq dars tugating.",
        )
    chosen = _place_answers(_pick_balanced(pool, _plan_count(len(lessons), len(pool))))
    penalty = _penalty_for(student, await _attempt_count(db, student.id))
    att = SummativeAttempt(
        student_id=student.id, scope="quarter", lang=lang, total=len(chosen), questions=chosen,
        time_limit_seconds=TEST_SECONDS,
    )
    db.add(att)
    await db.commit()
    await db.refresh(att)
    if penalty > 0:
        # Retake: the points are taken once, at the moment the new test is created
        # (resuming it later doesn't charge again).
        await RankingService(db).revoke_earned_points(student.id, penalty)
    return _start_payload(att, penalty)


def _start_payload(att: SummativeAttempt, penalty: int = 0) -> dict:
    remaining = max(0, int((_deadline(att) - utcnow()).total_seconds()))
    hinted = [i for i, q in enumerate(att.questions) if q.get("hint")]
    return {
        "id": att.id, "total": att.total, "remaining_seconds": remaining,
        "violations": att.violations, "max_violations": MAX_VIOLATIONS,
        "questions": _public_questions(att),
        "answers": att.answers, "hinted": hinted, "hints_left": MAX_HINTS - len(hinted),
        "penalty": penalty,
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


class HintBody(BaseModel):
    q: int


@router.post("/{attempt_id}/hint")
async def use_hint(
        attempt_id: int,
        body: HintBody,
        db: AsyncSession = Depends(get_db),
        student: Student = Depends(get_current_student),
):
    """💡 The server picks the answer for this question (the client then selects
    it). Three per test; asking again about the same question is free."""
    att = await _mine(db, attempt_id, student)
    if att.status != "in_progress":
        raise HTTPException(status_code=409, detail="Test tugagan")
    if not 0 <= body.q < len(att.questions):
        raise HTTPException(status_code=422, detail="Savol topilmadi")
    questions = [dict(q) for q in att.questions]
    used = sum(1 for q in questions if q.get("hint"))
    if not questions[body.q].get("hint"):
        if used >= MAX_HINTS:
            raise HTTPException(status_code=409, detail="Yordam tugagan")
        questions[body.q]["hint"] = True
        att.questions = questions  # reassign so the JSON column is flagged dirty
        used += 1
        await db.commit()
    return {"correct": att.questions[body.q]["correct"], "hints_left": MAX_HINTS - used}


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


# DISABLED — teacher-built tests (re-enable by removing the leading "# ")
# # ── teacher: build and manage sets ──────────────────────────────────────────
# # Registered after the student routes; none of these paths collide with
# # "/{attempt_id}" (they all have a second segment).
#
# class SetBody(BaseModel):
#     group_ids: List[int]
#     title: str = ""
#     question_count: int = 25
#     quarter: int = 0
#     minutes: int = 30
#
#
# async def _own_group(db: AsyncSession, group_id: int, teacher: Student) -> Group:
#     g = (await db.execute(select(Group).where(Group.id == group_id))).scalar_one_or_none()
#     if g is None or g.teacher_id != teacher.id:
#         raise HTTPException(status_code=403, detail="Bu guruh sizga tegishli emas")
#     return g
#
#
# @router.get("/teacher/groups")
# async def teacher_groups(
#         db: AsyncSession = Depends(get_db),
#         teacher: Student = Depends(get_current_instructor),
# ):
#     rows = (await db.execute(
#         select(Group.id, Group.name, func.count(student_groups.c.student_id))
#         .outerjoin(student_groups, student_groups.c.group_id == Group.id)
#         .where(Group.teacher_id == teacher.id).group_by(Group.id, Group.name).order_by(Group.name)
#     )).all()
#     return [{"id": i, "name": n, "students": c} for i, n, c in rows]
#
#
# @router.post("/teacher/sets")
# async def create_set(
#         body: SetBody,
#         db: AsyncSession = Depends(get_db),
#         teacher: Student = Depends(get_current_instructor),
# ):
#     group_ids = list(dict.fromkeys(body.group_ids))
#     if not group_ids:
#         raise HTTPException(status_code=422, detail="Kamida bitta sinfni tanlang")
#     for gid in group_ids:
#         await _own_group(db, gid, teacher)
#     if not 1 <= body.question_count <= 100:
#         raise HTTPException(status_code=422, detail="Savollar soni 1 dan 100 gacha bo'lishi kerak")
#     if not 5 <= body.minutes <= 180:
#         raise HTTPException(status_code=422, detail="Vaqt 5 dan 180 daqiqagacha bo'lishi kerak")
#     if body.quarter not in (0, 1, 2, 3, 4):
#         raise HTTPException(status_code=422, detail="Chorak 1-4 bo'lishi kerak")
#     # One live test per group: a new one replaces the previous.
#     for old in (await db.execute(
#         select(SummativeSet).where(SummativeSet.group_id.in_(group_ids), SummativeSet.is_active.is_(True))
#     )).scalars().all():
#         old.is_active = False
#     title = body.title.strip()[:200] or "Summativ test"
#     for gid in group_ids:
#         db.add(SummativeSet(
#             teacher_id=teacher.id, group_id=gid, title=title, question_count=body.question_count,
#             quarter=body.quarter, minutes=body.minutes,
#         ))
#     await db.commit()
#     return {"created": len(group_ids), "count": body.question_count}
#
#
# @router.get("/teacher/sets")
# async def list_sets(
#         db: AsyncSession = Depends(get_db),
#         teacher: Student = Depends(get_current_instructor),
# ):
#     rows = (await db.execute(
#         select(SummativeSet, Group.name).join(Group, Group.id == SummativeSet.group_id)
#         .where(SummativeSet.teacher_id == teacher.id).order_by(SummativeSet.id.desc()).limit(50)
#     )).all()
#     out = []
#     for st, gname in rows:
#         stats = (await db.execute(
#             select(func.count(SummativeAttempt.id), func.avg(SummativeAttempt.score)).where(
#                 SummativeAttempt.set_id == st.id, SummativeAttempt.status == "finished")
#         )).one()
#         members = (await db.execute(
#             select(func.count(student_groups.c.student_id)).where(student_groups.c.group_id == st.group_id)
#         )).scalar() or 0
#         out.append({
#             "id": st.id, "title": st.title, "group_id": st.group_id, "group": gname, "count": _set_count(st),
#             "minutes": st.minutes, "quarter": st.quarter, "is_active": st.is_active, "created_at": st.created_at,
#             "finished": stats[0] or 0, "average": round(float(stats[1])) if stats[1] is not None else None,
#             "students": members,
#         })
#     return out
#
#
# class ActiveBody(BaseModel):
#     is_active: bool
#
#
# async def _own_set(db: AsyncSession, set_id: int, teacher: Student) -> SummativeSet:
#     st = (await db.execute(select(SummativeSet).where(SummativeSet.id == set_id))).scalar_one_or_none()
#     if st is None or st.teacher_id != teacher.id:
#         raise HTTPException(status_code=404, detail="Test topilmadi")
#     return st
#
#
# @router.patch("/teacher/sets/{set_id}")
# async def toggle_set(
#         set_id: int,
#         body: ActiveBody,
#         db: AsyncSession = Depends(get_db),
#         teacher: Student = Depends(get_current_instructor),
# ):
#     st = await _own_set(db, set_id, teacher)
#     if body.is_active:  # one live test per group
#         for other in (await db.execute(
#             select(SummativeSet).where(SummativeSet.group_id == st.group_id, SummativeSet.is_active.is_(True),
#                                        SummativeSet.id != st.id)
#         )).scalars().all():
#             other.is_active = False
#     st.is_active = body.is_active
#     await db.commit()
#     return {"ok": True}
#
#
# @router.delete("/teacher/sets/{set_id}")
# async def delete_set(
#         set_id: int,
#         db: AsyncSession = Depends(get_db),
#         teacher: Student = Depends(get_current_instructor),
# ):
#     st = await _own_set(db, set_id, teacher)
#     await db.delete(st)
#     await db.commit()
#     return {"ok": True}
#
#
# @router.get("/teacher/sets/{set_id}/results")
# async def set_results(
#         set_id: int,
#         db: AsyncSession = Depends(get_db),
#         teacher: Student = Depends(get_current_instructor),
# ):
#     st = await _own_set(db, set_id, teacher)
#     students = (await db.execute(
#         select(Student.id, Student.full_name, Student.username)
#         .join(student_groups, student_groups.c.student_id == Student.id)
#         .where(student_groups.c.group_id == st.group_id).order_by(Student.full_name)
#     )).all()
#     atts = {a.student_id: a for a in (await db.execute(
#         select(SummativeAttempt).where(SummativeAttempt.set_id == st.id).order_by(SummativeAttempt.id)
#     )).scalars().all()}
#     for a in atts.values():
#         await _expire_if_late(db, a)
#     return {
#         "title": st.title, "count": _set_count(st),
#         "students": [
#             {
#                 "id": sid, "name": full or uname,
#                 "status": atts[sid].status if sid in atts else "not_started",
#                 "score": atts[sid].score if sid in atts and atts[sid].status == "finished" else None,
#                 "correct": atts[sid].correct if sid in atts else None,
#                 "total": atts[sid].total if sid in atts else _set_count(st),
#                 "violations": atts[sid].violations if sid in atts else 0,
#                 "finish_reason": atts[sid].finish_reason if sid in atts else None,
#             }
#             for sid, full, uname in students
#         ],
#     }
#