"""Simple in-memory IP rate limiter — no external dependencies required.

Uses a sliding-window counter keyed by (client_ip, endpoint). Works for a
single-process deployment (one uvicorn worker). If you scale to multiple
workers, replace the in-memory dict with a Redis backend (e.g. fastapi-limiter).

Two things to know before relying on this in production:
- **Per-process state.** With multiple uvicorn workers each worker has its
  own `_counters` dict, so the effective limit is `max_calls * worker_count`,
  not `max_calls` — fine for today's single-worker deploy (see
  docs/PROJECT_KNOWLEDGE.md §13), but re-check this the moment worker count
  changes.
- **Resets on restart.** `_counters` is a plain in-memory dict; a service
  restart (deploy, crash, `systemctl restart`) silently zeroes every
  counter, so a client mid-window gets a fresh allowance. Acceptable for
  abuse-throttling; do not rely on this for anything that needs a durable
  audit trail of request counts.

Migrating to Redis fixes both at once (shared state across processes,
survives restarts) — left as a follow-up, not done here.
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


# ── Failure-based lockout (same in-memory store and caveats as rate_limit) ────

def _clock() -> float:
    return time.monotonic()


def client_ip(request: Request) -> str:
    return _client_ip(request)


def failure_block_active(scope: str, key: str) -> bool:
    """True while `key` is blocked in `scope` (set by record_failure)."""
    now = _clock()
    with _lock:
        until = _counters.get(("block", scope, key))
        if until and until[0] > now:
            return True
        _counters.pop(("block", scope, key), None)
        return False


def record_failure(scope: str, key: str, max_failures: int, block_seconds: int) -> None:
    """Count one failure for `key`; the `max_failures`-th within `block_seconds` blocks the
    key for `block_seconds` from that moment (see failure_block_active)."""
    now = _clock()
    cutoff = now - block_seconds
    fkey = ("fail", scope, key)
    with _lock:
        recent = [t for t in _counters[fkey] if t > cutoff]
        recent.append(now)
        if len(recent) >= max_failures:
            _counters[("block", scope, key)] = [now + block_seconds]
            _counters.pop(fkey, None)
        else:
            _counters[fkey] = recent
