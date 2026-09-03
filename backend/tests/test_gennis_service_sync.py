"""Regression test for the stale-group/stale-flow cleanup bug in
GennisService.sync_teacher_data (fixed 2026-09-03).

Reproduced live: turon teacher rimefara_teach_turon (turon_id 19146) kept
showing group "1-blue" in student_platform's "Мои студенты" long after their
only timetable assignment to it was soft-deleted on the turon side. Root
cause: the stale-cleanup queries were guarded by `if current_ext_ids:`,
which skipped cleanup whenever the login response's group/flow list came
back empty — but sync_teacher_data is only ever called after a *successful*
login (see auth_service.login), so an empty list there is never an API
hiccup, it's an authoritative "this teacher has zero groups/flows now".
"""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.core.security import get_password_hash
from app.models.flow import Flow
from app.models.group import Group
from app.models.user import Student, UserRole
from app.services.gennis_service import GennisService


@pytest_asyncio.fixture
async def turon_teacher(db_session) -> Student:
    uid = uuid.uuid4().hex[:8]
    teacher = Student(
        username=f"teach_{uid}",
        email=f"teach_{uid}@turon.uz",
        hashed_password=get_password_hash("irrelevant"),
        role=UserRole.teacher,
        is_active=True,
        turon_id=19146,
    )
    db_session.add(teacher)
    await db_session.commit()
    await db_session.refresh(teacher)
    return teacher


def _login_data(groups: list, flows: list | None = None) -> dict:
    """Shape of a real, successful management-v2 shim response — see
    student_platform_login's turon branch in
    management-v2/app/routers/v1/integrations/student_platform.py."""
    return {
        "access_token": "tok",
        "source": "turon",
        "user": {
            "id": 19146,
            "name": "Test",
            "surname": "Teacher",
            "role": "teacher",
            "phone": [],
            "teacher": {"group": groups, "flow": flows or []},
        },
    }


@pytest.mark.asyncio
async def test_group_released_when_teacher_now_has_zero_groups(db_session, turon_teacher, monkeypatch):
    """A group the teacher previously owned must be released (teacher_id =
    NULL) once a real, successful login reports zero groups — not kept
    forever, which was the bug."""
    # turon_id (and Group.name) are unique columns, and test.db is a real
    # file that persists across pytest invocations (see conftest.py) — a
    # fixed literal here collides with a leftover row from a prior run.
    group_turon_id = int(uuid.uuid4().int % 1_000_000_000)
    stale_group = Group(name=f"1-blue-test-{group_turon_id}", turon_id=group_turon_id, teacher_id=turon_teacher.id)
    db_session.add(stale_group)
    await db_session.commit()

    async def _no_students(*args, **kwargs):
        return []

    monkeypatch.setattr(GennisService, "fetch_group_students", classmethod(_no_students))

    await GennisService.sync_teacher_data(
        db_session, turon_teacher, _login_data(groups=[]), system="turon"
    )

    refreshed = (
        await db_session.execute(select(Group).where(Group.id == stale_group.id))
    ).scalar_one()
    assert refreshed.teacher_id is None


@pytest.mark.asyncio
async def test_flow_released_when_teacher_now_has_zero_flows(db_session, turon_teacher, monkeypatch):
    flow_turon_id = int(uuid.uuid4().int % 1_000_000_000)
    stale_flow = Flow(name=f"flow-test-{flow_turon_id}", turon_id=flow_turon_id, teacher_id=turon_teacher.id)
    db_session.add(stale_flow)
    await db_session.commit()

    async def _no_students(*args, **kwargs):
        return []

    monkeypatch.setattr(GennisService, "fetch_group_students", classmethod(_no_students))
    monkeypatch.setattr(GennisService, "fetch_flow_students", classmethod(_no_students))

    await GennisService.sync_teacher_data(
        db_session, turon_teacher, _login_data(groups=[], flows=[]), system="turon"
    )

    refreshed = (
        await db_session.execute(select(Flow).where(Flow.id == stale_flow.id))
    ).scalar_one()
    assert refreshed.teacher_id is None


@pytest.mark.asyncio
async def test_active_group_still_synced_with_students(db_session, turon_teacher, monkeypatch):
    """Sanity check the fix didn't break the normal (non-empty) path: a
    group still reported by login stays assigned and its students sync."""
    group_turon_id = int(uuid.uuid4().int % 1_000_000_000)
    student_turon_id = int(uuid.uuid4().int % 1_000_000_000)

    async def _one_student(*args, **kwargs):
        return [{"id": student_turon_id, "name": "Ali", "surname": "Valiyev"}]

    monkeypatch.setattr(GennisService, "fetch_group_students", classmethod(_one_student))

    await GennisService.sync_teacher_data(
        db_session,
        turon_teacher,
        _login_data(groups=[{"id": group_turon_id, "name": f"1-blue-test-{group_turon_id}", "price": 0}]),
        system="turon",
    )

    group = (
        await db_session.execute(select(Group).where(Group.turon_id == group_turon_id))
    ).scalar_one()
    assert group.teacher_id == turon_teacher.id

    student = (
        await db_session.execute(select(Student).where(Student.turon_id == student_turon_id))
    ).scalar_one()
    assert student in group.students
