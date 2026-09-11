"""Regression coverage for the team_game_session.py -> team_game_session.py +
team_game_session_reports.py + team_game_common.py split (2026-09-11).

The split itself is a pure refactor (no intended behavior change) and is
mostly covered by test_team_game.py continuing to pass unchanged against
the new file layout. This file guards two things specific to the split:

1. The real bug found and fixed while splitting: GET .../export.csv's
   @router.get decorator used to sit directly above _csv_option_label (an
   unrelated private helper with signature (q: dict, idx)), not above
   session_export_csv, the actual handler below it — so FastAPI registered
   the wrong function as the route's endpoint and the CSV export was
   completely unreachable in its real form. Verified live-broken via
   `app.routes` before the fix (see docs/BACKEND_BUGS.md).
2. Every route that existed on the single pre-split file still exists,
   at the same path/method, after being distributed across the two new
   router modules.
"""
from app.main import app


def _route_map() -> dict[tuple[str, frozenset], str]:
    """(path, methods) -> endpoint function name, for every HTTP route."""
    out = {}
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        endpoint = getattr(route, "endpoint", None)
        if path is None or methods is None or endpoint is None:
            continue
        out[(path, frozenset(methods))] = endpoint.__name__
    return out


def test_export_csv_route_resolves_to_the_real_handler():
    """The exact regression: this used to resolve to _csv_option_label."""
    routes = _route_map()
    key = ("/api/v1/game-sessions/{session_id}/export.csv", frozenset({"GET"}))
    assert key in routes, "export.csv route is missing entirely"
    assert routes[key] == "session_export_csv", (
        f"export.csv resolved to {routes[key]!r}, not session_export_csv — "
        "the decorator-misplacement bug is back"
    )


def test_all_game_session_routes_present_after_split():
    """Every route team_game_session.py + team_game_session_reports.py
    together must still expose, split across the two router modules."""
    routes = _route_map()
    # session_ws (WebSocketRoute) is checked separately below — it has no
    # `.methods` attribute, so _route_map() (which only tracks HTTP routes)
    # skips it by design.
    expected = [
        ("/api/v1/game-sessions", frozenset({"POST"})),
        ("/api/v1/game-sessions", frozenset({"GET"})),
        ("/api/v1/game-sessions/", frozenset({"GET"})),
        ("/api/v1/game-sessions/{session_id}", frozenset({"GET"})),
        ("/api/v1/game-sessions/{session_id}/students", frozenset({"GET"})),
        ("/api/v1/game-sessions/{session_id}/start", frozenset({"POST"})),
        ("/api/v1/game-sessions/{session_id}/activate-auto", frozenset({"POST"})),
        ("/api/v1/game-sessions/{session_id}/score", frozenset({"PATCH"})),
        ("/api/v1/game-sessions/{session_id}/complete", frozenset({"POST"})),
        ("/api/v1/game-sessions/{session_id}", frozenset({"DELETE"})),
        ("/api/v1/game-sessions/{session_id}/summary", frozenset({"GET"})),
        ("/api/v1/game-sessions/{session_id}/export.csv", frozenset({"GET"})),
        ("/api/v1/game-sessions/{session_id}/summary-public", frozenset({"GET"})),
        ("/api/v1/game-sessions/completed-today", frozenset({"GET"})),
    ]
    missing = [key for key in expected if key not in routes]
    assert not missing, f"routes missing after the split: {missing}"

    ws_paths = {
        getattr(r, "path", None) for r in app.routes
        if "WebSocketRoute" in type(r).__name__
    }
    assert "/api/v1/game-sessions/{session_id}/ws" in ws_paths


def test_team_game_aggregator_source_still_lists_all_three_sub_routers():
    """team_game.py's router aggregator is dead code (nothing imports it —
    app/api/v1/router.py mounts the three sub-routers directly), found
    while making this split; kept, not deleted, since removing dead code is
    out of scope for this refactor. It can't actually be *imported* in a
    test — that would call APIRouter.include_router() with no prefix on a
    router carrying an empty-path route (create_session's `@router.post("")`),
    which FastAPI rejects; that's a pre-existing latent bug in this same
    dead file, present before the split too, also out of scope here. This
    just checks the source text stays in sync with the real sub-router set,
    so a future editor touching this file notices if it silently drifts.
    """
    import pathlib
    import app.api.v1.endpoints as endpoints_pkg  # importing the package itself
    # doesn't execute team_game.py — only `from ...endpoints import team_game`
    # (or accessing it via fromlist=[...]) would, which is exactly the crash
    # described above.
    source = pathlib.Path(endpoints_pkg.__file__).parent.joinpath("team_game.py").read_text()
    for name in ("team_game_session", "team_game_session_reports", "team_game_questions"):
        assert f"from app.api.v1.endpoints.{name} import router" in source
