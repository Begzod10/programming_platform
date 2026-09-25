"""1-vs-1 math race for kids ("Poyga"), pairing by a 4-digit room code.

Rooms live in this process's memory only — a race lasts a couple of minutes,
nothing needs to survive a restart, and there's no table to migrate. That
does mean it assumes ONE uvicorn worker (which is how student_platform runs);
a multi-worker deploy would need a shared store (Redis) instead.

The questions AND their answers stay on the server: clients only ever get the
question text + options, so a kid can't read the answer out of the network
tab, and "who answered first" is decided by arrival order here, not by two
untrusted clocks.

Rules: both players get the SAME endless stream of questions but each moves
through it at their own pace — a wrong answer just moves you on to the next
question (nobody ever waits for the other). The first player to reach
WIN_SCORE correct answers wins immediately. Leaving mid-race forfeits after a
short reconnect grace period (flaky wifi shouldn't lose a game instantly).
"""
import asyncio
import hashlib
import json
import logging
import random
import re
import time
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import rate_limit
from app.core.security import decode_access_token
from app.dependencies import get_current_student, get_db
from app.models.user import Student

logger = logging.getLogger(__name__)
router = APIRouter()

WIN_SCORE = 8
INITIAL_QUESTIONS = 12
COUNTDOWN_SECONDS = 3.2
RECONNECT_GRACE_SECONDS = 15
EMPTY_ROOM_TTL_SECONDS = 300


# Player ids are strings: "u<student id>" for logged-in students, "g<random
# guest id>" for kids playing from /play without an account. For a guest the
# raw id is effectively their password (it's all that identifies them on
# reconnect), so it is NEVER sent to the other player — everything outward
# uses `_public(pid)` instead, a short hash. Without that, the opponent could
# read the host's id from the state and connect with it to hijack their slot.
_GUEST_RE = re.compile(r"^[A-Za-z0-9_-]{8,40}$")


def _public(pid: Optional[str]) -> Optional[str]:
    if pid is None:
        return None
    if pid.startswith("g"):
        return "g" + hashlib.sha256(pid.encode()).hexdigest()[:8]
    return pid


def _clean_name(raw: Optional[str]) -> str:
    name = " ".join((raw or "").split())[:20]
    return name or "Mehmon"


class Player:
    def __init__(self, user_id: str, name: str, ws: WebSocket):
        self.user_id = user_id  # internal pid — see _public above
        self.pub = _public(user_id)
        self.name = name
        self.ws: Optional[WebSocket] = ws
        self.score = 0
        self.q_index = 0  # this player's own position in the shared question stream
        self.last: Optional[dict] = None  # their previous answer: {q, correct, answer}


class Room:
    def __init__(self, code: str, host_id: str):
        self.code = code
        self.host_id = host_id
        self.players: Dict[str, Player] = {}
        self.status = "waiting"  # waiting | countdown | playing | finished
        self.questions: List[dict] = []  # shared stream, extended lazily
        self.winner_id: Optional[str] = None
        self.finish_reason: Optional[str] = None
        self.lock = asyncio.Lock()
        self.created_at = time.time()


ROOMS: Dict[str, Room] = {}


# ── question generation ─────────────────────────────────────────────────────

def _make_question() -> dict:
    if random.random() < 0.5:
        a, b = random.randint(0, 9), random.randint(0, 9)
        if random.random() < 0.5:
            text, answer = f"{a} + {b}", a + b
        else:
            if a < b:
                a, b = b, a
            text, answer = f"{a} − {b}", a - b
        wrongs = set()
        for d in random.sample([1, -1, 2, -2, 3, -3], 6):
            if len(wrongs) >= 3:
                break
            if answer + d >= 0:
                wrongs.add(answer + d)
        while len(wrongs) < 3:
            wrongs.add(random.randint(0, 18))
            wrongs.discard(answer)
        options = [str(answer)] + [str(w) for w in wrongs]
        random.shuffle(options)
        return {"text": text, "options": options, "answer": str(answer)}
    a = random.randint(0, 20)
    b = a if random.random() < 0.17 else random.randint(0, 20)
    sign = "<" if a < b else ">" if a > b else "="
    return {"text": f"{a} ? {b}", "options": ["<", "=", ">"], "answer": sign}


# ── state broadcasting ──────────────────────────────────────────────────────

def _state_for(room: Room, viewer_id: str) -> dict:
    me = room.players.get(viewer_id)
    question = None
    if room.status == "playing" and me is not None:
        _ensure_question(room, me.q_index)
        q = room.questions[me.q_index]
        question = {"text": q["text"], "options": q["options"]}
    return {
        "code": room.code,
        "status": room.status,
        "you": _public(viewer_id),
        "host_id": _public(room.host_id),
        "players": [
            {"id": p.pub, "name": p.name, "score": p.score, "online": p.ws is not None}
            for p in room.players.values()
        ],
        "q_index": me.q_index if me else 0,
        "target": WIN_SCORE,
        "question": question,
        # Only the viewer's OWN previous answer — what the opponent just
        # answered (and whether it was right) is none of their business.
        "last": me.last if me else None,
        "winner_id": _public(room.winner_id),
        "finish_reason": room.finish_reason,
    }


def _ensure_question(room: Room, index: int) -> None:
    while len(room.questions) <= index:
        room.questions.append(_make_question())


async def _send(player: Player, payload: dict) -> None:
    if player.ws is None:
        return
    try:
        await player.ws.send_json(payload)
    except Exception:
        player.ws = None


async def _broadcast_state(room: Room) -> None:
    for p in list(room.players.values()):
        await _send(p, {"type": "state", "data": _state_for(room, p.user_id)})


def _schedule_cleanup(room: Room) -> None:
    async def _later():
        await asyncio.sleep(EMPTY_ROOM_TTL_SECONDS)
        if ROOMS.get(room.code) is room and all(p.ws is None for p in room.players.values()):
            ROOMS.pop(room.code, None)
    asyncio.create_task(_later())


# ── game flow ───────────────────────────────────────────────────────────────

def _reset_round(room: Room) -> None:
    room.questions = [_make_question() for _ in range(INITIAL_QUESTIONS)]
    room.winner_id = None
    room.finish_reason = None
    for p in room.players.values():
        p.score = 0
        p.q_index = 0
        p.last = None


async def _run_countdown(room: Room) -> None:
    await asyncio.sleep(COUNTDOWN_SECONDS)
    async with room.lock:
        if room.status != "countdown" or len(room.players) < 2:
            return
        _reset_round(room)
        room.status = "playing"
        await _broadcast_state(room)


def _finish(room: Room, reason: str, forced_winner: Optional[str] = None) -> None:
    room.status = "finished"
    room.finish_reason = reason
    room.winner_id = forced_winner
    _schedule_cleanup(room)


async def _handle_answer(room: Room, player: Player, msg: dict) -> None:
    async with room.lock:
        if room.status != "playing":
            return
        # Ignore anything not for this player's CURRENT question (a double
        # tap, or a message that raced the state update).
        if msg.get("q") != player.q_index:
            return
        _ensure_question(room, player.q_index)
        q = room.questions[player.q_index]
        correct = str(msg.get("choice")) == q["answer"]
        if correct:
            player.score += 1
        player.last = {"q": player.q_index, "correct": correct, "answer": q["answer"]}
        player.q_index += 1
        if player.score >= WIN_SCORE:
            _finish(room, reason="done", forced_winner=player.user_id)
        await _broadcast_state(room)


async def _forfeit_after_grace(room: Room, player: Player) -> None:
    await asyncio.sleep(RECONNECT_GRACE_SECONDS)
    async with room.lock:
        if player.ws is not None or room.status not in ("countdown", "playing"):
            return
        others = [p for p in room.players.values() if p.user_id != player.user_id]
        _finish(room, reason="left", forced_winner=others[0].user_id if others else None)
        await _broadcast_state(room)


# ── HTTP: create a room ─────────────────────────────────────────────────────

@router.post("/")
async def create_duel(
        current_student: Student = Depends(get_current_student),
        _rl: None = Depends(rate_limit(max_calls=10, window_seconds=60)),
):
    """Reserve a fresh 4-digit code; the creator becomes the host when they
    then open the WebSocket for it. An unclaimed room expires on its own."""
    for _ in range(50):
        code = f"{random.randint(0, 9999):04d}"
        if code not in ROOMS:
            break
    else:
        raise HTTPException(status_code=503, detail="Hozir bo'sh xona yo'q, qayta urinib ko'ring")
    room = Room(code, f"u{current_student.id}")
    ROOMS[code] = room
    _schedule_cleanup(room)
    return {"code": code}


class GuestCreate(BaseModel):
    guest_id: str


@router.post("/guest")
async def create_guest_duel(
        body: GuestCreate,
        _rl: None = Depends(rate_limit(max_calls=10, window_seconds=60)),
):
    """Same as POST / for a kid playing from /play with no account. The
    client generates and keeps its own random guest id (localStorage); the
    rate limit (per IP) is what stops someone from filling ROOMS."""
    if not _GUEST_RE.match(body.guest_id):
        raise HTTPException(status_code=422, detail="guest_id noto'g'ri")
    for _ in range(50):
        code = f"{random.randint(0, 9999):04d}"
        if code not in ROOMS:
            break
    else:
        raise HTTPException(status_code=503, detail="Hozir bo'sh xona yo'q, qayta urinib ko'ring")
    room = Room(code, f"g{body.guest_id}")
    ROOMS[code] = room
    _schedule_cleanup(room)
    return {"code": code}


# ── WebSocket ───────────────────────────────────────────────────────────────

async def _reject(websocket: WebSocket, reason: str) -> None:
    await websocket.accept()
    await websocket.send_json({"type": "error", "reason": reason})
    await websocket.close(code=4000)


@router.websocket("/{code}/ws")
async def duel_ws(
        code: str,
        websocket: WebSocket,
        token: Optional[str] = Query(default=None),
        guest: Optional[str] = Query(default=None),
        guest_name: Optional[str] = Query(default=None, alias="name"),
        db: AsyncSession = Depends(get_db),
):
    if token:
        user_id = decode_access_token(token)
        user = None
        if user_id is not None:
            user = (await db.execute(select(Student).where(Student.id == user_id))).scalar_one_or_none()
        if user is None or not user.is_active:
            await websocket.close(code=4001)
            return
        pid = f"u{user.id}"
        name = user.full_name or user.username
    else:
        if not guest or not _GUEST_RE.match(guest):
            await websocket.close(code=4001)
            return
        pid = f"g{guest}"
        name = _clean_name(guest_name)

    room = ROOMS.get(code)
    if room is None:
        await _reject(websocket, "not_found")
        return

    await websocket.accept()

    async with room.lock:
        existing = room.players.get(pid)
        if existing is not None:
            existing.ws = websocket  # reconnect (also cancels a pending forfeit)
            player = existing
        elif len(room.players) >= 2:
            await websocket.send_json({"type": "error", "reason": "full"})
            await websocket.close(code=4000)
            return
        elif room.status != "waiting":
            await websocket.send_json({"type": "error", "reason": "started"})
            await websocket.close(code=4000)
            return
        else:
            player = Player(pid, name, websocket)
            room.players[pid] = player
        await _broadcast_state(room)

    try:
        while True:
            raw = await websocket.receive_text()
            if raw == "ping":
                await websocket.send_text("pong")
                continue
            try:
                msg = json.loads(raw)
            except ValueError:
                continue
            kind = msg.get("type")
            if kind == "start":
                async with room.lock:
                    if pid == room.host_id and room.status == "waiting" and len(room.players) == 2:
                        room.status = "countdown"
                        await _broadcast_state(room)
                        asyncio.create_task(_run_countdown(room))
            elif kind == "answer":
                await _handle_answer(room, player, msg)
            elif kind == "rematch":
                async with room.lock:
                    if room.status == "finished" and pid == room.host_id and len(room.players) == 2:
                        room.status = "countdown"
                        room.finish_reason = None
                        room.winner_id = None
                        await _broadcast_state(room)
                        asyncio.create_task(_run_countdown(room))
    except WebSocketDisconnect:
        pass
    finally:
        async with room.lock:
            if player.ws is websocket:
                player.ws = None
                if room.status == "waiting":
                    room.players.pop(pid, None)
                    if pid == room.host_id:
                        for p in list(room.players.values()):
                            await _send(p, {"type": "error", "reason": "host_left"})
                        ROOMS.pop(room.code, None)
                    else:
                        await _broadcast_state(room)
                elif room.status in ("countdown", "playing"):
                    await _broadcast_state(room)
                    asyncio.create_task(_forfeit_after_grace(room, player))
                else:
                    await _broadcast_state(room)
                if all(p.ws is None for p in room.players.values()):
                    _schedule_cleanup(room)
