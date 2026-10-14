"""Make the project brief of course 9, lesson id=7 ("4-dars Class id") consistent.

The description asked for "6 cards, each h2 + img + p + a" while the requirement list only had 5 loose
points, so students (and the AI grader) disagreed about what "done" means: a submission met four of the
five listed points yet was rejected for not having six full cards. One brief now says the same thing in
both places: 3 complete cards, and every listed point is checkable.

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
    "Mahsulotlar yoki xizmatlar uchun kamida 3 ta kartochka yarating. Har bir kartochka 4 ta tegdan iborat: "
    "h2 (sarlavha), img (rasm), p (matn) va a (havola). Div hali o'tilmagan, shuning uchun class'larni shu "
    "teglarning o'ziga bering. Umumiy .card class'ini kartochka teglarida qayta ishlating, sahifaning bosh "
    "sarlavhasiga #header, asosiy harakat havolasiga #cta unique id bering."
)
TASK_REQUIREMENTS = (
    "• Kamida 3 ta kartochka; har birida h2, img (alt bilan), p va a teglari bor\n"
    "• .card umumiy class'i kartochkalarning teglariga berilgan (jami kamida 6 ta elementda)\n"
    "• Har kartochkada .card-title (h2), .card-body (p), .card-footer (a) class'lari mos teglarga berilgan\n"
    "• 3 ta kartochka 3 xil rang varianti bilan (masalan .card-primary, .card-danger, .card-success)\n"
    "• #header unique id: sahifa bosh sarlavhasida (h1), sahifada faqat 1 marta\n"
    "• #cta unique id: asosiy harakat havolasida (a), sahifada faqat 1 marta"
)

TASK_DESCRIPTION_RU = (
    "Создайте минимум 3 карточки для товаров или услуг. Каждая карточка состоит из 4 тегов: h2 (заголовок), "
    "img (изображение), p (текст) и a (ссылка). Div ещё не изучался, поэтому давайте классы самим этим тегам. "
    "Переиспользуйте общий класс .card на тегах карточек, главному заголовку страницы задайте уникальный id "
    "#header, а основной ссылке-действию — #cta."
)
TASK_REQUIREMENTS_RU = (
    "• Минимум 3 карточки; в каждой есть теги h2, img (с alt), p и a\n"
    "• Общий класс .card задан тегам карточек (всего минимум на 6 элементах)\n"
    "• В каждой карточке классы .card-title (h2), .card-body (p), .card-footer (a) заданы подходящим тегам\n"
    "• 3 карточки с 3 разными цветовыми вариантами (например .card-primary, .card-danger, .card-success)\n"
    "• Уникальный id #header: у главного заголовка страницы (h1), на странице только 1 раз\n"
    "• Уникальный id #cta: у основной ссылки-действия (a), на странице только 1 раз"
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
