"""A student's balance must follow gennis on every login — but a login payload
that carries NO balance must never reset it to 0."""
import uuid

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
