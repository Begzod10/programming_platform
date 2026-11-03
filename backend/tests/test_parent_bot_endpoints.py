"""The parent bot's server-to-server endpoints: reachable at their real paths and guarded by the shared secret."""
from app.config import settings


async def test_completed_today_is_not_swallowed_by_the_session_id_route(async_client):
    # PARENT_BOT_SECRET is empty in tests: the reports handler answers 503. Before the fix the request fell into
    # GET /game-sessions/{session_id} and was refused with 401 "Not authenticated" (a JWT message).
    resp = await async_client.get("/api/v1/game-sessions/completed-today")
    assert resp.status_code == 503, resp.text
    assert "not configured" in resp.text.lower()


async def test_completed_today_checks_the_shared_secret(async_client, monkeypatch):
    monkeypatch.setattr(settings, "PARENT_BOT_SECRET", "test-secret-xyz")
    wrong = await async_client.get("/api/v1/game-sessions/completed-today", headers={"X-Internal-Secret": "nope"})
    assert wrong.status_code == 401 and "Invalid internal secret" in wrong.text
    ok = await async_client.get("/api/v1/game-sessions/completed-today", headers={"X-Internal-Secret": "test-secret-xyz"})
    assert ok.status_code == 200, ok.text
    assert ok.json() == {"sessions": []} or isinstance(ok.json()["sessions"], list)


async def test_a_real_session_id_still_reaches_the_session_route(async_client):
    resp = await async_client.get("/api/v1/game-sessions/999999")
    assert resp.status_code == 401                         # the JWT-protected session route, as before


async def test_summary_public_and_student_stats_need_the_secret(async_client, monkeypatch):
    monkeypatch.setattr(settings, "PARENT_BOT_SECRET", "test-secret-xyz")
    assert (await async_client.get("/api/v1/game-sessions/1/summary-public")).status_code == 401
    assert (await async_client.get("/api/v1/bot/student-stats/1")).status_code == 401
    assert (await async_client.get("/api/v1/bot/student-stats/1", headers={"X-Internal-Secret": "test-secret-xyz"})).status_code in (200, 404)
