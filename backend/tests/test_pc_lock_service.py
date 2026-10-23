import uuid

import pytest

from sqlalchemy import delete

from app.db.database import AsyncSessionLocal
from app.models.pc_control import PcDevice, PcCommand
from app.services.pc_lock_service import decide_lock, resolve_override, compute_state


def _uid() -> str:
    return uuid.uuid4().hex[:10]


def test_no_student_always_locked():
    assert decide_lock(has_student=False, override="unlock", quota_unlocked=True) == (True, "no_student")
    assert decide_lock(has_student=False, override=None, quota_unlocked=True) == (True, "no_student")


def test_lock_override_beats_met_quota():
    assert decide_lock(has_student=True, override="lock", quota_unlocked=True) == (True, "teacher_lock")


def test_unlock_override_beats_pending_quota():
    assert decide_lock(has_student=True, override="unlock", quota_unlocked=False) == (False, "teacher_unlock")


def test_no_override_follows_quota():
    assert decide_lock(has_student=True, override=None, quota_unlocked=False) == (True, "quota_pending")
    assert decide_lock(has_student=True, override=None, quota_unlocked=True) == (False, "quota_met")


async def _device(db, group_id=None):
    # DB is shared across tests; start from a clean command table.
    await db.execute(delete(PcCommand))
    d = PcDevice(hostname="lab", machine_key_hash=f"h-{_uid()}", group_id=group_id)
    db.add(d)
    await db.commit()
    await db.refresh(d)
    return d


def _cmd(scope_type, scope_id, type_):
    return PcCommand(scope_type=scope_type, scope_id=scope_id, type=type_, created_by=1)


async def test_device_scope_beats_newer_all_scope():
    async with AsyncSessionLocal() as db:
        d = await _device(db)
        db.add(_cmd("device", d.id, "unlock"))
        await db.commit()
        db.add(_cmd("all", None, "lock"))
        await db.commit()
        assert await resolve_override(db, d) == "unlock"


async def test_later_clear_returns_none():
    async with AsyncSessionLocal() as db:
        d = await _device(db)
        db.add(_cmd("device", d.id, "lock"))
        await db.commit()
        db.add(_cmd("device", d.id, "clear"))
        await db.commit()
        # an all-scope lock exists elsewhere but device-scope clear is most specific
        assert await resolve_override(db, d) is None


async def test_group_command_ignored_for_other_group():
    async with AsyncSessionLocal() as db:
        d = await _device(db, group_id=None)
        db.add(_cmd("group", 987654, "lock"))
        db.add(_cmd("device", d.id, "message"))
        await db.commit()
        assert await resolve_override(db, d) is None


async def test_compute_state_no_session():
    async with AsyncSessionLocal() as db:
        d = await _device(db)
        st = await compute_state(db, d)
        assert st["locked"] is True
        assert st["reason"] == "no_student"
        assert st["student"] is None
        assert (st["remaining"], st["completed"], st["required"]) == (0, 0, 0)
        assert "code.exe" in [a["exe"] for a in st["allowlist"]]
        assert isinstance(st["browser_hosts"], list)
        assert st["server_time"]
