"""Seed "React: Redux Toolkit, TypeScript va Testlash" (13 lessons: 11 main +
2 revisions).

Usage:
    cd backend
    python scripts/seed_react_advanced.py
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists.

Target audience: "React Asoslari" (course 43) graduates — assumes JSX, props,
useState, conditional rendering/forms, useEffect, custom hooks, Router,
Context API, and memo/useMemo/useCallback are already known (course 43 covers
all of those in depth; this course does NOT re-teach them). Scope is
deliberately narrow: Redux Toolkit, React + TypeScript, and Jest/React
Testing Library — the three gaps identified after auditing course 43.
Language: Uzbek content, same WIN-FIRST lesson shape as seed_react_basics.py:
BLOKA 1/2/3 hands-on hook -> deliberate-error -> theory -> "Bu darsdan keyin
siz bilasizki" wrap.

STATUS: only Lesson 1 is fully written so far (content + exercises + namuna).
Lessons 2-13 are stubbed in LESSON_PLAN below with their scope so the course
structure is visible, but have no TEXT/CODE/exercises yet — _resolve_lessons()
will raise clearly if you try to seed() before filling one in. Fill in the
matching L{n}_TEXT/L{n}_CODE/L{n}_EX globals and flip STATUS to "done" as
each lesson is written; run --dry-run after each to review before applying.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import engine, AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 ensure all models registered
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from app.models.lesson_sample import LessonSample  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Course-level metadata
# ─────────────────────────────────────────────────────────────────────────────
COURSE = {
    "title": "React: Redux Toolkit, TypeScript va Testlash",
    "description": (
        "React Asoslari kursini tugatgan dasturchilar uchun: Redux Toolkit "
        "bilan markazlashgan state boshqaruvi (createSlice, RTK Query), "
        "TypeScript bilan komponent va state'larni tiplash, va Jest + React "
        "Testing Library bilan komponentlarni testlash. Yakunda — to'liq "
        "tiplangan, testlangan, Redux Toolkit asosidagi savdo ilovasi."
    ),
    "instructor_id": 2,
    "difficulty_level": "Advanced",
    "duration_weeks": 5,
    "max_points": 250,
    "category_id": 9,  # same category as course 43 (React)
    "prerequisite_course_id": 43,  # React Asoslari
    "is_active": True,
    "is_published": False,  # flip to True once all 13 lessons are written
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson plan — scope reference for lessons not yet written.
# ═════════════════════════════════════════════════════════════════════════════
LESSON_PLAN = [
    {"order": 0,  "ref": "L1",  "status": "done",
     "title": "1-Nega Redux Toolkit? Context'ning chegaralari",
     "scope": "Context re-render cascade problem, when Context is enough vs. "
              "when you need a real store, RTK vs classic Redux boilerplate."},
    {"order": 1,  "ref": "L2",  "status": "done",
     "title": "2-configureStore + createSlice",
     "scope": "Store setup, slices, auto-generated actions/reducers, Provider."},
    {"order": 2,  "ref": "L3",  "status": "done",
     "title": "3-useSelector / useDispatch va komponentlarni ulash",
     "scope": "Connecting components to the store, selecting state slices, "
              "dispatching from event handlers."},
    {"order": 3,  "ref": "L4",  "status": "done",
     "title": "4-Async holat: createAsyncThunk",
     "scope": "Fetching into the store, pending/fulfilled/rejected, "
              "loading/error UI states."},
    {"order": 4,  "ref": "R1",  "status": "done",
     "title": "R1-Todo + Cart takrorlash (RTK)",
     "scope": "Combine slices + thunk + selectors in one small app — "
              "revision covering lessons 1-4."},
    {"order": 5,  "ref": "L5",  "status": "done",
     "title": "5-RTK Query asoslari",
     "scope": "createApi, auto-generated hooks (useGetXQuery), why it "
              "replaces useEffect+useState data-fetching boilerplate."},
    {"order": 6,  "ref": "L6",  "status": "done",
     "title": "6-Selectors va performance (reselect)",
     "scope": "createSelector, memoized selectors, avoiding unnecessary "
              "re-renders from derived state."},
    {"order": 7,  "ref": "L7",  "status": "done", "lang": "tsx",
     "title": "7-React + TypeScript: props va state tiplash",
     "scope": ".tsx, typing function components, useState<T>, typing "
              "ChangeEvent/FormEvent handlers."},
    {"order": 8,  "ref": "L8",  "status": "done", "lang": "tsx",
     "title": "8-Generics va murakkab tiplar komponentlarda",
     "scope": "Generic components, utility types (Partial/Pick/Omit) on "
              "props, typing children."},
    {"order": 9,  "ref": "L9",  "status": "done", "lang": "tsx",
     "title": "9-Redux Toolkit + TypeScript birga",
     "scope": "Typing RootState/AppDispatch, typed hooks (useAppSelector/"
              "useAppDispatch), typing slice state and thunk payloads."},
    {"order": 10, "ref": "R2",  "status": "done", "lang": "tsx",
     "title": "R2-TS + RTK mini-loyiha (takrorlash)",
     "scope": "Small typed app combining lessons 7-9."},
    {"order": 11, "ref": "L10", "status": "done", "lang": "tsx",
     "title": "10-Jest + React Testing Library: birinchi test",
     "scope": "Setup, render/screen, querying by role/text, \"test "
              "behavior not implementation\"."},
    {"order": 12, "ref": "L11", "status": "done", "lang": "tsx",
     "title": "11-User events, async testing, mocking API",
     "scope": "userEvent, testing forms/clicks, waitFor, mocking fetch/RTK "
              "Query in tests."},
    {"order": 13, "ref": "CAPSTONE", "status": "done", "lang": "tsx",
     "title": "12-CAPSTONE: Typed shopping cart (RTK + TS + tests)",
     "scope": "Full app: TS components, RTK Query for products, RTK slice "
              "for cart, >=5 RTL tests, deploy. Project-graded, no inline "
              "exercises."},
]


# ═════════════════════════════════════════════════════════════════════════════
# Lesson 1 content
# ═════════════════════════════════════════════════════════════════════════════
L1_TEXT = """\
<h2>Nega Redux Toolkit? Context'ning chegaralarini his qiling</h2>

<pre class="mermaid">
flowchart LR
    P["Provider value o'zgardi"] --> A["useContext(X) — komponent A"]
    P --> B["useContext(X) — komponent B"]
    P --> C["useContext(X) — komponent C"]
    A -->|hech narsa X'dan ishlatmasa ham| RA["qayta render"]
    B -->|hech narsa X'dan ishlatmasa ham| RB["qayta render"]
    C -->|faqat shu haqiqatan kerak| RC["qayta render"]
</pre>

<p>React Asoslari kursida siz <code>Context API</code>'ni o'rgandingiz — global state uchun yaxshi vosita. Lekin katta ilovalarda dasturchilar ko'pincha Context'ni tashlab, <strong>Redux Toolkit</strong>ga o'tishadi. Nega? Bu darsda buni <em>his qilasiz</em> — nazariya emas, jonli demo orqali.</p>

<h3>🏆 5 daqiqada g'alaba — muammoni his qiling</h3>

<h4>BLOKA 1 — ikkita mustaqil qiymat, bitta Context</h4>
<pre><code>import { createContext, useContext, useState } from 'react';

const AppContext = createContext(null);

function ThemeLabel() {
  const { theme } = useContext(AppContext);
  console.log("🎨 ThemeLabel qayta render bo'ldi");
  return &lt;p&gt;Mavzu: {theme}&lt;/p&gt;;
}

function CounterLabel() {
  const { count } = useContext(AppContext);
  console.log("🔢 CounterLabel qayta render bo'ldi");
  return &lt;p&gt;Son: {count}&lt;/p&gt;;
}

function App() {
  const [theme, setTheme] = useState("light");
  const [count, setCount] = useState(0);

  return (
    &lt;AppContext.Provider value={{ theme, count }}&gt;
      &lt;ThemeLabel /&gt;
      &lt;CounterLabel /&gt;
      &lt;button onClick={() =&gt; setCount(c =&gt; c + 1)}&gt;+1 (faqat son)&lt;/button&gt;
    &lt;/AppContext.Provider&gt;
  );
}</code></pre>

<p>Konsolni oching va <strong>+1</strong> tugmasini bosing. Siz faqat <code>count</code>ni o'zgartirdingiz — <code>theme</code>ga tegmadingiz. Lekin konsolda nima ko'rinadi?</p>

<pre><code>🎨 ThemeLabel qayta render bo'ldi   ← bu nega render bo'ldi?!
🔢 CounterLabel qayta render bo'ldi</code></pre>

<p><strong>Mana muammo.</strong> <code>ThemeLabel</code> — <code>theme</code>dan boshqa hech narsa ishlatmaydi. Lekin u ham qayta render bo'ldi, chunki Context bitta butun <code>value</code> obyektini uzatadi. React qaysi maydon o'zgarganini bilmaydi — u faqat "value obyekti yangi referensga ega bo'ldi" deb biladi va <strong>barcha obunachilarni</strong> qayta render qiladi.</p>

<h4>BLOKA 2 — muammoni kattalashtiring</h4>
<pre><code>// Endi 50 ta ThemeLabel'ga o'xshash komponent tasavvur qiling —
// har biri faqat theme'ni ko'rsatadi, count bilan ishi yo'q.
// Foydalanuvchi "+1" tugmasini har bosganda — 50 tasi ham qayta render bo'ladi.
// 1 komponentda sezilmaydi. 50 tada — jank (sekinlashuv) sezasiz.

function ManyThemeLabels() {
  return (
    &lt;&gt;
      {Array.from({ length: 50 }).map((_, i) =&gt; (
        &lt;ThemeLabel key={i} /&gt;
      ))}
    &lt;/&gt;
  );
}</code></pre>

<h4>BLOKA 3 — Redux Toolkit qanday hal qiladi (ko'rib qo'ying, hali yozmaysiz)</h4>
<pre><code>// Keyingi darsda buni to'liq o'rganasiz. Hozircha — shakliga qarang:

function ThemeLabelRTK() {
  // faqat theme slice'iga OBUNA BO'LADI — count o'zgarsa, bu qayta render BO'LMAYDI
  const theme = useSelector((state) =&gt; state.app.theme);
  return &lt;p&gt;Mavzu: {theme}&lt;/p&gt;;
}</code></pre>

<p><code>useSelector</code> — <strong>faqat</strong> siz so'ragan qismga obuna bo'ladi. <code>count</code> o'zgarganda, <code>state.app.theme</code> o'zgarmagani uchun, <code>ThemeLabelRTK</code> qayta render bo'lmaydi. Bu — Context bilan Redux Toolkit orasidagi asosiy farq.</p>

<h3>🐛 Ataylab xato — "hamma narsani bitta Context'ga tiqish"</h3>
<pre><code>// Yangi boshlovchilarning eng keng tarqalgan xatosi:
const MegaContext = createContext(null);

function App() {
  const [user, setUser] = useState(null);        // kamdan-kam o'zgaradi
  const [theme, setTheme] = useState("light");   // kamdan-kam o'zgaradi
  const [mousePos, setMousePos] = useState({x:0,y:0}); // HAR harakatda o'zgaradi!

  useEffect(() =&gt; {
    const handler = (e) =&gt; setMousePos({ x: e.clientX, y: e.clientY });
    window.addEventListener("mousemove", handler);
    return () =&gt; window.removeEventListener("mousemove", handler);
  }, []);

  return (
    &lt;MegaContext.Provider value={{ user, theme, mousePos }}&gt;
      &lt;WholeApp /&gt;
    &lt;/MegaContext.Provider&gt;
  );
}</code></pre>

<p><strong>Natija:</strong> sichqoncha harakatlanganda (soniyasiga o'nlab marta!) — <code>MegaContext</code>ga obuna bo'lgan <strong>butun ilova</strong> qayta render bo'ladi, hatto <code>user</code> yoki <code>theme</code>ni ko'rsatadigan komponentlar ham. Sabab — <code>mousePos</code> tez-tez o'zgaruvchi qiymat bilan kamdan-kam o'zgaruvchi qiymatlar bitta Context ichida aralashtirilgan.</p>

<p>Bu xato Context'ning aybi emas — <strong>noto'g'ri foydalanish</strong>. Lekin katta ilovada bunga o'xshash holatlar tez-tez chiqadi, va aynan shuning uchun tashqi state-management kutubxonasi kerak bo'ladi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Context nima uchun har doim "hammasi yoki hech narsa"</h4>
<p>Context'ning <code>value</code> propi — bitta obyekt (yoki qiymat). React <code>Object.is()</code> solishtiruvi bilan "eski value === yangi value" tekshiradi. Agar yo'q — <strong>barcha</strong> <code>useContext</code> chaqirgan komponentlar qayta render bo'ladi. Obyekt ichida qaysi maydon o'zgarganini React bilmaydi va bilishni ham xohlamaydi — bu Context'ning dizayn qarori.</p>

<h4>2. Redux (va RTK) boshqacha ishlaydi — selector orqali obuna</h4>
<table>
<tr><th></th><th>Context</th><th>Redux / RTK</th></tr>
<tr><td>Obuna birligi</td><td>Butun Provider value</td><td>Har bir <code>useSelector</code> — faqat o'zi so'ragan qism</td></tr>
<tr><td>Qayta render triggeri</td><td>Value referensi o'zgarsa — hammasi</td><td>Faqat selector natijasi o'zgarsa — o'shagina</td></tr>
<tr><td>DevTools / time-travel</td><td>Yo'q</td><td>Bor (Redux DevTools)</td></tr>
<tr><td>Boilerplate</td><td>Kam</td><td>RTK bilan kam, klassik Redux'da ko'p</td></tr>
</table>

<h4>3. Qachon Context yetarli?</h4>
<ul>
<li>Kamdan-kam o'zgaruvchi qiymatlar: theme, til (locale), login qilgan foydalanuvchi</li>
<li>Kichik-o'rta ilovalar, chuqur component daraxti bo'lmasa</li>
<li>Faqat "props drilling"ni yechish kerak bo'lsa (10 qavat props uzatishdan qochish)</li>
</ul>

<h4>4. Qachon Redux Toolkit kerak?</h4>
<ul>
<li>Tez-tez yangilanadigan, ko'plab komponent ishlatadigan state (savat, filtrlar, real-time ma'lumot)</li>
<li>Murakkab async logika (API chaqiruvlari, loading/error holatlari)</li>
<li>Debugging uchun DevTools/time-travel kerak bo'lsa</li>
<li>Katta jamoa — action/reducer'lar aniq struktura beradi</li>
</ul>

<h4>5. RTK vs klassik Redux — nima farq?</h4>
<pre><code>// Klassik Redux — har bir action uchun qo'lda kod
const INCREMENT = "counter/increment";
function increment() { return { type: INCREMENT }; }
function counterReducer(state = { value: 0 }, action) {
  switch (action.type) {
    case INCREMENT:
      return { ...state, value: state.value + 1 }; // qo'lda immutable update
    default:
      return state;
  }
}

// Redux Toolkit — createSlice avtomatik yaratadi
const counterSlice = createSlice({
  name: "counter",
  initialState: { value: 0 },
  reducers: {
    increment: (state) =&gt; { state.value += 1; }, // Immer — "mutatsiya" ko'rinishida, aslida immutable
  },
});
// action creator, action type, reducer — hammasi avtomatik</code></pre>

<p>RTK — Redux'ning o'zi emas, balki Redux ustidan qurilgan <strong>rasmiy, tavsiya etilgan</strong> qatlam. Boilerplate'ni kamaytiradi, Immer orqali "mutatsiya kabi yozilgan" kodni xavfsiz immutable update'ga aylantiradi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Context'ning value o'zgarsa — BARCHA obunachilar qayta render bo'ladi, qaysi maydon o'zgarganidan qat'iy nazar</li>
<li>✅ Redux/RTK — <code>useSelector</code> orqali faqat kerakli qismga obuna bo'lish imkonini beradi</li>
<li>✅ Context — kamdan-kam o'zgaruvchi global qiymatlar uchun yetarli (theme, til, user)</li>
<li>✅ Redux Toolkit — tez-tez yangilanadigan, murakkab, katta ilovalar uchun mos</li>
<li>✅ RTK <code>createSlice</code> — action/reducer boilerplate'ni avtomatlashtiradi, Immer bilan xavfsiz "mutatsiya" yozish imkonini beradi</li>
</ul>
"""

L1_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 1: Nega Redux Toolkit? Context'ning chegaralari
// ════════════════════════════════════════════════════════════════════

import { createContext, useContext, useState, useEffect } from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) Muammoni ko'rsatish — bitta Context, ikkita mustaqil qiymat
// ─────────────────────────────────────────────────────────────────────

const AppContext = createContext(null);

function ThemeLabel() {
  const { theme } = useContext(AppContext);
  console.log("🎨 ThemeLabel qayta render bo'ldi");
  return <p>Mavzu: {theme}</p>;
}

function CounterLabel() {
  const { count } = useContext(AppContext);
  console.log("🔢 CounterLabel qayta render bo'ldi");
  return <p>Son: {count}</p>;
}

function ContextMuammosiDemo() {
  const [theme, setTheme] = useState("light");
  const [count, setCount] = useState(0);

  return (
    <AppContext.Provider value={{ theme, count }}>
      <ThemeLabel />
      <CounterLabel />
      <button onClick={() => setCount(c => c + 1)}>+1 (faqat son)</button>
      <button onClick={() => setTheme(t => t === "light" ? "dark" : "light")}>
        Mavzuni almashtirish
      </button>
    </AppContext.Provider>
  );
}

// Konsolga qarang: "+1" bossangiz ham ThemeLabel qayta render bo'ladi —
// garchi u faqat theme'ni ishlatsa ham.

// ─────────────────────────────────────────────────────────────────────
// 2) Muammoni kattalashtirish — 50 ta obunachi
// ─────────────────────────────────────────────────────────────────────

function ManyThemeLabels() {
  return (
    <>
      {Array.from({ length: 50 }).map((_, i) => (
        <ThemeLabel key={i} />
      ))}
    </>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) Ataylab xato — "hamma narsani bitta Context'ga tiqish"
// ─────────────────────────────────────────────────────────────────────

const MegaContext = createContext(null);

function MegaProviderXato({ children }) {
  const [user] = useState({ name: "Olim" });          // kamdan-kam o'zgaradi
  const [theme, setTheme] = useState("light");         // kamdan-kam o'zgaradi
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 }); // HAR harakatda!

  useEffect(() => {
    const handler = (e) => setMousePos({ x: e.clientX, y: e.clientY });
    window.addEventListener("mousemove", handler);
    return () => window.removeEventListener("mousemove", handler);
  }, []);

  return (
    <MegaContext.Provider value={{ user, theme, mousePos }}>
      {children}
    </MegaContext.Provider>
  );
}

function UserBadge() {
  const { user } = useContext(MegaContext);
  console.log("👤 UserBadge qayta render bo'ldi (mousePos o'zgargani uchun ham!)");
  return <span>{user.name}</span>;
}

// ─────────────────────────────────────────────────────────────────────
// 4) Yechim yo'nalishi — Redux Toolkit useSelector (keyingi darsda to'liq)
// ─────────────────────────────────────────────────────────────────────

/*
function ThemeLabelRTK() {
  // faqat theme slice'iga obuna — mousePos yoki boshqa state o'zgarsa,
  // bu komponent qayta render BO'LMAYDI.
  const theme = useSelector((state) => state.app.theme);
  return <p>Mavzu: {theme}</p>;
}
*/

// ─────────────────────────────────────────────────────────────────────
// 5) RTK vs klassik Redux — boilerplate solishtiruvi
// ─────────────────────────────────────────────────────────────────────

// Klassik Redux:
const INCREMENT = "counter/increment";
function increment() { return { type: INCREMENT }; }
function counterReducerClassic(state = { value: 0 }, action) {
  switch (action.type) {
    case INCREMENT:
      return { ...state, value: state.value + 1 };
    default:
      return state;
  }
}

/*
// Redux Toolkit (keyingi darsda import qilamiz):
const counterSlice = createSlice({
  name: "counter",
  initialState: { value: 0 },
  reducers: {
    increment: (state) => { state.value += 1; }, // Immer — xavfsiz "mutatsiya"
  },
});
*/
"""

L1_EX = [
    {
        "title": "Context obunachilari qanday yangilanadi?",
        "description": (
            "ThemeContext value'si o'zgarsa (masalan, faqat `theme` maydoni), "
            "ushbu Context'ga obuna bo'lgan (useContext orqali) barcha "
            "komponentlar nima qiladi?"
        ),
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat theme'ni ishlatgan komponent qayta render bo'ladi",
            "Contextga obuna bo'lgan BARCHA komponentlar qayta render bo'ladi, "
            "hatto ular theme'ni ishlatmasa ham",
            "Hech biri qayta render bo'lmaydi",
            "Faqat Provider qayta render bo'ladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Context — bu bitta 'value' obyekt. React qaysi maydon o'zgarganini bilmaydi.",
        "explanation": (
            "Context Provider har safar value o'zgarganda, useContext qilingan "
            "BARCHA komponentlarni qayta render qiladi — value obyekti ichida "
            "qaysi maydon o'zgarganidan qat'iy nazar."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Context qachon muammoga aylanadi?",
        "description": "Qaysi holatda Context'dan foydalanish ko'proq performance muammosi keltirib chiqaradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Kamdan-kam o'zgaruvchi global sozlama (masalan, til)",
            "Har soniyada o'zgaruvchi qiymat (masalan, sichqoncha pozitsiyasi) "
            "ko'plab komponentlar bilan bir Context ichida",
            "Bitta komponent ichidagi local state",
            "Statik konfiguratsiya obyekti",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Nechog'lik tez-tez o'zgaradi va nechta komponent obuna bo'lgan — shu ikkisi narxni belgilaydi.",
        "explanation": (
            "Tez-tez o'zgaruvchi qiymat + ko'p sonli obunachi komponent = har "
            "o'zgarishda katta qayta render kaskadi. Bu aynan Redux kabi "
            "tashqi do'kon kerak bo'ladigan holat."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Context yangilanish zanjirini to'g'ri tartibda joylang",
        "description": "Provider value'si o'zgarganda nima sodir bo'lishini to'g'ri ketma-ketlikda joylang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Provider value obyekti yangilanadi",
            "React barcha useContext qilgan komponentlarni belgilaydi",
            "Har bir belgilangan komponent qayta render bo'ladi",
            "React DOM'ni solishtiradi (diffing)",
            "Faqat haqiqatan o'zgargan DOM qismlari yangilanadi",
        ],
        "correct_order": [
            "Provider value obyekti yangilanadi",
            "React barcha useContext qilgan komponentlarni belgilaydi",
            "Har bir belgilangan komponent qayta render bo'ladi",
            "React DOM'ni solishtiradi (diffing)",
            "Faqat haqiqatan o'zgargan DOM qismlari yangilanadi",
        ],
        "hint": "Context — value darajasida ishlaydi, DOM darajasida emas.",
        "explanation": (
            "Context'ning qimmati — komponent funksiyalarini qayta chaqirishda "
            "(render), DOM'ni yangilashda emas. DOM diffing keyingi, alohida bosqich."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega katta ilovalarda faqat Context yetarli emas?",
        "description": (
            "O'z so'zlaringiz bilan tushuntiring: nima uchun katta, tez-tez "
            "yangilanadigan state'ga ega ilovalarda dasturchilar Context "
            "o'rniga Redux Toolkit kabi tashqi state-management kutubxonasini "
            "tanlashadi?"
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Context har bir yangilanishda barcha obunachilarni qayta render "
            "qiladi, chunki u qaysi maydon o'zgarganini farqlay olmaydi. Katta "
            "ilovada bu ko'plab keraksiz qayta render va sekinlashuvga olib "
            "keladi. Redux Toolkit kabi tashqi do'kon esa selector orqali "
            "faqat kerakli state qismiga obuna bo'lish imkonini beradi — shu "
            "bilan faqat haqiqatan bog'liq komponentlar qayta render bo'ladi. "
            "Bundan tashqari Redux DevTools, middleware kabi tooling beradi."
        ),
        "hint": "Re-render performance, tanlab obuna bo'lish, va debugging tooling haqida o'ylab ko'ring.",
        "difficulty_level": "Medium",
        "points": 4,
    },
]


L2_TEXT = """\
<h2>configureStore + createSlice — Redux Toolkit'ni ishga tushirish</h2>

<pre class="mermaid">
flowchart LR
    S["createSlice"] -->|avtomatik yaratadi| AC["action creators"]
    S -->|avtomatik yaratadi| R["reducer"]
    R -->|configureStore ichida| ST["store"]
    ST -->|Provider orqali| APP["butun ilova"]
</pre>

<p>O'tgan darsda va'da qildik: <code>useSelector</code> faqat kerakli qismga obuna bo'ladi. Endi buni haqiqatan quramiz — o'tgan darsdagi <code>ThemeLabel</code> / <code>CounterLabel</code> muammosini Redux Toolkit bilan yechamiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — o'rnatish va birinchi slice</h4>
<pre><code>// Terminal:
npm install @reduxjs/toolkit react-redux</code></pre>

<pre><code>// src/features/appSlice.js
import { createSlice } from '@reduxjs/toolkit';

const appSlice = createSlice({
  name: 'app',
  initialState: {
    theme: 'light',
    count: 0,
  },
  reducers: {
    toggleTheme: (state) =&gt; {
      state.theme = state.theme === 'light' ? 'dark' : 'light'; // "mutatsiya" ko'rinishida
    },
    increment: (state) =&gt; {
      state.count += 1;
    },
  },
});

export const { toggleTheme, increment } = appSlice.actions;
export default appSlice.reducer;</code></pre>

<p>Diqqat: <code>state.count += 1</code> — bu haqiqiy mutatsiyaga o'xshaydi! Lekin xavotir olmang — buning sababini pastda tushuntiramiz (Immer).</p>

<h4>BLOKA 2 — store yaratish va Provider bilan ulash</h4>
<pre><code>// src/store.js
import { configureStore } from '@reduxjs/toolkit';
import appReducer from './features/appSlice';

export const store = configureStore({
  reducer: {
    app: appReducer, // state.app.theme, state.app.count
  },
});</code></pre>

<pre><code>// src/main.jsx
import { Provider } from 'react-redux';
import { store } from './store';

ReactDOM.createRoot(document.getElementById('root')).render(
  &lt;Provider store={store}&gt;
    &lt;App /&gt;
  &lt;/Provider&gt;
);</code></pre>

<h4>BLOKA 3 — o'tgan darsning muammosini yechish</h4>
<pre><code>import { useSelector, useDispatch } from 'react-redux';
import { toggleTheme, increment } from './features/appSlice';

function ThemeLabel() {
  const theme = useSelector((state) =&gt; state.app.theme); // FAQAT theme'ga obuna
  console.log("🎨 ThemeLabel qayta render bo'ldi");
  return &lt;p&gt;Mavzu: {theme}&lt;/p&gt;;
}

function CounterLabel() {
  const count = useSelector((state) =&gt; state.app.count); // FAQAT count'ga obuna
  console.log("🔢 CounterLabel qayta render bo'ldi");
  return &lt;p&gt;Son: {count}&lt;/p&gt;;
}

function App() {
  const dispatch = useDispatch();
  return (
    &lt;&gt;
      &lt;ThemeLabel /&gt;
      &lt;CounterLabel /&gt;
      &lt;button onClick={() =&gt; dispatch(increment())}&gt;+1 (faqat son)&lt;/button&gt;
    &lt;/&gt;
  );
}</code></pre>

<p>Endi <strong>+1</strong> tugmasini bosing va konsolga qarang: faqat <code>🔢 CounterLabel qayta render bo'ldi</code> chiqadi. <code>ThemeLabel</code> — <strong>umuman qayta render bo'lmaydi</strong>, chunki <code>state.app.theme</code> o'zgarmadi. Bu — o'tgan darsdagi Context muammosining aynan yechimi.</p>

<h3>🐛 Ataylab xato — Provider'ni unutish</h3>
<pre><code>// main.jsx — Provider yo'q!
ReactDOM.createRoot(document.getElementById('root')).render(
  &lt;App /&gt; {/* ❌ store bilan o'ralmagan */}
);</code></pre>

<p><code>App</code> ichida <code>useSelector</code> chaqirilsa:</p>
<pre><code>Error: could not find react-redux context value; please ensure the component is wrapped in a &lt;Provider&gt;</code></pre>

<p><strong>Sabab:</strong> <code>react-redux</code>ning <code>useSelector</code>/<code>useDispatch</code> — store'ni topish uchun ichki Context'dan foydalanadi (ha, Context — lekin boshqacha rolda, pastda tushuntiramiz). <code>&lt;Provider store={store}&gt;</code> bo'lmasa, bu ichki Context bo'sh bo'ladi va xato chiqadi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Kutib turing — Redux ham Context ishlatadimi?! O'tgan darsda uni tanqid qildik-ku!</h4>
<p>Ha, <code>react-redux</code> ichkarida Context ishlatadi — lekin butunlay boshqa maqsadda. Context orqali faqat <strong>store obyektining o'zi</strong> (bitta, hech qachon o'zgarmaydigan referens) uzatiladi. Component qayta render bo'lish-bo'lmasligi Context orqali emas — <code>useSelector</code>ning <strong>o'z ichki obuna mexanizmi</strong> orqali hal qilinadi: u store'ga to'g'ridan-to'g'ri obuna bo'ladi va faqat o'zi tanlagan qism o'zgarsa, komponentni qayta render qilishga majbur qiladi. Context bu yerda faqat "quvur" (store'ni uzatish uchun), performance yechimi emas.</p>

<h4>2. configureStore anatomiyasi</h4>
<pre><code>configureStore({
  reducer: {
    app: appReducer,     // state.app.*
    cart: cartReducer,   // state.cart.* (keyingi darslarda)
  },
});</code></pre>
<p><code>reducer</code> obyektidagi har bir kalit — <code>state</code> ichida shu nomdagi bo'lim bo'ladi. <code>configureStore</code> — bundan tashqari, avtomatik ravishda: Redux DevTools'ni yoqadi, va foydali middleware'larni (masalan, immutability tekshiruvi dev rejimida) qo'shadi. Klassik Redux'da bularning barchasi qo'lda sozlanardi.</p>

<h4>3. createSlice anatomiyasi</h4>
<pre><code>createSlice({
  name: 'app',           // action type prefiksi: "app/increment"
  initialState: {...},   // boshlang'ich state
  reducers: {             // har biri = bitta action + bitta reducer logikasi
    increment: (state) =&gt; { state.count += 1 },
  },
});</code></pre>
<p><code>createSlice</code> avtomatik yaratadi:</p>
<ul>
<li><strong>action creator</strong>: <code>appSlice.actions.increment()</code> → <code>{ type: "app/increment" }</code></li>
<li><strong>reducer funksiyasi</strong>: <code>appSlice.reducer</code> — <code>configureStore</code>ga beriladi</li>
</ul>

<h4>4. Immer — nega "mutatsiya" xavfsiz?</h4>
<p><code>createSlice</code> ichida Redux Toolkit avtomatik ravishda <strong>Immer</strong> kutubxonasidan foydalanadi. Siz <code>state.count += 1</code> deb yozganingizda, aslida:</p>
<ul>
<li>Immer sizga "draft" (qoralama) versiyasini beradi</li>
<li>Siz draft'ni "mutatsiya qilganingizda", Immer buni kuzatib boradi</li>
<li>Funksiya tugagach, Immer draft'dagi o'zgarishlar asosida <strong>yangi, immutable state</strong> yaratadi</li>
</ul>
<p>Ya'ni — kod mutatsiyaga o'xshaydi, lekin natija har doim yangi obyekt. Bitta qoida: <strong>reducer yoki yangi state qaytaring, yoki draft'ni mutatsiya qiling — ikkalasini birga qilmang.</strong></p>
<pre><code>// ✅ Draft mutatsiya (Immer boshqaradi)
increment: (state) =&gt; { state.count += 1; }

// ✅ Yangi obyekt qaytarish (ham to'g'ri)
increment: (state) =&gt; ({ ...state, count: state.count + 1 })

// ❌ Ikkalasini aralashtirish — xato xatti-harakat
increment: (state) =&gt; { state.count += 1; return { ...state }; }</code></pre>

<h4>5. Provider — store'ni butun ilovaga ulash</h4>
<p><code>&lt;Provider store={store}&gt;</code> — daraxtning eng tepasida, bir marta. Ichidagi har qanday komponent (chuqurligidan qat'iy nazar) <code>useSelector</code>/<code>useDispatch</code> orqali store'ga kira oladi — props orqali uzatishga hojat yo'q.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>createSlice</code> — name, initialState, reducers'dan action creator + reducer avtomatik yasaydi</li>
<li>✅ <code>configureStore</code> — slice reducerlarini birlashtiradi, DevTools va middleware'ni avtomatik sozlaydi</li>
<li>✅ Immer — reducer ichida "mutatsiya kabi" yozish xavfsiz, chunki draft ustida ishlaydi va yangi immutable state qaytaradi</li>
<li>✅ <code>&lt;Provider store={store}&gt;</code> — butun ilova store'ga kira oladi, lekin bu faqat "quvur"; qayta render — useSelector'ning o'z obunasi orqali</li>
<li>✅ Provider'siz <code>useSelector</code>/<code>useDispatch</code> — "could not find react-redux context value" xatosi</li>
</ul>
"""

L2_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 2: configureStore + createSlice
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) src/features/appSlice.js
// ─────────────────────────────────────────────────────────────────────

import { createSlice, configureStore } from '@reduxjs/toolkit';
import { useSelector, useDispatch, Provider } from 'react-redux';

const appSlice = createSlice({
  name: 'app',
  initialState: {
    theme: 'light',
    count: 0,
  },
  reducers: {
    toggleTheme: (state) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
    },
    increment: (state) => {
      state.count += 1;
    },
  },
});

export const { toggleTheme, increment } = appSlice.actions;

// ─────────────────────────────────────────────────────────────────────
// 2) src/store.js
// ─────────────────────────────────────────────────────────────────────

const store = configureStore({
  reducer: {
    app: appSlice.reducer,
  },
});

// ─────────────────────────────────────────────────────────────────────
// 3) O'tgan darsning muammosini yechish — faqat kerakli qismga obuna
// ─────────────────────────────────────────────────────────────────────

function ThemeLabel() {
  const theme = useSelector((state) => state.app.theme);
  console.log("🎨 ThemeLabel qayta render bo'ldi");
  return <p>Mavzu: {theme}</p>;
}

function CounterLabel() {
  const count = useSelector((state) => state.app.count);
  console.log("🔢 CounterLabel qayta render bo'ldi");
  return <p>Son: {count}</p>;
}

function AppIchki() {
  const dispatch = useDispatch();
  return (
    <>
      <ThemeLabel />
      <CounterLabel />
      <button onClick={() => dispatch(increment())}>+1 (faqat son)</button>
      <button onClick={() => dispatch(toggleTheme())}>Mavzuni almashtirish</button>
    </>
  );
}

function App() {
  return (
    <Provider store={store}>
      <AppIchki />
    </Provider>
  );
}

// Konsolga qarang: "+1" bossangiz — faqat CounterLabel qayta render bo'ladi.
// ThemeLabel butunlay tinch qoladi. Bu — 1-darsdagi Context muammosining yechimi.

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato — Provider'ni unutish
// ─────────────────────────────────────────────────────────────────────

/*
function AppXato() {
  return <AppIchki />; // ❌ Provider yo'q
}
// AppIchki ichidagi useSelector chaqirilganda:
// Error: could not find react-redux context value;
// please ensure the component is wrapped in a <Provider>
*/

// ─────────────────────────────────────────────────────────────────────
// 5) Immer — mutatsiya kabi yozish, aslida immutable
// ─────────────────────────────────────────────────────────────────────

const demoSlice = createSlice({
  name: 'demo',
  initialState: { count: 0 },
  reducers: {
    // ✅ Draft mutatsiya — Immer boshqaradi, xavfsiz
    incrementOk: (state) => { state.count += 1; },

    // ✅ Yangi obyekt qaytarish — bu ham to'g'ri
    incrementAlsoOk: (state) => ({ ...state, count: state.count + 1 }),

    // ❌ Ikkalasini aralashtirish — noto'g'ri xatti-harakat
    // incrementXato: (state) => { state.count += 1; return { ...state }; }
  },
});
"""

L2_EX = [
    {
        "title": "createSlice nima avtomatik yaratadi?",
        "description": "createSlice({ name, initialState, reducers }) chaqirilganda, u nimalarni avtomatik yaratadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat reducer funksiyasini",
            "Faqat action creatorlarni",
            "Action creatorlarni HAM, reducer funksiyasini HAM",
            "Hech narsani — ularni qo'lda yozish kerak",
        ],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "appSlice.actions va appSlice.reducer — ikkalasi ham createSlice natijasida keladi.",
        "explanation": (
            "createSlice — reducers obyektidagi har bir funksiya uchun mos "
            "action creator (appSlice.actions.increment) VA butun slice uchun "
            "bitta reducer funksiyasini (appSlice.reducer) avtomatik yaratadi."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Provider ichida qaysi Context ishlatiladi?",
        "description": (
            "1-darsda Context'ning re-render muammosini ko'rdik. react-redux "
            "ham ichkarida Context ishlatadi. Bu qanday farq qiladi?"
        ),
        "exercise_type": "multiple_choice",
        "options": [
            "Farq qilmaydi — bir xil muammo bor",
            "Context faqat store obyektining o'zini (o'zgarmas referens) "
            "uzatadi; qayta render useSelector'ning o'z obunasi orqali "
            "boshqariladi",
            "react-redux Context umuman ishlatmaydi",
            "Context har bir state o'zgarishida yangi qiymat oladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Store obyektining o'zi qachon o'zgaradi? Deyarli hech qachon.",
        "explanation": (
            "react-redux Context orqali faqat bitta, barqaror store referensini "
            "uzatadi. Qayta renderni store obyekti emas, useSelector'ning ichki "
            "obunasi (subscription) hal qiladi — shuning uchun 1-darsdagi "
            "muammo bu yerda yo'q."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "RTK sozlash ketma-ketligini to'g'ri joylang",
        "description": "Yangi loyihada Redux Toolkit'ni sozlashning to'g'ri tartibini joylang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "npm install @reduxjs/toolkit react-redux",
            "createSlice bilan slice yaratish",
            "configureStore bilan reducerlarni birlashtirish",
            "<Provider store={store}> bilan App'ni o'rash",
            "useSelector / useDispatch bilan komponentlarda ishlatish",
        ],
        "correct_order": [
            "npm install @reduxjs/toolkit react-redux",
            "createSlice bilan slice yaratish",
            "configureStore bilan reducerlarni birlashtirish",
            "<Provider store={store}> bilan App'ni o'rash",
            "useSelector / useDispatch bilan komponentlarda ishlatish",
        ],
        "hint": "Avval kutubxona, keyin state ta'rifi, keyin store, keyin ulash, keyin foydalanish.",
        "explanation": "",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega reducer ichida state.count += 1 xavfsiz?",
        "description": (
            "createSlice'dagi reducer funksiyasi ichida `state.count += 1` "
            "yozish React/Redux'ning \"never mutate state\" qoidasini "
            "buzayotganday ko'rinadi. Nega bu aslida xavfsiz? O'z so'zlaringiz "
            "bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "createSlice ichida Redux Toolkit Immer kutubxonasidan foydalanadi. "
            "Reducer ichidagi `state` aslida haqiqiy state emas, balki Immer "
            "bergan \"draft\" (qoralama) versiya. Siz draft'ni mutatsiya qilganda, "
            "Immer buni kuzatib boradi va reducer tugagach avtomatik ravishda "
            "yangi, immutable state obyektini yaratadi. Shuning uchun kod "
            "tashqi ko'rinishda mutatsiyaga o'xshaydi, lekin natijada har doim "
            "yangi obyekt qaytariladi va asl state o'zgarmaydi."
        ),
        "hint": "Immer, draft, va reducer tugagandan keyin nima sodir bo'lishi haqida o'ylab ko'ring.",
        "difficulty_level": "Medium",
        "points": 4,
    },
]


L3_TEXT = """\
<h2>useSelector / useDispatch chuqurroq — payload'li action'lar va selector tuzoqlari</h2>

<pre class="mermaid">
flowchart LR
    UI["dispatch(addTodo({text}))"] --> R["reducer: action.payload'ni o'qiydi"]
    R --> ST["store yangilanadi"]
    ST -->|faqat mos selector| SEL["useSelector qayta hisoblanadi"]
</pre>

<p>1-2 darslarda <code>increment()</code> va <code>toggleTheme()</code>ni ko'rdik — ularga hech qanday ma'lumot uzatilmagan. Aksariyat real action'lar esa <strong>payload</strong> (ma'lumot) bilan keladi: "shu matnli todo qo'sh", "shu id'li elementni o'chir". Bu darsda buni va selector'lardagi keng tarqalgan tuzoqni ko'ramiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — payload'li action'lar</h4>
<pre><code>const todosSlice = createSlice({
  name: 'todos',
  initialState: { items: [] },
  reducers: {
    addTodo: (state, action) =&gt; {
      // action.payload — dispatch qilinganda uzatilgan ma'lumot
      state.items.push({ id: Date.now(), text: action.payload, done: false });
    },
    toggleTodo: (state, action) =&gt; {
      const todo = state.items.find(t =&gt; t.id === action.payload);
      if (todo) todo.done = !todo.done;
    },
    removeTodo: (state, action) =&gt; {
      state.items = state.items.filter(t =&gt; t.id !== action.payload);
    },
  },
});

export const { addTodo, toggleTodo, removeTodo } = todosSlice.actions;</code></pre>

<h4>BLOKA 2 — komponentda ishlatish</h4>
<pre><code>function TodoForm() {
  const [matn, setMatn] = useState('');
  const dispatch = useDispatch();

  const qoshish = () =&gt; {
    if (!matn.trim()) return;
    dispatch(addTodo(matn)); // addTodo('Non olish') → { type: 'todos/addTodo', payload: 'Non olish' }
    setMatn('');
  };

  return (
    &lt;div&gt;
      &lt;input value={matn} onChange={e =&gt; setMatn(e.target.value)} /&gt;
      &lt;button onClick={qoshish}&gt;Qo'shish&lt;/button&gt;
    &lt;/div&gt;
  );
}

function TodoItem({ todo }) {
  const dispatch = useDispatch();
  return (
    &lt;li style={{ textDecoration: todo.done ? 'line-through' : 'none' }}&gt;
      &lt;input type="checkbox" checked={todo.done}
        onChange={() =&gt; dispatch(toggleTodo(todo.id))} /&gt;
      {todo.text}
      &lt;button onClick={() =&gt; dispatch(removeTodo(todo.id))}&gt;x&lt;/button&gt;
    &lt;/li&gt;
  );
}</code></pre>

<h4>BLOKA 3 — hisoblangan (derived) qiymatni selector'da olish</h4>
<pre><code>function QolganSoni() {
  // Selector ichida .filter() — HAR safar YANGI array qaytaradi!
  const qolgan = useSelector((state) =&gt;
    state.todos.items.filter((t) =&gt; !t.done)
  );
  console.log("📋 QolganSoni qayta render bo'ldi");
  return &lt;p&gt;Bajarilmagan: {qolgan.length}&lt;/p&gt;;
}</code></pre>

<p>Bu ishlaydi, lekin — <code>todos</code> bilan bog'liq bo'lmagan boshqa har qanday action dispatch qilinganda ham (masalan, <code>theme</code>ni almashtirsangiz) bu komponent qayta render bo'ladimi? Keling tekshiramiz.</p>

<h3>🐛 Ataylab xato — selector har safar yangi referens qaytaradi</h3>
<pre><code>// theme'ni almashtiring (todos bilan aloqasi yo'q!) va konsolga qarang:
dispatch(toggleTheme());

// Natija konsolda:
// 📋 QolganSoni qayta render bo'ldi   ← nega?! todos o'zgarmadi-ku!</code></pre>

<p><strong>Sabab:</strong> <code>useSelector</code> — har bir action dispatch qilinganda selector funksiyasini <strong>qayta chaqiradi</strong> va natijani oldingi natija bilan <code>===</code> orqali solishtiradi. <code>.filter()</code> — har chaqirilganda <strong>yangi array obyekti</strong> yaratadi, hatto ichidagi elementlar bir xil bo'lsa ham. <code>yangiArray === eskiArray</code> — <strong>har doim false</strong>. Shuning uchun React bu komponentni "o'zgargan" deb hisoblaydi va qayta render qiladi — <code>todos</code> haqiqatan o'zgarmagan bo'lsa ham.</p>

<p>Bu — kichik ilovada sezilmaydi, lekin katta ilovada har bir action HAR BIR shunday selector'ni qayta render qildiradi. (6-darsda <code>createSelector</code> bilan buni to'g'ri yechamiz — hozircha muammoni tanib olish yetarli.)</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. action.payload — konventsiya, majburiyat emas</h4>
<p><code>createSlice</code>da reducer ikkinchi argument sifatida <code>action</code> obyektini oladi: <code>{ type: 'todos/addTodo', payload: ... }</code>. <code>action.payload</code> — Redux Toolkit'ning standart konventsiyasi (istalgan nom qo'yish mumkin edi, lekin RTK har doim <code>payload</code> deb nomlaydi).</p>

<h4>2. Bir nechta argument kerak bo'lsa</h4>
<pre><code>// payload — bitta qiymat bo'lishi shart, lekin bu qiymat obyekt bo'lishi mumkin:
dispatch(addTodo({ text: matn, priority: 'high' }));

// reducerda:
addTodo: (state, action) =&gt; {
  state.items.push({
    id: Date.now(),
    text: action.payload.text,
    priority: action.payload.priority,
    done: false,
  });
}</code></pre>

<h4>3. useSelector — HAR bir dispatch'da qayta chaqiriladi</h4>
<p>Bu — <code>useSelector</code>ning ishlash tamoyili: store'ga har qanday action kelganda, <strong>har bir</strong> komponentdagi <strong>har bir</strong> selector qayta hisoblanadi (arzon, tez amal). Faqat natija <code>===</code> solishtiruvda farqli bo'lsagina, komponent qayta render bo'ladi. Muammo selector qayta chaqirilishida emas — <strong>yangi referens qaytarishida</strong>.</p>

<h4>4. Qaysi selector'lar xavfli?</h4>
<table>
<tr><th>Xavfsiz (primitivlarni qaytaradi)</th><th>Xavfli (har safar yangi referens)</th></tr>
<tr><td><code>state =&gt; state.todos.items.length</code></td><td><code>state =&gt; state.todos.items.filter(...)</code></td></tr>
<tr><td><code>state =&gt; state.app.theme</code></td><td><code>state =&gt; ({ theme: state.app.theme })</code> (yangi obyekt!)</td></tr>
<tr><td><code>state =&gt; state.todos.items[0]?.id</code></td><td><code>state =&gt; state.todos.items.map(...)</code></td></tr>
</table>

<h4>5. Vaqtinchalik yechim (to'liq yechim — 6-darsda)</h4>
<p>Hozircha: agar selector <code>.filter()/.map()/.sort()</code> yoki yangi obyekt qaytarsa — ehtiyot bo'ling. Kichik ilovalarda muammo emas, lekin buni <strong>tanib olish</strong> — performance debugging'ning birinchi qadami.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Action'lar <code>action.payload</code> orqali ma'lumot uzatadi — <code>addTodo(matn)</code> → <code>{ type, payload: matn }</code></li>
<li>✅ Payload bir nechta qiymat kerak bo'lsa — obyekt qilib uzatiladi</li>
<li>✅ <code>useSelector</code> HAR bir dispatch'da qayta chaqiriladi, lekin komponent faqat natija <code>===</code> bo'yicha farqli bo'lsa qayta render bo'ladi</li>
<li>✅ <code>.filter()/.map()</code> selector ichida — har safar yangi array/obyekt qaytaradi → keraksiz qayta render</li>
<li>✅ Muammoni tanish: agar selector transformatsiya qilsa (filter/map/yangi obyekt) — ehtiyot bo'ling</li>
</ul>
"""

L3_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 3: useSelector / useDispatch chuqurroq
// ════════════════════════════════════════════════════════════════════

import { createSlice, configureStore } from '@reduxjs/toolkit';
import { useSelector, useDispatch, Provider } from 'react-redux';
import { useState } from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) Payload'li action'lar
// ─────────────────────────────────────────────────────────────────────

const todosSlice = createSlice({
  name: 'todos',
  initialState: { items: [] },
  reducers: {
    addTodo: (state, action) => {
      state.items.push({ id: Date.now(), text: action.payload, done: false });
    },
    toggleTodo: (state, action) => {
      const todo = state.items.find(t => t.id === action.payload);
      if (todo) todo.done = !todo.done;
    },
    removeTodo: (state, action) => {
      state.items = state.items.filter(t => t.id !== action.payload);
    },
  },
});

const themeSlice = createSlice({
  name: 'theme',
  initialState: { value: 'light' },
  reducers: {
    toggleTheme: (state) => { state.value = state.value === 'light' ? 'dark' : 'light'; },
  },
});

export const { addTodo, toggleTodo, removeTodo } = todosSlice.actions;
export const { toggleTheme } = themeSlice.actions;

const store = configureStore({
  reducer: {
    todos: todosSlice.reducer,
    theme: themeSlice.reducer,
  },
});

// ─────────────────────────────────────────────────────────────────────
// 2) Komponentlar — dispatch bilan
// ─────────────────────────────────────────────────────────────────────

function TodoForm() {
  const [matn, setMatn] = useState('');
  const dispatch = useDispatch();

  const qoshish = () => {
    if (!matn.trim()) return;
    dispatch(addTodo(matn));
    setMatn('');
  };

  return (
    <div>
      <input value={matn} onChange={e => setMatn(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && qoshish()} />
      <button onClick={qoshish}>Qo'shish</button>
    </div>
  );
}

function TodoItem({ todo }) {
  const dispatch = useDispatch();
  return (
    <li style={{ textDecoration: todo.done ? 'line-through' : 'none' }}>
      <input type="checkbox" checked={todo.done}
        onChange={() => dispatch(toggleTodo(todo.id))} />
      {todo.text}
      <button onClick={() => dispatch(removeTodo(todo.id))}>x</button>
    </li>
  );
}

function TodoList() {
  const items = useSelector((state) => state.todos.items); // xavfsiz — reducer o'zi yangi array qaytaradi faqat o'zgarganda
  return (
    <ul>
      {items.map(t => <TodoItem key={t.id} todo={t} />)}
    </ul>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) Ataylab xato — selector har safar yangi referens qaytaradi
// ─────────────────────────────────────────────────────────────────────

function QolganSoniXato() {
  // ❌ .filter() har chaqirilganda yangi array — theme o'zgarsa ham re-render qiladi
  const qolgan = useSelector((state) =>
    state.todos.items.filter((t) => !t.done)
  );
  console.log("📋 QolganSoniXato qayta render bo'ldi");
  return <p>Bajarilmagan: {qolgan.length}</p>;
}

// Isbot uchun: ThemeButton bosilganda konsolga qarang —
// QolganSoniXato ham qayta render bo'lganini ko'rasiz, garchi todos o'zgarmagan bo'lsa ham.

function ThemeButton() {
  const dispatch = useDispatch();
  const theme = useSelector((state) => state.theme.value); // xavfsiz — primitiv qiymat
  return (
    <button onClick={() => dispatch(toggleTheme())}>
      Mavzu: {theme} (bosing va konsolga qarang)
    </button>
  );
}

// ✅ Xavfsizroq vaqtinchalik variant — faqat sonni saqlab, filter natijasini emas
function QolganSoniYaxshiroq() {
  const qolganSoni = useSelector((state) =>
    state.todos.items.filter((t) => !t.done).length // son — primitiv, taqqoslash to'g'ri ishlaydi
  );
  console.log("📋 QolganSoniYaxshiroq qayta render bo'ldi (faqat son o'zgarsa)");
  return <p>Bajarilmagan: {qolganSoni}</p>;
}

function App() {
  return (
    <Provider store={store}>
      <TodoForm />
      <TodoList />
      <QolganSoniXato />
      <QolganSoniYaxshiroq />
      <ThemeButton />
    </Provider>
  );
}
"""

L3_EX = [
    {
        "title": "action.payload nima?",
        "description": "dispatch(addTodo('Non olish')) chaqirilganda, reducer ichidagi action obyekti qanday ko'rinishda bo'ladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "{ type: 'todos/addTodo' } — payload yo'q",
            "{ type: 'todos/addTodo', payload: 'Non olish' }",
            "{ payload: 'Non olish' } — type yo'q",
            "'Non olish' — to'g'ridan-to'g'ri string",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "createSlice avtomatik action creator yaratadi: addTodo(x) → { type, payload: x }.",
        "explanation": (
            "createSlice yaratgan action creator chaqirilgan argumentni "
            "avtomatik ravishda `payload` maydoniga joylaydi va `type`ni "
            "slice nomi + reducer nomidan yasaydi."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Selector qachon komponentni qayta render qildiradi?",
        "description": "useSelector — qaysi holatda komponentni qayta render qilishga majbur qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Har safar HAR QANDAY action dispatch qilinganda, natijadan qat'iy nazar",
            "Faqat selector natijasi oldingisidan === bo'yicha farqli bo'lsa",
            "Faqat komponent birinchi marta render bo'lganda",
            "Hech qachon avtomatik render bo'lmaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Selector har dispatch'da qayta CHAQIRILADI, lekin qayta RENDER qilish alohida qaror.",
        "explanation": (
            "useSelector har action'da selectorni qayta chaqiradi, lekin "
            "komponent faqat yangi natija bilan eski natija === bo'yicha "
            "farqli bo'lsagina qayta render bo'ladi."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Qaysi selector xavfli (keraksiz re-render beradi)?",
        "description": "Quyidagi selectorlardan qaysi biri har chaqirilganda yangi referens qaytarib, keraksiz qayta renderga sabab bo'lishi mumkin?",
        "exercise_type": "multiple_choice",
        "options": [
            "state => state.todos.items.length",
            "state => state.app.theme",
            "state => state.todos.items.filter(t => !t.done)",
            "state => state.todos.items[0]?.id",
        ],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": ".filter() — har chaqirilganda yangi array yaratadi, kontent bir xil bo'lsa ham.",
        "explanation": (
            ".filter() har safar YANGI array obyekti qaytaradi, hatto natija "
            "mantiqan bir xil bo'lsa ham. Yangi referens !== eski referens, "
            "shuning uchun komponent har dispatch'da qayta render bo'ladi."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega .filter() ishlatgan selector muammo keltirib chiqaradi?",
        "description": (
            "useSelector((state) => state.todos.items.filter(t => !t.done)) — "
            "bu selector nega \"todos bilan aloqasi yo'q\" boshqa action "
            "dispatch qilinganda ham komponentni qayta render qildiradi? "
            "O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "useSelector har bir dispatch qilingan action'dan keyin barcha "
            "selectorlarni qayta chaqiradi, hatto action o'sha state qismiga "
            "aloqasi bo'lmasa ham. .filter() metodi har chaqirilganda yangi "
            "array obyektini yaratadi — hatto ichidagi elementlar avvalgisi "
            "bilan bir xil bo'lsa ham, bu yangi array eski array bilan === "
            "solishtiruvda teng emas. useSelector aynan shu === solishtiruv "
            "orqali qayta render kerakligini aniqlaydi, shuning uchun har "
            "safar \"o'zgargan\" deb hisoblab komponentni qayta render qiladi."
        ),
        "hint": "useSelector qayta renderni qanday aniqlaydi (=== solishtiruv) va .filter() nima qaytaradi haqida o'ylang.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L4_TEXT = """\
<h2>Async holat: createAsyncThunk — yuklash/xato/muvaffaqiyat</h2>

<pre class="mermaid">
flowchart LR
    D["dispatch(fetchUsers())"] --> P["pending: loading=true"]
    P --> F["fulfilled: data keldi"]
    P --> R["rejected: xato"]
    F --> UI1["Ro'yxatni ko'rsatish"]
    R --> UI2["Xato xabarini ko'rsatish"]
</pre>

<p>React Asoslari'da <code>useEffect</code> ichida <code>fetch</code> qilib, <code>loading</code>/<code>error</code>/<code>data</code>ni <code>useState</code> bilan qo'lda boshqargansiz. Bu darsda xuddi shu narsani Redux Toolkit'ning <code>createAsyncThunk</code> bilan qilamiz — endi loading/error/data butun ilova bo'ylab bir joyda, har qanday komponentdan ko'rinadigan bo'ladi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — eslatma: eski usul (useEffect + useState)</h4>
<pre><code>// React Asoslari'dagi tanish usul:
function FoydalanuvchilarEski() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() =&gt; {
    fetch('/api/users')
      .then(res =&gt; res.json())
      .then(setData)
      .catch(err =&gt; setError(err.message))
      .finally(() =&gt; setLoading(false));
  }, []);

  // Muammo: bu state faqat SHU komponentda. Boshqa komponent ham
  // foydalanuvchilar ro'yxatini kerak qilsa — yana fetch qilishi kerak.
}</code></pre>

<h4>BLOKA 2 — createAsyncThunk bilan</h4>
<pre><code>import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

// Birinchi argument — action type prefiksi, ikkinchisi — async funksiya
export const fetchUsers = createAsyncThunk(
  'users/fetchUsers',
  async () =&gt; {
    const res = await fetch('/api/users');
    if (!res.ok) throw new Error('Server xatosi');
    return res.json(); // bu — fulfilled action.payload bo'ladi
  }
);</code></pre>

<p><code>createAsyncThunk</code> — bitta funksiyadan <strong>3 ta action type</strong> avtomatik yasaydi: <code>users/fetchUsers/pending</code>, <code>users/fetchUsers/fulfilled</code>, <code>users/fetchUsers/rejected</code>.</p>

<h4>BLOKA 3 — slice'da qabul qilish (extraReducers)</h4>
<pre><code>const usersSlice = createSlice({
  name: 'users',
  initialState: { items: [], loading: false, error: null },
  reducers: {}, // oddiy action yo'q — hammasi thunk orqali
  extraReducers: (builder) =&gt; {
    builder
      .addCase(fetchUsers.pending, (state) =&gt; {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) =&gt; {
        state.loading = false;
        state.items = action.payload; // thunk qaytargan JSON
      })
      .addCase(fetchUsers.rejected, (state, action) =&gt; {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});</code></pre>

<pre><code>function FoydalanuvchilarYangi() {
  const dispatch = useDispatch();
  const { items, loading, error } = useSelector((state) =&gt; state.users);

  useEffect(() =&gt; {
    dispatch(fetchUsers());
  }, [dispatch]);

  if (loading) return &lt;p&gt;⏳ Yuklanmoqda...&lt;/p&gt;;
  if (error) return &lt;p&gt;❌ Xato: {error}&lt;/p&gt;;
  return &lt;ul&gt;{items.map(u =&gt; &lt;li key={u.id}&gt;{u.name}&lt;/li&gt;)}&lt;/ul&gt;;
}</code></pre>

<p>Endi <strong>istalgan boshqa komponent</strong> ham <code>useSelector(state =&gt; state.users)</code> orqali xuddi shu ma'lumotga, xuddi shu loading holatiga kira oladi — qayta fetch qilmasdan.</p>

<h3>🐛 Ataylab xato — rejected holatini unutish</h3>
<pre><code>const usersSlice = createSlice({
  name: 'users',
  initialState: { items: [], loading: false, error: null },
  reducers: {},
  extraReducers: (builder) =&gt; {
    builder
      .addCase(fetchUsers.pending, (state) =&gt; { state.loading = true; })
      .addCase(fetchUsers.fulfilled, (state, action) =&gt; {
        state.loading = false;
        state.items = action.payload;
      });
      // ❌ .addCase(fetchUsers.rejected, ...) YO'Q!
  },
});</code></pre>

<p><strong>Natija:</strong> Server xato qaytarsa (masalan, 500), <code>rejected</code> action dispatch bo'ladi, lekin uni hech kim ushlamaydi. <code>state.loading</code> — <strong>hech qachon <code>false</code>ga qaytmaydi</strong>, chunki faqat <code>fulfilled</code> uni <code>false</code> qiladi. Foydalanuvchi ekranda abadiy "⏳ Yuklanmoqda..." ko'radi — hech qanday xato ko'rinmaydi, hech qanday konsol xatosi ham yo'q. Bu — <strong>eng xavfli</strong> turdagi bug: jim, sekin, sababi aniq ko'rinmaydigan.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. createAsyncThunk — 3 action, 1 funksiya</h4>
<table>
<tr><th>Action</th><th>Qachon</th><th>action.payload / action.error</th></tr>
<tr><td><code>pending</code></td><td>Funksiya chaqirilgan zahoti</td><td>yo'q</td></tr>
<tr><td><code>fulfilled</code></td><td>Promise muvaffaqiyatli tugasa</td><td><code>payload</code> = qaytarilgan qiymat</td></tr>
<tr><td><code>rejected</code></td><td>Promise reject bo'lsa yoki throw</td><td><code>error.message</code> = xato matni</td></tr>
</table>

<h4>2. extraReducers — nega alohida?</h4>
<p><code>reducers</code> obyekti — faqat <strong>siz o'zingiz</strong> yaratgan action'lar uchun (masalan, <code>increment</code>). <code>extraReducers</code> — <strong>boshqa joyda</strong> yaratilgan action'larga (createAsyncThunk kabi) javob berish uchun. <code>builder.addCase(actionType, handler)</code> — "shu action kelsa, shu funksiyani ishga tushir" degani.</p>

<h4>3. rejectWithValue — maxsus xato xabari</h4>
<pre><code>export const fetchUsers = createAsyncThunk(
  'users/fetchUsers',
  async (_, { rejectWithValue }) =&gt; {
    const res = await fetch('/api/users');
    if (!res.ok) {
      return rejectWithValue(`Server ${res.status} qaytardi`); // action.payload'da bo'ladi
    }
    return res.json();
  }
);

// extraReducers'da:
.addCase(fetchUsers.rejected, (state, action) =&gt; {
  state.error = action.payload ?? action.error.message; // rejectWithValue ustunlik qiladi
})</code></pre>

<h4>4. Nega bu useEffect+useState'dan yaxshiroq?</h4>
<ul>
<li>Ma'lumot <strong>global</strong> — istalgan komponent qayta fetch qilmasdan foydalanadi</li>
<li>Loading/error holati bir joyda — dublikatsiya yo'q</li>
<li>Redux DevTools'da har bir fetch bosqichini (pending/fulfilled/rejected) ko'rish mumkin</li>
</ul>

<h4>5. Keyingi darsda...</h4>
<p>Bu naqsh (thunk + pending/fulfilled/rejected + loading/error state) shu qadar keng tarqalganki, Redux Toolkit uni butunlay avtomatlashtiradigan alohida vosita beradi — <strong>RTK Query</strong>. 5-darsda buni ko'ramiz.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>createAsyncThunk</code> — bitta async funksiyadan pending/fulfilled/rejected action'larini avtomatik yaratadi</li>
<li>✅ <code>extraReducers</code> + <code>builder.addCase</code> — tashqi (thunk kabi) action'larga javob berish uchun</li>
<li>✅ <code>fulfilled</code>ning <code>action.payload</code> — thunk funksiyasi qaytargan qiymat</li>
<li>✅ <code>rejectWithValue</code> — maxsus, aniqroq xato xabari uzatish uchun</li>
<li>✅ <code>rejected</code>ni ushlamaslik — loading holati abadiy "true"da qolib ketishiga olib keladi (jim bug)</li>
</ul>
"""

L4_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 4: Async holat — createAsyncThunk
// ════════════════════════════════════════════════════════════════════

import { createAsyncThunk, createSlice, configureStore } from '@reduxjs/toolkit';
import { useSelector, useDispatch, Provider } from 'react-redux';
import { useEffect } from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) Thunk — 3 action avtomatik: pending / fulfilled / rejected
// ─────────────────────────────────────────────────────────────────────

export const fetchUsers = createAsyncThunk(
  'users/fetchUsers',
  async (_, { rejectWithValue }) => {
    const res = await fetch('/api/users');
    if (!res.ok) {
      return rejectWithValue(`Server ${res.status} qaytardi`);
    }
    return res.json();
  }
);

// ─────────────────────────────────────────────────────────────────────
// 2) Slice — extraReducers bilan thunk'ning 3 holatini ushlash
// ─────────────────────────────────────────────────────────────────────

const usersSlice = createSlice({
  name: 'users',
  initialState: { items: [], loading: false, error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? action.error.message;
      });
  },
});

const store = configureStore({
  reducer: { users: usersSlice.reducer },
});

// ─────────────────────────────────────────────────────────────────────
// 3) Komponent — loading / error / data uch holat
// ─────────────────────────────────────────────────────────────────────

function FoydalanuvchilarRoyxati() {
  const dispatch = useDispatch();
  const { items, loading, error } = useSelector((state) => state.users);

  useEffect(() => {
    dispatch(fetchUsers());
  }, [dispatch]);

  if (loading) return <p>⏳ Yuklanmoqda...</p>;
  if (error) return <p>❌ Xato: {error}</p>;
  return (
    <ul>
      {items.map(u => <li key={u.id}>{u.name}</li>)}
    </ul>
  );
}

function App() {
  return (
    <Provider store={store}>
      <FoydalanuvchilarRoyxati />
    </Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato — rejected holatini unutish
// ─────────────────────────────────────────────────────────────────────

/*
const usersSliceXato = createSlice({
  name: 'users',
  initialState: { items: [], loading: false, error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => { state.loading = true; })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      });
      // ❌ rejected uchun addCase yo'q — server xato qaytarsa,
      // state.loading HECH QACHON false bo'lmaydi. UI abadiy
      // "Yuklanmoqda..." ko'rsatadi, hech qanday xato chiqmasdan.
  },
});
*/
"""

L4_EX = [
    {
        "title": "createAsyncThunk nechta action yaratadi?",
        "description": "createAsyncThunk('users/fetchUsers', asyncFn) chaqirilganda, u avtomatik nechta action type yaratadi va qanday?",
        "exercise_type": "multiple_choice",
        "options": [
            "1 ta — fetchUsers",
            "2 ta — pending va fulfilled",
            "3 ta — pending, fulfilled, rejected",
            "4 ta — pending, loading, fulfilled, rejected",
        ],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Har bir async operatsiya uch holatdan biriga ega bo'lishi mumkin: kutilmoqda, muvaffaqiyatli, xato.",
        "explanation": (
            "createAsyncThunk har doim 3 ta action type yaratadi: "
            "`{prefix}/pending`, `{prefix}/fulfilled`, `{prefix}/rejected` — "
            "Promise'ning uchta mumkin bo'lgan holatiga mos."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Thunk action'larini qayerda ushlaymiz?",
        "description": "createAsyncThunk yaratgan pending/fulfilled/rejected action'lariga slice ichida qayerda javob beriladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "reducers obyekti ichida",
            "extraReducers ichida, builder.addCase orqali",
            "configureStore ichida",
            "useSelector ichida",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "reducers — faqat siz shu slice ichida yaratgan action'lar uchun.",
        "explanation": (
            "reducers — faqat shu slice o'zi yaratgan action'lar uchun. "
            "createAsyncThunk boshqa joyda (thunk ichida) action yaratadi, "
            "shuning uchun ularga extraReducers + builder.addCase orqali "
            "javob beriladi."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Thunk hayot siklini to'g'ri tartibda joylang",
        "description": "dispatch(fetchUsers()) chaqirilgandan API javobi kelgunga qadar bo'lgan voqealarni to'g'ri tartibda joylang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "dispatch(fetchUsers()) chaqiriladi",
            "pending action dispatch bo'ladi — loading=true",
            "async funksiya ichida fetch() ishga tushadi",
            "fulfilled YOKI rejected action dispatch bo'ladi",
            "extraReducers state'ni yangilaydi (loading=false, items yoki error)",
        ],
        "correct_order": [
            "dispatch(fetchUsers()) chaqiriladi",
            "pending action dispatch bo'ladi — loading=true",
            "async funksiya ichida fetch() ishga tushadi",
            "fulfilled YOKI rejected action dispatch bo'ladi",
            "extraReducers state'ni yangilaydi (loading=false, items yoki error)",
        ],
        "hint": "pending — funksiya boshlanishi bilanoq, natija kelishidan OLDIN dispatch bo'ladi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega rejected holatini unutish xavfli?",
        "description": (
            "extraReducers'da faqat pending va fulfilled ushlanib, rejected "
            "uchun addCase yozilmasa, server xato qaytarganda foydalanuvchi "
            "nima ko'radi va nega bu ayniqsa xavfli turdagi bug hisoblanadi? "
            "O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Agar rejected uchun addCase yozilmasa, server xato qaytarganda "
            "rejected action dispatch bo'ladi, lekin uni hech kim ushlamaydi "
            "va state o'zgarmaydi. loading maydoni faqat fulfilled orqali "
            "false qilingani uchun, u abadiy true bo'lib qoladi. Natijada "
            "foydalanuvchi ekranda doimiy \"Yuklanmoqda...\" ko'radi — hech "
            "qanday konsol xatosi yoki ko'zga tashlanadigan nosozlik "
            "bo'lmaydi. Bu ayniqsa xavfli, chunki bug jim (silent) — uni "
            "log'larsiz yoki maxsus testsiz payqash qiyin."
        ),
        "hint": "loading qachon false bo'ladi, va agar fulfilled hech qachon kelmasa nima bo'ladi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


R1_TEXT = """\
<h2>R1 — Modul 1 takrorlash: Todo + Savat (RTK bilan to'liq)</h2>

<p>1-4 darslarni birga ishlatib, ikkita real slice yasaymiz: <strong>Todo</strong> (payload'li action'lar, xavfsiz selector) va <strong>Savat</strong> (createAsyncThunk bilan mahsulotlarni yuklash). Bu — o'tgan 4 darsning hammasi birga.</p>

<h3>Loyihaning maqsadi</h3>
<ul>
<li><code>todosSlice</code> — qo'shish, o'chirish, bajarildi belgisi (2-3 darslar)</li>
<li><code>cartSlice</code> — <code>createAsyncThunk</code> bilan mahsulotlarni "serverdan" yuklash, keyin savatga qo'shish (4-dars)</li>
<li>Yuqorida — global statistika: bajarilmagan todolar soni, savatdagi jami summa</li>
</ul>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — todosSlice</h4>
<p>Reducers: <code>addTodo(text)</code>, <code>toggleTodo(id)</code>, <code>removeTodo(id)</code> — xuddi 3-darsdagidek.</p>

<h4>Vazifa 2 — cartSlice + fetchProducts thunk</h4>
<p><code>createAsyncThunk('cart/fetchProducts', ...)</code> — pending/fulfilled/rejected uchun <code>extraReducers</code>. Fulfilled bo'lganda — <code>state.products</code>ga saqlang. Alohida reducer: <code>addToCart(productId)</code>.</p>

<h4>Vazifa 3 — global statistika</h4>
<p><code>useSelector</code> orqali: bajarilmagan todolar soni (3-darsdagi xavfsiz variant — <code>.length</code> qaytaring, butun array emas!) va savatdagi mahsulotlar soni.</p>

<h4>Vazifa 4 — loading/error UI</h4>
<p>Mahsulotlar yuklanayotganda — "Yuklanmoqda...", xato bo'lsa — xato xabari (4-darsdagi naqsh).</p>

<h3>🐛 Ataylab qiyin: ikkita mustaqil slice, bitta store</h3>
<p>Boshlovchilar ko'pincha ikkita slice'ni bitta katta slice qilib yozishga urinishadi. To'g'ri yondashuv — <strong>har bir domen uchun alohida slice</strong>, <code>configureStore</code>da birlashtiring:</p>
<pre><code>const store = configureStore({
  reducer: {
    todos: todosSlice.reducer,
    cart: cartSlice.reducer,
  },
});</code></pre>

<h3>Boshlang'ich kod</h3>
<pre><code>const todosSlice = createSlice({
  name: 'todos',
  initialState: { items: [] },
  reducers: {
    // Vazifa: addTodo, toggleTodo, removeTodo
  },
});

const cartSlice = createSlice({
  name: 'cart',
  initialState: { products: [], inCart: [], loading: false, error: null },
  reducers: {
    // Vazifa: addToCart
  },
  extraReducers: (builder) =&gt; {
    // Vazifa: fetchProducts.pending/fulfilled/rejected
  },
});</code></pre>

<h3>Yechim</h3>
<details>
<summary>To'liq yechim — avval o'zingiz urinib ko'ring!</summary>
<pre><code>import { createSlice, createAsyncThunk, configureStore } from '@reduxjs/toolkit';
import { useSelector, useDispatch, Provider } from 'react-redux';
import { useEffect, useState } from 'react';

// ─── Todos ───
const todosSlice = createSlice({
  name: 'todos',
  initialState: { items: [] },
  reducers: {
    addTodo: (state, action) =&gt; {
      state.items.push({ id: Date.now(), text: action.payload, done: false });
    },
    toggleTodo: (state, action) =&gt; {
      const t = state.items.find(x =&gt; x.id === action.payload);
      if (t) t.done = !t.done;
    },
    removeTodo: (state, action) =&gt; {
      state.items = state.items.filter(x =&gt; x.id !== action.payload);
    },
  },
});

// ─── Cart ───
export const fetchProducts = createAsyncThunk('cart/fetchProducts', async () =&gt; {
  const res = await fetch('/api/products');
  if (!res.ok) throw new Error('Mahsulotlarni yuklab bo\\'lmadi');
  return res.json();
});

const cartSlice = createSlice({
  name: 'cart',
  initialState: { products: [], inCart: [], loading: false, error: null },
  reducers: {
    addToCart: (state, action) =&gt; { state.inCart.push(action.payload); },
  },
  extraReducers: (builder) =&gt; {
    builder
      .addCase(fetchProducts.pending, (state) =&gt; { state.loading = true; state.error = null; })
      .addCase(fetchProducts.fulfilled, (state, action) =&gt; {
        state.loading = false;
        state.products = action.payload;
      })
      .addCase(fetchProducts.rejected, (state, action) =&gt; {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { addTodo, toggleTodo, removeTodo } = todosSlice.actions;
export const { addToCart } = cartSlice.actions;

const store = configureStore({
  reducer: { todos: todosSlice.reducer, cart: cartSlice.reducer },
});

// ─── Statistika (xavfsiz selectorlar — faqat son qaytaradi) ───
function Statistika() {
  const qolgan = useSelector((state) =&gt;
    state.todos.items.filter(t =&gt; !t.done).length // .length — primitiv, xavfsiz
  );
  const savatSoni = useSelector((state) =&gt; state.cart.inCart.length);
  return &lt;h2&gt;Qolgan: {qolgan} | Savatda: {savatSoni}&lt;/h2&gt;;
}

// ─── Todo UI ───
function TodoApp() {
  const [matn, setMatn] = useState('');
  const items = useSelector((state) =&gt; state.todos.items);
  const dispatch = useDispatch();

  return (
    &lt;div&gt;
      &lt;input value={matn} onChange={e =&gt; setMatn(e.target.value)} /&gt;
      &lt;button onClick={() =&gt; { dispatch(addTodo(matn)); setMatn(''); }}&gt;+&lt;/button&gt;
      &lt;ul&gt;
        {items.map(t =&gt; (
          &lt;li key={t.id} style={{ textDecoration: t.done ? 'line-through' : 'none' }}&gt;
            &lt;input type="checkbox" checked={t.done} onChange={() =&gt; dispatch(toggleTodo(t.id))} /&gt;
            {t.text}
            &lt;button onClick={() =&gt; dispatch(removeTodo(t.id))}&gt;x&lt;/button&gt;
          &lt;/li&gt;
        ))}
      &lt;/ul&gt;
    &lt;/div&gt;
  );
}

// ─── Cart UI ───
function CartApp() {
  const dispatch = useDispatch();
  const { products, loading, error } = useSelector((state) =&gt; state.cart);

  useEffect(() =&gt; { dispatch(fetchProducts()); }, [dispatch]);

  if (loading) return &lt;p&gt;⏳ Yuklanmoqda...&lt;/p&gt;;
  if (error) return &lt;p&gt;❌ {error}&lt;/p&gt;;
  return (
    &lt;ul&gt;
      {products.map(p =&gt; (
        &lt;li key={p.id}&gt;
          {p.name} — {p.price} so'm
          &lt;button onClick={() =&gt; dispatch(addToCart(p.id))}&gt;Savatga&lt;/button&gt;
        &lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}

function App() {
  return (
    &lt;Provider store={store}&gt;
      &lt;Statistika /&gt;
      &lt;TodoApp /&gt;
      &lt;CartApp /&gt;
    &lt;/Provider&gt;
  );
}</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ 1-4 darslarning hammasi birga: createSlice, payload action, xavfsiz selector, createAsyncThunk</li>
<li>✅ Har bir domen — alohida slice, configureStore ichida birlashtiriladi</li>
<li>✅ Statistika kabi hisoblangan qiymatlar — faqat primitiv (son) qaytarilsa xavfsiz</li>
<li>✅ Har ikkala slice mustaqil ishlaydi, lekin bitta store orqali butun ilova ko'radi</li>
</ul>
"""

R1_CODE = """\
// ════════════════════════════════════════════════════════════════════
// REVISION 1: Todo + Savat (RTK to'liq)
// Modul 1: createSlice + payload action + selector + createAsyncThunk
// ════════════════════════════════════════════════════════════════════

import { createSlice, createAsyncThunk, configureStore } from '@reduxjs/toolkit';
import { useSelector, useDispatch, Provider } from 'react-redux';
import { useEffect, useState } from 'react';

const todosSlice = createSlice({
  name: 'todos',
  initialState: { items: [] },
  reducers: {
    addTodo: (state, action) => {
      state.items.push({ id: Date.now(), text: action.payload, done: false });
    },
    toggleTodo: (state, action) => {
      const t = state.items.find(x => x.id === action.payload);
      if (t) t.done = !t.done;
    },
    removeTodo: (state, action) => {
      state.items = state.items.filter(x => x.id !== action.payload);
    },
  },
});

export const fetchProducts = createAsyncThunk('cart/fetchProducts', async () => {
  const res = await fetch('/api/products');
  if (!res.ok) throw new Error("Mahsulotlarni yuklab bo'lmadi");
  return res.json();
});

const cartSlice = createSlice({
  name: 'cart',
  initialState: { products: [], inCart: [], loading: false, error: null },
  reducers: {
    addToCart: (state, action) => { state.inCart.push(action.payload); },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.products = action.payload;
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { addTodo, toggleTodo, removeTodo } = todosSlice.actions;
export const { addToCart } = cartSlice.actions;

const store = configureStore({
  reducer: { todos: todosSlice.reducer, cart: cartSlice.reducer },
});

function Statistika() {
  const qolgan = useSelector((state) => state.todos.items.filter(t => !t.done).length);
  const savatSoni = useSelector((state) => state.cart.inCart.length);
  return <h2>Qolgan: {qolgan} | Savatda: {savatSoni}</h2>;
}

function TodoApp() {
  const [matn, setMatn] = useState('');
  const items = useSelector((state) => state.todos.items);
  const dispatch = useDispatch();

  return (
    <div>
      <input value={matn} onChange={e => setMatn(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && (dispatch(addTodo(matn)), setMatn(''))} />
      <button onClick={() => { dispatch(addTodo(matn)); setMatn(''); }}>+</button>
      <ul>
        {items.map(t => (
          <li key={t.id} style={{ textDecoration: t.done ? 'line-through' : 'none' }}>
            <input type="checkbox" checked={t.done} onChange={() => dispatch(toggleTodo(t.id))} />
            {t.text}
            <button onClick={() => dispatch(removeTodo(t.id))}>x</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function CartApp() {
  const dispatch = useDispatch();
  const { products, loading, error } = useSelector((state) => state.cart);

  useEffect(() => { dispatch(fetchProducts()); }, [dispatch]);

  if (loading) return <p>⏳ Yuklanmoqda...</p>;
  if (error) return <p>❌ {error}</p>;
  return (
    <ul>
      {products.map(p => (
        <li key={p.id}>
          {p.name} — {p.price} so'm
          <button onClick={() => dispatch(addToCart(p.id))}>Savatga</button>
        </li>
      ))}
    </ul>
  );
}

function App() {
  return (
    <Provider store={store}>
      <Statistika />
      <TodoApp />
      <CartApp />
    </Provider>
  );
}
"""

R1_EX = [
    {
        "title": "Ikkita domen uchun to'g'ri struktura",
        "description": "Todo va Savat kabi ikkita mustaqil domen bo'lsa, RTK'da tavsiya etilgan struktura qanday?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ikkalasini bitta katta slice ichiga yozish",
            "Har biriga alohida slice, configureStore ichida birlashtirish",
            "Har biriga alohida store yaratish",
            "Context API'ga qaytish",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "configureStore'ning reducer obyekti — bir nechta slice'ni birlashtirish uchun aynan shu maqsadda.",
        "explanation": (
            "Har bir domen (todos, cart) — o'z alohida slice'iga ega bo'lishi "
            "kerak. configureStore ularni bitta store ichida `reducer: { "
            "todos: ..., cart: ... }` orqali birlashtiradi."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Savatdagi mahsulotlar sonini xavfsiz olish",
        "description": "state.cart.inCart massividan mahsulotlar sonini useSelector orqali xavfsiz (keraksiz re-render bermaydigan) tarzda qanday olamiz?",
        "exercise_type": "multiple_choice",
        "options": [
            "useSelector(state => state.cart.inCart)",
            "useSelector(state => state.cart.inCart.length)",
            "useSelector(state => [...state.cart.inCart])",
            "useSelector(state => state.cart.inCart.filter(() => true))",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "3-darsni eslang: son — primitiv qiymat, taqqoslash to'g'ri ishlaydi.",
        "explanation": (
            "`.length` — son (primitiv), shuning uchun === solishtiruv to'g'ri "
            "ishlaydi. Massivning o'zini yoki uning nusxasini/filtrlangan "
            "versiyasini qaytarish har safar yangi referens beradi."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "fetchProducts loyihasini to'g'ri tartibda joylang",
        "description": "Komponent mount bo'lgandan mahsulotlar ekranga chiqquncha bo'lgan voqealarni tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "useEffect ichida dispatch(fetchProducts()) chaqiriladi",
            "pending — state.loading = true",
            "fetch('/api/products') server bilan gaplashadi",
            "fulfilled — state.products = action.payload, loading=false",
            "Komponent qayta render bo'lib ro'yxatni ko'rsatadi",
        ],
        "correct_order": [
            "useEffect ichida dispatch(fetchProducts()) chaqiriladi",
            "pending — state.loading = true",
            "fetch('/api/products') server bilan gaplashadi",
            "fulfilled — state.products = action.payload, loading=false",
            "Komponent qayta render bo'lib ro'yxatni ko'rsatadi",
        ],
        "hint": "Har doim: dispatch → pending → server bilan ishlash → fulfilled/rejected → UI yangilanadi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega todosSlice va cartSlice'ni birlashtirmaslik kerak?",
        "description": (
            "Nega Todo va Savat uchun ikkita alohida slice yaratish, ularni "
            "bitta katta slice qilib yozishdan yaxshiroq? O'z so'zlaringiz "
            "bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Har bir slice — o'z domeniga tegishli state va logikani "
            "izolyatsiya qiladi. Agar todos va cart bitta slice'da bo'lsa, "
            "kod chalkash bo'lib qoladi, action nomlari to'qnashishi mumkin, "
            "va bitta domendagi o'zgarish boshqasiga aloqasi yo'q kodga "
            "ta'sir qilish xavfi oshadi. Alohida slice'lar — kodni o'qish, "
            "test qilish va jamoada parallel ishlashni osonlashtiradi; "
            "configureStore ularni reducer obyekti orqali oddiygina "
            "birlashtiradi."
        ),
        "hint": "Kodni o'qish, test qilish, va jamoada ishlashni osonlashtirish nuqtai nazaridan o'ylang.",
        "difficulty_level": "Medium",
        "points": 4,
    },
]


L5_TEXT = """\
<h2>RTK Query asoslari — createAsyncThunk boilerplate'ini yo'q qilish</h2>

<pre class="mermaid">
flowchart LR
    API["createApi({ endpoints })"] -->|avtomatik| H["useGetProductsQuery()"]
    H --> D["data, isLoading, error — hammasi tayyor"]
    M["useAddProductMutation()"] -->|invalidatesTags| H
</pre>

<p>4-darsda <code>createAsyncThunk</code> bilan bitta so'rov uchun: thunk, slice, 3 ta extraReducers case, loading/error state — hammasi qo'lda. <strong>RTK Query</strong> — bularning hammasini bir necha qatorga tushiradi va qo'shimcha: keshlash, avtomatik qayta yuklash, deduplikatsiya beradi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — API slice yaratish</h4>
<pre><code>// src/features/apiSlice.js
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  tagTypes: ['Product'],
  endpoints: (builder) =&gt; ({
    getProducts: builder.query({
      query: () =&gt; '/products',
      providesTags: ['Product'],
    }),
    addProduct: builder.mutation({
      query: (newProduct) =&gt; ({
        url: '/products',
        method: 'POST',
        body: newProduct,
      }),
      invalidatesTags: ['Product'],
    }),
  }),
});

// Nomlash konvensiyasi avtomatik: getProducts → useGetProductsQuery
//                                  addProduct → useAddProductMutation
export const { useGetProductsQuery, useAddProductMutation } = api;</code></pre>

<h4>BLOKA 2 — store'ga ulash</h4>
<pre><code>import { configureStore } from '@reduxjs/toolkit';
import { api } from './features/apiSlice';

const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer, // "api": {...}
  },
  middleware: (getDefaultMiddleware) =&gt;
    getDefaultMiddleware().concat(api.middleware), // keshlash/refetch shu orqali ishlaydi
});</code></pre>

<h4>BLOKA 3 — komponentda ishlatish (createAsyncThunk'siz!)</h4>
<pre><code>function MahsulotlarRoyxati() {
  // Bitta qator — data, isLoading, error, hammasi tayyor!
  const { data, isLoading, error } = useGetProductsQuery();

  if (isLoading) return &lt;p&gt;⏳ Yuklanmoqda...&lt;/p&gt;;
  if (error) return &lt;p&gt;❌ Xato yuz berdi&lt;/p&gt;;
  return &lt;ul&gt;{data.map(p =&gt; &lt;li key={p.id}&gt;{p.name}&lt;/li&gt;)}&lt;/ul&gt;;
}

function YangiMahsulotForma() {
  const [addProduct, { isLoading }] = useAddProductMutation();

  const yuborish = async () =&gt; {
    await addProduct({ name: 'Yangi mahsulot', price: 10000 });
    // MahsulotlarRoyxati AVTOMATIK qayta yuklanadi — hech qanday qo'lda
    // dispatch(fetchProducts()) kerak emas!
  };

  return &lt;button onClick={yuborish} disabled={isLoading}&gt;Qo'shish&lt;/button&gt;;
}</code></pre>

<p>4-darsda buni qo'lda qilish uchun: thunk, 3 ta extraReducers case, keyin har bir mutatsiyadan keyin qayta <code>dispatch(fetchProducts())</code> chaqirish kerak edi. RTK Query'da — <code>invalidatesTags</code>/<code>providesTags</code> orqali bu <strong>avtomatik</strong>.</p>

<h3>🐛 Ataylab xato — invalidatesTags'ni unutish</h3>
<pre><code>addProduct: builder.mutation({
  query: (newProduct) =&gt; ({ url: '/products', method: 'POST', body: newProduct }),
  // ❌ invalidatesTags: ['Product'] YO'Q!
}),</code></pre>

<p><strong>Natija:</strong> <code>addProduct</code> mutatsiyasi <strong>muvaffaqiyatli</strong> ishlaydi — server yangi mahsulotni saqlaydi, xato yo'q. Lekin <code>MahsulotlarRoyxati</code> komponenti <strong>yangilanmaydi</strong> — yangi mahsulot ro'yxatda ko'rinmaydi, sahifani qo'lda yangilamaguningizcha (F5). Sabab: RTK Query <code>getProducts</code>ning keshlangan natijasini hali "eskirgan" deb belgilamadi, chunki hech kim unga aytmadi. Bu — muvaffaqiyatli, lekin foydalanuvchi uchun chalkash bug: "men qo'shdim-ku, nega ko'rinmayapti?"</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. createApi anatomiyasi</h4>
<table>
<tr><th>Maydon</th><th>Vazifasi</th></tr>
<tr><td><code>reducerPath</code></td><td>store ichida qaysi kalit ostida saqlanishi ("api")</td></tr>
<tr><td><code>baseQuery</code></td><td>barcha so'rovlar uchun umumiy sozlama (baseUrl, header'lar)</td></tr>
<tr><td><code>tagTypes</code></td><td>keshni guruhlash uchun "yorliq" nomlari ("Product")</td></tr>
<tr><td><code>endpoints</code></td><td>har bir so'rov — <code>builder.query</code> (GET) yoki <code>builder.mutation</code> (POST/PUT/DELETE)</td></tr>
</table>

<h4>2. Nomlash konvensiyasi — avtomatik hook'lar</h4>
<p><code>endpoints</code> ichidagi har bir nom uchun RTK Query avtomatik hook yasaydi: <code>getProducts</code> → <code>useGetProductsQuery</code>, <code>addProduct</code> → <code>useAddProductMutation</code>. Qo'lda export qilish shart emas — <code>api.endpoints.getProducts</code> orqali ham kirish mumkin, lekin hook'lar qulayroq.</p>

<h4>3. providesTags / invalidatesTags — avtomatik yangilanishning siri</h4>
<ul>
<li><code>getProducts</code> — <code>providesTags: ['Product']</code> — "men Product turidagi ma'lumotni taqdim etaman"</li>
<li><code>addProduct</code> — <code>invalidatesTags: ['Product']</code> — "men Product turidagi keshni eskirgan qilaman"</li>
</ul>
<p>Mutatsiya muvaffaqiyatli bo'lgach, RTK Query <code>invalidatesTags</code>dagi har bir tag uchun, o'sha tagni <code>providesTags</code>da e'lon qilgan barcha query'larni <strong>avtomatik qayta so'raydi</strong>. Bu — qo'lda <code>dispatch(fetch...())</code> chaqirishning o'rnini bosadi.</p>

<h4>4. Nega hali ham createAsyncThunk kerak?</h4>
<p>RTK Query — server bilan CRUD (GET/POST/PUT/DELETE) uchun ideal. Lekin har qanday async operatsiya server so'rovi emas: masalan, <code>localStorage</code>ni o'qish, murakkab hisoblash, yoki bir nechta API'ni ketma-ket chaqirish shartli logika bilan. Bunday hollarda <code>createAsyncThunk</code> hali ham to'g'ri vosita.</p>

<h4>5. isLoading vs isFetching</h4>
<p><code>useGetProductsQuery()</code> qaytaradi: <code>data</code>, <code>isLoading</code> (birinchi yuklashda), <code>isFetching</code> (har qanday qayta yuklashda, keshlangan data bo'lsa ham), <code>error</code>, <code>refetch</code> (qo'lda qayta so'rash).</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>createApi</code> — endpoints'dan useGetXQuery/useAddXMutation hook'larini avtomatik yaratadi</li>
<li>✅ Store'ga <code>[api.reducerPath]: api.reducer</code> va <code>api.middleware</code>ni qo'shish shart</li>
<li>✅ <code>providesTags</code>/<code>invalidatesTags</code> — mutatsiyadan keyin tegishli query'larni avtomatik qayta yuklaydi</li>
<li>✅ invalidatesTags'ni unutish — mutatsiya muvaffaqiyatli bo'ladi, lekin UI yangilanmaydi (jim bug)</li>
<li>✅ RTK Query — server CRUD uchun; createAsyncThunk — server bo'lmagan yoki murakkab async logika uchun</li>
</ul>
"""

L5_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 5: RTK Query asoslari
// ════════════════════════════════════════════════════════════════════

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { configureStore } from '@reduxjs/toolkit';
import { Provider } from 'react-redux';

// ─────────────────────────────────────────────────────────────────────
// 1) API slice — endpoints'dan hook'lar avtomatik yasaladi
// ─────────────────────────────────────────────────────────────────────

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  tagTypes: ['Product'],
  endpoints: (builder) => ({
    getProducts: builder.query({
      query: () => '/products',
      providesTags: ['Product'],
    }),
    addProduct: builder.mutation({
      query: (newProduct) => ({
        url: '/products',
        method: 'POST',
        body: newProduct,
      }),
      invalidatesTags: ['Product'], // shu bo'lmasa — 🐛 pastga qarang
    }),
  }),
});

export const { useGetProductsQuery, useAddProductMutation } = api;

// ─────────────────────────────────────────────────────────────────────
// 2) Store — reducerPath + middleware
// ─────────────────────────────────────────────────────────────────────

const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(api.middleware),
});

// ─────────────────────────────────────────────────────────────────────
// 3) Komponentlar — createAsyncThunk'siz
// ─────────────────────────────────────────────────────────────────────

function MahsulotlarRoyxati() {
  const { data, isLoading, error } = useGetProductsQuery();

  if (isLoading) return <p>⏳ Yuklanmoqda...</p>;
  if (error) return <p>❌ Xato yuz berdi</p>;
  return (
    <ul>
      {data.map(p => <li key={p.id}>{p.name} — {p.price} so'm</li>)}
    </ul>
  );
}

function YangiMahsulotForma() {
  const [addProduct, { isLoading }] = useAddProductMutation();

  const yuborish = async () => {
    await addProduct({ name: 'Yangi mahsulot', price: 10000 });
    // invalidatesTags tufayli MahsulotlarRoyxati avtomatik qayta yuklanadi
  };

  return <button onClick={yuborish} disabled={isLoading}>Qo'shish</button>;
}

function App() {
  return (
    <Provider store={store}>
      <MahsulotlarRoyxati />
      <YangiMahsulotForma />
    </Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato — invalidatesTags'ni unutish
// ─────────────────────────────────────────────────────────────────────

/*
const apiXato = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  tagTypes: ['Product'],
  endpoints: (builder) => ({
    getProducts: builder.query({
      query: () => '/products',
      providesTags: ['Product'],
    }),
    addProduct: builder.mutation({
      query: (newProduct) => ({ url: '/products', method: 'POST', body: newProduct }),
      // ❌ invalidatesTags yo'q — mutatsiya muvaffaqiyatli, lekin
      // MahsulotlarRoyxati keshi "eskirgan" deb belgilanmaydi.
      // Foydalanuvchi F5 bosmaguncha yangi mahsulotni ko'rmaydi.
    }),
  }),
});
*/
"""

L5_EX = [
    {
        "title": "createApi qanday hook yaratadi?",
        "description": "createApi'da endpoints ichida getProducts nomli builder.query bo'lsa, qaysi hook avtomatik yaratiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "useProducts()",
            "useGetProductsQuery()",
            "fetchProducts()",
            "useProductsData()",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Konvensiya: use + EndpointNomi (katta harf bilan) + Query/Mutation.",
        "explanation": (
            "RTK Query nomlash konvensiyasi: query endpoint uchun "
            "`use{EndpointName}Query`, mutation uchun `use{EndpointName}Mutation`. "
            "getProducts → useGetProductsQuery."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Mutatsiyadan keyin ro'yxat avtomatik qayta yuklanishi uchun nima kerak?",
        "description": "addProduct mutatsiyasidan keyin getProducts ro'yxati avtomatik qayta so'ralishi uchun nima sozlanishi kerak?",
        "exercise_type": "multiple_choice",
        "options": [
            "Hech narsa — bu har doim avtomatik",
            "getProducts'da providesTags, addProduct'da mos invalidatesTags",
            "useEffect ichida qo'lda refetch() chaqirish",
            "Sahifani to'liq qayta yuklash",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Ikki tomonlama sozlash kerak: kim taqdim etadi (provides), kim eskirtiradi (invalidates).",
        "explanation": (
            "providesTags va invalidatesTags bir xil tag nomi bilan mos "
            "kelishi kerak. Faqat shunda RTK Query mutatsiyadan keyin qaysi "
            "query'larni qayta so'rashni biladi."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "RTK Query sozlash ketma-ketligi",
        "description": "Yangi loyihada RTK Query'ni sozlashning to'g'ri tartibini joylang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "createApi bilan endpoints (query/mutation) ta'riflash",
            "Store'ga [api.reducerPath]: api.reducer qo'shish",
            "middleware'ga api.middleware qo'shish",
            "Komponentda useGetXQuery() / useXMutation() ishlatish",
        ],
        "correct_order": [
            "createApi bilan endpoints (query/mutation) ta'riflash",
            "Store'ga [api.reducerPath]: api.reducer qo'shish",
            "middleware'ga api.middleware qo'shish",
            "Komponentda useGetXQuery() / useXMutation() ishlatish",
        ],
        "hint": "Avval API ta'rifi, keyin store'ga ulash, keyin komponentda foydalanish.",
        "explanation": "",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega invalidatesTags'ni unutish jim bug beradi?",
        "description": (
            "addProduct mutatsiyasida invalidatesTags yozilmasa, server "
            "so'rovi muvaffaqiyatli bo'lishiga qaramay foydalanuvchi nega "
            "yangi mahsulotni ko'rmaydi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "RTK Query getProducts natijasini keshlab saqlaydi va uni faqat "
            "invalidatesTags orqali \"eskirgan\" deb belgilanganda qayta "
            "so'raydi. addProduct muvaffaqiyatli bo'lsa ham, agar u "
            "invalidatesTags: ['Product'] deb belgilanmagan bo'lsa, RTK "
            "Query getProducts keshini eskirgan deb hisoblamaydi va uni "
            "qayta so'ramaydi. Server tomonda ma'lumot yangilangan bo'lsa "
            "ham, foydalanuvchi ekranida eski, keshlangan ro'yxat ko'rinishda "
            "qoladi — sahifani qo'lda yangilamaguncha."
        ),
        "hint": "Kesh qachon \"eskirgan\" deb hisoblanadi, va buni kim aytishi kerak?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L6_TEXT = """\
<h2>Selectors va performance — createSelector bilan memoizatsiya</h2>

<pre class="mermaid">
flowchart LR
    S1["state.todos.items"] --> CS["createSelector"]
    CS -->|inputlar o'zgarmasa| CACHE["keshlangan natijani qaytaradi"]
    CS -->|inputlar o'zgarsa| RECALC["qayta hisoblaydi + yangi natija"]
</pre>

<p>3-darsda muammoni ko'rgandik: <code>.filter()</code> ishlatgan selector har safar yangi array qaytaradi, hatto natija bir xil bo'lsa ham. Bu darsda <strong>createSelector</strong> bilan buni to'g'ri yechamiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — 3-darsdagi muammoni eslash</h4>
<pre><code>// 3-darsdan — har chaqirilganda yangi array:
const qolgan = useSelector((state) =&gt;
  state.todos.items.filter((t) =&gt; !t.done)
);</code></pre>

<h4>BLOKA 2 — createSelector bilan yechish</h4>
<pre><code>import { createSelector } from '@reduxjs/toolkit';

// Input selector — qaysi state qismini kuzatamiz
const selectTodoItems = (state) =&gt; state.todos.items;

// createSelector(inputSelectors[], resultFn)
export const selectQolganTodos = createSelector(
  [selectTodoItems],
  (items) =&gt; items.filter((t) =&gt; !t.done) // faqat items o'zgarsa qayta ishlaydi
);</code></pre>

<pre><code>function QolganSoni() {
  const qolgan = useSelector(selectQolganTodos);
  console.log("📋 QolganSoni qayta render bo'ldi");
  return &lt;p&gt;Bajarilmagan: {qolgan.length}&lt;/p&gt;;
}</code></pre>

<p>Endi <code>toggleTheme()</code> dispatch qilinsa: <code>selectTodoItems(state)</code> — o'zgarmadi (<code>items</code> referensi bir xil qoldi, chunki todos slice'iga tegilmadi). <code>createSelector</code> buni ko'radi va <strong>qayta hisoblamasdan, avvalgi keshlangan array'ni qaytaradi</strong>. Natija: <code>QolganSoni</code> qayta render bo'lmaydi.</p>

<h4>BLOKA 3 — bir nechta input selector</h4>
<pre><code>const selectTheme = (state) =&gt; state.app.theme;

export const selectStatistika = createSelector(
  [selectTodoItems, selectTheme],
  (items, theme) =&gt; ({
    qolgan: items.filter((t) =&gt; !t.done).length,
    theme,
  })
);
// Faqat items YOKI theme o'zgarsa qayta hisoblaydi — ikkalasi ham o'zgarmasa, kesh qaytadi</code></pre>

<h3>🐛 Ataylab xato — bitta parametrlangan selectorni bir nechta komponent orasida ulashish</h3>
<pre><code>// "ID bo'yicha todo topish" selectori — parametr bilan
const selectTodoById = createSelector(
  [selectTodoItems, (state, id) =&gt; id],
  (items, id) =&gt; items.find((t) =&gt; t.id === id)
);

function TodoItem({ id }) {
  // ❌ Bir xil selectTodoById HAR BIR TodoItem instance uchun ishlatiladi
  const todo = useSelector((state) =&gt; selectTodoById(state, id));
  return &lt;li&gt;{todo?.text}&lt;/li&gt;;
}

function TodoList() {
  const ids = useSelector((state) =&gt; state.todos.items.map(t =&gt; t.id));
  return ids.map(id =&gt; &lt;TodoItem key={id} id={id} /&gt;); // 10 ta TodoItem — bitta selectTodoById!
}</code></pre>

<p><strong>Natija:</strong> <code>createSelector</code>ning standart keshi — <strong>faqat oxirgi 1 ta chaqiruvni</strong> eslab qoladi. 10 ta <code>TodoItem</code> bitta <code>selectTodoById</code>ni turli <code>id</code> bilan chaqirsa, har safar kesh "boshqa parametr" deb hisoblab qayta hisoblaydi — birinchi TodoItem'ning keshi ikkinchisi tomonidan "bosib chiqariladi", va aylanma davom etadi. Natijada memoizatsiya <strong>umuman ishlamaydi</strong> — har render'da hammasi qayta hisoblanadi, garchi kod "to'g'ri" ko'ringan bo'lsa ham.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. createSelector qanday ishlaydi</h4>
<p><code>createSelector([inputSelectors], resultFn)</code>: har chaqirilganda avval barcha input selectorlarni ishga tushiradi, natijalarini oldingi chaqiruvning natijalari bilan <code>===</code> orqali solishtiradi. Agar <strong>hammasi</strong> bir xil bo'lsa — keshlangan natijani qaytaradi, <code>resultFn</code>ni umuman chaqirmaydi. Agar birortasi farq qilsa — <code>resultFn</code>ni qayta chaqiradi va yangi natijani keshga saqlaydi.</p>

<h4>2. Standart kesh hajmi — 1</h4>
<p><code>createSelector</code> standart holatda faqat <strong>bitta</strong> (oxirgi) chaqiruvni eslab qoladi. Bu — bitta komponent joyida (masalan, <code>selectQolganTodos</code> faqat bitta joyda ishlatilsa) mukammal ishlaydi. Lekin parametrlangan selector bir nechta komponent instance orasida ulashilsa — kesh doimiy "bosib chiqariladi".</p>

<h4>3. Yechim — har komponent uchun o'z selector instance'i</h4>
<pre><code>import { useMemo } from 'react';

function TodoItem({ id }) {
  // Har bir TodoItem — o'zining alohida, memoizatsiya qilingan selectorini yaratadi
  const selectThisTodo = useMemo(
    () =&gt; createSelector([selectTodoItems], (items) =&gt; items.find(t =&gt; t.id === id)),
    [id]
  );
  const todo = useSelector(selectThisTodo);
  return &lt;li&gt;{todo?.text}&lt;/li&gt;;
}</code></pre>
<p>Endi har bir <code>TodoItem</code> — o'zining alohida keshiga ega, bir-birining keshini "bosib chiqarmaydi".</p>

<h4>4. Qachon createSelector kerak, qachon shart emas?</h4>
<table>
<tr><th>Kerak (createSelector ishlating)</th><th>Shart emas (oddiy selector yetarli)</th></tr>
<tr><td><code>.filter()/.map()/.sort()</code> ishlatuvchi hisoblash</td><td>Bitta maydonni to'g'ridan-to'g'ri o'qish: <code>state.app.theme</code></td></tr>
<tr><td>Bir nechta state qismidan yangi obyekt yasash</td><td>Son yoki string qaytarish (allaqachon primitiv)</td></tr>
<tr><td>Qimmat hisoblash (katta ro'yxatni saralash)</td><td>Kichik, arzon amallar</td></tr>
</table>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>createSelector([inputs], resultFn)</code> — inputlar o'zgarmasa, keshlangan natijani qaytaradi va resultFn'ni qayta chaqirmaydi</li>
<li>✅ 3-darsdagi <code>.filter()</code> muammosi — createSelector bilan to'g'ri yechiladi</li>
<li>✅ Standart kesh hajmi — 1 (faqat oxirgi chaqiruv)</li>
<li>✅ Parametrlangan selectorni bir nechta komponent instance orasida ulashish — keshni "bosib chiqarish"ga (cache thrashing) olib keladi</li>
<li>✅ Yechim — <code>useMemo</code> bilan har komponent instance uchun alohida selector yaratish</li>
</ul>
"""

L6_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 6: Selectors va performance — createSelector
// ════════════════════════════════════════════════════════════════════

import { createSlice, createSelector, configureStore } from '@reduxjs/toolkit';
import { useSelector, useDispatch, Provider } from 'react-redux';
import { useMemo } from 'react';

const todosSlice = createSlice({
  name: 'todos',
  initialState: { items: [{ id: 1, text: 'Non olish', done: false }] },
  reducers: {
    addTodo: (state, action) => {
      state.items.push({ id: Date.now(), text: action.payload, done: false });
    },
  },
});

const appSlice = createSlice({
  name: 'app',
  initialState: { theme: 'light' },
  reducers: {
    toggleTheme: (state) => { state.theme = state.theme === 'light' ? 'dark' : 'light'; },
  },
});

export const { addTodo } = todosSlice.actions;
export const { toggleTheme } = appSlice.actions;

const store = configureStore({
  reducer: { todos: todosSlice.reducer, app: appSlice.reducer },
});

// ─────────────────────────────────────────────────────────────────────
// 1) Input selectors + memoized derived selector
// ─────────────────────────────────────────────────────────────────────

const selectTodoItems = (state) => state.todos.items;
const selectTheme = (state) => state.app.theme;

export const selectQolganTodos = createSelector(
  [selectTodoItems],
  (items) => items.filter((t) => !t.done)
);

export const selectStatistika = createSelector(
  [selectTodoItems, selectTheme],
  (items, theme) => ({
    qolgan: items.filter((t) => !t.done).length,
    theme,
  })
);

function QolganSoni() {
  const qolgan = useSelector(selectQolganTodos);
  console.log("📋 QolganSoni qayta render bo'ldi");
  return <p>Bajarilmagan: {qolgan.length}</p>;
}

function ThemeButton() {
  const dispatch = useDispatch();
  const theme = useSelector(selectTheme);
  return <button onClick={() => dispatch(toggleTheme())}>Mavzu: {theme}</button>;
}

// ─────────────────────────────────────────────────────────────────────
// 2) Ataylab xato — parametrlangan selectorni ulashish
// ─────────────────────────────────────────────────────────────────────

const selectTodoByIdXato = createSelector(
  [selectTodoItems, (state, id) => id],
  (items, id) => items.find((t) => t.id === id)
);

function TodoItemXato({ id }) {
  // ❌ Bir xil selectTodoByIdXato barcha instance'lar orasida ulashiladi —
  // kesh hajmi 1 bo'lgani uchun, har instance boshqasining keshini bosib chiqaradi.
  const todo = useSelector((state) => selectTodoByIdXato(state, id));
  return <li>{todo?.text}</li>;
}

// ✅ To'g'ri variant — har instance o'z selectorini yaratadi
function TodoItemTogri({ id }) {
  const selectThisTodo = useMemo(
    () => createSelector([selectTodoItems], (items) => items.find(t => t.id === id)),
    [id]
  );
  const todo = useSelector(selectThisTodo);
  return <li>{todo?.text}</li>;
}

function TodoList() {
  const ids = useSelector((state) => state.todos.items.map(t => t.id));
  return (
    <ul>
      {ids.map(id => <TodoItemTogri key={id} id={id} />)}
    </ul>
  );
}

function App() {
  return (
    <Provider store={store}>
      <QolganSoni />
      <ThemeButton />
      <TodoList />
    </Provider>
  );
}
"""

L6_EX = [
    {
        "title": "createSelector nima uchun ishlatiladi?",
        "description": "createSelector([inputSelectors], resultFn) asosiy maqsadi nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Store'ga yangi state qo'shish uchun",
            "Input selectorlar o'zgarmaguncha natijani keshlab, keraksiz qayta hisoblashning oldini olish uchun",
            "Action dispatch qilish uchun",
            "Componentni qayta render qilishga majburlash uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Kesh — inputlar o'zgarmasa, natija ham qayta hisoblanmaydi.",
        "explanation": (
            "createSelector — input selectorlarning natijalarini oldingi "
            "chaqiruv bilan solishtiradi. Agar bir xil bo'lsa, resultFn'ni "
            "qayta chaqirmasdan keshlangan natijani qaytaradi."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "createSelector standart kesh hajmi qancha?",
        "description": "createSelector bilan yaratilgan selectorning standart (default) kesh hajmi nechta chaqiruvni eslab qoladi?",
        "exercise_type": "multiple_choice",
        "options": ["0 — kesh yo'q", "1 — faqat oxirgi chaqiruv", "10", "Cheksiz"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bitta parametrlangan selectorni bir nechta komponentda ulashish nega muammo bo'lishini eslang.",
        "explanation": (
            "Standart kesh hajmi — 1. Shuning uchun bitta parametrlangan "
            "selectorni turli argumentlar bilan navbatma-navbat chaqirish "
            "(masalan, bir nechta komponent instance) keshni doimiy "
            "\"bosib chiqaradi\" va memoizatsiya foydasiz bo'lib qoladi."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Parametrlangan selectorni to'g'ri ishlatish",
        "description": "Bir nechta TodoItem komponenti, har biri turli id bilan, selectTodoById'dan foydalanmoqchi. Cache thrashing'ni oldini olish uchun to'g'ri yondashuv qaysi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Barcha komponentlar bitta umumiy selectTodoById instansini ishlatishi",
            "Har bir komponent useMemo bilan o'zining alohida selector instance'ini yaratishi",
            "createSelector'ni umuman ishlatmaslik",
            "Har render'da yangi createSelector chaqirish (memo qilmasdan)",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Har instance — o'z keshi. useMemo selector instance'ini id o'zgarmaguncha saqlaydi.",
        "explanation": (
            "useMemo bilan har komponent instance o'zining alohida, "
            "memoizatsiya qilingan selectorini yaratadi va saqlaydi — shunda "
            "boshqa instance'larning chaqiruvlari bu keshga ta'sir qilmaydi."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega bitta parametrlangan selectorni ulashish memoizatsiyani buzadi?",
        "description": (
            "10 ta TodoItem komponenti, har biri turli id bilan, bitta umumiy "
            "selectTodoById(state, id) selectorini chaqirsa, nega bu "
            "createSelector'ning memoizatsiya foydasini yo'qqa chiqaradi? "
            "O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "createSelector standart holda faqat oxirgi bitta chaqiruvning "
            "inputlari va natijasini eslab qoladi (kesh hajmi 1). Agar 10 ta "
            "komponent bitta selector instance'ini turli id qiymatlari bilan "
            "navbatma-navbat chaqirsa, har safar id boshqacha bo'lgani uchun "
            "kesh \"mos kelmaydi\" deb hisoblanadi va qayta hisoblanadi — "
            "keyingi komponent chaqiruvi esa avvalgisining keshini bosib "
            "chiqaradi. Natijada har bir render'da barcha 10 ta chaqiruv "
            "qayta hisoblanadi, garchi ularning har biri o'z ichida bir xil "
            "id bilan takroran chaqirilsa ham — memoizatsiyadan hech qanday "
            "foyda qolmaydi."
        ),
        "hint": "Kesh hajmi 1 ekanini va har chaqiruvda id o'zgarishini birlashtirib o'ylang.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L7_TEXT = """\
<h2>React + TypeScript: props va state'ni tiplash</h2>

<pre class="mermaid">
flowchart LR
    P["interface CardProps"] -->|compile vaqtida tekshiradi| C["Card komponenti"]
    C -->|xato prop uzatilsa| E["Compile xatosi — runtime'gacha yetib bormaydi"]
</pre>

<p>React Asoslari'da yozgan barcha komponentlaringiz — <code>.jsx</code>. Prop nomida xato qilsangiz yoki noto'g'ri turdagi qiymat uzatsangiz, buni faqat <strong>runtime'da</strong>, ko'pincha production'da foydalanuvchi ko'rgandan keyin bilib qolasiz. TypeScript bu xatolarni <strong>yozayotganingizda</strong> ko'rsatadi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — .jsx dan .tsx ga: birinchi tiplangan komponent</h4>
<pre><code>// Terminal — yangi loyiha uchun:
npm create vite@latest mening-app -- --template react-ts</code></pre>

<pre><code>// Card.tsx
interface CardProps {
  sarlavha: string;
  matn: string;
  yulduzlar?: number; // ? — ixtiyoriy prop
}

function Card({ sarlavha, matn, yulduzlar = 0 }: CardProps) {
  return (
    &lt;div className="card"&gt;
      &lt;h3&gt;{sarlavha}&lt;/h3&gt;
      &lt;p&gt;{matn}&lt;/p&gt;
      &lt;span&gt;{'⭐'.repeat(yulduzlar)}&lt;/span&gt;
    &lt;/div&gt;
  );
}

// ❌ Compile xatosi — matn yo'q:
// &lt;Card sarlavha="React" /&gt;
// Property 'matn' is missing in type '{ sarlavha: string; }' but required in type 'CardProps'.

// ❌ Compile xatosi — noto'g'ri tur:
// &lt;Card sarlavha="React" matn="..." yulduzlar="besh" /&gt;
// Type 'string' is not assignable to type 'number | undefined'.</code></pre>

<h4>BLOKA 2 — useState&lt;T&gt; tiplash</h4>
<pre><code>function Forma() {
  // TS avtomatik xulosa qiladi: useState("") → string
  const [ism, setIsm] = useState("");

  // Lekin boshlang'ich qiymat null bo'lsa — TS "null" turini xulosa qiladi,
  // keyinchalik string berilsa xato beradi. Aniq tur kerak:
  const [xato, setXato] = useState&lt;string | null&gt;(null);

  // Massiv/obyekt uchun ham xuddi shunday:
  interface Foydalanuvchi { id: number; ism: string; }
  const [royxat, setRoyxat] = useState&lt;Foydalanuvchi[]&gt;([]);

  return null;
}</code></pre>

<h4>BLOKA 3 — event handler'larni tiplash</h4>
<pre><code>function Input() {
  const [qiymat, setQiymat] = useState("");

  // ChangeEvent<HTMLInputElement> — input o'zgarishi uchun aniq tur
  const onChange = (e: React.ChangeEvent&lt;HTMLInputElement&gt;) =&gt; {
    setQiymat(e.target.value); // TS biladi target — input, .value mavjud
  };

  const onSubmit = (e: React.FormEvent&lt;HTMLFormElement&gt;) =&gt; {
    e.preventDefault();
    console.log(qiymat);
  };

  return (
    &lt;form onSubmit={onSubmit}&gt;
      &lt;input value={qiymat} onChange={onChange} /&gt;
    &lt;/form&gt;
  );
}</code></pre>

<h3>🐛 Ataylab xato — event turini noto'g'ri yozish</h3>
<pre><code>function InputXato() {
  const [qiymat, setQiymat] = useState("");

  // ❌ e ning turi umuman yozilmagan — "implicitly has an 'any' type"
  const onChange = (e) =&gt; {
    setQiymat(e.target.value);
  };

  return &lt;input value={qiymat} onChange={onChange} /&gt;;
}</code></pre>

<pre><code>Parameter 'e' implicitly has an 'any' type.
  ts(7006)</code></pre>

<p><strong>Sabab:</strong> <code>tsconfig.json</code>da <code>strict: true</code> (yoki <code>noImplicitAny</code>) yoqilgan bo'lsa, TypeScript har bir parametr uchun aniq tur talab qiladi. Tur yozilmasa — u avtomatik <code>any</code> bo'ladi, bu esa "TypeScript'ni o'chirib qo'yish" bilan barobar: <code>any</code> turidagi qiymatda TS hech qanday tekshiruv qilmaydi, xato qilsangiz ham sukut saqlaydi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega bu compile xatolari muhim?</h4>
<p>JSda <code>&lt;Card sarlavha="X" /&gt;</code> (matn'siz) yozsangiz — kod ishga tushadi, faqat ekranda <code>matn</code> o'rnida <code>undefined</code> chiqadi, hech qanday xato xabari yo'q. TSda esa — bu <strong>build vaqtida</strong> to'xtaydi, production'ga chiqmasdan oldin.</p>

<h4>2. interface vs type — komponentlar uchun qaysi biri?</h4>
<pre><code>// Ikkalasi ham ishlaydi, props uchun interface ko'proq tavsiya etiladi
interface CardProps { sarlavha: string; }
type CardPropsAlt = { sarlavha: string; };</code></pre>

<h4>3. useState&lt;T&gt; qachon kerak?</h4>
<table>
<tr><th>TS avtomatik biladi</th><th>Aniq tur kerak</th></tr>
<tr><td><code>useState(0)</code> → number</td><td><code>useState&lt;string | null&gt;(null)</code></td></tr>
<tr><td><code>useState("")</code> → string</td><td><code>useState&lt;Foydalanuvchi[]&gt;([])</code></td></tr>
<tr><td><code>useState(false)</code> → boolean</td><td><code>useState&lt;'idle'|'loading'|'error'&gt;('idle')</code></td></tr>
</table>
<p>Qoida: agar boshlang'ich qiymat kelajakdagi barcha holatlarni "ko'rsata olmasa" (masalan, <code>null</code> boshlanadi, keyin string bo'ladi) — aniq generic tur bering.</p>

<h4>4. Eng ko'p ishlatiladigan event turlari</h4>
<table>
<tr><th>Element</th><th>Event turi</th></tr>
<tr><td><code>&lt;input onChange&gt;</code></td><td><code>React.ChangeEvent&lt;HTMLInputElement&gt;</code></td></tr>
<tr><td><code>&lt;form onSubmit&gt;</code></td><td><code>React.FormEvent&lt;HTMLFormElement&gt;</code></td></tr>
<tr><td><code>&lt;button onClick&gt;</code></td><td><code>React.MouseEvent&lt;HTMLButtonElement&gt;</code></td></tr>
<tr><td><code>&lt;input onKeyDown&gt;</code></td><td><code>React.KeyboardEvent&lt;HTMLInputElement&gt;</code></td></tr>
</table>

<h4>5. Ixtiyoriy prop'lar va default qiymat</h4>
<pre><code>interface TugmaProps {
  label: string;
  turi?: 'primary' | 'danger'; // ? — ixtiyoriy, union tur bilan cheklangan
}

function Tugma({ label, turi = 'primary' }: TugmaProps) { /* ... */ }</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Props <code>interface</code> orqali tiplanadi — noto'g'ri/yetishmayotgan prop compile xatosi beradi</li>
<li>✅ <code>useState&lt;T&gt;</code> — TS xulosa qila olmagan hollarda (masalan, boshlang'ich <code>null</code>) aniq tur kerak</li>
<li>✅ Event handler'lar <code>React.ChangeEvent&lt;HTMLInputElement&gt;</code> kabi aniq turlar bilan tiplanadi</li>
<li>✅ Tur yozilmasa (<code>noImplicitAny</code> yoqilganda) — "implicitly has an 'any' type" compile xatosi</li>
<li>✅ <code>any</code> — TypeScript tekshiruvini o'chirib qo'yadi, iloji boricha undan qoching</li>
</ul>
"""

L7_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 7: React + TypeScript — props va state tiplash
// ════════════════════════════════════════════════════════════════════

import { useState } from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) Props — interface bilan tiplash
// ─────────────────────────────────────────────────────────────────────

interface CardProps {
  sarlavha: string;
  matn: string;
  yulduzlar?: number;
}

function Card({ sarlavha, matn, yulduzlar = 0 }: CardProps) {
  return (
    <div className="card">
      <h3>{sarlavha}</h3>
      <p>{matn}</p>
      <span>{'⭐'.repeat(yulduzlar)}</span>
    </div>
  );
}

// <Card sarlavha="React" />                          // ❌ matn yetishmaydi
// <Card sarlavha="React" matn="..." yulduzlar="5" />  // ❌ yulduzlar string emas, number bo'lishi kerak

// ─────────────────────────────────────────────────────────────────────
// 2) useState<T> — aniq tur kerak bo'lgan holatlar
// ─────────────────────────────────────────────────────────────────────

interface Foydalanuvchi {
  id: number;
  ism: string;
}

function ForamaDemo() {
  const [ism, setIsm] = useState("");                       // TS xulosa: string
  const [xato, setXato] = useState<string | null>(null);     // aniq tur kerak
  const [royxat, setRoyxat] = useState<Foydalanuvchi[]>([]); // aniq tur kerak

  return (
    <div>
      <input value={ism} onChange={(e) => setIsm(e.target.value)} />
      {xato && <p>{xato}</p>}
      <ul>{royxat.map(f => <li key={f.id}>{f.ism}</li>)}</ul>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) Event handler'larni tiplash
// ─────────────────────────────────────────────────────────────────────

function Forma() {
  const [qiymat, setQiymat] = useState("");

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQiymat(e.target.value);
  };

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log(qiymat);
  };

  const onButtonClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    console.log('Bosildi', e.currentTarget.name);
  };

  return (
    <form onSubmit={onSubmit}>
      <input value={qiymat} onChange={onChange} />
      <button name="yubor" onClick={onButtonClick}>Yuborish</button>
    </form>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato — event turini yozmaslik
// ─────────────────────────────────────────────────────────────────────

/*
function InputXato() {
  const [qiymat, setQiymat] = useState("");

  // ❌ Parameter 'e' implicitly has an 'any' type. ts(7006)
  const onChange = (e) => {
    setQiymat(e.target.value);
  };

  return <input value={qiymat} onChange={onChange} />;
}
*/

// ─────────────────────────────────────────────────────────────────────
// 5) Ixtiyoriy prop + union tur bilan cheklash
// ─────────────────────────────────────────────────────────────────────

interface TugmaProps {
  label: string;
  turi?: 'primary' | 'danger';
}

function Tugma({ label, turi = 'primary' }: TugmaProps) {
  return <button className={`btn btn-${turi}`}>{label}</button>;
}
"""

L7_EX = [
    {
        "title": "Props qanday tiplanadi?",
        "description": "React + TypeScript'da komponent props'ini tiplashning standart usuli qaysi?",
        "exercise_type": "multiple_choice",
        "options": [
            "PropTypes kutubxonasi orqali",
            "interface yoki type e'lon qilib, funksiya parametriga biriktirish",
            "JSDoc kommentariyalari orqali",
            "Props tiplanmaydi, TS avtomatik aniqlaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "function Card({ ... }: CardProps) — CardProps qayerdan keladi?",
        "explanation": (
            "TypeScript'da props odatda alohida `interface` (yoki `type`) "
            "sifatida e'lon qilinadi va komponent parametriga `: CardProps` "
            "shaklida biriktiriladi."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Qachon useState<T> uchun aniq tur kerak?",
        "description": "Qaysi holatda useState uchun aniq generic tur (<T>) ko'rsatish shart, TS avtomatik xulosa qila olmaydi?",
        "exercise_type": "multiple_choice",
        "options": [
            "useState(0) — son bilan boshlanganda",
            "useState(null) keyinchalik string bo'lishi kutilganda — useState<string | null>(null)",
            "useState('') — bo'sh string bilan boshlanganda",
            "useState(false) — boolean bilan boshlanganda",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "null boshlang'ich qiymat bo'lsa, TS faqat \"null\" turini biladi, kelajakdagi string'ni emas.",
        "explanation": (
            "useState(null) bilan TS state turini faqat `null` deb xulosa "
            "qiladi. Agar keyinchalik string qiymat berilishi kutilsa, "
            "aniq union tur (`string | null`) ko'rsatish kerak."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Input onChange uchun to'g'ri event turi qaysi?",
        "description": "<input onChange={...}> uchun event handler parametrining to'g'ri TypeScript turi qaysi?",
        "exercise_type": "multiple_choice",
        "options": [
            "React.FormEvent<HTMLFormElement>",
            "React.ChangeEvent<HTMLInputElement>",
            "React.MouseEvent<HTMLButtonElement>",
            "Event",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Input qiymati o'zgarishi — Change event, element turi — HTMLInputElement.",
        "explanation": (
            "Input o'zgarishi uchun to'g'ri tur — `React.ChangeEvent<HTMLInputElement>`. "
            "Bu TS'ga `e.target.value` mavjudligini biladi va tekshiradi."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega compile-vaqtidagi prop xatosi runtime xatosidan yaxshiroq?",
        "description": (
            "<Card sarlavha=\"X\" /> (matn prop'isiz) chaqirilsa, JSda kod "
            "ishlayveradi (matn undefined bo'ladi), TSda esa compile xatosi "
            "chiqadi. Nega bu farq muhim, ayniqsa katta jamoa/loyihada? "
            "O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "JavaScript'da yetishmayotgan prop faqat runtime'da, ko'pincha "
            "foydalanuvchi sahifani ochganda \"undefined\" yoki bo'sh joy "
            "sifatida namoyon bo'ladi va buni darhol payqash qiyin bo'lishi "
            "mumkin. TypeScript esa bu xatoni dasturchi kodni yozayotganda, "
            "IDE'da darhol va build vaqtida ko'rsatadi — production'ga "
            "chiqmasdan oldin. Bu ayniqsa katta jamoa yoki loyihada muhim, "
            "chunki bir dasturchi komponent interfeysini o'zgartirsa, uni "
            "ishlatuvchi boshqa barcha joylar avtomatik tekshiriladi va "
            "moslashmagan joylar darhol compile xatosi sifatida ko'rinadi."
        ),
        "hint": "Xatoni qachon (build vaqtida vs foydalanuvchi ko'rgandan keyin) va kim ko'rishi haqida o'ylang.",
        "difficulty_level": "Medium",
        "points": 4,
    },
]


L8_TEXT = """\
<h2>Generics va murakkab tiplar — qayta ishlatiladigan, tiplangan komponentlar</h2>

<pre class="mermaid">
flowchart LR
    L["List&lt;T&gt;"] -->|T = Foydalanuvchi| U["List of users"]
    L -->|T = Mahsulot| P["List of products"]
    L -->|bitta kod, ko'p tur| REUSE["Qayta ishlatish + tip xavfsizligi"]
</pre>

<p>7-darsda bitta aniq turdagi props'ni tipladik. Lekin ba'zi komponentlar — masalan, "istalgan ro'yxatni ko'rsatuvchi" komponent — <strong>istalgan</strong> ma'lumot turi bilan ishlashi kerak, tip xavfsizligini yo'qotmasdan. Bunga <strong>generics</strong> yechim beradi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — generic komponent</h4>
<pre><code>interface ListProps&lt;T&gt; {
  items: T[];
  renderItem: (item: T) =&gt; React.ReactNode;
}

function List&lt;T&gt;({ items, renderItem }: ListProps&lt;T&gt;) {
  return &lt;ul&gt;{items.map((item, i) =&gt; &lt;li key={i}&gt;{renderItem(item)}&lt;/li&gt;)}&lt;/ul&gt;;
}</code></pre>

<pre><code>interface Foydalanuvchi { id: number; ism: string; }
interface Mahsulot { id: number; nomi: string; narx: number; }

// Bitta List komponenti — ikkala turda ham TO'LIQ tip xavfsizligi bilan ishlaydi:
&lt;List&lt;Foydalanuvchi&gt; items={foydalanuvchilar}
  renderItem={(f) =&gt; &lt;span&gt;{f.ism}&lt;/span&gt;} /&gt;

&lt;List&lt;Mahsulot&gt; items={mahsulotlar}
  renderItem={(m) =&gt; &lt;span&gt;{m.nomi} — {m.narx} so'm&lt;/span&gt;} /&gt;</code></pre>

<h4>BLOKA 2 — utility types: Partial, Pick, Omit</h4>
<pre><code>interface Foydalanuvchi {
  id: number;
  ism: string;
  email: string;
  yosh: number;
}

// Partial<T> — barcha maydonlarni ixtiyoriy qiladi (update funksiyalari uchun ideal)
function foydalanuvchiniYangila(id: number, ozgarish: Partial&lt;Foydalanuvchi&gt;) {
  // ozgarish = { ism: "Yangi ism" } — faqat bitta maydon yetarli
}

// Pick<T, K> — faqat kerakli maydonlarni tanlaydi
type FoydalanuvchiQisqa = Pick&lt;Foydalanuvchi, 'id' | 'ism'&gt;;
// { id: number; ism: string } — email va yosh yo'q

// Omit<T, K> — kerakmas maydonlarni chiqarib tashlaydi
type YangiFoydalanuvchi = Omit&lt;Foydalanuvchi, 'id'&gt;;
// { ism: string; email: string; yosh: number } — id yo'q (server yaratadi)</code></pre>

<h4>BLOKA 3 — children'ni tiplash</h4>
<pre><code>interface LayoutProps {
  children: React.ReactNode; // istalgan render qilinadigan narsa: matn, JSX, array, null
}

function Layout({ children }: LayoutProps) {
  return &lt;div className="container"&gt;{children}&lt;/div&gt;;
}

// Yoki qulayroq — PropsWithChildren utility:
import { PropsWithChildren } from 'react';

interface CardProps { sarlavha: string; }

function Card({ sarlavha, children }: PropsWithChildren&lt;CardProps&gt;) {
  return (
    &lt;div className="card"&gt;
      &lt;h3&gt;{sarlavha}&lt;/h3&gt;
      {children}
    &lt;/div&gt;
  );
}</code></pre>

<h3>🐛 Ataylab xato — cheklanmagan generic</h3>
<pre><code>interface ListProps&lt;T&gt; {
  items: T[];
  renderItem: (item: T) =&gt; React.ReactNode;
}

function ListWithId&lt;T&gt;({ items, renderItem }: ListProps&lt;T&gt;) {
  return (
    &lt;ul&gt;
      {items.map((item) =&gt; (
        // ❌ Compile xatosi!
        &lt;li key={item.id}&gt;{renderItem(item)}&lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}</code></pre>

<pre><code>Property 'id' does not exist on type 'T'.</code></pre>

<p><strong>Sabab:</strong> <code>T</code> — <strong>cheklanmagan</strong> generic, ya'ni "istalgan tur" degani. TypeScript <code>T</code> haqida hech narsa bilmaydi — u <code>id</code> maydoniga ega bo'lishi ham, bo'lmasligi ham mumkin. <code>item.id</code>ga murojaat qilish uchun, <code>T</code>ni <strong>cheklash</strong> kerak: "T albatta id maydoniga ega bo'lishi kerak" deb aytish.</p>

<pre><code>// ✅ To'g'ri — T cheklandi
function ListWithId&lt;T extends { id: number | string }&gt;({ items, renderItem }: ListProps&lt;T&gt;) {
  return (
    &lt;ul&gt;
      {items.map((item) =&gt; (
        &lt;li key={item.id}&gt;{renderItem(item)}&lt;/li&gt; // ✅ endi ishlaydi
      ))}
    &lt;/ul&gt;
  );
}</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. Generic — "kelajakda aniqlanadigan tur" uchun o'zgaruvchi</h4>
<p><code>&lt;T&gt;</code> — oddiy funksiya parametriga o'xshaydi, faqat qiymat emas, <strong>tur</strong> uchun. <code>List&lt;Foydalanuvchi&gt;</code> chaqirilganda, TS ichkarida <code>T</code>ni <code>Foydalanuvchi</code> bilan almashtiradi va butun komponent ichida shunga mos tekshiradi.</p>

<h4>2. extends bilan cheklash</h4>
<pre><code>function birinchi&lt;T extends { id: number }&gt;(royxat: T[]): T | undefined {
  return royxat[0];
}
// Endi TS biladi: T albatta id maydoniga ega — item.id xavfsiz</code></pre>

<h4>3. Partial/Pick/Omit — qachon qaysi biri?</h4>
<table>
<tr><th>Utility</th><th>Ishlatilishi</th></tr>
<tr><td><code>Partial&lt;T&gt;</code></td><td>Update funksiyalari — faqat o'zgargan maydonlar</td></tr>
<tr><td><code>Pick&lt;T, K&gt;</code></td><td>To'liq obyektdan faqat bir nechta maydonni ko'rsatish (masalan, ro'yxat elementi)</td></tr>
<tr><td><code>Omit&lt;T, K&gt;</code></td><td>Server-generated maydonlarni (id, createdAt) chiqarib tashlab, "yaratish" formasi turi yasash</td></tr>
</table>

<h4>4. children — React.ReactNode</h4>
<p><code>React.ReactNode</code> — React render qila oladigan <strong>hamma narsa</strong>: string, number, JSX element, array, <code>null</code>, <code>undefined</code>, boolean. <code>PropsWithChildren&lt;Props&gt;</code> — <code>Props</code>ga avtomatik <code>children?: ReactNode</code> qo'shadi, qo'lda yozishning o'rnini bosadi.</p>

<h4>5. Qachon generic kerak, qachon shart emas?</h4>
<p>Agar komponent <strong>bitta aniq</strong> ma'lumot turi bilan ishlasa (masalan, faqat <code>Foydalanuvchi</code> kartasi) — oddiy <code>interface</code> yetarli. Generic faqat komponent <strong>chindan ham</strong> turli xil ma'lumot turlari bilan qayta ishlatilishi kerak bo'lganda (List, Table, Select kabi umumiy komponentlar) kerak bo'ladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Generic komponent (<code>&lt;T&gt;</code>) — bitta kod bilan turli ma'lumot turlarida to'liq tip xavfsizligi</li>
<li>✅ <code>T extends {...}</code> — generic'ni cheklab, uning ichidagi maydonlarga xavfsiz murojaat qilish</li>
<li>✅ <code>Partial&lt;T&gt;</code> — update uchun; <code>Pick&lt;T,K&gt;</code> — tanlab olish; <code>Omit&lt;T,K&gt;</code> — chiqarib tashlash</li>
<li>✅ <code>children: React.ReactNode</code> yoki <code>PropsWithChildren&lt;Props&gt;</code> — bolalar elementlarini tiplash</li>
<li>✅ Generic faqat haqiqiy qayta ishlatish kerak bo'lganda ishlatiladi — har doim emas</li>
</ul>
"""

L8_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 8: Generics va murakkab tiplar
// ════════════════════════════════════════════════════════════════════

import { PropsWithChildren } from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) Generic komponent — cheklanmagan (muammoni ko'rsatish uchun)
// ─────────────────────────────────────────────────────────────────────

interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

function ListOddiy<T>({ items, renderItem }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, i) => <li key={i}>{renderItem(item)}</li>)}
    </ul>
  );
}

interface Foydalanuvchi { id: number; ism: string; email: string; yosh: number; }
interface Mahsulot { id: number; nomi: string; narx: number; }

function RoyxatlarDemo() {
  const foydalanuvchilar: Foydalanuvchi[] = [
    { id: 1, ism: 'Olim', email: 'olim@mail.uz', yosh: 22 },
  ];
  const mahsulotlar: Mahsulot[] = [
    { id: 1, nomi: 'Noutbuk', narx: 5000000 },
  ];

  return (
    <>
      <ListOddiy<Foydalanuvchi> items={foydalanuvchilar}
        renderItem={(f) => <span>{f.ism}</span>} />
      <ListOddiy<Mahsulot> items={mahsulotlar}
        renderItem={(m) => <span>{m.nomi} — {m.narx} so'm</span>} />
    </>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 2) Ataylab xato — cheklanmagan generic, item.id ishlatishga urinish
// ─────────────────────────────────────────────────────────────────────

/*
function ListWithIdXato<T>({ items, renderItem }: ListProps<T>) {
  return (
    <ul>
      {items.map((item) => (
        // ❌ Property 'id' does not exist on type 'T'.
        <li key={item.id}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}
*/

// ✅ To'g'ri — T cheklandi: "id maydoniga ega bo'lishi shart"
function ListWithId<T extends { id: number | string }>({ items, renderItem }: ListProps<T>) {
  return (
    <ul>
      {items.map((item) => (
        <li key={item.id}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) Partial / Pick / Omit
// ─────────────────────────────────────────────────────────────────────

function foydalanuvchiniYangila(id: number, ozgarish: Partial<Foydalanuvchi>) {
  console.log(`Yangilanmoqda #${id}:`, ozgarish);
}
// foydalanuvchiniYangila(1, { ism: 'Yangi ism' }); — faqat bitta maydon yetarli

type FoydalanuvchiQisqa = Pick<Foydalanuvchi, 'id' | 'ism'>;
// { id: number; ism: string }

type YangiFoydalanuvchi = Omit<Foydalanuvchi, 'id'>;
// { ism: string; email: string; yosh: number } — id yo'q, server yaratadi

function RoyxatQisqaKorinish({ user }: { user: FoydalanuvchiQisqa }) {
  return <span>{user.id}: {user.ism}</span>;
}

// ─────────────────────────────────────────────────────────────────────
// 4) children — React.ReactNode va PropsWithChildren
// ─────────────────────────────────────────────────────────────────────

interface LayoutProps {
  children: React.ReactNode;
}

function Layout({ children }: LayoutProps) {
  return <div className="container">{children}</div>;
}

interface CardProps { sarlavha: string; }

function Card({ sarlavha, children }: PropsWithChildren<CardProps>) {
  return (
    <div className="card">
      <h3>{sarlavha}</h3>
      {children}
    </div>
  );
}
"""

L8_EX = [
    {
        "title": "Generic komponent nima uchun kerak?",
        "description": "List<T> kabi generic komponent yaratishning asosiy maqsadi nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Kodni qisqartirish uchun (tip xavfsizligiga aloqasi yo'q)",
            "Bitta komponentni turli ma'lumot turlari bilan, tip xavfsizligini yo'qotmasdan qayta ishlatish uchun",
            "Faqat massivlar bilan ishlash uchun maxsus sintaksis",
            "any turini almashtirish uchun boshqa nom",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "List<Foydalanuvchi> va List<Mahsulot> — bitta kod, ikki xil to'liq tiplangan foydalanish.",
        "explanation": (
            "Generic komponentlar — bir marta yozilgan komponentni turli "
            "ma'lumot turlari bilan qayta ishlatish imkonini beradi, har "
            "safar to'liq tip tekshiruvini saqlab qolgan holda."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega item.id cheklanmagan T bilan xato beradi?",
        "description": "function List<T>({ items }: {...}) ichida items.map(item => item.id) yozilsa, nega TypeScript compile xatosi beradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "id — noto'g'ri nomlangan maydon",
            "T — cheklanmagan, TS uni id maydoniga ega deb hisoblamaydi",
            "map() funksiyasi id bilan ishlamaydi",
            "Bu xato emas, ogohlantirish (warning) xolos",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "T — \"istalgan tur\" degani. TS T haqida hech narsa bilmaydi, extends bilan aytilmasa.",
        "explanation": (
            "Cheklanmagan T — istalgan tur bo'lishi mumkin, shu jumladan id "
            "maydoni bo'lmagan tur ham. `T extends { id: ... }` deb "
            "cheklamasdan, TS item.id'ga xavfsiz murojaat qila olmaydi."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Qaysi utility type mos keladi?",
        "description": "Foydalanuvchi obyektidan faqat 'id' va 'ism' maydonlarini o'z ichiga olgan yangi tur yaratmoqchisiz. Qaysi utility type ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": ["Partial<Foydalanuvchi>", "Pick<Foydalanuvchi, 'id' | 'ism'>", "Omit<Foydalanuvchi, 'id' | 'ism'>", "Required<Foydalanuvchi>"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Pick — TANLAB olish (faqat shu maydonlar qoladi).",
        "explanation": "Pick<T, K> — T'dan faqat K'da ko'rsatilgan maydonlarni o'z ichiga olgan yangi tur yaratadi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega generic'ni har doim emas, faqat kerak bo'lganda ishlatish kerak?",
        "description": (
            "Agar bitta komponent faqat bitta aniq ma'lumot turi (masalan, "
            "faqat Foydalanuvchi) bilan ishlashi kerak bo'lsa, nega uni "
            "baribir generic qilib yozish yaxshi amaliyot hisoblanmaydi? "
            "O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Generic komponentlar qo'shimcha murakkablik qo'shadi — o'qish "
            "va tushunish qiyinroq bo'ladi, chunki komponent qanday "
            "ma'lumot turi bilan ishlashi darhol ko'rinmaydi. Agar komponent "
            "haqiqatda faqat bitta aniq tur (masalan, Foydalanuvchi) bilan "
            "ishlatilsa, oddiy interface aniqroq, o'qish uchun tushunarliroq "
            "va IDE'da avtomatik to'ldirish yaxshiroq ishlaydi. Generic — "
            "faqat komponent chindan ham bir nechta turli ma'lumot turi "
            "bilan qayta ishlatilishi kerak bo'lgandagina o'zini oqlaydi."
        ),
        "hint": "Kodni o'qish qulayligi va keraksiz murakkablik haqida o'ylang.",
        "difficulty_level": "Medium",
        "points": 4,
    },
]


L9_TEXT = """\
<h2>Redux Toolkit + TypeScript birga — RootState, AppDispatch, tiplangan hook'lar</h2>

<pre class="mermaid">
flowchart LR
    ST["store"] -->|ReturnType| RS["RootState"]
    ST -->|typeof| AD["AppDispatch"]
    RS --> UAS["useAppSelector"]
    AD --> UAD["useAppDispatch"]
</pre>

<p>2-3 darslarda <code>useSelector</code>/<code>useDispatch</code>'ni yozdik — lekin TypeScript loyihada, oddiy <code>useSelector</code> ishlatsangiz, <code>state</code> parametri <strong>avtomatik <code>any</code></strong> bo'ladi. Ya'ni <code>state.app.theme</code> yozganingizda TS hech qanday tekshiruv qilmaydi, xato qilsangiz ham sukut saqlaydi. Bu darsda buni to'g'rilaymiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — RootState va AppDispatch turlarini chiqarish</h4>
<pre><code>// src/store.ts
import { configureStore } from '@reduxjs/toolkit';
import appReducer from './features/appSlice';

export const store = configureStore({
  reducer: { app: appReducer },
});

// ❗ Muhim: bu turlarni QO'LDA yozmang — store'dan CHIQARING
export type RootState = ReturnType&lt;typeof store.getState&gt;;
export type AppDispatch = typeof store.dispatch;</code></pre>

<p>Nega qo'lda emas? Agar ertaga yangi slice qo'shsangiz, <code>RootState</code> avtomatik yangilanadi — qo'lda yozilgan interfeys esa eskirib qoladi va yolg'on xavfsizlik tuyg'usi beradi.</p>

<h4>BLOKA 2 — tiplangan hook'lar yaratish</h4>
<pre><code>// src/hooks.ts
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';
import type { RootState, AppDispatch } from './store';

export const useAppDispatch = () =&gt; useDispatch&lt;AppDispatch&gt;();
export const useAppSelector: TypedUseSelectorHook&lt;RootState&gt; = useSelector;</code></pre>

<pre><code>// Endi komponentlarda — RAW useSelector/useDispatch O'RNIGA doim shularni ishlating:
function ThemeLabel() {
  const theme = useAppSelector((state) =&gt; state.app.theme); // ✅ to'liq autocomplete + tekshiruv
  const dispatch = useAppDispatch(); // ✅ dispatch faqat haqiqiy action'larni qabul qiladi
  return &lt;p&gt;{theme}&lt;/p&gt;;
}</code></pre>

<h4>BLOKA 3 — slice state va thunk payload'ini tiplash</h4>
<pre><code>interface AppState {
  theme: 'light' | 'dark';
  count: number;
}

const initialState: AppState = { theme: 'light', count: 0 };

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    // action turi avtomatik xulosa qilinadi PayloadAction&lt;T&gt; orqali
    setTheme: (state, action: PayloadAction&lt;'light' | 'dark'&gt;) =&gt; {
      state.theme = action.payload;
    },
  },
});

// Thunk uchun ham ikkita generic: <Qaytadigan, Argument>
interface Foydalanuvchi { id: number; ism: string; }

export const fetchUser = createAsyncThunk&lt;Foydalanuvchi, number&gt;(
  'user/fetchUser',
  async (userId) =&gt; { // userId — TS biladi: number
    const res = await fetch(`/api/users/${userId}`);
    return res.json() as Promise&lt;Foydalanuvchi&gt;; // Qaytish turi — Foydalanuvchi
  }
);</code></pre>

<h3>🐛 Ataylab xato — ba'zi komponentlarda "eski" useSelector qoldirish</h3>
<pre><code>import { useSelector } from 'react-redux'; // ❌ TIPLANMAGAN, oddiy react-redux'dan

function EskiKomponent() {
  const theme = useSelector((state) =&gt; state.app.theme);
  // ❌ Parameter 'state' implicitly has an 'any' type.
  // Yoki (agar noImplicitAny o'chirilgan bo'lsa) — state.app.theme
  // hech qanday tekshiruvsiz, xato yozsangiz ham (masalan state.apr.theme) jim qoladi.
}</code></pre>

<p><strong>Sabab:</strong> loyihada <code>useAppSelector</code> yaratilgan bo'lsa ham, agar bironta komponent hali ham <code>react-redux</code>dan to'g'ridan-to'g'ri <code>useSelector</code> import qilsa — o'sha bitta joyda butun tip xavfsizligi yo'qoladi. Bu xatoni ESLint qoidasi bilan oldini olish mumkin (<code>no-restricted-imports</code>), lekin eng ishonchli yo'l — jamoada "har doim <code>useAppSelector</code>/<code>useAppDispatch</code>" qoidasiga rioya qilish.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega RootState'ni ReturnType orqali chiqarish kerak</h4>
<p><code>ReturnType&lt;typeof store.getState&gt;</code> — "getState funksiyasi nima qaytarsa, RootState o'sha" degani. Bu store'ning haqiqiy tuzilishidan <strong>avtomatik</strong> kelib chiqadi. Qo'lda yozilgan interfeys yangi slice qo'shilganda yangilanmay qoladi va yolg'on ishonch beradi.</p>

<h4>2. TypedUseSelectorHook nima qiladi?</h4>
<p>Bu — <code>react-redux</code>ning tayyor generic turi, <code>useSelector</code>ni ma'lum bir <code>RootState</code> bilan "qulflab qo'yadi". Natijada har safar qo'lda <code>&lt;RootState&gt;</code> yozish shart emas — <code>useAppSelector</code>ning o'zi buni biladi.</p>

<h4>3. PayloadAction&lt;T&gt; — action.payload'ni tiplash</h4>
<pre><code>import { PayloadAction } from '@reduxjs/toolkit';

reducers: {
  setTheme: (state, action: PayloadAction&lt;'light' | 'dark'&gt;) =&gt; {
    state.theme = action.payload; // TS biladi: faqat 'light' yoki 'dark'
  },
}</code></pre>

<h4>4. createAsyncThunk&lt;Qaytadigan, Argument&gt;</h4>
<p>Ikkita generic: birinchisi — thunk muvaffaqiyatli tugaganda nima qaytarishi (<code>fulfilled</code>ning <code>payload</code> turi), ikkinchisi — thunk chaqirilganda qanday argument kutilishi.</p>

<h4>5. Jamoaviy qoida — hech qachon xom useSelector/useDispatch ishlatmang</h4>
<p>Loyihaning boshidayoq <code>useAppSelector</code>/<code>useAppDispatch</code>ni yarating va <strong>hamma joyda</strong> shularni ishlating. Bitta joyda xom versiyasini qoldirish — butun loyiha bo'ylab tip xavfsizligidagi teshikka aylanadi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>RootState</code>/<code>AppDispatch</code> — store'dan <code>ReturnType</code>/<code>typeof</code> orqali chiqariladi, qo'lda yozilmaydi</li>
<li>✅ <code>useAppSelector</code>/<code>useAppDispatch</code> — loyiha bo'ylab HAR DOIM shular ishlatiladi, xom <code>useSelector</code>/<code>useDispatch</code> emas</li>
<li>✅ <code>PayloadAction&lt;T&gt;</code> — reducer'dagi action.payload'ni tiplaydi</li>
<li>✅ <code>createAsyncThunk&lt;Qaytadigan, Argument&gt;</code> — ikkita generic bilan to'liq tiplanadi</li>
<li>✅ Bitta joyda xom useSelector qoldirish — butun loyihaning tip xavfsizligini zaiflashtiradi</li>
</ul>
"""

L9_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 9: Redux Toolkit + TypeScript birga
// ════════════════════════════════════════════════════════════════════

import { configureStore, createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook, Provider } from 'react-redux';

// ─────────────────────────────────────────────────────────────────────
// 1) Slice state va PayloadAction bilan tiplash
// ─────────────────────────────────────────────────────────────────────

interface AppState {
  theme: 'light' | 'dark';
  count: number;
}

const initialState: AppState = { theme: 'light', count: 0 };

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    },
    increment: (state) => { state.count += 1; },
  },
});

export const { setTheme, increment } = appSlice.actions;

// ─────────────────────────────────────────────────────────────────────
// 2) Typed thunk — <Qaytadigan, Argument>
// ─────────────────────────────────────────────────────────────────────

interface Foydalanuvchi { id: number; ism: string; }

export const fetchUser = createAsyncThunk<Foydalanuvchi, number>(
  'user/fetchUser',
  async (userId) => {
    const res = await fetch(`/api/users/${userId}`);
    return res.json() as Promise<Foydalanuvchi>;
  }
);

// ─────────────────────────────────────────────────────────────────────
// 3) Store + RootState/AppDispatch — QO'LDA emas, store'dan chiqarilgan
// ─────────────────────────────────────────────────────────────────────

const store = configureStore({
  reducer: { app: appSlice.reducer },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// ─────────────────────────────────────────────────────────────────────
// 4) Tiplangan hook'lar — loyiha bo'ylab HAR DOIM shular ishlatiladi
// ─────────────────────────────────────────────────────────────────────

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ─────────────────────────────────────────────────────────────────────
// 5) Komponent — to'liq tiplangan
// ─────────────────────────────────────────────────────────────────────

function ThemeLabel() {
  const theme = useAppSelector((state) => state.app.theme); // to'liq autocomplete
  const dispatch = useAppDispatch();
  return (
    <div>
      <p>Mavzu: {theme}</p>
      <button onClick={() => dispatch(setTheme(theme === 'light' ? 'dark' : 'light'))}>
        Almashtirish
      </button>
    </div>
  );
}

function App() {
  return (
    <Provider store={store}>
      <ThemeLabel />
    </Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 6) Ataylab xato — xom useSelector ishlatish
// ─────────────────────────────────────────────────────────────────────

/*
import { useSelector } from 'react-redux'; // ❌ tiplanmagan, to'g'ridan-to'g'ri

function EskiKomponent() {
  const theme = useSelector((state) => state.app.theme);
  // ❌ Parameter 'state' implicitly has an 'any' type.
  // state.apr.theme kabi xato yozsangiz ham — jim qoladi, tekshirmaydi.
}
*/
"""

L9_EX = [
    {
        "title": "RootState qanday olinishi kerak?",
        "description": "RootState turini yaratishning to'g'ri, tavsiya etiladigan usuli qaysi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Qo'lda interface RootState { app: {...} } deb yozish",
            "export type RootState = ReturnType<typeof store.getState>",
            "any turini ishlatish",
            "Har bir komponentda alohida interface yozish",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Qo'lda yozilgan tur store o'zgarsa eskirib qoladi — avtomatik chiqarish yaxshiroq.",
        "explanation": (
            "RootState har doim `ReturnType<typeof store.getState>` orqali "
            "chiqariladi, shunda store'ga yangi slice qo'shilganda RootState "
            "avtomatik yangilanadi va hech qachon eskirmaydi."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega useAppSelector'ni loyiha bo'ylab har doim ishlatish kerak?",
        "description": "Agar bitta komponentda oddiy react-redux'ning useSelector'i ishlatilsa (useAppSelector o'rniga), nima yuz beradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Hech narsa — ikkalasi bir xil ishlaydi",
            "O'sha komponentda state parametri tiplanmagan (any) bo'lib qoladi, tip xavfsizligi yo'qoladi",
            "Ilova butunlay ishlamay qoladi",
            "Faqat production build'da muammo bo'ladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "useAppSelector — RootState bilan \"qulflangan\" useSelector. Xom versiyasi bunday qulflanmagan.",
        "explanation": (
            "Xom useSelector RootState haqida hech narsa bilmaydi — state "
            "avtomatik ravishda any (yoki tekshirilmagan) bo'lib qoladi. "
            "Shu bitta komponentda butun tip xavfsizligi yo'qoladi."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "createAsyncThunk generic'lari qanday tartibda?",
        "description": "createAsyncThunk<Foydalanuvchi, number>(...) yozilganda, generic'larning ma'nosi qaysi tartibda?",
        "exercise_type": "multiple_choice",
        "options": [
            "Birinchi — argument turi, ikkinchi — qaytadigan qiymat turi",
            "Birinchi — fulfilled qaytaradigan qiymat turi, ikkinchi — thunk argument turi",
            "Ikkalasi ham bir xil narsani anglatadi",
            "Birinchi — reducer nomi, ikkinchi — action turi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "createAsyncThunk<Returned, ThunkArg> — avval natija, keyin argument.",
        "explanation": (
            "createAsyncThunk<Returned, ThunkArg> — birinchi generic thunk "
            "muvaffaqiyatli tugaganda qaytaradigan qiymat turi (fulfilled "
            "payload), ikkinchisi — thunk chaqirilganda kutilgan argument turi."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega bitta joyda xom useSelector qoldirish butun loyihaga ta'sir qiladi?",
        "description": (
            "Loyihada useAppSelector/useAppDispatch yaratilgan bo'lsa-da, "
            "agar bitta eski komponent hali ham react-redux'dan to'g'ridan-"
            "to'g'ri useSelector import qilsa, bu nima uchun \"kichik\" emas, "
            "butun loyihaning tip xavfsizligiga ta'sir qiluvchi muammo "
            "hisoblanadi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "TypeScript'ning tip xavfsizligi faqat u qo'llanilgan joylarda "
            "ishlaydi. Agar bitta komponent xom useSelector ishlatsa, o'sha "
            "komponent ichida state parametri tekshirilmaydi va dasturchi "
            "state.app.theme o'rniga xato yozgan bo'lsa ham (masalan "
            "state.apr.theme), TypeScript bu haqda hech qanday xato "
            "bermaydi. Bu — kod bazasida \"teshik\" hosil qiladi: qolgan "
            "butun loyiha tiplangan bo'lsa ham, aynan shu joyda runtime "
            "xatosi yuzaga kelishi mumkin, va bu odatda kod ko'rib chiqishda "
            "(code review) yoki avtomatik lint qoidasi bo'lmasa, e'tibordan "
            "chetda qolib ketadi."
        ),
        "hint": "Tip xavfsizligi faqat qo'llanilgan joyda ishlaydi — qolgan joy tiplangan bo'lishi buni qoplamaydi.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


R2_TEXT = """\
<h2>R2 — Modul 2 takrorlash: Tiplangan Kutubxona ilovasi</h2>

<p>7-9 darslarni birga ishlatib, kichik <strong>Kutubxona</strong> ilovasi yasaymiz: generic <code>List&lt;T&gt;</code> komponenti (8-dars), tiplangan props/state (7-dars), va to'liq tiplangan Redux Toolkit — RootState, AppDispatch, typed thunk (9-dars).</p>

<h3>Loyihaning maqsadi</h3>
<ul>
<li><code>Book</code> interfeysi: <code>id, title, author, available: boolean</code></li>
<li><code>booksSlice</code> — <code>createAsyncThunk&lt;Book[], void&gt;</code> bilan kitoblarni yuklash</li>
<li>Generic <code>List&lt;T extends {'{'} id: number {'}'}&gt;</code> komponenti — kitoblarni ko'rsatish uchun qayta ishlatiladi</li>
<li><code>useAppSelector</code>/<code>useAppDispatch</code> — hamma joyda, xom versiyalarsiz</li>
</ul>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — Book interfeysi va booksSlice</h4>
<p><code>initialState: { items: Book[]; loading: boolean; error: string | null }</code>. <code>fetchBooks</code> thunk — <code>createAsyncThunk&lt;Book[], void&gt;</code>.</p>

<h4>Vazifa 2 — RootState/AppDispatch + typed hooks</h4>
<p>9-darsdagidek — store'dan chiqarilgan, qo'lda yozilmagan.</p>

<h4>Vazifa 3 — generic List&lt;T&gt; komponenti</h4>
<p>8-darsdagi <code>ListWithId&lt;T extends {'{'} id: number {'}'}&gt;</code>ni qayta ishlating — kitoblar ro'yxatini shu orqali ko'rsating.</p>

<h4>Vazifa 4 — mavjudlik belgisi</h4>
<p>Har bir kitob yonida: <code>available ? "✅ Mavjud" : "❌ Band"</code>.</p>

<h3>🐛 Ataylab qiyin: generic komponentni typed Redux state bilan birlashtirish</h3>
<p>Eng ko'p adashadigan joy: <code>useAppSelector((state) =&gt; state.books.items)</code> qaytargan <code>Book[]</code>ni to'g'ridan-to'g'ri generic <code>List&lt;T&gt;</code>ga uzatish — bu ikkalasi mustaqil tizim (Redux tipi va component generic tipi) bo'lsa-da, TypeScript ularni avtomatik moslashtiradi, chunki <code>Book</code> allaqachon <code>{'{'} id: number {'}'}</code> cheklovini qanoatlantiradi.</p>

<h3>Boshlang'ich kod</h3>
<pre><code>interface Book {
  id: number;
  title: string;
  author: string;
  available: boolean;
}

interface BooksState {
  items: Book[];
  loading: boolean;
  error: string | null;
}

// Vazifa: fetchBooks thunk, booksSlice, RootState/AppDispatch, typed hooks
</code></pre>

<h3>Yechim</h3>
<details>
<summary>To'liq yechim — avval o'zingiz urinib ko'ring!</summary>
<pre><code>import { createSlice, createAsyncThunk, configureStore, PayloadAction } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook, Provider } from 'react-redux';
import { useEffect } from 'react';

interface Book {
  id: number;
  title: string;
  author: string;
  available: boolean;
}

interface BooksState {
  items: Book[];
  loading: boolean;
  error: string | null;
}

const initialState: BooksState = { items: [], loading: false, error: null };

export const fetchBooks = createAsyncThunk&lt;Book[], void&gt;(
  'books/fetchBooks',
  async () =&gt; {
    const res = await fetch('/api/books');
    if (!res.ok) throw new Error('Kitoblarni yuklab bo\\'lmadi');
    return res.json() as Promise&lt;Book[]&gt;;
  }
);

const booksSlice = createSlice({
  name: 'books',
  initialState,
  reducers: {},
  extraReducers: (builder) =&gt; {
    builder
      .addCase(fetchBooks.pending, (state) =&gt; { state.loading = true; state.error = null; })
      .addCase(fetchBooks.fulfilled, (state, action: PayloadAction&lt;Book[]&gt;) =&gt; {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchBooks.rejected, (state, action) =&gt; {
        state.loading = false;
        state.error = action.error.message ?? "Noma'lum xato";
      });
  },
});

const store = configureStore({ reducer: { books: booksSlice.reducer } });

export type RootState = ReturnType&lt;typeof store.getState&gt;;
export type AppDispatch = typeof store.dispatch;
export const useAppDispatch = () =&gt; useDispatch&lt;AppDispatch&gt;();
export const useAppSelector: TypedUseSelectorHook&lt;RootState&gt; = useSelector;

// Generic List — 8-darsdagi naqsh
interface ListProps&lt;T&gt; {
  items: T[];
  renderItem: (item: T) =&gt; React.ReactNode;
}

function List&lt;T extends { id: number }&gt;({ items, renderItem }: ListProps&lt;T&gt;) {
  return &lt;ul&gt;{items.map((item) =&gt; &lt;li key={item.id}&gt;{renderItem(item)}&lt;/li&gt;)}&lt;/ul&gt;;
}

function KutubxonaRoyxati() {
  const dispatch = useAppDispatch();
  const { items, loading, error } = useAppSelector((state) =&gt; state.books);

  useEffect(() =&gt; { dispatch(fetchBooks()); }, [dispatch]);

  if (loading) return &lt;p&gt;⏳ Yuklanmoqda...&lt;/p&gt;;
  if (error) return &lt;p&gt;❌ {error}&lt;/p&gt;;

  return (
    &lt;List&lt;Book&gt; items={items} renderItem={(book) =&gt; (
      &lt;span&gt;{book.title} — {book.author} {book.available ? '✅ Mavjud' : '❌ Band'}&lt;/span&gt;
    )} /&gt;
  );
}

function App() {
  return (
    &lt;Provider store={store}&gt;
      &lt;KutubxonaRoyxati /&gt;
    &lt;/Provider&gt;
  );
}</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ 7-9 darslarning hammasi birga: tiplangan props/state, generic komponentlar, to'liq tiplangan Redux Toolkit</li>
<li>✅ Redux'dan kelgan tiplangan ma'lumot (Book[]) generic komponentga to'g'ridan-to'g'ri mos keladi, agar cheklovni qanoatlantirsa</li>
<li>✅ RootState/AppDispatch/typed hooks — har doim bir marta yaratilib, butun loyihada qayta ishlatiladi</li>
</ul>
"""

R2_CODE = """\
// ════════════════════════════════════════════════════════════════════
// REVISION 2: Tiplangan Kutubxona ilovasi
// Modul 2: typed props/state + generics + typed Redux Toolkit
// ════════════════════════════════════════════════════════════════════

import { createSlice, createAsyncThunk, configureStore, PayloadAction } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook, Provider } from 'react-redux';
import { useEffect } from 'react';

interface Book {
  id: number;
  title: string;
  author: string;
  available: boolean;
}

interface BooksState {
  items: Book[];
  loading: boolean;
  error: string | null;
}

const initialState: BooksState = { items: [], loading: false, error: null };

export const fetchBooks = createAsyncThunk<Book[], void>(
  'books/fetchBooks',
  async () => {
    const res = await fetch('/api/books');
    if (!res.ok) throw new Error("Kitoblarni yuklab bo'lmadi");
    return res.json() as Promise<Book[]>;
  }
);

const booksSlice = createSlice({
  name: 'books',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchBooks.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchBooks.fulfilled, (state, action: PayloadAction<Book[]>) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchBooks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? "Noma'lum xato";
      });
  },
});

const store = configureStore({ reducer: { books: booksSlice.reducer } });

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ─────────────────────────────────────────────────────────────────────
// Generic List — 8-darsdagi naqsh qayta ishlatildi
// ─────────────────────────────────────────────────────────────────────

interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

function List<T extends { id: number }>({ items, renderItem }: ListProps<T>) {
  return <ul>{items.map((item) => <li key={item.id}>{renderItem(item)}</li>)}</ul>;
}

function KutubxonaRoyxati() {
  const dispatch = useAppDispatch();
  const { items, loading, error } = useAppSelector((state) => state.books);

  useEffect(() => { dispatch(fetchBooks()); }, [dispatch]);

  if (loading) return <p>⏳ Yuklanmoqda...</p>;
  if (error) return <p>❌ {error}</p>;

  return (
    <List<Book> items={items} renderItem={(book) => (
      <span>{book.title} — {book.author} {book.available ? '✅ Mavjud' : '❌ Band'}</span>
    )} />
  );
}

function App() {
  return (
    <Provider store={store}>
      <KutubxonaRoyxati />
    </Provider>
  );
}
"""

R2_EX = [
    {
        "title": "Book[] generic List<T>ga mos keladimi?",
        "description": "List<T extends { id: number }> komponentiga Book[] (id, title, author, available maydonlari bilan) uzatish mumkinmi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Yo'q — Book maxsus konvertatsiya qilinishi kerak",
            "Ha — Book allaqachon id: number maydoniga ega, cheklovni qanoatlantiradi",
            "Faqat id maydonini alohida uzatish kerak",
            "Faqat List komponentini Book uchun qayta yozish kerak",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Cheklov faqat \"id: number bo'lishi kerak\" deydi — qo'shimcha maydonlar muammo emas.",
        "explanation": (
            "T extends { id: number } — T kamida id: number maydoniga ega "
            "bo'lishini talab qiladi. Book bu shartni qanoatlantiradi (va "
            "yana qo'shimcha maydonlarga ega), shuning uchun to'g'ridan-"
            "to'g'ri mos keladi."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "fetchBooks thunk generic'lari",
        "description": "createAsyncThunk<Book[], void>('books/fetchBooks', ...) — ikkinchi generic (void) nimani anglatadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Thunk hech narsa qaytarmaydi",
            "Thunk chaqirilganda hech qanday argument kutilmaydi",
            "Thunk hech qachon xato bermaydi",
            "Reducer hech narsa qilmaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Ikkinchi generic — ThunkArg, ya'ni dispatch(fetchBooks(???)) qavs ichidagi argument turi.",
        "explanation": (
            "createAsyncThunk<Returned, ThunkArg> — ikkinchi generic thunk "
            "argumentining turi. void — dispatch(fetchBooks()) hech qanday "
            "argumentsiz chaqirilishini bildiradi."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "useAppSelector qayerdan import qilinishi kerak?",
        "description": "Kutubxona ilovasidagi har bir komponentda state'ga kirish uchun qaysi hook ishlatilishi kerak?",
        "exercise_type": "multiple_choice",
        "options": [
            "react-redux'dan to'g'ridan-to'g'ri useSelector",
            "Loyihada yaratilgan, RootState bilan tiplangan useAppSelector",
            "useContext",
            "useState",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "9-darsni eslang — xom useSelector tip xavfsizligini yo'qotadi.",
        "explanation": (
            "Har doim loyihada yaratilgan, RootState bilan tiplangan "
            "useAppSelector ishlatilishi kerak — xom useSelector state "
            "parametrini tekshirishsiz qoldiradi."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega generic komponent va tiplangan Redux birga yaxshi ishlaydi?",
        "description": (
            "Generic List<T> komponenti va to'liq tiplangan Redux Toolkit "
            "(RootState, typed thunk) birga ishlatilganda, bu birlashma "
            "qanday amaliy foyda beradi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Redux Toolkit store'dan kelayotgan ma'lumot (masalan, Book[]) "
            "to'liq tiplangan bo'lgani uchun, uni generic komponentga "
            "uzatganda TypeScript avtomatik ravishda komponent ichidagi "
            "renderItem funksiyasi to'g'ri maydonlarni (title, author, "
            "available) ishlatayotganini tekshiradi. Agar kimdir noto'g'ri "
            "maydon nomi yozsa (masalan book.nomi), bu darhol compile "
            "xatosi sifatida ko'rinadi. Bu ikki qatlam — global state va "
            "qayta ishlatiladigan UI komponentlari — bir-biriga mos kelib, "
            "butun ma'lumot oqimi boshidan oxirigacha tip xavfsiz bo'ladi."
        ),
        "hint": "Ma'lumot store'dan komponentgacha bo'lgan butun yo'lni tip xavfsizligi qamrab olishi haqida o'ylang.",
        "difficulty_level": "Medium",
        "points": 4,
    },
]


L10_TEXT = """\
<h2>Jest + React Testing Library — birinchi test</h2>

<pre class="mermaid">
flowchart LR
    R["render(&lt;Component /&gt;)"] --> S["screen.getByRole(...)"]
    S --> A["expect(...).toBeInTheDocument()"]
    A --> V["Foydalanuvchi ko'radigan narsani tekshirish"]
</pre>

<p>Hozirgacha kodingizni <strong>qo'lda</strong> tekshirdingiz — brauzerni ochib, tugmani bosib, natijani ko'zingiz bilan ko'rdingiz. Bu ishlaydi, lekin loyiha kattalashgan sari sekinlashadi va unutilib qoladi. Bu darsda — kodni <strong>avtomatik</strong> tekshirishni boshlaymiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — o'rnatish va birinchi test fayli</h4>
<pre><code>// Terminal (Vite loyihasida):
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom</code></pre>

<pre><code>// Counter.tsx
function Counter() {
  const [son, setSon] = useState(0);
  return (
    &lt;div&gt;
      &lt;h2&gt;Hisoblagich&lt;/h2&gt;
      &lt;p&gt;Son: {son}&lt;/p&gt;
      &lt;button onClick={() =&gt; setSon(s =&gt; s + 1)}&gt;+1&lt;/button&gt;
    &lt;/div&gt;
  );
}</code></pre>

<pre><code>// Counter.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, test, expect } from 'vitest';
import Counter from './Counter';

describe('Counter', () =&gt; {
  test('boshlang\\'ich holatda 0 ko\\'rsatadi', () =&gt; {
    render(&lt;Counter /&gt;);
    expect(screen.getByText('Son: 0')).toBeInTheDocument();
  });
});</code></pre>

<h4>BLOKA 2 — screen bilan qidirish: getByRole, getByText</h4>
<pre><code>test('sarlavha va tugma ko\\'rinadi', () =&gt; {
  render(&lt;Counter /&gt;);

  // getByRole — eng tavsiya etiladigan usul: foydalanuvchi qanday ko'rsa, shunday qidiring
  expect(screen.getByRole('heading', { name: 'Hisoblagich' })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: '+1' })).toBeInTheDocument();

  // getByText — matn bo'yicha
  expect(screen.getByText('Son: 0')).toBeInTheDocument();
});</code></pre>

<h4>BLOKA 3 — bir nechta assertion, matcher'lar</h4>
<pre><code>test('Counter to\\'liq render bo\\'ladi', () =&gt; {
  render(&lt;Counter /&gt;);
  const sarlavha = screen.getByRole('heading');

  expect(sarlavha).toBeInTheDocument();
  expect(sarlavha).toHaveTextContent('Hisoblagich');
  expect(sarlavha).toBeVisible();
});</code></pre>

<h3>🐛 Ataylab xato — implementatsiya detalini test qilish</h3>
<pre><code>// ❌ CSS klass yoki DOM tuzilishi orqali qidirish
test('tugma ishlaydi (yomon test)', () =&gt; {
  const { container } = render(&lt;Counter /&gt;);
  const tugma = container.querySelector('.counter-btn-primary'); // ❌
  expect(tugma).toBeInTheDocument();
});</code></pre>

<p><strong>Muammo:</strong> Bu test ishlaydi — <strong>hozircha</strong>. Lekin dizayner CSS klass nomini <code>.counter-btn-primary</code>dan <code>.btn-counter-main</code>ga o'zgartirsa (foydalanuvchi uchun <strong>hech narsa o'zgarmaydi</strong> — tugma xuddi shunday ko'rinadi va ishlaydi), test <strong>buziladi</strong>. Siz kodni to'g'ri o'zgartirdingiz, lekin test "xato" deb signal beradi — bu <strong>yolg'on signal</strong> (false negative).</p>

<pre><code>// ✅ Foydalanuvchi ko'radigan narsa orqali qidirish — CSS o'zgarsa ham ishlaydi
test('tugma ishlaydi (yaxshi test)', () =&gt; {
  render(&lt;Counter /&gt;);
  const tugma = screen.getByRole('button', { name: '+1' });
  expect(tugma).toBeInTheDocument();
});</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. RTL falsafasi — "foydalanuvchi kabi test qiling"</h4>
<p>React Testing Library'ning asosiy qoidasi: <em>"Testingiz kod qanchalik ko'p foydalanuvchi ishlatish usuliga o'xshasa, shunchalik ko'proq ishonch beradi."</em> Foydalanuvchi CSS klass nomini yoki ichki state o'zgaruvchisini bilmaydi — u faqat ekranda nima ko'rinishini va bosishi mumkin bo'lgan narsalarni biladi.</p>

<h4>2. Qidiruv ustuvorligi (eng yaxshidan eng yomonga)</h4>
<table>
<tr><th>Daraja</th><th>Usul</th><th>Nega</th></tr>
<tr><td>1 (eng yaxshi)</td><td><code>getByRole</code></td><td>Accessibility'ga mos, eng barqaror</td></tr>
<tr><td>2</td><td><code>getByLabelText</code></td><td>Formalar uchun</td></tr>
<tr><td>3</td><td><code>getByText</code></td><td>Oddiy matn uchun</td></tr>
<tr><td>4 (oxirgi chora)</td><td><code>getByTestId</code></td><td>Faqat boshqa yo'l bo'lmaganda</td></tr>
<tr><td>❌</td><td><code>container.querySelector('.class')</code></td><td>Implementatsiya detali — ishlatmang</td></tr>
</table>

<h4>3. getBy vs queryBy vs findBy — qisqacha</h4>
<ul>
<li><code>getByX</code> — topilmasa, DARHOL xato (throw) — element albatta bo'lishi kerak bo'lganda</li>
<li><code>queryByX</code> — topilmasa <code>null</code> qaytaradi — "element YO'Qligini" tekshirish uchun</li>
<li><code>findByX</code> — async, kutadi — keyingi darsda (async testlash)</li>
</ul>

<h4>4. Nega implementatsiya detalini test qilmaslik kerak?</h4>
<p>Test — kodning <strong>tashqi xatti-harakatini</strong> tekshirishi kerak, <strong>qanday</strong> qilib erishilganini emas. Agar siz <code>useState</code>ni <code>useReducer</code>ga almashtirsangiz (natija bir xil bo'lsa), yaxshi test o'zgarishsiz o'tadi. Implementatsiyani tekshiruvchi test esa — kerak bo'lmagan joyda buziladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>render(&lt;Component /&gt;)</code> + <code>screen.getByX()</code> — asosiy test yozish naqshi</li>
<li>✅ <code>getByRole</code> — eng tavsiya etiladigan qidiruv usuli (accessibility'ga mos)</li>
<li>✅ <code>toBeInTheDocument()</code>, <code>toHaveTextContent()</code>, <code>toBeVisible()</code> — keng tarqalgan matcher'lar</li>
<li>✅ CSS klass/DOM tuzilishi orqali qidirish — implementatsiya detali, ishlatmang</li>
<li>✅ RTL falsafasi: "foydalanuvchi qanday ishlatsa, shunday test qiling"</li>
</ul>
"""

L10_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 10: Jest/Vitest + React Testing Library — birinchi test
// ════════════════════════════════════════════════════════════════════

import { useState } from 'react';
import { render, screen } from '@testing-library/react';
import { describe, test, expect } from 'vitest';

// ─────────────────────────────────────────────────────────────────────
// 1) Test qilinadigan komponent
// ─────────────────────────────────────────────────────────────────────

function Counter() {
  const [son, setSon] = useState(0);
  return (
    <div>
      <h2>Hisoblagich</h2>
      <p>Son: {son}</p>
      <button className="counter-btn-primary" onClick={() => setSon(s => s + 1)}>+1</button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 2) Testlar — getByRole, getByText, matcher'lar
// ─────────────────────────────────────────────────────────────────────

describe('Counter', () => {
  test("boshlang'ich holatda 0 ko'rsatadi", () => {
    render(<Counter />);
    expect(screen.getByText('Son: 0')).toBeInTheDocument();
  });

  test("sarlavha va tugma ko'rinadi", () => {
    render(<Counter />);
    expect(screen.getByRole('heading', { name: 'Hisoblagich' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '+1' })).toBeInTheDocument();
  });

  test('Counter to\\'liq render bo\\'ladi', () => {
    render(<Counter />);
    const sarlavha = screen.getByRole('heading');

    expect(sarlavha).toBeInTheDocument();
    expect(sarlavha).toHaveTextContent('Hisoblagich');
    expect(sarlavha).toBeVisible();
  });
});

// ─────────────────────────────────────────────────────────────────────
// 3) Ataylab xato — implementatsiya detalini test qilish
// ─────────────────────────────────────────────────────────────────────

/*
test('tugma ishlaydi (YOMON test — CSS klass orqali)', () => {
  const { container } = render(<Counter />);
  // ❌ .counter-btn-primary klass nomi o'zgarsa (dizayn refaktori),
  // bu test buziladi, garchi tugma foydalanuvchi uchun bir xil ishlasa ham.
  const tugma = container.querySelector('.counter-btn-primary');
  expect(tugma).toBeInTheDocument();
});
*/

// ✅ To'g'ri variant — CSS o'zgarsa ham ishlaydi
test('tugma ishlaydi (YAXSHI test — role orqali)', () => {
  render(<Counter />);
  const tugma = screen.getByRole('button', { name: '+1' });
  expect(tugma).toBeInTheDocument();
});
"""

L10_EX = [
    {
        "title": "RTL'ning asosiy falsafasi qaysi?",
        "description": "React Testing Library'ning asosiy tamoyili qaysi jumla bilan to'g'ri ifodalanadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Har bir ichki funksiyani alohida test qiling",
            "Testingiz foydalanuvchi ilovani qanday ishlatishiga qanchalik o'xshasa, shunchalik yaxshi",
            "Faqat CSS klasslar orqali element qidiring",
            "State o'zgaruvchilarini to'g'ridan-to'g'ri tekshiring",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "RTL — \"foydalanuvchi kabi test qilish\" kutubxonasi.",
        "explanation": (
            "RTL falsafasi: test kod qanday ishlatilishini emas, foydalanuvchi "
            "uni qanday ishlatishini simulyatsiya qilishi kerak — shunda test "
            "haqiqiy ishonch beradi."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Eng tavsiya etiladigan qidiruv usuli qaysi?",
        "description": "screen orqali element qidirishda, RTL bo'yicha eng ustuvor (tavsiya etiladigan) usul qaysi?",
        "exercise_type": "multiple_choice",
        "options": [
            "getByTestId",
            "container.querySelector('.class')",
            "getByRole",
            "getByClassName",
        ],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Accessibility rolига mos qidiruv — eng barqaror va foydalanuvchi tajribasiga eng yaqin.",
        "explanation": (
            "getByRole — eng tavsiya etiladigan usul, chunki u accessibility "
            "rollariga asoslangan va CSS/DOM tuzilishi o'zgarganda ham "
            "barqaror qoladi."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega CSS klass orqali qidirish yomon amaliyot?",
        "description": "container.querySelector('.btn-primary') orqali tugmani topish nega yaxshi test yozish amaliyoti hisoblanmaydi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bu sekinroq ishlaydi",
            "Chunki CSS klass nomi o'zgarsa (foydalanuvchi tajribasi o'zgarmasa ham), test yolg'on buziladi",
            "Chunki querySelector Vitest'da mavjud emas",
            "Bunda muammo yo'q, bu eng yaxshi usul",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "CSS klass — implementatsiya detali, foydalanuvchi buni bilmaydi va ko'rmaydi.",
        "explanation": (
            "CSS klass nomlari implementatsiya detali hisoblanadi — ular "
            "dizayn refaktorida tez-tez o'zgaradi, garchi foydalanuvchi "
            "tajribasi bir xil qolsa ham. Bunga bog'liq test yolg'on signal beradi."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega implementatsiya detalini emas, xatti-harakatni test qilish kerak?",
        "description": (
            "Agar komponent ichida useState o'rniga useReducer ishlatilsa "
            "(tashqi xatti-harakat bir xil qolgan holda), nega yaxshi "
            "yozilgan test buzilmasligi kerak? O'z so'zlaringiz bilan "
            "tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Yaxshi test komponentning foydalanuvchiga ko'rinadigan xatti-"
            "harakatini tekshiradi (masalan, tugma bosilganda ekranda nima "
            "ko'rsatiladi), ichki implementatsiya tafsilotlarini (qaysi hook "
            "ishlatilgani, ichki state o'zgaruvchi nomi) emas. useState'dan "
            "useReducer'ga o'tish — bu ichki refaktoring, foydalanuvchi uchun "
            "hech narsa o'zgarmaydi: tugma bosilganda son baribir oshadi. "
            "Shuning uchun getByRole/getByText orqali yozilgan test bu "
            "refaktoringdan keyin ham muvaffaqiyatli o'tishi kerak — aks "
            "holda test kodni erkin refaktor qilishga to'sqinlik qiladi."
        ),
        "hint": "Refaktoring — tashqi xatti-harakatni o'zgartirmasdan ichki kodni yaxshilash ekanini eslang.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L11_TEXT = """\
<h2>User events, async testlash va API mocking</h2>

<pre class="mermaid">
flowchart LR
    UE["userEvent.click(tugma)"] -->|dispatch(fetchUsers)| M["mock fetch javob beradi"]
    M -->|Promise resolve bo'ladi| FB["findByText — kutadi va topadi"]
</pre>

<p>10-darsda statik komponentlarni test qildik. Endi — foydalanuvchi <strong>haqiqiy harakat</strong> qilganda (bosish, yozish) va natija <strong>asinxron</strong> (API so'rovidan keyin) kelganda qanday test yozishni ko'ramiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — userEvent bilan haqiqiy foydalanuvchi harakati</h4>
<pre><code>import userEvent from '@testing-library/user-event';
import { render, screen } from '@testing-library/react';

test('tugma bosilganda son oshadi', async () =&gt; {
  const user = userEvent.setup();
  render(&lt;Counter /&gt;);

  const tugma = screen.getByRole('button', { name: '+1' });
  await user.click(tugma); // ✅ haqiqiy klik — focus, pointerdown, pointerup, click

  expect(screen.getByText('Son: 1')).toBeInTheDocument();
});

test('inputga yozish ishlaydi', async () =&gt; {
  const user = userEvent.setup();
  render(&lt;IsmForma /&gt;);

  const input = screen.getByRole('textbox');
  await user.type(input, 'Olim'); // har bir harfni alohida-alohida "yozadi"

  expect(screen.getByText('Salom, Olim!')).toBeInTheDocument();
});</code></pre>

<h4>BLOKA 2 — asinxron natijani kutish: findBy</h4>
<pre><code>function FoydalanuvchilarRoyxati() {
  const [data, setData] = useState&lt;string[] | null&gt;(null);

  useEffect(() =&gt; {
    fetch('/api/users').then(res =&gt; res.json()).then(setData);
  }, []);

  if (!data) return &lt;p&gt;Yuklanmoqda...&lt;/p&gt;;
  return &lt;ul&gt;{data.map(u =&gt; &lt;li key={u}&gt;{u}&lt;/li&gt;)}&lt;/ul&gt;;
}</code></pre>

<pre><code>test('foydalanuvchilar yuklanadi', async () =&gt; {
  render(&lt;FoydalanuvchilarRoyxati /&gt;);

  // Boshida "Yuklanmoqda..." ko'rinadi
  expect(screen.getByText('Yuklanmoqda...')).toBeInTheDocument();

  // findByText — TOPILGUNCHA KUTADI (default: 1000ms gacha qayta urinadi)
  const olim = await screen.findByText('Olim');
  expect(olim).toBeInTheDocument();
});</code></pre>

<h4>BLOKA 3 — fetch'ni mock qilish</h4>
<pre><code>import { vi } from 'vitest';

beforeEach(() =&gt; {
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () =&gt; ['Olim', 'Vali'],
  }) as any;
});</code></pre>

<p>Test haqiqiy serverga so'rov yubormaydi — <code>fetch</code>ning o'zi soxta (mock) javob qaytaradi. Bu — tezroq, ishonchli (internet kerak emas) va serverga bog'liq bo'lmagan testlar yozish imkonini beradi.</p>

<h3>🐛 Ataylab xato — getByText'ni asinxron natija uchun ishlatish</h3>
<pre><code>test('foydalanuvchilar yuklanadi (XATO)', async () =&gt; {
  render(&lt;FoydalanuvchilarRoyxati /&gt;);

  // ❌ getByText — SINXRON, darhol tekshiradi. Fetch hali tugamagan!
  const olim = screen.getByText('Olim');
  expect(olim).toBeInTheDocument();
});</code></pre>

<pre><code>TestingLibraryElementError: Unable to find an element with the text: Olim.</code></pre>

<p><strong>Sabab:</strong> <code>getByText</code> — <strong>darhol</strong> qidiradi, kutmaydi. Fetch hali <code>pending</code> holatida bo'lgani uchun, "Olim" hali DOM'da yo'q — komponent hali "Yuklanmoqda..." ko'rsatmoqda. <code>findByText</code> esa — element paydo bo'lguncha (yoki timeout'gacha) <strong>qayta-qayta tekshiradi</strong>.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. userEvent vs fireEvent</h4>
<p><code>fireEvent.click(btn)</code> — bitta xom DOM event yaratadi. <code>userEvent.click(btn)</code> — haqiqiy foydalanuvchi qiladigan <strong>butun zanjirni</strong> simulyatsiya qiladi: pointerdown → focus → pointerup → click. Ba'zi bug'lar (masalan, <code>disabled</code> tugma yoki <code>pointer-events: none</code>) faqat <code>userEvent</code> bilan to'g'ri aniqlanadi.</p>

<h4>2. getBy vs findBy — qachon qaysi biri?</h4>
<table>
<tr><th>Query</th><th>Sinxron/Async</th><th>Qachon ishlatiladi</th></tr>
<tr><td><code>getByX</code></td><td>Sinxron</td><td>Element HOZIR DOM'da bo'lishi kerak</td></tr>
<tr><td><code>findByX</code></td><td>Async (Promise)</td><td>Element ASINXRON (fetch, timeout) keyin paydo bo'ladi</td></tr>
<tr><td><code>queryByX</code></td><td>Sinxron, null qaytaradi</td><td>Element YO'Qligini tekshirish</td></tr>
</table>

<h4>3. waitFor — umumiyroq kutish vositasi</h4>
<pre><code>import { waitFor } from '@testing-library/react';

await waitFor(() =&gt; {
  expect(mockFn).toHaveBeenCalledTimes(1);
});
// findBy — faqat element qidirish uchun. waitFor — istalgan assertionni kutish uchun.</code></pre>

<h4>4. fetch'ni nega mock qilish kerak?</h4>
<ul>
<li>Test tezroq ishlaydi — haqiqiy tarmoq so'rovi yo'q</li>
<li>Test <strong>barqaror</strong> — internet yo'qligi yoki server o'chganda ham o'tadi</li>
<li>Xato holatlarini ham osongina simulyatsiya qilish mumkin (<code>mockRejectedValue</code>)</li>
</ul>

<h4>5. Xato holatini test qilish</h4>
<pre><code>test('server xato qaytarsa, xato xabari ko\\'rinadi', async () =&gt; {
  global.fetch = vi.fn().mockResolvedValue({ ok: false, status: 500 }) as any;
  render(&lt;FoydalanuvchilarRoyxati /&gt;);

  const xato = await screen.findByText(/xato/i);
  expect(xato).toBeInTheDocument();
});</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>userEvent</code> — haqiqiy foydalanuvchi harakatini to'liq simulyatsiya qiladi, <code>fireEvent</code>dan ishonchliroq</li>
<li>✅ <code>findByX</code> — asinxron paydo bo'ladigan elementlar uchun, element topilguncha kutadi</li>
<li>✅ <code>getByX</code>ni asinxron natija uchun ishlatish — "Unable to find element" xatosiga olib keladi</li>
<li>✅ <code>vi.fn()</code> bilan <code>fetch</code>ni mock qilish — tezroq, barqaror, server'siz testlar</li>
<li>✅ <code>waitFor</code> — element qidirishdan tashqari istalgan assertionni kutish uchun</li>
</ul>
"""

L11_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 11: User events, async testlash, API mocking
// ════════════════════════════════════════════════════════════════════

import { useState, useEffect } from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, test, expect, vi, beforeEach } from 'vitest';

// ─────────────────────────────────────────────────────────────────────
// 1) Test qilinadigan komponentlar
// ─────────────────────────────────────────────────────────────────────

function Counter() {
  const [son, setSon] = useState(0);
  return (
    <div>
      <p>Son: {son}</p>
      <button onClick={() => setSon(s => s + 1)}>+1</button>
    </div>
  );
}

function IsmForma() {
  const [ism, setIsm] = useState('');
  return (
    <div>
      <input aria-label="Ism" value={ism} onChange={(e) => setIsm(e.target.value)} />
      <p>Salom, {ism || 'mehmon'}!</p>
    </div>
  );
}

function FoydalanuvchilarRoyxati() {
  const [data, setData] = useState<string[] | null>(null);
  const [xato, setXato] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/users')
      .then(res => {
        if (!res.ok) throw new Error('Server xatosi');
        return res.json();
      })
      .then(setData)
      .catch(() => setXato('Xato yuz berdi'));
  }, []);

  if (xato) return <p>{xato}</p>;
  if (!data) return <p>Yuklanmoqda...</p>;
  return <ul>{data.map(u => <li key={u}>{u}</li>)}</ul>;
}

// ─────────────────────────────────────────────────────────────────────
// 2) userEvent — haqiqiy foydalanuvchi harakati
// ─────────────────────────────────────────────────────────────────────

describe('userEvent bilan testlash', () => {
  test('tugma bosilganda son oshadi', async () => {
    const user = userEvent.setup();
    render(<Counter />);

    await user.click(screen.getByRole('button', { name: '+1' }));

    expect(screen.getByText('Son: 1')).toBeInTheDocument();
  });

  test('inputga yozish ishlaydi', async () => {
    const user = userEvent.setup();
    render(<IsmForma />);

    await user.type(screen.getByRole('textbox'), 'Olim');

    expect(screen.getByText('Salom, Olim!')).toBeInTheDocument();
  });
});

// ─────────────────────────────────────────────────────────────────────
// 3) Async testlash + fetch mock
// ─────────────────────────────────────────────────────────────────────

describe('FoydalanuvchilarRoyxati (async)', () => {
  beforeEach(() => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ['Olim', 'Vali'],
    }) as any;
  });

  test('foydalanuvchilar yuklanadi', async () => {
    render(<FoydalanuvchilarRoyxati />);

    expect(screen.getByText('Yuklanmoqda...')).toBeInTheDocument();

    const olim = await screen.findByText('Olim'); // ✅ topilguncha kutadi
    expect(olim).toBeInTheDocument();
  });

  test('server xato qaytarsa, xato xabari ko\\'rinadi', async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false, status: 500 }) as any;
    render(<FoydalanuvchilarRoyxati />);

    const xato = await screen.findByText('Xato yuz berdi');
    expect(xato).toBeInTheDocument();
  });
});

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato — getByText'ni asinxron natija uchun ishlatish
// ─────────────────────────────────────────────────────────────────────

/*
test('foydalanuvchilar yuklanadi (XATO — getByText)', () => {
  render(<FoydalanuvchilarRoyxati />);
  // ❌ getByText SINXRON — fetch hali tugamagan, "Olim" hali DOM'da yo'q.
  // TestingLibraryElementError: Unable to find an element with the text: Olim.
  const olim = screen.getByText('Olim');
  expect(olim).toBeInTheDocument();
});
*/
"""

L11_EX = [
    {
        "title": "userEvent va fireEvent orasidagi farq",
        "description": "userEvent.click() fireEvent.click()'dan nima bilan farq qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Farq yo'q, ikkalasi bir xil",
            "userEvent haqiqiy foydalanuvchi harakatining butun zanjirini (pointerdown, focus, pointerup, click) simulyatsiya qiladi",
            "fireEvent tezroq, shuning uchun har doim afzal",
            "userEvent faqat tugmalar uchun, fireEvent faqat input uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "userEvent — real brauzerdagi kabi to'liq event ketma-ketligi.",
        "explanation": (
            "userEvent haqiqiy foydalanuvchi qiladigan barcha oraliq "
            "eventlarni (pointerdown, focus, pointerup, click) simulyatsiya "
            "qiladi, fireEvent esa faqat bitta xom DOM eventini yaratadi."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Asinxron paydo bo'ladigan element uchun qaysi query?",
        "description": "Fetch tugagandan keyin paydo bo'ladigan matnni topish uchun qaysi query ishlatilishi kerak?",
        "exercise_type": "multiple_choice",
        "options": ["getByText", "queryByText", "findByText", "getAllByText"],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Faqat findBy — async, element paydo bo'lguncha qayta-qayta tekshiradi.",
        "explanation": (
            "findByText — Promise qaytaradi va element paydo bo'lguncha "
            "(yoki timeout'gacha) qayta-qayta tekshiradi. getByText esa "
            "sinxron — darhol tekshiradi va hali paydo bo'lmagan elementni topolmaydi."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Fetch'ni test ichida mock qilishning sababi",
        "description": "Test ichida global.fetch'ni vi.fn() bilan almashtirishning asosiy sababi nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Kodni qisqartirish uchun",
            "Haqiqiy tarmoq so'rovisiz, tez va barqaror test yozish, xato holatlarini ham oson simulyatsiya qilish uchun",
            "TypeScript buni talab qiladi",
            "fetch testlarda ishlamaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Mock — real serverga bog'liqlikni yo'qotadi: tezroq, barqarorroq, xato holatlarini ham sinash mumkin.",
        "explanation": (
            "Fetch'ni mock qilish testni tezlashtiradi (tarmoq so'rovi yo'q), "
            "barqarorroq qiladi (internet/server holatiga bog'liq emas) va "
            "xato holatlarini (masalan, 500 status) osongina simulyatsiya "
            "qilish imkonini beradi."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega getByText asinxron natija uchun \"Unable to find element\" xatosini beradi?",
        "description": (
            "Fetch orqali kelayotgan ma'lumotni getByText bilan qidirsangiz, "
            "nega bu deyarli har doim xato beradi, hatto ma'lumot to'g'ri "
            "kelayotgan bo'lsa ham? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "getByText sinxron ishlaydi — u chaqirilgan zahoti DOM'ni bir "
            "marta tekshiradi va darhol natija qaytaradi yoki xato beradi. "
            "Fetch so'rovi esa asinxron — u tugashi uchun vaqt kerak (hech "
            "bo'lmaganda bitta microtask/event loop aylanishi). Test "
            "kodi getByText'ga yetganda, fetch promise'i hali resolve "
            "bo'lmagan bo'ladi, komponent hali \"Yuklanmoqda...\" holatida "
            "va kutilayotgan matn hali DOM'da yo'q. findByText esa Promise "
            "qaytaradi va element paydo bo'lguncha (yoki timeout'gacha) "
            "vaqt ichida qayta-qayta tekshiradi, shuning uchun asinxron "
            "natijalar uchun to'g'ri ishlaydi."
        ),
        "hint": "Fetch qachon tugaydi va getByText qachon tekshiradi — bu ikkisining vaqt tartibini solishtiring.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


CAPSTONE_TASK = {
    "task_title": "🚀 CAPSTONE: Tiplangan Xarid Savati (Redux Toolkit + TypeScript + Testlar)",
    "task_description": (
        "Kursning yakuniy loyihasi: to'liq tiplangan (.tsx) mahsulot va xarid "
        "savati ilovasi. RTK Query orqali mahsulotlarni yuklang, RTK slice "
        "bilan savatni boshqaring, hammasini TypeScript bilan tiplang va "
        "Vitest + React Testing Library bilan kamida 5 ta test yozing."
    ),
    "task_requirements": (
        "• React + TypeScript (.tsx) — barcha komponentlar tiplangan\n"
        "• RTK Query — mahsulotlar ro'yxatini yuklash (useGetProductsQuery)\n"
        "• Redux Toolkit slice — savat holati (qo'shish, o'chirish, miqdorni o'zgartirish)\n"
        "• RootState/AppDispatch + useAppSelector/useAppDispatch — hamma joyda\n"
        "• Kamida 1 ta generic yoki utility type (Partial/Pick/Omit) qo'llanilgan bo'lishi\n"
        "• Loading/error holatlari — RTK Query'ning isLoading/error orqali\n"
        "• Kamida 5 ta test (Vitest + React Testing Library):\n"
        "  - Komponent render bo'lishini tekshiruvchi test\n"
        "  - userEvent bilan \"savatga qo'shish\" tugmasini bosish testi\n"
        "  - Savat jami summasi to'g'ri hisoblanishini tekshiruvchi test\n"
        "  - Mock qilingan fetch bilan async yuklashni tekshiruvchi test (findBy)\n"
        "  - Xato holatini tekshiruvchi test (server 500 qaytarsa)\n"
        "• README — loyihani ishga tushirish va testlarni ishga tushirish yo'riqnomasi"
    ),
    "task_technologies": "React, TypeScript, Redux Toolkit, RTK Query, Vitest, React Testing Library",
    "task_deadline_days": 14,
}

CAPSTONE_TEXT = """\
<h2>🚀 CAPSTONE: Tiplangan Xarid Savati</h2>

<p>Bu — kursning yakuniy loyihasi. 1-11 darslarda o'rgangan hamma narsa — Redux Toolkit (slice, thunk, RTK Query, selectors), TypeScript (props, generics, typed Redux), va testlash (RTL, userEvent, mocking) — bitta real loyihada birlashadi.</p>

<h3>Loyihaning tuzilishi</h3>
<pre class="mermaid">
flowchart LR
    RTKQ["RTK Query — mahsulotlar"] --> UI["Mahsulotlar ro'yxati"]
    UI -->|savatga qo'shish| CS["cartSlice"]
    CS --> SUM["Savat sahifasi — jami summa"]
    TESTS["Vitest + RTL"] -.tekshiradi.-> UI
    TESTS -.tekshiradi.-> CS
</pre>

<h3>Nima qilishingiz kerak</h3>
<ol>
<li><strong>Mahsulotlar</strong> — <code>createApi</code> bilan <code>useGetProductsQuery()</code>, loading/error holatlari (5-dars)</li>
<li><strong>Savat</strong> — alohida <code>cartSlice</code>: <code>addToCart</code>, <code>removeFromCart</code>, <code>updateQuantity</code> (2-3 darslar)</li>
<li><strong>Tiplash</strong> — barcha komponentlar, state, thunk'lar to'liq tiplangan (7-9 darslar)</li>
<li><strong>Testlar</strong> — kamida 5 ta, render/userEvent/async/mocking (10-11 darslar)</li>
</ol>

<h3>Boshlash uchun skelet</h3>
<pre><code>interface Product {
  id: number;
  name: string;
  price: number;
}

interface CartItem {
  productId: number;
  quantity: number;
}

interface CartState {
  items: CartItem[];
}

// Vazifa: apiSlice (RTK Query) — getProducts endpoint
// Vazifa: cartSlice — addToCart, removeFromCart, updateQuantity
// Vazifa: RootState/AppDispatch + useAppSelector/useAppDispatch
// Vazifa: SavatSahifasi komponenti — jami summani hisoblab ko'rsatish
// Vazifa: kamida 5 ta test (Product.test.tsx, Cart.test.tsx)
</code></pre>

<h3>💡 Eslatma</h3>
<p>Bu loyiha — mustaqil ishlash uchun. 1-11 darslardagi kodlarni qayta ko'rib chiqing, ayniqsa R1/R2 revizion darslarini — ular xuddi shu naqshlarni kichikroq masshtabda ko'rsatgan edi.</p>

<h3>📌 Topshirilgandan keyin siz quyidagilarni bilib olasiz</h3>
<ul>
<li>✅ RTK Query + Redux Toolkit slice'ni bitta real loyihada birlashtirish</li>
<li>✅ To'liq tiplangan React + Redux ilovasini boshidan oxirigacha qurish</li>
<li>✅ Component va state logikasini avtomatlashtirilgan testlar bilan himoyalash</li>
<li>✅ Portfolio uchun tayyor, ishlab chiqarish sifatidagi kichik loyiha</li>
</ul>
"""

CAPSTONE_CODE = """\
// ════════════════════════════════════════════════════════════════════
// CAPSTONE: Tiplangan Xarid Savati — boshlang'ich skelet
// ════════════════════════════════════════════════════════════════════

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { createSlice, configureStore, PayloadAction } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook, Provider } from 'react-redux';

// ─────────────────────────────────────────────────────────────────────
// Turlar
// ─────────────────────────────────────────────────────────────────────

interface Product {
  id: number;
  name: string;
  price: number;
}

interface CartItem {
  productId: number;
  quantity: number;
}

interface CartState {
  items: CartItem[];
}

// ─────────────────────────────────────────────────────────────────────
// RTK Query — mahsulotlar (5-darsdagi naqsh)
// ─────────────────────────────────────────────────────────────────────

export const productsApi = createApi({
  reducerPath: 'productsApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  endpoints: (builder) => ({
    getProducts: builder.query<Product[], void>({
      query: () => '/products',
    }),
  }),
});

export const { useGetProductsQuery } = productsApi;

// ─────────────────────────────────────────────────────────────────────
// cartSlice — Vazifa: to'ldiring
// ─────────────────────────────────────────────────────────────────────

const initialCartState: CartState = { items: [] };

const cartSlice = createSlice({
  name: 'cart',
  initialState: initialCartState,
  reducers: {
    addToCart: (state, action: PayloadAction<number>) => {
      // Vazifa: agar productId allaqachon savatda bo'lsa — quantity += 1,
      // aks holda yangi CartItem qo'shing.
    },
    removeFromCart: (state, action: PayloadAction<number>) => {
      // Vazifa: state.items'dan productId bo'yicha o'chiring.
    },
    updateQuantity: (state, action: PayloadAction<{ productId: number; quantity: number }>) => {
      // Vazifa: mos CartItem'ning quantity'sini yangilang.
    },
  },
});

export const { addToCart, removeFromCart, updateQuantity } = cartSlice.actions;

// ─────────────────────────────────────────────────────────────────────
// Store + typed hooks (9-darsdagi naqsh)
// ─────────────────────────────────────────────────────────────────────

const store = configureStore({
  reducer: {
    [productsApi.reducerPath]: productsApi.reducer,
    cart: cartSlice.reducer,
  },
  middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(productsApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ─────────────────────────────────────────────────────────────────────
// Vazifa: MahsulotlarRoyxati, SavatSahifasi komponentlari
// Vazifa: kamida 5 ta test — Product.test.tsx, Cart.test.tsx fayllarida
// ─────────────────────────────────────────────────────────────────────

function App() {
  return (
    <Provider store={store}>
      {/* Vazifa: MahsulotlarRoyxati va SavatSahifasi komponentlarini qo'shing */}
    </Provider>
  );
}
"""


def _jdump(value):
    if value is None or value == "":
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_sections_json(order: int, text: str, code: str, video: str | None,
                         exercise_rows: list[Exercise], lang: str = "jsx",
                         project_task: dict | None = None) -> str:
    sections = [
        {"id": f"t{order}", "type": "text", "label": "Текст",
         "html": text, "order": 0},
        {"id": f"c{order}", "type": "code", "label": "Код",
         "code": code, "lang": lang, "order": 1},
    ]
    if video:
        sections.append({"id": f"v{order}", "type": "video", "label": "Видео",
                          "videoUrl": video, "order": 2})
    if exercise_rows:
        sections.append({
            "id": f"e{order}", "type": "exercise", "label": "Упражнения",
            "exercises": [
                {
                    "_localId": e.id, "id": e.id,
                    "title": e.title, "description": e.description,
                    "exercise_type": e.exercise_type,
                    "options": e.options or "",
                    "correct_answers": e.correct_answers or "",
                    "drag_items": e.drag_items or "",
                    "correct_order": e.correct_order or "",
                    "is_multiple_select": bool(e.is_multiple_select),
                    "expected_answer": e.expected_answer or "",
                    "hint": e.hint or "",
                    "explanation": e.explanation or "",
                    "difficulty_level": e.difficulty_level,
                    "points": e.points, "order": e.order,
                }
                for e in exercise_rows
            ],
            "order": 3,
        })
    if project_task:
        # NOTE: no lesson anywhere on the platform actually had this section
        # populated before — LessonContentBlocks.js/StudentLessonPage.js
        # gate the entire submit-project UI on finding a "project"-type
        # entry here (see feedback/project memory: platform-wide dead
        # feature). Populating it for real is what makes submission work.
        sections.append({
            "id": f"p{order}", "type": "project", "label": project_task["task_title"],
            "description": project_task["task_description"],
            "requirements": project_task["task_requirements"],
            "techStack": project_task["task_technologies"],
            "deadline": project_task["task_deadline_days"],
            "order": 4,
        })
    return json.dumps(sections, ensure_ascii=False)


async def seed(dry_run: bool = False) -> None:
    async with AsyncSessionLocal() as db:
        existing = (
            await db.execute(select(Course).where(Course.title == COURSE["title"]))
        ).scalar_one_or_none()

        if existing:
            course = existing
            print(f"Course '{COURSE['title']}' already exists (id={course.id}). "
                  f"Adding/updating lessons only.")
        else:
            course = Course(**COURSE)
            db.add(course)
            await db.flush()
            print(f"Created course: id={course.id}  title='{course.title}'")

        existing_orders = {
            row[0] for row in (
                await db.execute(select(Lesson.order).where(Lesson.course_id == course.id))
            ).all()
        }

        done_lessons = [l for l in LESSON_PLAN if l["status"] == "done"]
        print(f"\nSeeding {len(done_lessons)}/{len(LESSON_PLAN)} lessons "
              f"(rest are still 'todo' in LESSON_PLAN):\n")

        for ldata in done_lessons:
            if ldata["order"] in existing_orders:
                print(f"  ⏭️  order={ldata['order']:>2}  {ldata['title']:<55}  "
                      f"already seeded, skipped")
                continue

            text = globals()[f"{ldata['ref']}_TEXT"]
            code = globals()[f"{ldata['ref']}_CODE"]
            ex_list = globals().get(f"{ldata['ref']}_EX", [])
            task = globals().get(f"{ldata['ref']}_TASK")
            lang = ldata.get("lang", "jsx")

            lesson = Lesson(
                course_id=course.id,
                title=ldata["title"],
                order=ldata["order"],
                points_reward=10,
                text_content=text,
                code_content=code,
                code_language=lang,
                video_url=None,  # TODO: add a real video link before publishing
                sections_json=None,
                task_title=task.get("task_title") if task else None,
                task_description=task.get("task_description") if task else None,
                task_requirements=task.get("task_requirements") if task else None,
                task_technologies=task.get("task_technologies") if task else None,
                task_deadline_days=task.get("task_deadline_days") if task else None,
                is_active=True,
                is_published=True,
            )
            db.add(lesson)
            await db.flush()

            ex_rows: list[Exercise] = []
            for ex_order, ex in enumerate(ex_list):
                row = Exercise(
                    lesson_id=lesson.id,
                    title=ex["title"],
                    description=ex.get("description", ex["title"]),
                    exercise_type=ex["exercise_type"],
                    options=_jdump(ex.get("options")),
                    correct_answers=_jdump(ex.get("correct_answers")),
                    drag_items=_jdump(ex.get("drag_items")),
                    correct_order=_jdump(ex.get("correct_order")),
                    is_multiple_select=bool(ex.get("is_multiple_select", False)),
                    expected_answer=ex.get("expected_answer", ""),
                    hint=ex.get("hint", ""),
                    explanation=ex.get("explanation", ""),
                    difficulty_level=ex["difficulty_level"],
                    points=ex["points"],
                    order=ex_order,
                    is_active=True,
                )
                db.add(row)
                ex_rows.append(row)
            await db.flush()

            lesson.sections_json = build_sections_json(
                ldata["order"], text, code, None, ex_rows, lang=lang,
                project_task=task,
            )

            # Namuna — same real code as the lesson teaches, code-only viewer
            # (so students see the actual taught API, not a lookalike
            # substitute — see feedback_namuna_must_teach_lesson memory).
            sample = LessonSample(
                lesson_id=lesson.id,
                title=f"Namuna: {ldata['title']}",
                description=ldata["scope"],
                sample_type="code",
                code_files_json=json.dumps(
                    [{"filename": f"App.{lang}", "language": lang, "code": code}],
                    ensure_ascii=False,
                ),
            )
            db.add(sample)

            print(f"  lesson order={lesson.order:>2} id={lesson.id:>3}  "
                  f"{lesson.title:<55}  exercises={len(ex_rows)}")

        if dry_run:
            await db.rollback()
            print("\nDRY RUN — rolled back, nothing written.")
        else:
            await db.commit()
            print(f"\nSeeded {len(done_lessons)} lesson(s).")

    await engine.dispose()


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    asyncio.run(seed(dry_run=dry))
