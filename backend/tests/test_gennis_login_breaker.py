"""GennisService.login: fast connect timeout, a circuit breaker for an unreachable Gennis, and a log line that names the error type.
conftest replaces GennisService.login for every test, so the real classmethod is captured at import time."""
import logging
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

import app.services.gennis_service as gs
from app.services.gennis_service import GennisService, _LoginBreaker

real_login = GennisService.login                       # bound classmethod, taken before the autouse patch runs


@pytest.fixture(autouse=True)
def fresh_breaker(monkeypatch):
    monkeypatch.setattr(gs, "_login_breaker", _LoginBreaker())
    clock = {"now": 1000.0}
    monkeypatch.setattr(gs.time, "monotonic", lambda: clock["now"])
    return clock


def fake_client(monkeypatch, *, error=None, status=200, body=None):
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    response = MagicMock(status_code=status)
    response.json.return_value = body or {"token": "t"}
    client.post = AsyncMock(side_effect=error) if error else AsyncMock(return_value=response)
    monkeypatch.setattr(gs.httpx, "AsyncClient", MagicMock(return_value=client))
    return client


def test_connect_timeout_is_short_but_waiting_for_the_answer_is_not():
    assert gs._LOGIN_TIMEOUT.connect == 3.0 and gs._LOGIN_TIMEOUT.read == 10.0


async def test_after_three_unreachable_attempts_gennis_is_skipped_without_a_request(monkeypatch, fresh_breaker):
    client = fake_client(monkeypatch, error=httpx.ConnectTimeout(""))
    for _ in range(3):
        assert await real_login("ali", "pw") is None
    assert client.post.await_count == 3
    assert await real_login("ali", "pw") is None                      # the breaker is open: no 4th request
    assert client.post.await_count == 3


async def test_one_probe_after_the_pause_and_a_healthy_answer_closes_the_breaker(monkeypatch, fresh_breaker):
    client = fake_client(monkeypatch, error=httpx.ConnectTimeout(""))
    for _ in range(3):
        await real_login("ali", "pw")
    fresh_breaker["now"] += _LoginBreaker.OPEN_FOR + 1
    client = fake_client(monkeypatch, status=200, body={"token": "t", "source": "gennis"})
    assert await real_login("ali", "pw") == {"token": "t", "source": "gennis"}
    assert client.post.await_count == 1
    assert gs._login_breaker.allow(fresh_breaker["now"]) and gs._login_breaker.failures == 0


async def test_a_failed_probe_reopens_the_breaker_at_once(monkeypatch, fresh_breaker):
    fake_client(monkeypatch, error=httpx.ConnectTimeout(""))
    for _ in range(3):
        await real_login("ali", "pw")
    fresh_breaker["now"] += _LoginBreaker.OPEN_FOR + 1
    client = fake_client(monkeypatch, error=httpx.ConnectTimeout(""))
    await real_login("ali", "pw")                                     # the probe
    assert client.post.await_count == 1
    await real_login("ali", "pw")                                     # skipped again
    assert client.post.await_count == 1


async def test_a_401_from_gennis_means_it_is_healthy_and_never_opens_the_breaker(monkeypatch, fresh_breaker):
    client = fake_client(monkeypatch, status=401)
    for _ in range(6):
        assert await real_login("ali", "wrong") is None
    assert client.post.await_count == 6


async def test_a_success_resets_the_failure_count(monkeypatch, fresh_breaker):
    fake_client(monkeypatch, error=httpx.ConnectTimeout(""))
    await real_login("a", "p"); await real_login("a", "p")
    fake_client(monkeypatch, status=200)
    await real_login("a", "p")
    client = fake_client(monkeypatch, error=httpx.ConnectTimeout(""))
    await real_login("a", "p"); await real_login("a", "p")
    assert client.post.await_count == 2                               # two new failures are not enough to open it


async def test_the_error_log_names_the_exception_type(monkeypatch, caplog):
    fake_client(monkeypatch, error=httpx.ConnectTimeout(""))
    with caplog.at_level(logging.ERROR, logger="app.services.gennis_service"):
        await real_login("ali", "pw")
    assert any("Gennis login xatosi: ConnectTimeout" in r.getMessage() for r in caplog.records)
