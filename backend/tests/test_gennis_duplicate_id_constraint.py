"""Regression tests for the 2026-09-14 duplicate-turon_id incident: two
Student rows both had turon_id=19042, which corrupted a teacher's roster
sync and crashed login for everyone with that student in a group/flow.

Two things needed fixing, both covered here:
1. The DB now actually enforces uniqueness (ux_students_turon_id /
   ux_students_gennis_id, partial unique indexes — see
   database.py::_reconcile_indexes and the matching Alembic migration).
2. That constraint creates a NEW possible failure mode:
   GennisService._sync_container_student's own "row doesn't exist yet,
   create it" branch can now lose a race against a concurrent sync for
   the same brand-new turon_id/gennis_id and hit an IntegrityError on
   insert instead of silently duplicating. It must recover by picking up
   the row that won, not crash the login.
"""
import uuid

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.db.database import AsyncSessionLocal
from app.models.group import Group
from app.models.user import Student
from app.services.gennis_service import GennisService


async def test_duplicate_turon_id_is_rejected_at_the_db_level(db_session):
    """The actual constraint this whole incident was missing."""
    tid = 900_000_001
    a = Student(
        username=f"dup_a_{uuid.uuid4().hex[:8]}", email=f"dup_a_{uuid.uuid4().hex[:8]}@turon.uz",
        full_name="A", hashed_password="external_auth", role="student", turon_id=tid,
    )
    db_session.add(a)
    await db_session.commit()

    b = Student(
        username=f"dup_b_{uuid.uuid4().hex[:8]}", email=f"dup_b_{uuid.uuid4().hex[:8]}@turon.uz",
        full_name="B", hashed_password="external_auth", role="student", turon_id=tid,
    )
    db_session.add(b)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


async def test_duplicate_gennis_id_is_rejected_at_the_db_level(db_session):
    gid = 900_000_002
    a = Student(
        username=f"dup_g_a_{uuid.uuid4().hex[:8]}", email=f"dup_g_a_{uuid.uuid4().hex[:8]}@gennis.uz",
        full_name="A", hashed_password="external_auth", role="student", gennis_id=gid,
    )
    db_session.add(a)
    await db_session.commit()

    b = Student(
        username=f"dup_g_b_{uuid.uuid4().hex[:8]}", email=f"dup_g_b_{uuid.uuid4().hex[:8]}@gennis.uz",
        full_name="B", hashed_password="external_auth", role="student", gennis_id=gid,
    )
    db_session.add(b)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


async def test_multiple_null_turon_ids_are_still_allowed(db_session):
    """The partial index (WHERE turon_id IS NOT NULL) — and Postgres/SQLite's
    own NULL-is-distinct-from-NULL unique semantics — must not block the
    overwhelming majority of students who simply have no turon_id at all."""
    a = Student(
        username=f"null_a_{uuid.uuid4().hex[:8]}", email=f"null_a_{uuid.uuid4().hex[:8]}@example.com",
        full_name="A", hashed_password="x", role="student", turon_id=None,
    )
    b = Student(
        username=f"null_b_{uuid.uuid4().hex[:8]}", email=f"null_b_{uuid.uuid4().hex[:8]}@example.com",
        full_name="B", hashed_password="x", role="student", turon_id=None,
    )
    db_session.add_all([a, b])
    await db_session.commit()  # must not raise


async def test_sync_container_student_recovers_from_concurrent_duplicate_insert(db_session):
    """Simulates two near-simultaneous syncs for the same brand-new
    turon_id: both would see 'no existing row' and both attempt an
    INSERT. Reproduced here by having a genuinely separate session commit
    the 'winning' row first, then forcing this call's own duplicate-check
    to see what it would have seen a moment earlier (empty) — the
    interleaving a real race produces, without needing actual threads.
    """
    group = Group(name=f"RaceGrp_{uuid.uuid4().hex[:6]}", teacher_id=1)
    db_session.add(group)
    await db_session.commit()

    turon_id = 900_000_003
    s_data = {"id": turon_id, "name": "Race", "surname": "Test", "username": "race_test", "phone": "1"}

    async with AsyncSessionLocal() as other_session:
        winner = Student(
            username="race_winner", email="race_winner@turon.uz",
            full_name="Race Winner", hashed_password="external_auth",
            role="student", turon_id=turon_id,
        )
        other_session.add(winner)
        await other_session.commit()
        winner_id = winner.id

    class _EmptyResult:
        def scalars(self):
            return self

        def all(self):
            return []

    real_execute = db_session.execute
    intercepted = {"done": False}

    async def execute_with_stale_read(statement, *args, **kwargs):
        if not intercepted["done"] and "turon_id" in str(statement):
            intercepted["done"] = True
            return _EmptyResult()
        return await real_execute(statement, *args, **kwargs)

    db_session.execute = execute_with_stale_read
    try:
        result = await GennisService._sync_student(db_session, s_data, group.id, system="turon")
    finally:
        db_session.execute = real_execute

    assert result.id == winner_id
    assert result.full_name == "Race Winner"

    count = (await db_session.execute(
        select(func.count()).select_from(Student).where(Student.turon_id == turon_id)
    )).scalar()
    assert count == 1, "the race must not leave a duplicate row behind"
