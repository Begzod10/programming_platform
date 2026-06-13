import json
import logging
from collections import defaultdict
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self._sessions: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, session_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self._sessions[session_id].append(ws)
        logger.debug("WS connect session=%d total=%d", session_id, len(self._sessions[session_id]))

    def disconnect(self, session_id: int, ws: WebSocket) -> None:
        conns = self._sessions.get(session_id, [])
        try:
            conns.remove(ws)
        except ValueError:
            pass
        if not conns:
            self._sessions.pop(session_id, None)
        logger.debug("WS disconnect session=%d remaining=%d", session_id, len(conns))

    async def broadcast(self, session_id: int, payload: dict) -> None:
        dead: list[WebSocket] = []
        for ws in list(self._sessions.get(session_id, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(session_id, ws)


# Singleton used by both the WS endpoint and REST handlers
manager = ConnectionManager()
