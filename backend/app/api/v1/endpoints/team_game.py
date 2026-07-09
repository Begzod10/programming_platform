from fastapi import APIRouter

from app.api.v1.endpoints.team_game_session import router as session_router
from app.api.v1.endpoints.team_game_questions import router as questions_router

router = APIRouter(redirect_slashes=False)
router.include_router(session_router)
router.include_router(questions_router)
