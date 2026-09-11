"""Fix lesson 511 ("Extend va Placeholder Selectorlar", course 55 SASS/SCSS
Asoslari): its example code block introduced `@use "placeholders" as *;`
mid-snippet — (a) `@use` isn't taught until lesson 512 ("Partials, @use va
Loyiha Tuzilmasi"), which comes AFTER this lesson, and (b) more concretely,
Sass requires every `@use`/`@forward` rule to appear before any other rule
in a file — placing it after the %card-base/%card-hover placeholder
definitions is a real compile error if a student pastes this as one file
(the surrounding comments frame it as two separate files, "_placeholders
.scss" then "_cards.scss", but it's presented as a single "scss" code
block with no actual second file — this lesson's own runnable LessonSample
(id 1539) already correctly avoids this by keeping everything in one
actually-compilable style.scss).

Fix: drop the fake two-file framing and the @use line entirely, collapse
into one coherent, actually-valid single-file example (matching what the
LessonSample already does), replacing the misleading "_cards.scss" comment
with a plain one-line note that @use is covered next lesson — same
forward-reference style already used in this lesson's own "Amaliyot" text
section, so it's not an unexplained forward reference, just not a fake
broken code sample.

Edits both the UZ source column (lessons.sections_json) and the cached RU
translation (translation_cache), matching the two texts exactly captured
from the live DB before editing.
"""
from __future__ import annotations

import asyncio
import json
import sys

sys.path.insert(0, "/home/student_platform/backend")

from sqlalchemy import select  # noqa: E402

from app.db import base as _all_models  # noqa: E402,F401
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402
from app.services.translation_service import _hash_source  # noqa: E402

LESSON_ID = 511

OLD_UZ = """// _placeholders.scss — barcha kartochkalar uchun umumiy asos
// %card-base HTML'da hech qachon klass sifatida chiqmaydi,
// faqat @extend qilingan selektorlar ro'yxatiga qo'shiladi.

%card-base {"""

NEW_UZ = """// %card-base HTML'da hech qachon klass sifatida chiqmaydi,
// faqat @extend qilingan selektorlar ro'yxatiga qo'shiladi.
// (Katta loyihada bunday placeholder'lar alohida _placeholders.scss
// faylida yozilib, @use orqali ulanadi — @use haqida keyingi darsda
// o'rganasiz. Hozircha soddalik uchun hammasi bitta faylda.)

%card-base {"""

OLD_UZ_2 = """// _cards.scss — konkret variantlar %placeholder'ni kengaytiradi
@use "placeholders" as *;

.product-card {"""

NEW_UZ_2 = """// Konkret variantlar %placeholder'ni kengaytiradi:

.product-card {"""

OLD_RU = """// _placeholders.scss — общая основа для всех карточек
// %card-base никогда не появится как класс в HTML,
// он только добавится в список селекторов, вызвавших @extend.

%card-base {"""

NEW_RU = """// %card-base никогда не появится как класс в HTML,
// он только добавится в список селекторов, вызвавших @extend.
// (В большом проекте такие placeholder'ы обычно выносят в отдельный файл
// _placeholders.scss и подключают через @use — про @use вы узнаете в
// следующем уроке. Здесь для простоты всё в одном файле.)

%card-base {"""

OLD_RU_2 = """// _cards.scss — конкретные варианты расширяют %placeholder
@use "placeholders" as *;

.product-card {"""

NEW_RU_2 = """// Конкретные варианты расширяют %placeholder:

.product-card {"""


def apply_replacements(text: str, pairs: list[tuple[str, str]]) -> str:
    for old, new in pairs:
        if old not in text:
            raise RuntimeError(f"expected substring not found:\n{old!r}")
        text = text.replace(old, new, 1)
    return text


async def main():
    async with AsyncSessionLocal() as db:
        lesson = (await db.execute(select(Lesson).where(Lesson.id == LESSON_ID))).scalar_one()
        sections = json.loads(lesson.sections_json)
        code_sec = next(s for s in sections if s.get("type") == "code")
        code_sec["code"] = apply_replacements(code_sec["code"], [(OLD_UZ, NEW_UZ), (OLD_UZ_2, NEW_UZ_2)])
        # The word "@use" legitimately still appears once, inside the new
        # explanatory comment ("@use haqida keyingi darsda o'rganasiz") —
        # only the actual DIRECTIVE (@use "...") must be gone.
        assert '@use "' not in code_sec["code"], "UZ code still contains an @use directive after fix"
        lesson.sections_json = json.dumps(sections, ensure_ascii=False)

        ru_row = (
            await db.execute(
                select(TranslationCache).where(
                    TranslationCache.entity_type == "lesson",
                    TranslationCache.entity_id == LESSON_ID,
                    TranslationCache.lang == "ru",
                    TranslationCache.field_name == "sections_json",
                )
            )
        ).scalar_one_or_none()
        if ru_row is not None:
            ru_sections = json.loads(ru_row.translated_text)
            ru_code_sec = next(s for s in ru_sections if s.get("type") == "code")
            ru_code_sec["code"] = apply_replacements(ru_code_sec["code"], [(OLD_RU, NEW_RU), (OLD_RU_2, NEW_RU_2)])
            assert '@use "' not in ru_code_sec["code"], "RU code still contains an @use directive after fix"
            ru_row.translated_text = json.dumps(ru_sections, ensure_ascii=False)
            ru_row.source_text_hash = _hash_source(lesson.sections_json)
            print("RU cache updated")
        else:
            print("no RU cache row found — nothing to update there")

        await db.commit()
        print("lesson 511 UZ source updated; committed")


if __name__ == "__main__":
    asyncio.run(main())
