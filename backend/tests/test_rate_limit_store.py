"""The in-memory rate-limit store is bounded: expired keys are swept and a hard cap
evicts the least recently touched keys first."""
import pytest
from fastapi import HTTPException
from starlette.requests import Request

import app.core.rate_limit as rl


def _req(ip: str, path: str = "/x") -> Request:
    return Request({"type": "http", "method": "GET", "path": path, "headers": [],
                    "client": (ip, 1234), "query_string": b""})


@pytest.fixture
def clock(monkeypatch):
    now = [1_000.0]
    monkeypatch.setattr(rl, "_clock", lambda: now[0])
    return now


async def test_cap_evicts_oldest_keys_first(monkeypatch, clock):
    monkeypatch.setattr(rl, "MAX_KEYS", 3)
    check = rl.rate_limit(5, 60)
    for ip in ("a", "b", "c"):
        await check(_req(ip))
        clock[0] += 1
    await check(_req("a"))           # touching "a" makes "b" the oldest
    await check(_req("d"))
    keys = {k[0] for k in rl._counters}
    assert len(rl._counters) == 3 and keys == {"a", "c", "d"}


async def test_cap_applies_to_failure_and_block_keys(monkeypatch, clock):
    monkeypatch.setattr(rl, "MAX_KEYS", 4)
    for i in range(10):
        rl.record_failure("s", f"k{i}", 5, 600)
    assert len(rl._counters) == 4
    assert ("fail", "s", "k9") in rl._counters and ("fail", "s", "k0") not in rl._counters


async def test_sweep_drops_expired_keys(monkeypatch, clock):
    check = rl.rate_limit(5, 60)
    await check(_req("old"))
    rl.record_failure("s", "old-fail", 5, 600)
    for _ in range(5):
        rl.record_failure("s", "blocked", 5, 600)
    clock[0] += 61
    await check(_req("new"))          # "old" window has passed, failures/block have not
    rl._sweep(force=True)
    assert ("old", "/x") not in rl._counters
    assert ("new", "/x") in rl._counters
    assert ("fail", "s", "old-fail") in rl._counters
    assert ("block", "s", "blocked") in rl._counters
    clock[0] += 600
    rl._sweep(force=True)
    assert ("fail", "s", "old-fail") not in rl._counters
    assert ("block", "s", "blocked") not in rl._counters


async def test_sweep_runs_periodically_on_use(monkeypatch, clock):
    check = rl.rate_limit(5, 60)
    await check(_req("old"))
    clock[0] += rl.SWEEP_INTERVAL + 61
    await check(_req("new"))
    assert ("old", "/x") not in rl._counters


async def test_limit_and_block_behaviour_unchanged(clock):
    check = rl.rate_limit(2, 60)
    await check(_req("ip"))
    await check(_req("ip"))
    with pytest.raises(HTTPException) as e:
        await check(_req("ip"))
    assert e.value.status_code == 429
    clock[0] += 61
    await check(_req("ip"))
    for _ in range(3):
        rl.record_failure("s", "k", 3, 600)
    assert rl.failure_block_active("s", "k")
    clock[0] += 601
    assert not rl.failure_block_active("s", "k")


def test_clear_resets_everything():
    rl._counters[("x",)] = [1.0]
    rl._counters.clear()
    assert len(rl._counters) == 0
