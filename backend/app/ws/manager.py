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


# Singleton used by both the WS endpoint and REST handlers (team-game feature).
manager = ConnectionManager()

# Team Projects gets its OWN two manager instances rather than reusing `manager`
# above, keyed by team_id and team_project_id respectively. Two reasons:
#   1. team_id/team_project_id and game_sessions.id are separate autoincrement
#      PK spaces — reusing one dict keyed by a bare int risks a real session
#      broadcasting into an unrelated team-project channel (or vice versa) the
#      moment their ids happen to coincide.
#   2. Team Projects has a privacy boundary game sessions don't: students on
#      different teams within the same project must never see each other's
#      task detail/skill levels (see team_project.py's
#      _redact_team_read_for_other_student — a real leak was found and fixed
#      there once already this session). A single project-wide channel
#      broadcasting the full unredacted project to every connected socket
#      would reopen exactly that leak over WebSocket. So: team_ws_manager
#      carries one team's own detail to that team's members + owning teacher;
#      team_project_ws_manager carries the full multi-team project detail,
#      teacher-only.
team_ws_manager = ConnectionManager()
team_project_ws_manager = ConnectionManager()
