"""Advanced React course: Performance va Optimizatsiya — fills the one clear
remaining gap in category_id=9 (React). Course 43 (React Asoslari) teaches
components/props/state/hooks and touches memo/useMemo/useCallback only
briefly in its final lesson. Course 72 (Redux Toolkit, TypeScript va
Testlash) teaches state management, typing and testing. Course 139 (Next.js
va Server-Side Rendering) teaches server rendering. NONE of them teach how
to actually MEASURE and FIX a slow React app: the Profiler workflow, why
re-renders cascade, when memoization helps vs hurts, code splitting,
virtualization, Context re-render pitfalls, concurrent features, bundle
size, Redux selector performance, Web Vitals, and the everyday anti-patterns
that cause slow renders. This course closes that gap.

Grounding note (do not remove this comment): this repository's own frontend
(frontend/src/) is a real, substantial Create React App codebase, and this
course draws several of its examples directly from it — read, verified,
never fabricated:
  - frontend/src/views/student/courses/Courses/StudentCourses.js: the
    `CourseCard` component is not wrapped in React.memo, and its parent
    passes `onOpen={() => goToCourse(course)}` — a fresh inline arrow
    function every render. Also: `displayed` and `categoryCounts` are
    derived with plain .filter()/.map() on every render with NO useMemo —
    a genuine, correct example of a case where the list is small (a
    student's own course list, at most a few dozen items) and the
    computation cheap enough that memoizing it would be pure overhead, not
    an optimization.
  - frontend/src/views/student/projects/ProjectCard.js line 41: `{(techStack
    || []).map((tech, index) => (<span key={index} ...>`, a real
    index-as-key instance — and, honestly, a fairly low-risk one, since the
    tech list is static per project and never reordered, which is itself a
    useful real "when is index-as-key actually fine" teaching point.
  - frontend/src/context/StoreContext.js: `useMemo`-wraps its context value
    (balance, lifetimePoints, recent, inventory, equipped, loading + three
    functions all bundled into ONE object), so ANY consumer re-renders on
    ANY of those changing — e.g. a header coin-balance chip that only reads
    `balance` still re-renders when `inventory` changes from browsing the
    store. frontend/src/context/AuthContext.js goes one step further: its
    Provider value (`{ user, isAuthenticated, login, logout }`) is a bare
    object literal, not even wrapped in useMemo, so it is a NEW reference on
    every AuthProvider render regardless of whether anything inside actually
    changed. Both are real, accurately described — not disparaged; low
    actual impact today because these providers rarely re-render, but exactly
    the shape of bug that bites at scale.
  - frontend/src/AppRouter.js: every single student AND teacher view (over
    25 imports, including the 1273-line TeacherTeamGame.js) is imported
    eagerly at the top of one file with zero React.lazy/Suspense anywhere in
    the app. A student who only ever visits /student routes still downloads
    every teacher view in their initial bundle. Real, verifiable, and a
    textbook route-based code-splitting opportunity.
  - frontend/src/views/student/rankings/LeaderBoard.js: fetches
    `?period=...&limit=50` and renders up to 50 rows directly with no
    windowing — an honest "does NOT need virtualization yet" example (50
    DOM rows is cheap), used to teach exactly where the real threshold is,
    not to claim a problem that doesn't exist.
  - frontend/src/views/student/teamgame/StudentTeamGame.js line 111: a
    `setInterval(tick, 250)` countdown updates state four times a second —
    a real, verifiable source of frequent re-renders used for the
    Profiler-measurement and end-to-end diagnosis lessons.
  - frontend/src/store/store.js + coursesSlice.js/studentsSlice.js: a real
    configureStore with two slices — used honestly, including noting that
    no component in this codebase currently calls useSelector on them (the
    live course browsing UI fetches via REST instead, see StudentCourses.js
    above); the selector-performance lesson is upfront that this is a real
    but currently-unused store, and builds its granularity example as a
    clearly-labeled hypothetical extension of that real shape rather than
    pretending a live selector exists where none does.

No invented benchmark numbers anywhere (no "3x faster" claims) — only
qualitative descriptions and relative before/after render-COUNT comparisons
of the kind React DevTools Profiler actually reports.

Built with the course_builder scaffold — see course_builder/__init__.py for
the spec contract. Every lesson gets both task + sample from the start
(review lesson R1 excepted, matching the sanctioned shorter-review pattern),
full UZ+RU authored here directly, Mermaid diagrams where they genuinely
clarify. is_published stays False — a human reviews first.
"""

COURSE = {
    "title": "React: Performance va Optimizatsiya",
    "title_ru": "React: производительность и оптимизация",
    "description": (
        "React Asoslari (43-kurs) komponentlar, props/state va hook'larni o'rgatadi; "
        "Redux Toolkit, TypeScript va Testlash (72-kurs) holatni boshqarish, tiplash va "
        "testlashni chuqurlashtiradi. Lekin ikkalasi ham bitta muhim savolni deyarli "
        "chetlab o'tadi: ilova nega sekin ishlayapti, va buni qanday ISHONCHLI aniqlash "
        "va tuzatish mumkin? Bu kurs aynan shu bo'shliqni to'ldiradi. React DevTools "
        "Profiler bilan taxmin qilmasdan o'lchashni, komponent nega qayta render "
        "bo'lishini, React.memo/useMemo/useCallback nima qilishini va — muhimi — ULARDAN "
        "QACHON FOYDALANMASLIK kerakligini (haddan tashqari memoizatsiya sekinlashtirishi "
        "mumkin), React.lazy/Suspense orqali code splitting'ni, uzun ro'yxatlar uchun "
        "virtualizatsiyani (react-window), Context'ning keng tarqalgan qayta-render "
        "tuzog'ini, useTransition/useDeferredValue orqali concurrent renderni, bundle "
        "hajmini tahlil qilish va qisqartirishni, Redux selector'lar orqali holat "
        "boshqaruvi performансini, React ilovasida Web Vitals'ni (LCP/INP/CLS) va sekin "
        "render'larga olib keladigan kundalik xatolarni o'rgatadi. Barcha misollar ushbu "
        "platformaning haqiqiy frontend kodidan (StudentCourses.js, AppRouter.js, "
        "StoreContext.js, LeaderBoard.js va boshqalar) olingan haqiqiy naqshlar bilan "
        "asoslanadi — o'ylab topilgan raqamlarsiz. Kurs oxirida atayin sekin qilib "
        "qurilgan kichik React ilovani profil qilib, bir nechta texnikani qo'llab "
        "optimallashtirasiz."
    ),
    "description_ru": (
        "Курс «React Asoslari» (43) учит компонентам, props/state и хукам; «Redux "
        "Toolkit, TypeScript va Testlash» (72) углубляет управление состоянием, "
        "типизацию и тестирование. Но оба почти обходят один важный вопрос: почему "
        "приложение работает медленно, и как это НАДЁЖНО определить и исправить? Этот "
        "курс закрывает именно этот пробел. Вы научитесь измерять, а не гадать, с "
        "помощью React DevTools Profiler; поймёте, почему компонент перерендеривается; "
        "разберёте, что реально делают React.memo/useMemo/useCallback — и, что важно, "
        "КОГДА их НЕ стоит использовать (чрезмерная мемоизация может замедлить, а не "
        "ускорить); освоите code splitting через React.lazy/Suspense, виртуализацию "
        "длинных списков (react-window), частую ловушку с перерендером через Context, "
        "конкурентный рендеринг через useTransition/useDeferredValue, анализ и "
        "сокращение размера бандла, производительность управления состоянием через "
        "селекторы Redux, Web Vitals в React-приложении (LCP/INP/CLS) и повседневные "
        "антипаттерны, вызывающие медленный рендеринг. Все примеры опираются на "
        "реальный код фронтенда этой платформы (StudentCourses.js, AppRouter.js, "
        "StoreContext.js, LeaderBoard.js и другие) — без выдуманных цифр. В конце курса "
        "вы профилируете и оптимизируете специально замедленное небольшое React-"
        "приложение, применяя несколько техник из курса."
    ),
    "instructor_id": 2,
    "difficulty_level": "Advanced",
    "duration_weeks": 4,
    "max_points": 0,  # computed at the bottom of this file from LESSONS
    "category_id": 9,
    "prerequisite_course_id": 72,
    "display_order": 405,
    "image_url": "https://img.icons8.com/color/96/speed.png",
    "thumbnail_url": "https://img.icons8.com/color/240/speed.png",
    "is_active": True,
    "is_published": False,
}

LESSONS = [
    {
        "order": 0,
        "title": "1-Nega React performance muhim? DevTools Profiler bilan o'lchash",
        "title_ru": "1-Зачем нужна производительность React? Измерение через DevTools Profiler",
        "points_reward": 15,
        "text_content": (
            "<h3>\"Sekin tuyuladi\" — bu o'lchov emas</h3>"
            "<p>Foydalanuvchi \"ilova sekin ishlayapti\" deganda, bu his-tuyg'u — aniq son "
            "emas. Tajribasiz dasturchi bunga ko'pincha taxmin bilan javob beradi: \"balki "
            "useMemo qo'shsam yordam berar\", \"balki bu komponentni memo qilsam\". Bu "
            "yondashuvning ikkita muammosi bor: birinchidan, muammoning haqiqiy manbasi "
            "boshqa joyda bo'lishi mumkin; ikkinchidan, noto'g'ri joyga qo'yilgan "
            "memoizatsiya ba'zan ilovani SEKINLASHTIRADI (2-darsda buni ko'ramiz). Ushbu "
            "kursning birinchi va eng muhim qoidasi: <strong>avval o'lchang, keyin "
            "tuzating</strong>. Buning vositasi — React DevTools kengaytmasidagi "
            "\"Profiler\" bo'limi.</p>"
            "<h3>React DevTools Profiler bilan tanishuv</h3>"
            "<p>Brauzer kengaytmasi sifatida o'rnatilgan React DevTools'da ikkita tab bor: "
            "\"Components\" (daraxtni ko'rish uchun) va \"Profiler\" (o'lchash uchun). "
            "Profiler tab'ida yozib olish tugmasini (record, doira belgisi) bosasiz, "
            "ilova bilan odatdagidek ishlaysiz (masalan, filtr bosasiz yoki forma "
            "to'ldirasiz), keyin yozishni to'xtatasiz. Natijada har bir \"commit\" "
            "(React'ning ekranga o'zgarishlarni qo'llagan bir marta) uchun: qaysi "
            "komponentlar render bo'lgani, har biri qancha vaqt olgani (flamegraph — har "
            "bir to'rtburchak bir komponent, kengligi vaqtga mutanosib) va \"ranked\" "
            "ko'rinishda eng ko'p vaqt olgan komponentlar ro'yxati ko'rsatiladi.</p>"
            "<h3>\"Nega bu komponent render bo'ldi?\" savoli</h3>"
            "<p>Profiler sozlamalarida \"Record why each component rendered while "
            "profiling\" katagini yoqish mumkin. Yoqilgandan so'ng, har bir komponentni "
            "bosganingizda u NEGA render bo'lganini ko'rasiz — masalan \"props "
            "changed: onOpen\", \"hooks changed: 1\" yoki \"parent component "
            "rendered\". Aynan shu oxirgisi — \"parent component rendered\" — React'ning "
            "eng ko'p tushunmaydigan xatti-harakati: komponent HECH QANDAY o'z props yoki "
            "state'i o'zgarmagan bo'lsa ham, ota-komponent qayta render bo'lgani sababli "
            "qayta render bo'lishi mumkin. Buni 2-darsda batafsil ko'ramiz.</p>"
            "<h3>Diagramma: taxmin qilish va o'lchash</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Foydalanuvchi: 'ilova sekin'\"] --> B{\"Qanday yondashasiz?\"}\n"
            "  B -->|\"Taxmin\"| C[\"useMemo/memo qo'shib ko'ramiz\n"
            "sabab noma'lum\"]\n"
            "  C --> D[\"Ba'zan yordam bermaydi\n"
            "yoki sekinlashtiradi\"]\n"
            "  B -->|\"O'lchash\"| E[\"Profiler'da yozib olish\"]\n"
            "  E --> F[\"Qaysi komponent, qancha vaqt,\n"
            "nega render bo'lganini ko'rish\"]\n"
            "  F --> G[\"Aniq sababga mos tuzatish\"]\n"
            "  G --> H[\"Qayta o'lchab tasdiqlash\"]\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: \"taxmin\" yo'li tasodifiy tuzatishga va "
            "ba'zan yomonlashishga olib keladi, \"o'lchash\" yo'li esa aniq sabab va "
            "tasdiqlangan tuzatishga olib keladi. Ushbu kursning har bir darsi shu ikkinchi "
            "yo'lni mustahkamlaydi.</p>"
            "<h3>Ushbu platformaning haqiqiy koddan misoli</h3>"
            "<p>Bu — o'ylab topilgan misol emas: <code>frontend/src/views/student/teamgame/"
            "StudentTeamGame.js</code> faylining 111-qatorida haqiqiy "
            "<code>setInterval(tick, 250)</code> chaqiruvi bor — bu o'yin savoliga "
            "qolgan vaqtni sekundiga 4 marta (har 250ms'da) yangilaydigan taymer. Har "
            "safar <code>tick()</code> ishga tushganda, u <code>setTimeLeft(...)</code> "
            "orqali state'ni yangilaydi, bu esa komponentni qayta render qiladi. Savol: "
            "bu — muammomi? Taxmin qilish o'rniga to'g'ri javob: Profiler'ni yoqib, o'sha "
            "komponentni ko'rib chiqish kerak — agar faqat taymer raqami va unga bog'liq "
            "kichik UI qismi render bo'lsa (butun sahifa emas), bu odatda muammo emas. "
            "Agar esa butun ota-komponent yoki og'ir ro'yxat har 250ms'da qayta render "
            "bo'lsa, bu — aniq, o'lchangan muammo. 12-darsda aynan shu komponentni "
            "diagnostika qilamiz.</p>"
            "<h3>Bu kursda nimalarni o'rganamiz</h3>"
            "<p>Re-renderlarning haqiqiy sababi va ota-bola kaskadi, React.memo/useMemo/"
            "useCallback va ulardan qachon foydalanmaslik, React.lazy va Suspense orqali "
            "code splitting, uzun ro'yxatlar uchun virtualizatsiya, Context'ning "
            "qayta-render tuzog'i, useTransition/useDeferredValue, bundle hajmini tahlil "
            "qilish, Redux selector performance, Web Vitals va kundalik anti-patternlar. "
            "Kurs oxirida haqiqiy \"sekin komponentni topib tuzatish\" mashqini "
            "bajarasiz.</p>"
            "<h3>Flamegraph rangларини o'qish</h3>"
            "<p>Flamegraph'dagi har bir to'rtburchakning rangi ham ma'lumot beradi: "
            "sariq/to'q ranglar ko'proq vaqt olgan komponentlarni, ko'k/och ranglar "
            "tezroq render bo'lganlarni bildiradi (aniq rang sxemasi DevTools "
            "versiyasiga qarab farq qilishi mumkin, lekin nisbiy taqqoslash printsipi "
            "bir xil qoladi). \"Ranked\" ko'rinish esa shu commit ichida eng ko'p vaqt "
            "olgan komponentlarni kamayish tartibida ro'yxat qilib beradi — katta "
            "ilovada flamegraph'ni ko'zdan kechirgandan ko'ra, qayerdan boshlash "
            "kerakligini tezroq ko'rsatadi. Muhim nuance: bitta komponentning "
            "\"actualDuration\"i katta bo'lishi shart emas uning KODI sekin ekanini "
            "anglatmaydi — ko'pincha bu shunchaki uning ichida ko'p bola komponent "
            "borligidan (ularning render vaqti yig'indisi shu komponentga qo'shilib "
            "ko'rsatiladi). Shuning uchun \"nega bu komponent qayta render bo'ldi\" "
            "savolini har doim \"bu render qancha ODDIY REAL vaqt oldi\" savolidan "
            "oldin so'rash kerak — ba'zan javob \"umuman render bo'lmasligi kerak "
            "edi\" bo'ladi, va bu holatda vaqtni optimallashtirishning hojati yo'q, "
            "chunki render'ning o'zi keraksiz.</p>"
        ),
        "text_content_ru": (
            "<h3>«Кажется медленным» — это не измерение</h3>"
            "<p>Когда пользователь говорит «приложение работает медленно», это ощущение, "
            "а не точное число. Неопытный разработчик часто отвечает на это догадкой: "
            "«может, добавить useMemo», «может, обернуть этот компонент в memo». У "
            "такого подхода две проблемы: во-первых, реальный источник проблемы может "
            "быть совсем в другом месте; во-вторых, мемоизация не в том месте иногда "
            "СЗАМЕДЛЯЕТ приложение (увидим это в уроке 2). Первое и самое важное правило "
            "этого курса: <strong>сначала измерь, потом исправляй</strong>. Инструмент "
            "для этого — вкладка «Profiler» в расширении React DevTools.</p>"
            "<h3>Знакомство с React DevTools Profiler</h3>"
            "<p>В расширении React DevTools есть две вкладки: «Components» (для "
            "просмотра дерева) и «Profiler» (для измерения). На вкладке Profiler вы "
            "нажимаете кнопку записи (кружок), взаимодействуете с приложением как обычно "
            "(например, нажимаете фильтр или заполняете форму), затем останавливаете "
            "запись. В результате для каждого «commit» (момент, когда React применил "
            "изменения на экране) показывается: какие компоненты отрендерились, сколько "
            "времени занял каждый (flamegraph — каждый прямоугольник это компонент, "
            "ширина пропорциональна времени) и список компонентов, занявших больше всего "
            "времени, в виде «ranked».</p>"
            "<h3>Вопрос «почему этот компонент отрендерился?»</h3>"
            "<p>В настройках Profiler можно включить «Record why each component rendered "
            "while profiling». После включения, при клике на компонент вы видите ПОЧЕМУ "
            "он отрендерился — например «props changed: onOpen», «hooks changed: 1» или "
            "«parent component rendered». Именно последнее — «parent component "
            "rendered» — самое непонятное поведение React: компонент может "
            "отрендериться заново, даже если НИ ОДИН из его собственных props или state "
            "не изменился, просто потому что родительский компонент отрендерился. "
            "Разберём это подробно в уроке 2.</p>"
            "<h3>Диаграмма: догадка и измерение</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Пользователь: 'приложение медленное'\"] --> B{\"Какой подход выбрать?\"}\n"
            "  B -->|\"Догадка\"| C[\"Добавляем useMemo/memo\n"
            "причина неизвестна\"]\n"
            "  C --> D[\"Иногда не помогает\n"
            "или замедляет\"]\n"
            "  B -->|\"Измерение\"| E[\"Запись в Profiler\"]\n"
            "  E --> F[\"Смотрим какой компонент, сколько времени,\n"
            "почему отрендерился\"]\n"
            "  F --> G[\"Исправление под конкретную причину\"]\n"
            "  G --> H[\"Повторное измерение для подтверждения\"]\n"
            "</pre>"
            "<p>Диаграмма показывает: путь «догадки» ведёт к случайным правкам и иногда "
            "к ухудшению, путь «измерения» — к точной причине и подтверждённому "
            "исправлению. Каждый урок этого курса закрепляет именно второй путь.</p>"
            "<h3>Как читать цвета flamegraph</h3>"
            "<p>Цвет каждого прямоугольника во flamegraph тоже несёт информацию: жёлтые/"
            "тёмные оттенки означают компоненты, занявшие больше времени, "
            "синие/светлые — отрендерившиеся быстрее (точная цветовая схема может "
            "отличаться в разных версиях DevTools, но принцип относительного сравнения "
            "остаётся тем же). Вид «ranked» же выводит список компонентов этого commit "
            "по убыванию затраченного времени — в большом приложении это быстрее "
            "показывает, с чего начинать, чем разглядывание flamegraph целиком. Важный "
            "нюанс: большой «actualDuration» у компонента не обязательно означает, что "
            "именно его КОД медленный — часто это просто потому, что внутри него много "
            "дочерних компонентов (их суммарное время рендера добавляется к нему). "
            "Поэтому вопрос «почему этот компонент отрендерился заново» всегда стоит "
            "задавать раньше вопроса «сколько РЕАЛЬНОГО времени занял этот рендер» — "
            "иногда ответ звучит как «рендера вообще не должно было быть», и тогда "
            "оптимизировать время не нужно, потому что сам рендер был лишним.</p>"
            "<h3>Пример из реального кода этой платформы</h3>"
            "<p>Это не выдуманный пример: в файле <code>frontend/src/views/student/"
            "teamgame/StudentTeamGame.js</code> на строке 111 есть настоящий вызов "
            "<code>setInterval(tick, 250)</code> — это таймер, обновляющий оставшееся "
            "время вопроса в игре 4 раза в секунду (каждые 250мс). Каждый раз, когда "
            "запускается <code>tick()</code>, он обновляет состояние через "
            "<code>setTimeLeft(...)</code>, что перерендеривает компонент. Вопрос: это "
            "проблема? Вместо догадки правильный ответ — включить Profiler и "
            "посмотреть на этот компонент: если рендерится только цифра таймера и "
            "связанная с ней небольшая часть UI (а не вся страница), это обычно не "
            "проблема. Если же весь родительский компонент или тяжёлый список "
            "перерендериваются каждые 250мс — это уже конкретная, измеренная проблема. "
            "В уроке 12 мы продиагностируем именно этот компонент.</p>"
            "<h3>Что мы изучим в этом курсе</h3>"
            "<p>Реальную причину ре-рендеров и каскад от родителя к детям, React.memo/"
            "useMemo/useCallback и когда их не использовать, code splitting через React."
            "lazy и Suspense, виртуализацию длинных списков, ловушку перерендера через "
            "Context, useTransition/useDeferredValue, анализ размера бандла, "
            "производительность селекторов Redux, Web Vitals и повседневные "
            "антипаттерны. В конце курса вы выполните настоящее упражнение по поиску и "
            "исправлению медленного компонента.</p>"
        ),
        "code_content": (
            "// useRenderCount — har bir render'da hisoblagichni oshiradigan kichik hook.\n"
            "// DevTools Profiler'ni ochmasdan ham konsolda \"bu komponent nechta marta\n"
            "// render bo'ldi\" degan savolga tezkor javob olish uchun ishlatiladi.\n"
            "import { useRef, useEffect, useState, useCallback } from 'react';\n\n"
            "function useRenderCount(label) {\n"
            "  const countRef = useRef(0);\n"
            "  countRef.current += 1;\n"
            "  useEffect(() => {\n"
            "    console.log(`[render-count] ${label}: ${countRef.current}`);\n"
            "  });\n"
            "  return countRef.current;\n"
            "}\n\n"
            "// Demo: ota komponent state'i o'zgarganda bola komponent nega\n"
            "// qayta render bo'lishini ko'rsatadigan kichik ilova.\n"
            "function Child({ label }) {\n"
            "  const renders = useRenderCount(`Child(${label})`);\n"
            "  return (\n"
            "    <div style={{ padding: 8, border: '1px solid #ddd', marginTop: 4 }}>\n"
            "      {label} komponenti {renders} marta render bo'ldi\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "export default function RenderCountDemo() {\n"
            "  const [tick, setTick] = useState(0);\n"
            "  const [unrelated, setUnrelated] = useState(0);\n"
            "  const parentRenders = useRenderCount('Parent');\n\n"
            "  // Diqqat: bu funksiya har render'da YANGI reference bo'ladi — bu haqida\n"
            "  // 2-darsda batafsil gaplashamiz. Hozircha faqat kuzatib boring.\n"
            "  const handleTick = useCallback(() => setTick((t) => t + 1), []);\n\n"
            "  return (\n"
            "    <div style={{ fontFamily: 'sans-serif', padding: 16 }}>\n"
            "      <h4>Parent {parentRenders} marta render bo'ldi</h4>\n"
            "      <button onClick={handleTick}>tick: {tick}</button>\n"
            "      <button onClick={() => setUnrelated((n) => n + 1)}>\n"
            "        unrelated: {unrelated}\n"
            "      </button>\n"
            "      {/* Har ikkala tugma ham Parent'ni qayta render qiladi, demak\n"
            "          Child ham (memo qilinmagan bo'lsa) qayta render bo'ladi — hatto\n"
            "          \"unrelated\" tugmasi bosilganda ham, garchi Child hech qanday\n"
            "          bog'liq ma'lumot olmasa ham. */}\n"
            "      <Child label=\"A\" />\n"
            "      <Child label=\"B\" />\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// Alternativ: DevTools o'rniga dasturiy o'lchash uchun React'ning\n"
            "// o'rnatilgan <Profiler> komponenti (onRender callback bilan).\n"
            "// commit paytida real vaqt qiymatlarini beradi — CI'da yoki avtomatik\n"
            "// tekshiruvda foydali, DevTools esa qo'lda tekshirish uchun.\n"
            "import { Profiler } from 'react';\n\n"
            "function onRenderCallback(\n"
            "  id, phase, actualDuration, baseDuration, startTime, commitTime\n"
            ") {\n"
            "  console.log(\n"
            "    `[Profiler] ${id} (${phase}): actual=${actualDuration.toFixed(2)}ms, `\n"
            "    + `base=${baseDuration.toFixed(2)}ms`\n"
            "  );\n"
            "}\n\n"
            "export function ProfiledDemo() {\n"
            "  return (\n"
            "    <Profiler id=\"RenderCountDemo\" onRender={onRenderCallback}>\n"
            "      <RenderCountDemo />\n"
            "    </Profiler>\n"
            "  );\n"
            "}\n\n"
            "// \"Nega qayta render bo'ldi\" savolini qo'lda tekshirish uchun kichik\n"
            "// yordamchi hook — oldingi va joriy props'ni solishtirib, qaysi kalit\n"
            "// o'zgarganini konsolga chiqaradi. DevTools Profiler'ning \"why did this\n"
            "// render\" xususiyatiga o'xshash, lekin to'liq qo'lda va shaffof.\n"
            "function useWhyDidYouUpdate(name, props) {\n"
            "  const previousProps = useRef();\n"
            "  useEffect(() => {\n"
            "    if (previousProps.current) {\n"
            "      const allKeys = Object.keys({ ...previousProps.current, ...props });\n"
            "      const changed = {};\n"
            "      allKeys.forEach((key) => {\n"
            "        if (previousProps.current[key] !== props[key]) {\n"
            "          changed[key] = { from: previousProps.current[key], to: props[key] };\n"
            "        }\n"
            "      });\n"
            "      if (Object.keys(changed).length) {\n"
            "        console.log('[why-did-you-update]', name, changed);\n"
            "      }\n"
            "    }\n"
            "    previousProps.current = props;\n"
            "  });\n"
            "}\n\n"
            "// Foydalanish: ChildWithReason props o'zgarganda ANIQ qaysi prop\n"
            "// o'zgarganini ko'rsatadi — \"parent qayta render bo'lgani uchun\" degan\n"
            "// noaniq javob o'rniga.\n"
            "function ChildWithReason({ label, onOpen }) {\n"
            "  useWhyDidYouUpdate(`ChildWithReason(${label})`, { label, onOpen });\n"
            "  return <button onClick={onOpen}>{label}</button>;\n"
            "}\n"
        ),
        "code_content_ru": (
            "// useRenderCount — небольшой хук, увеличивающий счётчик при каждом рендере.\n"
            "// Используется, чтобы быстро получить ответ на вопрос «сколько раз\n"
            "// отрендерился этот компонент» без открытия DevTools Profiler.\n"
            "import { useRef, useEffect, useState, useCallback } from 'react';\n\n"
            "function useRenderCount(label) {\n"
            "  const countRef = useRef(0);\n"
            "  countRef.current += 1;\n"
            "  useEffect(() => {\n"
            "    console.log(`[render-count] ${label}: ${countRef.current}`);\n"
            "  });\n"
            "  return countRef.current;\n"
            "}\n\n"
            "// Демо: небольшое приложение, показывающее, почему дочерний компонент\n"
            "// перерендеривается при изменении state родителя.\n"
            "function Child({ label }) {\n"
            "  const renders = useRenderCount(`Child(${label})`);\n"
            "  return (\n"
            "    <div style={{ padding: 8, border: '1px solid #ddd', marginTop: 4 }}>\n"
            "      Компонент {label} отрендерился {renders} раз(а)\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "export default function RenderCountDemo() {\n"
            "  const [tick, setTick] = useState(0);\n"
            "  const [unrelated, setUnrelated] = useState(0);\n"
            "  const parentRenders = useRenderCount('Parent');\n\n"
            "  // Внимание: эта функция на каждом рендере — НОВАЯ ссылка — подробно\n"
            "  // об этом поговорим в уроке 2. Пока просто понаблюдайте.\n"
            "  const handleTick = useCallback(() => setTick((t) => t + 1), []);\n\n"
            "  return (\n"
            "    <div style={{ fontFamily: 'sans-serif', padding: 16 }}>\n"
            "      <h4>Parent отрендерился {parentRenders} раз(а)</h4>\n"
            "      <button onClick={handleTick}>tick: {tick}</button>\n"
            "      <button onClick={() => setUnrelated((n) => n + 1)}>\n"
            "        unrelated: {unrelated}\n"
            "      </button>\n"
            "      {/* Обе кнопки перерендеривают Parent, а значит и Child (если не\n"
            "          обёрнут в memo) — даже когда нажата кнопка \"unrelated\",\n"
            "          хотя Child не получает никаких связанных с ней данных. */}\n"
            "      <Child label=\"A\" />\n"
            "      <Child label=\"B\" />\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// Альтернатива: вместо DevTools — встроенный компонент <Profiler>\n"
            "// (с колбэком onRender) для программного измерения. Даёт реальные\n"
            "// значения времени во время commit — полезно в CI или автоматической\n"
            "// проверке, тогда как DevTools — для ручной проверки.\n"
            "import { Profiler } from 'react';\n\n"
            "function onRenderCallback(\n"
            "  id, phase, actualDuration, baseDuration, startTime, commitTime\n"
            ") {\n"
            "  console.log(\n"
            "    `[Profiler] ${id} (${phase}): actual=${actualDuration.toFixed(2)}ms, `\n"
            "    + `base=${baseDuration.toFixed(2)}ms`\n"
            "  );\n"
            "}\n\n"
            "export function ProfiledDemo() {\n"
            "  return (\n"
            "    <Profiler id=\"RenderCountDemo\" onRender={onRenderCallback}>\n"
            "      <RenderCountDemo />\n"
            "    </Profiler>\n"
            "  );\n"
            "}\n\n"
            "// Небольшой вспомогательный хук для ручной проверки вопроса «почему\n"
            "// перерендерился» — сравнивает предыдущие и текущие props и выводит в\n"
            "// консоль, какой именно ключ изменился. Похоже на функцию Profiler «why\n"
            "// did this render», но полностью вручную и прозрачно.\n"
            "function useWhyDidYouUpdate(name, props) {\n"
            "  const previousProps = useRef();\n"
            "  useEffect(() => {\n"
            "    if (previousProps.current) {\n"
            "      const allKeys = Object.keys({ ...previousProps.current, ...props });\n"
            "      const changed = {};\n"
            "      allKeys.forEach((key) => {\n"
            "        if (previousProps.current[key] !== props[key]) {\n"
            "          changed[key] = { from: previousProps.current[key], to: props[key] };\n"
            "        }\n"
            "      });\n"
            "      if (Object.keys(changed).length) {\n"
            "        console.log('[why-did-you-update]', name, changed);\n"
            "      }\n"
            "    }\n"
            "    previousProps.current = props;\n"
            "  });\n"
            "}\n\n"
            "// Использование: ChildWithReason точно покажет, какой именно prop\n"
            "// изменился, вместо расплывчатого «родитель перерендерился».\n"
            "function ChildWithReason({ label, onOpen }) {\n"
            "  useWhyDidYouUpdate(`ChildWithReason(${label})`, { label, onOpen });\n"
            "  return <button onClick={onOpen}>{label}</button>;\n"
            "}\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Profiler bilan haqiqiy render sessiyasini yozib oling",
            "task_title_ru": "Запишите реальную сессию рендера через Profiler",
            "task_description": (
                "Har qanday o'zingiz yozgan yoki oldingi kursdan qolgan React ilovasini "
                "(yoki ushbu darsdagi RenderCountDemo namunasini) oching. React DevTools "
                "kengaytmasining Profiler tab'ida \"Record why each component rendered\" "
                "sozlamasini yoqing, yozishni boshlang, ilova bilan bir necha marta "
                "o'zaro ta'sirlashing (tugma bosing, forma to'ldiring), so'ng to'xtating. "
                "Flamegraph'dan kamida ikkita komponentni tanlab, ularning render sababini "
                "(masalan \"props changed\", \"hooks changed\", \"parent rendered\") va "
                "actualDuration qiymatini yozib oling."
            ),
            "task_description_ru": (
                "Откройте любое написанное вами приложение на React (или оставшееся с "
                "прошлого курса, либо пример RenderCountDemo из этого урока). Включите "
                "настройку «Record why each component rendered» на вкладке Profiler "
                "расширения React DevTools, начните запись, несколько раз "
                "провзаимодействуйте с приложением (нажмите кнопку, заполните форму), "
                "затем остановите. Выберите на flamegraph минимум два компонента и "
                "запишите причину их рендера (например «props changed», «hooks "
                "changed», «parent rendered») и значение actualDuration."
            ),
            "task_requirements": (
                "Kamida ikkita komponentning render sababi va actualDuration qiymati "
                "yozma taqdim etilishi shart. Kamida bitta komponentda \"parent "
                "rendered\" sababi topilgan bo'lishi kerak."
            ),
            "task_requirements_ru": (
                "Обязательно письменно указать причину рендера и значение "
                "actualDuration минимум для двух компонентов. Минимум для одного "
                "компонента должна быть найдена причина «parent rendered»."
            ),
            "task_technologies": "React, React DevTools Profiler",
            "task_deadline_days": 4,
        },
        "sample": {
            "title": "Namuna: render sonini kuzatish",
            "description": "useRenderCount hook'i va o'rnatilgan <Profiler> komponenti bilan real render hisoblash namunasi.",
            "sample_type": "code",
            "code_files": [
                {"filename": "RenderCountDemo.jsx", "language": "jsx", "code": (
                    "import { useRef, useEffect, useState, useCallback, Profiler } from 'react';\n\n"
                    "function useRenderCount(label) {\n"
                    "  const countRef = useRef(0);\n"
                    "  countRef.current += 1;\n"
                    "  useEffect(() => { console.log(`${label}: ${countRef.current}`); });\n"
                    "  return countRef.current;\n"
                    "}\n\n"
                    "function Child({ label }) {\n"
                    "  const renders = useRenderCount(`Child(${label})`);\n"
                    "  return <div>{label}: {renders} render</div>;\n"
                    "}\n\n"
                    "export default function App() {\n"
                    "  const [tick, setTick] = useState(0);\n"
                    "  const [unrelated, setUnrelated] = useState(0);\n"
                    "  const onRender = (id, phase, actualDuration) =>\n"
                    "    console.log(`${id} (${phase}): ${actualDuration.toFixed(2)}ms`);\n"
                    "  return (\n"
                    "    <Profiler id=\"App\" onRender={onRender}>\n"
                    "      <button onClick={() => setTick((t) => t + 1)}>tick {tick}</button>\n"
                    "      <button onClick={() => setUnrelated((n) => n + 1)}>unrelated {unrelated}</button>\n"
                    "      <Child label=\"A\" />\n"
                    "      <Child label=\"B\" />\n"
                    "    </Profiler>\n"
                    "  );\n"
                    "}\n"
                )},
            ],
        },
        "exercises": [
            {
                "title": "Profiler nima uchun kerak",
                "title_ru": "Зачем нужен Profiler",
                "description": "React DevTools Profiler asosan nima uchun ishlatiladi?",
                "description_ru": "Для чего в основном используется React DevTools Profiler?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Kodni taxmin qilish o'rniga qaysi komponent qancha vaqt render bo'lganini o'lchash",
                    "CSS xatolarini topish",
                    "Backend so'rovlarini tezlashtirish",
                    "TypeScript xatolarini tekshirish",
                ],
                "options_ru": [
                    "Измерять, какой компонент сколько времени рендерился, вместо догадок",
                    "Находить ошибки в CSS",
                    "Ускорять запросы к бэкенду",
                    "Проверять ошибки TypeScript",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Darsning boshidagi \"avval o'lchang, keyin tuzating\" qoidasini eslang.",
                "hint_ru": "Вспомните правило из начала урока: «сначала измерь, потом исправляй».",
                "explanation": "Profiler kodni emas, balki render vaqtini va sababini o'lchaydi — bu tuzatishni taxmin emas, dalilga asoslaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Render sababini ko'rish",
                "title_ru": "Просмотр причины рендера",
                "description": (
                    "Bo'shliqni to'ldiring: Profiler sozlamalarida \"Record why each "
                    "component ___ while profiling\" katagini yoqish orqali har bir "
                    "komponentning render sababini ko'rish mumkin."
                ),
                "description_ru": (
                    "Заполните пропуск: включив в настройках Profiler опцию «Record why "
                    "each component ___ while profiling», можно увидеть причину рендера "
                    "каждого компонента."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "rendered",
                "hint": "Darsdagi Profiler sozlamasi nomini qidiring — inglizcha so'z.",
                "hint_ru": "Найдите название этой настройки Profiler в тексте урока — английское слово.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "O'lchash oqimi",
                "title_ru": "Поток измерения",
                "description": "\"Avval o'lchang, keyin tuzating\" yondashuvining to'g'ri tartibini joylashtiring.",
                "description_ru": "Расставьте по порядку шаги подхода «сначала измерь, потом исправляй».",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Profiler'da yozib olishni boshlash",
                    "Ilova bilan odatdagidek ishlash",
                    "Yozishni to'xtatib, flamegraph'ni ko'rish",
                    "Aniq sababga mos tuzatish kiritish",
                    "Qayta o'lchab, tuzatish ishlaganini tasdiqlash",
                ],
                "drag_items_ru": [
                    "Начать запись в Profiler",
                    "Работать с приложением как обычно",
                    "Остановить запись и посмотреть flamegraph",
                    "Внести исправление под конкретную причину",
                    "Измерить снова и подтвердить, что исправление сработало",
                ],
                "correct_order": [
                    "Profiler'da yozib olishni boshlash",
                    "Ilova bilan odatdagidek ishlash",
                    "Yozishni to'xtatib, flamegraph'ni ko'rish",
                    "Aniq sababga mos tuzatish kiritish",
                    "Qayta o'lchab, tuzatish ishlaganini tasdiqlash",
                ],
                "hint": "Yozib olish har doim eng boshida, tasdiqlash — eng oxirida bo'ladi.",
                "hint_ru": "Запись всегда в самом начале, подтверждение — в самом конце.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 1,
        "title": "2-Re-renderlar: sabab va ota-bola kaskadi",
        "title_ru": "2-Ре-рендеры: причина и каскад от родителя к детям",
        "points_reward": 15,
        "text_content": (
            "<h3>Render va re-render — aniq ta'rif</h3>"
            "<p>\"Render\" — bu React komponent funksiyasini chaqirib, u qaytargan JSX'dan "
            "element daraxtini qurish jarayoni. \"Commit\" — React shu daraxtni haqiqiy "
            "DOM'ga qo'llash bosqichi (faqat o'zgargan qismlar yangilanadi). \"Re-render\" "
            "esa — komponent funksiyasi ikkinchi (yoki keyingi) marta chaqirilishi. Muhim "
            "nuance: re-render DOM'ni albatta o'zgartiradi degani emas — React avval yangi "
            "va eski elementlarni taqqoslaydi (reconciliation) va faqat haqiqatan "
            "farq qilgan joylarni DOM'ga qo'llaydi. Lekin komponent funksiyasining o'zi "
            "baribir qayta ISHGA TUSHADI — va agar u ichida qimmat hisob-kitob bo'lsa, "
            "bu hisob-kitob DOM o'zgarmasa ham qayta bajariladi.</p>"
            "<h3>Re-render'ga olib keladigan to'rtta sabab</h3>"
            "<p><strong>1. O'z state'i o'zgarishi.</strong> <code>useState</code> yoki "
            "<code>useReducer</code>'ning setter funksiyasi chaqirilsa (yangi qiymat "
            "eskisidan farq qilsa), shu komponent qayta render bo'ladi. "
            "<strong>2. Props o'zgarishi.</strong> Ota komponent yangi qiymat bilan prop "
            "uzatsa. <strong>3. Context qiymati o'zgarishi.</strong> Komponent "
            "<code>useContext</code> orqali o'qiyotgan Provider'ning <code>value</code>si "
            "o'zgarsa (6-darsda batafsil). <strong>4. Ota komponent qayta render "
            "bo'lishi.</strong> Bu — eng ko'p tushunilmaydigani: <strong>React'da bola "
            "komponent DEFAULT holatda ota render bo'lganda ham qayta render "
            "bo'ladi — hatto o'zining props'i AYNAN bir xil qolgan bo'lsa ham</strong>. "
            "React bu holatda \"ehtiyot chorasi sifatida\" har doim qayta render qiladi, "
            "chunki u props obyektlarini chuqur solishtirmaydi (faqat "
            "<code>React.memo</code> bilan o'raganda solishtiradi — 3-darsda ko'ramiz).</p>"
            "<h3>Haqiqiy kaskad: StudentCourses.js'dagi CourseCard</h3>"
            "<p>Bu — ushbu platformaning haqiqiy kodi: <code>frontend/src/views/student/"
            "courses/Courses/StudentCourses.js</code> ichida <code>CourseCard</code> "
            "komponenti <code>React.memo</code> bilan o'ralmagan, oddiy funksiya sifatida "
            "yozilgan. Uni chaqirgan joyda: <code>&lt;CourseCard key={{course.id}} "
            "course={{course}} onOpen={{() =&gt; goToCourse(course)}} /&gt;</code> — "
            "e'tibor bering, <code>onOpen</code> — har safar <code>StudentCourses</code> "
            "qayta render bo'lganda YANGI yaratiladigan strelka funksiya. Demak: "
            "foydalanuvchi qidiruv maydoniga bitta harf yozganda (<code>search</code> "
            "state'i o'zgaradi), butun <code>StudentCourses</code> qayta render bo'ladi, "
            "bu esa <code>displayed.map(...)</code> ichidagi HAR BIR "
            "<code>CourseCard</code>ni ham qayta render qiladi — hatto ko'rsatilayotgan "
            "kurslar ro'yxati filtrlangandan keyin deyarli bir xil qolsa ham, va hatto "
            "aylanmagan kartalarning o'z ma'lumotlari (nomi, progressi) umuman "
            "o'zgarmagan bo'lsa ham.</p>"
            "<h3>Diagramma: bitta state o'zgarishi, ko'p qayta render</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  S[\"search state o'zgaradi\n"
            "(foydalanuvchi harf yozadi)\"] --> P[\"StudentCourses qayta render bo'ladi\"]\n"
            "  P --> C1[\"CourseCard #1\n"
            "qayta render (props bir xil)\"]\n"
            "  P --> C2[\"CourseCard #2\n"
            "qayta render (props bir xil)\"]\n"
            "  P --> C3[\"CourseCard #3\n"
            "qayta render (props bir xil)\"]\n"
            "  P --> CN[\"... har bir ko'rinadigan karta\"]\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: bitta kichik state o'zgarishi (bitta harf) "
            "butun ro'yxat bo'ylab tarqaladi — bu React'ning standart xatti-harakati, xato "
            "emas. Muammo faqat shunda paydo bo'ladiki, agar kartalar soni juda ko'p "
            "bo'lsa YOKI har bir kartaning render funksiyasi ichida qimmat hisob-kitob "
            "bo'lsa.</p>"
            "<h3>Bu har doim muammomi? Halol javob</h3>"
            "<p>Yo'q. React'ning reconciliation jarayoni odatda juda tez — o'nlab oddiy "
            "komponentlarni qayta render qilish (masalan, <code>StudentCourses</code>dagi "
            "bir necha o'nlab <code>CourseCard</code>) sekundning mingdan bir ulushini "
            "oladi va foydalanuvchi buni sezmaydi ham. Bu kaskad haqiqiy muammoga "
            "aylanishi uchun odatda ikkitadan biri kerak: (1) bola komponentlar soni "
            "yuzlab/minglab bo'lishi (5-darsda virtualizatsiya), yoki (2) bola "
            "komponentning render funksiyasi ichida chindan ham qimmat hisob-kitob "
            "bo'lishi (masalan, katta massivni saralash yoki filtrlash har render'da). "
            "Shuning uchun 3-darsda <code>React.memo</code>ni o'rganamiz — lekin uni "
            "HAR bir komponentga tiqishtirish o'rniga, aynan shu ikkita holatni aniqlab, "
            "faqat kerakli joyga qo'llashni.</p>"
            "<h3>Xulosa</h3>"
            "<p>Re-render kaskadi — React'ning atayin qilingan, oldindan aytib bo'ladigan "
            "xatti-harakati: ota render bo'lsa, bolalar ham render bo'ladi, props bir xil "
            "qolgan bo'lsa ham. Buni \"xato\" deb emas, \"standart xavfsiz holat\" deb "
            "bilish kerak — optimallashtirish esa faqat o'lchov shuni ko'rsatganda "
            "kerak bo'ladi.</p>"
        ),
        "text_content_ru": (
            "<h3>Рендер и ре-рендер — точное определение</h3>"
            "<p>«Рендер» — это процесс вызова функции React-компонента, в результате "
            "которого из возвращённого JSX строится дерево элементов. «Commit» — этап, "
            "когда React применяет это дерево к настоящему DOM (обновляются только "
            "изменившиеся части). «Ре-рендер» — это повторный (второй и последующий) "
            "вызов функции компонента. Важный нюанс: ре-рендер не обязательно меняет "
            "DOM — React сначала сравнивает новые и старые элементы (reconciliation) и "
            "применяет к DOM только реально отличающиеся места. Но сама функция "
            "компонента всё равно ЗАПУСКАЕТСЯ заново — и если внутри неё есть дорогое "
            "вычисление, оно выполнится заново, даже если DOM не изменится.</p>"
            "<h3>Четыре причины ре-рендера</h3>"
            "<p><strong>1. Изменение собственного state.</strong> Вызван setter из "
            "<code>useState</code> или <code>useReducer</code> (новое значение "
            "отличается от старого) — этот компонент перерендеривается. "
            "<strong>2. Изменение props.</strong> Родитель передал новое значение "
            "пропа. <strong>3. Изменение значения Context.</strong> Значение "
            "<code>value</code> Provider'а, который компонент читает через "
            "<code>useContext</code>, изменилось (подробно в уроке 6). "
            "<strong>4. Перерендер родителя.</strong> Это самое непонятное: <strong>в "
            "React дочерний компонент по УМОЛЧАНИЮ перерендеривается при перерендере "
            "родителя — даже если его собственные props остались АБСОЛЮТНО теми "
            "же</strong>. React делает это «на всякий случай», потому что не сравнивает "
            "объекты props глубоко (сравнение появляется только при оборачивании в "
            "<code>React.memo</code> — увидим в уроке 3).</p>"
            "<h3>Реальный каскад: CourseCard в StudentCourses.js</h3>"
            "<p>Это настоящий код этой платформы: в файле <code>frontend/src/views/"
            "student/courses/Courses/StudentCourses.js</code> компонент "
            "<code>CourseCard</code> написан как обычная функция, НЕ обёрнутая в "
            "<code>React.memo</code>. В месте вызова: <code>&lt;CourseCard "
            "key={{course.id}} course={{course}} onOpen={{() =&gt; "
            "goToCourse(course)}} /&gt;</code> — обратите внимание, <code>onOpen</code> "
            "— это стрелочная функция, создаваемая НОВОЙ каждый раз, когда "
            "<code>StudentCourses</code> перерендеривается. Значит: когда пользователь "
            "вводит одну букву в поле поиска (меняется state <code>search</code>), весь "
            "<code>StudentCourses</code> перерендеривается, а это перерендеривает "
            "КАЖДЫЙ <code>CourseCard</code> внутри <code>displayed.map(...)</code> — "
            "даже если список отфильтрованных курсов почти не изменился, и даже если "
            "собственные данные непоказанных карточек (название, прогресс) вообще не "
            "изменились.</p>"
            "<h3>Диаграмма: одно изменение state, много ре-рендеров</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  S[\"Меняется state search\n"
            "(пользователь вводит букву)\"] --> P[\"StudentCourses перерендеривается\"]\n"
            "  P --> C1[\"CourseCard #1\n"
            "перерендер (props те же)\"]\n"
            "  P --> C2[\"CourseCard #2\n"
            "перерендер (props те же)\"]\n"
            "  P --> C3[\"CourseCard #3\n"
            "перерендер (props те же)\"]\n"
            "  P --> CN[\"... каждая видимая карточка\"]\n"
            "</pre>"
            "<p>Диаграмма показывает: одно небольшое изменение state (одна буква) "
            "распространяется по всему списку — это стандартное поведение React, не "
            "ошибка. Проблемой это становится, только если карточек очень много ИЛИ "
            "функция рендера каждой карточки содержит дорогое вычисление.</p>"
            "<h3>Это всегда проблема? Честный ответ</h3>"
            "<p>Нет. Процесс reconciliation в React обычно очень быстрый — "
            "перерендерить несколько десятков простых компонентов (например, "
            "несколько десятков <code>CourseCard</code> в <code>StudentCourses</code>) "
            "занимает тысячные доли секунды, и пользователь этого даже не замечает. Чтобы "
            "этот каскад стал реальной проблемой, обычно нужно одно из двух: (1) "
            "количество дочерних компонентов исчисляется сотнями/тысячами (урок 5, "
            "виртуализация), или (2) функция рендера дочернего компонента содержит "
            "действительно дорогое вычисление (например, сортировку или фильтрацию "
            "большого массива при каждом рендере). Поэтому в уроке 3 мы изучим "
            "<code>React.memo</code> — но не для того, чтобы впихнуть его в КАЖДЫЙ "
            "компонент, а чтобы точно определить эти два случая и применить только там, "
            "где нужно.</p>"
            "<h3>Итог</h3>"
            "<p>Каскад ре-рендеров — намеренное, предсказуемое поведение React: если "
            "родитель рендерится, дети тоже рендерятся, даже если props остались теми "
            "же. Это стоит воспринимать не как «баг», а как «безопасное поведение по "
            "умолчанию» — оптимизация нужна только тогда, когда измерение это "
            "подтверждает.</p>"
        ),
        "code_content": (
            "// Kaskadni ko'rsatuvchi kichik demo: Parent'da ikkita mustaqil state bor.\n"
            "// \"search\" — StudentCourses'dagi haqiqiy qidiruv maydoniga o'xshaydi.\n"
            "// \"unrelated\" — kartalarga umuman aloqasi yo'q boshqa state.\n"
            "import { useState } from 'react';\n\n"
            "function Card({ item, onOpen, renderLogRef }) {\n"
            "  // Har render'da hisoblagichni oshiramiz — DevTools'siz ham ko'rish uchun.\n"
            "  renderLogRef.current[item.id] = (renderLogRef.current[item.id] || 0) + 1;\n"
            "  return (\n"
            "    <div style={{ border: '1px solid #ddd', padding: 8, marginTop: 4 }}>\n"
            "      <span>{item.title} — {renderLogRef.current[item.id]} marta render</span>\n"
            "      <button onClick={onOpen} style={{ marginLeft: 8 }}>Ochish</button>\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "export default function CascadeDemo() {\n"
            "  const [search, setSearch] = useState('');\n"
            "  const [unrelated, setUnrelated] = useState(0);\n"
            "  const renderLogRef = { current: {} }; // demo uchun soddalashtirilgan\n\n"
            "  const items = [\n"
            "    { id: 1, title: 'React Asoslari' },\n"
            "    { id: 2, title: 'Redux Toolkit' },\n"
            "    { id: 3, title: 'Next.js va SSR' },\n"
            "  ].filter((c) => c.title.toLowerCase().includes(search.toLowerCase()));\n\n"
            "  return (\n"
            "    <div style={{ fontFamily: 'sans-serif', padding: 16 }}>\n"
            "      <input\n"
            "        value={search}\n"
            "        onChange={(e) => setSearch(e.target.value)}\n"
            "        placeholder=\"Qidirish...\"\n"
            "      />\n"
            "      <button onClick={() => setUnrelated((n) => n + 1)}>\n"
            "        unrelated: {unrelated}\n"
            "      </button>\n"
            "      {/* HAR IKKALA holatda ham (search yoki unrelated o'zgarganda)\n"
            "          quyidagi barcha Card'lar qayta render bo'ladi, chunki ularning\n"
            "          ota komponenti — CascadeDemo — qayta render bo'ldi. */}\n"
            "      {items.map((item) => (\n"
            "        <Card\n"
            "          key={item.id}\n"
            "          item={item}\n"
            "          renderLogRef={renderLogRef}\n"
            "          onOpen={() => console.log('ochildi:', item.title)}\n"
            "        />\n"
            "      ))}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// Solishtirish uchun: StudentCourses.js'dagi haqiqiy naqsh (soddalashtirilgan\n"
            "// iqtibos) — CourseCard React.memo bilan o'ralmagan, onOpen inline strelka:\n"
            "//\n"
            "//   {displayed.map((course) => (\n"
            "//       <CourseCard key={course.id} course={course}\n"
            "//                   onOpen={() => goToCourse(course)} />\n"
            "//   ))}\n"
            "//\n"
            "// 3-darsda aynan shu ikki qatorni React.memo + useCallback bilan qanday\n"
            "// o'zgartirish (va qachon buning arzishi) ko'ramiz.\n\n"
            "// Konsolda barcha kartalarning render sonini bir joyda ko'rish uchun\n"
            "// kichik yordamchi komponent — katta ro'yxatlarda foydali.\n"
            "function RenderSummary({ renderLogRef }) {\n"
            "  const entries = Object.entries(renderLogRef.current);\n"
            "  const total = entries.reduce((sum, [, count]) => sum + count, 0);\n"
            "  return (\n"
            "    <p style={{ fontSize: 12, color: '#888' }}>\n"
            "      Jami render'lar: {total} ({entries.length} ta karta bo'yicha)\n"
            "    </p>\n"
            "  );\n"
            "}\n\n"
            "// Taqqoslash uchun: agar CourseCard'ni React.memo bilan o'rasak-u, lekin\n"
            "// onOpen'ni useCallback qilmasak, memo befoyda bo'ladi — chunki har\n"
            "// render'da yangi onOpen reference kelib, shallow-equal har doim\n"
            "// \"props o'zgardi\" deydi. Bu holatni 3-darsda to'g'irlaymiz.\n"
            "import { memo } from 'react';\n"
            "const CourseCardNaiveMemo = memo(function CourseCardNaiveMemo({ course, onOpen }) {\n"
            "  return <div>{course.title}<button onClick={onOpen}>Ochish</button></div>;\n"
            "});\n"
        ),
        "code_content_ru": (
            "// Небольшое демо каскада: у Parent есть два независимых state.\n"
            "// \"search\" — похоже на настоящее поле поиска в StudentCourses.\n"
            "// \"unrelated\" — state, вообще не связанный с карточками.\n"
            "import { useState } from 'react';\n\n"
            "function Card({ item, onOpen, renderLogRef }) {\n"
            "  // Увеличиваем счётчик на каждом рендере — чтобы видеть без DevTools.\n"
            "  renderLogRef.current[item.id] = (renderLogRef.current[item.id] || 0) + 1;\n"
            "  return (\n"
            "    <div style={{ border: '1px solid #ddd', padding: 8, marginTop: 4 }}>\n"
            "      <span>{item.title} — рендер №{renderLogRef.current[item.id]}</span>\n"
            "      <button onClick={onOpen} style={{ marginLeft: 8 }}>Открыть</button>\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "export default function CascadeDemo() {\n"
            "  const [search, setSearch] = useState('');\n"
            "  const [unrelated, setUnrelated] = useState(0);\n"
            "  const renderLogRef = { current: {} }; // упрощено для демо\n\n"
            "  const items = [\n"
            "    { id: 1, title: 'React Asoslari' },\n"
            "    { id: 2, title: 'Redux Toolkit' },\n"
            "    { id: 3, title: 'Next.js va SSR' },\n"
            "  ].filter((c) => c.title.toLowerCase().includes(search.toLowerCase()));\n\n"
            "  return (\n"
            "    <div style={{ fontFamily: 'sans-serif', padding: 16 }}>\n"
            "      <input\n"
            "        value={search}\n"
            "        onChange={(e) => setSearch(e.target.value)}\n"
            "        placeholder=\"Поиск...\"\n"
            "      />\n"
            "      <button onClick={() => setUnrelated((n) => n + 1)}>\n"
            "        unrelated: {unrelated}\n"
            "      </button>\n"
            "      {/* В ОБОИХ случаях (при изменении search или unrelated) все\n"
            "          Card ниже перерендерятся, потому что перерендерился их\n"
            "          родитель — CascadeDemo. */}\n"
            "      {items.map((item) => (\n"
            "        <Card\n"
            "          key={item.id}\n"
            "          item={item}\n"
            "          renderLogRef={renderLogRef}\n"
            "          onOpen={() => console.log('открыт:', item.title)}\n"
            "        />\n"
            "      ))}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// Для сравнения: реальный паттерн из StudentCourses.js (упрощённая\n"
            "// цитата) — CourseCard не обёрнут в React.memo, onOpen — инлайн-стрелка:\n"
            "//\n"
            "//   {displayed.map((course) => (\n"
            "//       <CourseCard key={course.id} course={course}\n"
            "//                   onOpen={() => goToCourse(course)} />\n"
            "//   ))}\n"
            "//\n"
            "// В уроке 3 посмотрим, как изменить именно эти две строки с помощью\n"
            "// React.memo + useCallback (и когда это того стоит).\n\n"
            "// Небольшой вспомогательный компонент, чтобы видеть общее число\n"
            "// рендеров всех карточек в одном месте — полезно на больших списках.\n"
            "function RenderSummary({ renderLogRef }) {\n"
            "  const entries = Object.entries(renderLogRef.current);\n"
            "  const total = entries.reduce((sum, [, count]) => sum + count, 0);\n"
            "  return (\n"
            "    <p style={{ fontSize: 12, color: '#888' }}>\n"
            "      Всего рендеров: {total} (по {entries.length} карточкам)\n"
            "    </p>\n"
            "  );\n"
            "}\n\n"
            "// Для сравнения: если обернуть CourseCard в React.memo, но не сделать\n"
            "// onOpen через useCallback, memo не даст пользы — потому что на каждом\n"
            "// рендере приходит новая ссылка onOpen, и shallow-equal всегда скажет\n"
            "// «props изменились». Исправим это в уроке 3.\n"
            "import { memo } from 'react';\n"
            "const CourseCardNaiveMemo = memo(function CourseCardNaiveMemo({ course, onOpen }) {\n"
            "  return <div>{course.title}<button onClick={onOpen}>Открыть</button></div>;\n"
            "});\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Re-render kaskadini isbotlang",
            "task_title_ru": "Докажите каскад ре-рендеров",
            "task_description": (
                "Ushbu darsdagi CascadeDemo namunasiga o'xshash kichik komponent "
                "quring: bitta ota komponentda ikkita mustaqil state (masalan, "
                "\"search\" va \"unrelated\") bo'lsin, va ota kamida uchta bola "
                "komponentni render qilsin. Har bir bola komponentga useRef orqali "
                "render hisoblagichini qo'shing. \"unrelated\" state'i o'zgarganda "
                "ham HAMMA bola komponentlar qayta render bo'lishini isbotlang, va "
                "buning sababini (2-darsdagi to'rtta sababdan qaysi biri) yozing."
            ),
            "task_description_ru": (
                "Постройте небольшой компонент по образцу CascadeDemo из этого "
                "урока: пусть в одном родительском компоненте будет два "
                "независимых state (например, «search» и «unrelated»), а родитель "
                "рендерит минимум три дочерних компонента. Добавьте каждому "
                "дочернему компоненту счётчик рендеров через useRef. Докажите, что "
                "при изменении state «unrelated» ВСЕ дочерние компоненты "
                "перерендериваются, и напишите, какая из четырёх причин урока 2 "
                "это объясняет."
            ),
            "task_requirements": (
                "Kamida uchta bola komponent va har birida render hisoblagich "
                "bo'lishi shart. \"unrelated\" o'zgarganda barcha hisoblagichlar "
                "oshgani skrinshot yoki konsol logi bilan tasdiqlanishi kerak."
            ),
            "task_requirements_ru": (
                "Обязательны минимум три дочерних компонента, каждый со счётчиком "
                "рендеров. Увеличение всех счётчиков при изменении «unrelated» "
                "должно быть подтверждено скриншотом или логом консоли."
            ),
            "task_technologies": "React, useState, useRef",
            "task_deadline_days": 4,
        },
        "sample": {
            "title": "Namuna: kaskad re-render demo",
            "description": "Bitta state o'zgarishi bir nechta bola komponentni qanday qayta render qilishini ko'rsatuvchi ishlaydigan misol.",
            "sample_type": "code",
            "code_files": [
                {"filename": "CascadeDemo.jsx", "language": "jsx", "code": (
                    "import { useState, useRef } from 'react';\n\n"
                    "function Card({ item, onOpen }) {\n"
                    "  const renders = useRef(0);\n"
                    "  renders.current += 1;\n"
                    "  return (\n"
                    "    <div>{item.title} — render #{renders.current}"
                    " <button onClick={onOpen}>Ochish</button></div>\n"
                    "  );\n"
                    "}\n\n"
                    "export default function App() {\n"
                    "  const [search, setSearch] = useState('');\n"
                    "  const items = [{ id: 1, title: 'A' }, { id: 2, title: 'B' }]\n"
                    "    .filter((c) => c.title.toLowerCase().includes(search.toLowerCase()));\n"
                    "  return (\n"
                    "    <div>\n"
                    "      <input value={search} onChange={(e) => setSearch(e.target.value)} />\n"
                    "      {items.map((item) => (\n"
                    "        <Card key={item.id} item={item} onOpen={() => {}} />\n"
                    "      ))}\n"
                    "    </div>\n"
                    "  );\n"
                    "}\n"
                )},
            ],
        },
        "exercises": [
            {
                "title": "To'rtinchi sabab",
                "title_ru": "Четвёртая причина",
                "description": "Bola komponent qayta render bo'lishining eng ko'p tushunilmaydigan sababi qaysi?",
                "description_ru": "Какая причина ре-рендера дочернего компонента понимается хуже всего?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Ota komponent qayta render bo'lgani, hatto props bir xil qolsa ham",
                    "CSS fayli o'zgargani",
                    "Brauzer versiyasi eskirgani",
                    "Internet tezligi pasaygani",
                ],
                "options_ru": [
                    "Родитель перерендерился, даже если props остались теми же",
                    "Изменился CSS-файл",
                    "Устарела версия браузера",
                    "Снизилась скорость интернета",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Darsda \"eng ko'p tushunilmaydigani\" deb alohida ta'kidlangan sababni eslang.",
                "hint_ru": "Вспомните причину, которая в уроке отдельно названа «самой непонятной».",
                "explanation": "React default holatda bola komponentlarni ota render bo'lganda qayta render qiladi, props o'zgarmagan bo'lsa ham — bu React.memo bilan o'zgartiriladi (3-dars).",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "StudentCourses'dagi inline callback",
                "title_ru": "Инлайн-колбэк в StudentCourses",
                "description": (
                    "Bo'shliqni to'ldiring: StudentCourses.js'da CourseCard'ga uzatilgan "
                    "\"onOpen={() => goToCourse(course)}\" — bu har render'da yangi "
                    "yaratiladigan ___ funksiya."
                ),
                "description_ru": (
                    "Заполните пропуск: в StudentCourses.js переданный CourseCard "
                    "\"onOpen={() => goToCourse(course)}\" — это ___ функция, создаваемая "
                    "заново на каждом рендере."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "inline",
                "hint": "Darsda ishlatilgan atama — \"o'ralmagan, joyida yozilgan\" funksiya turi.",
                "hint_ru": "Термин из урока — тип функции, «написанной прямо на месте».",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Kaskad qachon muammo bo'ladi",
                "title_ru": "Когда каскад становится проблемой",
                "description": "Render-commit-reconciliation jarayonini to'g'ri tartibda joylashtiring.",
                "description_ru": "Расставьте по порядку этапы рендер-commit-reconciliation.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "State yoki props o'zgaradi",
                    "Komponent funksiyasi qayta chaqiriladi (render)",
                    "React yangi va eski elementlarni solishtiradi (reconciliation)",
                    "Faqat farq qilgan qismlar DOM'ga qo'llaniladi (commit)",
                ],
                "drag_items_ru": [
                    "Меняется state или props",
                    "Функция компонента вызывается заново (рендер)",
                    "React сравнивает новые и старые элементы (reconciliation)",
                    "Только отличающиеся части применяются к DOM (commit)",
                ],
                "correct_order": [
                    "State yoki props o'zgaradi",
                    "Komponent funksiyasi qayta chaqiriladi (render)",
                    "React yangi va eski elementlarni solishtiradi (reconciliation)",
                    "Faqat farq qilgan qismlar DOM'ga qo'llaniladi (commit)",
                ],
                "hint": "Sabab har doim eng boshida, DOM'ga qo'llash — eng oxirida.",
                "hint_ru": "Причина всегда в начале, применение к DOM — в конце.",
                "difficulty_level": "Hard",
                "points": 15,
            },
        ],
    },
    {
        "order": 2,
        "title": "3-React.memo, useMemo, useCallback — va ulardan qachon FOYDALANMASLIK kerak",
        "title_ru": "3-React.memo, useMemo, useCallback — и когда их НЕ стоит использовать",
        "points_reward": 15,
        "text_content": (
            "<h3>Uchta vosita, uchta aniq vazifa</h3>"
            "<p><code>React.memo(Component)</code> — komponentni o'raydi va, agar yangi "
            "props oldingi render'dagi props bilan \"shallow equal\" (yuza taqqoslash — "
            "har bir kalitning <code>===</code> orqali solishtirilishi) bo'lsa, "
            "komponentni QAYTA RENDER QILMAYDI, oldingi natijani qayta ishlatadi. "
            "<code>useMemo(fn, deps)</code> — HISOBLANGAN QIYMATNI keshlaydi: "
            "<code>deps</code> massivi o'zgarmaguncha, <code>fn()</code> qayta "
            "chaqirilmaydi, oldingi natija qaytariladi. <code>useCallback(fn, deps)</code> "
            "— FUNKSIYA REFERENSINI keshlaydi; aslida <code>useCallback(fn, deps)</code> "
            "— bu shunchaki <code>useMemo(() =&gt; fn, deps)</code>ning qisqartmasi. "
            "Uchalasi ham bitta umumiy g'oyaga xizmat qiladi: \"agar kirish "
            "ma'lumotlari (props yoki deps) o'zgarmagan bo'lsa, qayta ishlashning hojati "
            "yo'q\".</p>"
            "<h3>Amalda: CourseCard'ni React.memo bilan o'rash</h3>"
            "<p>2-darsda ko'rgan <code>StudentCourses.js</code>dagi holatni "
            "eslaymiz: <code>CourseCard</code> memo qilinmagan, "
            "<code>onOpen={{() =&gt; goToCourse(course)}}</code> esa har render'da yangi "
            "funksiya. Agar <code>CourseCard</code>ni <code>React.memo</code> bilan "
            "o'rasak-u, lekin <code>onOpen</code>ni o'zgartirmasak, memo HECH QANDAY "
            "foyda bermaydi — chunki har render'da <code>onOpen</code> yangi "
            "reference bo'lgani uchun shallow-equal taqqoslash har doim \"props "
            "o'zgardi\" deb topadi. To'g'ri yechim ikkalasini birga qo'llash: ota "
            "komponentda <code>const handleOpen = useCallback((courseId) =&gt; "
            "navigate(`/student/courses/${{courseId}}`), [navigate])</code> deb bitta "
            "barqaror funksiya yaratib, uni HAMMA kartalarga bir xil reference sifatida "
            "uzatish (<code>onOpen={{handleOpen}}</code>), ichkarida esa "
            "<code>onOpen(course.id)</code> deb chaqirish. Shunda "
            "<code>React.memo</code> endi haqiqiy foyda beradi: qidiruv maydoniga harf "
            "yozilganda, faqat filtrlash natijasida RO'YXATDAN CHIQQAN yoki QO'SHILGAN "
            "kartalar qayta render bo'ladi, qolganlari — yo'q.</p>"
            "<h3>Qachon FOYDALANMASLIK kerak — StudentCourses.js'ning o'zidan misol</h3>"
            "<p>Ayni shu faylda <code>displayed</code> va <code>categoryCounts</code> "
            "o'zgaruvchilari HAR RENDER'DA oddiy <code>.filter()</code>/<code>.map()</code> "
            "orqali qayta hisoblanadi — <code>useMemo</code>siz. Bu — XATO EMAS, TO'G'RI "
            "QAROR: talabaning kurslar ro'yxati odatda bir necha o'nlab elementdan "
            "oshmaydi, filtrlash operatsiyasi O(n) va juda arzon, va "
            "<code>useMemo</code>ning o'zi ham \"deps massivi o'zgarganmi\" deb "
            "solishtirish uchun vaqt sarflaydi — bu holatda solishtirish narxi "
            "hisoblashning o'zidan farq qilmaydi yoki undan qimmatroq bo'lishi ham "
            "mumkin. <strong>Amaliy qoida:</strong> <code>useMemo</code>/"
            "<code>useCallback</code>ni faqat quyidagi holatlarda qo'shing: (1) Profiler "
            "hisoblash chindan ham sezilarli vaqt (bir necha millisekund va undan ko'p) "
            "olayotganini ko'rsatgan bo'lsa, VA bu komponent tez-tez qayta render "
            "bo'lsa; yoki (2) natija <code>React.memo</code>ga uzatiladigan prop "
            "bo'lib, uning barqaror reference'i chindan ham bolaning qayta render "
            "bo'lishini oldini olishi kerak bo'lsa (yuqoridagi <code>handleOpen</code> "
            "kabi).</p>"
            "<h3>Haddan tashqari memoizatsiya nega sekinlashtiradi</h3>"
            "<p><code>useMemo</code>/<code>useCallback</code> \"bepul\" emas: har "
            "render'da React baribir <code>deps</code> massividagi har bir elementni "
            "eskisi bilan solishtiradi, va keshlangan qiymatni xotirada saqlab turadi. "
            "Agar deps massivi HAR RENDER'DA o'zgaradigan qiymat (masalan, inline "
            "obyekt yoki massiv literal) bo'lsa, memoizatsiya HECH QANDAY foyda bermaydi "
            "— hisoblash baribir har safar qayta bajariladi — lekin solishtirish "
            "narxini qo'shimcha to'laysiz. Bundan tashqari, har bir "
            "<code>useMemo</code>/<code>useCallback</code> kodni o'qishni "
            "qiyinlashtiradi: endi o'quvchi \"bu qiymat qachon yangilanadi\" deb "
            "deps massivini tahlil qilishi kerak, oddiy o'zgaruvchi o'rniga. Ko'plab "
            "yirik jamoalar bu haqda bir xil xulosaga kelishgan: \"memoizatsiyani "
            "standart amaliyot emas, maqsadli vosita sifatida ishlating\".</p>"
            "<h3>Diagramma: memoizatsiya haqida qaror qabul qilish</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Profiler'da sekinlik o'lchandimi?\"] -->|\"Yo'q\"| B[\"Memoizatsiya "
            "shart emas — kodni oddiy qoldiring\"]\n"
            "  A -->|\"Ha\"| C{\"Sabab: qimmat hisoblash\n"
            "yoki keraksiz bola re-render?\"}\n"
            "  C -->|\"Qimmat hisoblash\"| D[\"useMemo bilan qiymatni keshlash\"]\n"
            "  C -->|\"Bola re-render\"| E[\"Bola'ni React.memo bilan o'rash\n"
            "+ props'ni useCallback/useMemo bilan barqarorlashtirish\"]\n"
            "  D --> F[\"Qayta o'lchab tasdiqlash\"]\n"
            "  E --> F\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: birinchi qadam har doim o'lchash, "
            "memoizatsiya esa faqat aniq sabab topilgandan keyingi maqsadli javob.</p>"
        ),
        "text_content_ru": (
            "<h3>Три инструмента, три чётких задачи</h3>"
            "<p><code>React.memo(Component)</code> — оборачивает компонент и, если "
            "новые props «shallow equal» (поверхностное сравнение — сравнение каждого "
            "ключа через <code>===</code>) предыдущим props, НЕ перерендеривает "
            "компонент, а переиспользует прошлый результат. <code>useMemo(fn, deps)</code> "
            "— кеширует ВЫЧИСЛЕННОЕ ЗНАЧЕНИЕ: пока массив <code>deps</code> не "
            "изменится, <code>fn()</code> заново не вызывается, возвращается прошлый "
            "результат. <code>useCallback(fn, deps)</code> — кеширует ССЫЛКУ НА "
            "ФУНКЦИЮ; фактически <code>useCallback(fn, deps)</code> — это просто "
            "сокращение для <code>useMemo(() =&gt; fn, deps)</code>. Все три служат "
            "одной идее: «если входные данные (props или deps) не изменились, "
            "пересчитывать не нужно».</p>"
            "<h3>На практике: оборачиваем CourseCard в React.memo</h3>"
            "<p>Вспомним ситуацию из урока 2 в <code>StudentCourses.js</code>: "
            "<code>CourseCard</code> не мемоизирован, а <code>onOpen={{() =&gt; "
            "goToCourse(course)}}</code> — новая функция на каждом рендере. Если "
            "обернуть <code>CourseCard</code> в <code>React.memo</code>, но не "
            "изменить <code>onOpen</code>, memo НЕ ДАСТ никакой пользы — потому что на "
            "каждом рендере <code>onOpen</code> новая ссылка, и поверхностное сравнение "
            "всегда найдёт «props изменились». Правильное решение — применить оба "
            "инструмента вместе: в родителе создать одну стабильную функцию "
            "<code>const handleOpen = useCallback((courseId) =&gt; "
            "navigate(`/student/courses/${{courseId}}`), [navigate])</code> и передавать "
            "её ВСЕМ карточкам как одну и ту же ссылку (<code>onOpen={{handleOpen}}</code>), "
            "а внутри вызывать <code>onOpen(course.id)</code>. Тогда "
            "<code>React.memo</code> уже даёт реальную пользу: при вводе буквы в поиск "
            "перерендерятся только карточки, которые действительно ВЫШЛИ или ВОШЛИ в "
            "результат фильтрации, остальные — нет.</p>"
            "<h3>Когда НЕ стоит использовать — пример из самого StudentCourses.js</h3>"
            "<p>В этом же файле переменные <code>displayed</code> и "
            "<code>categoryCounts</code> пересчитываются НА КАЖДОМ РЕНДЕРЕ обычными "
            "<code>.filter()</code>/<code>.map()</code> — без <code>useMemo</code>. Это "
            "НЕ ошибка, а ПРАВИЛЬНОЕ решение: список курсов студента обычно не "
            "превышает нескольких десятков элементов, операция фильтрации O(n) и очень "
            "дешёвая, а сам <code>useMemo</code> тоже тратит время на сравнение "
            "«изменился ли массив deps» — в этом случае стоимость сравнения не "
            "отличается от стоимости самого вычисления или даже превышает её. "
            "<strong>Практическое правило:</strong> добавляйте <code>useMemo</code>/"
            "<code>useCallback</code> только когда: (1) Profiler показал, что "
            "вычисление реально занимает заметное время (несколько миллисекунд и "
            "больше), И этот компонент перерендеривается часто; либо (2) результат "
            "передаётся как prop в <code>React.memo</code>-компонент, и его "
            "стабильная ссылка реально должна предотвратить перерендер ребёнка "
            "(как <code>handleOpen</code> выше).</p>"
            "<h3>Почему чрезмерная мемоизация замедляет</h3>"
            "<p><code>useMemo</code>/<code>useCallback</code> не «бесплатны»: на "
            "каждом рендере React всё равно сравнивает каждый элемент массива "
            "<code>deps</code> со старым значением и хранит закешированное значение в "
            "памяти. Если массив deps содержит значение, меняющееся НА КАЖДОМ "
            "РЕНДЕРЕ (например, инлайн-объект или массив-литерал), мемоизация НЕ даёт "
            "никакой пользы — вычисление всё равно выполняется заново каждый раз — но "
            "вы дополнительно платите за сравнение. Кроме того, каждый "
            "<code>useMemo</code>/<code>useCallback</code> усложняет чтение кода: "
            "теперь читателю нужно анализировать массив deps, чтобы понять «когда это "
            "значение обновляется», вместо простой переменной. Многие крупные команды "
            "приходят к одному и тому же выводу: «используйте мемоизацию как "
            "целевой инструмент, а не стандартную практику».</p>"
            "<h3>Диаграмма: принятие решения о мемоизации</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Замедление измерено в Profiler?\"] -->|\"Нет\"| B[\"Мемоизация не "
            "нужна — оставьте код простым\"]\n"
            "  A -->|\"Да\"| C{\"Причина: дорогое вычисление\n"
            "или лишний перерендер ребёнка?\"}\n"
            "  C -->|\"Дорогое вычисление\"| D[\"Кешировать значение через useMemo\"]\n"
            "  C -->|\"Перерендер ребёнка\"| E[\"Обернуть ребёнка в React.memo\n"
            "+ стабилизировать props через useCallback/useMemo\"]\n"
            "  D --> F[\"Измерить снова и подтвердить\"]\n"
            "  E --> F\n"
            "</pre>"
            "<p>Диаграмма показывает: первый шаг — всегда измерение, а мемоизация — "
            "целевой ответ только после того, как найдена конкретная причина.</p>"
        ),
        "code_content": (
            "// TO'G'RI: React.memo + useCallback birga — CourseCard'ning haqiqiy\n"
            "// naqshini optimallashtirilgan holatga o'tkazish.\n"
            "import { memo, useCallback, useState } from 'react';\n\n"
            "// React.memo — shallow-equal props bo'lsa qayta render qilmaydi.\n"
            "const CourseCard = memo(function CourseCard({ course, onOpen }) {\n"
            "  console.log('CourseCard render:', course.title);\n"
            "  return (\n"
            "    <div className=\"card\">\n"
            "      <h3>{course.title}</h3>\n"
            "      <button onClick={() => onOpen(course.id)}>Ochish</button>\n"
            "    </div>\n"
            "  );\n"
            "});\n\n"
            "export default function CoursesList({ courses, navigate }) {\n"
            "  const [search, setSearch] = useState('');\n\n"
            "  // useCallback: BARCHA kartalarga bir xil reference beriladi —\n"
            "  // faqat 'navigate' o'zgarsa qayta yaratiladi (u deyarli hech qachon\n"
            "  // o'zgarmaydi), shuning uchun bu reference amalda doimiy.\n"
            "  const handleOpen = useCallback(\n"
            "    (courseId) => navigate(`/student/courses/${courseId}`),\n"
            "    [navigate]\n"
            "  );\n\n"
            "  const displayed = courses.filter((c) =>\n"
            "    c.title.toLowerCase().includes(search.toLowerCase())\n"
            "  );\n\n"
            "  return (\n"
            "    <div>\n"
            "      <input value={search} onChange={(e) => setSearch(e.target.value)} />\n"
            "      {displayed.map((course) => (\n"
            "        <CourseCard key={course.id} course={course} onOpen={handleOpen} />\n"
            "      ))}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// NOTO'G'RI (keng tarqalgan xato): useMemo'ni deps HAR RENDER'DA\n"
            "// o'zgaradigan qiymat bilan ishlatish — hech qanday foyda bermaydi,\n"
            "// faqat qo'shimcha xarajat qo'shadi.\n"
            "function BadMemoExample({ items }) {\n"
            "  // items har safar ota'dan YANGI massiv sifatida kelsa (masalan,\n"
            "  // items={data.filter(...)} inline chaqirilgan bo'lsa), useMemo\n"
            "  // HAR SAFAR qayta hisoblaydi — chunki 'items' reference'i har doim\n"
            "  // yangi, deps solishtiruvi hech qachon \"o'zgarmadi\" demaydi.\n"
            "  const total = React.useMemo(\n"
            "    () => items.reduce((sum, i) => sum + i.value, 0),\n"
            "    [items] // <- muammo shu yerda: items har render'da yangi reference\n"
            "  );\n"
            "  return <p>Jami: {total}</p>;\n"
            "}\n\n"
            "// TO'G'RI variant: hisoblash chindan ham arzon bo'lsa, useMemo'ning\n"
            "// o'zini olib tashlash — reduce() O(n) bo'lib, kichik ro'yxatda\n"
            "// useMemo narxidan farqi sezilmaydi.\n"
            "function SimpleTotal({ items }) {\n"
            "  const total = items.reduce((sum, i) => sum + i.value, 0);\n"
            "  return <p>Jami: {total}</p>;\n"
            "}\n\n"
            "// Ilg'or: React.memo ikkinchi argument sifatida o'z solishtirish\n"
            "// funksiyasini qabul qiladi — standart shallow-equal yetarli bo'lmasa.\n"
            "// Faqat aniq zaruratda ishlating: noto'g'ri yozilgan solishtirish funksiyasi\n"
            "// haqiqiy o'zgarishni \"ko'rmasligi\" mumkin va UI yangilanmay qoladi.\n"
            "const CourseCardCustom = memo(\n"
            "  function CourseCardCustom({ course, onOpen }) {\n"
            "    return (\n"
            "      <div><h3>{course.title}</h3>"
            "<button onClick={() => onOpen(course.id)}>Ochish</button></div>\n"
            "    );\n"
            "  },\n"
            "  (prevProps, nextProps) =>\n"
            "    // Faqat progress foizi va sarlavha muhim — boshqa maydonlar\n"
            "    // o'zgarishi bola'ni qayta render qilishga arzimaydi.\n"
            "    prevProps.course.title === nextProps.course.title &&\n"
            "    prevProps.course.progress_percentage === nextProps.course.progress_percentage\n"
            ");\n"
            "// Eslatma: bu qattiq muvozanat — bola komponentga kelajakda yangi prop\n"
            "// qo'shilsa, uni ham shu solishtirish funksiyasiga qo'shishni unutmang,\n"
            "// aks holda o'sha yangi prop o'zgarishi UI'ni yangilamay qoladi.\n"
        ),
        "code_content_ru": (
            "// ПРАВИЛЬНО: React.memo + useCallback вместе — перевод реального\n"
            "// паттерна CourseCard в оптимизированное состояние.\n"
            "import { memo, useCallback, useState } from 'react';\n\n"
            "// React.memo — не перерендеривает при shallow-equal props.\n"
            "const CourseCard = memo(function CourseCard({ course, onOpen }) {\n"
            "  console.log('CourseCard рендер:', course.title);\n"
            "  return (\n"
            "    <div className=\"card\">\n"
            "      <h3>{course.title}</h3>\n"
            "      <button onClick={() => onOpen(course.id)}>Открыть</button>\n"
            "    </div>\n"
            "  );\n"
            "});\n\n"
            "export default function CoursesList({ courses, navigate }) {\n"
            "  const [search, setSearch] = useState('');\n\n"
            "  // useCallback: ВСЕМ карточкам передаётся одна и та же ссылка —\n"
            "  // пересоздаётся только если изменится 'navigate' (он почти никогда\n"
            "  // не меняется), поэтому эта ссылка на практике постоянна.\n"
            "  const handleOpen = useCallback(\n"
            "    (courseId) => navigate(`/student/courses/${courseId}`),\n"
            "    [navigate]\n"
            "  );\n\n"
            "  const displayed = courses.filter((c) =>\n"
            "    c.title.toLowerCase().includes(search.toLowerCase())\n"
            "  );\n\n"
            "  return (\n"
            "    <div>\n"
            "      <input value={search} onChange={(e) => setSearch(e.target.value)} />\n"
            "      {displayed.map((course) => (\n"
            "        <CourseCard key={course.id} course={course} onOpen={handleOpen} />\n"
            "      ))}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// НЕПРАВИЛЬНО (частая ошибка): использование useMemo с deps,\n"
            "// меняющимся НА КАЖДОМ РЕНДЕРЕ — не даёт пользы, только добавляет\n"
            "// накладные расходы.\n"
            "function BadMemoExample({ items }) {\n"
            "  // Если items каждый раз приходит от родителя НОВЫМ массивом\n"
            "  // (например, items={data.filter(...)} вызван инлайн), useMemo\n"
            "  // пересчитывает КАЖДЫЙ РАЗ — потому что ссылка 'items' всегда новая,\n"
            "  // сравнение deps никогда не скажет «не изменилось».\n"
            "  const total = React.useMemo(\n"
            "    () => items.reduce((sum, i) => sum + i.value, 0),\n"
            "    [items] // <- проблема здесь: items — новая ссылка на каждом рендере\n"
            "  );\n"
            "  return <p>Итого: {total}</p>;\n"
            "}\n\n"
            "// ПРАВИЛЬНЫЙ вариант: если вычисление действительно дешёвое, просто\n"
            "// убрать useMemo — reduce() это O(n), и на небольшом списке разница\n"
            "// со стоимостью useMemo незаметна.\n"
            "function SimpleTotal({ items }) {\n"
            "  const total = items.reduce((sum, i) => sum + i.value, 0);\n"
            "  return <p>Итого: {total}</p>;\n"
            "}\n\n"
            "// Продвинуто: React.memo принимает вторым аргументом свою функцию\n"
            "// сравнения — если стандартного shallow-equal недостаточно. Используйте\n"
            "// только при явной необходимости: неверно написанная функция сравнения\n"
            "// может \"не заметить\" реальное изменение, и UI перестанет обновляться.\n"
            "const CourseCardCustom = memo(\n"
            "  function CourseCardCustom({ course, onOpen }) {\n"
            "    return (\n"
            "      <div><h3>{course.title}</h3>"
            "<button onClick={() => onOpen(course.id)}>Открыть</button></div>\n"
            "    );\n"
            "  },\n"
            "  (prevProps, nextProps) =>\n"
            "    // Важны только заголовок и процент прогресса — изменение других\n"
            "    // полей не стоит перерендера ребёнка.\n"
            "    prevProps.course.title === nextProps.course.title &&\n"
            "    prevProps.course.progress_percentage === nextProps.course.progress_percentage\n"
            ");\n"
            "// Заметка: это хрупкий баланс — если ребёнку в будущем добавят новый\n"
            "// prop, не забудьте включить его в эту функцию сравнения, иначе\n"
            "// изменение этого нового prop не обновит UI.\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Memoizatsiyani to'g'ri qo'llang — va qachon qo'llamaslikni tanlang",
            "task_title_ru": "Правильно примените мемоизацию — и решите, когда её не применять",
            "task_description": (
                "Sizga ikkita komponent beriladi: (1) memo qilinmagan "
                "ProductCard komponenti, ota'dan inline onOpen strelka funksiyasi "
                "bilan chaqiriladi — buni React.memo + useCallback yordamida to'g'ri "
                "memoizatsiya qiling, shunda faqat o'zgargan kartalar qayta render "
                "bo'ladi. (2) Kichik ro'yxatdagi (5-10 element) jami summani "
                "hisoblovchi komponent, hozircha useMemo'siz — bu holatda useMemo "
                "QO'SHISH KERAKMI yoki YO'QMI, deb yozma asoslang (darsdagi "
                "\"qachon foydalanmaslik\" mezonlaridan foydalaning)."
            ),
            "task_description_ru": (
                "Вам даны два компонента: (1) немемоизированный компонент "
                "ProductCard, вызываемый родителем с инлайн-стрелочной функцией "
                "onOpen — правильно мемоизируйте его через React.memo + "
                "useCallback, чтобы перерендеривались только изменившиеся карточки. "
                "(2) Компонент, считающий сумму по небольшому списку (5-10 "
                "элементов), пока без useMemo — письменно обоснуйте, НУЖНО ли "
                "добавлять useMemo в этом случае или НЕТ (используйте критерии "
                "«когда не стоит» из урока)."
            ),
            "task_requirements": (
                "ProductCard React.memo bilan o'ralgan va onOpen useCallback "
                "orqali barqarorlashtirilgan bo'lishi shart. Ikkinchi komponent "
                "uchun useMemo qo'shish/qo'shmaslik qarori aniq asoslab yozilishi "
                "kerak — \"chunki shunday deyilgan\" emas."
            ),
            "task_requirements_ru": (
                "ProductCard обязан быть обёрнут в React.memo, а onOpen "
                "стабилизирован через useCallback. Для второго компонента решение "
                "добавлять/не добавлять useMemo должно быть чётко обосновано — не "
                "«потому что так сказано»."
            ),
            "task_technologies": "React, React.memo, useMemo, useCallback",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: to'g'ri va noto'g'ri memoizatsiya",
            "description": "React.memo + useCallback'ning to'g'ri qo'llanishi va useMemo'ning foydasiz ishlatilishi taqqoslamasi.",
            "sample_type": "code",
            "code_files": [
                {"filename": "MemoPatterns.jsx", "language": "jsx", "code": (
                    "import { memo, useCallback, useState } from 'react';\n\n"
                    "const Card = memo(function Card({ item, onOpen }) {\n"
                    "  return <div>{item.title} <button onClick={() => onOpen(item.id)}>Open</button></div>;\n"
                    "});\n\n"
                    "export default function List({ items, navigate }) {\n"
                    "  const handleOpen = useCallback((id) => navigate(`/item/${id}`), [navigate]);\n"
                    "  return items.map((item) => (\n"
                    "    <Card key={item.id} item={item} onOpen={handleOpen} />\n"
                    "  ));\n"
                    "}\n"
                )},
            ],
        },
        "exercises": [
            {
                "title": "React.memo nima qiladi",
                "title_ru": "Что делает React.memo",
                "description": "React.memo bilan o'ralgan komponent qachon qayta render bo'lmaydi?",
                "description_ru": "Когда компонент, обёрнутый в React.memo, не перерендеривается?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Yangi props oldingi render'dagi props bilan shallow-equal bo'lsa",
                    "Komponent hech qachon state ishlatmasa",
                    "Fayl hajmi kichik bo'lsa",
                    "Komponent class sifatida yozilgan bo'lsa",
                ],
                "options_ru": [
                    "Когда новые props поверхностно равны (shallow-equal) предыдущим",
                    "Когда компонент вообще не использует state",
                    "Когда размер файла маленький",
                    "Когда компонент написан как класс",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"Shallow equal\" atamasi darsning boshida ta'riflangan.",
                "hint_ru": "Термин «shallow equal» определён в начале урока.",
                "explanation": "React.memo props'larni yuza (===) taqqoslaydi; agar barchasi bir xil bo'lsa, oldingi natija qayta ishlatiladi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "useCallback qanday tuzilgan",
                "title_ru": "Как устроен useCallback",
                "description": "Bo'shliqni to'ldiring: useCallback(fn, deps) — bu aslida useMemo(() => fn, ___) ning qisqartmasi.",
                "description_ru": "Заполните пропуск: useCallback(fn, deps) — это сокращение для useMemo(() => fn, ___).",
                "exercise_type": "fill_in_blank",
                "correct_answers": "deps",
                "hint": "Ikkinchi argument ikkalasida ham bir xil nomlanadi.",
                "hint_ru": "Второй аргумент называется одинаково в обоих случаях.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Memoizatsiya haqida qaror",
                "title_ru": "Решение о мемоизации",
                "description": "Memoizatsiya qo'shishdan oldingi to'g'ri qadamlar tartibini joylashtiring.",
                "description_ru": "Расставьте по порядку шаги перед добавлением мемоизации.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Profiler'da haqiqiy sekinlikni o'lchash",
                    "Sabab qimmat hisoblashmi yoki keraksiz bola re-render'imi aniqlash",
                    "Mos vositani tanlash: useMemo yoki React.memo+useCallback",
                    "Qayta o'lchab, yaxshilanishni tasdiqlash",
                ],
                "drag_items_ru": [
                    "Измерить реальное замедление в Profiler",
                    "Определить причину: дорогое вычисление или лишний перерендер ребёнка",
                    "Выбрать подходящий инструмент: useMemo или React.memo+useCallback",
                    "Измерить снова и подтвердить улучшение",
                ],
                "correct_order": [
                    "Profiler'da haqiqiy sekinlikni o'lchash",
                    "Sabab qimmat hisoblashmi yoki keraksiz bola re-render'imi aniqlash",
                    "Mos vositani tanlash: useMemo yoki React.memo+useCallback",
                    "Qayta o'lchab, yaxshilanishni tasdiqlash",
                ],
                "hint": "O'lchash har doim birinchi, tasdiqlash — oxirgi qadam.",
                "hint_ru": "Измерение всегда первое, подтверждение — последний шаг.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 3,
        "title": "4-Code splitting: React.lazy va Suspense",
        "title_ru": "4-Code splitting: React.lazy и Suspense",
        "points_reward": 15,
        "text_content": (
            "<h3>Bitta katta bundle muammosi</h3>"
            "<p>Create React App (va shunga o'xshash build tizimlari) standart holatda "
            "sizning barcha <code>import</code>langan modullaringizni bitta (yoki bir "
            "necha) katta JavaScript faylga (\"bundle\") yig'adi. Fayl boshida yozilgan "
            "<code>import X from './X'</code> — bu \"ehtiyot ekan, kerak bo'lsa "
            "ishlataman\" degani emas, balki \"buni HOZIROQ, sahifa yuklanayotganda "
            "bundle'ga qo'sh\" degani. Foydalanuvchi ilovaning bitta sahifasiga kirsa "
            "ham, u bundle ichidagi HAMMA narsani yuklab olishga majbur bo'ladi — hatto "
            "hech qachon ko'rmaydigan sahifalarni ham.</p>"
            "<h3>Haqiqiy misol: ushbu platformaning AppRouter.js fayli</h3>"
            "<p>Bu — o'ylab topilgan misol emas: <code>frontend/src/AppRouter.js</code> "
            "faylining boshida 25 dan ortiq <code>import</code> qatori bor, va ularning "
            "HAMMASI eager (darhol) — orasida talaba (student) sahifalari ham, "
            "o'qituvchi (teacher) sahifalari ham bor, jumladan "
            "<code>TeacherTeamGame.js</code> (1273 qator — platformadagi ENG KATTA "
            "komponent fayli!). Bitta talaba <code>/student/dashboard</code>'ga kirganda "
            "ham, u <code>TeacherTeamGame</code>, <code>TeacherCertificates</code>, "
            "<code>ActivityAnalytics</code> va boshqa 15+ o'qituvchi-sahifalarini "
            "HECH QACHON ko'rmasa ham, ularning barcha kodini boshlang'ich bundle "
            "ichida yuklab oladi — chunki <code>React.lazy</code> yoki dinamik "
            "<code>import()</code> hech qayerda ishlatilmagan, faqat oddiy statik "
            "<code>import</code>lar bor.</p>"
            "<h3>React.lazy + Suspense yechimi</h3>"
            "<p><code>React.lazy(() =&gt; import('./TeacherTeamGame'))</code> — "
            "komponentni DARHOL emas, balki u birinchi marta render qilinishi "
            "kerak bo'lganda yuklaydigan \"lazy\" komponent yaratadi. Build tizimi "
            "(webpack, CRA ichida) har bir dinamik <code>import()</code> chaqiruvi "
            "atrofida AVTOMATIK ravishda alohida JS chunk fayl yaratadi — bu sizdan "
            "qo'shimcha konfiguratsiya talab qilmaydi. Lazy komponent hali yuklanayotgan "
            "vaqtda nima ko'rsatish kerakligini React bilishi uchun uni "
            "<code>&lt;Suspense fallback={{&lt;Loader /&gt;}}&gt;</code> ichiga o'rash "
            "kerak — <code>fallback</code> chunk tarmoqdan kelayotgan paytda ko'rinadi.</p>"
            "<h3>AppRouter.js qanday o'zgargan bo'lardi</h3>"
            "<p>Talaba va o'qituvchi marshrutlari allaqachon ikkita alohida "
            "<code>&lt;Route path=\"/student\"&gt;</code> va "
            "<code>&lt;Route path=\"/teacher\"&gt;</code> guruhiga bo'lingan — bu "
            "route-based (marshrut asosidagi) code splitting uchun tayyor chegara. "
            "Har bir sahifa komponentini <code>lazy(() =&gt; import(...))</code> bilan "
            "almashtirish va butun <code>&lt;Routes&gt;</code>ni bitta "
            "<code>&lt;Suspense&gt;</code> bilan o'rash kifoya — talaba endi faqat "
            "student-chunk'larni, o'qituvchi esa faqat teacher-chunk'larni yuklab "
            "oladi.</p>"
            "<h3>Component-based splitting: har doim route bo'lishi shart emas</h3>"
            "<p>Splitting nafaqat marshrutlar darajasida bo'ladi. Kamdan-kam ochiladigan "
            "og'ir komponent (masalan, katta modal oyna, PDF ko'ruvchi yoki grafik "
            "kutubxonasi) ham <code>React.lazy</code> bilan o'ralishi mumkin — u faqat "
            "foydalanuvchi tugmani bosib modal ochganda yuklanadi, boshlang'ich "
            "sahifa yuklanishida emas.</p>"
            "<h3>Diagramma: bundle bo'linishidan oldin va keyin</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart LR\n"
            "  subgraph OLDIN[\"Oldin - bitta bundle\"]\n"
            "    B1[\"main.bundle.js\n"
            "student + teacher + hamma narsa\"]\n"
            "  end\n"
            "  subgraph KEYIN[\"Keyin - route-based splitting\"]\n"
            "    B2[\"main.bundle.js\n"
            "kichik, umumiy qism\"]\n"
            "    B3[\"student.chunk.js\n"
            "faqat /student sahifalari\"]\n"
            "    B4[\"teacher.chunk.js\n"
            "faqat /teacher sahifalari\"]\n"
            "    B2 -.->|\"talaba kirsa yuklanadi\"| B3\n"
            "    B2 -.->|\"o'qituvchi kirsa yuklanadi\"| B4\n"
            "  end\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: bo'lingandan keyin talaba HECH QACHON "
            "<code>teacher.chunk.js</code>ni yuklamaydi — bu haqiqiy tarmoq trafigi "
            "tejamkorligi, taxminiy emas.</p>"
            "<h3>Qachon foydali, qachon emas — halol nuance</h3>"
            "<p>Har bir dinamik <code>import()</code> — bu qo'shimcha tarmoq so'rovi "
            "degani. Juda kichik komponentni (bir necha qatorlik) lazy qilish odatda "
            "arzimaydi — chunk so'rovining o'zi (HTTP round-trip) komponentning "
            "yuklanish vaqtidan ko'proq vaqt olishi mumkin. Shuningdek, "
            "<code>/login</code> sahifasi kabi HAR DOIM darhol kerak bo'ladigan "
            "komponentlarni lazy qilish shart emas — foydalanuvchi baribir uni birinchi "
            "bo'lib ko'radi. Code splitting eng ko'p foyda beradigan joy — katta (yuzlab "
            "qator), kamdan-kam ochiladigan yoki foydalanuvchining faqat bir qismi "
            "(masalan, faqat o'qituvchilar) ko'radigan sahifalar.</p>"
            "<h3>Natijani qanday tekshirish mumkin</h3>"
            "<p>Bo'linish samarasini maxsus vositasiz ham tekshirish oson: brauzer "
            "DevTools'ining \"Network\" tab'i oddiy statik import bilan bitta katta "
            "<code>main.chunk.js</code>ni ko'rsatadi; <code>React.lazy</code>ga "
            "o'tgandan so'ng esa <code>3.chunk.js</code>, <code>4.chunk.js</code> kabi "
            "qo'shimcha fayllar paydo bo'ladi, va ularning har biri faqat mos "
            "marshrutga o'tilganda so'raladi — bu tarmoq so'rovlari ro'yxatida "
            "to'g'ridan-to'g'ri ko'rinadi, taxmin qilishning hojati yo'q.</p>"
        ),
        "text_content_ru": (
            "<h3>Проблема одного большого бандла</h3>"
            "<p>Create React App (и похожие системы сборки) по умолчанию собирают все "
            "ваши <code>import</code>-ированные модули в один (или несколько) большой "
            "JavaScript-файл («бандл»). <code>import X from './X'</code> в начале файла "
            "— это не «на всякий случай, вдруг понадобится», а «добавь это ПРЯМО "
            "СЕЙЧАС, при загрузке страницы, в бандл». Даже если пользователь заходит "
            "всего на одну страницу приложения, он вынужден загрузить ВСЁ содержимое "
            "бандла — включая страницы, которые никогда не увидит.</p>"
            "<h3>Реальный пример: файл AppRouter.js этой платформы</h3>"
            "<p>Это не выдуманный пример: в начале <code>frontend/src/AppRouter.js</code> "
            "более 25 строк <code>import</code>, и ВСЕ они eager (немедленные) — среди "
            "них есть и страницы студента, и страницы учителя, включая "
            "<code>TeacherTeamGame.js</code> (1273 строки — САМЫЙ большой файл "
            "компонента на платформе!). Когда один студент заходит на "
            "<code>/student/dashboard</code>, он загружает весь код "
            "<code>TeacherTeamGame</code>, <code>TeacherCertificates</code>, "
            "<code>ActivityAnalytics</code> и ещё 15+ учительских страниц в начальном "
            "бандле — даже если НИКОГДА их не увидит — потому что нигде не используется "
            "<code>React.lazy</code> или динамический <code>import()</code>, только "
            "обычные статические <code>import</code>.</p>"
            "<h3>Решение: React.lazy + Suspense</h3>"
            "<p><code>React.lazy(() =&gt; import('./TeacherTeamGame'))</code> создаёт "
            "«ленивый» компонент, который загружается НЕ СРАЗУ, а когда впервые должен "
            "быть отрендерен. Система сборки (webpack внутри CRA) АВТОМАТИЧЕСКИ создаёт "
            "отдельный JS-чанк вокруг каждого динамического вызова <code>import()</code> "
            "— это не требует от вас дополнительной настройки. Чтобы React знал, что "
            "показывать, пока ленивый компонент ещё загружается, его нужно обернуть в "
            "<code>&lt;Suspense fallback={{&lt;Loader /&gt;}}&gt;</code> — "
            "<code>fallback</code> виден, пока чанк идёт по сети.</p>"
            "<h3>Как изменился бы AppRouter.js</h3>"
            "<p>Маршруты студента и учителя уже разделены на две отдельные группы "
            "<code>&lt;Route path=\"/student\"&gt;</code> и <code>&lt;Route "
            "path=\"/teacher\"&gt;</code> — это готовая граница для route-based "
            "(маршрутного) code splitting. Достаточно заменить каждый компонент "
            "страницы на <code>lazy(() =&gt; import(...))</code> и обернуть весь "
            "<code>&lt;Routes&gt;</code> одним <code>&lt;Suspense&gt;</code> — теперь "
            "студент загружает только student-чанки, а учитель — только "
            "teacher-чанки.</p>"
            "<h3>Компонентный splitting: не только на уровне маршрутов</h3>"
            "<p>Разделение бывает не только на уровне маршрутов. Редко открываемый "
            "тяжёлый компонент (например, большое модальное окно, просмотрщик PDF или "
            "библиотека графиков) тоже можно обернуть в <code>React.lazy</code> — он "
            "загрузится только когда пользователь нажмёт кнопку и откроет модалку, а не "
            "при загрузке начальной страницы.</p>"
            "<h3>Диаграмма: бандл до и после разделения</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart LR\n"
            "  subgraph DO[\"До - один бандл\"]\n"
            "    B1[\"main.bundle.js\n"
            "студент + учитель + всё вместе\"]\n"
            "  end\n"
            "  subgraph POSLE[\"После - маршрутное разделение\"]\n"
            "    B2[\"main.bundle.js\n"
            "маленький, общая часть\"]\n"
            "    B3[\"student.chunk.js\n"
            "только /student страницы\"]\n"
            "    B4[\"teacher.chunk.js\n"
            "только /teacher страницы\"]\n"
            "    B2 -.->|\"загружается для студента\"| B3\n"
            "    B2 -.->|\"загружается для учителя\"| B4\n"
            "  end\n"
            "</pre>"
            "<p>Диаграмма показывает: после разделения студент НИКОГДА не загружает "
            "<code>teacher.chunk.js</code> — это реальная экономия сетевого трафика, а "
            "не предположение.</p>"
            "<h3>Когда полезно, а когда нет — честный нюанс</h3>"
            "<p>Каждый динамический <code>import()</code> — это дополнительный сетевой "
            "запрос. Оборачивать в lazy очень маленький компонент (в несколько строк) "
            "обычно не стоит — сам запрос чанка (HTTP round-trip) может занять больше "
            "времени, чем загрузка самого компонента. Также не нужно делать lazy "
            "компоненты, которые ВСЕГДА нужны сразу, вроде страницы <code>/login</code> "
            "— пользователь всё равно увидит её первой. Code splitting даёт больше "
            "всего пользы там, где страницы большие (сотни строк), редко открываются "
            "или видны только части пользователей (например, только учителям).</p>"
            "<h3>Как проверить результат</h3>"
            "<p>Проверить эффект разделения легко без специальных инструментов: вкладка "
            "«Network» в DevTools браузера при обычном статическом импорте покажет один "
            "большой <code>main.chunk.js</code>; после перехода на "
            "<code>React.lazy</code> появятся дополнительные файлы вида "
            "<code>3.chunk.js</code>, <code>4.chunk.js</code> и так далее, каждый из "
            "которых запрашивается только при переходе на соответствующий маршрут — это "
            "видно прямо в списке сетевых запросов, без гадания.</p>"
        ),
        "code_content": (
            "// AppRouter.js'ning haqiqiy naqshiga asoslangan OLDIN/KEYIN taqqoslash.\n\n"
            "// ===== OLDIN: barcha sahifalar eager import (haqiqiy holat) =====\n"
            "import StudentDashboard from './views/student/dashboard/StudentDashboard';\n"
            "import TeacherTeamGame from './views/teacher/teamgame/TeacherTeamGame'; // 1273 qator!\n"
            "import TeacherCertificates from './views/teacher/TeacherCertificates/Teachercertificates';\n"
            "import ActivityAnalytics from './views/teacher/activityanalytics/ActivityAnalytics';\n"
            "// ... yana 20+ shunga o'xshash eager import\n\n"
            "function AppRouterBefore() {\n"
            "  return (\n"
            "    <Routes>\n"
            "      <Route path=\"/student/dashboard\" element={<StudentDashboard />} />\n"
            "      <Route path=\"/teacher/team-game\" element={<TeacherTeamGame />} />\n"
            "      <Route path=\"/teacher/certificates\" element={<TeacherCertificates />} />\n"
            "      <Route path=\"/teacher/activity-analytics\" element={<ActivityAnalytics />} />\n"
            "    </Routes>\n"
            "  );\n"
            "}\n\n"
            "// ===== KEYIN: React.lazy + Suspense bilan route-based splitting =====\n"
            "import { lazy, Suspense } from 'react';\n\n"
            "const StudentDashboardLazy = lazy(\n"
            "  () => import('./views/student/dashboard/StudentDashboard')\n"
            ");\n"
            "const TeacherTeamGameLazy = lazy(\n"
            "  () => import('./views/teacher/teamgame/TeacherTeamGame')\n"
            ");\n"
            "const TeacherCertificatesLazy = lazy(\n"
            "  () => import('./views/teacher/TeacherCertificates/Teachercertificates')\n"
            ");\n"
            "const ActivityAnalyticsLazy = lazy(\n"
            "  () => import('./views/teacher/activityanalytics/ActivityAnalytics')\n"
            ");\n\n"
            "function RouteFallback() {\n"
            "  return <div className=\"route-loader\">Yuklanmoqda...</div>;\n"
            "}\n\n"
            "function AppRouterAfter() {\n"
            "  return (\n"
            "    <Suspense fallback={<RouteFallback />}>\n"
            "      <Routes>\n"
            "        <Route path=\"/student/dashboard\" element={<StudentDashboardLazy />} />\n"
            "        <Route path=\"/teacher/team-game\" element={<TeacherTeamGameLazy />} />\n"
            "        <Route path=\"/teacher/certificates\" element={<TeacherCertificatesLazy />} />\n"
            "        <Route\n"
            "          path=\"/teacher/activity-analytics\"\n"
            "          element={<ActivityAnalyticsLazy />}\n"
            "        />\n"
            "      </Routes>\n"
            "    </Suspense>\n"
            "  );\n"
            "}\n\n"
            "// Component-based splitting misoli: kamdan-kam ochiladigan og'ir modal.\n"
            "const HeavyReportModal = lazy(() => import('./HeavyReportModal'));\n\n"
            "function ReportButton() {\n"
            "  const [open, setOpen] = React.useState(false);\n"
            "  return (\n"
            "    <>\n"
            "      <button onClick={() => setOpen(true)}>Hisobotni ko'rish</button>\n"
            "      {open && (\n"
            "        <Suspense fallback={<RouteFallback />}>\n"
            "          <HeavyReportModal onClose={() => setOpen(false)} />\n"
            "        </Suspense>\n"
            "      )}\n"
            "    </>\n"
            "  );\n"
            "}\n\n"
            "// Prefetch: chunk'ni foydalanuvchi tugmani bosishidan OLDIN, sichqoncha\n"
            "// tugma ustiga kelganda oldindan so'rab qo'yish mumkin — shunda haqiqiy\n"
            "// bosish paytida chunk allaqachon tarmoqdan tushib bo'lgan bo'ladi.\n"
            "function ReportButtonWithPrefetch() {\n"
            "  const [open, setOpen] = React.useState(false);\n"
            "  const prefetch = () => import('./HeavyReportModal');\n"
            "  return (\n"
            "    <>\n"
            "      <button onMouseEnter={prefetch} onClick={() => setOpen(true)}>\n"
            "        Hisobotni ko'rish\n"
            "      </button>\n"
            "      {open && (\n"
            "        <Suspense fallback={<RouteFallback />}>\n"
            "          <HeavyReportModal onClose={() => setOpen(false)} />\n"
            "        </Suspense>\n"
            "      )}\n"
            "    </>\n"
            "  );\n"
            "}\n"
        ),
        "code_content_ru": (
            "// Сравнение ДО/ПОСЛЕ на основе реального паттерна AppRouter.js.\n\n"
            "// ===== ДО: все страницы eager import (реальное состояние) =====\n"
            "import StudentDashboard from './views/student/dashboard/StudentDashboard';\n"
            "import TeacherTeamGame from './views/teacher/teamgame/TeacherTeamGame'; // 1273 строки!\n"
            "import TeacherCertificates from './views/teacher/TeacherCertificates/Teachercertificates';\n"
            "import ActivityAnalytics from './views/teacher/activityanalytics/ActivityAnalytics';\n"
            "// ... ещё 20+ таких же eager импортов\n\n"
            "function AppRouterBefore() {\n"
            "  return (\n"
            "    <Routes>\n"
            "      <Route path=\"/student/dashboard\" element={<StudentDashboard />} />\n"
            "      <Route path=\"/teacher/team-game\" element={<TeacherTeamGame />} />\n"
            "      <Route path=\"/teacher/certificates\" element={<TeacherCertificates />} />\n"
            "      <Route path=\"/teacher/activity-analytics\" element={<ActivityAnalytics />} />\n"
            "    </Routes>\n"
            "  );\n"
            "}\n\n"
            "// ===== ПОСЛЕ: маршрутное разделение через React.lazy + Suspense =====\n"
            "import { lazy, Suspense } from 'react';\n\n"
            "const StudentDashboardLazy = lazy(\n"
            "  () => import('./views/student/dashboard/StudentDashboard')\n"
            ");\n"
            "const TeacherTeamGameLazy = lazy(\n"
            "  () => import('./views/teacher/teamgame/TeacherTeamGame')\n"
            ");\n"
            "const TeacherCertificatesLazy = lazy(\n"
            "  () => import('./views/teacher/TeacherCertificates/Teachercertificates')\n"
            ");\n"
            "const ActivityAnalyticsLazy = lazy(\n"
            "  () => import('./views/teacher/activityanalytics/ActivityAnalytics')\n"
            ");\n\n"
            "function RouteFallback() {\n"
            "  return <div className=\"route-loader\">Загрузка...</div>;\n"
            "}\n\n"
            "function AppRouterAfter() {\n"
            "  return (\n"
            "    <Suspense fallback={<RouteFallback />}>\n"
            "      <Routes>\n"
            "        <Route path=\"/student/dashboard\" element={<StudentDashboardLazy />} />\n"
            "        <Route path=\"/teacher/team-game\" element={<TeacherTeamGameLazy />} />\n"
            "        <Route path=\"/teacher/certificates\" element={<TeacherCertificatesLazy />} />\n"
            "        <Route\n"
            "          path=\"/teacher/activity-analytics\"\n"
            "          element={<ActivityAnalyticsLazy />}\n"
            "        />\n"
            "      </Routes>\n"
            "    </Suspense>\n"
            "  );\n"
            "}\n\n"
            "// Пример компонентного splitting: редко открываемая тяжёлая модалка.\n"
            "const HeavyReportModal = lazy(() => import('./HeavyReportModal'));\n\n"
            "function ReportButton() {\n"
            "  const [open, setOpen] = React.useState(false);\n"
            "  return (\n"
            "    <>\n"
            "      <button onClick={() => setOpen(true)}>Посмотреть отчёт</button>\n"
            "      {open && (\n"
            "        <Suspense fallback={<RouteFallback />}>\n"
            "          <HeavyReportModal onClose={() => setOpen(false)} />\n"
            "        </Suspense>\n"
            "      )}\n"
            "    </>\n"
            "  );\n"
            "}\n\n"
            "// Prefetch: можно запросить чанк ДО клика пользователя, ещё при наведении\n"
            "// курсора на кнопку — тогда к моменту реального клика чанк уже успеет\n"
            "// загрузиться по сети.\n"
            "function ReportButtonWithPrefetch() {\n"
            "  const [open, setOpen] = React.useState(false);\n"
            "  const prefetch = () => import('./HeavyReportModal');\n"
            "  return (\n"
            "    <>\n"
            "      <button onMouseEnter={prefetch} onClick={() => setOpen(true)}>\n"
            "        Посмотреть отчёт\n"
            "      </button>\n"
            "      {open && (\n"
            "        <Suspense fallback={<RouteFallback />}>\n"
            "          <HeavyReportModal onClose={() => setOpen(false)} />\n"
            "        </Suspense>\n"
            "      )}\n"
            "    </>\n"
            "  );\n"
            "}\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Berilgan router'ni route-based code splitting'ga o'tkazing",
            "task_title_ru": "Переведите данный роутер на маршрутный code splitting",
            "task_description": (
                "Sizga kamida to'rtta sahifa (masalan Dashboard, Settings, Reports, "
                "AdminPanel) uchun eager import qilingan oddiy React Router "
                "konfiguratsiyasi beriladi. Har bir sahifa importini "
                "lazy(() => import(...))ga almashtiring, umumiy fallback komponenti "
                "yarating va butun <Routes>ni <Suspense>ga o'rang. Brauzer DevTools "
                "Network tab'ida har bir sahifaga o'tganda alohida chunk fayl "
                "so'ralayotganini skrinshot bilan tasdiqlang."
            ),
            "task_description_ru": (
                "Вам дана простая конфигурация React Router с eager-импортом "
                "минимум четырёх страниц (например Dashboard, Settings, Reports, "
                "AdminPanel). Замените импорт каждой страницы на "
                "lazy(() => import(...)), создайте общий компонент fallback и "
                "оберните весь <Routes> в <Suspense>. Подтвердите скриншотом "
                "вкладки Network в DevTools браузера, что при переходе на каждую "
                "страницу запрашивается отдельный файл чанка."
            ),
            "task_requirements": (
                "Kamida to'rtta sahifa lazy() orqali import qilinishi shart. "
                "Suspense fallback UI'ga ega bo'lishi kerak. Network tab "
                "skrinshoti alohida chunk so'rovlarini ko'rsatishi shart."
            ),
            "task_requirements_ru": (
                "Минимум четыре страницы обязаны быть импортированы через lazy(). "
                "Suspense обязан иметь fallback UI. Скриншот вкладки Network "
                "должен показывать отдельные запросы чанков."
            ),
            "task_technologies": "React, React.lazy, Suspense, React Router",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: React.lazy + Suspense route splitting",
            "description": "AppRouter.js'ning haqiqiy tuzilishiga asoslangan lazy-loaded marshrutlar namunasi.",
            "sample_type": "code",
            "code_files": [
                {"filename": "AppRouter.lazy.jsx", "language": "jsx", "code": (
                    "import { lazy, Suspense } from 'react';\n"
                    "import { Routes, Route } from 'react-router-dom';\n\n"
                    "const StudentDashboard = lazy(() => import('./views/student/dashboard/StudentDashboard'));\n"
                    "const TeacherTeamGame = lazy(() => import('./views/teacher/teamgame/TeacherTeamGame'));\n\n"
                    "export default function AppRouter() {\n"
                    "  return (\n"
                    "    <Suspense fallback={<div>Yuklanmoqda...</div>}>\n"
                    "      <Routes>\n"
                    "        <Route path=\"/student/dashboard\" element={<StudentDashboard />} />\n"
                    "        <Route path=\"/teacher/team-game\" element={<TeacherTeamGame />} />\n"
                    "      </Routes>\n"
                    "    </Suspense>\n"
                    "  );\n"
                    "}\n"
                )},
            ],
        },
        "exercises": [
            {
                "title": "Lazy chunk qachon yuklanadi",
                "title_ru": "Когда загружается lazy-чанк",
                "description": "React.lazy(() => import('./X')) bilan yaratilgan komponent modul kodi qachon yuklanadi?",
                "description_ru": "Когда загружается код модуля компонента, созданного через React.lazy(() => import('./X'))?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Komponent birinchi marta render qilinishi kerak bo'lganda",
                    "Ilova ishga tushishi bilanoq, boshqalar kabi",
                    "Faqat sahifa qayta yuklanganda (F5)",
                    "Hech qachon, agar foydalanuvchi tugma bosmasa",
                ],
                "options_ru": [
                    "Когда компонент впервые должен быть отрендерен",
                    "Сразу при запуске приложения, как и остальные",
                    "Только при перезагрузке страницы (F5)",
                    "Никогда, если пользователь не нажмёт кнопку",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"Lazy\" so'zining ma'nosini eslang — \"dangasa\", ya'ni kerak bo'lgunga qadar kutadi.",
                "hint_ru": "Вспомните значение слова «lazy» — «ленивый», то есть ждёт до момента, когда действительно нужен.",
                "explanation": "lazy() modulni darhol emas, komponent birinchi marta render qilinishi kerak bo'lganda import qiladi — shu payt tarmoqdan chunk yuklanadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Suspense'ning vazifasi",
                "title_ru": "Роль Suspense",
                "description": "Bo'shliqni to'ldiring: Suspense'ning \"___\" prop'i chunk hali yuklanayotganda ko'rsatiladigan UI'ni belgilaydi.",
                "description_ru": "Заполните пропуск: проп Suspense «___» задаёт UI, показываемый пока чанк ещё загружается.",
                "exercise_type": "fill_in_blank",
                "correct_answers": "fallback",
                "hint": "Darsdagi kod namunasida <Suspense fallback={...}> deb yozilgan edi.",
                "hint_ru": "В примере кода урока было написано <Suspense fallback={...}>.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "AppRouter'ni bo'lish qadamlari",
                "title_ru": "Шаги разделения AppRouter",
                "description": "AppRouter.js'ni route-based code splitting'ga o'tkazish qadamlarini tartibga joylashtiring.",
                "description_ru": "Расставьте по порядку шаги перевода AppRouter.js на маршрутный code splitting.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Har bir sahifa importini lazy(() => import(...))ga almashtirish",
                    "Fallback UI komponentini yaratish",
                    "Butun <Routes>ni <Suspense fallback={...}> bilan o'rash",
                    "Talaba va o'qituvchi uchun alohida chunk'lar yuklanishini tekshirish",
                ],
                "drag_items_ru": [
                    "Заменить импорт каждой страницы на lazy(() => import(...))",
                    "Создать компонент fallback UI",
                    "Обернуть весь <Routes> в <Suspense fallback={...}>",
                    "Проверить, что для студента и учителя грузятся разные чанки",
                ],
                "correct_order": [
                    "Har bir sahifa importini lazy(() => import(...))ga almashtirish",
                    "Fallback UI komponentini yaratish",
                    "Butun <Routes>ni <Suspense fallback={...}> bilan o'rash",
                    "Talaba va o'qituvchi uchun alohida chunk'lar yuklanishini tekshirish",
                ],
                "hint": "Avval kod o'zgaradi, keyin tekshiriladi.",
                "hint_ru": "Сначала меняется код, потом проверяется результат.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 4,
        "title": "R1-Takrorlash: Memoizatsiya va code splitting mini-mashq",
        "title_ru": "R1-Повторение: мини-практика по мемоизации и code splitting",
        "points_reward": 20,
        "text_content": (
            "<h3>Bu — takrorlash darsi</h3>"
            "<p>Bu dars amaliy takrorlash bo'lgani uchun matn qisqaroq — yangi nazariy "
            "tushuncha berilmaydi, asosiy e'tibor 1-4-darslarda o'rganilganlarni "
            "(Profiler bilan o'lchash, re-render kaskadi, React.memo/useMemo/"
            "useCallback va React.lazy/Suspense) bitta kichik loyihada birlashtirishga "
            "qaratilgan.</p>"
            "<h3>Nimani takrorlaymiz</h3>"
            "<ul>"
            "<li><strong>O'lchash birinchi</strong>: har qanday tuzatishdan oldin "
            "Profiler'da \"nega bu komponent render bo'ldi\" savolini berish.</li>"
            "<li><strong>Re-render kaskadi</strong>: ota komponent render bo'lganda "
            "bolalar ham render bo'lishini, va bu odatda muammo emasligini eslash.</li>"
            "<li><strong>React.memo + useCallback</strong>: ikkalasini BIRGA "
            "qo'llamasangiz, memo befoyda bo'lishini yodda tutish.</li>"
            "<li><strong>React.lazy + Suspense</strong>: kamdan-kam kerak bo'ladigan "
            "og'ir qismni alohida chunk'ga ajratish.</li>"
            "</ul>"
            "<p>Quyidagi vazifada shu to'rttalasini bitta kichik \"kurslar ro'yxati + "
            "tafsilot modali\" komponentida qo'llaysiz.</p>"
        ),
        "text_content_ru": (
            "<h3>Это урок повторения</h3>"
            "<p>Этот урок — практическое повторение, поэтому текст короче — новой "
            "теории не будет, основное внимание уделено объединению изученного в "
            "уроках 1-4 (измерение через Profiler, каскад ре-рендеров, React.memo/"
            "useMemo/useCallback и React.lazy/Suspense) в одном небольшом проекте.</p>"
            "<h3>Что повторяем</h3>"
            "<ul>"
            "<li><strong>Сначала измерение</strong>: перед любым исправлением задать "
            "вопрос «почему этот компонент отрендерился» в Profiler.</li>"
            "<li><strong>Каскад ре-рендеров</strong>: помнить, что при рендере "
            "родителя дети тоже рендерятся, и это обычно не проблема.</li>"
            "<li><strong>React.memo + useCallback</strong>: помнить, что без "
            "совместного применения обоих memo не даёт пользы.</li>"
            "<li><strong>React.lazy + Suspense</strong>: выносить редко нужную тяжёлую "
            "часть в отдельный чанк.</li>"
            "</ul>"
            "<p>В задании ниже вы примените все четыре пункта в одном небольшом "
            "компоненте «список курсов + модалка деталей».</p>"
        ),
        "code_content": (
            "// Boshlang'ich (optimallashtirilmagan) holat — vazifada shuni tuzatasiz.\n"
            "function CourseListNaive({ courses, onOpenDetails }) {\n"
            "  const [search, setSearch] = React.useState('');\n"
            "  const filtered = courses.filter((c) => c.title.includes(search));\n"
            "  return (\n"
            "    <div>\n"
            "      <input value={search} onChange={(e) => setSearch(e.target.value)} />\n"
            "      {filtered.map((c) => (\n"
            "        <CourseRow key={c.id} course={c} onOpen={() => onOpenDetails(c)} />\n"
            "      ))}\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "function CourseRow({ course, onOpen }) {\n"
            "  return <div>{course.title}<button onClick={onOpen}>Batafsil</button></div>;\n"
            "}\n"
        ),
        "code_content_ru": (
            "// Начальное (неоптимизированное) состояние — вы исправите его в задании.\n"
            "function CourseListNaive({ courses, onOpenDetails }) {\n"
            "  const [search, setSearch] = React.useState('');\n"
            "  const filtered = courses.filter((c) => c.title.includes(search));\n"
            "  return (\n"
            "    <div>\n"
            "      <input value={search} onChange={(e) => setSearch(e.target.value)} />\n"
            "      {filtered.map((c) => (\n"
            "        <CourseRow key={c.id} course={c} onOpen={() => onOpenDetails(c)} />\n"
            "      ))}\n"
            "    </div>\n"
            "  );\n"
            "}\n"
            "function CourseRow({ course, onOpen }) {\n"
            "  return <div>{course.title}<button onClick={onOpen}>Подробнее</button></div>;\n"
            "}\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Kurslar ro'yxatini optimallashtiring",
            "task_title_ru": "Оптимизируйте список курсов",
            "task_description": (
                "Yuqoridagi CourseListNaive komponentini qayta yozing: (1) CourseRow'ni "
                "React.memo bilan o'rang, (2) onOpen'ni useCallback bilan barqarorlashtiring "
                "(ota'da bitta funksiya, ichida course.id orqali chaqiriladi), (3) tafsilot "
                "modalini React.lazy + Suspense orqali alohida chunk sifatida yuklang — "
                "modal faqat foydalanuvchi \"Batafsil\"ni bosganda yuklanishi kerak."
            ),
            "task_description_ru": (
                "Перепишите компонент CourseListNaive выше: (1) оберните CourseRow в "
                "React.memo, (2) стабилизируйте onOpen через useCallback (одна функция в "
                "родителе, вызывается внутри через course.id), (3) загрузите модалку "
                "деталей через React.lazy + Suspense как отдельный чанк — модалка должна "
                "загружаться только когда пользователь нажмёт «Подробнее»."
            ),
            "task_requirements": (
                "CourseRow — memo bilan o'ralgan bo'lishi shart. onOpen — barcha qatorlarga "
                "bir xil reference sifatida uzatilishi kerak. Modal komponenti lazy() orqali "
                "import qilinishi va Suspense bilan o'ralishi shart."
            ),
            "task_requirements_ru": (
                "CourseRow обязан быть обёрнут в memo. onOpen должен передаваться всем "
                "строкам как одна и та же ссылка. Компонент модалки обязан быть "
                "импортирован через lazy() и обёрнут в Suspense."
            ),
            "task_technologies": "React, React.memo, useCallback, React.lazy, Suspense",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: optimallashtirilgan kurslar ro'yxati",
            "description": "Vazifaning to'liq yechimi — memo, useCallback va lazy birga qo'llangan holat.",
            "sample_type": "code",
            "code_files": [
                {"filename": "CourseListOptimized.jsx", "language": "jsx", "code": (
                    "import { memo, useCallback, useState, lazy, Suspense } from 'react';\n\n"
                    "const CourseDetailsModal = lazy(() => import('./CourseDetailsModal'));\n\n"
                    "const CourseRow = memo(function CourseRow({ course, onOpen }) {\n"
                    "  return (\n"
                    "    <div>{course.title}<button onClick={() => onOpen(course.id)}>Batafsil</button></div>\n"
                    "  );\n"
                    "});\n\n"
                    "export default function CourseListOptimized({ courses }) {\n"
                    "  const [search, setSearch] = useState('');\n"
                    "  const [openId, setOpenId] = useState(null);\n"
                    "  const handleOpen = useCallback((id) => setOpenId(id), []);\n"
                    "  const filtered = courses.filter((c) => c.title.includes(search));\n"
                    "  return (\n"
                    "    <div>\n"
                    "      <input value={search} onChange={(e) => setSearch(e.target.value)} />\n"
                    "      {filtered.map((c) => (\n"
                    "        <CourseRow key={c.id} course={c} onOpen={handleOpen} />\n"
                    "      ))}\n"
                    "      {openId && (\n"
                    "        <Suspense fallback={<p>Yuklanmoqda...</p>}>\n"
                    "          <CourseDetailsModal courseId={openId} onClose={() => setOpenId(null)} />\n"
                    "        </Suspense>\n"
                    "      )}\n"
                    "    </div>\n"
                    "  );\n"
                    "}\n"
                )},
            ],
        },
        "exercises": [
            {
                "title": "Memo + useCallback birga",
                "title_ru": "Memo + useCallback вместе",
                "description": "React.memo bilan o'ralgan komponentga inline strelka funksiya (masalan onOpen={() => f(x)}) uzatilsa, nima bo'ladi?",
                "description_ru": "Что произойдёт, если компоненту, обёрнутому в React.memo, передать инлайн-стрелочную функцию (например onOpen={() => f(x)})?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Memo befoyda bo'ladi, chunki har render'da yangi funksiya reference keladi",
                    "Ilova ishlamay qoladi",
                    "Memo hamon ishlaydi, chunki funksiyalar har doim teng hisoblanadi",
                    "React xato xabari chiqaradi",
                ],
                "options_ru": [
                    "Memo не даёт пользы, потому что на каждом рендере приходит новая ссылка функции",
                    "Приложение перестаёт работать",
                    "Memo всё равно работает, потому что функции всегда считаются равными",
                    "React выдаст сообщение об ошибке",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "3-darsda ko'rgan CourseCard misolini eslang.",
                "hint_ru": "Вспомните пример CourseCard из урока 3.",
                "explanation": "Shallow-equal solishtiruv har safar yangi funksiya reference'ini \"o'zgargan\" deb hisoblaydi, shuning uchun useCallback shart.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Lazy komponent",
                "title_ru": "Lazy-компонент",
                "description": "Bo'shliqni to'ldiring: React.lazy bilan yaratilgan komponent ___ komponenti ichida ko'rsatilishi shart, aks holda yuklanish paytida xato chiqadi.",
                "description_ru": "Заполните пропуск: компонент, созданный через React.lazy, обязан быть показан внутри компонента ___, иначе во время загрузки возникнет ошибка.",
                "exercise_type": "fill_in_blank",
                "correct_answers": "Suspense",
                "hint": "4-darsda o'rgangan, fallback prop'iga ega komponent.",
                "hint_ru": "Компонент из урока 4, у которого есть проп fallback.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "To'rtta qadamni tartiblash",
                "title_ru": "Расставьте четыре шага",
                "description": "1-4-darslarda o'rgangan optimallashtirish yondashuvining to'g'ri tartibini joylashtiring.",
                "description_ru": "Расставьте по порядку подход к оптимизации из уроков 1-4.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Profiler'da sekinlikni o'lchash",
                    "Sababni aniqlash: kaskad, qimmat hisoblash yoki katta bundle",
                    "Mos vosita: memo+useCallback, useMemo yoki lazy+Suspense",
                    "Qayta o'lchab natijani tasdiqlash",
                ],
                "drag_items_ru": [
                    "Измерить замедление в Profiler",
                    "Определить причину: каскад, дорогое вычисление или большой бандл",
                    "Подходящий инструмент: memo+useCallback, useMemo или lazy+Suspense",
                    "Измерить снова и подтвердить результат",
                ],
                "correct_order": [
                    "Profiler'da sekinlikni o'lchash",
                    "Sababni aniqlash: kaskad, qimmat hisoblash yoki katta bundle",
                    "Mos vosita: memo+useCallback, useMemo yoki lazy+Suspense",
                    "Qayta o'lchab natijani tasdiqlash",
                ],
                "hint": "Bu — kursning har darsida takrorlangan umumiy oqim.",
                "hint_ru": "Это общий поток, повторяющийся в каждом уроке курса.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 5,
        "title": "5-Virtualization: uzun ro'yxatlar uchun react-window",
        "title_ru": "5-Виртуализация: react-window для длинных списков",
        "points_reward": 15,
        "text_content": (
            "<h3>Muammo: DOM node'lar soni chiziqli o'sadi</h3>"
            "<p>Ro'yxatda N ta element bo'lsa, React odatda N ta DOM node yaratadi — "
            "hattoki foydalanuvchi bir vaqtning o'zida ekranda faqat 10-15 tasini "
            "ko'rsa ham. Brauzer esa har bir DOM node uchun layout (joylashuvni "
            "hisoblash) va paint (chizish) ishini bajarishi kerak. Ro'yxat bir necha "
            "o'nlab elementdan iborat bo'lsa, bu sezilarli emas. Lekin ro'yxat "
            "minglab elementga yetganda — masalan, butun maktab bo'yicha reyting yoki "
            "yuzlab talabaning batafsil jadvali — minglab DOM node yaratish, ularni "
            "joylashtirish va scroll paytida qayta chizish sezilarli sekinlikka olib "
            "kelishi mumkin.</p>"
            "<h3>Yechim: faqat ko'rinadigan qatorlarni render qilish</h3>"
            "<p>\"Virtualizatsiya\" (yoki \"windowing\") g'oyasi oddiy: ro'yxatning "
            "HAMMA elementini emas, faqat foydalanuvchi HOZIR ko'rayotgan (va unga "
            "yaqin, kichik bufer) qatorlarni render qilish. Qolgan qatorlar o'rniga "
            "bitta katta \"bo'sh joy\" (spacer) qo'yiladi, shunda scroll balandligi "
            "to'g'ri qoladi — foydalanuvchi scroll qilganda, kutubxona qaysi qatorlar "
            "endi ko'rinishga kirganini hisoblab, ularni RENDER QILADI va ekrandan "
            "chiqqanlarini olib tashlaydi. Natijada DOM'da har doim atigi bir necha "
            "o'nlab qator bo'ladi — ro'yxat 50 ta elementdan iborat bo'lsa ham, 50,000 "
            "ta elementdan iborat bo'lsa ham. <code>react-window</code> kutubxonasi "
            "aynan shu g'oyani <code>FixedSizeList</code> (barcha qatorlar bir xil "
            "balandlikda) va <code>VariableSizeList</code> (har xil balandlik) "
            "komponentlari orqali amalga oshiradi.</p>"
            "<h3>Haqiqiy misol: LeaderBoard.js — kerakmi yoki yo'qmi?</h3>"
            "<p>Bu — ushbu platformaning haqiqiy kodi: <code>frontend/src/views/"
            "student/rankings/LeaderBoard.js</code> "
            "<code>v1/rankings/leaderboard?period=${{activeTab}}&amp;limit=50</code> "
            "so'rovini yuborib, natijada kelgan qatorlarni (podium'dan tashqari "
            "qolganlarini, <code>rest.map(...)</code> orqali) to'g'ridan-to'g'ri "
            "render qiladi — hech qanday windowing'siz. Savol: bu — muammomi? "
            "Halol javob: YO'Q, hozircha emas. 50 ta oddiy qator — zamonaviy brauzer "
            "uchun arzimas yuk; bu yerda virtualizatsiya qo'shish ortiqcha "
            "murakkablik bo'lardi (o'lchash Profiler'da hech qanday sezilarli vaqt "
            "ko'rsatmaydi). Lekin AGAR bu <code>limit=50</code> kelajakda butun "
            "maktab yoki hatto barcha talabalar bo'yicha reyting ko'rsatish uchun "
            "minglab qatorgacha oshirilsa — aynan o'sha payt, aynan shu "
            "<code>LeaderBoard.js</code> komponenti virtualizatsiyaga muhtoj "
            "bo'ladi. Bu — real chegara qayerda ekanini ko'rsatuvchi halol misol: "
            "muammo hozir yo'q, lekin qayerda paydo bo'lishi aniq bilinadi.</p>"
            "<h3>react-window bilan amalga oshirish</h3>"
            "<p>Faraz qiling, <code>LeaderBoard</code> minglab talabani ko'rsatishi "
            "kerak bo'lib qoldi. <code>FixedSizeList</code>ga <code>height</code> "
            "(ko'rinadigan balandlik), <code>itemCount</code> (jami qatorlar soni), "
            "<code>itemSize</code> (har bir qator balandligi piksellarda) va "
            "<code>children</code> sifatida har bir qatorni chizadigan funksiya "
            "beriladi — bu funksiya <code>index</code> va <code>style</code> "
            "prop'larini oladi. <code>style</code>ni albatta qatorning tashqi "
            "elementiga qo'llash SHART — aks holda kutubxonaning pozitsiyalash "
            "hisob-kitobi buziladi.</p>"
            "<h3>Muhim nuance: index-key bu yerda anti-pattern EMAS</h3"
            "><p>1-darslarda ko'rgan <code>key={{index}}</code> muammosidan farqli "
            "o'laroq, virtualizatsiya qilingan ro'yxatda qator <code>index</code>i "
            "aslida OYNA (window) ichidagi pozitsiyani bildiradi, ma'lumotning o'zini "
            "emas — shuning uchun bu yerda index asosidagi kalit to'g'ri va "
            "kutilgan holat.</p>"
            "<h3>Diagramma: barcha qatorlar va oynali render</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  subgraph ODDIY[\"Oddiy render - 5000 talaba\"]\n"
            "    A1[\"5000 ta DOM qator\n"
            "hammasi bir vaqtda mavjud\"]\n"
            "  end\n"
            "  subgraph VIRT[\"react-window - 5000 talaba\"]\n"
            "    B1[\"~15 ta DOM qator\n"
            "faqat ko'rinadigan + bufer\"]\n"
            "    B2[\"Bitta spacer\n"
            "scroll balandligini saqlaydi\"]\n"
            "    B1 -.->|\"scroll qilinsa\"| B3[\"Eski qatorlar chiqadi,\n"
            "yangilari kiradi\"]\n"
            "  end\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: ma'lumot hajmi bir xil (5000 talaba) "
            "bo'lsa ham, DOM'dagi haqiqiy qatorlar soni tubdan farq qiladi.</p>"
            "<h3>overscanCount va o'lchamni moslashtirish</h3>"
            "<p><code>FixedSizeList</code>ning <code>overscanCount</code> prop'i "
            "ko'rinadigan oynadan tashqarida qancha qo'shimcha qator oldindan "
            "render qilinishini belgilaydi (standart qiymat — 1). Buni oshirish tez "
            "scroll qilishda \"bo'sh joy miltillashi\"ni kamaytiradi, lekin har bir "
            "qo'shimcha qator DOM'ga qo'shimcha yuk qo'shadi — shuning uchun bu ham "
            "o'lchash bilan tanlanadigan muvozanat. Amalda konteyner kengligi "
            "moslashuvchan (responsive) bo'lishi kerak bo'lsa, "
            "<code>react-virtualized-auto-sizer</code> kutubxonasi "
            "<code>FixedSizeList</code>ni o'rab, unga aniq piksel <code>height</code>/"
            "<code>width</code> beradi — chunki virtualizatsiya kutubxonalari odatda "
            "aniq piksel o'lchamini talab qiladi, foiz (<code>%</code>) emas.</p>"
        ),
        "text_content_ru": (
            "<h3>Проблема: количество DOM-узлов растёт линейно</h3>"
            "<p>Если в списке N элементов, React обычно создаёт N DOM-узлов — даже "
            "если пользователь одновременно видит на экране всего 10-15 из них. "
            "Браузеру же приходится выполнять layout (расчёт расположения) и paint "
            "(отрисовку) для каждого DOM-узла. Если список состоит из нескольких "
            "десятков элементов, это незаметно. Но когда список достигает тысяч "
            "элементов — например, рейтинг по всей школе или подробная таблица "
            "сотен студентов — создание, расположение и перерисовка при скролле "
            "тысяч DOM-узлов может вызвать заметное замедление.</p>"
            "<h3>Решение: рендерить только видимые строки</h3>"
            "<p>Идея «виртуализации» (или «windowing») проста: рендерить не ВЕСЬ "
            "список, а только строки, которые пользователь ВИДИТ СЕЙЧАС (и небольшой "
            "буфер рядом). Вместо остальных строк ставится один большой «пустой "
            "промежуток» (spacer), чтобы высота скролла оставалась корректной — при "
            "скролле библиотека вычисляет, какие строки теперь попали в видимую "
            "область, РЕНДЕРИТ их и убирает те, что вышли за пределы экрана. В "
            "результате в DOM всегда всего несколько десятков строк — независимо от "
            "того, состоит ли список из 50 элементов или из 50 000. Библиотека "
            "<code>react-window</code> реализует именно эту идею через компоненты "
            "<code>FixedSizeList</code> (все строки одной высоты) и "
            "<code>VariableSizeList</code> (разная высота).</p>"
            "<h3>Реальный пример: LeaderBoard.js — нужно или нет?</h3>"
            "<p>Это настоящий код этой платформы: <code>frontend/src/views/student/"
            "rankings/LeaderBoard.js</code> отправляет запрос "
            "<code>v1/rankings/leaderboard?period=${{activeTab}}&amp;limit=50</code> и "
            "рендерит полученные строки (оставшихся после подиума, через "
            "<code>rest.map(...)</code>) напрямую — без какого-либо windowing. "
            "Вопрос: это проблема? Честный ответ: НЕТ, пока нет. 50 обычных строк — "
            "ничтожная нагрузка для современного браузера; добавление виртуализации "
            "здесь было бы излишней сложностью (измерение в Profiler не покажет "
            "никакого заметного времени). Но ЕСЛИ этот <code>limit=50</code> в "
            "будущем увеличится до тысяч строк для отображения рейтинга всей школы "
            "или всех студентов — именно тогда, именно этому компоненту "
            "<code>LeaderBoard.js</code> понадобится виртуализация. Это честный "
            "пример того, где именно проходит реальная граница: проблемы сейчас нет, "
            "но точно известно, где она появится.</p>"
            "<h3>Реализация через react-window</h3>"
            "<p>Представим, что <code>LeaderBoard</code> должен показывать тысячи "
            "студентов. <code>FixedSizeList</code> принимает <code>height</code> "
            "(видимую высоту), <code>itemCount</code> (общее число строк), "
            "<code>itemSize</code> (высоту одной строки в пикселях) и "
            "<code>children</code> — функцию, рисующую каждую строку; эта функция "
            "получает props <code>index</code> и <code>style</code>. "
            "<code>style</code> ОБЯЗАТЕЛЬНО нужно применить к внешнему элементу "
            "строки — иначе расчёт позиционирования библиотеки сломается.</p>"
            "<h3>Важный нюанс: index-key здесь НЕ антипаттерн</h3>"
            "<p>В отличие от проблемы <code>key={{index}}</code> из уроков 1-4, в "
            "виртуализированном списке <code>index</code> строки на самом деле "
            "обозначает позицию внутри ОКНА (window), а не саму сущность данных — "
            "поэтому здесь ключ на основе index — правильное и ожидаемое "
            "решение.</p>"
            "<h3>Диаграмма: обычный рендер и оконный рендер</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  subgraph OBYCHNYI[\"Обычный рендер - 5000 студентов\"]\n"
            "    A1[\"5000 DOM-строк\n"
            "все существуют одновременно\"]\n"
            "  end\n"
            "  subgraph VIRT[\"react-window - 5000 студентов\"]\n"
            "    B1[\"~15 DOM-строк\n"
            "только видимые + буфер\"]\n"
            "    B2[\"Один spacer\n"
            "сохраняет высоту скролла\"]\n"
            "    B1 -.->|\"при скролле\"| B3[\"Старые строки уходят,\n"
            "новые появляются\"]\n"
            "  end\n"
            "</pre>"
            "<p>Диаграмма показывает: при одинаковом объёме данных (5000 студентов) "
            "реальное число строк в DOM отличается кардинально.</p>"
            "<h3>overscanCount и адаптация размера</h3>"
            "<p>Проп <code>overscanCount</code> у <code>FixedSizeList</code> задаёт, "
            "сколько дополнительных строк за пределами видимого окна рендерится "
            "заранее (значение по умолчанию — 1). Увеличение этого значения снижает "
            "«мелькание пустоты» при быстром скролле, но каждая дополнительная строка "
            "добавляет нагрузку на DOM — так что это тоже баланс, который выбирается "
            "измерением. На практике, если ширина контейнера должна быть адаптивной, "
            "библиотека <code>react-virtualized-auto-sizer</code> оборачивает "
            "<code>FixedSizeList</code> и передаёт ему точные пиксельные "
            "<code>height</code>/<code>width</code> — потому что библиотеки "
            "виртуализации обычно требуют точный пиксельный размер, а не проценты "
            "(<code>%</code>).</p>"
        ),
        "code_content": (
            "// LeaderBoard.js'ning haqiqiy naqshi (soddalashtirilgan) — hozirgi\n"
            "// holatda virtualizatsiyasiz, chunki limit=50 kichik.\n"
            "function LeaderboardRestReal({ rest, getPoints }) {\n"
            "  return (\n"
            "    <div className=\"lb-list\">\n"
            "      {rest.map((student, idx) => (\n"
            "        <div key={student.id} className=\"lb-row\">\n"
            "          <span>{idx + 4}</span>\n"
            "          <span>{student.full_name}</span>\n"
            "          <span>{getPoints(student)} pts</span>\n"
            "        </div>\n"
            "      ))}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// Faraziy kengaytma: agar limit minglabgacha oshsa, shu komponentni\n"
            "// react-window bilan qanday qayta yozgan bo'lardik.\n"
            "import { FixedSizeList } from 'react-window';\n\n"
            "function LeaderboardRestVirtualized({ rest, getPoints }) {\n"
            "  const Row = ({ index, style }) => {\n"
            "    const student = rest[index];\n"
            "    return (\n"
            "      // style — MAJBURIY, u qatorning aniq joylashuvini belgilaydi.\n"
            "      <div style={style} className=\"lb-row\">\n"
            "        <span>{index + 4}</span>\n"
            "        <span>{student.full_name}</span>\n"
            "        <span>{getPoints(student)} pts</span>\n"
            "      </div>\n"
            "    );\n"
            "  };\n\n"
            "  return (\n"
            "    <FixedSizeList\n"
            "      height={480}          // ko'rinadigan balandlik (piksel)\n"
            "      width=\"100%\"\n"
            "      itemCount={rest.length}\n"
            "      itemSize={56}         // har bir qator balandligi\n"
            "    >\n"
            "      {Row}\n"
            "    </FixedSizeList>\n"
            "  );\n"
            "}\n\n"
            "// Taqqoslash uchun kichik yordamchi: ro'yxat hajmiga qarab qaysi\n"
            "// yondashuvni tanlashni ko'rsatadigan sodda qoida.\n"
            "function chooseRenderStrategy(itemCount) {\n"
            "  // Bu — qat'iy son emas, taxminiy yo'l ko'rsatuvchi chegara: haqiqiy\n"
            "  // qaror har doim Profiler o'lchovi bilan tasdiqlanishi kerak.\n"
            "  return itemCount > 300\n"
            "    ? 'virtualizatsiya (react-window) ko\\'rib chiqing'\n"
            "    : 'oddiy .map() yetarli';\n"
            "}\n\n"
            "// Konteyner kengligi moslashuvchan bo'lganda ishlatiladigan haqiqiy\n"
            "// naqsh — react-virtualized-auto-sizer aniq piksel o'lcham beradi.\n"
            "import AutoSizer from 'react-virtualized-auto-sizer';\n\n"
            "function LeaderboardResponsive({ rest, getPoints }) {\n"
            "  const Row = ({ index, style }) => (\n"
            "    <div style={style} className=\"lb-row\">\n"
            "      {rest[index].full_name} — {getPoints(rest[index])} pts\n"
            "    </div>\n"
            "  );\n"
            "  return (\n"
            "    <div style={{ height: 480 }}>\n"
            "      <AutoSizer>\n"
            "        {({ height, width }) => (\n"
            "          <FixedSizeList\n"
            "            height={height}\n"
            "            width={width}\n"
            "            itemCount={rest.length}\n"
            "            itemSize={56}\n"
            "            overscanCount={4}\n"
            "          >\n"
            "            {Row}\n"
            "          </FixedSizeList>\n"
            "        )}\n"
            "      </AutoSizer>\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// VariableSizeList — qatorlar har xil balandlikda bo'lsa (masalan,\n"
            "// ba'zi talabalarning ismi ikki qatorga tushsa). itemSize endi\n"
            "// funksiya bo'ladi: har bir index uchun balandlikni qaytaradi.\n"
            "import { VariableSizeList } from 'react-window';\n\n"
            "function LeaderboardVariable({ rest, getPoints }) {\n"
            "  const getItemSize = (index) =>\n"
            "    rest[index].full_name.length > 20 ? 72 : 56;\n"
            "  const Row = ({ index, style }) => (\n"
            "    <div style={style} className=\"lb-row\">\n"
            "      {rest[index].full_name} — {getPoints(rest[index])} pts\n"
            "    </div>\n"
            "  );\n"
            "  return (\n"
            "    <VariableSizeList\n"
            "      height={480}\n"
            "      width=\"100%\"\n"
            "      itemCount={rest.length}\n"
            "      itemSize={getItemSize}\n"
            "    >\n"
            "      {Row}\n"
            "    </VariableSizeList>\n"
            "  );\n"
            "}\n"
        ),
        "code_content_ru": (
            "// Реальный (упрощённый) паттерн LeaderBoard.js — сейчас без\n"
            "// виртуализации, потому что limit=50 небольшой.\n"
            "function LeaderboardRestReal({ rest, getPoints }) {\n"
            "  return (\n"
            "    <div className=\"lb-list\">\n"
            "      {rest.map((student, idx) => (\n"
            "        <div key={student.id} className=\"lb-row\">\n"
            "          <span>{idx + 4}</span>\n"
            "          <span>{student.full_name}</span>\n"
            "          <span>{getPoints(student)} pts</span>\n"
            "        </div>\n"
            "      ))}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// Гипотетическое расширение: как выглядел бы этот же компонент через\n"
            "// react-window, если бы limit вырос до тысяч.\n"
            "import { FixedSizeList } from 'react-window';\n\n"
            "function LeaderboardRestVirtualized({ rest, getPoints }) {\n"
            "  const Row = ({ index, style }) => {\n"
            "    const student = rest[index];\n"
            "    return (\n"
            "      // style — ОБЯЗАТЕЛЕН, задаёт точное расположение строки.\n"
            "      <div style={style} className=\"lb-row\">\n"
            "        <span>{index + 4}</span>\n"
            "        <span>{student.full_name}</span>\n"
            "        <span>{getPoints(student)} pts</span>\n"
            "      </div>\n"
            "    );\n"
            "  };\n\n"
            "  return (\n"
            "    <FixedSizeList\n"
            "      height={480}          // видимая высота (пиксели)\n"
            "      width=\"100%\"\n"
            "      itemCount={rest.length}\n"
            "      itemSize={56}         // высота одной строки\n"
            "    >\n"
            "      {Row}\n"
            "    </FixedSizeList>\n"
            "  );\n"
            "}\n\n"
            "// Небольшой помощник для сравнения: простое правило выбора подхода в\n"
            "// зависимости от размера списка.\n"
            "function chooseRenderStrategy(itemCount) {\n"
            "  // Это не точное число, а примерный ориентир: реальное решение\n"
            "  // всегда должно подтверждаться измерением в Profiler.\n"
            "  return itemCount > 300\n"
            "    ? 'рассмотрите виртуализацию (react-window)'\n"
            "    : 'обычного .map() достаточно';\n"
            "}\n\n"
            "// Реальный паттерн для адаптивной ширины контейнера —\n"
            "// react-virtualized-auto-sizer даёт точный пиксельный размер.\n"
            "import AutoSizer from 'react-virtualized-auto-sizer';\n\n"
            "function LeaderboardResponsive({ rest, getPoints }) {\n"
            "  const Row = ({ index, style }) => (\n"
            "    <div style={style} className=\"lb-row\">\n"
            "      {rest[index].full_name} — {getPoints(rest[index])} pts\n"
            "    </div>\n"
            "  );\n"
            "  return (\n"
            "    <div style={{ height: 480 }}>\n"
            "      <AutoSizer>\n"
            "        {({ height, width }) => (\n"
            "          <FixedSizeList\n"
            "            height={height}\n"
            "            width={width}\n"
            "            itemCount={rest.length}\n"
            "            itemSize={56}\n"
            "            overscanCount={4}\n"
            "          >\n"
            "            {Row}\n"
            "          </FixedSizeList>\n"
            "        )}\n"
            "      </AutoSizer>\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// VariableSizeList — когда строки разной высоты (например, у части\n"
            "// студентов имя переносится на две строки). itemSize теперь функция:\n"
            "// возвращает высоту для каждого index.\n"
            "import { VariableSizeList } from 'react-window';\n\n"
            "function LeaderboardVariable({ rest, getPoints }) {\n"
            "  const getItemSize = (index) =>\n"
            "    rest[index].full_name.length > 20 ? 72 : 56;\n"
            "  const Row = ({ index, style }) => (\n"
            "    <div style={style} className=\"lb-row\">\n"
            "      {rest[index].full_name} — {getPoints(rest[index])} pts\n"
            "    </div>\n"
            "  );\n"
            "  return (\n"
            "    <VariableSizeList\n"
            "      height={480}\n"
            "      width=\"100%\"\n"
            "      itemCount={rest.length}\n"
            "      itemSize={getItemSize}\n"
            "    >\n"
            "      {Row}\n"
            "    </VariableSizeList>\n"
            "  );\n"
            "}\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Berilgan uzun ro'yxatga react-window qo'shing",
            "task_title_ru": "Добавьте react-window к данному длинному списку",
            "task_description": (
                "Sizga 3000 ta elementli oddiy .map() orqali render qilinadigan "
                "ro'yxat komponenti beriladi (masalan, talabalar ro'yxati). Uni "
                "react-window'ning FixedSizeList komponenti bilan virtualizatsiya "
                "qiling: height, itemCount, itemSize prop'larini to'g'ri sozlang va "
                "har bir qatorga style prop'ini albatta qo'llang. Virtualizatsiyadan "
                "oldin va keyin DOM'dagi haqiqiy qator elementlari sonini brauzer "
                "DevTools orqali solishtirib, natijani yozing."
            ),
            "task_description_ru": (
                "Вам дан обычный компонент списка из 3000 элементов, рендерящийся "
                "через простой .map() (например, список студентов). "
                "Виртуализируйте его через компонент FixedSizeList из "
                "react-window: правильно настройте пропсы height, itemCount, "
                "itemSize и обязательно примените проп style к каждой строке. "
                "Сравните реальное число элементов-строк в DOM до и после "
                "виртуализации через DevTools браузера и запишите результат."
            ),
            "task_requirements": (
                "FixedSizeList to'g'ri sozlangan bo'lishi, style prop har bir "
                "qatorga qo'llanishi shart. DOM'dagi qator soni taqqoslamasi (oldin "
                "3000 ga yaqin, keyin bir necha o'nlab) yozma yoki skrinshot bilan "
                "taqdim etilishi kerak."
            ),
            "task_requirements_ru": (
                "FixedSizeList обязан быть правильно настроен, проп style должен "
                "применяться к каждой строке. Сравнение числа строк в DOM (до — "
                "около 3000, после — несколько десятков) должно быть представлено "
                "письменно или скриншотом."
            ),
            "task_technologies": "React, react-window",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: react-window bilan virtualizatsiya",
            "description": "Minglab qatorli ro'yxatni faqat ko'rinadigan qismini render qiluvchi FixedSizeList namunasi.",
            "sample_type": "code",
            "code_files": [
                {"filename": "VirtualizedList.jsx", "language": "jsx", "code": (
                    "import { FixedSizeList } from 'react-window';\n\n"
                    "export default function VirtualizedList({ items }) {\n"
                    "  const Row = ({ index, style }) => (\n"
                    "    <div style={style}>{items[index].full_name}</div>\n"
                    "  );\n"
                    "  return (\n"
                    "    <FixedSizeList height={400} width=\"100%\" itemCount={items.length} itemSize={48}>\n"
                    "      {Row}\n"
                    "    </FixedSizeList>\n"
                    "  );\n"
                    "}\n"
                )},
            ],
        },
        "exercises": [
            {
                "title": "Virtualizatsiya nima qiladi",
                "title_ru": "Что делает виртуализация",
                "description": "react-window kabi kutubxonalar asosan nimani amalga oshiradi?",
                "description_ru": "Что в основном реализуют библиотеки вроде react-window?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Faqat ko'rinadigan qatorlarni DOM'da render qilib, qolganini spacer bilan almashtiradi",
                    "Ma'lumotlarni serverda oldindan saralaydi",
                    "CSS animatsiyalarini tezlashtiradi",
                    "Rasm fayllarini siqadi",
                ],
                "options_ru": [
                    "Рендерят в DOM только видимые строки, остальное заменяют spacer'ом",
                    "Предварительно сортируют данные на сервере",
                    "Ускоряют CSS-анимации",
                    "Сжимают файлы изображений",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"Windowing\" atamasi darsda ta'riflangan.",
                "hint_ru": "Термин «windowing» определён в уроке.",
                "explanation": "Virtualizatsiya DOM'da doim kichik, sobit sonli qatorni saqlaydi, scroll paytida ularni almashtiradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "LeaderBoard'ning hozirgi holati",
                "title_ru": "Текущее состояние LeaderBoard",
                "description": (
                    "Bo'shliqni to'ldiring: LeaderBoard.js hozircha limit=___ so'rov "
                    "yuborgani uchun virtualizatsiyaga muhtoj emas."
                ),
                "description_ru": (
                    "Заполните пропуск: LeaderBoard.js пока не нуждается в "
                    "виртуализации, потому что отправляет запрос с limit=___."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "50",
                "hint": "Darsda ko'rsatilgan haqiqiy so'rov parametrini eslang.",
                "hint_ru": "Вспомните реальный параметр запроса, показанный в уроке.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "FixedSizeList prop'lari",
                "title_ru": "Пропсы FixedSizeList",
                "description": "FixedSizeList'ning kerakli prop'larini mos ta'riflari bilan moslashtiring (tartib: height, itemCount, itemSize, keyingi — mos tavsif).",
                "description_ru": "Сопоставьте нужные пропсы FixedSizeList с их описаниями (порядок: height, itemCount, itemSize, далее — соответствующее описание).",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "height — ko'rinadigan oyna balandligi",
                    "itemCount — jami qatorlar soni",
                    "itemSize — har bir qator balandligi",
                    "style — qatorga MAJBURIY qo'llanadigan pozitsiya",
                ],
                "drag_items_ru": [
                    "height — высота видимого окна",
                    "itemCount — общее число строк",
                    "itemSize — высота одной строки",
                    "style — ОБЯЗАТЕЛЬНАЯ позиция для строки",
                ],
                "correct_order": [
                    "height — ko'rinadigan oyna balandligi",
                    "itemCount — jami qatorlar soni",
                    "itemSize — har bir qator balandligi",
                    "style — qatorga MAJBURIY qo'llanadigan pozitsiya",
                ],
                "hint": "Darsdagi kod namunasidagi prop'lar tartibini eslang.",
                "hint_ru": "Вспомните порядок пропсов в примере кода урока.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 6,
        "title": "6-Context re-render tuzoqlari",
        "title_ru": "6-Ловушки ре-рендера через Context",
        "points_reward": 15,
        "text_content": (
            "<h3>Context qanday ishlaydi — qisqacha eslatma</h3>"
            "<p><code>createContext</code> + <code>&lt;Provider value={{...}}&gt;</code> "
            "— komponent daraxti bo'ylab props orqali \"prop drilling\" qilmasdan "
            "ma'lumot uzatish usuli. <code>useContext(MyContext)</code> chaqirgan HAR "
            "BIR komponent — Provider'ning <code>value</code>si o'zgarganda AVTOMATIK "
            "qayta render bo'ladi. Aynan shu yerda eng ko'p uchraydigan tuzoq "
            "yashiringan: <strong>Context'ning butun <code>value</code>si BITTA "
            "birlik sifatida qaraladi — komponent value ichidagi qaysi maydonni "
            "o'qishidan qat'i nazar, HAR QANDAY maydon o'zgarishi uni qayta render "
            "qiladi</strong>.</p>"
            "<h3>Haqiqiy misol: StoreContext.js</h3>"
            "<p>Bu — ushbu platformaning haqiqiy kodi: <code>frontend/src/context/"
            "StoreContext.js</code>dagi <code>value</code> "
            "<code>useMemo</code> bilan to'g'ri keshlangan — bu yaxshi amaliyot. "
            "Lekin uning ICHIDA <strong>oltita</strong> turli xil narsa birlashtirilgan: "
            "<code>balance</code>, <code>lifetimePoints</code>, <code>recent</code>, "
            "<code>inventory</code>, <code>equipped</code>, <code>loading</code> — "
            "hammasi BITTA obyekt sifatida. Tasavvur qiling: sarlavhadagi tanga "
            "balansini ko'rsatuvchi kichik komponent faqat <code>balance</code>ni "
            "o'qiydi (<code>useStore().balance</code>). Foydalanuvchi do'kon sahifasida "
            "buyum ko'rib chiqsa va <code>inventory</code> yangilansa (masalan, "
            "<code>refreshInventory()</code> chaqirilsa) — <code>value</code> obyekti "
            "<code>useMemo</code> deps ro'yxatida <code>inventory</code> borligi "
            "sababli YANGI reference oladi, va bu esa <code>balance</code>ga "
            "umuman qiziqmagan sarlavha komponentini ham qayta render qiladi.</p>"
            "<h3>Yanada aniqroq misol: AuthContext.js</h3>"
            "<p><code>frontend/src/context/AuthContext.js</code>da bu muammo yanada "
            "yaqqolroq: <code>&lt;AuthContext.Provider value={{{{ user, "
            "isAuthenticated, login, logout }}}}&gt;</code> — bu qator "
            "<code>useMemo</code>siz, oddiy obyekt literali. Demak, "
            "<code>AuthProvider</code> HAR safar qayta render bo'lganda (masalan, "
            "ota komponentlardan biri render bo'lgani uchun kaskad orqali), "
            "<code>value</code> obyekti YANGI reference oladi — hatto "
            "<code>user</code>, <code>isAuthenticated</code>, <code>login</code>, "
            "<code>logout</code>ning HAMMASI aslida bir xil qolgan bo'lsa ham. Bu esa "
            "<code>useAuth()</code>ni chaqirgan HAMMA komponentni qayta render "
            "qiladi. Halol izoh: bu ikkalasi ham amaliy jihatdan hozircha katta "
            "muammo emas, chunki <code>AuthProvider</code> kamdan-kam qayta render "
            "bo'ladi — lekin bu aynan shunday xatolar qanday ko'rinishini "
            "ko'rsatuvchi haqiqiy, aniqlanadigan misol.</p>"
            "<h3>Yechim: Context'ni ajratish (splitting)</h3>"
            "<p>Bitta katta Context o'rniga, kam-kam o'zgaradigan ma'lumot (masalan, "
            "<code>user</code>, <code>login</code>, <code>logout</code>) va tez-tez "
            "o'zgaradigan ma'lumot (masalan, <code>inventory</code>) uchun ALOHIDA "
            "Context'lar yaratish mumkin. Shunda faqat kerakli Context'ga obuna "
            "bo'lgan komponentlar tegishli o'zgarishda qayta render bo'ladi. "
            "Muqobil yondashuv — <code>useSyncExternalStore</code> yoki tashqi holat "
            "kutubxonasi (masalan, Zustand) orqali \"selector\" naqshini qo'llash, u "
            "komponentga faqat u aslida o'qigan qismi o'zgarganda qayta render "
            "berishga imkon beradi — bu 9-darsda Redux selector'lari bilan yanada "
            "chuqurroq ko'riladigan naqsh bilan bir xil g'oya.</p>"
            "<h3>Diagramma: bitta Context, ko'p iste'molchi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  V[\"StoreContext value o'zgaradi\n"
            "(faqat inventory yangilandi)\"] --> C1[\"BalanceChip\n"
            "faqat balance'ni o'qiydi\n"
            "LEKIN baribir qayta render\"]\n"
            "  V --> C2[\"InventoryGrid\n"
            "inventory'ni o'qiydi\n"
            "haqiqatan render kerak\"]\n"
            "  V --> C3[\"ThemeSwitcher\n"
            "faqat equipped'ni o'qiydi\n"
            "LEKIN baribir qayta render\"]\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: faqat <code>InventoryGrid</code>ning "
            "qayta render bo'lishi kerak edi, lekin bitta birlashtirilgan Context "
            "value tufayli <code>BalanceChip</code> va <code>ThemeSwitcher</code> ham "
            "keraksiz qayta render bo'ladi.</p>"
            "<h3>Context — bu \"state management kutubxonasi\" emas</h3>"
            "<p>Muhim kontseptual farq: <strong>Context — bu faqat ma'lumot uzatish "
            "mexanizmi</strong> (props'ning muqobili), <strong>state management "
            "yechimi emas</strong>. Redux yoki Zustand kabi kutubxonalar har bir "
            "iste'molchiga faqat u aslida o'qigan qismi o'zgarganda qayta render "
            "berish uchun махсус \"selector\" mexanizmini o'z ichiga oladi (buni "
            "9-darsda Redux Toolkit orqali batafsil ko'ramiz). Context'ning o'zida "
            "esa bunday selektiv obuna yo'q — shuning uchun tez-tez o'zgaradigan "
            "global holat uchun Context'ni ehtiyotkorlik bilan, faqat kichik va "
            "kamdan-kam o'zgaradigan ma'lumotlar uchun ishlatish tavsiya etiladi.</p>"
        ),
        "text_content_ru": (
            "<h3>Как работает Context — краткое напоминание</h3>"
            "<p><code>createContext</code> + <code>&lt;Provider value={{...}}&gt;</code> "
            "— способ передавать данные по дереву компонентов без «prop drilling» "
            "через props. КАЖДЫЙ компонент, вызвавший <code>useContext(MyContext)</code>, "
            "АВТОМАТИЧЕСКИ перерендеривается при изменении <code>value</code> "
            "Provider'а. Именно здесь скрыта самая частая ловушка: <strong>весь "
            "<code>value</code> Context'а рассматривается как ЕДИНОЕ целое — "
            "независимо от того, какое поле внутри value читает компонент, ЛЮБОЕ "
            "изменение любого поля перерендерит его</strong>.</p>"
            "<h3>Реальный пример: StoreContext.js</h3>"
            "<p>Это настоящий код этой платформы: в <code>frontend/src/context/"
            "StoreContext.js</code> <code>value</code> правильно закеширован через "
            "<code>useMemo</code> — это хорошая практика. Но ВНУТРИ него объединены "
            "<strong>шесть</strong> разных вещей: <code>balance</code>, "
            "<code>lifetimePoints</code>, <code>recent</code>, <code>inventory</code>, "
            "<code>equipped</code>, <code>loading</code> — всё в ОДНОМ объекте. "
            "Представьте: маленький компонент в шапке, показывающий баланс монет, "
            "читает только <code>balance</code> (<code>useStore().balance</code>). "
            "Если пользователь просматривает товары в магазине и обновляется "
            "<code>inventory</code> (например, вызывается "
            "<code>refreshInventory()</code>) — объект <code>value</code> получает "
            "НОВУЮ ссылку, так как <code>inventory</code> есть в списке deps "
            "<code>useMemo</code>, и это перерендерит компонент шапки, которому "
            "<code>inventory</code> вообще не интересен.</p>"
            "<h3>Ещё более явный пример: AuthContext.js</h3>"
            "<p>В <code>frontend/src/context/AuthContext.js</code> эта проблема ещё "
            "заметнее: <code>&lt;AuthContext.Provider value={{{{ user, "
            "isAuthenticated, login, logout }}}}&gt;</code> — эта строка БЕЗ "
            "<code>useMemo</code>, обычный объектный литерал. Значит, КАЖДЫЙ раз, "
            "когда <code>AuthProvider</code> перерендеривается (например, каскадом "
            "из-за рендера одного из родителей), объект <code>value</code> получает "
            "НОВУЮ ссылку — даже если <code>user</code>, <code>isAuthenticated</code>, "
            "<code>login</code>, <code>logout</code> все остались теми же. Это "
            "перерендерит ВСЕ компоненты, вызвавшие <code>useAuth()</code>. Честная "
            "оговорка: на практике оба случая пока не большая проблема, поскольку "
            "<code>AuthProvider</code> редко перерендеривается — но это реальный, "
            "проверяемый пример того, как выглядят подобные ошибки.</p>"
            "<h3>Решение: разделение Context (splitting)</h3>"
            "<p>Вместо одного большого Context можно создать ОТДЕЛЬНЫЕ Context для "
            "редко меняющихся данных (например, <code>user</code>, <code>login</code>, "
            "<code>logout</code>) и часто меняющихся (например, <code>inventory</code>). "
            "Тогда перерендерятся только компоненты, подписанные на соответствующий "
            "Context. Альтернативный подход — паттерн «selector» через "
            "<code>useSyncExternalStore</code> или внешнюю библиотеку состояния "
            "(например, Zustand), который позволяет компоненту перерендериваться "
            "только при изменении той части, которую он реально читает — та же идея, "
            "что мы подробнее разберём с селекторами Redux в уроке 9.</p>"
            "<h3>Диаграмма: один Context, много потребителей</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  V[\"Значение StoreContext меняется\n"
            "(обновился только inventory)\"] --> C1[\"BalanceChip\n"
            "читает только balance\n"
            "НО всё равно перерендер\"]\n"
            "  V --> C2[\"InventoryGrid\n"
            "читает inventory\n"
            "действительно нужен рендер\"]\n"
            "  V --> C3[\"ThemeSwitcher\n"
            "читает только equipped\n"
            "НО всё равно перерендер\"]\n"
            "</pre>"
            "<p>Диаграмма показывает: перерендериться должен был только "
            "<code>InventoryGrid</code>, но из-за одного объединённого значения "
            "Context <code>BalanceChip</code> и <code>ThemeSwitcher</code> тоже "
            "перерендериваются без необходимости.</p>"
            "<h3>Context — это не «библиотека управления состоянием»</h3>"
            "<p>Важное концептуальное отличие: <strong>Context — это лишь механизм "
            "передачи данных</strong> (альтернатива props), <strong>а не решение "
            "для управления состоянием</strong>. Библиотеки вроде Redux или Zustand "
            "включают специальный механизм «selector», позволяющий каждому "
            "потребителю перерендериваться только при изменении той части, которую "
            "он реально читает (подробно разберём это с Redux Toolkit в уроке 9). У "
            "самого Context такой избирательной подписки нет — поэтому для часто "
            "меняющегося глобального состояния Context рекомендуется использовать "
            "осторожно, только для небольших и редко меняющихся данных.</p>"
        ),
        "code_content": (
            "// StoreContext.js'ning haqiqiy naqshi (soddalashtirilgan iqtibos):\n"
            "// value useMemo bilan keshlangan, lekin oltita narsa birlashtirilgan.\n"
            "const value = React.useMemo(() => ({\n"
            "  balance, lifetimePoints, recent, inventory, equipped, loading,\n"
            "  refreshWallet, refreshInventory, refreshAll,\n"
            "}), [balance, lifetimePoints, recent, inventory, equipped, loading,\n"
            "     refreshWallet, refreshInventory, refreshAll]);\n\n"
            "// Muammo: faqat balance'ni o'qigan komponent ham inventory\n"
            "// o'zgarganda qayta render bo'ladi, chunki value bitta obyekt.\n"
            "function BalanceChip() {\n"
            "  const { balance } = useStore(); // faqat balance kerak\n"
            "  return <span>{balance} tanga</span>;\n"
            "}\n\n"
            "// YECHIM: ikkita alohida Context — kam o'zgaradigan va tez-tez\n"
            "// o'zgaradigan qismlar uchun.\n"
            "const WalletContext = React.createContext(null);   // balance, lifetimePoints\n"
            "const InventoryContext = React.createContext(null); // inventory, equipped\n\n"
            "function StoreProviderSplit({ children }) {\n"
            "  const [balance, setBalance] = React.useState(null);\n"
            "  const [inventory, setInventory] = React.useState([]);\n\n"
            "  const walletValue = React.useMemo(\n"
            "    () => ({ balance, setBalance }),\n"
            "    [balance]\n"
            "  );\n"
            "  const inventoryValue = React.useMemo(\n"
            "    () => ({ inventory, setInventory }),\n"
            "    [inventory]\n"
            "  );\n\n"
            "  return (\n"
            "    <WalletContext.Provider value={walletValue}>\n"
            "      <InventoryContext.Provider value={inventoryValue}>\n"
            "        {children}\n"
            "      </InventoryContext.Provider>\n"
            "    </WalletContext.Provider>\n"
            "  );\n"
            "}\n\n"
            "// Endi BalanceChip faqat WalletContext'ga obuna bo'ladi — inventory\n"
            "// o'zgarishi uni umuman qayta render qilmaydi.\n"
            "function BalanceChipSplit() {\n"
            "  const { balance } = React.useContext(WalletContext);\n"
            "  return <span>{balance} tanga</span>;\n"
            "}\n\n"
            "// AuthContext.js'dagi muammoning tuzatilgan varianti: value albatta\n"
            "// useMemo bilan o'ralishi kerak, bo'sh obyekt literali emas.\n"
            "function AuthProviderFixed({ children }) {\n"
            "  const [user, setUser] = React.useState(null);\n"
            "  const [token, setToken] = React.useState(null);\n"
            "  const isAuthenticated = React.useMemo(() => !!user && !!token, [user, token]);\n"
            "  const login = React.useCallback((u, t) => { setUser(u); setToken(t); }, []);\n"
            "  const logout = React.useCallback(() => { setUser(null); setToken(null); }, []);\n\n"
            "  // TUZATISH: value endi useMemo bilan barqarorlashtirilgan.\n"
            "  const value = React.useMemo(\n"
            "    () => ({ user, isAuthenticated, login, logout }),\n"
            "    [user, isAuthenticated, login, logout]\n"
            "  );\n"
            "  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;\n"
            "}\n\n"
            "// Muhim halol ogohlantirish: \"selector\" funksiyasini qo'lda yozib,\n"
            "// useContext ustiga qo'yish YECHIM EMAS — useContext baribir Context\n"
            "// value o'zgargan HAR safar komponentni qayta render qiladi, selector\n"
            "// faqat QAYSI QIYMATNI o'qishni tanlaydi, QACHON render bo'lishini emas.\n"
            "function useStoreSelectorNaive(selector) {\n"
            "  const store = useContext(StoreContext); // baribor HAR o'zgarishda ishlaydi\n"
            "  return selector(store); // bu faqat o'qishni soddalashtiradi, render'ni emas\n"
            "}\n"
            "// Haqiqiy selektiv obuna uchun Context'ning o'zi yetarli emas — buning\n"
            "// uchun 'use-context-selector' kutubxonasi yoki tashqi do'kon (Zustand\n"
            "// kabi) + useSyncExternalStore kerak, chunki ular komponentni faqat\n"
            "// TANLANGAN qism o'zgarganda qayta render qilishga imkon beradi.\n"
        ),
        "code_content_ru": (
            "// Реальный (упрощённый) паттерн StoreContext.js: value закеширован\n"
            "// через useMemo, но внутри объединены шесть разных вещей.\n"
            "const value = React.useMemo(() => ({\n"
            "  balance, lifetimePoints, recent, inventory, equipped, loading,\n"
            "  refreshWallet, refreshInventory, refreshAll,\n"
            "}), [balance, lifetimePoints, recent, inventory, equipped, loading,\n"
            "     refreshWallet, refreshInventory, refreshAll]);\n\n"
            "// Проблема: даже компонент, читающий только balance, перерендерится\n"
            "// при изменении inventory, потому что value — один объект.\n"
            "function BalanceChip() {\n"
            "  const { balance } = useStore(); // нужен только balance\n"
            "  return <span>{balance} монет</span>;\n"
            "}\n\n"
            "// РЕШЕНИЕ: два отдельных Context — для редко и часто меняющихся\n"
            "// частей.\n"
            "const WalletContext = React.createContext(null);   // balance, lifetimePoints\n"
            "const InventoryContext = React.createContext(null); // inventory, equipped\n\n"
            "function StoreProviderSplit({ children }) {\n"
            "  const [balance, setBalance] = React.useState(null);\n"
            "  const [inventory, setInventory] = React.useState([]);\n\n"
            "  const walletValue = React.useMemo(\n"
            "    () => ({ balance, setBalance }),\n"
            "    [balance]\n"
            "  );\n"
            "  const inventoryValue = React.useMemo(\n"
            "    () => ({ inventory, setInventory }),\n"
            "    [inventory]\n"
            "  );\n\n"
            "  return (\n"
            "    <WalletContext.Provider value={walletValue}>\n"
            "      <InventoryContext.Provider value={inventoryValue}>\n"
            "        {children}\n"
            "      </InventoryContext.Provider>\n"
            "    </WalletContext.Provider>\n"
            "  );\n"
            "}\n\n"
            "// Теперь BalanceChip подписан только на WalletContext — изменение\n"
            "// inventory вообще его не перерендерит.\n"
            "function BalanceChipSplit() {\n"
            "  const { balance } = React.useContext(WalletContext);\n"
            "  return <span>{balance} монет</span>;\n"
            "}\n\n"
            "// Исправленный вариант проблемы из AuthContext.js: value обязательно\n"
            "// должен быть обёрнут в useMemo, а не быть пустым объектным литералом.\n"
            "function AuthProviderFixed({ children }) {\n"
            "  const [user, setUser] = React.useState(null);\n"
            "  const [token, setToken] = React.useState(null);\n"
            "  const isAuthenticated = React.useMemo(() => !!user && !!token, [user, token]);\n"
            "  const login = React.useCallback((u, t) => { setUser(u); setToken(t); }, []);\n"
            "  const logout = React.useCallback(() => { setUser(null); setToken(null); }, []);\n\n"
            "  // ИСПРАВЛЕНИЕ: value теперь стабилизирован через useMemo.\n"
            "  const value = React.useMemo(\n"
            "    () => ({ user, isAuthenticated, login, logout }),\n"
            "    [user, isAuthenticated, login, logout]\n"
            "  );\n"
            "  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;\n"
            "}\n\n"
            "// Важное честное предостережение: написать вручную функцию\n"
            "// «selector» поверх useContext — НЕ РЕШЕНИЕ — useContext всё равно\n"
            "// перерендерит компонент при КАЖДОМ изменении value Context, selector\n"
            "// лишь выбирает КАКОЕ значение читать, а не КОГДА рендериться.\n"
            "function useStoreSelectorNaive(selector) {\n"
            "  const store = useContext(StoreContext); // работает при ЛЮБОМ изменении\n"
            "  return selector(store); // упрощает только чтение, не рендер\n"
            "}\n"
            "// Для настоящей избирательной подписки самого Context недостаточно —\n"
            "// нужна библиотека 'use-context-selector' или внешнее хранилище\n"
            "// (вроде Zustand) + useSyncExternalStore, которые позволяют\n"
            "// перерендерить компонент только при изменении ВЫБРАННОЙ части.\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Bitta bloklangan Context'ni ajrating",
            "task_title_ru": "Разделите один раздутый Context",
            "task_description": (
                "Sizga bitta katta AppContext beriladi — uning value'sida "
                "\"theme\" (kam o'zgaradi) va \"notifications\" (tez-tez, "
                "sekundiga bir necha marta yangilanadi) birga saqlangan, "
                "useMemo'siz. Faqat \"theme\"ni o'qiydigan kichik komponent "
                "(masalan ThemeIcon) bor. Buni ikkita alohida Context'ga "
                "(ThemeContext va NotificationsContext) ajrating, har birining "
                "value'sini useMemo bilan keshlang, va ThemeIcon endi "
                "\"notifications\" o'zgarganda qayta render BO'LMASLIGINI Profiler "
                "orqali isbotlang."
            ),
            "task_description_ru": (
                "Вам дан один большой AppContext — в его value вместе хранятся "
                "«theme» (меняется редко) и «notifications» (часто, несколько раз "
                "в секунду), без useMemo. Есть маленький компонент (например "
                "ThemeIcon), читающий только «theme». Разделите это на два "
                "отдельных Context (ThemeContext и NotificationsContext), "
                "закешируйте value каждого через useMemo, и докажите через "
                "Profiler, что ThemeIcon больше НЕ перерендеривается при "
                "изменении «notifications»."
            ),
            "task_requirements": (
                "Ikkita alohida Context yaratilishi, har birining value'si "
                "useMemo bilan keshlangan bo'lishi shart. ThemeIcon'ning "
                "notifications o'zgarishida qayta render bo'lmasligi Profiler "
                "skrinshoti bilan tasdiqlanishi kerak."
            ),
            "task_requirements_ru": (
                "Обязательны два отдельных Context, value каждого закешировано "
                "через useMemo. Отсутствие перерендера ThemeIcon при изменении "
                "notifications должно быть подтверждено скриншотом Profiler."
            ),
            "task_technologies": "React, Context API, useMemo",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: Context'ni ajratish",
            "description": "Bitta katta Context'ni kam va tez o'zgaradigan qismlarga ajratish orqali keraksiz re-render'ni oldini olish.",
            "sample_type": "code",
            "code_files": [
                {"filename": "SplitContext.jsx", "language": "jsx", "code": (
                    "import { createContext, useContext, useMemo, useState } from 'react';\n\n"
                    "const WalletContext = createContext(null);\n"
                    "const InventoryContext = createContext(null);\n\n"
                    "export function StoreProvider({ children }) {\n"
                    "  const [balance, setBalance] = useState(0);\n"
                    "  const [inventory, setInventory] = useState([]);\n"
                    "  const wallet = useMemo(() => ({ balance, setBalance }), [balance]);\n"
                    "  const inv = useMemo(() => ({ inventory, setInventory }), [inventory]);\n"
                    "  return (\n"
                    "    <WalletContext.Provider value={wallet}>\n"
                    "      <InventoryContext.Provider value={inv}>{children}</InventoryContext.Provider>\n"
                    "    </WalletContext.Provider>\n"
                    "  );\n"
                    "}\n\n"
                    "export const useWallet = () => useContext(WalletContext);\n"
                    "export const useInventory = () => useContext(InventoryContext);\n"
                )},
            ],
        },
        "exercises": [
            {
                "title": "Context'ning asosiy tuzog'i",
                "title_ru": "Основная ловушка Context",
                "description": "Context value'sining bir maydoni o'zgarsa, faqat boshqa maydonni o'qiydigan komponentga nima bo'ladi?",
                "description_ru": "Что происходит с компонентом, читающим другое поле, если меняется одно поле в value Context?",
                "exercise_type": "multiple_choice",
                "options": [
                    "U ham qayta render bo'ladi, chunki butun value bitta birlik hisoblanadi",
                    "U hech qachon qayta render bo'lmaydi",
                    "Faqat sahifa yangilanganda (F5) qayta render bo'ladi",
                    "React avtomatik ravishda uni optimallashtiradi",
                ],
                "options_ru": [
                    "Он тоже перерендерится, потому что весь value считается единым целым",
                    "Он никогда не перерендерится",
                    "Перерендерится только при перезагрузке страницы (F5)",
                    "React автоматически оптимизирует это сам",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Darsning boshida qalin harflar bilan ta'kidlangan qoidani eslang.",
                "hint_ru": "Вспомните правило, выделенное жирным в начале урока.",
                "explanation": "useContext orqali obuna bo'lgan komponent, value obyektining istalgan qismi o'zgarganda qayta render bo'ladi, faqat o'qigan qismidan qat'i nazar.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "AuthContext'dagi haqiqiy holat",
                "title_ru": "Реальное состояние AuthContext",
                "description": (
                    "Bo'shliqni to'ldiring: AuthContext.js'da Provider value'si "
                    "___ bilan o'ralmagan, shuning uchun har render'da yangi obyekt "
                    "reference oladi."
                ),
                "description_ru": (
                    "Заполните пропуск: в AuthContext.js value Provider'а не обёрнут "
                    "в ___, поэтому на каждом рендере получает новую ссылку объекта."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "useMemo",
                "hint": "StoreContext.js esa aynan shu hook bilan value'ni keshlagan.",
                "hint_ru": "StoreContext.js как раз кеширует value именно этим хуком.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Context'ni ajratish qadamlari",
                "title_ru": "Шаги разделения Context",
                "description": "Bitta katta Context'ni ajratish yechimining qadamlarini tartibga joylashtiring.",
                "description_ru": "Расставьте по порядку шаги решения по разделению одного большого Context.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Qaysi maydonlar birga, qaysilari alohida o'zgarishini aniqlash",
                    "Har bir guruh uchun alohida Context yaratish",
                    "Har birining value'sini useMemo bilan keshlash",
                    "Komponentlarni faqat kerakli Context'ga obuna qildirish",
                ],
                "drag_items_ru": [
                    "Определить, какие поля меняются вместе, а какие отдельно",
                    "Создать отдельный Context для каждой группы",
                    "Закешировать value каждого через useMemo",
                    "Подписать компоненты только на нужный Context",
                ],
                "correct_order": [
                    "Qaysi maydonlar birga, qaysilari alohida o'zgarishini aniqlash",
                    "Har bir guruh uchun alohida Context yaratish",
                    "Har birining value'sini useMemo bilan keshlash",
                    "Komponentlarni faqat kerakli Context'ga obuna qildirish",
                ],
                "hint": "Avval tahlil, keyin bo'lish, keyin keshlash, oxirida ulash.",
                "hint_ru": "Сначала анализ, потом разделение, потом кеширование, в конце подписка.",
                "difficulty_level": "Hard",
                "points": 15,
            },
        ],
    },
    {
        "order": 7,
        "title": "7-Concurrent React: useTransition va useDeferredValue",
        "title_ru": "7-Конкурентный React: useTransition и useDeferredValue",
        "points_reward": 15,
        "text_content": (
            "<h3>Muammo: barcha yangilanishlar bir xil ustuvorlikda emas</h3>"
            "<p>Odatiy React'da <code>setState</code> chaqirilgan HAR bir yangilanish "
            "bir xil ustuvorlikda ishlanadi — foydalanuvchi klaviaturada harf "
            "bosishi ham, natijada qayta hisoblanishi kerak bo'lgan katta ro'yxat "
            "ham bir xil \"navbat\"da turadi. Agar filtrlash natijasida qayta "
            "chizilishi kerak bo'lgan ro'yxat katta bo'lsa, klaviatura kiritilishi "
            "\"sekin\" his qilinishi mumkin — chunki brauzer katta render bilan band "
            "bo'lib, keyingi harfni darhol ko'rsatolmaydi. React 18'dagi "
            "\"concurrent\" xususiyatlar aynan shu muammoni hal qilish uchun "
            "kiritilgan: ba'zi yangilanishlarni \"shoshilinch\" (urgent), boshqalarini "
            "\"shoshilmas\" (non-urgent, kechiktirilishi mumkin) deb belgilash.</p>"
            "<h3>Haqiqiy misol: StudentCourses.js'dagi qidiruv</h3>"
            "<p>Bu — ushbu platformaning haqiqiy kodi: <code>frontend/src/views/"
            "student/courses/Courses/StudentCourses.js</code>da "
            "<code>&lt;input value={{search}} onChange={{(e) =&gt; "
            "setSearch(e.target.value)}} /&gt;</code> yozilgan, va "
            "<code>displayed</code> — <code>courses.filter(...)</code> orqali har "
            "harfda qayta hisoblanadi. Hozircha kurslar ro'yxati kichik bo'lgani "
            "uchun bu sezilarli emas (5-darsda ko'rganimizdek). Lekin agar bu naqsh "
            "minglab elementli katta jadvalga (masalan, katta talabalar reytingini "
            "qidirish) qo'llanilsa, klaviatura kiritilishi bilan filtrlash "
            "natijasini ko'rsatish orasida haqiqiy kechikish paydo bo'lishi mumkin.</p>"
            "<h3>useTransition: yangilanishni \"shoshilmas\" deb belgilash</h3>"
            "<p><code>const [isPending, startTransition] = useTransition()</code> — "
            "<code>startTransition(() =&gt; setDisplayed(...))</code> ichiga o'ralgan "
            "har qanday state yangilanishi \"kechiktirilishi mumkin\" deb "
            "belgilanadi. React input maydonining o'zini (foydalanuvchi darhol "
            "ko'rishi kerak bo'lgan qism) DARHOL yangilaydi, natija ro'yxatini esa "
            "orqa fonda, shoshilmasdan hisoblaydi — agar foydalanuvchi yana harf "
            "kiritsa, eski hisoblash bekor qilinib, yangisi boshlanadi. "
            "<code>isPending</code> orqali \"hisoblanmoqda\" indikatorini ko'rsatish "
            "mumkin.</p>"
            "<h3>useDeferredValue: qiymatning \"kechiktirilgan\" nusxasi</h3>"
            "<p><code>const deferredSearch = useDeferredValue(search)</code> — "
            "<code>useTransition</code>ga o'xshash muammoni boshqacha yechadi: "
            "<code>search</code>ning o'zi darhol yangilanadi (input uchun), lekin "
            "<code>deferredSearch</code> — bir oz \"orqada qolgan\" nusxa, filtrlash "
            "kabi qimmat hisoblashlarda ISHLATISH uchun mo'ljallangan. React ikkalasi "
            "orasidagi farqni avtomatik tekshirib, <code>deferredSearch</code>ni "
            "orqa fonda yangilaydi. Bu — komponentni o'zgartirishni talab qilmaydigan "
            "holatlarda (masalan, uchinchi tomon kutubxona ichida) foydali.</p>"
            "<h3>Halol nuance: bu sehr emas, bu \"kim birinchi\" degan savol</h3>"
            "<p>Muhim tushunish kerak: <code>useTransition</code>/"
            "<code>useDeferredValue</code> hisoblashni TEZLASHTIRMAYDI — ular "
            "hisoblash QANDAY TARTIBDA bajarilishini o'zgartiradi. Agar filtrlash "
            "hisoblashning o'zi sekin bo'lsa (masalan, juda katta massiv, murakkab "
            "solishtiruv), bu vositalar uni tezroq qilmaydi — ular faqat "
            "foydalanuvchi INPUT'ining JAVOB BERISH TEZLIGINI (responsiveness) "
            "yaxshilaydi, orqa fon hisoblashi hali ham xuddi o'sha vaqtni oladi. "
            "Shuning uchun bu — 5-darsdagi virtualizatsiya yoki 2-3-darslardagi "
            "memoizatsiya o'rniga emas, ularga QO'SHIMCHA vosita.</p>"
            "<h3>Diagramma: shoshilinch va kechiktirilgan yangilanishlar</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  U[\"Foydalanuvchi harf yozadi\"] --> A[\"Input qiymati\n"
            "DARHOL yangilanadi (shoshilinch)\"]\n"
            "  U --> B[\"displayed ro'yxati\n"
            "startTransition ichida (shoshilmas)\"]\n"
            "  B --> C{\"Foydalanuvchi yana harf yozdimi?\"}\n"
            "  C -->|\"Ha\"| D[\"Eski hisoblash bekor qilinadi,\n"
            "yangisi boshlanadi\"]\n"
            "  C -->|\"Yo'q\"| E[\"Hisoblash tugab, ro'yxat yangilanadi\"]\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: input har doim darhol javob beradi, "
            "og'ir ro'yxat esa orqa fonda, kerak bo'lsa bekor qilinadigan tarzda "
            "yangilanadi.</p>"
            "<h3>useDeferredValue'ni React.memo bilan birga ishlatish</h3>"
            "<p><code>useDeferredValue</code>ning haqiqiy foydasi faqat ro'yxat "
            "elementlari <code>React.memo</code> bilan o'ralganda to'liq namoyon "
            "bo'ladi: <code>deferredSearch</code> hali \"eski\" qiymatda turgan "
            "vaqtda ham, o'zgarmagan elementlar qayta render bo'lmaydi (2-3-darslarda "
            "ko'rgan memoizatsiya bilan bir xil printsip). Ya'ni bu vosita "
            "memoizatsiya o'rniga emas, u bilan BIRGA to'liq kuchga ega bo'ladi — "
            "yakka o'zi ishlatilganda foyda kamroq seziladi.</p>"
            "<h3>Kichik tuzoq: startTransition ichida asinxronlikka yo'l qo'yilmaydi</h3>"
            "<p><code>startTransition</code>ga uzatilgan funksiya SINXRON tarzda "
            "<code>setState</code> chaqirishi kerak — uni <code>async</code> "
            "funksiyaga o'rash yoki <code>setTimeout</code> orqali kechiktirish "
            "ustuvorlik mexanizmini buzadi, React bu yangilanishni \"transition\" "
            "sifatida tanib olmay qoladi.</p>"
        ),
        "text_content_ru": (
            "<h3>Проблема: не все обновления имеют одинаковый приоритет</h3>"
            "<p>В обычном React КАЖДОЕ обновление, вызванное <code>setState</code>, "
            "обрабатывается с одинаковым приоритетом — нажатие буквы на клавиатуре "
            "и большой список, который нужно пересчитать в результате, стоят в одной "
            "«очереди». Если список, который нужно перерисовать после фильтрации, "
            "большой, ввод с клавиатуры может ощущаться «медленным» — потому что "
            "браузер занят большим рендером и не может сразу показать следующую "
            "букву. «Конкурентные» возможности React 18 введены именно для решения "
            "этой проблемы: пометить одни обновления как «срочные» (urgent), а "
            "другие как «несрочные» (non-urgent, которые можно отложить).</p>"
            "<h3>Реальный пример: поиск в StudentCourses.js</h3>"
            "<p>Это настоящий код этой платформы: в <code>frontend/src/views/"
            "student/courses/Courses/StudentCourses.js</code> написано "
            "<code>&lt;input value={{search}} onChange={{(e) =&gt; "
            "setSearch(e.target.value)}} /&gt;</code>, а <code>displayed</code> — "
            "пересчитывается через <code>courses.filter(...)</code> при каждой "
            "букве. Пока список курсов небольшой, это незаметно (как мы видели в "
            "уроке 5). Но если этот паттерн применить к большой таблице из тысяч "
            "элементов (например, поиск по большому рейтингу студентов), между "
            "вводом с клавиатуры и отображением результата фильтрации может "
            "появиться реальная задержка.</p>"
            "<h3>useTransition: пометить обновление как «несрочное»</h3>"
            "<p><code>const [isPending, startTransition] = useTransition()</code> — "
            "любое обновление state, обёрнутое в <code>startTransition(() =&gt; "
            "setDisplayed(...))</code>, помечается как «может быть отложено». React "
            "НЕМЕДЛЕННО обновляет само поле ввода (часть, которую пользователь "
            "должен увидеть сразу), а список результатов вычисляет в фоне, без "
            "спешки — если пользователь введёт ещё одну букву, старое вычисление "
            "отменяется и начинается новое. Через <code>isPending</code> можно "
            "показать индикатор «идёт вычисление».</p>"
            "<h3>useDeferredValue: «отложенная» копия значения</h3>"
            "<p><code>const deferredSearch = useDeferredValue(search)</code> — "
            "решает похожую проблему иначе: сам <code>search</code> обновляется "
            "немедленно (для поля ввода), а <code>deferredSearch</code> — немного "
            "«отстающая» копия, предназначенная для ИСПОЛЬЗОВАНИЯ в дорогих "
            "вычислениях вроде фильтрации. React автоматически отслеживает разницу "
            "между ними и обновляет <code>deferredSearch</code> в фоне. Это полезно "
            "там, где нельзя изменить сам компонент вычисления (например, внутри "
            "сторонней библиотеки).</p>"
            "<h3>Честный нюанс: это не магия, это вопрос «кто первый»</h3>"
            "<p>Важно понимать: <code>useTransition</code>/<code>useDeferredValue</code> "
            "НЕ УСКОРЯЮТ вычисление — они меняют ПОРЯДОК, в котором оно "
            "выполняется. Если само вычисление фильтрации медленное (например, "
            "очень большой массив, сложное сравнение), эти инструменты не сделают "
            "его быстрее — они лишь улучшают ОТЗЫВЧИВОСТЬ поля ввода, фоновое "
            "вычисление всё равно занимает то же время. Поэтому это — не замена "
            "виртуализации из урока 5 или мемоизации из уроков 2-3, а "
            "ДОПОЛНИТЕЛЬНЫЙ инструмент к ним.</p>"
            "<h3>Диаграмма: срочные и отложенные обновления</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  U[\"Пользователь вводит букву\"] --> A[\"Значение input\n"
            "обновляется НЕМЕДЛЕННО (срочно)\"]\n"
            "  U --> B[\"Список displayed\n"
            "внутри startTransition (несрочно)\"]\n"
            "  B --> C{\"Пользователь ввёл ещё букву?\"}\n"
            "  C -->|\"Да\"| D[\"Старое вычисление отменяется,\n"
            "начинается новое\"]\n"
            "  C -->|\"Нет\"| E[\"Вычисление завершается, список обновляется\"]\n"
            "</pre>"
            "<p>Диаграмма показывает: поле ввода всегда отвечает мгновенно, а "
            "тяжёлый список обновляется в фоне, с возможностью отмены при "
            "необходимости.</p>"
            "<h3>useDeferredValue вместе с React.memo</h3>"
            "<p>Настоящая польза <code>useDeferredValue</code> раскрывается только "
            "когда элементы списка обёрнуты в <code>React.memo</code>: пока "
            "<code>deferredSearch</code> ещё держит «старое» значение, "
            "неизменившиеся элементы не перерендериваются (тот же принцип "
            "мемоизации из уроков 2-3). То есть этот инструмент не заменяет "
            "мемоизацию, а раскрывает полную силу ВМЕСТЕ с ней — при использовании "
            "в одиночку польза заметно меньше.</p>"
            "<h3>Небольшая ловушка: startTransition не терпит асинхронности внутри</h3>"
            "<p>Функция, переданная в <code>startTransition</code>, должна СИНХРОННО "
            "вызывать setState — обёртывание в <code>async</code> функцию или отложенный "
            "через <code>setTimeout</code> вызов сломает механизм приоритизации, "
            "React просто не сможет распознать это обновление как переход.</p>"
        ),
        "code_content": (
            "// StudentCourses.js'ning haqiqiy naqshi (soddalashtirilgan): filtrlash\n"
            "// har harf kiritilganda darhol, sinxron tarzda bajariladi.\n"
            "function StudentCoursesSync({ courses }) {\n"
            "  const [search, setSearch] = React.useState('');\n"
            "  const displayed = courses.filter((c) =>\n"
            "    c.title?.toLowerCase().includes(search.toLowerCase())\n"
            "  );\n"
            "  return (\n"
            "    <div>\n"
            "      <input value={search} onChange={(e) => setSearch(e.target.value)} />\n"
            "      {displayed.map((c) => <CourseCard key={c.id} course={c} />)}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// useTransition bilan: input darhol, ro'yxat esa 'shoshilmas' tarzda\n"
            "// yangilanadi. Katta ro'yxatlar uchun foydali — kichik ro'yxatda\n"
            "// (masalan, StudentCourses'ning hozirgi holati) sezilarli farq yo'q.\n"
            "function StudentCoursesTransition({ courses }) {\n"
            "  const [search, setSearch] = React.useState('');\n"
            "  const [displayed, setDisplayed] = React.useState(courses);\n"
            "  const [isPending, startTransition] = React.useTransition();\n\n"
            "  const handleChange = (e) => {\n"
            "    const value = e.target.value;\n"
            "    setSearch(value); // shoshilinch — input darhol yangilanadi\n"
            "    startTransition(() => {\n"
            "      // shoshilmas — katta ro'yxat orqa fonda hisoblanadi\n"
            "      setDisplayed(\n"
            "        courses.filter((c) => c.title?.toLowerCase().includes(value.toLowerCase()))\n"
            "      );\n"
            "    });\n"
            "  };\n\n"
            "  return (\n"
            "    <div>\n"
            "      <input value={search} onChange={handleChange} />\n"
            "      {isPending && <span className=\"muted\">Yangilanmoqda...</span>}\n"
            "      {displayed.map((c) => <CourseCard key={c.id} course={c} />)}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// useDeferredValue bilan: bitta manba (search), ikkita nusxa —\n"
            "// input uchun darhol, filtrlash uchun kechiktirilgan.\n"
            "function StudentCoursesDeferred({ courses }) {\n"
            "  const [search, setSearch] = React.useState('');\n"
            "  const deferredSearch = React.useDeferredValue(search);\n"
            "  const isStale = search !== deferredSearch;\n\n"
            "  const displayed = courses.filter((c) =>\n"
            "    c.title?.toLowerCase().includes(deferredSearch.toLowerCase())\n"
            "  );\n\n"
            "  return (\n"
            "    <div style={{ opacity: isStale ? 0.6 : 1 }}>\n"
            "      <input value={search} onChange={(e) => setSearch(e.target.value)} />\n"
            "      {displayed.map((c) => <CourseCard key={c.id} course={c} />)}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// TO'LIQ FOYDA: useDeferredValue + React.memo birga. Har harfda\n"
            "// deferredSearch bir oz kechikadi, lekin shu payt ichida ham\n"
            "// o'zgarmagan CourseCard'lar (memo tufayli) qayta render bo'lmaydi.\n"
            "const CourseCard = React.memo(function CourseCard({ course }) {\n"
            "  return <div className=\"card\">{course.title}</div>;\n"
            "});\n\n"
            "function StudentCoursesDeferredMemo({ courses }) {\n"
            "  const [search, setSearch] = React.useState('');\n"
            "  const deferredSearch = React.useDeferredValue(search);\n"
            "  const displayed = React.useMemo(\n"
            "    () => courses.filter((c) =>\n"
            "      c.title?.toLowerCase().includes(deferredSearch.toLowerCase())\n"
            "    ),\n"
            "    [courses, deferredSearch]\n"
            "  );\n"
            "  return (\n"
            "    <div>\n"
            "      <input value={search} onChange={(e) => setSearch(e.target.value)} />\n"
            "      {displayed.map((c) => <CourseCard key={c.id} course={c} />)}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// TUZOQ: startTransition ichidagi funksiya sinxron bo'lishi shart —\n"
            "// async o'rash yoki setTimeout transition ustuvorligini buzadi.\n"
            "function badTransitionExample(startTransition, value) {\n"
            "  startTransition(async () => {\n"
            "    // NOTO'G'RI: React buni transition sifatida tanimaydi\n"
            "    await Promise.resolve();\n"
            "  });\n"
            "}\n"
        ),
        "code_content_ru": (
            "// Реальный (упрощённый) паттерн StudentCourses.js: фильтрация\n"
            "// выполняется немедленно, синхронно, при каждой введённой букве.\n"
            "function StudentCoursesSync({ courses }) {\n"
            "  const [search, setSearch] = React.useState('');\n"
            "  const displayed = courses.filter((c) =>\n"
            "    c.title?.toLowerCase().includes(search.toLowerCase())\n"
            "  );\n"
            "  return (\n"
            "    <div>\n"
            "      <input value={search} onChange={(e) => setSearch(e.target.value)} />\n"
            "      {displayed.map((c) => <CourseCard key={c.id} course={c} />)}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// С useTransition: input обновляется немедленно, список — «несрочно».\n"
            "// Полезно для больших списков — на небольшом списке (как сейчас в\n"
            "// StudentCourses) заметной разницы нет.\n"
            "function StudentCoursesTransition({ courses }) {\n"
            "  const [search, setSearch] = React.useState('');\n"
            "  const [displayed, setDisplayed] = React.useState(courses);\n"
            "  const [isPending, startTransition] = React.useTransition();\n\n"
            "  const handleChange = (e) => {\n"
            "    const value = e.target.value;\n"
            "    setSearch(value); // срочно — input обновляется немедленно\n"
            "    startTransition(() => {\n"
            "      // несрочно — большой список вычисляется в фоне\n"
            "      setDisplayed(\n"
            "        courses.filter((c) => c.title?.toLowerCase().includes(value.toLowerCase()))\n"
            "      );\n"
            "    });\n"
            "  };\n\n"
            "  return (\n"
            "    <div>\n"
            "      <input value={search} onChange={handleChange} />\n"
            "      {isPending && <span className=\"muted\">Обновляется...</span>}\n"
            "      {displayed.map((c) => <CourseCard key={c.id} course={c} />)}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// С useDeferredValue: один источник (search), две копии — для\n"
            "// input немедленная, для фильтрации отложенная.\n"
            "function StudentCoursesDeferred({ courses }) {\n"
            "  const [search, setSearch] = React.useState('');\n"
            "  const deferredSearch = React.useDeferredValue(search);\n"
            "  const isStale = search !== deferredSearch;\n\n"
            "  const displayed = courses.filter((c) =>\n"
            "    c.title?.toLowerCase().includes(deferredSearch.toLowerCase())\n"
            "  );\n\n"
            "  return (\n"
            "    <div style={{ opacity: isStale ? 0.6 : 1 }}>\n"
            "      <input value={search} onChange={(e) => setSearch(e.target.value)} />\n"
            "      {displayed.map((c) => <CourseCard key={c.id} course={c} />)}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// ПОЛНАЯ ПОЛЬЗА: useDeferredValue + React.memo вместе. При каждой\n"
            "// букве deferredSearch немного запаздывает, но пока это происходит,\n"
            "// неизменившиеся CourseCard (благодаря memo) не перерендериваются.\n"
            "const CourseCard = React.memo(function CourseCard({ course }) {\n"
            "  return <div className=\"card\">{course.title}</div>;\n"
            "});\n\n"
            "function StudentCoursesDeferredMemo({ courses }) {\n"
            "  const [search, setSearch] = React.useState('');\n"
            "  const deferredSearch = React.useDeferredValue(search);\n"
            "  const displayed = React.useMemo(\n"
            "    () => courses.filter((c) =>\n"
            "      c.title?.toLowerCase().includes(deferredSearch.toLowerCase())\n"
            "    ),\n"
            "    [courses, deferredSearch]\n"
            "  );\n"
            "  return (\n"
            "    <div>\n"
            "      <input value={search} onChange={(e) => setSearch(e.target.value)} />\n"
            "      {displayed.map((c) => <CourseCard key={c.id} course={c} />)}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// ЛОВУШКА: функция внутри startTransition должна быть синхронной —\n"
            "// async-обёртка или setTimeout сломают приоритизацию перехода.\n"
            "function badTransitionExample(startTransition, value) {\n"
            "  startTransition(async () => {\n"
            "    // НЕПРАВИЛЬНО: React не распознает это как переход\n"
            "    await Promise.resolve();\n"
            "  });\n"
            "}\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Sekin qidiruv input'ini useTransition bilan tuzating",
            "task_title_ru": "Исправьте медленное поле поиска через useTransition",
            "task_description": (
                "Sizga 3000+ elementli ro'yxatni har harf kiritilganda sinxron "
                "filtrlaydigan qidiruv input'i beriladi — hozircha yozish paytida "
                "sezilarli \"tirjirash\" bor. Buni useTransition yordamida "
                "tuzating: input qiymati darhol, ro'yxat esa startTransition ichida "
                "yangilansin, va isPending orqali \"yangilanmoqda\" indikatorini "
                "ko'rsating. Muqobil sifatida, xuddi shu muammoni useDeferredValue "
                "bilan ham yeching va ikkala yondashuvni qisqacha solishtiring."
            ),
            "task_description_ru": (
                "Вам дано поле поиска, синхронно фильтрующее список из 3000+ "
                "элементов при каждой введённой букве — сейчас при вводе заметно "
                "«подтормаживание». Исправьте это через useTransition: значение "
                "input обновляется немедленно, а список — внутри startTransition, "
                "с индикатором «обновляется» через isPending. В качестве "
                "альтернативы решите ту же проблему через useDeferredValue и "
                "кратко сравните оба подхода."
            ),
            "task_requirements": (
                "useTransition to'g'ri qo'llanilgan bo'lishi, isPending indikatori "
                "ko'rsatilishi shart. useDeferredValue bilan muqobil yechim va "
                "ikkalasining qisqacha solishtiruvi yozma taqdim etilishi kerak."
            ),
            "task_requirements_ru": (
                "useTransition обязан быть правильно применён, индикатор isPending "
                "должен отображаться. Альтернативное решение через useDeferredValue "
                "и краткое сравнение обоих подходов должны быть представлены "
                "письменно."
            ),
            "task_technologies": "React, useTransition, useDeferredValue",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: useTransition va useDeferredValue taqqoslamasi",
            "description": "Ikkala concurrent hook orqali qidiruv input'ining javob berish tezligini yaxshilash namunasi.",
            "sample_type": "code",
            "code_files": [
                {"filename": "ConcurrentSearch.jsx", "language": "jsx", "code": (
                    "import { useState, useTransition } from 'react';\n\n"
                    "export default function ConcurrentSearch({ items }) {\n"
                    "  const [search, setSearch] = useState('');\n"
                    "  const [results, setResults] = useState(items);\n"
                    "  const [isPending, startTransition] = useTransition();\n\n"
                    "  const onChange = (e) => {\n"
                    "    const value = e.target.value;\n"
                    "    setSearch(value);\n"
                    "    startTransition(() => {\n"
                    "      setResults(items.filter((i) => i.title.includes(value)));\n"
                    "    });\n"
                    "  };\n\n"
                    "  return (\n"
                    "    <div>\n"
                    "      <input value={search} onChange={onChange} />\n"
                    "      {isPending && <span>...</span>}\n"
                    "      {results.map((r) => <div key={r.id}>{r.title}</div>)}\n"
                    "    </div>\n"
                    "  );\n"
                    "}\n"
                )},
            ],
        },
        "exercises": [
            {
                "title": "useTransition nima qiladi",
                "title_ru": "Что делает useTransition",
                "description": "startTransition ichiga o'ralgan yangilanish nima uchun \"shoshilmas\" deb belgilanadi?",
                "description_ru": "Зачем обновление, обёрнутое в startTransition, помечается как «несрочное»?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Foydalanuvchining shoshilinch harakatlari (masalan, yozish) birinchi ishlanishi uchun",
                    "Xotira sarfini kamaytirish uchun",
                    "Serverga so'rovlar sonini kamaytirish uchun",
                    "TypeScript xatolarini oldini olish uchun",
                ],
                "options_ru": [
                    "Чтобы срочные действия пользователя (например, ввод текста) обрабатывались первыми",
                    "Чтобы уменьшить расход памяти",
                    "Чтобы уменьшить число запросов к серверу",
                    "Чтобы предотвратить ошибки TypeScript",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Darsning boshidagi \"shoshilinch va shoshilmas\" farqini eslang.",
                "hint_ru": "Вспомните разницу «срочное и несрочное» из начала урока.",
                "explanation": "startTransition orqa fon yangilanishlarini kechiktiradi, shu bilan shoshilinch (masalan, klaviatura) yangilanishlari darhol ishlanadi.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "useDeferredValue nima qaytaradi",
                "title_ru": "Что возвращает useDeferredValue",
                "description": "Bo'shliqni to'ldiring: useDeferredValue(search) qiymatning bir oz ___ qolgan nusxasini qaytaradi.",
                "description_ru": "Заполните пропуск: useDeferredValue(search) возвращает копию значения, немного ___.",
                "exercise_type": "fill_in_blank",
                "correct_answers": "orqada",
                "correct_answers_ru": "отстающую",
                "hint": "Darsda \"kechiktirilgan nusxa\" deb ta'riflangan.",
                "hint_ru": "В уроке это описано как «отстающая копия».",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Concurrent vositalar nimani tezlashtirmaydi",
                "title_ru": "Что НЕ ускоряют конкурентные инструменты",
                "description": "useTransition/useDeferredValue haqidagi to'g'ri va noto'g'ri fikrlarni ajratib, to'g'ri tartibga joylashtiring: avval ular NIMA qiladi, keyin ular NIMA QILMAYDI.",
                "description_ru": "Расставьте по порядку: сначала что useTransition/useDeferredValue ДЕЛАЮТ, затем что они НЕ ДЕЛАЮТ.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Input javob berish tezligini yaxshilaydi",
                    "Yangilanishlar orasidagi ustuvorlikni belgilaydi",
                    "Hisoblashning o'zini tezlashtirmaydi",
                    "Memoizatsiya yoki virtualizatsiya o'rnini bosmaydi",
                ],
                "drag_items_ru": [
                    "Улучшают отзывчивость поля ввода",
                    "Задают приоритет между обновлениями",
                    "Не ускоряют само вычисление",
                    "Не заменяют мемоизацию или виртуализацию",
                ],
                "correct_order": [
                    "Input javob berish tezligini yaxshilaydi",
                    "Yangilanishlar orasidagi ustuvorlikni belgilaydi",
                    "Hisoblashning o'zini tezlashtirmaydi",
                    "Memoizatsiya yoki virtualizatsiya o'rnini bosmaydi",
                ],
                "hint": "Avval ular NIMA qilishi, keyin ular NIMA QILMASLIGI keladi.",
                "hint_ru": "Сначала то, что они ДЕЛАЮТ, потом то, что они НЕ ДЕЛАЮТ.",
                "difficulty_level": "Hard",
                "points": 15,
            },
        ],
    },
    {
        "order": 8,
        "title": "8-Bundle hajmini tahlil qilish va qisqartirish",
        "title_ru": "8-Анализ и сокращение размера бандла",
        "points_reward": 15,
        "text_content": (
            "<h3>Nega bundle hajmi performance masalasi</h3>"
            "<p>4-darsda ko'rganimizdek, katta bundle — bu foydalanuvchi birinchi "
            "marta sahifani ochganda yuklab olishi kerak bo'lgan JavaScript hajmi. "
            "Bu hajm qancha katta bo'lsa, tarmoq orqali yuklanish shuncha uzoq "
            "davom etadi, va yuklangandan keyin ham brauzer uni PARSE va EXECUTE "
            "qilishi (kodni tahlil qilib, ishga tushirishi) kerak — bu ham vaqt "
            "oladi, ayniqsa sekinroq telefonlarda. Code splitting (4-dars) bundle'ni "
            "BO'LAKLARGA ajratadi, lekin har bir bo'lakning O'ZI qanchalik katta "
            "ekanini kamaytirmaydi — bu darsda aynan shu masalaga qaraymiz.</p>"
            "<h3>Bundle ichida nima bor — tahlil qilish</h3>"
            "<p>CRA loyihasida <code>source-map-explorer</code> (yoki Vite loyihalarida "
            "<code>rollup-plugin-visualizer</code>) kabi vosita build natijasidagi "
            "bundle faylini tahlil qilib, uning ICHIDA qaysi modul qancha joy "
            "egallaganini vizual \"treemap\" (har bir to'rtburchak — bir modul, "
            "maydoni hajmiga mutanosib) shaklida ko'rsatadi. Ko'pincha bu tahlil "
            "kutilmagan natija beradi: bitta kichik funksiya uchun ishlatilgan "
            "og'ir kutubxonaning TO'LIQ nusxasi bundle'ga kirib qolgani, yoki bir "
            "xil kutubxonaning ikkita turli versiyasi ikkalasi ham qo'shilib "
            "ketgani aniqlanishi mumkin.</p>"
            "<h3>Tree-shaking: ishlatilmagan kodni olib tashlash</h3>"
            "<p>\"Tree-shaking\" — build tizimining ES module <code>import</code>/"
            "<code>export</code> tuzilishini tahlil qilib, HAQIQATDA ishlatilmagan "
            "eksportlarni yakuniy bundle'dan olib tashlash jarayoni. Bu avtomatik "
            "ishlaydi, lekin faqat ES module sintaksisi (<code>import { X } from "
            "'lib'</code>) bilan to'g'ri ishlaydi — ba'zi eski kutubxonalar "
            "CommonJS (<code>require</code>) formatida bo'lib, ularni "
            "tree-shake qilish qiyinroq yoki imkonsiz bo'ladi. Shuning uchun "
            "kutubxona tanlashda \"ES modules qo'llab-quvvatlaydimi\" degan savol "
            "amaliy ahamiyatga ega.</p>"
            "<h3>Dinamik import — nafaqat sahifalar uchun</h3>"
            "<p>4-darsda <code>React.lazy</code> orqali komponentlarni bo'lganini "
            "ko'rgan edik. Xuddi shu <code>import()</code> naqshi oddiy "
            "kutubxonalarga ham qo'llanadi: agar bitta og'ir kutubxona (masalan, "
            "grafik chizish yoki PDF yaratish uchun) faqat bitta kamdan-kam ishlatiladigan "
            "funksiyada kerak bo'lsa, uni faylning boshida statik "
            "<code>import</code> qilish o'rniga, aynan o'sha funksiya ichida "
            "<code>const lib = await import('heavy-lib')</code> deb dinamik "
            "chaqirish mumkin — shunda u faqat shu funksiya chaqirilganda "
            "yuklanadi.</p>"
            "<h3>Kutubxona tanlashda hajm haqida o'ylash</h3>"
            "<p>Ba'zan bitta katta kutubxonaning bitta funksiyasi kerak bo'ladi — "
            "masalan, sana formatlash uchun butun <code>moment.js</code> "
            "o'rniga faqat kerakli funksiyalarni o'z ichiga olgan yengilroq "
            "muqobil (masalan, <code>date-fns</code>, faqat ishlatilgan "
            "funksiyalarni import qilish imkonini beradi) tanlash bundle hajmini "
            "sezilarli kamaytirishi mumkin. Bu — \"qaysi kutubxona nomi mashhur\" "
            "emas, \"loyihamga qancha KB qo'shadi\" degan savolga asoslangan "
            "qaror.</p>"
            "<h3>Diagramma: bundle tahlili va qisqartirish oqimi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Build qilish (npm run build)\"] --> B[\"source-map-explorer bilan\n"
            "bundle'ni tahlil qilish\"]\n"
            "  B --> C{\"Kutilmagan katta modul\n"
            "topildimi?\"}\n"
            "  C -->|\"Ha, butun kutubxona\n"
            "bitta funksiya uchun\"| D[\"Yengilroq muqobil yoki\n"
            "dinamik import qo'llash\"]\n"
            "  C -->|\"Ha, kamdan-kam\n"
            "ishlatiladigan qism\"| E[\"React.lazy bilan\n"
            "alohida chunk qilish\"]\n"
            "  C -->|\"Yo'q\"| F[\"Hozircha o'zgartirish shart emas\"]\n"
            "  D --> G[\"Qayta build qilib, hajmni solishtirish\"]\n"
            "  E --> G\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: bundle tahlili — bu qaror qabul "
            "qilishdan oldingi o'lchash bosqichi, xuddi Profiler render vaqtini "
            "o'lchagani kabi.</p>"
            "<h3>Ikkilangan versiyalar — kam ko'zga tashlanadigan muammo</h3>"
            "<p>Ba'zan bundle katta bo'lishining sababi umuman ortiqcha kutubxona "
            "emas, balki BIR XIL kutubxonaning IKKI XIL versiyasi tasodifan ikkalasi "
            "ham bundle'ga kirib qolgani — masalan, sizning loyihangiz "
            "<code>lodash@4</code>ni to'g'ridan-to'g'ri ishlatsa, lekin boshqa bir "
            "bog'liqlik o'zining ichida <code>lodash@3</code>ga muhtoj bo'lsa, "
            "paket menejeri ikkalasini ham saqlab qolishi mumkin. "
            "<code>npm ls lodash</code> (yoki <code>yarn why lodash</code>) buyrug'i "
            "aynan shu holatni — loyihada nechta versiya borligini va ular qayerdan "
            "kelayotganini — ko'rsatadi. Bunday holatlarda paket menejerining "
            "\"dedupe\" buyrug'i yoki <code>package.json</code>dagi "
            "<code>resolutions</code>/<code>overrides</code> maydoni orqali bitta "
            "versiyaga majburlash mumkin.</p>"
            "<h3>Siqish (compression) — bundle o'lchash bilan aralashtirmaslik</h3>"
            "<p>Muhim farq: server odatda JS faylni Brotli yoki Gzip bilan siqib "
            "yuboradi, va brauzer DevTools Network tab'ida ko'rsatilgan \"Size\" "
            "ustuni ko'pincha siqilgan hajmni ko'rsatadi — bu esa "
            "<code>source-map-explorer</code>ning SIQILMAGAN hajm ko'rsatishidan "
            "farq qiladi. Ikkalasi ham foydali, lekin ular bir xil narsani "
            "o'lchamaydi — siqilgan hajm haqiqiy tarmoq trafigini, siqilmagan hajm "
            "esa brauzer PARSE/EXECUTE qilishi kerak bo'lgan haqiqiy kod hajmini "
            "ko'rsatadi.</p>"
        ),
        "text_content_ru": (
            "<h3>Почему размер бандла — это вопрос производительности</h3>"
            "<p>Как мы видели в уроке 4, большой бандл — это объём JavaScript, "
            "который пользователь должен загрузить при первом открытии страницы. "
            "Чем больше этот объём, тем дольше загрузка по сети, а после загрузки "
            "браузеру ещё нужно PARSE и EXECUTE (разобрать и выполнить) этот код — "
            "это тоже занимает время, особенно на более медленных телефонах. Code "
            "splitting (урок 4) разбивает бандл на ЧАСТИ, но не уменьшает, "
            "насколько велика каждая ЧАСТЬ сама по себе — этому и посвящён этот "
            "урок.</p>"
            "<h3>Что внутри бандла — анализ</h3>"
            "<p>В проекте CRA инструмент вроде <code>source-map-explorer</code> (или "
            "<code>rollup-plugin-visualizer</code> в проектах на Vite) анализирует "
            "итоговый файл бандла и показывает, сколько места занимает каждый "
            "модуль ВНУТРИ него, в виде визуального «treemap» (каждый прямоугольник "
            "— модуль, площадь пропорциональна размеру). Часто такой анализ даёт "
            "неожиданный результат: обнаруживается, что ради одной маленькой "
            "функции в бандл попала ПОЛНАЯ копия тяжёлой библиотеки, или что две "
            "разные версии одной и той же библиотеки попали внутрь одновременно.</p>"
            "<h3>Tree-shaking: удаление неиспользуемого кода</h3>"
            "<p>«Tree-shaking» — процесс, при котором система сборки анализирует "
            "структуру ES module <code>import</code>/<code>export</code> и удаляет "
            "из итогового бандла экспорты, которые РЕАЛЬНО не используются. Это "
            "работает автоматически, но корректно только с синтаксисом ES modules "
            "(<code>import { X } from 'lib'</code>) — некоторые старые библиотеки в "
            "формате CommonJS (<code>require</code>) сложнее или вовсе невозможно "
            "tree-shake. Поэтому при выборе библиотеки вопрос «поддерживает ли она "
            "ES modules» имеет практическое значение.</p>"
            "<h3>Динамический импорт — не только для страниц</h3>"
            "<p>В уроке 4 мы видели, как <code>React.lazy</code> разбивает "
            "компоненты. Тот же паттерн <code>import()</code> применим и к обычным "
            "библиотекам: если одна тяжёлая библиотека (например, для построения "
            "графиков или генерации PDF) нужна только в одной редко используемой "
            "функции, вместо статического <code>import</code> в начале файла можно "
            "вызвать её динамически прямо внутри этой функции: "
            "<code>const lib = await import('heavy-lib')</code> — тогда она "
            "загрузится только при вызове этой функции.</p>"
            "<h3>Учитывать размер при выборе библиотеки</h3>"
            "<p>Иногда нужна всего одна функция из большой библиотеки — например, "
            "вместо целого <code>moment.js</code> для форматирования дат более "
            "лёгкая альтернатива (например, <code>date-fns</code>, позволяющая "
            "импортировать только используемые функции) может заметно уменьшить "
            "размер бандла. Это решение основано не на «какая библиотека "
            "популярнее», а на вопросе «сколько КБ она добавляет моему проекту».</p>"
            "<h3>Диаграмма: анализ и сокращение бандла</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Сборка (npm run build)\"] --> B[\"Анализ бандла через\n"
            "source-map-explorer\"]\n"
            "  B --> C{\"Найден неожиданно\n"
            "большой модуль?\"}\n"
            "  C -->|\"Да, целая библиотека\n"
            "ради одной функции\"| D[\"Более лёгкая альтернатива\n"
            "или динамический импорт\"]\n"
            "  C -->|\"Да, редко используемая\n"
            "часть\"| E[\"Вынести в отдельный чанк\n"
            "через React.lazy\"]\n"
            "  C -->|\"Нет\"| F[\"Изменения пока не нужны\"]\n"
            "  D --> G[\"Пересобрать и сравнить размер\"]\n"
            "  E --> G\n"
            "</pre>"
            "<p>Диаграмма показывает: анализ бандла — этап измерения перед "
            "принятием решения, точно так же, как Profiler измеряет время "
            "рендера.</p>"
            "<h3>Дублирующиеся версии — менее заметная проблема</h3>"
            "<p>Иногда причина большого бандла — вовсе не лишняя библиотека, а то, "
            "что ДВЕ РАЗНЫЕ версии ОДНОЙ И ТОЙ ЖЕ библиотеки случайно попали в бандл "
            "одновременно — например, ваш проект напрямую использует "
            "<code>lodash@4</code>, но другая зависимость внутри себя требует "
            "<code>lodash@3</code>, и менеджер пакетов может сохранить обе. Команда "
            "<code>npm ls lodash</code> (или <code>yarn why lodash</code>) как раз "
            "показывает эту ситуацию — сколько версий в проекте и откуда они "
            "пришли. В таких случаях можно принудительно свести к одной версии "
            "через команду «dedupe» менеджера пакетов или поле "
            "<code>resolutions</code>/<code>overrides</code> в "
            "<code>package.json</code>.</p>"
            "<h3>Сжатие (compression) — не путать с размером бандла</h3>"
            "<p>Важное отличие: сервер обычно отдаёт JS-файл сжатым через Brotli "
            "или Gzip, и колонка «Size» на вкладке Network в DevTools браузера "
            "часто показывает именно сжатый размер — а это отличается от "
            "НЕСЖАТОГО размера, который показывает <code>source-map-explorer</code>. "
            "Оба показателя полезны, но измеряют разное: сжатый размер — это "
            "реальный сетевой трафик, а несжатый — это реальный объём кода, "
            "который браузеру нужно PARSE/EXECUTE.</p>"
        ),
        "code_content": (
            "// package.json'ga source-map-explorer'ni qo'shish va script yozish:\n"
            "//\n"
            "// {\n"
            "//   \"scripts\": {\n"
            "//     \"build\": \"react-scripts build\",\n"
            "//     \"analyze\": \"source-map-explorer 'build/static/js/*.js'\"\n"
            "//   },\n"
            "//   \"devDependencies\": { \"source-map-explorer\": \"^2.5.3\" }\n"
            "// }\n"
            "//\n"
            "// Ishlatish: npm run build && npm run analyze\n\n"
            "// Og'ir kutubxonani dinamik import qilish misoli — HeavyReportModal\n"
            "// ichida PDF generatsiya funksiyasi faqat kerak bo'lganda yuklanadi.\n"
            "function ReportGenerator() {\n"
            "  const [generating, setGenerating] = React.useState(false);\n\n"
            "  const handleGenerate = async () => {\n"
            "    setGenerating(true);\n"
            "    // 'heavy-pdf-lib' faqat shu tugma bosilganda tarmoqdan yuklanadi —\n"
            "    // boshlang'ich bundle'ga umuman kirmaydi.\n"
            "    const { generatePdf } = await import('heavy-pdf-lib');\n"
            "    const blob = await generatePdf({ title: 'Hisobot' });\n"
            "    setGenerating(false);\n"
            "    return blob;\n"
            "  };\n\n"
            "  return (\n"
            "    <button onClick={handleGenerate} disabled={generating}>\n"
            "      {generating ? 'Yaratilmoqda...' : 'PDF hisobot yaratish'}\n"
            "    </button>\n"
            "  );\n"
            "}\n\n"
            "// Tree-shaking'ga mos import naqshi: faqat kerakli funksiyani olish,\n"
            "// butun kutubxonani emas.\n"
            "// NOTO'G'RI (butun kutubxona bundle'ga kirishi mumkin):\n"
            "// import _ from 'lodash';\n"
            "// const result = _.debounce(fn, 300);\n"
            "//\n"
            "// TO'G'RI (faqat kerakli modul import qilinadi, tree-shaking oson):\n"
            "import debounce from 'lodash/debounce';\n"
            "const result = debounce(() => console.log('qidiruv'), 300);\n\n"
            "// Bundle hajmini tekshirish uchun CI'da oddiy skript: build hajmi\n"
            "// belgilangan chegaradan oshsa, ogohlantirish beradi.\n"
            "// (package.json ichida \"bundlesize\" kabi vosita bilan ham qilinadi)\n"
            "function checkBundleBudget(actualKb, budgetKb = 300) {\n"
            "  if (actualKb > budgetKb) {\n"
            "    console.warn(\n"
            "      `Bundle hajmi ${actualKb}KB, belgilangan ${budgetKb}KB chegaradan katta!`\n"
            "    );\n"
            "    return false;\n"
            "  }\n"
            "  return true;\n"
            "}\n\n"
            "// Ikkilangan versiyalarni tekshirish (terminal buyrug'i, kod emas,\n"
            "// lekin loyihada ishga tushirib ko'rish mumkin):\n"
            "//\n"
            "//   npm ls lodash\n"
            "//   # chiqishi: lodash@4.17.21, va agar boshqa bog'liqlik ichida\n"
            "//   # lodash@3.10.1 ham bo'lsa, ikkalasi ham daraxtda ko'rinadi\n"
            "//\n"
            "// Bitta versiyaga majburlash (package.json ichida, yarn uchun):\n"
            "//\n"
            "//   {\n"
            "//     \"resolutions\": { \"lodash\": \"4.17.21\" }\n"
            "//   }\n\n"
            "// Siqilgan va siqilmagan hajmni solishtirish uchun kichik yordamchi —\n"
            "// ikkalasi ham foydali, lekin boshqa-boshqa narsani ko'rsatadi.\n"
            "function summarizeBundleSize({ rawKb, gzipKb, brotliKb }) {\n"
            "  return {\n"
            "    parseExecuteCost: `${rawKb}KB (brauzer PARSE/EXECUTE qiladigan hajm)`,\n"
            "    networkCost: `${brotliKb ?? gzipKb}KB (haqiqiy tarmoq trafigi)`,\n"
            "  };\n"
            "}\n\n"
            "// CRA'ni \"eject\" qilmasdan webpack sozlamalarini o'zgartirish uchun\n"
            "// craco (Create React App Configuration Override) ishlatiladi —\n"
            "// webpack-bundle-analyzer plaginini shu orqali ulash mumkin.\n"
            "// craco.config.js:\n"
            "//\n"
            "//   const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');\n"
            "//   module.exports = {\n"
            "//     webpack: {\n"
            "//       plugins: {\n"
            "//         add: [new BundleAnalyzerPlugin({ analyzerMode: 'static' })],\n"
            "//       },\n"
            "//     },\n"
            "//   };\n"
        ),
        "code_content_ru": (
            "// Добавление source-map-explorer в package.json и скрипт:\n"
            "//\n"
            "// {\n"
            "//   \"scripts\": {\n"
            "//     \"build\": \"react-scripts build\",\n"
            "//     \"analyze\": \"source-map-explorer 'build/static/js/*.js'\"\n"
            "//   },\n"
            "//   \"devDependencies\": { \"source-map-explorer\": \"^2.5.3\" }\n"
            "// }\n"
            "//\n"
            "// Использование: npm run build && npm run analyze\n\n"
            "// Пример динамического импорта тяжёлой библиотеки — функция\n"
            "// генерации PDF внутри HeavyReportModal загружается только по\n"
            "// требованию.\n"
            "function ReportGenerator() {\n"
            "  const [generating, setGenerating] = React.useState(false);\n\n"
            "  const handleGenerate = async () => {\n"
            "    setGenerating(true);\n"
            "    // 'heavy-pdf-lib' загрузится по сети только при нажатии этой\n"
            "    // кнопки — вообще не попадёт в начальный бандл.\n"
            "    const { generatePdf } = await import('heavy-pdf-lib');\n"
            "    const blob = await generatePdf({ title: 'Отчёт' });\n"
            "    setGenerating(false);\n"
            "    return blob;\n"
            "  };\n\n"
            "  return (\n"
            "    <button onClick={handleGenerate} disabled={generating}>\n"
            "      {generating ? 'Создаётся...' : 'Создать PDF-отчёт'}\n"
            "    </button>\n"
            "  );\n"
            "}\n\n"
            "// Паттерн импорта, дружественный tree-shaking: брать только нужную\n"
            "// функцию, а не всю библиотеку.\n"
            "// НЕПРАВИЛЬНО (вся библиотека может попасть в бандл):\n"
            "// import _ from 'lodash';\n"
            "// const result = _.debounce(fn, 300);\n"
            "//\n"
            "// ПРАВИЛЬНО (импортируется только нужный модуль, tree-shaking проще):\n"
            "import debounce from 'lodash/debounce';\n"
            "const result = debounce(() => console.log('поиск'), 300);\n\n"
            "// Простой скрипт для CI, проверяющий бюджет размера бандла:\n"
            "// предупреждает, если размер сборки превышает заданный порог.\n"
            "// (на практике так же делают инструментом вроде \"bundlesize\")\n"
            "function checkBundleBudget(actualKb, budgetKb = 300) {\n"
            "  if (actualKb > budgetKb) {\n"
            "    console.warn(\n"
            "      `Размер бандла ${actualKb}КБ превышает бюджет ${budgetKb}КБ!`\n"
            "    );\n"
            "    return false;\n"
            "  }\n"
            "  return true;\n"
            "}\n\n"
            "// Проверка дублирующихся версий (команда терминала, не код, но её\n"
            "// можно выполнить прямо в проекте):\n"
            "//\n"
            "//   npm ls lodash\n"
            "//   # вывод: lodash@4.17.21, и если в другой зависимости есть\n"
            "//   # lodash@3.10.1, обе версии будут видны в дереве\n"
            "//\n"
            "// Принудительное сведение к одной версии (в package.json, для yarn):\n"
            "//\n"
            "//   {\n"
            "//     \"resolutions\": { \"lodash\": \"4.17.21\" }\n"
            "//   }\n\n"
            "// Небольшой помощник для сравнения сжатого и несжатого размера —\n"
            "// оба полезны, но показывают разное.\n"
            "function summarizeBundleSize({ rawKb, gzipKb, brotliKb }) {\n"
            "  return {\n"
            "    parseExecuteCost: `${rawKb}КБ (объём для PARSE/EXECUTE браузером)`,\n"
            "    networkCost: `${brotliKb ?? gzipKb}КБ (реальный сетевой трафик)`,\n"
            "  };\n"
            "}\n\n"
            "// Чтобы изменить настройки webpack без «eject» из CRA, используют\n"
            "// craco (Create React App Configuration Override) — через него можно\n"
            "// подключить плагин webpack-bundle-analyzer.\n"
            "// craco.config.js:\n"
            "//\n"
            "//   const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');\n"
            "//   module.exports = {\n"
            "//     webpack: {\n"
            "//       plugins: {\n"
            "//         add: [new BundleAnalyzerPlugin({ analyzerMode: 'static' })],\n"
            "//       },\n"
            "//     },\n"
            "//   };\n"
            "//\n"
            "// package.json скрипта:  \"craco build\"  вместо  \"react-scripts build\"\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Berilgan bundle'ni tahlil qilib, kamida bitta og'ir modulni qisqartiring",
            "task_title_ru": "Проанализируйте данный бандл и сократите минимум один тяжёлый модуль",
            "task_description": (
                "Sizga bitta katta kutubxonani (masalan, to'liq lodash yoki "
                "moment.js) faqat bitta kichik funksiyasi uchun import qiladigan "
                "kichik loyiha beriladi. source-map-explorer (yoki shunga o'xshash "
                "vosita) yordamida build'ni tahlil qiling, eng katta modulni "
                "aniqlang, so'ng uni (a) faqat kerakli kichik import bilan "
                "almashtiring (masalan lodash/debounce) YOKI (b) dinamik "
                "import()ga o'tkazing. Tahlil natijasini (oldingi/keyingi hajm) "
                "yozib qoldiring."
            ),
            "task_description_ru": (
                "Вам дан небольшой проект, импортирующий одну большую библиотеку "
                "(например, весь lodash или moment.js) ради одной маленькой "
                "функции. Проанализируйте сборку через source-map-explorer (или "
                "аналогичный инструмент), найдите самый крупный модуль, затем (a) "
                "замените его точечным импортом нужной функции (например "
                "lodash/debounce) ЛИБО (b) переведите на динамический import(). "
                "Запишите результат анализа (размер до/после)."
            ),
            "task_requirements": (
                "source-map-explorer (yoki muqobil) orqali tahlil bajarilgan "
                "bo'lishi shart. Kamida bitta modul hajmi kamaytirilgan va "
                "oldingi/keyingi hajm solishtiruvi yozma taqdim etilishi kerak."
            ),
            "task_requirements_ru": (
                "Обязательно выполнить анализ через source-map-explorer (или "
                "аналог). Минимум один модуль должен быть сокращён, сравнение "
                "размера до/после должно быть представлено письменно."
            ),
            "task_technologies": "source-map-explorer, webpack, dynamic import()",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: dinamik import va tree-shaking'ga mos kod",
            "description": "Og'ir kutubxonani faqat kerak bo'lganda yuklash va tree-shaking'ga mos import qilish namunasi.",
            "sample_type": "code",
            "code_files": [
                {"filename": "BundleOptimization.jsx", "language": "jsx", "code": (
                    "import debounce from 'lodash/debounce';\n\n"
                    "export default function SearchBox({ onSearch }) {\n"
                    "  const debounced = React.useMemo(() => debounce(onSearch, 300), [onSearch]);\n\n"
                    "  const handleExport = async () => {\n"
                    "    const { exportToCsv } = await import('./csvExporter');\n"
                    "    exportToCsv();\n"
                    "  };\n\n"
                    "  return (\n"
                    "    <div>\n"
                    "      <input onChange={(e) => debounced(e.target.value)} />\n"
                    "      <button onClick={handleExport}>Export CSV</button>\n"
                    "    </div>\n"
                    "  );\n"
                    "}\n"
                )},
            ],
        },
        "exercises": [
            {
                "title": "Tree-shaking nima qiladi",
                "title_ru": "Что делает tree-shaking",
                "description": "Tree-shaking asosan nimani amalga oshiradi?",
                "description_ru": "Что в основном реализует tree-shaking?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Haqiqatda ishlatilmagan eksportlarni yakuniy bundle'dan olib tashlaydi",
                    "CSS animatsiyalarini optimallashtiradi",
                    "Rasm fayllarini siqadi",
                    "Serverga so'rovlar sonini kamaytiradi",
                ],
                "options_ru": [
                    "Удаляет из итогового бандла реально неиспользуемые экспорты",
                    "Оптимизирует CSS-анимации",
                    "Сжимает файлы изображений",
                    "Уменьшает число запросов к серверу",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"Shaking\" (silkitish) so'zi — daraxtdan quruq barglarni tushirish metaforasi.",
                "hint_ru": "Слово «shaking» (встряхивание) — метафора стряхивания сухих листьев с дерева.",
                "explanation": "Tree-shaking ES module import/export tuzilishini tahlil qilib, ishlatilmagan kodni bundle'dan chiqarib tashlaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Bundle tahlil vositasi",
                "title_ru": "Инструмент анализа бандла",
                "description": "Bo'shliqni to'ldiring: CRA loyihasida bundle ichidagi modullar hajmini vizual ko'rish uchun ___ kabi vosita ishlatiladi.",
                "description_ru": "Заполните пропуск: в проекте CRA для визуального просмотра размера модулей внутри бандла используется инструмент вроде ___.",
                "exercise_type": "fill_in_blank",
                "correct_answers": "source-map-explorer",
                # Technical npm package name — stays identical in RU, not
                # translated as natural language (see is_natural_language_answer
                # heuristic in course_builder/db_helpers.py: hyphenated tokens
                # aren't recognized as code-shaped, so an explicit RU value is
                # still required here to satisfy translate_exercises_from_spec).
                "correct_answers_ru": "source-map-explorer",
                "hint": "Darsda ikkinchi bo'limda ismi bilan aytilgan vosita.",
                "hint_ru": "Инструмент назван по имени во втором разделе урока.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Bundle qisqartirish qadamlari",
                "title_ru": "Шаги сокращения бандла",
                "description": "Bundle hajmini tahlil qilish va qisqartirish oqimini tartibga joylashtiring.",
                "description_ru": "Расставьте по порядку процесс анализа и сокращения размера бандла.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Loyihani build qilish",
                    "source-map-explorer bilan tahlil qilish",
                    "Kutilmagan katta modulni topish",
                    "Yengilroq muqobil yoki dinamik import qo'llash",
                    "Qayta build qilib hajmni solishtirish",
                ],
                "drag_items_ru": [
                    "Собрать проект",
                    "Проанализировать через source-map-explorer",
                    "Найти неожиданно большой модуль",
                    "Применить более лёгкую альтернативу или динамический импорт",
                    "Пересобрать и сравнить размер",
                ],
                "correct_order": [
                    "Loyihani build qilish",
                    "source-map-explorer bilan tahlil qilish",
                    "Kutilmagan katta modulni topish",
                    "Yengilroq muqobil yoki dinamik import qo'llash",
                    "Qayta build qilib hajmni solishtirish",
                ],
                "hint": "Build har doim eng boshida, solishtirish — eng oxirida.",
                "hint_ru": "Сборка всегда в начале, сравнение — в конце.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 9,
        "title": "9-Holatni boshqarish performance: Redux selectors va reselect",
        "title_ru": "9-Производительность управления состоянием: селекторы Redux и reselect",
        "points_reward": 15,
        "text_content": (
            "<h3>Halol boshlanish nuqtasi: bu platformadagi haqiqiy Redux holati</h3>"
            "<p>Bu darsni boshlashdan oldin halol bir narsani aytish kerak: ushbu "
            "platformaning <code>frontend/src/store/store.js</code> fayli haqiqatan "
            "ham <code>configureStore</code> orqali <code>courses</code> va "
            "<code>students</code> nomli ikkita slice'ni ro'yxatga oladi "
            "(<code>coursesSlice.js</code>/<code>studentsSlice.js</code> orqali). "
            "Lekin butun <code>frontend/src</code> bo'ylab qidiruv shuni ko'rsatadiki, "
            "HECH BIR komponent <code>useSelector</code>'ni chaqirmaydi — haqiqiy "
            "kurslar ro'yxati (masalan, <code>StudentCourses.js</code>) bu Redux "
            "slice'idan emas, to'g'ridan-to'g'ri REST API'dan (<code>useHttp</code> "
            "orqali) o'qiladi. Demak, bu — real, lekin hozircha ishlatilmayotgan "
            "do'kon. Shu sababli bu darsdagi <code>useSelector</code> misollari "
            "ushbu haqiqiy store shakliga asoslangan, LEKIN aniq belgilangan "
            "FARAZIY kengaytma sifatida taqdim etiladi — mavjud bo'lmagan jonli "
            "selector'ni bor deb da'vo qilmasdan.</p>"
            "<h3>useSelector'ning asosiy qoidasi: granularity (donadorlik)</h3>"
            "<p>Agar bu Redux do'koni ishlatilganda edi, eng muhim qoida shu bo'lardi: "
            "<code>useSelector</code>ga qanchalik KICHIK va ANIQ funksiya bersangiz, "
            "komponentingiz shunchalik kamroq keraksiz qayta render bo'ladi. "
            "<code>useSelector((state) =&gt; state.courses)</code> — butun "
            "<code>courses</code> slice'ini oladi, demak slice ICHIDAGI istalgan "
            "maydon o'zgarishi (hatto komponent umuman qiziqmagan maydon ham) "
            "qayta render'ga olib keladi. <code>useSelector((state) =&gt; "
            "state.courses.chapters)</code> esa faqat <code>chapters</code> "
            "massivi o'zgarganda qayta render beradi — bu xuddi 6-darsda ko'rgan "
            "Context muammosi bilan bir xil printsip, faqat Redux'da bu muammoni "
            "hal qilish uchun maxsus vosita (selector) mavjud.</p>"
            "<h3>Yangi obyekt qaytaruvchi selector — yashirin tuzoq</h3>"
            "<p>Muhim nuance: <code>useSelector((state) =&gt; ({{ count: "
            "state.courses.courses.length, chapters: state.courses.chapters }}))</code> "
            "kabi selector HAR safar YANGI obyekt qaytaradi — hatto ichidagi "
            "qiymatlar o'zgarmagan bo'lsa ham. <code>useSelector</code> standart "
            "holatda <code>===</code> orqali solishtiradi, demak bunday selector "
            "HAR store yangilanishida (hatto aloqasiz slice o'zgarsa ham) "
            "komponentni qayta render qiladi. Bu — 2-darsda ko'rgan \"inline obyekt "
            "prop\" muammosining Redux versiyasi.</p>"
            "<h3>reselect: hisoblangan selector'larni keshlash</h3>"
            "<p><code>reselect</code> kutubxonasining <code>createSelector</code> "
            "funksiyasi — bir nechta \"input selector\"larni oladi va ularning "
            "natijalarini <code>useMemo</code>ga o'xshash tarzda keshlaydi: agar "
            "input'lar (masalan, <code>state.courses.courses</code> va "
            "<code>state.courses.chapters</code>) OLDINGI chaqiruvdagi bilan bir "
            "xil bo'lsa, hisoblangan natija qayta HISOBLANMAYDI, oldingi (bir xil "
            "reference'li) natija qaytariladi. Bu — Context'dagi <code>useMemo</code>ga "
            "o'xshash yechim, faqat Redux store darajasida.</p>"
            "<h3>Diagramma: keng va tor selector taqqoslamasi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  S[\"studentsSlice yangilanadi\n"
            "(courses'ga aloqasi yo'q)\"] --> W[\"useSelector(state => state.courses)\n"
            "BUTUN slice'ni oladi\"]\n"
            "  W --> R1[\"Komponent qayta render bo'ladi\n"
            "(kerak emas edi)\"]\n"
            "  S -.->|\"courses o'zgarmadi\"| N[\"useSelector(state => "
            "state.courses.chapters)\"]\n"
            "  N --> R2[\"Komponent qayta render BO'LMAYDI\n"
            "(to'g'ri natija)\"]\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: aloqasiz slice o'zgarishi ham keng "
            "selector orqali keraksiz qayta render keltirib chiqarishi mumkin, tor "
            "selector esa bundan himoyalaydi.</p>"
            "<h3>Yashirin tuzoq: bitta selector'ni ro'yxat elementlari orasida bo'lishish</h3>"
            "<p><code>reselect</code>ning standart <code>createSelector</code>i "
            "faqat OXIRGI chaqiruv natijasini keshlaydi — bitta yozuv, bitta "
            "kesh. Agar bitta <code>selectCourseById</code> selectorini "
            "RO'YXATDAGI HAR BIR element uchun BIR XIL instansiya sifatida "
            "ishlatilsa (masalan, har bir <code>CourseRow</code> komponenti bir xil "
            "modul darajasidagi selectorni chaqirsa, lekin har xil <code>id</code> "
            "bilan), har bir chaqiruv OLDINGI keshni \"bekor qiladi\" — chunki "
            "kirish qiymati (<code>id</code>) har safar boshqacha. Natijada kesh "
            "HECH QACHON \"hit\" bo'lmaydi, faqat doimiy \"miss\" — memoizatsiya "
            "amalda ishlamay qoladi. To'g'ri yechim: HAR BIR komponent instansiyasi "
            "uchun ALOHIDA selector yaratish (\"selector factory\" naqshi, "
            "<code>useMemo(() =&gt; makeSelectCourseById(), [])</code> orqali "
            "komponent umri davomida bitta selector saqlanadi).</p>"
        ),
        "text_content_ru": (
            "<h3>Честная отправная точка: реальное состояние Redux на платформе</h3>"
            "<p>Прежде чем начать этот урок, нужно честно сказать: файл "
            "<code>frontend/src/store/store.js</code> этой платформы "
            "действительно регистрирует через <code>configureStore</code> два "
            "слайса — <code>courses</code> и <code>students</code> (через "
            "<code>coursesSlice.js</code>/<code>studentsSlice.js</code>). Но поиск "
            "по всему <code>frontend/src</code> показывает, что НИ ОДИН компонент "
            "не вызывает <code>useSelector</code> — реальный список курсов "
            "(например, в <code>StudentCourses.js</code>) читается не из этого "
            "слайса Redux, а напрямую из REST API (через <code>useHttp</code>). "
            "То есть это реальный, но пока неиспользуемый store. Поэтому примеры "
            "<code>useSelector</code> в этом уроке опираются на реальную форму "
            "этого store, НО явно представлены как ГИПОТЕТИЧЕСКОЕ расширение — без "
            "утверждения, что несуществующий живой селектор на самом деле есть.</p>"
            "<h3>Главное правило useSelector: гранулярность</h3>"
            "<p>Если бы этот Redux store использовался, самое важное правило было "
            "бы таким: чем МЕНЬШЕ и ТОЧНЕЕ функция, переданная в "
            "<code>useSelector</code>, тем меньше лишних ре-рендеров у вашего "
            "компонента. <code>useSelector((state) =&gt; state.courses)</code> — "
            "берёт ВЕСЬ слайс <code>courses</code>, а значит изменение ЛЮБОГО поля "
            "внутри слайса (даже совсем не интересующего компонент) вызовет "
            "ре-рендер. <code>useSelector((state) =&gt; "
            "state.courses.chapters)</code> же даёт ре-рендер только при изменении "
            "массива <code>chapters</code> — тот же принцип, что и проблема "
            "Context из урока 6, только в Redux для этого есть специальный "
            "инструмент (селектор).</p>"
            "<h3>Селектор, возвращающий новый объект — скрытая ловушка</h3>"
            "<p>Важный нюанс: селектор вроде <code>useSelector((state) =&gt; "
            "({{ count: state.courses.courses.length, chapters: "
            "state.courses.chapters }}))</code> КАЖДЫЙ РАЗ возвращает НОВЫЙ "
            "объект — даже если значения внутри не изменились. "
            "<code>useSelector</code> по умолчанию сравнивает через "
            "<code>===</code>, значит такой селектор перерендерит компонент при "
            "КАЖДОМ обновлении store (даже если изменился совсем не связанный "
            "слайс). Это Redux-версия проблемы «инлайн-объект как prop» из "
            "урока 2.</p>"
            "<h3>reselect: кеширование вычисляемых селекторов</h3>"
            "<p>Функция <code>createSelector</code> из библиотеки "
            "<code>reselect</code> принимает несколько «input-селекторов» и "
            "кеширует их результат похоже на <code>useMemo</code>: если входные "
            "данные (например, <code>state.courses.courses</code> и "
            "<code>state.courses.chapters</code>) совпадают с ПРЕДЫДУЩИМ вызовом, "
            "вычисленный результат НЕ ПЕРЕСЧИТЫВАЕТСЯ, возвращается прежний "
            "(с той же ссылкой) результат. Это решение, аналогичное "
            "<code>useMemo</code> в Context, но на уровне Redux store.</p>"
            "<h3>Диаграмма: широкий и узкий селектор</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  S[\"studentsSlice обновляется\n"
            "(не связан с courses)\"] --> W[\"useSelector(state => state.courses)\n"
            "берёт ВЕСЬ слайс\"]\n"
            "  W --> R1[\"Компонент перерендеривается\n"
            "(это было не нужно)\"]\n"
            "  S -.->|\"courses не изменился\"| N[\"useSelector(state => "
            "state.courses.chapters)\"]\n"
            "  N --> R2[\"Компонент НЕ перерендеривается\n"
            "(правильный результат)\"]\n"
            "</pre>"
            "<p>Диаграмма показывает: изменение несвязанного слайса может вызвать "
            "лишний ре-рендер через широкий селектор, а узкий селектор от этого "
            "защищает.</p>"
            "<h3>Скрытая ловушка: один селектор на все элементы списка</h3>"
            "<p>Стандартный <code>createSelector</code> из <code>reselect</code> "
            "кеширует только результат ПОСЛЕДНЕГО вызова — одна запись, один кеш. "
            "Если использовать ОДИН селектор <code>selectCourseById</code> как ОДИН "
            "И ТОТ ЖЕ экземпляр для КАЖДОГО элемента списка (например, каждый "
            "компонент <code>CourseRow</code> вызывает один и тот же селектор "
            "уровня модуля, но с разным <code>id</code>), каждый вызов "
            "«отменяет» предыдущий кеш — потому что входное значение "
            "(<code>id</code>) каждый раз другое. В итоге кеш НИКОГДА не "
            "«попадает» (hit), только постоянные «промахи» (miss) — мемоизация "
            "фактически перестаёт работать. Правильное решение: создавать "
            "ОТДЕЛЬНЫЙ селектор для КАЖДОГО экземпляра компонента (паттерн "
            "«selector factory», через <code>useMemo(() =&gt; "
            "makeSelectCourseById(), [])</code> — один селектор хранится всё время "
            "жизни компонента). Этот паттерн стоит держать в голове при любом "
            "списке, где каждая строка обращается к общему store по своему id.</p>"
        ),
        "code_content": (
            "// store/store.js'ning haqiqiy tuzilishi (real kod):\n"
            "//\n"
            "//   import { configureStore } from '@reduxjs/toolkit';\n"
            "//   import coursesReducer  from './coursesSlice';\n"
            "//   import studentsReducer from './studentsSlice';\n"
            "//   const store = configureStore({\n"
            "//     reducer: { courses: coursesReducer, students: studentsReducer },\n"
            "//   });\n"
            "//\n"
            "// FARAZIY KENGAYTMA: agar bu store'dan komponentda foydalanilsa.\n\n"
            "import { useSelector } from 'react-redux';\n"
            "import { createSelector } from 'reselect';\n\n"
            "// NOTO'G'RI: butun slice olinadi — students'ga aloqasi bo'lmagan\n"
            "// o'zgarish ham bu komponentni qayta render qiladi.\n"
            "function ChaptersListWide() {\n"
            "  const courses = useSelector((state) => state.courses);\n"
            "  return <ul>{courses.chapters.map((c) => <li key={c}>{c}</li>)}</ul>;\n"
            "}\n\n"
            "// YAXSHIROQ: faqat kerakli maydon tanlanadi.\n"
            "function ChaptersListNarrow() {\n"
            "  const chapters = useSelector((state) => state.courses.chapters);\n"
            "  return <ul>{chapters.map((c) => <li key={c}>{c}</li>)}</ul>;\n"
            "}\n\n"
            "// NOTO'G'RI: selector har safar YANGI obyekt qaytaradi — hatto\n"
            "// qiymatlar bir xil qolsa ham, useSelector'ning === solishtiruvi\n"
            "// buni har doim \"o'zgardi\" deb hisoblaydi.\n"
            "function CourseSummaryBad() {\n"
            "  const summary = useSelector((state) => ({\n"
            "    count: state.courses.courses.length,\n"
            "    chapters: state.courses.chapters,\n"
            "  }));\n"
            "  return <p>{summary.count} ta kurs, {summary.chapters.length} ta bo'lim</p>;\n"
            "}\n\n"
            "// TO'G'RI: reselect orqali keshlangan selector — input'lar\n"
            "// o'zgarmasa, natija qayta hisoblanmaydi, bir xil reference qaytadi.\n"
            "const selectCourses = (state) => state.courses.courses;\n"
            "const selectChapters = (state) => state.courses.chapters;\n\n"
            "const selectCourseSummary = createSelector(\n"
            "  [selectCourses, selectChapters],\n"
            "  (courses, chapters) => ({\n"
            "    count: courses.length,\n"
            "    chapters,\n"
            "  })\n"
            ");\n\n"
            "function CourseSummaryGood() {\n"
            "  const summary = useSelector(selectCourseSummary);\n"
            "  return <p>{summary.count} ta kurs, {summary.chapters.length} ta bo'lim</p>;\n"
            "}\n\n"
            "// NOTO'G'RI: bitta modul darajasidagi selector barcha ro'yxat\n"
            "// elementlari orasida BO'LISHILADI — har xil id bilan chaqirilganda\n"
            "// kesh doim \"miss\" bo'ladi, memoizatsiya amalda ishlamaydi.\n"
            "const selectCourseByIdShared = createSelector(\n"
            "  [selectCourses, (state, courseId) => courseId],\n"
            "  (courses, courseId) => courses.find((c) => c.id === courseId)\n"
            ");\n\n"
            "function CourseRowBad({ courseId }) {\n"
            "  // Ro'yxatdagi HAR bir qator BIR XIL selectCourseByIdShared'ni\n"
            "  // chaqiradi — har biri boshqasining keshini bekor qiladi.\n"
            "  const course = useSelector((state) => selectCourseByIdShared(state, courseId));\n"
            "  return <div>{course?.title}</div>;\n"
            "}\n\n"
            "// TO'G'RI: \"selector factory\" — har bir komponent instansiyasi\n"
            "// o'ziga xos selector nusxasini oladi, kesh ular orasida bo'lishilmaydi.\n"
            "const makeSelectCourseById = () =>\n"
            "  createSelector(\n"
            "    [selectCourses, (state, courseId) => courseId],\n"
            "    (courses, courseId) => courses.find((c) => c.id === courseId)\n"
            "  );\n\n"
            "function CourseRowGood({ courseId }) {\n"
            "  // useMemo komponent umri davomida BITTA selector nusxasini saqlaydi.\n"
            "  const selectCourseById = React.useMemo(() => makeSelectCourseById(), []);\n"
            "  const course = useSelector((state) => selectCourseById(state, courseId));\n"
            "  return <div>{course?.title}</div>;\n"
            "}\n"
        ),
        "code_content_ru": (
            "// Реальная структура store/store.js (настоящий код):\n"
            "//\n"
            "//   import { configureStore } from '@reduxjs/toolkit';\n"
            "//   import coursesReducer  from './coursesSlice';\n"
            "//   import studentsReducer from './studentsSlice';\n"
            "//   const store = configureStore({\n"
            "//     reducer: { courses: coursesReducer, students: studentsReducer },\n"
            "//   });\n"
            "//\n"
            "// ГИПОТЕТИЧЕСКОЕ РАСШИРЕНИЕ: если бы этот store использовался в компоненте.\n\n"
            "import { useSelector } from 'react-redux';\n"
            "import { createSelector } from 'reselect';\n\n"
            "// НЕПРАВИЛЬНО: берётся весь слайс — изменение, не связанное со\n"
            "// students, тоже перерендерит этот компонент.\n"
            "function ChaptersListWide() {\n"
            "  const courses = useSelector((state) => state.courses);\n"
            "  return <ul>{courses.chapters.map((c) => <li key={c}>{c}</li>)}</ul>;\n"
            "}\n\n"
            "// ЛУЧШЕ: выбирается только нужное поле.\n"
            "function ChaptersListNarrow() {\n"
            "  const chapters = useSelector((state) => state.courses.chapters);\n"
            "  return <ul>{chapters.map((c) => <li key={c}>{c}</li>)}</ul>;\n"
            "}\n\n"
            "// НЕПРАВИЛЬНО: селектор каждый раз возвращает НОВЫЙ объект — даже\n"
            "// если значения не изменились, сравнение === в useSelector всегда\n"
            "// считает это «изменением».\n"
            "function CourseSummaryBad() {\n"
            "  const summary = useSelector((state) => ({\n"
            "    count: state.courses.courses.length,\n"
            "    chapters: state.courses.chapters,\n"
            "  }));\n"
            "  return <p>{summary.count} курсов, {summary.chapters.length} разделов</p>;\n"
            "}\n\n"
            "// ПРАВИЛЬНО: закешированный через reselect селектор — если входные\n"
            "// данные не изменились, результат не пересчитывается, возвращается\n"
            "// та же ссылка.\n"
            "const selectCourses = (state) => state.courses.courses;\n"
            "const selectChapters = (state) => state.courses.chapters;\n\n"
            "const selectCourseSummary = createSelector(\n"
            "  [selectCourses, selectChapters],\n"
            "  (courses, chapters) => ({\n"
            "    count: courses.length,\n"
            "    chapters,\n"
            "  })\n"
            ");\n\n"
            "function CourseSummaryGood() {\n"
            "  const summary = useSelector(selectCourseSummary);\n"
            "  return <p>{summary.count} курсов, {summary.chapters.length} разделов</p>;\n"
            "}\n\n"
            "// НЕПРАВИЛЬНО: один селектор уровня модуля РАЗДЕЛЯЕТСЯ между всеми\n"
            "// элементами списка — при вызове с разными id кеш всегда «промах»,\n"
            "// мемоизация фактически не работает.\n"
            "const selectCourseByIdShared = createSelector(\n"
            "  [selectCourses, (state, courseId) => courseId],\n"
            "  (courses, courseId) => courses.find((c) => c.id === courseId)\n"
            ");\n\n"
            "function CourseRowBad({ courseId }) {\n"
            "  // КАЖДАЯ строка списка вызывает ОДИН И ТОТ ЖЕ selectCourseByIdShared\n"
            "  // — каждая отменяет кеш другой.\n"
            "  const course = useSelector((state) => selectCourseByIdShared(state, courseId));\n"
            "  return <div>{course?.title}</div>;\n"
            "}\n\n"
            "// ПРАВИЛЬНО: «selector factory» — каждый экземпляр компонента\n"
            "// получает свой собственный экземпляр селектора, кеши не делятся.\n"
            "const makeSelectCourseById = () =>\n"
            "  createSelector(\n"
            "    [selectCourses, (state, courseId) => courseId],\n"
            "    (courses, courseId) => courses.find((c) => c.id === courseId)\n"
            "  );\n\n"
            "function CourseRowGood({ courseId }) {\n"
            "  // useMemo хранит ОДИН экземпляр селектора всё время жизни компонента.\n"
            "  const selectCourseById = React.useMemo(() => makeSelectCourseById(), []);\n"
            "  const course = useSelector((state) => selectCourseById(state, courseId));\n"
            "  return <div>{course?.title}</div>;\n"
            "}\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Berilgan slice uchun keshlangan reselect selector yozing",
            "task_title_ru": "Напишите закешированный reselect-селектор для данного слайса",
            "task_description": (
                "Sizga oddiy Redux slice beriladi (masalan, \"products\" — id, "
                "name, category, price maydonlari bilan). Avval "
                "useSelector((state) => state.products) kabi KENG selector "
                "ishlatilgan komponent berilgan bo'ladi. Buni: (1) faqat kerakli "
                "maydonni oluvchi TOR selector'ga o'tkazing, (2) reselect'ning "
                "createSelector orqali \"berilgan category bo'yicha filtrlangan va "
                "narx bo'yicha saralangan mahsulotlar\" ni hisoblovchi keshlangan "
                "selector yozing, (3) bitta selector'ni ro'yxat elementlari orasida "
                "bo'lishib yuborish xatosidan saqlaning (\"selector factory\" "
                "naqshi kerak bo'lsa qo'llang)."
            ),
            "task_description_ru": (
                "Вам дан обычный Redux-слайс (например, «products» — с полями id, "
                "name, category, price). Сначала дан компонент, использующий "
                "ШИРОКИЙ селектор вроде useSelector((state) => state.products). "
                "Переведите его: (1) на УЗКИЙ селектор, берущий только нужное "
                "поле, (2) напишите через createSelector из reselect "
                "закешированный селектор, вычисляющий «товары, отфильтрованные по "
                "заданной категории и отсортированные по цене», (3) избегайте "
                "ошибки разделения одного селектора между элементами списка "
                "(при необходимости примените паттерн «selector factory»)."
            ),
            "task_requirements": (
                "Tor selector va reselect orqali keshlangan selector yozilishi "
                "shart. Agar ro'yxat elementlari uchun ishlatilsa, selector "
                "factory naqshi qo'llanilgan bo'lishi kerak."
            ),
            "task_requirements_ru": (
                "Обязательны узкий селектор и закешированный через reselect "
                "селектор. Если используется для элементов списка, обязан быть "
                "применён паттерн selector factory."
            ),
            "task_technologies": "Redux Toolkit, react-redux, reselect",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: reselect bilan keshlangan selector",
            "description": "Keng va tor selector taqqoslamasi hamda reselect orqali keshlangan hisoblangan selector namunasi.",
            "sample_type": "code",
            "code_files": [
                {"filename": "selectors.js", "language": "javascript", "code": (
                    "import { createSelector } from 'reselect';\n\n"
                    "export const selectCourses = (state) => state.courses.courses;\n"
                    "export const selectChapters = (state) => state.courses.chapters;\n\n"
                    "export const selectCourseSummary = createSelector(\n"
                    "  [selectCourses, selectChapters],\n"
                    "  (courses, chapters) => ({ count: courses.length, chapters })\n"
                    ");\n"
                )},
            ],
        },
        "exercises": [
            {
                "title": "Ushbu platformadagi Redux'ning haqiqiy holati",
                "title_ru": "Реальное состояние Redux на этой платформе",
                "description": "Darsda ta'kidlanganidek, ushbu platforma kodida useSelector haqida qanday haqiqat bor?",
                "description_ru": "Как отмечено в уроке, какова правда об useSelector в коде этой платформы?",
                "exercise_type": "multiple_choice",
                "options": [
                    "store.js real, lekin hech bir komponent useSelector chaqirmaydi — kurslar REST API'dan olinadi",
                    "Barcha komponentlar useSelector orqali ishlaydi",
                    "Redux umuman ishlatilmaydi, hatto store.js ham yo'q",
                    "useSelector faqat teacher sahifalarida ishlatiladi",
                ],
                "options_ru": [
                    "store.js реален, но ни один компонент не вызывает useSelector — курсы берутся из REST API",
                    "Все компоненты работают через useSelector",
                    "Redux вообще не используется, даже store.js не существует",
                    "useSelector используется только на страницах учителя",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Darsning \"halol boshlanish nuqtasi\" bo'limini eslang.",
                "hint_ru": "Вспомните раздел «честная отправная точка» в уроке.",
                "explanation": "store.js real konfiguratsiya, lekin StudentCourses.js kabi haqiqiy komponentlar ma'lumotni REST API orqali oladi, useSelector orqali emas.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Keng va tor selector",
                "title_ru": "Широкий и узкий селектор",
                "description": (
                    "Bo'shliqni to'ldiring: useSelector((state) => state.courses) — "
                    "bu ___ selector, chunki u butun slice'ni oladi va aloqasiz "
                    "o'zgarishlarda ham qayta render keltirib chiqaradi."
                ),
                "description_ru": (
                    "Заполните пропуск: useSelector((state) => state.courses) — это "
                    "___ селектор, потому что он берёт весь слайс и вызывает "
                    "ре-рендер даже при несвязанных изменениях."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "keng",
                "correct_answers_ru": "широкий",
                "hint": "Uning qarama-qarshisi — \"tor\" (narrow) selector.",
                "hint_ru": "Его противоположность — «узкий» (narrow) селектор.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "reselect qanday ishlaydi",
                "title_ru": "Как работает reselect",
                "description": "createSelector'ning ishlash bosqichlarini tartibga joylashtiring.",
                "description_ru": "Расставьте по порядку этапы работы createSelector.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Input selector'lar (masalan, selectCourses) chaqiriladi",
                    "Natijalar oldingi chaqiruv bilan solishtiriladi",
                    "Agar bir xil bo'lsa, keshlangan natija qaytariladi",
                    "Agar farq qilsa, hisoblash funksiyasi qayta ishga tushadi",
                ],
                "drag_items_ru": [
                    "Вызываются input-селекторы (например, selectCourses)",
                    "Результаты сравниваются с предыдущим вызовом",
                    "Если совпадают, возвращается закешированный результат",
                    "Если отличаются, функция вычисления запускается заново",
                ],
                "correct_order": [
                    "Input selector'lar (masalan, selectCourses) chaqiriladi",
                    "Natijalar oldingi chaqiruv bilan solishtiriladi",
                    "Agar bir xil bo'lsa, keshlangan natija qaytariladi",
                    "Agar farq qilsa, hisoblash funksiyasi qayta ishga tushadi",
                ],
                "hint": "useMemo'ning ishlash tartibi bilan bir xil mantiq.",
                "hint_ru": "Та же логика, что и порядок работы useMemo.",
                "difficulty_level": "Hard",
                "points": 15,
            },
        ],
    },
    {
        "order": 10,
        "title": "10-Web Vitals React ilovasida (LCP, INP, CLS)",
        "title_ru": "10-Web Vitals в React-приложении (LCP, INP, CLS)",
        "points_reward": 15,
        "text_content": (
            "<h3>Web Vitals — brauzer o'lchaydigan, foydalanuvchi his qiladigan metrikalar</h3>"
            "<p>Oldingi darslarda biz React DevTools Profiler orqali \"komponent "
            "qancha render bo'ldi\" degan savolni o'lchashni o'rgandik. Web Vitals "
            "esa boshqa, kengroq savolga javob beradi: \"foydalanuvchi sahifani "
            "QANDAY his qiladi\" — bu React'ga xos emas, HAR QANDAY veb-sahifaga "
            "tegishli, lekin React ilovalarida ko'proq uchraydigan o'ziga xos "
            "sabablari bor. Uchta asosiy metrika: <strong>LCP</strong> (Largest "
            "Contentful Paint — eng katta ko'rinadigan element qachon chizilgani), "
            "<strong>INP</strong> (Interaction to Next Paint — foydalanuvchi "
            "harakatidan keyin ekran qachon javob berishi, 2024-yilda FID'ni "
            "almashtirgan), <strong>CLS</strong> (Cumulative Layout Shift — sahifa "
            "yuklanish paytida elementlar qancha \"sakraganini\" o'lchaydigan "
            "ko'rsatkich).</p>"
            "<h3>React ilovalari LCP bilan nima xato qiladi</h3>"
            "<p>4-darsda ko'rganimizdek, CRA arxitekturasida server bo'sh "
            "<code>&lt;div id=\"root\"&gt;&lt;/div&gt;</code> qaytaradi — bu esa "
            "LCP'ni YOMONLASHTIRADI, chunki brauzer \"eng katta kontent\" deb "
            "hisoblanadigan elementni faqat JS yuklanib, React render bo'lgandan "
            "keyingina ko'radi. Bundan tashqari, agar sahifadagi ENG KATTA element "
            "— masalan, kurs muqovasi rasmi — <code>&lt;img&gt;</code> orqali "
            "keyin, boshqa ma'lumotlar (JSON javob) kelgandan so'ng qo'shilsa, LCP "
            "yanada kechikadi. Yechim: rasm manzili oldindan ma'lum bo'lsa, uni "
            "<code>&lt;link rel=\"preload\"&gt;</code> orqali oldindan yuklashni "
            "boshlash mumkin.</p>"
            "<h3>INP va React'dagi \"sekin event handler\" muammosi</h3>"
            "<p>INP — foydalanuvchi biror narsa bosgandan (klik, klaviatura) "
            "ekran birinchi marta javob berishigacha bo'lgan vaqtni o'lchaydi. Agar "
            "<code>onClick</code> handler ICHIDA katta, sinxron hisoblash bo'lsa "
            "(masalan, katta massivni saralash), brauzer shu vaqt davomida "
            "\"muzlab\" qoladi — foydalanuvchi tugmani bossa ham, ekran darhol "
            "javob bermaydi. Bu — aynan 7-darsda ko'rgan <code>useTransition</code> "
            "yechadigan muammoning bir turi: qimmat ishni kichik bo'laklarga bo'lish "
            "yoki \"shoshilmas\" deb belgilash INP'ni yaxshilaydi.</p>"
            "<h3>CLS va React'ning dinamik render qilishi</h3>"
            "<p>React komponentlari ma'lumot kelgandan keyin render bo'lgani "
            "uchun, agar ma'lumot kelmasdan oldin ELEMENT O'LCHAMI aniq "
            "belgilanmagan bo'lsa (masalan, rasm uchun <code>width</code>/"
            "<code>height</code> yo'q, yoki skeleton loader'ning balandligi "
            "haqiqiy kontentnikidan farq qilsa), ma'lumot kelgandan keyin sahifa "
            "\"sakraydi\" — bu CLS'ni oshiradi. <code>StudentCourses.js</code>dagi "
            "<code>CardSkeleton</code> komponenti aynan shu muammoni oldini olish "
            "uchun mavjud: u haqiqiy <code>CourseCard</code> bilan bir xil "
            "o'lchamdagi bo'sh joy egallaydi, shunda ma'lumot kelganda hech narsa "
            "sakramaydi.</p>"
            "<h3>O'lchash: web-vitals kutubxonasi</h3>"
            "<p>Google'ning <code>web-vitals</code> npm paketi haqiqiy "
            "foydalanuvchi brauzerida shu uchta metrikani o'lchab, callback "
            "orqali qaytaradi — bu Lighthouse'dagi LABORATORIYA o'lchovidan farqli "
            "o'laroq, HAQIQIY foydalanuvchi tajribasini ko'rsatadi (\"field data\"). "
            "Ikkalasi ham foydali: Lighthouse — rivojlanish paytida tezkor tekshirish "
            "uchun, <code>web-vitals</code> production'da haqiqiy foydalanuvchilar "
            "tajribasini kuzatish uchun.</p>"
            "<h3>Diagramma: sahifa yuklanishi va uchta metrika</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart LR\n"
            "  A[\"So'rov yuboriladi\"] --> B[\"Bo'sh HTML keladi\n"
            "(CRA'da div#root bo'sh)\"]\n"
            "  B --> C[\"JS yuklanadi va ishga tushadi\"]\n"
            "  C --> D[\"React render qiladi\n"
            "LCP shu yerda o'lchanadi\"]\n"
            "  D --> E[\"Foydalanuvchi bosadi\n"
            "INP shu yerda o'lchanadi\"]\n"
            "  B -.->|\"o'lcham noaniq element\n"
            "kontent bilan almashsa\"| F[\"Layout siljiydi\n"
            "CLS shu yerda oshadi\"]\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: har bir metrika sahifa hayotining "
            "boshqa bosqichida o'lchanadi, va React arxitekturasi (CRA'ning bo'sh "
            "HTML'i, dinamik render) har uchtasiga ham ta'sir qilishi mumkin.</p>"
            "<h3>INP'ning uchta qismi</h3>"
            "<p>INP amalda uchta bosqichdan iborat: <strong>input delay</strong> "
            "(brauzer boshqa ish bilan band bo'lgani uchun hodisani darhol qabul "
            "qilmasligi), <strong>processing time</strong> (event handler'ning o'zi "
            "ishlash vaqti — aynan shu yerda React komponentining "
            "<code>onClick</code>i ichidagi qimmat hisoblash ko'rinadi) va "
            "<strong>presentation delay</strong> (React yangi holatni render qilib, "
            "brauzer uni ekranga chizib bo'lgunicha bo'lgan vaqt). Uchta bosqichning "
            "har biri alohida tuzatilishi mumkin — masalan, <code>processing "
            "time</code>ni <code>startTransition</code> kamaytiradi, "
            "<code>presentation delay</code>ni esa ortiqcha qayta render'larni "
            "(1-3-darslar) kamaytirish yaxshilaydi.</p>"
            "<h3>CLS qanday hisoblanadi — qisqacha</h3>"
            "<p>CLS = \"impact fraction\" (siljigan elementning ekrandagi qanday "
            "qismini egallashi) ko'paytirilgan \"distance fraction\"ga (element "
            "qancha masofaga siljigani). Bu shuni anglatadiki, KATTA element "
            "(masalan, butun kurs kartasi) hatto BIR NECHA piksel siljisa ham, "
            "kichik elementning katta masofaga siljishidan ko'ra CLS'ga ko'proq "
            "ta'sir qiladi — shuning uchun ayniqsa katta, ko'rinadigan "
            "elementlarning o'lchamini oldindan belgilash muhim.</p>"
        ),
        "text_content_ru": (
            "<h3>Web Vitals — метрики, которые измеряет браузер, а ощущает пользователь</h3>"
            "<p>В предыдущих уроках мы измеряли через React DevTools Profiler "
            "вопрос «сколько раз отрендерился компонент». Web Vitals отвечает на "
            "другой, более широкий вопрос: «КАК пользователь ощущает страницу» — "
            "это не специфично для React, относится к ЛЮБОЙ веб-странице, но в "
            "React-приложениях встречаются свои характерные причины. Три основные "
            "метрики: <strong>LCP</strong> (Largest Contentful Paint — когда "
            "отрисован самый крупный видимый элемент), <strong>INP</strong> "
            "(Interaction to Next Paint — как быстро экран отвечает после "
            "действия пользователя, в 2024 году заменил FID), <strong>CLS</strong> "
            "(Cumulative Layout Shift — насколько элементы «прыгают» при загрузке "
            "страницы).</p>"
            "<h3>Что React-приложения делают не так с LCP</h3>"
            "<p>Как мы видели в уроке 4, в архитектуре CRA сервер возвращает "
            "пустой <code>&lt;div id=\"root\"&gt;&lt;/div&gt;</code> — это "
            "УХУДШАЕТ LCP, потому что браузер видит элемент, считающийся «самым "
            "крупным контентом», только после загрузки JS и рендера React. Кроме "
            "того, если САМЫЙ КРУПНЫЙ элемент страницы — например, изображение "
            "обложки курса — добавляется через <code>&lt;img&gt;</code> ПОСЛЕ "
            "прихода других данных (JSON-ответа), LCP задерживается ещё сильнее. "
            "Решение: если адрес изображения известен заранее, можно начать его "
            "загрузку заранее через <code>&lt;link rel=\"preload\"&gt;</code>.</p>"
            "<h3>INP и проблема «медленного обработчика события» в React</h3>"
            "<p>INP измеряет время от действия пользователя (клик, клавиатура) до "
            "первого ответа экрана. Если ВНУТРИ <code>onClick</code>-обработчика "
            "есть большое синхронное вычисление (например, сортировка большого "
            "массива), браузер «замирает» на это время — даже если пользователь "
            "нажал кнопку, экран не отвечает немедленно. Это тот же тип проблемы, "
            "что решает <code>useTransition</code> из урока 7: разбиение дорогой "
            "работы на части или пометка её как «несрочной» улучшает INP.</p>"
            "<h3>CLS и динамический рендер React</h3>"
            "<p>Поскольку компоненты React рендерятся после прихода данных, если "
            "РАЗМЕР ЭЛЕМЕНТА не задан заранее (например, у изображения нет "
            "<code>width</code>/<code>height</code>, или высота skeleton-загрузчика "
            "отличается от реального контента), после прихода данных страница "
            "«прыгает» — это увеличивает CLS. Компонент <code>CardSkeleton</code> в "
            "<code>StudentCourses.js</code> существует именно для предотвращения "
            "этой проблемы: он занимает пустое место того же размера, что и "
            "настоящий <code>CourseCard</code>, поэтому при приходе данных ничего "
            "не прыгает.</p>"
            "<h3>Измерение: библиотека web-vitals</h3>"
            "<p>npm-пакет <code>web-vitals</code> от Google измеряет эти три "
            "метрики в реальном браузере пользователя и возвращает их через "
            "колбэк — в отличие от ЛАБОРАТОРНОГО измерения Lighthouse, это "
            "показывает РЕАЛЬНЫЙ опыт пользователя («field data»). Оба полезны: "
            "Lighthouse — для быстрой проверки во время разработки, "
            "<code>web-vitals</code> — для отслеживания реального опыта "
            "пользователей в production.</p>"
            "<h3>Диаграмма: загрузка страницы и три метрики</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart LR\n"
            "  A[\"Отправляется запрос\"] --> B[\"Приходит пустой HTML\n"
            "(в CRA div#root пуст)\"]\n"
            "  B --> C[\"JS загружается и запускается\"]\n"
            "  C --> D[\"React рендерит\n"
            "здесь измеряется LCP\"]\n"
            "  D --> E[\"Пользователь кликает\n"
            "здесь измеряется INP\"]\n"
            "  B -.->|\"элемент с неизвестным размером\n"
            "заменяется контентом\"| F[\"Layout сдвигается\n"
            "здесь растёт CLS\"]\n"
            "</pre>"
            "<p>Диаграмма показывает: каждая метрика измеряется на своём этапе "
            "жизни страницы, и архитектура React (пустой HTML в CRA, "
            "динамический рендер) может повлиять на все три.</p>"
            "<h3>Три части INP</h3>"
            "<p>INP на практике состоит из трёх этапов: <strong>input delay</strong> "
            "(браузер не может немедленно принять событие, потому что занят "
            "другой работой), <strong>processing time</strong> (время работы "
            "самого обработчика события — именно здесь видно дорогое вычисление "
            "внутри <code>onClick</code> React-компонента) и <strong>presentation "
            "delay</strong> (время между рендером нового состояния React и "
            "моментом, когда браузер отрисовывает его на экране). Каждый из трёх "
            "этапов можно улучшать отдельно — например, <code>processing "
            "time</code> уменьшает <code>startTransition</code>, а "
            "<code>presentation delay</code> улучшается за счёт уменьшения лишних "
            "ре-рендеров (уроки 1-3).</p>"
            "<h3>Как считается CLS — кратко</h3>"
            "<p>CLS = «impact fraction» (какую часть экрана занимает сдвинувшийся "
            "элемент), умноженная на «distance fraction» (на какое расстояние он "
            "сдвинулся). Это значит, что КРУПНЫЙ элемент (например, вся карточка "
            "курса), сдвинувшийся даже на НЕСКОЛЬКО пикселей, влияет на CLS "
            "сильнее, чем маленький элемент, сдвинувшийся на большое расстояние — "
            "поэтому особенно важно заранее задавать размер крупных, видимых "
            "элементов.</p>"
        ),
        "code_content": (
            "// web-vitals kutubxonasini o'rnatish va ishlatish (CRA'ning\n"
            "// src/reportWebVitals.js fayli aynan shu naqshni ishlatadi).\n"
            "import { onLCP, onINP, onCLS } from 'web-vitals';\n\n"
            "function sendToAnalytics({ name, value, id }) {\n"
            "  // Haqiqiy loyihada bu ma'lumot backend'ga yoki analytics\n"
            "  // xizmatiga yuboriladi — bu yerda faqat konsolga chiqaramiz.\n"
            "  console.log(`[web-vitals] ${name}: ${value.toFixed(2)} (id=${id})`);\n"
            "}\n\n"
            "onLCP(sendToAnalytics);\n"
            "onINP(sendToAnalytics);\n"
            "onCLS(sendToAnalytics);\n\n"
            "// LCP'ni yaxshilash: eng katta element (kurs muqovasi) manzili\n"
            "// oldindan ma'lum bo'lsa, uni index.html'da preload qilish.\n"
            "// public/index.html ichida:\n"
            "//\n"
            "//   <link rel=\"preload\" as=\"image\" href=\"/hero-course-cover.jpg\" />\n\n"
            "// INP'ni yaxshilash: og'ir hisoblashni kichik bo'laklarga bo'lish\n"
            "// (yoki useTransition bilan shoshilmas deb belgilash — 7-dars).\n"
            "function handleSortLargeList(items, setSorted) {\n"
            "  // NOTO'G'RI: butun saralash bitta sinxron blokda — INP yomonlashadi.\n"
            "  // const sorted = items.slice().sort(expensiveCompare);\n"
            "  // setSorted(sorted);\n\n"
            "  // TO'G'RIROQ: React'ning o'zining scheduler'iga ishonib,\n"
            "  // startTransition ichida bajarish.\n"
            "  React.startTransition(() => {\n"
            "    const sorted = items.slice().sort(expensiveCompare);\n"
            "    setSorted(sorted);\n"
            "  });\n"
            "}\n\n"
            "// CLS'ni yaxshilash: StudentCourses.js'dagi haqiqiy naqsh — skeleton\n"
            "// haqiqiy karta bilan bir xil o'lchamda bo'lishi shart.\n"
            "function CardSkeletonReal() {\n"
            "  return (\n"
            "    <div className=\"sc-skeleton\">\n"
            "      {/* Balandlik va kenglik haqiqiy .sc-card bilan bir xil CSS'da\n"
            "          belgilangan — shuning uchun ma'lumot kelganda hech narsa\n"
            "          sakramaydi. */}\n"
            "      <div className=\"sc-skeleton-img\" />\n"
            "      <div className=\"sc-skeleton-body\">\n"
            "        <div className=\"sc-skeleton-line w70\" />\n"
            "        <div className=\"sc-skeleton-line w45\" />\n"
            "      </div>\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// INP'ning uchta bosqichini alohida ko'rish uchun PerformanceObserver\n"
            "// orqali xom 'event' yozuvlarini kuzatish (web-vitals buni ichida\n"
            "// avtomatik qiladi, lekin diagnostika uchun qo'lda ham ko'rish mumkin).\n"
            "function observeInteractionBreakdown() {\n"
            "  const observer = new PerformanceObserver((list) => {\n"
            "    for (const entry of list.getEntries()) {\n"
            "      const inputDelay = entry.processingStart - entry.startTime;\n"
            "      const processingTime = entry.processingEnd - entry.processingStart;\n"
            "      const presentationDelay = entry.duration - inputDelay - processingTime;\n"
            "      console.log('[INP breakdown]', {\n"
            "        inputDelay: inputDelay.toFixed(1),\n"
            "        processingTime: processingTime.toFixed(1),\n"
            "        presentationDelay: presentationDelay.toFixed(1),\n"
            "      });\n"
            "    }\n"
            "  });\n"
            "  observer.observe({ type: 'event', durationThreshold: 40, buffered: true });\n"
            "  return () => observer.disconnect();\n"
            "}\n\n"
            "// CLS diagnostikasi: web-vitals'ning attribution build'i qaysi\n"
            "// element siljiganini aniq ko'rsatadi.\n"
            "import { onCLS } from 'web-vitals/attribution';\n\n"
            "onCLS((metric) => {\n"
            "  const culprit = metric.attribution?.largestShiftTarget;\n"
            "  console.log(`[CLS] qiymat=${metric.value.toFixed(3)}, sabab=${culprit}`);\n"
            "});\n\n"
            "// Xulosa: uchta metrika uchta turli bosqichni qamrab oladi — LCP\n"
            "// birinchi chizish haqida, INP harakatga javob haqida, CLS esa\n"
            "// yuklanish paytidagi vizual barqarorlik haqida.\n"
        ),
        "code_content_ru": (
            "// Установка и использование web-vitals (файл src/reportWebVitals.js\n"
            "// в CRA использует именно этот паттерн).\n"
            "import { onLCP, onINP, onCLS } from 'web-vitals';\n\n"
            "function sendToAnalytics({ name, value, id }) {\n"
            "  // В реальном проекте это отправляется на бэкенд или в сервис\n"
            "  // аналитики — здесь просто выводим в консоль.\n"
            "  console.log(`[web-vitals] ${name}: ${value.toFixed(2)} (id=${id})`);\n"
            "}\n\n"
            "onLCP(sendToAnalytics);\n"
            "onINP(sendToAnalytics);\n"
            "onCLS(sendToAnalytics);\n\n"
            "// Улучшение LCP: если адрес самого крупного элемента (обложка\n"
            "// курса) известен заранее, предзагрузить его в index.html.\n"
            "// внутри public/index.html:\n"
            "//\n"
            "//   <link rel=\"preload\" as=\"image\" href=\"/hero-course-cover.jpg\" />\n\n"
            "// Улучшение INP: разбить тяжёлое вычисление на части (или\n"
            "// пометить его несрочным через useTransition — урок 7).\n"
            "function handleSortLargeList(items, setSorted) {\n"
            "  // НЕПРАВИЛЬНО: вся сортировка в одном синхронном блоке — INP хуже.\n"
            "  // const sorted = items.slice().sort(expensiveCompare);\n"
            "  // setSorted(sorted);\n\n"
            "  // ЛУЧШЕ: довериться собственному планировщику React,\n"
            "  // выполнить внутри startTransition.\n"
            "  React.startTransition(() => {\n"
            "    const sorted = items.slice().sort(expensiveCompare);\n"
            "    setSorted(sorted);\n"
            "  });\n"
            "}\n\n"
            "// Улучшение CLS: реальный паттерн из StudentCourses.js — skeleton\n"
            "// обязан быть того же размера, что и настоящая карточка.\n"
            "function CardSkeletonReal() {\n"
            "  return (\n"
            "    <div className=\"sc-skeleton\">\n"
            "      {/* Высота и ширина заданы в CSS такими же, как у настоящей\n"
            "          .sc-card — поэтому при приходе данных ничего не прыгает. */}\n"
            "      <div className=\"sc-skeleton-img\" />\n"
            "      <div className=\"sc-skeleton-body\">\n"
            "        <div className=\"sc-skeleton-line w70\" />\n"
            "        <div className=\"sc-skeleton-line w45\" />\n"
            "      </div>\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// Отдельное наблюдение за тремя этапами INP через PerformanceObserver\n"
            "// (web-vitals делает это автоматически внутри, но для диагностики\n"
            "// можно посмотреть и вручную).\n"
            "function observeInteractionBreakdown() {\n"
            "  const observer = new PerformanceObserver((list) => {\n"
            "    for (const entry of list.getEntries()) {\n"
            "      const inputDelay = entry.processingStart - entry.startTime;\n"
            "      const processingTime = entry.processingEnd - entry.processingStart;\n"
            "      const presentationDelay = entry.duration - inputDelay - processingTime;\n"
            "      console.log('[INP breakdown]', {\n"
            "        inputDelay: inputDelay.toFixed(1),\n"
            "        processingTime: processingTime.toFixed(1),\n"
            "        presentationDelay: presentationDelay.toFixed(1),\n"
            "      });\n"
            "    }\n"
            "  });\n"
            "  observer.observe({ type: 'event', durationThreshold: 40, buffered: true });\n"
            "  return () => observer.disconnect();\n"
            "}\n\n"
            "// Диагностика CLS: attribution-сборка web-vitals точно показывает,\n"
            "// какой элемент сдвинулся.\n"
            "import { onCLS } from 'web-vitals/attribution';\n\n"
            "onCLS((metric) => {\n"
            "  const culprit = metric.attribution?.largestShiftTarget;\n"
            "  console.log(`[CLS] значение=${metric.value.toFixed(3)}, причина=${culprit}`);\n"
            "});\n\n"
            "// Итог: три метрики закрывают три разных этапа — LCP про первую\n"
            "// отрисовку, INP про отклик на действие, CLS про визуальную\n"
            "// стабильность во время загрузки.\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "web-vitals'ni ulang va bitta CLS muammosini toping",
            "task_title_ru": "Подключите web-vitals и найдите одну проблему CLS",
            "task_description": (
                "Berilgan kichik React ilovasiga web-vitals kutubxonasini ulang "
                "(onLCP, onINP, onCLS) va natijalarni konsolga chiqaring. Ilovada "
                "atayin qo'yilgan kamida bitta CLS muammosi bor (masalan, "
                "width/height'i belgilanmagan rasm yoki skeleton'siz "
                "ma'lumot yuklash) — uni web-vitals/attribution orqali aniqlang va "
                "tuzating (rasm o'lchamini belgilash yoki mos o'lchamdagi skeleton "
                "qo'shish orqali). Tuzatishdan oldin va keyingi CLS qiymatini yozing."
            ),
            "task_description_ru": (
                "Подключите библиотеку web-vitals (onLCP, onINP, onCLS) к данному "
                "небольшому React-приложению и выводите результаты в консоль. В "
                "приложении специально заложена минимум одна проблема CLS "
                "(например, изображение без заданных width/height или загрузка "
                "данных без skeleton) — найдите её через web-vitals/attribution и "
                "исправьте (задав размер изображения или добавив skeleton "
                "нужного размера). Запишите значение CLS до и после исправления."
            ),
            "task_requirements": (
                "web-vitals uchta metrikani ham konsolga chiqarishi shart. Topilgan "
                "CLS muammosi va uning tuzatilishi, oldingi/keyingi CLS qiymati "
                "bilan yozma taqdim etilishi kerak."
            ),
            "task_requirements_ru": (
                "web-vitals обязан выводить в консоль все три метрики. Найденная "
                "проблема CLS и её исправление должны быть представлены письменно "
                "со значением CLS до и после."
            ),
            "task_technologies": "web-vitals, React DevTools",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: web-vitals kuzatuvi",
            "description": "LCP, INP va CLS metrikalarini o'lchab, konsolga chiqaruvchi to'liq namuna.",
            "sample_type": "code",
            "code_files": [
                {"filename": "reportWebVitals.js", "language": "javascript", "code": (
                    "import { onLCP, onINP, onCLS } from 'web-vitals';\n\n"
                    "export function reportWebVitals(onPerfEntry) {\n"
                    "  if (onPerfEntry && onPerfEntry instanceof Function) {\n"
                    "    onLCP(onPerfEntry);\n"
                    "    onINP(onPerfEntry);\n"
                    "    onCLS(onPerfEntry);\n"
                    "  }\n"
                    "}\n"
                )},
            ],
        },
        "exercises": [
            {
                "title": "Uchta Web Vitals metrikasi",
                "title_ru": "Три метрики Web Vitals",
                "description": "INP metrikasi asosan nimani o'lchaydi?",
                "description_ru": "Что в основном измеряет метрика INP?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Foydalanuvchi harakatidan keyin ekran qancha tezlikda javob berishini",
                    "Sahifadagi rasm fayllar sonini",
                    "Server javob berish vaqtini",
                    "CSS fayl hajmini",
                ],
                "options_ru": [
                    "Как быстро экран отвечает после действия пользователя",
                    "Количество файлов изображений на странице",
                    "Время ответа сервера",
                    "Размер CSS-файла",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"Interaction to Next Paint\" nomini so'zma-so'z o'qing.",
                "hint_ru": "Прочитайте название «Interaction to Next Paint» дословно.",
                "explanation": "INP foydalanuvchi harakati (klik, klaviatura) va ekranning keyingi javobi orasidagi vaqtni o'lchaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "CardSkeleton'ning vazifasi",
                "title_ru": "Роль CardSkeleton",
                "description": (
                    "Bo'shliqni to'ldiring: StudentCourses.js'dagi CardSkeleton "
                    "haqiqiy CourseCard bilan bir xil ___da bo'lishi kerak, aks holda "
                    "CLS oshadi."
                ),
                "description_ru": (
                    "Заполните пропуск: CardSkeleton в StudentCourses.js должен "
                    "быть того же ___, что и настоящий CourseCard, иначе CLS "
                    "увеличится."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "o'lcham",
                "correct_answers_ru": "размера",
                "hint": "Darsda \"balandlik va kenglik\" haqida gapirilgan.",
                "hint_ru": "В уроке говорится о «высоте и ширине».",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Metrika va sahifa bosqichi",
                "title_ru": "Метрика и этап страницы",
                "description": "Sahifa yuklanishi davomida metrikalar o'lchanadigan tartibni joylashtiring.",
                "description_ru": "Расставьте по порядку этапы загрузки страницы, на которых измеряются метрики.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Bo'sh HTML keladi (potentsial CLS manbai)",
                    "JS yuklanadi va React render qiladi (LCP o'lchanadi)",
                    "Foydalanuvchi birinchi marta bosadi (INP o'lchanadi)",
                    "web-vitals kutubxonasi natijalarni analytics'ga yuboradi",
                ],
                "drag_items_ru": [
                    "Приходит пустой HTML (потенциальный источник CLS)",
                    "Загружается JS и React рендерит (измеряется LCP)",
                    "Пользователь кликает впервые (измеряется INP)",
                    "Библиотека web-vitals отправляет результаты в аналитику",
                ],
                "correct_order": [
                    "Bo'sh HTML keladi (potentsial CLS manbai)",
                    "JS yuklanadi va React render qiladi (LCP o'lchanadi)",
                    "Foydalanuvchi birinchi marta bosadi (INP o'lchanadi)",
                    "web-vitals kutubxonasi natijalarni analytics'ga yuboradi",
                ],
                "hint": "Sahifa hayoti HTML kelishidan boshlanadi, hisobot yuborish bilan tugaydi.",
                "hint_ru": "Жизнь страницы начинается с прихода HTML, заканчивается отправкой отчёта.",
                "difficulty_level": "Medium",
                "points": 10,
            },
        ],
    },
    {
        "order": 11,
        "title": "11-Umumiy anti-patternlar: sekin render'larning haqiqiy sabablari",
        "title_ru": "11-Общие антипаттерны: реальные причины медленного рендера",
        "points_reward": 15,
        "text_content": (
            "<h3>Bu dars — kursning \"amaliy nazorat ro'yxati\"</h3>"
            "<p>1-10-darslarda har biri alohida chuqur ko'rilgan mavzular bor edi. "
            "Bu darsda esa kod ko'rib chiqishda (code review) ENG KO'P uchraydigan, "
            "kichik lekin ko'p uchraydigan naqshlarni bitta ro'yxatga jamlaymiz — "
            "har biri ushbu platformaning haqiqiy kodidan olingan haqiqiy misol "
            "bilan.</p>"
            "<h3>1. Inline obyekt/massiv literal — <code>style={{{{...}}}}</code></h3>"
            "<p>Bu — ushbu platformaning haqiqiy kodi: <code>frontend/src/views/"
            "student/projects/ProjectCard.js</code>da <code>&lt;div "
            "style={{{{ display: 'flex', gap: '6px', alignItems: 'center' "
            "}}}}&gt;</code> yozilgan. Har render'da bu — YANGI obyekt. Agar bu "
            "<code>div</code> <code>React.memo</code> qilingan komponentga prop "
            "sifatida uzatilsa, memo befoyda bo'lardi (3-darsda ko'rganimiz). "
            "Ushbu aniq holatda bu <code>div</code> memo'lanmagan komponent ichida "
            "bo'lgani uchun HOZIRCHA muammo emas — lekin bu naqsh xuddi shu faylda "
            "boshqa joyda takrorlansa yoki memo qo'shilsa, muammo kelib chiqadi. "
            "Yechim (agar kerak bo'lsa): obyektni komponent tashqarisiga chiqarish "
            "yoki CSS klassiga o'tkazish.</p>"
            "<h3>2. Index asosidagi key — <code>key={{index}}</code></h3>"
            "<p>Xuddi shu faylning 41-qatorida: <code>{{(techStack || []).map((tech, "
            "index) =&gt; (&lt;span key={{index}} ...&gt;))}}</code>. 1-darsda "
            "ko'rganimizdek, index-key ro'yxat QAYTA TARTIBLANSA yoki elementlar "
            "o'rtadan qo'shilsa/o'chirilsa xato natijalarga olib kelishi mumkin "
            "(React eski DOM state'ini noto'g'ri elementga bog'lab qo'yishi). "
            "Lekin bu ANIQ holatda — texnologiyalar ro'yxati (masalan, [\"React\", "
            "\"Redux\"]) — har bir loyiha uchun STATIK, hech qachon qayta "
            "tartiblanmaydi va ichida interaktiv holat (masalan, checkbox) yo'q. "
            "Shuning uchun bu — halol, past xavfli holat, ADABIY xato emas. Qoida: "
            "index-key faqat ro'yxat statik va elementlar o'z holatiga ega "
            "bo'lmaganda xavfsiz.</p>"
            "<h3>3. Har render'da yangi inline funksiya</h3>"
            "<p>2-3-darslarda batafsil ko'rgan <code>onOpen={{() =&gt; "
            "goToCourse(course)}}</code> naqshi — bu keng tarqalgan, ammo "
            "<code>React.memo</code> bilan birga bo'lmasa, umuman zararsiz "
            "(memo yo'q joyda inline funksiya narxi arzimaydi). Xato — bu naqshni "
            "HAR joyda \"yomon\" deb, hamma joyga <code>useCallback</code> "
            "qo'shishdir (3-darsdagi \"qachon foydalanmaslik\" mavzusi).</p>"
            "<h3>4. Keraksiz state ko'tarish (lifting state up)</h3>"
            "<p>State'ni kerak bo'lmagan darajada yuqoriga ko'tarish — masalan, "
            "faqat bitta kichik komponentga tegishli \"is this dropdown open\" "
            "degan state'ni butun sahifa darajasidagi komponentga qo'yish — "
            "2-darsda ko'rgan kaskad muammosini SUN'IY ravishda kattalashtiradi: "
            "endi bitta dropdown ochilishi BUTUN SAHIFANI qayta render qiladi, "
            "faqat o'sha dropdown'ni emas. To'g'ri yondashuv: state'ni unga eng "
            "yaqin, uni ishlatadigan komponentda saqlash — faqat bir nechta "
            "komponent orasida haqiqatan bo'lishilishi kerak bo'lgandagina "
            "yuqoriga ko'tarish.</p>"
            "<h3>5. Komponentni boshqa komponent ICHIDA aniqlash</h3>"
            "<p>Bu — yuqoridagi to'rttadan farqli o'laroq, HAR DOIM zararli "
            "anti-pattern: <code>function Parent() {{ function Child() {{ ... }} "
            "return &lt;Child /&gt;; }}</code> — <code>Child</code> funksiyasi "
            "<code>Parent</code>ning HAR render'ida QAYTA E'LON QILINADI, demak u "
            "har safar React uchun \"YANGI komponent turi\" hisoblanadi (funksiya "
            "reference'i har doim boshqacha). React buni ko'rganda eski "
            "<code>Child</code>ni butunlay OLIB TASHLAYDI va yangisini SIFATDAN "
            "BOSHLAB yaratadi — bu shunchaki qayta render emas, TO'LIQ QAYTA "
            "MONTAJ (unmount + mount), <code>Child</code>ning barcha ICHKI state'i "
            "(masalan, input'ga yozilgan matn) YO'QOLADI. Yechim — har doim: "
            "komponentlarni boshqa komponent funksiyasi ICHIDA emas, modul "
            "darajasida (fayl boshida) e'lon qilish.</p>"
            "<h3>Diagramma: beshta anti-pattern va ularning haqiqiy xavfi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Inline style/obyekt\"] -->|\"faqat memo bilan birga xavfli\"| A1[\"3-dars\"]\n"
            "  B[\"Index-key\"] -->|\"faqat qayta tartiblansa xavfli\"| B1[\"1-dars\"]\n"
            "  C[\"Inline funksiya\"] -->|\"faqat memo bilan birga xavfli\"| C1[\"3-dars\"]\n"
            "  D[\"Keraksiz state ko'tarish\"] -->|\"har doim kaskadni kattalashtiradi\"| D1[\"2-dars\"]\n"
            "  E[\"Komponentni ichida e'lon qilish\"] -->|\"har doim state'ni yo'qotadi\"| E1[\"hozirgi bo'lim\"]\n"
            "</pre>"
            "<p>Diagramma shuni ko'rsatadi: bu naqshlarning aksariyati KONTEKSTGA "
            "bog'liq xavf — <code>D</code> va <code>E</code> esa har doim, "
            "kontekstdan qat'i nazar, zarar keltiradi (D — kaskadni kattalashtirib, "
            "E — butunlay state'ni yo'qotib).</p>"
        ),
        "text_content_ru": (
            "<h3>Этот урок — «практический чек-лист» курса</h3>"
            "<p>В уроках 1-10 каждый раз глубоко разбиралась отдельная тема. В "
            "этом уроке мы соберём в один список САМЫЕ частые, небольшие, но часто "
            "встречающиеся в код-ревью паттерны — каждый с реальным примером из "
            "кода этой платформы.</p>"
            "<h3>1. Инлайн-объект/массив-литерал — <code>style={{{{...}}}}</code></h3>"
            "<p>Это настоящий код этой платформы: в <code>frontend/src/views/"
            "student/projects/ProjectCard.js</code> написано <code>&lt;div "
            "style={{{{ display: 'flex', gap: '6px', alignItems: 'center' "
            "}}}}&gt;</code>. На каждом рендере это НОВЫЙ объект. Если бы этот "
            "<code>div</code> передавался как prop в компонент с "
            "<code>React.memo</code>, memo не дал бы пользы (как в уроке 3). В "
            "этом конкретном случае этот <code>div</code> находится внутри "
            "немемоизированного компонента, так что ПОКА это не проблема — но "
            "если этот паттерн повторится в другом месте того же файла или "
            "добавится memo, проблема появится. Решение (если понадобится): "
            "вынести объект за пределы компонента или перевести в CSS-класс.</p>"
            "<h3>2. Ключ на основе index — <code>key={{index}}</code></h3>"
            "<p>В том же файле, строка 41: <code>{{(techStack || []).map((tech, "
            "index) =&gt; (&lt;span key={{index}} ...&gt;))}}</code>. Как мы "
            "видели в уроке 1, index-key может привести к неверным результатам, "
            "ЕСЛИ список ПЕРЕУПОРЯДОЧИВАЕТСЯ или элементы добавляются/удаляются "
            "посередине (React неверно свяжет старое DOM-состояние с другим "
            "элементом). Но в ЭТОМ КОНКРЕТНОМ случае — список технологий "
            "(например, [\"React\", \"Redux\"]) — он СТАТИЧЕН для каждого проекта, "
            "никогда не переупорядочивается и не содержит внутреннего "
            "интерактивного состояния (например, чекбоксов). Поэтому это честный, "
            "низкорисковый случай, а не буквальная ошибка. Правило: index-key "
            "безопасен только когда список статичен и элементы не имеют "
            "собственного состояния.</p>"
            "<h3>3. Новая инлайн-функция на каждом рендере</h3>"
            "<p>Подробно разобранный в уроках 2-3 паттерн <code>onOpen={{() =&gt; "
            "goToCourse(course)}}</code> — распространён, но совершенно безобиден "
            "без <code>React.memo</code> (там, где memo нет, стоимость "
            "инлайн-функции ничтожна). Ошибка — считать этот паттерн «плохим» "
            "ВЕЗДЕ и добавлять <code>useCallback</code> повсюду (тема «когда не "
            "стоит» из урока 3).</p>"
            "<h3>4. Излишний подъём state (lifting state up)</h3>"
            "<p>Поднятие state выше необходимого уровня — например, состояние "
            "«открыт ли этот dropdown», относящееся только к одному маленькому "
            "компоненту, помещённое в компонент уровня всей страницы — ИСКУССТВЕННО "
            "усиливает проблему каскада из урока 2: теперь открытие одного "
            "dropdown перерендеривает ВСЮ СТРАНИЦУ, а не только этот dropdown. "
            "Правильный подход: хранить state как можно ближе к компоненту, "
            "который его использует — поднимать выше только когда он реально "
            "должен быть общим между несколькими компонентами.</p>"
            "<h3>5. Определение компонента ВНУТРИ другого компонента</h3>"
            "<p>В отличие от четырёх предыдущих, это ВСЕГДА вредный антипаттерн: "
            "<code>function Parent() {{ function Child() {{ ... }} return "
            "&lt;Child /&gt;; }}</code> — функция <code>Child</code> "
            "ОБЪЯВЛЯЕТСЯ ЗАНОВО на КАЖДОМ рендере <code>Parent</code>, а значит "
            "каждый раз React считает её «НОВЫМ типом компонента» (ссылка функции "
            "всегда другая). Увидев это, React полностью УДАЛЯЕТ старый "
            "<code>Child</code> и создаёт новый С НУЛЯ — это не просто ре-рендер, "
            "а ПОЛНЫЙ ПЕРЕМОНТАЖ (unmount + mount), весь ВНУТРЕННИЙ state "
            "<code>Child</code> (например, введённый в поле текст) ТЕРЯЕТСЯ. "
            "Решение — всегда: объявлять компоненты на уровне модуля (в начале "
            "файла), а не ВНУТРИ функции другого компонента.</p>"
            "<h3>Диаграмма: пять антипаттернов и их реальный риск</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Инлайн style/объект\"] -->|\"опасно только с memo\"| A1[\"Урок 3\"]\n"
            "  B[\"Index-key\"] -->|\"опасно только при переупорядочивании\"| B1[\"Урок 1\"]\n"
            "  C[\"Инлайн-функция\"] -->|\"опасно только с memo\"| C1[\"Урок 3\"]\n"
            "  D[\"Излишний подъём state\"] -->|\"всегда усиливает каскад\"| D1[\"Урок 2\"]\n"
            "  E[\"Компонент внутри компонента\"] -->|\"всегда теряет state\"| E1[\"этот раздел\"]\n"
            "</pre>"
            "<p>Диаграмма показывает: большинство этих паттернов — риск, "
            "зависящий от контекста, а <code>D</code> и <code>E</code> вредят "
            "всегда, независимо от контекста (D — усиливая каскад, E — полностью "
            "теряя state).</p>"
        ),
        "code_content": (
            "// ProjectCard.js'ning haqiqiy naqshi (soddalashtirilgan iqtibos):\n"
            "function ProjectCard({ title, techStack, grade, points, onDetails }) {\n"
            "  return (\n"
            "    <div className=\"project-card\">\n"
            "      <div className=\"project-header\">\n"
            "        {/* 1-anti-pattern: inline style obyekti — memo bo'lmagan\n"
            "            joyda zararsiz, memo bilan birga bo'lsa muammo bo'ladi. */}\n"
            "        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>\n"
            "          {grade && <span className={`grade-badge grade-${grade}`}>{grade}</span>}\n"
            "          <span className=\"points-badge\">+{points ?? 0} pts</span>\n"
            "        </div>\n"
            "      </div>\n"
            "      <h3>{title}</h3>\n"
            "      <div className=\"tech-stack\">\n"
            "        {/* 2-anti-pattern: index-key — LEKIN techStack statik va\n"
            "            qayta tartiblanmaydi, shuning uchun bu holatda XAVFSIZ. */}\n"
            "        {(techStack || []).map((tech, index) => (\n"
            "          <span key={index} className=\"tech-tag\">{tech}</span>\n"
            "        ))}\n"
            "      </div>\n"
            "      <button onClick={onDetails}>Batafsil</button>\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// 3-anti-pattern namunasi: inline funksiya (o'zi zararsiz, memo bilan\n"
            "// birga bo'lsagina muammo).\n"
            "function ProjectList({ projects, openDetails }) {\n"
            "  return projects.map((p) => (\n"
            "    <ProjectCard key={p.id} {...p} onDetails={() => openDetails(p.id)} />\n"
            "  ));\n"
            "}\n\n"
            "// 4-anti-pattern: keraksiz state ko'tarish — NOTO'G'RI variant.\n"
            "function PageWithLiftedState() {\n"
            "  // dropdownOpen faqat BITTA kichik komponentga tegishli, lekin\n"
            "  // sahifa darajasida saqlangan — uni ochish BUTUN sahifani\n"
            "  // qayta render qiladi.\n"
            "  const [dropdownOpen, setDropdownOpen] = React.useState(false);\n"
            "  return (\n"
            "    <div>\n"
            "      <HeavyUnrelatedSection />\n"
            "      <SmallDropdown open={dropdownOpen} onToggle={() => setDropdownOpen((o) => !o)} />\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// TO'G'RI variant: state SmallDropdown'ning o'zida — sahifa\n"
            "// qolgan qismi umuman qayta render bo'lmaydi.\n"
            "function SmallDropdownSelfContained() {\n"
            "  const [open, setOpen] = React.useState(false);\n"
            "  return (\n"
            "    <div>\n"
            "      <button onClick={() => setOpen((o) => !o)}>Menyu</button>\n"
            "      {open && <ul><li>Variant 1</li><li>Variant 2</li></ul>}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// 5-anti-pattern: komponentni boshqa komponent ICHIDA e'lon qilish —\n"
            "// bu HAR DOIM zararli, kontekstdan qat'i nazar.\n"
            "function SearchPanelBad() {\n"
            "  const [query, setQuery] = React.useState('');\n\n"
            "  // NOTO'G'RI: Field har render'da QAYTA E'LON QILINADI — React uni\n"
            "  // \"yangi komponent turi\" deb hisoblaydi va HAR safar butunlay\n"
            "  // qayta montaj qiladi, ichidagi input matni yo'qoladi.\n"
            "  function Field({ label, value, onChange }) {\n"
            "    return (\n"
            "      <label>\n"
            "        {label}\n"
            "        <input value={value} onChange={onChange} />\n"
            "      </label>\n"
            "    );\n"
            "  }\n\n"
            "  return <Field label=\"Qidirish\" value={query} onChange={(e) => setQuery(e.target.value)} />;\n"
            "}\n\n"
            "// TO'G'RI: Field modul darajasida, faylning boshida, bir marta\n"
            "// e'lon qilinadi — reference doim bir xil, state saqlanib qoladi.\n"
            "function Field({ label, value, onChange }) {\n"
            "  return (\n"
            "    <label>\n"
            "      {label}\n"
            "      <input value={value} onChange={onChange} />\n"
            "    </label>\n"
            "  );\n"
            "}\n"
            "function SearchPanelGood() {\n"
            "  const [query, setQuery] = React.useState('');\n"
            "  return <Field label=\"Qidirish\" value={query} onChange={(e) => setQuery(e.target.value)} />;\n"
            "}\n"
        ),
        "code_content_ru": (
            "// Реальный (упрощённый) паттерн ProjectCard.js:\n"
            "function ProjectCard({ title, techStack, grade, points, onDetails }) {\n"
            "  return (\n"
            "    <div className=\"project-card\">\n"
            "      <div className=\"project-header\">\n"
            "        {/* Антипаттерн 1: инлайн-объект style — безобиден там, где\n"
            "            нет memo, станет проблемой вместе с memo. */}\n"
            "        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>\n"
            "          {grade && <span className={`grade-badge grade-${grade}`}>{grade}</span>}\n"
            "          <span className=\"points-badge\">+{points ?? 0} pts</span>\n"
            "        </div>\n"
            "      </div>\n"
            "      <h3>{title}</h3>\n"
            "      <div className=\"tech-stack\">\n"
            "        {/* Антипаттерн 2: index-key — НО techStack статичен и не\n"
            "            переупорядочивается, поэтому в этом случае БЕЗОПАСНО. */}\n"
            "        {(techStack || []).map((tech, index) => (\n"
            "          <span key={index} className=\"tech-tag\">{tech}</span>\n"
            "        ))}\n"
            "      </div>\n"
            "      <button onClick={onDetails}>Подробнее</button>\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// Пример антипаттерна 3: инлайн-функция (сама по себе безобидна,\n"
            "// проблема только вместе с memo).\n"
            "function ProjectList({ projects, openDetails }) {\n"
            "  return projects.map((p) => (\n"
            "    <ProjectCard key={p.id} {...p} onDetails={() => openDetails(p.id)} />\n"
            "  ));\n"
            "}\n\n"
            "// Антипаттерн 4: излишний подъём state — НЕПРАВИЛЬНЫЙ вариант.\n"
            "function PageWithLiftedState() {\n"
            "  // dropdownOpen относится только к ОДНОМУ маленькому компоненту,\n"
            "  // но хранится на уровне страницы — его открытие перерендеривает\n"
            "  // ВСЮ страницу.\n"
            "  const [dropdownOpen, setDropdownOpen] = React.useState(false);\n"
            "  return (\n"
            "    <div>\n"
            "      <HeavyUnrelatedSection />\n"
            "      <SmallDropdown open={dropdownOpen} onToggle={() => setDropdownOpen((o) => !o)} />\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// ПРАВИЛЬНЫЙ вариант: state внутри самого SmallDropdown — остальная\n"
            "// часть страницы вообще не перерендеривается.\n"
            "function SmallDropdownSelfContained() {\n"
            "  const [open, setOpen] = React.useState(false);\n"
            "  return (\n"
            "    <div>\n"
            "      <button onClick={() => setOpen((o) => !o)}>Меню</button>\n"
            "      {open && <ul><li>Вариант 1</li><li>Вариант 2</li></ul>}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// Антипаттерн 5: объявление компонента ВНУТРИ другого компонента —\n"
            "// это ВСЕГДА вредно, независимо от контекста.\n"
            "function SearchPanelBad() {\n"
            "  const [query, setQuery] = React.useState('');\n\n"
            "  // НЕПРАВИЛЬНО: Field ОБЪЯВЛЯЕТСЯ ЗАНОВО на каждом рендере — React\n"
            "  // считает её «новым типом компонента» и КАЖДЫЙ раз полностью\n"
            "  // перемонтирует, текст внутри input теряется.\n"
            "  function Field({ label, value, onChange }) {\n"
            "    return (\n"
            "      <label>\n"
            "        {label}\n"
            "        <input value={value} onChange={onChange} />\n"
            "      </label>\n"
            "    );\n"
            "  }\n\n"
            "  return <Field label=\"Поиск\" value={query} onChange={(e) => setQuery(e.target.value)} />;\n"
            "}\n\n"
            "// ПРАВИЛЬНО: Field объявлена на уровне модуля, в начале файла, один\n"
            "// раз — ссылка всегда одна и та же, state сохраняется.\n"
            "function Field({ label, value, onChange }) {\n"
            "  return (\n"
            "    <label>\n"
            "      {label}\n"
            "      <input value={value} onChange={onChange} />\n"
            "    </label>\n"
            "  );\n"
            "}\n"
            "function SearchPanelGood() {\n"
            "  const [query, setQuery] = React.useState('');\n"
            "  return <Field label=\"Поиск\" value={query} onChange={(e) => setQuery(e.target.value)} />;\n"
            "}\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Berilgan komponentdagi anti-patternlarni toping va xavf darajasi bo'yicha tuzating",
            "task_title_ru": "Найдите антипаттерны в данном компоненте и исправьте по уровню риска",
            "task_description": (
                "Sizga kamida uchta anti-pattern (masalan, komponentni boshqa "
                "komponent ichida e'lon qilish, keraksiz state ko'tarish va "
                "index-key) atayin qo'yilgan kichik komponent beriladi. Har bir "
                "anti-patternni toping va uning XAVF DARAJASINI yozing (har doim "
                "xavfli — masalan komponentni ichida e'lon qilish, yoki faqat "
                "kontekstga bog'liq — masalan index-key). Faqat HAQIQATAN xavfli "
                "bo'lganlarini tuzating, past xavfli holatlarni esa nima uchun "
                "hozircha xavfsiz ekanini asoslab qoldiring."
            ),
            "task_description_ru": (
                "Вам дан небольшой компонент со специально заложенными минимум "
                "тремя антипаттернами (например, объявление компонента внутри "
                "другого компонента, излишний подъём state и index-key). Найдите "
                "каждый антипаттерн и запишите его УРОВЕНЬ РИСКА (всегда опасно — "
                "например объявление компонента внутри, или риск зависит от "
                "контекста — например index-key). Исправьте только те, что "
                "РЕАЛЬНО опасны, а низкорисковые случаи оставьте, обосновав "
                "письменно, почему они пока безопасны."
            ),
            "task_requirements": (
                "Kamida uchta anti-pattern topilgan va xavf darajasi bo'yicha "
                "tasniflangan bo'lishi shart. Har doim xavfli deb topilganlari "
                "tuzatilgan, past xavflilar esa asoslab qoldirilgan bo'lishi kerak."
            ),
            "task_requirements_ru": (
                "Обязательно найти минимум три антипаттерна и классифицировать по "
                "уровню риска. Всегда опасные должны быть исправлены, "
                "низкорисковые — оставлены с письменным обоснованием."
            ),
            "task_technologies": "React",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: beshta anti-pattern va tuzatilgan variantlari",
            "description": "ProjectCard.js'ga asoslangan anti-pattern misollari va ularning to'g'ri (yoki halol xavfsiz) variantlari.",
            "sample_type": "code",
            "code_files": [
                {"filename": "AntiPatterns.jsx", "language": "jsx", "code": (
                    "function ProjectCard({ title, techStack }) {\n"
                    "  return (\n"
                    "    <div>\n"
                    "      <h3>{title}</h3>\n"
                    "      {techStack.map((t, i) => <span key={i}>{t}</span>)}\n"
                    "    </div>\n"
                    "  );\n"
                    "}\n\n"
                    "function SmallDropdownSelfContained() {\n"
                    "  const [open, setOpen] = React.useState(false);\n"
                    "  return (\n"
                    "    <div>\n"
                    "      <button onClick={() => setOpen((o) => !o)}>Menu</button>\n"
                    "      {open && <ul><li>Option 1</li></ul>}\n"
                    "    </div>\n"
                    "  );\n"
                    "}\n"
                )},
            ],
        },
        "exercises": [
            {
                "title": "Index-key qachon xavfsiz",
                "title_ru": "Когда index-key безопасен",
                "description": "ProjectCard.js'dagi key={index} nima uchun bu holatda past xavfli deb hisoblanadi?",
                "description_ru": "Почему key={index} в ProjectCard.js в данном случае считается низкорисковым?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Ro'yxat statik, qayta tartiblanmaydi va elementlar o'z holatiga ega emas",
                    "React index-key'larni umuman tekshirmaydi",
                    "ProjectCard React.memo bilan o'ralgan",
                    "Ro'yxat har doim bo'sh bo'ladi",
                ],
                "options_ru": [
                    "Список статичен, не переупорядочивается, элементы не имеют своего состояния",
                    "React вообще не проверяет index-key",
                    "ProjectCard обёрнут в React.memo",
                    "Список всегда пустой",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "1-darsdagi index-key haqidagi qoidani eslang.",
                "hint_ru": "Вспомните правило про index-key из урока 1.",
                "explanation": "Index-key faqat ro'yxat qayta tartiblanganda yoki elementlar o'rtadan o'zgarganda muammoli — statik ro'yxatda xavfsiz.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Har doim xavfli anti-pattern",
                "title_ru": "Всегда опасный антипаттерн",
                "description": (
                    "Bo'shliqni to'ldiring: beshta anti-pattern orasida faqat "
                    "keraksiz ___ ko'tarish kontekstdan qat'i nazar har doim "
                    "kaskadni kattalashtiradi (komponentni ichida e'lon qilish esa "
                    "boshqacha — u kaskad emas, state'ni butunlay yo'qotadi)."
                ),
                "description_ru": (
                    "Заполните пропуск: среди пяти антипаттернов только "
                    "излишний подъём ___ всегда, независимо от контекста, "
                    "усиливает каскад (объявление компонента внутри — другое дело, "
                    "оно не про каскад, а про полную потерю state)."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "state",
                "hint": "Darsdagi 4-bandni eslang.",
                "hint_ru": "Вспомните пункт 4 в уроке.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Anti-patternlarni xavf darajasiga qarab tartiblash",
                "title_ru": "Расставьте антипаттерны по уровню риска",
                "description": "Anti-patternlarni ENG kam xavflidan ENG ko'p xavfligacha (kontekstdan qat'i nazar) tartiblang.",
                "description_ru": "Расставьте антипаттерны от НАИМЕНЕЕ рискованного к НАИБОЛЕЕ рискованному (независимо от контекста).",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Statik ro'yxatda index-key",
                    "Memo'siz inline funksiya/obyekt",
                    "Memo bilan birga inline funksiya/obyekt",
                    "Keraksiz state ko'tarish",
                    "Komponentni boshqa komponent ichida e'lon qilish",
                ],
                "drag_items_ru": [
                    "Index-key в статичном списке",
                    "Инлайн-функция/объект без memo",
                    "Инлайн-функция/объект вместе с memo",
                    "Излишний подъём state",
                    "Объявление компонента внутри другого компонента",
                ],
                "correct_order": [
                    "Statik ro'yxatda index-key",
                    "Memo'siz inline funksiya/obyekt",
                    "Memo bilan birga inline funksiya/obyekt",
                    "Keraksiz state ko'tarish",
                    "Komponentni boshqa komponent ichida e'lon qilish",
                ],
                "hint": "Eng past xavf — statik holatlar, eng yuqori xavf — state'ni butunlay yo'qotadigani.",
                "hint_ru": "Наименьший риск — статичные случаи, наибольший — то, что полностью теряет state.",
                "difficulty_level": "Hard",
                "points": 15,
            },
        ],
    },
    {
        "order": 12,
        "title": "R2-Profiling workflow: sekin komponentni boshidan oxirigacha diagnostika qilish",
        "title_ru": "R2-Рабочий процесс профилирования: диагностика медленного компонента от начала до конца",
        "points_reward": 20,
        "text_content": (
            "<h3>Bu — sintez darsi, sof takrorlash emas</h3>"
            "<p>Bu dars R2 deb belgilangan, lekin u sof takrorlash emas — bu "
            "1-11-darslarda o'rgangan HAMMA narsani bitta REAL diagnostika "
            "jarayoniga birlashtiruvchi amaliy sintez. Shuning uchun matn va kod "
            "boshqa \"R\" darsi (R1) kabi qisqartirilmagan — bu yerda haqiqiy "
            "\"men sekin komponentni topib, tuzataman\" ishchi jarayonini "
            "boshidan oxirigacha ko'ramiz.</p>"
            "<h3>Haqiqiy misol: StudentTeamGame.js'dagi taymer</h3>"
            "<p>Bu — ushbu platformaning haqiqiy kodi: <code>frontend/src/views/"
            "student/teamgame/StudentTeamGame.js</code>ning 111-qatorida "
            "<code>setInterval(tick, 250)</code> — o'yin savoliga qolgan vaqtni "
            "sekundiga 4 marta yangilaydigan taymer bor. 1-darsda bu misolni "
            "\"savol\" sifatida qoldirgan edik: bu — muammomi? Endi to'liq "
            "diagnostika jarayonini qo'llaymiz.</p>"
            "<h3>1-qadam: Profiler'da yozib olish</h3>"
            "<p>React DevTools Profiler'da yozishni boshlaymiz, o'yin savoli "
            "ekranida bir necha soniya kutamiz (taymer bir necha marta "
            "\"tick\" qiladi), keyin to'xtatamiz. Flamegraph'da har 250ms'da "
            "commit paydo bo'lganini ko'ramiz.</p>"
            "<h3>2-qadam: \"nega bu komponent render bo'ldi\" savolini berish</h3>"
            "<p>Taymer ko'rsatuvchi komponentni bosamiz — \"hooks changed: 1\" "
            "(ya'ni <code>setTimeLeft</code> orqali state o'zgardi) ko'rinadi. Bu "
            "kutilgan: taymer state'i haqiqatan ham har 250ms'da o'zgaradi. Endi "
            "muhim savol: BU komponentdan TASHQARI, YANA nima qayta render "
            "bo'lyapti? Agar faqat kichik \"vaqt qoldi: N soniya\" matni render "
            "bo'lsa — bu arzimas. Agar butun savol kartasi, javob variantlari va "
            "boshqa UI ham har 250ms'da qayta render bo'lsa — bu 2-darsda "
            "ko'rgan re-render kaskadi muammosi: taymer state'i o'zining "
            "komponentida emas, YUQORIDA, umumiy ota komponentda saqlangan "
            "bo'lishi mumkin.</p>"
            "<h3>3-qadam: haqiqiy vaqtni tekshirish</h3>"
            "<p>\"Ranked\" ko'rinishda shu commit'ning <code>actualDuration</code>"
            "ini ko'ramiz. Agar bu bir necha millisekunddan kam bo'lsa (oddiy "
            "matn yangilanishi uchun odatiy holat), demak — HATTO kaskad bo'lsa "
            "ham, haqiqiy vaqt narxi arzimas, va bu real muammo EMAS (8-dars "
            "\"halol javob\" bo'limi bilan bir xil printsip: har qanday qayta "
            "render muammo emas). Agar vaqt sezilarli (10ms+) bo'lsa va bu "
            "qatorlar/soniyada takrorlansa, foydalanuvchi buni animatsiya "
            "\"tirjirashi\" sifatida sezishi mumkin.</p>"
            "<h3>4-qadam: sababga mos yechim tanlash</h3>"
            "<p>Agar diagnostika \"taymer state'i keraksiz yuqorida saqlangan\" "
            "degan xulosaga kelsa — yechim 11-darsdagi \"keraksiz state "
            "ko'tarish\" anti-patternini tuzatish: taymer state'ini faqat "
            "taymerni ko'rsatuvchi KICHIK komponentga tushirish. Agar sabab "
            "\"qo'shni komponentlar memo qilinmagan\" bo'lsa — 3-darsdagi "
            "<code>React.memo</code> + <code>useCallback</code> naqshini "
            "qo'llash. Agar sabab \"tick funksiyasining o'zi og'ir hisoblash "
            "qilyapti\" bo'lsa — bu hisoblashni soddalashtirish yoki "
            "7-darsdagi <code>useTransition</code>ni ko'rib chiqish.</p>"
            "<h3>5-qadam: qayta o'lchab tasdiqlash</h3>"
            "<p>Tuzatishdan keyin Profiler'da QAYTA yozib olamiz — endi faqat "
            "kutilgan komponent(lar) render bo'layotganini va "
            "<code>actualDuration</code> avvalgidan kam yoki bir xil ekanini "
            "tasdiqlaymiz. Agar yaxshilanish ko'rinmasa, demak diagnostika "
            "noto'g'ri edi — 1-qadamga qaytamiz, taxmin qilmaymiz.</p>"
            "<h3>Diagramma: to'liq diagnostika oqimi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"1. Profiler'da yozib olish\"] --> B[\"2. Nega render bo'ldi?\n"
            "(qo'shimcha keraksiz komponentlar bormi?)\"]\n"
            "  B --> C[\"3. actualDuration'ni tekshirish\n"
            "(haqiqatan sezilarlimi?)\"]\n"
            "  C -->|\"Arzimas\"| Z[\"Tuzatish shart emas\"]\n"
            "  C -->|\"Sezilarli\"| D[\"4. Sabab: state joylashuvi,\n"
            "memo yo'qligi yoki og'ir hisoblash\"]\n"
            "  D --> E[\"Mos texnika: state'ni tushirish,\n"
            "memo+useCallback yoki useTransition\"]\n"
            "  E --> F[\"5. Qayta o'lchab tasdiqlash\"]\n"
            "  F -->|\"Yaxshilanmadi\"| A\n"
            "  F -->|\"Tasdiqlandi\"| Z2[\"Tugallandi\"]\n"
            "</pre>"
            "<p>Diagramma — bu kursning har darsida takrorlangan \"avval o'lchang, "
            "keyin tuzating\" printsipining to'liq, amaliy versiyasi.</p>"
            "<h3>Agar birinchi taxmin noto'g'ri chiqsa</h3>"
            "<p>Halol stsenariy: 4-qadamda \"state joylashuvi muammosi\" deb "
            "taxmin qilib tuzatgan bo'lsangiz-u, 5-qadamda qayta o'lchash hech "
            "qanday farq ko'rsatmasa — bu diagnostikaning o'zi noto'g'ri "
            "bo'lganini bildiradi, kodning o'zi buzilganini emas. Bunday holatda "
            "to'g'ri javob — orqaga, 2-qadamga qaytib, \"nega render bo'ldi\" "
            "ma'lumotini yana diqqat bilan o'qish (masalan, aslida sabab Context "
            "qiymati o'zgarishi bo'lishi mumkin, 6-darsdagi kabi), aksincha "
            "boshqa, tasodifiy tuzatishni sinab ko'rish emas.</p>"
        ),
        "text_content_ru": (
            "<h3>Это урок синтеза, а не чистого повторения</h3>"
            "<p>Этот урок помечен как R2, но это не чистое повторение — это "
            "практический синтез, объединяющий ВСЁ изученное в уроках 1-11 в "
            "один РЕАЛЬНЫЙ процесс диагностики. Поэтому текст и код не сокращены, "
            "как в другом уроке «R» (R1) — здесь мы разберём настоящий рабочий "
            "процесс «нахожу медленный компонент и исправляю его» от начала до "
            "конца.</p>"
            "<h3>Реальный пример: таймер в StudentTeamGame.js</h3>"
            "<p>Это настоящий код этой платформы: в <code>frontend/src/views/"
            "student/teamgame/StudentTeamGame.js</code> на строке 111 есть "
            "<code>setInterval(tick, 250)</code> — таймер, обновляющий "
            "оставшееся время вопроса игры 4 раза в секунду. В уроке 1 мы "
            "оставили этот пример как «вопрос»: это проблема? Теперь применим "
            "полный процесс диагностики.</p>"
            "<h3>Шаг 1: запись в Profiler</h3>"
            "<p>Начинаем запись в React DevTools Profiler, ждём несколько секунд "
            "на экране вопроса игры (таймер несколько раз «тикает»), затем "
            "останавливаем. На flamegraph видим, что commit появляется каждые "
            "250мс.</p>"
            "<h3>Шаг 2: вопрос «почему этот компонент отрендерился»</h3>"
            "<p>Нажимаем на компонент, показывающий таймер — видим «hooks "
            "changed: 1» (то есть state изменился через <code>setTimeLeft</code>). "
            "Это ожидаемо: state таймера действительно меняется каждые 250мс. "
            "Теперь важный вопрос: ПОМИМО этого компонента, что ЕЩЁ "
            "перерендеривается? Если рендерится только маленький текст "
            "«осталось: N секунд» — это ничтожно. Если вся карточка вопроса, "
            "варианты ответов и остальной UI тоже перерендериваются каждые "
            "250мс — это проблема каскада ре-рендеров из урока 2: state таймера, "
            "возможно, хранится не в его собственном компоненте, а ВЫШЕ, в общем "
            "родительском компоненте.</p>"
            "<h3>Шаг 3: проверка реального времени</h3>"
            "<p>Смотрим <code>actualDuration</code> этого commit в виде "
            "«ranked». Если это меньше нескольких миллисекунд (обычное дело для "
            "простого обновления текста), значит — ДАЖЕ если каскад есть, "
            "реальная стоимость времени ничтожна, и это НЕ реальная проблема "
            "(тот же принцип, что и «честный ответ» из урока 8: не любой "
            "ре-рендер — проблема). Если время заметное (10мс+) и повторяется "
            "несколько раз в секунду, пользователь может ощутить это как "
            "«подёргивание» анимации.</p>"
            "<h3>Шаг 4: выбор решения под причину</h3>"
            "<p>Если диагностика приводит к выводу «state таймера излишне "
            "хранится выше» — решение из урока 11: исправить антипаттерн "
            "«излишний подъём state», опустив state таймера в МАЛЕНЬКИЙ "
            "компонент, показывающий только сам таймер. Если причина «соседние "
            "компоненты не мемоизированы» — применить паттерн "
            "<code>React.memo</code> + <code>useCallback</code> из урока 3. Если "
            "причина «сама функция tick выполняет тяжёлое вычисление» — "
            "упростить это вычисление или рассмотреть <code>useTransition</code> "
            "из урока 7.</p>"
            "<h3>Шаг 5: повторное измерение для подтверждения</h3>"
            "<p>После исправления СНОВА записываем в Profiler — теперь "
            "подтверждаем, что рендерится только ожидаемый компонент(ы), и "
            "<code>actualDuration</code> меньше или равен прежнему. Если "
            "улучшения не видно, значит диагностика была неверной — "
            "возвращаемся к шагу 1, не гадаем.</p>"
            "<h3>Диаграмма: полный поток диагностики</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"1. Запись в Profiler\"] --> B[\"2. Почему отрендерился?\n"
            "(есть ли лишние соседние компоненты?)\"]\n"
            "  B --> C[\"3. Проверка actualDuration\n"
            "(реально ли заметно?)\"]\n"
            "  C -->|\"Ничтожно\"| Z[\"Исправление не нужно\"]\n"
            "  C -->|\"Заметно\"| D[\"4. Причина: расположение state,\n"
            "отсутствие memo или тяжёлое вычисление\"]\n"
            "  D --> E[\"Подходящая техника: опустить state,\n"
            "memo+useCallback или useTransition\"]\n"
            "  E --> F[\"5. Повторное измерение для подтверждения\"]\n"
            "  F -->|\"Не улучшилось\"| A\n"
            "  F -->|\"Подтверждено\"| Z2[\"Завершено\"]\n"
            "</pre>"
            "<p>Диаграмма — это полная, практическая версия принципа «сначала "
            "измерь, потом исправляй», повторяющегося в каждом уроке этого "
            "курса.</p>"
            "<h3>Если первая догадка оказалась неверной</h3>"
            "<p>Честный сценарий: если на шаге 4 вы предположили «проблема в "
            "расположении state» и исправили это, а на шаге 5 повторное "
            "измерение не показывает никакой разницы — это значит, что "
            "диагностика была неверной, а не что сам код сломан. В таком случае "
            "правильный ответ — вернуться назад, к шагу 2, и снова внимательно "
            "прочитать данные «почему отрендерился» (например, реальная причина "
            "может быть в изменении значения Context, как в уроке 6), а не "
            "пробовать другое случайное исправление.</p>"
        ),
        "code_content": (
            "// StudentTeamGame.js'ning haqiqiy naqshi (soddalashtirilgan iqtibos):\n"
            "// taymer state'i 250ms'da bir marta yangilanadi.\n"
            "function QuestionTimerReal({ timeLimit }) {\n"
            "  const [timeLeft, setTimeLeft] = React.useState(timeLimit);\n\n"
            "  React.useEffect(() => {\n"
            "    const t = setInterval(() => {\n"
            "      setTimeLeft((prev) => Math.max(0, prev - 0.25));\n"
            "    }, 250);\n"
            "    return () => clearInterval(t);\n"
            "  }, []);\n\n"
            "  return <span className=\"timer\">{timeLeft.toFixed(1)}s</span>;\n"
            "}\n\n"
            "// DIAGNOSTIKA QILINGAN MUAMMO (faraziy): taymer state'i noto'g'ri\n"
            "// joyda — butun savol ekranini boshqaruvchi ota komponentda.\n"
            "function QuestionScreenBad({ question }) {\n"
            "  // NOTO'G'RI: timeLeft shu yerda, demak har 250ms'da BUTUN\n"
            "  // QuestionScreen (savol matni, javob variantlari, hammasi)\n"
            "  // qayta render bo'ladi.\n"
            "  const [timeLeft, setTimeLeft] = React.useState(question.time_limit);\n"
            "  React.useEffect(() => {\n"
            "    const t = setInterval(() => setTimeLeft((p) => Math.max(0, p - 0.25)), 250);\n"
            "    return () => clearInterval(t);\n"
            "  }, []);\n\n"
            "  return (\n"
            "    <div>\n"
            "      <h2>{question.text}</h2>\n"
            "      <span className=\"timer\">{timeLeft.toFixed(1)}s</span>\n"
            "      {question.options.map((opt) => <OptionButton key={opt.id} option={opt} />)}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// TUZATILGAN VARIANT: taymer state'i o'z KICHIK komponentiga\n"
            "// tushirilgan — endi har 250ms'da FAQAT QuestionTimer qayta render\n"
            "// bo'ladi, savol matni va javob variantlari — yo'q.\n"
            "const OptionButton = React.memo(function OptionButton({ option }) {\n"
            "  return <button>{option.text}</button>;\n"
            "});\n\n"
            "function QuestionScreenGood({ question }) {\n"
            "  return (\n"
            "    <div>\n"
            "      <h2>{question.text}</h2>\n"
            "      <QuestionTimerReal timeLimit={question.time_limit} />\n"
            "      {question.options.map((opt) => <OptionButton key={opt.id} option={opt} />)}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// Tasdiqlash uchun kichik yordamchi: Profiler onRender callback'i\n"
            "// orqali qaysi komponent qayta render bo'lganini avtomatik loglash.\n"
            "function logRenderedComponents(id, phase, actualDuration) {\n"
            "  if (actualDuration > 2) {\n"
            "    console.warn(`[diagnostika] ${id}: ${actualDuration.toFixed(2)}ms — tekshirish kerak`);\n"
            "  }\n"
            "}\n\n"
            "// Butun daraxtni <Profiler> bilan o'rab, chegaradan oshgan\n"
            "// komponentlarni avtomatik belgilash — katta ekranda qo'lda\n"
            "// tekshirishdan tezroq boshlanish nuqtasi beradi.\n"
            "function DiagnosticProfiler({ id, children, thresholdMs = 4 }) {\n"
            "  const handleRender = (profId, phase, actualDuration) => {\n"
            "    if (actualDuration > thresholdMs) {\n"
            "      console.warn(\n"
            "        `[diagnostika] ${profId} (${phase}): ${actualDuration.toFixed(2)}ms `\n"
            "        + `chegaradan (${thresholdMs}ms) oshdi`\n"
            "      );\n"
            "    }\n"
            "  };\n"
            "  return (\n"
            "    <React.Profiler id={id} onRender={handleRender}>\n"
            "      {children}\n"
            "    </React.Profiler>\n"
            "  );\n"
            "}\n\n"
            "// Foydalanish: shubhali qismni shu bilan o'rab, konsolni kuzatish.\n"
            "function QuestionScreenWithDiagnostics({ question }) {\n"
            "  return (\n"
            "    <DiagnosticProfiler id=\"QuestionScreen\">\n"
            "      <QuestionScreenGood question={question} />\n"
            "    </DiagnosticProfiler>\n"
            "  );\n"
            "}\n\n"
            "// Besh qadamning xulosasi: yozib olish, \"nega\" savoli, haqiqiy\n"
            "// vaqtni tekshirish, sababga mos texnika, qayta o'lchash — bu tsikl\n"
            "// kursning ISTALGAN komponentiga, faqat taymerga emas, qo'llanadi.\n"
        ),
        "code_content_ru": (
            "// Реальный (упрощённый) паттерн StudentTeamGame.js: state таймера\n"
            "// обновляется раз в 250мс.\n"
            "function QuestionTimerReal({ timeLimit }) {\n"
            "  const [timeLeft, setTimeLeft] = React.useState(timeLimit);\n\n"
            "  React.useEffect(() => {\n"
            "    const t = setInterval(() => {\n"
            "      setTimeLeft((prev) => Math.max(0, prev - 0.25));\n"
            "    }, 250);\n"
            "    return () => clearInterval(t);\n"
            "  }, []);\n\n"
            "  return <span className=\"timer\">{timeLeft.toFixed(1)}s</span>;\n"
            "}\n\n"
            "// ПРОДИАГНОСТИРОВАННАЯ ПРОБЛЕМА (гипотетическая): state таймера в\n"
            "// неправильном месте — в родительском компоненте, управляющем всем\n"
            "// экраном вопроса.\n"
            "function QuestionScreenBad({ question }) {\n"
            "  // НЕПРАВИЛЬНО: timeLeft здесь, значит каждые 250мс перерендерится\n"
            "  // ВЕСЬ QuestionScreen (текст вопроса, варианты ответов, всё).\n"
            "  const [timeLeft, setTimeLeft] = React.useState(question.time_limit);\n"
            "  React.useEffect(() => {\n"
            "    const t = setInterval(() => setTimeLeft((p) => Math.max(0, p - 0.25)), 250);\n"
            "    return () => clearInterval(t);\n"
            "  }, []);\n\n"
            "  return (\n"
            "    <div>\n"
            "      <h2>{question.text}</h2>\n"
            "      <span className=\"timer\">{timeLeft.toFixed(1)}s</span>\n"
            "      {question.options.map((opt) => <OptionButton key={opt.id} option={opt} />)}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// ИСПРАВЛЕННЫЙ ВАРИАНТ: state таймера опущен в собственный\n"
            "// МАЛЕНЬКИЙ компонент — теперь каждые 250мс перерендеривается\n"
            "// ТОЛЬКО QuestionTimer, текст вопроса и варианты — нет.\n"
            "const OptionButton = React.memo(function OptionButton({ option }) {\n"
            "  return <button>{option.text}</button>;\n"
            "});\n\n"
            "function QuestionScreenGood({ question }) {\n"
            "  return (\n"
            "    <div>\n"
            "      <h2>{question.text}</h2>\n"
            "      <QuestionTimerReal timeLimit={question.time_limit} />\n"
            "      {question.options.map((opt) => <OptionButton key={opt.id} option={opt} />)}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "// Небольшой помощник для подтверждения: автоматическое логирование\n"
            "// того, какой компонент перерендерился, через onRender Profiler.\n"
            "function logRenderedComponents(id, phase, actualDuration) {\n"
            "  if (actualDuration > 2) {\n"
            "    console.warn(`[диагностика] ${id}: ${actualDuration.toFixed(2)}мс — нужно проверить`);\n"
            "  }\n"
            "}\n\n"
            "// Оборачиваем всё дерево в <Profiler> и автоматически помечаем\n"
            "// компоненты, превысившие порог — быстрая отправная точка вместо\n"
            "// ручной проверки на большом экране.\n"
            "function DiagnosticProfiler({ id, children, thresholdMs = 4 }) {\n"
            "  const handleRender = (profId, phase, actualDuration) => {\n"
            "    if (actualDuration > thresholdMs) {\n"
            "      console.warn(\n"
            "        `[диагностика] ${profId} (${phase}): ${actualDuration.toFixed(2)}мс `\n"
            "        + `превысил порог (${thresholdMs}мс)`\n"
            "      );\n"
            "    }\n"
            "  };\n"
            "  return (\n"
            "    <React.Profiler id={id} onRender={handleRender}>\n"
            "      {children}\n"
            "    </React.Profiler>\n"
            "  );\n"
            "}\n\n"
            "// Использование: оборачиваем подозрительную часть и следим за\n"
            "// консолью.\n"
            "function QuestionScreenWithDiagnostics({ question }) {\n"
            "  return (\n"
            "    <DiagnosticProfiler id=\"QuestionScreen\">\n"
            "      <QuestionScreenGood question={question} />\n"
            "    </DiagnosticProfiler>\n"
            "  );\n"
            "}\n\n"
            "// Итог пяти шагов: запись, вопрос «почему», проверка реального\n"
            "// времени, техника под причину, повторное измерение — этот цикл\n"
            "// применим к ЛЮБОМУ компоненту этого курса, не только к таймеру.\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "Sekin komponentni diagnostika qiling va tuzating",
            "task_title_ru": "Продиагностируйте и исправьте медленный компонент",
            "task_description": (
                "QuestionScreenBad komponentini (yuqoridagi kod) diagnostika qiling: "
                "Profiler'da yozib oling, \"nega render bo'ldi\" savolini bering, va "
                "QuestionScreenGood'dagi kabi taymer state'ini alohida komponentga "
                "tushiring hamda OptionButton'ni React.memo bilan o'rang. Diagnostika "
                "qadamlarini va topilgan sababni qisqacha yozing."
            ),
            "task_description_ru": (
                "Продиагностируйте компонент QuestionScreenBad (код выше): запишите "
                "в Profiler, задайте вопрос «почему отрендерился», и опустите state "
                "таймера в отдельный компонент, а также оберните OptionButton в "
                "React.memo, как в QuestionScreenGood. Кратко опишите шаги "
                "диагностики и найденную причину."
            ),
            "task_requirements": (
                "Taymer state'i alohida komponentda bo'lishi shart. OptionButton "
                "memo bilan o'ralgan bo'lishi kerak. Diagnostika qadamlari (Profiler "
                "yozuvi, sabab, tuzatish, qayta o'lchash) yozma tavsiflanishi shart."
            ),
            "task_requirements_ru": (
                "State таймера обязан быть в отдельном компоненте. OptionButton "
                "должен быть обёрнут в memo. Шаги диагностики (запись Profiler, "
                "причина, исправление, повторное измерение) должны быть описаны "
                "письменно."
            ),
            "task_technologies": "React, React DevTools Profiler, React.memo",
            "task_deadline_days": 7,
        },
        "sample": {
            "title": "Namuna: taymer diagnostikasi va tuzatilgan versiya",
            "description": "StudentTeamGame.js'ga asoslangan taymer komponentini diagnostika qilish va tuzatishning to'liq namunasi.",
            "sample_type": "code",
            "code_files": [
                {"filename": "QuestionTimerFixed.jsx", "language": "jsx", "code": (
                    "import { memo, useState, useEffect } from 'react';\n\n"
                    "function QuestionTimer({ timeLimit }) {\n"
                    "  const [timeLeft, setTimeLeft] = useState(timeLimit);\n"
                    "  useEffect(() => {\n"
                    "    const t = setInterval(() => setTimeLeft((p) => Math.max(0, p - 0.25)), 250);\n"
                    "    return () => clearInterval(t);\n"
                    "  }, []);\n"
                    "  return <span>{timeLeft.toFixed(1)}s</span>;\n"
                    "}\n\n"
                    "const OptionButton = memo(function OptionButton({ option }) {\n"
                    "  return <button>{option.text}</button>;\n"
                    "});\n\n"
                    "export default function QuestionScreen({ question }) {\n"
                    "  return (\n"
                    "    <div>\n"
                    "      <h2>{question.text}</h2>\n"
                    "      <QuestionTimer timeLimit={question.time_limit} />\n"
                    "      {question.options.map((o) => <OptionButton key={o.id} option={o} />)}\n"
                    "    </div>\n"
                    "  );\n"
                    "}\n"
                )},
            ],
        },
        "exercises": [
            {
                "title": "Diagnostikaning birinchi qadami",
                "title_ru": "Первый шаг диагностики",
                "description": "Sekin komponentni diagnostika qilishning ENG BIRINCHI qadami nima?",
                "description_ru": "Какой ШАГ является ПЕРВЫМ в диагностике медленного компонента?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Profiler'da yozib olish",
                    "useMemo qo'shish",
                    "Kodni butunlay qayta yozish",
                    "Kutubxonani yangilash",
                ],
                "options_ru": [
                    "Запись в Profiler",
                    "Добавление useMemo",
                    "Полностью переписать код",
                    "Обновить библиотеку",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "1-darsdan boshlab takrorlangan qoidani eslang.",
                "hint_ru": "Вспомните правило, повторяющееся начиная с урока 1.",
                "explanation": "Har qanday tuzatishdan oldin, muammoning haqiqiy sababini aniqlash uchun Profiler'da o'lchash kerak.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "actualDuration'ning ahamiyati",
                "title_ru": "Значение actualDuration",
                "description": (
                    "Bo'shliqni to'ldiring: agar re-render kaskadi bo'lsa-yu, lekin "
                    "actualDuration arzimas bo'lsa, bu ___ muammo emas."
                ),
                "description_ru": (
                    "Заполните пропуск: если каскад ре-рендеров есть, но "
                    "actualDuration ничтожен, это не ___ проблема."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "real",
                "correct_answers_ru": "реальная",
                "hint": "8-darsdagi \"halol javob\" bo'limida ishlatilgan so'zni eslang.",
                "hint_ru": "Вспомните слово из раздела «честный ответ» урока 8.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "To'liq diagnostika oqimi",
                "title_ru": "Полный поток диагностики",
                "description": "StudentTeamGame taymerini diagnostika qilish qadamlarini to'g'ri tartibga joylashtiring.",
                "description_ru": "Расставьте по порядку шаги диагностики таймера StudentTeamGame.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Profiler'da yozib olish",
                    "\"Nega render bo'ldi\" va qo'shimcha keraksiz komponentlarni tekshirish",
                    "actualDuration'ni tekshirib, haqiqiy muammo ekanini aniqlash",
                    "Sababga mos texnika qo'llash (state tushirish yoki memo)",
                    "Qayta o'lchab, yaxshilanishni tasdiqlash",
                ],
                "drag_items_ru": [
                    "Запись в Profiler",
                    "Проверка «почему отрендерился» и лишних соседних компонентов",
                    "Проверка actualDuration и подтверждение реальности проблемы",
                    "Применение техники под причину (опустить state или memo)",
                    "Повторное измерение и подтверждение улучшения",
                ],
                "correct_order": [
                    "Profiler'da yozib olish",
                    "\"Nega render bo'ldi\" va qo'shimcha keraksiz komponentlarni tekshirish",
                    "actualDuration'ni tekshirib, haqiqiy muammo ekanini aniqlash",
                    "Sababga mos texnika qo'llash (state tushirish yoki memo)",
                    "Qayta o'lchab, yaxshilanishni tasdiqlash",
                ],
                "hint": "Bu — ushbu darsning besh qadamli diagnostika jarayoni.",
                "hint_ru": "Это пятишаговый процесс диагностики из этого урока.",
                "difficulty_level": "Hard",
                "points": 15,
            },
        ],
    },
    {
        "order": 13,
        "title": "13-CAPSTONE: Sekin ilovani profil qilish va optimallashtirish",
        "title_ru": "13-CAPSTONE: Профилирование и оптимизация медленного приложения",
        "points_reward": 25,
        "text_content": (
            "<h3>Kurs yakuni: hammasi birga</h3>"
            "<p>Bu — kursning yakuniy capstone loyihasi. Siz atayin SEKIN qilib "
            "qurilgan kichik \"kurslar katalogi\" ilovasini olasiz va kursda "
            "o'rgangan texnikalarning HAMMASINI (yoki kamida ko'pchiligini) real "
            "tartibda qo'llaysiz: avval o'lchaysiz, keyin sabablarni "
            "aniqlaysiz, keyin har biriga mos texnikani tanlaysiz, so'ngra qayta "
            "o'lchab tasdiqlaysiz.</p>"
            "<h3>Boshlang'ich ilova — atayin qo'yilgan besh muammo</h3>"
            "<p>Quyidagi kod bo'limida <code>SlowCatalogApp</code> beriladi — u "
            "kursda ko'rgan besh xil muammoni ATAYIN o'z ichiga oladi: "
            "(1) <code>CourseCard</code> memo qilinmagan va inline "
            "<code>onOpen</code> funksiyasi bilan chaqiriladi (2-3-darslar); "
            "(2) qidiruv natijasi <code>useMemo</code>siz har render'da qayta "
            "hisoblanadi, LEKIN bu holatda ro'yxat 2000 ta elementdan iborat — "
            "bu safar haqiqatan ham sezilarli (5-8-darslar); (3) barcha 2000 "
            "element virtualizatsiyasiz to'g'ridan-to'g'ri render qilinadi "
            "(5-dars); (4) filtr <code>Context</code> orqali uzatiladi, va "
            "Context <code>value</code>si <code>useMemo</code>siz, demak har "
            "render'da yangi (6-dars); (5) \"sevimlilar soni\" ko'rsatkichi "
            "state'i butun ilova ildizida saqlanadi, garchi faqat bitta kichik "
            "chip komponenti uni ko'rsatsa ham (11-dars).</p>"
            "<h3>Sizning vazifangiz</h3>"
            "<p>Har bir muammoni DevTools Profiler orqali o'lchab tasdiqlang "
            "(taxmin qilmang — hatto ushbu darsda \"besh muammo\" oldindan "
            "aytilgan bo'lsa ham, HAR birining haqiqiy ta'sirini o'zingiz "
            "o'lchashingiz kerak), keyin mos texnikani qo'llang: "
            "<code>React.memo</code> + <code>useCallback</code>, "
            "<code>useMemo</code>, <code>react-window</code> orqali "
            "virtualizatsiya, Context'ni ajratish yoki keshlash, va state'ni "
            "kerakli darajaga tushirish. Har bir tuzatishdan keyin QAYTA "
            "o'lchab, farqni yozib boring.</p>"
            "<h3>Nima kutilmaydi</h3>"
            "<p>Aniq raqamli \"X marta tezlashdi\" da'vosi kutilmaydi (kursning "
            "boshidan beri ta'kidlanganidek, bunday raqamlarni tekshirmasdan "
            "aytish noto'g'ri). Buning o'rniga: Profiler'dagi render SONI va "
            "commit'lar sonining OLDIN/KEYIN nisbiy taqqoslamasini (masalan, "
            "\"tahrirlashdan oldin har harfda 2000 ta CourseCard render bo'lardi, "
            "tuzatishdan keyin faqat 3-5 ta o'zgargan karta render bo'ladi\") "
            "yozib qoldirish kutiladi — bu haqiqiy, tekshirilishi mumkin bo'lgan "
            "dalil.</p>"
            "<h3>Diagramma: capstone arxitekturasi va besh tuzatish nuqtasi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  App[\"SlowCatalogApp\n"
            "(FilterContext value useMemo'siz)\"] --> Search[\"SearchBox\n"
            "(useMemo'siz filtrlash)\"]\n"
            "  App --> List[\"CourseList\n"
            "(2000 ta element, virtualizatsiyasiz)\"]\n"
            "  List --> Card1[\"CourseCard x2000\n"
            "(memo'siz, inline onOpen)\"]\n"
            "  App --> Fav[\"FavoritesChip\n"
            "(state ildizda, faqat shu componentga tegishli)\"]\n"
            "  Search -.->|\"5-tuzatish nuqtasi\"| Fix1[\"useMemo + FixedSizeList\"]\n"
            "  Card1 -.->|\"tuzatish\"| Fix2[\"React.memo + useCallback\"]\n"
            "  App -.->|\"tuzatish\"| Fix3[\"Context ajratish/keshlash\"]\n"
            "  Fav -.->|\"tuzatish\"| Fix4[\"State'ni FavoritesChip'ga tushirish\"]\n"
            "</pre>"
            "<p>Diagramma — sizning vazifangizning \"xarita\"si: har bir "
            "tuzatish nuqtasi kursning muayyan darsiga to'g'ri keladi.</p>"
            "<h3>O'z-o'zini tekshirish uchun nazorat ro'yxati</h3>"
            "<p>Topshirishdan oldin o'zingizga savol bering: har bir tuzatish "
            "uchun Profiler'da OLDIN va KEYIN'gi render sonini yozdimmi? "
            "<code>CourseCard</code> endi faqat o'zgargan kartalarda render "
            "bo'ladimi (qidiruv har harfida EMAS)? <code>FixedSizeList</code> "
            "DOM'da doim bir necha o'nlab qatorni saqlab turadimi (2000 emas)? "
            "<code>FilterContext</code> ikkiga bo'lingandami, shunda qidiruv "
            "o'zgarishi <code>FavoritesChip</code>ni qayta render QILMAYDImi? "
            "Va eng muhimi — har bir tuzatishni QILISHDAN OLDIN sababni "
            "Profiler orqali tasdiqladingizmi, yoki to'g'ridan-to'g'ri "
            "\"bilib turibman\" deb tuzatishga o'tdingizmi? Ikkinchisi — bu "
            "kursning birinchi darsidan beri ogohlantirilgan aynan o'sha "
            "\"taxmin qilish\" xatosi.</p>"
            "<h3>Bu — nafaqat sintaksis, balki jarayon haqidagi vazifa</h3>"
            "<p>Bu capstone'ning baholanishi faqat \"kod to'g'ri yozilganmi\" "
            "emas — u SIZNING diagnostika JARAYONINGIZ to'g'ri bo'lganmi degan "
            "savolga ham qaraydi. Ikki talaba bir xil yakuniy kodni yozishi "
            "mumkin, lekin biri Profiler'da har bir qadamni o'lchab borgan, "
            "ikkinchisi esa faqat \"bu darsda aytilgan edi\" deb ko'chirib "
            "yozgan bo'lishi mumkin — birinchisi kursning haqiqiy maqsadiga "
            "erishgan, ikkinchisi esa hali ham \"taxmin qilish\" rejimida "
            "qolgan.</p>"
            "<h3>Kursni tugatganingiz bilan tabriklaymiz</h3>"
            "<p>1-darsdagi \"avval o'lchang\"dan boshlab ushbu capstone'gacha "
            "bo'lgan yo'lni bosib o'tib, siz React performance'ning to'liq "
            "amaliy tsiklini o'zlashtirdingiz — bu xuddi shu tsikl istalgan "
            "haqiqiy ilovaga, jumladan ushbu platformaning o'z frontend'iga ham "
            "qo'llaniladi.</p>"
        ),
        "text_content_ru": (
            "<h3>Финал курса: всё вместе</h3>"
            "<p>Это финальный capstone-проект курса. Вы получаете небольшое, "
            "специально замедленное приложение «каталог курсов» и применяете "
            "ВСЕ (или большинство) изученных в курсе техник в реальном порядке: "
            "сначала измеряете, затем определяете причины, затем выбираете "
            "подходящую технику под каждую, затем измеряете снова для "
            "подтверждения.</p>"
            "<h3>Начальное приложение — пять специально заложенных проблем</h3>"
            "<p>В разделе кода ниже дан <code>SlowCatalogApp</code> — он "
            "СПЕЦИАЛЬНО содержит пять разных проблем из курса: (1) "
            "<code>CourseCard</code> не мемоизирован и вызывается с инлайн-функцией "
            "<code>onOpen</code> (уроки 2-3); (2) результат поиска пересчитывается "
            "на каждом рендере без <code>useMemo</code>, НО в этом случае список "
            "состоит из 2000 элементов — на этот раз это действительно заметно "
            "(уроки 5-8); (3) все 2000 элементов рендерятся напрямую без "
            "виртуализации (урок 5); (4) фильтр передаётся через "
            "<code>Context</code>, а <code>value</code> Context без "
            "<code>useMemo</code>, то есть новый на каждом рендере (урок 6); (5) "
            "state «количество избранного» хранится в корне всего приложения, "
            "хотя показывает его только один маленький компонент-чип (урок 11).</p>"
            "<h3>Ваша задача</h3>"
            "<p>Подтвердите КАЖДУЮ проблему измерением через DevTools Profiler "
            "(не догадывайтесь — даже если в этом уроке «пять проблем» названы "
            "заранее, реальное влияние КАЖДОЙ нужно измерить самостоятельно), "
            "затем примените подходящую технику: <code>React.memo</code> + "
            "<code>useCallback</code>, <code>useMemo</code>, виртуализацию через "
            "<code>react-window</code>, разделение или кеширование Context, и "
            "опускание state на нужный уровень. После каждого исправления "
            "измерьте СНОВА и запишите разницу.</p>"
            "<h3>Что не ожидается</h3>"
            "<p>Не ожидается точное числовое утверждение «ускорилось в X раз» "
            "(как подчёркивалось с начала курса, заявлять такие цифры без "
            "проверки неправильно). Вместо этого ожидается запись ОТНОСИТЕЛЬНОГО "
            "сравнения ДО/ПОСЛЕ по числу рендеров и commit'ов в Profiler "
            "(например, «до правки при каждой букве рендерилось 2000 "
            "CourseCard, после правки — только 3-5 реально изменившихся "
            "карточек») — это реальное, проверяемое доказательство.</p>"
            "<h3>Диаграмма: архитектура capstone и пять точек исправления</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  App[\"SlowCatalogApp\n"
            "(значение FilterContext без useMemo)\"] --> Search[\"SearchBox\n"
            "(фильтрация без useMemo)\"]\n"
            "  App --> List[\"CourseList\n"
            "(2000 элементов, без виртуализации)\"]\n"
            "  List --> Card1[\"CourseCard x2000\n"
            "(без memo, инлайн onOpen)\"]\n"
            "  App --> Fav[\"FavoritesChip\n"
            "(state в корне, относится только к этому компоненту)\"]\n"
            "  Search -.->|\"точка исправления 5\"| Fix1[\"useMemo + FixedSizeList\"]\n"
            "  Card1 -.->|\"исправление\"| Fix2[\"React.memo + useCallback\"]\n"
            "  App -.->|\"исправление\"| Fix3[\"Разделение/кеширование Context\"]\n"
            "  Fav -.->|\"исправление\"| Fix4[\"Опустить state в FavoritesChip\"]\n"
            "</pre>"
            "<p>Диаграмма — это «карта» вашего задания: каждая точка "
            "исправления соответствует конкретному уроку курса.</p>"
            "<h3>Чек-лист для самопроверки</h3>"
            "<p>Перед сдачей задайте себе вопрос: записали ли вы для каждого "
            "исправления число рендеров ДО и ПОСЛЕ в Profiler? Перерендеривается "
            "ли <code>CourseCard</code> теперь только для изменившихся карточек "
            "(а НЕ при каждой букве поиска)? Держит ли <code>FixedSizeList</code> "
            "в DOM всегда несколько десятков строк (а не 2000)? Разделён ли "
            "<code>FilterContext</code> на два, так что изменение поиска НЕ "
            "перерендеривает <code>FavoritesChip</code>? И самое главное — "
            "подтвердили ли вы причину через Profiler ПЕРЕД тем, как вносить "
            "каждое исправление, или сразу перешли к исправлению, «зная "
            "заранее»? Второе — та самая ошибка «догадки», от которой "
            "предостерегали с первого урока курса.</p>"
            "<h3>Это задание не только о синтаксисе, но и о процессе</h3>"
            "<p>Оценка этого capstone смотрит не только на то, «правильно ли "
            "написан код» — она также проверяет, был ли правильным ваш ПРОЦЕСС "
            "диагностики. Два студента могут написать одинаковый итоговый код, "
            "но один измерял каждый шаг в Profiler, а другой просто переписал "
            "«потому что так было сказано в уроке» — первый достиг реальной цели "
            "курса, второй всё ещё остаётся в режиме «догадки».</p>"
            "<h3>Поздравляем с завершением курса</h3>"
            "<p>Пройдя путь от «сначала измерь» в уроке 1 до этого capstone, вы "
            "прошли полный практический цикл производительности React — тот же "
            "цикл, который применим к любому реальному приложению, включая "
            "фронтенд этой самой платформы.</p>"
        ),
        "code_content": (
            "// SlowCatalogApp — capstone uchun ATAYIN sekin qurilgan boshlang'ich\n"
            "// nuqta. Beshta muammo izohlarda belgilangan — vazifa ularni\n"
            "// o'lchab, tuzatish.\n"
            "import { createContext, useContext, useState } from 'react';\n\n"
            "const FilterContext = createContext(null);\n\n"
            "function FilterProvider({ children }) {\n"
            "  const [search, setSearch] = useState('');\n"
            "  const [favoritesCount, setFavoritesCount] = useState(0); // 5-muammo\n\n"
            "  // 4-MUAMMO: value useMemo'siz — har render'da yangi obyekt,\n"
            "  // barcha iste'molchilarni keraksiz qayta render qiladi.\n"
            "  const value = { search, setSearch, favoritesCount, setFavoritesCount };\n"
            "  return <FilterContext.Provider value={value}>{children}</FilterContext.Provider>;\n"
            "}\n\n"
            "// 1-MUAMMO: CourseCard memo qilinmagan.\n"
            "function CourseCard({ course, onOpen }) {\n"
            "  return (\n"
            "    <div className=\"card\">\n"
            "      <h4>{course.title}</h4>\n"
            "      <button onClick={onOpen}>Ochish</button>\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "function CourseList({ courses }) {\n"
            "  const { search } = useContext(FilterContext);\n\n"
            "  // 2-MUAMMO: useMemo'siz filtrlash — 2000 ta elementda bu safar\n"
            "  // haqiqatan sezilarli.\n"
            "  const filtered = courses.filter((c) =>\n"
            "    c.title.toLowerCase().includes(search.toLowerCase())\n"
            "  );\n\n"
            "  return (\n"
            "    <div className=\"list\">\n"
            "      {/* 3-MUAMMO: barcha 2000 element virtualizatsiyasiz render\n"
            "          qilinadi. */}\n"
            "      {filtered.map((course) => (\n"
            "        <CourseCard\n"
            "          key={course.id}\n"
            "          course={course}\n"
            "          onOpen={() => console.log('ochildi:', course.title)} // inline\n"
            "        />\n"
            "      ))}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "function FavoritesChip() {\n"
            "  const { favoritesCount } = useContext(FilterContext);\n"
            "  return <span className=\"chip\">⭐ {favoritesCount}</span>;\n"
            "}\n\n"
            "function SearchBox() {\n"
            "  const { search, setSearch } = useContext(FilterContext);\n"
            "  return <input value={search} onChange={(e) => setSearch(e.target.value)} />;\n"
            "}\n\n"
            "export default function SlowCatalogApp({ courses }) {\n"
            "  // courses — 2000 ta element bilan generatsiya qilingan deb faraz\n"
            "  // qilinadi (vazifa fayllarida tayyor generator beriladi).\n"
            "  return (\n"
            "    <FilterProvider>\n"
            "      <FavoritesChip />\n"
            "      <SearchBox />\n"
            "      <CourseList courses={courses} />\n"
            "    </FilterProvider>\n"
            "  );\n"
            "}\n\n"
            "// Test ma'lumotlarini generatsiya qilish uchun yordamchi (vazifa\n"
            "// fayllarida shunga o'xshash tayyor holda beriladi).\n"
            "function generateTestCourses(count = 2000) {\n"
            "  return Array.from({ length: count }, (_, i) => ({\n"
            "    id: i + 1,\n"
            "    title: `Kurs #${i + 1}`,\n"
            "  }));\n"
            "}\n\n"
            "// 5-MUAMMONING tuzatilgan yechimi (5-dars vazifasidan tashqari,\n"
            "// bu yerda alohida ko'rsatilgan): favoritesCount state'i o'z\n"
            "// FavoritesChip komponentida — App darajasida umuman yo'q.\n"
            "function FavoritesChipFixed() {\n"
            "  const [favoritesCount, setFavoritesCount] = React.useState(0);\n"
            "  return <span className=\"chip\">⭐ {favoritesCount}</span>;\n"
            "}\n\n"
            "// Yakuniy tekshiruv uchun kichik yordamchi: har bir tuzatishdan\n"
            "// oldin/keyingi render sonini yozib boruvchi jadval tuzish.\n"
            "function buildBeforeAfterReport(measurements) {\n"
            "  // measurements: [{ label, before, after }]\n"
            "  return measurements.map(({ label, before, after }) => ({\n"
            "    label,\n"
            "    before: `${before} render`,\n"
            "    after: `${after} render`,\n"
            "    reduced: before > after,\n"
            "  }));\n"
            "}\n\n"
            "// Namuna hisobot (vazifa topshirig'iga qo'shib yuboriladi):\n"
            "// buildBeforeAfterReport([\n"
            "//   { label: 'CourseCard (harf kiritilganda)', before: 2000, after: 4 },\n"
            "//   { label: 'FavoritesChip (qidiruv o\\'zgarganda)', before: 1, after: 0 },\n"
            "// ]);\n"
        ),
        "code_content_ru": (
            "// SlowCatalogApp — специально медленная стартовая точка для\n"
            "// capstone. Пять проблем отмечены в комментариях — задача:\n"
            "// измерить и исправить.\n"
            "import { createContext, useContext, useState } from 'react';\n\n"
            "const FilterContext = createContext(null);\n\n"
            "function FilterProvider({ children }) {\n"
            "  const [search, setSearch] = useState('');\n"
            "  const [favoritesCount, setFavoritesCount] = useState(0); // проблема 5\n\n"
            "  // ПРОБЛЕМА 4: value без useMemo — новый объект на каждом рендере,\n"
            "  // излишне перерендеривает всех потребителей.\n"
            "  const value = { search, setSearch, favoritesCount, setFavoritesCount };\n"
            "  return <FilterContext.Provider value={value}>{children}</FilterContext.Provider>;\n"
            "}\n\n"
            "// ПРОБЛЕМА 1: CourseCard не мемоизирован.\n"
            "function CourseCard({ course, onOpen }) {\n"
            "  return (\n"
            "    <div className=\"card\">\n"
            "      <h4>{course.title}</h4>\n"
            "      <button onClick={onOpen}>Открыть</button>\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "function CourseList({ courses }) {\n"
            "  const { search } = useContext(FilterContext);\n\n"
            "  // ПРОБЛЕМА 2: фильтрация без useMemo — на 2000 элементах на этот\n"
            "  // раз действительно заметно.\n"
            "  const filtered = courses.filter((c) =>\n"
            "    c.title.toLowerCase().includes(search.toLowerCase())\n"
            "  );\n\n"
            "  return (\n"
            "    <div className=\"list\">\n"
            "      {/* ПРОБЛЕМА 3: все 2000 элементов рендерятся без\n"
            "          виртуализации. */}\n"
            "      {filtered.map((course) => (\n"
            "        <CourseCard\n"
            "          key={course.id}\n"
            "          course={course}\n"
            "          onOpen={() => console.log('открыт:', course.title)} // инлайн\n"
            "        />\n"
            "      ))}\n"
            "    </div>\n"
            "  );\n"
            "}\n\n"
            "function FavoritesChip() {\n"
            "  const { favoritesCount } = useContext(FilterContext);\n"
            "  return <span className=\"chip\">⭐ {favoritesCount}</span>;\n"
            "}\n\n"
            "function SearchBox() {\n"
            "  const { search, setSearch } = useContext(FilterContext);\n"
            "  return <input value={search} onChange={(e) => setSearch(e.target.value)} />;\n"
            "}\n\n"
            "export default function SlowCatalogApp({ courses }) {\n"
            "  // courses — предполагается сгенерированным с 2000 элементами\n"
            "  // (в файлах задания дан готовый генератор).\n"
            "  return (\n"
            "    <FilterProvider>\n"
            "      <FavoritesChip />\n"
            "      <SearchBox />\n"
            "      <CourseList courses={courses} />\n"
            "    </FilterProvider>\n"
            "  );\n"
            "}\n\n"
            "// Помощник для генерации тестовых данных (в файлах задания дан\n"
            "// похожий готовый вариант).\n"
            "function generateTestCourses(count = 2000) {\n"
            "  return Array.from({ length: count }, (_, i) => ({\n"
            "    id: i + 1,\n"
            "    title: `Курс #${i + 1}`,\n"
            "  }));\n"
            "}\n\n"
            "// Исправленное решение ПРОБЛЕМЫ 5 (показано отдельно, помимо задания\n"
            "// урока 5): state favoritesCount — в собственном компоненте\n"
            "// FavoritesChip, на уровне App его вообще нет.\n"
            "function FavoritesChipFixed() {\n"
            "  const [favoritesCount, setFavoritesCount] = React.useState(0);\n"
            "  return <span className=\"chip\">⭐ {favoritesCount}</span>;\n"
            "}\n\n"
            "// Небольшой помощник для итоговой проверки: построение таблицы с\n"
            "// числом рендеров до/после каждого исправления.\n"
            "function buildBeforeAfterReport(measurements) {\n"
            "  // measurements: [{ label, before, after }]\n"
            "  return measurements.map(({ label, before, after }) => ({\n"
            "    label,\n"
            "    before: `${before} рендер(ов)`,\n"
            "    after: `${after} рендер(ов)`,\n"
            "    reduced: before > after,\n"
            "  }));\n"
            "}\n\n"
            "// Пример отчёта (прикладывается к сдаче задания):\n"
            "// buildBeforeAfterReport([\n"
            "//   { label: 'CourseCard (при вводе буквы)', before: 2000, after: 4 },\n"
            "//   { label: 'FavoritesChip (при изменении поиска)', before: 1, after: 0 },\n"
            "// ]);\n"
        ),
        "code_language": "jsx",
        "video_url": None,
        "task": {
            "task_title": "CAPSTONE: SlowCatalogApp'ni profil qilib optimallashtiring",
            "task_title_ru": "CAPSTONE: профилируйте и оптимизируйте SlowCatalogApp",
            "task_description": (
                "Berilgan SlowCatalogApp'dagi beshta atayin qo'yilgan muammoni "
                "(CourseCard memo yo'qligi, useMemo'siz filtrlash, virtualizatsiya "
                "yo'qligi, Context value useMemo'siz, favoritesCount state'i noto'g'ri "
                "joyda) birma-bir Profiler orqali o'lchab tasdiqlang, so'ngra mos "
                "texnika bilan tuzating: React.memo+useCallback, useMemo, "
                "react-window (FixedSizeList), Context'ni ajratish/keshlash va "
                "favoritesCount state'ini FavoritesChip'ning o'ziga tushirish. Har "
                "bir tuzatishdan oldin va keyingi render sonini yozib qo'ying."
            ),
            "task_description_ru": (
                "В данном SlowCatalogApp продиагностируйте по очереди пять "
                "специально заложенных проблем (отсутствие memo у CourseCard, "
                "фильтрация без useMemo, отсутствие виртуализации, value Context без "
                "useMemo, state favoritesCount в неправильном месте) через Profiler, "
                "затем исправьте подходящей техникой: React.memo+useCallback, "
                "useMemo, react-window (FixedSizeList), разделение/кеширование "
                "Context и опускание state favoritesCount в сам FavoritesChip. "
                "Запишите число рендеров до и после каждого исправления."
            ),
            "task_requirements": (
                "Barcha beshta muammo Profiler o'lchovi bilan tasdiqlangan bo'lishi "
                "shart (taxmin emas). CourseCard memo qilinishi, filtrlash useMemo "
                "bilan, ro'yxat FixedSizeList bilan, Context ajratilgan/keshlangan, "
                "favoritesCount alohida komponentda bo'lishi shart. Har bir tuzatish "
                "uchun oldin/keyin render soni yozma taqdim etilishi kerak."
            ),
            "task_requirements_ru": (
                "Все пять проблем должны быть подтверждены измерением в Profiler (не "
                "догадкой). CourseCard обязан быть мемоизирован, фильтрация — через "
                "useMemo, список — через FixedSizeList, Context — разделён/закеширован, "
                "favoritesCount — в отдельном компоненте. Для каждого исправления "
                "нужно письменно указать число рендеров до/после."
            ),
            "task_technologies": "React, React DevTools Profiler, React.memo, useMemo, useCallback, react-window",
            "task_deadline_days": 10,
        },
        "sample": {
            "title": "Namuna: SlowCatalogApp'ning to'liq optimallashtirilgan versiyasi",
            "description": "Barcha beshta muammo tuzatilgan yakuniy capstone yechimi.",
            "sample_type": "code",
            "code_files": [
                {"filename": "FastCatalogApp.jsx", "language": "jsx", "code": (
                    "import { createContext, useContext, useState, useMemo, useCallback, memo } from 'react';\n"
                    "import { FixedSizeList } from 'react-window';\n\n"
                    "const SearchContext = createContext(null);   // ajratilgan: kam o'zgaradi\n"
                    "const FavoritesContext = createContext(null); // ajratilgan: alohida\n\n"
                    "function FilterProvider({ children }) {\n"
                    "  const [search, setSearch] = useState('');\n"
                    "  const [favoritesCount, setFavoritesCount] = useState(0);\n"
                    "  const searchValue = useMemo(() => ({ search, setSearch }), [search]);\n"
                    "  const favValue = useMemo(\n"
                    "    () => ({ favoritesCount, setFavoritesCount }),\n"
                    "    [favoritesCount]\n"
                    "  );\n"
                    "  return (\n"
                    "    <SearchContext.Provider value={searchValue}>\n"
                    "      <FavoritesContext.Provider value={favValue}>{children}</FavoritesContext.Provider>\n"
                    "    </SearchContext.Provider>\n"
                    "  );\n"
                    "}\n\n"
                    "const CourseCard = memo(function CourseCard({ course, onOpen }) {\n"
                    "  return (\n"
                    "    <div className=\"card\">\n"
                    "      <h4>{course.title}</h4>\n"
                    "      <button onClick={() => onOpen(course.id)}>Ochish</button>\n"
                    "    </div>\n"
                    "  );\n"
                    "});\n\n"
                    "function CourseList({ courses }) {\n"
                    "  const { search } = useContext(SearchContext);\n"
                    "  const handleOpen = useCallback((id) => console.log('ochildi:', id), []);\n"
                    "  const filtered = useMemo(\n"
                    "    () => courses.filter((c) => c.title.toLowerCase().includes(search.toLowerCase())),\n"
                    "    [courses, search]\n"
                    "  );\n"
                    "  const Row = ({ index, style }) => (\n"
                    "    <div style={style}>\n"
                    "      <CourseCard course={filtered[index]} onOpen={handleOpen} />\n"
                    "    </div>\n"
                    "  );\n"
                    "  return (\n"
                    "    <FixedSizeList height={480} width=\"100%\" itemCount={filtered.length} itemSize={64}>\n"
                    "      {Row}\n"
                    "    </FixedSizeList>\n"
                    "  );\n"
                    "}\n"
                )},
            ],
        },
        "exercises": [
            {
                "title": "Capstone'dagi 2-muammoning haqiqiy sababi",
                "title_ru": "Реальная причина проблемы 2 в capstone",
                "description": "SlowCatalogApp'da filtrlash nega bu safar (avvalgi darslardagi kichik ro'yxatlardan farqli) haqiqatan sezilarli bo'lishi mumkin?",
                "description_ru": "Почему фильтрация в SlowCatalogApp на этот раз (в отличие от небольших списков в прошлых уроках) может быть реально заметной?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Ro'yxat 2000 ta elementdan iborat — bu 5-8-darslardagi \"kichik ro'yxatda kerak emas\" chegarasidan ancha katta",
                    "React.memo umuman ishlamaydi",
                    "useState endi ishlamay qoladi",
                    "Context har doim sekin",
                ],
                "options_ru": [
                    "Список состоит из 2000 элементов — это значительно больше границы «не нужно на маленьком списке» из уроков 5-8",
                    "React.memo вообще не работает",
                    "useState перестаёт работать",
                    "Context всегда медленный",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "5-darsdagi \"qachon virtualizatsiya kerak\" chegarasini eslang.",
                "hint_ru": "Вспомните порог «когда нужна виртуализация» из урока 5.",
                "explanation": "Kursda ko'rgan barcha \"hozircha kerak emas\" xulosalari kichik ro'yxatlarga asoslangan edi — 2000 element bu chegaradan ancha yuqori.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Tuzatish tasdiqlanishi",
                "title_ru": "Подтверждение исправления",
                "description": (
                    "Bo'shliqni to'ldiring: har bir tuzatishdan keyin, ___ orqali "
                    "qayta o'lchab, yaxshilanishni tasdiqlash shart — taxmin bilan "
                    "cheklanib bo'lmaydi."
                ),
                "description_ru": (
                    "Заполните пропуск: после каждого исправления обязательно "
                    "измерить снова через ___ и подтвердить улучшение — "
                    "ограничиваться догадкой нельзя."
                ),
                "exercise_type": "fill_in_blank",
                "correct_answers": "Profiler",
                "hint": "Kursning birinchi darsidan beri asosiy o'lchash vositasi.",
                "hint_ru": "Основной инструмент измерения с первого урока курса.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Beshta tuzatishni mos darsga moslashtirish",
                "title_ru": "Сопоставьте пять исправлений с соответствующим уроком",
                "description": "Har bir tuzatish texnikasini kursdagi mos darsga (tartib bo'yicha) moslang.",
                "description_ru": "Сопоставьте каждую технику исправления с соответствующим уроком курса (по порядку).",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "React.memo + useCallback (CourseCard uchun)",
                    "useMemo (filtrlash uchun)",
                    "react-window FixedSizeList (2000 element uchun)",
                    "Context'ni ajratish/keshlash (FilterContext uchun)",
                    "State'ni tushirish (favoritesCount uchun)",
                ],
                "drag_items_ru": [
                    "React.memo + useCallback (для CourseCard)",
                    "useMemo (для фильтрации)",
                    "react-window FixedSizeList (для 2000 элементов)",
                    "Разделение/кеширование Context (для FilterContext)",
                    "Опускание state (для favoritesCount)",
                ],
                "correct_order": [
                    "React.memo + useCallback (CourseCard uchun)",
                    "useMemo (filtrlash uchun)",
                    "react-window FixedSizeList (2000 element uchun)",
                    "Context'ni ajratish/keshlash (FilterContext uchun)",
                    "State'ni tushirish (favoritesCount uchun)",
                ],
                "hint": "Tartib — kursdagi darslar tartibiga mos: 3-dars, 2-dars, 5-dars, 6-dars, 11-dars mavzulari.",
                "hint_ru": "Порядок соответствует урокам курса: темы уроков 3, 2, 5, 6, 11.",
                "difficulty_level": "Hard",
                "points": 15,
            },
        ],
    },
    # === END LESSONS ===
]

_lesson_points = sum(l.get("points_reward", 10) for l in LESSONS)
_exercise_points = sum(
    ex.get("points", 10) for l in LESSONS for ex in (l.get("exercises") or [])
)
COURSE["max_points"] = _lesson_points + _exercise_points
