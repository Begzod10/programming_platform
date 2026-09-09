"""Phase 2: hand-translated RU backfill for GameQuestion bug_hunt rows
(session 125, "Blue 5-6"). No translation API used — every string below was
composed by hand by a fluent Russian speaker.

Idempotent: only updates rows still missing question_text_ru; safe to re-run.
ORM-only via AsyncSessionLocal, no DDL, no app.main import.
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

# Keyed by the exact UZ question_text (source of truth), mapping to
# (question_text_ru, bug_explanation_ru). Populated by hand.
TRANSLATIONS: dict[str, tuple[str, str]] = {
    "Bu sahifada bitta teg to'g'ri yopilmagan. Xato qaysi qatorda?": (
        "На этой странице один тег закрыт неправильно. В какой строке ошибка?",
        "Во 2-й строке тег <p> открыт, но закрывающего тега </p> нет. В HTML почти все теги "
        "должны быть парными (открывающий и закрывающий). Правильно: <p>Salom, men Aziz!</p>.",
    ),
    "Bu sahifada bitta sarlavha noto'g'ri teg bilan yozilgan. Xato qaysi qatorda?": (
        "На этой странице один заголовок написан с неправильным тегом. В какой строке ошибка?",
        "Во 2-й строке используется тег <h7>, но в HTML заголовки существуют только от <h1> "
        "до <h6> — тега <h7> не существует, и он не работает. Правильно: для самого маленького "
        "заголовка используйте <h6>.",
    ),
    "Bu sahifada bitta qatorda tirnoq belgisi yetishmayapti. Xato qaysi qatorda?": (
        "На этой странице в одной строке не хватает кавычки. В какой строке ошибка?",
        'В 1-й строке в конце значения style="color: red не хватает закрывающей кавычки ("). '
        'Каждое значение style должно быть заключено между двумя кавычками. Правильно: '
        'style="color: red".',
    ),
    "Bu sahifada <img> tegiga kerak bo'lmagan teg qo'shilgan. Xato qaysi qatorda?": (
        "На этой странице к тегу <img> добавлен ненужный тег. В какой строке ошибка?",
        'Во 2-й строке добавлен закрывающий тег </img>, но, как говорилось на уроке, у тега '
        '<img> НЕТ закрывающего тега — он самозакрывающийся. Правильно: '
        '<img src="mushuk.jpg" alt="mushuk"> (без закрывающего тега).',
    ),
    "Bu sahifadagi ro'yxat teglari noto'g'ri joylashgan. Xato qaysi qatorda?": (
        "Теги списка на этой странице расположены неправильно. В какой строке ошибка?",
        "Теги <li> в строках 2 и 3 не обёрнуты в <ul> (список) — тег <li> всегда должен "
        "находиться внутри <ul> или <ol>. Правильно: нужно открыть тег <ul> перед тегами <li>, "
        "а затем закрыть его тегом </ul>.",
    ),
    "Bu sahifada tugma tegi to'g'ri yopilmagan. Xato qaysi qatorda?": (
        "На этой странице тег кнопки закрыт неправильно. В какой строке ошибка?",
        'Во 2-й строке тег <button> открыт, но закрывающего тега </button> нет. Правильно: '
        '<button style="background-color: pink">Bosing!</button>.',
    ),
}


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(GameQuestion).where(
                GameQuestion.question_kind == "bug_hunt",
                or_(GameQuestion.question_text_ru.is_(None), GameQuestion.question_text_ru == ""),
            ).order_by(GameQuestion.id)
        )
        rows = result.scalars().all()
        print(f"Phase2: {len(rows)} GameQuestion bug_hunt rows need RU")

        written = 0
        unmatched = []
        for row in rows:
            pair = TRANSLATIONS.get(row.question_text)
            if not pair:
                unmatched.append(row.id)
                continue
            row.question_text_ru, row.bug_explanation_ru = pair
            written += 1
        await db.commit()
        print(f"Phase2 wrote {written} rows. Unmatched (need manual review): {unmatched}")


if __name__ == "__main__":
    asyncio.run(main())
