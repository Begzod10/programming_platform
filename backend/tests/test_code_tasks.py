"""Teacher code tasks: a teacher gives a student a coding task, the student writes and submits code, the teacher
grades or returns it. See docs/superpowers/specs/2026-11-09-teacher-code-tasks-design.md."""
import asyncio
import uuid
from datetime import timedelta

from sqlalchemy import delete, func, select

from app.core.security import create_access_token
from app.db.database import AsyncSessionLocal
from app.models.code_task import CodeTask, CodeTaskSubmission
from app.models.group import Group, student_groups
from app.models.user import Student, UserRole
from app.utils.datetime_utils import utcnow

TEACHER_API = "/api/v1/teacher/code-tasks"
STUDENT_API = "/api/v1/code-tasks"


async def _user(*, teacher=False):
    uid = uuid.uuid4().hex[:8]
    async with AsyncSessionLocal() as db:
        s = Student(username=f"ct_{uid}", email=f"ct_{uid}@example.com", hashed_password="x",
                    full_name=f"User {uid}", role=UserRole.teacher if teacher else UserRole.student)
        db.add(s)
        await db.commit()
        return s.id


def _h(user_id):
    return {"Authorization": f"Bearer {create_access_token(subject=user_id)}"}


async def _teacher_with_student():
    """(teacher_id, student_id): the student sits in a group the teacher owns."""
    tid, sid = await _user(teacher=True), await _user()
    async with AsyncSessionLocal() as db:
        g = Group(name=f"g_{uuid.uuid4().hex[:6]}", teacher_id=tid)
        db.add(g)
        await db.flush()
        await db.execute(student_groups.insert().values(student_id=sid, group_id=g.id))
        await db.commit()
    return tid, sid


async def test_tables_exist_and_defaults_apply():
    tid, sid = await _user(teacher=True), await _user()
    async with AsyncSessionLocal() as db:
        t = CodeTask(teacher_id=tid, student_id=sid, title="T", description="D", language="python")
        db.add(t)
        await db.commit()
        await db.refresh(t)
        assert t.status == "assigned" and t.max_points == 20 and t.review_lang == "uz"
        assert t.graded_points is None and t.draft_code is None
        sub = CodeTaskSubmission(task_id=t.id, attempt_no=1, code="x")
        db.add(sub)
        await db.commit()
        await db.refresh(sub)
        assert sub.ai_status == "pending" and sub.typed_chars == 0 and sub.pasted_chars == 0


# ── Task 2: teacher side ────────────────────────────────────────────────────

def _body(student_id, **over):
    return {"student_id": student_id, "title": "Sort a list", "description": "Write bubble sort.",
            "language": "python", **over}


async def _create(client, tid, sid, **over):
    r = await client.post(f"{TEACHER_API}/", headers=_h(tid), json=_body(sid, **over))
    assert r.status_code == 201, r.text
    return r.json()


async def _set(task_id, **fields):
    async with AsyncSessionLocal() as db:
        t = await db.get(CodeTask, task_id)
        for k, v in fields.items():
            setattr(t, k, v)
        await db.commit()


async def test_teacher_creates_a_task_for_own_student(async_client):
    tid, sid = await _teacher_with_student()
    task = await _create(async_client, tid, sid, lang="ru")
    assert task["status"] == "assigned" and task["max_points"] == 20 and task["student_id"] == sid
    async with AsyncSessionLocal() as db:
        assert (await db.get(CodeTask, task["id"])).review_lang == "ru"


async def test_creating_for_a_student_outside_my_scope_is_404(async_client):
    tid, _ = await _teacher_with_student()
    _, stranger = await _teacher_with_student()
    r = await async_client.post(f"{TEACHER_API}/", headers=_h(tid), json=_body(stranger))
    assert r.status_code == 404


async def test_invalid_input_is_422(async_client):
    tid, sid = await _teacher_with_student()
    for over in ({"language": "cobol"}, {"max_points": 0}, {"max_points": 101}, {"title": ""},
                 {"title": "x" * 201}, {"description": "x" * 10_001}, {"starter_code": "x" * 100_001}):
        r = await async_client.post(f"{TEACHER_API}/", headers=_h(tid), json=_body(sid, **over))
        assert r.status_code == 422, over


async def test_a_student_cannot_use_the_teacher_api(async_client):
    tid, sid = await _teacher_with_student()
    r = await async_client.post(f"{TEACHER_API}/", headers=_h(sid), json=_body(sid))
    assert r.status_code == 403


async def test_list_for_a_student_shows_only_my_tasks_newest_first(async_client):
    tid, sid = await _teacher_with_student()
    other = await _user(teacher=True)
    async with AsyncSessionLocal() as db:                       # the same student also sits in another teacher's group
        g = Group(name=f"g_{uuid.uuid4().hex[:6]}", teacher_id=other)
        db.add(g)
        await db.flush()
        await db.execute(student_groups.insert().values(student_id=sid, group_id=g.id))
        await db.commit()
    first = await _create(async_client, tid, sid, title="first")
    second = await _create(async_client, tid, sid, title="second")
    theirs = await async_client.post(f"{TEACHER_API}/", headers=_h(other), json=_body(sid, title="theirs"))
    assert theirs.status_code == 201
    rows = (await async_client.get(f"{TEACHER_API}/student/{sid}", headers=_h(tid))).json()
    assert [r["title"] for r in rows] == ["second", "first"]
    assert {r["id"] for r in rows} == {first["id"], second["id"]}
    stranger = (await _teacher_with_student())[0]
    assert (await async_client.get(f"{TEACHER_API}/student/{sid}", headers=_h(stranger))).status_code == 404


async def test_another_teachers_task_is_404_on_read_patch_delete(async_client):
    tid, sid = await _teacher_with_student()
    task = await _create(async_client, tid, sid)
    other = await _user(teacher=True)
    assert (await async_client.get(f"{TEACHER_API}/{task['id']}", headers=_h(other))).status_code == 404
    assert (await async_client.patch(f"{TEACHER_API}/{task['id']}", headers=_h(other), json={"title": "x"})).status_code == 404
    assert (await async_client.delete(f"{TEACHER_API}/{task['id']}", headers=_h(other))).status_code == 404


async def test_detail_lists_submissions_with_ai_and_integrity_fields(async_client):
    tid, sid = await _teacher_with_student()
    task = await _create(async_client, tid, sid)
    async with AsyncSessionLocal() as db:
        db.add(CodeTaskSubmission(task_id=task["id"], attempt_no=1, code="print(1)", typed_chars=5, pasted_chars=45,
                                  paste_events=1, active_seconds=90, ai_status="done", ai_review={"summary": "ok"}))
        await db.commit()
    body = (await async_client.get(f"{TEACHER_API}/{task['id']}", headers=_h(tid))).json()
    sub = body["submissions"][0]
    assert sub["code"] == "print(1)" and sub["pasted_chars"] == 45 and sub["ai_review"] == {"summary": "ok"}


async def test_patch_and_delete_only_before_submission(async_client):
    tid, sid = await _teacher_with_student()
    task = await _create(async_client, tid, sid)
    r = await async_client.patch(f"{TEACHER_API}/{task['id']}", headers=_h(tid), json={"title": "New", "max_points": 30})
    assert r.status_code == 200 and r.json()["title"] == "New" and r.json()["max_points"] == 30
    assert (await async_client.delete(f"{TEACHER_API}/{task['id']}", headers=_h(tid))).status_code == 204
    again = await _create(async_client, tid, sid)
    await _set(again["id"], status="submitted")
    assert (await async_client.patch(f"{TEACHER_API}/{again['id']}", headers=_h(tid), json={"title": "x"})).status_code == 409
    assert (await async_client.delete(f"{TEACHER_API}/{again['id']}", headers=_h(tid))).status_code == 409
    returned = await _create(async_client, tid, sid)
    await _set(returned["id"], status="returned")
    async with AsyncSessionLocal() as db:
        db.add(CodeTaskSubmission(task_id=returned["id"], attempt_no=1, code="x"))
        await db.commit()
    assert (await async_client.delete(f"{TEACHER_API}/{returned['id']}", headers=_h(tid))).status_code == 409


# ── Task 3: student side ────────────────────────────────────────────────────

async def _task(async_client, **over):
    tid, sid = await _teacher_with_student()
    task = await _create(async_client, tid, sid, **over)
    return tid, sid, task["id"]


def _submit_body(**over):
    return {"code": "print('hi')", "active_seconds": 90, "typed_chars": 8, "pasted_chars": 3, "paste_events": 1, **over}


async def test_student_lists_and_reads_only_own_tasks(async_client):
    tid, sid, task_id = await _task(async_client, title="Mine")
    _, other_sid = await _teacher_with_student()
    rows = (await async_client.get(f"{STUDENT_API}/", headers=_h(sid))).json()
    assert [r["title"] for r in rows] == ["Mine"]
    assert (await async_client.get(f"{STUDENT_API}/", headers=_h(other_sid))).json() == []
    h = _h(other_sid)
    assert (await async_client.get(f"{STUDENT_API}/{task_id}", headers=h)).status_code == 404
    assert (await async_client.put(f"{STUDENT_API}/{task_id}/draft", headers=h, json={"code": "x"})).status_code == 404
    assert (await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=h, json=_submit_body())).status_code == 404


async def test_read_returns_starter_then_draft(async_client):
    tid, sid, task_id = await _task(async_client, starter_code="# start here")
    assert (await async_client.get(f"{STUDENT_API}/{task_id}", headers=_h(sid))).json()["code"] == "# start here"
    r = await async_client.put(f"{STUDENT_API}/{task_id}/draft", headers=_h(sid), json={"code": "x = 1"})
    assert r.status_code == 200
    assert (await async_client.get(f"{STUDENT_API}/{task_id}", headers=_h(sid))).json()["code"] == "x = 1"


async def test_student_response_has_no_ai_or_integrity_fields(async_client):
    tid, sid, task_id = await _task(async_client)
    assert (await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=_h(sid), json=_submit_body())).status_code == 200
    async with AsyncSessionLocal() as db:
        sub = (await db.execute(select(CodeTaskSubmission).where(CodeTaskSubmission.task_id == task_id))).scalar_one()
        sub.ai_review = {"summary": "secret"}
        sub.ai_status = "done"
        await db.commit()
    for url in (f"{STUDENT_API}/", f"{STUDENT_API}/{task_id}"):
        text = (await async_client.get(url, headers=_h(sid))).text
        for key in ("ai_review", "ai_status", "pasted_chars", "typed_chars", "paste_events", "active_seconds", "secret"):
            assert key not in text, (url, key)


async def test_submit_moves_to_submitted_and_stores_attempt(async_client):
    tid, sid, task_id = await _task(async_client)
    await async_client.put(f"{STUDENT_API}/{task_id}/draft", headers=_h(sid), json={"code": "draft"})
    r = await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=_h(sid), json=_submit_body())
    assert r.status_code == 200 and r.json()["status"] == "submitted"
    async with AsyncSessionLocal() as db:
        sub = (await db.execute(select(CodeTaskSubmission).where(CodeTaskSubmission.task_id == task_id))).scalar_one()
        assert (sub.attempt_no, sub.code, sub.typed_chars, sub.pasted_chars, sub.paste_events, sub.active_seconds) == \
               (1, "print('hi')", 8, 3, 1, 90)
        task = await db.get(CodeTask, task_id)
        assert task.status == "submitted" and task.draft_code is None


async def test_cannot_edit_or_resubmit_when_submitted(async_client):
    tid, sid, task_id = await _task(async_client)
    await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=_h(sid), json=_submit_body())
    assert (await async_client.put(f"{STUDENT_API}/{task_id}/draft", headers=_h(sid), json={"code": "x"})).status_code == 409
    assert (await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=_h(sid), json=_submit_body())).status_code == 409


async def test_double_submit_only_one_wins(async_client):
    tid, sid, task_id = await _task(async_client)
    rs = await asyncio.gather(*[
        async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=_h(sid), json=_submit_body()) for _ in range(2)])
    assert sorted(r.status_code for r in rs) == [200, 409]
    async with AsyncSessionLocal() as db:
        n = (await db.execute(select(func.count(CodeTaskSubmission.id)).where(CodeTaskSubmission.task_id == task_id))).scalar()
        assert n == 1


async def test_empty_whitespace_and_oversized_code_are_rejected(async_client):
    tid, sid, task_id = await _task(async_client)
    h = _h(sid)
    for code in ("", " \n\t "):
        assert (await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=h, json=_submit_body(code=code))).status_code == 422
    assert (await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=h, json=_submit_body(code="x" * 100_001))).status_code == 422
    assert (await async_client.put(f"{STUDENT_API}/{task_id}/draft", headers=h, json={"code": "x" * 100_001})).status_code == 422
    assert (await async_client.put(f"{STUDENT_API}/{task_id}/draft", headers=h, json={"code": ""})).status_code == 200
    assert (await async_client.put(f"{STUDENT_API}/{task_id}/draft", headers=h, json={"code": "x" * 100_000})).status_code == 200
    assert (await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=h, json=_submit_body(code="x" * 100_000))).status_code == 200


async def test_markup_like_code_round_trips_verbatim(async_client):
    tid, sid, task_id = await _task(async_client)
    code = "<script>alert(1)</script></pre>"
    await async_client.put(f"{STUDENT_API}/{task_id}/draft", headers=_h(sid), json={"code": code})
    assert (await async_client.get(f"{STUDENT_API}/{task_id}", headers=_h(sid))).json()["code"] == code


async def test_resubmit_after_return(async_client):
    tid, sid, task_id = await _task(async_client)
    await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=_h(sid), json=_submit_body())
    await _set(task_id, status="returned")
    r = await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=_h(sid), json=_submit_body(code="v2"))
    assert r.status_code == 200
    async with AsyncSessionLocal() as db:
        nos = (await db.execute(select(CodeTaskSubmission.attempt_no).where(CodeTaskSubmission.task_id == task_id)
                                .order_by(CodeTaskSubmission.attempt_no))).scalars().all()
        assert nos == [1, 2]


async def test_late_submission_is_allowed(async_client):
    past = (utcnow() - timedelta(days=2)).isoformat()
    tid, sid, task_id = await _task(async_client, deadline=past)
    assert (await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=_h(sid), json=_submit_body())).status_code == 200


# ── Task 4: grade and return ────────────────────────────────────────────────

async def _submitted(async_client, **over):
    tid, sid, task_id = await _task(async_client, **over)
    r = await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=_h(sid), json=_submit_body())
    assert r.status_code == 200, r.text
    return tid, sid, task_id


async def _balances(sid):
    async with AsyncSessionLocal() as db:
        s = await db.get(Student, sid)
        return s.total_points, s.lifetime_points


async def test_grade_awards_points_once(async_client):
    tid, sid, task_id = await _submitted(async_client)
    before = await _balances(sid)
    r = await async_client.post(f"{TEACHER_API}/{task_id}/grade", headers=_h(tid), json={"points": 15, "feedback": "Yaxshi"})
    assert r.status_code == 200 and r.json()["status"] == "graded" and r.json()["graded_points"] == 15
    assert r.json()["teacher_feedback"] == "Yaxshi"
    assert await _balances(sid) == (before[0] + 15, before[1] + 15)
    mine = (await async_client.get(f"{STUDENT_API}/{task_id}", headers=_h(sid))).json()
    assert mine["status"] == "graded" and mine["graded_points"] == 15 and mine["teacher_feedback"] == "Yaxshi"


async def test_grade_zero_awards_nothing(async_client):
    tid, sid, task_id = await _submitted(async_client)
    before = await _balances(sid)
    r = await async_client.post(f"{TEACHER_API}/{task_id}/grade", headers=_h(tid), json={"points": 0})
    assert r.status_code == 200 and r.json()["status"] == "graded"
    assert await _balances(sid) == before


async def test_double_grade_is_409_and_points_are_added_once(async_client):
    tid, sid, task_id = await _submitted(async_client)
    before = await _balances(sid)
    rs = await asyncio.gather(*[
        async_client.post(f"{TEACHER_API}/{task_id}/grade", headers=_h(tid), json={"points": 10}) for _ in range(2)])
    assert sorted(r.status_code for r in rs) == [200, 409]
    again = await async_client.post(f"{TEACHER_API}/{task_id}/grade", headers=_h(tid), json={"points": 10})
    assert again.status_code == 409
    assert await _balances(sid) == (before[0] + 10, before[1] + 10)


async def test_points_above_max_or_negative_are_422_and_only_submitted_can_be_graded(async_client):
    tid, sid, task_id = await _submitted(async_client, max_points=20)
    for points in (21, -1):
        r = await async_client.post(f"{TEACHER_API}/{task_id}/grade", headers=_h(tid), json={"points": points})
        assert r.status_code == 422, points
    assert (await async_client.post(f"{TEACHER_API}/{task_id}/grade", headers=_h(tid), json={"points": 20})).status_code == 200
    _, _, fresh = await _task(async_client)                 # never submitted
    tid2 = await _owner_of(fresh)
    assert (await async_client.post(f"{TEACHER_API}/{fresh}/grade", headers=_h(tid2), json={"points": 5})).status_code == 409


async def _owner_of(task_id):
    async with AsyncSessionLocal() as db:
        return (await db.get(CodeTask, task_id)).teacher_id


async def test_return_needs_feedback_and_reopens_for_the_student(async_client):
    tid, sid, task_id = await _submitted(async_client)
    for fb in ("", "   "):
        assert (await async_client.post(f"{TEACHER_API}/{task_id}/return", headers=_h(tid), json={"feedback": fb})).status_code == 422
    r = await async_client.post(f"{TEACHER_API}/{task_id}/return", headers=_h(tid), json={"feedback": "Funksiyaga ajrating"})
    assert r.status_code == 200 and r.json()["status"] == "returned"
    mine = (await async_client.get(f"{STUDENT_API}/{task_id}", headers=_h(sid))).json()
    assert mine["status"] == "returned" and mine["returned_feedback"] == "Funksiyaga ajrating"
    assert (await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=_h(sid), json=_submit_body(code="v2"))).status_code == 200
    assert (await async_client.post(f"{TEACHER_API}/{task_id}/return", headers=_h(tid), json={"feedback": "again"})).status_code == 200


async def test_grading_does_not_touch_the_daily_quota(async_client):
    from app.models.daily_quota import StudentDailyProgress
    tid, sid, task_id = await _submitted(async_client)
    async with AsyncSessionLocal() as db:
        before = (await db.execute(select(func.count()).select_from(StudentDailyProgress)
                                   .where(StudentDailyProgress.student_id == sid))).scalar()
    await async_client.post(f"{TEACHER_API}/{task_id}/grade", headers=_h(tid), json={"points": 10})
    async with AsyncSessionLocal() as db:
        after = (await db.execute(select(func.count()).select_from(StudentDailyProgress)
                                  .where(StudentDailyProgress.student_id == sid))).scalar()
    assert after == before


async def test_another_teacher_cannot_grade_or_return(async_client):
    tid, sid, task_id = await _submitted(async_client)
    other = await _user(teacher=True)
    assert (await async_client.post(f"{TEACHER_API}/{task_id}/grade", headers=_h(other), json={"points": 5})).status_code == 404
    assert (await async_client.post(f"{TEACHER_API}/{task_id}/return", headers=_h(other), json={"feedback": "x"})).status_code == 404


# ── Task 6: notifications ───────────────────────────────────────────────────

async def _notes(recipient_id, type_):
    from app.models.notification import Notification
    async with AsyncSessionLocal() as db:
        return list((await db.execute(select(Notification).where(
            Notification.student_id == recipient_id, Notification.type == type_))).scalars().all())


async def test_creating_a_task_notifies_the_student(async_client):
    tid, sid, task_id = await _task(async_client, title="Bubble sort")
    notes = await _notes(sid, "code_task_assigned")
    assert len(notes) == 1 and notes[0].title == "Bubble sort" and notes[0].link == f"/student/code-tasks/{task_id}"


async def test_submitting_notifies_the_teacher(async_client):
    tid, sid, task_id = await _submitted(async_client, title="Bubble sort")
    notes = await _notes(tid, "code_task_submitted")
    assert len(notes) == 1 and "Bubble sort" in notes[0].title
    assert notes[0].link == f"/teacher/students/{sid}?tab=tasks"


async def test_grading_and_returning_notify_the_student(async_client):
    tid, sid, task_id = await _submitted(async_client)
    await async_client.post(f"{TEACHER_API}/{task_id}/return", headers=_h(tid), json={"feedback": "Qayta urinib ko'ring"})
    returned = await _notes(sid, "code_task_returned")
    assert len(returned) == 1 and returned[0].body == "Qayta urinib ko'ring"
    await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=_h(sid), json=_submit_body(code="v2"))
    await async_client.post(f"{TEACHER_API}/{task_id}/grade", headers=_h(tid), json={"points": 12, "feedback": "Barakalla"})
    graded = await _notes(sid, "code_task_graded")
    assert len(graded) == 1 and graded[0].points == 12 and graded[0].body == "Barakalla" and graded[0].extra == "20"


async def test_a_failing_notification_never_fails_the_request(async_client, monkeypatch):
    from app.services import notification_service

    async def boom(*a, **k):
        raise RuntimeError("socket layer down")

    monkeypatch.setattr(notification_service, "_emit", boom)
    tid, sid = await _teacher_with_student()
    r = await async_client.post(f"{TEACHER_API}/", headers=_h(tid), json=_body(sid))
    assert r.status_code == 201
    task_id = r.json()["id"]
    assert (await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=_h(sid), json=_submit_body())).status_code == 200
    assert (await async_client.post(f"{TEACHER_API}/{task_id}/grade", headers=_h(tid), json={"points": 5})).status_code == 200


# ── review fixes ────────────────────────────────────────────────────────────

async def test_after_submitting_or_returning_the_student_still_sees_their_own_code(async_client):
    tid, sid, task_id = await _task(async_client, starter_code="# start")
    await async_client.post(f"{STUDENT_API}/{task_id}/submit", headers=_h(sid), json=_submit_body(code="my solution"))
    assert (await async_client.get(f"{STUDENT_API}/{task_id}", headers=_h(sid))).json()["code"] == "my solution"
    await async_client.post(f"{TEACHER_API}/{task_id}/return", headers=_h(tid), json={"feedback": "Funksiyaga ajrating"})
    back = (await async_client.get(f"{STUDENT_API}/{task_id}", headers=_h(sid))).json()
    assert back["status"] == "returned" and back["code"] == "my solution"          # edit the attempt, do not retype it
    await async_client.put(f"{STUDENT_API}/{task_id}/draft", headers=_h(sid), json={"code": "my solution v2"})
    assert (await async_client.get(f"{STUDENT_API}/{task_id}", headers=_h(sid))).json()["code"] == "my solution v2"


async def test_the_graded_result_persists_even_when_the_points_call_does_not_commit(async_client, monkeypatch):
    """add_points_to_student returns early (no commit) for a demo student; the grade must not depend on the
    notification that follows happening to commit."""
    from app.services import notification_service

    async def quiet(*a, **k):
        return None

    monkeypatch.setattr(notification_service, "_emit", quiet)
    tid, sid, task_id = await _submitted(async_client)
    async with AsyncSessionLocal() as db:
        (await db.get(Student, sid)).is_demo = True
        await db.commit()
    r = await async_client.post(f"{TEACHER_API}/{task_id}/grade", headers=_h(tid), json={"points": 10})
    assert r.status_code == 200
    async with AsyncSessionLocal() as db:
        task = await db.get(CodeTask, task_id)
        assert task.status == "graded" and task.graded_points == 10
