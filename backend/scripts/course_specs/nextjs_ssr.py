"""Advanced React course: Next.js and Server-Side Rendering — fills a real
gap in category_id=9 (React). Course 43 (React Asoslari) teaches components/
props/state/hooks/forms/basic routing. Course 72 (Redux Toolkit, TypeScript
va Testlash) teaches state management, typing, and testing. Course 86/92 are
full-stack capstones on top of those. NONE of them teach Next.js — the App
Router, Server Components, SSR/SSG/ISR, or anything about "what happens when
React runs on a server, not just in the browser". That is the single most
in-demand "next step after React" skill in the real industry, and this
course exists to close that gap.

Honesty note on grounding (do not remove this comment): this repository's
actual frontend (frontend/) is Create React App (react-scripts 5.0.1), NOT
Next.js — confirmed directly: frontend/public/index.html has one empty
`<div id="root"></div>` and one static `<title>Gennis Tech</title>` /
`<meta name="description" ...>` pair for the entire site; frontend/src/
index.js calls `ReactDOM.createRoot(...).render(<App />)`; frontend/src/
App.js wraps everything in react-router-dom's `<BrowserRouter>`. There is no
real Next.js code anywhere in this repo to reference. So this course does
NOT pretend the platform runs on Next.js. Instead, lesson 0 draws an honest,
explicit, verifiable comparison between what this platform's own CRA
frontend does (the three facts above are real, cited directly) and what the
same feature looks like in Next.js — that comparison is genuine grounding,
since the CRA side is 100% real. Every Next.js-specific code example after
that is a realistic, runnable file (a small blog / product catalog), held to
the same quality bar as this platform's other courses, without any false
"this exact code exists in our repo" claim.

Built with the course_builder scaffold — see course_builder/__init__.py for
the spec contract. Every lesson gets both task + sample from the start, full
UZ+RU authored here directly (not machine-translated), Mermaid diagrams
where they genuinely clarify (Server/Client boundary, request lifecycle
through middleware, SSR/SSG/ISR comparison, file-to-route mapping, the
capstone architecture). is_published stays False — a human reviews first.
"""

COURSE = {
    "title": "React: Next.js va Server-Side Rendering",
    "title_ru": "React: Next.js и серверный рендеринг",
    "description": (
        "React Asoslari (43-kurs) komponentlar, props/state, hook'lar, forma va "
        "asosiy marshrutlashni o'rgatadi. Redux Toolkit, TypeScript va Testlash "
        "(72-kurs) esa holatni boshqarish, tiplash va testlashni chuqurlashtiradi. "
        "Lekin ikkalasi ham bitta katta mavzuni chetlab o'tadi: React server "
        "tomonida ishlaganda nima bo'ladi? Bu kurs aynan shu bo'shliqni to'ldiradi — "
        "Next.js freymvorki orqali fayl asosidagi marshrutlash (App Router), "
        "Server va Client Component'lar orasidagi farq ('use client' direktivasi — "
        "React'dan keyingi eng katta kontseptual sakrash), Server Component'lar "
        "ichida ma'lumot olish va keshlash, uchta render strategiyasini halol "
        "taqqoslash (SSR/SSG/ISR — o'ylab topilgan raqamlarsiz), ilova ichidagi "
        "Route Handler'lar, dinamik marshrutlar, Middleware, rasm/shrift "
        "optimallashtirish va Metadata API orqali SEO'ni o'rgatadi. "
        "MUHIM: ushbu platformaning haqiqiy frontend'i Next.js emas, balki Create "
        "React App (CRA) — buni kurs yashirmaydi. Aksincha, 1-dars ushbu "
        "platformaning haqiqiy CRA kodini (frontend/public/index.html'dagi bo'sh "
        "div#root, frontend/src/index.js'dagi ReactDOM.createRoot) ochiq taqqoslash "
        "sifatida ishlatadi — bu haqiqiy, tekshirilishi mumkin bo'lgan asoslash. "
        "Next.js kodining o'zi esa real, ishlaydigan misollarda (blog, mahsulotlar "
        "katalogi) o'qitiladi. Kurs oxirida to'liq Next.js ilova qurasiz."
    ),
    "description_ru": (
        "Курс «React Asoslari» (43) учит компонентам, props/state, хукам, формам и "
        "базовой маршрутизации. «Redux Toolkit, TypeScript va Testlash» (72) "
        "углубляет управление состоянием, типизацию и тестирование. Но оба курса "
        "обходят одну большую тему: что происходит, когда React выполняется на "
        "сервере? Этот курс закрывает именно этот пробел — через фреймворк "
        "Next.js: файловую маршрутизацию (App Router), разницу между Server и "
        "Client Component (директива 'use client' — самый большой концептуальный "
        "скачок после React), получение и кеширование данных внутри Server "
        "Component, честное сравнение трёх стратегий рендеринга (SSR/SSG/ISR — "
        "без выдуманных цифр), Route Handler'ы внутри самого приложения, "
        "динамические маршруты, Middleware, оптимизацию изображений/шрифтов и "
        "Metadata API для SEO. ВАЖНО: реальный фронтенд этой платформы — не "
        "Next.js, а Create React App (CRA), и курс этого не скрывает. Наоборот, "
        "урок 1 использует настоящий CRA-код платформы (пустой div#root в "
        "frontend/public/index.html, ReactDOM.createRoot в frontend/src/index.js) "
        "как честное сравнение — это реальное, проверяемое обоснование. Сам код "
        "Next.js даётся на реалистичных, рабочих примерах (блог, каталог "
        "товаров). В конце курса — полноценное Next.js-приложение."
    ),
    "instructor_id": 2,
    "difficulty_level": "Advanced",
    "duration_weeks": 5,
    "max_points": 0,  # computed at the bottom of this file from LESSONS
    "category_id": 9,
    "prerequisite_course_id": 43,
    "display_order": 404,
    "image_url": "https://img.icons8.com/color/96/nextjs.png",
    "thumbnail_url": "https://img.icons8.com/color/240/nextjs.png",
    "is_active": True,
    "is_published": False,
}

LESSONS = [
    {
        "order": 0,
        "title": "1-Next.js nima uchun kerak? CRA'ning chegaralari",
        "title_ru": "1-Зачем нужен Next.js? Ограничения CRA",
        "points_reward": 15,
        "text_content": (
            "<h3>Bu platformaning frontend'i qanday ishlaydi?</h3>"
            "<p>React Asoslari kursida siz shu platformaning haqiqiy frontend kodini "
            "ko'rgansiz: <code>frontend/public/index.html</code> faylida bitta bo'sh "
            "<code>&lt;div id=\"root\"&gt;&lt;/div&gt;</code> bor, va "
            "<code>frontend/src/index.js</code> faylida "
            "<code>ReactDOM.createRoot(document.getElementById('root')).render(&lt;App /&gt;)</code> "
            "chaqiriladi. Bu — Create React App (CRA, <code>react-scripts</code> paketi orqali) "
            "arxitekturasi: server hech qanday HTML render qilmaydi, u faqat bitta deyarli bo'sh "
            "sahifa va JavaScript bundle'ni (<code>bundle.js</code>) jo'natadi. Sahifani "
            "to'ldirish — butunlay brauzer ishi. <code>frontend/src/App.js</code> esa "
            "hammasini <code>react-router-dom</code>'ning <code>&lt;BrowserRouter&gt;</code> "
            "komponenti ichiga o'raydi — marshrutlash ham 100% mijoz tomonida ishlaydi.</p>"
            "<p>Bu yondashuv login talab qiladigan platformalar uchun (aynan shu platforma kabi) "
            "juda yaxshi ishlaydi: foydalanuvchi baribir tizimga kirishi kerak, qidiruv botlari "
            "esa login sahifasidan nariga o'tolmaydi, shuning uchun SEO masalasi deyarli "
            "ahamiyatsiz. Lekin bu arxitekturaning aniq chegaralari bor, va aynan o'sha "
            "chegaralar — Next.js nima uchun yaratilganini tushuntiradi.</p>"
            "<h3>CRA'ning uchta real chegarasi</h3>"
            "<p><strong>1. Bo'sh sahifa muammosi.</strong> Brauzer serverdan HTML so'raganda, "
            "u deyarli bo'sh javob oladi — faqat <code>&lt;div id=\"root\"&gt;&lt;/div&gt;</code>. "
            "Foydalanuvchi biror narsa ko'rishi uchun avval butun JS bundle yuklanishi, keyin "
            "brauzerda ishga tushishi, keyin React komponentlarni render qilishi kerak. Sekin "
            "internetda yoki eski qurilmada bu — uzoq davom etadigan oq ekran sifatida seziladi.</p>"
            "<p><strong>2. SEO va meta teglar muammosi.</strong> "
            "<code>frontend/public/index.html</code>dagi <code>&lt;title&gt;Gennis Tech&lt;/title&gt;</code> "
            "va <code>&lt;meta name=\"description\" content=\"Gennis Tech — IT ta'lim platformasi\"&gt;</code> "
            "— bitta, statik, butun sayt uchun umumiy teglar. Foydalanuvchi qaysi sahifaga "
            "kirmasin, brauzer tab sarlavhasi va qidiruv natijasidagi tavsif bir xil bo'lib "
            "qoladi. Har bir sahifa uchun alohida sarlavha yozish qo'shimcha kutubxona "
            "(masalan, <code>react-helmet</code>) talab qiladi, va hatto shunda ham bu teglar "
            "faqat JS ishga tushgandan KEYIN paydo bo'ladi.</p>"
            "<p><strong>3. Qo'lda code splitting va server-side ma'lumot yo'qligi.</strong> "
            "CRA'da <code>React.lazy()</code> va <code>&lt;Suspense&gt;</code> orqali bundle'ni "
            "bo'laklarga bo'lish mumkin, lekin bu — dasturchining qo'lda qiladigan ishi. Server "
            "esa \"bu URL qanday sahifa\" degan tushunchaga umuman ega emas — u har qanday yo'l "
            "uchun bir xil <code>index.html</code>'ni qaytaradi, qolgan hamma narsani brauzer hal qiladi.</p>"
            "<h3>Next.js nimani boshqacha qiladi?</h3>"
            "<p>Next.js — React ustiga qurilgan freymvork (shunchaki kutubxona emas). Uning "
            "asosiy g'oyasi: <strong>komponentlar server'da ham render bo'lishi mumkin</strong>. "
            "Server so'rovni qabul qiladi, kerakli komponentlarni ishga tushiradi, ularni "
            "to'liq HTML'ga aylantiradi va shuni brauzerga jo'natadi. Brauzer darhol tayyor "
            "HTML'ni ko'rsatadi — JS hali yuklanmagan bo'lsa ham, foydalanuvchi matn va "
            "rasmlarni ko'radi. Bundan tashqari, Next.js marshrutlashni <strong>fayl "
            "tizimidan</strong> avtomatik quradi (2-darsda ko'ramiz), har bir sahifa uchun "
            "alohida meta teglar yozish imkonini beradi (Metadata API — 11-darsda), va code "
            "splitting'ni marshrut darajasida avtomatik qiladi.</p>"
            "<h3>Diagram: ikki arxitekturaning so'rov hayoti</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  subgraph CRA[\"CRA (shu platforma) - GET /courses\"]\n"
            "    A1[\"Brauzer so'rov yuboradi\"] --> A2[\"Server: bo'sh index.html\n"
            "div#root ichi bo'sh\"]\n"
            "    A2 --> A3[\"Brauzer bundle.js'ni yuklaydi\"]\n"
            "    A3 --> A4[\"ReactDOM.createRoot ishga tushadi\"]\n"
            "    A4 --> A5[\"Komponentlar render bo'ladi\n"
            "foydalanuvchi UI'ni ko'radi\"]\n"
            "  end\n"
            "  subgraph NEXTJS[\"Next.js - GET /courses\"]\n"
            "    B1[\"Brauzer so'rov yuboradi\"] --> B2[\"Server: Server Component\n"
            "darhol to'liq HTML qaytaradi\"]\n"
            "    B2 --> B3[\"Brauzer tayyor HTML'ni\n"
            "zudlik bilan ko'rsatadi\"]\n"
            "    B3 --> B4[\"JS yuklanadi\n"
            "interaktivlik (hydration) qo'shiladi\"]\n"
            "  end\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: CRA'da foydalanuvchi hech narsa ko'rmasdan turib "
            "to'rtta qadam kutadi, Next.js'da esa uchinchi qadamdayoq (B3) tayyor mazmun "
            "ko'rinadi — JS hali orqadan yuklanmoqda bo'lsa ham.</p>"
            "<h3>Bu kursda nimalarni o'rganamiz</h3>"
            "<p>Next.js — React'dan keyingi eng talab qilinadigan ko'nikma. Ushbu kursda App "
            "Router, Server va Client Component'lar orasidagi farq, ma'lumot olish "
            "strategiyalari, render strategiyalari (SSR/SSG/ISR), Route Handler'lar, dinamik "
            "marshrutlar, Middleware, rasm/shrift optimallashtirish, SEO uchun Metadata API va "
            "deploy masalalarini bosqichma-bosqich ko'rib chiqamiz. Kurs oxirida haqiqiy "
            "to'liq-stack Next.js ilova (blog yoki mahsulotlar katalogi) qurasiz.</p>"
        ),
        "text_content_ru": (
            "<h3>Как устроен фронтенд этой платформы?</h3>"
            "<p>В курсе «React Asoslari» вы видели настоящий код фронтенда этой платформы: "
            "в файле <code>frontend/public/index.html</code> есть один пустой "
            "<code>&lt;div id=\"root\"&gt;&lt;/div&gt;</code>, а в "
            "<code>frontend/src/index.js</code> вызывается "
            "<code>ReactDOM.createRoot(document.getElementById('root')).render(&lt;App /&gt;)</code>. "
            "Это архитектура Create React App (CRA, через пакет <code>react-scripts</code>): "
            "сервер не рендерит никакого HTML, он лишь отдаёт почти пустую страницу и "
            "JavaScript-бандл (<code>bundle.js</code>). Заполнение страницы — целиком работа "
            "браузера. А <code>frontend/src/App.js</code> оборачивает всё в "
            "<code>&lt;BrowserRouter&gt;</code> из <code>react-router-dom</code> — маршрутизация "
            "тоже на 100% работает на клиенте.</p>"
            "<p>Такой подход отлично работает для платформ, требующих входа в систему (как "
            "и эта платформа): пользователь всё равно должен авторизоваться, а поисковые боты "
            "дальше страницы логина не проходят, поэтому SEO почти не имеет значения. Но у "
            "этой архитектуры есть конкретные ограничения, и именно они объясняют, зачем "
            "появился Next.js.</p>"
            "<h3>Три реальных ограничения CRA</h3>"
            "<p><strong>1. Проблема пустой страницы.</strong> Когда браузер запрашивает HTML у "
            "сервера, он получает почти пустой ответ — только "
            "<code>&lt;div id=\"root\"&gt;&lt;/div&gt;</code>. Прежде чем пользователь что-то "
            "увидит, должен загрузиться весь JS-бандл, запуститься в браузере, и только потом "
            "React отрендерит компоненты. На медленном интернете или старом устройстве это "
            "ощущается как долгий белый экран.</p>"
            "<p><strong>2. Проблема SEO и мета-тегов.</strong> "
            "<code>&lt;title&gt;Gennis Tech&lt;/title&gt;</code> и "
            "<code>&lt;meta name=\"description\" content=\"Gennis Tech — IT ta'lim platformasi\"&gt;</code> "
            "в <code>frontend/public/index.html</code> — единственные, статичные теги для всего "
            "сайта. На какую бы страницу пользователь ни зашёл, заголовок вкладки браузера и "
            "описание в поисковой выдаче остаются одинаковыми. Для отдельного заголовка на "
            "каждой странице нужна дополнительная библиотека (например, <code>react-helmet</code>), "
            "и даже тогда эти теги появляются только ПОСЛЕ запуска JS.</p>"
            "<p><strong>3. Ручное разделение кода и отсутствие серверных данных.</strong> В CRA "
            "можно разбить бандл на части через <code>React.lazy()</code> и "
            "<code>&lt;Suspense&gt;</code>, но это — ручная работа разработчика. Сервер вообще "
            "не имеет понятия, «какой URL — какая страница»: он отдаёт один и тот же "
            "<code>index.html</code> для любого пути, а всё остальное решает браузер.</p>"
            "<h3>Что Next.js делает иначе?</h3>"
            "<p>Next.js — это фреймворк поверх React (а не просто библиотека). Его главная "
            "идея: <strong>компоненты могут рендериться и на сервере</strong>. Сервер принимает "
            "запрос, запускает нужные компоненты, превращает их в готовый HTML и отправляет "
            "его браузеру. Браузер сразу показывает готовый HTML — даже если JS ещё не "
            "загрузился, пользователь видит текст и изображения. Кроме того, Next.js "
            "автоматически строит маршрутизацию <strong>из файловой системы</strong> (урок 2), "
            "позволяет писать отдельные мета-теги для каждой страницы (Metadata API — урок 11) "
            "и автоматически делает code splitting на уровне маршрутов.</p>"
            "<h3>Диаграмма: жизненный цикл запроса в двух архитектурах</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  subgraph CRA[\"CRA (эта платформа) - GET /courses\"]\n"
            "    A1[\"Браузер отправляет запрос\"] --> A2[\"Сервер: пустой index.html\n"
            "внутри div#root ничего нет\"]\n"
            "    A2 --> A3[\"Браузер загружает bundle.js\"]\n"
            "    A3 --> A4[\"Запускается ReactDOM.createRoot\"]\n"
            "    A4 --> A5[\"Компоненты рендерятся\n"
            "пользователь видит UI\"]\n"
            "  end\n"
            "  subgraph NEXTJS[\"Next.js - GET /courses\"]\n"
            "    B1[\"Браузер отправляет запрос\"] --> B2[\"Сервер: Server Component\n"
            "сразу возвращает готовый HTML\"]\n"
            "    B2 --> B3[\"Браузер немедленно\n"
            "показывает готовый HTML\"]\n"
            "    B3 --> B4[\"Загружается JS\n"
            "добавляется интерактивность (hydration)\"]\n"
            "  end\n"
            "</pre>"
            "<p>Диаграмма показывает: в CRA пользователь ждёт четыре шага, ничего не видя, а в "
            "Next.js уже на третьем шаге (B3) виден готовый контент — даже пока JS ещё "
            "загружается в фоне.</p>"
            "<h3>Что мы изучим в этом курсе</h3>"
            "<p>Next.js — самый востребованный навык после React. В этом курсе мы поэтапно "
            "разберём App Router, разницу между Server и Client Component, стратегии получения "
            "данных, стратегии рендеринга (SSR/SSG/ISR), Route Handler'ы, динамические "
            "маршруты, Middleware, оптимизацию изображений/шрифтов, Metadata API для SEO и "
            "вопросы деплоя. В конце курса вы соберёте настоящее полноценное Next.js-приложение "
            "(блог или каталог товаров).</p>"
        ),
        "code_content": (
            "// ===== frontend/src/index.js (HAQIQIY — shu platforma, CRA) =====\n"
            "import ReactDOM from 'react-dom/client';\n"
            "import App from './App';\n"
            "\n"
            "const root = ReactDOM.createRoot(document.getElementById('root'));\n"
            "root.render(<App />); // <-- HAMMA render ishi shu yerda, brauzerda boshlanadi\n"
            "\n"
            "// ===== frontend/src/App.js (HAQIQIY — soddalashtirilgan) =====\n"
            "import { BrowserRouter, Routes, Route } from 'react-router-dom';\n"
            "import { useState, useEffect } from 'react';\n"
            "import CoursesPage from './pages/CoursesPage';\n"
            "\n"
            "export default function App() {\n"
            "  return (\n"
            "    <BrowserRouter>\n"
            "      <Routes>\n"
            "        <Route path=\"/courses\" element={<CoursesPage />} />\n"
            "      </Routes>\n"
            "    </BrowserRouter>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== frontend/src/pages/CoursesPage.js (HAQIQIY naqsh — CRA'da yagona yo'l) =====\n"
            "function CoursesPage() {\n"
            "  const [courses, setCourses] = useState(null); // boshida bo'sh\n"
            "  const [loading, setLoading] = useState(true);\n"
            "\n"
            "  useEffect(() => {\n"
            "    // Render bo'lgandan KEYIN, brauzerda ishga tushadi\n"
            "    fetch('/api/courses')\n"
            "      .then((r) => r.json())\n"
            "      .then((data) => {\n"
            "        setCourses(data);\n"
            "        setLoading(false);\n"
            "      });\n"
            "  }, []);\n"
            "\n"
            "  if (loading) return <p>Yuklanmoqda...</p>; // foydalanuvchi buni ko'radi\n"
            "  return (\n"
            "    <ul>\n"
            "      {courses.map((c) => <li key={c.id}>{c.title}</li>)}\n"
            "    </ul>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===================================================================\n"
            "// Next.js'da MOS KELADIGAN fayl: app/courses/page.js\n"
            "// Bu — Server Component (default holat, hech qanday direktiva kerak emas)\n"
            "// ===================================================================\n"
            "async function getCourses() {\n"
            "  const res = await fetch('https://api.example.com/courses');\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function CoursesPage() {\n"
            "  // Bu funksiya SERVERDA ishlaydi va tayyor HTML qaytaradi.\n"
            "  // Hech qanday useState/useEffect/\"loading\" holati kerak emas —\n"
            "  // ma'lumot render BOSHLANISHIDAN OLDIN allaqachon tayyor.\n"
            "  const courses = await getCourses();\n"
            "\n"
            "  return (\n"
            "    <ul>\n"
            "      {courses.map((c) => <li key={c.id}>{c.title}</li>)}\n"
            "    </ul>\n"
            "  );\n"
            "}\n"
            "\n"
            "// XATO YO'L (CRA odatini Server Component'ga ko'chirish — ISHLAMAYDI):\n"
            "// export default function CoursesPage() {\n"
            "//   const [courses, setCourses] = useState(null); // ❌ useState serverda yo'q\n"
            "//   useEffect(() => { ... }, []);                 // ❌ useEffect serverda yo'q\n"
            "//   ...\n"
            "// }\n"
            "// Server Component'da useState/useEffect ishlatib bo'lmaydi — ular faqat\n"
            "// brauzerda ma'noga ega tushunchalar (4-darsda batafsil ko'ramiz).\n"
            "//\n"
            "// BANDLE HAJMI: getCourses() funksiyasi va uning tanasi Next.js versiyasida\n"
            "// brauzer JS bandle'iga HECH QACHON tushmaydi — ular faqat serverda mavjud.\n"
            "// CRA versiyasida esa BUTUN CoursesPage.js fayli (useEffect/fetch mantig'i\n"
            "// bilan birga) bundle.js'ga kompilyatsiya qilinadi va har bir foydalanuvchi\n"
            "// tomonidan yuklab olinadi.\n"
            "\n"
            "// Aralash holat: agar shu sahifada bitta interaktiv qism kerak bo'lsa\n"
            "// (masalan, \"Yangilash\" tugmasi), faqat O'SHA qism alohida faylga\n"
            "// chiqariladi va 'use client' bilan belgilanadi — qolgan hamma narsa\n"
            "// (ro'yxatning o'zi) Server Component bo'lib qoladi (4-darsda chuqur ko'ramiz):\n"
            "// app/courses/RefreshButton.js\n"
            "// 'use client';\n"
            "// import { useState } from 'react';\n"
            "// export default function RefreshButton() {\n"
            "//   const [spinning, setSpinning] = useState(false);\n"
            "//   return (\n"
            "//     <button onClick={() => { setSpinning(true); location.reload(); }}>\n"
            "//       {spinning ? 'Yangilanmoqda...' : \"Ro'yxatni yangilash\"}\n"
            "//     </button>\n"
            "//   );\n"
            "// }\n"
        ),
        "code_content_ru": (
            "// ===== frontend/src/index.js (РЕАЛЬНО — эта платформа, CRA) =====\n"
            "import ReactDOM from 'react-dom/client';\n"
            "import App from './App';\n"
            "\n"
            "const root = ReactDOM.createRoot(document.getElementById('root'));\n"
            "root.render(<App />); // <-- ВСЯ работа рендеринга начинается тут, в браузере\n"
            "\n"
            "// ===== frontend/src/App.js (РЕАЛЬНО — упрощённо) =====\n"
            "import { BrowserRouter, Routes, Route } from 'react-router-dom';\n"
            "import { useState, useEffect } from 'react';\n"
            "import CoursesPage from './pages/CoursesPage';\n"
            "\n"
            "export default function App() {\n"
            "  return (\n"
            "    <BrowserRouter>\n"
            "      <Routes>\n"
            "        <Route path=\"/courses\" element={<CoursesPage />} />\n"
            "      </Routes>\n"
            "    </BrowserRouter>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== frontend/src/pages/CoursesPage.js (РЕАЛЬНЫЙ паттерн — единственный путь в CRA) =====\n"
            "function CoursesPage() {\n"
            "  const [courses, setCourses] = useState(null); // изначально пусто\n"
            "  const [loading, setLoading] = useState(true);\n"
            "\n"
            "  useEffect(() => {\n"
            "    // Выполняется ПОСЛЕ рендера, в браузере\n"
            "    fetch('/api/courses')\n"
            "      .then((r) => r.json())\n"
            "      .then((data) => {\n"
            "        setCourses(data);\n"
            "        setLoading(false);\n"
            "      });\n"
            "  }, []);\n"
            "\n"
            "  if (loading) return <p>Загрузка...</p>; // это видит пользователь\n"
            "  return (\n"
            "    <ul>\n"
            "      {courses.map((c) => <li key={c.id}>{c.title}</li>)}\n"
            "    </ul>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===================================================================\n"
            "// СООТВЕТСТВУЮЩИЙ файл в Next.js: app/courses/page.js\n"
            "// Это Server Component (состояние по умолчанию, директива не нужна)\n"
            "// ===================================================================\n"
            "async function getCourses() {\n"
            "  const res = await fetch('https://api.example.com/courses');\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function CoursesPage() {\n"
            "  // Эта функция выполняется на СЕРВЕРЕ и возвращает готовый HTML.\n"
            "  // useState/useEffect/состояние \"загрузка\" не нужны —\n"
            "  // данные готовы ДО НАЧАЛА рендера.\n"
            "  const courses = await getCourses();\n"
            "\n"
            "  return (\n"
            "    <ul>\n"
            "      {courses.map((c) => <li key={c.id}>{c.title}</li>)}\n"
            "    </ul>\n"
            "  );\n"
            "}\n"
            "\n"
            "// НЕПРАВИЛЬНЫЙ ПУТЬ (перенос привычки CRA в Server Component — НЕ РАБОТАЕТ):\n"
            "// export default function CoursesPage() {\n"
            "//   const [courses, setCourses] = useState(null); // ❌ useState нет на сервере\n"
            "//   useEffect(() => { ... }, []);                 // ❌ useEffect нет на сервере\n"
            "//   ...\n"
            "// }\n"
            "// В Server Component нельзя использовать useState/useEffect — это понятия,\n"
            "// имеющие смысл только в браузере (подробно разберём в уроке 4).\n"
            "//\n"
            "// РАЗМЕР БАНДЛА: функция getCourses() и её тело НИКОГДА не попадают в\n"
            "// JS-бандл браузера в Next.js-версии — они существуют только на сервере.\n"
            "// В CRA-версии ВЕСЬ файл CoursesPage.js (включая useEffect/fetch-логику)\n"
            "// компилируется в bundle.js и скачивается каждым пользователем.\n"
            "\n"
            "// Смешанный случай: если на этой странице нужна одна интерактивная часть\n"
            "// (например, кнопка «Обновить»), только ЭТА часть выносится в отдельный\n"
            "// файл и помечается 'use client' — всё остальное (сам список) остаётся\n"
            "// Server Component (подробно разберём в уроке 4):\n"
            "// app/courses/RefreshButton.js\n"
            "// 'use client';\n"
            "// import { useState } from 'react';\n"
            "// export default function RefreshButton() {\n"
            "//   const [spinning, setSpinning] = useState(false);\n"
            "//   return (\n"
            "//     <button onClick={() => { setSpinning(true); location.reload(); }}>\n"
            "//       {spinning ? 'Обновляется...' : 'Обновить список'}\n"
            "//     </button>\n"
            "//   );\n"
            "// }\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Solishtirish jadvali: CRA vs Next.js",
            "task_title_ru": "Таблица сравнения: CRA vs Next.js",
            "task_description": (
                "Ushbu platformaning frontend kodini (frontend/public/index.html, "
                "frontend/src/index.js, frontend/src/App.js) o'zingiz o'qib chiqing va "
                "kamida 5 qatorli solishtirish jadvali tayyorlang: har bir qatorda bitta "
                "xususiyat (masalan, 'boshlang'ich HTML', 'marshrutlash', 'SEO meta teglar') "
                "va uning CRA'da qanday ishlashi hamda Next.js'da qanday ishlashi yozilgan "
                "bo'lsin."
            ),
            "task_description_ru": (
                "Изучите фронтенд-код этой платформы (frontend/public/index.html, "
                "frontend/src/index.js, frontend/src/App.js) и подготовьте таблицу "
                "сравнения минимум из 5 строк: в каждой строке — одна характеристика "
                "(например, «начальный HTML», «маршрутизация», «SEO мета-теги») и то, как "
                "она работает в CRA и как в Next.js."
            ),
            "task_requirements": (
                "Jadvalda kamida: boshlang'ich HTML, marshrutlash, SEO, code splitting va "
                "render joyi (server/brauzer) qatorlari bo'lishi kerak. Har bir CRA ustuni "
                "shu platformaning haqiqiy fayllariga asoslangan bo'lishi shart."
            ),
            "task_requirements_ru": (
                "В таблице обязательны минимум: начальный HTML, маршрутизация, SEO, code "
                "splitting и место рендеринга (сервер/браузер). Каждая колонка CRA должна "
                "основываться на реальных файлах этой платформы."
            ),
            "task_technologies": "Markdown, Next.js, React",
            "task_deadline_days": 4,
        },
        "sample": {
            "title": "Namuna: bir xil sahifa, ikki arxitektura",
            "description": (
                "Chap tomonda — shu platformaning haqiqiy CRA yondashuvi (soddalashtirilgan), "
                "o'ng tomonda — xuddi shu sahifaning Next.js Server Component sifatidagi "
                "ko'rinishi."
            ),
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "cra-index.js",
                    "language": "javascript",
                    "code": (
                        "// CRA: frontend/src/index.js uslubi\n"
                        "import ReactDOM from 'react-dom/client';\n"
                        "import App from './App';\n\n"
                        "ReactDOM.createRoot(document.getElementById('root')).render(<App />);\n"
                        "// Bu yerda hali hech qanday HTML tayyor emas —\n"
                        "// server faqat bo'sh div#root'ni jo'natgan edi.\n"
                    ),
                },
                {
                    "filename": "app/page.js",
                    "language": "jsx",
                    "code": (
                        "// Next.js: app/page.js — Server Component\n"
                        "export default async function HomePage() {\n"
                        "  return (\n"
                        "    <main>\n"
                        "      <h1>Kurslar platformasi</h1>\n"
                        "      <p>Bu matn server tomonda render qilingan HTML ichida keladi.</p>\n"
                        "    </main>\n"
                        "  );\n"
                        "}\n"
                    ),
                },
            ],
        },
        "exercises": [
            {
                "title": "CRA'da server nimani qaytaradi?",
                "title_ru": "Что возвращает сервер в CRA?",
                "description": (
                    "Shu platformaning CRA arxitekturasida server brauzerga GET / so'rovi "
                    "uchun nima qaytaradi?"
                ),
                "description_ru": (
                    "В архитектуре CRA этой платформы что сервер возвращает браузеру на "
                    "запрос GET /?"
                ),
                "exercise_type": "multiple_choice",
                "options": [
                    "To'liq render qilingan HTML, barcha matn va rasmlar bilan",
                    "Ichida bo'sh div#root bo'lgan minimal index.html",
                    "Faqat JSON ma'lumot",
                    "404 xatolik, chunki server marshrutlarni bilmaydi",
                ],
                "options_ru": [
                    "Полностью отрендеренный HTML со всем текстом и изображениями",
                    "Минимальный index.html с пустым div#root внутри",
                    "Только JSON-данные",
                    "Ошибку 404, потому что сервер не знает о маршрутах",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "frontend/public/index.html faylini eslang.",
                "hint_ru": "Вспомните файл frontend/public/index.html.",
                "explanation": (
                    "CRA'da server faqat bitta statik index.html'ni qaytaradi, uning ichida "
                    "bo'sh div#root bor — hamma render ishi brauzerda, JS ishga tushgandan "
                    "keyin bo'ladi."
                ),
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Server tomonida render qilinadigan komponent",
                "title_ru": "Компонент, рендерящийся на сервере",
                "description": (
                    "Bo'shliqni to'ldiring: Next.js'da server tomonida render qilingan "
                    "komponentlar ___ Component deb ataladi (bu — default holat)."
                ),
                "description_ru": (
                    "Заполните пропуск: в Next.js компоненты, рендерящиеся на сервере, "
                    "называются ___ Component (это состояние по умолчанию)."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "Server",
                "hint": "Bu — App Router'dagi barcha komponentlarning default turi.",
                "hint_ru": "Это тип по умолчанию для всех компонентов в App Router.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "CRA so'rov hayotini tartiblang",
                "title_ru": "Расставьте по порядку жизненный цикл запроса CRA",
                "description": (
                    "Shu platformaning CRA arxitekturasida sahifa yuklanishi qadamlarini "
                    "to'g'ri tartibga joylashtiring."
                ),
                "description_ru": (
                    "Расставьте по правильному порядку шаги загрузки страницы в архитектуре "
                    "CRA этой платформы."
                ),
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Brauzer GET so'rovini yuboradi",
                    "Server bo'sh index.html qaytaradi",
                    "Brauzer bundle.js faylini yuklaydi",
                    "ReactDOM komponentlarni render qiladi",
                ],
                "drag_items_ru": [
                    "Браузер отправляет GET-запрос",
                    "Сервер возвращает пустой index.html",
                    "Браузер загружает файл bundle.js",
                    "ReactDOM рендерит компоненты",
                ],
                "correct_order": [
                    "Brauzer GET so'rovini yuboradi",
                    "Server bo'sh index.html qaytaradi",
                    "Brauzer bundle.js faylini yuklaydi",
                    "ReactDOM komponentlarni render qiladi",
                ],
                "hint": "Server hech narsa render qilmaydi — bu oxirgi qadam brauzerda bo'ladi.",
                "hint_ru": "Сервер ничего не рендерит — этот последний шаг происходит в браузере.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 1,
        "title": "2-Fayl asosidagi marshrutlash va App Router",
        "title_ru": "2-Файловая маршрутизация и App Router",
        "points_reward": 15,
        "text_content": (
            "<h3>Marshrutlash konfiguratsiya emas, fayl tizimi</h3>"
            "<p>CRA'da (shu platformaning frontend'ida) marshrutlash <code>react-router-dom</code> "
            "orqali qo'lda yoziladi: <code>&lt;Route path=\"/courses/:id\" element={&lt;CoursePage /&gt;} /&gt;</code> "
            "kabi qatorlarni <code>App.js</code> ichida ro'yxatga olish kerak. Next.js'ning App "
            "Router'ida esa marshrut — bu shunchaki <strong>papka</strong>. Konfiguratsiya "
            "fayli yo'q: <code>app/</code> papkasi ichidagi har bir papka nomi — URL "
            "segmenti, va shu papka ichidagi <code>page.js</code> fayli — o'sha marshrutning "
            "asosiy komponenti.</p>"
            "<h3>Asosiy qoida: page.js papkani marshrutga aylantiradi</h3>"
            "<p><code>app/page.js</code> — bu bosh sahifa (<code>/</code>). "
            "<code>app/courses/page.js</code> — <code>/courses</code>. "
            "<code>app/courses/[id]/page.js</code> — <code>/courses/42</code> kabi dinamik "
            "manzil (kvadrat qavslar — dinamik segment, buni 8-darsda chuqur ko'ramiz). "
            "Muhim nozik joy: agar papkada <code>page.js</code> bo'lmasa, o'sha papka HECH "
            "QANDAY marshrutga ega bo'lmaydi — u faqat ichki papkalarni tashkil qilish uchun "
            "ishlatilishi mumkin.</p>"
            "<h3>Maxsus fayllar — har biri o'z vazifasiga ega</h3>"
            "<p>App Router'da <code>page.js</code>dan tashqari bir nechta \"maxsus fayl\" "
            "konvensiyasi bor, va ularning har biri Next.js tomonidan avtomatik tan olinadi:</p>"
            "<ul>"
            "<li><code>layout.js</code> — shu marshrut va uning barcha bolalari uchun umumiy "
            "UI qatlami (3-darsda batafsil).</li>"
            "<li><code>loading.js</code> — sahifa ma'lumot yuklab bo'lguncha avtomatik "
            "ko'rsatiladigan yuklanish holati (React Suspense asosida).</li>"
            "<li><code>error.js</code> — shu marshrutda xatolik yuz berganda ko'rsatiladigan "
            "chegara (error boundary), albatta Client Component bo'lishi kerak.</li>"
            "<li><code>not-found.js</code> — <code>notFound()</code> chaqirilganda yoki mos "
            "marshrut topilmaganda ko'rsatiladi.</li>"
            "</ul>"
            "<p>Bu fayllarning barchasi ixtiyoriy — faqat <code>page.js</code> majburiy (agar "
            "shu segment uchun ko'rinadigan sahifa kerak bo'lsa).</p>"
            "<h3>Xususiy papkalar va route group'lar</h3>"
            "<p>Nomi pastki chiziq bilan boshlangan papka (masalan <code>_components</code>) "
            "marshrutlashdan butunlay chiqarib tashlanadi — bu yordamchi fayllarni (masalan, "
            "faqat shu bo'limga tegishli kichik komponentlarni) <code>app/</code> ichida "
            "saqlash uchun ishlatiladi, chunki App Router'da har qanday joyga oddiy fayl "
            "qo'yish mumkin, faqat <code>page.js</code> nomli fayllar marshrutga aylanadi. "
            "Route group'lar (nomi qavs ichida, masalan <code>(marketing)</code>) esa "
            "boshqacha ishlaydi — ular URL'ga umuman ta'sir qilmaydi, faqat loyihani mantiqiy "
            "guruhlarga bo'lish uchun ishlatiladi (masalan, <code>(marketing)</code> va "
            "<code>(dashboard)</code> guruhlari alohida root layout'larga ega bo'lishi mumkin). "
            "Route group'larni 3-darsda chuqurroq ko'ramiz.</p>"
            "<h3>Diagram: fayl tizimidan URL'ga</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart LR\n"
            "  A[\"app/\"] --> B[\"page.js\n"
            "= /\"]\n"
            "  A --> C[\"courses/\"]\n"
            "  C --> D[\"page.js\n"
            "= /courses\"]\n"
            "  C --> E[\"[id]/\"]\n"
            "  E --> F[\"page.js\n"
            "= /courses/42\"]\n"
            "  A --> G[\"_components/\n"
            "(marshrutga aylanmaydi)\"]\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: <code>page.js</code> bo'lgan har bir papka — "
            "ko'rinadigan URL, <code>_components</code> kabi pastki chiziqli papka esa "
            "marshrutlashda umuman ishtirok etmaydi.</p>"
            "<h3>Nega bu muhim</h3>"
            "<p>CRA'da marshrutlar ro'yxati qayerda ekanligini bilish uchun <code>App.js</code>ni "
            "o'qish kerak edi. Next.js'da esa <code>app/</code> papkasining o'zi — to'liq "
            "marshrutlar xaritasi. Katta loyihalarda bu katta farq: yangi dasturchi papka "
            "tuzilishiga qarab, qaysi URL qayerda ekanligini darhol tushunadi, hech qanday "
            "konfiguratsiya faylini qidirib yurmasdan.</p>"
            "<h3>Colocation: yordamchi fayllarni marshrut yonida saqlash</h3>"
            "<p>CRA'da odatda barcha komponentlar <code>src/components/</code> papkasida, "
            "sahifalar esa alohida joyda saqlanadi — bitta sahifaga tegishli yordamchi "
            "komponent ham, umumiy komponent ham bir xil umumiy joyda yashaydi. Next.js App "
            "Router'da esa \"colocation\" tamoyili qo'llab-quvvatlanadi: faqat <code>page.js</code>, "
            "<code>layout.js</code> kabi maxsus nomli fayllar marshrutga aylangani uchun, "
            "istalgan boshqa nomdagi faylni (masalan <code>CourseCard.js</code>, "
            "<code>utils.js</code>, hatto <code>page.test.js</code>) xuddi shu "
            "<code>courses/</code> papkasi ichiga qo'yish mumkin — u marshrutlashga hech qanday "
            "ta'sir qilmaydi. Bu degani: bitta marshrutga tegishli hamma narsa (komponent, "
            "uslub, test) bir joyda, uzoq umumiy <code>components/</code> papkasini titkilamasdan "
            "turib topiladi.</p>"
        ),
        "text_content_ru": (
            "<h3>Маршрутизация — это не конфигурация, а файловая система</h3>"
            "<p>В CRA (фронтенде этой платформы) маршрутизация пишется вручную через "
            "<code>react-router-dom</code>: нужно регистрировать строки вроде "
            "<code>&lt;Route path=\"/courses/:id\" element={&lt;CoursePage /&gt;} /&gt;</code> "
            "внутри <code>App.js</code>. В App Router Next.js маршрут — это просто "
            "<strong>папка</strong>. Файла конфигурации нет: каждое имя папки внутри "
            "<code>app/</code> — это сегмент URL, а файл <code>page.js</code> внутри неё — "
            "основной компонент этого маршрута.</p>"
            "<h3>Главное правило: page.js превращает папку в маршрут</h3>"
            "<p><code>app/page.js</code> — это главная страница (<code>/</code>). "
            "<code>app/courses/page.js</code> — <code>/courses</code>. "
            "<code>app/courses/[id]/page.js</code> — динамический адрес вроде "
            "<code>/courses/42</code> (квадратные скобки — динамический сегмент, подробно "
            "разберём в уроке 8). Важный нюанс: если в папке нет <code>page.js</code>, у этой "
            "папки НЕТ никакого маршрута — она может использоваться только для организации "
            "вложенных папок.</p>"
            "<h3>Специальные файлы — у каждого своя роль</h3>"
            "<p>Кроме <code>page.js</code>, в App Router есть несколько «специальных файлов», "
            "которые Next.js распознаёт автоматически:</p>"
            "<ul>"
            "<li><code>layout.js</code> — общий слой UI для этого маршрута и всех его "
            "потомков (подробно в уроке 3).</li>"
            "<li><code>loading.js</code> — состояние загрузки, показываемое автоматически, "
            "пока страница ждёт данные (на основе React Suspense).</li>"
            "<li><code>error.js</code> — граница ошибки для этого маршрута, обязательно "
            "должен быть Client Component.</li>"
            "<li><code>not-found.js</code> — показывается при вызове <code>notFound()</code> "
            "или когда подходящий маршрут не найден.</li>"
            "</ul>"
            "<p>Все эти файлы необязательны — обязателен только <code>page.js</code> (если для "
            "этого сегмента вообще нужна видимая страница).</p>"
            "<h3>Приватные папки и route group'ы</h3>"
            "<p>Папка с именем, начинающимся с подчёркивания (например "
            "<code>_components</code>), полностью исключается из маршрутизации — так удобно "
            "хранить вспомогательные файлы (например, мелкие компоненты, относящиеся только к "
            "этому разделу) прямо внутри <code>app/</code>, ведь маршрутом становится только "
            "файл с именем <code>page.js</code>. Route group'ы (имя в скобках, например "
            "<code>(marketing)</code>) работают иначе — они вообще не влияют на URL, а служат "
            "только для логической группировки проекта (например, у групп "
            "<code>(marketing)</code> и <code>(dashboard)</code> могут быть разные корневые "
            "layout'ы). Разберём route group'ы подробнее в уроке 3.</p>"
            "<h3>Диаграмма: от файловой системы к URL</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart LR\n"
            "  A[\"app/\"] --> B[\"page.js\n"
            "= /\"]\n"
            "  A --> C[\"courses/\"]\n"
            "  C --> D[\"page.js\n"
            "= /courses\"]\n"
            "  C --> E[\"[id]/\"]\n"
            "  E --> F[\"page.js\n"
            "= /courses/42\"]\n"
            "  A --> G[\"_components/\n"
            "(не становится маршрутом)\"]\n"
            "</pre>"
            "<p>Диаграмма показывает: каждая папка с <code>page.js</code> — видимый URL, а "
            "папка с подчёркиванием вроде <code>_components</code> вообще не участвует в "
            "маршрутизации.</p>"
            "<h3>Почему это важно</h3>"
            "<p>В CRA, чтобы узнать список маршрутов, нужно было читать <code>App.js</code>. В "
            "Next.js сама папка <code>app/</code> — это уже полная карта маршрутов. В крупных "
            "проектах это большая разница: новый разработчик сразу понимает, какой URL где "
            "находится, просто глядя на структуру папок, без поиска файла конфигурации.</p>"
            "<h3>Colocation: хранение вспомогательных файлов рядом с маршрутом</h3>"
            "<p>В CRA обычно все компоненты хранятся в <code>src/components/</code>, а страницы "
            "— в отдельном месте: и вспомогательный компонент для одной страницы, и общий "
            "компонент живут в одном общем месте. В App Router Next.js поддерживается принцип "
            "«colocation»: поскольку маршрутом становятся только файлы со специальными именами "
            "вроде <code>page.js</code>, <code>layout.js</code>, любой файл с другим именем "
            "(например, <code>CourseCard.js</code>, <code>utils.js</code>, даже "
            "<code>page.test.js</code>) можно положить прямо в ту же папку <code>courses/</code> "
            "— на маршрутизацию это никак не повлияет. Это значит: всё, что относится к одному "
            "маршруту (компонент, стили, тесты), находится в одном месте, без необходимости "
            "рыться в длинной общей папке <code>components/</code>.</p>"
            "<p>Это не запрещает по-прежнему держать по-настоящему общие компоненты (кнопки, "
            "карточки, используемые на многих страницах) в отдельной папке верхнего уровня — "
            "colocation просто даёт выбор: то, что нужно только одному маршруту, можно хранить "
            "рядом с ним, а не тащить в общее пространство «на всякий случай».</p>"
        ),
        "code_content": (
            "// ===== To'liq blog fayl tuzilishi -> URL xaritasi =====\n"
            "app/\n"
            "  page.js                    // GET /\n"
            "  layout.js                  // umumiy UI (barcha sahifalar uchun)\n"
            "  about/\n"
            "    page.js                  // GET /about\n"
            "  blog/\n"
            "    page.js                  // GET /blog\n"
            "    loading.js               // /blog yuklanayotganda ko'rinadi\n"
            "    _components/             // pastki chiziq -> marshrutga aylanmaydi\n"
            "      PostCard.js            // faqat shu bo'lim ichida ishlatiladi\n"
            "    [slug]/\n"
            "      page.js                // GET /blog/nextjs-asoslari, /blog/app-router, ...\n"
            "      not-found.js           // post topilmasa\n"
            "\n"
            "// ===== app/blog/page.js — postlar ro'yxati =====\n"
            "import PostCard from './_components/PostCard';\n"
            "\n"
            "async function getPosts() {\n"
            "  const res = await fetch('https://api.example.com/posts');\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function BlogListPage() {\n"
            "  const posts = await getPosts();\n"
            "  return (\n"
            "    <section>\n"
            "      <h1>Barcha postlar</h1>\n"
            "      <ul>\n"
            "        {posts.map((post) => (\n"
            "          <li key={post.slug}>\n"
            "            <PostCard post={post} />\n"
            "          </li>\n"
            "        ))}\n"
            "      </ul>\n"
            "    </section>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/blog/_components/PostCard.js — colocation namunasi =====\n"
            "// next/link ishlatiladi (oddiy <a> emas) — sahifa TO'LIQ qayta\n"
            "// yuklanmasdan, faqat kerakli qism almashadi (client-side navigatsiya)\n"
            "import Link from 'next/link';\n"
            "\n"
            "export default function PostCard({ post }) {\n"
            "  return (\n"
            "    <Link href={`/blog/${post.slug}`}>\n"
            "      <h3>{post.title}</h3>\n"
            "      <p>{post.excerpt}</p>\n"
            "    </Link>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/blog/layout.js — /blog bo'limi uchun qo'shimcha nested layout =====\n"
            "// (root layout ustiga qo'shiladi — 3-darsda ichma-ich layout'larni\n"
            "// chuqur ko'ramiz, bu yerda faqat fayl qanday joylashishini ko'rsatamiz)\n"
            "import Link from 'next/link';\n"
            "\n"
            "export default function BlogLayout({ children }) {\n"
            "  return (\n"
            "    <div className=\"blog-shell\">\n"
            "      <nav><Link href=\"/blog\">Barcha postlar</Link></nav>\n"
            "      {children}\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/blog/[slug]/page.js — dinamik segment =====\n"
            "import { notFound } from 'next/navigation';\n"
            "\n"
            "async function getPost(slug) {\n"
            "  const res = await fetch(`https://api.example.com/posts/${slug}`);\n"
            "  if (res.status === 404) return null;\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function PostPage({ params }) {\n"
            "  const { slug } = await params; // params — Promise, shuning uchun await\n"
            "  const post = await getPost(slug);\n"
            "\n"
            "  if (!post) notFound(); // -> not-found.js'ni ko'rsatadi\n"
            "\n"
            "  return (\n"
            "    <article>\n"
            "      <h1>{post.title}</h1>\n"
            "      <div>{post.body}</div>\n"
            "    </article>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/blog/[slug]/not-found.js =====\n"
            "export default function PostNotFound() {\n"
            "  return <p>Bunday post topilmadi. Boshqa slug bilan urinib ko'ring.</p>;\n"
            "}\n"
            "\n"
            "// ===== app/blog/loading.js — /blog yuklanayotganda avtomatik ko'rinadi =====\n"
            "export default function BlogLoading() {\n"
            "  return <p>Postlar yuklanmoqda...</p>;\n"
            "}\n"
            "\n"
            "// ===== app/about/page.js — oddiy statik marshrut =====\n"
            "export default function AboutPage() {\n"
            "  return (\n"
            "    <section>\n"
            "      <h1>Biz haqimizda</h1>\n"
            "      <p>Bu — Next.js'ni real misollarda o'rgatadigan kurs blogi.</p>\n"
            "    </section>\n"
            "  );\n"
            "}\n"
        ),
        "code_content_ru": (
            "// ===== Полная структура файлов блога -> карта URL =====\n"
            "app/\n"
            "  page.js                    // GET /\n"
            "  layout.js                  // общий UI (для всех страниц)\n"
            "  about/\n"
            "    page.js                  // GET /about\n"
            "  blog/\n"
            "    page.js                  // GET /blog\n"
            "    loading.js               // видно, пока /blog загружается\n"
            "    _components/             // подчёркивание -> не становится маршрутом\n"
            "      PostCard.js            // используется только внутри этого раздела\n"
            "    [slug]/\n"
            "      page.js                // GET /blog/osnovy-nextjs, /blog/app-router, ...\n"
            "      not-found.js           // если пост не найден\n"
            "\n"
            "// ===== app/blog/page.js — список постов =====\n"
            "import PostCard from './_components/PostCard';\n"
            "\n"
            "async function getPosts() {\n"
            "  const res = await fetch('https://api.example.com/posts');\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function BlogListPage() {\n"
            "  const posts = await getPosts();\n"
            "  return (\n"
            "    <section>\n"
            "      <h1>Все посты</h1>\n"
            "      <ul>\n"
            "        {posts.map((post) => (\n"
            "          <li key={post.slug}>\n"
            "            <PostCard post={post} />\n"
            "          </li>\n"
            "        ))}\n"
            "      </ul>\n"
            "    </section>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/blog/_components/PostCard.js — пример colocation =====\n"
            "// Используется next/link (не обычный <a>) — страница НЕ перезагружается\n"
            "// целиком, меняется только нужная часть (клиентская навигация)\n"
            "import Link from 'next/link';\n"
            "\n"
            "export default function PostCard({ post }) {\n"
            "  return (\n"
            "    <Link href={`/blog/${post.slug}`}>\n"
            "      <h3>{post.title}</h3>\n"
            "      <p>{post.excerpt}</p>\n"
            "    </Link>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/blog/layout.js — дополнительный вложенный layout для /blog =====\n"
            "// (добавляется поверх root layout — подробно вложенные layout'ы разберём\n"
            "// в уроке 3, здесь просто показано расположение файла)\n"
            "import Link from 'next/link';\n"
            "\n"
            "export default function BlogLayout({ children }) {\n"
            "  return (\n"
            "    <div className=\"blog-shell\">\n"
            "      <nav><Link href=\"/blog\">Все посты</Link></nav>\n"
            "      {children}\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/blog/[slug]/page.js — динамический сегмент =====\n"
            "import { notFound } from 'next/navigation';\n"
            "\n"
            "async function getPost(slug) {\n"
            "  const res = await fetch(`https://api.example.com/posts/${slug}`);\n"
            "  if (res.status === 404) return null;\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function PostPage({ params }) {\n"
            "  const { slug } = await params; // params — Promise, поэтому await\n"
            "  const post = await getPost(slug);\n"
            "\n"
            "  if (!post) notFound(); // -> покажет not-found.js\n"
            "\n"
            "  return (\n"
            "    <article>\n"
            "      <h1>{post.title}</h1>\n"
            "      <div>{post.body}</div>\n"
            "    </article>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/blog/[slug]/not-found.js =====\n"
            "export default function PostNotFound() {\n"
            "  return <p>Такой пост не найден. Попробуйте другой slug.</p>;\n"
            "}\n"
            "\n"
            "// ===== app/blog/loading.js — автоматически видно, пока /blog загружается =====\n"
            "export default function BlogLoading() {\n"
            "  return <p>Посты загружаются...</p>;\n"
            "}\n"
            "\n"
            "// ===== app/about/page.js — простой статичный маршрут =====\n"
            "export default function AboutPage() {\n"
            "  return (\n"
            "    <section>\n"
            "      <h1>О нас</h1>\n"
            "      <p>Это — блог курса, обучающего Next.js на реальных примерах.</p>\n"
            "    </section>\n"
            "  );\n"
            "}\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Blog uchun marshrut xaritasi qurish",
            "task_title_ru": "Постройте карту маршрутов для блога",
            "task_description": (
                "Kichik blog uchun app/ papka tuzilishini loyihalang: bosh sahifa (/), "
                "barcha postlar ro'yxati (/blog), bitta post (/blog/[slug]), va 'Biz haqimizda' "
                "sahifasi (/about). Har bir marshrut uchun qaysi fayl kerakligini yozing."
            ),
            "task_description_ru": (
                "Спроектируйте структуру папки app/ для небольшого блога: главная страница "
                "(/), список всех постов (/blog), отдельный пост (/blog/[slug]) и страница "
                "«О нас» (/about). Укажите, какой файл нужен для каждого маршрута."
            ),
            "task_requirements": (
                "Kamida 4 ta marshrut, har biri uchun to'g'ri page.js joylashuvi ko'rsatilgan "
                "bo'lishi kerak. Dinamik segment ([slug]) to'g'ri ishlatilishi shart."
            ),
            "task_requirements_ru": (
                "Минимум 4 маршрута, для каждого указано правильное расположение page.js. "
                "Динамический сегмент ([slug]) должен быть использован корректно."
            ),
            "task_technologies": "Next.js, App Router",
            "task_deadline_days": 4,
        },
        "sample": {
            "title": "Namuna: blog papka tuzilishi",
            "description": "Kichik blog uchun to'liq app/ papka tuzilishi va page.js namunalari.",
            "sample_type": "code",
            "code_files": [
                {"filename": "app/page.js", "language": "jsx",
                 "code": "export default function HomePage() {\n  return <h1>Blogga xush kelibsiz</h1>;\n}\n"},
                {"filename": "app/blog/page.js", "language": "jsx",
                 "code": "export default async function BlogListPage() {\n  const posts = await fetch('https://api.example.com/posts').then((r) => r.json());\n  return (\n    <ul>\n      {posts.map((p) => (\n        <li key={p.slug}>{p.title}</li>\n      ))}\n    </ul>\n  );\n}\n"},
                {"filename": "app/blog/[slug]/page.js", "language": "jsx",
                 "code": "export default async function PostPage({ params }) {\n  const { slug } = await params;\n  const post = await fetch(`https://api.example.com/posts/${slug}`).then((r) => r.json());\n  return (\n    <article>\n      <h1>{post.title}</h1>\n      <p>{post.body}</p>\n    </article>\n  );\n}\n"},
            ],
        },
        "exercises": [
            {
                "title": "URL manzilini aniqlash",
                "title_ru": "Определите URL-адрес",
                "description": (
                    "Next.js App Router'da app/dashboard/settings/page.js fayli qaysi URL "
                    "manziliga mos keladi?"
                ),
                "description_ru": (
                    "В App Router Next.js какому URL-адресу соответствует файл "
                    "app/dashboard/settings/page.js?"
                ),
                "exercise_type": "multiple_choice",
                "options": ["/dashboard/settings", "/dashboard", "/settings/dashboard", "/app/dashboard/settings"],
                "options_ru": ["/dashboard/settings", "/dashboard", "/settings/dashboard", "/app/dashboard/settings"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "app/ o'zi URL'ning bir qismi emas — u faqat ildiz papka.",
                "hint_ru": "Сама папка app/ не часть URL — это только корневая папка.",
                "explanation": "app/ o'zi hech qachon URL'ga kirmaydi, faqat ichidagi papkalar segment bo'ladi.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Marshrutning asosiy fayli",
                "title_ru": "Основной файл маршрута",
                "description": (
                    "Bo'shliqni to'ldiring: har qanday route papkasida ko'rinadigan asosiy "
                    "komponent ___.js fayli orqali belgilanadi."
                ),
                "description_ru": (
                    "Заполните пропуск: видимый основной компонент любой папки-маршрута "
                    "определяется файлом ___.js."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "page.js",
                "hint": "layout.js emas, sahifaning o'zini render qiladigan fayl.",
                "hint_ru": "Не layout.js, а файл, рендерящий саму страницу.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Nesting tartibini tiklang",
                "title_ru": "Восстановите порядок вложенности",
                "description": (
                    "app/blog/[slug]/page.js manziliga olib boradigan papka/fayl segmentlarini "
                    "to'g'ri (ichma-ich) tartibda joylashtiring."
                ),
                "description_ru": (
                    "Расставьте сегменты папок/файлов, ведущие к app/blog/[slug]/page.js, в "
                    "правильном порядке вложенности."
                ),
                "exercise_type": "drag_and_drop",
                "drag_items": ["app", "blog", "[slug]", "page.js"],
                "drag_items_ru": ["app", "blog", "[slug]", "page.js"],
                "correct_order": ["app", "blog", "[slug]", "page.js"],
                "hint": "Eng tashqi papkadan eng ichki faylgacha.",
                "hint_ru": "От самой внешней папки до самого вложенного файла.",
                "difficulty_level": "Easy",
                "points": 10,
            },
        ],
    },
    {
        "order": 2,
        "title": "3-Layout'lar, nested route'lar va route group'lar",
        "title_ru": "3-Layout'ы, вложенные маршруты и route group'ы",
        "points_reward": 15,
        "text_content": (
            "<h3>Layout — sahifalar orasida saqlanib qoladigan qobiq</h3>"
            "<p>CRA'da (shu platformaning frontend'ida) umumiy UI — masalan, yon navigatsiya "
            "yoki header — odatda <code>App.js</code> ichida qo'lda har bir <code>&lt;Route&gt;</code> "
            "atrofiga o'raladi, yoki alohida \"Layout\" komponenti yozib, har bir sahifada "
            "qo'lda import qilinadi. Next.js'da bu konvensiya darajasiga ko'tarilgan: har "
            "qanday papkaga <code>layout.js</code> fayli qo'yilsa, u shu papka va uning barcha "
            "ichki marshrutlari uchun umumiy qobiq bo'lib qoladi. Eng muhimi — navigatsiya "
            "vaqtida <code>layout.js</code> QAYTA RENDER BO'LMAYDI, faqat <code>page.js</code> "
            "qismi almashadi. Bu degani: agar layout'da scroll holati, ochiq modal yoki hatto "
            "Client Component'dagi useState bo'lsa, foydalanuvchi sahifalar orasida yurganda "
            "ular saqlanib qoladi — CRA'dagi <code>&lt;BrowserRouter&gt;</code> ichidagi umumiy "
            "komponentlar kabi, lekin buni qo'lda tashkil qilish shart emas.</p>"
            "<h3>Root layout — majburiy va yagona</h3>"
            "<p><code>app/layout.js</code> — ildiz layout, va u MAJBURIY: aynan shu yerda "
            "<code>&lt;html&gt;</code> va <code>&lt;body&gt;</code> teglari yoziladi (CRA'dagi "
            "<code>public/index.html</code>ning o'rnini bosadi). Har bir ichki papka o'zining "
            "<code>layout.js</code>'ini qo'shishi mumkin — u root layout'ning <code>children</code> "
            "o'rniga joylashadi, va bu ichma-ich (nested) tarzda davom etaveradi.</p>"
            "<h3>Ichma-ich layout'lar qanday birlashadi</h3>"
            "<p>Masalan, <code>app/dashboard/settings/page.js</code> uchun uchta layout "
            "birlashishi mumkin: <code>app/layout.js</code> (root) → "
            "<code>app/dashboard/layout.js</code> (dashboard uchun umumiy sidebar) → "
            "<code>app/dashboard/settings/layout.js</code> (settings ichidagi tab'lar). Har "
            "biri o'zidan keyingisini <code>{children}</code> orqali o'z ichiga oladi — natijada "
            "uchta qobiq bir-birining ichiga joylashgan holda yakuniy sahifani hosil qiladi.</p>"
            "<h3>Route group'lar: URL'ga ta'sir qilmaydigan tashkilot</h3>"
            "<p>Ba'zan siz marshrutlarni mantiqiy guruhlarga bo'lmoqchi bo'lasiz, lekin bu URL "
            "manzilida ko'rinishini xohlamaysiz. Aynan shu uchun route group'lar bor: papka "
            "nomini qavs ichiga olasiz, masalan <code>(marketing)</code> yoki "
            "<code>(dashboard)</code>. Next.js bu qavsli qismni URL yasashda butunlay e'tiborsiz "
            "qoldiradi. Bu ikki narsa uchun foydali: (1) turli bo'limlarga turli root layout "
            "berish (masalan, <code>(marketing)</code> ochiq sahifalar uchun oddiy header, "
            "<code>(dashboard)</code> esa login qilingan foydalanuvchi uchun sidebar bilan "
            "layout), (2) shunchaki fayllarni mantiqiy guruhlash, hech qanday URL o'zgarishisiz.</p>"
            "<h3>Diagram: ichma-ich layout daraxti</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  R[\"app/layout.js (root)\n"
            "html, body\"] --> M[\"(marketing)/layout.js\n"
            "oddiy header\"]\n"
            "  R --> DA[\"(dashboard)/layout.js\n"
            "sidebar + navbar\"]\n"
            "  M --> MP[\"(marketing)/page.js\n"
            "= /\"]\n"
            "  DA --> DS[\"dashboard/settings/layout.js\n"
            "tab'lar\"]\n"
            "  DS --> DSP[\"dashboard/settings/page.js\n"
            "= /dashboard/settings\"]\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: <code>(marketing)</code> va <code>(dashboard)</code> "
            "qavs ichida bo'lgani uchun URL'da umuman ko'rinmaydi — final manzil shunchaki "
            "<code>/</code> va <code>/dashboard/settings</code> bo'lib qoladi, lekin ikkalasi "
            "butunlay boshqa root layout ostida yashaydi.</p>"
            "<h3>Nega bu CRA'dan yaxshiroq</h3>"
            "<p>CRA'da bunday ikki xil \"tashqi ko'rinish\"ni (masalan, ochiq marketing "
            "sahifalari va login qilingan dashboard) alohida qilish uchun shartli render "
            "mantiqi yozish kerak bo'lardi — masalan, <code>&lt;Route&gt;</code> darajasida "
            "\"agar bu marketing sahifasi bo'lsa, MarketingLayout, aks holda DashboardLayout\" "
            "kabi tekshiruv. Next.js'da bu — shunchaki papka tuzilishi masalasi, aql bilan "
            "yozilgan shartlar emas.</p>"
            "<h3>template.js: layout'ning \"qayta yaratiladigan\" varianti</h3>"
            "<p>Ba'zan aksincha natija kerak bo'ladi — har bir navigatsiyada komponent qayta "
            "yaratilishi (state qayta boshlanishi, useEffect qayta ishga tushishi). Aynan shu "
            "uchun <code>template.js</code> bor: u tashqi ko'rinishi bo'yicha "
            "<code>layout.js</code>ga o'xshaydi (bir xil <code>{children}</code> prop qabul "
            "qiladi), lekin navigatsiya vaqtida QAYTA RENDER BO'LADI — yangi DOM elementlari "
            "yaratiladi, ichidagi state yo'qoladi. Bu enter/exit animatsiyalari yoki har safar "
            "boshidan boshlanishi kerak bo'lgan forma kabi holatlar uchun foydali.</p>"
        ),
        "text_content_ru": (
            "<h3>Layout — оболочка, сохраняющаяся между страницами</h3>"
            "<p>В CRA (фронтенде этой платформы) общий UI — например, боковая навигация или "
            "шапка — обычно вручную оборачивается вокруг каждого <code>&lt;Route&gt;</code> "
            "внутри <code>App.js</code>, либо пишется отдельный компонент «Layout», который "
            "вручную импортируется на каждой странице. В Next.js это возведено в конвенцию: "
            "если положить файл <code>layout.js</code> в любую папку, он станет общей оболочкой "
            "для этой папки и всех вложенных маршрутов. Самое важное — при навигации "
            "<code>layout.js</code> НЕ ПЕРЕРЕНДЕРИВАЕТСЯ, меняется только часть "
            "<code>page.js</code>. Это значит: если в layout'е есть состояние скролла, "
            "открытое модальное окно или даже useState в Client Component, они сохраняются "
            "при переходах между страницами — как общие компоненты внутри "
            "<code>&lt;BrowserRouter&gt;</code> в CRA, но без необходимости организовывать это "
            "вручную.</p>"
            "<h3>Root layout — обязательный и единственный</h3>"
            "<p><code>app/layout.js</code> — корневой layout, и он ОБЯЗАТЕЛЕН: именно здесь "
            "пишутся теги <code>&lt;html&gt;</code> и <code>&lt;body&gt;</code> (он заменяет "
            "<code>public/index.html</code> из CRA). Любая вложенная папка может добавить "
            "свой <code>layout.js</code> — он встанет на место <code>children</code> "
            "родительского layout'а, и так может продолжаться вложенно.</p>"
            "<h3>Как объединяются вложенные layout'ы</h3>"
            "<p>Например, для <code>app/dashboard/settings/page.js</code> могут объединиться "
            "три layout'а: <code>app/layout.js</code> (корневой) → "
            "<code>app/dashboard/layout.js</code> (общий сайдбар для дашборда) → "
            "<code>app/dashboard/settings/layout.js</code> (вкладки внутри настроек). Каждый "
            "оборачивает следующий через <code>{children}</code> — в итоге три оболочки "
            "вкладываются друг в друга, формируя итоговую страницу.</p>"
            "<h3>Route group'ы: организация без влияния на URL</h3>"
            "<p>Иногда нужно логически сгруппировать маршруты, не желая, чтобы это отражалось "
            "в URL. Для этого есть route group'ы: имя папки берётся в скобки, например "
            "<code>(marketing)</code> или <code>(dashboard)</code>. Next.js полностью "
            "игнорирует эту часть в скобках при построении URL. Это полезно для двух вещей: "
            "(1) дать разным разделам разные корневые layout'ы (например, "
            "<code>(marketing)</code> для открытых страниц с простой шапкой, "
            "<code>(dashboard)</code> — для авторизованного пользователя с сайдбаром), "
            "(2) просто логически сгруппировать файлы без изменения URL.</p>"
            "<h3>Диаграмма: дерево вложенных layout'ов</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  R[\"app/layout.js (root)\n"
            "html, body\"] --> M[\"(marketing)/layout.js\n"
            "простая шапка\"]\n"
            "  R --> DA[\"(dashboard)/layout.js\n"
            "sidebar + navbar\"]\n"
            "  M --> MP[\"(marketing)/page.js\n"
            "= /\"]\n"
            "  DA --> DS[\"dashboard/settings/layout.js\n"
            "вкладки\"]\n"
            "  DS --> DSP[\"dashboard/settings/page.js\n"
            "= /dashboard/settings\"]\n"
            "</pre>"
            "<p>Диаграмма показывает: <code>(marketing)</code> и <code>(dashboard)</code> "
            "находятся в скобках, поэтому вообще не видны в URL — итоговый адрес просто "
            "<code>/</code> и <code>/dashboard/settings</code>, но оба живут под совершенно "
            "разными корневыми layout'ами.</p>"
            "<h3>Почему это лучше, чем в CRA</h3>"
            "<p>В CRA, чтобы разделить два разных «внешних вида» (например, открытые "
            "маркетинговые страницы и авторизованный дашборд), пришлось бы писать условную "
            "логику рендеринга — например, проверку на уровне <code>&lt;Route&gt;</code>: "
            "«если это маркетинговая страница — MarketingLayout, иначе — DashboardLayout». В "
            "Next.js это — просто вопрос структуры папок, а не написанных вручную условий.</p>"
            "<h3>template.js: «пересоздаваемый» вариант layout'а</h3>"
            "<p>Иногда нужен противоположный эффект — чтобы компонент пересоздавался при каждой "
            "навигации (состояние сбрасывалось, useEffect запускался заново). Для этого есть "
            "<code>template.js</code>: внешне он похож на <code>layout.js</code> (принимает тот "
            "же проп <code>{children}</code>), но при навигации ПЕРЕРЕНДЕРИВАЕТСЯ — создаются "
            "новые DOM-элементы, состояние внутри теряется. Это полезно для анимаций "
            "входа/выхода или форм, которые должны каждый раз начинаться заново.</p>"
            "<p>Выбор между <code>layout.js</code> и <code>template.js</code> — это осознанное "
            "архитектурное решение, а не просто вопрос вкуса: если нужен постоянный сайдбар с "
            "состоянием фильтров, берите layout.js, а если нужна форма обратной связи, которая "
            "обязана очищаться при каждом заходе на страницу — template.js подойдёт лучше.</p>"
        ),
        "code_content": (
            "// ===== To'liq papka tuzilishi =====\n"
            "app/\n"
            "  layout.js                       // ROOT — html/body, majburiy\n"
            "  (marketing)/                    // route group — URL'ga ta'sir qilmaydi\n"
            "    layout.js                     // ochiq sahifalar uchun oddiy header\n"
            "    page.js                       // -> URL: /\n"
            "    pricing/\n"
            "      page.js                     // -> URL: /pricing\n"
            "  (dashboard)/                    // route group — boshqa root layout\n"
            "    layout.js                     // sidebar bilan dashboard qobig'i\n"
            "    dashboard/\n"
            "      page.js                     // -> URL: /dashboard\n"
            "      settings/\n"
            "        layout.js                 // ichma-ich: sozlamalar tab'lari\n"
            "        template.js               // har navigatsiyada QAYTA yaratiladi\n"
            "        page.js                   // -> URL: /dashboard/settings\n"
            "\n"
            "// ===== app/layout.js — ROOT layout, majburiy, html/body shu yerda =====\n"
            "export default function RootLayout({ children }) {\n"
            "  return (\n"
            "    <html lang=\"uz\">\n"
            "      <body>{children}</body>\n"
            "    </html>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/(marketing)/layout.js — ochiq sahifalar uchun =====\n"
            "import Link from 'next/link';\n"
            "\n"
            "export default function MarketingLayout({ children }) {\n"
            "  return (\n"
            "    <div className=\"marketing-shell\">\n"
            "      <header>\n"
            "        <Link href=\"/\">Bosh sahifa</Link>\n"
            "        <Link href=\"/pricing\">Narxlar</Link>\n"
            "      </header>\n"
            "      <main>{children}</main>\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/(dashboard)/layout.js — faqat dashboard guruhi uchun =====\n"
            "export default function DashboardLayout({ children }) {\n"
            "  return (\n"
            "    <div className=\"dashboard-shell\">\n"
            "      <nav>Sidebar: Kurslar / Profil / Sozlamalar</nav>\n"
            "      <main>{children}</main>\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/(dashboard)/dashboard/settings/layout.js — ichma-ich =====\n"
            "// Bu layout DashboardLayout ICHIGA joylashadi — ikkalasi ham render bo'ladi\n"
            "export default function SettingsLayout({ children }) {\n"
            "  return (\n"
            "    <div className=\"settings-tabs\">\n"
            "      <nav>Profil | Xavfsizlik | Bildirishnomalar</nav>\n"
            "      {children}\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/(dashboard)/dashboard/settings/template.js =====\n"
            "// layout.js'dan farqli — bu HAR navigatsiyada qaytadan yaratiladi,\n"
            "// ichidagi state (masalan, forma qiymati) har safar boshidan boshlanadi\n"
            "export default function SettingsTemplate({ children }) {\n"
            "  return <div className=\"fade-in\">{children}</div>;\n"
            "}\n"
            "\n"
            "// ===== app/(dashboard)/dashboard/settings/page.js =====\n"
            "// -> URL: /dashboard/settings (guruh nomlari URL'da UMUMAN yo'q!)\n"
            "export default function SettingsPage() {\n"
            "  return <h2>Sozlamalar</h2>;\n"
            "}\n"
            "\n"
            "// ===== app/(marketing)/pricing/page.js =====\n"
            "// MarketingLayout ichiga joylashadi (route group orqali avtomatik)\n"
            "export default function PricingPage() {\n"
            "  return (\n"
            "    <section>\n"
            "      <h1>Narxlar</h1>\n"
            "      <p>Bepul reja va Pro reja mavjud.</p>\n"
            "    </section>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/(dashboard)/dashboard/page.js =====\n"
            "// DashboardLayout ichiga joylashadi -> URL: /dashboard\n"
            "// E'tibor bering: bu segmentda ham \"dashboard\" so'zi ikki marta\n"
            "// takrorlanadi — bittasi route group (qavs ichida, URL'da yo'q),\n"
            "// ikkinchisi haqiqiy papka nomi (URL'ning bir qismi).\n"
            "export default function DashboardHomePage() {\n"
            "  return <h1>Boshqaruv paneli</h1>;\n"
            "}\n"
        ),
        "code_content_ru": (
            "// ===== Полная структура папок =====\n"
            "app/\n"
            "  layout.js                       // ROOT — html/body, обязателен\n"
            "  (marketing)/                    // route group — не влияет на URL\n"
            "    layout.js                     // простая шапка для открытых страниц\n"
            "    page.js                       // -> URL: /\n"
            "    pricing/\n"
            "      page.js                     // -> URL: /pricing\n"
            "  (dashboard)/                    // route group — другой root layout\n"
            "    layout.js                     // оболочка дашборда с сайдбаром\n"
            "    dashboard/\n"
            "      page.js                     // -> URL: /dashboard\n"
            "      settings/\n"
            "        layout.js                 // вложенный: вкладки настроек\n"
            "        template.js               // пересоздаётся при каждой навигации\n"
            "        page.js                   // -> URL: /dashboard/settings\n"
            "\n"
            "// ===== app/layout.js — ROOT layout, обязателен, html/body здесь =====\n"
            "export default function RootLayout({ children }) {\n"
            "  return (\n"
            "    <html lang=\"ru\">\n"
            "      <body>{children}</body>\n"
            "    </html>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/(marketing)/layout.js — для открытых страниц =====\n"
            "import Link from 'next/link';\n"
            "\n"
            "export default function MarketingLayout({ children }) {\n"
            "  return (\n"
            "    <div className=\"marketing-shell\">\n"
            "      <header>\n"
            "        <Link href=\"/\">Главная</Link>\n"
            "        <Link href=\"/pricing\">Цены</Link>\n"
            "      </header>\n"
            "      <main>{children}</main>\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/(dashboard)/layout.js — только для группы dashboard =====\n"
            "export default function DashboardLayout({ children }) {\n"
            "  return (\n"
            "    <div className=\"dashboard-shell\">\n"
            "      <nav>Sidebar: Курсы / Профиль / Настройки</nav>\n"
            "      <main>{children}</main>\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/(dashboard)/dashboard/settings/layout.js — вложенный =====\n"
            "// Этот layout встраивается ВНУТРЬ DashboardLayout — рендерятся оба\n"
            "export default function SettingsLayout({ children }) {\n"
            "  return (\n"
            "    <div className=\"settings-tabs\">\n"
            "      <nav>Профиль | Безопасность | Уведомления</nav>\n"
            "      {children}\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/(dashboard)/dashboard/settings/template.js =====\n"
            "// В отличие от layout.js — пересоздаётся при КАЖДОЙ навигации,\n"
            "// состояние внутри (например, значение формы) сбрасывается каждый раз\n"
            "export default function SettingsTemplate({ children }) {\n"
            "  return <div className=\"fade-in\">{children}</div>;\n"
            "}\n"
            "\n"
            "// ===== app/(dashboard)/dashboard/settings/page.js =====\n"
            "// -> URL: /dashboard/settings (имён групп в URL ВООБЩЕ нет!)\n"
            "export default function SettingsPage() {\n"
            "  return <h2>Настройки</h2>;\n"
            "}\n"
            "\n"
            "// ===== app/(marketing)/pricing/page.js =====\n"
            "// Встраивается внутрь MarketingLayout (автоматически через route group)\n"
            "export default function PricingPage() {\n"
            "  return (\n"
            "    <section>\n"
            "      <h1>Цены</h1>\n"
            "      <p>Доступны бесплатный план и план Pro.</p>\n"
            "    </section>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/(dashboard)/dashboard/page.js =====\n"
            "// Встраивается внутрь DashboardLayout -> URL: /dashboard\n"
            "// Обратите внимание: слово \"dashboard\" повторяется здесь дважды —\n"
            "// один раз как route group (в скобках, не входит в URL), второй\n"
            "// раз как настоящее имя папки (часть URL).\n"
            "export default function DashboardHomePage() {\n"
            "  return <h1>Панель управления</h1>;\n"
            "}\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Ikki xil layout: marketing va dashboard",
            "task_title_ru": "Два разных layout'а: marketing и dashboard",
            "task_description": (
                "Route group'lardan foydalanib, bitta loyihada ikkita mustaqil root layout "
                "loyihalang: (marketing) guruhi oddiy header bilan, (dashboard) guruhi sidebar "
                "bilan. Har biri uchun kamida bitta ichki sahifa qo'shing."
            ),
            "task_description_ru": (
                "Используя route group'ы, спроектируйте в одном проекте два независимых "
                "корневых layout'а: группа (marketing) с простой шапкой, группа (dashboard) с "
                "сайдбаром. Добавьте хотя бы по одной вложенной странице для каждой."
            ),
            "task_requirements": (
                "Papka tuzilishi (marketing)/layout.js va (dashboard)/layout.js'ni o'z ichiga "
                "olishi, va route group nomlari yakuniy URL'da ko'rinmasligini tushuntirish kerak."
            ),
            "task_requirements_ru": (
                "Структура папок должна включать (marketing)/layout.js и "
                "(dashboard)/layout.js, и нужно объяснить, что имена route group'ов не видны в "
                "итоговом URL."
            ),
            "task_technologies": "Next.js, App Router",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: ichma-ich layout'lar",
            "description": "Root layout, dashboard guruh layout'i va ichki sahifa birgalikda.",
            "sample_type": "code",
            "code_files": [
                {"filename": "app/layout.js", "language": "jsx",
                 "code": "export default function RootLayout({ children }) {\n  return (\n    <html lang=\"uz\">\n      <body>{children}</body>\n    </html>\n  );\n}\n"},
                {"filename": "app/(dashboard)/layout.js", "language": "jsx",
                 "code": "export default function DashboardLayout({ children }) {\n  return (\n    <div className=\"dashboard\">\n      <nav>Sidebar</nav>\n      <section>{children}</section>\n    </div>\n  );\n}\n"},
                {"filename": "app/(dashboard)/profile/page.js", "language": "jsx",
                 "code": "export default function ProfilePage() {\n  return <h1>Mening profilim</h1>; // URL: /profile\n}\n"},
            ],
        },
        "exercises": [
            {
                "title": "Layout qayta render bo'ladimi?",
                "title_ru": "Перерендеривается ли layout?",
                "description": "Ichma-ich (nested) layout haqida qaysi fikr to'g'ri?",
                "description_ru": "Какое утверждение о вложенном (nested) layout верно?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Har bir navigatsiyada layout qayta yaratiladi va uning holati yo'qoladi",
                    "Layout sahifalar orasida saqlanib qoladi, faqat page.js qismi almashadi",
                    "Layout faqat CSS uchun ishlatiladi, komponent bo'la olmaydi",
                    "Bitta loyihada faqat bitta layout bo'lishi mumkin",
                ],
                "options_ru": [
                    "При каждой навигации layout создаётся заново и его состояние теряется",
                    "Layout сохраняется между страницами, меняется только часть page.js",
                    "Layout используется только для CSS и не может быть компонентом",
                    "В одном проекте может быть только один layout",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Bu — layout'ning eng katta afzalligi.",
                "hint_ru": "Это главное преимущество layout'а.",
                "explanation": "Navigatsiya vaqtida faqat page.js qayta render bo'ladi, layout o'z holatini saqlaydi.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Bolalar uchun umumiy qobiq",
                "title_ru": "Общая оболочка для потомков",
                "description": (
                    "Bo'shliqni to'ldiring: bir papka va uning barcha ichki marshrutlari uchun "
                    "umumiy UI qatlamini ___.js fayli beradi."
                ),
                "description_ru": (
                    "Заполните пропуск: общий слой UI для папки и всех вложенных маршрутов "
                    "задаёт файл ___.js."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "layout.js",
                "hint": "page.js emas — bu sahifani o'raydigan fayl.",
                "hint_ru": "Не page.js — это файл, оборачивающий страницу.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Route group nima uchun ishlatiladi?",
                "title_ru": "Для чего используется route group?",
                "description": (
                    "(marketing) kabi qavsli papka nomi Next.js'da ___ deb ataladi va URL "
                    "manziliga ta'sir qilmaydi."
                ),
                "description_ru": (
                    "Папка с именем в скобках, например (marketing), в Next.js называется "
                    "___ и не влияет на URL-адрес."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "route group",
                "correct_answers_ru": "route group",
                "hint": "Ikki so'zdan iborat ingliz atamasi, o'zbek va rus texnik matnlarida ham xuddi shunday ishlatiladi.",
                "hint_ru": "Термин из двух слов, используется одинаково и в узбекских, и в русских технических текстах.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 3,
        "title": "4-Server Components vs Client Components ('use client')",
        "title_ru": "4-Server Components и Client Components (директива 'use client')",
        "points_reward": 20,
        "text_content": (
            "<h3>React'dan keyingi eng katta kontseptual sakrash</h3>"
            "<p>CRA'da (shu platformaning frontend'ida) BARCHA komponentlar bir xil joyda "
            "ishlaydi — brauzerda. <code>frontend/src/index.js</code>dagi "
            "<code>ReactDOM.createRoot(...).render(&lt;App /&gt;)</code> chaqirilganda, butun "
            "komponent daraxti — <code>App.js</code>dan tortib eng ichki tugmagacha — brauzerda "
            "JavaScript sifatida ishga tushadi. Next.js App Router'da esa bu taxmin endi to'g'ri "
            "emas: har bir komponent ikki joydan BIRIDA ishlaydi — serverda yoki brauzerda — va "
            "bu tanlov dasturchi tomonidan aniq ko'rsatilishi kerak.</p>"
            "<h3>Default holat: hammasi Server Component</h3>"
            "<p>App Router'da <strong>hech qanday direktivasiz yozilgan har qanday komponent — "
            "Server Component</strong> hisoblanadi. U faqat SERVERDA ishga tushadi: kompilyatsiya "
            "qilingandan keyin, uning JavaScript kodi umuman brauzerga jo'natilmaydi — faqat "
            "natijaviy HTML jo'natiladi. Bu ikkita katta afzallik beradi: (1) bandle hajmi "
            "kichrayadi, chunki server komponentining kodi mijozga tushmaydi; (2) server "
            "komponenti to'g'ridan-to'g'ri backend resurslariga (masalan, ma'lumotlar bazasi "
            "yoki maxfiy API kaliti) xavfsiz murojaat qila oladi — kalit hech qachon brauzerga "
            "chiqmaydi, chunki kod o'zi brauzerga bormaydi.</p>"
            "<h3>'use client': chegarani belgilash</h3>"
            "<p>Interaktivlik kerak bo'lgan joyda — <code>useState</code>, <code>useEffect</code>, "
            "<code>onClick</code> kabi event handler'lar, yoki <code>window</code>/"
            "<code>localStorage</code> kabi brauzer-only API'lar — komponent faylining ENG "
            "BOSHIGA <code>'use client'</code> direktivasi yozilishi kerak. Bu — oddiy string, "
            "lekin Next.js buni maxsus belgi sifatida o'qiydi: shu fayldan boshlab, shu fayl "
            "IMPORT qiladigan barcha bolalar komponentlari ham Client Component hisoblanadi va "
            "ular UCHUN JavaScript kodi brauzerga jo'natiladi (keyin u yerda \"hydration\" — "
            "serverda tayyorlangan HTML'ga interaktivlikni ulash jarayoni — sodir bo'ladi).</p>"
            "<h3>Nima qila olmaydi, nima qila oladi</h3>"
            "<p>Server Component: <code>async/await</code> bilan to'g'ridan-to'g'ri ma'lumot "
            "olishi mumkin (5-darsda ko'ramiz), lekin <code>useState</code>, <code>useEffect</code>, "
            "yoki <code>onClick</code> ishlata olmaydi — bular brauzerga tegishli tushunchalar. "
            "Client Component: interaktiv bo'la oladi, lekin server-only kod (masalan, "
            "ma'lumotlar bazasiga to'g'ridan-to'g'ri so'rov) ishlata olmaydi.</p>"
            "<h3>Kompozitsiya: Server Component'ni Client Component ICHIGA qanday qo'yish mumkin</h3>"
            "<p>Muhim cheklov: Client Component ICHIDA Server Component'ni import qilib, uni "
            "oddiy funksiya sifatida chaqirib bo'lmaydi. Lekin Server Component'ni Client "
            "Component'ga <code>children</code> yoki boshqa prop sifatida \"uzatish\" mumkin — "
            "bu \"slot\" naqshi deb ataladi. Masalan, interaktiv <code>&lt;ExpandableBox&gt;</code> "
            "(Client Component, ochiladi/yopiladi) ichiga server tomonda render qilingan "
            "<code>&lt;CourseDetails /&gt;</code> (Server Component) ni <code>children</code> "
            "sifatida joylashtirish mumkin — bunda <code>ExpandableBox</code> hech qachon "
            "<code>CourseDetails</code>ni import qilmaydi, uni faqat qabul qiladi.</p>"
            "<h3>Diagram: Server/Client chegarasi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  P[\"page.js (Server)\n"
            "ma'lumotni serverda oladi\"] --> SC[\"CourseDetails (Server)\n"
            "JS brauzerga jo'natilmaydi\"]\n"
            "  P --> CC[\"'use client'\n"
            "LikeButton (Client)\"]\n"
            "  CC --> H[\"useState, onClick\n"
            "brauzerda hydration bilan ishlaydi\"]\n"
            "  P -.->|\"children sifatida uzatiladi\"| SLOT[\"'use client'\n"
            "ExpandableBox (Client)\n"
            "ichida CourseDetails (Server)\"]\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: <code>page.js</code> va <code>CourseDetails</code> — "
            "ikkalasi ham server chegarasida qoladi va ularning kodi brauzerga tushmaydi, faqat "
            "<code>LikeButton</code> kabi <code>'use client'</code> bilan belgilangan qismgina "
            "brauzerda JavaScript sifatida ishga tushadi.</p>"
            "<h3>Nega bu CRA'dagidan tubdan farq qiladi</h3>"
            "<p>CRA'da bu tanlov umuman yo'q edi — har bir komponent avtomatik ravishda brauzer "
            "komponenti edi, chunki boshqa variant yo'q edi. Next.js'da esa har bir yangi "
            "komponent yozganda dasturchi o'ziga savol berishi kerak: \"bu komponentga "
            "interaktivlik kerakmi, yoki u faqat ma'lumotni ko'rsatish uchunmi?\" Agar faqat "
            "ko'rsatish uchun bo'lsa — uni Server Component holida qoldirish kerak, chunki bu "
            "bepul: kamroq JS, tezroq yuklanish, xavfsizroq ma'lumot olish.</p>"
        ),
        "text_content_ru": (
            "<h3>Самый большой концептуальный скачок после React</h3>"
            "<p>В CRA (фронтенде этой платформы) ВСЕ компоненты работают в одном месте — в "
            "браузере. Когда вызывается "
            "<code>ReactDOM.createRoot(...).render(&lt;App /&gt;)</code> из "
            "<code>frontend/src/index.js</code>, всё дерево компонентов — от <code>App.js</code> "
            "до самой вложенной кнопки — запускается в браузере как JavaScript. В App Router "
            "Next.js это предположение больше не верно: каждый компонент работает в ОДНОМ из "
            "двух мест — на сервере или в браузере — и этот выбор должен быть явно указан "
            "разработчиком.</p>"
            "<h3>Состояние по умолчанию: всё — Server Component</h3>"
            "<p>В App Router <strong>любой компонент, написанный без всякой директивы, "
            "считается Server Component</strong>. Он выполняется ТОЛЬКО НА СЕРВЕРЕ: после "
            "компиляции его JavaScript-код вообще не отправляется в браузер — отправляется "
            "только итоговый HTML. Это даёт два больших преимущества: (1) размер бандла "
            "уменьшается, ведь код серверного компонента не попадает к клиенту; (2) серверный "
            "компонент может напрямую и безопасно обращаться к серверным ресурсам (например, к "
            "базе данных или секретному API-ключу) — ключ никогда не попадёт в браузер, "
            "поскольку сам код туда не отправляется.</p>"
            "<h3>'use client': обозначение границы</h3>"
            "<p>Там, где нужна интерактивность — <code>useState</code>, <code>useEffect</code>, "
            "обработчики событий вроде <code>onClick</code>, или браузерные API вроде "
            "<code>window</code>/<code>localStorage</code> — в самое НАЧАЛО файла компонента "
            "нужно написать директиву <code>'use client'</code>. Это обычная строка, но Next.js "
            "читает её как специальный маркер: начиная с этого файла, все дочерние компоненты, "
            "которые он ИМПОРТИРУЕТ, тоже считаются Client Component, и ДЛЯ НИХ JavaScript-код "
            "отправляется в браузер (там происходит «hydration» — процесс подключения "
            "интерактивности к уже готовому серверному HTML).</p>"
            "<h3>Что может, а что не может</h3>"
            "<p>Server Component: может напрямую получать данные через <code>async/await</code> "
            "(разберём в уроке 5), но не может использовать <code>useState</code>, "
            "<code>useEffect</code> или <code>onClick</code> — это браузерные понятия. Client "
            "Component: может быть интерактивным, но не может выполнять серверный код (например, "
            "прямой запрос к базе данных).</p>"
            "<h3>Композиция: как поместить Server Component ВНУТРЬ Client Component</h3>"
            "<p>Важное ограничение: внутри Client Component нельзя импортировать Server "
            "Component и вызывать его как обычную функцию. Но можно «передать» Server Component "
            "в Client Component через проп <code>children</code> или другой проп — это "
            "называется паттерном «слота». Например, внутрь интерактивного "
            "<code>&lt;ExpandableBox&gt;</code> (Client Component, открывается/закрывается) "
            "можно поместить отрендеренный на сервере <code>&lt;CourseDetails /&gt;</code> "
            "(Server Component) как <code>children</code> — при этом <code>ExpandableBox</code> "
            "никогда не импортирует <code>CourseDetails</code>, он лишь принимает его.</p>"
            "<h3>Диаграмма: граница Server/Client</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  P[\"page.js (Server)\n"
            "получает данные на сервере\"] --> SC[\"CourseDetails (Server)\n"
            "JS не отправляется в браузер\"]\n"
            "  P --> CC[\"'use client'\n"
            "LikeButton (Client)\"]\n"
            "  CC --> H[\"useState, onClick\n"
            "работает в браузере через hydration\"]\n"
            "  P -.->|\"передаётся как children\"| SLOT[\"'use client'\n"
            "ExpandableBox (Client)\n"
            "внутри CourseDetails (Server)\"]\n"
            "</pre>"
            "<p>Диаграмма показывает: <code>page.js</code> и <code>CourseDetails</code> — оба "
            "остаются в серверной границе, их код не попадает в браузер, и только часть, "
            "помеченная <code>'use client'</code>, вроде <code>LikeButton</code>, запускается в "
            "браузере как JavaScript.</p>"
            "<h3>Почему это принципиально отличается от CRA</h3>"
            "<p>В CRA такого выбора вообще не было — каждый компонент автоматически был "
            "браузерным, потому что другого варианта не существовало. В Next.js при написании "
            "каждого нового компонента разработчик должен задать себе вопрос: «нужна ли этому "
            "компоненту интерактивность, или он только показывает данные?» Если только "
            "показывает — его стоит оставить Server Component'ом, потому что это бесплатно: "
            "меньше JS, быстрее загрузка, безопаснее получение данных.</p>"
            "<p>На практике хорошее правило: начинайте каждый новый компонент как Server "
            "Component и добавляйте <code>'use client'</code> только тогда, когда реально "
            "требуется интерактивность — а не «на всякий случай» в начале работы над файлом.</p>"
        ),
        "code_content": (
            "// app/courses/[id]/page.js — Server Component (default, direktivasiz)\n"
            "import LikeButton from './LikeButton';\n"
            "import CourseDetails from './CourseDetails';\n"
            "\n"
            "export default async function CoursePage({ params }) {\n"
            "  const { id } = await params;\n"
            "  // To'g'ridan-to'g'ri await — useEffect/useState kerak emas.\n"
            "  const course = await fetch(`https://api.example.com/courses/${id}`).then((r) => r.json());\n"
            "\n"
            "  return (\n"
            "    <article>\n"
            "      <CourseDetails course={course} />   {/* Server Component */}\n"
            "      <LikeButton courseId={course.id} /> {/* Client Component */}\n"
            "    </article>\n"
            "  );\n"
            "}\n"
            "\n"
            "// app/courses/[id]/LikeButton.js — Client Component\n"
            "'use client';\n"
            "\n"
            "import { useState } from 'react';\n"
            "\n"
            "export default function LikeButton({ courseId }) {\n"
            "  const [liked, setLiked] = useState(false);\n"
            "\n"
            "  return (\n"
            "    <button onClick={() => setLiked((v) => !v)}>\n"
            "      {liked ? 'Yoqdi ✓' : \"Yoqdi bosing\"}\n"
            "    </button>\n"
            "  );\n"
            "}\n"
            "\n"
            "// app/courses/[id]/CourseDetails.js — Server Component (JS brauzerga tushmaydi)\n"
            "export default function CourseDetails({ course }) {\n"
            "  return (\n"
            "    <div>\n"
            "      <h1>{course.title}</h1>\n"
            "      <p>{course.description}</p>\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===================================================================\n"
            "// XATO YO'L: Server Component'ni Client Component ICHIDA import qilish\n"
            "// ===================================================================\n"
            "// app/courses/[id]/ExpandableBox.js\n"
            "'use client';\n"
            "import { useState } from 'react';\n"
            "import CourseDetails from './CourseDetails'; // ❌ BU ISHLAMAYDI!\n"
            "\n"
            "export default function ExpandableBoxWrong({ course }) {\n"
            "  const [open, setOpen] = useState(false);\n"
            "  return (\n"
            "    <div>\n"
            "      <button onClick={() => setOpen((v) => !v)}>Ko'rsatish</button>\n"
            "      {open && <CourseDetails course={course} />} {/* ❌ xato */}\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "// Sabab: 'use client' bilan boshlangan fayl IMPORT qilgan har qanday\n"
            "// komponent ham Client Component deb hisoblanadi — CourseDetails endi\n"
            "// serverda emas, brauzerda ishlashga majbur bo'ladi.\n"
            "\n"
            "// ===================================================================\n"
            "// TO'G'RI YO'L: \"slot\" naqshi — children orqali uzatish\n"
            "// ===================================================================\n"
            "// app/courses/[id]/ExpandableBox.js — Server Component'ni QABUL qiladi,\n"
            "// uni import QILMAYDI\n"
            "'use client';\n"
            "import { useState } from 'react';\n"
            "\n"
            "export default function ExpandableBox({ children }) {\n"
            "  const [open, setOpen] = useState(false);\n"
            "  return (\n"
            "    <div>\n"
            "      <button onClick={() => setOpen((v) => !v)}>\n"
            "        {open ? 'Yashirish' : \"Ko'rsatish\"}\n"
            "      </button>\n"
            "      {open && children} {/* ✅ CourseDetails serverda tayyorlanadi */}\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "\n"
            "// app/courses/[id]/page.js (yangilangan) — bu yerda kompozitsiya sodir bo'ladi\n"
            "export default async function CoursePageWithSlot({ params }) {\n"
            "  const { id } = await params;\n"
            "  const course = await fetch(`https://api.example.com/courses/${id}`).then((r) => r.json());\n"
            "\n"
            "  return (\n"
            "    <ExpandableBox>\n"
            "      <CourseDetails course={course} /> {/* Server Component, children sifatida */}\n"
            "    </ExpandableBox>\n"
            "  );\n"
            "}\n"
            "// Bu yerda page.js (Server Component) CourseDetails'ni ExpandableBox'ga\n"
            "// (Client Component) UZATADI — ExpandableBox uni hech qachon import qilmaydi,\n"
            "// faqat 'children' sifatida qabul qiladi. Shuning uchun bu ishlaydi.\n"
        ),
        "code_content_ru": (
            "// app/courses/[id]/page.js — Server Component (по умолчанию, без директивы)\n"
            "import LikeButton from './LikeButton';\n"
            "import CourseDetails from './CourseDetails';\n"
            "\n"
            "export default async function CoursePage({ params }) {\n"
            "  const { id } = await params;\n"
            "  // Прямой await — useEffect/useState не нужны.\n"
            "  const course = await fetch(`https://api.example.com/courses/${id}`).then((r) => r.json());\n"
            "\n"
            "  return (\n"
            "    <article>\n"
            "      <CourseDetails course={course} />   {/* Server Component */}\n"
            "      <LikeButton courseId={course.id} /> {/* Client Component */}\n"
            "    </article>\n"
            "  );\n"
            "}\n"
            "\n"
            "// app/courses/[id]/LikeButton.js — Client Component\n"
            "'use client';\n"
            "\n"
            "import { useState } from 'react';\n"
            "\n"
            "export default function LikeButton({ courseId }) {\n"
            "  const [liked, setLiked] = useState(false);\n"
            "\n"
            "  return (\n"
            "    <button onClick={() => setLiked((v) => !v)}>\n"
            "      {liked ? 'Нравится ✓' : 'Нажмите Нравится'}\n"
            "    </button>\n"
            "  );\n"
            "}\n"
            "\n"
            "// app/courses/[id]/CourseDetails.js — Server Component (JS не попадает в браузер)\n"
            "export default function CourseDetails({ course }) {\n"
            "  return (\n"
            "    <div>\n"
            "      <h1>{course.title}</h1>\n"
            "      <p>{course.description}</p>\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===================================================================\n"
            "// НЕПРАВИЛЬНЫЙ ПУТЬ: импорт Server Component ВНУТРЬ Client Component\n"
            "// ===================================================================\n"
            "// app/courses/[id]/ExpandableBox.js\n"
            "'use client';\n"
            "import { useState } from 'react';\n"
            "import CourseDetails from './CourseDetails'; // ❌ ЭТО НЕ РАБОТАЕТ!\n"
            "\n"
            "export default function ExpandableBoxWrong({ course }) {\n"
            "  const [open, setOpen] = useState(false);\n"
            "  return (\n"
            "    <div>\n"
            "      <button onClick={() => setOpen((v) => !v)}>Показать</button>\n"
            "      {open && <CourseDetails course={course} />} {/* ❌ ошибка */}\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "// Причина: любой компонент, который ИМПОРТИРУЕТ файл, начинающийся с\n"
            "// 'use client', тоже считается Client Component — CourseDetails теперь\n"
            "// вынужден выполняться в браузере, а не на сервере.\n"
            "\n"
            "// ===================================================================\n"
            "// ПРАВИЛЬНЫЙ ПУТЬ: паттерн «слота» — передача через children\n"
            "// ===================================================================\n"
            "// app/courses/[id]/ExpandableBox.js — ПРИНИМАЕТ Server Component,\n"
            "// но НЕ ИМПОРТИРУЕТ его\n"
            "'use client';\n"
            "import { useState } from 'react';\n"
            "\n"
            "export default function ExpandableBox({ children }) {\n"
            "  const [open, setOpen] = useState(false);\n"
            "  return (\n"
            "    <div>\n"
            "      <button onClick={() => setOpen((v) => !v)}>\n"
            "        {open ? 'Скрыть' : 'Показать'}\n"
            "      </button>\n"
            "      {open && children} {/* ✅ CourseDetails подготовлен на сервере */}\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "\n"
            "// app/courses/[id]/page.js (обновлённый) — здесь происходит композиция\n"
            "export default async function CoursePageWithSlot({ params }) {\n"
            "  const { id } = await params;\n"
            "  const course = await fetch(`https://api.example.com/courses/${id}`).then((r) => r.json());\n"
            "\n"
            "  return (\n"
            "    <ExpandableBox>\n"
            "      <CourseDetails course={course} /> {/* Server Component, как children */}\n"
            "    </ExpandableBox>\n"
            "  );\n"
            "}\n"
            "// Здесь page.js (Server Component) ПЕРЕДАЁТ CourseDetails в ExpandableBox\n"
            "// (Client Component) — ExpandableBox никогда его не импортирует, а лишь\n"
            "// принимает как 'children'. Именно поэтому это работает.\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Server/Client chegarasini loyihalash",
            "task_title_ru": "Спроектируйте границу Server/Client",
            "task_description": (
                "Kurs sahifasi uchun komponentlar daraxtini loyihalang: kamida bitta Server "
                "Component (ma'lumot ko'rsatuvchi) va kamida bitta Client Component "
                "(interaktiv, masalan sharh qoldirish formasi). Har bir komponent uchun nima "
                "uchun aynan shu turni tanlaganingizni yozing."
            ),
            "task_description_ru": (
                "Спроектируйте дерево компонентов для страницы курса: минимум один Server "
                "Component (показывает данные) и минимум один Client Component (интерактивный, "
                "например форма комментария). Для каждого компонента объясните, почему выбран "
                "именно этот тип."
            ),
            "task_requirements": (
                "Kamida 3 ta komponent, ulardan kamida bittasi 'use client' bilan boshlanishi "
                "kerak. Slot naqshidan foydalanilgan bo'lsa, alohida ta'kidlang."
            ),
            "task_requirements_ru": (
                "Минимум 3 компонента, хотя бы один должен начинаться с 'use client'. Если "
                "используется паттерн слота — отдельно укажите это."
            ),
            "task_technologies": "Next.js, React Server Components",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: Server + Client komponentlar birgalikda",
            "description": "Kurs sahifasi: server tomonda ma'lumot, client tomonda interaktiv tugma.",
            "sample_type": "code",
            "code_files": [
                {"filename": "app/courses/[id]/page.js", "language": "jsx",
                 "code": "import LikeButton from './LikeButton';\n\nexport default async function CoursePage({ params }) {\n  const { id } = await params;\n  const course = await fetch(`https://api.example.com/courses/${id}`).then((r) => r.json());\n  return (\n    <article>\n      <h1>{course.title}</h1>\n      <LikeButton courseId={course.id} />\n    </article>\n  );\n}\n"},
                {"filename": "app/courses/[id]/LikeButton.js", "language": "jsx",
                 "code": "'use client';\nimport { useState } from 'react';\n\nexport default function LikeButton({ courseId }) {\n  const [liked, setLiked] = useState(false);\n  return <button onClick={() => setLiked((v) => !v)}>{liked ? 'Yoqdi' : 'Yoqtirish'}</button>;\n}\n"},
            ],
        },
        "exercises": [
            {
                "title": "Default komponent turi",
                "title_ru": "Тип компонента по умолчанию",
                "description": (
                    "App Router'da hech qanday direktivasiz yozilgan komponent qaysi turga "
                    "kiradi?"
                ),
                "description_ru": (
                    "К какому типу относится компонент, написанный в App Router без всякой "
                    "директивы?"
                ),
                "exercise_type": "multiple_choice",
                "options": ["Client Component", "Server Component", "Hybrid Component", "Bunday tur yo'q, xato beradi"],
                "options_ru": ["Client Component", "Server Component", "Hybrid Component", "Такого типа нет, будет ошибка"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Bu — App Router'ning default holati.",
                "hint_ru": "Это состояние по умолчанию в App Router.",
                "explanation": "Direktivasiz komponentlar avtomatik Server Component hisoblanadi.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Client Component'ni belgilash",
                "title_ru": "Обозначение Client Component",
                "description": (
                    "Bo'shliqni to'ldiring: interaktivlik (useState, onClick) kerak bo'lgan "
                    "komponent faylining eng boshiga ___ direktivasi yozilishi kerak."
                ),
                "description_ru": (
                    "Заполните пропуск: в самое начало файла компонента, которому нужна "
                    "интерактивность (useState, onClick), нужно написать директиву ___."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "use client",
                "correct_answers_ru": "use client",
                "hint": "Ikki so'zdan iborat, tirnoq ichida yoziladigan direktiva.",
                "hint_ru": "Директива из двух слов, пишется в кавычках.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Server Component afzalliklari",
                "title_ru": "Преимущества Server Component",
                "description": (
                    "Server Component ishlatishning haqiqiy afzalliklarini AI-grading uchun "
                    "tushuntiring: JS bandle hajmi va maxfiy ma'lumotlarga xavfsiz murojaat "
                    "nuqtai nazaridan yozing."
                ),
                "description_ru": (
                    "Объясните для AI-проверки реальные преимущества использования Server "
                    "Component: с точки зрения размера JS-бандла и безопасного доступа к "
                    "секретным данным."
                ),
                "exercise_type": "text_input",
                "expected_answer": (
                    "Server Component kodi brauzerga jo'natilmaydi, shuning uchun JS bandle "
                    "kichrayadi; u to'g'ridan-to'g'ri maxfiy API kalit yoki ma'lumotlar bazasiga "
                    "xavfsiz murojaat qila oladi, chunki bu kod hech qachon brauzerga chiqmaydi."
                ),
                "hint": "Ikki asosiy afzallikni eslang: bundle hajmi va xavfsizlik.",
                "hint_ru": "Вспомните два главных преимущества: размер бандла и безопасность.",
                "difficulty_level": "Medium",
                "points": 15,
            },
        ],
    },
    {
        "order": 4,
        "title": "R1-Blog: Server Components bilan post ro'yxati (takrorlash)",
        "title_ru": "R1-Блог: список постов на Server Components (повторение)",
        "points_reward": 20,
        "text_content": (
            "<h3>Bu — takrorlash darsi</h3>"
            "<p>Bu dars amaliy takrorlash bo'lgani uchun matn qisqaroq — asosiy e'tibor "
            "quyidagi vazifada amaliyot qilishga qaratilgan, yangi nazariy tushuncha "
            "berilmaydi. 1-3-darslarda o'rganilganlarni (App Router, layout'lar, Server/Client "
            "chegarasi) bitta kichik, lekin to'liq ishlaydigan misolda birlashtiramiz: blog "
            "bosh sahifasi.</p>"
            "<h3>Nimani takrorlaymiz</h3>"
            "<ul>"
            "<li><strong>Fayl asosidagi marshrutlash</strong>: <code>app/blog/page.js</code> — "
            "postlar ro'yxati sahifasi.</li>"
            "<li><strong>Server Component orqali ma'lumot olish</strong>: "
            "<code>BlogListPage</code> — <code>async</code> funksiya, to'g'ridan-to'g'ri "
            "<code>fetch</code> chaqiradi, hech qanday <code>useEffect</code> kerak emas.</li>"
            "<li><strong>Server/Client chegarasi</strong>: har bir post kartasi statik (Server "
            "Component), lekin \"Like\" tugmasi interaktiv bo'lishi kerak — bu "
            "<code>'use client'</code> bilan belgilangan alohida kichik komponent bo'lishi "
            "shart, butun sahifa emas.</li>"
            "</ul>"
            "<p>Eng keng tarqalgan xato — butun <code>BlogListPage</code>'ni "
            "<code>'use client'</code> qilib qo'yish, chunki \"bitta tugma interaktiv bo'lishi "
            "kerak\". To'g'ri yondashuv — faqat o'sha tugmani alohida faylga chiqarib, faqat "
            "o'sha faylni Client Component qilish, qolgan hamma narsani Server Component "
            "holida qoldirish.</p>"
        ),
        "text_content_ru": (
            "<h3>Это урок повторения</h3>"
            "<p>Поскольку это практический урок повторения, текст короче — основной акцент на "
            "практике в задании ниже, новая теория не даётся. Мы объединяем изученное в уроках "
            "1-3 (App Router, layout'ы, граница Server/Client) в одном небольшом, но полностью "
            "рабочем примере: главная страница блога.</p>"
            "<h3>Что мы повторяем</h3>"
            "<ul>"
            "<li><strong>Файловая маршрутизация</strong>: <code>app/blog/page.js</code> — "
            "страница списка постов.</li>"
            "<li><strong>Получение данных через Server Component</strong>: "
            "<code>BlogListPage</code> — <code>async</code>-функция, напрямую вызывает "
            "<code>fetch</code>, useEffect не нужен.</li>"
            "<li><strong>Граница Server/Client</strong>: каждая карточка поста статична (Server "
            "Component), но кнопка «Нравится» должна быть интерактивной — это обязательно "
            "отдельный небольшой компонент, помеченный <code>'use client'</code>, а не вся "
            "страница целиком.</li>"
            "</ul>"
            "<p>Самая частая ошибка — сделать весь <code>BlogListPage</code> "
            "<code>'use client'</code>, потому что «одна кнопка должна быть интерактивной». "
            "Правильный подход — вынести только эту кнопку в отдельный файл и сделать Client "
            "Component только его, оставив всё остальное как Server Component.</p>"
        ),
        "code_content": (
            "// app/blog/page.js — Server Component\n"
            "import PostCard from './PostCard';\n"
            "\n"
            "export default async function BlogListPage() {\n"
            "  const posts = await fetch('https://api.example.com/posts').then((r) => r.json());\n"
            "  return (\n"
            "    <ul>\n"
            "      {posts.map((post) => (\n"
            "        <PostCard key={post.slug} post={post} />\n"
            "      ))}\n"
            "    </ul>\n"
            "  );\n"
            "}\n"
            "\n"
            "// app/blog/PostCard.js — Server Component (statik qism)\n"
            "import LikeButton from './LikeButton';\n"
            "\n"
            "export default function PostCard({ post }) {\n"
            "  return (\n"
            "    <li>\n"
            "      <h3>{post.title}</h3>\n"
            "      <LikeButton postSlug={post.slug} /> {/* faqat shu qism Client */}\n"
            "    </li>\n"
            "  );\n"
            "}\n"
            "\n"
            "// app/blog/LikeButton.js — YAGONA Client Component (1-3-darslar takrori)\n"
            "'use client';\n"
            "import { useState } from 'react';\n"
            "\n"
            "export default function LikeButton({ postSlug }) {\n"
            "  const [liked, setLiked] = useState(false);\n"
            "  return (\n"
            "    <button onClick={() => setLiked((v) => !v)}>\n"
            "      {liked ? 'Yoqdi ✓' : \"Yoqtirish\"}\n"
            "    </button>\n"
            "  );\n"
            "}\n"
        ),
        "code_content_ru": (
            "// app/blog/page.js — Server Component\n"
            "import PostCard from './PostCard';\n"
            "\n"
            "export default async function BlogListPage() {\n"
            "  const posts = await fetch('https://api.example.com/posts').then((r) => r.json());\n"
            "  return (\n"
            "    <ul>\n"
            "      {posts.map((post) => (\n"
            "        <PostCard key={post.slug} post={post} />\n"
            "      ))}\n"
            "    </ul>\n"
            "  );\n"
            "}\n"
            "\n"
            "// app/blog/PostCard.js — Server Component (статичная часть)\n"
            "import LikeButton from './LikeButton';\n"
            "\n"
            "export default function PostCard({ post }) {\n"
            "  return (\n"
            "    <li>\n"
            "      <h3>{post.title}</h3>\n"
            "      <LikeButton postSlug={post.slug} /> {/* только эта часть — Client */}\n"
            "    </li>\n"
            "  );\n"
            "}\n"
            "\n"
            "// app/blog/LikeButton.js — ЕДИНСТВЕННЫЙ Client Component (повтор уроков 1-3)\n"
            "'use client';\n"
            "import { useState } from 'react';\n"
            "\n"
            "export default function LikeButton({ postSlug }) {\n"
            "  const [liked, setLiked] = useState(false);\n"
            "  return (\n"
            "    <button onClick={() => setLiked((v) => !v)}>\n"
            "      {liked ? 'Нравится ✓' : 'Нравится'}\n"
            "    </button>\n"
            "  );\n"
            "}\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Blog bosh sahifasini quring",
            "task_title_ru": "Соберите главную страницу блога",
            "task_description": (
                "app/blog/page.js (Server Component, fetch orqali postlar ro'yxatini oladi), "
                "PostCard.js (Server Component) va LikeButton.js ('use client', useState bilan) "
                "fayllarini yozing. Postlar ro'yxati kamida sarlavha va Like tugmasini "
                "ko'rsatishi kerak."
            ),
            "task_description_ru": (
                "Напишите файлы app/blog/page.js (Server Component, получает список постов "
                "через fetch), PostCard.js (Server Component) и LikeButton.js ('use client', с "
                "useState). Список постов должен показывать минимум заголовок и кнопку "
                "«Нравится»."
            ),
            "task_requirements": (
                "Faqat LikeButton.js 'use client' bilan boshlanishi kerak, qolgan fayllar Server "
                "Component bo'lib qolishi shart."
            ),
            "task_requirements_ru": (
                "Только LikeButton.js должен начинаться с 'use client', остальные файлы "
                "обязаны оставаться Server Component."
            ),
            "task_technologies": "Next.js, App Router, React Server Components",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: blog bosh sahifasi",
            "description": "To'liq ishlaydigan blog ro'yxati: Server Component'lar + bitta Client Component.",
            "sample_type": "code",
            "code_files": [
                {"filename": "app/blog/page.js", "language": "jsx",
                 "code": "import PostCard from './PostCard';\n\nexport default async function BlogListPage() {\n  const posts = await fetch('https://api.example.com/posts').then((r) => r.json());\n  return <ul>{posts.map((p) => <PostCard key={p.slug} post={p} />)}</ul>;\n}\n"},
                {"filename": "app/blog/LikeButton.js", "language": "jsx",
                 "code": "'use client';\nimport { useState } from 'react';\n\nexport default function LikeButton({ postSlug }) {\n  const [liked, setLiked] = useState(false);\n  return <button onClick={() => setLiked((v) => !v)}>{liked ? 'Yoqdi' : 'Yoqtirish'}</button>;\n}\n"},
            ],
        },
        "exercises": [
            {
                "title": "Qaysi fayl Client Component bo'lishi kerak?",
                "title_ru": "Какой файл должен быть Client Component?",
                "description": (
                    "Blog ro'yxati sahifasida faqat Like tugmasi interaktiv bo'lishi kerak. "
                    "Qaysi yondashuv to'g'ri?"
                ),
                "description_ru": (
                    "На странице списка блога интерактивной должна быть только кнопка "
                    "«Нравится». Какой подход правильный?"
                ),
                "exercise_type": "multiple_choice",
                "options": [
                    "Butun BlogListPage'ni 'use client' qilish",
                    "Faqat LikeButton'ni alohida faylga chiqarib, o'shani 'use client' qilish",
                    "Har bir komponentni 'use client' qilish, xavfsizroq bo'ladi",
                    "'use client' hech qachon kerak emas",
                ],
                "options_ru": [
                    "Сделать весь BlogListPage 'use client'",
                    "Вынести только LikeButton в отдельный файл и сделать его 'use client'",
                    "Сделать 'use client' для каждого компонента, так безопаснее",
                    "'use client' никогда не нужен",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Chegarani iloji boricha kichik qiling.",
                "hint_ru": "Делайте границу максимально маленькой.",
                "explanation": "Faqat interaktiv qismni Client Component qilish — bandle hajmini minimal saqlaydi.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Blog ro'yxatida ma'lumot olish",
                "title_ru": "Получение данных в списке блога",
                "description": (
                    "Bo'shliqni to'ldiring: Server Component ichida ma'lumot olish uchun "
                    "komponent funksiyasi ___ kalit so'zi bilan e'lon qilinishi kerak (fetch'ni "
                    "await qilish uchun)."
                ),
                "description_ru": (
                    "Заполните пропуск: чтобы получать данные внутри Server Component, функция "
                    "компонента должна быть объявлена с ключевым словом ___ (чтобы можно было "
                    "делать await для fetch)."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "async",
                "hint": "Bu — JavaScript'ning umumiy kalit so'zi, faqat Next.js'ga xos emas.",
                "hint_ru": "Это общее ключевое слово JavaScript, не специфичное для Next.js.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Komponentlar tartibini tiklang",
                "title_ru": "Восстановите порядок компонентов",
                "description": (
                    "Blog ro'yxati ma'lumot oqimini tashqi qatlamdan eng ichki interaktiv "
                    "qismgacha tartibga joylashtiring."
                ),
                "description_ru": (
                    "Расставьте поток данных списка блога от внешнего слоя до самого "
                    "вложенного интерактивного элемента."
                ),
                "exercise_type": "drag_and_drop",
                "drag_items": ["BlogListPage (fetch qiladi)", "PostCard (post'ni ko'rsatadi)", "LikeButton (interaktiv)"],
                "drag_items_ru": ["BlogListPage (делает fetch)", "PostCard (показывает post)", "LikeButton (интерактивный)"],
                "correct_order": ["BlogListPage (fetch qiladi)", "PostCard (post'ni ko'rsatadi)", "LikeButton (interaktiv)"],
                "hint": "Ma'lumot yuqoridan pastga oqadi.",
                "hint_ru": "Данные текут сверху вниз.",
                "difficulty_level": "Easy",
                "points": 10,
            },
        ],
    },
    {
        "order": 5,
        "title": "5-Ma'lumot olish: async komponentlar, fetch keshi va revalidatsiya",
        "title_ru": "5-Получение данных: async-компоненты, кеш fetch и ревалидация",
        "points_reward": 15,
        "text_content": (
            "<h3>CRA'dagi useEffect naqshidan qutulish</h3>"
            "<p>CRA'da (shu platformaning frontend'ida) ma'lumot olish deyarli har doim uchta "
            "qadamdan iborat: <code>useState</code> bilan bo'sh holat yaratiladi, "
            "<code>useEffect</code> ichida <code>fetch</code> chaqiriladi, keyin natija "
            "<code>setState</code> orqali holatga yoziladi — va shu vaqt oralig'ida komponent "
            "\"yuklanmoqda\" holatini ko'rsatadi. Bu naqsh ishlaydi, lekin u — brauzerda "
            "ishlaydigan kod uchun kerak bo'lgan \"aylanma yo'l\": chunki brauzer render "
            "paytida ma'lumot hali yo'q, keyin keladi.</p>"
            "<p>Server Component'da bu muammo umuman yo'q. Komponent funksiyasining o'zi "
            "<code>async</code> deb e'lon qilinadi, va ichida to'g'ridan-to'g'ri "
            "<code>await fetch(...)</code> yoziladi — server render qilishdan OLDIN ma'lumotni "
            "kutib turadi, shuning uchun \"yuklanmoqda\" holati kerak emas (agar kerak bo'lsa, "
            "<code>loading.js</code> orqali butun marshrut darajasida ko'rsatiladi — 2-darsda "
            "ko'rgan edik).</p>"
            "<h3>fetch — kengaytirilgan, keshlash bilan</h3>"
            "<p>Next.js oddiy brauzer/Node <code>fetch</code> funksiyasini kengaytiradi va "
            "unga ikkinchi argument sifatida keshlash sozlamalarini qo'shadi:</p>"
            "<ul>"
            "<li><code>fetch(url)</code> — sozlamasiz chaqirilsa, natija KESHLANADI (build "
            "vaqtida yoki birinchi so'rovda olingan ma'lumot qayta ishlatiladi — bu SSG'ga "
            "yaqin xatti-harakat, 6-darsda chuqur ko'ramiz).</li>"
            "<li><code>fetch(url, { cache: 'no-store' })</code> — hech qachon keshlanmaydi, "
            "har bir so'rovda serverdan yangi ma'lumot olinadi (SSR'ga mos xatti-harakat).</li>"
            "<li><code>fetch(url, { next: { revalidate: 60 } })</code> — natija 60 soniya "
            "davomida keshda saqlanadi, shundan keyin fon rejimida yangilanadi (bu — ISR, "
            "Incremental Static Regeneration).</li>"
            "</ul>"
            "<h3>Parallel va ketma-ket ma'lumot olish</h3>"
            "<p>Agar bir komponentga ikkita bog'liq bo'lmagan ma'lumot kerak bo'lsa (masalan, "
            "kurs ma'lumoti va sharhlar ro'yxati), ularni ketma-ket <code>await</code> qilish — "
            "\"waterfall\" (sharshara) muammosini keltirib chiqaradi: ikkinchi so'rov birinchisi "
            "tugagunga qadar boshlanmaydi. To'g'ri yechim — <code>Promise.all</code> orqali "
            "ikkalasini BIR VAQTDA boshlash, keyin ikkalasini ham kutish. Bu tarmoq so'rovlari "
            "sonini o'zgartirmaydi, lekin ularni parallel bajaradi.</p>"
            "<h3>Ma'lumotni props orqali pastga uzatish</h3>"
            "<p>Server Component'da olingan ma'lumot — oddiy JavaScript qiymati, uni istalgan "
            "bola komponentga <code>props</code> sifatida uzatish mumkin, xuddi CRA'dagidek. "
            "Farqi shundaki, bu ma'lumot Client Component'ga uzatilganda, u \"serializable\" "
            "(JSON'ga aylantirilishi mumkin) bo'lishi kerak — funksiyalar yoki maxsus klasslar "
            "obyektlarini Server'dan Client'ga to'g'ridan-to'g'ri uzatib bo'lmaydi.</p>"
            "<h3>Dinamik funksiyalar avtomatik SSR'ni yoqadi</h3>"
            "<p>Next.js bir nechta \"dinamik funksiya\"ni taniydi — <code>cookies()</code>, "
            "<code>headers()</code>, yoki sahifaning <code>searchParams</code> propi. Agar "
            "Server Component ichida ulardan biri ishlatilsa, Next.js avtomatik ravishda o'sha "
            "marshrutni HAR BIR SO'ROVDA qayta render qilishga (dynamic rendering) o'tkazadi — "
            "hatto siz buni aniq so'ramagan bo'lsangiz ham. Bu mantiqiy: agar komponent "
            "so'rovga xos cookie'ni o'qisa, uni build vaqtida bir marta render qilib, natijani "
            "keshlab bo'lmaydi — har bir foydalanuvchi boshqa cookie bilan keladi. Buni "
            "keyingi darsda \"render strategiyalari\" mavzusida yanada chuqur ko'ramiz.</p>"
            "<h3>Talab bo'yicha revalidatsiya: revalidatePath / revalidateTag</h3>"
            "<p>Vaqt asosidagi revalidatsiya (<code>next: { revalidate: 60 }</code>) ba'zan "
            "yetarli emas — masalan, admin yangi kurs qo'shganda, keshni 60 soniya kutmasdan "
            "DARHOL yangilash kerak bo'lishi mumkin. Aynan shu uchun Next.js "
            "<code>revalidatePath('/courses')</code> va <code>revalidateTag('courses')</code> "
            "funksiyalarini beradi — bu funksiyalar odatda Route Handler yoki Server Action "
            "ichida chaqiriladi (masalan, yangi kurs saqlangandan darhol keyin) va aniq bir "
            "yo'l yoki teg bo'yicha keshni majburan eskirgan deb belgilaydi.</p>"
            "<h3>Diagram: parallel vs ketma-ket so'rovlar</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  subgraph SEQ[\"Ketma-ket (waterfall) - sekinroq\"]\n"
            "    S1[\"await getCourse()\"] --> S2[\"await getReviews()\"]\n"
            "    S2 --> S3[\"Render\"]\n"
            "  end\n"
            "  subgraph PAR[\"Parallel (Promise.all) - tezroq\"]\n"
            "    P1[\"getCourse()\"] --> P3[\"Promise.all\n"
            "ikkalasini kutish\"]\n"
            "    P2[\"getReviews()\"] --> P3\n"
            "    P3 --> P4[\"Render\"]\n"
            "  end\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: ketma-ket yondashuvda ikkinchi so'rov birinchisi "
            "tugagunga qadar hatto boshlanmaydi ham, parallel yondashuvda esa ikkalasi bir "
            "vaqtda ishga tushadi.</p>"
        ),
        "text_content_ru": (
            "<h3>Избавляемся от паттерна useEffect из CRA</h3>"
            "<p>В CRA (фронтенде этой платформы) получение данных почти всегда состоит из трёх "
            "шагов: создаётся пустое состояние через <code>useState</code>, внутри "
            "<code>useEffect</code> вызывается <code>fetch</code>, затем результат "
            "записывается в состояние через <code>setState</code> — и всё это время компонент "
            "показывает состояние «загрузка». Этот паттерн работает, но это «обходной путь», "
            "нужный именно потому, что код выполняется в браузере: во время рендера данных ещё "
            "нет, они появятся позже.</p>"
            "<p>В Server Component этой проблемы вообще нет. Сама функция компонента "
            "объявляется как <code>async</code>, и внутри неё пишется прямой "
            "<code>await fetch(...)</code> — сервер дожидается данных ДО рендеринга, поэтому "
            "состояние «загрузка» не нужно (а если нужно — оно показывается на уровне всего "
            "маршрута через <code>loading.js</code>, который мы видели в уроке 2).</p>"
            "<h3>fetch — расширенный, с кешированием</h3>"
            "<p>Next.js расширяет обычную функцию <code>fetch</code> браузера/Node и добавляет "
            "ей второй аргумент с настройками кеширования:</p>"
            "<ul>"
            "<li><code>fetch(url)</code> — без настроек результат КЕШИРУЕТСЯ (данные, "
            "полученные во время сборки или при первом запросе, переиспользуются — это "
            "поведение, близкое к SSG, подробно разберём в уроке 6).</li>"
            "<li><code>fetch(url, { cache: 'no-store' })</code> — никогда не кешируется, при "
            "каждом запросе данные получаются заново с сервера (поведение, соответствующее "
            "SSR).</li>"
            "<li><code>fetch(url, { next: { revalidate: 60 } })</code> — результат хранится в "
            "кеше 60 секунд, после чего обновляется в фоне (это ISR, Incremental Static "
            "Regeneration).</li>"
            "</ul>"
            "<h3>Параллельное и последовательное получение данных</h3>"
            "<p>Если одному компоненту нужны две независимые друг от друга порции данных "
            "(например, информация о курсе и список отзывов), их последовательный "
            "<code>await</code> вызывает проблему «waterfall» (водопад): второй запрос не "
            "начинается, пока не завершится первый. Правильное решение — запустить оба запроса "
            "ОДНОВРЕМЕННО через <code>Promise.all</code>, а затем дождаться обоих. Это не "
            "меняет количество сетевых запросов, но выполняет их параллельно.</p>"
            "<h3>Передача данных вниз через props</h3>"
            "<p>Данные, полученные в Server Component, — обычное значение JavaScript, его можно "
            "передать любому дочернему компоненту через <code>props</code>, точно как в CRA. "
            "Разница в том, что при передаче в Client Component это значение должно быть "
            "«сериализуемым» (превращаемым в JSON) — функции или объекты специальных классов "
            "нельзя напрямую передать с сервера на клиент.</p>"
            "<h3>Динамические функции автоматически включают SSR</h3>"
            "<p>Next.js распознаёт несколько «динамических функций» — <code>cookies()</code>, "
            "<code>headers()</code>, или проп страницы <code>searchParams</code>. Если внутри "
            "Server Component используется одна из них, Next.js автоматически переводит этот "
            "маршрут на рендеринг ПРИ КАЖДОМ ЗАПРОСЕ (dynamic rendering) — даже если вы явно "
            "об этом не просили. Это логично: если компонент читает cookie конкретного запроса, "
            "нельзя отрендерить его один раз во время сборки и закешировать результат — каждый "
            "пользователь приходит с другим cookie. Разберём это подробнее в следующем уроке о "
            "стратегиях рендеринга.</p>"
            "<h3>Ревалидация по требованию: revalidatePath / revalidateTag</h3>"
            "<p>Ревалидации по времени (<code>next: { revalidate: 60 }</code>) иногда "
            "недостаточно — например, когда админ добавляет новый курс, кеш может понадобиться "
            "обновить НЕМЕДЛЕННО, не дожидаясь 60 секунд. Именно для этого Next.js предоставляет "
            "функции <code>revalidatePath('/courses')</code> и "
            "<code>revalidateTag('courses')</code> — они обычно вызываются внутри Route "
            "Handler'а или Server Action (например, сразу после сохранения нового курса) и "
            "принудительно помечают кеш по конкретному пути или тегу как устаревший.</p>"
            "<h3>Диаграмма: параллельные vs последовательные запросы</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  subgraph SEQ[\"Последовательно (waterfall) - медленнее\"]\n"
            "    S1[\"await getCourse()\"] --> S2[\"await getReviews()\"]\n"
            "    S2 --> S3[\"Render\"]\n"
            "  end\n"
            "  subgraph PAR[\"Параллельно (Promise.all) - быстрее\"]\n"
            "    P1[\"getCourse()\"] --> P3[\"Promise.all\n"
            "ждём оба\"]\n"
            "    P2[\"getReviews()\"] --> P3\n"
            "    P3 --> P4[\"Render\"]\n"
            "  end\n"
            "</pre>"
            "<p>Диаграмма показывает: в последовательном подходе второй запрос даже не "
            "начинается, пока не завершится первый, а в параллельном оба запускаются "
            "одновременно.</p>"
        ),
        "code_content": (
            "// ===== app/courses/[id]/page.js — uchta keshlash strategiyasi yonma-yon =====\n"
            "async function getCourse(id) {\n"
            "  // 1) DEFAULT: keshlanadi (SSG'ga yaqin) — build/birinchi so'rovda olinadi\n"
            "  const res = await fetch(`https://api.example.com/courses/${id}`);\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "async function getReviews(id) {\n"
            "  // 2) NO-STORE: har doim yangi (SSR'ga yaqin) — har so'rovda qayta olinadi\n"
            "  const res = await fetch(`https://api.example.com/courses/${id}/reviews`, {\n"
            "    cache: 'no-store',\n"
            "  });\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "async function getRelatedCourses(categoryId) {\n"
            "  // 3) REVALIDATE: ISR — 120 soniyada bir marta fonda yangilanadi\n"
            "  const res = await fetch(`https://api.example.com/categories/${categoryId}/courses`, {\n"
            "    next: { revalidate: 120 },\n"
            "  });\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function CoursePage({ params }) {\n"
            "  const { id } = await params;\n"
            "\n"
            "  // XATO YO'L (waterfall) — ikkinchisi birinchisi tugagunga qadar kutadi:\n"
            "  // const course = await getCourse(id);\n"
            "  // const reviews = await getReviews(id);       // ❌ keraksiz kutish\n"
            "\n"
            "  // TO'G'RI YO'L: barchasi bir vaqtda boshlanadi\n"
            "  const course = await getCourse(id); // categoryId kerak, shuning uchun avval\n"
            "  const [reviews, related] = await Promise.all([\n"
            "    getReviews(id),\n"
            "    getRelatedCourses(course.categoryId),\n"
            "  ]);\n"
            "\n"
            "  return (\n"
            "    <article>\n"
            "      <h1>{course.title}</h1>\n"
            "      <p>{course.description}</p>\n"
            "      <h2>Sharhlar ({reviews.length})</h2>\n"
            "      <ul>\n"
            "        {reviews.map((r) => (\n"
            "          <li key={r.id}>{r.text}</li>\n"
            "        ))}\n"
            "      </ul>\n"
            "      <h2>O'xshash kurslar</h2>\n"
            "      <ul>\n"
            "        {related.map((c) => (\n"
            "          <li key={c.id}>{c.title}</li>\n"
            "        ))}\n"
            "      </ul>\n"
            "    </article>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/courses/page.js — tag orqali belgilangan fetch =====\n"
            "// revalidateTag bilan ishlashi uchun fetch'ning o'ziga teg berilishi kerak\n"
            "async function getAllCourses() {\n"
            "  const res = await fetch('https://api.example.com/courses', {\n"
            "    next: { tags: ['courses'] }, // <- shu teg keyinroq revalidateTag'da ishlatiladi\n"
            "  });\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function CoursesListPage() {\n"
            "  const courses = await getAllCourses();\n"
            "  return <ul>{courses.map((c) => <li key={c.id}>{c.title}</li>)}</ul>;\n"
            "}\n"
            "\n"
            "// ===== app/api/courses/route.js — talab bo'yicha revalidatsiya =====\n"
            "import { NextResponse } from 'next/server';\n"
            "import { revalidatePath, revalidateTag } from 'next/cache';\n"
            "\n"
            "export async function POST(request) {\n"
            "  const body = await request.json();\n"
            "  // ... yangi kursni saqlash mantig'i shu yerda ...\n"
            "  revalidatePath('/courses');   // /courses sahifasi keshini darhol yangilaydi\n"
            "  revalidateTag('courses');     // 'courses' tegi bilan olingan HAR QANDAY fetch'ni ham\n"
            "  return NextResponse.json({ ok: true }, { status: 201 });\n"
            "}\n"
            "\n"
            "// ===== Uchta strategiyaning solishtiruv jadvali (izoh sifatida) =====\n"
            "// fetch(url)                                  -> keshlanadi, qayta so'ralmaydi\n"
            "// fetch(url, { cache: 'no-store' })            -> hech qachon keshlanmaydi\n"
            "// fetch(url, { next: { revalidate: 120 } })    -> 120s'dan keyin fonda yangilanadi\n"
            "// fetch(url, { next: { tags: ['courses'] } })  -> revalidateTag('courses') bilan\n"
            "//                                                  QO'LDA yangilanishi mumkin\n"
        ),
        "code_content_ru": (
            "// ===== app/courses/[id]/page.js — три стратегии кеширования рядом =====\n"
            "async function getCourse(id) {\n"
            "  // 1) DEFAULT: кешируется (близко к SSG) — получается при сборке/первом запросе\n"
            "  const res = await fetch(`https://api.example.com/courses/${id}`);\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "async function getReviews(id) {\n"
            "  // 2) NO-STORE: всегда свежие (близко к SSR) — заново при каждом запросе\n"
            "  const res = await fetch(`https://api.example.com/courses/${id}/reviews`, {\n"
            "    cache: 'no-store',\n"
            "  });\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "async function getRelatedCourses(categoryId) {\n"
            "  // 3) REVALIDATE: ISR — обновляется в фоне раз в 120 секунд\n"
            "  const res = await fetch(`https://api.example.com/categories/${categoryId}/courses`, {\n"
            "    next: { revalidate: 120 },\n"
            "  });\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function CoursePage({ params }) {\n"
            "  const { id } = await params;\n"
            "\n"
            "  // НЕПРАВИЛЬНЫЙ ПУТЬ (waterfall) — второй ждёт завершения первого:\n"
            "  // const course = await getCourse(id);\n"
            "  // const reviews = await getReviews(id);       // ❌ лишнее ожидание\n"
            "\n"
            "  // ПРАВИЛЬНЫЙ ПУТЬ: всё запускается одновременно\n"
            "  const course = await getCourse(id); // нужен categoryId, поэтому сначала\n"
            "  const [reviews, related] = await Promise.all([\n"
            "    getReviews(id),\n"
            "    getRelatedCourses(course.categoryId),\n"
            "  ]);\n"
            "\n"
            "  return (\n"
            "    <article>\n"
            "      <h1>{course.title}</h1>\n"
            "      <p>{course.description}</p>\n"
            "      <h2>Отзывы ({reviews.length})</h2>\n"
            "      <ul>\n"
            "        {reviews.map((r) => (\n"
            "          <li key={r.id}>{r.text}</li>\n"
            "        ))}\n"
            "      </ul>\n"
            "      <h2>Похожие курсы</h2>\n"
            "      <ul>\n"
            "        {related.map((c) => (\n"
            "          <li key={c.id}>{c.title}</li>\n"
            "        ))}\n"
            "      </ul>\n"
            "    </article>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/courses/page.js — fetch, помеченный тегом =====\n"
            "// чтобы работал revalidateTag, самому fetch нужно дать тег\n"
            "async function getAllCourses() {\n"
            "  const res = await fetch('https://api.example.com/courses', {\n"
            "    next: { tags: ['courses'] }, // <- этот тег позже используется в revalidateTag\n"
            "  });\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function CoursesListPage() {\n"
            "  const courses = await getAllCourses();\n"
            "  return <ul>{courses.map((c) => <li key={c.id}>{c.title}</li>)}</ul>;\n"
            "}\n"
            "\n"
            "// ===== app/api/courses/route.js — ревалидация по требованию =====\n"
            "import { NextResponse } from 'next/server';\n"
            "import { revalidatePath, revalidateTag } from 'next/cache';\n"
            "\n"
            "export async function POST(request) {\n"
            "  const body = await request.json();\n"
            "  // ... логика сохранения нового курса здесь ...\n"
            "  revalidatePath('/courses');   // немедленно обновляет кеш страницы /courses\n"
            "  revalidateTag('courses');     // и ЛЮБОЙ fetch, полученный с тегом 'courses'\n"
            "  return NextResponse.json({ ok: true }, { status: 201 });\n"
            "}\n"
            "\n"
            "// ===== Сравнительная таблица трёх стратегий (в виде комментария) =====\n"
            "// fetch(url)                                  -> кешируется, заново не запрашивается\n"
            "// fetch(url, { cache: 'no-store' })            -> никогда не кешируется\n"
            "// fetch(url, { next: { revalidate: 120 } })    -> обновляется в фоне через 120с\n"
            "// fetch(url, { next: { tags: ['courses'] } })  -> можно обновить ВРУЧНУЮ через\n"
            "//                                                  revalidateTag('courses')\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Parallel ma'lumot olishni amalga oshiring",
            "task_title_ru": "Реализуйте параллельное получение данных",
            "task_description": (
                "Kurs sahifasi uchun ikkita mustaqil ma'lumot manbasini (kurs ma'lumoti va "
                "sharhlar) Promise.all orqali parallel oling. Har biriga mos keshlash "
                "sozlamasini (cache yoki next.revalidate) tanlang va nima uchun aynan shuni "
                "tanlaganingizni tushuntiring."
            ),
            "task_description_ru": (
                "Получите два независимых источника данных для страницы курса (информация о "
                "курсе и отзывы) параллельно через Promise.all. Для каждого выберите "
                "подходящую настройку кеширования (cache или next.revalidate) и объясните, "
                "почему выбрали именно её."
            ),
            "task_requirements": (
                "Promise.all ishlatilishi, kamida bitta fetch'da cache: 'no-store' yoki "
                "next.revalidate qo'llanilishi shart."
            ),
            "task_requirements_ru": (
                "Обязательно использование Promise.all, минимум один fetch должен применять "
                "cache: 'no-store' или next.revalidate."
            ),
            "task_technologies": "Next.js, fetch API",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: parallel ma'lumot olish",
            "description": "Kurs va sharhlarni Promise.all orqali parallel olish namunasi.",
            "sample_type": "code",
            "code_files": [
                {"filename": "app/courses/[id]/page.js", "language": "jsx",
                 "code": "async function getCourse(id) {\n  return fetch(`https://api.example.com/courses/${id}`).then((r) => r.json());\n}\nasync function getReviews(id) {\n  return fetch(`https://api.example.com/courses/${id}/reviews`, { cache: 'no-store' }).then((r) => r.json());\n}\n\nexport default async function CoursePage({ params }) {\n  const { id } = await params;\n  const [course, reviews] = await Promise.all([getCourse(id), getReviews(id)]);\n  return (\n    <article>\n      <h1>{course.title}</h1>\n      <p>{reviews.length} ta sharh</p>\n    </article>\n  );\n}\n"},
            ],
        },
        "exercises": [
            {
                "title": "Har doim yangi ma'lumot",
                "title_ru": "Всегда свежие данные",
                "description": "Har bir so'rovda hech qachon keshlanmaydigan fetch sozlamasi qaysi?",
                "description_ru": "Какая настройка fetch означает, что данные никогда не кешируются на каждый запрос?",
                "exercise_type": "multiple_choice",
                "options": [
                    "fetch(url)",
                    "fetch(url, { cache: 'no-store' })",
                    "fetch(url, { next: { revalidate: 60 } })",
                    "fetch(url, { method: 'GET' })",
                ],
                "options_ru": [
                    "fetch(url)",
                    "fetch(url, { cache: 'no-store' })",
                    "fetch(url, { next: { revalidate: 60 } })",
                    "fetch(url, { method: 'GET' })",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Bu SSR'ga mos xatti-harakat.",
                "hint_ru": "Это поведение, соответствующее SSR.",
                "explanation": "cache: 'no-store' fetch natijasini hech qachon keshlamaydi.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Server Component funksiyasi",
                "title_ru": "Функция Server Component",
                "description": (
                    "Bo'shliqni to'ldiring: Server Component ichida to'g'ridan-to'g'ri fetch "
                    "await qilish uchun komponent funksiyasi ___ kalit so'zi bilan yozilishi kerak."
                ),
                "description_ru": (
                    "Заполните пропуск: чтобы напрямую делать await для fetch внутри Server "
                    "Component, функция компонента должна быть написана с ключевым словом ___."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "async",
                "hint": "JavaScript'ning standart kalit so'zi.",
                "hint_ru": "Стандартное ключевое слово JavaScript.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Waterfall'dan qutulish qadamlari",
                "title_ru": "Шаги избавления от waterfall",
                "description": (
                    "Ikkita mustaqil so'rovni parallel bajarish qadamlarini to'g'ri tartibga "
                    "joylashtiring."
                ),
                "description_ru": (
                    "Расставьте по порядку шаги параллельного выполнения двух независимых "
                    "запросов."
                ),
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "getCourse(id) chaqiriladi (await qilinmasdan)",
                    "getReviews(id) chaqiriladi (await qilinmasdan)",
                    "Promise.all([...]) ikkalasini kutadi",
                    "Natijalar destrukturizatsiya qilinadi",
                ],
                "drag_items_ru": [
                    "Вызывается getCourse(id) (без await)",
                    "Вызывается getReviews(id) (без await)",
                    "Promise.all([...]) ждёт оба",
                    "Результаты деструктурируются",
                ],
                "correct_order": [
                    "getCourse(id) chaqiriladi (await qilinmasdan)",
                    "getReviews(id) chaqiriladi (await qilinmasdan)",
                    "Promise.all([...]) ikkalasini kutadi",
                    "Natijalar destrukturizatsiya qilinadi",
                ],
                "hint": "Ikkala funksiya avval await'siz chaqiriladi, keyin birgalikda kutiladi.",
                "hint_ru": "Обе функции сначала вызываются без await, потом ожидаются вместе.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 6,
        "title": "6-Render strategiyalari: SSR, SSG va ISR",
        "title_ru": "6-Стратегии рендеринга: SSR, SSG и ISR",
        "points_reward": 15,
        "text_content": (
            "<h3>Uchta strategiya — bitta savolga uchta javob</h3>"
            "<p>Oldingi darsda ko'rgan <code>fetch</code>'ning keshlash sozlamalari aslida "
            "kattaroq savolga javob beradi: <strong>\"HTML qachon tayyorlanadi — build "
            "vaqtidami, so'rov paytidami, yoki ikkalasi ham?\"</strong> Bu savolga uchta javob "
            "bor, va ular Next.js'ning uchta asosiy render strategiyasini tashkil qiladi. Bu "
            "yerda o'ylab topilgan raqamlar yoki benchmarklar yo'q — faqat har birining qachon "
            "mos kelishini halol taqqoslaymiz.</p>"
            "<h3>SSG — Static Site Generation</h3>"
            "<p>HTML <strong>build vaqtida</strong>, bir marta, oldindan tayyorlanadi. Keyin har "
            "bir so'rov uchun xuddi shu tayyor HTML qaytariladi — server hech qanday qo'shimcha "
            "ish qilmaydi, natijada bu strategiya eng tez javob beradi va CDN orqali osongina "
            "tarqatiladi. Mos keladigan holatlar: blog postlari, hujjatlar, mahsulot "
            "tavsiflari — tez-tez o'zgarmaydigan, barcha foydalanuvchilar uchun bir xil "
            "ko'rinadigan kontent. Kamchiligi: ma'lumot yangilanishi uchun qayta build kerak "
            "(yoki quyida ko'radigan ISR).</p>"
            "<h3>SSR — Server-Side Rendering</h3>"
            "<p>HTML <strong>har bir so'rovda serverda qaytadan</strong> render qilinadi — "
            "<code>fetch(url, { cache: 'no-store' })</code> ishlatilganda yoki 5-darsda "
            "ko'rgan dinamik funksiyalar (<code>cookies()</code>, <code>headers()</code>) "
            "chaqirilganda avtomatik yoqiladi. Mos keladigan holatlar: foydalanuvchiga xos "
            "kontent (masalan, \"Mening buyurtmalarim\" sahifasi), yoki har doim eng so'nggi "
            "ma'lumot ko'rsatilishi shart bo'lgan holatlar (masalan, birja narxlari). Kamchiligi: "
            "har bir so'rov server ishlashini talab qiladi — SSG kabi \"bepul\" emas.</p>"
            "<h3>ISR — Incremental Static Regeneration</h3>"
            "<p>SSG'ning tezligi bilan SSR'ning yangilanish imkoniyatini birlashtiradi: HTML "
            "static sifatida saqlanadi (SSG kabi), lekin belgilangan vaqt oralig'idan "
            "(<code>next: { revalidate: N }</code>) keyin FON REJIMIDA qayta generatsiya "
            "qilinadi — foydalanuvchi hech qachon \"kutish\" holatini ko'rmaydi, u eski (lekin "
            "hali ham tez) versiyani oladi, shu orada server orqada yangisini tayyorlaydi. Mos "
            "keladigan holatlar: kurs katalogi, mahsulotlar ro'yxati — vaqti-vaqti bilan "
            "o'zgaradigan, lekin har bir so'rovda qayta hisoblashga arzimaydigan kontent.</p>"
            "<h3>Diagram: uchta strategiyaning vaqt chizig'i</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  subgraph SSG[\"SSG\"]\n"
            "    G1[\"Build vaqtida bir marta render\"] --> G2[\"Har bir so'rovga\n"
            "xuddi shu tayyor HTML\"]\n"
            "  end\n"
            "  subgraph SSR[\"SSR\"]\n"
            "    R1[\"Har bir so'rov keladi\"] --> R2[\"Serverda qaytadan render\"]\n"
            "    R2 --> R3[\"Yangi HTML qaytadi\"]\n"
            "  end\n"
            "  subgraph ISR[\"ISR\"]\n"
            "    I1[\"Static HTML xizmat qiladi\n"
            "(tez)\"] --> I2{\"revalidate vaqti\n"
            "o'tdimi?\"}\n"
            "    I2 -->|\"yo'q\"| I1\n"
            "    I2 -->|\"ha\"| I3[\"Fonda qayta generatsiya\n"
            "keyingi so'rovlar yangisini oladi\"]\n"
            "  end\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: SSG bir marta render qilib, o'shani abadiy "
            "qaytaradi; SSR har safar qaytadan ishlaydi; ISR esa static tezlikni saqlab, "
            "fonda o'z-o'zini yangilab turadi.</p>"
            "<h3>Qanday tanlash kerak</h3>"
            "<p>Savol shu: \"bu kontent qanchalik tez-tez o'zgaradi, va u har bir foydalanuvchi "
            "uchun bir xilmi?\" Bir xil va kam o'zgaradigan — SSG. Foydalanuvchiga xos yoki "
            "doim yangi bo'lishi shart — SSR. Bir xil, lekin vaqti-vaqti bilan o'zgaradigan — "
            "ISR. Bitta ilova ichida uchtasini ham aralash ishlatish mumkin — hatto bitta "
            "sahifaning turli qismlari turli strategiyaga ega bo'lishi mumkin.</p>"
            "<h3>Marshrut darajasida boshqarish</h3>"
            "<p><code>fetch</code>'ning o'z sozlamalaridan tashqari, butun marshrut uchun ham "
            "aniq ko'rsatma berish mumkin: <code>export const dynamic = 'force-dynamic'</code> "
            "— marshrutni majburan har doim SSR qiladi (hech qanday fetch keshlash sozlamasidan "
            "qat'iy nazar); <code>export const dynamic = 'force-static'</code> — aksincha, "
            "hattoki dinamik funksiyalar bo'lsa ham build vaqtidagi natijani \"muzlatadi\". "
            "Bular — nozik holatlar uchun qo'lda boshqarish vositalari, kundalik ishda ko'pincha "
            "shunchaki <code>fetch</code>ning o'z sozlamalari yetarli bo'ladi.</p>"
            "<p>Dinamik marshrutlar ([id] kabi) uchun SSG'ni qanday ishlatish mumkinligini — "
            "ya'ni Next.js'ga oldindan qaysi id'lar uchun sahifa tayyorlash kerakligini qanday "
            "aytish mumkinligini (<code>generateStaticParams</code>) — 8-darsda ko'ramiz.</p>"
            "<p>Xulosa qilib aytganda: bu uch strategiya bir-biriga zid emas, balki bir vositalar "
            "to'plami — tajribali Next.js dasturchisi ularni loyihaning har bir qismi uchun "
            "alohida-alohida, ongli ravishda tanlaydi.</p>"
        ),
        "text_content_ru": (
            "<h3>Три стратегии — три ответа на один вопрос</h3>"
            "<p>Настройки кеширования <code>fetch</code>, которые мы видели в прошлом уроке, "
            "на самом деле отвечают на более крупный вопрос: <strong>«Когда готовится HTML — во "
            "время сборки, во время запроса, или и то, и другое?»</strong> На этот вопрос есть "
            "три ответа, и они формируют три основные стратегии рендеринга Next.js. Здесь нет "
            "выдуманных цифр или бенчмарков — только честное сравнение, когда какая подходит.</p>"
            "<h3>SSG — Static Site Generation (статическая генерация)</h3>"
            "<p>HTML готовится <strong>во время сборки</strong>, один раз, заранее. Затем на "
            "каждый запрос возвращается тот же самый готовый HTML — сервер не делает никакой "
            "дополнительной работы, поэтому эта стратегия отвечает быстрее всего и легко "
            "раздаётся через CDN. Подходящие случаи: посты блога, документация, описания "
            "товаров — контент, который не меняется часто и одинаков для всех пользователей. "
            "Недостаток: для обновления данных нужна пересборка (или ISR, которую разберём "
            "ниже).</p>"
            "<h3>SSR — Server-Side Rendering (серверный рендеринг)</h3>"
            "<p>HTML <strong>рендерится заново на сервере при каждом запросе</strong> — "
            "включается автоматически при использовании "
            "<code>fetch(url, { cache: 'no-store' })</code> или динамических функций из урока "
            "5 (<code>cookies()</code>, <code>headers()</code>). Подходящие случаи: контент, "
            "специфичный для пользователя (например, страница «Мои заказы»), или ситуации, где "
            "обязательно нужны самые свежие данные (например, биржевые котировки). Недостаток: "
            "каждый запрос требует работы сервера — это не «бесплатно», как SSG.</p>"
            "<h3>ISR — Incremental Static Regeneration (инкрементальная статическая регенерация)</h3>"
            "<p>Объединяет скорость SSG с возможностью обновления SSR: HTML хранится как "
            "статический (как в SSG), но по истечении заданного интервала "
            "(<code>next: { revalidate: N }</code>) регенерируется В ФОНЕ — пользователь "
            "никогда не видит состояния «ожидание», он получает старую (но всё ещё быструю) "
            "версию, пока сервер в фоне готовит новую. Подходящие случаи: каталог курсов, "
            "список товаров — контент, который меняется время от времени, но пересчитывать "
            "который на каждый запрос не имеет смысла.</p>"
            "<h3>Диаграмма: временная шкала трёх стратегий</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  subgraph SSG[\"SSG\"]\n"
            "    G1[\"Рендер один раз во время сборки\"] --> G2[\"На каждый запрос —\n"
            "тот же готовый HTML\"]\n"
            "  end\n"
            "  subgraph SSR[\"SSR\"]\n"
            "    R1[\"Приходит каждый запрос\"] --> R2[\"Рендер заново на сервере\"]\n"
            "    R2 --> R3[\"Возвращается новый HTML\"]\n"
            "  end\n"
            "  subgraph ISR[\"ISR\"]\n"
            "    I1[\"Статичный HTML отдаётся\n"
            "(быстро)\"] --> I2{\"Время revalidate\n"
            "прошло?\"}\n"
            "    I2 -->|\"нет\"| I1\n"
            "    I2 -->|\"да\"| I3[\"Регенерация в фоне\n"
            "следующие запросы получат новое\"]\n"
            "  end\n"
            "</pre>"
            "<p>Диаграмма показывает: SSG рендерит один раз и возвращает это вечно; SSR каждый "
            "раз работает заново; ISR же сохраняет скорость статики и обновляет себя в фоне.</p>"
            "<h3>Как выбирать</h3>"
            "<p>Вопрос такой: «Как часто меняется этот контент, и одинаков ли он для каждого "
            "пользователя?» Одинаковый и редко меняющийся — SSG. Специфичный для пользователя "
            "или обязательно самый свежий — SSR. Одинаковый, но меняющийся время от времени — "
            "ISR. В одном приложении можно смешивать все три — даже разные части одной страницы "
            "могут использовать разные стратегии.</p>"
            "<h3>Управление на уровне маршрута</h3>"
            "<p>Кроме собственных настроек <code>fetch</code>, можно дать явное указание для "
            "всего маршрута: <code>export const dynamic = 'force-dynamic'</code> — "
            "принудительно делает маршрут всегда SSR (независимо от настроек кеширования "
            "внутри fetch); <code>export const dynamic = 'force-static'</code> — наоборот, "
            "«замораживает» результат времени сборки, даже если используются динамические "
            "функции. Это инструменты ручного управления для нестандартных случаев, в "
            "повседневной работе обычно достаточно собственных настроек <code>fetch</code>.</p>"
            "<p>Как применять SSG к динамическим маршрутам (вроде [id]) — то есть как сказать "
            "Next.js заранее, для каких именно id нужно подготовить страницу "
            "(<code>generateStaticParams</code>) — разберём в уроке 8.</p>"
            "<p>Подводя итог: эти три стратегии не противоречат друг другу, а образуют единый "
            "набор инструментов — опытный разработчик на Next.js выбирает нужную осознанно, "
            "отдельно для каждой части проекта.</p>"
        ),
        "code_content": (
            "// ===== 1) SSG: app/blog/page.js — build vaqtida render, statik qoladi =====\n"
            "async function getStaticPosts() {\n"
            "  const res = await fetch('https://api.example.com/posts');\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function BlogPage() {\n"
            "  const posts = await getStaticPosts();\n"
            "  return (\n"
            "    <ul>\n"
            "      {posts.map((p) => <li key={p.id}>{p.title}</li>)}\n"
            "    </ul>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== 2) SSR: app/orders/page.js — har bir so'rovda serverda qaytadan =====\n"
            "import { cookies } from 'next/headers';\n"
            "\n"
            "async function getMyOrders(userId) {\n"
            "  const res = await fetch(`https://api.example.com/orders?user=${userId}`, {\n"
            "    cache: 'no-store', // yoki: dinamik funksiya (cookies/headers) SSR'ni avtomatik yoqadi\n"
            "  });\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function OrdersPage() {\n"
            "  const cookieStore = await cookies(); // <- dinamik funksiya, SSR'ni majburlaydi\n"
            "  const userId = cookieStore.get('user_id')?.value;\n"
            "  const orders = await getMyOrders(userId);\n"
            "\n"
            "  return (\n"
            "    <ul>\n"
            "      {orders.map((o) => <li key={o.id}>{o.total} so'm</li>)}\n"
            "    </ul>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== 3) ISR: app/products/page.js — statik, 300s'da bir fonda yangilanadi =====\n"
            "async function getProductCatalog() {\n"
            "  const res = await fetch('https://api.example.com/products', {\n"
            "    next: { revalidate: 300 },\n"
            "  });\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function ProductsPage() {\n"
            "  const products = await getProductCatalog();\n"
            "  return (\n"
            "    <ul>\n"
            "      {products.map((p) => <li key={p.id}>{p.name} — {p.price} so'm</li>)}\n"
            "    </ul>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== Marshrut darajasidagi majburiy sozlamalar =====\n"
            "// app/orders/page.js ichida ham yozish mumkin edi:\n"
            "// export const dynamic = 'force-dynamic'; // fetch sozlamasidan qat'iy nazar SSR\n"
            "// app/about/page.js kabi o'zgarmas sahifada:\n"
            "// export const dynamic = 'force-static';  // dinamik funksiya bo'lsa ham \"muzlatadi\"\n"
            "\n"
            "// ===== Solishtiruv jadvali (izoh sifatida) =====\n"
            "// Strategiya | HTML qachon tayyor        | Mos misol\n"
            "// -----------|----------------------------|---------------------------\n"
            "// SSG        | build vaqtida, bir marta   | blog postlari, hujjatlar\n"
            "// SSR        | har bir so'rovda            | \"Mening buyurtmalarim\"\n"
            "// ISR        | build'da + fonda vaqti-vaqti| mahsulotlar katalogi\n"
            "\n"
            "// ===== 8-darsda ko'radigan SSG + dinamik marshrut ko'rinishi (oldindan) =====\n"
            "// app/products/[id]/page.js\n"
            "export async function generateStaticParams() {\n"
            "  const products = await fetch('https://api.example.com/products').then((r) => r.json());\n"
            "  return products.map((p) => ({ id: String(p.id) })); // har biri uchun SSG sahifa\n"
            "}\n"
            "\n"
            "export default async function ProductPage({ params }) {\n"
            "  const { id } = await params;\n"
            "  const product = await fetch(`https://api.example.com/products/${id}`).then((r) => r.json());\n"
            "  return <h1>{product.name}</h1>;\n"
            "}\n"
            "\n"
            "// Diqqat: ProductPage'ning o'zi HECH QANDAY 'cache'/'revalidate' sozlamasi\n"
            "// yozmagan — chunki generateStaticParams allaqachon SSG'ni yoqadi, fetch esa\n"
            "// default holatda (keshlangan) ishlaydi. Bu ikkalasi doim birgalikda mos ishlaydi.\n"
        ),
        "code_content_ru": (
            "// ===== 1) SSG: app/blog/page.js — рендер во время сборки, остаётся статичным =====\n"
            "async function getStaticPosts() {\n"
            "  const res = await fetch('https://api.example.com/posts');\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function BlogPage() {\n"
            "  const posts = await getStaticPosts();\n"
            "  return (\n"
            "    <ul>\n"
            "      {posts.map((p) => <li key={p.id}>{p.title}</li>)}\n"
            "    </ul>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== 2) SSR: app/orders/page.js — рендер заново на сервере при каждом запросе =====\n"
            "import { cookies } from 'next/headers';\n"
            "\n"
            "async function getMyOrders(userId) {\n"
            "  const res = await fetch(`https://api.example.com/orders?user=${userId}`, {\n"
            "    cache: 'no-store', // или: динамическая функция (cookies/headers) сама включает SSR\n"
            "  });\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function OrdersPage() {\n"
            "  const cookieStore = await cookies(); // <- динамическая функция, принуждает к SSR\n"
            "  const userId = cookieStore.get('user_id')?.value;\n"
            "  const orders = await getMyOrders(userId);\n"
            "\n"
            "  return (\n"
            "    <ul>\n"
            "      {orders.map((o) => <li key={o.id}>{o.total} сум</li>)}\n"
            "    </ul>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== 3) ISR: app/products/page.js — статично, обновляется в фоне раз в 300с =====\n"
            "async function getProductCatalog() {\n"
            "  const res = await fetch('https://api.example.com/products', {\n"
            "    next: { revalidate: 300 },\n"
            "  });\n"
            "  return res.json();\n"
            "}\n"
            "\n"
            "export default async function ProductsPage() {\n"
            "  const products = await getProductCatalog();\n"
            "  return (\n"
            "    <ul>\n"
            "      {products.map((p) => <li key={p.id}>{p.name} — {p.price} сум</li>)}\n"
            "    </ul>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== Обязательные настройки на уровне маршрута =====\n"
            "// В app/orders/page.js можно было бы написать и так:\n"
            "// export const dynamic = 'force-dynamic'; // SSR независимо от настроек fetch\n"
            "// В неизменной странице вроде app/about/page.js:\n"
            "// export const dynamic = 'force-static';  // \"замораживает\", даже если есть динамическая функция\n"
            "\n"
            "// ===== Сравнительная таблица (в виде комментария) =====\n"
            "// Стратегия | Когда готов HTML             | Подходящий пример\n"
            "// ----------|-------------------------------|---------------------------\n"
            "// SSG       | во время сборки, один раз      | посты блога, документация\n"
            "// SSR       | при каждом запросе             | «Мои заказы»\n"
            "// ISR       | сборка + периодически в фоне   | каталог товаров\n"
            "\n"
            "// ===== Предпросмотр SSG + динамический маршрут (подробно в уроке 8) =====\n"
            "// app/products/[id]/page.js\n"
            "export async function generateStaticParams() {\n"
            "  const products = await fetch('https://api.example.com/products').then((r) => r.json());\n"
            "  return products.map((p) => ({ id: String(p.id) })); // страница SSG для каждого\n"
            "}\n"
            "\n"
            "export default async function ProductPage({ params }) {\n"
            "  const { id } = await params;\n"
            "  const product = await fetch(`https://api.example.com/products/${id}`).then((r) => r.json());\n"
            "  return <h1>{product.name}</h1>;\n"
            "}\n"
            "\n"
            "// Внимание: сам ProductPage НЕ пишет никакой настройки 'cache'/'revalidate' —\n"
            "// потому что generateStaticParams уже включает SSG, а fetch работает в\n"
            "// режиме по умолчанию (кешируется). Эти два механизма работают вместе.\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Har bir sahifa uchun strategiya tanlang",
            "task_title_ru": "Выберите стратегию для каждой страницы",
            "task_description": (
                "Kichik e-commerce ilovasi uchun 4 ta sahifani ko'rib chiqing: mahsulot "
                "katalogi, mahsulot tafsilotlari, 'Mening savatim', va 'Biz haqimizda'. Har biri "
                "uchun SSG/SSR/ISR'dan qaysi birini tanlaysiz va nima uchun — yozing."
            ),
            "task_description_ru": (
                "Рассмотрите 4 страницы небольшого e-commerce приложения: каталог товаров, "
                "детали товара, «Моя корзина» и «О нас». Для каждой напишите, какую стратегию "
                "(SSG/SSR/ISR) вы выберете и почему."
            ),
            "task_requirements": (
                "Har bir sahifa uchun aniq strategiya va kamida bitta jumlali asoslash "
                "yozilishi shart. Kamida bittasi SSR, kamida bittasi ISR yoki SSG bo'lishi kerak."
            ),
            "task_requirements_ru": (
                "Для каждой страницы должна быть указана конкретная стратегия и минимум одно "
                "предложение обоснования. Минимум одна должна быть SSR, минимум одна — ISR или "
                "SSG."
            ),
            "task_technologies": "Next.js, SSR, SSG, ISR",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: uchta strategiya bitta ilovada",
            "description": "Bitta ilovada SSG, SSR va ISR qanday aralash ishlatilishi mumkinligi.",
            "sample_type": "code",
            "code_files": [
                {"filename": "app/blog/page.js (SSG)", "language": "jsx",
                 "code": "export default async function BlogPage() {\n  const posts = await fetch('https://api.example.com/posts').then((r) => r.json());\n  return <ul>{posts.map((p) => <li key={p.id}>{p.title}</li>)}</ul>;\n}\n"},
                {"filename": "app/orders/page.js (SSR)", "language": "jsx",
                 "code": "export default async function OrdersPage() {\n  const orders = await fetch('https://api.example.com/orders', { cache: 'no-store' }).then((r) => r.json());\n  return <ul>{orders.map((o) => <li key={o.id}>{o.total}</li>)}</ul>;\n}\n"},
                {"filename": "app/products/page.js (ISR)", "language": "jsx",
                 "code": "export default async function ProductsPage() {\n  const products = await fetch('https://api.example.com/products', { next: { revalidate: 300 } }).then((r) => r.json());\n  return <ul>{products.map((p) => <li key={p.id}>{p.name}</li>)}</ul>;\n}\n"},
            ],
        },
        "exercises": [
            {
                "title": "Foydalanuvchiga xos kontent",
                "title_ru": "Контент, специфичный для пользователя",
                "description": "\"Mening buyurtmalarim\" sahifasi uchun qaysi strategiya eng mos keladi?",
                "description_ru": "Какая стратегия наиболее подходит для страницы «Мои заказы»?",
                "exercise_type": "multiple_choice",
                "options": ["SSG", "SSR", "ISR", "Hech biri, faqat CSR kerak"],
                "options_ru": ["SSG", "SSR", "ISR", "Ни одна, нужен только CSR"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Bu kontent har bir foydalanuvchi uchun boshqacha va doim yangi bo'lishi kerak.",
                "hint_ru": "Этот контент разный для каждого пользователя и должен быть всегда свежим.",
                "explanation": "Foydalanuvchiga xos, doim yangi kontent uchun SSR mos keladi.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "ISR nima uchun ishlatiladi",
                "title_ru": "Для чего используется ISR",
                "description": (
                    "Bo'shliqni to'ldiring: statik tezlikni saqlab, belgilangan vaqt oralig'ida "
                    "fonda qayta generatsiya qiladigan strategiya ___ deb ataladi (qisqartma)."
                ),
                "description_ru": (
                    "Заполните пропуск: стратегия, сохраняющая скорость статики и "
                    "регенерирующая контент в фоне через заданный интервал, называется ___ "
                    "(аббревиатура)."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "ISR",
                "hint": "Incremental Static Regeneration'ning qisqartmasi.",
                "hint_ru": "Аббревиатура от Incremental Static Regeneration.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "To'g'ri strategiyani moslashtiring",
                "title_ru": "Сопоставьте правильную стратегию",
                "description": "Har bir kontent turini mos strategiya bilan tartibda joylashtiring (SSG->SSR->ISR misolida).",
                "description_ru": "Расставьте типы контента в порядке SSG->SSR->ISR по соответствию.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Blog posti (kamdan kam o'zgaradi) - SSG",
                    "Foydalanuvchi savati (doim yangi) - SSR",
                    "Mahsulotlar katalogi (vaqti-vaqti bilan) - ISR",
                ],
                "drag_items_ru": [
                    "Пост блога (редко меняется) - SSG",
                    "Корзина пользователя (всегда свежая) - SSR",
                    "Каталог товаров (время от времени) - ISR",
                ],
                "correct_order": [
                    "Blog posti (kamdan kam o'zgaradi) - SSG",
                    "Foydalanuvchi savati (doim yangi) - SSR",
                    "Mahsulotlar katalogi (vaqti-vaqti bilan) - ISR",
                ],
                "hint": "O'zgarish chastotasi kamdan ko'pga qarab o'sib boradi.",
                "hint_ru": "Частота изменений возрастает от меньшей к большей.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 7,
        "title": "7-Route Handlers: ilova ichida backend endpoint yaratish",
        "title_ru": "7-Route Handlers: создание backend-эндпоинтов внутри приложения",
        "points_reward": 15,
        "text_content": (
            "<h3>Ushbu platformada backend qayerda joylashgan?</h3>"
            "<p>Ushbu platformaning arxitekturasi aniq: frontend (CRA) va backend (FastAPI, "
            "<code>backend/app/api/v1/endpoints/*.py</code>) — ikkita mustaqil xizmat, alohida "
            "portlarda ishlaydi, ular orasida HTTP orqali muloqot bo'ladi. Bu — juda keng "
            "tarqalgan va sog'lom arxitektura: frontend va backend mustaqil deploy qilinadi, "
            "mustaqil masshtablanadi, boshqa-boshqa jamoalar tomonidan qo'llab-quvvatlanishi "
            "mumkin.</p>"
            "<p>Next.js esa boshqacha imkoniyat ham beradi: <strong>Route Handler</strong> "
            "orqali backend endpoint'ni xuddi shu Next.js ilovasining o'zi ichida yozish mumkin "
            "— alohida server, alohida deploy jarayoni kerak emas.</p>"
            "<h3>Route Handler qanday yoziladi</h3>"
            "<p><code>app/</code> ichidagi istalgan papkaga <code>route.js</code> fayli "
            "qo'shilsa (masalan, <code>app/api/courses/route.js</code>), u shu marshrut uchun "
            "HTTP metodlariga mos nomlangan funksiyalarni eksport qiladi: "
            "<code>GET</code>, <code>POST</code>, <code>PUT</code>, <code>DELETE</code> va "
            "hokazo. Muhim: bitta papkada <code>page.js</code> HAM, <code>route.js</code> HAM "
            "bir vaqtda bo'la olmaydi — chunki ikkalasi ham xuddi shu URL'ga javob berishga "
            "urinadi.</p>"
            "<h3>So'rov va javob bilan ishlash</h3>"
            "<p>Har bir handler funksiyasi <code>NextRequest</code> obyektini qabul qiladi — "
            "undan so'rov tanasini (<code>await request.json()</code>), query parametrlarni "
            "(<code>request.nextUrl.searchParams.get('q')</code>) yoki cookie/header'larni "
            "o'qish mumkin. Javob esa <code>NextResponse.json(data, { status: 201 })</code> "
            "kabi qaytariladi — bu, mohiyatan, FastAPI'dagi <code>@router.get(...)</code> "
            "endpoint'iga to'g'ridan-to'g'ri o'xshash tushuncha, faqat Python o'rniga "
            "JavaScript'da.</p>"
            "<h3>Qachon Route Handler, qachon alohida backend</h3>"
            "<p>Bu — \"qaysi biri yaxshiroq\" degan savol emas, balki \"qaysi vazifaga qaysi "
            "vosita mos\" degan savol. Route Handler mos keladi: kichik webhook qabul qilish "
            "(masalan, to'lov tizimidan xabarnoma), forma yuborish, yoki BFF (backend-for-"
            "frontend) qatlami — ya'ni frontend'ga qulay formatda ma'lumot berish uchun asosiy "
            "backend'ni \"qayta o'rash\". Alohida backend (bu platformadagi FastAPI kabi) mos "
            "keladi: murakkab biznes mantiq, ko'p jadvalli ma'lumotlar bazasi operatsiyalari, "
            "boshqa xizmatlar (Telegram bot, admin panel) bilan bo'lishiladigan umumiy API, yoki "
            "frontend'dan mustaqil ravishda masshtablanishi kerak bo'lgan yuklama.</p>"
            "<h3>Diagram: ikki arxitektura yonma-yon</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart LR\n"
            "  subgraph BU[\"Bu platforma\"]\n"
            "    F1[\"CRA frontend\"] -->|\"HTTP so'rov\"| B1[\"FastAPI backend\n"
            "(alohida xizmat)\"]\n"
            "  end\n"
            "  subgraph NJ[\"Next.js Route Handler\"]\n"
            "    F2[\"Client Component\"] -->|\"fetch('/api/courses')\"| R2[\"route.js\n"
            "(shu ilova ichida)\"]\n"
            "    R2 -->|\"ixtiyoriy\"| B2[\"tashqi haqiqiy backend\"]\n"
            "  end\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: bu platformada frontend va backend har doim ikkita "
            "alohida xizmat, Next.js'da esa Route Handler ilovaning o'zi ichida yashaydi va "
            "xohlasa tashqi backend'ga ham murojaat qilishi mumkin (masalan, BFF sifatida).</p>"
            "<h3>Xavfsizlik: maxfiy kalitlar faqat serverda qoladi</h3>"
            "<p>Route Handler kodi — Server Component kabi — hech qachon brauzerga jo'natilmaydi. "
            "Bu degani, u ichida <code>process.env.STRIPE_SECRET_KEY</code> kabi maxfiy "
            "o'zgaruvchilarni xavfsiz ishlatish mumkin, chunki bu qiymat mijoz bandle'iga "
            "umuman kirmaydi. Solishtirish uchun: 10-darsda ko'radigan "
            "<code>NEXT_PUBLIC_</code> prefiksli o'zgaruvchilar esa ataylab brauzerga "
            "jo'natiladi — ular hech qachon maxfiy ma'lumot uchun ishlatilmasligi kerak. Bu "
            "farq — CRA'dagi <code>REACT_APP_</code> prefiksi bilan bir xil mantiqqa ega, "
            "faqat nomi boshqacha.</p>"
            "<h3>Dinamik segmentlar bilan Route Handler</h3>"
            "<p>Route Handler'lar ham oddiy sahifalar kabi dinamik segmentlarni qo'llab-"
            "quvvatlaydi: <code>app/api/courses/[id]/route.js</code> fayli "
            "<code>GET(request, { params })</code> imzosi orqali <code>id</code> qiymatini "
            "qabul qiladi. Bu — bitta resursni ID bo'yicha olish yoki yangilash (REST'dagi "
            "<code>/courses/{id}</code> naqshi) uchun aynan kerak bo'ladigan narsa, va u "
            "8-darsda ko'radigan dinamik sahifa marshrutlari bilan bir xil qavs sintaksisini "
            "ishlatadi. Shunday qilib, bitta <code>[id]</code> papkasi ostida ham "
            "<code>page.js</code> (foydalanuvchi ko'radigan sahifa), ham qo'shni "
            "<code>api/courses/[id]/route.js</code> (dastur uchun JSON endpoint) mavjud "
            "bo'lishi mumkin — ular alohida papkalarda joylashgani uchun konflikt yo'q.</p>"
        ),
        "text_content_ru": (
            "<h3>Где расположен backend в этой платформе?</h3>"
            "<p>Архитектура этой платформы чёткая: фронтенд (CRA) и backend (FastAPI, "
            "<code>backend/app/api/v1/endpoints/*.py</code>) — два независимых сервиса, "
            "работающих на разных портах, общающихся через HTTP. Это очень распространённая и "
            "здоровая архитектура: фронтенд и backend деплоятся независимо, независимо "
            "масштабируются, могут поддерживаться разными командами.</p>"
            "<p>Next.js же предлагает и другую возможность: <strong>Route Handler</strong> "
            "позволяет написать backend-эндпоинт прямо внутри самого Next.js-приложения — без "
            "отдельного сервера, без отдельного процесса деплоя.</p>"
            "<h3>Как пишется Route Handler</h3>"
            "<p>Если в любую папку внутри <code>app/</code> добавить файл <code>route.js</code> "
            "(например, <code>app/api/courses/route.js</code>), он экспортирует функции, "
            "названные по HTTP-методам для этого маршрута: <code>GET</code>, <code>POST</code>, "
            "<code>PUT</code>, <code>DELETE</code> и так далее. Важно: в одной папке НЕ МОГУТ "
            "одновременно быть и <code>page.js</code>, И <code>route.js</code> — оба пытаются "
            "отвечать на один и тот же URL.</p>"
            "<h3>Работа с запросом и ответом</h3>"
            "<p>Каждая функция-обработчик принимает объект <code>NextRequest</code> — из него "
            "можно прочитать тело запроса (<code>await request.json()</code>), query-параметры "
            "(<code>request.nextUrl.searchParams.get('q')</code>) или cookie/заголовки. Ответ "
            "возвращается как <code>NextResponse.json(data, { status: 201 })</code> — это, по "
            "сути, понятие, напрямую аналогичное эндпоинту <code>@router.get(...)</code> в "
            "FastAPI, только на JavaScript вместо Python.</p>"
            "<h3>Когда Route Handler, а когда отдельный backend</h3>"
            "<p>Это не вопрос «что лучше», а вопрос «какой инструмент для какой задачи». Route "
            "Handler подходит: приём небольшого webhook (например, уведомление от платёжной "
            "системы), отправка формы, или слой BFF (backend-for-frontend) — то есть "
            "«переупаковка» основного backend'а в удобный для фронтенда формат. Отдельный "
            "backend (как FastAPI в этой платформе) подходит: сложная бизнес-логика, операции "
            "с базой данных на много таблиц, общий API, которым пользуются другие сервисы "
            "(Telegram-бот, админ-панель), или нагрузка, которую нужно масштабировать "
            "независимо от фронтенда.</p>"
            "<h3>Диаграмма: две архитектуры рядом</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart LR\n"
            "  subgraph BU[\"Эта платформа\"]\n"
            "    F1[\"CRA фронтенд\"] -->|\"HTTP-запрос\"| B1[\"FastAPI backend\n"
            "(отдельный сервис)\"]\n"
            "  end\n"
            "  subgraph NJ[\"Next.js Route Handler\"]\n"
            "    F2[\"Client Component\"] -->|\"fetch('/api/courses')\"| R2[\"route.js\n"
            "(внутри этого же приложения)\"]\n"
            "    R2 -->|\"опционально\"| B2[\"внешний реальный backend\"]\n"
            "  end\n"
            "</pre>"
            "<p>Диаграмма показывает: в этой платформе фронтенд и backend — всегда два "
            "отдельных сервиса, а в Next.js Route Handler живёт внутри самого приложения и при "
            "желании тоже может обращаться к внешнему backend'у (например, в роли BFF).</p>"
            "<h3>Безопасность: секретные ключи остаются только на сервере</h3>"
            "<p>Код Route Handler — как и Server Component — никогда не отправляется в браузер. "
            "Это значит, что внутри него можно безопасно использовать секретные переменные "
            "вроде <code>process.env.STRIPE_SECRET_KEY</code>, потому что это значение вообще "
            "не попадает в клиентский бандл. Для сравнения: переменные с префиксом "
            "<code>NEXT_PUBLIC_</code>, которые мы увидим в уроке 10, специально отправляются в "
            "браузер — их никогда нельзя использовать для секретных данных. Эта разница "
            "работает по той же логике, что и префикс <code>REACT_APP_</code> в CRA, просто "
            "называется иначе.</p>"
            "<h3>Route Handler с динамическими сегментами</h3>"
            "<p>Route Handler'ы тоже поддерживают динамические сегменты, как и обычные "
            "страницы: файл <code>app/api/courses/[id]/route.js</code> получает значение "
            "<code>id</code> через сигнатуру <code>GET(request, { params })</code>. Это именно "
            "то, что нужно для получения или обновления одного ресурса по ID (паттерн REST "
            "<code>/courses/{id}</code>), и использует тот же синтаксис скобок, что и "
            "динамические маршруты страниц, которые мы увидим в уроке 8.</p>"
            "<p>Таким образом, под одной папкой <code>[id]</code> могут существовать и "
            "<code>page.js</code> (страница, видимая пользователю), и соседний "
            "<code>api/courses/[id]/route.js</code> (JSON-эндпоинт для приложения) — конфликта "
            "нет, поскольку они находятся в разных папках.</p>"
        ),
        "code_content": (
            "// ===== app/api/courses/route.js — ro'yxat (GET) va yaratish (POST) =====\n"
            "import { NextResponse } from 'next/server';\n"
            "\n"
            "let courses = [\n"
            "  { id: 1, title: 'Next.js asoslari' },\n"
            "  { id: 2, title: 'React Server Components' },\n"
            "];\n"
            "\n"
            "export async function GET(request) {\n"
            "  const query = request.nextUrl.searchParams.get('q');\n"
            "  const filtered = query\n"
            "    ? courses.filter((c) => c.title.toLowerCase().includes(query.toLowerCase()))\n"
            "    : courses;\n"
            "  return NextResponse.json(filtered);\n"
            "}\n"
            "\n"
            "export async function POST(request) {\n"
            "  const body = await request.json();\n"
            "  if (!body.title || typeof body.title !== 'string') {\n"
            "    return NextResponse.json({ error: 'title majburiy va string bo\\'lishi kerak' }, { status: 400 });\n"
            "  }\n"
            "  const newCourse = { id: courses.length + 1, title: body.title };\n"
            "  courses.push(newCourse);\n"
            "  return NextResponse.json(newCourse, { status: 201 });\n"
            "}\n"
            "\n"
            "// ===== app/api/courses/[id]/route.js — bitta resurs: GET/PUT/DELETE =====\n"
            "import { NextResponse } from 'next/server';\n"
            "\n"
            "export async function GET(request, { params }) {\n"
            "  const { id } = await params;\n"
            "  const course = courses.find((c) => c.id === Number(id));\n"
            "  if (!course) {\n"
            "    return NextResponse.json({ error: 'Kurs topilmadi' }, { status: 404 });\n"
            "  }\n"
            "  return NextResponse.json(course);\n"
            "}\n"
            "\n"
            "export async function PUT(request, { params }) {\n"
            "  const { id } = await params;\n"
            "  const body = await request.json();\n"
            "  const index = courses.findIndex((c) => c.id === Number(id));\n"
            "  if (index === -1) {\n"
            "    return NextResponse.json({ error: 'Kurs topilmadi' }, { status: 404 });\n"
            "  }\n"
            "  if (!body.title) {\n"
            "    return NextResponse.json({ error: 'title majburiy' }, { status: 400 });\n"
            "  }\n"
            "  courses[index] = { ...courses[index], title: body.title };\n"
            "  return NextResponse.json(courses[index]);\n"
            "}\n"
            "\n"
            "export async function DELETE(request, { params }) {\n"
            "  const { id } = await params;\n"
            "  const exists = courses.some((c) => c.id === Number(id));\n"
            "  if (!exists) {\n"
            "    return NextResponse.json({ error: 'Kurs topilmadi' }, { status: 404 });\n"
            "  }\n"
            "  courses = courses.filter((c) => c.id !== Number(id));\n"
            "  return new NextResponse(null, { status: 204 }); // muvaffaqiyatli, tana yo'q\n"
            "}\n"
            "\n"
            "// ===== app/api/courses/route.js — GET'ga sahifalash (pagination) qo'shish =====\n"
            "export async function GET_withPagination(request) {\n"
            "  const page = Number(request.nextUrl.searchParams.get('page') || '1');\n"
            "  const limit = Number(request.nextUrl.searchParams.get('limit') || '10');\n"
            "  const start = (page - 1) * limit;\n"
            "  const pageItems = courses.slice(start, start + limit);\n"
            "  return NextResponse.json({\n"
            "    items: pageItems,\n"
            "    total: courses.length,\n"
            "    page,\n"
            "    limit,\n"
            "  });\n"
            "}\n"
            "// Solishtirish: bu platformaning FastAPI backend'ida xuddi shu mantiq\n"
            "// backend/app/api/v1/endpoints/*.py ichida Pydantic sxemasi + SQLAlchemy\n"
            "// so'rovi bilan yoziladi — Route Handler'da esa hammasi bitta JS faylida.\n"
            "\n"
            "// ===== So'rov tanasidagi noto'g'ri JSON'ni qayta ishlash =====\n"
            "export async function POST_safe(request) {\n"
            "  let body;\n"
            "  try {\n"
            "    body = await request.json(); // yaroqsiz JSON bo'lsa xato tashlaydi\n"
            "  } catch {\n"
            "    return NextResponse.json({ error: 'So\\'rov tanasida noto\\'g\\'ri JSON' }, { status: 400 });\n"
            "  }\n"
            "  // ... qolgan validatsiya yuqoridagi POST() kabi ...\n"
            "}\n"
        ),
        "code_content_ru": (
            "// ===== app/api/courses/route.js — список (GET) и создание (POST) =====\n"
            "import { NextResponse } from 'next/server';\n"
            "\n"
            "let courses = [\n"
            "  { id: 1, title: 'Основы Next.js' },\n"
            "  { id: 2, title: 'React Server Components' },\n"
            "];\n"
            "\n"
            "export async function GET(request) {\n"
            "  const query = request.nextUrl.searchParams.get('q');\n"
            "  const filtered = query\n"
            "    ? courses.filter((c) => c.title.toLowerCase().includes(query.toLowerCase()))\n"
            "    : courses;\n"
            "  return NextResponse.json(filtered);\n"
            "}\n"
            "\n"
            "export async function POST(request) {\n"
            "  const body = await request.json();\n"
            "  if (!body.title || typeof body.title !== 'string') {\n"
            "    return NextResponse.json({ error: 'title обязателен и должен быть строкой' }, { status: 400 });\n"
            "  }\n"
            "  const newCourse = { id: courses.length + 1, title: body.title };\n"
            "  courses.push(newCourse);\n"
            "  return NextResponse.json(newCourse, { status: 201 });\n"
            "}\n"
            "\n"
            "// ===== app/api/courses/[id]/route.js — один ресурс: GET/PUT/DELETE =====\n"
            "import { NextResponse } from 'next/server';\n"
            "\n"
            "export async function GET(request, { params }) {\n"
            "  const { id } = await params;\n"
            "  const course = courses.find((c) => c.id === Number(id));\n"
            "  if (!course) {\n"
            "    return NextResponse.json({ error: 'Курс не найден' }, { status: 404 });\n"
            "  }\n"
            "  return NextResponse.json(course);\n"
            "}\n"
            "\n"
            "export async function PUT(request, { params }) {\n"
            "  const { id } = await params;\n"
            "  const body = await request.json();\n"
            "  const index = courses.findIndex((c) => c.id === Number(id));\n"
            "  if (index === -1) {\n"
            "    return NextResponse.json({ error: 'Курс не найден' }, { status: 404 });\n"
            "  }\n"
            "  if (!body.title) {\n"
            "    return NextResponse.json({ error: 'title обязателен' }, { status: 400 });\n"
            "  }\n"
            "  courses[index] = { ...courses[index], title: body.title };\n"
            "  return NextResponse.json(courses[index]);\n"
            "}\n"
            "\n"
            "export async function DELETE(request, { params }) {\n"
            "  const { id } = await params;\n"
            "  const exists = courses.some((c) => c.id === Number(id));\n"
            "  if (!exists) {\n"
            "    return NextResponse.json({ error: 'Курс не найден' }, { status: 404 });\n"
            "  }\n"
            "  courses = courses.filter((c) => c.id !== Number(id));\n"
            "  return new NextResponse(null, { status: 204 }); // успешно, без тела\n"
            "}\n"
            "\n"
            "// ===== app/api/courses/route.js — добавление пагинации к GET =====\n"
            "export async function GET_withPagination(request) {\n"
            "  const page = Number(request.nextUrl.searchParams.get('page') || '1');\n"
            "  const limit = Number(request.nextUrl.searchParams.get('limit') || '10');\n"
            "  const start = (page - 1) * limit;\n"
            "  const pageItems = courses.slice(start, start + limit);\n"
            "  return NextResponse.json({\n"
            "    items: pageItems,\n"
            "    total: courses.length,\n"
            "    page,\n"
            "    limit,\n"
            "  });\n"
            "}\n"
            "// Для сравнения: та же логика в FastAPI backend'е этой платформы пишется\n"
            "// внутри backend/app/api/v1/endpoints/*.py через Pydantic-схему и запрос\n"
            "// SQLAlchemy — а в Route Handler всё умещается в одном JS-файле.\n"
            "\n"
            "// ===== Обработка некорректного JSON в теле запроса =====\n"
            "export async function POST_safe(request) {\n"
            "  let body;\n"
            "  try {\n"
            "    body = await request.json(); // выбросит ошибку на невалидный JSON\n"
            "  } catch {\n"
            "    return NextResponse.json({ error: 'Некорректный JSON в теле запроса' }, { status: 400 });\n"
            "  }\n"
            "  // ... остальная валидация как в POST() выше ...\n"
            "}\n"
        ),
        "code_language": "javascript",
        "video_url": None,
        "task": {
            "task_title": "Qidiruv Route Handler yarating",
            "task_title_ru": "Создайте Route Handler для поиска",
            "task_description": (
                "app/api/products/route.js faylida GET (query parametr bo'yicha filtrlash) va "
                "POST (yangi mahsulot qo'shish, validatsiya bilan) metodlarini yozing. Keyin "
                "shu Route Handler'ni bu platformaning FastAPI backend'i bilan solishtirib, "
                "qaysi holatda qaysi biri afzalligini tushuntiring."
            ),
            "task_description_ru": (
                "Напишите в файле app/api/products/route.js методы GET (фильтрация по "
                "query-параметру) и POST (добавление нового товара с валидацией). Затем "
                "сравните этот Route Handler с FastAPI backend'ом этой платформы и объясните, "
                "в каком случае что предпочтительнее."
            ),
            "task_requirements": (
                "GET so'rov parametrini o'qishi, POST esa majburiy maydonni tekshirib, xato "
                "bo'lsa 400 status bilan javob qaytarishi shart."
            ),
            "task_requirements_ru": (
                "GET должен читать параметр запроса, POST — проверять обязательное поле и при "
                "ошибке возвращать статус 400."
            ),
            "task_technologies": "Next.js, Route Handlers, NextResponse",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: qidiruv Route Handler",
            "description": "GET (filtrlash) va POST (validatsiya bilan qo'shish) metodlari.",
            "sample_type": "code",
            "code_files": [
                {"filename": "app/api/products/route.js", "language": "javascript",
                 "code": "import { NextResponse } from 'next/server';\n\nlet products = [{ id: 1, name: 'Klaviatura' }, { id: 2, name: 'Sichqoncha' }];\n\nexport async function GET(request) {\n  const q = request.nextUrl.searchParams.get('q');\n  const result = q ? products.filter((p) => p.name.toLowerCase().includes(q.toLowerCase())) : products;\n  return NextResponse.json(result);\n}\n\nexport async function POST(request) {\n  const body = await request.json();\n  if (!body.name) return NextResponse.json({ error: 'name majburiy' }, { status: 400 });\n  const item = { id: products.length + 1, name: body.name };\n  products.push(item);\n  return NextResponse.json(item, { status: 201 });\n}\n"},
            ],
        },
        "exercises": [
            {
                "title": "Route Handler va page.js bitta papkada",
                "title_ru": "Route Handler и page.js в одной папке",
                "description": "Bitta papkada page.js va route.js bir vaqtda bo'lishi mumkinmi?",
                "description_ru": "Могут ли page.js и route.js существовать одновременно в одной папке?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Ha, ikkalasi ham muammosiz ishlaydi",
                    "Yo'q, ikkalasi ham xuddi shu URL'ga javob berishga urinadi",
                    "Ha, lekin faqat GET metodida",
                    "Yo'q, chunki route.js har doim /api ichida bo'lishi shart",
                ],
                "options_ru": [
                    "Да, оба будут работать без проблем",
                    "Нет, оба пытаются отвечать на один и тот же URL",
                    "Да, но только для метода GET",
                    "Нет, потому что route.js обязательно должен быть внутри /api",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Ikkalasi ham bir xil marshrutning \"asosiy\" javobgar fayli bo'lishga da'vo qiladi.",
                "hint_ru": "Оба претендуют на роль «основного» файла-обработчика одного маршрута.",
                "explanation": "page.js va route.js bir xil segmentda birga bo'la olmaydi — konflikt yuzaga keladi.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Route Handler faylining nomi",
                "title_ru": "Имя файла Route Handler",
                "description": (
                    "Bo'shliqni to'ldiring: HTTP metodlarga mos funksiyalarni eksport qiladigan "
                    "maxsus fayl nomi ___.js."
                ),
                "description_ru": (
                    "Заполните пропуск: специальное имя файла, экспортирующего функции, "
                    "названные по HTTP-методам — ___.js."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "route.js",
                "hint": "page.js emas — bu backend endpoint uchun fayl.",
                "hint_ru": "Не page.js — это файл для backend-эндпоинта.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Route Handler yoki alohida backend?",
                "title_ru": "Route Handler или отдельный backend?",
                "description": (
                    "Quyidagi holatlar uchun Route Handler qanchalik mos ekanligini eng mosdan "
                    "eng kam mosgacha tartiblang: kichik webhook qabul qilish, murakkab "
                    "ko'p-jadvalli tranzaksiya, forma yuborish."
                ),
                "description_ru": (
                    "Расставьте следующие случаи от наиболее подходящих для Route Handler до "
                    "наименее: приём небольшого webhook, сложная многотабличная транзакция, "
                    "отправка формы."
                ),
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Kichik webhook qabul qilish",
                    "Forma yuborish",
                    "Murakkab ko'p-jadvalli tranzaksiya",
                ],
                "drag_items_ru": [
                    "Приём небольшого webhook",
                    "Отправка формы",
                    "Сложная многотабличная транзакция",
                ],
                "correct_order": [
                    "Kichik webhook qabul qilish",
                    "Forma yuborish",
                    "Murakkab ko'p-jadvalli tranzaksiya",
                ],
                "hint": "Murakkablik oshgani sayin, alohida backend afzalroq bo'lib boradi.",
                "hint_ru": "С ростом сложности отдельный backend становится предпочтительнее.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 8,
        "title": "8-Dinamik marshrutlar va generateStaticParams",
        "title_ru": "8-Динамические маршруты и generateStaticParams",
        "points_reward": 15,
        "text_content": (
            "<h3>CRA'dagi :id'dan Next.js'dagi [id]'ga</h3>"
            "<p>CRA'da (shu platformaning frontend'ida) dinamik marshrut "
            "<code>react-router-dom</code>'da <code>&lt;Route path=\"/courses/:id\" /&gt;</code> "
            "kabi yoziladi, va komponent ichida <code>useParams()</code> hook orqali "
            "<code>id</code> qiymati o'qiladi. Next.js App Router'da bunga mos keladigan "
            "narsa — papka nomini kvadrat qavs ichiga olish: <code>app/courses/[id]/page.js</code>. "
            "Qiymat esa hook orqali emas, balki komponentga <code>params</code> propi sifatida "
            "keladi (va u — Promise, shuning uchun <code>await params</code> qilish kerak).</p>"
            "<h3>Uch xil dinamik segment</h3>"
            "<ul>"
            "<li><code>[id]</code> — bitta segmentni ushlaydi: <code>/courses/42</code> mos "
            "keladi, <code>/courses/42/reviews</code> mos kelmaydi.</li>"
            "<li><code>[...slug]</code> (catch-all) — bir nechta segmentni birdaniga ushlaydi: "
            "<code>/docs/[...slug]</code> papkasi <code>/docs/a</code>, <code>/docs/a/b</code>, "
            "<code>/docs/a/b/c</code> — barchasiga mos keladi, <code>slug</code> massiv "
            "sifatida keladi (<code>['a','b','c']</code>).</li>"
            "<li><code>[[...slug]]</code> (ixtiyoriy catch-all) — yuqoridagi kabi, lekin "
            "<code>/docs</code>ning o'ziga ham (segmentsiz) mos keladi.</li>"
            "</ul>"
            "<h3>generateStaticParams: SSG'ni dinamik marshrutlarga qo'llash</h3>"
            "<p>6-darsda ko'rganimizdek, SSG HTML'ni build vaqtida tayyorlaydi. Lekin "
            "<code>[id]</code> uchun Next.js qanday qilib \"barcha mumkin bo'lgan id'lar\"ni "
            "biladi? Javob — <code>generateStaticParams</code> nomli maxsus async funksiya: u "
            "oldindan render qilinishi kerak bo'lgan barcha parametr qiymatlari ro'yxatini "
            "qaytaradi (masalan, ma'lumotlar bazasidagi barcha kurs ID'larini so'rab). Build "
            "jarayonida Next.js shu ro'yxatdagi HAR BIR qiymat uchun alohida statik HTML sahifa "
            "tayyorlaydi — xuddi ular alohida-alohida qo'lda yozilgandek.</p>"
            "<h3>Ro'yxatda yo'q id kelsa nima bo'ladi?</h3>"
            "<p>Bu <code>dynamicParams</code> sozlamasiga bog'liq (default — <code>true</code>): "
            "agar foydalanuvchi <code>generateStaticParams</code> ro'yxatida bo'lmagan id "
            "so'rasa, Next.js o'sha sahifani so'rov paytida (SSR kabi) render qilib, keyin "
            "keshga qo'shadi. Agar <code>dynamicParams = false</code> qilib qo'yilsa, ro'yxatda "
            "yo'q id uchun avtomatik <code>404 Not Found</code> qaytariladi — bu, masalan, "
            "faqat cheklangan, oldindan ma'lum sahifalar to'plami kerak bo'lgan hollarda "
            "foydali.</p>"
            "<h3>Diagram: id ro'yxati va build vaqtidagi sahifalar</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  GSP[\"generateStaticParams()\n"
            "qaytaradi: [{id:'1'},{id:'2'},{id:'3'}]\"] --> B1[\"/courses/1 (statik HTML)\"]\n"
            "  GSP --> B2[\"/courses/2 (statik HTML)\"]\n"
            "  GSP --> B3[\"/courses/3 (statik HTML)\"]\n"
            "  U[\"Foydalanuvchi /courses/99'ni so'raydi\n"
            "(ro'yxatda yo'q)\"] --> D{\"dynamicParams?\"}\n"
            "  D -->|\"true (default)\"| SSR[\"So'rov vaqtida render,\n"
            "keyin keshga qo'shiladi\"]\n"
            "  D -->|\"false\"| NF[\"404 Not Found\"]\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: <code>generateStaticParams</code>dagi id'lar build "
            "vaqtida statik sahifaga aylanadi, ro'yxatda yo'q id esa <code>dynamicParams</code> "
            "sozlamasiga qarab yo SSR qilinadi, yo 404 qaytaradi.</p>"
            "<h3>Ichma-ich dinamik segmentlar</h3>"
            "<p>Dinamik segmentlarni ichma-ich joylashtirish ham mumkin: masalan, "
            "<code>app/shop/[category]/[product]/page.js</code> — bunda "
            "<code>/shop/electronics/laptop-15</code> kabi manzilda <code>params</code> "
            "ikkalasini ham beradi: <code>{ category: 'electronics', product: 'laptop-15' }</code>. "
            "Bunday holatda <code>generateStaticParams</code> odatda ota segment (masalan, "
            "<code>[category]</code>) uchun yozilib, uning ichida mos mahsulotlar bo'yicha yana "
            "bir daraja qaytariladi, yoki har ikkala segment uchun to'liq kombinatsiyalar "
            "ro'yxati tuziladi.</p>"
            "<h3>notFound(): dasturiy ravishda 404'ga o'tish</h3>"
            "<p>Ba'zan id texnik jihatdan to'g'ri formatda bo'ladi, lekin unga mos yozuv "
            "ma'lumotlar bazasida topilmaydi (masalan, o'chirilgan kurs). Bunday holatda "
            "sahifa komponenti ichida <code>next/navigation</code>'dan import qilingan "
            "<code>notFound()</code> funksiyasini chaqirish mumkin — bu darhol shu marshrutning "
            "<code>not-found.js</code> faylini (2-darsda ko'rgan edik) ko'rsatadi va 404 status "
            "kodini qaytaradi, xuddi Next.js o'zi mos marshrut topmagandagidek.</p>"
            "<p>Bu ikkala vosita — <code>generateStaticParams</code> va <code>notFound()</code> "
            "— birgalikda ishlaydi: birinchisi \"nima oldindan tayyorlansin\" degan savolga, "
            "ikkinchisi esa \"ma'lumot topilmasa nima bo'lsin\" degan savolga javob beradi.</p>"
        ),
        "text_content_ru": (
            "<h3>От :id в CRA к [id] в Next.js</h3>"
            "<p>В CRA (фронтенде этой платформы) динамический маршрут пишется в "
            "<code>react-router-dom</code> как <code>&lt;Route path=\"/courses/:id\" /&gt;</code>, "
            "а значение <code>id</code> читается внутри компонента через хук "
            "<code>useParams()</code>. В App Router Next.js аналог этого — взять имя папки в "
            "квадратные скобки: <code>app/courses/[id]/page.js</code>. Значение же приходит не "
            "через хук, а как проп <code>params</code> компонента (и это — Promise, поэтому "
            "нужно делать <code>await params</code>).</p>"
            "<h3>Три вида динамических сегментов</h3>"
            "<ul>"
            "<li><code>[id]</code> — захватывает один сегмент: <code>/courses/42</code> "
            "подходит, <code>/courses/42/reviews</code> — нет.</li>"
            "<li><code>[...slug]</code> (catch-all) — захватывает сразу несколько сегментов: "
            "папка <code>/docs/[...slug]</code> подходит для <code>/docs/a</code>, "
            "<code>/docs/a/b</code>, <code>/docs/a/b/c</code> — всех сразу, <code>slug</code> "
            "приходит массивом (<code>['a','b','c']</code>).</li>"
            "<li><code>[[...slug]]</code> (опциональный catch-all) — как выше, но подходит и "
            "для самого <code>/docs</code> (без сегмента вообще).</li>"
            "</ul>"
            "<h3>generateStaticParams: применение SSG к динамическим маршрутам</h3>"
            "<p>Как мы видели в уроке 6, SSG готовит HTML во время сборки. Но откуда Next.js "
            "знает «все возможные id» для <code>[id]</code>? Ответ — специальная async-функция "
            "<code>generateStaticParams</code>: она возвращает список всех значений "
            "параметров, которые нужно предварительно отрендерить (например, запросив все ID "
            "курсов из базы данных). Во время сборки Next.js готовит отдельную статическую "
            "HTML-страницу для КАЖДОГО значения из этого списка — как будто они были написаны "
            "вручную по отдельности.</p>"
            "<h3>Что происходит, если приходит id не из списка?</h3>"
            "<p>Это зависит от настройки <code>dynamicParams</code> (по умолчанию — "
            "<code>true</code>): если пользователь запрашивает id, которого нет в списке "
            "<code>generateStaticParams</code>, Next.js рендерит эту страницу во время запроса "
            "(как SSR), а затем добавляет в кеш. Если установить "
            "<code>dynamicParams = false</code>, для id не из списка автоматически "
            "возвращается <code>404 Not Found</code> — это полезно, например, когда нужен "
            "только ограниченный, заранее известный набор страниц.</p>"
            "<h3>Диаграмма: список id и страницы времени сборки</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  GSP[\"generateStaticParams()\n"
            "возвращает: [{id:'1'},{id:'2'},{id:'3'}]\"] --> B1[\"/courses/1 (статичный HTML)\"]\n"
            "  GSP --> B2[\"/courses/2 (статичный HTML)\"]\n"
            "  GSP --> B3[\"/courses/3 (статичный HTML)\"]\n"
            "  U[\"Пользователь запрашивает /courses/99\n"
            "(нет в списке)\"] --> D{\"dynamicParams?\"}\n"
            "  D -->|\"true (по умолчанию)\"| SSR[\"Рендер во время запроса,\n"
            "затем добавляется в кеш\"]\n"
            "  D -->|\"false\"| NF[\"404 Not Found\"]\n"
            "</pre>"
            "<p>Диаграмма показывает: id из <code>generateStaticParams</code> становятся "
            "статичными страницами во время сборки, а id не из списка либо рендерятся как SSR, "
            "либо возвращают 404 — в зависимости от <code>dynamicParams</code>.</p>"
            "<h3>Вложенные динамические сегменты</h3>"
            "<p>Динамические сегменты можно вкладывать друг в друга: например, "
            "<code>app/shop/[category]/[product]/page.js</code> — тогда для адреса вроде "
            "<code>/shop/electronics/laptop-15</code> проп <code>params</code> отдаёт оба "
            "значения: <code>{ category: 'electronics', product: 'laptop-15' }</code>. В таком "
            "случае <code>generateStaticParams</code> обычно пишется для родительского сегмента "
            "(например, <code>[category]</code>), внутри которого возвращается ещё один уровень "
            "по соответствующим товарам, либо составляется полный список комбинаций обоих "
            "сегментов.</p>"
            "<h3>notFound(): программный переход на 404</h3>"
            "<p>Иногда id технически имеет правильный формат, но соответствующая запись не "
            "найдена в базе данных (например, удалённый курс). В этом случае внутри компонента "
            "страницы можно вызвать функцию <code>notFound()</code>, импортированную из "
            "<code>next/navigation</code>, — она немедленно покажет файл "
            "<code>not-found.js</code> этого маршрута (который мы видели в уроке 2) и вернёт "
            "код статуса 404, точно так же, как если бы сам Next.js не нашёл подходящий "
            "маршрут.</p>"
            "<p>Эти два инструмента — <code>generateStaticParams</code> и <code>notFound()</code> "
            "— работают вместе: первый отвечает на вопрос «что подготовить заранее», а второй "
            "— «что делать, если данные не найдены».</p>"
        ),
        "code_content": (
            "// ===== app/courses/[id]/page.js — SSG + generateStaticParams =====\n"
            "import { notFound } from 'next/navigation';\n"
            "\n"
            "export async function generateStaticParams() {\n"
            "  const courses = await fetch('https://api.example.com/courses').then((r) => r.json());\n"
            "  return courses.map((c) => ({ id: String(c.id) }));\n"
            "}\n"
            "\n"
            "// Ro'yxatda yo'q id kelsa nima bo'lishini boshqarish:\n"
            "// export const dynamicParams = true;  // DEFAULT — SSR qilinadi, keshga qo'shiladi\n"
            "// export const dynamicParams = false; // faqat ro'yxatdagilar — aks holda 404\n"
            "\n"
            "export default async function CoursePage({ params }) {\n"
            "  const { id } = await params;\n"
            "  const res = await fetch(`https://api.example.com/courses/${id}`);\n"
            "  if (res.status === 404) notFound(); // -> not-found.js\n"
            "  const course = await res.json();\n"
            "\n"
            "  return (\n"
            "    <article>\n"
            "      <h1>{course.title}</h1>\n"
            "    </article>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/shop/[category]/[product]/page.js — ICHMA-ICH dinamik segmentlar =====\n"
            "// URL: /shop/electronics/laptop-15 -> params = { category: 'electronics', product: 'laptop-15' }\n"
            "export async function generateStaticParams() {\n"
            "  const categories = await fetch('https://api.example.com/categories').then((r) => r.json());\n"
            "  // Har bir kategoriya uchun uning mahsulotlarini olib, TO'LIQ kombinatsiya quramiz\n"
            "  const all = await Promise.all(\n"
            "    categories.map(async (cat) => {\n"
            "      const products = await fetch(`https://api.example.com/categories/${cat.slug}/products`).then((r) => r.json());\n"
            "      return products.map((p) => ({ category: cat.slug, product: p.slug }));\n"
            "    })\n"
            "  );\n"
            "  return all.flat();\n"
            "}\n"
            "\n"
            "export default async function ProductPage({ params }) {\n"
            "  const { category, product } = await params;\n"
            "  const data = await fetch(`https://api.example.com/categories/${category}/products/${product}`).then((r) => r.json());\n"
            "  return <h1>{data.name}</h1>;\n"
            "}\n"
            "\n"
            "// ===== app/docs/[...slug]/page.js — catch-all =====\n"
            "// /docs/a -> slug=['a'], /docs/a/b -> slug=['a','b'], /docs/a/b/c -> slug=['a','b','c']\n"
            "export default async function DocsPage({ params }) {\n"
            "  const { slug } = await params;\n"
            "  return <p>Yo'l: {slug.join(' / ')}</p>;\n"
            "}\n"
            "\n"
            "// ===== app/docs/[[...slug]]/page.js — IXTIYORIY catch-all =====\n"
            "// Yuqoridagidan farqli — /docs (segmentsiz) ga ham mos keladi, slug === undefined\n"
            "export default async function DocsOptionalPage({ params }) {\n"
            "  const { slug } = await params; // slug bo'lmasa: undefined\n"
            "  if (!slug) return <p>Barcha hujjatlar bo'limi</p>;\n"
            "  return <p>Yo'l: {slug.join(' / ')}</p>;\n"
            "}\n"
            "\n"
            "// ===== Segment turlari solishtiruvi (izoh sifatida) =====\n"
            "// [id]           -> bitta segment:      /courses/42\n"
            "// [...slug]      -> 1+ segment:          /docs/a, /docs/a/b, /docs/a/b/c\n"
            "// [[...slug]]    -> 0+ segment:          /docs, /docs/a, /docs/a/b\n"
            "//\n"
            "// Muhim: params HAR DOIM Promise (Next.js'ning yangi versiyalarida) —\n"
            "// shuning uchun har bir sahifa komponentida `await params` yozish shart,\n"
            "// hatto sinxron ko'rinsa ham. Buni unutish — eng ko'p uchraydigan tuzatish\n"
            "// qiyin bo'lgan xatolardan biri. Kompilyator har doim ham buni ochiq ogohlantirmaydi.\n"
        ),
        "code_content_ru": (
            "// ===== app/courses/[id]/page.js — SSG + generateStaticParams =====\n"
            "import { notFound } from 'next/navigation';\n"
            "\n"
            "export async function generateStaticParams() {\n"
            "  const courses = await fetch('https://api.example.com/courses').then((r) => r.json());\n"
            "  return courses.map((c) => ({ id: String(c.id) }));\n"
            "}\n"
            "\n"
            "// Управление тем, что происходит с id не из списка:\n"
            "// export const dynamicParams = true;  // ПО УМОЛЧАНИЮ — SSR, добавляется в кеш\n"
            "// export const dynamicParams = false; // только из списка — иначе 404\n"
            "\n"
            "export default async function CoursePage({ params }) {\n"
            "  const { id } = await params;\n"
            "  const res = await fetch(`https://api.example.com/courses/${id}`);\n"
            "  if (res.status === 404) notFound(); // -> not-found.js\n"
            "  const course = await res.json();\n"
            "\n"
            "  return (\n"
            "    <article>\n"
            "      <h1>{course.title}</h1>\n"
            "    </article>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/shop/[category]/[product]/page.js — ВЛОЖЕННЫЕ динамические сегменты =====\n"
            "// URL: /shop/electronics/laptop-15 -> params = { category: 'electronics', product: 'laptop-15' }\n"
            "export async function generateStaticParams() {\n"
            "  const categories = await fetch('https://api.example.com/categories').then((r) => r.json());\n"
            "  // Для каждой категории получаем её товары и строим ПОЛНУЮ комбинацию\n"
            "  const all = await Promise.all(\n"
            "    categories.map(async (cat) => {\n"
            "      const products = await fetch(`https://api.example.com/categories/${cat.slug}/products`).then((r) => r.json());\n"
            "      return products.map((p) => ({ category: cat.slug, product: p.slug }));\n"
            "    })\n"
            "  );\n"
            "  return all.flat();\n"
            "}\n"
            "\n"
            "export default async function ProductPage({ params }) {\n"
            "  const { category, product } = await params;\n"
            "  const data = await fetch(`https://api.example.com/categories/${category}/products/${product}`).then((r) => r.json());\n"
            "  return <h1>{data.name}</h1>;\n"
            "}\n"
            "\n"
            "// ===== app/docs/[...slug]/page.js — catch-all =====\n"
            "// /docs/a -> slug=['a'], /docs/a/b -> slug=['a','b'], /docs/a/b/c -> slug=['a','b','c']\n"
            "export default async function DocsPage({ params }) {\n"
            "  const { slug } = await params;\n"
            "  return <p>Путь: {slug.join(' / ')}</p>;\n"
            "}\n"
            "\n"
            "// ===== app/docs/[[...slug]]/page.js — ОПЦИОНАЛЬНЫЙ catch-all =====\n"
            "// В отличие от выше — подходит и для /docs (без сегмента), slug === undefined\n"
            "export default async function DocsOptionalPage({ params }) {\n"
            "  const { slug } = await params; // если нет сегмента: undefined\n"
            "  if (!slug) return <p>Раздел всех документов</p>;\n"
            "  return <p>Путь: {slug.join(' / ')}</p>;\n"
            "}\n"
            "\n"
            "// ===== Сравнение типов сегментов (в виде комментария) =====\n"
            "// [id]           -> один сегмент:        /courses/42\n"
            "// [...slug]      -> 1+ сегмент:           /docs/a, /docs/a/b, /docs/a/b/c\n"
            "// [[...slug]]    -> 0+ сегментов:         /docs, /docs/a, /docs/a/b\n"
            "//\n"
            "// Важно: params ВСЕГДА Promise (в новых версиях Next.js) — поэтому в\n"
            "// каждом компоненте страницы нужно писать `await params`, даже если это\n"
            "// выглядит синхронно. Забыть об этом — одна из самых частых и трудно\n"
            "// диагностируемых ошибок. Компилятор не всегда явно предупреждает об этом,\n"
            "// поэтому стоит взять это в привычку с самого начала.\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Dinamik blog marshrutini generateStaticParams bilan quring",
            "task_title_ru": "Постройте динамический маршрут блога с generateStaticParams",
            "task_description": (
                "app/blog/[slug]/page.js sahifasi uchun generateStaticParams funksiyasini "
                "yozing (barcha post slug'larini qaytarsin) va dynamicParams sozlamasini "
                "tanlab, nima uchun aynan shu qiymatni tanlaganingizni tushuntiring."
            ),
            "task_description_ru": (
                "Напишите функцию generateStaticParams для страницы app/blog/[slug]/page.js "
                "(она должна возвращать все slug'и постов), выберите настройку dynamicParams и "
                "объясните, почему выбрали именно такое значение."
            ),
            "task_requirements": (
                "generateStaticParams massiv qaytarishi, har bir element {slug: '...'} "
                "shaklida bo'lishi shart."
            ),
            "task_requirements_ru": (
                "generateStaticParams должна возвращать массив, каждый элемент в форме "
                "{slug: '...'}."
            ),
            "task_technologies": "Next.js, generateStaticParams, dynamic routes",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: dinamik blog post sahifasi",
            "description": "generateStaticParams orqali barcha postlarni oldindan render qilish.",
            "sample_type": "code",
            "code_files": [
                {"filename": "app/blog/[slug]/page.js", "language": "jsx",
                 "code": "export async function generateStaticParams() {\n  const posts = await fetch('https://api.example.com/posts').then((r) => r.json());\n  return posts.map((p) => ({ slug: p.slug }));\n}\n\nexport default async function PostPage({ params }) {\n  const { slug } = await params;\n  const post = await fetch(`https://api.example.com/posts/${slug}`).then((r) => r.json());\n  return (\n    <article>\n      <h1>{post.title}</h1>\n      <p>{post.body}</p>\n    </article>\n  );\n}\n"},
            ],
        },
        "exercises": [
            {
                "title": "Catch-all segment",
                "title_ru": "Catch-all сегмент",
                "description": "app/docs/[...slug]/page.js qaysi URL'larga mos keladi?",
                "description_ru": "Каким URL соответствует app/docs/[...slug]/page.js?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Faqat /docs/a",
                    "Faqat /docs",
                    "/docs/a, /docs/a/b, /docs/a/b/c — barchasi",
                    "Hech qaysi biriga, bu xato sintaksis",
                ],
                "options_ru": [
                    "Только /docs/a",
                    "Только /docs",
                    "/docs/a, /docs/a/b, /docs/a/b/c — всем сразу",
                    "Ни одному, это неверный синтаксис",
                ],
                "correct_answers": "C",
                "is_multiple_select": False,
                "hint": "Uch nuqta (...) bir nechta segmentni birdaniga ushlaydi.",
                "hint_ru": "Троеточие (...) захватывает сразу несколько сегментов.",
                "explanation": "[...slug] — catch-all, u istalgan sonli ichki segmentlarga mos keladi.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Build vaqtida qaysi id'lar render qilinishi",
                "title_ru": "Какие id рендерятся во время сборки",
                "description": (
                    "Bo'shliqni to'ldiring: build vaqtida qaysi parametr qiymatlari uchun "
                    "statik sahifa tayyorlanishini ___ funksiyasi belgilaydi."
                ),
                "description_ru": (
                    "Заполните пропуск: для каких значений параметров готовится статичная "
                    "страница во время сборки, определяет функция ___."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "generateStaticParams",
                "hint": "Nomi o'zi vazifasini aytib turibdi: statik parametrlar generatsiya qiladi.",
                "hint_ru": "Имя говорит само за себя: генерирует статичные параметры.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Ro'yxatda yo'q id kelganda oqim",
                "title_ru": "Поток при id, отсутствующем в списке",
                "description": (
                    "dynamicParams=true holatida ro'yxatda yo'q id so'ralganda sodir bo'ladigan "
                    "qadamlarni to'g'ri tartibga joylashtiring."
                ),
                "description_ru": (
                    "Расставьте по порядку шаги, происходящие при dynamicParams=true, когда "
                    "запрашивается id не из списка."
                ),
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Foydalanuvchi ro'yxatda yo'q id'ni so'raydi",
                    "Next.js sahifani so'rov vaqtida render qiladi",
                    "Natija keshga qo'shiladi",
                    "Keyingi xuddi shu so'rovlar keshdan xizmat qiladi",
                ],
                "drag_items_ru": [
                    "Пользователь запрашивает id не из списка",
                    "Next.js рендерит страницу во время запроса",
                    "Результат добавляется в кеш",
                    "Следующие такие же запросы обслуживаются из кеша",
                ],
                "correct_order": [
                    "Foydalanuvchi ro'yxatda yo'q id'ni so'raydi",
                    "Next.js sahifani so'rov vaqtida render qiladi",
                    "Natija keshga qo'shiladi",
                    "Keyingi xuddi shu so'rovlar keshdan xizmat qiladi",
                ],
                "hint": "Bu — ISR'ga o'xshash \"birinchi so'rovda to'ldirish\" xatti-harakati.",
                "hint_ru": "Это поведение похоже на ISR — «заполнение по первому запросу».",
                "difficulty_level": "Hard",
                "points": 15,
            },
        ],
    },
    {
        "order": 9,
        "title": "9-Middleware: so'rov hayotiy sikli, auth va redirect",
        "title_ru": "9-Middleware: жизненный цикл запроса, auth и редиректы",
        "points_reward": 15,
        "text_content": (
            "<h3>CRA'da auth tekshiruvi qayerda bo'ladi?</h3>"
            "<p>CRA'da (shu platformaning frontend'ida) himoyalangan sahifani tekshirish "
            "odatda komponent ichida amalga oshiriladi: <code>useEffect</code> ichida token bor-"
            "yo'qligi tekshiriladi, yo'q bo'lsa <code>navigate('/login')</code> chaqiriladi. "
            "Muammo shundaki, bu tekshiruv FAQAT komponent render bo'lgandan keyin ishga "
            "tushadi — ya'ni brauzer avval himoyalangan sahifaning bir qismini (hatto bir lahza "
            "bo'lsa ham) ko'rsatib, keyin qayta yo'naltiradi.</p>"
            "<h3>Middleware — so'rov sahifaga yetib bormasdan oldin</h3>"
            "<p>Next.js'da <code>middleware.js</code> (loyihaning ILDIZIDA, <code>app/</code> "
            "papkasidan tashqarida) — so'rov HALI HECH QANDAY sahifa yoki Route Handler'ga "
            "yetib bormasdan oldin ishga tushadigan funksiya. U so'rovni ko'rib chiqadi (cookie, "
            "header, URL) va uchta narsadan birini qila oladi: "
            "<code>NextResponse.next()</code> — so'rovni odatdagidek davom ettirish; "
            "<code>NextResponse.redirect(url)</code> — brauzerni butunlay boshqa URL'ga "
            "yo'naltirish; <code>NextResponse.rewrite(url)</code> — brauzerga ko'rinmas holda, "
            "ichki ravishda boshqa marshrutga xizmat qilish (URL brauzerda o'zgarmaydi).</p>"
            "<h3>Auth guard misoli</h3>"
            "<p>Middleware yordamida <code>/dashboard</code> ostidagi barcha sahifalarni "
            "himoyalash mumkin: agar so'rovda haqiqiy sessiya cookie'si bo'lmasa, foydalanuvchi "
            "hech qanday dashboard HTML'ini ko'rmasdan turib, darhol <code>/login</code>ga "
            "yo'naltiriladi. Bu — CRA'dagi \"avval ko'rsatib, keyin yo'naltirish\" muammosini "
            "butunlay yo'q qiladi, chunki middleware sahifa render bo'lishidan OLDIN ishlaydi.</p>"
            "<h3>matcher: qayerda ishlashini cheklash</h3>"
            "<p>Middleware har bir so'rovda ishga tushishi shart emas — bu haddan tashqari "
            "isrofgarchilik bo'lardi (masalan, rasm yoki CSS fayli uchun ham ishga tushishi "
            "shart emas). <code>config.matcher</code> orqali middleware faqat kerakli yo'llarda "
            "(masalan, <code>/dashboard/:path*</code>) ishlashi aniq belgilanadi, static "
            "fayllar va <code>_next</code> ichki resurslari odatda chetlab o'tiladi.</p>"
            "<h3>Muhim cheklov: Edge runtime</h3>"
            "<p>Middleware odatda \"Edge\" muhitida ishlaydi — bu to'liq Node.js muhitiga "
            "qaraganda ancha cheklangan (masalan, ba'zi Node kutubxonalari yoki to'g'ridan-"
            "to'g'ri ma'lumotlar bazasi drayverlari ishlamasligi mumkin). Shuning uchun "
            "middleware'da odatda faqat yengil tekshiruvlar (cookie/header o'qish, oddiy "
            "qaror qabul qilish) bajariladi, og'ir mantiq esa Route Handler yoki Server "
            "Component'ga qoldiriladi.</p>"
            "<h3>Diagram: so'rov middleware orqali qanday o'tadi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  REQ[\"Brauzer so'rovi:\n"
            "GET /dashboard/settings\"] --> MW[\"middleware.js ishga tushadi\"]\n"
            "  MW --> CK{\"Sessiya cookie\n"
            "mavjudmi?\"}\n"
            "  CK -->|\"yo'q\"| RED[\"NextResponse.redirect('/login')\n"
            "sahifa hech qachon render bo'lmaydi\"]\n"
            "  CK -->|\"ha\"| NEXT[\"NextResponse.next()\"]\n"
            "  NEXT --> PAGE[\"app/dashboard/settings/page.js\n"
            "render bo'ladi\"]\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: cookie yo'q bo'lsa, foydalanuvchi "
            "<code>/dashboard/settings</code>ning HECH QANDAY HTML qismini ko'rmaydi — "
            "yo'naltirish sahifa render bo'lishidan oldin sodir bo'ladi.</p>"
            "<h3>rewrite: boshqa foydalanish holatlari</h3>"
            "<p><code>redirect</code>dan tashqari, <code>NextResponse.rewrite()</code> ham "
            "muhim vosita: u brauzer manzil satrini o'zgartirmasdan, ichki ravishda boshqa "
            "sahifaga xizmat qiladi. Bu, masalan, A/B testlash uchun foydali — foydalanuvchining "
            "yarmi <code>/home-a</code>, yarmi <code>/home-b</code> versiyasini ko'radi, lekin "
            "ikkalasi ham brauzerda xuddi shu <code>/</code> manzilida ko'rinadi. Yana bir keng "
            "tarqalgan holat — tilga qarab yo'naltirish: <code>Accept-Language</code> "
            "header'iga qarab foydalanuvchini <code>/uz/...</code> yoki <code>/ru/...</code> "
            "prefiksli ichki marshrutga rewrite qilish.</p>"
            "<h3>Middleware'da javobni o'zgartirish</h3>"
            "<p>Middleware faqat redirect/rewrite qilib qolmay, javobga yangi header yoki "
            "cookie ham qo'sha oladi — masalan, xavfsizlik header'larini har bir javobga "
            "avtomatik qo'shish uchun ishlatilishi mumkin.</p>"
            "<p>Middleware — bu ilova bo'ylab bir marta yozilib, hamma joyda ishlaydigan qoida "
            "qatlami: uni har bir sahifada alohida qayta yozish o'rniga, bitta markazlashgan "
            "faylda saqlash xatolik qilish ehtimolini kamaytiradi.</p>"
            "<p>Keyingi darsda next/image va next/font rasm va shriftlarni qanday avtomatik "
            "optimallashtirishini ko'ramiz — bu CRA'da qo'lda hal qilinishi kerak bo'lgan "
            "yana bir masala.</p>"
        ),
        "text_content_ru": (
            "<h3>Где в CRA происходит проверка авторизации?</h3>"
            "<p>В CRA (фронтенде этой платформы) проверка защищённой страницы обычно "
            "выполняется внутри компонента: внутри <code>useEffect</code> проверяется наличие "
            "токена, если его нет — вызывается <code>navigate('/login')</code>. Проблема в том, "
            "что эта проверка срабатывает ТОЛЬКО после рендера компонента — то есть браузер "
            "сначала показывает часть защищённой страницы (пусть даже на мгновение), а потом "
            "перенаправляет.</p>"
            "<h3>Middleware — до того, как запрос дойдёт до страницы</h3>"
            "<p>В Next.js <code>middleware.js</code> (в КОРНЕ проекта, вне папки "
            "<code>app/</code>) — это функция, которая выполняется ДО того, как запрос вообще "
            "дойдёт до какой-либо страницы или Route Handler'а. Она изучает запрос (cookie, "
            "заголовки, URL) и может сделать одно из трёх: <code>NextResponse.next()</code> — "
            "продолжить запрос как обычно; <code>NextResponse.redirect(url)</code> — "
            "перенаправить браузер на совсем другой URL; <code>NextResponse.rewrite(url)</code> "
            "— незаметно для браузера внутренне обслужить другой маршрут (URL в браузере не "
            "меняется).</p>"
            "<h3>Пример auth guard</h3>"
            "<p>С помощью middleware можно защитить все страницы под <code>/dashboard</code>: "
            "если в запросе нет настоящего cookie сессии, пользователь немедленно "
            "перенаправляется на <code>/login</code>, вообще не увидев HTML дашборда. Это "
            "полностью устраняет проблему CRA «сначала показать, потом перенаправить», ведь "
            "middleware работает ДО рендера страницы.</p>"
            "<h3>matcher: ограничение области действия</h3>"
            "<p>Middleware не обязан срабатывать на каждый запрос — это было бы избыточно "
            "(например, не нужно срабатывать на запрос изображения или CSS-файла). Через "
            "<code>config.matcher</code> явно указывается, на каких путях middleware должен "
            "работать (например, <code>/dashboard/:path*</code>), статичные файлы и внутренние "
            "ресурсы <code>_next</code> обычно обходятся стороной.</p>"
            "<h3>Важное ограничение: Edge runtime</h3>"
            "<p>Middleware обычно выполняется в среде «Edge» — она значительно более "
            "ограничена, чем полноценная среда Node.js (например, некоторые Node-библиотеки или "
            "прямые драйверы баз данных могут не работать). Поэтому в middleware обычно "
            "выполняются только лёгкие проверки (чтение cookie/заголовков, простые решения), а "
            "тяжёлая логика оставляется для Route Handler или Server Component.</p>"
            "<h3>Диаграмма: как запрос проходит через middleware</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  REQ[\"Запрос браузера:\n"
            "GET /dashboard/settings\"] --> MW[\"выполняется middleware.js\"]\n"
            "  MW --> CK{\"Есть ли\n"
            "cookie сессии?\"}\n"
            "  CK -->|\"нет\"| RED[\"NextResponse.redirect('/login')\n"
            "страница никогда не рендерится\"]\n"
            "  CK -->|\"да\"| NEXT[\"NextResponse.next()\"]\n"
            "  NEXT --> PAGE[\"app/dashboard/settings/page.js\n"
            "рендерится\"]\n"
            "</pre>"
            "<p>Диаграмма показывает: если cookie нет, пользователь НЕ ВИДИТ никакой части HTML "
            "<code>/dashboard/settings</code> — перенаправление происходит до рендера "
            "страницы.</p>"
            "<h3>rewrite: другие случаи использования</h3>"
            "<p>Кроме <code>redirect</code>, важным инструментом является "
            "<code>NextResponse.rewrite()</code>: он обслуживает другую страницу внутренне, не "
            "меняя адресную строку браузера. Это полезно, например, для A/B-тестирования — "
            "половина пользователей видит версию <code>/home-a</code>, половина — "
            "<code>/home-b</code>, но обе видны в браузере по одному и тому же адресу "
            "<code>/</code>. Ещё один распространённый случай — маршрутизация по языку: в "
            "зависимости от заголовка <code>Accept-Language</code> перенаправлять пользователя "
            "на внутренний маршрут с префиксом <code>/uz/...</code> или <code>/ru/...</code>.</p>"
            "<h3>Изменение ответа в middleware</h3>"
            "<p>Middleware может не только делать redirect/rewrite, но и добавлять к ответу "
            "новые заголовки или cookie — например, использоваться для автоматического "
            "добавления заголовков безопасности к каждому ответу.</p>"
            "<p>Middleware — это слой правил, написанный один раз для всего приложения: вместо "
            "того чтобы переписывать проверку на каждой странице отдельно, хранение её в одном "
            "централизованном файле снижает вероятность ошибки.</p>"
            "<p>В следующем уроке мы разберём, как next/image и next/font автоматически "
            "оптимизируют медиафайлы и шрифты — ещё один класс задач, которые в CRA приходится "
            "решать вручную, без встроенной поддержки со стороны фреймворка.</p>"
        ),
        "code_content": (
            "// ===== middleware.js — ILDIZDA, app/ papkasidan tashqarida =====\n"
            "// To'liq misol: auth guard + xavfsizlik header'lari + A/B test rewrite\n"
            "import { NextResponse } from 'next/server';\n"
            "\n"
            "export function middleware(request) {\n"
            "  const { pathname } = request.nextUrl;\n"
            "\n"
            "  // 1) AUTH GUARD: /dashboard va /admin ostidagi sahifalarni himoyalash\n"
            "  if (pathname.startsWith('/dashboard') || pathname.startsWith('/admin')) {\n"
            "    const sessionCookie = request.cookies.get('session_token');\n"
            "    if (!sessionCookie) {\n"
            "      const loginUrl = new URL('/login', request.url);\n"
            "      loginUrl.searchParams.set('from', pathname); // login'dan keyin qayerga qaytish\n"
            "      return NextResponse.redirect(loginUrl);\n"
            "    }\n"
            "  }\n"
            "\n"
            "  // 2) A/B TEST: bosh sahifaning ikkita versiyasini rewrite orqali ko'rsatish\n"
            "  if (pathname === '/') {\n"
            "    const bucket = request.cookies.get('ab_bucket')?.value ?? (Math.random() < 0.5 ? 'a' : 'b');\n"
            "    const response = NextResponse.rewrite(new URL(`/home-${bucket}`, request.url));\n"
            "    response.cookies.set('ab_bucket', bucket); // keyingi tashrifda ham bir xil versiya\n"
            "    return response;\n"
            "  }\n"
            "\n"
            "  // 3) XAVFSIZLIK HEADER'LARI: har bir javobga qo'shiladi\n"
            "  const response = NextResponse.next();\n"
            "  response.headers.set('X-Content-Type-Options', 'nosniff');\n"
            "  response.headers.set('X-Frame-Options', 'DENY');\n"
            "  return response;\n"
            "}\n"
            "\n"
            "export const config = {\n"
            "  // Statik fayllar va _next ichki resurslarida ISHLAMAYDI — performance uchun muhim\n"
            "  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],\n"
            "};\n"
            "\n"
            "// ===================================================================\n"
            "// QO'SHIMCHA MISOL: Accept-Language asosida tilga qarab rewrite\n"
            "// (yuqoridagi asosiy middleware'dan ALOHIDA, faqat naqshni ko'rsatish uchun)\n"
            "// ===================================================================\n"
            "function localeMiddleware(request) {\n"
            "  const { pathname } = request.nextUrl;\n"
            "  const hasLocale = /^\\/(uz|ru|en)(\\/|$)/.test(pathname);\n"
            "  if (hasLocale) return NextResponse.next();\n"
            "\n"
            "  const acceptLanguage = request.headers.get('accept-language') || '';\n"
            "  const preferred = acceptLanguage.startsWith('ru') ? 'ru' : 'uz';\n"
            "  return NextResponse.redirect(new URL(`/${preferred}${pathname}`, request.url));\n"
            "}\n"
            "\n"
            "// matcher naqshi qanday o'qiladi:\n"
            "//   '/((?!_next/static|_next/image|favicon.ico).*)'\n"
            "//   -> \"har qanday yo'l, BUNDAN TASHQARI _next/static, _next/image, favicon.ico\n"
            "//      bilan boshlanadigan yo'llar\" (negative lookahead)\n"
            "// Bu — middleware'ni HAR bir rasm/CSS so'rovida ham ishga tushirib,\n"
            "// keraksiz sekinlik keltirib chiqarmaslik uchun standart naqsh.\n"
            "\n"
            "// ===================================================================\n"
            "// XATO YO'L: Edge runtime cheklovini e'tiborsiz qoldirish\n"
            "// ===================================================================\n"
            "// export async function middleware(request) {\n"
            "//   const user = await db.query('SELECT * FROM users WHERE ...'); // ❌\n"
            "//   // Ko'p to'g'ridan-to'g'ri ma'lumotlar bazasi drayverlari Edge\n"
            "//   // runtime'da ishlamaydi — bu server-only Node.js kutubxonasi.\n"
            "// }\n"
            "// TO'G'RI: middleware'da faqat cookie/header o'qish kabi yengil\n"
            "// tekshiruvlar qiling, og'ir mantiqni Route Handler'ga qoldiring.\n"
        ),
        "code_content_ru": (
            "// ===== middleware.js — В КОРНЕ, вне папки app/ =====\n"
            "// Полный пример: auth guard + заголовки безопасности + A/B-тест через rewrite\n"
            "import { NextResponse } from 'next/server';\n"
            "\n"
            "export function middleware(request) {\n"
            "  const { pathname } = request.nextUrl;\n"
            "\n"
            "  // 1) AUTH GUARD: защита страниц под /dashboard и /admin\n"
            "  if (pathname.startsWith('/dashboard') || pathname.startsWith('/admin')) {\n"
            "    const sessionCookie = request.cookies.get('session_token');\n"
            "    if (!sessionCookie) {\n"
            "      const loginUrl = new URL('/login', request.url);\n"
            "      loginUrl.searchParams.set('from', pathname); // куда вернуться после логина\n"
            "      return NextResponse.redirect(loginUrl);\n"
            "    }\n"
            "  }\n"
            "\n"
            "  // 2) A/B-ТЕСТ: показ двух версий главной страницы через rewrite\n"
            "  if (pathname === '/') {\n"
            "    const bucket = request.cookies.get('ab_bucket')?.value ?? (Math.random() < 0.5 ? 'a' : 'b');\n"
            "    const response = NextResponse.rewrite(new URL(`/home-${bucket}`, request.url));\n"
            "    response.cookies.set('ab_bucket', bucket); // та же версия при следующем визите\n"
            "    return response;\n"
            "  }\n"
            "\n"
            "  // 3) ЗАГОЛОВКИ БЕЗОПАСНОСТИ: добавляются к каждому ответу\n"
            "  const response = NextResponse.next();\n"
            "  response.headers.set('X-Content-Type-Options', 'nosniff');\n"
            "  response.headers.set('X-Frame-Options', 'DENY');\n"
            "  return response;\n"
            "}\n"
            "\n"
            "export const config = {\n"
            "  // НЕ работает для статичных файлов и внутренних ресурсов _next — важно для производительности\n"
            "  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],\n"
            "};\n"
            "\n"
            "// ===================================================================\n"
            "// ДОПОЛНИТЕЛЬНЫЙ ПРИМЕР: rewrite по языку на основе Accept-Language\n"
            "// (ОТДЕЛЬНО от основного middleware выше, показан только сам паттерн)\n"
            "// ===================================================================\n"
            "function localeMiddleware(request) {\n"
            "  const { pathname } = request.nextUrl;\n"
            "  const hasLocale = /^\\/(uz|ru|en)(\\/|$)/.test(pathname);\n"
            "  if (hasLocale) return NextResponse.next();\n"
            "\n"
            "  const acceptLanguage = request.headers.get('accept-language') || '';\n"
            "  const preferred = acceptLanguage.startsWith('ru') ? 'ru' : 'uz';\n"
            "  return NextResponse.redirect(new URL(`/${preferred}${pathname}`, request.url));\n"
            "}\n"
            "\n"
            "// Как читается паттерн matcher:\n"
            "//   '/((?!_next/static|_next/image|favicon.ico).*)'\n"
            "//   -> «любой путь, КРОМЕ путей, начинающихся с _next/static, _next/image,\n"
            "//      favicon.ico» (negative lookahead)\n"
            "// Это стандартный паттерн, чтобы не запускать middleware на КАЖДОМ запросе\n"
            "// изображения/CSS и не создавать лишнюю задержку.\n"
            "\n"
            "// ===================================================================\n"
            "// НЕПРАВИЛЬНЫЙ ПУТЬ: игнорирование ограничений Edge runtime\n"
            "// ===================================================================\n"
            "// export async function middleware(request) {\n"
            "//   const user = await db.query('SELECT * FROM users WHERE ...'); // ❌\n"
            "//   // Многие драйверы баз данных не работают в Edge runtime —\n"
            "//   // это серверная Node.js-библиотека.\n"
            "// }\n"
            "// ПРАВИЛЬНО: в middleware делайте только лёгкие проверки вроде чтения\n"
            "// cookie/заголовков, тяжёлую логику оставляйте для Route Handler.\n"
        ),
        "code_language": "javascript",
        "video_url": None,
        "task": {
            "task_title": "Auth guard middleware yozing",
            "task_title_ru": "Напишите middleware для auth guard",
            "task_description": (
                "middleware.js yozing: /admin ostidagi barcha sahifalarni himoyalang — sessiya "
                "cookie'si yo'q bo'lsa /login'ga redirect qiling, qaytish manzilini query "
                "parametr sifatida saqlang. matcher orqali middleware faqat /admin/* uchun "
                "ishlashini ta'minlang."
            ),
            "task_description_ru": (
                "Напишите middleware.js: защитите все страницы под /admin — при отсутствии "
                "cookie сессии делайте redirect на /login, сохраняя адрес возврата как "
                "query-параметр. Через matcher обеспечьте, чтобы middleware работал только для "
                "/admin/*."
            ),
            "task_requirements": (
                "config.matcher aniq belgilangan, redirect logikasi cookie yo'qligini to'g'ri "
                "tekshirishi shart."
            ),
            "task_requirements_ru": (
                "config.matcher должен быть чётко указан, логика redirect обязана корректно "
                "проверять отсутствие cookie."
            ),
            "task_technologies": "Next.js, Middleware, NextResponse",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: /admin uchun auth middleware",
            "description": "Sessiya cookie tekshiruvi va redirect bilan middleware namunasi.",
            "sample_type": "code",
            "code_files": [
                {"filename": "middleware.js", "language": "javascript",
                 "code": "import { NextResponse } from 'next/server';\n\nexport function middleware(request) {\n  const token = request.cookies.get('session_token');\n  if (!token) {\n    const url = new URL('/login', request.url);\n    return NextResponse.redirect(url);\n  }\n  return NextResponse.next();\n}\n\nexport const config = { matcher: ['/admin/:path*'] };\n"},
            ],
        },
        "exercises": [
            {
                "title": "Middleware qachon ishga tushadi",
                "title_ru": "Когда выполняется middleware",
                "description": "Middleware so'rov hayotiy siklida qachon ishga tushadi?",
                "description_ru": "Когда в жизненном цикле запроса выполняется middleware?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Sahifa render bo'lgandan keyin, brauzerda",
                    "Sahifa yoki Route Handler'ga yetib bormasdan oldin",
                    "Faqat foydalanuvchi formani yuborganda",
                    "Faqat build vaqtida, bir marta",
                ],
                "options_ru": [
                    "После рендера страницы, в браузере",
                    "До того, как запрос дойдёт до страницы или Route Handler'а",
                    "Только когда пользователь отправляет форму",
                    "Только во время сборки, один раз",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Bu — middleware'ning eng katta afzalligi (auth guard uchun).",
                "hint_ru": "Это главное преимущество middleware (для auth guard).",
                "explanation": "Middleware so'rov sahifaga yetib borishidan oldin ishga tushadi, shuning uchun himoyalangan kontent hech qachon ko'rinmaydi.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Middleware faylining joylashuvi",
                "title_ru": "Расположение файла middleware",
                "description": (
                    "Bo'shliqni to'ldiring: middleware fayli loyihaning ___ida, app/ "
                    "papkasidan tashqarida joylashishi kerak."
                ),
                "description_ru": (
                    "Заполните пропуск: файл middleware должен находиться в ___ проекта, вне "
                    "папки app/."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "root",
                "hint": "Ildiz papka — loyihaning eng yuqori darajasi.",
                "hint_ru": "Корневая папка — самый верхний уровень проекта.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "So'rov middleware orqali oqimi",
                "title_ru": "Поток запроса через middleware",
                "description": "Sessiya cookie yo'q bo'lgan holatda sodir bo'ladigan qadamlarni tartibga joylashtiring.",
                "description_ru": "Расставьте по порядку шаги, происходящие при отсутствии cookie сессии.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Brauzer /dashboard so'rovini yuboradi",
                    "middleware.js ishga tushadi",
                    "Cookie yo'qligi aniqlanadi",
                    "NextResponse.redirect('/login') qaytariladi",
                ],
                "drag_items_ru": [
                    "Браузер отправляет запрос /dashboard",
                    "Выполняется middleware.js",
                    "Обнаруживается отсутствие cookie",
                    "Возвращается NextResponse.redirect('/login')",
                ],
                "correct_order": [
                    "Brauzer /dashboard so'rovini yuboradi",
                    "middleware.js ishga tushadi",
                    "Cookie yo'qligi aniqlanadi",
                    "NextResponse.redirect('/login') qaytariladi",
                ],
                "hint": "Sahifa hech qachon render bo'lmaydi.",
                "hint_ru": "Страница никогда не рендерится.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 10,
        "title": "10-Rasm va shrift optimizatsiyasi (next/image, next/font)",
        "title_ru": "10-Оптимизация изображений и шрифтов (next/image, next/font)",
        "points_reward": 15,
        "text_content": (
            "<h3>CRA'da rasm va shrift qanday ishlaydi</h3>"
            "<p>CRA'da (shu platformaning frontend'ida) rasm oddiy <code>&lt;img src=\"...\" /&gt;</code> "
            "tegi orqali qo'yiladi — brauzer uni asl o'lchamida yuklaydi, hech qanday avtomatik "
            "siqish yoki format konversiyasi bo'lmaydi, va agar <code>width</code>/<code>height</code> "
            "belgilanmasa, rasm yuklangach sahifa \"sakrab\" ketishi mumkin (layout shift). "
            "Shriftlar esa <code>frontend/public/index.html</code>da ko'ramiz: "
            "<code>&lt;link rel=\"preconnect\" href=\"https://fonts.googleapis.com\"&gt;</code> "
            "kabi tashqi Google Fonts manziliga ulanish orqali yuklanadi — bu degani, har bir "
            "foydalanuvchi brauzeri sahifani ko'rsatish uchun tashqi <code>fonts.googleapis.com</code> "
            "serveriga alohida so'rov yuborishi kerak.</p>"
            "<h3>next/image: avtomatik optimallashtirish</h3>"
            "<p><code>&lt;Image&gt;</code> komponenti (<code>next/image</code>dan) oddiy "
            "<code>&lt;img&gt;</code>ning o'rnini bosadi, lekin bir nechta avtomatik "
            "xususiyatga ega: (1) rasmni brauzer qo'llab-quvvatlaydigan zamonaviy formatga "
            "(masalan, WebP) avtomatik aylantiradi; (2) <code>width</code> va <code>height</code> "
            "MAJBURIY (yoki <code>fill</code> propi) — bu layout shift'ning oldini oladi, "
            "chunki brauzer rasm hali yuklanmasidan turib uning egallaydigan joyini biladi; "
            "(3) default holatda \"lazy loading\" — ekrandan tashqaridagi rasmlar faqat "
            "foydalanuvchi ularga yaqinlashganda yuklanadi; (4) <code>priority</code> propi — "
            "birinchi ekranda ko'rinadigan muhim rasm (masalan, hero banner) uchun lazy "
            "loading'ni o'chirib, uni erta yuklashni ta'minlaydi.</p>"
            "<h3>Tashqi manba rasmlar uchun sozlash</h3>"
            "<p>Agar rasm boshqa domendan (masalan, bulutli saqlash xizmatidan) kelayotgan "
            "bo'lsa, uni <code>next.config.js</code> faylida <code>images.remotePatterns</code> "
            "orqali oldindan ruxsat berish kerak — bu xavfsizlik chorasi: Next.js faqat aniq "
            "ruxsat berilgan domenlardan rasm optimallashtirishga rozi bo'ladi.</p>"
            "<h3>next/font: shriftlarni build vaqtida joylashtirish</h3>"
            "<p><code>next/font/google</code> orqali Google Fonts'dan shrift ulash — CRA'dagi "
            "kabi HAR SAFAR foydalanuvchi brauzerida tashqi so'rov yuborish o'rniga, shrift "
            "fayllari BUILD VAQTIDA yuklab olinadi va ilova bilan birga o'z serveringizdan "
            "xizmat qilinadi. Bu ikki foyda beradi: tashqi so'rov umuman yo'q (tezroq va "
            "maxfiylikka foydali), va shrift avtomatik <code>font-display</code> sozlamasi bilan "
            "keladi (matn shrift yuklanishini kutmasdan darhol ko'rinadi). Maxsus/lokal shrift "
            "fayllari uchun esa <code>next/font/local</code> ishlatiladi.</p>"
            "<h3>Nega bu ahamiyatli</h3>"
            "<p>Rasm va shrift — sahifaning \"og'irligi\"ni belgilaydigan eng katta ikki "
            "omil. CRA'da bularni optimallashtirish — qo'lda qilinadigan qo'shimcha ish "
            "(rasmlarni oldindan siqish, shriftlarni o'zi joylashtirish). Next.js'da bu — "
            "freymvorkning o'zi taqdim etadigan standart xatti-harakat, dasturchi faqat "
            "<code>&lt;Image&gt;</code> va <code>next/font</code>ni ishlatishni tanlashi kifoya.</p>"
            "<h3>sizes propi va turli ekran o'lchamlari</h3>"
            "<p>Responsiv dizaynda bir xil rasm turli ekranlarda turli fizik o'lchamda "
            "ko'rsatiladi (masalan, mobil telefonda butun ekran kengligida, desktopda esa "
            "sahifaning uchdan bir qismida). <code>&lt;Image&gt;</code>ga <code>sizes</code> "
            "propini berish orqali brauzerga \"bu rasm turli ekran kengliklarida taxminan "
            "qancha joy egallaydi\" haqida ma'lumot beriladi — shunda brauzer avtomatik "
            "generatsiya qilingan bir nechta o'lchamdan eng mos kelganini yuklaydi, ortiqcha "
            "katta faylni behuda yuklab olmaydi.</p>"
            "<h3>Lokal shrift fayllari</h3>"
            "<p>Agar shrift Google Fonts'da bo'lmagan maxsus fayl bo'lsa (masalan, kompaniyaning "
            "o'z brend shrifti), <code>next/font/local</code> ishlatiladi — bunda "
            "<code>.woff2</code> fayl loyihaning o'zida saqlanadi va xuddi Google Fonts kabi "
            "build vaqtida optimallashtiriladi, faqat tashqi manbadan yuklab olish qadami "
            "umuman yo'q.</p>"
            "<p>Xulosa qilib aytganda: <code>next/image</code> va <code>next/font</code> — "
            "ikkalasi ham bir xil g'oyani ifodalaydi — brauzerga eng kam ishni qoldirish, "
            "imkon qadar ko'proq ishni build vaqtida yoki serverda hal qilish, natijada "
            "foydalanuvchi qurilmasi tezroq va kamroq trafik bilan sahifani ko'rsatadi.</p>"
            "<p>Bu ikkala vosita ham 11-darsda ko'radigan Metadata API bilan bir qatorda "
            "turadi — ularning barchasi \"CRA'da qo'lda qilinadigan narsani Next.js'da bepul "
            "olish\" mavzusining bir qismi.</p>"
        ),
        "text_content_ru": (
            "<h3>Как работают изображения и шрифты в CRA</h3>"
            "<p>В CRA (фронтенде этой платформы) изображение вставляется обычным тегом "
            "<code>&lt;img src=\"...\" /&gt;</code> — браузер загружает его в исходном размере, "
            "без автоматического сжатия или конвертации формата, и если "
            "<code>width</code>/<code>height</code> не указаны, страница может «прыгнуть» после "
            "загрузки картинки (layout shift). Шрифты же мы видим в "
            "<code>frontend/public/index.html</code>: они загружаются через подключение к "
            "внешнему адресу Google Fonts вроде "
            "<code>&lt;link rel=\"preconnect\" href=\"https://fonts.googleapis.com\"&gt;</code> "
            "— это значит, что браузер каждого пользователя должен отправить отдельный запрос "
            "на внешний сервер <code>fonts.googleapis.com</code>, чтобы показать страницу.</p>"
            "<h3>next/image: автоматическая оптимизация</h3>"
            "<p>Компонент <code>&lt;Image&gt;</code> (из <code>next/image</code>) заменяет "
            "обычный <code>&lt;img&gt;</code>, но имеет несколько автоматических особенностей: "
            "(1) автоматически конвертирует изображение в современный формат, поддерживаемый "
            "браузером (например, WebP); (2) <code>width</code> и <code>height</code> "
            "ОБЯЗАТЕЛЬНЫ (либо проп <code>fill</code>) — это предотвращает layout shift, ведь "
            "браузер знает, какое место займёт изображение, ещё до его загрузки; (3) по "
            "умолчанию «ленивая загрузка» — изображения вне экрана загружаются только когда "
            "пользователь к ним приближается; (4) проп <code>priority</code> — для важного "
            "изображения на первом экране (например, hero-баннер) отключает ленивую загрузку, "
            "обеспечивая её раннюю загрузку.</p>"
            "<h3>Настройка для изображений с внешних источников</h3>"
            "<p>Если изображение приходит с другого домена (например, из облачного хранилища), "
            "его нужно заранее разрешить в файле <code>next.config.js</code> через "
            "<code>images.remotePatterns</code> — это мера безопасности: Next.js соглашается "
            "оптимизировать изображения только с явно разрешённых доменов.</p>"
            "<h3>next/font: размещение шрифтов во время сборки</h3>"
            "<p>Подключение шрифта из Google Fonts через <code>next/font/google</code> — вместо "
            "того чтобы, как в CRA, КАЖДЫЙ РАЗ отправлять внешний запрос из браузера "
            "пользователя, файлы шрифта скачиваются ВО ВРЕМЯ СБОРКИ и обслуживаются с вашего "
            "собственного сервера вместе с приложением. Это даёт два преимущества: внешнего "
            "запроса вообще нет (быстрее и лучше для приватности), и шрифт автоматически "
            "получает настройку <code>font-display</code> (текст виден сразу, не дожидаясь "
            "загрузки шрифта). Для собственных/локальных файлов шрифтов используется "
            "<code>next/font/local</code>.</p>"
            "<h3>Почему это важно</h3>"
            "<p>Изображения и шрифты — два крупнейших фактора, определяющих «вес» страницы. В "
            "CRA их оптимизация — дополнительная ручная работа (заранее сжимать изображения, "
            "самостоятельно размещать шрифты). В Next.js это — стандартное поведение самого "
            "фреймворка, разработчику достаточно просто выбрать использовать "
            "<code>&lt;Image&gt;</code> и <code>next/font</code>.</p>"
            "<h3>Проп sizes и разные размеры экрана</h3>"
            "<p>В адаптивном дизайне одно и то же изображение показывается в разных физических "
            "размерах на разных экранах (например, во весь экран на телефоне, но лишь треть "
            "страницы на десктопе). Передавая <code>&lt;Image&gt;</code> проп <code>sizes</code>, "
            "браузеру сообщается, «сколько места примерно займёт это изображение при разной "
            "ширине экрана» — тогда браузер автоматически загружает наиболее подходящий из "
            "нескольких сгенерированных размеров, не скачивая зря слишком крупный файл.</p>"
            "<h3>Локальные файлы шрифтов</h3>"
            "<p>Если шрифт — не из Google Fonts, а собственный файл (например, фирменный шрифт "
            "компании), используется <code>next/font/local</code> — файл <code>.woff2</code> "
            "хранится в самом проекте и оптимизируется во время сборки так же, как и Google "
            "Fonts, только без шага скачивания из внешнего источника.</p>"
            "<p>Подводя итог: <code>next/image</code> и <code>next/font</code> выражают одну и "
            "ту же идею — переложить как можно больше работы с браузера на время сборки или на "
            "сервер, чтобы устройство пользователя показывало страницу быстрее и с меньшим "
            "трафиком.</p>"
            "<p>Оба этих инструмента стоят в одном ряду с Metadata API, который мы увидим в "
            "уроке 11 — все они часть одной темы: «то, что в CRA делается вручную, в Next.js "
            "достаётся бесплатно».</p>"
        ),
        "code_content": (
            "// ===== app/courses/[id]/page.js — hero rasm + shrift =====\n"
            "import Image from 'next/image';\n"
            "import { Inter } from 'next/font/google';\n"
            "\n"
            "const inter = Inter({ subsets: ['latin'], display: 'swap' });\n"
            "\n"
            "export default async function CoursePage({ params }) {\n"
            "  const { id } = await params;\n"
            "  const course = await fetch(`https://api.example.com/courses/${id}`).then((r) => r.json());\n"
            "\n"
            "  return (\n"
            "    <article className={inter.className}>\n"
            "      <Image\n"
            "        src={course.coverUrl}\n"
            "        alt={course.title}\n"
            "        width={800}\n"
            "        height={400}\n"
            "        priority // birinchi ekranda ko'rinadigan muhim rasm\n"
            "      />\n"
            "      <h1>{course.title}</h1>\n"
            "    </article>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/products/page.js — galereya: sizes propi bilan responsiv rasm =====\n"
            "export default async function ProductGalleryPage() {\n"
            "  const products = await fetch('https://api.example.com/products').then((r) => r.json());\n"
            "\n"
            "  return (\n"
            "    <div className=\"grid\">\n"
            "      {products.map((p) => (\n"
            "        <div key={p.id} style={{ position: 'relative', aspectRatio: '4 / 3' }}>\n"
            "          <Image\n"
            "            src={p.imageUrl}\n"
            "            alt={p.name}\n"
            "            fill // ota konteyner o'lchamini to'ldiradi, width/height o'rniga\n"
            "            sizes=\"(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw\"\n"
            "            style={{ objectFit: 'cover' }}\n"
            "          />\n"
            "        </div>\n"
            "      ))}\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== Lokal shrift fayli (Google Fonts'da bo'lmagan brend shrifti) =====\n"
            "// app/fonts/local-font.js\n"
            "import localFont from 'next/font/local';\n"
            "\n"
            "export const brandFont = localFont({\n"
            "  src: '../../public/fonts/BrandSans.woff2',\n"
            "  display: 'swap',\n"
            "});\n"
            "\n"
            "// next.config.js — tashqi domenga ruxsat berish\n"
            "module.exports = {\n"
            "  images: {\n"
            "    remotePatterns: [{ protocol: 'https', hostname: 'cdn.example.com' }],\n"
            "  },\n"
            "};\n"
            "\n"
            "// ===================================================================\n"
            "// XATO YO'L: oddiy <img>, o'lchamsiz — layout shift keltirib chiqaradi\n"
            "// ===================================================================\n"
            "// <img src={course.coverUrl} alt={course.title} /> // ❌\n"
            "// Brauzer rasm yuklanmaguncha uning balandligini bilmaydi — sahifa\n"
            "// tarkibi rasm paydo bo'lganda pastga \"sakraydi\".\n"
            "\n"
            "// TO'G'RI YO'L: har doim width/height (yoki fill + konteyner o'lchami)\n"
            "// <Image src={course.coverUrl} alt={course.title} width={800} height={400} /> // ✅\n"
            "\n"
            "// ===== app/layout.js — bir nechta og'irlikdagi shrift + CSS o'zgaruvchisi =====\n"
            "import { Inter, Roboto_Mono } from 'next/font/google';\n"
            "\n"
            "const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });\n"
            "const robotoMono = Roboto_Mono({\n"
            "  subsets: ['latin'],\n"
            "  weight: ['400', '700'],\n"
            "  variable: '--font-mono',\n"
            "});\n"
            "\n"
            "export default function RootLayout({ children }) {\n"
            "  return (\n"
            "    <html lang=\"uz\" className={`${inter.variable} ${robotoMono.variable}`}>\n"
            "      <body>{children}</body>\n"
            "    </html>\n"
            "  );\n"
            "}\n"
            "// CSS'da: font-family: var(--font-inter); yoki var(--font-mono);\n"
            "// Ikkalasi ham build vaqtida yuklab olinadi — tashqi so'rov yo'q, foydalanuvchi maxfiyligi ancha yaxshiroq.\n"
        ),
        "code_content_ru": (
            "// ===== app/courses/[id]/page.js — hero-изображение + шрифт =====\n"
            "import Image from 'next/image';\n"
            "import { Inter } from 'next/font/google';\n"
            "\n"
            "const inter = Inter({ subsets: ['latin'], display: 'swap' });\n"
            "\n"
            "export default async function CoursePage({ params }) {\n"
            "  const { id } = await params;\n"
            "  const course = await fetch(`https://api.example.com/courses/${id}`).then((r) => r.json());\n"
            "\n"
            "  return (\n"
            "    <article className={inter.className}>\n"
            "      <Image\n"
            "        src={course.coverUrl}\n"
            "        alt={course.title}\n"
            "        width={800}\n"
            "        height={400}\n"
            "        priority // важное изображение на первом экране\n"
            "      />\n"
            "      <h1>{course.title}</h1>\n"
            "    </article>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/products/page.js — галерея: адаптивное изображение с sizes =====\n"
            "export default async function ProductGalleryPage() {\n"
            "  const products = await fetch('https://api.example.com/products').then((r) => r.json());\n"
            "\n"
            "  return (\n"
            "    <div className=\"grid\">\n"
            "      {products.map((p) => (\n"
            "        <div key={p.id} style={{ position: 'relative', aspectRatio: '4 / 3' }}>\n"
            "          <Image\n"
            "            src={p.imageUrl}\n"
            "            alt={p.name}\n"
            "            fill // заполняет родительский контейнер вместо width/height\n"
            "            sizes=\"(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw\"\n"
            "            style={{ objectFit: 'cover' }}\n"
            "          />\n"
            "        </div>\n"
            "      ))}\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== Локальный файл шрифта (фирменный шрифт не из Google Fonts) =====\n"
            "// app/fonts/local-font.js\n"
            "import localFont from 'next/font/local';\n"
            "\n"
            "export const brandFont = localFont({\n"
            "  src: '../../public/fonts/BrandSans.woff2',\n"
            "  display: 'swap',\n"
            "});\n"
            "\n"
            "// next.config.js — разрешение внешнего домена\n"
            "module.exports = {\n"
            "  images: {\n"
            "    remotePatterns: [{ protocol: 'https', hostname: 'cdn.example.com' }],\n"
            "  },\n"
            "};\n"
            "\n"
            "// ===================================================================\n"
            "// НЕПРАВИЛЬНЫЙ ПУТЬ: обычный <img> без размеров — вызывает layout shift\n"
            "// ===================================================================\n"
            "// <img src={course.coverUrl} alt={course.title} /> // ❌\n"
            "// Браузер не знает высоту изображения, пока оно не загрузится — контент\n"
            "// страницы «прыгает» вниз, когда картинка появляется.\n"
            "\n"
            "// ПРАВИЛЬНЫЙ ПУТЬ: всегда width/height (или fill + размер контейнера)\n"
            "// <Image src={course.coverUrl} alt={course.title} width={800} height={400} /> // ✅\n"
            "\n"
            "// ===== app/layout.js — несколько начертаний шрифта + CSS-переменная =====\n"
            "import { Inter, Roboto_Mono } from 'next/font/google';\n"
            "\n"
            "const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });\n"
            "const robotoMono = Roboto_Mono({\n"
            "  subsets: ['latin'],\n"
            "  weight: ['400', '700'],\n"
            "  variable: '--font-mono',\n"
            "});\n"
            "\n"
            "export default function RootLayout({ children }) {\n"
            "  return (\n"
            "    <html lang=\"ru\" className={`${inter.variable} ${robotoMono.variable}`}>\n"
            "      <body>{children}</body>\n"
            "    </html>\n"
            "  );\n"
            "}\n"
            "// В CSS: font-family: var(--font-inter); или var(--font-mono);\n"
            "// Оба скачиваются во время сборки — внешнего запроса нет, приватность пользователя заметно выше.\n"
            "// Это тоже часть общей темы курса: меньше работы для браузера.\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Rasm va shriftni optimallashtiring",
            "task_title_ru": "Оптимизируйте изображение и шрифт",
            "task_description": (
                "Mahsulot kartasi komponentini next/image bilan qayta yozing (width/height "
                "yoki fill bilan, hero rasm uchun priority bilan) va next/font/google orqali "
                "shrift ulang. next.config.js'da tashqi rasm domenini ruxsat bering."
            ),
            "task_description_ru": (
                "Перепишите компонент карточки товара с next/image (с width/height или fill, с "
                "priority для hero-изображения) и подключите шрифт через next/font/google. "
                "Разрешите внешний домен изображений в next.config.js."
            ),
            "task_requirements": (
                "Image komponentida width/height (yoki fill) va alt propi bo'lishi shart, "
                "next.config.js'da remotePatterns to'g'ri sozlangan bo'lishi kerak."
            ),
            "task_requirements_ru": (
                "У компонента Image должны быть width/height (или fill) и проп alt, в "
                "next.config.js должен быть корректно настроен remotePatterns."
            ),
            "task_technologies": "Next.js, next/image, next/font",
            "task_deadline_days": 4,
        },
        "sample": {
            "title": "Namuna: optimallashtirilgan mahsulot kartasi",
            "description": "next/image va next/font bilan mahsulot kartasi.",
            "sample_type": "code",
            "code_files": [
                {"filename": "app/products/[id]/ProductCard.js", "language": "jsx",
                 "code": "import Image from 'next/image';\n\nexport default function ProductCard({ product }) {\n  return (\n    <div>\n      <Image src={product.imageUrl} alt={product.name} width={400} height={300} />\n      <h3>{product.name}</h3>\n    </div>\n  );\n}\n"},
            ],
        },
        "exercises": [
            {
                "title": "Layout shift'ning oldini olish",
                "title_ru": "Предотвращение layout shift",
                "description": "next/image'da layout shift'ning oldini olish uchun qaysi proplar MAJBURIY?",
                "description_ru": "Какие пропы ОБЯЗАТЕЛЬНЫ в next/image для предотвращения layout shift?",
                "exercise_type": "multiple_choice",
                "options": ["src va alt", "width va height (yoki fill)", "priority va loading", "quality va format"],
                "options_ru": ["src и alt", "width и height (либо fill)", "priority и loading", "quality и format"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Brauzer rasm egallaydigan joyni oldindan bilishi kerak.",
                "hint_ru": "Браузер должен заранее знать, какое место займёт изображение.",
                "explanation": "width/height (yoki fill) brauzerga rasm hali yuklanmasdan turib joy ajratish imkonini beradi.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Shriftlarni joylashtirish vaqti",
                "title_ru": "Время размещения шрифтов",
                "description": (
                    "Bo'shliqni to'ldiring: next/font orqali ulangan shrift fayllari brauzerda "
                    "so'rov yuborish o'rniga ___ vaqtida yuklab olinadi."
                ),
                "description_ru": (
                    "Заполните пропуск: файлы шрифта, подключённые через next/font, вместо "
                    "запроса в браузере скачиваются во время ___."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "build",
                "hint": "Bu — kodni yig'ish jarayoni.",
                "hint_ru": "Это процесс сборки кода.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Rasm yuklash ustuvorligi",
                "title_ru": "Приоритет загрузки изображений",
                "description": (
                    "Sahifadagi rasmlarni yuklanish tartibiga ko'ra joylashtiring: birinchi "
                    "ekrandagi hero rasm (priority bilan) eng avval yuklanishi kerak."
                ),
                "description_ru": (
                    "Расставьте изображения страницы по порядку загрузки: hero-изображение на "
                    "первом экране (с priority) должно загружаться первым."
                ),
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Hero rasm (priority={true})",
                    "Sahifa o'rtasidagi rasm (lazy, ekranga yaqin)",
                    "Sahifa pastidagi rasm (lazy, hali uzoq)",
                ],
                "drag_items_ru": [
                    "Hero-изображение (priority={true})",
                    "Изображение в середине страницы (lazy, близко к экрану)",
                    "Изображение внизу страницы (lazy, ещё далеко)",
                ],
                "correct_order": [
                    "Hero rasm (priority={true})",
                    "Sahifa o'rtasidagi rasm (lazy, ekranga yaqin)",
                    "Sahifa pastidagi rasm (lazy, hali uzoq)",
                ],
                "hint": "priority bo'lgan rasm darhol, qolganlari ekranga yaqinlashganda yuklanadi.",
                "hint_ru": "Изображение с priority загружается сразу, остальные — по мере приближения к экрану.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 11,
        "title": "11-Metadata API va SEO (generateMetadata)",
        "title_ru": "11-Metadata API и SEO (generateMetadata)",
        "points_reward": 15,
        "text_content": (
            "<h3>1-darsdagi muammoga qaytamiz</h3>"
            "<p>Kursning boshida biz shu platformaning haqiqiy cheklovini ko'rgan edik: "
            "<code>frontend/public/index.html</code>da faqat bitta statik "
            "<code>&lt;title&gt;Gennis Tech&lt;/title&gt;</code> va bitta "
            "<code>&lt;meta name=\"description\"&gt;</code> bor — barcha sahifalar uchun umumiy. "
            "Metadata API — aynan shu muammoni hal qiladigan Next.js xususiyati.</p>"
            "<h3>Statik metadata: oddiy holatlar uchun</h3>"
            "<p>Har qanday <code>page.js</code> yoki <code>layout.js</code> faylida "
            "<code>export const metadata = {...}</code> obyektini e'lon qilish mumkin — u "
            "<code>title</code>, <code>description</code>, <code>openGraph</code> (ijtimoiy "
            "tarmoqlarda ulashilganda ko'rinadigan rasm/sarlavha) kabi maydonlarni o'z ichiga "
            "oladi. Bu — o'zgarmas, oldindan ma'lum sahifalar (masalan, \"Biz haqimizda\") "
            "uchun mos.</p>"
            "<h3>Title Template: ota-bola sarlavha merosxo'rligi</h3>"
            "<p>Root layout'da <code>title: { template: '%s | Kurslar platformasi', default: "
            "'Kurslar platformasi' }</code> kabi shablon belgilash mumkin. Ichki sahifa faqat "
            "<code>title: 'React Asoslari'</code> deb yozsa, natijaviy brauzer tab sarlavhasi "
            "avtomatik <code>\"React Asoslari | Kurslar platformasi\"</code> bo'ladi — har bir "
            "ichki sahifa butun shablonni qayta yozishi shart emas.</p>"
            "<h3>Dinamik metadata: generateMetadata</h3>"
            "<p>Aynan mana shu — 1-darsdagi muammoni to'g'ridan-to'g'ri hal qiladigan qism: "
            "<code>generateMetadata({ params })</code> — bu <code>async</code> funksiya bo'lib, "
            "u sahifa uchun kerakli ma'lumotni (masalan, kurs nomini) fetch qilib, o'sha "
            "ma'lumot asosida <strong>har bir sahifa uchun individual</strong> sarlavha va "
            "tavsif qaytaradi. Natijada <code>/courses/43</code> sahifasi "
            "\"React Asoslari | Kurslar platformasi\" sarlavhasini, <code>/courses/72</code> esa "
            "\"Redux Toolkit... | Kurslar platformasi\" sarlavhasini oladi — CRA'dagi kabi "
            "hammasi uchun bitta umumiy sarlavha emas.</p>"
            "<p>Muhim afzallik: bu metadata SERVERDA render qilinadi va HTML'ning "
            "<code>&lt;head&gt;</code> qismida ALLAQACHON tayyor holda keladi — 1-darsda "
            "aytilganidek, qidiruv botlari JS ishga tushishini kutmasdan uni darhol o'qiy oladi.</p>"
            "<h3>Metadata Files: robots.js va sitemap.js</h3>"
            "<p>Metadata API'ning yana bir qismi — maxsus fayl konvensiyalari: <code>app/robots.js</code> "
            "qidiruv botlari uchun qaysi sahifalarni indekslash mumkinligini belgilaydi, "
            "<code>app/sitemap.js</code> esa saytdagi barcha muhim URL'lar ro'yxatini "
            "generatsiya qiladi — ikkalasi ham oddiy JavaScript funksiyasi sifatida yoziladi, "
            "qo'lda statik <code>robots.txt</code>/<code>sitemap.xml</code> fayl yozishga hojat "
            "qoldirmaydi.</p>"
            "<h3>Diagram: metadata merosxo'rligi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  R[\"app/layout.js\n"
            "title.template: '%s | Kurslar platformasi'\"] --> P1[\"app/courses/[id]/page.js\n"
            "generateMetadata -> 'React Asoslari'\"]\n"
            "  R --> P2[\"app/about/page.js\n"
            "metadata.title = 'Biz haqimizda'\"]\n"
            "  P1 --> T1[\"Natija: 'React Asoslari | Kurslar platformasi'\"]\n"
            "  P2 --> T2[\"Natija: 'Biz haqimizda | Kurslar platformasi'\"]\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: root layout shablonni belgilaydi, har bir ichki "
            "sahifa esa faqat o'ziga xos qismini beradi — natija avtomatik birlashadi.</p>"
            "<h3>openGraph va ijtimoiy tarmoqlarda ko'rinish</h3>"
            "<p><code>metadata.openGraph</code> maydoni — havola Telegram, Twitter yoki "
            "Facebook'da ulashilganda ko'rinadigan katta rasmli \"karta\"ni belgilaydi (sarlavha, "
            "tavsif, rasm). Bu — CRA'da <code>react-helmet</code> orqali qo'lda amalga "
            "oshiriladigan, va hatto shunda ham ijtimoiy tarmoq bot'lari ko'pincha JS'ni "
            "bajarmasdan sahifani skanerlaganligi sabab noto'g'ri ishlashi mumkin bo'lgan "
            "narsa — Next.js'da esa bu HTML'ning o'zida, server tomonda tayyor keladi.</p>"
            "<h3>canonical URL: dublikat kontent muammosi</h3>"
            "<p>Ba'zan bitta kontentga bir nechta URL orqali kirish mumkin (masalan, "
            "<code>?ref=email</code> kabi kuzatuv parametri qo'shilgan yoki qo'shilmagan "
            "holda). <code>metadata.alternates.canonical</code> orqali qidiruv tizimlariga shu "
            "kontentning asosiy, rasmiy manzili qaysi ekanini aniq ko'rsatish mumkin — bu "
            "qidiruv reytingini bir nechta URL orasida bo'linib ketishining oldini oladi.</p>"
            "<p>Xulosa: Metadata API — bu 1-darsdan boshlangan hikoyaning yakuni. CRA'da bitta "
            "statik <code>index.html</code>dan boshlab, endi biz har bir sahifaning o'z "
            "haqiqiy, server tomonda tayyorlangan SEO ma'lumotiga ega bo'lishini ta'minlaydigan "
            "to'liq vositalar to'plamiga ega bo'ldik.</p>"
        ),
        "text_content_ru": (
            "<h3>Возвращаемся к проблеме из урока 1</h3>"
            "<p>В начале курса мы видели реальное ограничение этой платформы: в "
            "<code>frontend/public/index.html</code> есть только один статичный "
            "<code>&lt;title&gt;Gennis Tech&lt;/title&gt;</code> и один "
            "<code>&lt;meta name=\"description\"&gt;</code> — общие для всех страниц. Metadata "
            "API — это именно та особенность Next.js, которая решает эту проблему.</p>"
            "<h3>Статичные метаданные: для простых случаев</h3>"
            "<p>В любом файле <code>page.js</code> или <code>layout.js</code> можно объявить "
            "объект <code>export const metadata = {...}</code> — он включает поля вроде "
            "<code>title</code>, <code>description</code>, <code>openGraph</code> "
            "(изображение/заголовок, видимые при публикации в соцсетях). Это подходит для "
            "неизменных, заранее известных страниц (например, «О нас»).</p>"
            "<h3>Title Template: наследование заголовка родитель-потомок</h3>"
            "<p>В корневом layout можно задать шаблон вроде "
            "<code>title: { template: '%s | Платформа курсов', default: 'Платформа курсов' }</code>. "
            "Если вложенная страница просто напишет <code>title: 'Основы React'</code>, "
            "итоговый заголовок вкладки браузера автоматически станет "
            "<code>«Основы React | Платформа курсов»</code> — каждой вложенной странице не "
            "нужно переписывать весь шаблон заново.</p>"
            "<h3>Динамические метаданные: generateMetadata</h3>"
            "<p>Именно эта часть напрямую решает проблему из урока 1: "
            "<code>generateMetadata({ params })</code> — это <code>async</code>-функция, "
            "которая получает нужные для страницы данные (например, название курса) и на их "
            "основе возвращает <strong>индивидуальные для каждой страницы</strong> заголовок и "
            "описание. В результате страница <code>/courses/43</code> получает заголовок "
            "«Основы React | Платформа курсов», а <code>/courses/72</code> — «Redux Toolkit... "
            "| Платформа курсов» — а не один общий заголовок для всех, как в CRA.</p>"
            "<p>Важное преимущество: эти метаданные рендерятся НА СЕРВЕРЕ и приходят УЖЕ "
            "готовыми в <code>&lt;head&gt;</code> HTML — как говорилось в уроке 1, поисковые "
            "боты могут прочитать их немедленно, не дожидаясь запуска JS.</p>"
            "<h3>Metadata Files: robots.js и sitemap.js</h3>"
            "<p>Ещё одна часть Metadata API — специальные файловые конвенции: "
            "<code>app/robots.js</code> определяет, какие страницы можно индексировать "
            "поисковым ботам, а <code>app/sitemap.js</code> генерирует список всех важных URL "
            "сайта — оба пишутся как обычная функция JavaScript, избавляя от необходимости "
            "вручную писать статичные файлы <code>robots.txt</code>/<code>sitemap.xml</code>.</p>"
            "<h3>Диаграмма: наследование метаданных</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  R[\"app/layout.js\n"
            "title.template: '%s | Платформа курсов'\"] --> P1[\"app/courses/[id]/page.js\n"
            "generateMetadata -> 'Основы React'\"]\n"
            "  R --> P2[\"app/about/page.js\n"
            "metadata.title = 'О нас'\"]\n"
            "  P1 --> T1[\"Результат: 'Основы React | Платформа курсов'\"]\n"
            "  P2 --> T2[\"Результат: 'О нас | Платформа курсов'\"]\n"
            "</pre>"
            "<p>Диаграмма показывает: корневой layout задаёт шаблон, а каждая вложенная "
            "страница даёт только свою уникальную часть — результат объединяется "
            "автоматически.</p>"
            "<h3>openGraph и отображение в соцсетях</h3>"
            "<p>Поле <code>metadata.openGraph</code> определяет большую «карточку» с "
            "изображением, которая видна при публикации ссылки в Telegram, Twitter или "
            "Facebook (заголовок, описание, изображение). Это то, что в CRA делается вручную "
            "через <code>react-helmet</code>, и даже тогда может работать некорректно, потому "
            "что боты соцсетей часто сканируют страницу, не выполняя JS — в Next.js же это "
            "приходит готовым прямо в HTML, отрендеренное на сервере.</p>"
            "<h3>canonical URL: проблема дублирующегося контента</h3>"
            "<p>Иногда к одному и тому же контенту можно попасть по нескольким URL (например, "
            "с параметром отслеживания вроде <code>?ref=email</code> или без него). Через "
            "<code>metadata.alternates.canonical</code> можно явно указать поисковым системам, "
            "какой адрес этого контента основной, официальный — это предотвращает "
            "«размытие» поискового рейтинга между несколькими URL.</p>"
            "<p>Итог: Metadata API — это завершение истории, начатой в уроке 1. От одного "
            "статичного <code>index.html</code> в CRA мы пришли к полному набору инструментов, "
            "гарантирующих, что у каждой страницы есть собственные, настоящие, отрендеренные на "
            "сервере SEO-данные, а не одинаковые для всего сайта мета-теги.</p>"
        ),
        "code_content": (
            "// ===== app/layout.js — shablon =====\n"
            "export const metadata = {\n"
            "  title: {\n"
            "    template: '%s | Kurslar platformasi',\n"
            "    default: 'Kurslar platformasi',\n"
            "  },\n"
            "  description: \"IT ta'lim platformasi\",\n"
            "};\n"
            "\n"
            "// ===== XATO YO'L: statik metadata dinamik sahifada =====\n"
            "// export const metadata = { title: 'Kurs' }; // ❌ har bir kurs uchun bir xil!\n"
            "\n"
            "// ===== TO'G'RI YO'L: app/courses/[id]/page.js — dinamik metadata =====\n"
            "import { notFound } from 'next/navigation';\n"
            "\n"
            "export async function generateMetadata({ params }) {\n"
            "  const { id } = await params;\n"
            "  const res = await fetch(`https://api.example.com/courses/${id}`);\n"
            "  if (res.status === 404) return { title: 'Kurs topilmadi' };\n"
            "  const course = await res.json();\n"
            "\n"
            "  return {\n"
            "    title: course.title, // -> \"Kurs nomi | Kurslar platformasi\" (shablon orqali)\n"
            "    description: course.description,\n"
            "    alternates: {\n"
            "      canonical: `https://example.com/courses/${id}`, // dublikat URL muammosi\n"
            "    },\n"
            "    openGraph: {\n"
            "      title: course.title,\n"
            "      description: course.description,\n"
            "      images: [course.coverUrl],\n"
            "      type: 'article',\n"
            "    },\n"
            "  };\n"
            "}\n"
            "\n"
            "export default async function CoursePage({ params }) {\n"
            "  const { id } = await params;\n"
            "  const res = await fetch(`https://api.example.com/courses/${id}`);\n"
            "  if (res.status === 404) notFound();\n"
            "  const course = await res.json();\n"
            "  return <h1>{course.title}</h1>;\n"
            "}\n"
            "\n"
            "// ===== app/sitemap.js =====\n"
            "export default async function sitemap() {\n"
            "  const courses = await fetch('https://api.example.com/courses').then((r) => r.json());\n"
            "  return [\n"
            "    { url: 'https://example.com', lastModified: new Date() },\n"
            "    ...courses.map((c) => ({\n"
            "      url: `https://example.com/courses/${c.id}`,\n"
            "      lastModified: new Date(),\n"
            "    })),\n"
            "  ];\n"
            "}\n"
            "\n"
            "// ===== app/robots.js =====\n"
            "export default function robots() {\n"
            "  return {\n"
            "    rules: {\n"
            "      userAgent: '*',\n"
            "      allow: '/',\n"
            "      disallow: ['/admin', '/api'], // botlar bularni indekslamasin\n"
            "    },\n"
            "    sitemap: 'https://example.com/sitemap.xml',\n"
            "  };\n"
            "}\n"
            "\n"
            "// ===== Ota metadata bilan birlashtirish (parent parametri) =====\n"
            "// generateMetadata ikkinchi argument sifatida `parent`ni oladi — bu orqali\n"
            "// ota layout/sahifaning metadatasini o'qib, unga QO'SHIMCHA qilish mumkin\n"
            "export async function generateMetadataWithParent({ params }, parent) {\n"
            "  const { id } = await params;\n"
            "  const course = await fetch(`https://api.example.com/courses/${id}`).then((r) => r.json());\n"
            "  const parentImages = (await parent).openGraph?.images || [];\n"
            "\n"
            "  return {\n"
            "    title: course.title,\n"
            "    openGraph: {\n"
            "      images: [course.coverUrl, ...parentImages], // o'zinikini ota rasmlari bilan qo'shadi\n"
            "    },\n"
            "    twitter: {\n"
            "      card: 'summary_large_image',\n"
            "      title: course.title,\n"
            "      images: [course.coverUrl],\n"
            "    },\n"
            "  };\n"
            "}\n"
            "// Bu naqsh Metadata API'ning boshqa maxsus fayllar bilan (robots.js,\n"
            "// sitemap.js) birgalikda bitta yaxlit SEO strategiyasini tashkil qilishini\n"
            "// ko'rsatadi — barchasi oddiy JavaScript funksiyalari sifatida yoziladi, hech\n"
            "// qanday maxsus konfiguratsiya fayli kerak emas.\n"
        ),
        "code_content_ru": (
            "// ===== app/layout.js — шаблон =====\n"
            "export const metadata = {\n"
            "  title: {\n"
            "    template: '%s | Платформа курсов',\n"
            "    default: 'Платформа курсов',\n"
            "  },\n"
            "  description: 'IT образовательная платформа',\n"
            "};\n"
            "\n"
            "// ===== НЕПРАВИЛЬНЫЙ ПУТЬ: статичные метаданные на динамической странице =====\n"
            "// export const metadata = { title: 'Курс' }; // ❌ одинаково для каждого курса!\n"
            "\n"
            "// ===== ПРАВИЛЬНЫЙ ПУТЬ: app/courses/[id]/page.js — динамические метаданные =====\n"
            "import { notFound } from 'next/navigation';\n"
            "\n"
            "export async function generateMetadata({ params }) {\n"
            "  const { id } = await params;\n"
            "  const res = await fetch(`https://api.example.com/courses/${id}`);\n"
            "  if (res.status === 404) return { title: 'Курс не найден' };\n"
            "  const course = await res.json();\n"
            "\n"
            "  return {\n"
            "    title: course.title, // -> «Название курса | Платформа курсов» (через шаблон)\n"
            "    description: course.description,\n"
            "    alternates: {\n"
            "      canonical: `https://example.com/courses/${id}`, // проблема дублей URL\n"
            "    },\n"
            "    openGraph: {\n"
            "      title: course.title,\n"
            "      description: course.description,\n"
            "      images: [course.coverUrl],\n"
            "      type: 'article',\n"
            "    },\n"
            "  };\n"
            "}\n"
            "\n"
            "export default async function CoursePage({ params }) {\n"
            "  const { id } = await params;\n"
            "  const res = await fetch(`https://api.example.com/courses/${id}`);\n"
            "  if (res.status === 404) notFound();\n"
            "  const course = await res.json();\n"
            "  return <h1>{course.title}</h1>;\n"
            "}\n"
            "\n"
            "// ===== app/sitemap.js =====\n"
            "export default async function sitemap() {\n"
            "  const courses = await fetch('https://api.example.com/courses').then((r) => r.json());\n"
            "  return [\n"
            "    { url: 'https://example.com', lastModified: new Date() },\n"
            "    ...courses.map((c) => ({\n"
            "      url: `https://example.com/courses/${c.id}`,\n"
            "      lastModified: new Date(),\n"
            "    })),\n"
            "  ];\n"
            "}\n"
            "\n"
            "// ===== app/robots.js =====\n"
            "export default function robots() {\n"
            "  return {\n"
            "    rules: {\n"
            "      userAgent: '*',\n"
            "      allow: '/',\n"
            "      disallow: ['/admin', '/api'], // ботам сюда нельзя\n"
            "    },\n"
            "    sitemap: 'https://example.com/sitemap.xml',\n"
            "  };\n"
            "}\n"
            "\n"
            "// ===== Объединение с родительскими метаданными (параметр parent) =====\n"
            "// generateMetadata принимает вторым аргументом `parent` — через него можно\n"
            "// прочитать метаданные родительского layout/страницы и ДОПОЛНИТЬ их\n"
            "export async function generateMetadataWithParent({ params }, parent) {\n"
            "  const { id } = await params;\n"
            "  const course = await fetch(`https://api.example.com/courses/${id}`).then((r) => r.json());\n"
            "  const parentImages = (await parent).openGraph?.images || [];\n"
            "\n"
            "  return {\n"
            "    title: course.title,\n"
            "    openGraph: {\n"
            "      images: [course.coverUrl, ...parentImages], // свои + родительские изображения\n"
            "    },\n"
            "    twitter: {\n"
            "      card: 'summary_large_image',\n"
            "      title: course.title,\n"
            "      images: [course.coverUrl],\n"
            "    },\n"
            "  };\n"
            "}\n"
            "// Этот паттерн показывает, как Metadata API вместе с другими специальными\n"
            "// файлами (robots.js, sitemap.js) образует единую цельную SEO-стратегию —\n"
            "// всё пишется как обычные функции JavaScript, без специальных файлов\n"
            "// конфигурации и без стороннего SEO-пакета.\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Dinamik SEO metadata yarating",
            "task_title_ru": "Создайте динамические SEO-метаданные",
            "task_description": (
                "app/blog/[slug]/page.js sahifasi uchun generateMetadata funksiyasini yozing — "
                "post ma'lumotini fetch qilib, uning haqiqiy sarlavhasi va tavsifini "
                "qaytaring. Root layout'da title template ham belgilang."
            ),
            "task_description_ru": (
                "Напишите функцию generateMetadata для страницы app/blog/[slug]/page.js — "
                "получите данные поста и верните его настоящий заголовок и описание. Также "
                "задайте title template в корневом layout."
            ),
            "task_requirements": (
                "generateMetadata async funksiya bo'lishi, fetch orqali real ma'lumot olishi va "
                "title/description qaytarishi shart. Root layout'da title.template bo'lishi kerak."
            ),
            "task_requirements_ru": (
                "generateMetadata должна быть async-функцией, получать реальные данные через "
                "fetch и возвращать title/description. В корневом layout должен быть "
                "title.template."
            ),
            "task_technologies": "Next.js, Metadata API, SEO",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: dinamik SEO metadata",
            "description": "Blog posti uchun generateMetadata namunasi.",
            "sample_type": "code",
            "code_files": [
                {"filename": "app/blog/[slug]/page.js", "language": "jsx",
                 "code": "export async function generateMetadata({ params }) {\n  const { slug } = await params;\n  const post = await fetch(`https://api.example.com/posts/${slug}`).then((r) => r.json());\n  return { title: post.title, description: post.excerpt };\n}\n\nexport default async function PostPage({ params }) {\n  const { slug } = await params;\n  const post = await fetch(`https://api.example.com/posts/${slug}`).then((r) => r.json());\n  return <article><h1>{post.title}</h1></article>;\n}\n"},
            ],
        },
        "exercises": [
            {
                "title": "1-darsdagi muammoni hal qilish",
                "title_ru": "Решение проблемы из урока 1",
                "description": (
                    "Har bir sahifa uchun alohida, ma'lumotga asoslangan sarlavha yaratish "
                    "uchun qaysi funksiya ishlatiladi?"
                ),
                "description_ru": (
                    "Какая функция используется для создания индивидуального, основанного на "
                    "данных заголовка для каждой страницы?"
                ),
                "exercise_type": "multiple_choice",
                "options": ["export const metadata", "generateMetadata", "useMetadata", "next/head"],
                "options_ru": ["export const metadata", "generateMetadata", "useMetadata", "next/head"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Bu — async funksiya, statik obyekt emas.",
                "hint_ru": "Это async-функция, а не статичный объект.",
                "explanation": "generateMetadata ma'lumotni fetch qilib, shunga mos individual metadata qaytaradi.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Sitemap generatsiya qilish fayli",
                "title_ru": "Файл генерации sitemap",
                "description": (
                    "Bo'shliqni to'ldiring: saytdagi barcha URL'lar ro'yxatini avtomatik "
                    "generatsiya qilish uchun app/ ildizida ___.js fayli yoziladi."
                ),
                "description_ru": (
                    "Заполните пропуск: для автоматической генерации списка всех URL сайта в "
                    "корне app/ пишется файл ___.js."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "sitemap.js",
                "hint": "robots.js emas — bu URL ro'yxati uchun.",
                "hint_ru": "Не robots.js — это для списка URL.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Title Template oqimi",
                "title_ru": "Поток Title Template",
                "description": (
                    "Root layout'da title.template = '%s | Kurslar platformasi' bo'lganda, "
                    "'React Asoslari' sahifasi uchun sarlavha qanday hosil bo'lish qadamlarini "
                    "tartibga joylashtiring."
                ),
                "description_ru": (
                    "Если в корневом layout title.template = '%s | Платформа курсов', "
                    "расставьте по порядку шаги формирования заголовка для страницы 'Основы "
                    "React'."
                ),
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Sahifa title: 'React Asoslari' deb belgilaydi",
                    "Next.js root layout'dagi shablonni topadi",
                    "%s o'rniga 'React Asoslari' qo'yiladi",
                    "Yakuniy: 'React Asoslari | Kurslar platformasi'",
                ],
                "drag_items_ru": [
                    "Страница задаёт title: 'Основы React'",
                    "Next.js находит шаблон в корневом layout",
                    "%s заменяется на 'Основы React'",
                    "Итог: 'Основы React | Платформа курсов'",
                ],
                "correct_order": [
                    "Sahifa title: 'React Asoslari' deb belgilaydi",
                    "Next.js root layout'dagi shablonni topadi",
                    "%s o'rniga 'React Asoslari' qo'yiladi",
                    "Yakuniy: 'React Asoslari | Kurslar platformasi'",
                ],
                "hint": "Ichki sahifa faqat o'z qismini beradi, shablon esa tashqarida.",
                "hint_ru": "Вложенная страница даёт только свою часть, шаблон — снаружи.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 12,
        "title": "R2-Mini-capstone: mahsulotlar katalogi + Deploy asoslari (takrorlash)",
        "title_ru": "R2-Мини-капстоун: каталог товаров + основы деплоя (повторение)",
        "points_reward": 20,
        "text_content": (
            "<h3>Bu — takrorlash darsi</h3>"
            "<p>Bu dars ham amaliy takrorlash bo'lgani uchun matn qisqaroq — yangi nazariy "
            "tushuncha berilmaydi, faqat ikkita narsa birlashtiriladi: 5-8-darslarda "
            "o'rganilgan ma'lumot olish/render strategiyalari/dinamik marshrutlarni bitta "
            "mahsulotlar katalogida mustahkamlash, va deploy haqida qisqa, amaliy tushuncha "
            "berish.</p>"
            "<h3>Mini-capstone: mahsulotlar katalogi</h3>"
            "<p>Vazifa — <code>app/products/page.js</code> (ISR bilan katalog ro'yxati), "
            "<code>app/products/[id]/page.js</code> (generateStaticParams bilan mahsulot "
            "tafsilotlari) va <code>app/api/products/route.js</code> (qidiruv uchun Route "
            "Handler, Client Component'dagi qidiruv maydonidan chaqiriladi) — uchtasini "
            "birlashtirish.</p>"
            "<h3>Deploy: bu CRA'ni deploy qilishdan nimasi bilan farq qiladi</h3>"
            "<p>Shu platformaning CRA frontend'i <code>npm run build</code>dan keyin faqat "
            "STATIK fayllar (HTML/CSS/JS) chiqaradi — ularni istalgan statik fayl serveri "
            "(nginx, Vercel, Netlify, hatto oddiy S3 bucket) xizmat qila oladi, chunki hech "
            "qanday server-tomon kodi yo'q. Next.js ilovasi esa, agar u Server Component, "
            "Route Handler yoki Middleware ishlatsa, deploy qilinadigan joy albatta Node.js "
            "jarayonini ISHGA TUSHIRA olishi kerak — bu faqat statik fayl xizmatidan tubdan "
            "farqli talab.</p>"
            "<p>Vercel (Next.js'ni yaratgan kompaniya) — bu freymvork uchun \"nol "
            "konfiguratsiyali\" deploy tajribasini beradi: ISR, Route Handler, Middleware "
            "avtomatik ishlaydi. Lekin Next.js o'z-o'zini boshqarish (self-hosting) uchun ham "
            "to'liq imkoniyat beradi: <code>next start</code> buyrug'i orqali oddiy Node.js "
            "serveri sifatida ishga tushirish, yoki <code>output: 'standalone'</code> sozlamasi "
            "orqali minimal, mustaqil Docker image yasash mumkin.</p>"
            "<p>Environment o'zgaruvchilar haqida ham muhim farq bor: CRA'da mijozga "
            "ochiladigan o'zgaruvchilar <code>REACT_APP_</code> prefiksi bilan boshlanadi, "
            "Next.js'da esa xuddi shu maqsad uchun <code>NEXT_PUBLIC_</code> prefiksi "
            "ishlatiladi — prefikssiz o'zgaruvchilar esa faqat serverda (Server Component, "
            "Route Handler, Middleware ichida) ko'rinadi, brauzerga hech qachon chiqmaydi.</p>"
        ),
        "text_content_ru": (
            "<h3>Это урок повторения</h3>"
            "<p>Этот урок тоже практический урок повторения, поэтому текст короче — новая "
            "теория не даётся, объединяются две вещи: закрепление изученных в уроках 5-8 "
            "получения данных / стратегий рендеринга / динамических маршрутов на одном каталоге "
            "товаров, и краткое, практическое понимание деплоя.</p>"
            "<h3>Мини-капстоун: каталог товаров</h3>"
            "<p>Задача — объединить три части: <code>app/products/page.js</code> (список "
            "каталога с ISR), <code>app/products/[id]/page.js</code> (детали товара с "
            "generateStaticParams) и <code>app/api/products/route.js</code> (Route Handler для "
            "поиска, вызываемый из поля поиска в Client Component).</p>"
            "<h3>Деплой: чем отличается от деплоя CRA</h3>"
            "<p>Фронтенд CRA этой платформы после <code>npm run build</code> выдаёт только "
            "СТАТИЧНЫЕ файлы (HTML/CSS/JS) — их может обслуживать любой статичный файловый "
            "сервер (nginx, Vercel, Netlify, даже простой S3 bucket), потому что серверного кода "
            "вообще нет. Next.js-приложение же, если использует Server Component, Route "
            "Handler или Middleware, обязательно требует, чтобы место деплоя могло ЗАПУСТИТЬ "
            "процесс Node.js — это принципиально другое требование, отличное от простого "
            "обслуживания статичных файлов.</p>"
            "<p>Vercel (компания, создавшая Next.js) предоставляет опыт деплоя «без "
            "конфигурации» для этого фреймворка: ISR, Route Handler, Middleware работают "
            "автоматически. Но Next.js также полностью поддерживает самостоятельный хостинг "
            "(self-hosting): запуск как обычный Node.js-сервер через команду "
            "<code>next start</code>, либо создание минимального, автономного Docker-образа "
            "через настройку <code>output: 'standalone'</code>.</p>"
            "<p>Есть важная разница и в переменных окружения: в CRA переменные, открытые "
            "клиенту, начинаются с префикса <code>REACT_APP_</code>, в Next.js для той же цели "
            "используется префикс <code>NEXT_PUBLIC_</code> — переменные без префикса видны "
            "только на сервере (внутри Server Component, Route Handler, Middleware) и никогда "
            "не попадают в браузер.</p>"
        ),
        "code_content": (
            "// app/products/page.js — ISR (300 soniyada bir yangilanadi)\n"
            "export default async function ProductsPage() {\n"
            "  const products = await fetch('https://api.example.com/products', {\n"
            "    next: { revalidate: 300 },\n"
            "  }).then((r) => r.json());\n"
            "  return <ul>{products.map((p) => <li key={p.id}>{p.name}</li>)}</ul>;\n"
            "}\n"
            "\n"
            "// app/products/[id]/page.js — SSG + generateStaticParams\n"
            "export async function generateStaticParams() {\n"
            "  const products = await fetch('https://api.example.com/products').then((r) => r.json());\n"
            "  return products.map((p) => ({ id: String(p.id) }));\n"
            "}\n"
            "\n"
            "export default async function ProductPage({ params }) {\n"
            "  const { id } = await params;\n"
            "  const product = await fetch(`https://api.example.com/products/${id}`).then((r) => r.json());\n"
            "  return <h1>{product.name}</h1>;\n"
            "}\n"
            "\n"
            "// .env.local\n"
            "// NEXT_PUBLIC_SITE_NAME=Kurslar platformasi   <- brauzerga chiqadi\n"
            "// DATABASE_URL=postgres://...                <- faqat serverda\n"
        ),
        "code_content_ru": (
            "// app/products/page.js — ISR (обновляется раз в 300 секунд)\n"
            "export default async function ProductsPage() {\n"
            "  const products = await fetch('https://api.example.com/products', {\n"
            "    next: { revalidate: 300 },\n"
            "  }).then((r) => r.json());\n"
            "  return <ul>{products.map((p) => <li key={p.id}>{p.name}</li>)}</ul>;\n"
            "}\n"
            "\n"
            "// app/products/[id]/page.js — SSG + generateStaticParams\n"
            "export async function generateStaticParams() {\n"
            "  const products = await fetch('https://api.example.com/products').then((r) => r.json());\n"
            "  return products.map((p) => ({ id: String(p.id) }));\n"
            "}\n"
            "\n"
            "export default async function ProductPage({ params }) {\n"
            "  const { id } = await params;\n"
            "  const product = await fetch(`https://api.example.com/products/${id}`).then((r) => r.json());\n"
            "  return <h1>{product.name}</h1>;\n"
            "}\n"
            "\n"
            "// .env.local\n"
            "// NEXT_PUBLIC_SITE_NAME=Платформа курсов   <- попадает в браузер\n"
            "// DATABASE_URL=postgres://...              <- только на сервере\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Mahsulotlar katalogini yig'ing va deploy rejasini yozing",
            "task_title_ru": "Соберите каталог товаров и напишите план деплоя",
            "task_description": (
                "app/products/page.js (ISR), app/products/[id]/page.js (SSG + "
                "generateStaticParams) va app/api/products/route.js (qidiruv) fayllarini "
                "yozing. Keyin qisqa deploy rejasi tayyorlang: Vercel orqalimi yoki self-"
                "hosting orqalimi, va nima uchun."
            ),
            "task_description_ru": (
                "Напишите файлы app/products/page.js (ISR), app/products/[id]/page.js (SSG + "
                "generateStaticParams) и app/api/products/route.js (поиск). Затем подготовьте "
                "краткий план деплоя: через Vercel или self-hosting, и почему."
            ),
            "task_requirements": (
                "Uchala fayl ham ishlashi, deploy rejasida environment o'zgaruvchilar "
                "(NEXT_PUBLIC_ vs server-only) aniq ajratilgan bo'lishi shart."
            ),
            "task_requirements_ru": (
                "Все три файла должны работать, в плане деплоя должны быть чётко разделены "
                "переменные окружения (NEXT_PUBLIC_ vs только сервер)."
            ),
            "task_technologies": "Next.js, ISR, SSG, Route Handlers, Deploy",
            "task_deadline_days": 6,
        },
        "sample": {
            "title": "Namuna: mahsulotlar katalogi to'liq",
            "description": "ISR ro'yxat, SSG tafsilot va qidiruv Route Handler birgalikda.",
            "sample_type": "code",
            "code_files": [
                {"filename": "app/products/page.js", "language": "jsx",
                 "code": "export default async function ProductsPage() {\n  const products = await fetch('https://api.example.com/products', { next: { revalidate: 300 } }).then((r) => r.json());\n  return <ul>{products.map((p) => <li key={p.id}>{p.name}</li>)}</ul>;\n}\n"},
                {"filename": "app/api/products/route.js", "language": "javascript",
                 "code": "import { NextResponse } from 'next/server';\n\nexport async function GET(request) {\n  const q = request.nextUrl.searchParams.get('q') || '';\n  const products = await fetch('https://api.example.com/products').then((r) => r.json());\n  const filtered = products.filter((p) => p.name.toLowerCase().includes(q.toLowerCase()));\n  return NextResponse.json(filtered);\n}\n"},
            ],
        },
        "exercises": [
            {
                "title": "Deploy talabi",
                "title_ru": "Требование к деплою",
                "description": (
                    "Server Component va Route Handler ishlatadigan Next.js ilovasini deploy "
                    "qilish uchun nima zarur?"
                ),
                "description_ru": (
                    "Что необходимо для деплоя Next.js-приложения, использующего Server "
                    "Component и Route Handler?"
                ),
                "exercise_type": "multiple_choice",
                "options": [
                    "Faqat statik fayl serveri (nginx, S3) yetarli",
                    "Node.js jarayonini ishga tushira oladigan muhit kerak",
                    "Hech qanday server kerak emas, hammasi brauzerda ishlaydi",
                    "Faqat Vercel'da ishlaydi, boshqa joyda umuman bo'lmaydi",
                ],
                "options_ru": [
                    "Достаточно только статичного файлового сервера (nginx, S3)",
                    "Нужна среда, способная запустить процесс Node.js",
                    "Сервер вообще не нужен, всё работает в браузере",
                    "Работает только на Vercel, больше нигде",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "CRA'dan farqli o'laroq, bu yerda server-tomon kodi bor.",
                "hint_ru": "В отличие от CRA, здесь есть серверный код.",
                "explanation": "Server Component/Route Handler/Middleware server tomonda ishlaydi, shuning uchun Node.js muhiti zarur.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Brauzerga ochiladigan environment o'zgaruvchi",
                "title_ru": "Переменная окружения, открытая браузеру",
                "description": (
                    "Bo'shliqni to'ldiring: Next.js'da brauzerga ochiladigan environment "
                    "o'zgaruvchilar ___ prefiksi bilan boshlanishi kerak."
                ),
                "description_ru": (
                    "Заполните пропуск: в Next.js переменные окружения, открытые браузеру, "
                    "должны начинаться с префикса ___."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "NEXT_PUBLIC_",
                "hint": "CRA'dagi REACT_APP_ prefiksining Next.js versiyasi.",
                "hint_ru": "Версия для Next.js аналога REACT_APP_ из CRA.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Katalog qurish qadamlari",
                "title_ru": "Шаги построения каталога",
                "description": "Mahsulotlar katalogini qurish qadamlarini mantiqiy tartibga joylashtiring.",
                "description_ru": "Расставьте шаги построения каталога товаров в логическом порядке.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "generateStaticParams barcha mahsulot ID'larini qaytaradi",
                    "Har bir ID uchun build vaqtida statik sahifa tayyorlanadi",
                    "Route Handler qidiruv so'rovlariga JSON bilan javob beradi",
                    "Client Component qidiruv natijasini ko'rsatadi",
                ],
                "drag_items_ru": [
                    "generateStaticParams возвращает все ID товаров",
                    "Для каждого ID во время сборки готовится статичная страница",
                    "Route Handler отвечает JSON на запросы поиска",
                    "Client Component показывает результат поиска",
                ],
                "correct_order": [
                    "generateStaticParams barcha mahsulot ID'larini qaytaradi",
                    "Har bir ID uchun build vaqtida statik sahifa tayyorlanadi",
                    "Route Handler qidiruv so'rovlariga JSON bilan javob beradi",
                    "Client Component qidiruv natijasini ko'rsatadi",
                ],
                "hint": "Build vaqtidagi qadamlar avval, so'rov vaqtidagi qadamlar keyin.",
                "hint_ru": "Сначала шаги времени сборки, потом шаги времени запроса.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 13,
        "title": "12-CAPSTONE: To'liq stack Next.js ilova (blog/katalog)",
        "title_ru": "12-КАПСТОУН: Полноценное Next.js-приложение (блог/каталог)",
        "points_reward": 30,
        "text_content": (
            "<h3>Kursning yakuni: hammasi bir joyda</h3>"
            "<p>Ushbu kursda biz 1-darsdan boshlab bitta hikoyani qurib keldik: shu "
            "platformaning haqiqiy CRA cheklovlaridan (bo'sh <code>div#root</code>, bitta "
            "statik meta teg, mijoz-tomon marshrutlash) boshlab, Next.js ularni qanday hal "
            "qilishini — App Router, Server/Client Component'lar, ma'lumot olish strategiyalari, "
            "SSR/SSG/ISR, Route Handler'lar, dinamik marshrutlar, Middleware, media "
            "optimizatsiyasi, Metadata API — birma-bir ko'rdik. Capstone loyihasi — shularning "
            "barchasini bitta kichik, lekin haqiqiy ishlaydigan ilovada birlashtirish.</p>"
            "<h3>Loyiha: mini-blog platformasi</h3>"
            "<p>Quyidagi arxitekturaga ega kichik blog ilovasini quramiz:</p>"
            "<ul>"
            "<li><code>app/page.js</code> — bosh sahifa, so'nggi postlarni ko'rsatadi (SSG, "
            "chunki barcha foydalanuvchilar uchun bir xil).</li>"
            "<li><code>app/blog/[slug]/page.js</code> — bitta post, "
            "<code>generateStaticParams</code> orqali barcha mavjud postlar uchun oldindan "
            "render qilingan, va <code>generateMetadata</code> orqali har bir post o'zining "
            "haqiqiy sarlavhasi/tavsifiga ega (1-va-11-darslardagi SEO muammosining yakuniy "
            "yechimi).</li>"
            "<li><code>app/api/posts/route.js</code> — qidiruv/filtrlash uchun Route Handler, "
            "Client Component'dagi qidiruv maydonidan chaqiriladi.</li>"
            "<li><code>app/api/posts/[slug]/comments/route.js</code> — sharh qo'shish uchun "
            "POST endpoint; sharh qo'shilgandan keyin <code>revalidatePath</code> chaqirilib, "
            "post sahifasining keshi darhol yangilanadi.</li>"
            "<li><code>CommentForm.js</code> ('use client') — interaktiv forma, "
            "<code>useState</code> bilan holatni boshqaradi, submit paytida yuqoridagi Route "
            "Handler'ga <code>fetch</code> qiladi.</li>"
            "<li><code>middleware.js</code> — <code>/admin</code> ostidagi sahifalarni "
            "himoyalaydi (faqat autentifikatsiya qilingan foydalanuvchilar postlarni tahrirlay "
            "oladi).</li>"
            "</ul>"
            "<h3>Server/Client chegarasini qayta eslash</h3>"
            "<p>Butun ilovada faqat <code>CommentForm.js</code> (va, agar qo'shsangiz, \"Like\" "
            "tugmasi) <code>'use client'</code> bilan boshlanadi — qolgan hamma narsa (post "
            "ro'yxati, post matni, sarlavha) Server Component bo'lib qoladi. Bu — 4-darsda "
            "o'rgangan eng muhim tamoyilni amalda qo'llash: chegarani iloji boricha kichik "
            "saqlash.</p>"
            "<h3>Diagram: capstone arxitekturasi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  MW[\"middleware.js\n"
            "/admin'ni himoyalaydi\"] --> HOME[\"app/page.js (SSG)\n"
            "so'nggi postlar\"]\n"
            "  HOME --> POST[\"app/blog/[slug]/page.js\n"
            "generateStaticParams + generateMetadata\"]\n"
            "  POST --> CF[\"'use client'\n"
            "CommentForm.js\"]\n"
            "  CF -->|\"fetch POST\"| API[\"app/api/posts/[slug]/comments/route.js\"]\n"
            "  API -->|\"revalidatePath\"| POST\n"
            "  HOME -->|\"fetch GET ?q=\"| SEARCH[\"app/api/posts/route.js\n"
            "qidiruv Route Handler\"]\n"
            "</pre>"
            "<p>Diagramma butun ilovani bitta ko'rinishda ko'rsatadi: qaysi qismlar statik "
            "(SSG), qaysi qism interaktiv (Client Component), va ular Route Handler'lar orqali "
            "qanday bog'lanadi — bu kursda o'rgangan har bir tushunchaning birgalikda "
            "ishlashi.</p>"
            "<h3>Baholash mezonlari</h3>"
            "<p>Loyiha quyidagilarga ega bo'lishi kerak: kamida ikkita render strategiyasi "
            "aralash ishlatilgan bo'lishi (masalan, SSG bosh sahifa + SSR yoki ISR biror "
            "qism), aniq Server/Client chegarasi (faqat kerakli joylarda "
            "<code>'use client'</code>), kamida bitta Route Handler, kamida bitta dinamik "
            "marshrut <code>generateStaticParams</code> bilan, va har bir post uchun "
            "individual SEO metadata.</p>"
            "<h3>Kengaytirish g'oyalari (ixtiyoriy)</h3>"
            "<p>Agar asosiy talablarni bajarib bo'lgach vaqtingiz qolsa, loyihani quyidagi "
            "yo'nalishlarda kengaytirishingiz mumkin: <code>next/image</code> orqali post "
            "muqova rasmlarini optimallashtirish (10-dars), <code>app/sitemap.js</code> "
            "qo'shish (11-dars), yoki \"Like\" tugmasi kabi ikkinchi kichik Client Component "
            "qo'shib, Server/Client kompozitsiyasini yanada mustahkamlash. Bularning hech "
            "birini qilish shart emas — asosiy talablar to'liq bajarilgan capstone allaqachon "
            "kursning barcha muhim tushunchalarini qamrab oladi.</p>"
            "<h3>Nima uchun bu haqiqiy loyiha, o'yinchoq misol emas</h3>"
            "<p>Bu capstone ataylab \"hello world\" darajasida emas: unda haqiqiy foydalanuvchi "
            "harakati (sharh qoldirish) haqiqiy ma'lumot yangilanishiga (revalidatePath) olib "
            "keladi, haqiqiy SEO muammosi (1-darsdan) haqiqiy yechim bilan yopiladi "
            "(generateMetadata), va haqiqiy xavfsizlik talabi (admin sahifalarini himoyalash) "
            "haqiqiy vosita bilan (middleware) hal qilinadi. Aynan shu — sanoatda Next.js "
            "loyihalari qanday ko'rinishini aks ettiradi.</p>"
        ),
        "text_content_ru": (
            "<h3>Финал курса: всё в одном месте</h3>"
            "<p>В этом курсе мы с урока 1 строили одну историю: начав с реальных ограничений "
            "CRA этой платформы (пустой <code>div#root</code>, один статичный мета-тег, "
            "клиентская маршрутизация), мы шаг за шагом увидели, как Next.js их решает — App "
            "Router, Server/Client Component, стратегии получения данных, SSR/SSG/ISR, Route "
            "Handler'ы, динамические маршруты, Middleware, оптимизация медиа, Metadata API. "
            "Капстоун-проект — объединение всего этого в одном небольшом, но по-настоящему "
            "рабочем приложении.</p>"
            "<h3>Проект: мини-платформа блога</h3>"
            "<p>Мы построим небольшое блог-приложение со следующей архитектурой:</p>"
            "<ul>"
            "<li><code>app/page.js</code> — главная страница, показывает последние посты "
            "(SSG, ведь она одинакова для всех пользователей).</li>"
            "<li><code>app/blog/[slug]/page.js</code> — отдельный пост, предварительно "
            "отрендеренный через <code>generateStaticParams</code> для всех существующих "
            "постов, и через <code>generateMetadata</code> каждый пост получает свой "
            "настоящий заголовок/описание (финальное решение проблемы SEO из уроков 1 и 11).</li>"
            "<li><code>app/api/posts/route.js</code> — Route Handler для поиска/фильтрации, "
            "вызываемый из поля поиска в Client Component.</li>"
            "<li><code>app/api/posts/[slug]/comments/route.js</code> — POST-эндпоинт для "
            "добавления комментария; после добавления комментария вызывается "
            "<code>revalidatePath</code>, и кеш страницы поста немедленно обновляется.</li>"
            "<li><code>CommentForm.js</code> ('use client') — интерактивная форма, управляет "
            "состоянием через <code>useState</code>, при отправке делает <code>fetch</code> к "
            "вышеуказанному Route Handler'у.</li>"
            "<li><code>middleware.js</code> — защищает страницы под <code>/admin</code> "
            "(только авторизованные пользователи могут редактировать посты).</li>"
            "</ul>"
            "<h3>Вспоминаем границу Server/Client</h3>"
            "<p>Во всём приложении только <code>CommentForm.js</code> (и, если добавите, "
            "кнопка «Нравится») начинается с <code>'use client'</code> — всё остальное (список "
            "постов, текст поста, заголовок) остаётся Server Component. Это — применение на "
            "практике важнейшего принципа из урока 4: держать границу максимально маленькой.</p>"
            "<h3>Диаграмма: архитектура капстоуна</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  MW[\"middleware.js\n"
            "защищает /admin\"] --> HOME[\"app/page.js (SSG)\n"
            "последние посты\"]\n"
            "  HOME --> POST[\"app/blog/[slug]/page.js\n"
            "generateStaticParams + generateMetadata\"]\n"
            "  POST --> CF[\"'use client'\n"
            "CommentForm.js\"]\n"
            "  CF -->|\"fetch POST\"| API[\"app/api/posts/[slug]/comments/route.js\"]\n"
            "  API -->|\"revalidatePath\"| POST\n"
            "  HOME -->|\"fetch GET ?q=\"| SEARCH[\"app/api/posts/route.js\n"
            "Route Handler поиска\"]\n"
            "</pre>"
            "<p>Диаграмма показывает всё приложение в одном виде: какие части статичны (SSG), "
            "какая часть интерактивна (Client Component), и как они связаны через Route "
            "Handler'ы — совместная работа каждого понятия, изученного в этом курсе.</p>"
            "<h3>Критерии оценки</h3>"
            "<p>Проект должен включать: минимум две смешанные стратегии рендеринга (например, "
            "SSG для главной + SSR или ISR для какой-то части), чёткую границу Server/Client "
            "(<code>'use client'</code> только там, где нужно), минимум один Route Handler, "
            "минимум один динамический маршрут с <code>generateStaticParams</code>, и "
            "индивидуальные SEO-метаданные для каждого поста.</p>"
            "<h3>Идеи для расширения (опционально)</h3>"
            "<p>Если после выполнения основных требований останется время, проект можно "
            "расширить: оптимизировать обложки постов через <code>next/image</code> (урок 10), "
            "добавить <code>app/sitemap.js</code> (урок 11), либо добавить второй небольшой "
            "Client Component вроде кнопки «Нравится», ещё больше закрепив композицию "
            "Server/Client. Ничего из этого не обязательно — капстоун с полностью выполненными "
            "основными требованиями уже охватывает все важные понятия курса.</p>"
            "<h3>Почему это настоящий проект, а не игрушечный пример</h3>"
            "<p>Этот капстоун намеренно не на уровне «hello world»: в нём настоящее действие "
            "пользователя (оставление комментария) приводит к настоящему обновлению данных "
            "(revalidatePath), настоящая проблема SEO (из урока 1) закрывается настоящим "
            "решением (generateMetadata), а настоящее требование безопасности (защита "
            "админ-страниц) решается настоящим инструментом (middleware). Именно так выглядят "
            "реальные Next.js-проекты в индустрии.</p>"
        ),
        "code_content": (
            "// ===== To'liq capstone fayl tuzilishi =====\n"
            "app/\n"
            "  layout.js                        // ROOT: title.template, html/body\n"
            "  page.js                          // GET / — SSG, so'nggi postlar\n"
            "  blog/\n"
            "    _components/\n"
            "      SearchBox.js                  // 'use client' — qidiruv input'i\n"
            "    [slug]/\n"
            "      page.js                       // SSG + generateStaticParams + generateMetadata\n"
            "      CommentForm.js                // 'use client' — sharh formasi\n"
            "      LikeButton.js                 // 'use client' — yoqtirish tugmasi\n"
            "  admin/\n"
            "    page.js                         // middleware bilan himoyalangan\n"
            "  api/\n"
            "    posts/\n"
            "      route.js                      // GET — qidiruv/filtrlash\n"
            "      [slug]/\n"
            "        comments/\n"
            "          route.js                   // POST — sharh qo'shish + revalidatePath\n"
            "middleware.js                       // /admin'ni himoyalaydi\n"
            "\n"
            "// ===== app/layout.js — ROOT, SEO shabloni =====\n"
            "export const metadata = {\n"
            "  title: { template: '%s | Mini-Blog', default: 'Mini-Blog' },\n"
            "  description: \"Next.js'da qurilgan namunaviy blog\",\n"
            "};\n"
            "\n"
            "export default function RootLayout({ children }) {\n"
            "  return (\n"
            "    <html lang=\"uz\">\n"
            "      <body>{children}</body>\n"
            "    </html>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/page.js — bosh sahifa (SSG) =====\n"
            "import Link from 'next/link';\n"
            "import SearchBox from './blog/_components/SearchBox';\n"
            "\n"
            "export default async function HomePage() {\n"
            "  const posts = await fetch('https://api.example.com/posts').then((r) => r.json());\n"
            "  return (\n"
            "    <main>\n"
            "      <h1>So'nggi postlar</h1>\n"
            "      <SearchBox /> {/* Client Component, Route Handler'ga fetch qiladi */}\n"
            "      <ul>\n"
            "        {posts.map((p) => (\n"
            "          <li key={p.slug}><Link href={`/blog/${p.slug}`}>{p.title}</Link></li>\n"
            "        ))}\n"
            "      </ul>\n"
            "    </main>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/blog/_components/SearchBox.js — Client Component + Route Handler =====\n"
            "'use client';\n"
            "import { useState } from 'react';\n"
            "\n"
            "export default function SearchBox() {\n"
            "  const [query, setQuery] = useState('');\n"
            "  const [results, setResults] = useState(null);\n"
            "\n"
            "  async function handleSearch(e) {\n"
            "    e.preventDefault();\n"
            "    const res = await fetch(`/api/posts?q=${encodeURIComponent(query)}`);\n"
            "    setResults(await res.json());\n"
            "  }\n"
            "\n"
            "  return (\n"
            "    <form onSubmit={handleSearch}>\n"
            "      <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder=\"Qidirish...\" />\n"
            "      <button type=\"submit\">Qidirish</button>\n"
            "      {results && (\n"
            "        <ul>{results.map((p) => <li key={p.slug}>{p.title}</li>)}</ul>\n"
            "      )}\n"
            "    </form>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/api/posts/route.js — qidiruv Route Handler =====\n"
            "import { NextResponse } from 'next/server';\n"
            "\n"
            "export async function GET(request) {\n"
            "  const q = request.nextUrl.searchParams.get('q') || '';\n"
            "  const posts = await fetch('https://api.example.com/posts').then((r) => r.json());\n"
            "  const filtered = posts.filter((p) => p.title.toLowerCase().includes(q.toLowerCase()));\n"
            "  return NextResponse.json(filtered);\n"
            "}\n"
            "\n"
            "// ===== app/blog/[slug]/page.js — SSG + dinamik metadata + sharhlar =====\n"
            "import { notFound } from 'next/navigation';\n"
            "import CommentForm from './CommentForm';\n"
            "import LikeButton from './LikeButton';\n"
            "\n"
            "export async function generateStaticParams() {\n"
            "  const posts = await fetch('https://api.example.com/posts').then((r) => r.json());\n"
            "  return posts.map((p) => ({ slug: p.slug }));\n"
            "}\n"
            "\n"
            "export async function generateMetadata({ params }) {\n"
            "  const { slug } = await params;\n"
            "  const post = await fetch(`https://api.example.com/posts/${slug}`).then((r) => r.json());\n"
            "  return {\n"
            "    title: post.title,\n"
            "    description: post.excerpt,\n"
            "    openGraph: { title: post.title, images: [post.coverUrl] },\n"
            "  };\n"
            "}\n"
            "\n"
            "export default async function PostPage({ params }) {\n"
            "  const { slug } = await params;\n"
            "  const postRes = await fetch(`https://api.example.com/posts/${slug}`);\n"
            "  if (postRes.status === 404) notFound();\n"
            "\n"
            "  const [post, comments] = await Promise.all([\n"
            "    postRes.json(),\n"
            "    fetch(`https://api.example.com/posts/${slug}/comments`).then((r) => r.json()),\n"
            "  ]);\n"
            "\n"
            "  return (\n"
            "    <article>\n"
            "      <h1>{post.title}</h1>\n"
            "      <div>{post.body}</div>\n"
            "      <LikeButton postSlug={slug} />\n"
            "      <h2>Sharhlar ({comments.length})</h2>\n"
            "      <ul>{comments.map((c) => <li key={c.id}>{c.text}</li>)}</ul>\n"
            "      <CommentForm slug={slug} />\n"
            "    </article>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/api/posts/[slug]/comments/route.js — sharh qo'shish + revalidatsiya =====\n"
            "import { NextResponse } from 'next/server';\n"
            "import { revalidatePath } from 'next/cache';\n"
            "\n"
            "export async function POST(request, { params }) {\n"
            "  const { slug } = await params;\n"
            "  let body;\n"
            "  try {\n"
            "    body = await request.json();\n"
            "  } catch {\n"
            "    return NextResponse.json({ error: 'Yaroqsiz JSON' }, { status: 400 });\n"
            "  }\n"
            "  if (!body.text || typeof body.text !== 'string') {\n"
            "    return NextResponse.json({ error: 'text majburiy' }, { status: 400 });\n"
            "  }\n"
            "  // ... yangi sharhni saqlash mantig'i shu yerda ...\n"
            "  revalidatePath(`/blog/${slug}`); // post sahifasi keshini darhol yangilaydi\n"
            "  return NextResponse.json({ ok: true }, { status: 201 });\n"
            "}\n"
            "\n"
            "// ===== app/blog/[slug]/CommentForm.js — Client Component =====\n"
            "'use client';\n"
            "import { useState } from 'react';\n"
            "import { useRouter } from 'next/navigation';\n"
            "\n"
            "export default function CommentForm({ slug }) {\n"
            "  const [text, setText] = useState('');\n"
            "  const [submitting, setSubmitting] = useState(false);\n"
            "  const router = useRouter();\n"
            "\n"
            "  async function handleSubmit(e) {\n"
            "    e.preventDefault();\n"
            "    setSubmitting(true);\n"
            "    await fetch(`/api/posts/${slug}/comments`, {\n"
            "      method: 'POST',\n"
            "      body: JSON.stringify({ text }),\n"
            "    });\n"
            "    setText('');\n"
            "    setSubmitting(false);\n"
            "    router.refresh(); // Server Component'larni yangi ma'lumot bilan qayta chizadi\n"
            "  }\n"
            "\n"
            "  return (\n"
            "    <form onSubmit={handleSubmit}>\n"
            "      <textarea value={text} onChange={(e) => setText(e.target.value)} />\n"
            "      <button type=\"submit\" disabled={submitting}>\n"
            "        {submitting ? 'Yuborilmoqda...' : 'Yuborish'}\n"
            "      </button>\n"
            "    </form>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/blog/[slug]/LikeButton.js — kichik Client Component =====\n"
            "'use client';\n"
            "import { useState } from 'react';\n"
            "\n"
            "export default function LikeButton({ postSlug }) {\n"
            "  const [liked, setLiked] = useState(false);\n"
            "  return (\n"
            "    <button onClick={() => setLiked((v) => !v)}>\n"
            "      {liked ? 'Yoqdi ✓' : \"Yoqtirish\"}\n"
            "    </button>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== middleware.js — /admin'ni himoyalash =====\n"
            "import { NextResponse } from 'next/server';\n"
            "\n"
            "export function middleware(request) {\n"
            "  const token = request.cookies.get('session_token');\n"
            "  if (!token) {\n"
            "    return NextResponse.redirect(new URL('/login', request.url));\n"
            "  }\n"
            "  return NextResponse.next();\n"
            "}\n"
            "\n"
            "export const config = { matcher: ['/admin/:path*'] };\n"
        ),
        "code_content_ru": (
            "// ===== Полная структура файлов капстоуна =====\n"
            "app/\n"
            "  layout.js                        // ROOT: title.template, html/body\n"
            "  page.js                          // GET / — SSG, последние посты\n"
            "  blog/\n"
            "    _components/\n"
            "      SearchBox.js                  // 'use client' — поле поиска\n"
            "    [slug]/\n"
            "      page.js                       // SSG + generateStaticParams + generateMetadata\n"
            "      CommentForm.js                // 'use client' — форма комментария\n"
            "      LikeButton.js                 // 'use client' — кнопка «Нравится»\n"
            "  admin/\n"
            "    page.js                         // защищена через middleware\n"
            "  api/\n"
            "    posts/\n"
            "      route.js                      // GET — поиск/фильтрация\n"
            "      [slug]/\n"
            "        comments/\n"
            "          route.js                   // POST — добавление комментария + revalidatePath\n"
            "middleware.js                       // защищает /admin\n"
            "\n"
            "// ===== app/layout.js — ROOT, шаблон SEO =====\n"
            "export const metadata = {\n"
            "  title: { template: '%s | Mini-Blog', default: 'Mini-Blog' },\n"
            "  description: 'Демонстрационный блог, построенный на Next.js',\n"
            "};\n"
            "\n"
            "export default function RootLayout({ children }) {\n"
            "  return (\n"
            "    <html lang=\"ru\">\n"
            "      <body>{children}</body>\n"
            "    </html>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/page.js — главная страница (SSG) =====\n"
            "import Link from 'next/link';\n"
            "import SearchBox from './blog/_components/SearchBox';\n"
            "\n"
            "export default async function HomePage() {\n"
            "  const posts = await fetch('https://api.example.com/posts').then((r) => r.json());\n"
            "  return (\n"
            "    <main>\n"
            "      <h1>Последние посты</h1>\n"
            "      <SearchBox /> {/* Client Component, делает fetch к Route Handler'у */}\n"
            "      <ul>\n"
            "        {posts.map((p) => (\n"
            "          <li key={p.slug}><Link href={`/blog/${p.slug}`}>{p.title}</Link></li>\n"
            "        ))}\n"
            "      </ul>\n"
            "    </main>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/blog/_components/SearchBox.js — Client Component + Route Handler =====\n"
            "'use client';\n"
            "import { useState } from 'react';\n"
            "\n"
            "export default function SearchBox() {\n"
            "  const [query, setQuery] = useState('');\n"
            "  const [results, setResults] = useState(null);\n"
            "\n"
            "  async function handleSearch(e) {\n"
            "    e.preventDefault();\n"
            "    const res = await fetch(`/api/posts?q=${encodeURIComponent(query)}`);\n"
            "    setResults(await res.json());\n"
            "  }\n"
            "\n"
            "  return (\n"
            "    <form onSubmit={handleSearch}>\n"
            "      <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder=\"Поиск...\" />\n"
            "      <button type=\"submit\">Найти</button>\n"
            "      {results && (\n"
            "        <ul>{results.map((p) => <li key={p.slug}>{p.title}</li>)}</ul>\n"
            "      )}\n"
            "    </form>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/api/posts/route.js — Route Handler поиска =====\n"
            "import { NextResponse } from 'next/server';\n"
            "\n"
            "export async function GET(request) {\n"
            "  const q = request.nextUrl.searchParams.get('q') || '';\n"
            "  const posts = await fetch('https://api.example.com/posts').then((r) => r.json());\n"
            "  const filtered = posts.filter((p) => p.title.toLowerCase().includes(q.toLowerCase()));\n"
            "  return NextResponse.json(filtered);\n"
            "}\n"
            "\n"
            "// ===== app/blog/[slug]/page.js — SSG + динамические метаданные + комментарии =====\n"
            "import { notFound } from 'next/navigation';\n"
            "import CommentForm from './CommentForm';\n"
            "import LikeButton from './LikeButton';\n"
            "\n"
            "export async function generateStaticParams() {\n"
            "  const posts = await fetch('https://api.example.com/posts').then((r) => r.json());\n"
            "  return posts.map((p) => ({ slug: p.slug }));\n"
            "}\n"
            "\n"
            "export async function generateMetadata({ params }) {\n"
            "  const { slug } = await params;\n"
            "  const post = await fetch(`https://api.example.com/posts/${slug}`).then((r) => r.json());\n"
            "  return {\n"
            "    title: post.title,\n"
            "    description: post.excerpt,\n"
            "    openGraph: { title: post.title, images: [post.coverUrl] },\n"
            "  };\n"
            "}\n"
            "\n"
            "export default async function PostPage({ params }) {\n"
            "  const { slug } = await params;\n"
            "  const postRes = await fetch(`https://api.example.com/posts/${slug}`);\n"
            "  if (postRes.status === 404) notFound();\n"
            "\n"
            "  const [post, comments] = await Promise.all([\n"
            "    postRes.json(),\n"
            "    fetch(`https://api.example.com/posts/${slug}/comments`).then((r) => r.json()),\n"
            "  ]);\n"
            "\n"
            "  return (\n"
            "    <article>\n"
            "      <h1>{post.title}</h1>\n"
            "      <div>{post.body}</div>\n"
            "      <LikeButton postSlug={slug} />\n"
            "      <h2>Комментарии ({comments.length})</h2>\n"
            "      <ul>{comments.map((c) => <li key={c.id}>{c.text}</li>)}</ul>\n"
            "      <CommentForm slug={slug} />\n"
            "    </article>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/api/posts/[slug]/comments/route.js — добавление + ревалидация =====\n"
            "import { NextResponse } from 'next/server';\n"
            "import { revalidatePath } from 'next/cache';\n"
            "\n"
            "export async function POST(request, { params }) {\n"
            "  const { slug } = await params;\n"
            "  let body;\n"
            "  try {\n"
            "    body = await request.json();\n"
            "  } catch {\n"
            "    return NextResponse.json({ error: 'Некорректный JSON' }, { status: 400 });\n"
            "  }\n"
            "  if (!body.text || typeof body.text !== 'string') {\n"
            "    return NextResponse.json({ error: 'text обязателен' }, { status: 400 });\n"
            "  }\n"
            "  // ... логика сохранения нового комментария здесь ...\n"
            "  revalidatePath(`/blog/${slug}`); // немедленно обновляет кеш страницы поста\n"
            "  return NextResponse.json({ ok: true }, { status: 201 });\n"
            "}\n"
            "\n"
            "// ===== app/blog/[slug]/CommentForm.js — Client Component =====\n"
            "'use client';\n"
            "import { useState } from 'react';\n"
            "import { useRouter } from 'next/navigation';\n"
            "\n"
            "export default function CommentForm({ slug }) {\n"
            "  const [text, setText] = useState('');\n"
            "  const [submitting, setSubmitting] = useState(false);\n"
            "  const router = useRouter();\n"
            "\n"
            "  async function handleSubmit(e) {\n"
            "    e.preventDefault();\n"
            "    setSubmitting(true);\n"
            "    await fetch(`/api/posts/${slug}/comments`, {\n"
            "      method: 'POST',\n"
            "      body: JSON.stringify({ text }),\n"
            "    });\n"
            "    setText('');\n"
            "    setSubmitting(false);\n"
            "    router.refresh(); // перерисовывает Server Component'ы со свежими данными\n"
            "  }\n"
            "\n"
            "  return (\n"
            "    <form onSubmit={handleSubmit}>\n"
            "      <textarea value={text} onChange={(e) => setText(e.target.value)} />\n"
            "      <button type=\"submit\" disabled={submitting}>\n"
            "        {submitting ? 'Отправка...' : 'Отправить'}\n"
            "      </button>\n"
            "    </form>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== app/blog/[slug]/LikeButton.js — небольшой Client Component =====\n"
            "'use client';\n"
            "import { useState } from 'react';\n"
            "\n"
            "export default function LikeButton({ postSlug }) {\n"
            "  const [liked, setLiked] = useState(false);\n"
            "  return (\n"
            "    <button onClick={() => setLiked((v) => !v)}>\n"
            "      {liked ? 'Нравится ✓' : 'Нравится'}\n"
            "    </button>\n"
            "  );\n"
            "}\n"
            "\n"
            "// ===== middleware.js — защита /admin =====\n"
            "import { NextResponse } from 'next/server';\n"
            "\n"
            "export function middleware(request) {\n"
            "  const token = request.cookies.get('session_token');\n"
            "  if (!token) {\n"
            "    return NextResponse.redirect(new URL('/login', request.url));\n"
            "  }\n"
            "  return NextResponse.next();\n"
            "}\n"
            "\n"
            "export const config = { matcher: ['/admin/:path*'] };\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "CAPSTONE: To'liq stack Next.js blog ilovasi",
            "task_title_ru": "КАПСТОУН: Полноценное Next.js-приложение блога",
            "task_description": (
                "Kursda o'rgangan barcha tushunchalarni birlashtirgan kichik blog (yoki "
                "mahsulotlar katalogi) ilovasini qurib bering: bosh sahifa (SSG), dinamik post "
                "sahifasi (generateStaticParams + generateMetadata), qidiruv Route Handler, "
                "sharh qo'shish uchun POST Route Handler (revalidatePath bilan), interaktiv "
                "CommentForm ('use client'), va /admin'ni himoyalaydigan middleware."
            ),
            "task_description_ru": (
                "Постройте небольшое приложение блога (или каталога товаров), объединяющее все "
                "изученные в курсе понятия: главная страница (SSG), динамическая страница поста "
                "(generateStaticParams + generateMetadata), Route Handler для поиска, POST "
                "Route Handler для добавления комментария (с revalidatePath), интерактивная "
                "CommentForm ('use client'), и middleware, защищающий /admin."
            ),
            "task_requirements": (
                "Kamida: 1 SSG sahifa, 1 dinamik marshrut generateStaticParams bilan, 1 "
                "generateMetadata, 2 Route Handler (GET va POST), 1 Client Component, 1 "
                "middleware. Server/Client chegarasi aniq va minimal bo'lishi shart."
            ),
            "task_requirements_ru": (
                "Минимум: 1 страница SSG, 1 динамический маршрут с generateStaticParams, 1 "
                "generateMetadata, 2 Route Handler (GET и POST), 1 Client Component, 1 "
                "middleware. Граница Server/Client должна быть чёткой и минимальной."
            ),
            "task_technologies": "Next.js, App Router, Server Components, Route Handlers, Middleware",
            "task_deadline_days": 10,
        },
        "sample": {
            "title": "Namuna: to'liq capstone arxitekturasi",
            "description": "Blog capstone loyihasining asosiy fayllari birgalikda.",
            "sample_type": "code",
            "code_files": [
                {"filename": "app/page.js", "language": "jsx",
                 "code": "export default async function HomePage() {\n  const posts = await fetch('https://api.example.com/posts').then((r) => r.json());\n  return (\n    <ul>\n      {posts.map((p) => (\n        <li key={p.slug}><a href={`/blog/${p.slug}`}>{p.title}</a></li>\n      ))}\n    </ul>\n  );\n}\n"},
                {"filename": "middleware.js", "language": "javascript",
                 "code": "import { NextResponse } from 'next/server';\n\nexport function middleware(request) {\n  const token = request.cookies.get('session_token');\n  if (!token) return NextResponse.redirect(new URL('/login', request.url));\n  return NextResponse.next();\n}\n\nexport const config = { matcher: ['/admin/:path*'] };\n"},
                {"filename": "app/api/posts/route.js", "language": "javascript",
                 "code": "import { NextResponse } from 'next/server';\n\nexport async function GET(request) {\n  const q = request.nextUrl.searchParams.get('q') || '';\n  const posts = await fetch('https://api.example.com/posts').then((r) => r.json());\n  const filtered = posts.filter((p) => p.title.toLowerCase().includes(q.toLowerCase()));\n  return NextResponse.json(filtered);\n}\n"},
            ],
        },
        "exercises": [
            {
                "title": "Capstone'da Client Component qaysi qism",
                "title_ru": "Какая часть капстоуна — Client Component",
                "description": (
                    "Capstone arxitekturasida qaysi fayl 'use client' bilan boshlanishi kerak?"
                ),
                "description_ru": (
                    "В архитектуре капстоуна какой файл должен начинаться с 'use client'?"
                ),
                "exercise_type": "multiple_choice",
                "options": ["app/page.js", "app/blog/[slug]/page.js", "CommentForm.js", "app/api/posts/route.js"],
                "options_ru": ["app/page.js", "app/blog/[slug]/page.js", "CommentForm.js", "app/api/posts/route.js"],
                "correct_answers": "C",
                "is_multiple_select": False,
                "hint": "Interaktivlik (useState, forma yuborish) faqat shu qismda kerak.",
                "hint_ru": "Интерактивность (useState, отправка формы) нужна только в этой части.",
                "explanation": "CommentForm.js interaktiv forma bo'lgani uchun 'use client' bilan boshlanishi shart, qolganlari Server Component.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Sharh qo'shilgandan keyin keshni yangilash",
                "title_ru": "Обновление кеша после добавления комментария",
                "description": (
                    "Bo'shliqni to'ldiring: sharh qo'shilgandan keyin post sahifasining keshini "
                    "darhol yangilash uchun Route Handler ichida ___ funksiyasi chaqiriladi."
                ),
                "description_ru": (
                    "Заполните пропуск: чтобы немедленно обновить кеш страницы поста после "
                    "добавления комментария, внутри Route Handler вызывается функция ___."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "revalidatePath",
                "hint": "5-darsda ko'rgan \"talab bo'yicha revalidatsiya\" vositalaridan biri.",
                "hint_ru": "Один из инструментов «ревалидации по требованию» из урока 5.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "So'rovdan sharh saqlanishigacha oqim",
                "title_ru": "Поток от запроса до сохранения комментария",
                "description": (
                    "Foydalanuvchi sharh yuborganidan to sahifa yangilanishigacha bo'lgan "
                    "qadamlarni tartibga joylashtiring."
                ),
                "description_ru": (
                    "Расставьте по порядку шаги от отправки комментария пользователем до "
                    "обновления страницы."
                ),
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "CommentForm submit hodisasini ushlaydi",
                    "fetch orqali POST /api/posts/[slug]/comments chaqiriladi",
                    "Route Handler sharhni saqlaydi",
                    "revalidatePath post sahifasi keshini yangilaydi",
                ],
                "drag_items_ru": [
                    "CommentForm перехватывает событие submit",
                    "Через fetch вызывается POST /api/posts/[slug]/comments",
                    "Route Handler сохраняет комментарий",
                    "revalidatePath обновляет кеш страницы поста",
                ],
                "correct_order": [
                    "CommentForm submit hodisasini ushlaydi",
                    "fetch orqali POST /api/posts/[slug]/comments chaqiriladi",
                    "Route Handler sharhni saqlaydi",
                    "revalidatePath post sahifasi keshini yangilaydi",
                ],
                "hint": "Client'dan boshlanadi, Route Handler orqali o'tadi, kesh yangilanishi bilan tugaydi.",
                "hint_ru": "Начинается с клиента, проходит через Route Handler, заканчивается обновлением кеша.",
                "difficulty_level": "Hard",
                "points": 15,
            },
        ],
    },
]

_lesson_points = sum(l.get("points_reward", 10) for l in LESSONS)
_exercise_points = sum(
    ex.get("points", 10) for l in LESSONS for ex in (l.get("exercises") or [])
)
COURSE["max_points"] = _lesson_points + _exercise_points
