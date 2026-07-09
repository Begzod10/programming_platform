"""Simple in-memory IP rate limiter — no external dependencies required.

Uses a sliding-window counter keyed by (client_ip, endpoint). Works for a
single-process deployment (one uvicorn worker). If you scale to multiple
workers, replace the in-memory dict with a Redis backend (e.g. fastapi-limiter).
"""
import time
from collections import defaultdict
from threading import Lock
from fastapi import Request, HTTPException, status

# (ip, endpoint) → list of timestamps within the current window
_counters: dict[tuple, list[float]] = defaultdict(list)
_lock = Lock()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(max_calls: int, window_seconds: int = 60):
    """FastAPI dependency — raises 429 when the caller exceeds the limit.

    Usage:
        @router.post("/login")
        async def login(..., _=Depends(rate_limit(10, 60))):
            ...
    """
    async def _check(request: Request):
        ip = _client_ip(request)
        key = (ip, request.url.path)
        now = time.monotonic()
        cutoff = now - window_seconds

        with _lock:
            timestamps = _counters[key]
            # Evict timestamps outside the window
            _counters[key] = [t for t in timestamps if t > cutoff]
            if len(_counters[key]) >= max_calls:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many requests — max {max_calls} per {window_seconds}s",
                )
            _counters[key].append(now)

    return _check
