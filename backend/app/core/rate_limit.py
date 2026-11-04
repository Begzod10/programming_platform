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

Bounded store. Every key carries an expiry (the moment its state stops mattering); expired
keys are swept at most every SWEEP_INTERVAL seconds on use, and a hard cap of MAX_KEYS evicts
the least recently touched keys first. A token-less endpoint fed random IPs/keys therefore
cannot grow memory without bound. Under cap pressure an eviction can drop a live counter or
block early (the client gets a fresh allowance); that is the accepted price of the bound, and
the cap is far above legitimate traffic.
"""
import time
from collections import OrderedDict
from threading import Lock
from typing import Optional

from fastapi import Request, HTTPException, status

MAX_KEYS = 50_000
SWEEP_INTERVAL = 60.0


class _Store(OrderedDict):
    """key -> list of floats (timestamps, or [until] for a block), ordered oldest-touched first.
    `expires` holds each key's expiry; `clear()` (used by tests) resets everything."""

    def __init__(self):
        super().__init__()
        self.expires: dict = {}
        self.last_sweep: Optional[float] = None

    def clear(self):
        super().clear()
        self.expires.clear()
        self.last_sweep = None


# (ip, endpoint) → list of timestamps within the current window; also failure/block keys.
_counters: _Store = _Store()
_lock = Lock()


def _clock() -> float:
    return time.monotonic()


def _drop(key) -> None:
    _counters.pop(key, None)
    _counters.expires.pop(key, None)


def _put(key, value: list, expires_at: float) -> None:
    """Store `value` under `key` as the most recently touched entry, then enforce the cap.
    Caller holds _lock."""
    _counters[key] = value
    _counters.move_to_end(key)
    _counters.expires[key] = expires_at
    while len(_counters) > MAX_KEYS:
        old, _ = _counters.popitem(last=False)
        _counters.expires.pop(old, None)


def _sweep(force: bool = False) -> None:
    """Drop every expired key; runs at most every SWEEP_INTERVAL unless forced. Caller holds
    _lock (or the store is otherwise not shared, as in tests)."""
    now = _clock()
    if not force and _counters.last_sweep is not None and now - _counters.last_sweep < SWEEP_INTERVAL:
        return
    _counters.last_sweep = now
    for key, exp in list(_counters.expires.items()):
        if exp <= now:
            _drop(key)


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
        now = _clock()
        cutoff = now - window_seconds

        with _lock:
            _sweep()
            # Evict timestamps outside the window
            recent = [t for t in _counters.get(key, ()) if t > cutoff]
            if len(recent) >= max_calls:
                _put(key, recent, recent[-1] + window_seconds)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many requests — max {max_calls} per {window_seconds}s",
                )
            recent.append(now)
            _put(key, recent, now + window_seconds)

    return _check


# ── Failure-based lockout (same in-memory store and caveats as rate_limit) ────

def client_ip(request: Request) -> str:
    return _client_ip(request)


def failure_block_active(scope: str, key: str) -> bool:
    """True while `key` is blocked in `scope` (set by record_failure). Never creates state."""
    now = _clock()
    with _lock:
        until = _counters.get(("block", scope, key))
        if until and until[0] > now:
            return True
        _drop(("block", scope, key))
        return False


def record_failure(scope: str, key: str, max_failures: int, block_seconds: int) -> None:
    """Count one failure for `key`; the `max_failures`-th within `block_seconds` blocks the
    key for `block_seconds` from that moment (see failure_block_active)."""
    now = _clock()
    cutoff = now - block_seconds
    fkey = ("fail", scope, key)
    with _lock:
        _sweep()
        recent = [t for t in _counters.get(fkey, ()) if t > cutoff]
        recent.append(now)
        if len(recent) >= max_failures:
            _drop(fkey)
            _put(("block", scope, key), [now + block_seconds], now + block_seconds)
        else:
            _put(fkey, recent, now + block_seconds)
