"""PC Guard one-time maintenance codes: a teacher issues a 6-digit code for one device,
the signed-out agent redeems it with only its machine_key."""
import hashlib
import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update

from app.db.database import AsyncSessionLocal
from app.models.pc_control import PcDevice, PcMaintenanceCode
from app.models.user import Student, UserRole

PW = "securepass123"
T = "/api/v1/teacher/pc"
REDEEM = "/api/v1/pc/maintenance/redeem"
INVALID = {"detail": "invalid_code"}


def _uid() -> str:
    return uuid.uuid4().hex[:10]


async def _register(client, role=None):
    uid = _uid()
    r = await client.post("/api/v1/auth/register", json={
        "username": f"pcm_{uid}", "email": f"pcm_{uid}@example.com", "password": PW})
    assert r.status_code == 201, r.text
    body = r.json()
    if role is not None:
        async with AsyncSessionLocal() as db:
            await db.execute(update(Student).where(Student.id == body["user"]["id"]).values(role=role))
            await db.commit()
    r = await client.post("/api/v1/auth/login", json={"username": f"pcm_{uid}", "password": PW})
    assert r.status_code == 200, r.text
    return body["user"]["id"], {"Authorization": f"Bearer {r.json()['access_token']}"}


async def _device() -> tuple[int, str]:
    mk = f"mk-maint-{_uid()}"
    async with AsyncSessionLocal() as db:
        d = PcDevice(hostname=f"lab-m-{_uid()}",
                     machine_key_hash=hashlib.sha256(mk.encode("utf-8")).hexdigest())
        db.add(d)
        await db.commit()
        await db.refresh(d)
        return d.id, mk


async def _issue(client, headers, device_id, minutes=None):
    body = {} if minutes is None else {"minutes": minutes}
    return await client.post(f"{T}/devices/{device_id}/maintenance-code", json=body, headers=headers)


async def _redeem(client, machine_key, code):
    return await client.post(REDEEM, json={"machine_key": machine_key, "code": code})


def _wrong(code: str) -> str:
    return f"{(int(code) + 1) % 1_000_000:06d}"


def _app_log(caplog) -> str:
    # SQLAlchemy echo (DEBUG=true only) prints bound params; the audit rule is about app logs.
    return "\n".join(r.getMessage() for r in caplog.records if not r.name.startswith("sqlalchemy"))


def _clear_limiter():
    from app.core.rate_limit import _counters
    _counters.clear()


async def _rows(device_id):
    async with AsyncSessionLocal() as db:
        return (await db.execute(select(PcMaintenanceCode).where(
            PcMaintenanceCode.device_id == device_id).order_by(PcMaintenanceCode.id))).scalars().all()


# ── issue ───────────────────────────────────────────────────────────────────

async def test_issue_returns_six_digit_string_and_stores_only_a_hash(async_client, caplog):
    tid, th = await _register(async_client, UserRole.teacher)
    did, _ = await _device()
    with caplog.at_level(logging.INFO):
        r = await _issue(async_client, th, did, 15)
    assert r.status_code == 201, r.text
    body = r.json()
    assert set(body) == {"code", "expires_at", "minutes"}
    assert isinstance(body["code"], str) and len(body["code"]) == 6 and body["code"].isdigit()
    assert body["minutes"] == 15
    exp = datetime.fromisoformat(body["expires_at"])
    exp = exp if exp.tzinfo else exp.replace(tzinfo=timezone.utc)
    left = exp - datetime.now(timezone.utc)
    assert timedelta(minutes=4) < left <= timedelta(minutes=5, seconds=5)

    rows = await _rows(did)
    assert len(rows) == 1
    row = rows[0]
    assert row.minutes == 15 and row.created_by_user_id == tid
    assert row.used_at is None and row.failed_attempts == 0
    for col in PcMaintenanceCode.__table__.columns:
        assert body["code"] not in str(getattr(row, col.key)), col.key
    assert row.code_hash and row.salt
    log = _app_log(caplog)
    assert f"maintenance code issued device={did} by={tid} minutes=15" in log
    assert body["code"] not in log
    assert row.code_hash not in log and row.salt not in log


async def test_issue_defaults_to_60_minutes(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    did, _ = await _device()
    r = await _issue(async_client, th, did)
    assert r.status_code == 201 and r.json()["minutes"] == 60


async def test_issue_invalid_minutes_422(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    did, _ = await _device()
    for bad in (0, 30, 241, -15, "abc", None):
        r = await async_client.post(f"{T}/devices/{did}/maintenance-code",
                                    json={"minutes": bad}, headers=th)
        assert r.status_code == 422, (bad, r.text)
    assert await _rows(did) == []


async def test_issue_requires_teacher(async_client):
    _, sh = await _register(async_client)
    did, _ = await _device()
    assert (await _issue(async_client, sh, did)).status_code == 403
    assert (await async_client.post(f"{T}/devices/{did}/maintenance-code", json={})).status_code == 401
    assert await _rows(did) == []


async def test_issue_unknown_device_404(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    r = await _issue(async_client, th, 987_654_321)
    assert r.status_code == 404


async def test_any_teacher_may_issue_for_a_shared_device(async_client):
    _, th1 = await _register(async_client, UserRole.teacher)
    _, th2 = await _register(async_client, UserRole.teacher)
    did, mk = await _device()
    assert (await _issue(async_client, th1, did)).status_code == 201
    r = await _issue(async_client, th2, did)
    assert r.status_code == 201
    assert (await _redeem(async_client, mk, r.json()["code"])).status_code == 200


async def test_new_code_invalidates_previous(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    did, mk = await _device()
    first = (await _issue(async_client, th, did, 15)).json()["code"]
    second = (await _issue(async_client, th, did, 240)).json()["code"]
    rows = await _rows(did)
    assert rows[0].used_at is not None and rows[1].used_at is None
    if first != second:
        r = await _redeem(async_client, mk, first)
        assert r.status_code == 403 and r.json() == INVALID
    r = await _redeem(async_client, mk, second)
    assert r.status_code == 200 and r.json() == {"minutes": 240}


async def test_hourly_issue_limit_429(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    did, _ = await _device()
    for _ in range(10):
        assert (await _issue(async_client, th, did)).status_code == 201
    assert (await _issue(async_client, th, did)).status_code == 429
    # another device is not affected
    other, _ = await _device()
    assert (await _issue(async_client, th, other)).status_code == 201


async def test_issue_deletes_codes_older_than_7_days(async_client):
    tid, th = await _register(async_client, UserRole.teacher)
    did, _ = await _device()
    old = datetime.now(timezone.utc) - timedelta(days=8)
    async with AsyncSessionLocal() as db:
        db.add(PcMaintenanceCode(device_id=did, code_hash="x" * 64, salt="y" * 32, minutes=60,
                                 created_by_user_id=tid, created_at=old,
                                 expires_at=old + timedelta(minutes=5)))
        await db.commit()
    assert len(await _rows(did)) == 1
    assert (await _issue(async_client, th, did)).status_code == 201
    rows = await _rows(did)
    assert len(rows) == 1 and rows[0].code_hash != "x" * 64


# ── redeem ──────────────────────────────────────────────────────────────────

async def test_redeem_success_consumes_code_without_token(async_client, caplog):
    _, th = await _register(async_client, UserRole.teacher)
    did, mk = await _device()
    code = (await _issue(async_client, th, did, 240)).json()["code"]
    with caplog.at_level(logging.INFO):
        r = await _redeem(async_client, mk, code)  # no Authorization header
    assert r.status_code == 200, r.text
    assert r.json() == {"minutes": 240}
    log = _app_log(caplog)
    assert f"maintenance code redeemed device={did} minutes=240" in log
    assert code not in log
    assert (await _rows(did))[0].used_at is not None
    again = await _redeem(async_client, mk, code)
    assert again.status_code == 403 and again.json() == INVALID


async def test_wrong_code_403_and_increments(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    did, mk = await _device()
    code = (await _issue(async_client, th, did)).json()["code"]
    r = await _redeem(async_client, mk, _wrong(code))
    assert r.status_code == 403 and r.json() == INVALID
    r = await _redeem(async_client, mk, "abc")
    assert r.status_code == 403 and r.json() == INVALID
    row = (await _rows(did))[0]
    assert row.failed_attempts == 2 and row.used_at is None
    assert (await _redeem(async_client, mk, code)).json() == {"minutes": 60}


async def test_five_wrong_attempts_invalidate_the_code(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    did, mk = await _device()
    code = (await _issue(async_client, th, did)).json()["code"]
    for _ in range(5):
        assert (await _redeem(async_client, mk, _wrong(code))).status_code == 403
    row = (await _rows(did))[0]
    assert row.failed_attempts == 5 and row.used_at is not None
    _clear_limiter()  # take the rate-limit layer out: the code itself must be dead
    r = await _redeem(async_client, mk, code)
    assert r.status_code == 403 and r.json() == INVALID


async def test_expired_code_403(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    did, mk = await _device()
    code = (await _issue(async_client, th, did)).json()["code"]
    async with AsyncSessionLocal() as db:
        await db.execute(update(PcMaintenanceCode).where(PcMaintenanceCode.device_id == did).values(
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=1)))
        await db.commit()
    r = await _redeem(async_client, mk, code)
    assert r.status_code == 403 and r.json() == INVALID
    assert (await _rows(did))[0].used_at is None


async def test_unknown_machine_key_403_same_as_wrong_code_and_no_device(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    did, mk = await _device()
    code = (await _issue(async_client, th, did)).json()["code"]
    async with AsyncSessionLocal() as db:
        before = (await db.execute(select(func.count(PcDevice.id)))).scalar_one()
    unknown = await _redeem(async_client, f"mk-unknown-{_uid()}", code)
    wrong = await _redeem(async_client, mk, _wrong(code))
    assert unknown.status_code == wrong.status_code == 403
    assert unknown.json() == wrong.json() == INVALID
    assert unknown.headers.get("content-type") == wrong.headers.get("content-type")
    assert unknown.content == wrong.content
    async with AsyncSessionLocal() as db:
        after = (await db.execute(select(func.count(PcDevice.id)))).scalar_one()
    assert after == before


async def test_device_without_code_403(async_client):
    _, mk = await _device()
    r = await _redeem(async_client, mk, "123456")
    assert r.status_code == 403 and r.json() == INVALID


async def test_all_failures_identical_in_shape(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    responses = []
    # unknown machine key
    responses.append(await _redeem(async_client, f"mk-unknown-{_uid()}", "000000"))
    # device without a code
    _, mk0 = await _device()
    responses.append(await _redeem(async_client, mk0, "000000"))
    # wrong code
    did1, mk1 = await _device()
    c1 = (await _issue(async_client, th, did1)).json()["code"]
    responses.append(await _redeem(async_client, mk1, _wrong(c1)))
    _clear_limiter()
    # used code
    assert (await _redeem(async_client, mk1, c1)).status_code == 200
    responses.append(await _redeem(async_client, mk1, c1))
    # expired code
    did2, mk2 = await _device()
    c2 = (await _issue(async_client, th, did2)).json()["code"]
    async with AsyncSessionLocal() as db:
        await db.execute(update(PcMaintenanceCode).where(PcMaintenanceCode.device_id == did2).values(
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1)))
        await db.commit()
    responses.append(await _redeem(async_client, mk2, c2))
    for r in responses:
        assert r.status_code == 403
        assert r.content == responses[0].content
        assert sorted(r.headers.keys()) == sorted(responses[0].headers.keys())


async def test_redeem_rate_limited_per_machine_key(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    did, mk = await _device()
    code = (await _issue(async_client, th, did)).json()["code"]
    for _ in range(4):
        assert (await _redeem(async_client, mk, _wrong(code))).status_code == 403
    # 5th failure on a brand-new code still counts against the machine key
    code = (await _issue(async_client, th, did)).json()["code"]
    assert (await _redeem(async_client, mk, _wrong(code))).status_code == 403
    r = await _redeem(async_client, mk, code)
    assert r.status_code == 429
    # a blocked attempt is not validated: the code survives
    assert (await _rows(did))[-1].used_at is None


async def test_unknown_keys_and_spoofed_ips_do_not_block_the_lab(async_client):
    # Lab PCs share one NAT IP and X-Forwarded-For is client-controlled: failures must not
    # block an IP. Unknown machine keys leave no limiter state at all.
    from app.core.rate_limit import _counters
    _, th = await _register(async_client, UserRole.teacher)
    did, mk = await _device()
    code = (await _issue(async_client, th, did)).json()["code"]
    for _ in range(10):
        for xff in (None, "203.0.113.7"):
            headers = {"X-Forwarded-For": xff} if xff else {}
            r = await async_client.post(REDEEM, json={"machine_key": f"mk-unknown-{_uid()}",
                                                      "code": "000000"}, headers=headers)
            assert r.status_code == 403 and r.json() == INVALID
    assert not [k for k in _counters if k[0] in ("fail", "block")]
    r = await async_client.post(REDEEM, json={"machine_key": mk, "code": code},
                                headers={"X-Forwarded-For": "203.0.113.7"})
    assert r.status_code == 200 and r.json() == {"minutes": 60}


async def test_failures_on_one_device_do_not_block_another(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    did_a, mk_a = await _device()
    did_b, mk_b = await _device()
    _issue_a = (await _issue(async_client, th, did_a)).json()["code"]
    code_b = (await _issue(async_client, th, did_b)).json()["code"]
    for _ in range(5):
        assert (await _redeem(async_client, mk_a, _wrong(_issue_a))).status_code == 403
    assert (await _redeem(async_client, mk_a, _issue_a)).status_code == 429
    assert (await _redeem(async_client, mk_b, code_b)).status_code == 200


async def test_redeem_has_a_generous_flood_limit(async_client):
    for _ in range(120):
        r = await _redeem(async_client, f"mk-unknown-{_uid()}", "000000")
        assert r.status_code == 403
    assert (await _redeem(async_client, f"mk-unknown-{_uid()}", "000000")).status_code == 429


async def _add_code(device_id, user_id, code, minutes=60):
    from app.services.pc_maintenance_service import _hash
    now = datetime.now(timezone.utc)
    async with AsyncSessionLocal() as db:
        db.add(PcMaintenanceCode(device_id=device_id, code_hash=_hash("s" * 32, code), salt="s" * 32,
                                 minutes=minutes, created_by_user_id=user_id, created_at=now,
                                 expires_at=now + timedelta(minutes=5), failed_attempts=0))
        await db.commit()


async def test_two_active_codes_from_a_race_both_redeemable_once(async_client):
    # Two concurrent issues can each supersede before the other's INSERT is visible,
    # leaving two active codes; redeem must accept either, then neither.
    tid, _ = await _register(async_client, UserRole.teacher)
    did, mk = await _device()
    await _add_code(did, tid, "111111", 15)
    await _add_code(did, tid, "222222", 240)
    r = await _redeem(async_client, mk, "111111")  # the OLDER code
    assert r.status_code == 200 and r.json() == {"minutes": 15}
    assert all(row.used_at is not None for row in await _rows(did))
    assert (await _redeem(async_client, mk, "222222")).status_code == 403


async def test_wrong_guess_counts_against_every_active_code(async_client):
    tid, _ = await _register(async_client, UserRole.teacher)
    did, mk = await _device()
    await _add_code(did, tid, "111111")
    await _add_code(did, tid, "222222")
    assert (await _redeem(async_client, mk, "333333")).status_code == 403
    assert [row.failed_attempts for row in await _rows(did)] == [1, 1]
    for _ in range(4):
        assert (await _redeem(async_client, mk, "333333")).status_code == 403
    assert all(row.used_at is not None for row in await _rows(did))


# ── maintenance_until on the device ─────────────────────────────────────────

async def test_redeem_records_maintenance_until_and_devices_list_shows_it(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    did, mk = await _device()
    code = (await _issue(async_client, th, did, 15)).json()["code"]
    before = datetime.now(timezone.utc)
    assert (await _redeem(async_client, mk, code)).status_code == 200
    async with AsyncSessionLocal() as db:
        until = (await db.get(PcDevice, did)).maintenance_until
    until = until if until.tzinfo else until.replace(tzinfo=timezone.utc)
    assert before + timedelta(minutes=15) - timedelta(seconds=5) <= until \
        <= datetime.now(timezone.utc) + timedelta(minutes=15)
    listed = next(d for d in (await async_client.get(f"{T}/devices", headers=th)).json() if d["id"] == did)
    got = datetime.fromisoformat(listed["maintenance_until"])
    got = got if got.tzinfo else got.replace(tzinfo=timezone.utc)
    assert abs((got - until).total_seconds()) < 1


async def test_devices_list_maintenance_until_null_when_none_or_passed(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    did_none, _ = await _device()
    did_past, _ = await _device()
    async with AsyncSessionLocal() as db:
        await db.execute(update(PcDevice).where(PcDevice.id == did_past).values(
            maintenance_until=datetime.now(timezone.utc) - timedelta(seconds=1)))
        await db.commit()
    listed = {d["id"]: d for d in (await async_client.get(f"{T}/devices", headers=th)).json()}
    assert "maintenance_until" in listed[did_none]
    assert listed[did_none]["maintenance_until"] is None
    assert listed[did_past]["maintenance_until"] is None


async def test_failed_redeem_does_not_set_maintenance_until(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    did, mk = await _device()
    code = (await _issue(async_client, th, did)).json()["code"]
    assert (await _redeem(async_client, mk, _wrong(code))).status_code == 403
    async with AsyncSessionLocal() as db:
        assert (await db.get(PcDevice, did)).maintenance_until is None


async def test_redeem_block_lasts_ten_minutes(async_client, monkeypatch):
    import app.core.rate_limit as rl
    now = [1_000_000.0]
    monkeypatch.setattr(rl, "_clock", lambda: now[0])
    _, mk = await _device()
    for _ in range(5):
        assert (await _redeem(async_client, mk, "000000")).status_code == 403
    assert (await _redeem(async_client, mk, "000000")).status_code == 429
    now[0] += 9 * 60
    assert (await _redeem(async_client, mk, "000000")).status_code == 429
    now[0] += 61
    assert (await _redeem(async_client, mk, "000000")).status_code == 403


async def test_success_does_not_count_as_failure(async_client):
    _, th = await _register(async_client, UserRole.teacher)
    did, mk = await _device()
    for _ in range(6):
        code = (await _issue(async_client, th, did)).json()["code"]
        assert (await _redeem(async_client, mk, code)).status_code == 200
