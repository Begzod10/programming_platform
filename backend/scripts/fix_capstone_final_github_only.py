"""Change the capstone-finale submission requirement: GitHub URL only.

Previously every capstone's final ("CAPSTONE yakuni") lesson task_requirements
included a "Submission'da live_demo_url to'ldirilgan" bullet. live_demo_url
was already 100% optional everywhere in the actual submission/grading code
(frontend never required it, backend never sent it to the AI grader) — so
that bullet was an unenforceable claim. This script drops it and replaces it
with an explicit "GitHub URL only" bullet, for all 4 capstone finales:

    lesson 742 (course 86, Capstone 1 "TaskFlow")
    lesson 756 (course 88, Capstone 2 "StudyMate")
    lesson 770 (course 90, Capstone 3 "MoneyLog")
    lesson 784 (course 92, Capstone 4 "IssueForge")

Updates: Lesson.task_requirements (source of truth), the embedded project
section's "requirements" field inside Lesson.sections_json (kept in sync —
this is what the lesson page actually renders), and the RU translation_cache
row for task_requirements (requirements/techStack are NOT in
_TRANSLATABLE_KEYS inside sections_json, so no sections_json translation
cache update is needed — see translation_service.py).

Usage:
    cd backend
    python -m scripts.fix_capstone_final_github_only
    # add --dry-run to preview without writing
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from write_ru_translations import _write as write_ru  # noqa: E402


UPDATES = {
    742: {
        "requirements_uz": (
            "• Backend haqiqiy hostingda ishlab turibdi (github_url'dagi repo bilan bog'liq)\n"
            "• Frontend haqiqiy hostingda ishlab turibdi, deploy qilingan\n"
            "• CORS origin production frontend domeniga to'g'ri sozlangan (localhost qattiq yozilmagan)\n"
            "• Frontend'dagi API manzili production backend domeniga sozlangan\n"
            "• Ro'yxatdan o'tish, kirish, task qo'shish/o'chirish, qidiruv — barchasi jonli saytda ishlaydi\n"
            "• README.md: jonli havolalar (frontend + backend), texnologiyalar, 6/6 bosqich yakunlangan checklist\n"
            "• Submission uchun FAQAT GitHub repository URL talab qilinadi — AI baholash butun repo kodini "
            "(backend + frontend) tekshiradi, alohida live_demo_url maydoni endi shart emas"
        ),
        "requirements_ru": (
            "• Backend работает на реальном хостинге (связан с репозиторием из github_url)\n"
            "• Frontend работает на реальном хостинге, развёрнут\n"
            "• CORS origin правильно настроен на домен production frontend (localhost не прописан жёстко)\n"
            "• Адрес API во frontend настроен на домен production backend\n"
            "• Регистрация, вход, добавление/удаление задач, поиск — всё работает на живом сайте\n"
            "• README.md: рабочие ссылки (frontend + backend), технологии, чеклист завершения 6/6 этапов\n"
            "• Для отправки требуется ТОЛЬКО GitHub URL репозитория — AI-проверка анализирует весь код "
            "репозитория (backend + frontend), отдельное поле live_demo_url больше не обязательно"
        ),
    },
    756: {
        "requirements_uz": (
            "• Django backend haqiqiy hostingda Web Service sifatida ishlab turibdi\n"
            "• React frontend haqiqiy hostingda statik build sifatida ishlab turibdi\n"
            "• Telegram bot haqiqiy hostingda Background Worker sifatida ishlab turibdi (Web Service emas)\n"
            "• Bot va Django backend BIR XIL production PostgreSQL bazasiga ulangan\n"
            "• Ro'yxatdan o'tish, kirish, topshiriq qo'shish web saytda ishlaydi\n"
            "• /link va /topshiriqlar buyruqlari haqiqiy botda ishlaydi\n"
            "• README.md: jonli havolalar (frontend, backend, bot), 7/7 bosqich yakunlangan checklist, sinov ro'yxati\n"
            "• Submission uchun FAQAT GitHub repository URL talab qilinadi — AI baholash butun repo kodini "
            "(backend + frontend + bot) tekshiradi, alohida live_demo_url maydoni endi shart emas"
        ),
        "requirements_ru": (
            "• Django backend работает на реальном хостинге как Web Service\n"
            "• React frontend работает на реальном хостинге как статичная сборка\n"
            "• Telegram-бот работает на реальном хостинге как Background Worker (не Web Service)\n"
            "• Бот и Django backend подключены к ОДНОЙ production-базе PostgreSQL\n"
            "• Регистрация, вход, добавление задания работают на веб-сайте\n"
            "• Команды /link и /topshiriqlar работают в реальном боте\n"
            "• README.md: рабочие ссылки (frontend, backend, бот), чеклист завершения 7/7 этапов, чеклист проверки\n"
            "• Для отправки требуется ТОЛЬКО GitHub URL репозитория — AI-проверка анализирует весь код "
            "репозитория (backend + frontend + бот), отдельное поле live_demo_url больше не обязательно"
        ),
    },
    770: {
        "requirements_uz": (
            "• Flask (API + frontend) haqiqiy hostingda Web Service sifatida ishlab turibdi\n"
            "• Statik fayl yo'llari os.path.dirname(os.path.abspath(__file__)) asosida mutlaq qurilgan\n"
            "• Bosh sahifa va barcha CSS/JS fayllar production'da TO'G'RI yuklanadi (404 emas)\n"
            "• Telegram bot haqiqiy hostingda Background Worker sifatida ishlab turibdi (Web Service emas)\n"
            "• Bot va Flask BIR XIL production PostgreSQL bazasiga ulangan\n"
            "• Web saytda xarajat qo'shish HAMDA Telegram bot orqali matn bilan xarajat qo'shish ikkalasi ham ishlaydi\n"
            "• README.md: jonli havola, 7/7 bosqich yakunlangan checklist, sinov ro'yxati\n"
            "• Submission uchun FAQAT GitHub repository URL talab qilinadi — AI baholash butun repo kodini "
            "(Flask + bot) tekshiradi, alohida live_demo_url maydoni endi shart emas"
        ),
        "requirements_ru": (
            "• Flask (API + frontend) работает на реальном хостинге как Web Service\n"
            "• Пути к статическим файлам построены абсолютно, на основе os.path.dirname(os.path.abspath(__file__))\n"
            "• Главная страница и все CSS/JS файлы загружаются ПРАВИЛЬНО в production (не 404)\n"
            "• Telegram-бот работает на реальном хостинге как Background Worker (не Web Service)\n"
            "• Бот и Flask подключены к ОДНОЙ И ТОЙ ЖЕ production-базе PostgreSQL\n"
            "• Работает и добавление расхода на сайте, и добавление расхода через Telegram-бот текстом\n"
            "• README.md: живая ссылка, чеклист завершения 7/7 этапов, список проверки\n"
            "• Для отправки требуется ТОЛЬКО GitHub URL репозитория — AI-проверка анализирует весь код "
            "репозитория (Flask + бот), отдельное поле live_demo_url больше не обязательно"
        ),
    },
    784: {
        "requirements_uz": (
            "• Backend (Express + TypeScript) haqiqiy hostingda Web Service sifatida ishlab turibdi\n"
            "• Frontend (React) haqiqiy hostingda alohida deploy qilingan\n"
            "• Build jarayonida tsc-alias ishlatilgan (yoki path alias umuman ishlatilmagan) — node dist/server.js xatosiz ishga tushadi\n"
            "• CORS production frontend domeniga to'g'ri sozlangan\n"
            "• Ro'yxatdan o'tish, kirish, issue yaratish/ko'rish — barchasi jonli saytda ishlaydi\n"
            "• README.md: jonli havolalar, texnologiyalar, 7/7 bosqich yakunlangan checklist\n"
            "• Submission uchun FAQAT GitHub repository URL talab qilinadi — AI baholash butun repo kodini "
            "(backend + frontend) tekshiradi, alohida live_demo_url maydoni endi shart emas"
        ),
        "requirements_ru": (
            "• Backend (Express + TypeScript) работает на реальном хостинге как Web Service\n"
            "• Frontend (React) задеплоен на реальном хостинге отдельно\n"
            "• В процессе сборки использован tsc-alias (или path alias вообще не используется) — node dist/server.js запускается без ошибок\n"
            "• CORS правильно настроен на production-домен frontend'а\n"
            "• Регистрация, вход, создание/просмотр issue — всё работает на живом сайте\n"
            "• README.md: живые ссылки, технологии, чеклист завершения 7/7 этапов\n"
            "• Для отправки требуется ТОЛЬКО GitHub URL репозитория — AI-проверка анализирует весь код "
            "репозитория (backend + frontend), отдельное поле live_demo_url больше не обязательно"
        ),
    },
}


def _update_sections_json_requirements(sections_json: str, new_requirements: str) -> str:
    tree = json.loads(sections_json)
    found = False
    for section in tree:
        if section.get("type") == "project":
            section["requirements"] = new_requirements
            found = True
    if not found:
        raise ValueError("no 'project' section found in sections_json")
    return json.dumps(tree, ensure_ascii=False)


async def run(dry_run: bool = False) -> None:
    async with AsyncSessionLocal() as db:
        for lesson_id, data in UPDATES.items():
            lesson = (
                await db.execute(select(Lesson).where(Lesson.id == lesson_id))
            ).scalar_one()

            old_requirements = lesson.task_requirements
            new_requirements = data["requirements_uz"]

            lesson.task_requirements = new_requirements
            if lesson.sections_json:
                lesson.sections_json = _update_sections_json_requirements(
                    lesson.sections_json, new_requirements
                )

            await write_ru(
                db, "lesson", lesson_id, "task_requirements",
                new_requirements, data["requirements_ru"],
            )

            print(f"lesson {lesson_id}: task_requirements updated "
                  f"({len(old_requirements or '')} -> {len(new_requirements)} chars), "
                  f"sections_json project.requirements synced, RU cache written")

        if dry_run:
            await db.rollback()
            print("\nDRY RUN — rolled back, nothing written.")
        else:
            await db.commit()
            print(f"\nUpdated {len(UPDATES)} lesson(s).")


if __name__ == "__main__":
    asyncio.run(run(dry_run="--dry-run" in sys.argv))
