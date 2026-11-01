"""Make the project brief of course 9, lesson id=7 ("4-dars Class id") match what the lesson teaches.

The lesson teaches ONE thing: a class (".", many elements) versus an id ("#", exactly one element); the tags
(h1-h6, p, a, img) and CSS properties (color, font, width, border) come from lessons 2-3. The old brief also asked
for things nobody had met: a shared ".card" class with no tag to put it on (div is taught later), two classes on
one element ("card-title card-primary") and "colour variants". A student with a nearly complete page failed ~10 times,
each time for something different. The brief now asks only for: cards made of the known tags, ONE class reused on
all the headings and on all the paragraphs, and two ids (#header, #cta) used once. No div, nothing untaught, and
no wording a model can read as a rule ("exactly one class", "div is forbidden", example names are free).

    python scripts/fix_lesson7_class_id_task.py           # dry-run: prints the diff
    python scripts/fix_lesson7_class_id_task.py --apply   # writes UZ (in place) + RU (translation_cache)
"""
from __future__ import annotations
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from write_ru_translations import _write  # noqa: E402

LESSON_ID = 7

TASK_DESCRIPTION = (
    "Mahsulotlar yoki xizmatlar uchun kamida 3 ta kartochka yarating. Har bir kartochkada h2 (sarlavha), img (rasm), "
    "p (matn) va a (havola) teglari bo'lsin. Bu darsning maqsadi: bir xil ko'rinishdagi elementlarga bir xil CLASS "
    "berish (u ko'p elementga beriladi) va sahifada faqat bittadan bo'ladigan elementlarga ID berish (u faqat bitta "
    "elementga beriladi)."
)
TASK_REQUIREMENTS = (
    "• Kamida 3 ta kartochka (ko'p bo'lsa ham bo'ladi); har birida h2, img (alt bilan), p va a teglari bor (tartibi ixtiyoriy)\n"
    "• CLASS: hamma h2 larda bir xil class nomi bor (nomini o'zingiz tanlaysiz; boshqa class qo'shilsa ham bo'ladi) va "
    "CSS'da shu class uchun stil yozilgan (rang yoki shrift)\n"
    "• CLASS: hamma p larda ham bir xil class nomi bor (nomini o'zingiz tanlaysiz) va CSS'da shu class uchun stil yozilgan "
    "(rang, fon yoki chegara)\n"
    "• ID: bosh sarlavha h1 da id=\"header\" bor, CSS'da #header uchun stil yozilgan, sahifada id=\"header\" faqat 1 marta\n"
    "• ID: kartochkalardan tashqaridagi bitta alohida havola a da id=\"cta\" bor, CSS'da #cta uchun stil yozilgan, "
    "sahifada id=\"cta\" faqat 1 marta"
)

TASK_DESCRIPTION_RU = (
    "Создайте минимум 3 карточки для товаров или услуг. В каждой карточке есть теги h2 (заголовок), img (изображение), "
    "p (текст) и a (ссылка). Цель урока: задать один и тот же CLASS одинаково выглядящим элементам (он даётся многим "
    "элементам) и ID элементам, которые на странице только в одном экземпляре (он даётся только одному элементу)."
)
TASK_REQUIREMENTS_RU = (
    "• Минимум 3 карточки (больше — тоже можно); в каждой есть теги h2, img (с alt), p и a (порядок любой)\n"
    "• CLASS: у всех h2 одинаковое название класса (название выбираете сами; другие классы можно добавлять) и для этого "
    "класса в CSS есть стиль (цвет или шрифт)\n"
    "• CLASS: у всех p тоже одинаковое название класса (название выбираете сами) и для этого класса в CSS есть стиль "
    "(цвет, фон или рамка)\n"
    "• ID: у главного заголовка h1 есть id=\"header\", в CSS есть стиль для #header, на странице id=\"header\" только 1 раз\n"
    "• ID: у одной отдельной ссылки a вне карточек есть id=\"cta\", в CSS есть стиль для #cta, на странице id=\"cta\" "
    "только 1 раз"
)


async def main(apply: bool):
    async with AsyncSessionLocal() as db:
        lesson = (await db.execute(select(Lesson).where(Lesson.id == LESSON_ID))).scalar_one()
        print("lesson:", lesson.title)
        for name, old, new in (("task_description", lesson.task_description, TASK_DESCRIPTION),
                               ("task_requirements", lesson.task_requirements, TASK_REQUIREMENTS)):
            print(f"\n--- {name} (hozir)\n{old}\n--- {name} (yangi)\n{new}")
        if not apply:
            print("\nDRY-RUN: hech narsa yozilmadi.")
            return
        lesson.task_description = TASK_DESCRIPTION
        lesson.task_requirements = TASK_REQUIREMENTS
        await db.flush()
        await _write(db, "lesson", LESSON_ID, "task_description", TASK_DESCRIPTION, TASK_DESCRIPTION_RU)
        await _write(db, "lesson", LESSON_ID, "task_requirements", TASK_REQUIREMENTS, TASK_REQUIREMENTS_RU)
        await db.commit()
        print("\nyozildi (UZ joyida, RU translation_cache'ga). Servisni qayta ishga tushiring.")


if __name__ == "__main__":
    asyncio.run(main("--apply" in sys.argv))
