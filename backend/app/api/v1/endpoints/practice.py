"""Dictionary practice — thin router that composes sub-routers."""
from fastapi import APIRouter

from .practice_words import router as _words_router
from .practice_session import router as _session_router
from .practice_stats import router as _stats_router

router = APIRouter()
router.include_router(_words_router)
router.include_router(_session_router)
router.include_router(_stats_router)
