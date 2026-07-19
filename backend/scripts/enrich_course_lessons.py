"""Enrich lessons with rich UZ + RU content from a JSON manifest.

This is the reusable version of the one-shot ``/tmp/enrich_c67.py`` … ``c70.py``
scripts that ran during the "10× more HTML + mermaid + code + 5–7 mixed
exercises" pass on JS courses 67–70. Content is now loaded from a manifest
file instead of being baked into a per-course script, so the pattern can be
run again for any course without editing Python.

What it does for every lesson in the manifest:

  1. Loads existing exercises. Anything with ``id < protect_below`` is left
     alone (guards pre-existing hand-curated rows). Anything at or above the
     threshold that isn't referenced by ``uz.exercises`` is deleted.
  2. Inserts/updates the exercises listed under ``uz.exercises``. RU fields
     are pulled from ``ru.exercises`` (positional). Both languages are
     required — an entry missing a RU counterpart aborts the whole lesson.
  3. Rebuilds ``lessons.sections_json`` from ``uz.sections`` (keeping the
     existing ``type:"file"`` section at order 0 when
     ``keep_file_section`` is true — the file upload widget lives there).
     Newly-inserted exercise IDs are stitched into the ``type:"exercise"``
     section so the frontend can render them.
  4. Upserts one ``translation_cache`` row per lesson with
     ``field_name='sections_json'``, ``lang='ru'`` and the RU sections
     serialised. That's what the read path uses when a student opens the
     lesson in Russian.

Manifest format (see ``enrich_manifests/example.json`` for a full sample):

    {
      "course_id": 67,
      "protect_exercise_ids_below": 3000,
      "keep_file_section": true,
      "lessons": [
        {
          "lesson_id": 541,
          "uz": {
            "sections": [
              {"type": "text",     "label": "Nazariya", "html": "<h2>…</h2>…"},
              {"type": "code",     "label": "Misol",    "code": "// …",
               "lang": "javascript"}
            ],
            "exercises": [
              {
                "title": "…",
                "description": "…",
                "exercise_type": "multiple_choice",
                "options": ["A", "B", "C", "D"],
                "correct_answers": "B",
                "is_multiple_select": false,
                "hint": "…",
                "explanation": "…",
                "difficulty_level": "Medium",
                "points": 3
              }
            ]
          },
          "ru": {
            "sections": [ /* same shape as uz.sections */ ],
            "exercises": [ /* same length as uz.exercises, positional */ ]
          }
        }
      ]
    }

Usage:
    cd backend
    # Dry-run (default) — prints planned changes without touching the DB:
    python scripts/enrich_course_lessons.py --manifest scripts/enrich_manifests/js_advanced.json

    # Actually write:
    python scripts/enrich_course_lessons.py \\
        --manifest scripts/enrich_manifests/js_advanced.json --apply

The dry-run is verbose on purpose — it's the review surface. Never run
``--apply`` before a clean dry-run.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 — ensure all mappers registered
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise, ExerciseType  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402


# Difficulty → default points if the manifest doesn't override.
DEFAULT_POINTS = {"Easy": 2, "Medium": 3, "Hard": 4}
VALID_EXERCISE_TYPES = {t.value for t in ExerciseType}
VALID_SECTION_TYPES = {"text", "code", "exercise", "file"}


# ─── manifest loading + validation ─────────────────────────────────────────


def _load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "lessons" not in data:
        raise ValueError(f"{path}: manifest must be an object with 'lessons' key")
    _validate_manifest(data, path)
    return data


def _validate_manifest(m: dict, path: Path) -> None:
    """Fail loudly on shape problems before we touch a single row."""
    for i, lesson in enumerate(m.get("lessons", [])):
        prefix = f"{path.name}: lessons[{i}]"
        lid = lesson.get("lesson_id")
        if not isinstance(lid, int):
            raise ValueError(f"{prefix}: lesson_id must be an int, got {lid!r}")

        uz = lesson.get("uz") or {}
        ru = lesson.get("ru") or {}
        if not uz or not ru:
            raise ValueError(
                f"{prefix} (lesson_id={lid}): both 'uz' and 'ru' blocks are required"
            )

        uz_sections = uz.get("sections") or []
        ru_sections = ru.get("sections") or []
        if len(uz_sections) != len(ru_sections):
            raise ValueError(
                f"{prefix} (lesson_id={lid}): sections count mismatch — "
                f"uz={len(uz_sections)} vs ru={len(ru_sections)}"
            )
        for j, s in enumerate(uz_sections):
            if s.get("type") not in VALID_SECTION_TYPES:
                raise ValueError(
                    f"{prefix}.uz.sections[{j}]: bad type {s.get('type')!r}"
                )

        uz_exercises = uz.get("exercises") or []
        ru_exercises = ru.get("exercises") or []
        if len(uz_exercises) != len(ru_exercises):
            raise ValueError(
                f"{prefix} (lesson_id={lid}): exercises count mismatch — "
                f"uz={len(uz_exercises)} vs ru={len(ru_exercises)}"
            )
        for j, ex in enumerate(uz_exercises):
            et = ex.get("exercise_type")
            if et not in VALID_EXERCISE_TYPES:
                raise ValueError(
                    f"{prefix}.uz.exercises[{j}]: bad exercise_type {et!r}"
                )


# ─── small helpers ─────────────────────────────────────────────────────────


def _jdump(value: Any) -> str | None:
    """Consistent JSON serialisation — array/object → string, scalars pass through."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _build_exercise_kwargs(
    ex_uz: dict,
    ex_ru: dict,
    lesson_id: int,
    order: int,
) -> dict:
    """Turn a manifest exercise pair (UZ + RU) into Exercise column kwargs."""
    difficulty = ex_uz.get("difficulty_level", "Easy")
    return dict(
        lesson_id=lesson_id,
        title=ex_uz["title"],
        title_ru=ex_ru.get("title"),
        description=ex_uz.get("description", ex_uz["title"]),
        description_ru=ex_ru.get("description"),
        exercise_type=ex_uz["exercise_type"],
        options=_jdump(ex_uz.get("options")),
        correct_answers=_jdump(ex_uz.get("correct_answers")),
        drag_items=_jdump(ex_uz.get("drag_items")),
        correct_order=_jdump(ex_uz.get("correct_order")),
        is_multiple_select=bool(ex_uz.get("is_multiple_select", False)),
        expected_answer=ex_uz.get("expected_answer"),
        expected_answer_ru=ex_ru.get("expected_answer"),
        hint=ex_uz.get("hint"),
        hint_ru=ex_ru.get("hint"),
        explanation=ex_uz.get("explanation"),
        explanation_ru=ex_ru.get("explanation"),
        difficulty_level=difficulty,
        points=int(ex_uz.get("points", DEFAULT_POINTS.get(difficulty, 2))),
        order=order,
        is_active=True,
    )


def _build_sections_json(
    manifest_sections: list[dict],
    exercise_ids: list[int],
    file_section: dict | None,
) -> str:
    """Compose the sections_json blob the frontend reads.

    ``file_section`` (if given) is placed at order 0 — it carries the file
    upload widget config for the lesson. Manifest sections start at order 1.
    An exercise section gets its ``exercises`` array populated with stub
    objects that only need an ``id`` — the frontend fetches the real row.
    """
    result: list[dict] = []
    if file_section is not None:
        result.append({**file_section, "order": 0})

    ex_iter = iter(exercise_ids)
    for i, section in enumerate(manifest_sections, start=1):
        if section["type"] == "exercise":
            result.append({
                **section,
                "order": i,
                "exercises": [{"id": next(ex_iter)} for _ in range(len(exercise_ids))],
            })
        else:
            result.append({**section, "order": i})
    return json.dumps(result, ensure_ascii=False)


async def _upsert_ru_translation(
    db,
    lesson_id: int,
    source_sections_json: str,
    ru_sections_json: str,
) -> str:
    """Upsert the RU sections_json into translation_cache. Returns 'insert' | 'update' | 'noop'."""
    row = (
        await db.execute(
            select(TranslationCache).where(
                TranslationCache.entity_type == "lesson",
                TranslationCache.entity_id == lesson_id,
                TranslationCache.lang == "ru",
                TranslationCache.field_name == "sections_json",
            )
        )
    ).scalar_one_or_none()
    source_hash = _sha256(source_sections_json)
    if row is None:
        db.add(TranslationCache(
            entity_type="lesson",
            entity_id=lesson_id,
            lang="ru",
            field_name="sections_json",
            translated_text=ru_sections_json,
            source_text_hash=source_hash,
            provider="manual",
        ))
        return "insert"
    if row.translated_text == ru_sections_json and row.source_text_hash == source_hash:
        return "noop"
    row.translated_text = ru_sections_json
    row.source_text_hash = source_hash
    row.provider = "manual"
    return "update"


# ─── main enrich flow ──────────────────────────────────────────────────────


async def enrich(manifest_path: Path, apply: bool) -> None:
    manifest = _load_manifest(manifest_path)
    protect_below = int(manifest.get("protect_exercise_ids_below", 0))
    keep_file_section = bool(manifest.get("keep_file_section", True))

    label = "APPLY" if apply else "DRY-RUN"
    print(f"=== Enrich lessons ({label}) — {manifest_path.name} ===")
    print(f"course_id={manifest.get('course_id', '?')}  "
          f"lessons={len(manifest['lessons'])}  "
          f"protect_below={protect_below}  "
          f"keep_file={keep_file_section}\n")

    totals = dict(deleted=0, inserted=0, sections_updated=0, ru_cached=0, skipped=0)

    async with AsyncSessionLocal() as db:
        for entry in manifest["lessons"]:
            lesson_id = entry["lesson_id"]
            uz = entry["uz"]
            ru = entry["ru"]

            lesson = (
                await db.execute(select(Lesson).where(Lesson.id == lesson_id))
            ).scalar_one_or_none()
            if lesson is None:
                print(f"  ⚠️  lesson_id={lesson_id} — not found in DB, skipped")
                totals["skipped"] += 1
                continue

            file_section = None
            if keep_file_section and lesson.sections_json:
                try:
                    current = json.loads(lesson.sections_json)
                    if isinstance(current, list):
                        for s in current:
                            if isinstance(s, dict) and s.get("type") == "file":
                                file_section = {k: v for k, v in s.items() if k != "order"}
                                break
                except json.JSONDecodeError:
                    print(f"     • sections_json unparseable, no file section preserved")

            existing = (
                await db.execute(
                    select(Exercise)
                    .where(Exercise.lesson_id == lesson_id)
                    .order_by(Exercise.id)
                )
            ).scalars().all()

            to_delete = [e for e in existing if e.id >= protect_below]
            deleted_count = len(to_delete)
            if apply:
                for row in to_delete:
                    await db.delete(row)
                if to_delete:
                    await db.flush()

            new_ids: list[int] = []
            uz_ex = uz.get("exercises", [])
            ru_ex = ru.get("exercises", [])
            inserted_count = 0
            for order, (ex_uz, ex_ru) in enumerate(zip(uz_ex, ru_ex)):
                new_row = Exercise(**_build_exercise_kwargs(ex_uz, ex_ru, lesson_id, order))
                inserted_count += 1
                if apply:
                    db.add(new_row)
                    await db.flush()  # so new_row.id is populated
                    new_ids.append(new_row.id)
                else:
                    # Dry-run: fake an id so sections_json preview still renders.
                    new_ids.append(-(order + 1))

            uz_sections_json = _build_sections_json(uz["sections"], new_ids, file_section)
            ru_sections_json = _build_sections_json(ru["sections"], new_ids, file_section)

            sections_changed = lesson.sections_json != uz_sections_json
            if apply and sections_changed:
                lesson.sections_json = uz_sections_json

            ru_action = "noop"
            if apply:
                ru_action = await _upsert_ru_translation(
                    db, lesson_id, uz_sections_json, ru_sections_json,
                )
                await db.commit()  # per-lesson so a bad manifest entry doesn't nuke prior ones

            print(f"  📝 lesson_id={lesson_id:>4} "
                  f"delete={deleted_count} insert={inserted_count} "
                  f"sections={'yes' if sections_changed else 'no'} "
                  f"ru={ru_action}")

            totals["deleted"] += deleted_count
            totals["inserted"] += inserted_count
            if sections_changed:
                totals["sections_updated"] += 1
            if ru_action in ("insert", "update"):
                totals["ru_cached"] += 1

    print(f"\n--- Summary ---")
    for k, v in totals.items():
        print(f"  {k}: {v}")
    if not apply:
        print("\n(dry-run — no changes written. Re-run with --apply to commit.)")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--manifest", required=True, type=Path,
                   help="Path to the JSON manifest describing the enrichment.")
    p.add_argument("--apply", action="store_true",
                   help="Actually write to the DB. Default is dry-run.")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    if not args.manifest.exists():
        raise SystemExit(f"Manifest not found: {args.manifest}")
    asyncio.run(enrich(args.manifest, apply=args.apply))
