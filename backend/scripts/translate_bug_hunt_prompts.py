"""Backfill question_text_ru for bug_hunt lesson_questions.

bug_hunt rows have always had bug_explanation/bug_explanation_ru, but
question_text_ru never existed as a column until the migration that added
it (bb44cc55dd66) — so every bug-hunt prompt in the bank was Uzbek-only.
This is a one-off backfill for the existing bank; new rows should pass
question_text_ru directly (see insert_lesson_bug_questions_batch.py).

Reuses bulk_translate.py's translate_with_retry (same model, same
Retry-After-aware backoff) rather than reinventing the OpenAI call.

Usage: python3 translate_bug_hunt_prompts.py [--dry-run]
"""
from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402

import httpx  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.config import settings  # noqa: E402
from bulk_translate import translate_with_retry, engine, CONCURRENCY, TIMEOUT_S  # noqa: E402

COMMIT_EVERY = 25


async def main(dry_run: bool) -> None:
    t_start = time.monotonic()
    async with engine.connect() as conn:
        rows = (await conn.execute(text("""
            SELECT id, question_text FROM lesson_questions
            WHERE question_kind = 'bug_hunt'
              AND (question_text_ru IS NULL OR question_text_ru = '')
            ORDER BY id
        """))).all()

    print(f"Bug-hunt prompts needing RU: {len(rows)}")
    if not rows:
        return
    if dry_run:
        for rid, text_uz in rows[:5]:
            print(f"  [{rid}] {text_uz[:80]!r}")
        print("(dry run — no API calls made, no writes)")
        return

    sem = asyncio.Semaphore(CONCURRENCY)
    results: dict[int, str] = {}
    failed: list[int] = []
    completed = 0

    async with httpx.AsyncClient(timeout=TIMEOUT_S, proxy=settings.HTTP_PROXY or None) as client:
        async def _translate_one(row_id: int, source: str):
            nonlocal completed
            async with sem:
                tr = await translate_with_retry(client, source)
                if tr:
                    results[row_id] = tr
                else:
                    failed.append(row_id)
                completed += 1
                if completed % 20 == 0 or completed == len(rows):
                    print(f"  {completed}/{len(rows)} translated ({len(failed)} failed so far)")

        await asyncio.gather(*[_translate_one(rid, txt) for rid, txt in rows])

    print(f"Translated: {len(results)}  Failed: {len(failed)}")
    if failed:
        print(f"Failed ids (left NULL, re-run script to retry): {failed}")

    async with engine.begin() as conn:
        written = 0
        for rid, translated in results.items():
            await conn.execute(
                text("UPDATE lesson_questions SET question_text_ru = :t WHERE id = :id"),
                {"t": translated, "id": rid},
            )
            written += 1
            if written % COMMIT_EVERY == 0:
                print(f"  wrote {written}/{len(results)}")

    print(f"Done in {time.monotonic() - t_start:.1f}s. Wrote {len(results)} rows.")


if __name__ == "__main__":
    asyncio.run(main(dry_run="--dry-run" in sys.argv))
