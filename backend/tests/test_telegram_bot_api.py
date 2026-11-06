"""Bot-facing Telegram API: verify a link code, list the active chats with their students, unlink."""
import uuid
from datetime import timedelta

import pytest
from sqlalchemy import select, func

from app.config import settings
from app.db.database import AsyncSessionLocal
from app.models.group import student_groups
from app.models.telegram_chat import TelegramChat, TelegramChatStudent, TelegramLinkCode
from app.models.user import Student
from app.services import telegram_chats as svc
from app.utils.datetime_utils import utcnow
from tests.test_telegram_chats import _teacher, _student, _group, _chat, _selected

SECRET = {"X-Internal-Secret": "test-secret"}
BOT = "/api/v1/bot/telegram"


@pytest.fixture(autouse=True)
def secret(monkeypatch):
    monkeypatch.setattr(settings, "PARENT_BOT_SECRET", "test-secret")


async def _code(teacher_id):
    async with AsyncSessionLocal() as db:
        return (await svc.create_link_code(db, teacher_id)).code


def _chat_id():
    return -(10**12 + uuid.uuid4().int % 10**9)


async def _link(async_client, code, chat_id, title="7-sinf"):
    return await async_client.post(f"{BOT}/link", headers=SECRET,
                                   json={"code": code, "chat_id": chat_id, "chat_title": title})


async def _row(chat_id):
    async with AsyncSessionLocal() as db:
        return (await db.execute(select(TelegramChat).where(TelegramChat.chat_id == chat_id))).scalar_one_or_none()


async def test_link_attaches_the_chat_to_the_code_owner_and_burns_the_code(async_client):
    tid, _ = await _teacher(async_client)
    code, chat_id = await _code(tid), _chat_id()
    r = await _link(async_client, code, chat_id)
    assert r.status_code == 200, r.text
    assert r.json()["ok"] is True and r.json()["teacher_name"]
    row = await _row(chat_id)
    assert row.teacher_id == tid and row.is_active and row.title == "7-sinf"
    async with AsyncSessionLocal() as db:
        assert (await db.execute(select(TelegramLinkCode.used_at).where(TelegramLinkCode.code == code))).scalar() is not None


async def test_a_used_or_expired_code_is_404_and_changes_nothing(async_client):
    tid, _ = await _teacher(async_client)
    code = await _code(tid)
    assert (await _link(async_client, code, _chat_id())).status_code == 200
    again_chat = _chat_id()
    assert (await _link(async_client, code, again_chat)).status_code == 404
    assert await _row(again_chat) is None

    expired = await _code(tid)
    async with AsyncSessionLocal() as db:
        row = (await db.execute(select(TelegramLinkCode).where(TelegramLinkCode.code == expired))).scalar_one()
        row.expires_at = utcnow() - timedelta(minutes=1)
        await db.commit()
    late_chat = _chat_id()
    assert (await _link(async_client, expired, late_chat)).status_code == 404
    assert await _row(late_chat) is None
    assert (await _link(async_client, "no-such-code-at-all-xx", _chat_id())).status_code == 404


async def test_a_chat_linked_to_another_teacher_is_409(async_client):
    a, _ = await _teacher(async_client)
    b, _ = await _teacher(async_client)
    chat_id = _chat_id()
    assert (await _link(async_client, await _code(a), chat_id)).status_code == 200
    assert (await _link(async_client, await _code(b), chat_id)).status_code == 409
    assert (await _row(chat_id)).teacher_id == a
    assert (await _link(async_client, await _code(a), chat_id)).status_code == 200      # the owner may re-link


async def test_relinking_a_removed_chat_reactivates_it(async_client):
    a, _ = await _teacher(async_client)
    b, _ = await _teacher(async_client)
    mine = await _student(group_id=await _group(a))
    chat_row = await _chat(a, selected=[mine], active=False)
    async with AsyncSessionLocal() as db:
        chat_id = (await db.execute(select(TelegramChat.chat_id).where(TelegramChat.id == chat_row))).scalar_one()

    assert (await _link(async_client, await _code(a), chat_id)).status_code == 200      # same owner keeps the selection
    assert (await _row(chat_id)).is_active and await _selected(chat_row) == [mine]

    async with AsyncSessionLocal() as db:                                               # the bot is removed again
        await svc.deactivate_chat(db, chat_id)
    assert (await _link(async_client, await _code(b), chat_id)).status_code == 200      # a different teacher takes it
    row = await _row(chat_id)
    assert row.is_active and row.teacher_id == b and await _selected(chat_row) == []


async def test_chats_list_has_only_in_scope_active_students(async_client):
    tid, _ = await _teacher(async_client)
    gid = await _group(tid)
    keep, left, demo, inactive = (await _student(group_id=gid, name="Qoladi"), await _student(group_id=gid, name="Ketdi"),
                                  await _student(group_id=gid, name="Demo", demo=True),
                                  await _student(group_id=gid, name="Nofaol", active=False))
    chat_row = await _chat(tid, selected=[keep, left, demo, inactive], title="Guruh A")
    await _chat(tid, selected=[keep], title="Chiqarilgan", active=False)
    async with AsyncSessionLocal() as db:                                               # `left` leaves the teacher's class
        await db.execute(student_groups.delete().where(student_groups.c.student_id == left))
        await db.commit()

    rows = (await async_client.get(f"{BOT}/chats", headers=SECRET)).json()
    mine = [r for r in rows if r["title"] == "Guruh A"]
    assert len(mine) == 1 and [s["name"] for s in mine[0]["students"]] == ["Qoladi"]
    assert not [r for r in rows if r["title"] == "Chiqarilgan"]                         # inactive chats are not reported
    assert chat_row                                                                     # row kept for the teacher


async def test_unlink_deactivates_and_reports_found(async_client):
    tid, th = await _teacher(async_client)
    chat_id = _chat_id()
    await _link(async_client, await _code(tid), chat_id, "Guruh B")
    r = await async_client.post(f"{BOT}/unlink", headers=SECRET, json={"chat_id": chat_id})
    assert r.json() == {"ok": True, "found": True}
    assert not (await _row(chat_id)).is_active
    assert not [c for c in (await async_client.get(f"{BOT}/chats", headers=SECRET)).json() if c["title"] == "Guruh B"]
    mine = (await async_client.get("/api/v1/teacher/telegram/chats", headers=th)).json()
    assert [c["is_active"] for c in mine if c["title"] == "Guruh B"] == [False]
    r = await async_client.post(f"{BOT}/unlink", headers=SECRET, json={"chat_id": _chat_id()})
    assert r.json() == {"ok": True, "found": False}


async def test_the_secret_is_required(async_client, monkeypatch):
    assert (await async_client.get(f"{BOT}/chats")).status_code == 401
    assert (await async_client.get(f"{BOT}/chats", headers={"X-Internal-Secret": "nope"})).status_code == 401
    assert (await async_client.post(f"{BOT}/unlink", json={"chat_id": 1})).status_code == 401
    monkeypatch.setattr(settings, "PARENT_BOT_SECRET", "")
    assert (await async_client.get(f"{BOT}/chats", headers=SECRET)).status_code == 503
