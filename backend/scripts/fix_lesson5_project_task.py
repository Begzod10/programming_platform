"""Fill in the missing project-submission brief for course 9, lesson id=5
("2-dars Teglar bilan ishlash"). The frontend (StudentCourses.js) already
synthesizes a project section whenever task_title is set, but
task_description/task_requirements/task_technologies were all empty, so
students saw an empty submission panel. Writes UZ (source) + RU translation.
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

LESSON_ID = 5

TASK_TITLE = "Loyiha: Mening birinchi HTML sahifam"
TASK_DESCRIPTION = (
    "Ushbu darsda o'rgangan teglaringizni ishlatib, oddiy shaxsiy sahifa "
    "yarating. Sahifada o'zingiz haqingizda qisqacha ma'lumot, bitta rasm "
    "va foydali havola bo'lishi kerak."
)
TASK_REQUIREMENTS = (
    "• <title> — brauzer tabida ko'rinadigan sarlavha\n"
    "• Kamida bitta <h1> va bitta <h2> yoki <h3> sarlavha\n"
    "• Kamida 2 ta <p> paragraf\n"
    "• <a href=\"...\">...</a> — kamida bitta tashqi havola\n"
    "• <img src=\"...\" alt=\"...\"> — kamida bitta rasm (alt matni bilan)\n"
    "• <ul> yoki <ol> — kamida 3 ta <li> elementli ro'yxat\n"
    "• To'g'ri HTML tuzilishi: <!DOCTYPE html>, <html>, <head>, <body>"
)
TASK_TECHNOLOGIES = "HTML5"

TASK_TITLE_RU = "Проект: Моя первая HTML-страница"
TASK_DESCRIPTION_RU = (
    "Используя теги, изученные на этом уроке, создайте простую личную "
    "страницу. На странице должна быть краткая информация о себе, одно "
    "изображение и полезная ссылка."
)
TASK_REQUIREMENTS_RU = (
    "• <title> — заголовок, видимый во вкладке браузера\n"
    "• Минимум один <h1> и один <h2> или <h3>\n"
    "• Минимум 2 параграфа <p>\n"
    "• <a href=\"...\">...</a> — минимум одна внешняя ссылка\n"
    "• <img src=\"...\" alt=\"...\"> — минимум одно изображение (с атрибутом alt)\n"
    "• <ul> или <ol> — список минимум с 3 элементами <li>\n"
    "• Правильная структура HTML: <!DOCTYPE html>, <html>, <head>, <body>"
)
TASK_TECHNOLOGIES_RU = "HTML5"


async def main():
    async with AsyncSessionLocal() as db:
        lesson = (await db.execute(select(Lesson).where(Lesson.id == LESSON_ID))).scalar_one()

        lesson.task_title = TASK_TITLE
        lesson.task_description = TASK_DESCRIPTION
        lesson.task_requirements = TASK_REQUIREMENTS
        lesson.task_technologies = TASK_TECHNOLOGIES
        await db.flush()

        await _write(db, "lesson", LESSON_ID, "task_title", TASK_TITLE, TASK_TITLE_RU)
        await _write(db, "lesson", LESSON_ID, "task_description", TASK_DESCRIPTION, TASK_DESCRIPTION_RU)
        await _write(db, "lesson", LESSON_ID, "task_requirements", TASK_REQUIREMENTS, TASK_REQUIREMENTS_RU)
        await _write(db, "lesson", LESSON_ID, "task_technologies", TASK_TECHNOLOGIES, TASK_TECHNOLOGIES_RU)

        await db.commit()
        print(f"Lesson {LESSON_ID}: task_title/description/requirements/technologies "
              f"written (uz updated in place, ru cached).")


if __name__ == "__main__":
    asyncio.run(main())
