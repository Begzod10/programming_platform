"""One-off fix: lesson 515 ("Bootstrap Komponentlar", course 56) required
Pagination in its mini-project (task_requirements: "Pagination mavjud") but
never taught it anywhere in the lesson content -- the intro line enumerated
Navbar/Buttons/Cards/Alerts/Badges/List group/Spinners and stopped there.

Adds:
  1. "Pagination" to the intro's component list (sections_json only --
     text_content is an older, superseded draft the frontend never renders
     once sections_json is present)
  2. A Pagination theory subsection (classes: pagination, page-item,
     page-item active, page-item disabled, justify-content-center)
  3. A working pagination block in the code example, matching what the
     mini-project's "Pastda pagination qo'shing" line asks for
  4. A new multiple_choice exercise on the pagination state classes

Writes matching RU translations for every new/changed string, since this
lesson already has a full RU translation cached -- see
write_ru_translations.py's module docstring for why skipping this is a bug,
not a later TODO. Verify after running with:
    python scripts/check_ru_coverage.py 56
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from scripts.enhance_lesson_helpers import add_exercise, sync_exercise_section  # noqa: E402
from scripts.write_ru_translations import translate_exercises  # noqa: E402

LESSON_ID = 515

# ── UZ: intro sentence edit ──────────────────────────────────────────────
UZ_INTRO_OLD = "<strong>List group</strong> va <strong>Spinners</strong>."
UZ_INTRO_NEW = "<strong>List group</strong>, <strong>Spinners</strong> va <strong>Pagination</strong>."

RU_INTRO_OLD = "<strong>List group</strong> и <strong>Spinners</strong>."
RU_INTRO_NEW = "<strong>List group</strong>, <strong>Spinners</strong> и <strong>Pagination</strong>."

# ── UZ/RU: new theory subsection, inserted right before the mermaid diagram ──
MERMAID_MARKER = '<pre class="mermaid">'

UZ_PAGINATION_THEORY = (
    "<h3>Pagination (sahifalash)</h3>"
    "<p><code>pagination</code> — ko'p sahifali ro'yxatlarni (masalan qidiruv "
    "natijalari yoki mahsulotlar) sahifalarga bo'lib ko'rsatish uchun "
    "navigatsiya komponenti. Tuzilishi: tashqi <code>&lt;ul class=\"pagination\"&gt;</code>, "
    "ichida har bir sahifa uchun <code>&lt;li class=\"page-item\"&gt;&lt;a class=\"page-link\"&gt;"
    "...&lt;/a&gt;&lt;/li&gt;</code>.</p>"
    "<ul>"
    "<li><code>page-item active</code> — foydalanuvchi hozir turgan sahifani belgilaydi</li>"
    "<li><code>page-item disabled</code> — bosib bo'lmaydigan band (masalan birinchi "
    "sahifada \"Oldingi\" tugmasi)</li>"
    "<li><code>justify-content-center</code> — pagination'ni gorizontal markazga tekislaydi</li>"
    "</ul>"
)

RU_PAGINATION_THEORY = (
    "<h3>Pagination (постраничная навигация)</h3>"
    "<p><code>pagination</code> — компонент навигации для разбиения длинных списков "
    "(например результатов поиска или товаров) на страницы. Структура: внешний "
    "<code>&lt;ul class=\"pagination\"&gt;</code>, внутри — <code>&lt;li class=\"page-item\"&gt;"
    "&lt;a class=\"page-link\"&gt;...&lt;/a&gt;&lt;/li&gt;</code> для каждой страницы.</p>"
    "<ul>"
    "<li><code>page-item active</code> — отмечает страницу, на которой сейчас находится "
    "пользователь</li>"
    "<li><code>page-item disabled</code> — недоступный пункт (например кнопка \"Назад\" "
    "на первой странице)</li>"
    "<li><code>justify-content-center</code> — выравнивает pagination по центру по "
    "горизонтали</li>"
    "</ul>"
)

# ── UZ/RU: pagination block in the live code example, inserted right after
# the cards row's closing </div>, before the .container's closing </div> ──
UZ_ROW_END_MARKER = (
    '          <p class="mt-2">Ma\'lumot yuklanmoqda</p>\n'
    "        </div>\n"
    "      </div>\n"
    "    </div>\n"
    "  </div>\n"
    "</div>\n"
)
UZ_ROW_END_WITH_PAGINATION = (
    '          <p class="mt-2">Ma\'lumot yuklanmoqda</p>\n'
    "        </div>\n"
    "      </div>\n"
    "    </div>\n"
    "  </div>\n\n"
    '  <!-- Pagination: joriy sahifa "active" bilan belgilangan -->\n'
    '  <nav aria-label="Mahsulotlar sahifalari" class="mt-4">\n'
    '    <ul class="pagination justify-content-center">\n'
    '      <li class="page-item disabled"><a class="page-link" href="#">Oldingi</a></li>\n'
    '      <li class="page-item active"><a class="page-link" href="#">1</a></li>\n'
    '      <li class="page-item"><a class="page-link" href="#">2</a></li>\n'
    '      <li class="page-item"><a class="page-link" href="#">Keyingi</a></li>\n'
    "    </ul>\n"
    "  </nav>\n"
    "</div>\n"
)

RU_ROW_END_MARKER = (
    '          <p class="mt-2">Данные загружаются</p>\n'
    "        </div>\n"
    "      </div>\n"
    "    </div>\n"
    "  </div>\n"
    "</div>\n"
)
RU_ROW_END_WITH_PAGINATION = (
    '          <p class="mt-2">Данные загружаются</p>\n'
    "        </div>\n"
    "      </div>\n"
    "    </div>\n"
    "  </div>\n\n"
    '  <!-- Pagination: текущая страница отмечена классом "active" -->\n'
    '  <nav aria-label="Страницы товаров" class="mt-4">\n'
    '    <ul class="pagination justify-content-center">\n'
    '      <li class="page-item disabled"><a class="page-link" href="#">Назад</a></li>\n'
    '      <li class="page-item active"><a class="page-link" href="#">1</a></li>\n'
    '      <li class="page-item"><a class="page-link" href="#">2</a></li>\n'
    '      <li class="page-item"><a class="page-link" href="#">Вперёд</a></li>\n'
    "    </ul>\n"
    "  </nav>\n"
    "</div>\n"
)

EX_TITLE = "Pagination holat klasslari"
EX_DESCRIPTION = (
    "Sahifalash (pagination) ro'yxatida joriy sahifani va bosib bo'lmaydigan "
    "bandni (masalan, birinchi sahifadagi \"Oldingi\" tugmasi) belgilash uchun "
    "qaysi klasslar kerak?"
)
EX_OPTIONS = [
    "page-item active + page-item disabled",
    "page-active + page-disabled",
    "pagination-active + pagination-disabled",
    "page-item-active + page-item-inactive",
]
EX_CORRECT = EX_OPTIONS[0]
EX_HINT = "Har ikkalasi ham asosiy <li> klassi page-item ustiga qo'shiladigan modifikator."
EX_EXPLANATION = (
    "page-item active joriy sahifani, page-item disabled esa bosib bo'lmaydigan "
    "bandni (masalan birinchi sahifada \"Oldingi\") belgilaydi. Ikkalasi ham "
    "page-item bazaviy klassiga qo'shiladigan modifikator."
)

EX_TITLE_RU = "Классы состояния Pagination"
EX_DESCRIPTION_RU = (
    "Какие классы нужны, чтобы отметить текущую страницу и недоступный пункт "
    "(например кнопку \"Назад\" на первой странице) в списке pagination?"
)
EX_OPTIONS_RU = [
    "page-item active + page-item disabled",
    "page-active + page-disabled",
    "pagination-active + pagination-disabled",
    "page-item-active + page-item-inactive",
]
EX_HINT_RU = "Оба варианта — это модификаторы поверх базового класса <li> page-item."
EX_EXPLANATION_RU = (
    "page-item active отмечает текущую страницу, page-item disabled — недоступный "
    "пункт (например \"Назад\" на первой странице). Оба — модификаторы базового "
    "класса page-item."
)


def _apply_theory_and_code(html: str, code: str, intro_old, intro_new,
                            theory_addition, row_end_old, row_end_new) -> tuple[str, str]:
    assert intro_old in html, "intro sentence not found -- lesson content changed since this script was written"
    html = html.replace(intro_old, intro_new, 1)
    assert MERMAID_MARKER in html, "mermaid marker not found -- lesson content changed"
    html = html.replace(MERMAID_MARKER, theory_addition + MERMAID_MARKER, 1)

    assert row_end_old in code, "code example row-end marker not found -- code changed since this script was written"
    code = code.replace(row_end_old, row_end_new, 1)
    return html, code


async def main() -> None:
    async with AsyncSessionLocal() as db:
        lesson = (await db.execute(select(Lesson).where(Lesson.id == LESSON_ID))).scalar_one()

        # text_content is untouched deliberately: it's an older, structurally
        # different draft of this lesson (apiToLesson() in the frontend
        # prefers sections_json whenever it's present, so text_content never
        # renders here) -- editing it would be dead work on unused content.
        tree = json.loads(lesson.sections_json)
        theory_section = next(s for s in tree if s["type"] == "text" and s["order"] == 1)
        code_section = next(s for s in tree if s["type"] == "code")

        theory_section["html"], code_section["code"] = _apply_theory_and_code(
            theory_section["html"], code_section["code"],
            UZ_INTRO_OLD, UZ_INTRO_NEW, UZ_PAGINATION_THEORY,
            UZ_ROW_END_MARKER, UZ_ROW_END_WITH_PAGINATION,
        )
        lesson.sections_json = json.dumps(tree, ensure_ascii=False)

        ex = await add_exercise(
            db, LESSON_ID,
            title=EX_TITLE, description=EX_DESCRIPTION,
            exercise_type="multiple_choice",
            options=json.dumps(EX_OPTIONS, ensure_ascii=False),
            correct_answers=EX_CORRECT,
            hint=EX_HINT, explanation=EX_EXPLANATION,
            difficulty_level="Medium", points=3,
        )
        await sync_exercise_section(db, LESSON_ID)
        ex_id, ex_order = ex.id, ex.order

        # Rebuild the RU sections_json tree the same way, from the RU cache.
        # Same session/transaction as the UZ writes above so ex_id/ex_order
        # never need to survive past a session boundary.
        from app.models.translation_cache import TranslationCache
        ru_row = (await db.execute(select(TranslationCache).where(
            TranslationCache.entity_type == "lesson",
            TranslationCache.entity_id == LESSON_ID,
            TranslationCache.lang == "ru",
            TranslationCache.field_name == "sections_json",
        ))).scalar_one()
        ru_tree = json.loads(ru_row.translated_text)
        ru_theory = next(s for s in ru_tree if s["type"] == "text" and s["order"] == 1)
        ru_code = next(s for s in ru_tree if s["type"] == "code")
        ru_theory["html"], ru_code["code"] = _apply_theory_and_code(
            ru_theory["html"], ru_code["code"],
            RU_INTRO_OLD, RU_INTRO_NEW, RU_PAGINATION_THEORY,
            RU_ROW_END_MARKER, RU_ROW_END_WITH_PAGINATION,
        )
        # The exercise section in the RU tree must also carry the new
        # exercise, embedded the same way sync_exercise_section() does.
        ru_exercise_section = next(s for s in ru_tree if s["type"] == "exercise")
        ru_exercise_section["exercises"].append({
            "_localId": ex_id, "id": ex_id, "title": EX_TITLE_RU,
            "description": EX_DESCRIPTION_RU, "exercise_type": "multiple_choice",
            "options": json.dumps(EX_OPTIONS_RU, ensure_ascii=False),
            "correct_answers": EX_CORRECT, "drag_items": "", "correct_order": "",
            "is_multiple_select": False, "expected_answer": "",
            "hint": EX_HINT_RU, "explanation": EX_EXPLANATION_RU,
            "difficulty_level": "Medium", "points": 3, "order": ex_order,
        })
        ru_row.translated_text = json.dumps(ru_tree, ensure_ascii=False)

        await translate_exercises(db, {
            ex_id: {
                "title": EX_TITLE_RU,
                "description": EX_DESCRIPTION_RU,
                "options": json.dumps(EX_OPTIONS_RU, ensure_ascii=False),
                "hint": EX_HINT_RU,
            },
        })

        await db.commit()
        print(f"UZ + RU content and exercise {ex_id} written for lesson {LESSON_ID}")


if __name__ == "__main__":
    asyncio.run(main())
