"""1-vs-1 race for kids ("Poyga") — math AND emoji/logic questions — paired by a
4-digit room code.

Rooms live in this process's memory only — a race lasts a couple of minutes,
nothing needs to survive a restart, and there's no table to migrate. That
does mean it assumes ONE uvicorn worker (which is how student_platform runs);
a multi-worker deploy would need a shared store (Redis) instead.

The questions AND their answers stay on the server: clients only ever get the
question text + options, so a kid can't read the answer out of the network
tab, and "who answered first" is decided by arrival order here, not by two
untrusted clocks.

Rooms hold 2-4 players; the host can also add a computer opponent (a "bot").
Rules: every player gets the SAME endless stream of questions but each moves
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
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import rate_limit
from app.core.security import decode_access_token
from app.dependencies import get_current_student, get_db
from app.db.database import AsyncSessionLocal
from app.models.duel_stat import DuelStat
from app.models.user import Student
from app.services.duel_questions import ALL_KINDS, DEFAULT_KINDS, LEVELS, make_question, option_value

logger = logging.getLogger(__name__)
router = APIRouter()

WIN_SCORE = 8
MAX_PLAYERS = 4
TEAM_TARGET = WIN_SCORE * 2  # 2v2: a team wins when its members' scores add up to this
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
    def __init__(self, user_id: str, name: str, ws: Optional[WebSocket], is_bot: bool = False):
        self.user_id = user_id  # internal pid — see _public above
        self.pub = _public(user_id)
        self.name = name
        self.ws: Optional[WebSocket] = ws
        self.score = 0
        self.q_index = 0  # this player's own position in the shared question stream
        self.last: Optional[dict] = None  # their previous answer: {q, correct, answer}
        self.is_bot = is_bot
        self.left = False  # forfeited mid-race (grace period ran out)


class Room:
    def __init__(self, code: str, host_id: str):
        self.code = code
        self.host_id = host_id
        self.players: Dict[str, Player] = {}
        self.status = "waiting"  # waiting | countdown | playing | finished
        self.questions: List[dict] = []  # shared stream, extended lazily
        self.kinds: List[str] = list(DEFAULT_KINDS)
        self.level = "medium"
        self.team_mode = False  # 2v2: seats alternate A,B,A,B in join order
        self.winner_team: Optional[int] = None
        self.round_id = 0  # bumps every round so a stale bot loop can tell it is over  # question types the host enabled
        self.winner_id: Optional[str] = None
        self.finish_reason: Optional[str] = None
        self.lock = asyncio.Lock()
        self.created_at = time.time()


ROOMS: Dict[str, Room] = {}


# ── question generation ─────────────────────────────────────────────────────

def _make_question(room: 'Room') -> dict:
    return make_question(room.kinds, room.level)


# ── state broadcasting ──────────────────────────────────────────────────────

def _team_of(room: Room, pid: str) -> Optional[int]:
    if not room.team_mode:
        return None
    return list(room.players).index(pid) % 2


def _team_scores(room: Room) -> List[int]:
    scores = [0, 0]
    for pid, p in room.players.items():
        scores[_team_of(room, pid)] += p.score
    return scores


def _can_start(room: Room) -> bool:
    n = len(room.players)
    return n == MAX_PLAYERS if room.team_mode else n >= 2


def _state_for(room: Room, viewer_id: str) -> dict:
    me = room.players.get(viewer_id)
    question = None
    if room.status == "playing" and me is not None:
        _ensure_question(room, me.q_index)
        q = room.questions[me.q_index]
        question = {k: q[k] for k in ("kind", "text", "options", "ink") if k in q}
    return {
        "code": room.code,
        "status": room.status,
        "you": _public(viewer_id),
        "host_id": _public(room.host_id),
        "players": [
            {
                "id": p.pub, "name": p.name, "score": p.score, "bot": p.is_bot, "left": p.left,
                "online": p.is_bot or p.ws is not None, "team": _team_of(room, pid),
            }
            for pid, p in room.players.items()
        ],
        "q_index": me.q_index if me else 0,
        "target": WIN_SCORE,
        "max_players": MAX_PLAYERS,
        "team_mode": room.team_mode,
        "team_scores": _team_scores(room) if room.team_mode else None,
        "team_target": TEAM_TARGET,
        "winner_team": room.winner_team,
        "kinds": room.kinds,
        "level": room.level,
        "all_kinds": ALL_KINDS,
        "question": question,
        # Only the viewer's OWN previous answer — what the opponent just
        # answered (and whether it was right) is none of their business.
        "last": me.last if me else None,
        "winner_id": _public(room.winner_id),
        "finish_reason": room.finish_reason,
    }


def _ensure_question(room: Room, index: int) -> None:
    while len(room.questions) <= index:
        room.questions.append(_make_question(room))


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
    room.questions = [_make_question(room) for _ in range(INITIAL_QUESTIONS)]
    room.winner_id = None
    room.finish_reason = None
    room.winner_team = None
    room.round_id += 1
    for p in room.players.values():
        p.left = False
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
        for p in room.players.values():
            if p.is_bot:
                asyncio.create_task(_bot_loop(room, p, room.round_id))


async def _record_stats(winners: List[str], humans: List[str]) -> None:
    """+1 game for every logged-in human (+1 win for the winner). Best effort."""
    try:
        ids = {int(h[1:]): (h in winners) for h in humans if h.startswith("u")}
        if not ids:
            return
        async with AsyncSessionLocal() as db:
            for sid, won in ids.items():
                stmt = pg_insert(DuelStat).values(student_id=sid, wins=1 if won else 0, games=1)
                stmt = stmt.on_conflict_do_update(
                    index_elements=[DuelStat.student_id],
                    set_={"wins": DuelStat.wins + (1 if won else 0), "games": DuelStat.games + 1},
                )
                await db.execute(stmt)
            await db.commit()
    except Exception:
        logger.exception("duel stats update failed")


# How a bot plays, per difficulty: (min, max) seconds per question and the
# chance each answer is right. Tuned so a bot is beatable but not a pushover.
_BOT_SKILL = {"easy": ((4.0, 7.0), 0.55), "medium": ((3.0, 5.5), 0.7), "hard": ((2.0, 3.8), 0.85)}


async def _bot_loop(room: Room, bot: Player, round_id: int) -> None:
    (lo, hi), p_right = _BOT_SKILL.get(room.level, _BOT_SKILL["medium"])
    while True:
        await asyncio.sleep(random.uniform(lo, hi))
        if room.status != "playing" or room.round_id != round_id or ROOMS.get(room.code) is not room:
            return
        async with room.lock:
            if room.status != "playing" or room.round_id != round_id:
                return
            _ensure_question(room, bot.q_index)
            q = room.questions[bot.q_index]
            if random.random() < p_right:
                choice = q["answer"]
            else:
                choice = random.choice([option_value(o) for o in q["options"] if option_value(o) != q["answer"]])
            msg = {"q": bot.q_index, "choice": choice}
        await _handle_answer(room, bot, msg)


def _finish(room: Room, reason: str, forced_winner: Optional[str] = None, winner_team: Optional[int] = None) -> None:
    room.status = "finished"
    room.finish_reason = reason
    room.winner_id = forced_winner
    room.winner_team = winner_team
    _schedule_cleanup(room)
    humans = [p.user_id for p in room.players.values() if not p.is_bot]
    # Only real head-to-head races count (not vs. a bot, not an abandoned
    # room), so the leaderboard can't be farmed by beating the computer.
    if reason == "done" and len(humans) >= 2:
        if room.team_mode:
            winners = [pid for pid in humans if _team_of(room, pid) == winner_team]
        else:
            winners = [forced_winner] if forced_winner else []
        asyncio.create_task(_record_stats(winners, humans))


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
        label = next((o for o in q["options"] if isinstance(o, dict) and o["v"] == q["answer"]), None)
        player.last = {"q": player.q_index, "correct": correct, "answer": q["answer"]}
        if label:  # localized answers: let the client show it in the player's language
            player.last["answer_label"] = {"uz": label["uz"], "ru": label["ru"]}
        player.q_index += 1
        if room.team_mode:
            scores = _team_scores(room)
            if max(scores) >= TEAM_TARGET:
                _finish(room, reason="done", forced_winner=player.user_id, winner_team=scores.index(max(scores)))
        elif player.score >= WIN_SCORE:
            _finish(room, reason="done", forced_winner=player.user_id)
        await _broadcast_state(room)


async def _forfeit_after_grace(room: Room, player: Player) -> None:
    await asyncio.sleep(RECONNECT_GRACE_SECONDS)
    async with room.lock:
        if player.ws is not None or room.status not in ("countdown", "playing"):
            return
        player.left = True
        still_in = [p for p in room.players.values() if not p.left]
        humans_in = [p for p in still_in if not p.is_bot]
        if room.team_mode:
            alive_teams = {_team_of(room, p.user_id) for p in still_in}
            if len(alive_teams) <= 1 or not humans_in:
                _finish(room, reason="left", winner_team=next(iter(alive_teams)) if len(alive_teams) == 1 and humans_in else None)
        elif len(still_in) <= 1 or not humans_in:
            # Nobody (or only one) is left to race: the last human standing
            # wins; if only a bot remains there is no winner.
            _finish(room, reason="left", forced_winner=humans_in[0].user_id if humans_in else None)
        await _broadcast_state(room)


@router.get("/leaderboard")
async def duel_leaderboard(
        db: AsyncSession = Depends(get_db),
        current_student: Student = Depends(get_current_student),
):
    """Top 20 by wins, plus the caller's own line (they may not be in the top)."""
    rows = (await db.execute(
        select(DuelStat, Student.full_name, Student.username)
        .join(Student, Student.id == DuelStat.student_id)
        .order_by(DuelStat.wins.desc(), DuelStat.games.asc())
        .limit(20)
    )).all()
    me = (await db.execute(select(DuelStat).where(DuelStat.student_id == current_student.id))).scalar_one_or_none()
    return {
        "top": [
            {"student_id": st.student_id, "name": full or uname, "wins": st.wins, "games": st.games}
            for st, full, uname in rows
        ],
        "me": {"wins": me.wins, "games": me.games} if me else {"wins": 0, "games": 0},
        "me_id": current_student.id,
    }


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
            existing.left = False
            player = existing
        elif len(room.players) >= MAX_PLAYERS:
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
                    if pid == room.host_id and room.status == "waiting" and _can_start(room):
                        room.status = "countdown"
                        await _broadcast_state(room)
                        asyncio.create_task(_run_countdown(room))
            elif kind == "kinds":
                async with room.lock:
                    chosen = msg.get("kinds")
                    if (
                        pid == room.host_id
                        and room.status in ("waiting", "finished")
                        and isinstance(chosen, list)
                    ):
                        valid = [k for k in ALL_KINDS if k in chosen]
                        if valid:
                            room.kinds = valid
                            await _broadcast_state(room)
            elif kind in ("add_bot", "remove_bot"):
                async with room.lock:
                    if pid == room.host_id and room.status in ("waiting", "finished"):
                        bots = [k for k, p in room.players.items() if p.is_bot]
                        if kind == "add_bot" and len(room.players) < MAX_PLAYERS:
                            key = f"bot{len(bots) + 1}"
                            room.players[key] = Player(key, f"Robot {len(bots) + 1} 🤖", None, is_bot=True)
                        elif kind == "remove_bot" and bots:
                            room.players.pop(bots[-1], None)
                        await _broadcast_state(room)
            elif kind == "team_mode":
                async with room.lock:
                    if pid == room.host_id and room.status in ("waiting", "finished"):
                        room.team_mode = bool(msg.get("on"))
                        await _broadcast_state(room)
            elif kind == "level":
                async with room.lock:
                    if pid == room.host_id and room.status in ("waiting", "finished") and msg.get("level") in LEVELS:
                        room.level = msg["level"]
                        await _broadcast_state(room)
            elif kind == "answer":
                await _handle_answer(room, player, msg)
            elif kind == "rematch":
                async with room.lock:
                    if room.status == "finished" and pid == room.host_id:
                        for p in [p for p in room.players.values() if p.left and p.ws is None]:
                            room.players.pop(p.user_id, None)  # dropped out last round
                        if not _can_start(room):
                            await _broadcast_state(room)
                            continue
                        room.status = "countdown"
                        room.finish_reason = None
                        room.winner_id = None
                        room.winner_team = None
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
