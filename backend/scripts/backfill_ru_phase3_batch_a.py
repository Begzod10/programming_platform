"""Phase 3 batch A: hand-translated RU backfill for GameQuestion quiz rows
in sessions 16, 27, 23, 17, 35, 33, 36 (HTML/CSS/Flexbox basics quizzes).
No translation API used — every string below composed by hand.

Idempotent: only updates rows still missing question_text_ru/options_ru;
safe to re-run. ORM-only via AsyncSessionLocal, no DDL, no app.main import.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402

from sqlalchemy import select, or_  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.team_game import GameQuestion  # noqa: E402

SESSIONS = [16, 27, 23, 17, 35, 33, 36]

QUESTION_MAP: dict[str, str] = {
    "2+2=?": "2+2=?",
    "HTML nima?": "Что такое HTML?",
    "HTML faylning to'g'ri kengaytmasi qaysi?": "Какое правильное расширение файла HTML?",
    "Veb-sahifada ko'rinadigan kontent qaysi tegda joylashadi?": "В каком теге размещается видимый на веб-странице контент?",
    "HTML tegni yozishning to'g'ri usuli qaysi?": "Какой правильный способ написания HTML-тега?",
    "Sarlavha teglari qancha darajadan iborat?": "Из скольких уровней состоят теги заголовков?",
    "Ternumli (raqamli) ro'yxat uchun qaysi teg ishlatiladi?": "Какой тег используется для нумерованного списка?",
    "Giperhavolalar yaratish uchun qaysi teg ishlatiladi?": "Какой тег используется для создания гиперссылок?",
    "Rasm qo'shish uchun qaysi teg ishlatiladi?": "Какой тег используется для добавления изображения?",
    "Tashqi CSS faylini ulash uchun qaysi teg ishlatiladi?": "Какой тег используется для подключения внешнего CSS-файла?",
    "Inline CSS qanday yoziladi?": "Как записывается встроенный (inline) CSS?",
    "CSS da izoh qanday yoziladi?": "Как пишется комментарий в CSS?",
    "Qaysi CSS uslubi eng yuqori ustuvorlikka ega?": "Какой способ подключения CSS имеет наивысший приоритет?",
    "CSS da class selektori qanday belgi bilan boshlanadi?": "С какого символа начинается селектор класса в CSS?",
    "CSS da ID selektori qanday belgi bilan boshlanadi?": "С какого символа начинается селектор ID в CSS?",
    "Bir sahifada bir ID necha marta ishlatilishi mumkin?": "Сколько раз один ID может использоваться на одной странице?",
    "Class va ID ning farqi nima?": "В чём разница между class и ID?",
    "<span> tegi qanday elementga kiradi?": "К какому типу элементов относится тег <span>?",
    "<div> tegi qanday elementga kiradi?": "К какому типу элементов относится тег <div>?",
    "display: none xususiyati nima qiladi?": "Что делает свойство display: none?",
    "inline-block va inline ning farqi nima?": "В чём разница между inline-block и inline?",
    "<div> tegi asosan nima uchun ishlatiladi?": "Для чего в основном используется тег <div>?",
    "Div elementiga chegara qo'shish uchun qaysi CSS xususiyati?": "Какое CSS-свойство используется для добавления границы к элементу div?",
    "Div ni gorizontal markazga qo'yish uchun:": "Чтобы расположить div по центру по горизонтали:",
    "Div ichiga div qo'ysa bo'ladimi?": "Можно ли вкладывать div внутрь div?",
    "Flexbox konteynerini yoqish uchun qanday yoziladi?": "Как включить flex-контейнер?",
    "justify-content xususiyati nimani boshqaradi?": "Чем управляет свойство justify-content?",
    "align-items: center nimani qiladi?": "Что делает align-items: center?",
    "flex-direction: column nimani o'zgartiradi?": "Что изменяет flex-direction: column?",
}

OPTION_MAP: dict[str, str] = {
    "3": "3", "4": "4", "5": "5", "6": "6",
    "HyperText Markup Language — veb-sahifalar yaratish tili": "HyperText Markup Language — язык разметки веб-страниц",
    "High Transfer Markup Language": "High Transfer Markup Language",
    "Hiper Murojaat Tili": "Язык гипер-обращений",
    "Asosiy Matn Dasturlash Tili": "Базовый язык программирования текста",
    ".html": ".html", ".hml": ".hml", ".hyp": ".hyp", ".web": ".web",
    "<body>": "<body>", "<head>": "<head>", "<html>": "<html>", "<meta>": "<meta>",
    "<p>Matn</p>": "<p>Текст</p>",
    "p>Matn<p>": "p>Текст<p>",
    "<<p>>Matn<</p>>": "<<p>>Текст<</p>>",
    "<p>Matn": "<p>Текст",
    "10 daraja": "10 уровней",
    "4 daraja": "4 уровня",
    "3 daraja": "3 уровня",
    "6 daraja (h1—h6)": "6 уровней (h1—h6)",
    "<ol>": "<ol>", "<ul>": "<ul>", "<li>": "<li>", "<list>": "<list>",
    "<href>": "<href>", "<url>": "<url>", "<a>": "<a>", "<link>": "<link>",
    "<img>": "<img>", "<photo>": "<photo>", "<image>": "<image>", "<pic>": "<pic>",
    "<style src='style.css'>": "<style src='style.css'>",
    "<css src='style.css'>": "<css src='style.css'>",
    "<link rel='stylesheet' href='style.css'>": "<link rel='stylesheet' href='style.css'>",
    "<script src='style.css'>": "<script src='style.css'>",
    "<p class='color:red'>": "<p class='color:red'>",
    "<p style='color:red'>": "<p style='color:red'>",
    "<style p='color:red'>": "<style p='color:red'>",
    "<p css='color:red'>": "<p css='color:red'>",
    "# izoh": "# комментарий",
    "/* izoh */": "/* комментарий */",
    "// izoh": "// комментарий",
    "<!-- izoh -->": "<!-- комментарий -->",
    "Hammasi teng": "Все равны",
    "Inline uslub (style='')": "Инлайн-стиль (style='')",
    "Tashqi .css fayl": "Внешний .css файл",
    "Ichki <style> tegi": "Внутренний тег <style>",
    "Panjara (#)": "Решётка (#)",
    "Belgi (@)": "Символ (@)",
    "Nuqta (.)": "Точка (.)",
    "Yulduzcha (*)": "Звёздочка (*)",
    "Foiz (%)": "Процент (%)",
    "Cheksiz": "Бесконечно",
    "2 marta": "2 раза",
    "Faqat 1 marta": "Только 1 раз",
    "5 marta": "5 раз",
    "Class faqat HTML5 da ishlaydi": "Class работает только в HTML5",
    "ID ko'p elementga, class bitta elementga": "ID — для многих элементов, class — для одного элемента",
    "Class ko'p elementga, ID faqat bitta elementga ishlatiladi": "Class используется для многих элементов, ID — только для одного элемента",
    "Ular bir xil": "Они одинаковые",
    "Flex element": "Flex-элемент",
    "Block element": "Блочный элемент",
    "Inline element": "Строчный элемент",
    "Grid element": "Grid-элемент",
    "None element": "Элемент типа none",
    "Inline-block element": "Строчно-блочный элемент (inline-block)",
    "Elementni pastga siljitadi": "Сдвигает элемент вниз",
    "Elementni yashiradi va joyini bo'shatadi": "Скрывает элемент и освобождает его место",
    "Elementni o'chiradi": "Удаляет элемент",
    "Elementni shaffof qiladi": "Делает элемент прозрачным",
    "inline-block kenglik/balandlik qabul qiladi, inline emas": "inline-block принимает ширину/высоту, а inline — нет",
    "inline block dan katta": "inline больше, чем block",
    "inline-block faqat div uchun": "inline-block только для div",
    "Matn kiritish uchun": "Для ввода текста",
    "Blok konteyner yaratish uchun": "Для создания блочного контейнера",
    "Jadval yaratish uchun": "Для создания таблицы",
    "Havolalar yaratish uchun": "Для создания ссылок",
    "frame": "frame", "edge": "edge", "outline": "outline", "border": "border",
    "position: center": "position: center",
    "margin: 0 auto (kenglik belgilangan bo'lishi kerak)": "margin: 0 auto (ширина должна быть задана)",
    "center: true": "center: true",
    "align: center": "align: center",
    "Faqat 2 daraja": "Только 2 уровня",
    "Faqat 3 daraja": "Только 3 уровня",
    "Ha, ixtiyoriy darajada ichma-ich bo'lishi mumkin": "Да, можно вкладывать на любую глубину",
    "Yo'q": "Нет",
    "display: flexbox": "display: flexbox",
    "use-flex: on": "use-flex: on",
    "display: flex": "display: flex",
    "flex: true": "flex: true",
    "Element balandligini": "Высоту элемента",
    "Matn shriftini": "Шрифт текста",
    "Asosiy o'q (gorizontal) bo'ylab joylashuvni": "Расположение вдоль главной оси (горизонтальной)",
    "Ko'ndalang o'q bo'ylab joylashuvni": "Расположение вдоль поперечной оси",
    "Elementni kengaytiradi": "Растягивает элемент",
    "Elementlarni ko'ndalang o'q (vertikal) bo'ylab markazlashtiradi": "Центрирует элементы вдоль поперечной оси (по вертикали)",
    "Elementlarni gorizontal markazlashtiradi": "Центрирует элементы по горизонтали",
    "Matnni markazlashtiradi": "Центрирует текст",
    "Elementlar tasodifiy joylashadi": "Элементы располагаются случайным образом",
    "Elementlar o'ngdan chapga joylashadi": "Элементы располагаются справа налево",
    "Elementlar chapdan o'ngga joylashadi": "Элементы располагаются слева направо",
    "Flex elementlar ustunga (vertikal) joylashadi": "Flex-элементы располагаются в колонку (по вертикали)",
}


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(GameQuestion).where(
                GameQuestion.question_kind == "quiz",
                GameQuestion.session_id.in_(SESSIONS),
                or_(GameQuestion.question_text_ru.is_(None), GameQuestion.question_text_ru == "", GameQuestion.options_ru.is_(None)),
            ).order_by(GameQuestion.id)
        )
        rows = result.scalars().all()
        print(f"Batch A: {len(rows)} rows need RU")

        written = 0
        for row in rows:
            q_ru = QUESTION_MAP.get(row.question_text)
            if q_ru is None:
                print(f"  SKIP id={row.id} session={row.session_id}: no question mapping for {row.question_text!r}")
                continue
            opts_ru = []
            ok = True
            for o in row.options:
                tr = OPTION_MAP.get(o)
                if tr is None:
                    ok = False
                    print(f"  SKIP id={row.id}: missing option mapping for {o!r}")
                opts_ru.append(tr)
            if not ok:
                continue
            row.question_text_ru = q_ru
            row.options_ru = opts_ru
            written += 1
        await db.commit()
        print(f"Batch A wrote {written}/{len(rows)} rows.")


if __name__ == "__main__":
    asyncio.run(main())
