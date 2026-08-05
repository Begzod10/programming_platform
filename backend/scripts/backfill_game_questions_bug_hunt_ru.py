"""Backfill question_text_ru on already-imported game_questions rows.

import_questions_from_lesson now copies lesson_questions.question_text_ru
into new GameQuestion rows going forward, but that fix only applies to
future imports. Sessions that already imported bug-hunt questions (before
the fix, or before translate_bug_hunt_prompts.py populated the bank) have
GameQuestion rows with question_text_ru still NULL even though their
source lesson_questions row now has a translation.

Matches by exact question_text equality — the import path copies
question_text verbatim with no transformation, so this is a safe join key.
Ambiguous matches (same bug-hunt prompt text reused across multiple bank
rows) are skipped and reported rather than guessed at.

Usage: python3 backfill_game_questions_bug_hunt_ru.py [--dry-run]
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402

from sqlalchemy import text  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401


async def main(dry_run: bool) -> None:
    async with AsyncSessionLocal() as db:
        gq_rows = (await db.execute(text("""
            SELECT id, question_text FROM game_questions
            WHERE question_kind = 'bug_hunt'
              AND (question_text_ru IS NULL OR question_text_ru = '')
        """))).all()
        print(f"game_questions needing backfill: {len(gq_rows)}")
        if not gq_rows:
            return

        lq_rows = (await db.execute(text("""
            SELECT question_text, question_text_ru FROM lesson_questions
            WHERE question_kind = 'bug_hunt'
              AND question_text_ru IS NOT NULL AND question_text_ru <> ''
        """))).all()

        by_text: dict[str, list[str]] = {}
        for src, ru in lq_rows:
            by_text.setdefault(src, []).append(ru)

        updates: dict[int, str] = {}
        unmatched: list[int] = []
        ambiguous: list[int] = []
        for gq_id, src in gq_rows:
            candidates = by_text.get(src)
            if not candidates:
                unmatched.append(gq_id)
            elif len(set(candidates)) > 1:
                ambiguous.append(gq_id)
            else:
                updates[gq_id] = candidates[0]

        print(f"Matched: {len(updates)}  Unmatched (no bank translation yet): {len(unmatched)}  Ambiguous: {len(ambiguous)}")
        if unmatched:
            print(f"  unmatched ids: {unmatched}")
        if ambiguous:
            print(f"  ambiguous ids: {ambiguous}")

        if dry_run:
            print("(dry run — no writes)")
            return

        for gq_id, ru in updates.items():
            await db.execute(
                text("UPDATE game_questions SET question_text_ru = :ru WHERE id = :id"),
                {"ru": ru, "id": gq_id},
            )
        await db.commit()
        print(f"Wrote {len(updates)} rows.")


if __name__ == "__main__":
    asyncio.run(main(dry_run="--dry-run" in sys.argv))
