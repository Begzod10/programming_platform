"""Russian translation for the class-name glossary added by
enhance_course_61_tailwind_glossary.py. Must run AFTER the UZ script.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))  # noqa: E402

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402
from write_ru_translations import _write  # noqa: E402

MARKER_RU = "📖 Словарь классов"

SYSTEM_INTRO_RU = """<p>В Tailwind классы называются по определённым правилам:</p>
<ul>
  <li>Отступы/размеры (padding, margin, height, width): число × 0.25rem (например 4 = 1rem = 16px).</li>
  <li>Цвета: <code>название-цвета-оттенок</code>, оттенок от 50 (самый светлый) до 950 (самый тёмный).</li>
  <li><code>hover:</code>, <code>focus:</code>, <code>active:</code>, <code>disabled:</code> — префиксы, включаемые в зависимости от действия пользователя.</li>
  <li><code>sm:</code>, <code>md:</code>, <code>lg:</code>, <code>xl:</code> — как в Bootstrap, mobile-first: "начиная с этого размера экрана и крупнее".</li>
</ul>"""

GLOSSARY_RU = {
    525: [
        ("bg-gray-100", "Очень светло-серый фон (семейство gray, оттенок 100)."),
        ("font-semibold", "Шрифт средней жирности (чуть легче bold)."),
        ("hover:bg-blue-700", "При наведении курсора фон становится тёмно-синим (blue-700)."),
        ("justify-center", "Выравнивает flex/grid-элементы по центру вдоль основной оси."),
        ("mb-2 / mb-4", "Внешний отступ снизу, 0.5rem и 1rem соответственно."),
        ("min-h-screen", "Задаёт минимальную высоту в 100% высоты экрана."),
        ("px-4", "Внутренний отступ слева-справа, 1rem."),
        ("text-gray-600", "Серый цвет текста средней насыщенности."),
        ("transition-colors", "Плавно анимирует изменения цвета (фон, текст, граница)."),
    ],
    526: [
        ("bg-gradient-to-br", "Запускает градиентный фон, направленный из верхнего левого угла в нижний правый."),
        ("from-indigo-500 / to-purple-600", "Начальный и конечный цвет градиента."),
        ("bg-indigo-600, bg-slate-50/100/200", "Цвета фона по семейству (indigo, slate) + номеру оттенка."),
        ("text-indigo-600, text-slate-500/600/800", "Цвета текста по тому же принципу."),
        ("hover:text-indigo-600", "При наведении курсора цвет текста меняется на indigo-600."),
        ("lg:col-span-2", "С экрана lg занимает 2 колонки грида."),
        ("gap-3", "Отступ между элементами grid/flex, 0.75rem."),
        ("h-10 / h-32 / w-10", "Фиксированная высота/ширина (10 = 2.5rem, 32 = 8rem)."),
        ("mb-8 / mt-4 / mt-auto", "Внешние отступы (mt-auto — прижимает элемент вниз внутри flex)."),
        ("opacity-90", "Показывает элемент с прозрачностью 90% (лёгкая прозрачность)."),
        ("p-8 / px-3 / px-6 / py-1 / py-4", "Внутренние отступы, число × 0.25rem."),
        ("rounded-lg / rounded-2xl", "Степень скругления углов (2xl — радиус больше)."),
        ("shadow / shadow-sm", "Стандартная и лёгкая тень."),
        ("text-lg / text-xl", "Размеры текста крупнее стандартной шкалы."),
    ],
    527: [
        ("group-hover: / peer-*:", "group-hover — наведение на родительский элемент влияет на дочерний (у родителя должен быть класс `group`); peer-* — состояние соседнего элемента влияет на другой (у элемента перед ним должен быть класс `peer`)."),
        ("[...] (квадратные скобки)", "Произвольное значение вне стандартной шкалы, например h-[73px] или bg-[#4f46e5]."),
        ("active:bg-indigo-800 / active:scale-95", "В момент нажатия (active) меняется фон или размер."),
        ("bg-[#4f46e5]", "Произвольный цвет фона — точное HEX-значение."),
        ("border / border-slate-300", "Стандартная толщина и цвет границы."),
        ("dark:bg-slate-700/800, dark:border-slate-600, dark:text-slate-100/400", "Цвета фона/границы/текста, применяемые в тёмном режиме."),
        ("dark:group-hover:text-indigo-400", "В тёмном режиме, при наведении на родителя, меняется цвет текста (три префикса вместе)."),
        ("dark:hover:bg-slate-600", "Цвет фона при hover в тёмном режиме."),
        ("dark:shadow-slate-950", "Цвет тени в тёмном режиме."),
        ("disabled:cursor-not-allowed", "Если элемент отключён (disabled), курсор превращается в значок «запрещено»."),
        ("focus-visible:outline / outline-2 / outline-indigo-500", "Включение, толщина и цвет видимого контура при фокусе с клавиатуры."),
        ("focus:border-indigo-500", "Цвет границы поля при фокусе."),
        ("group-hover:text-indigo-600 / translate-x-1", "При наведении на родителя меняется цвет или позиция дочернего элемента."),
        ("h-[73px] / rounded-[14px]", "Произвольные значения в пикселях."),
        ("hover:bg-slate-300 / hover:shadow-lg", "Фон и тень при наведении."),
        ("inline-block", "Делает элемент inline-block."),
        ("invalid:border-rose-500", "Если поле заполнено неверно (invalid), граница становится розово-красной."),
        ("mt-1 / mt-2 / mt-8", "Внешние отступы сверху."),
        ("peer-placeholder-shown:hidden", "Если у «соседнего» поля ещё виден placeholder (оно пустое), этот элемент скрывается."),
        ("rounded", "Стандартное скругление углов."),
        ("sm:w-auto", "С экрана sm ширина становится автоматической (по содержимому)."),
        ("space-y-4", "Добавляет вертикальный отступ между дочерними элементами."),
        ("text-rose-600 / text-slate-900", "Цвета текста по семейству цветов."),
        ("transition-transform", "Плавно анимирует изменения transform (scale, translate)."),
    ],
    529: [
        ("цвет/число (например bg-white/70)", "Число после \"/\" после названия цвета — процент прозрачности (bg-white/70 — белый фон с прозрачностью 70%)."),
        ("отрицательное значение (например -top-3, -translate-x-1/2)", "Сдвигает элемент в сторону, противоположную указанной — обычно для центрирования или «нависания» за край."),
        ("-top-3", "Сдвигает элемент вверх на 0.75rem — чтобы «повесить» бейдж/метку за край."),
        ("-translate-x-1/2 + left-1/2", "Классический способ центрирования: сдвигает элемент на 50% слева, затем возвращает назад на половину его собственной ширины."),
        ("backdrop-blur-md", "Размывает фон ЗА элементом (эффект стекла)."),
        ("bg-emerald-100 / bg-indigo-100 / bg-pink-100", "Светлые цвета фона (оттенок 100)."),
        ("border-2", "Толщина границы 2px."),
        ("border-b / border-t", "Только нижняя или только верхняя граница."),
        ("border-indigo-500 / border-slate-200", "Цвета границы."),
        ("dark:bg-emerald-900/50 и подобные", "В тёмном режиме — тёмные цвета фона с прозрачностью 50%."),
        ("dark:from-indigo-900/40, dark:to-pink-900/30", "Цвета градиента в тёмном режиме (с прозрачностью)."),
        ("font-extrabold / font-medium / font-normal", "Степени жирности шрифта."),
        ("gap-4", "Отступ между элементами grid/flex, 1rem."),
        ("h-6 / h-12 / w-6 / w-12", "Фиксированные размеры."),
        ("hover:shadow-xl", "Более крупная тень при наведении."),
        ("inset-0", "Прижимает элемент ко всем сторонам родителя (сверху-снизу-слева-справа — везде 0)."),
        ("max-w-2xl / max-w-5xl / max-w-7xl", "Ограничения максимальной ширины (2xl — самое маленькое, 7xl — самое большое)."),
        ("mb-1 / mb-3 / mb-6 / mb-10 / mb-16", "Отступы снизу, чем больше число — тем больше отступ."),
        ("md:grid-cols-3 / md:grid-cols-4", "С экрана md грид становится в 3 или 4 колонки."),
        ("md:py-32 / md:scale-105 / md:text-4xl/6xl/xl", "Отступ, увеличение и размер текста, применяемые с экрана md."),
        ("mx-auto / my-6", "Горизонтальное центрирование (авто-отступы слева-справа) и вертикальный внешний отступ."),
        ("overflow-hidden", "Скрывает содержимое, выходящее за пределы контейнера."),
        ("px-8 / py-3 / py-12", "Внутренние отступы."),
        ("rounded-full", "Полностью круглые/овальные углы."),
        ("scroll-smooth", "Включает плавную анимацию прокрутки внутри страницы."),
        ("shadow-2xl", "Максимальная степень тени."),
        ("shadow-indigo-500/20", "Тень цвета indigo с прозрачностью 20%."),
        ("sm:flex-row", "С экрана sm flex-элементы располагаются в строку."),
        ("space-y-2 / space-y-3", "Вертикальный отступ между дочерними элементами."),
        ("text-3xl / text-4xl / text-base / text-xs", "Размеры текста."),
        ("text-center", "Выравнивает текст по центру."),
        ("text-emerald-600 / text-indigo-700 / text-pink-600", "Цвета текста по семействам цветов."),
        ("to-pink-500/20", "Конечный цвет градиента с прозрачностью 20%."),
        ("tracking-tight", "Уменьшает расстояние между буквами (letter-spacing)."),
        ("via-purple-500/10", "Средний цвет трёхцветного градиента с прозрачностью 10%."),
    ],
}


def build_html_ru(lesson_id: int, entries: list[tuple[str, str]]) -> str:
    items = "\n".join(
        f"  <li><code>{cls}</code> — {desc}</li>" for cls, desc in entries
    )
    intro = SYSTEM_INTRO_RU + "\n" if lesson_id == 525 else ""
    return (
        f"<h3>{MARKER_RU}</h3>\n"
        f"{intro}"
        f"<p>Классы, использованные в примере выше, но ещё не объяснённые отдельно:</p>\n"
        f"<ul>\n{items}\n</ul>"
    )


async def main() -> None:
    async with AsyncSessionLocal() as db:
        for lesson_id, entries in GLOSSARY_RU.items():
            lesson = (await db.execute(select(Lesson).where(Lesson.id == lesson_id))).scalar_one()

            old_ru_text = (await db.execute(select(TranslationCache).where(
                TranslationCache.entity_type == "lesson", TranslationCache.entity_id == lesson_id,
                TranslationCache.lang == "ru", TranslationCache.field_name == "text_content",
            ))).scalar_one().translated_text
            old_ru_sections = (await db.execute(select(TranslationCache).where(
                TranslationCache.entity_type == "lesson", TranslationCache.entity_id == lesson_id,
                TranslationCache.lang == "ru", TranslationCache.field_name == "sections_json",
            ))).scalar_one().translated_text

            glossary_html_ru = build_html_ru(lesson_id, entries)

            if MARKER_RU in old_ru_text:
                print(f"lesson {lesson_id}: RU glossary already present, skipping")
                continue

            new_ru_text = old_ru_text + "\n\n" + glossary_html_ru
            await _write(db, "lesson", lesson_id, "text_content", lesson.text_content, new_ru_text)

            ru_tree = json.loads(old_ru_sections)
            uz_tree = json.loads(lesson.sections_json)
            uz_text_sections = [s for s in uz_tree if s["type"] == "text"]
            ru_text_sections = [s for s in ru_tree if s["type"] == "text"]
            assert len(uz_text_sections) == len(ru_text_sections), \
                f"lesson {lesson_id}: UZ/RU text section count mismatch"
            ru_text_sections[-1]["html"] = (ru_text_sections[-1].get("html") or "") + "\n\n" + glossary_html_ru

            new_ru_sections_json = json.dumps(ru_tree, ensure_ascii=False)
            await _write(db, "lesson", lesson_id, "sections_json", lesson.sections_json, new_ru_sections_json)

            print(f"lesson {lesson_id}: RU glossary written ({len(entries)} entries)")

        await db.commit()
        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
