"""
Integration tests for the bug-hunt question kind on /api/v1/game-sessions.

Covers:
- Auth/role requirements on POST /bug-questions
- Server-side shuffle: options[correct_option] always equals str(bug_line)
- Validation errors for malformed bug_line/distractor_lines input
- Security regressions: bug_line/bug_explanation must never leak to students
  before they answer (question_start payload, /my-questions response)
- chosen_option bounds checking
- Mixed quiz + bug-hunt questions coexist in one auto-mode session
"""

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select, update

from app.api.v1.endpoints.team_game_common import question_start_payload
from app.models.team_game import (
    GameSession, GameTeam, GameTeamMember, GameQuestion,
    SessionStatus,
)

BASE = "/api/v1/game-sessions"


def _bug_payload(**overrides) -> dict:
    defaults = {
        "question_text": "Nega natija noto'g'ri?",
        "code_snippet": "function sum(a, b) {\n  return a - b;\n}\nconsole.log(sum(2, 3));",
        "code_language": "javascript",
        "bug_line": 2,
        "distractor_lines": [1, 4],
        "bug_explanation": "a - b o'rniga a + b bo'lishi kerak",
    }
    return {**defaults, **overrides}


@pytest_asyncio.fixture
async def teacher_headers(async_client: AsyncClient, db_session) -> dict:
    from app.models.user import Student, UserRole

    uid = uuid.uuid4().hex[:8]
    username = f"teacher_{uid}"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "teacherpass123"},
    )
    assert reg.status_code == 201, reg.text
    user_id = reg.json()["user"]["id"]

    await db_session.execute(update(Student).where(Student.id == user_id).values(role=UserRole.teacher))
    await db_session.commit()

    login = await async_client.post(
        "/api/v1/auth/login", json={"username": username, "password": "teacherpass123"}
    )
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest_asyncio.fixture
async def student_with_headers(async_client: AsyncClient) -> tuple:
    """Register a fresh student, return (student_id, headers)."""
    uid = uuid.uuid4().hex[:8]
    username = f"student_{uid}"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "studentpass123"},
    )
    assert reg.status_code == 201, reg.text
    student_id = reg.json()["user"]["id"]

    login = await async_client.post(
        "/api/v1/auth/login", json={"username": username, "password": "studentpass123"}
    )
    assert login.status_code == 200, login.text
    return student_id, {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest_asyncio.fixture
async def bug_session(async_client: AsyncClient, teacher_headers: dict) -> int:
    """A pending team-game session owned by teacher_headers, auto_mode on."""
    resp = await async_client.post(
        BASE,
        json={"title": "Bug Hunt Test", "game_type": "individual", "team_count": 2},
        headers=teacher_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# ── Auth / role ──────────────────────────────────────────────────────────────

async def test_add_bug_question_requires_auth(async_client: AsyncClient, bug_session: int):
    resp = await async_client.post(f"{BASE}/{bug_session}/bug-questions", json=_bug_payload())
    assert resp.status_code == 401


async def test_add_bug_question_student_role_returns_403(
    async_client: AsyncClient, bug_session: int, auth_headers: dict
):
    resp = await async_client.post(
        f"{BASE}/{bug_session}/bug-questions", json=_bug_payload(), headers=auth_headers
    )
    assert resp.status_code == 403


async def test_add_bug_question_as_teacher_returns_201(
    async_client: AsyncClient, bug_session: int, teacher_headers: dict
):
    resp = await async_client.post(
        f"{BASE}/{bug_session}/bug-questions", json=_bug_payload(), headers=teacher_headers
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["question_kind"] == "bug_hunt"
    assert data["code_language"] == "javascript"
    assert data["bug_line"] == 2


# ── Server-side shuffle correctness ──────────────────────────────────────────

async def test_shuffled_options_match_bug_line(
    async_client: AsyncClient, bug_session: int, teacher_headers: dict
):
    """options[correct_option] must always equal str(bug_line), regardless
    of shuffle order — this is the whole point of deriving the index
    server-side instead of trusting a client-sent correct_option."""
    resp = await async_client.post(
        f"{BASE}/{bug_session}/bug-questions",
        json=_bug_payload(
            code_snippet="\n".join(f"line{i}" for i in range(1, 11)),
            bug_line=7, distractor_lines=[1, 3, 9],
        ),
        headers=teacher_headers,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert set(data["options"]) == {"7", "1", "3", "9"}
    assert data["options"][data["correct_option"]] == "7"


# ── Validation errors ─────────────────────────────────────────────────────────

async def test_bug_line_exceeds_snippet_length_returns_422(
    async_client: AsyncClient, bug_session: int, teacher_headers: dict
):
    resp = await async_client.post(
        f"{BASE}/{bug_session}/bug-questions",
        json=_bug_payload(bug_line=99),
        headers=teacher_headers,
    )
    assert resp.status_code == 422


async def test_distractor_exceeds_snippet_length_returns_422(
    async_client: AsyncClient, bug_session: int, teacher_headers: dict
):
    resp = await async_client.post(
        f"{BASE}/{bug_session}/bug-questions",
        json=_bug_payload(distractor_lines=[1, 99]),
        headers=teacher_headers,
    )
    assert resp.status_code == 422


async def test_duplicate_distractor_lines_returns_422(
    async_client: AsyncClient, bug_session: int, teacher_headers: dict
):
    resp = await async_client.post(
        f"{BASE}/{bug_session}/bug-questions",
        json=_bug_payload(distractor_lines=[1, 1]),
        headers=teacher_headers,
    )
    assert resp.status_code == 422


async def test_bug_line_in_distractors_returns_422(
    async_client: AsyncClient, bug_session: int, teacher_headers: dict
):
    resp = await async_client.post(
        f"{BASE}/{bug_session}/bug-questions",
        json=_bug_payload(bug_line=2, distractor_lines=[1, 2]),
        headers=teacher_headers,
    )
    assert resp.status_code == 422


async def test_too_few_distractors_returns_422(
    async_client: AsyncClient, bug_session: int, teacher_headers: dict
):
    """min_length=2 on distractor_lines — a single distractor is rejected."""
    resp = await async_client.post(
        f"{BASE}/{bug_session}/bug-questions",
        json=_bug_payload(distractor_lines=[1]),
        headers=teacher_headers,
    )
    assert resp.status_code == 422


async def test_missing_explanation_returns_422(
    async_client: AsyncClient, bug_session: int, teacher_headers: dict
):
    """bug_explanation is required — this is the pedagogical payload, not optional."""
    resp = await async_client.post(
        f"{BASE}/{bug_session}/bug-questions",
        json=_bug_payload(bug_explanation=""),
        headers=teacher_headers,
    )
    assert resp.status_code == 422


# ── Security regression: answer must never leak before reveal ───────────────

def test_question_start_payload_never_includes_bug_answer():
    """Regression guard for the WS question_start broadcast. A student
    connected to the session must not be able to read the answer out of
    the WS payload (e.g. via devtools) before they submit."""
    q = GameQuestion(
        id=1, session_id=1,
        question_text="Find the bug", options=["7", "1", "3"], correct_option=0,
        time_limit=90, points=1500, order_index=0,
        question_kind="bug_hunt",
        code_snippet="line1\nline2\nline3\nline4\nline5\nline6\nline7",
        code_language="javascript",
        bug_line=7,
        bug_explanation="This is the answer — must never leak pre-reveal",
        bug_explanation_ru="Ответ — не должен утекать до раскрытия",
        activated_at=None,
    )
    payload = question_start_payload(q)
    assert "bug_line" not in payload
    assert "bug_explanation" not in payload
    assert "bug_explanation_ru" not in payload
    assert "correct_option" not in payload
    # Sanity: the fields that SHOULD be there are
    assert payload["question_kind"] == "bug_hunt"
    assert payload["code_snippet"] == q.code_snippet
    assert payload["code_language"] == "javascript"


async def test_my_questions_never_leaks_bug_answer(
    async_client: AsyncClient, db_session, bug_session: int,
    teacher_headers: dict, student_with_headers: tuple,
):
    """/my-questions (auto-mode) serializes straight from the ORM object via
    from_attributes — the one place a stray field name on AutoQuestionRead
    would silently auto-populate the answer into a student-facing response."""
    student_id, student_headers = student_with_headers

    add = await async_client.post(
        f"{BASE}/{bug_session}/bug-questions", json=_bug_payload(), headers=teacher_headers
    )
    assert add.status_code == 201, add.text

    # Flip to auto_mode + active, and make the student a participant —
    # done directly via the ORM to keep this test focused on the payload
    # shape rather than the full start_session team-assignment flow.
    session_row = (await db_session.execute(
        select(GameSession).where(GameSession.id == bug_session)
    )).scalar_one()
    session_row.auto_mode = True
    session_row.status = SessionStatus.active

    team = GameTeam(session_id=bug_session, name=f"solo-{student_id}", color="#4aa8ff")
    db_session.add(team)
    await db_session.flush()
    db_session.add(GameTeamMember(team_id=team.id, student_id=student_id))
    await db_session.commit()

    resp = await async_client.get(f"{BASE}/{bug_session}/my-questions", headers=student_headers)
    assert resp.status_code == 200, resp.text
    questions = resp.json()
    assert len(questions) == 1
    q = questions[0]
    assert q["question_kind"] == "bug_hunt"
    assert "code_snippet" in q
    assert "bug_line" not in q
    assert "bug_explanation" not in q
    assert "bug_explanation_ru" not in q
    assert "correct_option" not in q


# ── chosen_option bounds check ───────────────────────────────────────────────

async def test_submit_answer_auto_rejects_out_of_range_chosen_option(
    async_client: AsyncClient, db_session, bug_session: int,
    teacher_headers: dict, student_with_headers: tuple,
):
    student_id, student_headers = student_with_headers

    add = await async_client.post(
        f"{BASE}/{bug_session}/bug-questions", json=_bug_payload(), headers=teacher_headers
    )
    assert add.status_code == 201, add.text
    question_id = add.json()["id"]

    session_row = (await db_session.execute(
        select(GameSession).where(GameSession.id == bug_session)
    )).scalar_one()
    session_row.auto_mode = True
    session_row.status = SessionStatus.active
    team = GameTeam(session_id=bug_session, name=f"solo-{student_id}", color="#4aa8ff")
    db_session.add(team)
    await db_session.flush()
    db_session.add(GameTeamMember(team_id=team.id, student_id=student_id))
    await db_session.commit()

    # 3 candidates -> valid indices are 0,1,2. Index 5 is within the schema's
    # le=5 bound but out of range for THIS question's option count — this is
    # exactly the gap the endpoint-level bounds check closes.
    resp = await async_client.post(
        f"{BASE}/{bug_session}/questions/{question_id}/answer-auto",
        json={"chosen_option": 5},
        headers=student_headers,
    )
    assert resp.status_code == 400


# ── Mixed session ─────────────────────────────────────────────────────────────

async def test_mixed_quiz_and_bug_questions_both_appear_in_my_questions(
    async_client: AsyncClient, db_session, bug_session: int,
    teacher_headers: dict, student_with_headers: tuple,
):
    student_id, student_headers = student_with_headers

    quiz_resp = await async_client.post(
        f"{BASE}/{bug_session}/questions",
        json={
            "question_text": "2 + 2 = ?",
            "options": ["3", "4", "5", "6"],
            "correct_option": 1,
        },
        headers=teacher_headers,
    )
    assert quiz_resp.status_code == 201, quiz_resp.text

    bug_resp = await async_client.post(
        f"{BASE}/{bug_session}/bug-questions", json=_bug_payload(), headers=teacher_headers
    )
    assert bug_resp.status_code == 201, bug_resp.text

    session_row = (await db_session.execute(
        select(GameSession).where(GameSession.id == bug_session)
    )).scalar_one()
    session_row.auto_mode = True
    session_row.status = SessionStatus.active
    team = GameTeam(session_id=bug_session, name=f"solo-{student_id}", color="#4aa8ff")
    db_session.add(team)
    await db_session.flush()
    db_session.add(GameTeamMember(team_id=team.id, student_id=student_id))
    await db_session.commit()

    resp = await async_client.get(f"{BASE}/{bug_session}/my-questions", headers=student_headers)
    assert resp.status_code == 200, resp.text
    kinds = {q["question_kind"] for q in resp.json()}
    assert kinds == {"quiz", "bug_hunt"}


# ── order_index regression (task: manually-added questions used to all land at 0) ──

async def test_manually_added_questions_get_increasing_order_index(
    async_client: AsyncClient, bug_session: int, teacher_headers: dict
):
    first = await async_client.post(
        f"{BASE}/{bug_session}/questions",
        json={"question_text": "Q1", "options": ["a", "b"], "correct_option": 0},
        headers=teacher_headers,
    )
    second = await async_client.post(
        f"{BASE}/{bug_session}/bug-questions", json=_bug_payload(), headers=teacher_headers
    )
    assert first.status_code == 201 and second.status_code == 201
    assert second.json()["order_index"] > first.json()["order_index"]
