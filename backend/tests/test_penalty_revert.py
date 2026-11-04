"""Reverting a teacher penalty ("jarimani qaytarish"): exact refund, once only, teacher's own students, student told."""
import uuid

from sqlalchemy import delete, select

from app.core.security import create_access_token
from app.db.database import AsyncSessionLocal
from app.models.group import Group, student_groups
from app.models.notification import Notification
from app.models.ranking import Ranking
from app.models.teacher_penalty import TeacherPenalty
from app.models.user import Student, UserRole

BASE = "/api/v1/teacher/penalties"


async def _user(async_client, role=None):
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post("/api/v1/auth/register", json={
        "username": f"pr_{uid}", "email": f"pr_{uid}@example.com", "password": "securepass123"})
    assert reg.status_code == 201, reg.text
    sid = reg.json()["user"]["id"]
    if role:
        async with AsyncSessionLocal() as db:
            s = (await db.execute(select(Student).where(Student.id == sid))).scalar_one()
            s.role = role
            await db.execute(delete(Ranking).where(Ranking.student_id == sid))
            await db.commit()
    return sid, {"Authorization": f"Bearer {create_access_token(subject=sid)}"}


async def _setup(async_client, *, lifetime=1000, wallet=1000):
    """A teacher with a group holding one student who has the given balances."""
    tid, th = await _user(async_client, role=UserRole.teacher)
    sid, _ = await _user(async_client)
    async with AsyncSessionLocal() as db:
        g = Group(name=f"g_{uuid.uuid4().hex[:6]}", teacher_id=tid)
        db.add(g)
        await db.flush()
        await db.execute(student_groups.insert().values(student_id=sid, group_id=g.id))
        s = (await db.execute(select(Student).where(Student.id == sid))).scalar_one()
        s.lifetime_points, s.total_points = lifetime, wallet
        await db.commit()
    return tid, th, sid


async def _balances(sid):
    async with AsyncSessionLocal() as db:
        s = (await db.execute(select(Student).where(Student.id == sid))).scalar_one()
        r = (await db.execute(select(Ranking).where(Ranking.student_id == sid))).scalar_one_or_none()
        return s.lifetime_points, s.total_points, (r.total_points if r else None)


async def _penalise(async_client, th, sid, amount):
    r = await async_client.post(BASE, headers=th, json={"student_id": sid, "amount": amount, "penalty_type": "plagiarism"})
    assert r.status_code == 200, r.text
    return r.json()["penalty"]["id"]


async def test_reverting_gives_back_exactly_what_the_penalty_took(async_client):
    tid, th, sid = await _setup(async_client)
    pid = await _penalise(async_client, th, sid, 300)
    assert (await _balances(sid))[:2] == (700, 700)

    r = await async_client.post(f"{BASE}/{pid}/revert", headers=th)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["refunded_points"] == 300 and body["refunded_wallet"] == 300 and body["reverted_at"]
    lifetime, wallet, ranking = await _balances(sid)
    assert (lifetime, wallet) == (1000, 1000) and ranking in (None, 1000)


async def test_a_spent_wallet_is_not_topped_up_beyond_what_was_taken(async_client):
    # rating 1000 but only 200 left in the wallet: a 500 penalty takes 500 rating and just 200 wallet
    tid, th, sid = await _setup(async_client, lifetime=1000, wallet=200)
    pid = await _penalise(async_client, th, sid, 500)
    assert (await _balances(sid))[:2] == (500, 0)

    r = await async_client.post(f"{BASE}/{pid}/revert", headers=th)
    assert r.status_code == 200
    assert (r.json()["refunded_points"], r.json()["refunded_wallet"]) == (500, 200)
    assert (await _balances(sid))[:2] == (1000, 200)


async def test_a_penalty_can_be_reverted_only_once(async_client):
    tid, th, sid = await _setup(async_client)
    pid = await _penalise(async_client, th, sid, 100)
    assert (await async_client.post(f"{BASE}/{pid}/revert", headers=th)).status_code == 200
    again = await async_client.post(f"{BASE}/{pid}/revert", headers=th)
    assert again.status_code == 409
    assert (await _balances(sid))[:2] == (1000, 1000)          # not 1100


async def test_an_old_penalty_without_a_stored_wallet_part_refunds_only_the_rating(async_client):
    tid, th, sid = await _setup(async_client)
    pid = await _penalise(async_client, th, sid, 100)
    async with AsyncSessionLocal() as db:
        p = (await db.execute(select(TeacherPenalty).where(TeacherPenalty.id == pid))).scalar_one()
        p.wallet_deducted = None                                # as before this feature existed
        await db.commit()
    r = await async_client.post(f"{BASE}/{pid}/revert", headers=th)
    assert r.json()["refunded_points"] == 100 and r.json()["refunded_wallet"] == 0
    assert (await _balances(sid))[:2] == (1000, 900)


async def test_only_a_teacher_of_that_student_may_revert(async_client):
    tid, th, sid = await _setup(async_client)
    pid = await _penalise(async_client, th, sid, 100)

    _, other_teacher = await _user(async_client, role=UserRole.teacher)
    assert (await async_client.post(f"{BASE}/{pid}/revert", headers=other_teacher)).status_code == 403
    _, a_student = await _user(async_client)
    assert (await async_client.post(f"{BASE}/{pid}/revert", headers=a_student)).status_code == 403
    assert (await async_client.post(f"{BASE}/999999999/revert", headers=th)).status_code == 404
    assert (await _balances(sid))[:2] == (900, 900)            # nothing moved


async def test_another_teacher_of_the_same_student_may_revert_and_is_named(async_client):
    tid, th, sid = await _setup(async_client)
    pid = await _penalise(async_client, th, sid, 100)
    t2, th2 = await _user(async_client, role=UserRole.teacher)
    async with AsyncSessionLocal() as db:
        g = Group(name=f"g_{uuid.uuid4().hex[:6]}", teacher_id=t2)
        db.add(g)
        await db.flush()
        await db.execute(student_groups.insert().values(student_id=sid, group_id=g.id))
        await db.commit()

    assert (await async_client.post(f"{BASE}/{pid}/revert", headers=th2)).status_code == 200
    rows = (await async_client.get(f"{BASE}?student_id={sid}", headers=th)).json()
    row = next(x for x in rows if x["id"] == pid)
    assert row["reverted_at"] and row["reverted_by_name"] and row["refunded_points"] == 100


async def test_the_student_gets_a_notification(async_client):
    tid, th, sid = await _setup(async_client)
    pid = await _penalise(async_client, th, sid, 250)
    await async_client.post(f"{BASE}/{pid}/revert", headers=th)
    async with AsyncSessionLocal() as db:
        notes = (await db.execute(
            select(Notification).where(Notification.student_id == sid, Notification.type == "penalty_reverted")
        )).scalars().all()
    assert len(notes) == 1 and notes[0].points == 250 and notes[0].extra == "plagiarism"


async def test_a_new_penalty_records_the_wallet_part(async_client):
    tid, th, sid = await _setup(async_client, lifetime=1000, wallet=50)
    pid = await _penalise(async_client, th, sid, 300)
    async with AsyncSessionLocal() as db:
        p = (await db.execute(select(TeacherPenalty).where(TeacherPenalty.id == pid))).scalar_one()
    assert p.wallet_deducted == 50 and p.reverted_at is None
