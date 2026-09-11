# DEAD CODE, found 2026-09-11 while splitting team_game_session.py: nothing
# imports this module. app/api/v1/router.py mounts team_game_session,
# team_game_session_reports, and team_game_questions directly with their own
# prefix/tags instead of going through this aggregator. Left in place rather
# than deleted (out of scope for that refactor) but kept internally
# consistent — if this ever does get wired in, it now matches router.py's
# actual route set.
#
# ALSO LATENT AND PRE-EXISTING (not introduced by the split above): actually
# importing this module raises a FastAPI startup error —
# `router.include_router(session_router)` below has no prefix, and
# session_router carries an empty-path route (create_session's
# `@router.post("", ...)`), which FastAPI's include_router() rejects
# ("Prefix and path cannot be both empty"). router.py's real mounts all
# pass an explicit prefix="/game-sessions" and don't hit this. Confirmed
# this predates the split (the same empty-path route and the same
# no-prefix include_router call both already existed in the single-file
# version) — not something to fix here, just flagging it accurately.
from fastapi import APIRouter

from app.api.v1.endpoints.team_game_session import router as session_router
from app.api.v1.endpoints.team_game_session_reports import router as session_reports_router
from app.api.v1.endpoints.team_game_questions import router as questions_router

router = APIRouter(redirect_slashes=False)
router.include_router(session_router)
router.include_router(session_reports_router)
router.include_router(questions_router)
