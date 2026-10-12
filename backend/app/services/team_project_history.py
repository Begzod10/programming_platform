"""Results of a student's team projects: standings per project and a short summary per team.

Only teams that FINISHED (final project submitted) get a place; an unfinished team is
listed with what it has done, unplaced — a half-done team must not look like it came 3rd.
The summary is assembled from facts, not written by an AI, so it can't invent anything.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app.models.team_project import TaskStatus, TeamProject, TeamProjectTeam, TeamStatus

_GRADE_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3, "F": 4}
_FINISHED = (TeamStatus.submitted, TeamStatus.reviewed)
_OPEN_TASK = (TaskStatus.assigned, TaskStatus.changes_requested)


@dataclass
class TeamStanding:
    team: TeamProjectTeam
    approved: int
    total: int
    avg_score: Optional[int]
    final_grade: Optional[str]
    points: int
    overdue_open: int
    finished: bool
    place: Optional[int] = None


def _aware(moment: Optional[datetime]) -> Optional[datetime]:
    if moment is not None and moment.tzinfo is None:
        return moment.replace(tzinfo=timezone.utc)
    return moment


def build_standing(team: TeamProjectTeam, final_grade: Optional[str], now: datetime) -> TeamStanding:
    tasks = list(team.tasks)
    scored = [t.ai_score for t in tasks if t.status == TaskStatus.approved and t.ai_score is not None]
    overdue = sum(
        1 for t in tasks
        if t.status in _OPEN_TASK and t.deadline_at is not None and _aware(t.deadline_at) < now
    )
    return TeamStanding(
        team=team,
        approved=sum(1 for t in tasks if t.status == TaskStatus.approved),
        total=len(tasks),
        avg_score=round(sum(scored) / len(scored)) if scored else None,
        final_grade=final_grade,
        points=sum(t.points_awarded or 0 for t in tasks),
        overdue_open=overdue,
        finished=team.status in _FINISHED,
    )


def rank(standings: list[TeamStanding]) -> list[TeamStanding]:
    """Finished teams first, placed 1..n; the rest follow by progress, unplaced."""
    def finished_key(s: TeamStanding):
        return (
            _GRADE_ORDER.get(s.final_grade or "", 99),
            -(s.approved / s.total if s.total else 0),
            -(s.avg_score or 0),
            _aware(s.team.submitted_at) or datetime.max.replace(tzinfo=timezone.utc),
            s.team.id,
        )

    finished = sorted((s for s in standings if s.finished), key=finished_key)
    for i, s in enumerate(finished, start=1):
        s.place = i
    unfinished = sorted(
        (s for s in standings if not s.finished),
        key=lambda s: (-(s.approved / s.total if s.total else 0), -(s.avg_score or 0), s.team.id),
    )
    return finished + unfinished


def summary(s: TeamStanding) -> tuple[str, str]:
    """(uz, ru) one-paragraph summary built from the team's numbers."""
    avg_uz = f" (o'rtacha {s.avg_score})" if s.avg_score is not None else ""
    avg_ru = f" (средний балл {s.avg_score})" if s.avg_score is not None else ""
    if s.finished:
        grade_uz = f", bahosi {s.final_grade}" if s.final_grade else ""
        grade_ru = f", оценка {s.final_grade}" if s.final_grade else ""
        return (
            f"{s.approved}/{s.total} vazifa tasdiqlandi{avg_uz}. Yakuniy loyiha topshirildi{grade_uz}. Jamoa ballari: {s.points}.",
            f"Подтверждено заданий: {s.approved}/{s.total}{avg_ru}. Итоговый проект сдан{grade_ru}. Баллы команды: {s.points}.",
        )
    late_uz = f" {s.overdue_open} ta vazifa muddatida topshirilmagan." if s.overdue_open else ""
    late_ru = f" Заданий не сдано в срок: {s.overdue_open}." if s.overdue_open else ""
    return (
        f"Tugallanmagan: {s.approved}/{s.total} vazifa tasdiqlandi{avg_uz}.{late_uz}",
        f"Не завершено: подтверждено {s.approved}/{s.total}{avg_ru}.{late_ru}",
    )


def project_title(tp: TeamProject, my_team: TeamProjectTeam) -> str:
    return my_team.project_title or tp.title or "Jamoaviy loyiha"
