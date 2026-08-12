"""Russian translation for the class-name glossary added by
enhance_course_56_bootstrap_glossary.py.

Must run AFTER the UZ script (reads the now-current lesson.text_content /
sections_json as the translation source, mirroring ru_enhance_course_56_
bootstrap.py's pattern).
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

GLOSSARY_RU = {
    514: [
        ("align-items-center", "Выравнивает элементы flex-контейнера по центру по вертикали."),
        ("bg-light", "Задаёт светло-серый фон."),
        ("bg-white", "Задаёт белый фон."),
        ("col-lg-9", "На экранах ≥992px (lg) занимает 9 из 12 колонок."),
        ("col-md-10", "На экранах ≥768px (md) занимает 10 из 12 колонок."),
        ("col-md-3", "На md занимает 3 из 12 колонок."),
        ("col-md-9", "На md занимает 9 из 12 колонок."),
        ("col-sm-6", "На sm (≥576px) занимает 6 из 12 колонок."),
        ("fs-5", "Задаёт размер шрифта уровня 5 (шкала от 1 до 6, чем больше число — тем мельче текст)."),
        ("fw-bold", "Делает текст жирным."),
        ("list-unstyled", "Убирает маркеры и отступы у списка <ul>/<ol>."),
        ("mb-4", "Внешний отступ снизу (margin-bottom), уровень 4 (шкала 0-5)."),
        ("mt-3", "Внешний отступ сверху, уровень 3."),
        ("offset-md-1", "На md сдвигает колонку вправо на 1 колонку свободного места слева."),
        ("py-3", "Внутренний отступ сверху и снизу (padding), уровень 3."),
        ("shadow-sm", "Добавляет лёгкую тень."),
        ("text-end", "Выравнивает текст по правому краю."),
    ],
    515: [
        ("active", "Класс состояния \"активный\" (например, текущий пункт меню)."),
        ("alert-success", "Зелёное уведомление \"успех\"."),
        ("bg-danger", "Красный фон (для ошибок/опасности)."),
        ("bg-success", "Зелёный фон (для успеха)."),
        ("bg-warning", "Жёлтый фон (для предупреждений)."),
        ("btn-outline-secondary", "Кнопка без заливки, с серой обводкой."),
        ("d-flex", "Делает элемент flex-контейнером (display: flex)."),
        ("fade", "Включает CSS-переход (transition), обычно работает вместе с .show."),
        ("justify-content-between", "Равномерно распределяет flex-элементы, крайние — по краям."),
        ("list-group-flush", "Убирает внешние границы и скругления у списка (для вставки в карточку)."),
        ("ms-auto", "Автоматический отступ слева — сдвигает элемент вправо во flex-контейнере."),
        ("mt-2", "Отступ сверху, уровень 2."),
        ("my-4", "Отступ сверху и снизу, уровень 4."),
        ("nav-item", "Контейнер одного пункта навигации."),
        ("nav-link", "Кликабельная ссылка внутри навигации."),
        ("navbar-brand", "Класс для логотипа/названия сайта в navbar."),
        ("navbar-nav", "Контейнер списка навигации внутри navbar."),
        ("navbar-toggler-icon", "Иконка внутри мобильной кнопки-гамбургера."),
        ("show", "Переводит элемент в видимое состояние (вместе с collapse/modal/fade)."),
        ("text-center", "Выравнивает текст по центру."),
        ("text-dark", "Делает цвет текста тёмным."),
        ("text-primary", "Красит текст в основной цвет темы (синий)."),
    ],
    516: [
        ("btn-secondary", "Серая кнопка второстепенного действия."),
        ("form-check-label", "Подпись рядом с checkbox/radio."),
        ("form-label", "Подпись над полем ввода."),
        ("has-validation", "Служебный класс, нужный, чтобы сообщение валидации правильно располагалось внутри input-group."),
        ("mb-3", "Отступ снизу, уровень 3."),
        ("modal-title", "Класс заголовка модального окна."),
    ],
    517: [
        ("align-items-start", "Выравнивает flex-элементы по верхнему краю."),
        ("border-bottom", "Добавляет нижнюю границу."),
        ("btn-dark", "Чёрная кнопка."),
        ("btn-lg", "Увеличивает размер кнопки."),
        ("btn-outline-primary", "Кнопка без заливки с основным цветом обводки."),
        ("flex-grow-1", "Позволяет flex-элементу расти и занимать свободное место."),
        ("flex-md-row", "С md-экрана и шире располагает flex-элементы в строку."),
        ("fs-2 / fs-3 / fs-4", "Разные уровни размера шрифта (чем меньше число, тем крупнее текст)."),
        ("fs-md-1", "С md-экрана применяется самый крупный уровень размера шрифта."),
        ("m-0", "Убирает внешние отступы со всех сторон."),
        ("mb-2", "Отступ снизу, уровень 2."),
        ("mt-5", "Отступ сверху, максимальный уровень 5."),
        ("px-5", "Внутренний отступ слева-справа, уровень 5."),
        ("py-5", "Внутренний отступ сверху-снизу, уровень 5."),
        ("py-md-6", "С md-экрана — внутренний отступ сверху-снизу, уровень 6 (расширенная шкала)."),
        ("small", "Уменьшает размер текста (аналог тега <small>)."),
        ("text-white", "Делает цвет текста белым."),
    ],
    518: [
        ("align-middle", "Выравнивает содержимое ячейки таблицы по центру по вертикали."),
        ("bi-speedometer2", "Класс иконки \"спидометр\" из библиотеки Bootstrap Icons."),
        ("border-0", "Убирает все границы."),
        ("btn-close-white", "Делает кнопку закрытия (×) белой — для тёмного фона."),
        ("col-lg-10 / col-lg-2", "На lg занимают 10 и 2 колонки соответственно."),
        ("h5", "Применяет стиль заголовка <h5> к любому тегу."),
        ("m-auto", "Автоматический отступ со всех сторон — центрирует элемент."),
        ("mb-0", "Убирает отступ снизу."),
        ("me-2", "Отступ справа, уровень 2."),
        ("min-vh-100", "Задаёт минимальную высоту в 100% высоты экрана."),
        ("navbar-light", "Светлая цветовая схема navbar (тёмный текст для светлого фона)."),
        ("p-0", "Убирает внутренние отступы со всех сторон."),
        ("toast", "Контейнер короткого всплывающего уведомления (\"toast\")."),
        ("toast-body", "Основная текстовая часть внутри toast-уведомления."),
    ],
}


def build_html_ru(entries: list[tuple[str, str]]) -> str:
    items = "\n".join(
        f"  <li><code>{cls}</code> — {desc}</li>" for cls, desc in entries
    )
    return (
        f"<h3>{MARKER_RU}</h3>\n"
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

            glossary_html_ru = build_html_ru(entries)

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

            print(f"lesson {lesson_id}: RU glossary written ({len(entries)} classes)")

        await db.commit()
        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
