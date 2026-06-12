"""
clean_dictionary_contexts.py
============================

Scan UserDictionary rows whose `context` looks like AI keyword-stew and
either clear them or regenerate them via the explainer service.

Why:
    Earlier versions of the AI explanation pipeline let token-soup
    contexts slip through (e.g. "content appearance behavior HTML
    structure tags Browser CSS …" or short comma-lists like
    "Frontend, Backend, JavaScript, HTML, CSS"). The current
    `_looks_like_keyword_stew` heuristic in grok_service.py rejects
    those, but rows saved before the fix are still in the DB.

Usage:
    cd /var/www/tech_gennis/backend && source venv/bin/activate
    python -m scripts.clean_dictionary_contexts                # dry-run, lists offenders
    python -m scripts.clean_dictionary_contexts --apply         # clear contexts in place
    python -m scripts.clean_dictionary_contexts --apply --regen # re-ask the AI for each one
    python -m scripts.clean_dictionary_contexts --student-id 80 # scope to one student

The script never deletes rows — it only mutates `context` (and
`part_of_speech` if --regen is set). Safe to re-run.
"""

import argparse
import asyncio
import sys
from typing import Optional

# Ensure project root is on sys.path when invoked directly
sys.path.insert(0, ".")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.db import base as _b  # noqa: F401 — registers mappers
from app.models.dictionary import UserDictionary
from app.models.lesson import Lesson
from app.models.course import Course
from app.services.grok_service import (
    _looks_like_keyword_stew,
    explain_word_with_ai,
)


def _is_bad_context(context: Optional[str]) -> bool:
    """Conservative — only flags genuine keyword stew, not short notes."""
    if not context:
        return False
    s = context.strip()
    if not s:
        return False
    return _looks_like_keyword_stew(s)


async def _regen_context(
    db: AsyncSession,
    row: UserDictionary,
) -> tuple[str, Optional[str]]:
    """Return (new_context, new_part_of_speech)."""
    course_title = ""
    lesson_title = ""
    lesson_excerpt = ""
    if row.lesson_id:
        lesson = (
            await db.execute(select(Lesson).where(Lesson.id == row.lesson_id))
        ).scalar_one_or_none()
        if lesson:
            lesson_title = lesson.title or ""
            lesson_excerpt = (lesson.text_content or "")[:400]
            if lesson.course_id:
                course_title = (
                    await db.execute(
                        select(Course.title).where(Course.id == lesson.course_id)
                    )
                ).scalar_one_or_none() or ""

    try:
        ai = await explain_word_with_ai(
            row.word,
            course_title=course_title,
            lesson_title=lesson_title,
            lesson_excerpt=lesson_excerpt,
        )
        new_ctx = (ai.get("short_definition") or "").strip()
        pos_raw = (ai.get("part_of_speech") or "").strip().lower()
        new_pos = pos_raw if pos_raw and len(pos_raw) <= 40 else None
        return new_ctx, new_pos
    except Exception as e:
        print(f"  ! regen failed for word={row.word!r}: {e}")
        return "", None


async def run(args: argparse.Namespace) -> None:
    async with AsyncSessionLocal() as db:
        stmt = select(UserDictionary)
        if args.student_id is not None:
            stmt = stmt.where(UserDictionary.student_id == args.student_id)
        rows = (await db.execute(stmt)).scalars().all()

        offenders = [r for r in rows if _is_bad_context(r.context)]
        print(f"Scanned {len(rows)} dictionary rows; flagged {len(offenders)} bad contexts.")
        if not offenders:
            return

        if not args.apply:
            print("\n-- DRY RUN — would touch these rows (use --apply to mutate) --")
            for r in offenders[:30]:
                preview = (r.context or "")[:80].replace("\n", " ")
                print(f"  #{r.id:>6}  student={r.student_id}  word={r.word!r:<28}  ctx={preview!r}")
            if len(offenders) > 30:
                print(f"  … {len(offenders) - 30} more")
            return

        touched = 0
        for r in offenders:
            if args.regen:
                new_ctx, new_pos = await _regen_context(db, r)
                if new_ctx:
                    r.context = new_ctx
                    if new_pos:
                        r.part_of_speech = new_pos
                    touched += 1
                    print(f"  ✓ regen #{r.id} word={r.word!r} -> {new_ctx[:60]!r}")
                else:
                    # Regen failed sanity — clear rather than keep junk
                    r.context = ""
                    touched += 1
                    print(f"  ⚠ cleared #{r.id} word={r.word!r} (regen produced nothing usable)")
            else:
                r.context = ""
                touched += 1

        await db.commit()
        print(f"\nDone. Mutated {touched} rows.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply", action="store_true",
                   help="Actually mutate rows. Without this, the script is a dry run.")
    p.add_argument("--regen", action="store_true",
                   help="When applying, re-ask the AI for each flagged row instead of just clearing.")
    p.add_argument("--student-id", type=int, default=None,
                   help="Limit to one student's dictionary (debug aid).")
    args = p.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
