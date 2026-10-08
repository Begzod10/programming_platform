"""A student with a negative balance (owes tuition) cannot download a certificate."""
import uuid

import pytest
from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.user import Student

DOWNLOADS = [
    "/api/v1/achievements/course/1/download",
    "/api/v1/achievements/category/1/download",
    "/api/v1/achievements/1/download",
]


async def _student(async_client, balance):
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post("/api/v1/auth/register", json={
        "username": f"debt_{uid}", "email": f"debt_{uid}@example.com", "password": "securepass123"})
    assert reg.status_code == 201, reg.text
    token, sid = reg.json()["access_token"], reg.json()["user"]["id"]
    async with AsyncSessionLocal() as db:
        s = (await db.execute(select(Student).where(Student.id == sid))).scalar_one()
        s.balance = balance
        await db.commit()
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize("url", DOWNLOADS)
async def test_negative_balance_is_refused_in_both_languages(async_client, url):
    h = await _student(async_client, -250000)
    r = await async_client.get(url, headers=h)
    assert r.status_code == 403
    detail = r.json()["error"]["message"]
    assert detail["code"] == "negative_balance" and detail["debt"] == 250000
    assert "250 000" in detail["message_uz"] and "qarz" in detail["message_uz"]
    assert "250 000" in detail["message_ru"] and "задолженность" in detail["message_ru"]


@pytest.mark.parametrize("balance", [0, 1, 430000])
@pytest.mark.parametrize("url", DOWNLOADS)
async def test_zero_or_positive_balance_is_not_blocked(async_client, url, balance):
    h = await _student(async_client, balance)
    r = await async_client.get(url, headers=h)
    # no certificate exists for this fresh student, but it is not the debt refusal
    body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    msg = (body.get("error") or {}).get("message")
    assert not (isinstance(msg, dict) and msg.get("code") == "negative_balance")
