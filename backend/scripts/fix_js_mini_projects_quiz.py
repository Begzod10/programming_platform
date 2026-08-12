"""Replace the team-game quiz question bank for course 49 ("JavaScript
Mini-Projects") — questions were shifted ~1 lesson out of sync with their
actual mini-project content (e.g. lesson "Rang almashtiruvchi" (Color
Switcher) had Todo-list questions), same systemic bug as courses 43 and 50.

Writes UZ+RU dual rows per lesson (order_index 0..7 for each language),
matching the pattern the team-game import endpoint already expects.
"""
from __future__ import annotations
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson_question import LessonQuestion  # noqa: E402

QUESTIONS = {
    467: {  # Mini-Loyiha 1: Kalkulyator
        "uz": [
            ("Foydalanuvchi kiritgan qiymatni olish uchun qaysi DOM usuli ishlatiladi?", ["document.write()", "document.getElementById() / querySelector()", "console.log()", "window.alert()"], 1),
            ("Foydalanuvchi input qiymati odatda qanday turda keladi?", ["Har doim son (number)", "String (matn)", "Boolean", "Obyekt"], 1),
            ("Matn ko'rinishidagi sonni haqiqiy songa aylantirish uchun qaysi funksiya ishlatiladi?", ["toString()", "parseFloat() yoki Number()", "String()", "Boolean()"], 1),
            ("Amal turini (qo'shish, ayirish...) tanlash uchun odatda qaysi struktura ishlatiladi?", ["for sikli", "if/else yoki switch", "while sikli", "try/catch"], 1),
            ("Natijani ekranga chiqarish uchun qaysi DOM xususiyati ko'p ishlatiladi?", ["innerHTML / textContent", "console.error()", "JSON.stringify()", "Array.push()"], 0),
            ("Tugma bosilganda funksiya chaqirish uchun nima kerak?", ["setTimeout()", "addEventListener('click', ...)", "return", "import"], 1),
            ("Nolga bo'lishni (division by zero) tekshirish nima uchun muhim?", ["Kod chiroyliroq ko'rinishi uchun", "Dastur noto'g'ri natija (Infinity/NaN) bermasligi uchun", "Sahifa tezroq yuklanishi uchun", "Ahamiyati yo'q"], 1),
            ("Ikki sonni qo'shuvchi oddiy funksiya odatda nimani qaytaradi?", ["Hech narsa qaytarmaydi", "Ikkala sonning yig'indisini", "Har doim 0", "Matnni"], 1),
        ],
        "ru": [
            ("Какой DOM-метод используется для получения значения, введённого пользователем?", ["document.write()", "document.getElementById() / querySelector()", "console.log()", "window.alert()"], 1),
            ("В каком типе обычно приходит значение из input?", ["Всегда число (number)", "Строка (string)", "Boolean", "Объект"], 1),
            ("Какая функция превращает текстовое число в настоящее число?", ["toString()", "parseFloat() или Number()", "String()", "Boolean()"], 1),
            ("Какая конструкция обычно используется для выбора операции (сложение, вычитание...)?", ["Цикл for", "if/else или switch", "Цикл while", "try/catch"], 1),
            ("Какое DOM-свойство часто используется для вывода результата на экран?", ["innerHTML / textContent", "console.error()", "JSON.stringify()", "Array.push()"], 0),
            ("Что нужно, чтобы вызвать функцию при нажатии кнопки?", ["setTimeout()", "addEventListener('click', ...)", "return", "import"], 1),
            ("Почему важно проверять деление на ноль?", ["Чтобы код выглядел красивее", "Чтобы программа не выдала неверный результат (Infinity/NaN)", "Чтобы страница загружалась быстрее", "Не важно"], 1),
            ("Что обычно возвращает простая функция сложения двух чисел?", ["Ничего не возвращает", "Сумму этих чисел", "Всегда 0", "Текст"], 1),
        ],
    },
    468: {  # Mini-Loyiha 2: Rang almashtiruvchi
        "uz": [
            ("Rang almashtiruvchi loyihasida foydalanuvchi rangni odatda qanday tanlaydi?", ["Faqat konsol orqali", "<input type=\"color\"> yoki tugmalar orqali", "Fayl yuklab", "URL orqali"], 1),
            ("Fon rangini JS orqali o'zgartirish uchun qaysi xususiyat ishlatiladi?", ["style.color", "style.backgroundColor", "style.border", "style.fontSize"], 1),
            ("if/else bu loyihada odatda nima uchun ishlatiladi?", ["Sahifani qayta yuklash uchun", "Tanlangan rangga qarab boshqa-boshqa amal bajarish uchun", "Rasm yuklash uchun", "API chaqirish uchun"], 1),
            ("document.body.style.backgroundColor = \"red\" qatori nima qiladi?", ["Matn rangini qizil qiladi", "Sahifa fonini qizil qiladi", "Tugmani o'chiradi", "Hech narsa qilmaydi"], 1),
            ("Rang qiymatlari odatda qaysi formatda bo'ladi?", ["Faqat so'z bilan (masalan \"qizil\")", "HEX yoki RGB", "Faqat son", "Faqat boolean"], 1),
            ("Tasodifiy rang tanlash uchun qaysi funksiya ishlatilishi mumkin?", ["Date.now()", "Math.random()", "parseInt()", "JSON.parse()"], 1),
            ("Tugma bosilgach rangni almashtirish uchun qaysi event kerak?", ["load", "click", "scroll", "resize"], 1),
            ("Tanlangan rangni \"active\" deb belgilash uchun odatda nima qo'shiladi?", ["Yangi HTML fayl", "CSS klass (masalan \"active\")", "Yangi funksiya nomi", "Yangi o'zgaruvchi turi"], 1),
        ],
        "ru": [
            ("Как пользователь обычно выбирает цвет в проекте переключателя цветов?", ["Только через консоль", "Через <input type=\"color\"> или кнопки", "Загружая файл", "Через URL"], 1),
            ("Какое свойство используется, чтобы менять фон через JS?", ["style.color", "style.backgroundColor", "style.border", "style.fontSize"], 1),
            ("Для чего обычно используется if/else в этом проекте?", ["Чтобы перезагрузить страницу", "Чтобы выполнять разные действия в зависимости от выбранного цвета", "Чтобы загружать изображение", "Чтобы вызывать API"], 1),
            ("Что делает строка document.body.style.backgroundColor = \"red\"?", ["Делает цвет текста красным", "Делает фон страницы красным", "Отключает кнопку", "Ничего не делает"], 1),
            ("В каком формате обычно задаются значения цвета?", ["Только словом (например \"red\")", "HEX или RGB", "Только числом", "Только boolean"], 1),
            ("Какая функция может использоваться для выбора случайного цвета?", ["Date.now()", "Math.random()", "parseInt()", "JSON.parse()"], 1),
            ("Какое событие нужно, чтобы менять цвет по нажатию кнопки?", ["load", "click", "scroll", "resize"], 1),
            ("Что обычно добавляют, чтобы отметить выбранный цвет как \"active\"?", ["Новый HTML-файл", "CSS-класс (например \"active\")", "Новое имя функции", "Новый тип переменной"], 1),
        ],
    },
    469: {  # Mini-Loyiha 3: Ilg'or Kalkulyator
        "uz": [
            ("switch-case qachon if/else'dan qulayroq bo'ladi?", ["Hech qachon", "Bitta qiymatni ko'p variant bilan solishtirishda", "Faqat booleanlar uchun", "Faqat massivlarda"], 1),
            ("switch ichida har bir holat qaysi kalit so'z bilan boshlanadi?", ["if", "case", "when", "match"], 1),
            ("switch'da break yozilmasa nima bo'ladi?", ["Xato chiqadi", "Bajarilish keyingi case'ga ham \"tushib\" ketaveradi", "switch umuman ishlamaydi", "Faqat birinchi case ishlaydi"], 1),
            ("default kalit so'zi switch'da nima uchun kerak?", ["Birinchi case'ni belgilash uchun", "Hech qaysi case mos kelmasa ishga tushadigan holat uchun", "switch'ni to'xtatish uchun", "Kerak emas, ixtiyoriy emas ham"], 1),
            ("Ilg'or kalkulyatorda amal turini tanlashda odatda nima ishlatiladi?", ["for sikli", "switch(amal) { case '+': ... }", "while sikli", "try/catch"], 1),
            ("&& operatori nima uchun ishlatiladi?", ["Kamida bitta shart TRUE bo'lishi kifoya bo'lganda", "Ikkala shart ham TRUE bo'lishi kerak bo'lganda", "Shartni inkor qilish uchun", "Massiv elementlarini solishtirish uchun"], 1),
            ("|| operatori nima uchun ishlatiladi?", ["Ikkala shart ham TRUE bo'lishi kerak bo'lganda", "Kamida bitta shart TRUE bo'lishi kifoya bo'lganda", "Faqat sonlar uchun", "Faqat matnlar uchun"], 1),
            ("! operatori nima qiladi?", ["Qo'shish amalini bajaradi", "Qiymatni mantiqiy jihatdan teskarisiga aylantiradi", "Massivni saralaydi", "Sonni songa aylantiradi"], 1),
        ],
        "ru": [
            ("Когда switch-case удобнее, чем if/else?", ["Никогда", "Когда одно значение сравнивается со многими вариантами", "Только для boolean", "Только для массивов"], 1),
            ("С какого ключевого слова начинается каждый вариант внутри switch?", ["if", "case", "when", "match"], 1),
            ("Что произойдёт, если не написать break в switch?", ["Возникнет ошибка", "Выполнение \"провалится\" и в следующий case", "switch вообще не сработает", "Сработает только первый case"], 1),
            ("Зачем в switch нужно ключевое слово default?", ["Чтобы отметить первый case", "Для случая, когда ни один case не подошёл", "Чтобы остановить switch", "Не нужно, оно необязательно"], 1),
            ("Что обычно используется в продвинутом калькуляторе для выбора операции?", ["Цикл for", "switch(amal) { case '+': ... }", "Цикл while", "try/catch"], 1),
            ("Для чего используется оператор &&?", ["Когда достаточно, чтобы хотя бы одно условие было TRUE", "Когда оба условия должны быть TRUE", "Чтобы инвертировать условие", "Чтобы сравнивать элементы массива"], 1),
            ("Для чего используется оператор ||?", ["Когда оба условия должны быть TRUE", "Когда достаточно, чтобы хотя бы одно условие было TRUE", "Только для чисел", "Только для строк"], 1),
            ("Что делает оператор !?", ["Выполняет сложение", "Логически инвертирует значение", "Сортирует массив", "Превращает число в число"], 1),
        ],
    },
    470: {  # Mini-Loyiha 4: Sahifalash (Pagination)
        "uz": [
            ("Pagination (sahifalash) nima uchun ishlatiladi?", ["Ma'lumotni o'chirish uchun", "Ko'p ma'lumotni kichik qismlarga bo'lib ko'rsatish uchun", "Ma'lumotni saralash uchun", "Formani validatsiya qilish uchun"], 1),
            ("for sikli odatda qanday holatlarda qulay?", ["Necha marta ishlashi noma'lum bo'lganda", "Necha marta ishga tushishi oldindan ma'lum bo'lganda", "Faqat bir marta ishlatilganda", "Hech qachon"], 1),
            ("while sikli qachon ko'proq mos keladi?", ["Tsikl necha marta ishlashi oldindan aniq bo'lmasa", "Har doim, for o'rniga", "Faqat massivlar uchun", "Faqat obyektlar uchun"], 1),
            ("Ma'lumotlarni sahifalarga bo'lishda odatda nima hisoblanadi?", ["Faqat umumiy elementlar soni", "Har bir sahifadagi elementlar soni (itemsPerPage)", "Faqat rang", "Faqat shrift"], 1),
            ("Joriy sahifa raqami odatda qanday saqlanadi?", ["Har doim URL'da", "O'zgaruvchida (masalan currentPage)", "Faqat CSS'da", "Umuman saqlanmaydi"], 1),
            ("for sikli sintaksisi nechta asosiy qismdan iborat?", ["1 ta", "3 ta (boshlang'ich, shart, qadam)", "5 ta", "2 ta"], 1),
            ("Cheksiz sikl (infinite loop) qachon yuzaga keladi?", ["Sikl ichida o'zgaruvchi bo'lmasa", "To'xtash sharti hech qachon bajarilmasa", "break yozilsa", "Massiv bo'sh bo'lsa"], 1),
            ("Sahifa tugmalarini (1, 2, 3...) dinamik yaratish uchun odatda qaysi sikl qulay?", ["while", "for", "do-while", "Sikl kerak emas"], 1),
        ],
        "ru": [
            ("Для чего используется pagination (пагинация)?", ["Чтобы удалить данные", "Чтобы показывать большой объём данных небольшими частями", "Чтобы сортировать данные", "Чтобы валидировать форму"], 1),
            ("В каких случаях удобен цикл for?", ["Когда неизвестно, сколько раз он выполнится", "Когда заранее известно количество повторений", "Только при однократном использовании", "Никогда"], 1),
            ("Когда цикл while подходит лучше?", ["Когда заранее неизвестно, сколько раз выполнится цикл", "Всегда, вместо for", "Только для массивов", "Только для объектов"], 1),
            ("Что обычно вычисляется при разбиении данных на страницы?", ["Только общее число элементов", "Число элементов на одной странице (itemsPerPage)", "Только цвет", "Только шрифт"], 1),
            ("Как обычно хранится номер текущей страницы?", ["Всегда в URL", "В переменной (например currentPage)", "Только в CSS", "Вообще не хранится"], 1),
            ("Из скольких основных частей состоит синтаксис цикла for?", ["Из 1", "Из 3 (начало, условие, шаг)", "Из 5", "Из 2"], 1),
            ("Когда возникает бесконечный цикл (infinite loop)?", ["Когда в цикле нет переменной", "Когда условие остановки никогда не выполняется", "Когда написан break", "Когда массив пуст"], 1),
            ("Какой цикл обычно удобен для динамического создания кнопок страниц (1, 2, 3...)?", ["while", "for", "do-while", "Цикл не нужен"], 1),
        ],
    },
    471: {  # Mini-Loyiha 5: Todo Ro'yxat
        "uz": [
            ("Todo elementlarini saqlash uchun odatda qaysi ma'lumot tuzilmasi ishlatiladi?", ["Bitta o'zgaruvchi", "Massiv (array)", "Boolean", "Funksiya"], 1),
            ("Yangi todo qo'shish uchun qaysi massiv metodi ishlatiladi?", ["pop()", "push()", "shift()", "slice()"], 1),
            ("Todo'ni ro'yxatdan o'chirish uchun ko'p ishlatiladigan massiv metodi?", ["push()", "filter() yoki splice()", "join()", "concat()"], 1),
            ("CRUD nimalarning qisqartmasi?", ["Create, Read, Update, Delete", "Copy, Run, Undo, Delay", "Check, Render, Use, Draw", "Create, Render, Update, Display"], 0),
            ("Todo'ni \"bajarildi\" deb belgilash odatda qanday amalga oshiriladi?", ["Todo'ni butunlay o'chirib", "Obyekt xususiyatini (masalan bajarildi: true) o'zgartirib", "Sahifani qayta yuklab", "Yangi massiv yaratib"], 1),
            ("Ro'yxatni ekranga chiqarish uchun massiv odatda qanday aylanib chiqiladi?", ["for...in bilan", "forEach() yoki map() bilan", "JSON.stringify() bilan", "typeof bilan"], 1),
            ("Checkbox bosilganda todo holatini o'zgartirish uchun qaysi event kerak?", ["load", "change yoki click", "scroll", "resize"], 1),
            ("Todo ro'yxatini sahifa yopilsa ham saqlab qolish uchun odatda nima ishlatiladi?", ["sessionStorage har doim", "localStorage", "Faqat o'zgaruvchi", "console.log"], 1),
        ],
        "ru": [
            ("Какая структура данных обычно используется для хранения задач todo?", ["Одна переменная", "Массив (array)", "Boolean", "Функция"], 1),
            ("Какой метод массива используется для добавления новой задачи?", ["pop()", "push()", "shift()", "slice()"], 1),
            ("Какой метод массива часто используется для удаления задачи из списка?", ["push()", "filter() или splice()", "join()", "concat()"], 1),
            ("Что означает аббревиатура CRUD?", ["Create, Read, Update, Delete", "Copy, Run, Undo, Delay", "Check, Render, Use, Draw", "Create, Render, Update, Display"], 0),
            ("Как обычно отмечают задачу как \"выполненную\"?", ["Полностью удаляя её", "Изменяя свойство объекта (например bajarildi: true)", "Перезагружая страницу", "Создавая новый массив"], 1),
            ("Как обычно перебирают массив для вывода списка на экран?", ["Через for...in", "Через forEach() или map()", "Через JSON.stringify()", "Через typeof"], 1),
            ("Какое событие нужно для изменения статуса задачи по нажатию чекбокса?", ["load", "change или click", "scroll", "resize"], 1),
            ("Что обычно используется, чтобы список задач сохранялся даже после закрытия страницы?", ["Всегда sessionStorage", "localStorage", "Только переменная", "console.log"], 1),
        ],
    },
    472: {  # Mini-Loyiha 6: Hisobchilik Ilovasi
        "uz": [
            ("Funksiyalarni alohida yozishning asosiy afzalligi nima?", ["Kod uzunroq bo'ladi", "Kodni qayta ishlatish va tartibli qilish imkonini beradi", "Sahifa tezroq yuklanadi", "Hech qanday afzalligi yo'q"], 1),
            ("Funksiya e'lon qilishning asosiy sintaksisi qaysi?", ["let nomi = { ... }", "function nomi(parametrlar) { ... }", "class nomi { ... }", "import nomi from ..."], 1),
            ("Funksiya natijani qanday qaytaradi?", ["console.log() bilan", "return kalit so'zi bilan", "print() bilan", "yield bilan"], 1),
            ("Funksiya parametri va argument orasidagi farq nima?", ["Farqi yo'q", "Parametr — e'londagi o'zgaruvchi, argument — chaqirilganda beriladigan qiymat", "Argument faqat sonlar uchun", "Parametr faqat matnlar uchun"], 1),
            ("Bir funksiya ichidan boshqa funksiyani chaqirish mumkinmi?", ["Yo'q, taqiqlangan", "Ha, mumkin", "Faqat bitta marta", "Faqat arrow function bo'lsa"], 1),
            ("Hisobchilik ilovasida daromad va xarajatni hisoblash uchun odatda nima yaratiladi?", ["Yangi HTML fayl", "Alohida funksiyalar (masalan hisoblaJami())", "Faqat CSS klass", "Faqat massiv"], 1),
            ("Funksiya hech narsa qaytarmasa (return yozilmasa), natija qanday bo'ladi?", ["0", "undefined", "null", "Xato chiqadi"], 1),
            ("Arrow function oddiy function'dan sintaksis jihatidan qanday farq qiladi?", ["Umuman farq yo'q", "Qisqaroq yoziladi, function kalit so'zisiz", "Faqat obyektlarda ishlaydi", "Faqat async bo'ladi"], 1),
        ],
        "ru": [
            ("В чём главное преимущество написания отдельных функций?", ["Код становится длиннее", "Позволяет переиспользовать код и делать его более организованным", "Страница загружается быстрее", "Никакого преимущества нет"], 1),
            ("Какой основной синтаксис объявления функции?", ["let nomi = { ... }", "function nomi(parametrlar) { ... }", "class nomi { ... }", "import nomi from ..."], 1),
            ("Как функция возвращает результат?", ["Через console.log()", "Через ключевое слово return", "Через print()", "Через yield"], 1),
            ("В чём разница между параметром и аргументом функции?", ["Разницы нет", "Параметр — переменная в объявлении, аргумент — значение при вызове", "Аргумент только для чисел", "Параметр только для строк"], 1),
            ("Можно ли вызвать одну функцию из другой функции?", ["Нет, запрещено", "Да, можно", "Только один раз", "Только если это arrow function"], 1),
            ("Что обычно создаётся для подсчёта доходов и расходов в бухгалтерском приложении?", ["Новый HTML-файл", "Отдельные функции (например hisoblaJami())", "Только CSS-класс", "Только массив"], 1),
            ("Каким будет результат, если функция ничего не возвращает (нет return)?", ["0", "undefined", "null", "Возникнет ошибка"], 1),
            ("Чем стрелочная функция (arrow function) отличается синтаксически от обычной?", ["Вообще ничем не отличается", "Пишется короче, без ключевого слова function", "Работает только с объектами", "Всегда является async"], 1),
        ],
    },
    473: {  # Mini-Loyiha 7: Filmlar Ilovasi
        "uz": [
            ("Har bir filmni ifodalash uchun odatda qaysi tuzilma ishlatiladi?", ["Oddiy o'zgaruvchi", "Obyekt (object)", "Boolean", "Funksiya"], 1),
            ("Filmning nomi, yili kabi xususiyatlariga qanday murojaat qilinadi?", ["obyekt[funksiya]", "obyekt.xususiyat (dot notation)", "obyekt->xususiyat", "obyekt::xususiyat"], 1),
            ("Bir nechta filmni saqlash uchun odatda nima ishlatiladi?", ["Bitta katta string", "Obyektlar massivi", "Bitta boolean", "Bitta funksiya"], 1),
            ("Obyektlar massivini muayyan shartga ko'ra filtrlash uchun qaysi metod ishlatiladi?", ["map()", "filter()", "join()", "sort() faqat"], 1),
            ("Obyektlar massividan yangi massiv yasash (masalan faqat nomlarini olish) uchun qaysi metod ishlatiladi?", ["filter()", "map()", "reduce() faqat", "concat()"], 1),
            ("Film qidiruv funksiyasi odatda qaysi metod(lar) bilan amalga oshiriladi?", ["push() bilan", "filter() yoki find() bilan", "pop() bilan", "delete bilan"], 1),
            ("Obyekt ichidagi xususiyatni yangilash qanday amalga oshiriladi?", ["obyekt.xususiyat = yangiQiymat", "delete obyekt", "obyekt.push(qiymat)", "Object.freeze(obyekt)"], 0),
            ("JSON.stringify() nima uchun ishlatiladi?", ["Matnni songa aylantirish uchun", "Obyekt/massivni matn (JSON) ko'rinishiga aylantirish uchun", "Massivni saralash uchun", "Elementni DOM'dan o'chirish uchun"], 1),
        ],
        "ru": [
            ("Какая структура обычно используется для представления одного фильма?", ["Обычная переменная", "Объект (object)", "Boolean", "Функция"], 1),
            ("Как обращаются к свойствам фильма вроде названия, года?", ["obyekt[funksiya]", "obyekt.xususiyat (через точку)", "obyekt->xususiyat", "obyekt::xususiyat"], 1),
            ("Что обычно используется для хранения нескольких фильмов?", ["Одна большая строка", "Массив объектов", "Один boolean", "Одна функция"], 1),
            ("Какой метод используется для фильтрации массива объектов по условию?", ["map()", "filter()", "join()", "только sort()"], 1),
            ("Какой метод используется, чтобы создать новый массив из массива объектов (например только названий)?", ["filter()", "map()", "только reduce()", "concat()"], 1),
            ("С помощью каких методов обычно реализуется поиск фильма?", ["С push()", "С filter() или find()", "С pop()", "С delete"], 1),
            ("Как обновляется свойство внутри объекта?", ["obyekt.xususiyat = yangiQiymat", "delete obyekt", "obyekt.push(qiymat)", "Object.freeze(obyekt)"], 0),
            ("Для чего используется JSON.stringify()?", ["Чтобы превратить текст в число", "Чтобы превратить объект/массив в текст (JSON)", "Чтобы отсортировать массив", "Чтобы удалить элемент из DOM"], 1),
        ],
    },
    474: {  # Mini-Loyiha 8: Overlay Effektlar
        "uz": [
            ("Overlay effekt odatda nima uchun ishlatiladi?", ["Sahifani tezlashtirish uchun", "Rasm/kontent ustiga qo'shimcha ma'lumot yoki effekt ko'rsatish uchun", "Ma'lumotlar bazasiga ulanish uchun", "Formani yuborish uchun"], 1),
            ("Overlay'ni ko'rsatish/yashirish uchun odatda nima o'zgartiriladi?", ["Fayl nomi", "CSS klass yoki style (masalan display/opacity)", "Domen nomi", "Brauzer sozlamalari"], 1),
            ("classList.add() va classList.remove() nima uchun ishlatiladi?", ["Elementni butunlay o'chirish uchun", "Elementga CSS klass qo'shish/olib tashlash uchun", "Yangi element yaratish uchun", "Massivni saralash uchun"], 1),
            ("classList.toggle() nima qiladi?", ["Klassni doim qo'shadi", "Klass mavjud bo'lsa olib tashlaydi, yo'q bo'lsa qo'shadi", "Elementni o'chiradi", "Sahifani qayta yuklaydi"], 1),
            ("Sichqoncha elementga kirganda (hover) overlay ko'rsatish uchun JS orqali qaysi event ko'p ishlatiladi?", ["load", "mouseenter / mouseover", "submit", "resize"], 1),
            ("Overlay galereya loyihasida odatda nechta rasm elementi bilan ishlanadi?", ["Faqat bitta", "Bir nechtasi (ro'yxat)", "Hech biri", "Faqat ikkitasi, ko'proq bo'lmaydi"], 1),
            ("Overlay yopish tugmasi (X) bosilganda odatda nima sodir bo'ladi?", ["Sahifa yopiladi", "Overlay yashiriladi", "Yangi overlay ochiladi", "Hech narsa"], 1),
            ("DOM elementini dinamik (JS orqali) yaratish uchun qaysi metod ishlatiladi?", ["document.querySelector()", "document.createElement()", "document.getElementById()", "document.write()"], 1),
        ],
        "ru": [
            ("Для чего обычно используется эффект overlay?", ["Чтобы ускорить страницу", "Чтобы показать дополнительную информацию или эффект поверх изображения/контента", "Чтобы подключиться к базе данных", "Чтобы отправить форму"], 1),
            ("Что обычно меняется, чтобы показать/скрыть overlay?", ["Имя файла", "CSS-класс или style (например display/opacity)", "Имя домена", "Настройки браузера"], 1),
            ("Для чего используются classList.add() и classList.remove()?", ["Чтобы полностью удалить элемент", "Чтобы добавить/убрать CSS-класс у элемента", "Чтобы создать новый элемент", "Чтобы отсортировать массив"], 1),
            ("Что делает classList.toggle()?", ["Всегда добавляет класс", "Убирает класс, если он есть, и добавляет, если его нет", "Удаляет элемент", "Перезагружает страницу"], 1),
            ("Какое событие через JS чаще используют для показа overlay при наведении (hover)?", ["load", "mouseenter / mouseover", "submit", "resize"], 1),
            ("Со сколькими элементами изображений обычно работает проект overlay-галереи?", ["Только с одним", "С несколькими (список)", "Ни с одним", "Только с двумя, не больше"], 1),
            ("Что обычно происходит при нажатии кнопки закрытия overlay (X)?", ["Страница закрывается", "Overlay скрывается", "Открывается новый overlay", "Ничего"], 1),
            ("Какой метод используется для динамического (через JS) создания DOM-элемента?", ["document.querySelector()", "document.createElement()", "document.getElementById()", "document.write()"], 1),
        ],
    },
    475: {  # Mini-Loyiha 9: CRUD Jadval
        "uz": [
            ("CRUD jadvaliga yangi qator qo'shish uchun odatda qaysi DOM metodi ishlatiladi?", ["remove()", "appendChild() yoki insertAdjacentHTML()", "querySelector()", "JSON.parse()"], 1),
            ("Jadval qatorini o'chirish uchun qaysi metod ishlatiladi?", ["appendChild()", "remove() yoki removeChild()", "push()", "createElement()"], 1),
            ("Qatorni tahrirlash (edit) uchun odatda nima qilinadi?", ["Butun jadval o'chiriladi", "Mavjud qiymatlar inputga qo'yilib, so'ng yangilanadi", "Sahifa qayta yuklanadi", "Hech narsa qilinmaydi"], 1),
            ("Dinamik yaratilgan elementlarga event qo'shish uchun tavsiya etiladigan usul?", ["Har bir elementga alohida listener", "Event delegation (ota-elementga bitta listener)", "setInterval", "Hech qanday usul kerak emas"], 1),
            ("Admin panelning asosiy patterni nimadan iborat?", ["Faqat ko'rsatish", "Ma'lumotlarni qo'shish, o'zgartirish, o'chirish (CRUD)", "Faqat login qilish", "Faqat CSS animatsiya"], 1),
            ("Har bir jadval qatoriga unikal identifikator (id) berish nima uchun muhim?", ["Muhim emas", "Aynan qaysi qatorni tahrirlash/o'chirishni bilish uchun", "Faqat dizayn uchun", "SEO uchun"], 1),
            ("document.createElement('tr') nima yaratadi?", ["Yangi ustun (th)", "Yangi jadval qatori (tr elementi)", "Yangi jadval (table)", "Yangi rasm"], 1),
            ("Jadvaldagi ma'lumotlarni sahifa yopilgandan keyin ham saqlab qolish uchun odatda nima ishlatiladi?", ["Faqat state", "Massiv/obyekt + localStorage", "Faqat CSS", "Hech narsa kerak emas"], 1),
        ],
        "ru": [
            ("Какой DOM-метод обычно используется для добавления новой строки в CRUD-таблицу?", ["remove()", "appendChild() или insertAdjacentHTML()", "querySelector()", "JSON.parse()"], 1),
            ("Какой метод используется для удаления строки таблицы?", ["appendChild()", "remove() или removeChild()", "push()", "createElement()"], 1),
            ("Что обычно делают для редактирования строки?", ["Удаляют всю таблицу", "Помещают текущие значения в input, затем обновляют их", "Перезагружают страницу", "Ничего не делают"], 1),
            ("Какой подход рекомендуется для добавления событий динамически созданным элементам?", ["Отдельный listener на каждый элемент", "Делегирование событий (один listener на родителе)", "setInterval", "Никакой подход не нужен"], 1),
            ("В чём заключается основной паттерн админ-панели?", ["Только отображение", "Добавление, изменение, удаление данных (CRUD)", "Только вход в систему", "Только CSS-анимация"], 1),
            ("Почему важно давать каждой строке таблицы уникальный идентификатор (id)?", ["Не важно", "Чтобы точно знать, какую строку редактировать/удалять", "Только для дизайна", "Для SEO"], 1),
            ("Что создаёт document.createElement('tr')?", ["Новый столбец (th)", "Новую строку таблицы (элемент tr)", "Новую таблицу (table)", "Новое изображение"], 1),
            ("Что обычно используется, чтобы данные таблицы сохранялись даже после закрытия страницы?", ["Только state", "Массив/объект + localStorage", "Только CSS", "Ничего не нужно"], 1),
        ],
    },
    476: {  # Mini-Loyiha 10: Pizza Buyurtma Ilovasi
        "uz": [
            ("Savatcha (shopping cart) ma'lumotlarini saqlash uchun odatda nima ishlatiladi?", ["console.log", "localStorage", "CSS", "HTML atributi"], 1),
            ("localStorage'ga ma'lumot yozish uchun qaysi metod ishlatiladi?", ["localStorage.getItem()", "localStorage.setItem()", "localStorage.write()", "localStorage.push()"], 1),
            ("localStorage'dan ma'lumot o'qish uchun qaysi metod ishlatiladi?", ["localStorage.setItem()", "localStorage.getItem()", "localStorage.read()", "localStorage.fetch()"], 1),
            ("localStorage faqat qanday turdagi ma'lumotni to'g'ridan-to'g'ri saqlaydi?", ["Obyekt", "String (matn)", "Massiv", "Funksiya"], 1),
            ("Obyekt/massivni localStorage'ga saqlashdan oldin nima qilish kerak?", ["Hech narsa, to'g'ridan-to'g'ri saqlansa bo'ladi", "JSON.stringify() bilan matnga aylantirish", "parseInt() qilish", "Boolean() qilish"], 1),
            ("localStorage'dan olingan matnni qayta obyekt/massivga aylantirish uchun qaysi funksiya ishlatiladi?", ["JSON.stringify()", "JSON.parse()", "String()", "Number()"], 1),
            ("Savatchadagi mahsulotlarning umumiy narxini hisoblash uchun odatda qaysi massiv metodi qulay?", ["map()", "reduce()", "filter() faqat", "join()"], 1),
            ("Sahifa yopilib qayta ochilganda savatcha saqlanib qolishi uchun nima muhim?", ["Hech narsa qilish shart emas", "localStorage'dan ma'lumotni sahifa yuklanganda qayta o'qish", "Faqat CSS", "Faqat HTML"], 1),
        ],
        "ru": [
            ("Что обычно используется для хранения данных корзины покупок?", ["console.log", "localStorage", "CSS", "HTML-атрибут"], 1),
            ("Какой метод используется для записи данных в localStorage?", ["localStorage.getItem()", "localStorage.setItem()", "localStorage.write()", "localStorage.push()"], 1),
            ("Какой метод используется для чтения данных из localStorage?", ["localStorage.setItem()", "localStorage.getItem()", "localStorage.read()", "localStorage.fetch()"], 1),
            ("Какой тип данных localStorage хранит напрямую?", ["Объект", "Строку (string)", "Массив", "Функцию"], 1),
            ("Что нужно сделать перед сохранением объекта/массива в localStorage?", ["Ничего, можно сохранить напрямую", "Превратить в строку через JSON.stringify()", "Выполнить parseInt()", "Выполнить Boolean()"], 1),
            ("Какая функция превращает строку из localStorage обратно в объект/массив?", ["JSON.stringify()", "JSON.parse()", "String()", "Number()"], 1),
            ("Какой метод массива удобен для подсчёта общей стоимости товаров в корзине?", ["map()", "reduce()", "только filter()", "join()"], 1),
            ("Что важно, чтобы корзина сохранялась после закрытия и повторного открытия страницы?", ["Ничего делать не нужно", "Заново читать данные из localStorage при загрузке страницы", "Только CSS", "Только HTML"], 1),
        ],
    },
    477: {  # Mini-Loyiha 11: Karusel (Slider)
        "uz": [
            ("Karusel rasmlarini avtomatik almashtirish uchun odatda qaysi funksiya ishlatiladi?", ["setTimeout() faqat", "setInterval()", "addEventListener()", "fetch()"], 1),
            ("setInterval() ikkinchi argumenti nimani bildiradi?", ["Rasm soni", "Har chaqiriq orasidagi vaqt (millisekundlarda)", "Rang kodi", "Massiv uzunligi"], 1),
            ("setInterval'ni to'xtatish uchun qaysi funksiya ishlatiladi?", ["stopInterval()", "clearInterval()", "endInterval()", "cancelInterval()"], 1),
            ("Joriy slayd indeksini oshirishda oxiridan boshiga qaytish uchun odatda qaysi amal ishlatiladi?", ["index = index - 1", "index = (index + 1) % rasmlar.length", "index = 0 doim", "index = rasmlar.length"], 1),
            ("Foizli qoldiq (%) operatori karuselda nima uchun ishlatiladi?", ["Narxni hisoblash uchun", "Oxirgi slayddan keyin birinchisiga qaytish uchun", "Ranglarni aralashtirish uchun", "Vaqtni hisoblash uchun"], 1),
            ("\"Oldingi\"/\"Keyingi\" tugmalari odatda nimani o'zgartiradi?", ["Sahifa ranggini", "Joriy slayd indeksini", "Brauzer nomini", "Fayl hajmini"], 1),
            ("Slayd nuqtalarini (indicator dots) dinamik yaratish uchun qaysi massiv metodi qulay?", ["reduce() faqat", "map() yoki forEach()", "sort()", "concat()"], 1),
            ("Sichqoncha karusel ustida turganda avtomatik almashishni to'xtatish odatiy amaliyotmi?", ["Yo'q, hech qachon qilinmaydi", "Ha, foydalanuvchi tajribasi uchun tavsiya etiladi", "Faqat mobil qurilmada", "Faqat rasm yo'q bo'lsa"], 1),
        ],
        "ru": [
            ("Какая функция обычно используется для автоматической смены слайдов карусели?", ["Только setTimeout()", "setInterval()", "addEventListener()", "fetch()"], 1),
            ("Что означает второй аргумент setInterval()?", ["Количество изображений", "Время между вызовами (в миллисекундах)", "Код цвета", "Длину массива"], 1),
            ("Какая функция используется для остановки setInterval?", ["stopInterval()", "clearInterval()", "endInterval()", "cancelInterval()"], 1),
            ("Какое действие обычно используется, чтобы после последнего слайда вернуться к первому?", ["index = index - 1", "index = (index + 1) % rasmlar.length", "index = 0 всегда", "index = rasmlar.length"], 1),
            ("Для чего в карусели используется оператор остатка от деления (%)?", ["Для расчёта цены", "Чтобы после последнего слайда вернуться к первому", "Для смешивания цветов", "Для расчёта времени"], 1),
            ("Что обычно изменяют кнопки \"Назад\"/\"Вперёд\"?", ["Цвет страницы", "Индекс текущего слайда", "Имя браузера", "Размер файла"], 1),
            ("Какой метод массива удобен для динамического создания точек-индикаторов слайдов?", ["Только reduce()", "map() или forEach()", "sort()", "concat()"], 1),
            ("Является ли остановка автопрокрутки при наведении мыши на карусель обычной практикой?", ["Нет, так никогда не делают", "Да, это рекомендуется для удобства пользователя", "Только на мобильных устройствах", "Только если нет изображений"], 1),
        ],
    },
    478: {  # Mini-Loyiha 12: Musiqa Pleyer
        "uz": [
            ("HTML5'da audio faylni ijro etish uchun qaysi teg ishlatiladi?", ["<sound>", "<audio>", "<media>", "<play>"], 1),
            ("Audio elementini JS orqali ijro etish uchun qaysi metod ishlatiladi?", ["start()", "play()", "run()", "begin()"], 1),
            ("Audio'ni to'xtatish/pauza qilish uchun qaysi metod ishlatiladi?", ["stop()", "pause()", "end()", "halt()"], 1),
            ("Audio elementining joriy ijro vaqtini bildiruvchi xususiyat?", ["duration", "currentTime", "volume", "playbackRate"], 1),
            ("Audio faylning umumiy davomiyligini bildiruvchi xususiyat?", ["currentTime", "duration", "length", "time"], 1),
            ("Qo'shiq tugaganda avtomatik keyingisiga o'tish uchun qaysi event ishlatiladi?", ["load", "ended", "click", "pause"], 1),
            ("Ovoz balandligini boshqarish uchun qaysi xususiyat ishlatiladi?", ["speed", "volume", "loudness", "sound"], 1),
            ("Bitta Play/Pause tugmasi holatga qarab ishlashi uchun odatda nima kuzatib boriladi?", ["Faqat CSS klass", "State (masalan isPlaying)", "Fayl nomi", "Brauzer versiyasi"], 1),
        ],
        "ru": [
            ("Какой тег HTML5 используется для воспроизведения аудиофайла?", ["<sound>", "<audio>", "<media>", "<play>"], 1),
            ("Какой метод используется для воспроизведения аудио через JS?", ["start()", "play()", "run()", "begin()"], 1),
            ("Какой метод используется для остановки/паузы аудио?", ["stop()", "pause()", "end()", "halt()"], 1),
            ("Какое свойство показывает текущее время воспроизведения аудио?", ["duration", "currentTime", "volume", "playbackRate"], 1),
            ("Какое свойство показывает общую длительность аудиофайла?", ["currentTime", "duration", "length", "time"], 1),
            ("Какое событие используется для автоматического перехода к следующей песне после окончания текущей?", ["load", "ended", "click", "pause"], 1),
            ("Какое свойство используется для управления громкостью?", ["speed", "volume", "loudness", "sound"], 1),
            ("Что обычно отслеживается, чтобы одна кнопка Play/Pause работала в зависимости от состояния?", ["Только CSS-класс", "State (например isPlaying)", "Имя файла", "Версия браузера"], 1),
        ],
    },
    479: {  # Mini-Loyiha 13: Admin Dashboard
        "uz": [
            ("Bu capstone loyihasi nima uchun mo'ljallangan?", ["Faqat CSS o'rganish uchun", "Kurs davomida o'rganilgan barcha JS bilimlarini birlashtirish uchun", "Faqat login qilish uchun", "Faqat rasm yuklash uchun"], 1),
            ("Admin Dashboard loyihasini portfolio'ga qo'shish nima uchun foydali?", ["Foydasi yo'q", "Real ko'nikmalarni ish beruvchilarga ko'rsatish uchun", "Faqat baho olish uchun", "Faqat safe uchun"], 1),
            ("Capstone loyihada odatda qaysi avvalgi mini-loyihalar ko'nikmalari ishlatiladi?", ["Faqat birinchi loyihaniki", "DOM, massivlar, obyektlar, localStorage va boshqalar — barchasi", "Hech qaysi", "Faqat CSS ko'nikmalari"], 1),
            ("Loyihani GitHub Pages orqali joylashtirish (deploy) nima uchun foydali?", ["Kodni o'chirish uchun", "Loyihani onlayn, boshqalarga ko'rsatish uchun", "Faqat backup uchun", "Foydasi yo'q"], 1),
            ("Responsive dizayn capstone loyihada nima uchun muhim?", ["Muhim emas", "Loyiha turli ekranlarda to'g'ri ko'rinishi uchun", "Faqat mobil uchun kerak, boshqa hech narsaga", "Faqat rangni belgilash uchun"], 1),
            ("Kodni tartibli va o'qilishi oson qilish nima uchun muhim?", ["Ahamiyati yo'q", "Boshqalar (yoki kelajakda o'zingiz) tushunishi uchun", "Faqat baholash uchun", "Faqat tezlik uchun"], 1),
            ("README fayli loyihada nima uchun yoziladi?", ["Kodni yashirish uchun", "Loyiha haqida va uni qanday ishga tushirish haqida ma'lumot berish uchun", "Faqat litsenziya uchun", "Hech qanday sabab yo'q"], 1),
            ("Capstone loyihani tugatgandan keyin odatda keyingi qadam nima bo'ladi?", ["Dasturlashni to'xtatish", "Yangi, murakkabroq mavzular yoki freymvorklarni o'rganish", "Faqat dam olish", "Loyihani o'chirib tashlash"], 1),
        ],
        "ru": [
            ("Для чего предназначен этот capstone-проект?", ["Только для изучения CSS", "Чтобы объединить все знания JS, полученные за курс", "Только для входа в систему", "Только для загрузки изображений"], 1),
            ("Зачем полезно добавить проект Admin Dashboard в портфолио?", ["Пользы нет", "Чтобы показать реальные навыки работодателям", "Только чтобы получить оценку", "Только для сохранности"], 1),
            ("Навыки каких предыдущих мини-проектов обычно используются в capstone-проекте?", ["Только из первого проекта", "DOM, массивы, объекты, localStorage и другие — всё вместе", "Ни одного", "Только навыки CSS"], 1),
            ("Зачем полезно развернуть (deploy) проект через GitHub Pages?", ["Чтобы удалить код", "Чтобы показать проект онлайн другим людям", "Только для резервной копии", "Пользы нет"], 1),
            ("Почему важен адаптивный (responsive) дизайн в capstone-проекте?", ["Не важен", "Чтобы проект корректно отображался на разных экранах", "Нужен только для мобильных, больше ни для чего", "Только чтобы задать цвет"], 1),
            ("Почему важно делать код аккуратным и легко читаемым?", ["Неважно", "Чтобы другие (или вы сами в будущем) могли его понять", "Только для оценки", "Только для скорости"], 1),
            ("Зачем в проекте пишется файл README?", ["Чтобы скрыть код", "Чтобы дать информацию о проекте и о том, как его запустить", "Только для лицензии", "Без особой причины"], 1),
            ("Что обычно является следующим шагом после завершения capstone-проекта?", ["Перестать программировать", "Изучение новых, более сложных тем или фреймворков", "Только отдых", "Удаление проекта"], 1),
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
