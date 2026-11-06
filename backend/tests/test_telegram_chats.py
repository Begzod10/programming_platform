"""Teacher's Telegram chats: link code, student selection (scoped to the teacher), disconnect."""
import re
import uuid
from datetime import timedelta

from sqlalchemy import delete, select, func

from app.core.security import create_access_token
from app.db.database import AsyncSessionLocal
from app.models.group import Group, student_groups
from app.models.ranking import Ranking
from app.models.telegram_chat import TelegramChat, TelegramChatStudent
from app.models.user import Student, UserRole
from app.utils.datetime_utils import utcnow

BASE = "/api/v1/teacher/telegram"


async def _teacher(async_client):
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post("/api/v1/auth/register", json={
        "username": f"tg_{uid}", "email": f"tg_{uid}@example.com", "password": "securepass123"})
    assert reg.status_code == 201, reg.text
    tid = reg.json()["user"]["id"]
    async with AsyncSessionLocal() as db:
        s = (await db.execute(select(Student).where(Student.id == tid))).scalar_one()
        s.role = UserRole.teacher
        await db.execute(delete(Ranking).where(Ranking.student_id == tid))
        await db.commit()
    return tid, {"Authorization": f"Bearer {create_access_token(subject=tid)}"}


async def _student(*, group_id=None, name=None, demo=False, active=True):
    uid = uuid.uuid4().hex[:8]
    async with AsyncSessionLocal() as db:
        s = Student(username=f"ts_{uid}", email=f"ts_{uid}@example.com", hashed_password="x",
                    full_name=name or f"Oquvchi {uid}", is_demo=demo, is_active=active)
        db.add(s)
        await db.flush()
        if group_id:
            await db.execute(student_groups.insert().values(student_id=s.id, group_id=group_id))
        await db.commit()
        return s.id


async def _group(teacher_id, name=None):
    async with AsyncSessionLocal() as db:
        g = Group(name=name or f"g_{uuid.uuid4().hex[:6]}", teacher_id=teacher_id)
        db.add(g)
        await db.commit()
        return g.id


async def _chat(teacher_id, *, selected=(), title="7-sinf", active=True):
    async with AsyncSessionLocal() as db:
        c = TelegramChat(chat_id=-(10**12 + uuid.uuid4().int % 10**9), title=title, teacher_id=teacher_id, is_active=active)
        db.add(c)
        await db.flush()
        for sid in selected:
            db.add(TelegramChatStudent(chat_row_id=c.id, student_id=sid))
        await db.commit()
        return c.id


async def _selected(chat_row_id):
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(select(TelegramChatStudent.student_id)
                                 .where(TelegramChatStudent.chat_row_id == chat_row_id))).scalars().all()
        return sorted(rows)


async def test_link_code_is_24_telegram_safe_chars_valid_for_one_hour(async_client):
    _, th = await _teacher(async_client)
    r = await async_client.post(f"{BASE}/link-code", headers=th)
    assert r.status_code == 200, r.text
    body = r.json()
    assert re.fullmatch(r"[A-Za-z0-9_-]{24}", body["code"])
    assert body["url"] == f"https://t.me/gennis_parent_bot?startgroup={body['code']}"
    from datetime import datetime
    exp = datetime.fromisoformat(body["expires_at"].replace("Z", "+00:00"))
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=utcnow().tzinfo)
    assert timedelta(minutes=59) < exp - utcnow() < timedelta(minutes=61)


async def test_a_student_cannot_create_a_code(async_client):
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post("/api/v1/auth/register", json={
        "username": f"tg_{uid}", "email": f"tg_{uid}@example.com", "password": "securepass123"})
    h = {"Authorization": f"Bearer {create_access_token(subject=reg.json()['user']['id'])}"}
    assert (await async_client.post(f"{BASE}/link-code", headers=h)).status_code == 403


async def test_students_list_has_only_my_active_non_demo_students_with_class_labels(async_client):
    tid, th = await _teacher(async_client)
    other, _ = await _teacher(async_client)
    gid = await _group(tid, "7-A")
    ali = await _student(group_id=gid, name="Ali Valiyev")
    await _student(group_id=gid, name="Demo Bola", demo=True)
    await _student(group_id=gid, name="Nofaol Bola", active=False)
    await _student(group_id=await _group(other), name="Begona Bola")

    rows = (await async_client.get(f"{BASE}/students", headers=th)).json()
    assert [r["name"] for r in rows] == ["Ali Valiyev"]
    assert rows[0]["id"] == ali and rows[0]["classes"] == ["7-A"]
    found = (await async_client.get(f"{BASE}/students?search=valiy", headers=th)).json()
    assert [r["name"] for r in found] == ["Ali Valiyev"]
    assert (await async_client.get(f"{BASE}/students?search=zzz", headers=th)).json() == []


async def test_put_students_replaces_the_selection(async_client):
    tid, th = await _teacher(async_client)
    gid = await _group(tid)
    a, b = await _student(group_id=gid), await _student(group_id=gid)
    chat = await _chat(tid)
    r = await async_client.put(f"{BASE}/chats/{chat}/students", headers=th, json={"student_ids": [a, b]})
    assert r.status_code == 200 and len(r.json()["students"]) == 2
    r = await async_client.put(f"{BASE}/chats/{chat}/students", headers=th, json={"student_ids": [b]})
    assert [s["id"] for s in r.json()["students"]] == [b]
    assert await _selected(chat) == [b]


async def test_put_with_a_student_outside_my_scope_is_403_and_saves_nothing(async_client):
    tid, th = await _teacher(async_client)
    other, _ = await _teacher(async_client)
    mine = await _student(group_id=await _group(tid))
    foreign = await _student(group_id=await _group(other))
    chat = await _chat(tid, selected=[mine])
    r = await async_client.put(f"{BASE}/chats/{chat}/students", headers=th, json={"student_ids": [mine, foreign]})
    assert r.status_code == 403
    assert await _selected(chat) == [mine]                     # the old selection is untouched


async def test_chats_are_private_to_their_teacher(async_client):
    tid, th = await _teacher(async_client)
    _, other_h = await _teacher(async_client)
    chat = await _chat(tid, title="Mening guruhim")
    assert [c["title"] for c in (await async_client.get(f"{BASE}/chats", headers=th)).json()] == ["Mening guruhim"]
    assert (await async_client.get(f"{BASE}/chats", headers=other_h)).json() == []
    assert (await async_client.put(f"{BASE}/chats/{chat}/students", headers=other_h, json={"student_ids": []})).status_code == 404
    assert (await async_client.delete(f"{BASE}/chats/{chat}", headers=other_h)).status_code == 404


async def test_delete_removes_the_chat_and_its_selection(async_client):
    tid, th = await _teacher(async_client)
    s = await _student(group_id=await _group(tid))
    chat = await _chat(tid, selected=[s])
    assert (await async_client.delete(f"{BASE}/chats/{chat}", headers=th)).status_code == 204
    async with AsyncSessionLocal() as db:
        assert (await db.execute(select(func.count(TelegramChat.id)).where(TelegramChat.id == chat))).scalar() == 0
        assert (await db.execute(select(func.count()).select_from(TelegramChatStudent)
                                 .where(TelegramChatStudent.chat_row_id == chat))).scalar() == 0
