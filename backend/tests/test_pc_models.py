import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.security import get_password_hash
from app.db.database import AsyncSessionLocal
from app.models.pc_control import PcDevice, PcSession, PcUsageEvent, PcCommand
from app.models.user import Student, UserRole


def _uid() -> str:
    return uuid.uuid4().hex[:10]


async def test_can_create_device_session_usage_and_command():
    async with AsyncSessionLocal() as db:
        uid = _uid()
        student = Student(
            username=f"pc_{uid}", email=f"pc_{uid}@example.com", full_name="PC Student",
            hashed_password=get_password_hash("x"), role=UserRole.student,
        )
        device = PcDevice(hostname="lab-01", machine_key_hash=f"hash-{uid}")
        db.add_all([student, device])
        await db.commit()

        sess = PcSession(device_id=device.id, student_id=student.id)
        db.add(sess)
        await db.commit()

        usage = PcUsageEvent(session_id=sess.id, app_name="code.exe")
        cmd = PcCommand(scope_type="device", scope_id=device.id, type="lock", created_by=student.id)
        db.add_all([usage, cmd])
        await db.commit()

        for obj in (device, sess, usage, cmd):
            await db.refresh(obj)
            assert obj.id is not None
        assert sess.signed_out_at is None
        assert usage.was_locked is False
        assert device.group_id is None


async def test_machine_key_hash_unique():
    h = f"dup-{_uid()}"
    async with AsyncSessionLocal() as db:
        db.add(PcDevice(hostname="a", machine_key_hash=h))
        await db.commit()
    async with AsyncSessionLocal() as db:
        db.add(PcDevice(hostname="b", machine_key_hash=h))
        with pytest.raises(IntegrityError):
            await db.commit()
