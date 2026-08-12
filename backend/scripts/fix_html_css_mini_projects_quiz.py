"""Replace the team-game quiz question bank for course 50 ("HTML/CSS
Mini-Projects") — all 13 lessons' questions were topically unrelated to
their actual lesson content (generic "trendy CSS effects" trivia instead
of questions about the lesson's real subject), and had zero Russian
translation.

Writes both UZ and RU rows per lesson using the SAME dual-row-per-language
pattern already used correctly elsewhere on the platform (e.g. lesson 496,
"HTML/CSS: Keyingi Bosqich" — confirmed via import_questions_from_lesson's
_detect_lang() Cyrillic-detection pairing): N Uzbek rows at order_index
0..N-1, followed by N Russian rows reusing the same order_index values.
The team-game import endpoint pairs them positionally by order_index, so
the exact order here matters — each language block must list its 8
questions in the same conceptual order as the other language's block.
"""
from __future__ import annotations
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select, delete  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson_question import LessonQuestion  # noqa: E402

# lesson_id -> {"uz": [(question, options, correct_idx), ...], "ru": [...]}
QUESTIONS = {
    480: {  # Mini-Loyiha 1: HTML Jadvallar
        "uz": [
            ("Jadval yaratish uchun asosiy HTML tegi qaysi?", ["<table>", "<grid>", "<list>", "<div>"], 0),
            ("Jadval qatorini belgilaydigan teg?", ["<td>", "<tr>", "<th>", "<row>"], 1),
            ("Jadval sarlavha katakchasi uchun teg?", ["<td>", "<head>", "<th>", "<title>"], 2),
            ("Oddiy ma'lumot katakchasi uchun teg?", ["<th>", "<tc>", "<td>", "<cell>"], 2),
            ("Bir nechta ustunni birlashtirish uchun atribut?", ["rowspan", "colspan", "merge", "union"], 1),
            ("Bir nechta qatorni birlashtirish uchun atribut?", ["colspan", "merge", "rowspan", "span"], 2),
            ("Jadval chegarasini CSS bilan qo'yish uchun xususiyat?", ["border", "outline", "edge", "frame"], 0),
            ("Juft va toq qatorlarni turlicha ranglash uchun CSS pseudo-klass?", [":first-child", ":nth-child()", ":not()", ":before"], 1),
        ],
        "ru": [
            ("Какой основной HTML-тег используется для создания таблицы?", ["<table>", "<grid>", "<list>", "<div>"], 0),
            ("Какой тег обозначает строку таблицы?", ["<td>", "<tr>", "<th>", "<row>"], 1),
            ("Какой тег используется для заголовочной ячейки таблицы?", ["<td>", "<head>", "<th>", "<title>"], 2),
            ("Какой тег используется для обычной ячейки с данными?", ["<th>", "<tc>", "<td>", "<cell>"], 2),
            ("Какой атрибут объединяет несколько столбцов?", ["rowspan", "colspan", "merge", "union"], 1),
            ("Какой атрибут объединяет несколько строк?", ["colspan", "merge", "rowspan", "span"], 2),
            ("Какое CSS-свойство задаёт границу таблицы?", ["border", "outline", "edge", "frame"], 0),
            ("Какой CSS-псевдокласс красит чётные/нечётные строки по-разному?", [":first-child", ":nth-child()", ":not()", ":before"], 1),
        ],
    },
    481: {  # Mini-Loyiha 2: Ro'yxat Dizayni
        "uz": [
            ("Ro'yxat belgisini (marker) olib tashlash uchun CSS xususiyati?", ["list-style: none", "display: none", "marker: off", "list: hidden"], 0),
            ("<ul> va <ol> orasidagi asosiy farq nima?", ["<ul> — tartiblangan, <ol> — tartibsiz", "<ul> — tartibsiz, <ol> — tartiblangan", "Farqi yo'q", "<ol> faqat raqamlar uchun emas"], 1),
            ("Ro'yxat elementlarini gorizontal qatorga joylashtirish uchun eng oson usul?", ["display: flex", "position: fixed", "float: none", "list-style: row"], 0),
            ("backdrop-filter CSS xususiyati nima uchun ishlatiladi?", ["Matn rangini o'zgartirish", "Elementning orqasidagi kontentga effekt (blur va h.k.) berish", "Ro'yxat tartibini o'zgartirish", "Animatsiya yaratish"], 1),
            ("Ro'yxat elementi (bandi) uchun HTML tegi qaysi?", ["<item>", "<li>", "<row>", "<list>"], 1),
            ("Flexbox konteynerida elementlar orasidagi bo'shliqni belgilaydigan xususiyat?", ["margin", "gap", "space", "padding"], 1),
            ("backdrop-filter: blur(10px) nima qiladi?", ["Elementning o'zini xiralashtiradi", "Elementning orqasidagi fonni xiralashtiradi", "Matnni o'chiradi", "Ranglarni teskari qiladi"], 1),
            ("Flexbox'da elementlarni vertikal markazlashtirish uchun xususiyat?", ["justify-content", "align-items", "text-align", "vertical-align"], 1),
        ],
        "ru": [
            ("Какое CSS-свойство убирает маркер списка?", ["list-style: none", "display: none", "marker: off", "list: hidden"], 0),
            ("В чём главное различие между <ul> и <ol>?", ["<ul> — упорядоченный, <ol> — неупорядоченный", "<ul> — неупорядоченный, <ol> — упорядоченный", "Разницы нет", "<ol> не только для чисел"], 1),
            ("Какой самый простой способ расположить элементы списка в строку?", ["display: flex", "position: fixed", "float: none", "list-style: row"], 0),
            ("Для чего используется CSS-свойство backdrop-filter?", ["Изменить цвет текста", "Применить эффект (например blur) к тому, что находится позади элемента", "Изменить порядок списка", "Создать анимацию"], 1),
            ("Какой HTML-тег используется для пункта списка?", ["<item>", "<li>", "<row>", "<list>"], 1),
            ("Какое свойство flex-контейнера задаёт расстояние между элементами?", ["margin", "gap", "space", "padding"], 1),
            ("Что делает backdrop-filter: blur(10px)?", ["Размывает сам элемент", "Размывает фон позади элемента", "Убирает текст", "Инвертирует цвета"], 1),
            ("Какое свойство вертикально центрирует элементы во flex-контейнере?", ["justify-content", "align-items", "text-align", "vertical-align"], 1),
        ],
    },
    482: {  # Mini-Loyiha 3: Navigatsiya Paneli
        "uz": [
            ("Navigatsiya uchun mo'ljallangan semantik HTML tegi qaysi?", ["<navigation>", "<nav>", "<menu>", "<header>"], 1),
            ("Scroll qilganda ma'lum nuqtaga yetganda \"yopishib qoladigan\" position qiymati?", ["fixed", "absolute", "sticky", "relative"], 2),
            ("Navigatsiya havolalarini gorizontal joylashtirish uchun eng keng tarqalgan usul?", ["display: flex", "position: sticky", "float: right", "text-align: center"], 0),
            ("z-index xususiyati sticky navbar uchun nima uchun kerak bo'lishi mumkin?", ["Ranglarni almashtirish uchun", "Navbar boshqa kontent ustida qolishini ta'minlash uchun", "Shriftni o'zgartirish uchun", "Animatsiya berish uchun"], 1),
            ("Navigatsiya ro'yxati odatda qaysi teglar birikmasida joylashadi?", ["<ul><li><a>", "<table><tr><td>", "<div><span><p>", "<form><input><button>"], 0),
            ("position: sticky va position: fixed orasidagi asosiy farq?", ["Farqi yo'q", "sticky ota-konteyner ichida ishlaydi, fixed butun oynaga bog'lanadi", "fixed faqat navbar uchun ishlaydi", "sticky eski brauzerlarda ishlamaydi"], 1),
            ("Sticky elementning qaysi nuqtada \"yopishishini\" belgilash uchun qaysi xususiyat kerak?", ["margin", "top (yoki boshqa chekka)", "z-index", "display"], 1),
            ("Navbar fonini scroll paytida o'zgartirish (masalan shaffofdan qattiqqa) odatda qanday amalga oshiriladi?", ["Faqat CSS bilan, hech qanday kod kerak emas", "JavaScript bilan scroll holatini kuzatib", "HTML atributi orqali", "Bu imkonsiz"], 1),
        ],
        "ru": [
            ("Какой семантический HTML-тег предназначен для навигации?", ["<navigation>", "<nav>", "<menu>", "<header>"], 1),
            ("Какое значение position \"прилипает\" в определённой точке при прокрутке?", ["fixed", "absolute", "sticky", "relative"], 2),
            ("Какой самый распространённый способ расположить ссылки навигации в строку?", ["display: flex", "position: sticky", "float: right", "text-align: center"], 0),
            ("Зачем может понадобиться z-index для sticky-навбара?", ["Чтобы менять цвета", "Чтобы навбар оставался поверх остального контента", "Чтобы менять шрифт", "Чтобы добавить анимацию"], 1),
            ("В каком сочетании тегов обычно располагается список навигации?", ["<ul><li><a>", "<table><tr><td>", "<div><span><p>", "<form><input><button>"], 0),
            ("В чём основное различие между position: sticky и position: fixed?", ["Разницы нет", "sticky работает внутри родительского контейнера, fixed привязан ко всему окну", "fixed работает только для навбара", "sticky не работает в старых браузерах"], 1),
            ("Какое свойство задаёт точку, в которой \"прилипает\" sticky-элемент?", ["margin", "top (или другой край)", "z-index", "display"], 1),
            ("Как обычно меняют фон навбара при прокрутке (например с прозрачного на сплошной)?", ["Только через CSS, без кода", "Через JavaScript, отслеживая состояние прокрутки", "Через HTML-атрибут", "Это невозможно"], 1),
        ],
    },
    483: {  # Mini-Loyiha 4: Kartochkalar (Cards)
        "uz": [
            ("Bir nechta kartochkani panjara (grid) shaklida joylashtirish uchun CSS xususiyati?", ["display: flex", "display: grid", "display: table", "display: card"], 1),
            ("Grid ustunlari sonini va o'lchamini belgilaydigan xususiyat?", ["grid-gap", "grid-template-columns", "grid-area", "grid-flow"], 1),
            ("Kartaga sichqoncha olib borilganda (hover) kattalashtirish effekti uchun CSS xususiyati?", ["transform", "position", "float", "clear"], 0),
            ("transform: scale(1.05) nima qiladi?", ["Elementni 5% kattalashtiradi", "Elementni 105 pikselga suradi", "Elementni aylantiradi", "Elementni yashiradi"], 0),
            ("Kartochkaga soya (shadow) berish uchun CSS xususiyati?", ["box-shadow", "text-shadow", "border-shadow", "drop-shadow"], 0),
            ("Grid elementlari orasidagi bo'shliqni belgilaydigan xususiyat?", ["margin", "gap", "spacing", "padding"], 1),
            ("Kartochka burchaklarini yumaloqlash uchun CSS xususiyati?", ["border-round", "corner-radius", "border-radius", "round-corner"], 2),
            ("hover paytidagi o'zgarishni silliq (animatsion) qilish uchun qaysi xususiyat kerak?", ["transition", "animation-name", "delay", "smooth"], 0),
        ],
        "ru": [
            ("Какое CSS-свойство располагает несколько карточек в виде сетки (grid)?", ["display: flex", "display: grid", "display: table", "display: card"], 1),
            ("Какое свойство задаёт количество и размер колонок сетки?", ["grid-gap", "grid-template-columns", "grid-area", "grid-flow"], 1),
            ("Какое CSS-свойство используется для эффекта увеличения карточки при наведении?", ["transform", "position", "float", "clear"], 0),
            ("Что делает transform: scale(1.05)?", ["Увеличивает элемент на 5%", "Сдвигает элемент на 105 пикселей", "Поворачивает элемент", "Скрывает элемент"], 0),
            ("Какое CSS-свойство добавляет тень карточке?", ["box-shadow", "text-shadow", "border-shadow", "drop-shadow"], 0),
            ("Какое свойство задаёт расстояние между элементами сетки?", ["margin", "gap", "spacing", "padding"], 1),
            ("Какое CSS-свойство скругляет углы карточки?", ["border-round", "corner-radius", "border-radius", "round-corner"], 2),
            ("Какое свойство нужно, чтобы изменение при hover было плавным (анимированным)?", ["transition", "animation-name", "delay", "smooth"], 0),
        ],
    },
    484: {  # Mini-Loyiha 5: Flexbox Layout
        "uz": [
            ("Flex konteyner yaratish uchun CSS xususiyati?", ["display: flex", "display: block", "position: flex", "flex: true"], 0),
            ("Elementlarni asosiy o'q (odatda gorizontal) bo'yicha joylashtiradigan xususiyat?", ["align-items", "justify-content", "flex-wrap", "order"], 1),
            ("Elementlarni ko'ndalang o'q (odatda vertikal) bo'yicha joylashtiradigan xususiyat?", ["justify-content", "align-items", "flex-basis", "gap"], 1),
            ("flex-direction xususiyatining standart (default) qiymati?", ["column", "row", "row-reverse", "wrap"], 1),
            ("Elementlarni sig'masa keyingi qatorga o'tkazish uchun xususiyat?", ["flex-wrap: wrap", "overflow: hidden", "flex-grow: 1", "display: block"], 0),
            ("Bitta elementning bo'sh joyni qanchalik egallashini belgilaydigan xususiyat?", ["flex-shrink", "flex-grow", "flex-basis", "order"], 1),
            ("justify-content: space-between nima qiladi?", ["Elementlarni chetlarga yopishtiradi, orasida teng bo'shliq qoldiradi", "Elementlarni markazga joylashtiradi", "Elementlarni bir-biriga yopishtiradi", "Hech narsa qilmaydi"], 0),
            ("Bitta elementni boshqalaridan farqli tarzda joylashtirish uchun ishlatiladigan xususiyat?", ["align-items", "align-self", "justify-self", "self-align"], 1),
        ],
        "ru": [
            ("Какое CSS-свойство создаёт flex-контейнер?", ["display: flex", "display: block", "position: flex", "flex: true"], 0),
            ("Какое свойство располагает элементы по главной (обычно горизонтальной) оси?", ["align-items", "justify-content", "flex-wrap", "order"], 1),
            ("Какое свойство располагает элементы по поперечной (обычно вертикальной) оси?", ["justify-content", "align-items", "flex-basis", "gap"], 1),
            ("Каково значение flex-direction по умолчанию?", ["column", "row", "row-reverse", "wrap"], 1),
            ("Какое свойство переносит элементы на новую строку, если они не помещаются?", ["flex-wrap: wrap", "overflow: hidden", "flex-grow: 1", "display: block"], 0),
            ("Какое свойство определяет, сколько свободного места займёт один элемент?", ["flex-shrink", "flex-grow", "flex-basis", "order"], 1),
            ("Что делает justify-content: space-between?", ["Прижимает элементы к краям, оставляя равные промежутки между ними", "Центрирует элементы", "Прижимает элементы друг к другу", "Ничего не делает"], 0),
            ("Какое свойство используется, чтобы расположить один элемент иначе, чем остальные?", ["align-items", "align-self", "justify-self", "self-align"], 1),
        ],
    },
    485: {  # Mini-Loyiha 6: Div Layout (Bugatti)
        "uz": [
            ("<div> tegi asosan nima uchun ishlatiladi?", ["Faqat matn uchun", "Generic (umumiy) konteyner, tuzilma yaratish uchun", "Faqat rasm uchun", "Faqat jadval uchun"], 1),
            ("Div ichidagi kontentni markazlashtirish uchun keng tarqalgan usul?", ["float: center", "display: flex + justify-content/align-items", "text-decoration: center", "position: center"], 1),
            ("Bir nechta div'ni gorizontal qatorga joylashtirishning eng oson yo'li?", ["display: flex", "display: none", "position: static", "clear: both"], 0),
            ("Div'ning ichki bo'shlig'ini belgilaydigan CSS xususiyati?", ["margin", "padding", "gap", "border"], 1),
            ("Div'lar orasidagi tashqi bo'shliqni belgilaydigan CSS xususiyati?", ["padding", "gap", "margin", "spacing"], 2),
            ("Div'ga fon rasm qo'yish uchun CSS xususiyati?", ["background-image", "src", "img-src", "background-source"], 0),
            ("box-sizing: border-box nima qiladi?", ["padding va border'ni elementning belgilangan width/height ichiga hisoblaydi", "Barcha chegaralarni olib tashlaydi", "Elementni ko'rinmas qiladi", "Faqat rangni o'zgartiradi"], 0),
            ("width: 100% bilan max-width: 100% orasidagi farq?", ["Farqi yo'q", "width majburiy o'lcham beradi, max-width faqat yuqori chegara qo'yadi", "max-width faqat rasm uchun ishlaydi", "width faqat flexbox'da ishlaydi"], 1),
        ],
        "ru": [
            ("Для чего в основном используется тег <div>?", ["Только для текста", "Как обобщённый контейнер для создания структуры", "Только для изображений", "Только для таблиц"], 1),
            ("Какой распространённый способ центрировать содержимое внутри div?", ["float: center", "display: flex + justify-content/align-items", "text-decoration: center", "position: center"], 1),
            ("Какой самый простой способ расположить несколько div в одну строку?", ["display: flex", "display: none", "position: static", "clear: both"], 0),
            ("Какое CSS-свойство задаёт внутренний отступ div?", ["margin", "padding", "gap", "border"], 1),
            ("Какое CSS-свойство задаёт внешний отступ между div?", ["padding", "gap", "margin", "spacing"], 2),
            ("Какое CSS-свойство задаёт фоновое изображение div?", ["background-image", "src", "img-src", "background-source"], 0),
            ("Что делает box-sizing: border-box?", ["Учитывает padding и border внутри заданной ширины/высоты элемента", "Убирает все границы", "Делает элемент невидимым", "Только меняет цвет"], 0),
            ("В чём разница между width: 100% и max-width: 100%?", ["Разницы нет", "width задаёт фиксированный размер, max-width — лишь верхнюю границу", "max-width работает только для изображений", "width работает только во flexbox"], 1),
        ],
    },
    486: {  # Mini-Loyiha 7: CSS Position — Shaxsiy Kartochka
        "uz": [
            ("position: relative element qaysi nuqtaga nisbatan joylashadi?", ["Eng yaqin positioned ota-elementga nisbatan", "O'zining odatdagi (normal) joyiga nisbatan", "Butun sahifaga nisbatan", "Brauzer oynasiga nisbatan"], 1),
            ("position: absolute element qaysi nuqtaga nisbatan joylashadi?", ["Eng yaqin positioned ota-elementga nisbatan", "Har doim brauzer oynasiga nisbatan", "O'zining odatdagi joyiga nisbatan", "Hech qanday nuqtaga bog'liq emas"], 0),
            ("position: fixed element nimaga nisbatan joylashadi?", ["Ota-elementga", "Brauzer oynasiga (viewport)", "Eng yaqin div'ga", "Sahifaning boshiga"], 1),
            ("position: sticky elementning xususiyati nimadan iborat?", ["Har doim qat'iy joyda turadi", "Scroll qilinganda ma'lum nuqtagacha oddiy, keyin \"yopishib\" qoladi", "Hech qachon ko'rinmaydi", "Faqat rasm uchun ishlatiladi"], 1),
            ("top, left, right, bottom xususiyatlari qaysi xususiyat bilan birga ishlatiladi?", ["display", "position", "float", "overflow"], 1),
            ("position: absolute berilgan element to'g'ri joylashishi uchun ota-elementda odatda nima bo'lishi kerak?", ["display: flex", "position: relative (yoki boshqa positioned qiymat)", "overflow: hidden", "Hech narsa kerak emas"], 1),
            ("z-index xususiyati nima uchun ishlatiladi?", ["Elementning kengligini belgilash uchun", "Ustma-ust joylashgan elementlarning qatlamini (tartibini) boshqarish uchun", "Rangni o'zgartirish uchun", "Shriftni o'zgartirish uchun"], 1),
            ("position: static (standart qiymat) haqida qaysi gap to'g'ri?", ["top/left kabi xususiyatlar unga ta'sir qilmaydi", "U har doim sahifa markazida turadi", "U faqat rasm uchun ishlatiladi", "U sticky bilan bir xil"], 0),
        ],
        "ru": [
            ("Относительно чего позиционируется элемент с position: relative?", ["Относительно ближайшего позиционированного родителя", "Относительно своего обычного (нормального) положения", "Относительно всей страницы", "Относительно окна браузера"], 1),
            ("Относительно чего позиционируется элемент с position: absolute?", ["Относительно ближайшего позиционированного родителя", "Всегда относительно окна браузера", "Относительно своего обычного положения", "Ни от чего не зависит"], 0),
            ("Относительно чего позиционируется элемент с position: fixed?", ["Относительно родителя", "Относительно окна браузера (viewport)", "Относительно ближайшего div", "Относительно начала страницы"], 1),
            ("В чём особенность position: sticky?", ["Всегда остаётся на строго фиксированном месте", "При прокрутке ведёт себя обычно до определённой точки, затем \"прилипает\"", "Никогда не видим", "Используется только для изображений"], 1),
            ("С каким свойством используются top, left, right, bottom?", ["display", "position", "float", "overflow"], 1),
            ("Что обычно должно быть у родительского элемента, чтобы position: absolute сработал правильно?", ["display: flex", "position: relative (или другое позиционированное значение)", "overflow: hidden", "Ничего не нужно"], 1),
            ("Для чего используется свойство z-index?", ["Чтобы задать ширину элемента", "Чтобы управлять порядком (слоями) наложенных друг на друга элементов", "Чтобы изменить цвет", "Чтобы изменить шрифт"], 1),
            ("Какое утверждение о position: static (значение по умолчанию) верно?", ["Свойства вроде top/left на него не влияют", "Он всегда находится в центре страницы", "Используется только для изображений", "Он идентичен sticky"], 0),
        ],
    },
    487: {  # Mini-Loyiha 8: CSS Position — Ilg'or
        "uz": [
            ("Overlay (fonni qorong'ilashtiruvchi qatlam) effekti uchun odatda qaysi position ishlatiladi?", ["static", "absolute (yoki fixed)", "relative", "inherit"], 1),
            ("Fixed navbar scroll qilinganda qanday xatti-harakat qiladi?", ["Sahifa bilan birga siljib ketadi", "Har doim ekranning bir joyida qoladi", "Yo'qolib ketadi", "Kattalashadi"], 1),
            ("Sticky sidebar qachon \"yopishib\" qoladi?", ["Sahifa yuklangan zahoti", "Belgilangan chegaraga (masalan top: 0) yetganda", "Hech qachon", "Faqat mobil qurilmada"], 1),
            ("Overlay uchun orqa fonni qorong'ilashtirish odatda qaysi usul bilan qilinadi?", ["background-color: rgba(0,0,0,0.5) kabi shaffof rang", "font-weight: bold", "text-align: center", "border: 1px solid black"], 0),
            ("inset xususiyati bir vaqtning o'zida qaysi 4 ta xususiyatni belgilaydi?", ["margin, padding, border, outline", "top, right, bottom, left", "width, height, min-width, max-width", "color, background, border, shadow"], 1),
            ("position: fixed elementlar scroll paytida sahifa bilan birga harakatlanadimi?", ["Ha, doim harakatlanadi", "Yo'q, ular ekranga nisbatan qat'iy turadi", "Faqat mobil qurilmada harakatlanadi", "Bog'liq emas"], 1),
            ("Modal oyna (dialog) ni ekran markaziga joylashtirish uchun odatiy usul?", ["position: fixed + transform: translate(-50%, -50%)", "float: center", "display: none", "text-align: center"], 0),
            ("Ikkita positioned element z-index belgilanmasdan ustma-ust kelsa, qaysi biri tepada ko'rinadi?", ["Har doim birinchisi", "HTML kodida keyinroq yozilgani", "Tasodifiy tanlanadi", "Hech biri ko'rinmaydi"], 1),
        ],
        "ru": [
            ("Какой position обычно используется для эффекта overlay (затемняющего слоя поверх фона)?", ["static", "absolute (или fixed)", "relative", "inherit"], 1),
            ("Как ведёт себя fixed-навбар при прокрутке страницы?", ["Прокручивается вместе со страницей", "Всегда остаётся на одном месте экрана", "Исчезает", "Увеличивается"], 1),
            ("Когда \"прилипает\" sticky-сайдбар?", ["Сразу при загрузке страницы", "Когда достигает заданной границы (например top: 0)", "Никогда", "Только на мобильных устройствах"], 1),
            ("Каким способом обычно затемняют фон для overlay?", ["Полупрозрачный цвет вроде background-color: rgba(0,0,0,0.5)", "font-weight: bold", "text-align: center", "border: 1px solid black"], 0),
            ("Какие 4 свойства одновременно задаёт inset?", ["margin, padding, border, outline", "top, right, bottom, left", "width, height, min-width, max-width", "color, background, border, shadow"], 1),
            ("Двигаются ли элементы с position: fixed вместе со страницей при прокрутке?", ["Да, всегда двигаются", "Нет, они остаются неподвижны относительно экрана", "Только на мобильных устройствах", "Не имеет значения"], 1),
            ("Какой типичный способ разместить модальное окно по центру экрана?", ["position: fixed + transform: translate(-50%, -50%)", "float: center", "display: none", "text-align: center"], 0),
            ("Если два позиционированных элемента накладываются без заданного z-index, какой окажется сверху?", ["Всегда первый", "Тот, что написан позже в HTML-коде", "Выбирается случайно", "Ни один не будет виден"], 1),
        ],
    },
    488: {  # Mini-Loyiha 9: Login Formasi
        "uz": [
            ("Login formasi uchun asosiy HTML tegi qaysi?", ["<form>", "<login>", "<input>", "<section>"], 0),
            ("Parol maydoni uchun qaysi input turi ishlatiladi?", ["type=\"text\"", "type=\"password\"", "type=\"hidden\"", "type=\"secret\""], 1),
            ("Forma ma'lumotlarini yuborish uchun tugma turi?", ["type=\"button\"", "type=\"reset\"", "type=\"submit\"", "type=\"send\""], 2),
            ("Input maydoniga nom berish (server tomonda aniqlash uchun) atribut?", ["id", "name", "class", "label"], 1),
            ("placeholder atributi nima qiladi?", ["Maydonni majburiy qiladi", "Maydon bo'sh bo'lganda ko'rinadigan maslahat matnini ko'rsatadi", "Maydonni o'chirib qo'yadi", "Maydon turini o'zgartiradi"], 1),
            ("Forma elementlarini vertikal ravishda tartibli joylashtirish uchun keng tarqalgan usul?", ["display: flex; flex-direction: column", "display: table", "position: absolute", "float: left"], 0),
            ("<label> va <input> ni bog'lash uchun ishlatiladigan atributlar?", ["name va id", "for (label'da) va id (input'da)", "class va style", "type va value"], 1),
            ("required atributi input'ga qo'shilsa nima bo'ladi?", ["Maydon ixtiyoriy bo'ladi", "Maydonni to'ldirmasdan forma yuborilmaydi", "Maydon yashiriladi", "Hech narsa o'zgarmaydi"], 1),
        ],
        "ru": [
            ("Какой основной HTML-тег используется для формы входа?", ["<form>", "<login>", "<input>", "<section>"], 0),
            ("Какой тип input используется для поля пароля?", ["type=\"text\"", "type=\"password\"", "type=\"hidden\"", "type=\"secret\""], 1),
            ("Какой тип кнопки используется для отправки данных формы?", ["type=\"button\"", "type=\"reset\"", "type=\"submit\"", "type=\"send\""], 2),
            ("Какой атрибут задаёт имя поля ввода (для распознавания на сервере)?", ["id", "name", "class", "label"], 1),
            ("Что делает атрибут placeholder?", ["Делает поле обязательным", "Показывает подсказку, видимую пока поле пустое", "Отключает поле", "Меняет тип поля"], 1),
            ("Какой распространённый способ расположить элементы формы вертикально по порядку?", ["display: flex; flex-direction: column", "display: table", "position: absolute", "float: left"], 0),
            ("Какие атрибуты связывают <label> и <input>?", ["name и id", "for (у label) и id (у input)", "class и style", "type и value"], 1),
            ("Что произойдёт, если добавить атрибут required к input?", ["Поле станет необязательным", "Форма не отправится, пока поле не заполнено", "Поле скроется", "Ничего не изменится"], 1),
        ],
    },
    489: {  # Mini-Loyiha 10: Register Formasi
        "uz": [
            ("Email kiritish maydoni uchun input turi?", ["type=\"text\"", "type=\"email\"", "type=\"mail\"", "type=\"address\""], 1),
            ("Register formasida odatda nechta parol maydoni bo'ladi (tasdiqlash uchun)?", ["1 ta", "2 ta", "3 ta", "Umuman kerak emas"], 1),
            ("type=\"email\" bilan brauzerda avtomatik validatsiya ishlaydimi?", ["Yo'q, hech qachon", "Ha, brauzer email formatini avtomatik tekshiradi", "Faqat Chrome'da ishlaydi", "Faqat JavaScript bilan ishlaydi"], 1),
            ("\"Shartlarga roziman\" kabi belgilarni tanlash uchun qaysi input turi ishlatiladi?", ["type=\"radio\"", "type=\"checkbox\"", "type=\"select\"", "type=\"toggle\""], 1),
            ("minlength atributi nima qiladi?", ["Maksimal belgilar sonini belgilaydi", "Minimal belgilar sonini belgilaydi", "Maydon kengligini belgilaydi", "Shrift o'lchamini belgilaydi"], 1),
            ("pattern atributi nima uchun ishlatiladi?", ["Fon rasmini belgilash uchun", "Regex orqali maxsus formatga mos kelishini tekshirish uchun", "Ranglarni almashtirish uchun", "Forma dizaynini o'zgartirish uchun"], 1),
            ("Forma yuborilishidan oldin ma'lumotlarni tekshirish jarayoni odatda nima deb ataladi?", ["Rendering", "Validatsiya", "Kompilyatsiya", "Animatsiya"], 1),
            ("Ro'yxatdan tanlash (masalan mamlakat tanlash) uchun HTML elementi?", ["<input type=\"list\">", "<select>", "<pick>", "<dropdown>"], 1),
        ],
        "ru": [
            ("Какой тип input используется для ввода email?", ["type=\"text\"", "type=\"email\"", "type=\"mail\"", "type=\"address\""], 1),
            ("Сколько полей пароля обычно бывает в форме регистрации (для подтверждения)?", ["1", "2", "3", "Не нужно вообще"], 1),
            ("Работает ли автоматическая валидация в браузере с type=\"email\"?", ["Нет, никогда", "Да, браузер автоматически проверяет формат email", "Только в Chrome", "Только с JavaScript"], 1),
            ("Какой тип input используется для галочки вроде \"Согласен с условиями\"?", ["type=\"radio\"", "type=\"checkbox\"", "type=\"select\"", "type=\"toggle\""], 1),
            ("Что делает атрибут minlength?", ["Задаёт максимальное число символов", "Задаёт минимальное число символов", "Задаёт ширину поля", "Задаёт размер шрифта"], 1),
            ("Для чего используется атрибут pattern?", ["Чтобы задать фоновое изображение", "Чтобы проверить соответствие вводу через regex", "Чтобы поменять цвета", "Чтобы изменить дизайн формы"], 1),
            ("Как обычно называется процесс проверки данных перед отправкой формы?", ["Rendering", "Валидация", "Компиляция", "Анимация"], 1),
            ("Какой HTML-элемент используется для выбора из списка (например страны)?", ["<input type=\"list\">", "<select>", "<pick>", "<dropdown>"], 1),
        ],
    },
    490: {  # Mini-Loyiha 11: CSS Animatsiya — Asoslar
        "uz": [
            ("CSS animatsiyasining bosqichlarini belgilaydigan direktiv?", ["@animation", "@keyframes", "@frames", "@motion"], 1),
            ("Animatsiyani elementga bog'lash uchun asosiy xususiyat?", ["animation-name", "transition-name", "keyframe-name", "motion-name"], 0),
            ("Animatsiya qancha vaqt davom etishini belgilaydigan xususiyat?", ["animation-delay", "animation-duration", "animation-timing", "animation-length"], 1),
            ("Oddiy fade-in effekti odatda qaysi CSS xususiyatini o'zgartiradi?", ["color", "opacity", "font-size", "border"], 1),
            ("Animatsiyani cheksiz takrorlash uchun qiymat?", ["animation-iteration-count: infinite", "animation-repeat: always", "animation-loop: true", "animation-count: max"], 0),
            ("@keyframes ichidagi 0% va 100% nimani bildiradi?", ["Ranglarni", "Animatsiyaning boshlanish va tugash holatlarini", "Elementning o'lchamini", "Sahifa yuklanish tezligini"], 1),
            ("transition va animation orasidagi asosiy farq nima?", ["Ular bir xil narsa", "transition — holat o'zgarishida ishga tushadi, animation — mustaqil, avtomatik ishlay oladi", "animation faqat rangga ta'sir qiladi", "transition cheksiz takrorlanadi, animation yo'q"], 1),
            ("animation-timing-function xususiyati nimani belgilaydi?", ["Animatsiyaning ranglarini", "Animatsiya tezligining o'zgarish egri chizig'ini (masalan ease, linear)", "Animatsiya nechta marta takrorlanishini", "Animatsiya boshlanish vaqtini kechiktirish"], 1),
        ],
        "ru": [
            ("Какая директива определяет этапы CSS-анимации?", ["@animation", "@keyframes", "@frames", "@motion"], 1),
            ("Какое основное свойство привязывает анимацию к элементу?", ["animation-name", "transition-name", "keyframe-name", "motion-name"], 0),
            ("Какое свойство задаёт длительность анимации?", ["animation-delay", "animation-duration", "animation-timing", "animation-length"], 1),
            ("Какое CSS-свойство обычно меняется в простом эффекте fade-in?", ["color", "opacity", "font-size", "border"], 1),
            ("Какое значение задаёт бесконечное повторение анимации?", ["animation-iteration-count: infinite", "animation-repeat: always", "animation-loop: true", "animation-count: max"], 0),
            ("Что означают 0% и 100% внутри @keyframes?", ["Цвета", "Начальное и конечное состояния анимации", "Размер элемента", "Скорость загрузки страницы"], 1),
            ("В чём основное различие между transition и animation?", ["Это одно и то же", "transition срабатывает при изменении состояния, animation может работать самостоятельно, автоматически", "animation влияет только на цвет", "transition бесконечно повторяется, animation — нет"], 1),
            ("Что задаёт свойство animation-timing-function?", ["Цвета анимации", "Кривую изменения скорости анимации (например ease, linear)", "Сколько раз повторится анимация", "Задержку начала анимации"], 1),
        ],
    },
    491: {  # Mini-Loyiha 12: CSS Animatsiya — Ilg'or
        "uz": [
            ("Animatsiyani borib-kelib (oldinga-orqaga) ishlatish uchun xususiyat?", ["animation-direction: alternate", "animation-name: reverse", "animation-loop: bounce", "animation-type: toggle"], 0),
            ("Animatsiya tugagandan keyin oxirgi holatni saqlash uchun xususiyat?", ["animation-end: keep", "animation-fill-mode: forwards", "animation-hold: true", "animation-stay: last"], 1),
            ("Animatsiyani vaqtincha to'xtatib turish uchun xususiyat?", ["animation-play-state: paused", "animation-stop: true", "animation-pause: on", "animation-hold: paused"], 0),
            ("Bitta elementga bir nechta animatsiyani bir vaqtda qo'llash mumkinmi?", ["Yo'q, faqat bittasi ishlaydi", "Ha, vergul bilan ajratib ko'rsatib bo'ladi", "Faqat JavaScript orqali mumkin", "Faqat SVG uchun mumkin"], 1),
            ("animation-delay xususiyati nima qiladi?", ["Animatsiya davomiyligini uzaytiradi", "Animatsiyaning boshlanishini kechiktiradi", "Animatsiyani tezlashtiradi", "Animatsiyani takrorlaydi"], 1),
            ("Performance nuqtai nazaridan, animatsiya uchun qaysi xususiyatlar odatda tavsiya etiladi?", ["width va height", "transform va opacity", "margin va padding", "top va left"], 1),
            ("cubic-bezier() funksiyasi nima uchun ishlatiladi?", ["Ranglarni aralashtirish uchun", "Maxsus, o'ziga xos timing (tezlik egri chizig'i) funksiyasini yaratish uchun", "Elementni aylantirish uchun", "Shaffoflikni belgilash uchun"], 1),
            ("will-change CSS xususiyati nima uchun ishlatiladi?", ["Elementning rangini belgilash uchun", "Brauzerga qaysi xususiyat o'zgarishini oldindan bildirib, optimallashtirish uchun", "Animatsiyani butunlay o'chirish uchun", "Elementni ko'rinmas qilish uchun"], 1),
        ],
        "ru": [
            ("Какое свойство заставляет анимацию идти туда-обратно?", ["animation-direction: alternate", "animation-name: reverse", "animation-loop: bounce", "animation-type: toggle"], 0),
            ("Какое свойство сохраняет конечное состояние после завершения анимации?", ["animation-end: keep", "animation-fill-mode: forwards", "animation-hold: true", "animation-stay: last"], 1),
            ("Какое свойство временно приостанавливает анимацию?", ["animation-play-state: paused", "animation-stop: true", "animation-pause: on", "animation-hold: paused"], 0),
            ("Можно ли применить к одному элементу несколько анимаций одновременно?", ["Нет, сработает только одна", "Да, можно перечислить через запятую", "Только через JavaScript", "Только для SVG"], 1),
            ("Что делает свойство animation-delay?", ["Увеличивает длительность анимации", "Задерживает начало анимации", "Ускоряет анимацию", "Повторяет анимацию"], 1),
            ("С точки зрения производительности, какие свойства обычно рекомендуются для анимации?", ["width и height", "transform и opacity", "margin и padding", "top и left"], 1),
            ("Для чего используется функция cubic-bezier()?", ["Для смешивания цветов", "Для создания собственной, особой timing-функции (кривой скорости)", "Для поворота элемента", "Для задания прозрачности"], 1),
            ("Для чего используется CSS-свойство will-change?", ["Чтобы задать цвет элемента", "Чтобы заранее сообщить браузеру, какое свойство изменится, для оптимизации", "Чтобы полностью отключить анимацию", "Чтобы сделать элемент невидимым"], 1),
        ],
    },
    492: {  # Mini-Loyiha 13: Parallax Effekti
        "uz": [
            ("Parallax effekt uchun asosiy CSS xususiyati?", ["background-position: fixed", "background-attachment: fixed", "background-repeat: fixed", "position: parallax"], 1),
            ("background-attachment: fixed berilganda fon rasm scroll paytida qanday tutadi?", ["Kontent bilan birga siljiydi", "O'z joyida qoladi, kontent uning ustidan o'tadi", "Yo'qolib ketadi", "Kattalashadi"], 1),
            ("Parallax effekt odatda qaysi CSS xususiyati bilan birga ishlatiladi?", ["background-size: cover", "font-size: large", "border: none", "color: transparent"], 0),
            ("Parallax uchun ishlatiladigan fon rasm sifat jihatidan qanday bo'lishi kerak?", ["Kichik va past sifatli", "Yetarlicha katta va yuqori sifatli", "Farqi yo'q", "Faqat qora-oq bo'lishi kerak"], 1),
            ("background-position: center xususiyati nima qiladi?", ["Fon rasmni chapga suradi", "Fon rasmni konteyner markaziga joylashtiradi", "Fon rasmni o'chiradi", "Fon rasmni takrorlaydi"], 1),
            ("background-attachment: fixed ba'zi mobil brauzerlarda qanday muammoga duch kelishi mumkin?", ["Hech qanday muammo yo'q", "Ba'zi mobil brauzerlarda to'g'ri ishlamasligi mumkin", "Faqat desktopda ishlamaydi", "Rangni o'zgartirib yuboradi"], 1),
            ("Parallax effektni faqat CSS'siz, JavaScript bilan ham amalga oshirish mumkinmi?", ["Yo'q, faqat CSS bilan mumkin", "Ha, scroll hodisasini (event) kuzatib amalga oshirish mumkin", "Faqat rasm formatiga bog'liq", "Bu tushuncha JavaScript'ga aloqasi yo'q"], 1),
            ("background-repeat: no-repeat xususiyati nima qiladi?", ["Fon rasmni bir necha marta takrorlaydi", "Fon rasmni takrorlamaydi, bir marta ko'rsatadi", "Fon rasmni butunlay yashiradi", "Fon rangini o'zgartiradi"], 1),
        ],
        "ru": [
            ("Какое основное CSS-свойство используется для эффекта parallax?", ["background-position: fixed", "background-attachment: fixed", "background-repeat: fixed", "position: parallax"], 1),
            ("Как ведёт себя фоновое изображение при прокрутке с background-attachment: fixed?", ["Двигается вместе с контентом", "Остаётся на месте, контент проходит поверх него", "Исчезает", "Увеличивается"], 1),
            ("Какое CSS-свойство обычно используется вместе с parallax-эффектом?", ["background-size: cover", "font-size: large", "border: none", "color: transparent"], 0),
            ("Каким по качеству должно быть фоновое изображение для parallax?", ["Маленьким и низкого качества", "Достаточно большим и высокого качества", "Не имеет значения", "Обязательно чёрно-белым"], 1),
            ("Что делает свойство background-position: center?", ["Сдвигает фоновое изображение влево", "Располагает фоновое изображение по центру контейнера", "Убирает фоновое изображение", "Повторяет фоновое изображение"], 1),
            ("С какой проблемой может столкнуться background-attachment: fixed на некоторых мобильных браузерах?", ["Проблем нет", "Может работать некорректно на некоторых мобильных браузерах", "Не работает только на десктопе", "Меняет цвет"], 1),
            ("Можно ли реализовать parallax-эффект и через JavaScript, а не только CSS?", ["Нет, только через CSS", "Да, можно реализовать, отслеживая событие прокрутки", "Зависит только от формата изображения", "Это понятие не связано с JavaScript"], 1),
            ("Что делает свойство background-repeat: no-repeat?", ["Повторяет фоновое изображение несколько раз", "Не повторяет фоновое изображение, показывает один раз", "Полностью скрывает фон", "Меняет цвет фона"], 1),
        ],
    },
}


async def main():
    async with AsyncSessionLocal() as db:
        total_deleted = 0
        total_inserted = 0
        for lesson_id, data in QUESTIONS.items():
            result = await db.execute(
                delete(LessonQuestion).where(LessonQuestion.lesson_id == lesson_id)
            )
            total_deleted += result.rowcount or 0

            for order_index, (text, options, correct) in enumerate(data["uz"]):
                db.add(LessonQuestion(
                    lesson_id=lesson_id, question_text=text, options=options,
                    correct_option=correct, order_index=order_index,
                ))
                total_inserted += 1
            for order_index, (text, options, correct) in enumerate(data["ru"]):
                db.add(LessonQuestion(
                    lesson_id=lesson_id, question_text=text, options=options,
                    correct_option=correct, order_index=order_index,
                ))
                total_inserted += 1

        await db.commit()
        print(f"Deleted {total_deleted} old questions, inserted {total_inserted} new "
              f"({len(QUESTIONS)} lessons x 8 UZ + 8 RU)")


if __name__ == "__main__":
    asyncio.run(main())
