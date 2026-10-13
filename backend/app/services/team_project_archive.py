"""When a team project is over, so the teacher can move it out of the active list.

`TeamProject.status` cannot decide this: on production the only project has status `planning` and no
`activated_at` although its teams work and the last task deadline passed. The facts that do exist are the
teams' statuses and the tasks' deadlines, so "past" is read from those.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.models.team_project import TeamProject, TeamProjectStatus, TeamStatus

_FINISHED_TEAM = (TeamStatus.submitted, TeamStatus.reviewed)


def _aware(moment: Optional[datetime]) -> Optional[datetime]:
    if moment is not None and moment.tzinfo is None:
        return moment.replace(tzinfo=timezone.utc)
    return moment


def is_past(tp: TeamProject, now: datetime) -> bool:
    """Cancelled; every team finished; or no task can still be worked on (the latest task deadline of any team, with
    teacher extensions already applied to the tasks, is behind us). Without any task deadline a started project ends
    when `deadline_days` after activation run out. A project nobody has planned yet is never past."""
    if tp.status == TeamProjectStatus.cancelled:
        return True
    if tp.teams and all(team.status in _FINISHED_TEAM for team in tp.teams):
        return True
    deadlines = [_aware(t.deadline_at) for team in tp.teams for t in team.tasks if t.deadline_at is not None]
    if deadlines:
        return max(deadlines) < now
    started = _aware(tp.activated_at)
    return started is not None and started + timedelta(days=tp.deadline_days) < now
