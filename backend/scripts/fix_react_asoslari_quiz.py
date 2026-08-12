"""Replace the team-game quiz question bank for course 43 ("React Asoslari")
— all 14 lessons' questions were shifted ~2 lessons out of sync with their
actual content (e.g. lesson 2 "Props va kompozitsiya" had useState/useEffect
questions that belonged to later lessons), same systemic bug as course 50.

Writes UZ+RU dual rows per lesson (order_index 0..7 for each language),
matching the pattern the team-game import endpoint already expects
(import_questions_from_lesson's _detect_lang() Cyrillic-based pairing).
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
    383: {  # 1-Vite + birinchi komponent (JSX)
        "uz": [
            ("React nima?", ["Ma'lumotlar bazasi", "UI yasash uchun kutubxona", "Server tili", "CSS freymvork"], 1),
            ("JSX nima?", ["Alohida dasturlash tili", "JavaScript ichida HTML'ga o'xshash sintaksis", "CSS preprocessori", "Ma'lumotlar formati"], 1),
            ("Vite bilan yangi React loyihasini yaratish uchun buyruq?", ["npm start react", "npm create vite@latest", "npx react-new", "npm init react"], 1),
            ("React'da sayt asosan nimadan iborat?", ["Faqat bitta katta fayldan", "Komponentlar daraxtidan", "Faqat CSS fayllardan", "Server shablonlaridan"], 1),
            ("Component (komponent) nima?", ["Faqat CSS klassi", "Qayta ishlatiladigan UI qismi", "Ma'lumotlar bazasi jadvali", "Server route'i"], 1),
            ("JSX brauzerda ishlashi uchun nimaga aylantiriladi?", ["To'g'ridan-to'g'ri HTML'ga", "Babel orqali sof JavaScript'ga", "PHP kodiga", "SQL so'roviga"], 1),
            ("React eski usul (document.createElement, innerHTML) dan nimasi bilan farq qiladi?", ["Hech qanday farqi yo'q", "DOM manipulatsiyasini yashirib, deklarativ yozishga imkon beradi", "Faqat serverda ishlaydi", "CSS'ni butunlay taqiqlaydi"], 1),
            ("Bitta React komponenti odatda nima qaytaradi?", ["JSON", "JSX", "SQL so'rov", "CSS fayl"], 1),
        ],
        "ru": [
            ("Что такое React?", ["База данных", "Библиотека для создания UI", "Серверный язык", "CSS-фреймворк"], 1),
            ("Что такое JSX?", ["Отдельный язык программирования", "HTML-подобный синтаксис внутри JavaScript", "CSS-препроцессор", "Формат данных"], 1),
            ("Какая команда создаёт новый React-проект с Vite?", ["npm start react", "npm create vite@latest", "npx react-new", "npm init react"], 1),
            ("Из чего в основном состоит сайт на React?", ["Только из одного большого файла", "Из дерева компонентов", "Только из CSS-файлов", "Из серверных шаблонов"], 1),
            ("Что такое компонент (component)?", ["Только CSS-класс", "Переиспользуемая часть UI", "Таблица базы данных", "Серверный route"], 1),
            ("Во что превращается JSX, чтобы работать в браузере?", ["Напрямую в HTML", "В чистый JavaScript через Babel", "В код PHP", "В SQL-запрос"], 1),
            ("Чем React отличается от старого подхода (document.createElement, innerHTML)?", ["Ничем не отличается", "Скрывает манипуляции с DOM, позволяя писать декларативно", "Работает только на сервере", "Полностью запрещает CSS"], 1),
            ("Что обычно возвращает один React-компонент?", ["JSON", "JSX", "SQL-запрос", "CSS-файл"], 1),
        ],
    },
    384: {  # 2-Props va kompozitsiya
        "uz": [
            ("Prop nima?", ["Komponent ichidagi o'zgaruvchan qiymat", "Komponentga tashqaridan uzatiladigan ma'lumot", "CSS xususiyati", "Server so'rovi"], 1),
            ("Props qanday sintaksis bilan qabul qilinadi?", ["function Card(state)", "function Card({ sarlavha, matn })", "function Card(this.props)", "function Card(context)"], 1),
            ("Komponentga prop qanday uzatiladi?", ["<Card sarlavha=\"React\" />", "Card.props = {...}", "props(Card, {...})", "<Card>{props}</Card>"], 0),
            ("Props komponent ichida o'zgartirilishi mumkinmi?", ["Ha, istalgan vaqtda", "Yo'q, ular faqat o'qish uchun (read-only)", "Faqat useEffect ichida", "Faqat birinchi renderda"], 1),
            ("Kompozitsiya React'da nimani anglatadi?", ["Bitta katta komponent yozish", "Kichik komponentlarni birlashtirib kattasini yasash", "CSS fayllarni birlashtirish", "Ma'lumotlar bazasini loyihalash"], 1),
            ("Bitta komponentni turli props bilan bir necha marta chaqirish mumkinmi?", ["Yo'q, faqat bir marta", "Ha, har birida turli qiymatlar bilan", "Faqat ikki marta", "Faqat class komponentlarda"], 1),
            ("Props orqali funksiya (masalan onClick) uzatish mumkinmi?", ["Yo'q, faqat matn/son uzatiladi", "Ha, funksiyalar ham prop sifatida uzatiladi", "Faqat useCallback bilan", "Faqat Context orqali"], 1),
            ("Props va state orasidagi asosiy farq nima?", ["Farqi yo'q", "Props tashqaridan keladi, state komponent ichida boshqariladi", "Props faqat CSS uchun", "State faqat class komponentlarda bo'ladi"], 1),
        ],
        "ru": [
            ("Что такое prop?", ["Изменяемое значение внутри компонента", "Данные, передаваемые компоненту извне", "CSS-свойство", "Серверный запрос"], 1),
            ("С каким синтаксисом компонент принимает props?", ["function Card(state)", "function Card({ sarlavha, matn })", "function Card(this.props)", "function Card(context)"], 1),
            ("Как передать prop компоненту?", ["<Card sarlavha=\"React\" />", "Card.props = {...}", "props(Card, {...})", "<Card>{props}</Card>"], 0),
            ("Можно ли изменить props внутри компонента?", ["Да, в любое время", "Нет, они доступны только для чтения (read-only)", "Только внутри useEffect", "Только при первом рендере"], 1),
            ("Что означает композиция в React?", ["Написание одного большого компонента", "Объединение маленьких компонентов в больший", "Объединение CSS-файлов", "Проектирование базы данных"], 1),
            ("Можно ли вызвать один компонент несколько раз с разными props?", ["Нет, только один раз", "Да, каждый раз с разными значениями", "Только два раза", "Только в классовых компонентах"], 1),
            ("Можно ли передать функцию (например onClick) через props?", ["Нет, передаются только текст/число", "Да, функции тоже передаются как prop", "Только через useCallback", "Только через Context"], 1),
            ("В чём основное отличие props от state?", ["Разницы нет", "Props приходят извне, state управляется внутри компонента", "Props только для CSS", "State есть только в классовых компонентах"], 1),
        ],
    },
    385: {  # 3-useState va event handler'lar
        "uz": [
            ("useState nima uchun kerak?", ["API so'rov yuborish uchun", "Komponent xotirasi (state) saqlash uchun", "CSS stil berish uchun", "Marshrutlash uchun"], 1),
            ("useState qanday massiv qaytaradi?", ["[funksiya, obyekt]", "[joriy qiymat, o'zgartiruvchi funksiya]", "[props, state]", "[komponent, ref]"], 1),
            ("setState (masalan setSon) chaqirilganda nima bo'ladi?", ["Hech narsa", "Komponent qayta render bo'ladi", "Sahifa to'liq qayta yuklanadi", "Server qayta ishga tushadi"], 1),
            ("onClick handler nima uchun ishlatiladi?", ["Sahifa yuklanganda ishga tushirish uchun", "Tugma bosilganda funksiyani chaqirish uchun", "CSS animatsiya uchun", "API javobini kutish uchun"], 1),
            ("useState(0) nima qiladi?", ["0 qiymatli o'zgarmas konstant yaratadi", "Boshlang'ich qiymati 0 bo'lgan state yaratadi", "Komponentni o'chiradi", "CSS xususiyatini belgilaydi"], 1),
            ("Counter komponentida sonni bittaga oshirish odatda qanday yoziladi?", ["son = son + 1", "setSon(son + 1)", "son.push(1)", "useEffect(son + 1)"], 1),
            ("Event handler funksiyasi qachon chaqiriladi?", ["Komponent birinchi marta render bo'lganda", "Foydalanuvchi harakati (masalan, click) sodir bo'lganda", "Sahifa yopilganda", "Har 1 sekundda"], 1),
            ("useState qaysi paketdan import qilinadi?", ["'react-dom'", "'react'", "'react-router-dom'", "'react-hooks'"], 1),
        ],
        "ru": [
            ("Зачем нужен useState?", ["Для отправки API-запросов", "Для хранения памяти (state) компонента", "Для задания CSS-стилей", "Для маршрутизации"], 1),
            ("Какой массив возвращает useState?", ["[функция, объект]", "[текущее значение, функция изменения]", "[props, state]", "[компонент, ref]"], 1),
            ("Что происходит при вызове setState (например setSon)?", ["Ничего", "Компонент перерисовывается (re-render)", "Страница полностью перезагружается", "Сервер перезапускается"], 1),
            ("Для чего используется обработчик onClick?", ["Для запуска при загрузке страницы", "Для вызова функции при нажатии кнопки", "Для CSS-анимации", "Для ожидания ответа API"], 1),
            ("Что делает useState(0)?", ["Создаёт неизменяемую константу со значением 0", "Создаёт state с начальным значением 0", "Удаляет компонент", "Задаёт CSS-свойство"], 1),
            ("Как обычно увеличивают число на единицу в компоненте Counter?", ["son = son + 1", "setSon(son + 1)", "son.push(1)", "useEffect(son + 1)"], 1),
            ("Когда вызывается функция-обработчик события?", ["Когда компонент рендерится в первый раз", "Когда происходит действие пользователя (например click)", "Когда страница закрывается", "Каждую секунду"], 1),
            ("Из какого пакета импортируется useState?", ["'react-dom'", "'react'", "'react-router-dom'", "'react-hooks'"], 1),
        ],
    },
    386: {  # R1-Counter + Todo list (takrorlash)
        "uz": [
            ("Bu takrorlash darsida qaysi 3 mavzu birlashtiriladi?", ["Router, Context, hooks", "JSX, Props, useState", "Formalar, useEffect, memo", "SQL, API, JWT"], 1),
            ("Loyihadagi har bir Counter komponenti qanday state'ga ega bo'lishi kerak?", ["Barchasi bitta umumiy state'ni bo'lishadi", "Har biri o'zining alohida, mustaqil state'iga ega", "State kerak emas", "Faqat birinchisida state bo'ladi"], 1),
            ("TodoList uchun qaysi amallar talab qilinadi?", ["Faqat ko'rsatish", "Yozish, o'chirish, bajarildi belgisini qo'yish", "Faqat o'chirish", "Faqat saralash"], 1),
            ("Bajarilmagan todolar sonini ko'rsatish uchun nima qilinadi?", ["Qo'lda sanaladi", "State massivi filter/hisoblash orqali hisoblanadi", "Serverdan so'raladi", "CSS orqali hisoblanadi"], 1),
            ("Counter komponentiga label va start proplarini berish nima uchun kerak?", ["Kerak emas", "Komponentni qayta ishlatuvchan va moslashuvchan qilish uchun", "Faqat dizayn uchun", "React talab qilgani uchun"], 1),
            ("Bir nechta Counter komponenti bir xil state'ni bo'lishadimi?", ["Ha, doim bir xil", "Yo'q, har biri mustaqil ishlaydi", "Faqat ikkitasi bo'lishadi", "Faqat props orqali bog'lansa"], 1),
            ("Todo elementini ro'yxatdan o'chirish odatda qanday amalga oshiriladi?", ["delete kalit so'zi bilan", "filter() bilan massivdan chiqarib, yangi massiv bilan state yangilanadi", "Sahifani qayta yuklab", "CSS display:none bilan"], 1),
            ("Bu loyihada kompozitsiya qanday qo'llaniladi?", ["Umuman qo'llanilmaydi", "Kichik komponentlar (Counter, TodoList) birlashtirilib App yasaladi", "Faqat CSS orqali", "Faqat useEffect orqali"], 1),
        ],
        "ru": [
            ("Какие 3 темы объединяются в этом повторительном уроке?", ["Router, Context, hooks", "JSX, Props, useState", "Формы, useEffect, memo", "SQL, API, JWT"], 1),
            ("Каким должен быть state у каждого компонента Counter в проекте?", ["Все используют один общий state", "У каждого свой отдельный, независимый state", "State не нужен", "State есть только у первого"], 1),
            ("Какие действия требуются для TodoList?", ["Только отображение", "Добавление, удаление, отметка \"выполнено\"", "Только удаление", "Только сортировка"], 1),
            ("Как получить количество невыполненных задач?", ["Считается вручную", "Вычисляется через filter/подсчёт по массиву state", "Запрашивается с сервера", "Вычисляется через CSS"], 1),
            ("Зачем компоненту Counter передавать props label и start?", ["Не нужно", "Чтобы сделать компонент переиспользуемым и гибким", "Только для дизайна", "Потому что этого требует React"], 1),
            ("Используют ли несколько компонентов Counter один и тот же state?", ["Да, всегда один", "Нет, каждый работает независимо", "Только два из них", "Только если связаны через props"], 1),
            ("Как обычно удаляют элемент todo из списка?", ["Ключевым словом delete", "Через filter(), обновляя state новым массивом", "Перезагрузкой страницы", "Через CSS display:none"], 1),
            ("Как в этом проекте применяется композиция?", ["Не применяется вообще", "Маленькие компоненты (Counter, TodoList) объединяются в App", "Только через CSS", "Только через useEffect"], 1),
        ],
    },
    387: {  # 4-Conditional rendering va lists (key)
        "uz": [
            ("React JSX ichida to'g'ridan-to'g'ri if/else yozish mumkinmi?", ["Ha, har doim mumkin", "Yo'q, chunki ular statement, JSX faqat expression qabul qiladi", "Faqat class komponentda mumkin", "Faqat useEffect ichida mumkin"], 1),
            ("Shartli render qilish uchun eng ko'p ishlatiladigan operator?", ["switch-case", "Ternary (? :)", "for sikli", "while sikli"], 1),
            ("Faqat shart TRUE bo'lgandagina biror narsa ko'rsatish uchun qaysi operator ishlatiladi?", ["||", "&&", "!", "=="], 1),
            ("Ro'yxatni render qilish uchun qaysi massiv metodi ishlatiladi?", ["arr.filter()", "arr.map()", "arr.reduce()", "arr.forEach()"], 1),
            ("Ro'yxat elementlariga key nima uchun beriladi?", ["Faqat CSS stillash uchun", "React'ga har bir elementni farqlab, samarali yangilash uchun", "SEO uchun", "Hech qanday sabab yo'q"], 1),
            ("key sifatida odatda nima ishlatiladi?", ["Tasodifiy son", "item.id kabi unikal identifikator", "Elementning matni", "Har doim 0"], 1),
            ("key sifatida array index ishlatish nega tavsiya etilmaydi?", ["Bu umuman ishlamaydi", "Ro'yxat o'zgarganda (qo'shilsa/o'chirilsa) noto'g'ri render'ga olib kelishi mumkin", "React xato beradi", "Faqat performance uchun yaxshi"], 1),
            ("\"Agar foydalanuvchi tizimga kirgan bo'lsa profilni ko'rsat\" kabi holat qanday deyiladi?", ["Lifting state up", "Conditional rendering", "Prop drilling", "Custom hook"], 1),
        ],
        "ru": [
            ("Можно ли писать if/else напрямую внутри JSX?", ["Да, всегда можно", "Нет, потому что это statement, а JSX принимает только expression", "Только в классовом компоненте", "Только внутри useEffect"], 1),
            ("Какой оператор чаще всего используется для условного рендеринга?", ["switch-case", "Тернарный (? :)", "Цикл for", "Цикл while"], 1),
            ("Какой оператор используется, чтобы показать что-то только когда условие TRUE?", ["||", "&&", "!", "=="], 1),
            ("Какой метод массива используется для рендера списка?", ["arr.filter()", "arr.map()", "arr.reduce()", "arr.forEach()"], 1),
            ("Зачем элементам списка присваивается key?", ["Только для CSS-стилизации", "Чтобы React мог различать элементы и эффективно обновлять их", "Для SEO", "Без особой причины"], 1),
            ("Что обычно используют в качестве key?", ["Случайное число", "Уникальный идентификатор вроде item.id", "Текст элемента", "Всегда 0"], 1),
            ("Почему не рекомендуется использовать индекс массива в качестве key?", ["Это вообще не работает", "При изменении списка (добавлении/удалении) может привести к неверному рендерингу", "React выдаёт ошибку", "Хорошо только для производительности"], 1),
            ("Как называется ситуация \"показать профиль, если пользователь вошёл в систему\"?", ["Lifting state up", "Условный рендеринг (conditional rendering)", "Prop drilling", "Custom hook"], 1),
        ],
    },
    388: {  # 5-Forms va controlled inputs
        "uz": [
            ("Controlled component nima?", ["Faqat CSS bilan boshqariladigan komponent", "Input qiymati React state orqali boshqariladigan komponent", "Faqat class komponent", "Server tomonidan render qilinadigan komponent"], 1),
            ("Controlled input uchun qaysi ikkita narsa majburiy?", ["className va id", "value va onChange", "key va ref", "style va type"], 1),
            ("onChange handler odatda nima qiladi?", ["Sahifani qayta yuklaydi", "State'ni input'ning yangi qiymati bilan yangilaydi", "Formani yuboradi", "CSS'ni o'zgartiradi"], 1),
            ("Forma yuborilganda sahifa qayta yuklanmasligi uchun nima chaqiriladi?", ["event.stopPropagation()", "event.preventDefault()", "event.target.reset()", "event.cancel()"], 1),
            ("onSubmit handler odatda qaysi elementga biriktiriladi?", ["<input>", "<form>", "<button>", "<div>"], 1),
            ("Controlled input'da qiymat qayerda \"yashaydi\"?", ["Faqat brauzer DOM'ida", "React state'da", "Faqat serverda", "localStorage'da doim"], 1),
            ("e.target.value nimani qaytaradi?", ["Input'ning nomi", "Input'ning joriy qiymati", "Input'ning turi", "Formaning barcha maydonlari"], 1),
            ("Controlled komponentlarning asosiy afzalligi nima?", ["Kod qisqaroq bo'ladi", "Input qiymatini to'liq React orqali nazorat qilish imkonini beradi", "CSS kerak emas", "Server bilan bog'lanish shart emas"], 1),
        ],
        "ru": [
            ("Что такое controlled component?", ["Компонент, управляемый только через CSS", "Компонент, значение input которого управляется React state", "Только классовый компонент", "Компонент, рендерящийся на сервере"], 1),
            ("Какие два свойства обязательны для controlled input?", ["className и id", "value и onChange", "key и ref", "style и type"], 1),
            ("Что обычно делает обработчик onChange?", ["Перезагружает страницу", "Обновляет state новым значением input", "Отправляет форму", "Меняет CSS"], 1),
            ("Что вызывается, чтобы страница не перезагружалась при отправке формы?", ["event.stopPropagation()", "event.preventDefault()", "event.target.reset()", "event.cancel()"], 1),
            ("К какому элементу обычно привязывается обработчик onSubmit?", ["<input>", "<form>", "<button>", "<div>"], 1),
            ("Где \"живёт\" значение controlled input?", ["Только в DOM браузера", "В React state", "Только на сервере", "Всегда в localStorage"], 1),
            ("Что возвращает e.target.value?", ["Имя input", "Текущее значение input", "Тип input", "Все поля формы"], 1),
            ("В чём главное преимущество controlled-компонентов?", ["Код становится короче", "Позволяют полностью контролировать значение input через React", "CSS не нужен", "Не требуется связь с сервером"], 1),
        ],
    },
    389: {  # 6-useEffect va lifecycle
        "uz": [
            ("useEffect nima uchun ishlatiladi?", ["Faqat CSS berish uchun", "Side effect (tashqi ta'sir)larni boshqarish uchun", "Faqat props tekshirish uchun", "Komponentni o'chirish uchun"], 1),
            ("Bo'sh dependency array ([]) bilan useEffect qachon ishga tushadi?", ["Har render'da", "Faqat komponent mount bo'lganda (birinchi render)", "Hech qachon", "Faqat unmount bo'lganda"], 1),
            ("Dependency array bo'sh bo'lsa bu nimani anglatadi?", ["Effect cheksiz qayta ishga tushadi", "Effect faqat bir marta ishga tushadi", "Effect umuman ishlamaydi", "Xato yuz beradi"], 1),
            ("useEffect'dagi cleanup funksiyasi qachon chaqiriladi?", ["Faqat mount bo'lganda", "Komponent unmount bo'lganda yoki keyingi effectdan oldin", "Hech qachon", "Faqat foydalanuvchi tugma bossa"], 1),
            ("Side effect'ga misol keltiring.", ["Oddiy o'zgaruvchi e'lon qilish", "API'dan ma'lumot olish yoki timer qo'yish", "JSX qaytarish", "Prop qabul qilish"], 1),
            ("useEffect ichida document.title'ni o'zgartirish nimaga misol?", ["Sof (pure) funksiyaga", "Side effect'ga (tashqi dunyo bilan ishlash)", "Conditional rendering'ga", "Prop drilling'ga"], 1),
            ("Dependency array'da bir o'zgaruvchi ko'rsatilsa nima bo'ladi?", ["Effect umuman ishlamaydi", "Shu o'zgaruvchi o'zgarganda effect qayta ishga tushadi", "Komponent butunlay qayta yaratiladi", "Xato chiqadi"], 1),
            ("useEffect qaysi paketdan import qilinadi?", ["'react-router-dom'", "'react'", "'react-dom'", "'react-effects'"], 1),
        ],
        "ru": [
            ("Зачем используется useEffect?", ["Только для задания CSS", "Для управления side effect (побочными эффектами)", "Только для проверки props", "Для удаления компонента"], 1),
            ("Когда срабатывает useEffect с пустым массивом зависимостей ([])?", ["При каждом рендере", "Только при mount компонента (первый рендер)", "Никогда", "Только при unmount"], 1),
            ("Что означает пустой массив зависимостей?", ["Эффект будет срабатывать бесконечно", "Эффект сработает только один раз", "Эффект вообще не работает", "Возникнет ошибка"], 1),
            ("Когда вызывается cleanup-функция внутри useEffect?", ["Только при mount", "При unmount компонента или перед следующим эффектом", "Никогда", "Только по клику пользователя"], 1),
            ("Приведите пример side effect.", ["Обычное объявление переменной", "Получение данных с API или установка таймера", "Возврат JSX", "Приём prop"], 1),
            ("Изменение document.title внутри useEffect — пример чего?", ["Чистой (pure) функции", "Side effect (работы с внешним миром)", "Условного рендеринга", "Prop drilling"], 1),
            ("Что произойдёт, если в массиве зависимостей указать переменную?", ["Эффект вообще перестанет работать", "Эффект будет перезапускаться при изменении этой переменной", "Компонент полностью пересоздастся", "Возникнет ошибка"], 1),
            ("Из какого пакета импортируется useEffect?", ["'react-router-dom'", "'react'", "'react-dom'", "'react-effects'"], 1),
        ],
    },
    390: {  # R2-Weather widget (takrorlash)
        "uz": [
            ("Bu loyihada qaysi mavzular birlashtiriladi?", ["Router, Context, memo", "Controlled form, conditional rendering, list, useEffect", "JWT, auth, protected route", "SQL, API, JSON"], 1),
            ("Ob-havo ma'lumoti so'ralayotganda odatda qaysi holat ko'rsatiladi?", ["To'g'ridan-to'g'ri xato", "Yuklanmoqda (loading) holati", "Bo'sh sahifa", "Login formasi"], 1),
            ("API so'rovi muvaffaqiyatsiz bo'lsa nima ko'rsatilishi kerak?", ["Hech narsa ko'rsatilmaydi", "Xato xabari va qayta urinish tugmasi", "Sahifa avtomatik yopiladi", "Login sahifasiga o'tkaziladi"], 1),
            ("Loading/error/data kabi 3 holat qanday boshqariladi?", ["CSS orqali", "Conditional rendering orqali", "Faqat useState orqali, shart yozilmasdan", "Router orqali"], 1),
            ("Foydalanuvchi shaharni qanday tanlaydi?", ["Faqat URL orqali", "Controlled input yoki dropdown orqali", "Fayl yuklab", "Console orqali"], 1),
            ("5 kunlik prognozni ko'rsatish uchun qaysi React texnikasi kerak?", ["useContext", "Ro'yxatni map() va key bilan render qilish", "useCallback", "React.memo"], 1),
            ("Tashqi API'dan ma'lumot olish uchun qaysi hook ishlatiladi?", ["useState", "useEffect", "useRef", "useContext"], 1),
            ("Open-Meteo misolida bu loyiha uchun API kaliti kerakmi?", ["Ha, majburiy", "Yo'q, kerak emas", "Faqat pullik tarifda kerak", "Faqat production'da kerak"], 1),
        ],
        "ru": [
            ("Какие темы объединяются в этом проекте?", ["Router, Context, memo", "Controlled form, условный рендеринг, список, useEffect", "JWT, auth, protected route", "SQL, API, JSON"], 1),
            ("Какое состояние обычно показывается во время запроса погоды?", ["Сразу ошибка", "Состояние загрузки (loading)", "Пустая страница", "Форма входа"], 1),
            ("Что должно показываться при неудачном запросе к API?", ["Ничего не показывается", "Сообщение об ошибке и кнопка повтора", "Страница закрывается автоматически", "Переход на страницу входа"], 1),
            ("Как управляются 3 состояния вроде loading/error/data?", ["Через CSS", "Через условный рендеринг", "Только через useState, без условий", "Через Router"], 1),
            ("Как пользователь выбирает город?", ["Только через URL", "Через controlled input или выпадающий список", "Загружая файл", "Через консоль"], 1),
            ("Какая техника React нужна для отображения прогноза на 5 дней?", ["useContext", "Рендер списка через map() и key", "useCallback", "React.memo"], 1),
            ("Какой hook используется для получения данных с внешнего API?", ["useState", "useEffect", "useRef", "useContext"], 1),
            ("Нужен ли API-ключ для этого проекта на примере Open-Meteo?", ["Да, обязателен", "Нет, не нужен", "Нужен только на платном тарифе", "Нужен только в production"], 1),
        ],
    },
    391: {  # 7-Custom hooks
        "uz": [
            ("Custom hook nima?", ["React'ning ichki maxsus komponenti", "Takroriy mantiqni alohida funksiyaga ajratib, qayta ishlatish usuli", "CSS klassi", "Server endpoint'i"], 1),
            ("Custom hook nomi odatda qanday boshlanadi?", ["get bilan", "use bilan (masalan useToggle)", "handle bilan", "make bilan"], 1),
            ("Custom hook ichida oddiy React hook'laridan (useState, useEffect) foydalanish mumkinmi?", ["Yo'q, taqiqlangan", "Ha, mumkin", "Faqat class komponentda", "Faqat useMemo bilan"], 1),
            ("Nega har bir komponentda useState+useEffect+try/catch qayta yozish yomon odat?", ["Bu yaxshi amaliyot", "Kod takrorlanadi va qo'llab-quvvatlash qiyinlashadi", "React bunga ruxsat bermaydi", "Sekinroq ishlaydi"], 1),
            ("useFetch kabi custom hook odatda nimalarni qaytarishi mumkin?", ["Faqat JSX", "data, loading, error kabi qiymatlarni", "Faqat CSS klass", "Faqat boolean"], 1),
            ("Bir custom hook bir nechta komponentda ishlatilsa, ularning state'lari bo'lishiladimi?", ["Ha, hammasi bitta state'ni ishlatadi", "Yo'q, har birida alohida, mustaqil state bo'ladi", "Faqat ikkitasida bo'lishiladi", "Bog'liq emas"], 1),
            ("useCallback custom hook ichida ko'pincha nima uchun ishlatiladi?", ["Komponentni o'chirish uchun", "Funksiyani qayta yaratilishining oldini olish uchun", "CSS berish uchun", "Route yaratish uchun"], 1),
            ("Custom hook aslida nima?", ["Maxsus React komponenti", "Oddiy JavaScript funksiyasi (ichida hook chaqiradigan)", "CSS fayli", "JSON obyekti"], 1),
        ],
        "ru": [
            ("Что такое custom hook?", ["Внутренний специальный компонент React", "Способ вынести повторяющуюся логику в отдельную переиспользуемую функцию", "CSS-класс", "Серверный endpoint"], 1),
            ("С чего обычно начинается название custom hook?", ["С get", "С use (например useToggle)", "С handle", "С make"], 1),
            ("Можно ли использовать обычные хуки React (useState, useEffect) внутри custom hook?", ["Нет, запрещено", "Да, можно", "Только в классовом компоненте", "Только с useMemo"], 1),
            ("Почему плохо каждый раз заново писать useState+useEffect+try/catch в каждом компоненте?", ["Это хорошая практика", "Код дублируется, и его сложнее поддерживать", "React это запрещает", "Работает медленнее"], 1),
            ("Что обычно может возвращать custom hook вроде useFetch?", ["Только JSX", "Значения вроде data, loading, error", "Только CSS-класс", "Только boolean"], 1),
            ("Если один custom hook используется в нескольких компонентах, разделяют ли они state?", ["Да, все используют один state", "Нет, у каждого свой независимый state", "Только у двух из них общий", "Не имеет значения"], 1),
            ("Для чего часто используется useCallback внутри custom hook?", ["Чтобы удалить компонент", "Чтобы предотвратить пересоздание функции", "Чтобы задать CSS", "Чтобы создать route"], 1),
            ("Чем на самом деле является custom hook?", ["Специальным компонентом React", "Обычной JavaScript-функцией (вызывающей внутри хуки)", "CSS-файлом", "JSON-объектом"], 1),
        ],
    },
    392: {  # 8-React Router
        "uz": [
            ("React Router nima uchun ishlatiladi?", ["State boshqarish uchun", "Sahifalar (URL) orasida navigatsiya qilish uchun", "API so'rov yuborish uchun", "CSS animatsiya uchun"], 1),
            ("React Router'ni o'rnatish uchun buyruq?", ["npm install react-router", "npm install react-router-dom", "npm install router", "npm install react-navigation"], 1),
            ("Butun ilovani o'rab, routing imkonini beruvchi komponent?", ["<Routes>", "<BrowserRouter>", "<Link>", "<Navigate>"], 1),
            ("Bitta manzil (URL) va u ko'rsatadigan komponentni bog'lash uchun ishlatiladigan komponent?", ["<Link>", "<Route path=\"...\" element={...} />", "<Navigate>", "<Outlet>"], 1),
            ("Sahifa qayta yuklanmasdan boshqa sahifaga o'tish uchun ishlatiladigan komponent?", ["<a>", "<Link>", "<button>", "<form>"], 1),
            ("Dasturiy ravishda (masalan formadan keyin) boshqa sahifaga o'tkazish uchun hook?", ["useParams", "useNavigate", "useLocation", "useRoutes"], 1),
            ("URL parametrini (masalan /kurslar/:id dagi id) olish uchun hook?", ["useNavigate", "useParams", "useSearchParams", "useContext"], 1),
            ("Hech qanday manzilga mos kelmagan sahifalar uchun odatda nima yaratiladi?", ["Hech narsa kerak emas", "404 route", "Login route", "Redirect faqat bosh sahifaga"], 1),
        ],
        "ru": [
            ("Зачем используется React Router?", ["Для управления state", "Для навигации между страницами (URL)", "Для отправки API-запросов", "Для CSS-анимации"], 1),
            ("Какая команда устанавливает React Router?", ["npm install react-router", "npm install react-router-dom", "npm install router", "npm install react-navigation"], 1),
            ("Какой компонент оборачивает всё приложение, включая маршрутизацию?", ["<Routes>", "<BrowserRouter>", "<Link>", "<Navigate>"], 1),
            ("Какой компонент связывает конкретный URL с отображаемым компонентом?", ["<Link>", "<Route path=\"...\" element={...} />", "<Navigate>", "<Outlet>"], 1),
            ("Какой компонент используется для перехода на другую страницу без перезагрузки?", ["<a>", "<Link>", "<button>", "<form>"], 1),
            ("Какой хук используется для программного перехода (например после формы)?", ["useParams", "useNavigate", "useLocation", "useRoutes"], 1),
            ("Какой хук получает параметр URL (например id из /kurslar/:id)?", ["useNavigate", "useParams", "useSearchParams", "useContext"], 1),
            ("Что обычно создаётся для страниц, не совпадающих ни с одним маршрутом?", ["Ничего не нужно", "404 route", "Login route", "Редирект только на главную"], 1),
        ],
    },
    393: {  # 9-Context API
        "uz": [
            ("Prop drilling nima?", ["Componentga CSS berish", "Propni ko'p qavat orqali uzatishga majbur bo'lish", "State'ni o'chirish", "Router yaratish"], 1),
            ("Context yaratish uchun qaysi funksiya ishlatiladi?", ["useContext()", "createContext()", "new Context()", "Context.new()"], 1),
            ("Context qiymatini ta'minlaydigan komponent?", ["Context.Consumer", "Context.Provider", "Context.Value", "Context.Wrapper"], 1),
            ("Context qiymatini o'qish uchun qaysi hook ishlatiladi?", ["useState", "useContext", "useEffect", "useRef"], 1),
            ("Context qachon ishlatilishi tavsiya etiladi?", ["Har doim, har qanday holatda", "Global holatni ko'p komponent ishlatganda (masalan foydalanuvchi ma'lumoti)", "Faqat CSS uchun", "Faqat bitta komponentda"], 1),
            ("Provider'ning value prop'i nima uchun kerak?", ["Faqat CSS uchun", "Context orqali uzatiladigan ma'lumotni belgilash uchun", "Komponent nomini belgilash uchun", "Router manzilini belgilash uchun"], 1),
            ("Context qiymati o'zgarganda nima sodir bo'ladi?", ["Hech narsa", "Undan foydalanuvchi barcha komponentlar qayta render bo'ladi", "Faqat Provider qayta render bo'ladi", "Sahifa qayta yuklanadi"], 1),
            ("Context'ning asosiy vazifasi nima?", ["CSS uslublashtirish", "Prop drilling'siz ma'lumotni chuqur komponentlarga yetkazish", "API so'rov yuborish", "Formani validatsiya qilish"], 1),
        ],
        "ru": [
            ("Что такое prop drilling?", ["Задание CSS компоненту", "Необходимость передавать prop через много уровней", "Удаление state", "Создание Router"], 1),
            ("Какая функция создаёт Context?", ["useContext()", "createContext()", "new Context()", "Context.new()"], 1),
            ("Какой компонент предоставляет значение Context?", ["Context.Consumer", "Context.Provider", "Context.Value", "Context.Wrapper"], 1),
            ("Какой хук используется для чтения значения Context?", ["useState", "useContext", "useEffect", "useRef"], 1),
            ("Когда рекомендуется использовать Context?", ["Всегда, в любой ситуации", "Когда глобальное состояние используют много компонентов (например данные пользователя)", "Только для CSS", "Только в одном компоненте"], 1),
            ("Зачем нужен prop value у Provider?", ["Только для CSS", "Чтобы задать данные, передаваемые через Context", "Чтобы задать имя компонента", "Чтобы задать адрес маршрута"], 1),
            ("Что происходит при изменении значения Context?", ["Ничего", "Все компоненты, использующие его, перерисовываются", "Перерисовывается только Provider", "Страница перезагружается"], 1),
            ("Какова основная задача Context?", ["Стилизация через CSS", "Передача данных вглубь компонентов без prop drilling", "Отправка API-запросов", "Валидация формы"], 1),
        ],
    },
    394: {  # R3-Auth flow + protected routes (takrorlash)
        "uz": [
            ("Bu loyihada qaysi 3 mavzu birlashtiriladi?", ["JSX, props, useState", "Custom hooks, Context, Router", "Formalar, useEffect, memo", "SQL, JSON, API"], 1),
            ("Foydalanuvchi ma'lumotini butun ilova bo'ylab boshqarish uchun nima ishlatiladi?", ["Faqat props", "AuthContext (Context API)", "Faqat useState", "CSS o'zgaruvchilari"], 1),
            ("Protected route nima?", ["Har kim kira oladigan sahifa", "Faqat tizimga kirgan foydalanuvchilar kira oladigan sahifa", "Faqat mobil qurilma uchun sahifa", "404 sahifasi"], 1),
            ("Sahifa qayta yuklansa ham foydalanuvchi tizimda qolishi uchun nima ishlatiladi?", ["sessionStorage har doim", "localStorage", "Faqat state", "Cookie majburiy"], 1),
            ("Tizimga kirmagan foydalanuvchi protected sahifaga kirishga urinsa, u qayerga yo'naltiriladi?", ["Bosh sahifaga", "Login sahifasiga", "404 sahifasiga", "Hech qayerga"], 1),
            ("Muvaffaqiyatli login'dan keyin foydalanuvchi odatda qayerga qaytariladi?", ["Har doim bosh sahifaga", "Avval kirmoqchi bo'lgan sahifaga", "Har doim profil sahifasiga", "Chiqish (logout) sahifasiga"], 1),
            ("Header'da foydalanuvchi holatiga qarab nima ko'rsatilishi kerak?", ["Har doim bir xil menyu", "Kirgan bo'lsa ism+chiqish tugmasi, bo'lmasa kirish tugmasi", "Faqat logotip", "Hech narsa"], 1),
            ("useLocalStorage kabi custom hook bu loyihada nima uchun kerak?", ["Kerak emas", "localStorage bilan ishlashni qayta ishlatiladigan qilish uchun", "Faqat CSS uchun", "Faqat Router uchun"], 1),
        ],
        "ru": [
            ("Какие 3 темы объединяются в этом проекте?", ["JSX, props, useState", "Custom hooks, Context, Router", "Формы, useEffect, memo", "SQL, JSON, API"], 1),
            ("Что используется для управления данными пользователя во всём приложении?", ["Только props", "AuthContext (Context API)", "Только useState", "CSS-переменные"], 1),
            ("Что такое protected route?", ["Страница, доступная всем", "Страница, доступная только вошедшим пользователям", "Страница только для мобильных устройств", "Страница 404"], 1),
            ("Что используется, чтобы пользователь оставался в системе после перезагрузки страницы?", ["Всегда sessionStorage", "localStorage", "Только state", "Обязательно cookie"], 1),
            ("Куда перенаправляется невошедший пользователь при попытке зайти на protected-страницу?", ["На главную страницу", "На страницу входа", "На страницу 404", "Никуда"], 1),
            ("Куда обычно возвращается пользователь после успешного входа?", ["Всегда на главную", "На страницу, куда он изначально пытался попасть", "Всегда в профиль", "На страницу выхода"], 1),
            ("Что должно показываться в Header в зависимости от статуса пользователя?", ["Всегда одно и то же меню", "Если вошёл — имя и кнопка выхода, если нет — кнопка входа", "Только логотип", "Ничего"], 1),
            ("Зачем в этом проекте нужен custom hook вроде useLocalStorage?", ["Не нужен", "Чтобы сделать работу с localStorage переиспользуемой", "Только для CSS", "Только для Router"], 1),
        ],
    },
    395: {  # 10-Performance: memo, useMemo, useCallback
        "uz": [
            ("React.memo nima qiladi?", ["Komponentni har render'da qayta chizadi", "Komponentni faqat props o'zgarganda qayta render qiladi", "State'ni o'chiradi", "CSS keshlaydi"], 1),
            ("useMemo nimani keshlaydi (eslab qoladi)?", ["Funksiyani", "Hisoblangan qiymatni", "Komponentni", "CSS klassini"], 1),
            ("useCallback nimani keshlaydi?", ["Qiymatni", "Funksiyani", "Komponentni", "State'ni"], 1),
            ("Bu mavzuda qanday xavf haqida ogohlantiriladi?", ["Xotira yetishmasligi", "Premature optimization (hamma joyga memo qo'yish)", "Xavfsizlik zaifligi", "SEO muammosi"], 1),
            ("Optimizatsiyani qachon qo'llash tavsiya etiladi?", ["Loyihani boshlashdan oldin", "Avval sekinlik aniq sezilganda, oldindan emas", "Har doim, hamma komponentga", "Faqat production'da"], 1),
            ("1000 ta elementli ro'yxat har klavishada qayta render bo'lsa nima yuz berishi mumkin?", ["Hech narsa", "Sezilarli sekinlik", "Xatolik chiqadi", "Ilova to'xtaydi"], 1),
            ("useMemo va useCallback orasidagi asosiy farq nima?", ["Farqi yo'q", "useMemo qiymatni, useCallback funksiyani qaytaradi", "useCallback faqat class komponentda ishlaydi", "useMemo faqat CSS uchun"], 1),
            ("React.memo qanday turdagi komponentlarga qo'llaniladi?", ["Faqat class komponentlarga", "Function komponentlarga", "Faqat Context Provider'larga", "Faqat Router komponentlariga"], 1),
        ],
        "ru": [
            ("Что делает React.memo?", ["Перерисовывает компонент при каждом рендере", "Перерисовывает компонент только при изменении props", "Удаляет state", "Кеширует CSS"], 1),
            ("Что кеширует (запоминает) useMemo?", ["Функцию", "Вычисленное значение", "Компонент", "CSS-класс"], 1),
            ("Что кеширует useCallback?", ["Значение", "Функцию", "Компонент", "State"], 1),
            ("О какой опасности предупреждают в этой теме?", ["Нехватка памяти", "Преждевременная оптимизация (memo повсюду)", "Уязвимость безопасности", "Проблема с SEO"], 1),
            ("Когда рекомендуется применять оптимизацию?", ["До начала проекта", "Когда замедление реально ощущается, а не заранее", "Всегда, во всех компонентах", "Только в production"], 1),
            ("Что может произойти, если список из 1000 элементов перерисовывается при каждом нажатии клавиши?", ["Ничего", "Заметное замедление", "Возникнет ошибка", "Приложение остановится"], 1),
            ("В чём основное различие useMemo и useCallback?", ["Разницы нет", "useMemo возвращает значение, useCallback — функцию", "useCallback работает только в классовых компонентах", "useMemo только для CSS"], 1),
            ("К каким компонентам применяется React.memo?", ["Только к классовым", "К функциональным компонентам", "Только к Context Provider", "Только к компонентам Router"], 1),
        ],
    },
    396: {  # 11-CAPSTONE: Recipe finder (React + Flask)
        "uz": [
            ("Capstone loyihasida frontend qaysi texnologiyalar bilan qurilgan?", ["Vue + Vuex", "React + Vite + React Router", "Angular + RxJS", "jQuery + Bootstrap"], 1),
            ("Capstone loyihasida backend sifatida nima ishlatiladi?", ["Django", "Flask", "Express", "Laravel"], 1),
            ("Ma'lumotlar bazasi sifatida nima tavsiya etiladi?", ["MongoDB", "PostgreSQL", "Redis", "SQLite majburiy"], 1),
            ("Foydalanuvchi autentifikatsiyasi qanday amalga oshiriladi?", ["Faqat cookie orqali", "JWT (frontend Context, backend Flask-JWT-Extended)", "Faqat localStorage orqali, token'siz", "Autentifikatsiya kerak emas"], 1),
            ("Saqlangan retseptlar frontend tomonda qayerda saqlanadi?", ["Faqat serverda", "localStorage", "Faqat state'da, saqlanmaydi", "CSS'da"], 1),
            ("Bu capstone loyihasi qaysi darslardagi bilimlarni birlashtiradi?", ["Faqat 1-darsni", "Butun kursda o'rganilgan React mavzularini", "Faqat CSS mavzularini", "Faqat SQL mavzularini"], 1),
            ("Frontend backend bilan qanday gaplashadi?", ["To'g'ridan-to'g'ri ma'lumotlar bazasiga ulanib", "fetch orqali API so'rovlar yuborib", "Faqat WebSocket orqali", "Fayl orqali almashinib"], 1),
            ("Recipe Finder foydalanuvchiga nima qilish imkonini beradi?", ["Faqat ro'yxatdan o'tish", "Retsept qidirish, ko'rish, saqlash va sharhlash", "Faqat login qilish", "Faqat rasm yuklash"], 1),
        ],
        "ru": [
            ("На каких технологиях построен frontend в этом capstone-проекте?", ["Vue + Vuex", "React + Vite + React Router", "Angular + RxJS", "jQuery + Bootstrap"], 1),
            ("Что используется в качестве backend в этом capstone-проекте?", ["Django", "Flask", "Express", "Laravel"], 1),
            ("Какая база данных рекомендуется?", ["MongoDB", "PostgreSQL", "Redis", "Обязательно SQLite"], 1),
            ("Как реализована аутентификация пользователя?", ["Только через cookie", "JWT (frontend Context, backend Flask-JWT-Extended)", "Только через localStorage, без токена", "Аутентификация не нужна"], 1),
            ("Где на стороне frontend хранятся сохранённые рецепты?", ["Только на сервере", "localStorage", "Только в state, не сохраняются", "В CSS"], 1),
            ("Знания из каких уроков объединяет этот capstone-проект?", ["Только из первого урока", "Все темы React, изученные за курс", "Только темы CSS", "Только темы SQL"], 1),
            ("Как frontend общается с backend?", ["Напрямую подключаясь к базе данных", "Отправляя API-запросы через fetch", "Только через WebSocket", "Обмениваясь файлами"], 1),
            ("Что позволяет делать Recipe Finder пользователю?", ["Только регистрироваться", "Искать, просматривать, сохранять рецепты и оставлять отзывы", "Только входить в систему", "Только загружать изображения"], 1),
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
