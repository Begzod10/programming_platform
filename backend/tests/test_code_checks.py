"""Code-check quizzes: who gets one, taking it, and the teacher's queue. A check never changes points by itself."""
import io
import json
import random
import uuid
import zipfile
from datetime import timedelta

import pytest
from sqlalchemy import delete, select

from app.core.security import create_access_token
from app.db.database import AsyncSessionLocal
from app.models.code_check import ProjectCodeCheck
from app.models.notification import Notification
from app.models.project import Project
from app.models.ranking import Ranking
from app.models.user import Student, UserRole
from app.services import code_check_service as svc
from app.services.github_repo_service import PROJECTS_UPLOAD_DIR
from app.utils.datetime_utils import utcnow


class Rng:
    """random stand-in: `roll` is what random() returns, shuffle keeps the order."""
    def __init__(self, roll): self.roll = roll
    def random(self): return self.roll
    def shuffle(self, xs): pass


# ── decide(): who gets a quiz ────────────────────────────────────────────────

def test_a_pace_above_the_limit_is_flagged():
    reason, pace = svc.decide(300, 3 * 60, Rng(0.99))          # 300 lines in 3 minutes = 100/min
    assert reason == "pace" and pace == 100.0


def test_a_human_pace_is_not_flagged_unless_the_random_draw_picks_it():
    assert svc.decide(120, 20 * 60, Rng(0.99)) is None          # 6 lines/min
    assert svc.decide(120, 20 * 60, Rng(0.05))[0] == "random"   # the 10% draw


def test_a_pace_exactly_at_the_limit_is_not_flagged():
    assert svc.decide(150, 10 * 60, Rng(0.99)) is None          # 15 lines/min


def test_tiny_projects_never_get_a_quiz():
    assert svc.decide(svc.MIN_LINES - 1, 30, Rng(0.0)) is None


def test_a_long_break_says_nothing_about_pace_and_a_missing_previous_project_neither():
    assert svc.decide(500, 5 * 3600, Rng(0.99)) is None
    assert svc.decide(500, None, Rng(0.99)) is None
    assert svc.decide(500, None, Rng(0.01))[0] == "random"


def test_the_gap_is_floored_at_one_minute_so_instant_submissions_do_not_divide_by_zero():
    reason, pace = svc.decide(60, 0, Rng(0.99))
    assert reason == "pace" and pace == 60.0


# ── reading the code ─────────────────────────────────────────────────────────

def _zip(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, text in files.items():
            zf.writestr(name, text)
    return buf.getvalue()


def test_only_real_code_files_are_read_and_counted():
    files = svc.read_code_files(_zip({
        "index.html": "<html>\n\n<body>\n</body>\n</html>\n", "css/a.css": "a {\n}\n", "README.md": "x\ny\n",
        "__MACOSX/._index.html": "junk\n", "node_modules/x/i.js": "a\n", "pic.png": "bin"}))
    assert set(files) == {"index.html", "css/a.css"}
    assert svc.count_lines(files) == 6
    assert svc.read_code_files(b"garbage") == {}


def test_the_prompt_code_is_capped():
    code = svc.code_for_prompt({f"f{i}.js": "x" * 5000 for i in range(10)})
    assert len(code) <= svc._PROMPT_CHARS + 200 and code.count("=== ") <= svc._PROMPT_FILES


# ── questions ────────────────────────────────────────────────────────────────

def _q(correct=0, n=4):
    opts = [f"variant {i}" for i in range(n)]
    return {"uz": {"q": "Savol?", "options": opts}, "ru": {"q": "Вопрос?", "options": [f"вариант {i}" for i in range(n)]}, "correct": correct}


def test_validate_questions_accepts_good_json_and_rejects_the_rest():
    good = {"questions": [_q(0), _q(1), _q(2)]}
    assert len(svc.validate_questions(good)) == 3
    assert svc.validate_questions({"questions": [_q(), _q()]}) is None            # too few
    assert svc.validate_questions({"questions": [_q(), _q(), _q(correct=7)]}) is None
    assert svc.validate_questions({"questions": [_q(), _q(), _q(n=3)]}) is None   # 3 options
    dup = _q(); dup["uz"]["options"] = ["a", "a", "b", "c"]
    assert svc.validate_questions({"questions": [_q(), _q(), dup]}) is None       # duplicate options
    assert svc.validate_questions("nonsense") is None and svc.validate_questions(None) is None


def test_shuffling_moves_the_right_answer_but_keeps_it_right():
    rng = random.Random(7)
    seen = set()
    for _ in range(40):
        out = svc.shuffle_options([_q(0)], rng)[0]
        assert out["uz"]["options"][out["correct"]] == "variant 0"
        assert out["ru"]["options"][out["correct"]] == "вариант 0"
        seen.add(out["correct"])
    assert len(seen) > 1


# ── the flow, on a real project ──────────────────────────────────────────────

async def _student(async_client, role=None):
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post("/api/v1/auth/register", json={
        "username": f"cc_{uid}", "email": f"cc_{uid}@example.com", "password": "securepass123"})
    assert reg.status_code == 201, reg.text
    sid = reg.json()["user"]["id"]
    if role:
        async with AsyncSessionLocal() as db:
            s = (await db.execute(select(Student).where(Student.id == sid))).scalar_one()
            s.role = role
            # registration made a student ranking row; a real teacher never has one
            await db.execute(delete(Ranking).where(Ranking.student_id == sid))
            await db.commit()
    return sid, {"Authorization": f"Bearer {create_access_token(subject=sid)}"}


async def _project(sid, *, lines=300, points=95, status="Approved", minutes_ago=2, prev_minutes_ago=5, with_prev=True):
    name = f"{uuid.uuid4()}.zip"
    PROJECTS_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (PROJECTS_UPLOAD_DIR / name).write_bytes(_zip({"app.js": "\n".join(f"const v{i} = {i};" for i in range(lines))}))
    async with AsyncSessionLocal() as db:
        if with_prev:
            db.add(Project(student_id=sid, title="Oldingi", description="d", difficulty_level="Easy", status="Approved",
                           points_earned=90, submitted_at=utcnow() - timedelta(minutes=prev_minutes_ago)))
        p = Project(student_id=sid, title="Yangi loyiha", description="d", difficulty_level="Easy", status=status,
                    points_earned=points, project_files=f"/uploads/projects/{name}", submitted_at=utcnow() - timedelta(minutes=minutes_ago))
        db.add(p)
        await db.commit()
        await db.refresh(p)
        return p


async def _create(project, roll=0.99):
    async with AsyncSessionLocal() as db:
        return await svc.maybe_create_check(db, project, rng=Rng(roll))


async def test_a_fast_big_zip_gets_a_pending_check_and_a_notification(async_client):
    sid, _ = await _student(async_client)
    p = await _project(sid)                                     # 300 lines, 3 minutes after the previous project
    check = await _create(p)
    assert check.status == "pending" and check.reason == "pace" and check.code_lines == 300 and not check.needs_teacher
    assert check.questions_json is None                         # built only when the student starts it
    async with AsyncSessionLocal() as db:
        note = (await db.execute(select(Notification).where(Notification.student_id == sid, Notification.type == "code_check"))).scalar_one()
    assert note.link == f"/student/code-check/{check.id}" and "Подтвердите" in note.title


@pytest.mark.parametrize("kw", [
    dict(points=60, status="Rejected"),             # not approved
    dict(lines=20),                                  # tiny
    dict(minutes_ago=2, prev_minutes_ago=200),       # a long break
    dict(with_prev=False),                           # nothing to compare with
])
async def test_these_projects_get_no_check(async_client, kw):
    sid, _ = await _student(async_client)
    assert await _create(await _project(sid, **kw)) is None


async def test_a_slow_project_gets_no_check_unless_randomly_drawn(async_client):
    sid, _ = await _student(async_client)
    p = await _project(sid, lines=100, minutes_ago=2, prev_minutes_ago=62)        # 100 lines in 60 minutes
    assert await _create(p, roll=0.99) is None
    assert (await _create(p, roll=0.01)).reason == "random"


async def test_a_project_is_checked_at_most_once(async_client):
    sid, _ = await _student(async_client)
    p = await _project(sid)
    assert await _create(p) is not None
    assert await _create(p) is None


async def test_a_second_pace_flag_while_one_is_open_goes_straight_to_the_teacher(async_client):
    sid, _ = await _student(async_client)
    first = await _create(await _project(sid))
    second = await _create(await _project(sid, with_prev=False) if False else await _project(sid))
    assert first.status == "pending"
    assert second.status == "unavailable" and second.needs_teacher           # not lost, but no second quiz


async def test_demo_students_and_projects_without_any_code_are_skipped(async_client):
    sid, _ = await _student(async_client)
    async with AsyncSessionLocal() as db:
        s = (await db.execute(select(Student).where(Student.id == sid))).scalar_one(); s.is_demo = True
        await db.execute(delete(Ranking).where(Ranking.student_id == sid))   # a real demo account has no ranking row
        await db.commit()
    assert await _create(await _project(sid)) is None
    sid2, _ = await _student(async_client)
    p = await _project(sid2); p.project_files = None          # no ZIP and no repo code to build questions from
    assert await _create(p) is None


QUESTIONS = [_q(0), _q(1), _q(2)]


@pytest.fixture()
def fake_ai(monkeypatch):
    async def gen(code): return json.loads(json.dumps(QUESTIONS))
    monkeypatch.setattr(svc, "generate_questions", gen)


async def _pending(async_client):
    sid, headers = await _student(async_client)
    check = await _create(await _project(sid))
    return sid, headers, check


async def test_starting_returns_the_questions_without_the_answers(async_client, fake_ai):
    sid, h, check = await _pending(async_client)
    r = await async_client.post(f"/api/v1/code-checks/{check.id}/start?lang=ru", headers=h)
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["questions"]) == 3 and body["seconds_per_question"] == svc.SECONDS_PER_QUESTION == 30 and "deadline" in body
    assert body["questions"][0]["options"][0].startswith("вариант")
    assert "correct" not in json.dumps(body)


async def test_passing_the_quiz_closes_it_without_the_teacher(async_client, fake_ai):
    sid, h, check = await _pending(async_client)
    await async_client.post(f"/api/v1/code-checks/{check.id}/start", headers=h)
    r = await async_client.post(f"/api/v1/code-checks/{check.id}/submit", headers=h,
                                json={"answers": [0, 1, 3], "blur_count": 0, "times_ms": [9000, 8000, 7000]})   # 2 of 3 right
    assert r.status_code == 200, r.text
    assert r.json()["passed"] is True and r.json()["correct"] == 2
    async with AsyncSessionLocal() as db:
        c = (await db.execute(select(ProjectCodeCheck).where(ProjectCodeCheck.id == check.id))).scalar_one()
    # fast AND passed: not lost — the teacher still sees it, below the cases that need them
    assert c.status == "passed" and c.needs_teacher and c.low_priority


async def test_a_randomly_picked_project_that_passes_is_closed(async_client, fake_ai):
    sid, h = await _student(async_client)
    check = await _create(await _project(sid, lines=100, minutes_ago=2, prev_minutes_ago=62), roll=0.01)   # slow: random draw
    assert check.reason == "random"
    await async_client.post(f"/api/v1/code-checks/{check.id}/start", headers=h)
    await async_client.post(f"/api/v1/code-checks/{check.id}/submit", headers=h, json={"answers": [0, 1, 2]})
    async with AsyncSessionLocal() as db:
        c = (await db.execute(select(ProjectCodeCheck).where(ProjectCodeCheck.id == check.id))).scalar_one()
    assert c.status == "passed" and not c.needs_teacher and not c.low_priority


async def test_right_answers_after_switching_tabs_still_go_to_the_teacher(async_client, fake_ai):
    sid, h, check = await _pending(async_client)
    await async_client.post(f"/api/v1/code-checks/{check.id}/start", headers=h)
    r = await async_client.post(f"/api/v1/code-checks/{check.id}/submit", headers=h, json={"answers": [0, 1, 2], "blur_count": 3})
    assert r.json()["passed"] is False and r.json()["correct"] == 3 and r.json()["status"] == "suspicious"
    async with AsyncSessionLocal() as db:
        c = (await db.execute(select(ProjectCodeCheck).where(ProjectCodeCheck.id == check.id))).scalar_one()
    assert c.needs_teacher and c.blur_count == 3


async def test_one_tab_switch_is_forgiven(async_client, fake_ai):
    sid, h, check = await _pending(async_client)
    await async_client.post(f"/api/v1/code-checks/{check.id}/start", headers=h)
    r = await async_client.post(f"/api/v1/code-checks/{check.id}/submit", headers=h, json={"answers": [0, 1, 2], "blur_count": 1})
    assert r.json()["passed"] is True and r.json()["status"] == "passed"


async def test_failing_sends_it_to_the_teacher_and_leaves_the_points_alone(async_client, fake_ai):
    sid, h, check = await _pending(async_client)
    await async_client.post(f"/api/v1/code-checks/{check.id}/start", headers=h)
    r = await async_client.post(f"/api/v1/code-checks/{check.id}/submit", headers=h, json={"answers": [3, 3, None], "blur_count": 5})
    assert r.json()["passed"] is False and r.json()["correct"] == 0
    async with AsyncSessionLocal() as db:
        c = (await db.execute(select(ProjectCodeCheck).where(ProjectCodeCheck.id == check.id))).scalar_one()
        p = (await db.execute(select(Project).where(Project.id == check.project_id))).scalar_one()
    assert c.status == "failed" and c.needs_teacher and c.blur_count == 5
    assert p.points_earned == 95                                 # untouched


async def test_a_late_answer_fails_even_if_it_is_right(async_client, fake_ai):
    sid, h, check = await _pending(async_client)
    await async_client.post(f"/api/v1/code-checks/{check.id}/start", headers=h)
    async with AsyncSessionLocal() as db:
        c = (await db.execute(select(ProjectCodeCheck).where(ProjectCodeCheck.id == check.id))).scalar_one()
        c.started_at = utcnow() - svc.time_limit() - timedelta(seconds=30)
        await db.commit()
    r = await async_client.post(f"/api/v1/code-checks/{check.id}/submit", headers=h, json={"answers": [0, 1, 2]})
    assert r.json()["passed"] is False and r.json()["on_time"] is False and r.json()["correct"] == 3


async def test_a_quiz_can_be_taken_only_once_and_only_by_its_student(async_client, fake_ai):
    sid, h, check = await _pending(async_client)
    _, other = await _student(async_client)
    assert (await async_client.post(f"/api/v1/code-checks/{check.id}/start", headers=other)).status_code == 404
    await async_client.post(f"/api/v1/code-checks/{check.id}/start", headers=h)
    await async_client.post(f"/api/v1/code-checks/{check.id}/submit", headers=h, json={"answers": [0, 1, 2]})
    assert (await async_client.post(f"/api/v1/code-checks/{check.id}/submit", headers=h, json={"answers": [0, 1, 2]})).status_code == 409
    assert (await async_client.post(f"/api/v1/code-checks/{check.id}/start", headers=h)).status_code == 409


async def test_submitting_without_starting_is_refused(async_client):
    sid, h, check = await _pending(async_client)
    assert (await async_client.post(f"/api/v1/code-checks/{check.id}/submit", headers=h, json={"answers": [0, 1, 2]})).status_code == 409


async def test_when_no_questions_can_be_made_the_teacher_gets_it(async_client, monkeypatch):
    async def none(code): return None
    monkeypatch.setattr(svc, "generate_questions", none)
    sid, h, check = await _pending(async_client)
    r = await async_client.post(f"/api/v1/code-checks/{check.id}/start", headers=h)
    assert r.status_code == 503
    async with AsyncSessionLocal() as db:
        c = (await db.execute(select(ProjectCodeCheck).where(ProjectCodeCheck.id == check.id))).scalar_one()
    assert c.status == "unavailable" and c.needs_teacher


async def test_my_pending_lists_only_open_quizzes(async_client, fake_ai):
    sid, h, check = await _pending(async_client)
    mine = (await async_client.get("/api/v1/code-checks/mine", headers=h)).json()
    assert [m["id"] for m in mine] == [check.id] and mine[0]["project_title"] == "Yangi loyiha"
    await async_client.post(f"/api/v1/code-checks/{check.id}/start", headers=h)
    await async_client.post(f"/api/v1/code-checks/{check.id}/submit", headers=h, json={"answers": [0, 1, 2]})
    assert (await async_client.get("/api/v1/code-checks/mine", headers=h)).json() == []


async def test_unanswered_quizzes_expire_into_the_teacher_queue(async_client):
    sid, h, check = await _pending(async_client)
    async with AsyncSessionLocal() as db:
        c = (await db.execute(select(ProjectCodeCheck).where(ProjectCodeCheck.id == check.id))).scalar_one()
        c.expires_at = utcnow() - timedelta(minutes=1)
        await db.commit()
        assert await svc.expire_old_checks(db) >= 1
        c = (await db.execute(select(ProjectCodeCheck).where(ProjectCodeCheck.id == check.id))).scalar_one()
    assert c.status == "expired" and c.needs_teacher


# ── the teacher ──────────────────────────────────────────────────────────────

async def test_the_teacher_sees_failed_checks_with_the_questions_and_resolves_them(async_client, fake_ai):
    sid, h, check = await _pending(async_client)
    await async_client.post(f"/api/v1/code-checks/{check.id}/start", headers=h)
    await async_client.post(f"/api/v1/code-checks/{check.id}/submit", headers=h, json={"answers": [3, 3, 3], "blur_count": 4})
    tid, th = await _student(async_client, role=UserRole.teacher)

    queue = (await async_client.get("/api/v1/teacher/code-checks", headers=th)).json()
    row = next(r for r in queue if r["id"] == check.id)
    assert row["status"] == "failed" and row["student"]["id"] == sid and row["blur_count"] == 4
    assert row["questions"][0]["correct"] == 0 and row["questions"][0]["answer"] == 3 and row["pace"] > 15
    assert (await async_client.get("/api/v1/teacher/code-checks", headers=h)).status_code == 403    # students cannot

    r = await async_client.post(f"/api/v1/teacher/code-checks/{check.id}/resolve", headers=th, json={"action": "revoke_points", "note": "suhbat"})
    assert r.status_code == 200 and r.json()["resolution"] == "points_revoked"
    async with AsyncSessionLocal() as db:
        p = (await db.execute(select(Project).where(Project.id == check.project_id))).scalar_one()
        s = (await db.execute(select(Student).where(Student.id == sid))).scalar_one()
    assert p.points_earned == 0
    assert not any(x["id"] == check.id for x in (await async_client.get("/api/v1/teacher/code-checks", headers=th)).json())
    assert (await async_client.post(f"/api/v1/teacher/code-checks/{check.id}/resolve", headers=th, json={"action": "dismiss"})).status_code == 409


async def test_dismissing_keeps_the_points(async_client, fake_ai):
    sid, h, check = await _pending(async_client)
    tid, th = await _student(async_client, role=UserRole.teacher)
    r = await async_client.post(f"/api/v1/teacher/code-checks/{check.id}/resolve", headers=th, json={"action": "dismiss"})
    assert r.status_code == 200 and r.json()["resolution"] == "dismissed"
    async with AsyncSessionLocal() as db:
        p = (await db.execute(select(Project).where(Project.id == check.project_id))).scalar_one()
    assert p.points_earned == 95


async def test_demo_accounts_cannot_reach_code_checks(async_client):
    r = await async_client.post("/api/v1/auth/demo", json={"first_name": "Test", "last_name": "Demo"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    assert (await async_client.get("/api/v1/code-checks/mine", headers=h)).status_code == 403


# ── GitHub-submitted projects follow the same rules ──────────────────────────

SNAPSHOT = """### index.html
```
<html>
<body>
</body>
</html>
```

### js/app.js
```
const a = 1;
function go() {
  return a;
}
```

### README.md
```
# not code
```

### node_modules/x/i.js
```
junk
```"""


def test_a_review_snapshot_is_split_back_into_code_files():
    files = svc.files_from_snapshot_text(SNAPSHOT)
    assert set(files) == {"index.html", "js/app.js"}
    assert files["js/app.js"].startswith("const a = 1;") and svc.count_lines(files) == 8
    assert svc.files_from_snapshot_text("") == {} and svc.files_from_snapshot_text(None) == {}


async def test_a_fast_github_project_gets_a_check_whose_code_is_kept(async_client, monkeypatch):
    sid, h = await _student(async_client)
    p = await _project(sid, lines=10)                                    # on-disk ZIP is tiny, irrelevant: the repo code is used
    big = {f"src/f{i}.js": "\n".join(f"let x{j} = {j};" for j in range(60)) for i in range(5)}      # 300 lines
    p.project_files, p.github_url = None, "https://github.com/someone/repo"
    async with AsyncSessionLocal() as db:
        check = await svc.maybe_create_check(db, p, files=big, rng=Rng(0.99))
    assert check.status == "pending" and check.reason == "pace" and check.code_lines == 300
    assert "=== src/f0.js ===" in check.code_excerpt

    seen = {}
    async def gen(code):
        seen["code"] = code
        return json.loads(json.dumps(QUESTIONS))
    monkeypatch.setattr(svc, "generate_questions", gen)
    r = await async_client.post(f"/api/v1/code-checks/{check.id}/start", headers=h)
    assert r.status_code == 200 and seen["code"] == check.code_excerpt          # no second trip to GitHub


async def test_a_github_project_with_a_slow_pace_is_left_alone(async_client):
    sid, _ = await _student(async_client)
    p = await _project(sid, minutes_ago=2, prev_minutes_ago=62)
    p.project_files, p.github_url = None, "https://github.com/someone/repo"
    async with AsyncSessionLocal() as db:
        assert await svc.maybe_create_check(db, p, files={"a.js": "\n".join("x" for _ in range(100))}, rng=Rng(0.99)) is None


# ── the teacher's badge and the order of the queue ───────────────────────────

async def test_the_queue_puts_real_cases_above_fast_but_passed_ones_and_counts_both(async_client, fake_ai):
    tid, th = await _student(async_client, role=UserRole.teacher)
    before = (await async_client.get("/api/v1/teacher/code-checks/count", headers=th)).json()

    sid_a, ha, passed = await _pending(async_client)         # fast, passes -> low priority
    await async_client.post(f"/api/v1/code-checks/{passed.id}/start", headers=ha)
    await async_client.post(f"/api/v1/code-checks/{passed.id}/submit", headers=ha, json={"answers": [0, 1, 2]})
    sid_b, hb, failed = await _pending(async_client)         # fast, fails -> needs the teacher
    await async_client.post(f"/api/v1/code-checks/{failed.id}/start", headers=hb)
    await async_client.post(f"/api/v1/code-checks/{failed.id}/submit", headers=hb, json={"answers": [3, 3, 3]})

    after = (await async_client.get("/api/v1/teacher/code-checks/count", headers=th)).json()
    assert after["count"] == before["count"] + 1 and after["low"] == before["low"] + 1

    queue = (await async_client.get("/api/v1/teacher/code-checks", headers=th)).json()
    ids = [r["id"] for r in queue]
    assert ids.index(failed.id) < ids.index(passed.id)                           # real case first
    low = next(r for r in queue if r["id"] == passed.id)
    assert low["low_priority"] is True and low["status"] == "passed"

    await async_client.post(f"/api/v1/teacher/code-checks/{passed.id}/resolve", headers=th, json={"action": "dismiss"})
    assert (await async_client.get("/api/v1/teacher/code-checks/count", headers=th)).json()["low"] == before["low"]


async def test_students_cannot_read_the_teacher_count(async_client):
    _, h = await _student(async_client)
    assert (await async_client.get("/api/v1/teacher/code-checks/count", headers=h)).status_code == 403
