"""Phase 3 sub-step: for GameQuestion quiz rows whose `question_text` /
`options` are ALREADY Russian (Cyrillic) — an artifact of the known
import-pairing bug where a lesson had only a ru-authored LessonQuestion row
at some position and it became the GameQuestion's primary text — the correct
`question_text_ru`/`options_ru` backfill is simply a copy of the existing
Russian content (no translation needed, since it's already Russian).

Uses the exact same _detect_lang rule as team_game_questions.py (Cyrillic
presence). No translation API used. ORM-only, idempotent, no DDL.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402

from sqlalchemy import select, or_  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.team_game import GameQuestion  # noqa: E402


def _detect_lang(text: str) -> str:
    """Mirrors team_game_questions.py's _detect_lang exactly."""
    return "ru" if any("Ѐ" <= c <= "ӿ" for c in text) else "uz"


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(GameQuestion).where(
                GameQuestion.question_kind == "quiz",
                or_(GameQuestion.question_text_ru.is_(None), GameQuestion.question_text_ru == "", GameQuestion.options_ru.is_(None)),
            )
        )
        rows = result.scalars().all()
        candidates = [r for r in rows if _detect_lang(r.question_text) == "ru"]
        print(f"Already-RU rows found: {len(candidates)} (of {len(rows)} total still needing work)")

        written = 0
        for row in candidates:
            row.question_text_ru = row.question_text
            row.options_ru = list(row.options)
            written += 1
        await db.commit()
        print(f"Copied {written} rows.")


if __name__ == "__main__":
    asyncio.run(main())
