"""A student's balance must follow gennis on every login — but a login payload
that carries NO balance must never reset it to 0."""
import uuid
from types import SimpleNamespace

import pytest

from app.models.user import Student, UserRole
from app.services.gennis_service import GennisService


@pytest.mark.parametrize("args,expected", [
    ((1500,), 1500),
    ((-200000,), -200000),
    ((0,), 0),                       # a real zero is a value
    (("12000",), 12000),
    ((None, -50), -50),              # the helper itself takes the first usable value
    ((None, None), None),            # nothing sent -> no value
    (("abc",), None),
    ((True,), None),
    ((), None),
])
def test_balance_from(args, expected):
    assert GennisService._balance_from(*args) == expected


def _login(balance_key=None, **student_info):
    user = {"name": "Ali", "surname": "Valiyev", "phone": [], "student": student_info}
    if balance_key is not None:
        user["balance"] = balance_key
    return {"access_token": "tok", "user": user}


async def _student(db_session, balance):
    s = Student(username=f"bal_{uuid.uuid4().hex[:8]}", email=f"{uuid.uuid4().hex[:8]}@x.uz",
                hashed_password="x", role=UserRole.student, balance=balance)
    db_session.add(s)
    await db_session.commit()
    await db_session.refresh(s)
    return s


async def test_login_updates_the_balance(db_session):
    s = await _student(db_session, 100)
    await GennisService.sync_student_data(db_session, s, _login(balance_key=-250000))
    await db_session.refresh(s)
    assert s.balance == -250000


async def test_combined_debt_is_a_price_not_a_balance(db_session):
    """combined_debt is the group price (always >= 0): storing it as the balance
    wiped out real debts and invented positive balances."""
    s = await _student(db_session, -70000)
    await GennisService.sync_student_data(db_session, s, _login(combined_debt=430000))
    await db_session.refresh(s)
    assert s.balance == -70000


async def test_the_real_balance_wins_even_when_combined_debt_is_present(db_session):
    s = await _student(db_session, 0)
    await GennisService.sync_student_data(db_session, s, _login(balance_key=-120000, combined_debt=430000))
    await db_session.refresh(s)
    assert s.balance == -120000


async def test_login_without_any_balance_keeps_the_existing_one(db_session):
    s = await _student(db_session, -90000)
    await GennisService.sync_student_data(db_session, s, _login())
    await db_session.refresh(s)
    assert s.balance == -90000       # used to be overwritten with 0


# ── name and photo come from the source ──────────────────────────────────────

async def test_login_restores_the_name_from_the_source(db_session):
    s = await _student(db_session, 0)
    s.full_name, s.surname = "Student O'zgartirgan", "Ism"
    await db_session.commit()
    await GennisService.sync_student_data(db_session, s, _login())
    await db_session.refresh(s)
    assert (s.full_name, s.surname) == ("Ali Valiyev", "Valiyev")


async def test_a_payload_without_a_name_keeps_the_stored_one(db_session):
    s = await _student(db_session, 0)
    s.full_name, s.surname = "Ali Valiyev", "Valiyev"
    await db_session.commit()
    await GennisService.sync_student_data(db_session, s, {"access_token": "t", "user": {"student": {}}})
    await db_session.refresh(s)
    assert (s.full_name, s.surname) == ("Ali Valiyev", "Valiyev")


# ── no profile photos for gennis/turon students: everyone shows the empty icon ──

@pytest.mark.parametrize("source_photo", [
    "https://admin.tisedu.uz/static/profile_photos/a9e7.jpg", None, "", "static/img_folder/x.jpg", "MISSING",
])
async def test_login_clears_the_photo_whatever_the_source_sends(db_session, source_photo):
    s = await _student(db_session, 0)
    s.avatar_url = "/uploads/avatars/uploaded-before.jpg"
    await db_session.commit()
    login = _login()
    if source_photo != "MISSING":
        login["user"]["photo_url"] = source_photo
    await GennisService.sync_student_data(db_session, s, login)
    await db_session.refresh(s)
    assert s.avatar_url is None


def test_clear_student_photo():
    s = SimpleNamespace(avatar_url="https://admin.tisedu.uz/static/profile_photos/a.jpg")
    GennisService._clear_student_photo(s)
    assert s.avatar_url is None


async def test_the_startup_migration_clears_photos_of_linked_students_only(db_session):
    """database.py::_reconcile_indexes runs on every start; its avatar statement
    drops photos of gennis/turon STUDENTS and leaves everyone else alone."""
    from sqlalchemy import text, select
    from app.db import database

    class Recorder:
        def __init__(self): self.sql = []
        async def execute(self, stmt): self.sql.append(str(stmt))
    rec = Recorder()
    await database._reconcile_indexes(rec)
    update = next(q for q in rec.sql if q.startswith("UPDATE students SET avatar_url"))

    linked = await _student(db_session, 0); turon = await _student(db_session, 0)
    local = await _student(db_session, 0); teacher = await _student(db_session, 0)
    linked.gennis_id, turon.turon_id = 880001, 880002
    teacher.gennis_id, teacher.role = 880003, UserRole.teacher
    for st in (linked, turon, local, teacher):
        st.avatar_url = f"/uploads/avatars/{st.id}.jpg"
    await db_session.commit()

    await db_session.execute(text(update))
    await db_session.commit()
    # read the column itself: the ORM identity map still holds the old objects
    rows = {i: a for i, a in (await db_session.execute(select(Student.id, Student.avatar_url).where(
        Student.id.in_([linked.id, turon.id, local.id, teacher.id])))).all()}
    assert rows[linked.id] is None and rows[turon.id] is None
    assert rows[local.id] == f"/uploads/avatars/{local.id}.jpg"
    assert rows[teacher.id] == f"/uploads/avatars/{teacher.id}.jpg"
