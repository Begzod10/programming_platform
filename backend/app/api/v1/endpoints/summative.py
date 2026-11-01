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
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import rate_limit
from app.dependencies import get_current_instructor, get_current_student, get_db
from app.models.course import Course
from app.models.group import Group, student_groups
from app.models.lesson import Lesson, LessonCompletion, LessonVocabulary
from app.models.lesson_question import LessonQuestion
from app.models.quiz import Question, Quiz
from app.models.summative import SummativeAttempt, SummativeSet
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


# ── teacher-made sets (student side) ────────────────────────────────────────

async def _active_set(db: AsyncSession, student: Student) -> Optional[SummativeSet]:
    """The newest active set assigned to any group the student is in."""
    group_ids = list((await db.execute(
        select(student_groups.c.group_id).where(student_groups.c.student_id == student.id)
    )).scalars().all())
    if not group_ids:
        return None
    return (await db.execute(
        select(SummativeSet).where(SummativeSet.group_id.in_(group_ids), SummativeSet.is_active.is_(True))
        .order_by(SummativeSet.id.desc()).limit(1)
    )).scalar_one_or_none()


async def _set_attempt(db: AsyncSession, set_id: int, student_id: int) -> Optional[SummativeAttempt]:
    return (await db.execute(
        select(SummativeAttempt).where(SummativeAttempt.set_id == set_id, SummativeAttempt.student_id == student_id)
        .order_by(SummativeAttempt.id.desc()).limit(1)
    )).scalar_one_or_none()


async def _questions_from_set(db: AsyncSession, tset: SummativeSet, lang: str) -> List[dict]:
    """The teacher's questions as pool items. The bank stores a uz and a ru row
    per question; the teacher ticks one of them, and a student in the other
    language gets that question's twin (same lesson, same position)."""
    rows = {q.id: q for q in (await db.execute(
        select(LessonQuestion).where(LessonQuestion.id.in_(tset.question_ids))
    )).scalars().all()}
    lesson_ids = {q.lesson_id for q in rows.values()}
    siblings = (await db.execute(
        select(LessonQuestion).where(LessonQuestion.lesson_id.in_(lesson_ids), LessonQuestion.question_kind == "quiz")
    )).scalars().all()
    by_lesson_lang: dict = {}
    for q in siblings:
        by_lesson_lang.setdefault((q.lesson_id, _lang_of(q.question_text)), []).append(q)
    for lst in by_lesson_lang.values():
        lst.sort(key=lambda x: (x.order_index, x.id))

    out, seen = [], set()
    for qid in tset.question_ids:
        q = rows.get(qid)
        if q is None or not q.options or q.correct_option is None:
            continue
        own = _lang_of(q.question_text)
        if own != lang:
            mine = by_lesson_lang.get((q.lesson_id, own), [])
            theirs = by_lesson_lang.get((q.lesson_id, lang), [])
            if q in mine and len(mine) == len(theirs):
                q = theirs[mine.index(q)]
        if q.id in seen or not (0 <= q.correct_option < len(q.options)):
            continue
        seen.add(q.id)
        out.append({"text": q.question_text, "options": [str(o) for o in q.options], "correct": q.correct_option,
                    "kind": "teacher", "explanation": None, "lesson_id": q.lesson_id})
    return out


# ── endpoints ───────────────────────────────────────────────────────────────

@router.get("/available")
async def available(
        lang: str = "uz",
        db: AsyncSession = Depends(get_db),
        student: Student = Depends(get_current_student),
):
    tset = await _active_set(db, student)
    if tset:
        att = await _set_attempt(db, tset.id, student.id)
        if att:
            await _expire_if_late(db, att)
        return {
            "teacher_set": {
                "id": tset.id, "title": tset.title, "count": len(tset.question_ids), "minutes": tset.minutes,
                "done": bool(att and att.status == "finished"), "score": att.score if att and att.status == "finished" else None,
            },
            "lessons": 0, "questions": len(tset.question_ids), "planned": len(tset.question_ids),
            "minutes": tset.minutes, "min_questions": 1,
            "in_progress": att.id if att and att.status == "in_progress" else None,
        }

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

    tset = await _active_set(db, student)
    if tset:
        if await _set_attempt(db, tset.id, student.id):
            raise HTTPException(status_code=409, detail="Siz bu testni allaqachon topshirgansiz")
        chosen = _place_answers(await _questions_from_set(db, tset, lang))
        if not chosen:
            raise HTTPException(status_code=400, detail="Testda savol topilmadi")
        att = SummativeAttempt(
            student_id=student.id, scope="teacher", lang=lang, total=len(chosen), questions=chosen,
            time_limit_seconds=tset.minutes * 60, set_id=tset.id,
        )
        db.add(att)
        await db.commit()
        await db.refresh(att)
        return _start_payload(att)

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


# ── teacher: build and manage sets ──────────────────────────────────────────
# Registered after the student routes; none of these paths collide with
# "/{attempt_id}" (they all have a second segment).

class SetBody(BaseModel):
    group_id: int
    title: str
    question_ids: List[int]
    minutes: int = 30


async def _own_group(db: AsyncSession, group_id: int, teacher: Student) -> Group:
    g = (await db.execute(select(Group).where(Group.id == group_id))).scalar_one_or_none()
    if g is None or g.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="Bu guruh sizga tegishli emas")
    return g


@router.get("/teacher/groups")
async def teacher_groups(
        db: AsyncSession = Depends(get_db),
        teacher: Student = Depends(get_current_instructor),
):
    rows = (await db.execute(
        select(Group.id, Group.name, func.count(student_groups.c.student_id))
        .outerjoin(student_groups, student_groups.c.group_id == Group.id)
        .where(Group.teacher_id == teacher.id).group_by(Group.id, Group.name).order_by(Group.name)
    )).all()
    return [{"id": i, "name": n, "students": c} for i, n, c in rows]


@router.get("/teacher/courses")
async def teacher_courses(
        db: AsyncSession = Depends(get_db),
        teacher: Student = Depends(get_current_instructor),
):
    """Courses that have a question bank to pick from."""
    rows = (await db.execute(
        select(Course.id, Course.title, func.count(LessonQuestion.id))
        .join(Lesson, Lesson.course_id == Course.id).join(LessonQuestion, LessonQuestion.lesson_id == Lesson.id)
        .where(LessonQuestion.question_kind == "quiz").group_by(Course.id, Course.title).order_by(Course.title)
    )).all()
    return [{"id": i, "title": t, "questions": c} for i, t, c in rows]


@router.get("/teacher/questions")
async def teacher_questions(
        course_id: int,
        lang: str = "uz",
        db: AsyncSession = Depends(get_db),
        teacher: Student = Depends(get_current_instructor),
):
    """Quiz questions of a course, grouped by lesson. Only one language is
    listed (every question exists as a uz and a ru twin; the student gets
    the twin in their own language)."""
    lang = "ru" if lang == "ru" else "uz"
    lessons = (await db.execute(
        select(Lesson).where(Lesson.course_id == course_id).order_by(Lesson.order, Lesson.id)
    )).scalars().all()
    qs = (await db.execute(
        select(LessonQuestion).where(
            LessonQuestion.lesson_id.in_([l.id for l in lessons]), LessonQuestion.question_kind == "quiz")
        .order_by(LessonQuestion.lesson_id, LessonQuestion.order_index, LessonQuestion.id)
    )).scalars().all() if lessons else []
    out = []
    for l in lessons:
        mine = [q for q in qs if q.lesson_id == l.id and q.options]
        pick = [q for q in mine if _lang_of(q.question_text) == lang] or mine
        if pick:
            out.append({
                "lesson_id": l.id, "title": l.title,
                "questions": [
                    {"id": q.id, "text": q.question_text, "options": q.options, "correct": q.correct_option}
                    for q in pick
                ],
            })
    return out


@router.post("/teacher/sets")
async def create_set(
        body: SetBody,
        db: AsyncSession = Depends(get_db),
        teacher: Student = Depends(get_current_instructor),
):
    await _own_group(db, body.group_id, teacher)
    ids = list(dict.fromkeys(body.question_ids))
    if not ids:
        raise HTTPException(status_code=422, detail="Kamida bitta savol tanlang")
    if len(ids) > 200:
        raise HTTPException(status_code=422, detail="Bitta testda 200 tadan ko'p savol bo'lmaydi")
    if not 5 <= body.minutes <= 180:
        raise HTTPException(status_code=422, detail="Vaqt 5 dan 180 daqiqagacha bo'lishi kerak")
    found = set((await db.execute(
        select(LessonQuestion.id).where(LessonQuestion.id.in_(ids), LessonQuestion.question_kind == "quiz")
    )).scalars().all())
    ids = [i for i in ids if i in found]
    if not ids:
        raise HTTPException(status_code=422, detail="Tanlangan savollar topilmadi")
    # One live test per group: a new one replaces the previous.
    for old in (await db.execute(
        select(SummativeSet).where(SummativeSet.group_id == body.group_id, SummativeSet.is_active.is_(True))
    )).scalars().all():
        old.is_active = False
    new = SummativeSet(
        teacher_id=teacher.id, group_id=body.group_id, title=body.title.strip()[:200] or "Summativ test",
        question_ids=ids, minutes=body.minutes,
    )
    db.add(new)
    await db.commit()
    await db.refresh(new)
    return {"id": new.id, "count": len(ids)}


@router.get("/teacher/sets")
async def list_sets(
        db: AsyncSession = Depends(get_db),
        teacher: Student = Depends(get_current_instructor),
):
    rows = (await db.execute(
        select(SummativeSet, Group.name).join(Group, Group.id == SummativeSet.group_id)
        .where(SummativeSet.teacher_id == teacher.id).order_by(SummativeSet.id.desc()).limit(50)
    )).all()
    out = []
    for st, gname in rows:
        stats = (await db.execute(
            select(func.count(SummativeAttempt.id), func.avg(SummativeAttempt.score)).where(
                SummativeAttempt.set_id == st.id, SummativeAttempt.status == "finished")
        )).one()
        members = (await db.execute(
            select(func.count(student_groups.c.student_id)).where(student_groups.c.group_id == st.group_id)
        )).scalar() or 0
        out.append({
            "id": st.id, "title": st.title, "group_id": st.group_id, "group": gname, "count": len(st.question_ids),
            "minutes": st.minutes, "is_active": st.is_active, "created_at": st.created_at,
            "finished": stats[0] or 0, "average": round(float(stats[1])) if stats[1] is not None else None,
            "students": members,
        })
    return out


class ActiveBody(BaseModel):
    is_active: bool


async def _own_set(db: AsyncSession, set_id: int, teacher: Student) -> SummativeSet:
    st = (await db.execute(select(SummativeSet).where(SummativeSet.id == set_id))).scalar_one_or_none()
    if st is None or st.teacher_id != teacher.id:
        raise HTTPException(status_code=404, detail="Test topilmadi")
    return st


@router.patch("/teacher/sets/{set_id}")
async def toggle_set(
        set_id: int,
        body: ActiveBody,
        db: AsyncSession = Depends(get_db),
        teacher: Student = Depends(get_current_instructor),
):
    st = await _own_set(db, set_id, teacher)
    if body.is_active:  # one live test per group
        for other in (await db.execute(
            select(SummativeSet).where(SummativeSet.group_id == st.group_id, SummativeSet.is_active.is_(True),
                                       SummativeSet.id != st.id)
        )).scalars().all():
            other.is_active = False
    st.is_active = body.is_active
    await db.commit()
    return {"ok": True}


@router.delete("/teacher/sets/{set_id}")
async def delete_set(
        set_id: int,
        db: AsyncSession = Depends(get_db),
        teacher: Student = Depends(get_current_instructor),
):
    st = await _own_set(db, set_id, teacher)
    await db.delete(st)
    await db.commit()
    return {"ok": True}


@router.get("/teacher/sets/{set_id}/results")
async def set_results(
        set_id: int,
        db: AsyncSession = Depends(get_db),
        teacher: Student = Depends(get_current_instructor),
):
    st = await _own_set(db, set_id, teacher)
    students = (await db.execute(
        select(Student.id, Student.full_name, Student.username)
        .join(student_groups, student_groups.c.student_id == Student.id)
        .where(student_groups.c.group_id == st.group_id).order_by(Student.full_name)
    )).all()
    atts = {a.student_id: a for a in (await db.execute(
        select(SummativeAttempt).where(SummativeAttempt.set_id == st.id).order_by(SummativeAttempt.id)
    )).scalars().all()}
    for a in atts.values():
        await _expire_if_late(db, a)
    return {
        "title": st.title, "count": len(st.question_ids),
        "students": [
            {
                "id": sid, "name": full or uname,
                "status": atts[sid].status if sid in atts else "not_started",
                "score": atts[sid].score if sid in atts and atts[sid].status == "finished" else None,
                "correct": atts[sid].correct if sid in atts else None,
                "total": atts[sid].total if sid in atts else len(st.question_ids),
                "violations": atts[sid].violations if sid in atts else 0,
                "finish_reason": atts[sid].finish_reason if sid in atts else None,
            }
            for sid, full, uname in students
        ],
    }
