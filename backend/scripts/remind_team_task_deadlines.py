"""Tell students how many days are left to submit their team-project task, on demand and to everyone with an open
task (the daily scheduler job only speaks up on milestone days, see app/services/team_project_deadline_reminders.py).
Safe to re-run the same day: a task already reminded today is skipped.

    python scripts/remind_team_task_deadlines.py            # dry-run: who would get what
    python scripts/remind_team_task_deadlines.py --apply    # create the notifications
"""
from __future__ import annotations
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.services.team_project_deadline_reminders import send_deadline_reminders  # noqa: E402


async def main(apply: bool) -> None:
    async with AsyncSessionLocal() as db:
        rows = await send_deadline_reminders(db, apply=apply, milestones_only=False)
    for r in rows:
        print(f"team {r['team_id']} task {r['task_id']} student {r['student_id']} left={r['left']:>3} "
              f"{'(already sent today) ' if r['skipped'] else ''}| {r['title']}")
    new = sum(1 for r in rows if not r["skipped"])
    print(f"\n{'sent' if apply else 'DRY-RUN, would send'}: {new} of {len(rows)} open tasks")


if __name__ == "__main__":
    asyncio.run(main("--apply" in sys.argv))
