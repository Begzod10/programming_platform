"""Seed the "React Asoslari" course (14 lessons: 11 main + 3 revisions).

Usage:
    cd backend
    python scripts/seed_react_basics.py
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists.

Target audience: "JavaScript: Keyingi Bosqich" graduates. Skips JS basics
and jumps straight into React: JSX, components, props, hooks (useState,
useEffect, custom), Router, Context, performance, fullstack capstone.
Language: Uzbek content with Russian section labels. Each lesson uses the
WIN-FIRST shape: BLOKA 1/2/3 hands-on hook -> deliberate-error -> theory ->
"Bu darsdan keyin siz bilasizki" wrap.
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


# ─────────────────────────────────────────────────────────────────────────────
# Course-level metadata
# ─────────────────────────────────────────────────────────────────────────────
COURSE = {
    "title": "React Asoslari",
    "description": (
        "JavaScript bilan tanish dasturchilar uchun React kutubxonasi: JSX, "
        "komponentlar, props, hooks (useState, useEffect, custom hooks), "
        "React Router, Context API, performance va to'liq fullstack capstone. "
        "Har bir modul oxirida amaliy loyiha."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 6,
    "max_points": 280,
    "is_active": True,
    "is_published": True,
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson content placeholders — filled in by subsequent edits.
# ═════════════════════════════════════════════════════════════════════════════
L1_TEXT = """\
<h2>React + Vite: birinchi komponent va JSX</h2>

<pre class="mermaid">
flowchart LR
    JSX["JSX kod"] -->|Vite + Babel| JS["sof JavaScript"]
    JS -->|virtual DOM| DOM["browser DOM"]
    STATE["state o'zgardi"] -->|render| JSX
</pre>

<p>React — bu UI yasash uchun Facebook tomonidan ochilgan kutubxona. Boshqa kutubxonalardan farqi: <strong>komponentlar</strong> — kichik, qayta ishlatish mumkin bo'lgan qismlar. Sayt = komponentlar daraxti.</p>

<p>Avval ham JS bilan DOM'ga yozgan bo'lsangiz, eslab ko'ring: <code>document.createElement</code>, <code>innerHTML</code>, <code>addEventListener</code>... React bularning hammasini sizdan yashiradi va shunchaki "men shu UI'ni xohlayman" deyish imkonini beradi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Vite bilan loyiha ochish</h4>
<pre><code># Terminal
npm create vite@latest mening-app -- --template react
cd mening-app
npm install
npm run dev</code></pre>

<p>2 daqiqa ichida sizda ishlovchi React loyiha bor. Brauzerda <code>http://localhost:5173</code>.</p>

<h4>BLOKA 2 — birinchi komponent</h4>
<pre><code>// src/App.jsx
function App() {
  const ism = "Olim";
  return (
    &lt;div&gt;
      &lt;h1&gt;Salom, {ism}!&lt;/h1&gt;
      &lt;p&gt;Bu mening birinchi React komponentim&lt;/p&gt;
    &lt;/div&gt;
  );
}

export default App;</code></pre>

<p>Diqqat:</p>
<ul>
<li>Komponent — bu <em>JSX qaytaruvchi funksiya</em></li>
<li>Nomi <strong>katta harf</strong> bilan boshlanadi (App, Button, Card)</li>
<li><code>{ifoda}</code> — JS ifodani JSX ichiga qo'yish</li>
<li>HTML kabi ko'rinadi, lekin <code>className</code> (class emas), <code>htmlFor</code> (for emas)</li>
</ul>

<h4>BLOKA 3 — ko'p komponent</h4>
<pre><code>function Salomlashish({ ism }) {
  return &lt;h2&gt;Salom, {ism}!&lt;/h2&gt;;
}

function App() {
  return (
    &lt;div&gt;
      &lt;Salomlashish ism="Olim" /&gt;
      &lt;Salomlashish ism="Vali" /&gt;
      &lt;Salomlashish ism="Karim" /&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p>Bitta <code>Salomlashish</code> komponentini 3 marta ishlatdik. Bu — React'ning butun falsafasi: <em>bir marta yoz, ko'p joyda ishlat</em>.</p>

<h3>🐛 Ataylab xato</h3>
<pre><code>function App() {
  return (
    &lt;h1&gt;Sarlavha&lt;/h1&gt;
    &lt;p&gt;Matn&lt;/p&gt;
  );
}</code></pre>

<p><strong>Natija:</strong> <code>Adjacent JSX elements must be wrapped in an enclosing tag</code>. Komponent <strong>bitta ildiz element</strong> qaytarishi shart. Yechim — wrapping div yoki Fragment (<code>&lt;&gt;...&lt;/&gt;</code>):</p>

<pre><code>// Fragment — ortiqcha div bo'lmaydi
function App() {
  return (
    &lt;&gt;
      &lt;h1&gt;Sarlavha&lt;/h1&gt;
      &lt;p&gt;Matn&lt;/p&gt;
    &lt;/&gt;
  );
}</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. JSX nima?</h4>
<p>JSX — JavaScript ichida HTML yozish uchun maxsus sintaksis. Brauzer JSX'ni tushunmaydi — Vite (Babel) uni oddiy <code>React.createElement</code> chaqiriqlariga aylantiradi:</p>

<pre><code>// Siz yozasiz:
&lt;h1 className="title"&gt;Salom&lt;/h1&gt;

// Vite buni JS ga aylantiradi:
React.createElement('h1', { className: 'title' }, 'Salom');</code></pre>

<h4>2. JSX qoidalari</h4>
<table>
<tr><th>HTML</th><th>JSX</th></tr>
<tr><td><code>class</code></td><td><code>className</code></td></tr>
<tr><td><code>for</code></td><td><code>htmlFor</code></td></tr>
<tr><td><code>onclick</code></td><td><code>onClick</code> (camelCase)</td></tr>
<tr><td><code>&lt;br&gt;</code></td><td><code>&lt;br /&gt;</code> (yopilgan)</td></tr>
<tr><td><code>style="color:red"</code></td><td><code>style={{color:'red'}}</code></td></tr>
<tr><td>komment</td><td><code>{/* komment */}</code></td></tr>
</table>

<h4>3. JS ifodalar JSX ichida</h4>
<pre><code>function App() {
  const ism = "Olim";
  const yosh = 18;
  const sevgan = ["pizza", "burger", "pasta"];

  return (
    &lt;div&gt;
      &lt;p&gt;Ism: {ism}&lt;/p&gt;
      &lt;p&gt;Yosh: {yosh}, balog'at: {yosh &gt;= 18 ? "ha" : "yo'q"}&lt;/p&gt;
      &lt;p&gt;Birinchi sevgani: {sevgan[0]}&lt;/p&gt;
      &lt;p&gt;Hisoblash: {2 + 2}&lt;/p&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><code>{...}</code> ichida har qanday <em>ifoda</em> bo'lishi mumkin. Lekin <strong>statement</strong> (if, for, va h.k.) — yo'q. Ular uchun ternary <code>? :</code> yoki <code>&&</code> ishlatamiz (4-darsda).</p>

<h4>4. Loyiha tuzilmasi</h4>
<pre><code>mening-app/
├── public/           # statik fayllar
├── src/
│   ├── App.jsx       # asosiy komponent
│   ├── main.jsx      # ildiz (DOM ga ulanish)
│   ├── index.css     # global stil
│   └── assets/       # rasm/font
├── index.html        # tek HTML fayl
├── package.json
└── vite.config.js</code></pre>

<p>main.jsx — bu yerda React ildizga ulanadi:</p>

<pre><code>// src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  &lt;React.StrictMode&gt;
    &lt;App /&gt;
  &lt;/React.StrictMode&gt;
);</code></pre>

<h4>5. Strict Mode — bu nima?</h4>
<p><code>React.StrictMode</code> — development'da ish vaqtidagi xato va eskirgan API'larni topishga yordam beradi. Production'da hech narsa qilmaydi. Doim qoldiring.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Vite bilan React loyiha ochish (<code>npm create vite@latest</code>)</li>
<li>✅ Komponent — JSX qaytaruvchi funksiya, nom katta harf bilan</li>
<li>✅ JSX qoidalari: <code>className</code>, <code>htmlFor</code>, <code>onClick</code>, yopilgan teglar</li>
<li>✅ <code>{ifoda}</code> — JS ifodani JSX ichiga qo'yish</li>
<li>✅ Bitta ildiz element majburiy (Fragment <code>&lt;&gt;&lt;/&gt;</code> bilan yechim)</li>
<li>✅ <code>main.jsx</code> — React ildizga ulanadi</li>
</ul>
"""

L1_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 1: Vite + birinchi komponent (JSX)
// ════════════════════════════════════════════════════════════════════
//
// Terminal:
//   npm create vite@latest mening-app -- --template react
//   cd mening-app
//   npm install
//   npm run dev
//
// ─────────────────────────────────────────────────────────────────────

// src/App.jsx
function App() {
  const ism = "Olim";
  const yosh = 18;
  const sevgan = ["pizza", "burger", "pasta"];

  return (
    <div className="app">
      <h1>Salom, {ism}!</h1>
      <p>Yosh: {yosh}, balog'at: {yosh >= 18 ? "ha" : "yo'q"}</p>
      <p>Sevimli taom: {sevgan[0]}</p>
      <p>2 + 2 = {2 + 2}</p>
    </div>
  );
}

export default App;


// ─────────────────────────────────────────────────────────────────────
// Ko'p komponent — bitta App ichida
// ─────────────────────────────────────────────────────────────────────

function Salomlashish({ ism }) {
  return <h2>Salom, {ism}!</h2>;
}

function Footer() {
  return (
    <footer style={{ marginTop: 40, color: "gray" }}>
      © 2026 Mening saytim
    </footer>
  );
}

function AppKopKomponent() {
  return (
    <>
      <Salomlashish ism="Olim" />
      <Salomlashish ism="Vali" />
      <Salomlashish ism="Karim" />
      <Footer />
    </>
  );
}


// ─────────────────────────────────────────────────────────────────────
// JSX ichida JS — barcha imkoniyatlar
// ─────────────────────────────────────────────────────────────────────

function MaqolaKarti() {
  const sarlavha = "React boshlash";
  const tags = ["react", "jsx", "frontend"];
  const oqilgan = true;

  return (
    <article className={oqilgan ? "card read" : "card"}>
      <h3>{sarlavha.toUpperCase()}</h3>

      {/* Bu JSX komment */}

      <div>
        Teglar:
        {tags.map((t) => (
          <span key={t} style={{ marginLeft: 8 }}>#{t}</span>
        ))}
      </div>

      <p>Holat: {oqilgan && "✓ o'qilgan"}</p>
    </article>
  );
}


// ─────────────────────────────────────────────────────────────────────
// src/main.jsx — ildiz ulanish
// ─────────────────────────────────────────────────────────────────────

/*
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
*/


// ─────────────────────────────────────────────────────────────────────
// Ataylab xato — wrapping element yo'q
// ─────────────────────────────────────────────────────────────────────

/*
function Xato() {
  return (
    <h1>Sarlavha</h1>     // ❌ XATO
    <p>Matn</p>
  );
}
// Adjacent JSX elements must be wrapped in an enclosing tag
*/

// To'g'risi:
function Togri1() {
  return (
    <div>
      <h1>Sarlavha</h1>
      <p>Matn</p>
    </div>
  );
}

function Togri2() {
  return (
    <>  {/* Fragment — ortiqcha div yo'q */}
      <h1>Sarlavha</h1>
      <p>Matn</p>
    </>
  );
}
"""
L2_TEXT = """\
<h2>Props — komponentlarga ma'lumot uzatish</h2>

<pre class="mermaid">
flowchart TB
    P["Parent App"] -->|ism, yosh, onClick| C1["Card"]
    P -->|ism, yosh, onClick| C2["Card"]
    P -->|ism, yosh, onClick| C3["Card"]
</pre>

<p>1-darsda biz statik <code>&lt;Salomlashish ism="Olim" /&gt;</code> yozdik. Endi <strong>nima uchun shunday ishladi</strong> va undan to'liq foydalanish vaqti. <code>ism="Olim"</code> — bu <strong>prop</strong>. Komponentlar bir-biriga shunday gaplashadi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — props qabul qilish</h4>
<pre><code>function Card({ sarlavha, matn }) {
  return (
    &lt;div className="card"&gt;
      &lt;h3&gt;{sarlavha}&lt;/h3&gt;
      &lt;p&gt;{matn}&lt;/p&gt;
    &lt;/div&gt;
  );
}

function App() {
  return (
    &lt;div&gt;
      &lt;Card sarlavha="React" matn="UI kutubxonasi" /&gt;
      &lt;Card sarlavha="Vite" matn="Tez build tool" /&gt;
      &lt;Card sarlavha="JSX" matn="JS ichida HTML" /&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><code>{ sarlavha, matn }</code> — bu destructuring. <code>props</code> obyekti keladi va undan kerakli xususiyatlarni ajratib olamiz.</p>

<h4>BLOKA 2 — turli ma'lumot turlari</h4>
<pre><code>function Profil({ ism, yosh, faol, sevganRanglar, profilRasm }) {
  return (
    &lt;div&gt;
      &lt;img src={profilRasm} alt={ism} /&gt;
      &lt;h2&gt;{ism}&lt;/h2&gt;
      &lt;p&gt;Yosh: {yosh}&lt;/p&gt;
      &lt;p&gt;Holat: {faol ? "🟢 faol" : "⚫ noaktiv"}&lt;/p&gt;
      &lt;p&gt;Ranglar: {sevganRanglar.join(", ")}&lt;/p&gt;
    &lt;/div&gt;
  );
}

&lt;Profil
  ism="Nigora"
  yosh={22}
  faol={true}
  sevganRanglar={["ko'k", "yashil"]}
  profilRasm="/avatar.png"
/&gt;</code></pre>

<p>Diqqat: <strong>string'lardan tashqari hamma narsa <code>{...}</code> ichida</strong>. <code>yosh={22}</code> — son, <code>faol={true}</code> — boolean. <code>yosh="22"</code> deb yozsangiz — string keladi, son emas.</p>

<h4>BLOKA 3 — children prop</h4>
<pre><code>function Layout({ children }) {
  return (
    &lt;div className="container"&gt;
      &lt;header&gt;Header&lt;/header&gt;
      &lt;main&gt;{children}&lt;/main&gt;
      &lt;footer&gt;Footer&lt;/footer&gt;
    &lt;/div&gt;
  );
}

function App() {
  return (
    &lt;Layout&gt;
      &lt;h1&gt;Asosiy sahifa&lt;/h1&gt;
      &lt;p&gt;Mazmun bu yerda&lt;/p&gt;
    &lt;/Layout&gt;
  );
}</code></pre>

<p><code>children</code> — bu komponent teglari orasidagi hammasi. <strong>Wrapper</strong> komponentlar (Modal, Card, Layout) shu bilan ishlaydi.</p>

<h3>🐛 Ataylab xato</h3>
<pre><code>function Card({ sarlavha }) {
  sarlavha = "yangi sarlavha"; // ❌
  return &lt;h3&gt;{sarlavha}&lt;/h3&gt;;
}</code></pre>

<p><strong>Sabab:</strong> Bu kod xato chiqarmaydi <em>hozirgina</em>, lekin bu — React qoidasiga zid: <strong>props read-only</strong>. Komponent o'z propsini o'zgartirmasin. Sabab: parent berdi, child o'zgartirsa, parent buni bilmaydi va sayt nomutanosib bo'ladi.</p>

<p>Agar value o'zgartirilishi kerak bo'lsa — <code>useState</code> ishlatish (3-darsda) yoki parent'ga callback yuborish.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Props bir tomonlama (one-way data flow)</h4>
<p>Ma'lumot doim <strong>yuqoridan pastga</strong> oqadi: parent → child. Bu — React'ning eng muhim qoidalaridan biri.</p>
<pre><code>App
 ├── Header
 │    └── Logo
 ├── Main
 │    ├── Card    ← App ma'lumotni shu yerga uzatadi
 │    └── List
 └── Footer</code></pre>

<h4>2. Destructuring vs to'liq props</h4>
<pre><code>// Destructuring (zamonaviy)
function Card({ sarlavha, matn }) {
  return &lt;h3&gt;{sarlavha} — {matn}&lt;/h3&gt;;
}

// Eskirgan — to'liq props obyekti
function Card(props) {
  return &lt;h3&gt;{props.sarlavha} — {props.matn}&lt;/h3&gt;;
}</code></pre>

<p>Destructuring tavsiya — kodingiz oz va aniq.</p>

<h4>3. Default qiymatlar</h4>
<pre><code>function Tugma({ label = "Tasdiqlash", turi = "primary", disabled = false }) {
  return (
    &lt;button className={`btn btn-${turi}`} disabled={disabled}&gt;
      {label}
    &lt;/button&gt;
  );
}

&lt;Tugma /&gt;                            // "Tasdiqlash"
&lt;Tugma label="Bekor qilish" /&gt;       // "Bekor qilish"
&lt;Tugma label="O'chirish" turi="danger" /&gt;</code></pre>

<h4>4. Rest props va spread</h4>
<pre><code>function Input({ label, ...boshqalari }) {
  return (
    &lt;label&gt;
      {label}
      &lt;input {...boshqalari} /&gt;
    &lt;/label&gt;
  );
}

&lt;Input label="Ism" type="text" placeholder="Olim" required /&gt;
// label maxsus, qolgani input'ga uzatildi</code></pre>

<h4>5. Funksiya prop (event handler)</h4>
<p>Prop sifatida <em>funksiya</em> ham yuborilishi mumkin. Bu — child'dan parent'ga "xabar yuborish" usuli:</p>

<pre><code>function Tugma({ label, onClick }) {
  return &lt;button onClick={onClick}&gt;{label}&lt;/button&gt;;
}

function App() {
  const salom = () =&gt; alert("Salom!");
  return &lt;Tugma label="Salom" onClick={salom} /&gt;;
}</code></pre>

<p>Soat: ma'lumot pastga, hodisa yuqoriga.</p>

<h4>6. Kompozitsiya — slot pattern</h4>
<pre><code>function Card({ sarlavha, ozClick, children }) {
  return (
    &lt;div className="card"&gt;
      &lt;header&gt;{sarlavha}&lt;/header&gt;
      &lt;div className="body"&gt;{children}&lt;/div&gt;
    &lt;/div&gt;
  );
}

// Children — har xil bo'lishi mumkin
&lt;Card sarlavha="Profil"&gt;
  &lt;img src="/avatar.png" /&gt;
  &lt;p&gt;Ism: Olim&lt;/p&gt;
  &lt;Tugma label="Tahrirlash" /&gt;
&lt;/Card&gt;</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Props — parent'dan child'ga ma'lumot. <strong>Read-only.</strong></li>
<li>✅ Destructuring: <code>function X({ a, b })</code></li>
<li>✅ String emas, hammasi <code>{...}</code> ichida</li>
<li>✅ Default qiymat: <code>{ ism = "Mehmon" }</code></li>
<li>✅ <code>...rest</code> bilan qolgani uzatish</li>
<li>✅ <code>children</code> — wrapping komponentlar uchun</li>
<li>✅ Funksiya prop — child'dan parent'ga hodisa</li>
</ul>
"""

L2_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 2: Props va kompozitsiya
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Oddiy props — destructuring
// ─────────────────────────────────────────────────────────────────────

function Card({ sarlavha, matn }) {
  return (
    <div className="card">
      <h3>{sarlavha}</h3>
      <p>{matn}</p>
    </div>
  );
}

function App() {
  return (
    <div>
      <Card sarlavha="React" matn="UI kutubxonasi" />
      <Card sarlavha="Vite" matn="Tez build tool" />
      <Card sarlavha="JSX" matn="JS ichida HTML" />
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 2) Turli ma'lumot turlari
// ─────────────────────────────────────────────────────────────────────

function Profil({ ism, yosh, faol, sevganRanglar, profilRasm }) {
  return (
    <div className="profil">
      <img src={profilRasm} alt={ism} width={64} height={64} />
      <h2>{ism}</h2>
      <p>Yosh: {yosh}</p>
      <p>Holat: {faol ? "🟢 faol" : "⚫ noaktiv"}</p>
      <p>Ranglar: {sevganRanglar.join(", ")}</p>
    </div>
  );
}

function ProfilApp() {
  return (
    <Profil
      ism="Nigora"
      yosh={22}
      faol={true}
      sevganRanglar={["ko'k", "yashil"]}
      profilRasm="/avatar.png"
    />
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) Default props
// ─────────────────────────────────────────────────────────────────────

function Tugma({ label = "Tasdiqlash", turi = "primary", disabled = false, onClick }) {
  return (
    <button
      className={`btn btn-${turi}`}
      disabled={disabled}
      onClick={onClick}
    >
      {label}
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 4) Children + kompozitsiya
// ─────────────────────────────────────────────────────────────────────

function Layout({ children }) {
  return (
    <div className="container">
      <header className="header">Header</header>
      <main className="main">{children}</main>
      <footer className="footer">© 2026</footer>
    </div>
  );
}

function AppKompozitsiya() {
  return (
    <Layout>
      <h1>Asosiy sahifa</h1>
      <p>Mazmun bu yerda</p>
      <Tugma label="Boshlash" />
    </Layout>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 5) Rest props va spread (input wrapper)
// ─────────────────────────────────────────────────────────────────────

function FormaInput({ label, ...inputProps }) {
  return (
    <label className="forma-input">
      <span>{label}</span>
      <input {...inputProps} />
    </label>
  );
}

function FormaApp() {
  return (
    <form>
      <FormaInput label="Ism"     type="text"  placeholder="Olim" required />
      <FormaInput label="Email"   type="email" placeholder="x@y.uz" />
      <FormaInput label="Parol"   type="password" minLength={8} />
    </form>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 6) Funksiya prop — child → parent xabar
// ─────────────────────────────────────────────────────────────────────

function HavolaTugmasi({ label, onClick }) {
  return (
    <button onClick={onClick} className="havola">
      {label}
    </button>
  );
}

function MenyuApp() {
  const tanlash = (nom) => alert(`Tanlandi: ${nom}`);

  return (
    <nav>
      <HavolaTugmasi label="Bosh"    onClick={() => tanlash("Bosh")} />
      <HavolaTugmasi label="Kurslar" onClick={() => tanlash("Kurslar")} />
      <HavolaTugmasi label="Profil"  onClick={() => tanlash("Profil")} />
    </nav>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Ataylab xato — props'ni o'zgartirish
// ─────────────────────────────────────────────────────────────────────

/*
function CardXato({ sarlavha }) {
  sarlavha = "yangi";   // ❌ react qoidasiga zid
  return <h3>{sarlavha}</h3>;
}
// Sabab: props read-only. Agar o'zgartirish kerak bo'lsa — useState.
*/
"""
L3_TEXT = """\
<h2>useState — komponent xotirasi va event handler'lar</h2>

<pre class="mermaid">
flowchart LR
    EV["onClick / onChange"] -->|setState| ST["state yangilanadi"]
    ST -->|React qayta render qiladi| UI["UI yangi qiymat ko'rsatadi"]
</pre>

<p>Hozirgacha komponentlar statik edi: bir marta render bo'lib, o'zgarmas. Endi siz hayotni boshlaysiz — <strong>state</strong>. Foydalanuvchi tugma bosadi, son o'sadi. Inputga yozadi, ekran yangilanadi. Bu — React'ning butun jonliligi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi counter</h4>
<pre><code>import { useState } from 'react';

function Counter() {
  const [son, setSon] = useState(0);

  return (
    &lt;div&gt;
      &lt;p&gt;Son: {son}&lt;/p&gt;
      &lt;button onClick={() =&gt; setSon(son + 1)}&gt;+1&lt;/button&gt;
      &lt;button onClick={() =&gt; setSon(son - 1)}&gt;-1&lt;/button&gt;
      &lt;button onClick={() =&gt; setSon(0)}&gt;Reset&lt;/button&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p>3 ta yangi narsa:</p>
<ol>
<li><code>import { useState } from 'react'</code> — hook'ni import</li>
<li><code>const [son, setSon] = useState(0)</code> — state e'lon (boshlang'ich qiymati 0)</li>
<li><code>setSon(...)</code> — yangi qiymat berish (React render qiladi)</li>
</ol>

<h4>BLOKA 2 — turli state turlari</h4>
<pre><code>function Forma() {
  const [ism, setIsm] = useState("");          // string
  const [yosh, setYosh] = useState(18);        // number
  const [faol, setFaol] = useState(false);     // boolean
  const [hobby, setHobby] = useState([]);      // array
  const [profil, setProfil] = useState({       // object
    shahar: "Toshkent",
    yosh: 25
  });

  return (
    &lt;div&gt;
      &lt;input value={ism} onChange={e =&gt; setIsm(e.target.value)} /&gt;
      &lt;p&gt;Salom, {ism || "mehmon"}!&lt;/p&gt;
    &lt;/div&gt;
  );
}</code></pre>

<h4>BLOKA 3 — event handler'lar</h4>
<pre><code>function Tutorial() {
  const [xabar, setXabar] = useState("");

  const onClick = () =&gt; setXabar("Bosildi");
  const onMouseEnter = () =&gt; setXabar("Sichqoncha ustida");
  const onMouseLeave = () =&gt; setXabar("Ketdi");
  const onKeyDown = (e) =&gt; {
    if (e.key === "Enter") setXabar("Enter bosildi");
  };

  return (
    &lt;div&gt;
      &lt;button onClick={onClick}&gt;Bos&lt;/button&gt;
      &lt;div
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
        style={{ border: "1px solid", padding: 20 }}
      &gt;
        Sichqonchani bu yerga&lt;/div&gt;
      &lt;input onKeyDown={onKeyDown} /&gt;
      &lt;p&gt;{xabar}&lt;/p&gt;
    &lt;/div&gt;
  );
}</code></pre>

<h3>🐛 Ataylab xato (juda ko'p uchraydi)</h3>
<pre><code>function CounterXato() {
  const [son, setSon] = useState(0);
  return &lt;button onClick={setSon(son + 1)}&gt;Bos&lt;/button&gt;;
}</code></pre>

<p><strong>Natija:</strong> Sayt yoqilishi bilanoq <code>setSon</code> chaqiriladi, son o'sadi, bu — qayta render, yana <code>setSon</code> chaqiriladi... <strong>cheksiz aylanma</strong> va brauzer qotadi.</p>

<p>Sabab: <code>setSon(son + 1)</code> — bu <em>chaqiriq</em>. <code>onClick</code> — <em>funksiyani kutadi</em>. To'g'risi:</p>

<pre><code>// Variant 1: arrow function
&lt;button onClick={() =&gt; setSon(son + 1)}&gt;Bos&lt;/button&gt;

// Variant 2: alohida funksiya
const oshirish = () =&gt; setSon(son + 1);
&lt;button onClick={oshirish}&gt;Bos&lt;/button&gt;</code></pre>

<p>Qoidasi: <code>onClick</code> ga funksiya, qiymat emas.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. useState anatomiyasi</h4>
<pre><code>const [QIYMAT, SET_FUNKSIYA] = useState(BOSHLANGICH);</code></pre>
<ul>
<li><strong>QIYMAT</strong> — joriy state qiymati (har render'da o'qiladi)</li>
<li><strong>SET_FUNKSIYA</strong> — yangi qiymat berish (React render'ni triggеrlaydi)</li>
<li><strong>BOSHLANGICH</strong> — birinchi render uchun</li>
</ul>

<h4>2. State immutable — har doim yangi qiymat</h4>
<pre><code>// ❌ NO — to'g'ridan-to'g'ri o'zgartirish ishlamaydi
hobby.push("kitob");
setHobby(hobby);

// ✅ HA — yangi array yarating
setHobby([...hobby, "kitob"]);

// ✅ HA — element o'chirish
setHobby(hobby.filter(h =&gt; h !== "kitob"));

// ✅ HA — element yangilash
setHobby(hobby.map(h =&gt; h === "old" ? "new" : h));</code></pre>

<p>Obyekt uchun ham — yangi obyekt yarating:</p>
<pre><code>setProfil({ ...profil, shahar: "Samarqand" });</code></pre>

<h4>3. Functional update — oldingi qiymatdan boshqa</h4>
<pre><code>// Bu xato bo'lishi mumkin (eski son'dan o'qishi mumkin)
setSon(son + 1);
setSon(son + 1);  // ikkalasi ham son = 0 dan, natija = 1

// To'g'risi — functional
setSon(s =&gt; s + 1);
setSon(s =&gt; s + 1);  // 0 → 1 → 2</code></pre>

<p>Qoidasi: oldingi state'ga bog'liq yangilanish — <code>setState(prev =&gt; ...)</code>.</p>

<h4>4. Render — qachon va nima</h4>
<p>Komponent qayta render bo'ladi:</p>
<ul>
<li>State o'zgarganda (<code>setX</code> chaqirilganda)</li>
<li>Props o'zgarganda (parent yangi qiymat bersa)</li>
<li>Parent render bo'lganda</li>
</ul>

<p>Har render'da — komponent funksiyasi qaytadan chaqiriladi. <code>const</code>'lar qaytadan e'lon qilinadi. Lekin <code>useState</code> bilan e'lon qilingan qiymat — React tomonidan eslab qolinadi.</p>

<h4>5. Event obyekti</h4>
<pre><code>function onChange(e) {
  console.log(e.target.value);   // input ichidagi qiymat
  console.log(e.target.name);    // input nomi
  console.log(e.key);            // bosilgan klavisha (keydown)
  e.preventDefault();            // default browser behavior'ni to'xtatish
}</code></pre>

<h4>6. Toggle qilish</h4>
<pre><code>function Switch() {
  const [yoq, setYoq] = useState(false);
  return (
    &lt;button onClick={() =&gt; setYoq(y =&gt; !y)}&gt;
      {yoq ? "yo'q" : "ha"}
    &lt;/button&gt;
  );
}</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>useState(boshlangich)</code> — komponent xotirasi</li>
<li>✅ <code>set...</code> — qiymat yangilash, render triggеrlaydi</li>
<li>✅ State immutable — yangi array/object yarating, mutate qilmang</li>
<li>✅ Functional update: <code>setX(prev =&gt; ...)</code></li>
<li>✅ <code>onClick</code> ga funksiya, qiymat emas</li>
<li>✅ Event: <code>e.target.value</code>, <code>e.preventDefault()</code></li>
</ul>
"""

L3_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 3: useState va event handler'lar
// ════════════════════════════════════════════════════════════════════

import { useState } from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) Birinchi counter
// ─────────────────────────────────────────────────────────────────────

function Counter() {
  const [son, setSon] = useState(0);

  return (
    <div>
      <p>Son: {son}</p>
      <button onClick={() => setSon(son + 1)}>+1</button>
      <button onClick={() => setSon(son - 1)}>-1</button>
      <button onClick={() => setSon(0)}>Reset</button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 2) Functional update — eski qiymatdan
// ─────────────────────────────────────────────────────────────────────

function CounterTogri() {
  const [son, setSon] = useState(0);

  // 3 marta ketma-ket — har biri oldingisidan o'sadi
  const ucMarta = () => {
    setSon(s => s + 1);
    setSon(s => s + 1);
    setSon(s => s + 1);
  };

  return (
    <div>
      <p>{son}</p>
      <button onClick={ucMarta}>+3</button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) Toggle (boolean state)
// ─────────────────────────────────────────────────────────────────────

function DarkMode() {
  const [dark, setDark] = useState(false);

  return (
    <div style={{
      background: dark ? "#222" : "#fff",
      color: dark ? "#fff" : "#000",
      padding: 20,
    }}>
      <p>{dark ? "Qorong'i rejim" : "Yorug'lik rejim"}</p>
      <button onClick={() => setDark(d => !d)}>
        Almashtirish
      </button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 4) String state — input bilan
// ─────────────────────────────────────────────────────────────────────

function SalomForma() {
  const [ism, setIsm] = useState("");

  return (
    <div>
      <input
        value={ism}
        onChange={(e) => setIsm(e.target.value)}
        placeholder="Ismingizni yozing"
      />
      <p>Salom, {ism || "mehmon"}!</p>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 5) Array state — todo ro'yxati
// ─────────────────────────────────────────────────────────────────────

function TodoOddiy() {
  const [matn, setMatn] = useState("");
  const [todos, setTodos] = useState([]);

  const qoshish = () => {
    if (!matn.trim()) return;
    setTodos([...todos, matn]);   // ✅ yangi array
    setMatn("");
  };

  const ochirish = (index) => {
    setTodos(todos.filter((_, i) => i !== index));
  };

  return (
    <div>
      <input
        value={matn}
        onChange={(e) => setMatn(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && qoshish()}
      />
      <button onClick={qoshish}>+</button>

      <ul>
        {todos.map((t, i) => (
          <li key={i}>
            {t}
            <button onClick={() => ochirish(i)}>x</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 6) Object state
// ─────────────────────────────────────────────────────────────────────

function ProfilForma() {
  const [profil, setProfil] = useState({
    ism: "",
    yosh: 0,
    shahar: "Toshkent",
  });

  const ozgartirish = (maydon, qiymat) => {
    setProfil(p => ({ ...p, [maydon]: qiymat }));
  };

  return (
    <div>
      <input
        value={profil.ism}
        onChange={(e) => ozgartirish("ism", e.target.value)}
        placeholder="Ism"
      />
      <input
        type="number"
        value={profil.yosh}
        onChange={(e) => ozgartirish("yosh", Number(e.target.value))}
        placeholder="Yosh"
      />
      <select
        value={profil.shahar}
        onChange={(e) => ozgartirish("shahar", e.target.value)}
      >
        <option>Toshkent</option>
        <option>Samarqand</option>
        <option>Buxoro</option>
      </select>

      <pre>{JSON.stringify(profil, null, 2)}</pre>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 7) Event obyekti — turli hodisalar
// ─────────────────────────────────────────────────────────────────────

function Tutorial() {
  const [xabar, setXabar] = useState("");

  return (
    <div>
      <button onClick={() => setXabar("Bosildi")}>
        Bos
      </button>

      <div
        onMouseEnter={() => setXabar("Sichqoncha ustida")}
        onMouseLeave={() => setXabar("Sichqoncha ketdi")}
        style={{ border: "1px solid", padding: 20, marginTop: 10 }}
      >
        Bu yerga sichqoncha keltiring
      </div>

      <input
        onKeyDown={(e) => {
          if (e.key === "Enter") setXabar("Enter bosildi");
          if (e.key === "Escape") setXabar("ESC bosildi");
        }}
        placeholder="Enter yoki Escape bosing"
      />

      <p>{xabar}</p>
    </div>
  );
}
"""
R1_TEXT = """\
<h2>R1 — Modul 1 takrorlash: Counter + Todo list</h2>

<p>Birinchi 3 ta dars (JSX, Props, useState) — birga ishlatib, ikkita real komponent yasaymiz. Bu — har bir React tutorial'ning klassikalari: <strong>Counter</strong> va <strong>Todo list</strong>. Lekin bu safar — sizdan kompozitsiya ham talab qilamiz.</p>

<h3>Loyihaning maqsadi</h3>

<p>Tek <code>App</code> komponentidan iborat sayt yaratasiz. Ichida:</p>
<ul>
<li>3 ta <code>Counter</code> komponenti — har biri o'z state'iga ega</li>
<li><code>TodoList</code> — yozish, o'chirish, "bajarildi" belgisini qo'yish</li>
<li>Yuqorida — global statistika: jami sonlar, bajarilmagan todolar soni</li>
</ul>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — Counter komponenti</h4>
<p>Quyidagi props bilan ishlasin:</p>
<ul>
<li><code>label</code> — nima sanaymiz (masalan, "Olma")</li>
<li><code>start</code> — boshlang'ich qiymat (default 0)</li>
<li><code>step</code> — qadam (default 1)</li>
</ul>

<p>UI: label, joriy son, +/− tugmalari, Reset.</p>

<h4>Vazifa 2 — TodoList komponenti</h4>
<p>Ichki state:</p>
<ul>
<li><code>matn</code> — input qiymati</li>
<li><code>todos</code> — <code>[{ id, matn, bajarildi }]</code></li>
</ul>

<p>Funksiyalar: qo'shish (Enter ham ishlasin), o'chirish, "bajarildi" toggle.</p>

<h4>Vazifa 3 — Global statistika</h4>
<p>App ichida — <strong>parent</strong> sifatida:</p>
<ul>
<li>Counter'lar yig'indisi (lekin Counter'lar state'i ichki — bu qiyin!)</li>
<li>Bajarilmagan todolar soni</li>
</ul>

<p>💡 Hint: Counter state'ni App'ga "ko'tarish" (lifting state up) kerak bo'ladi.</p>

<h4>Vazifa 4 — Stillash</h4>
<p>Bajarilgan todo — chiziq bilan kechib o'tilgan (line-through), och kulrang rang.</p>

<h4>Vazifa 5 — Bo'sh holat</h4>
<p>Agar todos bo'sh — "Hech narsa yo'q, birinchi vazifani qo'shing!" xabari ko'rsatilsin.</p>

<h3>🐛 Ataylab qiyin: state lifting</h3>

<p>Boshlang'ich versiyada har Counter o'zining son'iga ega. Lekin App'ga "jami" kerak — qanday qilamiz?</p>

<p><strong>Yo'l 1 (oson):</strong> Counter ichki state'da qoldiring va App'ga onChange callback yuboring. Counter qiymat o'zgarsa, App'ni xabardor qilsin.</p>

<p><strong>Yo'l 2 (zamonaviy):</strong> Counter state'ni App'ga ko'taring. Counter shunchaki props oladi va onChange chaqiradi.</p>

<h3>Boshlang'ich kod</h3>

<pre><code>import { useState } from 'react';

function Counter({ label, start = 0, step = 1, value, onChange }) {
  // Vazifa: shu komponentni to'ldiring
  // Variant A: ichki state (oddiy)
  // Variant B: controlled component (App'dan value, onChange)
}

function TodoList() {
  // Vazifa: ichki state bilan
}

function App() {
  return (
    &lt;div&gt;
      &lt;h1&gt;Counter + Todo&lt;/h1&gt;
      &lt;Counter label="Olma" /&gt;
      &lt;Counter label="Banan" /&gt;
      &lt;Counter label="Olcha" /&gt;
      &lt;TodoList /&gt;
    &lt;/div&gt;
  );
}</code></pre>

<h3>Yechim (controlled variant)</h3>

<details>
<summary>To'liq yechim — avval o'zingiz urinib ko'ring!</summary>
<pre><code>import { useState } from 'react';

function Counter({ label, value, onChange, step = 1 }) {
  return (
    &lt;div className="counter"&gt;
      &lt;span&gt;{label}: &lt;b&gt;{value}&lt;/b&gt;&lt;/span&gt;
      &lt;button onClick={() =&gt; onChange(value - step)}&gt;-&lt;/button&gt;
      &lt;button onClick={() =&gt; onChange(value + step)}&gt;+&lt;/button&gt;
      &lt;button onClick={() =&gt; onChange(0)}&gt;Reset&lt;/button&gt;
    &lt;/div&gt;
  );
}

function TodoList({ todos, setTodos }) {
  const [matn, setMatn] = useState("");

  const qoshish = () =&gt; {
    if (!matn.trim()) return;
    setTodos([...todos, { id: Date.now(), matn, bajarildi: false }]);
    setMatn("");
  };

  const ochirish = (id) =&gt; setTodos(todos.filter(t =&gt; t.id !== id));

  const toggle = (id) =&gt; setTodos(todos.map(t =&gt;
    t.id === id ? { ...t, bajarildi: !t.bajarildi } : t
  ));

  return (
    &lt;div&gt;
      &lt;input
        value={matn}
        onChange={(e) =&gt; setMatn(e.target.value)}
        onKeyDown={(e) =&gt; e.key === "Enter" && qoshish()}
        placeholder="Yangi vazifa"
      /&gt;
      &lt;button onClick={qoshish}&gt;Qo'shish&lt;/button&gt;

      {todos.length === 0 ? (
        &lt;p&gt;🌱 Hech narsa yo'q, birinchi vazifani qo'shing!&lt;/p&gt;
      ) : (
        &lt;ul&gt;
          {todos.map(t =&gt; (
            &lt;li key={t.id} style={{
              textDecoration: t.bajarildi ? "line-through" : "none",
              color: t.bajarildi ? "#999" : "inherit"
            }}&gt;
              &lt;input
                type="checkbox"
                checked={t.bajarildi}
                onChange={() =&gt; toggle(t.id)}
              /&gt;
              {t.matn}
              &lt;button onClick={() =&gt; ochirish(t.id)}&gt;x&lt;/button&gt;
            &lt;/li&gt;
          ))}
        &lt;/ul&gt;
      )}
    &lt;/div&gt;
  );
}

function App() {
  const [olma, setOlma] = useState(0);
  const [banan, setBanan] = useState(0);
  const [olcha, setOlcha] = useState(0);
  const [todos, setTodos] = useState([]);

  const jami = olma + banan + olcha;
  const qolgan = todos.filter(t =&gt; !t.bajarildi).length;

  return (
    &lt;div className="app"&gt;
      &lt;h1&gt;Counter + Todo&lt;/h1&gt;

      &lt;section&gt;
        &lt;h2&gt;Sonlar (jami: {jami})&lt;/h2&gt;
        &lt;Counter label="Olma"  value={olma}  onChange={setOlma} /&gt;
        &lt;Counter label="Banan" value={banan} onChange={setBanan} /&gt;
        &lt;Counter label="Olcha" value={olcha} onChange={setOlcha} step={2} /&gt;
      &lt;/section&gt;

      &lt;section&gt;
        &lt;h2&gt;Vazifalar ({qolgan} qoldi)&lt;/h2&gt;
        &lt;TodoList todos={todos} setTodos={setTodos} /&gt;
      &lt;/section&gt;
    &lt;/div&gt;
  );
}</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Modul 1 ning hammasi birga: JSX, Props, useState, event handler</li>
<li>✅ State lifting — child state'ni parent'ga ko'tarish</li>
<li>✅ Controlled components — value + onChange juftligi</li>
<li>✅ Array of objects state — qo'shish/o'chirish/yangilash</li>
<li>✅ Conditional rendering bilan birinchi tanishuv (bo'sh holat)</li>
</ul>
"""

R1_CODE = """\
// ════════════════════════════════════════════════════════════════════
// REVISION 1: Counter + Todo list
// Modul 1: JSX + Props + useState birga
// ════════════════════════════════════════════════════════════════════

import { useState } from 'react';

// ─────────────────────────────────────────────────────────────────────
// Counter — controlled component
// ─────────────────────────────────────────────────────────────────────

function Counter({ label, value, onChange, step = 1 }) {
  return (
    <div className="counter" style={{
      display: "flex",
      gap: 8,
      alignItems: "center",
      padding: 8,
    }}>
      <span style={{ minWidth: 80 }}>
        {label}: <b>{value}</b>
      </span>
      <button onClick={() => onChange(value - step)}>-</button>
      <button onClick={() => onChange(value + step)}>+</button>
      <button onClick={() => onChange(0)}>Reset</button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// TodoList — App'dan controlled
// ─────────────────────────────────────────────────────────────────────

function TodoList({ todos, setTodos }) {
  const [matn, setMatn] = useState("");

  const qoshish = () => {
    if (!matn.trim()) return;
    setTodos([
      ...todos,
      { id: Date.now(), matn: matn.trim(), bajarildi: false }
    ]);
    setMatn("");
  };

  const ochirish = (id) => {
    setTodos(todos.filter(t => t.id !== id));
  };

  const toggle = (id) => {
    setTodos(todos.map(t =>
      t.id === id ? { ...t, bajarildi: !t.bajarildi } : t
    ));
  };

  return (
    <div>
      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={matn}
          onChange={(e) => setMatn(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && qoshish()}
          placeholder="Yangi vazifa..."
          style={{ flex: 1, padding: 6 }}
        />
        <button onClick={qoshish}>Qo'shish</button>
      </div>

      {todos.length === 0 ? (
        <p style={{ color: "#888", marginTop: 16 }}>
          🌱 Hech narsa yo'q, birinchi vazifani qo'shing!
        </p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {todos.map(t => (
            <li
              key={t.id}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: 6,
                textDecoration: t.bajarildi ? "line-through" : "none",
                color: t.bajarildi ? "#999" : "inherit",
              }}
            >
              <input
                type="checkbox"
                checked={t.bajarildi}
                onChange={() => toggle(t.id)}
              />
              <span style={{ flex: 1 }}>{t.matn}</span>
              <button onClick={() => ochirish(t.id)}>x</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// App — bosh komponent, state lifting bilan
// ─────────────────────────────────────────────────────────────────────

function App() {
  const [olma, setOlma]   = useState(0);
  const [banan, setBanan] = useState(0);
  const [olcha, setOlcha] = useState(0);
  const [todos, setTodos] = useState([]);

  const jami = olma + banan + olcha;
  const qolgan = todos.filter(t => !t.bajarildi).length;
  const bajarilgan = todos.length - qolgan;

  return (
    <div className="app" style={{ maxWidth: 600, margin: "20px auto", padding: 20 }}>
      <h1>Counter + Todo Tasdiqlash</h1>

      <section style={{ marginBottom: 24 }}>
        <h2>Mevalar (jami: {jami})</h2>
        <Counter label="Olma"  value={olma}  onChange={setOlma}  />
        <Counter label="Banan" value={banan} onChange={setBanan} />
        <Counter label="Olcha" value={olcha} onChange={setOlcha} step={2} />
      </section>

      <section>
        <h2>Vazifalar ({qolgan} qoldi, {bajarilgan} bajarildi)</h2>
        <TodoList todos={todos} setTodos={setTodos} />
      </section>
    </div>
  );
}

export default App;
"""
L4_TEXT = """\
<h2>Conditional rendering va lists (key)</h2>

<pre class="mermaid">
flowchart LR
    DATA["arr.map(item => <Item />)"] --> RES["JSX qatorlar"]
    BOOL["shart ? A : B"] --> RES
    KEY["key={item.id}"] --> RES
</pre>

<p>React'da if/else va for siklini bevosita JSX ichida yoza olmaysiz (statement, not expression). Ammo har bir UI loyihasi ularsiz qila olmaydi: "agar foydalanuvchi tizimga kirgan bo'lsa profilini ko'rsat", "ro'yxatdagi har bir element uchun karta yarat". Bularning React usulini bugun o'rganamiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — ternary, &amp;&amp; va || bilan shart</h4>
<pre><code>function Salomlashish({ user }) {
  return (
    &lt;div&gt;
      {/* Ternary */}
      {user
        ? &lt;p&gt;Salom, {user.ism}!&lt;/p&gt;
        : &lt;p&gt;Tizimga kiring&lt;/p&gt;}

      {/* Faqat agar TRUE bo'lsa ko'rsatish */}
      {user && user.admin && &lt;button&gt;Admin panel&lt;/button&gt;}

      {/* Default qiymat */}
      &lt;p&gt;Til: {user?.til || "uz"}&lt;/p&gt;
    &lt;/div&gt;
  );
}</code></pre>

<h4>BLOKA 2 — ro'yxatni map bilan render</h4>
<pre><code>function MevaRoyxati() {
  const mevalar = [
    { id: 1, nomi: "Olma", narx: 5000 },
    { id: 2, nomi: "Banan", narx: 12000 },
    { id: 3, nomi: "Olcha", narx: 18000 },
  ];

  return (
    &lt;ul&gt;
      {mevalar.map(meva =&gt; (
        &lt;li key={meva.id}&gt;
          {meva.nomi} — {meva.narx} so'm
        &lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}</code></pre>

<p>Yangi: <code>key={meva.id}</code>. Bu — React'ga har element qaysi ekanligini aytadi. <strong>Doim noyob va statik</strong> bo'lishi kerak.</p>

<h4>BLOKA 3 — filter + map bilan</h4>
<pre><code>function ArzonMevalar({ mevalar, limit = 10000 }) {
  const arzon = mevalar.filter(m =&gt; m.narx &lt; limit);

  if (arzon.length === 0) {
    return &lt;p&gt;{limit} so'mdan arzon meva yo'q&lt;/p&gt;;
  }

  return (
    &lt;ul&gt;
      {arzon.map(m =&gt; (
        &lt;li key={m.id}&gt;
          {m.nomi}: {m.narx} so'm
        &lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>{mevalar.map((meva, index) =&gt; (
  &lt;li key={index}&gt;{meva.nomi}&lt;/li&gt;
))}</code></pre>

<p><strong>Natija:</strong> Kod ishlaydi! Lekin bu — <em>yashirin bug</em>. Agar ro'yxatdan element o'chirilsa yoki tartib o'zgartirilsa, React komponentlarni noto'g'ri "qayta ishlatadi" — input qiymatlari, state, animatsiyalar — hammasi chiziladi.</p>

<p>To'g'risi: ma'lumotning <strong>haqiqiy id</strong>'sini ishlating (<code>meva.id</code>). Index — faqat ro'yxat <em>hech qachon o'zgarmasa</em> ishlatish mumkin.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Conditional rendering — 4 ta usul</h4>

<table>
<tr><th>Vaziyat</th><th>Sintaksis</th></tr>
<tr><td>Ikkitadan biri</td><td><code>{shart ? A : B}</code></td></tr>
<tr><td>Faqat agar TRUE</td><td><code>{shart && A}</code></td></tr>
<tr><td>Default qiymat</td><td><code>{value || "default"}</code></td></tr>
<tr><td>Murakkab</td><td>Komponent tepasida <code>if</code> + alohida <code>return</code></td></tr>
</table>

<pre><code>// Murakkab variantni — early return bilan
function Profil({ user, yuklanyapti, xato }) {
  if (yuklanyapti) return &lt;Spinner /&gt;;
  if (xato) return &lt;Xato xabar={xato} /&gt;;
  if (!user) return &lt;Login /&gt;;

  return &lt;ProfilKartochkasi user={user} /&gt;;
}</code></pre>

<h4>2. ⚠️ <code>&amp;&amp;</code> ning xavfi</h4>
<pre><code>{soni && &lt;p&gt;{soni} ta xabar&lt;/p&gt;}

// soni = 0 bo'lsa, UI'da "0" so'zi ko'rinadi! 0 — falsy lekin renderlanadigan qiymat</code></pre>

<p>Yechim: aniq boolean qiling — <code>{soni > 0 && ...}</code> yoki <code>{Boolean(soni) && ...}</code>.</p>

<h4>3. key — nima uchun kerak?</h4>
<p>React har render'da yangi va eski JSX daraxtini taqqoslaydi (reconciliation). Kalit yo'q bo'lsa — qaysi element qaysi ekanini bilmaydi va xato qayta ishlatadi:</p>

<pre><code>// Render 1: [A, B, C]    keylar: 0, 1, 2
// Render 2: [X, A, B, C] keylar: 0, 1, 2, 3
// React: "0 idx — A edi, endi X — bu o'sha element, mazmuni o'zgardi"
// (Aslida X yangi, A o'sha)

// To'g'ri kalit bo'lsa:
// Render 1: A(id:1), B(id:2), C(id:3)
// Render 2: X(id:99), A(id:1), B(id:2), C(id:3)
// React: "X — yangi, qolganlari joyini o'zgartirgan"</code></pre>

<h4>4. key qoidalari</h4>
<ul>
<li>✅ <strong>Noyob</strong> shu ro'yxat ichida (boshqa ro'yxatda takrorlanishi mumkin)</li>
<li>✅ <strong>Statik</strong> — har render'da o'sha element o'sha key'ga ega</li>
<li>✅ <strong>Ma'lumot id</strong> eng yaxshi (database id, slug)</li>
<li>❌ <strong>Index</strong> — faqat ro'yxat o'zgarmas bo'lsa (kam holatda)</li>
<li>❌ <strong>Math.random()</strong> — har render'da yangi, butun shart bekor</li>
</ul>

<h4>5. Fragment'larda key</h4>
<pre><code>{ items.map(item =&gt; (
  &lt;React.Fragment key={item.id}&gt;
    &lt;dt&gt;{item.nomi}&lt;/dt&gt;
    &lt;dd&gt;{item.matn}&lt;/dd&gt;
  &lt;/React.Fragment&gt;
))}

// Qisqa &lt;&gt;...&lt;/&gt; — key qabul qila olmaydi, to'liq React.Fragment kerak</code></pre>

<h4>6. Murakkab — switch/CASE pattern</h4>
<pre><code>function Sahifa({ tur }) {
  const sahifalar = {
    bosh: &lt;Bosh /&gt;,
    profil: &lt;Profil /&gt;,
    sozlamalar: &lt;Sozlamalar /&gt;,
  };

  return sahifalar[tur] || &lt;NotFound /&gt;;
}</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>{shart ? A : B}</code>, <code>{shart && A}</code>, <code>{val || "def"}</code></li>
<li>✅ <code>&&</code> bilan 0 va '' xavfi — aniq boolean qiling</li>
<li>✅ <code>arr.map(...)</code> bilan ro'yxat render</li>
<li>✅ <code>key</code> noyob va statik — ma'lumot id'si</li>
<li>✅ Index'ni key qilib ishlatish — faqat o'zgarmas ro'yxatda</li>
<li>✅ Early return bilan murakkab shartlarni soddalashtirish</li>
</ul>
"""

L4_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 4: Conditional rendering va lists (key)
// ════════════════════════════════════════════════════════════════════

import { useState } from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) 4 ta conditional rendering uslubi
// ─────────────────────────────────────────────────────────────────────

function Salomlashish({ user }) {
  return (
    <div>
      {/* a) Ternary */}
      {user
        ? <p>Salom, {user.ism}!</p>
        : <p>Tizimga kiring</p>}

      {/* b) && */}
      {user && user.admin && <button>Admin panel</button>}

      {/* c) || (default) */}
      <p>Til: {user?.til || "uz"}</p>

      {/* d) Nested */}
      {user
        ? user.faol
          ? <span>🟢 onlayn</span>
          : <span>⚫ offlayn</span>
        : <span>Mehmon</span>}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 2) Early return — murakkab shartlar
// ─────────────────────────────────────────────────────────────────────

function Profil({ user, yuklanyapti, xato }) {
  if (yuklanyapti) return <p>Yuklanmoqda...</p>;
  if (xato) return <p>Xato: {xato}</p>;
  if (!user) return <p>Tizimga kiring</p>;

  return (
    <div>
      <h2>{user.ism}</h2>
      <p>{user.email}</p>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) Ro'yxatni map bilan
// ─────────────────────────────────────────────────────────────────────

function MevaRoyxati() {
  const mevalar = [
    { id: 1, nomi: "Olma",  narx:  5000 },
    { id: 2, nomi: "Banan", narx: 12000 },
    { id: 3, nomi: "Olcha", narx: 18000 },
    { id: 4, nomi: "O'rik", narx:  9000 },
  ];

  return (
    <ul>
      {mevalar.map(meva => (
        <li key={meva.id}>
          {meva.nomi} — <b>{meva.narx.toLocaleString()}</b> so'm
        </li>
      ))}
    </ul>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 4) Filter + map + bo'sh holat
// ─────────────────────────────────────────────────────────────────────

function ArzonRoyxat() {
  const [limit, setLimit] = useState(10000);

  const mevalar = [
    { id: 1, nomi: "Olma",  narx:  5000 },
    { id: 2, nomi: "Banan", narx: 12000 },
    { id: 3, nomi: "Olcha", narx: 18000 },
    { id: 4, nomi: "O'rik", narx:  9000 },
  ];

  const arzon = mevalar.filter(m => m.narx < limit);

  return (
    <div>
      <input
        type="number"
        value={limit}
        onChange={(e) => setLimit(Number(e.target.value))}
      />
      <p>{limit} so'mdan arzon mevalar:</p>

      {arzon.length === 0 ? (
        <p>🌱 Bu narxga arzon hech narsa yo'q</p>
      ) : (
        <ul>
          {arzon.map(m => (
            <li key={m.id}>{m.nomi}: {m.narx}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 5) && tuzog'i — 0 va ''
// ─────────────────────────────────────────────────────────────────────

function Korsatkich({ soni, matn }) {
  return (
    <div>
      {/* ❌ XATO: soni = 0 bo'lsa, "0" ekranda ko'rinadi */}
      {/* {soni && <p>{soni} ta xabar</p>} */}

      {/* ✅ TO'G'RI: aniq boolean */}
      {soni > 0 && <p>{soni} ta xabar</p>}
      {Boolean(matn) && <p>{matn}</p>}

      {/* ✅ Alternativ: ternary bilan null */}
      {soni > 0 ? <p>{soni} ta xabar</p> : null}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 6) Switch pattern — sahifalar
// ─────────────────────────────────────────────────────────────────────

function Bosh()         { return <div>🏠 Bosh sahifa</div>; }
function Kurslar()      { return <div>📚 Kurslar</div>; }
function Profil2()      { return <div>👤 Profil</div>; }
function NotFound()     { return <div>🚫 Topilmadi</div>; }

function Sahifa({ tur }) {
  const sahifalar = {
    bosh:    <Bosh />,
    kurslar: <Kurslar />,
    profil:  <Profil2 />,
  };

  return sahifalar[tur] || <NotFound />;
}

// ─────────────────────────────────────────────────────────────────────
// 7) Index xavfi — input ichidagi qiymat yo'qoladi
// ─────────────────────────────────────────────────────────────────────

function TodoXatoVsTogri() {
  const [todos, setTodos] = useState([
    { id: 1, matn: "A" },
    { id: 2, matn: "B" },
    { id: 3, matn: "C" },
  ]);

  const teskari = () => setTodos([...todos].reverse());

  return (
    <div>
      <button onClick={teskari}>Teskari</button>

      <h4>❌ key={"{index}"} — input qiymatlari aralashib ketadi</h4>
      <ul>
        {todos.map((t, i) => (
          <li key={i}>
            <input defaultValue={t.matn} />
          </li>
        ))}
      </ul>

      <h4>✅ key={"{t.id}"} — input qiymatlari to'g'ri qo'shilib ketadi</h4>
      <ul>
        {todos.map(t => (
          <li key={t.id}>
            <input defaultValue={t.matn} />
          </li>
        ))}
      </ul>
    </div>
  );
}
"""
L5_TEXT = """\
<h2>Forms va controlled inputs</h2>

<pre class="mermaid">
flowchart LR
    INP["input"] -->|onChange| ST["state"]
    ST -->|value=| INP
    SUB["onSubmit"] -->|preventDefault| API["API ga yuborish"]
</pre>

<p>Har bir veb-saytda forma bor: login, ro'yxatga olish, qidiruv, fikr-mulohaza. React'da formalar maxsus uslubda yoziladi — <strong>controlled components</strong>. Input qiymati React state'da yashaydi, browser'da emas.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi controlled input</h4>
<pre><code>function SaloLogin() {
  const [ism, setIsm] = useState("");

  return (
    &lt;div&gt;
      &lt;input
        value={ism}
        onChange={e =&gt; setIsm(e.target.value)}
        placeholder="Ismingiz"
      /&gt;
      &lt;p&gt;Salom, {ism || "mehmon"}!&lt;/p&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p>2 ta majburiy qism:</p>
<ol>
<li><code>value={ism}</code> — input qiymati state'dan</li>
<li><code>onChange={...}</code> — har klavisha bosilganda state yangilanadi</li>
</ol>

<h4>BLOKA 2 — multi-input form</h4>
<pre><code>function RoyxatdanOtish() {
  const [forma, setForma] = useState({
    ism: "",
    email: "",
    parol: "",
    yosh: 18,
  });

  const ozgartir = (e) =&gt; {
    const { name, value } = e.target;
    setForma(f =&gt; ({ ...f, [name]: value }));
  };

  const yuborish = (e) =&gt; {
    e.preventDefault();   // browser default'ni to'xtatish
    console.log("Yuborildi:", forma);
  };

  return (
    &lt;form onSubmit={yuborish}&gt;
      &lt;input name="ism"   value={forma.ism}   onChange={ozgartir} /&gt;
      &lt;input name="email" value={forma.email} onChange={ozgartir} /&gt;
      &lt;input name="parol" type="password" value={forma.parol} onChange={ozgartir} /&gt;
      &lt;input name="yosh"  type="number"   value={forma.yosh}  onChange={ozgartir} /&gt;
      &lt;button type="submit"&gt;Ro'yxatdan o'tish&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p>Bitta <code>ozgartir</code> funksiya, hamma input <code>name</code> attribute'i bilan farqlanadi. Bu — eng tez yo'l.</p>

<h4>BLOKA 3 — validatsiya</h4>
<pre><code>function FormaValidatsiyali() {
  const [email, setEmail] = useState("");
  const [parol, setParol] = useState("");

  const xatolar = {};
  if (!email.includes("@")) xatolar.email = "Email noto'g'ri";
  if (parol.length &lt; 8)     xatolar.parol = "Parol 8+ belgi bo'lsin";

  const yaroqli = Object.keys(xatolar).length === 0;

  return (
    &lt;form onSubmit={(e) =&gt; {
      e.preventDefault();
      if (!yaroqli) return;
      console.log({ email, parol });
    }}&gt;
      &lt;input
        value={email}
        onChange={e =&gt; setEmail(e.target.value)}
        placeholder="email"
      /&gt;
      {xatolar.email && &lt;p style={{color: 'red'}}&gt;{xatolar.email}&lt;/p&gt;}

      &lt;input
        type="password"
        value={parol}
        onChange={e =&gt; setParol(e.target.value)}
      /&gt;
      {xatolar.parol && &lt;p style={{color: 'red'}}&gt;{xatolar.parol}&lt;/p&gt;}

      &lt;button type="submit" disabled={!yaroqli}&gt;Kirish&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>&lt;input onChange={e =&gt; setIsm(e.target.value)} /&gt;
// (value attribute YO'Q)</code></pre>

<p><strong>Natija:</strong> Bu — uncontrolled component. React'da kam ishlatamiz, chunki bir necha muammo bor: validatsiya qiyin, dasturlash bilan tozalash qiyin, debug qilish chigal. Doim <code>value</code> + <code>onChange</code> juftligi.</p>

<p>Boshqa katta xato — <code>e.preventDefault()</code> ni unutib qoldirish. Bu yo'q bo'lsa, form submit qilganda <strong>sahifa to'liq qayta yuklanadi</strong> va React state'i yo'qoladi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Controlled vs Uncontrolled</h4>
<table>
<tr><th></th><th>Controlled</th><th>Uncontrolled</th></tr>
<tr><td>value qaerda</td><td>React state</td><td>DOM</td></tr>
<tr><td>O'qish</td><td>state'dan</td><td>ref bilan</td></tr>
<tr><td>Validatsiya</td><td>oson</td><td>qiyin</td></tr>
<tr><td>Misol</td><td><code>value={x} onChange={...}</code></td><td><code>defaultValue + ref</code></td></tr>
</table>

<p>Default — controlled. Uncontrolled — faqat juda kichik formalar yoki file upload uchun.</p>

<h4>2. Form elementlari</h4>

<table>
<tr><th>Element</th><th>value</th><th>onChange</th></tr>
<tr><td><code>input</code></td><td>matn</td><td><code>e.target.value</code></td></tr>
<tr><td><code>textarea</code></td><td>matn</td><td><code>e.target.value</code></td></tr>
<tr><td><code>select</code></td><td>tanlangan option</td><td><code>e.target.value</code></td></tr>
<tr><td><code>input type="checkbox"</code></td><td><code>checked={...}</code></td><td><code>e.target.checked</code></td></tr>
<tr><td><code>input type="radio"</code></td><td><code>checked={...}</code></td><td><code>e.target.value</code></td></tr>
<tr><td><code>input type="file"</code></td><td>—</td><td><code>e.target.files</code> (uncontrolled)</td></tr>
</table>

<h4>3. Select</h4>
<pre><code>const [shahar, setShahar] = useState("toshkent");

&lt;select value={shahar} onChange={e =&gt; setShahar(e.target.value)}&gt;
  &lt;option value="toshkent"&gt;Toshkent&lt;/option&gt;
  &lt;option value="samarqand"&gt;Samarqand&lt;/option&gt;
  &lt;option value="buxoro"&gt;Buxoro&lt;/option&gt;
&lt;/select&gt;</code></pre>

<h4>4. Checkbox</h4>
<pre><code>const [tanladi, setTanladi] = useState(false);

&lt;input
  type="checkbox"
  checked={tanladi}
  onChange={e =&gt; setTanladi(e.target.checked)}
/&gt;</code></pre>

<h4>5. Forma submit'ning butun yo'li</h4>
<pre><code>function Login() {
  const [forma, setForma] = useState({ email: "", parol: "" });
  const [yubormoq, setYubormoq] = useState(false);
  const [xato, setXato] = useState(null);

  const yuborish = async (e) =&gt; {
    e.preventDefault();
    setYubormoq(true);
    setXato(null);
    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(forma),
      });
      if (!res.ok) throw new Error("Login xato");
      // ... muvaffaqiyat
    } catch (e) {
      setXato(e.message);
    } finally {
      setYubormoq(false);
    }
  };

  return (
    &lt;form onSubmit={yuborish}&gt;
      ...
      &lt;button type="submit" disabled={yubormoq}&gt;
        {yubormoq ? "Yuklanmoqda..." : "Kirish"}
      &lt;/button&gt;
      {xato && &lt;p&gt;{xato}&lt;/p&gt;}
    &lt;/form&gt;
  );
}</code></pre>

<h4>6. Production'da — React Hook Form yoki Formik</h4>
<p>Haqiqiy ish boshlanganda, qo'lda yozish o'rniga <strong>React Hook Form</strong> yoki <strong>Formik</strong> ishlatasiz. Lekin qo'lda yozishni bilish — fundamental.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Controlled component = <code>value</code> + <code>onChange</code></li>
<li>✅ Multi-input — <code>name</code> attribute + spread state</li>
<li>✅ <code>e.preventDefault()</code> — sahifa qayta yuklanmasin</li>
<li>✅ Inline validatsiya — har render'da qaytadan hisoblash</li>
<li>✅ Checkbox: <code>checked</code> + <code>e.target.checked</code></li>
<li>✅ Submit jarayoni: <code>yubormoq</code> + <code>xato</code> state'lari</li>
</ul>
"""

L5_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 5: Forms va controlled inputs
// ════════════════════════════════════════════════════════════════════

import { useState } from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) Birinchi controlled input
// ─────────────────────────────────────────────────────────────────────

function SaloLogin() {
  const [ism, setIsm] = useState("");

  return (
    <div>
      <input
        value={ism}
        onChange={(e) => setIsm(e.target.value)}
        placeholder="Ismingiz"
      />
      <p>Salom, {ism || "mehmon"}!</p>
      <button onClick={() => setIsm("")}>Tozalash</button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 2) Multi-input — bitta state obyekti
// ─────────────────────────────────────────────────────────────────────

function RoyxatdanOtish() {
  const [forma, setForma] = useState({
    ism: "",
    email: "",
    parol: "",
    yosh: 18,
    obuna: false,
  });

  const ozgartir = (e) => {
    const { name, value, type, checked } = e.target;
    setForma(f => ({
      ...f,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const yuborish = (e) => {
    e.preventDefault();
    console.log("Yuborildi:", forma);
    alert("Forma yuborildi! Console'ga qarang.");
  };

  return (
    <form onSubmit={yuborish} style={{ display: "grid", gap: 8, maxWidth: 320 }}>
      <input
        name="ism" value={forma.ism} onChange={ozgartir}
        placeholder="Ism" required
      />
      <input
        name="email" type="email" value={forma.email} onChange={ozgartir}
        placeholder="Email" required
      />
      <input
        name="parol" type="password" value={forma.parol} onChange={ozgartir}
        placeholder="Parol" required minLength={8}
      />
      <input
        name="yosh" type="number" value={forma.yosh} onChange={ozgartir}
        min={14} max={100}
      />
      <label>
        <input
          name="obuna" type="checkbox" checked={forma.obuna} onChange={ozgartir}
        />
        Yangilik xabarlariga obuna
      </label>
      <button type="submit">Ro'yxatdan o'tish</button>

      <pre>{JSON.stringify(forma, null, 2)}</pre>
    </form>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) Validatsiya — render vaqtida hisoblash
// ─────────────────────────────────────────────────────────────────────

function FormaValidatsiyali() {
  const [email, setEmail] = useState("");
  const [parol, setParol] = useState("");
  const [yuborildi, setYuborildi] = useState(false);

  const xatolar = {};
  if (!email.includes("@")) xatolar.email = "Email noto'g'ri";
  if (parol.length < 8) xatolar.parol = "Parol 8+ belgi bo'lishi kerak";
  if (parol === email) xatolar.parol = "Parol email bilan bir xil bo'lmasin";

  const yaroqli = Object.keys(xatolar).length === 0;

  const yuborish = (e) => {
    e.preventDefault();
    setYuborildi(true);
    if (!yaroqli) return;
    console.log({ email, parol });
  };

  return (
    <form onSubmit={yuborish}>
      <div>
        <input
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="email"
          style={{ borderColor: yuborildi && xatolar.email ? "red" : undefined }}
        />
        {yuborildi && xatolar.email && (
          <p style={{ color: "red", margin: 4 }}>{xatolar.email}</p>
        )}
      </div>

      <div>
        <input
          type="password"
          value={parol}
          onChange={(e) => setParol(e.target.value)}
          placeholder="parol"
        />
        {yuborildi && xatolar.parol && (
          <p style={{ color: "red", margin: 4 }}>{xatolar.parol}</p>
        )}
      </div>

      <button type="submit" disabled={yuborildi && !yaroqli}>
        Kirish
      </button>
    </form>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 4) Select, radio, textarea — barcha element turlari
// ─────────────────────────────────────────────────────────────────────

function HarTuriForma() {
  const [forma, setForma] = useState({
    shahar: "toshkent",
    jins: "erkak",
    izoh: "",
    fanlar: { matematika: false, fizika: false, tarix: false },
  });

  const ozgartir = (e) => {
    const { name, value } = e.target;
    setForma(f => ({ ...f, [name]: value }));
  };

  const fanOzgartir = (fan) => {
    setForma(f => ({
      ...f,
      fanlar: { ...f.fanlar, [fan]: !f.fanlar[fan] },
    }));
  };

  return (
    <form>
      <label>
        Shahar:
        <select name="shahar" value={forma.shahar} onChange={ozgartir}>
          <option value="toshkent">Toshkent</option>
          <option value="samarqand">Samarqand</option>
          <option value="buxoro">Buxoro</option>
        </select>
      </label>

      <div>
        <label>
          <input type="radio" name="jins" value="erkak"
            checked={forma.jins === "erkak"} onChange={ozgartir} /> Erkak
        </label>
        <label>
          <input type="radio" name="jins" value="ayol"
            checked={forma.jins === "ayol"} onChange={ozgartir} /> Ayol
        </label>
      </div>

      <textarea
        name="izoh" value={forma.izoh} onChange={ozgartir}
        rows={4} placeholder="Izoh..."
      />

      <fieldset>
        <legend>Sevimli fanlar:</legend>
        {Object.entries(forma.fanlar).map(([fan, tanlangan]) => (
          <label key={fan}>
            <input
              type="checkbox" checked={tanlangan}
              onChange={() => fanOzgartir(fan)}
            />
            {fan}
          </label>
        ))}
      </fieldset>

      <pre>{JSON.stringify(forma, null, 2)}</pre>
    </form>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 5) Async submit — yuklanyapti state
// ─────────────────────────────────────────────────────────────────────

function LoginAsync() {
  const [forma, setForma] = useState({ email: "", parol: "" });
  const [yubormoq, setYubormoq] = useState(false);
  const [xato, setXato] = useState(null);

  const yuborish = async (e) => {
    e.preventDefault();
    setYubormoq(true);
    setXato(null);
    try {
      // Soxta API
      await new Promise(r => setTimeout(r, 1500));
      if (forma.email !== "admin@uz") throw new Error("Email topilmadi");
      alert("Muvaffaqiyatli!");
    } catch (e) {
      setXato(e.message);
    } finally {
      setYubormoq(false);
    }
  };

  return (
    <form onSubmit={yuborish}>
      <input
        value={forma.email}
        onChange={e => setForma(f => ({ ...f, email: e.target.value }))}
        placeholder="Email" required
      />
      <input
        type="password" value={forma.parol}
        onChange={e => setForma(f => ({ ...f, parol: e.target.value }))}
        placeholder="Parol" required
      />
      <button type="submit" disabled={yubormoq}>
        {yubormoq ? "Yuklanmoqda..." : "Kirish"}
      </button>
      {xato && <p style={{color:"red"}}>{xato}</p>}
    </form>
  );
}
"""
L6_TEXT = """\
<h2>useEffect — komponent hayoti va tashqi dunyo</h2>

<pre class="mermaid">
flowchart TB
    M["mount (birinchi render)"] -->|useEffect ishga tushadi| E1["effect"]
    E1 -->|cleanup yo'q| U["update — deps o'zgardi"]
    U -->|cleanup chaqiriladi| C["cleanup"]
    C -->|yangi effect| E2["effect"]
    UN["unmount"] -->|cleanup| END["tugadi"]
</pre>

<p>Hozirgacha har komponentingiz <strong>sof</strong> edi: ma'lumotni olib, JSX qaytaradi. Ammo real ilovalarda kerak: <em>tashqi API'dan ma'lumot olish, timer qo'yish, browser eventiga obuna bo'lish</em>. Bularning hammasi — <strong>side effects</strong>. <code>useEffect</code> — React'ning shu uchun maxsus huk'i.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi effect (mount)</h4>
<pre><code>import { useState, useEffect } from 'react';

function SoatBosh() {
  useEffect(() =&gt; {
    document.title = "Sahifa ochildi";
  }, []);   // [] — faqat bir marta (mount)

  return &lt;p&gt;Title o'zgardi&lt;/p&gt;;
}</code></pre>

<p><strong>[]</strong> — bo'sh dependency array. Effect <em>bir marta</em> — komponent ekran ko'ringanida. Ko'pincha API ga so'rov yuborish uchun.</p>

<h4>BLOKA 2 — qiymatga bog'liq effect</h4>
<pre><code>function SonHisoblagich() {
  const [son, setSon] = useState(0);

  useEffect(() =&gt; {
    document.title = `Son: ${son}`;
  }, [son]);   // har son o'zgarganda

  return &lt;button onClick={() =&gt; setSon(s =&gt; s + 1)}&gt;+1&lt;/button&gt;;
}</code></pre>

<h4>BLOKA 3 — cleanup (timer, listener)</h4>
<pre><code>function Soat() {
  const [vaqt, setVaqt] = useState(new Date());

  useEffect(() =&gt; {
    const id = setInterval(() =&gt; setVaqt(new Date()), 1000);

    return () =&gt; clearInterval(id);   // cleanup
  }, []);

  return &lt;p&gt;{vaqt.toLocaleTimeString()}&lt;/p&gt;;
}</code></pre>

<p>Cleanup funksiyasi qachon chaqiriladi:</p>
<ul>
<li>Komponent unmount (sahifadan olib tashlandi)</li>
<li>Deps o'zgardi (eski effect tozalanadi, yangi ishga tushadi)</li>
</ul>

<h4>BLOKA 4 — fetch bilan</h4>
<pre><code>function Foydalanuvchilar() {
  const [users, setUsers] = useState([]);
  const [yukla, setYukla] = useState(true);

  useEffect(() =&gt; {
    fetch("https://jsonplaceholder.typicode.com/users")
      .then(r =&gt; r.json())
      .then(data =&gt; {
        setUsers(data);
        setYukla(false);
      });
  }, []);

  if (yukla) return &lt;p&gt;Yuklanmoqda...&lt;/p&gt;;

  return (
    &lt;ul&gt;{users.map(u =&gt; &lt;li key={u.id}&gt;{u.name}&lt;/li&gt;)}&lt;/ul&gt;
  );
}</code></pre>

<h3>🐛 Ataylab xato (eng katta xato)</h3>
<pre><code>function CounterXato() {
  const [son, setSon] = useState(0);

  useEffect(() =&gt; {
    setSon(son + 1);    // ❌ infinite loop!
  });   // deps array YO'Q
}</code></pre>

<p><strong>Sabab:</strong></p>
<ol>
<li>Render</li>
<li>Effect ishga tushadi → <code>setSon</code></li>
<li>State o'zgardi → qayta render</li>
<li>Effect yana ishga tushadi → cheksiz...</li>
</ol>

<p>Brauzer qotadi. To'g'risi: deps array berish, va effekt ichida o'sha state'ni o'zgartirmaslik (yoki sharti bilan).</p>

<p>Ikkinchi katta xato — <strong>cleanup'ni unutish</strong>: timer, fetch (AbortController), socket listener'lar — hammasi memory leak yoki memory leak + bug.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Dependency array — 3 ta variant</h4>
<table>
<tr><th>Yozish</th><th>Effect qachon</th></tr>
<tr><td><code>useEffect(fn)</code></td><td>Har render'da (yomon — kam ishlatamiz)</td></tr>
<tr><td><code>useEffect(fn, [])</code></td><td>Faqat bir marta (mount)</td></tr>
<tr><td><code>useEffect(fn, [a, b])</code></td><td>a yoki b o'zgarganda</td></tr>
</table>

<h4>2. Cleanup pattern</h4>
<pre><code>useEffect(() =&gt; {
  // setup
  const id = setInterval(...)
  window.addEventListener("resize", handler)

  return () =&gt; {
    // cleanup
    clearInterval(id)
    window.removeEventListener("resize", handler)
  };
}, [deps]);</code></pre>

<h4>3. Race condition — fetch'da xavf</h4>
<pre><code>useEffect(() =&gt; {
  let ignore = false;
  fetch(`/api/user/${userId}`)
    .then(r =&gt; r.json())
    .then(data =&gt; {
      if (!ignore) setUser(data);
    });
  return () =&gt; { ignore = true; };
}, [userId]);</code></pre>

<p>Sabab: <code>userId</code> tez almashtirilsa, eski fetch hali ham keladi va yangi userni yozib tashlaydi. Cleanup bilan oldini olamiz.</p>

<h4>4. AbortController — yaxshi yo'l</h4>
<pre><code>useEffect(() =&gt; {
  const ctrl = new AbortController();

  fetch(url, { signal: ctrl.signal })
    .then(r =&gt; r.json())
    .then(setData)
    .catch(e =&gt; {
      if (e.name !== 'AbortError') throw e;
    });

  return () =&gt; ctrl.abort();
}, [url]);</code></pre>

<h4>5. Strict Mode'da effect 2 marta chaqiriladi (dev only)</h4>
<p>React 18+ StrictMode'da dev paytida har effect <strong>2 marta</strong> ishga tushiriladi — bu sizning cleanup'ingiz to'g'ri ekanligini tekshirish uchun. Production'da bir marta. Bu — bug emas, xususiyat.</p>

<h4>6. Qachon useEffect KERAK EMAS</h4>
<p>Eng katta xato — har narsani <code>useEffect</code>'ga solib qo'yish. Ko'p qiymatlar — derived state, alohida hisoblash kerak emas:</p>

<pre><code>// ❌ Yomon
const [tolaIsm, setTolaIsm] = useState("");
useEffect(() =&gt; {
  setTolaIsm(`${ism} ${familiya}`);
}, [ism, familiya]);

// ✅ Yaxshi
const tolaIsm = `${ism} ${familiya}`;  // har render'da hisoblanadi</code></pre>

<p>Qoidasi: <strong>state'ni state'dan hisoblash uchun useEffect kerak emas</strong>.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>useEffect(fn, deps)</code> — side effect</li>
<li>✅ <code>[]</code> — mount, <code>[a]</code> — a o'zgarganda</li>
<li>✅ Cleanup — <code>return () =&gt; ...</code> (timer, listener, fetch)</li>
<li>✅ Effect ichida setState — har doim ehtiyot (infinite loop)</li>
<li>✅ Race condition — <code>ignore</code> flag yoki AbortController</li>
<li>✅ StrictMode'da dev'da 2 marta — normal</li>
<li>✅ Derived state uchun useEffect kerak emas</li>
</ul>
"""

L6_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 6: useEffect va lifecycle
// ════════════════════════════════════════════════════════════════════

import { useState, useEffect } from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) Mount-only effect (deps = [])
// ─────────────────────────────────────────────────────────────────────

function Sahifa() {
  useEffect(() => {
    document.title = "Sahifa yuklandi";
    console.log("Mount");
  }, []);

  return <p>useEffect deps: []</p>;
}

// ─────────────────────────────────────────────────────────────────────
// 2) Qiymatga bog'liq
// ─────────────────────────────────────────────────────────────────────

function Hisoblagich() {
  const [son, setSon] = useState(0);

  useEffect(() => {
    document.title = `Son: ${son}`;
  }, [son]);

  return (
    <button onClick={() => setSon(s => s + 1)}>
      Son: {son}
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) Soat — cleanup bilan
// ─────────────────────────────────────────────────────────────────────

function Soat() {
  const [vaqt, setVaqt] = useState(new Date());

  useEffect(() => {
    const id = setInterval(() => setVaqt(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  return <p>{vaqt.toLocaleTimeString()}</p>;
}

// ─────────────────────────────────────────────────────────────────────
// 4) Window resize listener
// ─────────────────────────────────────────────────────────────────────

function OynaOlchami() {
  const [olcham, setOlcham] = useState({
    en: window.innerWidth,
    bo: window.innerHeight,
  });

  useEffect(() => {
    const handler = () => setOlcham({
      en: window.innerWidth,
      bo: window.innerHeight,
    });
    window.addEventListener("resize", handler);
    return () => window.removeEventListener("resize", handler);
  }, []);

  return <p>{olcham.en} × {olcham.bo}</p>;
}

// ─────────────────────────────────────────────────────────────────────
// 5) Fetch bilan — race condition yechimi
// ─────────────────────────────────────────────────────────────────────

function FoydalanuvchiKarti({ userId }) {
  const [user, setUser] = useState(null);
  const [yukla, setYukla] = useState(false);
  const [xato, setXato] = useState(null);

  useEffect(() => {
    let ignore = false;

    setYukla(true);
    setXato(null);

    fetch(`https://jsonplaceholder.typicode.com/users/${userId}`)
      .then(r => {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(data => {
        if (!ignore) {
          setUser(data);
          setYukla(false);
        }
      })
      .catch(e => {
        if (!ignore) {
          setXato(e.message);
          setYukla(false);
        }
      });

    return () => { ignore = true; };
  }, [userId]);

  if (yukla) return <p>Yuklanmoqda...</p>;
  if (xato) return <p>Xato: {xato}</p>;
  if (!user) return null;

  return (
    <div>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
      <p>{user.address?.city}</p>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 6) AbortController bilan
// ─────────────────────────────────────────────────────────────────────

function Maqolalar({ qidir }) {
  const [data, setData] = useState([]);
  const [yukla, setYukla] = useState(false);

  useEffect(() => {
    if (!qidir) return;

    const ctrl = new AbortController();
    setYukla(true);

    fetch(`https://jsonplaceholder.typicode.com/posts?q=${qidir}`, {
      signal: ctrl.signal,
    })
      .then(r => r.json())
      .then(d => {
        setData(d);
        setYukla(false);
      })
      .catch(e => {
        if (e.name !== "AbortError") {
          console.error(e);
          setYukla(false);
        }
      });

    return () => ctrl.abort();
  }, [qidir]);

  return (
    <div>
      {yukla && <p>Yuklanmoqda...</p>}
      <ul>{data.slice(0, 5).map(p => <li key={p.id}>{p.title}</li>)}</ul>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 7) ❌ Eng katta xato — infinite loop
// ─────────────────────────────────────────────────────────────────────

/*
function Xato() {
  const [son, setSon] = useState(0);
  useEffect(() => {
    setSon(son + 1);   // deps array YO'Q → har render'da, cheksiz
  });
  return <p>{son}</p>;
}
*/

// ─────────────────────────────────────────────────────────────────────
// 8) ❌ Yomon: derived state uchun useEffect
// ─────────────────────────────────────────────────────────────────────

function YomonForma({ ism, familiya }) {
  // ❌ Yomon
  // const [tola, setTola] = useState("");
  // useEffect(() => {
  //   setTola(`${ism} ${familiya}`);
  // }, [ism, familiya]);

  // ✅ Yaxshi — bevosita hisoblash
  const tola = `${ism} ${familiya}`;

  return <p>{tola}</p>;
}

// ─────────────────────────────────────────────────────────────────────
// 9) localStorage bilan
// ─────────────────────────────────────────────────────────────────────

function ThemeSwitcher() {
  const [dark, setDark] = useState(() => {
    return localStorage.getItem("dark") === "true";
  });

  useEffect(() => {
    localStorage.setItem("dark", dark);
    document.body.style.background = dark ? "#222" : "#fff";
    document.body.style.color = dark ? "#fff" : "#000";
  }, [dark]);

  return (
    <button onClick={() => setDark(d => !d)}>
      {dark ? "☀️ Yorug'" : "🌙 Qorong'i"}
    </button>
  );
}
"""
R2_TEXT = """\
<h2>R2 — Modul 2 takrorlash: Weather widget</h2>

<p>Modul 2 ning hammasi birga: <strong>controlled form</strong> (shahar tanlash), <strong>conditional rendering</strong> (yukla/xato/data), <strong>list</strong> (5 kunlik prognoz), <strong>useEffect</strong> (API'dan ma'lumot olish, race condition yechimi). Real ishlovchi mini-loyiha.</p>

<h3>Loyihaning maqsadi</h3>

<p>Foydalanuvchi shahar tanlaydi (dropdown yoki input), real API'dan ob-havo keladi va 3 ta holatdan birini ko'rsatadi:</p>
<ul>
<li>🔄 Yuklanmoqda — spinner</li>
<li>❌ Xato — qizil xabar + qayta urinish tugmasi</li>
<li>✅ Ma'lumot — joriy harorat + 5 kunlik prognoz</li>
</ul>

<h3>API tanlovi</h3>

<p>Bepul: <strong>Open-Meteo</strong> (API kalit shart emas):</p>
<pre><code>https://api.open-meteo.com/v1/forecast?latitude=41.31&amp;longitude=69.24&amp;current=temperature_2m,weather_code&amp;daily=temperature_2m_max,temperature_2m_min,weather_code&amp;timezone=Asia/Tashkent</code></pre>

<p>Shaharlar (lat/lon):</p>
<pre><code>const SHAHARLAR = {
  toshkent:  { lat: 41.31, lon: 69.24, nomi: "Toshkent" },
  samarqand: { lat: 39.65, lon: 66.97, nomi: "Samarqand" },
  buxoro:    { lat: 39.77, lon: 64.42, nomi: "Buxoro" },
  andijon:   { lat: 40.78, lon: 72.34, nomi: "Andijon" },
};</code></pre>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — Tuzilma</h4>
<p>3 ta komponent:</p>
<ul>
<li><code>ShaharTanlash</code> — dropdown</li>
<li><code>JoriyOb</code> — bugungi harorat + ikonka</li>
<li><code>BeshKunPrognoz</code> — ro'yxat</li>
<li><code>App</code> — hammasini bog'laydi</li>
</ul>

<h4>Vazifa 2 — Fetch va race condition</h4>
<p><code>useEffect</code> ichida shahar o'zgarganda qaytadan fetch. <strong>AbortController</strong> bilan eski so'rovni bekor qilish.</p>

<h4>Vazifa 3 — 3 ta holat</h4>
<p>Conditional rendering:</p>
<ul>
<li><code>yuklanmoqda</code>: "Yuklanmoqda..."</li>
<li><code>xato</code>: xato xabari + "Qayta urinish" tugmasi</li>
<li>aks holda: prognoz</li>
</ul>

<h4>Vazifa 4 — 5 kunlik prognoz</h4>
<p>5 ta kunni map bilan ro'yxatlang. Har kunda: sana (haftaning kuni), min/max harorat, ob-havo ikonkasi.</p>

<h4>Vazifa 5 — Refresh tugmasi</h4>
<p>Tugma bosilganda — qaytadan fetch (yoki avtomatik 5 daqiqada bir marta).</p>

<h3>🐛 Ataylab qiyin: race condition senariosi</h3>
<p>Foydalanuvchi tez-tez shaharlarni almashtirsa: Toshkent → Samarqand → Buxoro. 3 ta fetch ishga tushadi, lekin ular tartibsiz qaytishi mumkin. Buxoro fetch oldin qaytsa, keyin Samarqand keladi va Buxoro o'rniga ko'rinadi. AbortController bilan eski'larni bekor qilish — kerakli yechim.</p>

<h3>Yechim sketch</h3>

<details>
<summary>To'liq yechim — avval o'zingiz urinib ko'ring!</summary>
<pre><code>import { useState, useEffect } from 'react';

const SHAHARLAR = {
  toshkent:  { lat: 41.31, lon: 69.24, nomi: "Toshkent" },
  samarqand: { lat: 39.65, lon: 66.97, nomi: "Samarqand" },
  buxoro:    { lat: 39.77, lon: 64.42, nomi: "Buxoro" },
  andijon:   { lat: 40.78, lon: 72.34, nomi: "Andijon" },
};

const KOD_ICON = (code) =&gt; {
  if (code === 0) return "☀️";
  if (code &lt;= 3) return "⛅";
  if (code &lt;= 67) return "🌧️";
  return "❄️";
};

function ShaharTanlash({ qiymat, onChange }) {
  return (
    &lt;select value={qiymat} onChange={(e) =&gt; onChange(e.target.value)}&gt;
      {Object.entries(SHAHARLAR).map(([k, v]) =&gt; (
        &lt;option key={k} value={k}&gt;{v.nomi}&lt;/option&gt;
      ))}
    &lt;/select&gt;
  );
}

function App() {
  const [shahar, setShahar] = useState("toshkent");
  const [data, setData] = useState(null);
  const [yukla, setYukla] = useState(false);
  const [xato, setXato] = useState(null);
  const [yangilanish, setYangilanish] = useState(0);

  useEffect(() =&gt; {
    const { lat, lon } = SHAHARLAR[shahar];
    const ctrl = new AbortController();

    setYukla(true);
    setXato(null);

    fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${lat}&amp;longitude=${lon}&amp;current=temperature_2m,weather_code&amp;daily=temperature_2m_max,temperature_2m_min,weather_code&amp;timezone=Asia/Tashkent`,
      { signal: ctrl.signal }
    )
      .then(r =&gt; {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(d =&gt; {
        setData(d);
        setYukla(false);
      })
      .catch(e =&gt; {
        if (e.name !== "AbortError") {
          setXato(e.message);
          setYukla(false);
        }
      });

    return () =&gt; ctrl.abort();
  }, [shahar, yangilanish]);

  return (
    &lt;div&gt;
      &lt;ShaharTanlash qiymat={shahar} onChange={setShahar} /&gt;
      &lt;button onClick={() =&gt; setYangilanish(y =&gt; y + 1)}&gt;🔄&lt;/button&gt;

      {yukla && &lt;p&gt;⏳ Yuklanmoqda...&lt;/p&gt;}

      {xato && (
        &lt;div&gt;
          &lt;p style={{ color: 'red' }}&gt;❌ {xato}&lt;/p&gt;
          &lt;button onClick={() =&gt; setYangilanish(y =&gt; y + 1)}&gt;
            Qayta urinish
          &lt;/button&gt;
        &lt;/div&gt;
      )}

      {data && !yukla && (
        &lt;div&gt;
          &lt;h2&gt;{SHAHARLAR[shahar].nomi}&lt;/h2&gt;
          &lt;p&gt;{KOD_ICON(data.current.weather_code)} {data.current.temperature_2m}°C&lt;/p&gt;

          &lt;h3&gt;5 kun&lt;/h3&gt;
          &lt;ul&gt;
            {data.daily.time.slice(0, 5).map((sana, i) =&gt; (
              &lt;li key={sana}&gt;
                {sana}: {KOD_ICON(data.daily.weather_code[i])}
                {' '}{data.daily.temperature_2m_min[i]}° ↔ {data.daily.temperature_2m_max[i]}°
              &lt;/li&gt;
            ))}
          &lt;/ul&gt;
        &lt;/div&gt;
      )}
    &lt;/div&gt;
  );
}</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Modul 2 ning hammasi birga: forms + lists + conditional + useEffect</li>
<li>✅ AbortController bilan race condition yechish</li>
<li>✅ Refresh trigger pattern (incrementing state)</li>
<li>✅ Tashqi API bilan to'liq integratsiya</li>
<li>✅ 3 holat (yukla/xato/data) UX patterni</li>
</ul>
"""

R2_CODE = """\
// ════════════════════════════════════════════════════════════════════
// REVISION 2: Weather widget
// Modul 2: forms + lists + conditional + useEffect + fetch
// ════════════════════════════════════════════════════════════════════

import { useState, useEffect } from 'react';

const SHAHARLAR = {
  toshkent:  { lat: 41.31, lon: 69.24, nomi: "Toshkent" },
  samarqand: { lat: 39.65, lon: 66.97, nomi: "Samarqand" },
  buxoro:    { lat: 39.77, lon: 64.42, nomi: "Buxoro" },
  andijon:   { lat: 40.78, lon: 72.34, nomi: "Andijon" },
};

const KOD_ICON = (code) => {
  if (code === 0) return "☀️";
  if (code <= 3) return "⛅";
  if (code <= 48) return "🌫️";
  if (code <= 67) return "🌧️";
  if (code <= 77) return "❄️";
  if (code <= 99) return "⛈️";
  return "❔";
};

const HAFTAKUN = (sana) => {
  const kunlar = ["Yak","Du","Se","Ch","Pa","Ju","Sha"];
  return kunlar[new Date(sana).getDay()];
};

// ─────────────────────────────────────────────────────────────────────
// Komponentlar
// ─────────────────────────────────────────────────────────────────────

function ShaharTanlash({ qiymat, onChange }) {
  return (
    <select
      value={qiymat}
      onChange={(e) => onChange(e.target.value)}
      style={{ padding: 8, fontSize: 16 }}
    >
      {Object.entries(SHAHARLAR).map(([k, v]) => (
        <option key={k} value={k}>{v.nomi}</option>
      ))}
    </select>
  );
}

function JoriyOb({ data, shaharNomi }) {
  return (
    <div style={{ textAlign: "center", padding: 24 }}>
      <h2 style={{ margin: 0 }}>{shaharNomi}</h2>
      <div style={{ fontSize: 80 }}>{KOD_ICON(data.current.weather_code)}</div>
      <div style={{ fontSize: 48, fontWeight: "bold" }}>
        {Math.round(data.current.temperature_2m)}°
      </div>
    </div>
  );
}

function BeshKunPrognoz({ daily }) {
  return (
    <div>
      <h3>5 kunlik prognoz</h3>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {daily.time.slice(0, 5).map((sana, i) => (
          <li key={sana} style={{
            display: "flex",
            justifyContent: "space-between",
            padding: 8,
            borderBottom: "1px solid #eee",
          }}>
            <span style={{ width: 40 }}>{HAFTAKUN(sana)}</span>
            <span style={{ fontSize: 24 }}>{KOD_ICON(daily.weather_code[i])}</span>
            <span>
              {Math.round(daily.temperature_2m_min[i])}°
              {" / "}
              <b>{Math.round(daily.temperature_2m_max[i])}°</b>
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// App
// ─────────────────────────────────────────────────────────────────────

function App() {
  const [shahar, setShahar] = useState("toshkent");
  const [data, setData] = useState(null);
  const [yukla, setYukla] = useState(false);
  const [xato, setXato] = useState(null);
  const [yangilanish, setYangilanish] = useState(0);

  useEffect(() => {
    const { lat, lon } = SHAHARLAR[shahar];
    const ctrl = new AbortController();

    setYukla(true);
    setXato(null);

    const url =
      `https://api.open-meteo.com/v1/forecast` +
      `?latitude=${lat}&longitude=${lon}` +
      `&current=temperature_2m,weather_code` +
      `&daily=temperature_2m_max,temperature_2m_min,weather_code` +
      `&timezone=Asia/Tashkent`;

    fetch(url, { signal: ctrl.signal })
      .then(r => {
        if (!r.ok) throw new Error("Server xato: " + r.status);
        return r.json();
      })
      .then(d => {
        setData(d);
        setYukla(false);
      })
      .catch(e => {
        if (e.name === "AbortError") return;
        setXato(e.message);
        setYukla(false);
      });

    return () => ctrl.abort();
  }, [shahar, yangilanish]);

  return (
    <div style={{
      maxWidth: 360,
      margin: "20px auto",
      padding: 20,
      border: "1px solid #ddd",
      borderRadius: 12,
      fontFamily: "sans-serif",
    }}>
      <div style={{ display: "flex", gap: 8 }}>
        <ShaharTanlash qiymat={shahar} onChange={setShahar} />
        <button onClick={() => setYangilanish(y => y + 1)}>
          🔄
        </button>
      </div>

      {yukla && (
        <p style={{ textAlign: "center", marginTop: 20 }}>
          ⏳ Yuklanmoqda...
        </p>
      )}

      {xato && !yukla && (
        <div style={{ marginTop: 20, color: "red" }}>
          <p>❌ {xato}</p>
          <button onClick={() => setYangilanish(y => y + 1)}>
            Qayta urinish
          </button>
        </div>
      )}

      {data && !yukla && !xato && (
        <>
          <JoriyOb data={data} shaharNomi={SHAHARLAR[shahar].nomi} />
          <BeshKunPrognoz daily={data.daily} />
        </>
      )}
    </div>
  );
}

export default App;
"""
L7_TEXT = """\
<h2>Custom hooks — o'z hook'laringizni yozish</h2>

<pre class="mermaid">
flowchart LR
    L1["fetch + state + useEffect\n(har komponentda takror)"] -->|extract| H["useFetch — custom hook"]
    H -->|qayta ishlatish| C1["KomponentA"]
    H -->|qayta ishlatish| C2["KomponentB"]
    H -->|qayta ishlatish| C3["KomponentC"]
</pre>

<p>useEffect bilan fetch qilish — yaxshi. Lekin har komponentda <code>useState + useEffect + try/catch + AbortController</code> qaytarib yozish — yomon. <strong>Custom hook</strong> — bu mantiq'ni alohida funksiyaga ajratish va ko'p komponentda qayta ishlatish.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi custom hook (useToggle)</h4>
<pre><code>// hooks/useToggle.js
import { useState, useCallback } from 'react';

export function useToggle(initial = false) {
  const [val, setVal] = useState(initial);
  const toggle = useCallback(() =&gt; setVal(v =&gt; !v), []);
  return [val, toggle];
}

// Ishlatish:
function Komponent() {
  const [yoq, toggleYoq] = useToggle(false);
  return (
    &lt;button onClick={toggleYoq}&gt;
      {yoq ? "yoq" : "ha"}
    &lt;/button&gt;
  );
}</code></pre>

<p>2 ta qoidasi:</p>
<ol>
<li>Nomi <strong><code>use</code></strong> bilan boshlanadi (React shunda hook deb ko'radi)</li>
<li>Ichida boshqa hook'lar ishlatish mumkin (useState, useEffect, va h.k.)</li>
</ol>

<h4>BLOKA 2 — useFetch</h4>
<pre><code>// hooks/useFetch.js
export function useFetch(url) {
  const [data, setData] = useState(null);
  const [yukla, setYukla] = useState(true);
  const [xato, setXato] = useState(null);

  useEffect(() =&gt; {
    if (!url) return;
    const ctrl = new AbortController();
    setYukla(true);
    setXato(null);

    fetch(url, { signal: ctrl.signal })
      .then(r =&gt; {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(setData)
      .catch(e =&gt; {
        if (e.name !== "AbortError") setXato(e.message);
      })
      .finally(() =&gt; setYukla(false));

    return () =&gt; ctrl.abort();
  }, [url]);

  return { data, yukla, xato };
}

// Ishlatish:
function User({ id }) {
  const { data, yukla, xato } = useFetch(`/api/users/${id}`);
  if (yukla) return &lt;p&gt;Yuklanmoqda...&lt;/p&gt;;
  if (xato) return &lt;p&gt;Xato: {xato}&lt;/p&gt;;
  return &lt;h2&gt;{data.name}&lt;/h2&gt;;
}</code></pre>

<h4>BLOKA 3 — useLocalStorage</h4>
<pre><code>export function useLocalStorage(key, initial) {
  const [val, setVal] = useState(() =&gt; {
    const saved = localStorage.getItem(key);
    return saved !== null ? JSON.parse(saved) : initial;
  });

  useEffect(() =&gt; {
    localStorage.setItem(key, JSON.stringify(val));
  }, [key, val]);

  return [val, setVal];
}

// Ishlatish — useState kabi, lekin yoqilganda saqlanadi
const [tema, setTema] = useLocalStorage("tema", "yorug");</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>function Komponent({ shart }) {
  if (shart) {
    const [val, setVal] = useState(0);   // ❌
  }
  // ...
}</code></pre>

<p><strong>Natija:</strong> React xato chiqaradi: <em>"Rendered fewer hooks than expected"</em>. Hook'lar <strong>har doim bir xil tartibda</strong> chaqirilishi kerak. Sabab: React ularni "tartib raqami" bilan eslab qoladi.</p>

<p><strong>Hook qoidalari (React Rules):</strong></p>
<ol>
<li>Faqat top-level — if, for, while ichida hook chaqirmang</li>
<li>Faqat React komponentlari yoki boshqa hook'lar ichidan chaqiring</li>
<li>Nomi <code>use</code> bilan boshlanishi shart</li>
</ol>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nima uchun custom hook?</h4>
<table>
<tr><th>Sababi</th><th>Misol</th></tr>
<tr><td>DRY — kod takrorlanmasin</td><td>useFetch, useDebounce, useLocalStorage</td></tr>
<tr><td>Test qilish oson</td><td>Logic — komponentdan ajralgan</td></tr>
<tr><td>O'qish oson</td><td>Komponent kichik bo'ladi</td></tr>
<tr><td>Jamoa bilan kelishilgan interfeys</td><td>Hammada bir xil API</td></tr>
</table>

<h4>2. Kerakli pattern'lar</h4>

<table>
<tr><th>Hook</th><th>Vazifa</th></tr>
<tr><td>useToggle</td><td>boolean toggle</td></tr>
<tr><td>useCounter</td><td>+/-/reset</td></tr>
<tr><td>useFetch</td><td>API'dan ma'lumot</td></tr>
<tr><td>useLocalStorage</td><td>state + localStorage</td></tr>
<tr><td>useDebounce</td><td>kechiktirilgan qiymat</td></tr>
<tr><td>useOnClickOutside</td><td>tashqaridan bosish</td></tr>
<tr><td>usePrevious</td><td>oldingi prop/state qiymati</td></tr>
<tr><td>useMediaQuery</td><td>responsive — ekran o'lchami</td></tr>
</table>

<h4>3. useDebounce — qidiruv uchun</h4>
<pre><code>export function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);

  useEffect(() =&gt; {
    const id = setTimeout(() =&gt; setDebounced(value), delay);
    return () =&gt; clearTimeout(id);
  }, [value, delay]);

  return debounced;
}

// Qidiruv ishlatish
function Qidiruv() {
  const [matn, setMatn] = useState("");
  const debounced = useDebounce(matn, 500);

  const { data } = useFetch(
    debounced ? `/api/search?q=${debounced}` : null
  );

  return (
    &lt;&gt;
      &lt;input value={matn} onChange={e =&gt; setMatn(e.target.value)} /&gt;
      {data && &lt;ul&gt;{data.map(...)}&lt;/ul&gt;}
    &lt;/&gt;
  );
}</code></pre>

<h4>4. usePrevious</h4>
<pre><code>import { useRef, useEffect } from 'react';

export function usePrevious(value) {
  const ref = useRef();
  useEffect(() =&gt; { ref.current = value; }, [value]);
  return ref.current;
}

// Misol — qiymat o'zgarganini bilish
const oldingi = usePrevious(son);
console.log(`Oldingi: ${oldingi}, joriy: ${son}`);</code></pre>

<h4>5. useOnClickOutside (modal uchun)</h4>
<pre><code>export function useOnClickOutside(ref, handler) {
  useEffect(() =&gt; {
    const fn = (e) =&gt; {
      if (ref.current && !ref.current.contains(e.target)) handler(e);
    };
    document.addEventListener("mousedown", fn);
    return () =&gt; document.removeEventListener("mousedown", fn);
  }, [ref, handler]);
}</code></pre>

<h4>6. Mavjud kutubxonalar</h4>
<p>Production'da o'zingiz yozish o'rniga:</p>
<ul>
<li><strong>react-use</strong> — 100+ tayyor hook</li>
<li><strong>usehooks.com</strong> — copy-paste tayyor misollar</li>
<li><strong>TanStack Query</strong> — useFetch'ning professional versiyasi</li>
</ul>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Custom hook — funksiya, nomi <code>use</code> bilan</li>
<li>✅ Ichida boshqa hook'lar chaqirish mumkin</li>
<li>✅ <strong>Hook qoidalari:</strong> top-level, faqat komponent/hook ichida</li>
<li>✅ useToggle, useFetch, useLocalStorage, useDebounce — fundamental pattern'lar</li>
<li>✅ Production: react-use, TanStack Query — qayta ixtiro qilmaslik</li>
</ul>
"""

L7_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 7: Custom hooks
// ════════════════════════════════════════════════════════════════════

import { useState, useEffect, useRef, useCallback } from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) useToggle — eng oddiy custom hook
// ─────────────────────────────────────────────────────────────────────

export function useToggle(initial = false) {
  const [val, setVal] = useState(initial);
  const toggle = useCallback(() => setVal(v => !v), []);
  return [val, toggle, setVal];
}

function PaneliMisoli() {
  const [ochiq, toggleOchiq] = useToggle(false);
  return (
    <div>
      <button onClick={toggleOchiq}>
        {ochiq ? "Yopish" : "Ochish"}
      </button>
      {ochiq && <p>Panel ochildi 🎉</p>}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 2) useFetch — universal API hook
// ─────────────────────────────────────────────────────────────────────

export function useFetch(url) {
  const [data, setData] = useState(null);
  const [yukla, setYukla] = useState(false);
  const [xato, setXato] = useState(null);

  useEffect(() => {
    if (!url) return;

    const ctrl = new AbortController();
    setYukla(true);
    setXato(null);

    fetch(url, { signal: ctrl.signal })
      .then(r => {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(setData)
      .catch(e => {
        if (e.name !== "AbortError") setXato(e.message);
      })
      .finally(() => {
        if (!ctrl.signal.aborted) setYukla(false);
      });

    return () => ctrl.abort();
  }, [url]);

  return { data, yukla, xato };
}

function FoydalanuvchiKarti({ id }) {
  const { data, yukla, xato } = useFetch(
    `https://jsonplaceholder.typicode.com/users/${id}`
  );

  if (yukla) return <p>Yuklanmoqda...</p>;
  if (xato) return <p>Xato: {xato}</p>;
  if (!data) return null;

  return (
    <div>
      <h2>{data.name}</h2>
      <p>{data.email}</p>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) useLocalStorage
// ─────────────────────────────────────────────────────────────────────

export function useLocalStorage(key, initial) {
  const [val, setVal] = useState(() => {
    try {
      const saved = localStorage.getItem(key);
      return saved !== null ? JSON.parse(saved) : initial;
    } catch {
      return initial;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(val));
    } catch {
      // saqlash xato (quota, ssr)
    }
  }, [key, val]);

  return [val, setVal];
}

function TemaToggler() {
  const [tema, setTema] = useLocalStorage("tema", "yorug");
  return (
    <button onClick={() => setTema(tema === "yorug" ? "qorongi" : "yorug")}>
      Tema: {tema}
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 4) useDebounce — qidiruv uchun
// ─────────────────────────────────────────────────────────────────────

export function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);

  return debounced;
}

function Qidiruv() {
  const [matn, setMatn] = useState("");
  const debounced = useDebounce(matn, 500);

  const { data, yukla } = useFetch(
    debounced
      ? `https://jsonplaceholder.typicode.com/users?q=${debounced}`
      : null
  );

  return (
    <div>
      <input
        value={matn}
        onChange={(e) => setMatn(e.target.value)}
        placeholder="Qidir..."
      />
      <small>Real: "{matn}", debounced: "{debounced}"</small>
      {yukla && <p>...</p>}
      {data && (
        <ul>{data.slice(0, 5).map(u => <li key={u.id}>{u.name}</li>)}</ul>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 5) usePrevious
// ─────────────────────────────────────────────────────────────────────

export function usePrevious(value) {
  const ref = useRef();
  useEffect(() => { ref.current = value; }, [value]);
  return ref.current;
}

function HisoblaganVaqolda() {
  const [son, setSon] = useState(0);
  const oldingi = usePrevious(son);

  return (
    <div>
      <p>Joriy: {son}, oldingi: {oldingi ?? "—"}</p>
      <button onClick={() => setSon(s => s + 1)}>+1</button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 6) useOnClickOutside — modal/dropdown uchun
// ─────────────────────────────────────────────────────────────────────

export function useOnClickOutside(ref, handler) {
  useEffect(() => {
    const fn = (e) => {
      if (ref.current && !ref.current.contains(e.target)) handler(e);
    };
    document.addEventListener("mousedown", fn);
    document.addEventListener("touchstart", fn);
    return () => {
      document.removeEventListener("mousedown", fn);
      document.removeEventListener("touchstart", fn);
    };
  }, [ref, handler]);
}

function Modal() {
  const [ochiq, setOchiq] = useState(false);
  const ref = useRef();

  useOnClickOutside(ref, () => setOchiq(false));

  return (
    <div>
      <button onClick={() => setOchiq(true)}>Modal ochish</button>
      {ochiq && (
        <div ref={ref} style={{
          padding: 24, border: "2px solid", margin: 16,
        }}>
          <h3>Modal!</h3>
          <p>Tashqarisini bosing yopish uchun</p>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 7) useMediaQuery — responsive
// ─────────────────────────────────────────────────────────────────────

export function useMediaQuery(query) {
  const [matches, setMatches] = useState(() => window.matchMedia(query).matches);

  useEffect(() => {
    const m = window.matchMedia(query);
    const handler = (e) => setMatches(e.matches);
    m.addEventListener("change", handler);
    return () => m.removeEventListener("change", handler);
  }, [query]);

  return matches;
}

function Responsive() {
  const mobile = useMediaQuery("(max-width: 768px)");
  return <p>Sizning ekraningiz: {mobile ? "📱 mobil" : "🖥️ desktop"}</p>;
}

// ─────────────────────────────────────────────────────────────────────
// ❌ Hook qoidalarini buzish
// ─────────────────────────────────────────────────────────────────────

/*
function Xato({ shart }) {
  if (shart) {
    const [v, setV] = useState(0);   // ❌ "Rendered fewer hooks"
  }
  for (let i = 0; i < 5; i++) {
    useEffect(() => {});            // ❌ aynan shu xato
  }
}
*/
"""
L8_TEXT = """\
<h2>React Router — sahifa navigatsiyasi</h2>

<pre class="mermaid">
flowchart LR
    URL["/"] --> R{"Router"}
    URL2["/kurslar"] --> R
    URL3["/kurslar/:id"] --> R
    R --> P1["Bosh"]
    R --> P2["KurslarRoyxati"]
    R --> P3["KursTafsiloti"]
</pre>

<p>Hozirgacha bir komponentdan boshqasiga state bilan o'tdik. Lekin real ilovada — sahifalar (URL). <code>/</code>, <code>/kurslar</code>, <code>/kurslar/42</code>, <code>/profil</code>. <strong>React Router</strong> — eng mashhur kutubxona buning uchun.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — o'rnatish va asosiy routing</h4>
<pre><code># Terminal
npm install react-router-dom</code></pre>

<pre><code>// main.jsx
import { BrowserRouter } from 'react-router-dom';

ReactDOM.createRoot(document.getElementById('root')).render(
  &lt;BrowserRouter&gt;
    &lt;App /&gt;
  &lt;/BrowserRouter&gt;
);</code></pre>

<pre><code>// App.jsx
import { Routes, Route, Link } from 'react-router-dom';

function Bosh()     { return &lt;h1&gt;🏠 Bosh&lt;/h1&gt;; }
function Kurslar()  { return &lt;h1&gt;📚 Kurslar&lt;/h1&gt;; }
function Profil()   { return &lt;h1&gt;👤 Profil&lt;/h1&gt;; }

function App() {
  return (
    &lt;div&gt;
      &lt;nav&gt;
        &lt;Link to="/"&gt;Bosh&lt;/Link&gt;{' | '}
        &lt;Link to="/kurslar"&gt;Kurslar&lt;/Link&gt;{' | '}
        &lt;Link to="/profil"&gt;Profil&lt;/Link&gt;
      &lt;/nav&gt;

      &lt;Routes&gt;
        &lt;Route path="/"        element={&lt;Bosh /&gt;} /&gt;
        &lt;Route path="/kurslar" element={&lt;Kurslar /&gt;} /&gt;
        &lt;Route path="/profil"  element={&lt;Profil /&gt;} /&gt;
      &lt;/Routes&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p>3 ta sahifa, mukammal ishlovchi navigatsiya. Sahifa qayta yuklanmaydi (SPA — single page app).</p>

<h4>BLOKA 2 — dinamik parametrlar</h4>
<pre><code>import { useParams } from 'react-router-dom';

function KursTafsiloti() {
  const { id } = useParams();
  // URL: /kurslar/42  → id = "42"
  return &lt;h2&gt;Kurs #{id}&lt;/h2&gt;;
}

&lt;Route path="/kurslar/:id" element={&lt;KursTafsiloti /&gt;} /&gt;</code></pre>

<h4>BLOKA 3 — programmatic navigation</h4>
<pre><code>import { useNavigate } from 'react-router-dom';

function LoginForma() {
  const navigate = useNavigate();

  const yuborish = async () =&gt; {
    await login();
    navigate("/profil");          // sahifaga o'tish
    // navigate(-1);               // orqaga
    // navigate("/", { replace: true });  // tarix saqlanmaydi
  };

  return &lt;button onClick={yuborish}&gt;Kirish&lt;/button&gt;;
}</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>&lt;a href="/kurslar"&gt;Kurslar&lt;/a&gt;</code></pre>

<p><strong>Sabab:</strong> Bu — oddiy HTML link. Sahifa <strong>to'liq qayta yuklanadi</strong>, React state yo'qoladi, SPA effekti yo'qoladi. To'g'risi — har doim <code>&lt;Link to="..."&gt;</code> ishlatish.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. React Router'ning asosiy hook'lari</h4>
<table>
<tr><th>Hook</th><th>Vazifa</th></tr>
<tr><td><code>useNavigate()</code></td><td>Programmatic ko'chish (login keyin)</td></tr>
<tr><td><code>useParams()</code></td><td>URL parametrlari (<code>/kurslar/:id</code>)</td></tr>
<tr><td><code>useSearchParams()</code></td><td>Query string (?qidir=react)</td></tr>
<tr><td><code>useLocation()</code></td><td>Joriy URL ma'lumoti</td></tr>
</table>

<h4>2. Search params (?qidir=react&amp;sahifa=2)</h4>
<pre><code>import { useSearchParams } from 'react-router-dom';

function Qidiruv() {
  const [params, setParams] = useSearchParams();
  const qidir = params.get("qidir") ?? "";
  const sahifa = Number(params.get("sahifa") ?? 1);

  const update = (key, val) =&gt; {
    const next = new URLSearchParams(params);
    next.set(key, val);
    setParams(next);
  };

  return (
    &lt;&gt;
      &lt;input
        value={qidir}
        onChange={e =&gt; update("qidir", e.target.value)}
      /&gt;
      &lt;button onClick={() =&gt; update("sahifa", sahifa + 1)}&gt;
        Keyingi
      &lt;/button&gt;
    &lt;/&gt;
  );
}</code></pre>

<h4>3. Nested routes va Outlet</h4>
<pre><code>import { Outlet } from 'react-router-dom';

function KurslarLayout() {
  return (
    &lt;div&gt;
      &lt;aside&gt;Sidebar&lt;/aside&gt;
      &lt;main&gt;
        &lt;Outlet /&gt;  {/* child route bu yerga keladi */}
      &lt;/main&gt;
    &lt;/div&gt;
  );
}

&lt;Routes&gt;
  &lt;Route path="/kurslar" element={&lt;KurslarLayout /&gt;}&gt;
    &lt;Route index             element={&lt;Royxat /&gt;} /&gt;
    &lt;Route path=":id"        element={&lt;Tafsilot /&gt;} /&gt;
    &lt;Route path=":id/dars/:dars" element={&lt;Dars /&gt;} /&gt;
  &lt;/Route&gt;
&lt;/Routes&gt;</code></pre>

<h4>4. 404 page</h4>
<pre><code>&lt;Routes&gt;
  &lt;Route path="/" element={&lt;Bosh /&gt;} /&gt;
  &lt;Route path="*" element={&lt;NotFound /&gt;} /&gt;   {/* yakuniy */}
&lt;/Routes&gt;</code></pre>

<h4>5. NavLink — faol sahifa stili</h4>
<pre><code>import { NavLink } from 'react-router-dom';

&lt;NavLink
  to="/kurslar"
  className={({ isActive }) =&gt; isActive ? "active" : ""}
&gt;
  Kurslar
&lt;/NavLink&gt;</code></pre>

<h4>6. Protected routes (auth bilan)</h4>
<pre><code>function Protected({ children }) {
  const { user } = useAuth();
  if (!user) return &lt;Navigate to="/login" replace /&gt;;
  return children;
}

&lt;Route
  path="/profil"
  element={
    &lt;Protected&gt;
      &lt;Profil /&gt;
    &lt;/Protected&gt;
  }
/&gt;</code></pre>

<p>(<code>useAuth</code> — 9-darsda yaratamiz, Context bilan)</p>

<h4>7. URL qoidalari</h4>
<ul>
<li>Statik: <code>/kurslar</code>, <code>/profil</code></li>
<li>Parametr: <code>/kurslar/:id</code> → <code>useParams</code></li>
<li>Query: <code>?qidir=react</code> → <code>useSearchParams</code></li>
<li>Yakuniy: <code>*</code> (NotFound)</li>
</ul>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>BrowserRouter</code> wrap, <code>Routes</code> + <code>Route</code> mapping</li>
<li>✅ <code>&lt;Link to="..."&gt;</code> har doim, <code>&lt;a href&gt;</code> emas</li>
<li>✅ <code>useParams</code> — URL parametrlari</li>
<li>✅ <code>useSearchParams</code> — query string</li>
<li>✅ <code>useNavigate</code> — programmatic ko'chish</li>
<li>✅ Nested routes + <code>Outlet</code></li>
<li>✅ <code>path="*"</code> — 404</li>
<li>✅ NavLink — faol sahifa belgisi</li>
</ul>
"""

L8_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 8: React Router
// ════════════════════════════════════════════════════════════════════
//
// O'rnatish:
//   npm install react-router-dom
//
// main.jsx:
//   import { BrowserRouter } from 'react-router-dom';
//   ReactDOM.createRoot(...).render(
//     <BrowserRouter><App /></BrowserRouter>
//   );
// ════════════════════════════════════════════════════════════════════

import {
  Routes, Route, Link, NavLink, Outlet,
  useParams, useNavigate, useSearchParams, useLocation, Navigate,
} from 'react-router-dom';

// ─────────────────────────────────────────────────────────────────────
// 1) Sahifalar
// ─────────────────────────────────────────────────────────────────────

function Bosh() {
  return (
    <div>
      <h1>🏠 Bosh sahifa</h1>
      <p>Bizning saytga xush kelibsiz!</p>
    </div>
  );
}

function NotFound() {
  return (
    <div>
      <h1>🚫 404 — sahifa topilmadi</h1>
      <Link to="/">Bosh sahifaga qaytish</Link>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 2) KurslarLayout — nested route uchun (Outlet bilan)
// ─────────────────────────────────────────────────────────────────────

function KurslarLayout() {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "200px 1fr", gap: 20 }}>
      <aside style={{ borderRight: "1px solid", padding: 12 }}>
        <h3>Kurslar</h3>
        <nav style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          <NavLink to="/kurslar">📋 Ro'yxat</NavLink>
          <NavLink to="/kurslar/1">Python</NavLink>
          <NavLink to="/kurslar/2">React</NavLink>
        </nav>
      </aside>

      <main>
        <Outlet />
      </main>
    </div>
  );
}

function KurslarRoyxati() {
  const kurslar = [
    { id: 1, nomi: "Python Asoslari" },
    { id: 2, nomi: "React Asoslari" },
    { id: 3, nomi: "SQL va PostgreSQL" },
  ];

  return (
    <ul>
      {kurslar.map(k => (
        <li key={k.id}>
          <Link to={`/kurslar/${k.id}`}>{k.nomi}</Link>
        </li>
      ))}
    </ul>
  );
}

function KursTafsiloti() {
  const { id } = useParams();
  const navigate = useNavigate();

  return (
    <div>
      <h2>Kurs #{id}</h2>
      <p>Bu kurs haqida tafsilot...</p>
      <button onClick={() => navigate(-1)}>← Orqaga</button>
      <button onClick={() => navigate("/kurslar")}>Ro'yxatga</button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) Qidiruv — useSearchParams
// ─────────────────────────────────────────────────────────────────────

function Qidiruv() {
  const [params, setParams] = useSearchParams();
  const qidir = params.get("q") ?? "";
  const sahifa = Number(params.get("p") ?? 1);

  const update = (key, val) => {
    const next = new URLSearchParams(params);
    if (val === "" || val === null) next.delete(key);
    else next.set(key, val);
    setParams(next);
  };

  return (
    <div>
      <h2>🔍 Qidiruv</h2>
      <input
        value={qidir}
        onChange={(e) => update("q", e.target.value)}
        placeholder="Nimani qidiramiz?"
      />
      <p>Qidir: "{qidir}", sahifa: {sahifa}</p>

      <button onClick={() => update("p", sahifa - 1)} disabled={sahifa <= 1}>
        ← Oldingi
      </button>
      <button onClick={() => update("p", sahifa + 1)}>
        Keyingi →
      </button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 4) Login + programmatic navigation
// ─────────────────────────────────────────────────────────────────────

function Login() {
  const navigate = useNavigate();
  const location = useLocation();

  const yuborish = async (e) => {
    e.preventDefault();
    // ... fake login
    await new Promise(r => setTimeout(r, 500));

    // Kelgan joyga qaytish (yoki bosh sahifaga)
    const dan = location.state?.dan ?? "/";
    navigate(dan, { replace: true });
  };

  return (
    <form onSubmit={yuborish}>
      <h2>🔐 Kirish</h2>
      <input placeholder="Email" required />
      <input type="password" placeholder="Parol" required />
      <button type="submit">Kirish</button>
    </form>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 5) Protected route
// ─────────────────────────────────────────────────────────────────────

function useAuth() {
  // Soxta auth — 9-darsda Context bilan to'g'ri yozamiz
  const tizimda = localStorage.getItem("tizimda") === "ha";
  return { tizimda };
}

function Protected({ children }) {
  const { tizimda } = useAuth();
  const location = useLocation();

  if (!tizimda) {
    return <Navigate to="/login" state={{ dan: location.pathname }} replace />;
  }
  return children;
}

function Profil() {
  return <h2>👤 Profil — faqat tizimga kirganlar uchun</h2>;
}

// ─────────────────────────────────────────────────────────────────────
// 6) Asosiy App — barcha sahifalarni bog'laydi
// ─────────────────────────────────────────────────────────────────────

function NavBar() {
  const navStyle = ({ isActive }) => ({
    padding: "8px 12px",
    textDecoration: "none",
    color: isActive ? "white" : "black",
    background: isActive ? "#222" : "transparent",
    borderRadius: 4,
  });

  return (
    <nav style={{ display: "flex", gap: 8, padding: 12, borderBottom: "1px solid" }}>
      <NavLink to="/"        style={navStyle} end>Bosh</NavLink>
      <NavLink to="/kurslar" style={navStyle}>Kurslar</NavLink>
      <NavLink to="/qidiruv" style={navStyle}>Qidiruv</NavLink>
      <NavLink to="/profil"  style={navStyle}>Profil</NavLink>
      <NavLink to="/login"   style={navStyle}>Login</NavLink>
    </nav>
  );
}

function App() {
  return (
    <div>
      <NavBar />

      <main style={{ padding: 20 }}>
        <Routes>
          <Route path="/"          element={<Bosh />} />
          <Route path="/qidiruv"   element={<Qidiruv />} />
          <Route path="/login"     element={<Login />} />

          {/* Nested routes */}
          <Route path="/kurslar" element={<KurslarLayout />}>
            <Route index           element={<KurslarRoyxati />} />
            <Route path=":id"      element={<KursTafsiloti />} />
          </Route>

          {/* Protected */}
          <Route
            path="/profil"
            element={
              <Protected>
                <Profil />
              </Protected>
            }
          />

          {/* 404 — eng oxirida */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
"""
L9_TEXT = """\
<h2>Context API — global state</h2>

<pre class="mermaid">
flowchart TB
    P["Provider value={user}"] -.->|context| C1["A → B → C → User"]
    P -.->|context| C2["X → Y → Z → User"]
    NOTE["Prop drilling YO'Q\nbevosita useContext"] --> C1
</pre>

<p>Tasavvur qiling: <code>user</code> obyekti App ichida. Header'da kerak, Profile'da kerak, Comment'da kerak. Har komponentga props orqali yuborish — 5 darajadan o'tib ketsa, <strong>prop drilling</strong> deyiladi. Yomon. Yechim — <strong>Context</strong>.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Context yaratish</h4>
<pre><code>// contexts/UserContext.js
import { createContext, useContext, useState } from 'react';

const UserContext = createContext(null);

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);

  const login = (ism) =&gt; setUser({ ism, vaqt: new Date() });
  const logout = () =&gt; setUser(null);

  return (
    &lt;UserContext.Provider value={{ user, login, logout }}&gt;
      {children}
    &lt;/UserContext.Provider&gt;
  );
}

export function useUser() {
  return useContext(UserContext);
}</code></pre>

<h4>BLOKA 2 — Provider'ni o'rnatish</h4>
<pre><code>// main.jsx (yoki App.jsx eng yuqorisida)
import { UserProvider } from './contexts/UserContext';

ReactDOM.createRoot(document.getElementById('root')).render(
  &lt;UserProvider&gt;
    &lt;App /&gt;
  &lt;/UserProvider&gt;
);</code></pre>

<h4>BLOKA 3 — har joydan ishlatish</h4>
<pre><code>function Header() {
  const { user, logout } = useUser();   // bevosita
  return (
    &lt;header&gt;
      {user ? (
        &lt;&gt;
          &lt;span&gt;Salom, {user.ism}!&lt;/span&gt;
          &lt;button onClick={logout}&gt;Chiqish&lt;/button&gt;
        &lt;/&gt;
      ) : (
        &lt;Link to="/login"&gt;Kirish&lt;/Link&gt;
      )}
    &lt;/header&gt;
  );
}

function LoginForma() {
  const { login } = useUser();
  return &lt;button onClick={() =&gt; login("Olim")}&gt;Kirish&lt;/button&gt;;
}</code></pre>

<p>Header va LoginForma — <strong>props yo'q</strong>. Bevosita user'ga kirish. Bu — Context'ning sehri.</p>

<h3>🐛 Ataylab xato</h3>
<pre><code>function Komponent() {
  const user = useUser();   // null bo'lsa?
  return &lt;p&gt;{user.ism}&lt;/p&gt;;   // ❌ TypeError: cannot read property
}</code></pre>

<p><strong>Sabab:</strong> Provider bilan o'ralmagan komponent'da <code>useContext</code> <code>null</code> (yoki default qiymat) qaytaradi. Yechim — Provider o'rnatish yoki custom hook'da xato berib qo'yish:</p>

<pre><code>export function useUser() {
  const ctx = useContext(UserContext);
  if (!ctx) {
    throw new Error("useUser faqat UserProvider ichida ishlaydi");
  }
  return ctx;
}</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. Context qachon kerak?</h4>
<table>
<tr><th>Ishlatish</th><th>Misol</th></tr>
<tr><td>✅ User auth</td><td>tizimga kirgan foydalanuvchi</td></tr>
<tr><td>✅ Tema (yorug'/qorong'i)</td><td>UI sozlamalari</td></tr>
<tr><td>✅ Til (i18n)</td><td>tarjima funksiyasi</td></tr>
<tr><td>✅ Cart (xarid savatchasi)</td><td>e-commerce</td></tr>
<tr><td>❌ Har state</td><td>oddiy props yetadi</td></tr>
<tr><td>❌ Server state</td><td>TanStack Query yaxshiroq</td></tr>
</table>

<h4>2. Provider — qaerga qo'yish?</h4>
<p>Eng yuqori darajaga — main.jsx yoki App.jsx eng yuqorisida. Bir nechta Provider'ni nest qilish mumkin:</p>

<pre><code>&lt;UserProvider&gt;
  &lt;ThemeProvider&gt;
    &lt;CartProvider&gt;
      &lt;App /&gt;
    &lt;/CartProvider&gt;
  &lt;/ThemeProvider&gt;
&lt;/UserProvider&gt;</code></pre>

<h4>3. Provider value performance</h4>
<pre><code>// ❌ Yomon — har render'da yangi obyekt
&lt;UserContext.Provider value={{ user, setUser }}&gt;

// ✅ Yaxshi — useMemo bilan barqaror
const value = useMemo(() =&gt; ({ user, setUser }), [user]);
&lt;UserContext.Provider value={value}&gt;</code></pre>

<p>Sabab: har render'da yangi obyekt bo'lsa, har consumer ham qayta render bo'ladi — keraksiz.</p>

<h4>4. Context'ni bo'lib yuborish</h4>
<p>Bir Provider ichida ko'p ma'lumot bo'lsa — bo'lib yuboring. Har consumer faqat o'ziga keraklisini olsin:</p>

<pre><code>// O'rniga — bitta katta UserContext
&lt;UserDataContext.Provider value={user}&gt;
  &lt;UserActionsContext.Provider value={{ login, logout }}&gt;
    {children}
  &lt;/UserActionsContext.Provider&gt;
&lt;/UserDataContext.Provider&gt;</code></pre>

<h4>5. ThemeContext to'liq misol</h4>
<pre><code>const ThemeContext = createContext("yorug");

export function ThemeProvider({ children }) {
  const [tema, setTema] = useLocalStorage("tema", "yorug");

  useEffect(() =&gt; {
    document.body.dataset.tema = tema;
  }, [tema]);

  return (
    &lt;ThemeContext.Provider value={{ tema, setTema }}&gt;
      {children}
    &lt;/ThemeContext.Provider&gt;
  );
}

export const useTheme = () =&gt; useContext(ThemeContext);</code></pre>

<h4>6. Context vs Zustand / Redux</h4>
<p>Context — built-in, kichik state uchun. Lekin kattaroq app'lar:</p>
<ul>
<li><strong>Zustand</strong> — minimal global state, oddiy</li>
<li><strong>Redux Toolkit</strong> — enterprise, devtools</li>
<li><strong>Jotai</strong> — atom-based</li>
<li><strong>TanStack Query</strong> — server state (API ma'lumotlari) uchun</li>
</ul>

<p>Default — Context. Kerak bo'lsa — boshqasi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>createContext</code> + <code>Provider</code> + <code>useContext</code></li>
<li>✅ Custom <code>useUser/useTheme</code> hook'lari — qulayroq API</li>
<li>✅ Provider value — useMemo bilan barqaror</li>
<li>✅ Prop drilling oldini olish — global state</li>
<li>✅ Context vs prop drilling — qachon haqiqatan kerak</li>
<li>✅ Server state — Context emas, TanStack Query</li>
</ul>
"""

L9_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 9: Context API
// ════════════════════════════════════════════════════════════════════

import {
  createContext, useContext, useState, useEffect, useMemo
} from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) UserContext — auth misoli
// ─────────────────────────────────────────────────────────────────────

const UserContext = createContext(null);

export function UserProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem("user");
      return saved ? JSON.parse(saved) : null;
    } catch { return null; }
  });

  useEffect(() => {
    if (user) localStorage.setItem("user", JSON.stringify(user));
    else      localStorage.removeItem("user");
  }, [user]);

  const login = (ism, email) => {
    setUser({ ism, email, kirgan: new Date().toISOString() });
  };
  const logout = () => setUser(null);

  // ✅ useMemo bilan barqaror obyekt
  const value = useMemo(
    () => ({ user, login, logout }),
    [user]
  );

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const ctx = useContext(UserContext);
  if (!ctx) {
    throw new Error("useUser faqat UserProvider ichida ishlaydi");
  }
  return ctx;
}

// ─────────────────────────────────────────────────────────────────────
// 2) ThemeContext
// ─────────────────────────────────────────────────────────────────────

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [tema, setTema] = useState(() => {
    return localStorage.getItem("tema") ?? "yorug";
  });

  useEffect(() => {
    localStorage.setItem("tema", tema);
    document.body.style.background = tema === "qorongi" ? "#222" : "#fff";
    document.body.style.color = tema === "qorongi" ? "#fff" : "#000";
  }, [tema]);

  const value = useMemo(() => ({
    tema,
    setTema,
    toggle: () => setTema(t => t === "yorug" ? "qorongi" : "yorug"),
  }), [tema]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme faqat ThemeProvider ichida");
  return ctx;
};

// ─────────────────────────────────────────────────────────────────────
// 3) CartContext — e-commerce misoli
// ─────────────────────────────────────────────────────────────────────

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [items, setItems] = useState([]);

  const qoshish = (mahsulot) => {
    setItems(prev => {
      const mavjud = prev.find(i => i.id === mahsulot.id);
      if (mavjud) {
        return prev.map(i =>
          i.id === mahsulot.id ? { ...i, miqdor: i.miqdor + 1 } : i
        );
      }
      return [...prev, { ...mahsulot, miqdor: 1 }];
    });
  };

  const ochirish = (id) => setItems(prev => prev.filter(i => i.id !== id));

  const tozalash = () => setItems([]);

  const jami = items.reduce((s, i) => s + i.narx * i.miqdor, 0);
  const soni = items.reduce((s, i) => s + i.miqdor, 0);

  const value = useMemo(() => ({
    items, qoshish, ochirish, tozalash, jami, soni,
  }), [items, jami, soni]);

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart faqat CartProvider ichida");
  return ctx;
};

// ─────────────────────────────────────────────────────────────────────
// 4) Komponentlar — props yo'q, bevosita context
// ─────────────────────────────────────────────────────────────────────

function Header() {
  const { user, logout } = useUser();
  const { tema, toggle } = useTheme();
  const { soni } = useCart();

  return (
    <header style={{ display: "flex", gap: 16, padding: 12, borderBottom: "1px solid" }}>
      <h1 style={{ flex: 1 }}>Saytim</h1>

      <button onClick={toggle}>
        {tema === "yorug" ? "🌙" : "☀️"}
      </button>

      <span>🛒 {soni}</span>

      {user ? (
        <>
          <span>Salom, {user.ism}!</span>
          <button onClick={logout}>Chiqish</button>
        </>
      ) : (
        <button>Kirish</button>
      )}
    </header>
  );
}

function LoginForma() {
  const { user, login } = useUser();
  const [ism, setIsm] = useState("");

  if (user) return null;

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      if (ism) login(ism, `${ism.toLowerCase()}@uz`);
    }}>
      <input value={ism} onChange={(e) => setIsm(e.target.value)} />
      <button type="submit">Kirish</button>
    </form>
  );
}

function MahsulotKarti({ mahsulot }) {
  const { qoshish } = useCart();
  return (
    <div style={{ border: "1px solid", padding: 12 }}>
      <h3>{mahsulot.nomi}</h3>
      <p>{mahsulot.narx.toLocaleString()} so'm</p>
      <button onClick={() => qoshish(mahsulot)}>Savatga</button>
    </div>
  );
}

function SavatKorinishi() {
  const { items, ochirish, tozalash, jami } = useCart();

  if (items.length === 0) return <p>Savat bo'sh</p>;

  return (
    <div>
      <h2>Savatcha</h2>
      <ul>
        {items.map(i => (
          <li key={i.id}>
            {i.nomi} × {i.miqdor} — {(i.narx * i.miqdor).toLocaleString()}
            <button onClick={() => ochirish(i.id)}>x</button>
          </li>
        ))}
      </ul>
      <p>Jami: <b>{jami.toLocaleString()} so'm</b></p>
      <button onClick={tozalash}>Tozalash</button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 5) App — barcha Provider'lar bilan
// ─────────────────────────────────────────────────────────────────────

function App() {
  return (
    <UserProvider>
      <ThemeProvider>
        <CartProvider>
          <Header />

          <main style={{ padding: 20 }}>
            <LoginForma />

            <h2>Mahsulotlar</h2>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
              <MahsulotKarti mahsulot={{ id: 1, nomi: "iPhone", narx: 15000000 }} />
              <MahsulotKarti mahsulot={{ id: 2, nomi: "MacBook", narx: 22000000 }} />
              <MahsulotKarti mahsulot={{ id: 3, nomi: "AirPods", narx:  2500000 }} />
            </div>

            <SavatKorinishi />
          </main>
        </CartProvider>
      </ThemeProvider>
    </UserProvider>
  );
}

export default App;
"""
R3_TEXT = """\
<h2>R3 — Modul 3 takrorlash: Auth flow + protected routes</h2>

<p>Modul 3 ning hammasi birga: <strong>custom hooks</strong> (useFetch, useLocalStorage), <strong>Context</strong> (AuthContext), <strong>Router</strong> (login, protected). Real ilovalarda har kuni ishlatadigan pattern: foydalanuvchi kirishi va private sahifalar.</p>

<h3>Loyihaning maqsadi</h3>

<p>Yetkazib berishingiz kerak:</p>
<ul>
<li>Login sahifa (form bilan)</li>
<li>Public sahifalar: Bosh, Kurslar</li>
<li>Private sahifalar: Profil, Sozlamalar (faqat tizimga kirgan foydalanuvchilar uchun)</li>
<li>Header: agar kirgan bo'lsa — ism + chiqish; agar yo'q bo'lsa — kirish</li>
<li>localStorage'da saqlash — sahifa qayta yuklansa ham tizimda qoladi</li>
<li>Protected route'ga kirishga urinish → login + qaytib o'sha sahifaga</li>
</ul>

<h3>Tuzilma</h3>

<pre><code>src/
├── contexts/AuthContext.jsx    ← AuthProvider, useAuth
├── hooks/useLocalStorage.js    ← qayta ishlatish
├── components/
│   ├── Header.jsx              ← user + logout
│   ├── Protected.jsx           ← redirect to /login
│   └── LoginForma.jsx
├── pages/
│   ├── Bosh.jsx
│   ├── Kurslar.jsx
│   ├── Profil.jsx              ← private
│   ├── Sozlamalar.jsx          ← private
│   └── Login.jsx
└── App.jsx</code></pre>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — useLocalStorage hook</h4>
<p>7-darsdan eslang. Generic, har turli qiymat saqlasin (string, object).</p>

<h4>Vazifa 2 — AuthContext</h4>
<ul>
<li><code>user</code> state (null yoki <code>{ ism, email }</code>)</li>
<li><code>login(email, parol)</code> — soxta validatsiya (har qanday email + 8+ harfli parol qabul qilsin)</li>
<li><code>logout()</code> — null</li>
<li><strong>useLocalStorage</strong> bilan saqlash</li>
<li><code>useAuth()</code> custom hook</li>
</ul>

<h4>Vazifa 3 — Protected wrapper</h4>
<p>Login bo'lmasa <code>/login</code> ga redirect. <strong>state bilan</strong> kelgan sahifani saqlash — login keyin shu yerga qaytish.</p>

<h4>Vazifa 4 — Routes</h4>
<p>Public va Private sahifalar to'g'ri bog'langan bo'lsin. 404 ham bo'lsin.</p>

<h4>Vazifa 5 — UX</h4>
<ul>
<li>Login loading state (button "Yuklanmoqda...")</li>
<li>Xato xabari</li>
<li>Header'da real-time user holati</li>
</ul>

<h3>🐛 Ataylab qiyin: race condition</h3>
<p>Foydalanuvchi login tugmasini 2 marta tez bossa, 2 ta async login ishga tushadi. Yechim: <code>yubormoq</code> state bilan tugmani disable qilish va/yoki AbortController.</p>

<h3>Yechim sketch</h3>

<details>
<summary>To'liq yechim — avval o'zingiz urinib ko'ring!</summary>
<pre><code>// contexts/AuthContext.jsx
import { createContext, useContext, useState, useMemo, useEffect } from 'react';
import { useLocalStorage } from '../hooks/useLocalStorage';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useLocalStorage("user", null);

  const login = async (email, parol) =&gt; {
    // Soxta server
    await new Promise(r =&gt; setTimeout(r, 800));
    if (!email.includes("@")) throw new Error("Email noto'g'ri");
    if (parol.length &lt; 8) throw new Error("Parol 8+ belgi");

    setUser({
      ism: email.split("@")[0],
      email,
      kirgan: new Date().toISOString(),
    });
  };

  const logout = () =&gt; setUser(null);

  const value = useMemo(() =&gt; ({ user, login, logout }), [user]);

  return &lt;AuthContext.Provider value={value}&gt;{children}&lt;/AuthContext.Provider&gt;;
}

export const useAuth = () =&gt; {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth faqat AuthProvider ichida");
  return ctx;
};


// components/Protected.jsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export function Protected({ children }) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return &lt;Navigate to="/login" state={{ dan: location.pathname }} replace /&gt;;
  }
  return children;
}


// pages/Login.jsx
import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [parol, setParol] = useState("");
  const [yubormoq, setYubormoq] = useState(false);
  const [xato, setXato] = useState(null);

  const onSubmit = async (e) =&gt; {
    e.preventDefault();
    setYubormoq(true);
    setXato(null);
    try {
      await login(email, parol);
      navigate(location.state?.dan ?? "/profil", { replace: true });
    } catch (e) {
      setXato(e.message);
    } finally {
      setYubormoq(false);
    }
  };

  return (
    &lt;form onSubmit={onSubmit}&gt;
      &lt;h2&gt;Kirish&lt;/h2&gt;
      &lt;input value={email} onChange={(e)=&gt;setEmail(e.target.value)} placeholder="email" required /&gt;
      &lt;input type="password" value={parol} onChange={(e)=&gt;setParol(e.target.value)} placeholder="parol" required /&gt;
      {xato && &lt;p style={{color:'red'}}&gt;{xato}&lt;/p&gt;}
      &lt;button type="submit" disabled={yubormoq}&gt;
        {yubormoq ? "Yuklanmoqda..." : "Kirish"}
      &lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Modul 3 ning hammasi birga: custom hooks + Context + Router</li>
<li>✅ Auth flow — real production pattern</li>
<li>✅ Protected route + return-to-original sahifa</li>
<li>✅ localStorage bilan persistensiya</li>
<li>✅ UX: loading, error, disable patterns</li>
</ul>
"""

R3_CODE = """\
// ════════════════════════════════════════════════════════════════════
// REVISION 3: Auth flow + protected routes
// Modul 3: custom hooks + Context + Router birga
// ════════════════════════════════════════════════════════════════════

import {
  createContext, useContext, useState, useMemo, useEffect, useCallback
} from 'react';
import {
  BrowserRouter, Routes, Route, Link, NavLink, Navigate,
  useNavigate, useLocation,
} from 'react-router-dom';

// ─────────────────────────────────────────────────────────────────────
// 1) hooks/useLocalStorage.js
// ─────────────────────────────────────────────────────────────────────

function useLocalStorage(key, initial) {
  const [val, setVal] = useState(() => {
    try {
      const saved = localStorage.getItem(key);
      return saved !== null ? JSON.parse(saved) : initial;
    } catch {
      return initial;
    }
  });

  useEffect(() => {
    try {
      if (val === null || val === undefined) localStorage.removeItem(key);
      else localStorage.setItem(key, JSON.stringify(val));
    } catch {}
  }, [key, val]);

  return [val, setVal];
}

// ─────────────────────────────────────────────────────────────────────
// 2) contexts/AuthContext.jsx
// ─────────────────────────────────────────────────────────────────────

const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useLocalStorage("user", null);

  const login = useCallback(async (email, parol) => {
    // Soxta API — 800ms kechikish
    await new Promise(r => setTimeout(r, 800));

    if (!email.includes("@")) throw new Error("Email noto'g'ri");
    if (parol.length < 8)     throw new Error("Parol 8+ belgi bo'lishi kerak");

    setUser({
      ism: email.split("@")[0],
      email,
      kirgan: new Date().toISOString(),
    });
  }, [setUser]);

  const logout = useCallback(() => setUser(null), [setUser]);

  const value = useMemo(
    () => ({ user, login, logout }),
    [user, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth faqat AuthProvider ichida ishlaydi");
  return ctx;
}

// ─────────────────────────────────────────────────────────────────────
// 3) components/Protected.jsx
// ─────────────────────────────────────────────────────────────────────

function Protected({ children }) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ dan: location.pathname }} replace />;
  }
  return children;
}

// ─────────────────────────────────────────────────────────────────────
// 4) components/Header.jsx
// ─────────────────────────────────────────────────────────────────────

function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const chiqish = () => {
    logout();
    navigate("/", { replace: true });
  };

  const navStyle = ({ isActive }) => ({
    padding: "6px 10px",
    textDecoration: "none",
    color: isActive ? "white" : "black",
    background: isActive ? "#222" : "transparent",
    borderRadius: 4,
  });

  return (
    <header style={{
      display: "flex",
      gap: 8,
      padding: 12,
      borderBottom: "1px solid",
      alignItems: "center",
    }}>
      <NavLink to="/"        style={navStyle} end>Bosh</NavLink>
      <NavLink to="/kurslar" style={navStyle}>Kurslar</NavLink>
      <NavLink to="/profil"  style={navStyle}>Profil</NavLink>
      <NavLink to="/sozlamalar" style={navStyle}>Sozlamalar</NavLink>

      <div style={{ flex: 1 }} />

      {user ? (
        <>
          <span>👤 {user.ism}</span>
          <button onClick={chiqish}>Chiqish</button>
        </>
      ) : (
        <NavLink to="/login" style={navStyle}>Kirish</NavLink>
      )}
    </header>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 5) pages/*.jsx
// ─────────────────────────────────────────────────────────────────────

function Bosh()       { return <h1>🏠 Bosh sahifa — hammaga ochiq</h1>; }
function Kurslar()    { return <h1>📚 Kurslar — hammaga ochiq</h1>; }

function Profil() {
  const { user } = useAuth();
  return (
    <div>
      <h1>👤 Profil — faqat tizimga kirganlar</h1>
      <pre>{JSON.stringify(user, null, 2)}</pre>
    </div>
  );
}

function Sozlamalar() {
  return <h1>⚙️ Sozlamalar — faqat tizimga kirganlar</h1>;
}

function NotFound() {
  return (
    <div>
      <h1>🚫 404</h1>
      <Link to="/">Bosh sahifaga</Link>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 6) pages/Login.jsx
// ─────────────────────────────────────────────────────────────────────

function Login() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail]   = useState("");
  const [parol, setParol]   = useState("");
  const [yubormoq, setYub]  = useState(false);
  const [xato, setXato]     = useState(null);

  // Agar allaqachon kirgan bo'lsa — yangi sahifaga o'tkazib yuborish
  useEffect(() => {
    if (user) {
      const dan = location.state?.dan ?? "/profil";
      navigate(dan, { replace: true });
    }
  }, [user, navigate, location]);

  const onSubmit = async (e) => {
    e.preventDefault();
    setYub(true);
    setXato(null);
    try {
      await login(email, parol);
      // useEffect navigate'ni qiladi
    } catch (e) {
      setXato(e.message);
    } finally {
      setYub(false);
    }
  };

  return (
    <form onSubmit={onSubmit} style={{
      maxWidth: 320,
      margin: "40px auto",
      display: "grid",
      gap: 12,
      padding: 24,
      border: "1px solid",
      borderRadius: 8,
    }}>
      <h2>🔐 Kirish</h2>

      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="email@uz"
        type="email"
        required
        disabled={yubormoq}
      />

      <input
        value={parol}
        onChange={(e) => setParol(e.target.value)}
        placeholder="parol (8+ belgi)"
        type="password"
        required
        disabled={yubormoq}
      />

      {xato && (
        <p style={{ color: "red", margin: 0 }}>{xato}</p>
      )}

      <button type="submit" disabled={yubormoq}>
        {yubormoq ? "Yuklanmoqda..." : "Kirish"}
      </button>

      <small style={{ color: "#888" }}>
        Hint: har qanday email + 8+ belgili parol
      </small>
    </form>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 7) App
// ─────────────────────────────────────────────────────────────────────

function AppContent() {
  return (
    <>
      <Header />
      <main style={{ padding: 20 }}>
        <Routes>
          {/* Public */}
          <Route path="/"        element={<Bosh />} />
          <Route path="/kurslar" element={<Kurslar />} />
          <Route path="/login"   element={<Login />} />

          {/* Private */}
          <Route
            path="/profil"
            element={<Protected><Profil /></Protected>}
          />
          <Route
            path="/sozlamalar"
            element={<Protected><Sozlamalar /></Protected>}
          />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
"""
L10_TEXT = """\
<h2>Performance: memo, useMemo, useCallback</h2>

<pre class="mermaid">
flowchart LR
    P["Parent render"] --> CH{"Child render\nkerakmi?"}
    CH -->|props bir xil + memo| SK["skip"]
    CH -->|props o'zgardi| RE["re-render"]
    M["useMemo: hisoblash cache"] --> CH
    CB["useCallback: funksiya cache"] --> CH
</pre>

<p>React tez. Lekin katta app'lar sekinlashishi mumkin: 1000 ta element ro'yxati har klavishada qayta render bo'lsa — sekinlik sezilarli. Bu darsda 3 ta vosita: <strong>React.memo</strong> (komponent), <strong>useMemo</strong> (qiymat), <strong>useCallback</strong> (funksiya).</p>

<p>⚠️ <strong>Bu — premature optimization xavfi bor mavzu</strong>. Avval ishlatib ko'ring, sekin bo'lganda — optimizatsiya. Har joyga memo qo'yish — yomon odat.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — React.memo</h4>
<pre><code>// Komponent props o'zgarganidagina qayta render bo'ladi
const Card = React.memo(function Card({ user }) {
  console.log("Card render:", user.ism);
  return &lt;div&gt;{user.ism}&lt;/div&gt;;
});

function Royxat({ users }) {
  return users.map(u =&gt; &lt;Card key={u.id} user={u} /&gt;);
}</code></pre>

<p>Parent render bo'lsa — Card faqat <code>user</code> obyekti o'zgargan bo'lsa qayta render.</p>

<h4>BLOKA 2 — useMemo (qiymat cache)</h4>
<pre><code>function Royxat({ users, qidir }) {
  // Qimmat hisoblash — har render'da qaytadan
  const filterlangan = useMemo(() =&gt; {
    return users
      .filter(u =&gt; u.ism.toLowerCase().includes(qidir.toLowerCase()))
      .sort((a, b) =&gt; a.ism.localeCompare(b.ism));
  }, [users, qidir]);   // faqat users yoki qidir o'zgarganda

  return &lt;ul&gt;{filterlangan.map(u =&gt; &lt;li key={u.id}&gt;{u.ism}&lt;/li&gt;)}&lt;/ul&gt;;
}</code></pre>

<h4>BLOKA 3 — useCallback (funksiya cache)</h4>
<pre><code>function Parent() {
  const [son, setSon] = useState(0);

  // ❌ Har render'da yangi funksiya — Card.memo bekor
  const onClick = (id) =&gt; alert(id);

  // ✅ useCallback — bir xil reference qaytadi
  const onClick2 = useCallback((id) =&gt; alert(id), []);

  return (
    &lt;&gt;
      &lt;button onClick={() =&gt; setSon(s =&gt; s + 1)}&gt;{son}&lt;/button&gt;
      &lt;Card onClick={onClick2} /&gt;   {/* memo ishlaydi */}
    &lt;/&gt;
  );
}</code></pre>

<h3>🐛 Ataylab xato (premature optimization)</h3>
<pre><code>const Button = React.memo(({ children, onClick }) =&gt; (
  &lt;button onClick={onClick}&gt;{children}&lt;/button&gt;
));

// Har joyda:
&lt;Button onClick={() =&gt; alert("ok")}&gt;OK&lt;/Button&gt;</code></pre>

<p><strong>Sabab:</strong> Har render'da yangi <code>() =&gt; alert(...)</code> funksiya — props reference o'zgaradi — memo bekor. Plyus: memo'ning o'zi tekshirish qiladi (props comparison) — kichik komponent uchun bu tekshirish bilan render orasidagi farq sezilmas. Har joyga memo qo'yish — kod og'irligi va kichik foyda.</p>

<p>Qoidasi: profile qiling, qaerda sekin — o'sha yerda optimallashtiring.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. React qachon render qiladi?</h4>
<table>
<tr><th>Sabab</th><th>Render</th></tr>
<tr><td>State o'zgardi (<code>setX</code>)</td><td>✅ qayta render</td></tr>
<tr><td>Props o'zgardi</td><td>✅ qayta render</td></tr>
<tr><td>Parent render bo'ldi</td><td>✅ qayta render (children avtomatik)</td></tr>
<tr><td>Context o'zgardi</td><td>✅ consumer'lar render</td></tr>
</table>

<h4>2. React.memo — komponent darajasi</h4>
<pre><code>const Card = React.memo(function Card({ user }) {
  // ...
});

// Custom comparison (kam ishlatamiz)
const Card = React.memo(
  function Card({ user }) { ... },
  (prev, next) =&gt; prev.user.id === next.user.id
);</code></pre>

<p>Default — shallow comparison (props ning har xususiyatini <code>===</code> bilan).</p>

<h4>3. useMemo — qiymat darajasi</h4>
<pre><code>const natija = useMemo(() =&gt; qimmatHisoblash(a, b), [a, b]);</code></pre>

<p>Qachon foydali:</p>
<ul>
<li>Qimmat hisoblash (sort, filter, agg)</li>
<li>Obyekt/array reference barqarorligi (boshqa hook deps uchun)</li>
<li>Context value (consumerlar performance uchun)</li>
</ul>

<p>Qachon foydasiz:</p>
<ul>
<li>Oddiy ifoda (<code>a + b</code>) — useMemo o'zi qimmatroq</li>
<li>Primitive qiymat (string, number)</li>
</ul>

<h4>4. useCallback — funksiya darajasi</h4>
<pre><code>const onClick = useCallback((id) =&gt; {
  console.log(id);
}, []);

// Yoki useMemo bilan teng:
const onClick = useMemo(() =&gt; (id) =&gt; console.log(id), []);</code></pre>

<p>Qachon foydali:</p>
<ul>
<li>Funksiyani <code>React.memo</code> qilingan child'ga uzatish</li>
<li>useEffect deps'iga funksiya kerak bo'lganda</li>
<li>Custom hook qaytaradigan funksiyalar (jamoadoshlar ishonishi uchun)</li>
</ul>

<h4>5. Optimallashtirish ketma-ketligi</h4>
<ol>
<li><strong>Profile</strong> — React DevTools Profiler. Qaysi komponent qachon va nima uchun render bo'layapti?</li>
<li><strong>Kerakmi?</strong> — sekinlik foydalanuvchiga ko'rinadimi (200ms+)?</li>
<li><strong>O'lchang</strong> — optimizatsiyadan oldin va keyin</li>
<li><strong>Optimallashtiring</strong> — memo, useMemo, useCallback</li>
<li><strong>Tasdiqlang</strong> — yangi o'lchov</li>
</ol>

<h4>6. Boshqa katta optimizatsiyalar</h4>

<table>
<tr><th>Texnika</th><th>Vazifa</th></tr>
<tr><td>Code splitting</td><td><code>React.lazy</code> + Suspense</td></tr>
<tr><td>Virtualization</td><td>react-window — 10000+ qator ro'yxat</td></tr>
<tr><td>Debounce/throttle</td><td>Foydalanuvchi inputida</td></tr>
<tr><td>Image lazy loading</td><td><code>loading="lazy"</code></td></tr>
<tr><td>Server components</td><td>Next.js — render server'da</td></tr>
</table>

<h4>7. React.lazy — code splitting</h4>
<pre><code>import { lazy, Suspense } from 'react';

const Ogir = lazy(() =&gt; import('./Ogir'));

function App() {
  return (
    &lt;Suspense fallback={&lt;p&gt;Yuklanmoqda...&lt;/p&gt;}&gt;
      &lt;Ogir /&gt;
    &lt;/Suspense&gt;
  );
}
// Ogir alohida bundle, faqat kerak bo'lsa yuklanadi</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>React.memo</code> — komponent render skip</li>
<li>✅ <code>useMemo</code> — qimmat hisoblash cache</li>
<li>✅ <code>useCallback</code> — funksiya reference barqaror</li>
<li>✅ Premature optimization xavfi — profile birinchi</li>
<li>✅ Code splitting (<code>React.lazy</code> + Suspense)</li>
<li>✅ Katta ro'yxatlar — react-window</li>
<li>✅ React DevTools Profiler bilan ishlash</li>
</ul>
"""

L10_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 10: Performance — memo, useMemo, useCallback
// ════════════════════════════════════════════════════════════════════

import React, {
  useState, useMemo, useCallback, memo, lazy, Suspense
} from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) React.memo — komponent render skip
// ─────────────────────────────────────────────────────────────────────

const Card = memo(function Card({ user, onSelect }) {
  console.log("Card render:", user.ism);
  return (
    <div style={{ padding: 8, border: "1px solid", margin: 4 }}>
      <span>{user.ism}</span>
      <button onClick={() => onSelect(user.id)}>Tanlash</button>
    </div>
  );
});

// ─────────────────────────────────────────────────────────────────────
// 2) useMemo — qimmat hisoblash
// ─────────────────────────────────────────────────────────────────────

function FoydalanuvchilarRoyxati({ users, qidir }) {
  // ❌ Har render'da qaytadan hisoblanadi (sekin agar users katta bo'lsa)
  // const filterlangan = users.filter(...).sort(...);

  // ✅ Faqat qaramligi o'zgarganda
  const filterlangan = useMemo(() => {
    console.log("filter+sort...");
    return users
      .filter(u => u.ism.toLowerCase().includes(qidir.toLowerCase()))
      .sort((a, b) => a.ism.localeCompare(b.ism));
  }, [users, qidir]);

  return (
    <ul>
      {filterlangan.map(u => <li key={u.id}>{u.ism}</li>)}
    </ul>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) useCallback — funksiya reference barqaror
// ─────────────────────────────────────────────────────────────────────

function Parent() {
  const [son, setSon] = useState(0);
  const [users] = useState([
    { id: 1, ism: "Olim" },
    { id: 2, ism: "Vali" },
    { id: 3, ism: "Karim" },
  ]);

  // ❌ Har render'da yangi funksiya — Card.memo bekor
  // const onSelect = (id) => alert(`Tanlandi: ${id}`);

  // ✅ Barqaror reference
  const onSelect = useCallback((id) => {
    alert(`Tanlandi: ${id}`);
  }, []);

  return (
    <div>
      <button onClick={() => setSon(s => s + 1)}>
        Son: {son}
      </button>

      {/* Card'lar — son o'zgarganida ham re-render bo'lmaydi */}
      {users.map(u => (
        <Card key={u.id} user={u} onSelect={onSelect} />
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 4) Misol: qidiruv bilan ishlovchi katta ro'yxat
// ─────────────────────────────────────────────────────────────────────

function App() {
  const [qidir, setQidir] = useState("");
  const [son, setSon] = useState(0);

  // 1000 ta user generate (faqat bir marta)
  const users = useMemo(() => {
    return Array.from({ length: 1000 }, (_, i) => ({
      id: i,
      ism: `Foydalanuvchi ${i}`,
    }));
  }, []);

  return (
    <div>
      <input
        value={qidir}
        onChange={(e) => setQidir(e.target.value)}
        placeholder="Qidir..."
      />

      <button onClick={() => setSon(s => s + 1)}>
        Boshqa state: {son}
      </button>

      <FoydalanuvchilarRoyxati users={users} qidir={qidir} />
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 5) Custom comparison (memo'ning 2-arg)
// ─────────────────────────────────────────────────────────────────────

const KrupnoyCard = memo(
  function KrupnoyCard({ user, izoh }) {
    return <div>{user.ism} - {izoh}</div>;
  },
  // Faqat user.id va izoh o'zgarganida render
  (prev, next) =>
    prev.user.id === next.user.id && prev.izoh === next.izoh
);

// ─────────────────────────────────────────────────────────────────────
// 6) useMemo — Context value barqarorligi uchun
// ─────────────────────────────────────────────────────────────────────

const ThemeContext = React.createContext();

function ThemeProvider({ children }) {
  const [tema, setTema] = useState("yorug");

  // ✅ Provider value — useMemo bilan
  const value = useMemo(
    () => ({ tema, setTema }),
    [tema]
  );

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 7) React.lazy — code splitting
// ─────────────────────────────────────────────────────────────────────

// const Diagrammalar = lazy(() => import('./Diagrammalar'));
// const Sozlamalar   = lazy(() => import('./Sozlamalar'));

function AppLazy() {
  const [sahifa, setSahifa] = useState("bosh");

  return (
    <div>
      <button onClick={() => setSahifa("diagram")}>Diagrammalar</button>

      <Suspense fallback={<p>⏳ Yuklanmoqda...</p>}>
        {/* sahifa === "diagram" && <Diagrammalar /> */}
        <p>Bu yerda dynamic component yuklanadi</p>
      </Suspense>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 8) ❌ Premature optimization misoli
// ─────────────────────────────────────────────────────────────────────

// const Button = memo(({ onClick, children }) => (
//   <button onClick={onClick}>{children}</button>
// ));
//
// <Button onClick={() => alert("ok")}>OK</Button>
//
// → har render'da yangi () => alert("ok") funksiya
// → memo bekor (props reference o'zgaradi)
// → komparing tekshirish + foydasiz
//
// Avval — keraksiz. Memo qo'yishdan oldin: profile qiling.

// ─────────────────────────────────────────────────────────────────────
// 9) React DevTools Profiler ishlatish — terminalda
// ─────────────────────────────────────────────────────────────────────

// 1. React DevTools (browser extension) o'rnatish
// 2. Profiler tab ochish
// 3. ⏺️ Record bosish
// 4. Saytda harakatlar qilish
// 5. ⏹️ Stop
// 6. Flame chart — qaysi komponent qancha vaqt
// 7. "Why did this render?" — Settings'da yoqing

export default App;
"""
L11_TEXT = """\
<h2>🚀 CAPSTONE: Recipe finder (React + Flask)</h2>

<pre class="mermaid">
flowchart LR
    UI["React UI"] -->|fetch| API["Flask API"]
    API -->|JSON| UI
    UI -->|saqlash| LS["localStorage\n(saved recipes)"]
    AUTH["AuthContext"] --> UI
    ROUTER["Router /recipes /favorites"] --> UI
</pre>

<p>Yakuniy loyiha — to'liq fullstack ilova: <strong>Recipe Finder</strong>. Foydalanuvchi resept qidiradi, batafsil ko'radi, saqlaydi, sharhlaydi. Backend — Flask (kursning Modul 4 dan tanish). Bu — siz hozir o'rganganlaringizning hammasi birga.</p>

<h3>Sxema</h3>

<table>
<tr><th>Qism</th><th>Texnologiya</th></tr>
<tr><td>Frontend</td><td>React + Vite + React Router</td></tr>
<tr><td>Backend</td><td>Flask + SQLAlchemy (yoki bevosita SQL)</td></tr>
<tr><td>DB</td><td>PostgreSQL — recipes, users, favorites</td></tr>
<tr><td>Auth</td><td>JWT (frontend Context, backend Flask-JWT-Extended)</td></tr>
<tr><td>API</td><td>External — TheMealDB (bepul) yoki o'zingiz seed</td></tr>
</table>

<h3>Sahifalar (Router)</h3>

<table>
<tr><th>URL</th><th>Sahifa</th><th>Auth</th></tr>
<tr><td><code>/</code></td><td>Bosh — top resepetlar</td><td>Ochiq</td></tr>
<tr><td><code>/recipes</code></td><td>Qidir + filter</td><td>Ochiq</td></tr>
<tr><td><code>/recipes/:id</code></td><td>Batafsil</td><td>Ochiq</td></tr>
<tr><td><code>/favorites</code></td><td>Saqlaganlar</td><td>🔒</td></tr>
<tr><td><code>/profile</code></td><td>Profil + statistika</td><td>🔒</td></tr>
<tr><td><code>/login</code></td><td>Kirish</td><td>—</td></tr>
<tr><td><code>/register</code></td><td>Ro'yxat</td><td>—</td></tr>
</table>

<h3>Texnik talablar</h3>

<h4>Frontend (React)</h4>
<ul>
<li>✅ Vite + React + React Router</li>
<li>✅ AuthContext (login, logout, token, useLocalStorage)</li>
<li>✅ FavoritesContext (yoki TanStack Query)</li>
<li>✅ Custom hooks: useFetch, useDebounce, useLocalStorage</li>
<li>✅ Protected route'lar</li>
<li>✅ Forms: controlled inputs, validatsiya</li>
<li>✅ Conditional rendering: loading/error/empty/data holatlari</li>
<li>✅ Lists: map + key + filter</li>
<li>✅ useEffect + AbortController</li>
<li>✅ React.memo bilan optimizatsiya (kerakli joyda)</li>
<li>✅ Responsive (mobile/tablet/desktop)</li>
<li>✅ Dark mode (Context bilan)</li>
</ul>

<h4>Backend (Flask)</h4>
<ul>
<li>✅ <code>/api/recipes</code> — GET (filter, qidiruv, sahifalash)</li>
<li>✅ <code>/api/recipes/:id</code> — GET</li>
<li>✅ <code>/api/auth/register</code> — POST</li>
<li>✅ <code>/api/auth/login</code> — POST (JWT qaytaradi)</li>
<li>✅ <code>/api/favorites</code> — GET/POST/DELETE (JWT shart)</li>
<li>✅ <code>/api/recipes/:id/comments</code> — GET/POST (JWT shart)</li>
<li>✅ CORS — frontend bilan ishlash</li>
</ul>

<h4>Database</h4>
<ul>
<li><code>users(id, ism, email, parol_hash, yaratilgan)</code></li>
<li><code>recipes(id, nomi, tavsif, rasm, kategoriya, vaqt, qiyinlik)</code></li>
<li><code>ingredients(id, recipe_id, nomi, miqdor)</code></li>
<li><code>favorites(user_id, recipe_id, qoshilgan)</code></li>
<li><code>comments(id, user_id, recipe_id, matn, sana)</code></li>
</ul>

<h3>Bonus (ixtiyoriy)</h3>
<ul>
<li>🎯 TanStack Query — server state</li>
<li>📱 PWA — offline ishlash</li>
<li>🔍 Elasticsearch — yaxshi qidiruv</li>
<li>📊 Profil sahifasida statistika (eng ko'p kategoriya, sahifa, va h.k.)</li>
<li>🍴 "Ovqat tayyor" timer — ingredients tickoff</li>
<li>📤 Sharing — resept'ni Telegram'ga yuborish</li>
<li>🧪 Vitest + React Testing Library bilan testlar</li>
<li>🐳 Docker compose — bir buyruq bilan boshlash</li>
<li>🚀 Deploy — Vercel (frontend) + Railway/Render (backend)</li>
</ul>

<h3>Boshlash uchun loyiha tuzilmasi</h3>

<pre><code>recipe-finder/
├── frontend/                  (Vite + React)
│   ├── src/
│   │   ├── api/              ← API client
│   │   ├── contexts/         ← Auth, Theme, Favorites
│   │   ├── hooks/            ← useFetch, useDebounce, ...
│   │   ├── components/       ← Header, Card, Modal, ...
│   │   ├── pages/            ← Bosh, Recipes, Detail, ...
│   │   └── App.jsx
│   └── package.json
└── backend/                   (Flask)
    ├── app/
    │   ├── models/
    │   ├── routes/
    │   ├── auth.py
    │   └── __init__.py
    ├── requirements.txt
    └── run.py</code></pre>

<h3>Bosqichlar (3 hafta loyiha)</h3>

<h4>Hafta 1 — Backend + sxema</h4>
<ol>
<li>Flask loyihasi, SQLAlchemy models</li>
<li>Auth endpoints (register, login, JWT)</li>
<li>Recipes endpoints + seed ma'lumot</li>
<li>Favorites + Comments endpoints</li>
<li>Postman bilan testlar</li>
</ol>

<h4>Hafta 2 — Frontend asoslari</h4>
<ol>
<li>Vite + Router + sahifalar</li>
<li>AuthContext + Login/Register sahifalari</li>
<li>Recipes sahifa — qidiruv + ro'yxat</li>
<li>Recipe detail sahifa</li>
<li>Protected routes</li>
</ol>

<h4>Hafta 3 — UX va polish</h4>
<ol>
<li>Favorites — qo'shish/o'chirish</li>
<li>Comments — yozish</li>
<li>Profile sahifa</li>
<li>Dark mode</li>
<li>Responsive</li>
<li>Performance — memo, lazy</li>
<li>Deploy</li>
</ol>

<h3>🎯 Yakuniy g'olib bayonoti</h3>

<p>Bu loyihani tugatgan dasturchi <strong>real ish</strong> uchun tayyor. Sizda CV uchun loyiha (GitHub'da kod, live deploy), texnik suhbatlar uchun mavzular (custom hooks, Context, JWT, performance), va eng muhimi — siz endi React ekosistemasini chuqur tushunasiz.</p>

<p>Keyingi qadamlar:</p>
<ul>
<li>📘 <strong>TypeScript</strong> — type safety qo'shish</li>
<li>📦 <strong>TanStack Query</strong> — server state professional usulda</li>
<li>🎨 <strong>Tailwind / shadcn/ui</strong> — UI tezroq</li>
<li>⚡ <strong>Next.js</strong> — server components, SSR</li>
<li>🧪 <strong>Vitest + Playwright</strong> — testlar</li>
</ul>

<p>React — bu boshlanish. JS ekosistemasi keng. Lekin endi siz <em>fundament</em>'ga egasiz. Omad!</p>
"""

L11_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 🚀 CAPSTONE: Recipe Finder — fragment'lar (to'liq emas)
// To'liq loyiha o'zingiz yozasiz — bu yerda muhim qismlar
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) src/api/client.js — API client
// ─────────────────────────────────────────────────────────────────────

const API = import.meta.env.VITE_API_URL || "http://localhost:5000";

export async function apiGet(path, token) {
  const r = await fetch(`${API}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!r.ok) throw new Error("HTTP " + r.status);
  return r.json();
}

export async function apiPost(path, body, token) {
  const r = await fetch(`${API}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    throw new Error(err.message || "HTTP " + r.status);
  }
  return r.json();
}


// ─────────────────────────────────────────────────────────────────────
// 2) src/contexts/AuthContext.jsx
// ─────────────────────────────────────────────────────────────────────

import { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';
// import { apiPost } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("user");
    return saved ? JSON.parse(saved) : null;
  });

  useEffect(() => {
    if (token) localStorage.setItem("token", token);
    else       localStorage.removeItem("token");
  }, [token]);

  useEffect(() => {
    if (user) localStorage.setItem("user", JSON.stringify(user));
    else      localStorage.removeItem("user");
  }, [user]);

  const login = useCallback(async (email, parol) => {
    const data = await apiPost("/api/auth/login", { email, parol });
    setToken(data.token);
    setUser(data.user);
  }, []);

  const register = useCallback(async (ism, email, parol) => {
    const data = await apiPost("/api/auth/register", { ism, email, parol });
    setToken(data.token);
    setUser(data.user);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, token, login, register, logout }),
    [user, token, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth faqat AuthProvider ichida");
  return ctx;
};


// ─────────────────────────────────────────────────────────────────────
// 3) src/hooks/useRecipes.js — custom hook
// ─────────────────────────────────────────────────────────────────────

import { useState, useEffect } from 'react';

export function useRecipes({ qidir, kategoriya }) {
  const [recipes, setRecipes] = useState([]);
  const [yukla, setYukla] = useState(false);
  const [xato, setXato] = useState(null);

  useEffect(() => {
    const ctrl = new AbortController();
    setYukla(true);
    setXato(null);

    const params = new URLSearchParams();
    if (qidir)      params.set("q", qidir);
    if (kategoriya) params.set("kategoriya", kategoriya);

    fetch(`/api/recipes?${params}`, { signal: ctrl.signal })
      .then(r => r.json())
      .then(d => {
        setRecipes(d.data || []);
        setYukla(false);
      })
      .catch(e => {
        if (e.name !== "AbortError") {
          setXato(e.message);
          setYukla(false);
        }
      });

    return () => ctrl.abort();
  }, [qidir, kategoriya]);

  return { recipes, yukla, xato };
}


// ─────────────────────────────────────────────────────────────────────
// 4) src/pages/Recipes.jsx
// ─────────────────────────────────────────────────────────────────────

import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
// import { useRecipes } from '../hooks/useRecipes';
// import { useDebounce } from '../hooks/useDebounce';

export function Recipes() {
  const [params, setParams] = useSearchParams();
  const qidir = params.get("q") ?? "";
  const kategoriya = params.get("kategoriya") ?? "";

  const debouncedQidir = useDebounce(qidir, 300);
  const { recipes, yukla, xato } = useRecipes({
    qidir: debouncedQidir,
    kategoriya,
  });

  const update = (key, val) => {
    const next = new URLSearchParams(params);
    if (val) next.set(key, val);
    else     next.delete(key);
    setParams(next);
  };

  return (
    <div>
      <h1>🍽️ Resepetlar</h1>

      <div className="filters">
        <input
          value={qidir}
          onChange={(e) => update("q", e.target.value)}
          placeholder="Qidir..."
        />

        <select
          value={kategoriya}
          onChange={(e) => update("kategoriya", e.target.value)}
        >
          <option value="">Barchasi</option>
          <option value="palov">Palov</option>
          <option value="shorva">Shorva</option>
          <option value="salat">Salat</option>
          <option value="shirinlik">Shirinlik</option>
        </select>
      </div>

      {yukla && <p>Yuklanmoqda...</p>}
      {xato && <p className="xato">{xato}</p>}

      {!yukla && recipes.length === 0 && (
        <p>🌱 Resept topilmadi</p>
      )}

      <div className="grid">
        {recipes.map(r => (
          <Link key={r.id} to={`/recipes/${r.id}`} className="card">
            <img src={r.rasm} alt={r.nomi} loading="lazy" />
            <h3>{r.nomi}</h3>
            <small>⏱️ {r.vaqt} daq | {r.qiyinlik}</small>
          </Link>
        ))}
      </div>
    </div>
  );
}


// ─────────────────────────────────────────────────────────────────────
// 5) src/pages/RecipeDetail.jsx
// ─────────────────────────────────────────────────────────────────────

import { useParams } from 'react-router-dom';
// import { useFetch } from '../hooks/useFetch';
// import { useAuth } from '../contexts/AuthContext';
// import { useFavorites } from '../contexts/FavoritesContext';

export function RecipeDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const { recipe, yukla } = useFetch(`/api/recipes/${id}`);
  const { isFavorite, toggle } = useFavorites();

  if (yukla) return <p>Yuklanmoqda...</p>;
  if (!recipe) return <p>Resept topilmadi</p>;

  return (
    <article className="recipe-detail">
      <img src={recipe.rasm} alt={recipe.nomi} />
      <h1>{recipe.nomi}</h1>
      <p>{recipe.tavsif}</p>

      <div className="meta">
        <span>⏱️ {recipe.vaqt} daq</span>
        <span>📊 {recipe.qiyinlik}</span>
        <span>🍽️ {recipe.kategoriya}</span>
      </div>

      {user && (
        <button onClick={() => toggle(recipe.id)}>
          {isFavorite(recipe.id) ? "❤️ Saqlangan" : "🤍 Saqlash"}
        </button>
      )}

      <section>
        <h2>Ingredients</h2>
        <ul>
          {recipe.ingredients.map((i, idx) => (
            <li key={idx}>{i.nomi} — {i.miqdor}</li>
          ))}
        </ul>
      </section>

      <section>
        <h2>Tayyorlash</h2>
        <ol>
          {recipe.bosqichlar.map((b, i) => (
            <li key={i}>{b}</li>
          ))}
        </ol>
      </section>

      {/* Comments — agar tizimda bo'lsa */}
      {user && <Comments recipeId={recipe.id} />}
    </article>
  );
}


// ─────────────────────────────────────────────────────────────────────
// 6) src/App.jsx — yuqori daraja
// ─────────────────────────────────────────────────────────────────────

import { BrowserRouter, Routes, Route } from 'react-router-dom';
// import { AuthProvider } from './contexts/AuthContext';
// import { FavoritesProvider } from './contexts/FavoritesContext';
// import { ThemeProvider } from './contexts/ThemeContext';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ThemeProvider>
          <FavoritesProvider>
            <Header />
            <main>
              <Routes>
                <Route path="/"          element={<Bosh />} />
                <Route path="/recipes"   element={<Recipes />} />
                <Route path="/recipes/:id" element={<RecipeDetail />} />
                <Route path="/login"     element={<Login />} />
                <Route path="/register"  element={<Register />} />

                <Route path="/favorites" element={
                  <Protected><Favorites /></Protected>
                } />
                <Route path="/profile" element={
                  <Protected><Profile /></Protected>
                } />

                <Route path="*" element={<NotFound />} />
              </Routes>
            </main>
          </FavoritesProvider>
        </ThemeProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}


// ─────────────────────────────────────────────────────────────────────
// 7) backend — Flask sketch (Modul 4'dan eslang)
// ─────────────────────────────────────────────────────────────────────

/*
# app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'maxfiy-kalit'
    CORS(app, origins=['http://localhost:5173'])
    JWTManager(app)

    from .routes import auth, recipes, favorites
    app.register_blueprint(auth.bp,      url_prefix='/api/auth')
    app.register_blueprint(recipes.bp,   url_prefix='/api/recipes')
    app.register_blueprint(favorites.bp, url_prefix='/api/favorites')
    return app

# app/routes/recipes.py
from flask import Blueprint, request, jsonify
from ..models import Recipe

bp = Blueprint('recipes', __name__)

@bp.get('/')
def royxat():
    q = request.args.get('q', '')
    kategoriya = request.args.get('kategoriya', '')
    query = Recipe.query
    if q:
        query = query.filter(Recipe.nomi.ilike(f'%{q}%'))
    if kategoriya:
        query = query.filter_by(kategoriya=kategoriya)
    recipes = query.limit(50).all()
    return jsonify({'data': [r.to_dict() for r in recipes]})

@bp.get('/<int:id>')
def tafsilot(id):
    r = Recipe.query.get_or_404(id)
    return jsonify(r.to_dict())
*/

// ════════════════════════════════════════════════════════════════════
// To'liq loyiha — siz qurasiz!
// Repo: https://github.com/sizning-user/recipe-finder
// ════════════════════════════════════════════════════════════════════
"""


# ─────────────────────────────────────────────────────────────────────────────
# Exercise builders
# ─────────────────────────────────────────────────────────────────────────────
def mc(title, options, correct, *, multi=False, hint="", explanation="", diff="Easy", pts=2):
    return {"title": title, "description": title, "exercise_type": "multiple_choice",
            "options": options, "correct_answers": correct, "is_multiple_select": multi,
            "hint": hint, "explanation": explanation,
            "difficulty_level": diff, "points": pts}


def dd(title, items_in_order, *, hint="", explanation="", diff="Medium", pts=3):
    return {"title": title, "description": title, "exercise_type": "drag_and_drop",
            "drag_items": list(items_in_order), "correct_order": list(items_in_order),
            "is_multiple_select": False, "hint": hint, "explanation": explanation,
            "difficulty_level": diff, "points": pts}


def ti(title, expected, *, hint="", explanation="", diff="Hard", pts=4):
    return {"title": title, "description": title, "exercise_type": "text_input",
            "expected_answer": expected, "is_multiple_select": False,
            "hint": hint, "explanation": explanation,
            "difficulty_level": diff, "points": pts}


L1_EX: list = [
    mc("React komponentining nomi qanday boshlanishi kerak?",
       ["kichik harf bilan (myButton)",
        "katta harf bilan (MyButton)",
        "$ belgisi bilan",
        "Farqi yo'q"],
       "B", hint="React kichik harfli teglarni HTML element deb hisoblaydi.",
       diff="Easy", pts=2),
    mc("JSX'da `class` o'rniga nima ishlatamiz?",
       ["class",
        "className",
        "css-class",
        "cssClass"],
       "B", explanation="`class` — JS rezerv kalit so'zi. Shuning uchun React `className`.",
       diff="Easy", pts=2),
    mc("Quyidagi kod xato beradi. Sabab?\n```jsx\nfunction App() {\n  return (\n    <h1>Salom</h1>\n    <p>Dunyo</p>\n  );\n}\n```",
       ["JSX'da p tegi yo'q",
        "Komponent bitta ildiz element qaytarishi kerak",
        "Sarlavha bo'sh bo'lolmaydi",
        "import yo'q"],
       "B", explanation="Yechim: <div>...</div> ichiga o'rab olish yoki Fragment <>...</> ishlatish.",
       diff="Medium", pts=3),
    mc("JSX ichida JS ifoda qanday yoziladi?",
       ["${ifoda}",
        "{ifoda}",
        "{{ifoda}}",
        "<%ifoda%>"],
       "B", hint="Bitta jingalak qavslar.",
       diff="Easy", pts=2),
    mc("Quyidagilardan qaysilari TO'G'RI JSX?",
       ["<input type='text' />",
        "<img src='/x.png' />",
        "<div onClick={handle}>Bos</div>",
        "<label for='ism'>Ism</label>",
        "<button style={{color: 'red'}}>OK</button>"],
       "A,B,C,E", multi=True,
       hint="JSX'da `for` — `htmlFor`. Boshqalari to'g'ri.",
       diff="Medium", pts=3),
    dd("Vite + React loyihasini boshlash bosqichlari",
       ["npm create vite@latest mening-app -- --template react",
        "cd mening-app",
        "npm install",
        "npm run dev"],
       diff="Easy", pts=2),
    ti("`<h1>{2 + 2}</h1>` JSX nima render qiladi va nima uchun bu ishlaydi?",
       "Natija: <h1>4</h1>. JSX ichida `{...}` — JS IFODA uchun. 2 + 2 — ifoda, "
       "u 4 qaytaradi va render qilinadi. Statement (if, for) — yo'q, ifoda — ha. "
       "Shuning uchun ternary `? :` va `&&` ishlatamiz, oddiy `if` emas. "
       "JSX kompilyatorga aytadi: 'shu joyga shu ifoda natijasini qo'y'.",
       hint="Statement vs Expression farqi.",
       diff="Hard", pts=4),
]
L2_EX: list = [
    mc("Props nima?",
       ["State'ning eski nomi",
        "Parent komponentdan child komponentga uzatiladigan ma'lumot",
        "Komponent ichki o'zgaruvchisi",
        "React'ning ichki funksiyasi"],
       "B", diff="Easy", pts=2),
    mc("`<Profil yosh={22} />` va `<Profil yosh=\"22\" />` o'rtasidagi farq?",
       ["Hech qanday",
        "Birinchi: number, ikkinchi: string",
        "Birinchi xato",
        "Ikkinchi xato"],
       "B", explanation="JSX'da {} ichida — JS ifoda. \"...\" — har doim string.",
       diff="Medium", pts=3),
    mc("Props'ni komponent ichida o'zgartirish mumkinmi?",
       ["Ha, har qachon",
        "Yo'q — props read-only. O'zgartirish kerak bo'lsa useState yoki parent'ga callback yuborish",
        "Faqat birinchi marta",
        "Yangi React versiyada — ha"],
       "B", explanation="Bu — React'ning asosiy qoidalaridan biri. Ma'lumot yuqoridan pastga oqadi.",
       diff="Medium", pts=3),
    mc("`children` prop qachon foydali?",
       ["Faqat ro'yxat ko'rsatish uchun",
        "Wrapping komponentlar (Card, Modal, Layout) uchun — komponent teglari orasidagi mazmun",
        "Hech qachon",
        "Faqat sinflarda"],
       "B", explanation="Layout, Modal, Card — har doim children bilan ishlaydi. Slot pattern.",
       diff="Medium", pts=3),
    mc("Quyidagilardan qaysilari TO'G'RI props uzatish?",
       ["<Btn label='OK' />",
        "<Btn label={\"OK\"} />",
        "<Btn count={5} />",
        "<Btn faol={true} />",
        "<Btn label=true />"],
       "A,B,C,D", multi=True,
       hint="Boolean — har doim {}. String — \"\" yoki {} ham mumkin.",
       diff="Medium", pts=3),
    dd("Default qiymatli komponent yozish bosqichlari",
       ["function Tugma({",
        "    label = 'Tasdiqlash',",
        "    turi = 'primary',",
        "    onClick",
        "}) {",
        "    return <button className={`btn ${turi}`} onClick={onClick}>{label}</button>;",
        "}"],
       diff="Medium", pts=3),
    ti("Nima uchun React'da ma'lumot 'yuqoridan pastga' (one-way data flow) oqadi?",
       "1) Soddalik — har komponent qaerdan ma'lumot kelishini bilad. "
       "2) Debugging — xato qaerda? Yuqori darajaga ko'tarilib top. "
       "3) Predictability — child o'zgartirsa, parent bilmaydi va sayt sinadi. "
       "4) Performance — React qaysi qism qayta render bo'lishi kerakligini hisoblash oson. "
       "Two-way data flow (Angular eski versiyalari) — chigallikka olib keladi. "
       "React: ma'lumot pastga, hodisa (callback) yuqoriga.",
       hint="Soddalik va debugging.",
       diff="Hard", pts=4),
]
L3_EX: list = [
    mc("`const [son, setSon] = useState(0)` — bu yerda `0` nima?",
       ["State'ning yakuniy qiymati",
        "Boshlang'ich qiymat (faqat birinchi render uchun)",
        "Qator raqami",
        "Eskirgan prop"],
       "B", hint="Birinchi render — keyin set... bilan o'zgarib turadi.",
       diff="Easy", pts=2),
    mc("`<button onClick={setSon(son + 1)}>Bos</button>` — bu xato. Nima uchun?",
       ["onClick sintaksisi yo'q",
        "setSon darhol chaqiriladi va cheksiz render aylanmasi paydo bo'ladi",
        "+1 ishlamaydi",
        "Hech narsa — to'g'ri kod"],
       "B", explanation="onClick FUNKSIYA kutadi, qiymat emas. To'g'risi: onClick={() => setSon(son + 1)}.",
       diff="Hard", pts=4),
    mc("Array state'ga element qo'shish to'g'ri yo'li:",
       ["arr.push(x); setArr(arr);",
        "setArr([...arr, x])",
        "setArr(arr + x)",
        "arr.append(x)"],
       "B", explanation="Mutate emas, yangi array yarating.",
       diff="Medium", pts=3),
    mc("`setSon(son + 1); setSon(son + 1); setSon(son + 1);` — natija nima?",
       ["son 3 ga oshadi",
        "son 1 ga oshadi (uchalasi ham eski qiymatdan o'qiydi)",
        "Xato",
        "son 6 ga oshadi"],
       "B", explanation="Functional update kerak: setSon(s => s + 1) — har biri oldingisidan o'sadi.",
       diff="Hard", pts=4),
    mc("Object state'ni yangilash to'g'ri yo'li:",
       ["obj.x = 5; setObj(obj);",
        "setObj({ ...obj, x: 5 })",
        "setObj.x(5)",
        "useState(obj).x = 5"],
       "B", explanation="Yangi obyekt — spread bilan eskini ko'chirib, kerakli maydonni yangilash.",
       diff="Medium", pts=3),
    dd("Counter komponenti yozish bosqichlari",
       ["import { useState } from 'react';",
        "function Counter() {",
        "    const [son, setSon] = useState(0);",
        "    return (",
        "        <div>",
        "            <p>{son}</p>",
        "            <button onClick={() => setSon(s => s + 1)}>+1</button>",
        "        </div>",
        "    );",
        "}"],
       diff="Medium", pts=3),
    ti("Komponent ichida `let son = 0` deb e'lon qilsak va `son++` qilsak — UI yangilanmaydi. Nima uchun?",
       "Sabab: React UI'ni faqat STATE o'zgarganda qayta render qiladi. "
       "`let son = 0` — oddiy o'zgaruvchi. U o'zgartirilsa, React buni 'sezmaydi' va "
       "qayta render qilmaydi. Plus: har render'da funksiya qaytadan chaqiriladi va "
       "`let son = 0` qaytadan 0 ga qaytadi. "
       "Yechim: useState. React state'ni eslab qoladi va o'zgargach UI'ni yangilaydi.",
       hint="React qachon qayta render qiladi?",
       diff="Hard", pts=4),
]
R1_EX: list = [
    mc("'State lifting' nima?",
       ["State'ni komponentni o'chirib qayta yaratish",
        "Child komponent state'ni umumiy parent'ga ko'chirish — bir nechta child shu state'ni baham ko'rishi uchun",
        "useState'ni eskirgan nomi",
        "State'ni database'ga saqlash"],
       "B", explanation="Parent state'ni boshqaradi, child'lar props orqali oladi va onChange bilan xabar yuboradi.",
       diff="Medium", pts=3),
    mc("'Controlled component' nima?",
       ["Komponent o'ziga ega state'ga ega emas — value va onChange parent'dan keladi",
        "Bitta tugmasi bor komponent",
        "Eskirgan tushuncha",
        "Faqat input bilan ishlatiladi"],
       "A", explanation="Counter ham, Input ham — har biri controlled bo'lishi mumkin.",
       diff="Medium", pts=3),
    mc("Todo'larga unik `id` berishning eng oson yo'li:",
       ["i + 1 (index)",
        "Math.random()",
        "Date.now()",
        "todoCount++ (global o'zgaruvchi)"],
       "C", explanation="Date.now() — milliond aniqlik, unique. Production'da crypto.randomUUID() yaxshiroq.",
       diff="Easy", pts=2),
    mc("Quyidagilardan qaysilari TO'G'RI array state ishlatish?",
       ["setTodos([...todos, yangi])",
        "todos.push(yangi); setTodos(todos);",
        "setTodos(todos.filter(t => t.id !== id))",
        "setTodos(todos.map(t => t.id === id ? {...t, done: true} : t))",
        "todos[i] = yangi; setTodos(todos);"],
       "A,C,D", multi=True,
       hint="Mutate qilmang — yangi array yarating.",
       diff="Hard", pts=4),
    dd("Todo bajarildi/bajarilmadi toggle qilish bosqichlari",
       ["const toggle = (id) => {",
        "    setTodos(todos.map(t =>",
        "        t.id === id ? { ...t, bajarildi: !t.bajarildi } : t",
        "    ));",
        "};"],
       diff="Medium", pts=3),
    ti("Counter ichki state'ida ishlasa, App'da 'jami' hisoblash mumkinmi?",
       "Bevosita — yo'q, chunki App child state'iga bevosita kira olmaydi (encapsulation). "
       "Lekin yo'llar bor: 1) Counter onChange callback yuborib App'ni xabardor qilsin "
       "(App o'z state'ida saqlab borsin). 2) State lifting — state App'da, Counter "
       "shunchaki value + onChange oladi (controlled). Yo'l 2 — zamonaviy va aniqroq. "
       "React falsafasiga ko'ra: 'state shu yerda kerak — eng yuqori joyga qo'ying'.",
       hint="Encapsulation va lifting.",
       diff="Hard", pts=4),
    mc("`todos.length === 0 ? <p>Bo'sh</p> : <ul>...</ul>` — bu nima usul?",
       ["JSX'da ternary operator bilan conditional rendering",
        "If-else statement",
        "Faqat ko'rsatish",
        "Xato"],
       "A", diff="Easy", pts=2),
]
L4_EX: list = [
    mc("JSX'da `if` statement ishlamaydi. Buning o'rniga nima ishlatamiz?",
       ["for loop",
        "while",
        "Ternary `? :` yoki `&&` operator",
        "switch"],
       "C", diff="Easy", pts=2),
    mc("`{count && <p>{count}</p>}` — count = 0 bo'lsa nima ko'rinadi?",
       ["Hech narsa (yashirin)",
        "'0' so'zi UI'da ko'rinadi (chunki 0 falsy lekin renderlanadi)",
        "p teg bo'sh ko'rinadi",
        "Xato"],
       "B", explanation="To'g'risi: `{count > 0 && <p>{count}</p>}`.",
       diff="Hard", pts=4),
    mc("Ro'yxat render qilganda nima uchun `key` kerak?",
       ["UI chiroyli ko'rinishi uchun",
        "React qaysi element qaysi ekanini bilish va to'g'ri qayta ishlatish uchun",
        "Faqat performance",
        "Hech narsa uchun"],
       "B", explanation="Kalitsiz React noto'g'ri komponent qayta ishlatishi mumkin (input qiymatlari aralashadi).",
       diff="Medium", pts=3),
    mc("`key` qachon index bo'lishi mumkin?",
       ["Hech qachon",
        "Faqat ro'yxat tartibi/uzunligi hech qachon o'zgarmaganida",
        "Doim",
        "Faqat statik tepa darajada"],
       "B", diff="Hard", pts=4),
    mc("Quyidagi key'lardan qaysilari YAXSHI?",
       ["key={todo.id}",
        "key={user.email}",
        "key={Math.random()}",
        "key={index}",
        "key={`post-${post.id}`}"],
       "A,B,E", multi=True,
       hint="Math.random — har render'da yangi. Index — ro'yxat o'zgarsa muammoli.",
       diff="Medium", pts=3),
    dd("Filterlangan ro'yxatni bo'sh holat bilan render qilish",
       ["const arzon = mevalar.filter(m => m.narx < limit);",
        "if (arzon.length === 0) {",
        "    return <p>Hech narsa yo'q</p>;",
        "}",
        "return (",
        "    <ul>",
        "        {arzon.map(m => <li key={m.id}>{m.nomi}</li>)}",
        "    </ul>",
        ");"],
       diff="Medium", pts=3),
    ti("Nima uchun JSX'da `for` siklini bevosita yoza olmaymiz?",
       "JSX faqat IFODA (expression) qabul qiladi, statement emas. "
       "`for` — statement: qiymat qaytarmaydi. "
       "`map` esa — ifoda: yangi array qaytaradi. "
       "JSX'da har {...} ichi — ifoda bo'lishi shart. "
       "Shuning uchun: oddiy for ishlatib qator yig'ib, keyin JSX qaytarish — "
       "yoki ko'p hollarda map, filter, reduce — JS ning declarative usullari. "
       "React mantig'i: 'qanday qilish' emas, 'qaysi natija' (declarative).",
       hint="Statement vs Expression.",
       diff="Hard", pts=4),
]
L5_EX: list = [
    mc("Controlled component nima?",
       ["State'siz komponent",
        "Input qiymati React state'da yashaydi va `value` + `onChange` orqali boshqariladi",
        "Faqat checkbox",
        "React Hook Form'ning ichki komponenti"],
       "B", diff="Easy", pts=2),
    mc("Form submit qilganda nima uchun `e.preventDefault()` kerak?",
       ["Validation uchun",
        "Browser sahifani qayta yuklamasligi uchun (React state yo'qolmasin)",
        "Performance uchun",
        "Hech qachon kerak emas"],
       "B", explanation="Default browser xulqi: form GET/POST qiladi va sahifa yuklanadi. preventDefault buni to'xtatadi.",
       diff="Medium", pts=3),
    mc("Multi-input formada bitta `ozgartir` funksiya uchun nima trick kerak?",
       ["Har input uchun alohida funksiya",
        "Har input'ga `name` attribute + `[name]: value` spread bilan dynamic key",
        "Mumkin emas",
        "useReducer"],
       "B", diff="Medium", pts=3),
    mc("Checkbox uchun to'g'ri controlled atributlar:",
       ["value + onChange",
        "checked + onChange (e.target.checked)",
        "selected + onChange",
        "active + onClick"],
       "B", explanation="Checkbox — `checked` boolean. value belgilanadi lekin checked muhim.",
       diff="Medium", pts=3),
    mc("Quyidagilardan qaysilari TO'G'RI controlled input:",
       ["<input value={x} onChange={e => setX(e.target.value)} />",
        "<input defaultValue={x} />",
        "<input value={x} />",
        "<textarea value={x} onChange={e => setX(e.target.value)} />",
        "<select value={x} onChange={e => setX(e.target.value)}>...</select>"],
       "A,D,E", multi=True,
       hint="defaultValue — uncontrolled. value alone (onChange siz) — React ogohlantiradi.",
       diff="Hard", pts=4),
    dd("Async login formaning yuborish funksiyasi bosqichlari",
       ["const yuborish = async (e) => {",
        "    e.preventDefault();",
        "    setYubormoq(true);",
        "    setXato(null);",
        "    try {",
        "        const res = await fetch('/api/login', {",
        "            method: 'POST', headers: {'Content-Type':'application/json'},",
        "            body: JSON.stringify(forma)",
        "        });",
        "        if (!res.ok) throw new Error('Xato');",
        "    } catch (e) { setXato(e.message); }",
        "    finally { setYubormoq(false); }",
        "};"],
       diff="Hard", pts=4),
    ti("Nima uchun React validatsiyani `useState` bilan saqlamasdan, har render'da qayta hisoblash mumkin (va tavsiya etiladi)?",
       "Sabab: validatsiya — ma'lumotdan TUSHUVCHI qiymat. Email yaroqli yoki yo'qmi — "
       "bu email state'idan hisoblanadi. Alohida state'da saqlash — duplikatsiya. "
       "Render funksiyasi har gal qaytadan chaqirilganda — validatsiya ham qaytadan hisoblanadi "
       "(state o'zgargani uchun). Bu — 'derived state' anti-pattern'ning aksi. "
       "Qoidasi: agar X qiymatni boshqa state'dan hisoblash mumkin bo'lsa — uni state'da SAQLAMANG.",
       hint="Derived state anti-pattern.",
       diff="Hard", pts=4),
]
L6_EX: list = [
    mc("`useEffect(fn, [])` — `[]` nima anglatadi?",
       ["Effect ishlamaydi",
        "Effect faqat bir marta (mount'da) ishga tushadi",
        "Effect har render'da ishga tushadi",
        "Sintaktik xato"],
       "B", diff="Easy", pts=2),
    mc("`useEffect(fn, [son])` — qachon ishga tushadi?",
       ["Mount va son o'zgarganda",
        "Faqat son o'zgarganda",
        "Faqat mount'da",
        "Hech qachon"],
       "A", explanation="Birinchi marta — mount. Keyin har son o'zgarganda.",
       diff="Medium", pts=3),
    mc("`return () => clearInterval(id)` — bu nima va qachon ishga tushadi?",
       ["Cleanup. Komponent unmount yoki effect qayta ishga tushishidan oldin",
        "Setup. Komponent render'dan oldin",
        "Optimizatsiya",
        "Faqat dekoratsiya"],
       "A", diff="Medium", pts=3),
    mc("Quyidagi kod xato yaratadi. Sabab?\n```jsx\nuseEffect(() => {\n  setSon(son + 1);\n});\n```",
       ["Sintaktik xato",
        "Deps yo'q — har render'da effect, son o'zgaradi, qayta render, qayta effect — infinite loop",
        "setSon ishlatib bo'lmaydi",
        "Hech qanday xato"],
       "B", explanation="Deps array berish va effect ichida shu state'ni o'zgartirmaslik (yoki shartli).",
       diff="Hard", pts=4),
    mc("Race condition (eski fetch yangi'ni o'rnida yozish) yechimi:",
       ["useEffect ishlatmang",
        "`let ignore = false; ... if (!ignore) setX(data); ... return () => { ignore = true; }`",
        "AbortController bilan signal yuborish",
        "Faqat axios ishlatish"],
       "B,C", multi=True,
       hint="Ikkala usul ham ishlaydi. AbortController zamonaviyroq.",
       diff="Hard", pts=4),
    dd("Soat komponentini yozish bosqichlari",
       ["import { useState, useEffect } from 'react';",
        "function Soat() {",
        "    const [vaqt, setVaqt] = useState(new Date());",
        "    useEffect(() => {",
        "        const id = setInterval(() => setVaqt(new Date()), 1000);",
        "        return () => clearInterval(id);",
        "    }, []);",
        "    return <p>{vaqt.toLocaleTimeString()}</p>;",
        "}"],
       diff="Medium", pts=3),
    ti("Nima uchun React 18 StrictMode'da useEffect dev paytida 2 marta ishga tushiriladi?",
       "Sabab: cleanup'ingiz to'g'ri yozilganligini tekshirish uchun. Komponent mount → unmount → "
       "yana mount jarayonini simulatsiya qiladi. Agar cleanup yo'q yoki noto'g'ri bo'lsa — "
       "memory leak, double timer, double fetch xatosi ko'rinadi. Bu — bug emas, "
       "xususiyat. Production'da bir marta. Yechim: doim cleanup yozing va effect "
       "idempotent (bir necha marta xavfsiz ishlay oladigan) bo'lsin.",
       hint="Cleanup'ni tekshirish.",
       diff="Hard", pts=4),
]
R2_EX: list = [
    mc("Foydalanuvchi tez-tez shaharni almashtirsa, eski fetch yangini bosib ketishi mumkin. Bu — race condition. Yechim:",
       ["setTimeout bilan kechiktirish",
        "AbortController + signal: ctrl.signal yoki `let ignore = false; return () => ignore = true`",
        "Faqat bitta useEffect ishlatish",
        "Promise.all"],
       "B", diff="Hard", pts=4),
    mc("'Refresh' tugmasi useEffect'ni qayta ishga tushirish uchun qaysi pattern oson?",
       ["window.location.reload()",
        "useState bilan counter ko'paytirish va uni deps'ga qo'shish",
        "Faqat useEffect'ni qayta yozish",
        "Mumkin emas"],
       "B", explanation="setYangilanish(y => y + 1) → deps o'zgardi → effect qayta ishga tushadi.",
       diff="Medium", pts=3),
    mc("3 ta UI holatga to'g'ri keladigan conditional:",
       ["if (yukla) ... else if (xato) ... else ...",
        "{yukla && <Spinner/>}{xato && <Error/>}{data && <View/>}",
        "switch (status)",
        "Hamma variantlar — to'g'ri"],
       "D", diff="Easy", pts=2),
    mc("Open-Meteo API uchun nima MAJBURIY?",
       ["API kalit",
        "Hech narsa — bepul va kalit shart emas",
        "OAuth",
        "Token"],
       "B", diff="Easy", pts=2),
    dd("Shahar o'zgarganda fetch qilish — useEffect bosqichlari",
       ["useEffect(() => {",
        "    const { lat, lon } = SHAHARLAR[shahar];",
        "    const ctrl = new AbortController();",
        "    setYukla(true);",
        "    fetch(url, { signal: ctrl.signal })",
        "        .then(r => r.json())",
        "        .then(d => { setData(d); setYukla(false); })",
        "        .catch(e => { if (e.name !== 'AbortError') setXato(e.message); });",
        "    return () => ctrl.abort();",
        "}, [shahar]);"],
       diff="Hard", pts=4),
    ti("Nima uchun shahar o'zgarsa useEffect deps'ga `[shahar]` qo'yamiz, lekin AbortController'ning o'zini emas?",
       "AbortController har render'da yangi yaratilsa, deps'ga qo'yish — har render'da effect "
       "ishga tushadi (cheksiz loop). Lekin biz shahar o'zgarganda faqat qaytadan fetch xohlaymiz. "
       "Deps'ga shahar qo'yamiz: shahar o'zgarsa → cleanup (eski ctrl.abort()) → yangi effect "
       "(yangi ctrl, yangi fetch). Cleanup avtomatik eski'sini bekor qilib, yangisini boshlaydi. "
       "Bu — useEffect'ning sehri.",
       hint="Cleanup va lifecycle.",
       diff="Hard", pts=4),
    mc("`data?.current?.temperature_2m` — `?.` nima qiladi va nima uchun foydali?",
       ["Sintaktik xato",
        "Optional chaining — data null bo'lsa undefined qaytaradi, xato chiqarmaydi",
        "Default qiymat",
        "Async marker"],
       "B", explanation="Fetch hali kelmaganida data — null. data.current xato bo'ladi. data?.current — xavfsiz.",
       diff="Medium", pts=3),
]
L7_EX: list = [
    mc("Custom hook nomi qanday boshlanishi shart?",
       ["with",
        "use",
        "react",
        "hook"],
       "B", explanation="React `use` prefiksini ko'rib hook deb biladi va qoidalarni qo'llaydi.",
       diff="Easy", pts=2),
    mc("Hook qoidalaridan KAMINA bittasini ayting:",
       ["Faqat top-level — if/for ichida chaqirilmaydi",
        "Faqat komponent yoki boshqa hook ichidan chaqirish mumkin",
        "Nomi `use` bilan boshlansin",
        "Hammasi to'g'ri"],
       "D", diff="Medium", pts=3),
    mc("Quyidagi kod xato. Sabab?\n```jsx\nif (login) {\n  const [val] = useState(0);\n}\n```",
       ["Sintaksis xato",
        "Hook har doim bir xil tartibda chaqirilishi kerak — if ichi yo'l qo'yilmaydi",
        "useState ichki ishlatib bo'lmaydi",
        "Hech qanday xato"],
       "B", explanation="React hook'larni tartib raqami bilan eslaydi. Shart bo'lsa — har render'da tartib o'zgaradi.",
       diff="Hard", pts=4),
    mc("`useDebounce` qachon foydali?",
       ["Hech qachon",
        "Qidiruv input — har klavishada API chaqirmaslik, foydalanuvchi to'xtaganda bir marta",
        "Faqat counter uchun",
        "Faqat fetch tezligi uchun"],
       "B", diff="Medium", pts=3),
    mc("Quyidagilardan qaysilari MAVJUD foydali custom hook'lar?",
       ["useToggle",
        "useFetch",
        "useLocalStorage",
        "useChicken",
        "useDebounce",
        "useOnClickOutside"],
       "A,B,C,E,F", multi=True,
       hint="useChicken — yo'q.",
       diff="Easy", pts=2),
    dd("useToggle hook bosqichlari",
       ["export function useToggle(initial = false) {",
        "    const [val, setVal] = useState(initial);",
        "    const toggle = useCallback(() => setVal(v => !v), []);",
        "    return [val, toggle];",
        "}"],
       diff="Medium", pts=3),
    ti("Custom hook va oddiy funksiya orasidagi farq nima?",
       "Custom hook ichida boshqa REACT HOOK'lar (useState, useEffect, va h.k.) chaqirilishi "
       "mumkin. Oddiy funksiya — yo'q (Hook qoidalariga zid). Plyus: custom hook nomi `use` "
       "bilan boshlanishi shart — bu React'ga uni hook ekanligini bildiradi va lint "
       "qoidalarini qo'llaydi. Oddiy funksiya — har qanday joydan chaqirilishi mumkin, "
       "hook — faqat komponent yoki boshqa hook ichidan.",
       hint="Hook qoidalari va boshqa hook chaqirish.",
       diff="Hard", pts=4),
]
L8_EX: list = [
    mc("React Router'da sahifaga o'tish uchun nima ishlatamiz?",
       ["<a href=...>",
        "<Link to=...>",
        "window.location.href",
        "useState"],
       "B", explanation="<a href> — sahifa qayta yuklanadi. <Link> — SPA navigatsiya.",
       diff="Easy", pts=2),
    mc("URL `/kurslar/42` da `42` ni qanday olamiz?",
       ["useNavigate()",
        "useParams() — { id } = useParams()",
        "useLocation()",
        "useSearchParams()"],
       "B", diff="Easy", pts=2),
    mc("`useSearchParams` qachon ishlatamiz?",
       ["Path parametrlari uchun (/x/:id)",
        "Query string uchun (?qidir=react&p=2)",
        "Programmatic navigation uchun",
        "404 sahifa uchun"],
       "B", diff="Medium", pts=3),
    mc("404 sahifa uchun `path` qiymati:",
       ["path=\"404\"",
        "path=\"/not-found\"",
        "path=\"*\"",
        "path={null}"],
       "C", explanation="* — wildcard, har qanday URL ga mos keladi. Ro'yxat oxirida bo'lishi shart.",
       diff="Medium", pts=3),
    mc("Login bo'lgandan keyin sahifaga o'tish:",
       ["window.location = '/profil'",
        "navigate('/profil') (useNavigate'dan)",
        "<Link to='/profil' />",
        "history.push"],
       "B", explanation="useNavigate — programmatic navigation. window.location — sahifa qayta yuklanadi.",
       diff="Medium", pts=3),
    dd("Protected route komponenti yozish",
       ["function Protected({ children }) {",
        "    const { tizimda } = useAuth();",
        "    const location = useLocation();",
        "    if (!tizimda) {",
        "        return <Navigate to='/login' state={{ dan: location.pathname }} replace />;",
        "    }",
        "    return children;",
        "}"],
       diff="Hard", pts=4),
    ti("Nested routes (Outlet bilan) qachon foydali?",
       "Bir nechta sahifa umumiy LAYOUT (header, sidebar, footer) ulashishi kerak bo'lganda. "
       "Misol: /kurslar, /kurslar/:id, /kurslar/:id/dars/:dars — hammasi kurslar sidebar'iga ega "
       "bo'lsin. KurslarLayout komponentida sidebar + <Outlet /> bo'ladi. Outlet o'rniga "
       "joriy nested route'ning komponenti render bo'ladi. Bu — parent route ichida child route. "
       "Plyus URL ham mantiqiy: /kurslar/42 = kurs ichi, /profil/sozlamalar = profil ichi.",
       hint="Layout va URL iyerarxiyasi.",
       diff="Hard", pts=4),
]
L9_EX: list = [
    mc("'Prop drilling' nima?",
       ["Props'ni o'chirish",
        "Props'ni 3-4-5 darajadan o'tib uzatish, har komponent ularni shunchaki pastga uzatadi",
        "Performance optimizatsiya",
        "React kalit so'zi"],
       "B", explanation="Context — prop drilling muammosining yechimi.",
       diff="Medium", pts=3),
    mc("`createContext` va `useContext` qaysi import'dan?",
       ["react-router",
        "redux",
        "react",
        "@context/api"],
       "C", diff="Easy", pts=2),
    mc("Provider value har render'da yangi obyekt bo'lsa nima muammo?",
       ["Hech qanday",
        "Har consumer keraksiz qayta render bo'ladi (performance)",
        "Context ishlamaydi",
        "Context xatolik chiqaradi"],
       "B", explanation="Yechim: useMemo bilan barqaror qiymat.",
       diff="Hard", pts=4),
    mc("Context qachon TO'G'RI ishlatish?",
       ["Har komponent state'i uchun",
        "Auth, tema, til kabi global, kam o'zgaradigan ma'lumotlar uchun",
        "Faqat performance optimizatsiya uchun",
        "Hech qachon"],
       "B", diff="Medium", pts=3),
    mc("Quyidagilardan qaysilari TO'G'RI Context ishlatish?",
       ["createContext + Provider + useContext",
        "Custom hook yaratish (useUser, useTheme)",
        "Provider tepada, consumer'lar pastda",
        "Har komponentda createContext qilish",
        "useMemo bilan barqaror value"],
       "A,B,C,E", multi=True,
       diff="Medium", pts=3),
    dd("UserContext yaratish bosqichlari",
       ["const UserContext = createContext(null);",
        "export function UserProvider({ children }) {",
        "    const [user, setUser] = useState(null);",
        "    const value = useMemo(() => ({ user, setUser }), [user]);",
        "    return (",
        "        <UserContext.Provider value={value}>",
        "            {children}",
        "        </UserContext.Provider>",
        "    );",
        "}",
        "export const useUser = () => useContext(UserContext);"],
       diff="Hard", pts=4),
    ti("Server state (API'dan keluvchi ma'lumotlar) uchun Context o'rniga nima yaxshiroq?",
       "TanStack Query (eski nomi: React Query) yoki SWR. Sabablar: caching, background refetch, "
       "stale-while-revalidate, mutation invalidation, loading/error states — barchasi tayyor. "
       "Context bilan qilish — har shu funksionallikni qo'l bilan yozish kerak. Tasodifan ko'p "
       "qayta fetch, race condition, eski ma'lumot — bularning hammasi TanStack Query'da hal "
       "qilingan. Context — global UI state uchun (auth, tema), TanStack Query — server data uchun.",
       hint="Caching, background refetch, mutations.",
       diff="Hard", pts=4),
]
R3_EX: list = [
    mc("Protected route foydalanuvchi tizimga kirmagan bo'lsa nima qiladi?",
       ["404 ko'rsatadi",
        "/login ga redirect qiladi va kelgan sahifani state'da saqlaydi",
        "Hech narsa",
        "Komponentni render qiladi"],
       "B", explanation="Login keyin foydalanuvchini kelgan sahifaga qaytarish — UX uchun muhim.",
       diff="Medium", pts=3),
    mc("AuthProvider'ni qaerga qo'yamiz?",
       ["Har komponent ichida",
        "BrowserRouter ichida, lekin AppContent oldida (yuqori darajada)",
        "Faqat Login sahifasida",
        "useEffect ichida"],
       "B", explanation="Provider eng yuqori darajada — har komponent useAuth chaqira oladi.",
       diff="Medium", pts=3),
    mc("Tizim sahifa qayta yuklanganda saqlanishi uchun nima qilamiz?",
       ["useState yetadi",
        "localStorage (useLocalStorage hook)",
        "Context yetadi",
        "Mumkin emas"],
       "B", explanation="State faqat xotirada, sahifa yuklanganda yo'qoladi. localStorage — diskda saqlaydi.",
       diff="Easy", pts=2),
    mc("`<Navigate to='/login' state={{ dan: location.pathname }} replace />` — `state` nima uchun?",
       ["Sahifaga ma'lumot uzatish — login keyin shu sahifaga qaytish uchun",
        "Komponent state'i",
        "Browser history",
        "useState bilan ishlatish"],
       "A", explanation="Login sahifa location.state?.dan o'qiydi va keyin shu yerga navigate qiladi.",
       diff="Hard", pts=4),
    mc("Quyidagilardan qaysilari TO'G'RI auth flow uchun?",
       ["Login button disable while submitting",
        "Xato xabarini ko'rsatish",
        "localStorage'da saqlash",
        "Har sahifa yuklanganda login API ga so'rov",
        "Protected wrapper + Navigate"],
       "A,B,C,E", multi=True,
       hint="Har sahifa yuklanganda — yo'q. JWT/token validation faqat keraganda.",
       diff="Hard", pts=4),
    dd("AuthContext'ni yaratish bosqichlari",
       ["const AuthContext = createContext(null);",
        "function AuthProvider({ children }) {",
        "    const [user, setUser] = useLocalStorage('user', null);",
        "    const login = async (email, parol) => { /* ... */ setUser({...}); };",
        "    const logout = () => setUser(null);",
        "    const value = useMemo(() => ({ user, login, logout }), [user]);",
        "    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;",
        "}",
        "const useAuth = () => useContext(AuthContext);"],
       diff="Hard", pts=4),
    ti("Production auth uchun JWT tokenni qaerda saqlash xavfsiz: localStorage yoki httpOnly cookie?",
       "httpOnly cookie — xavfsizroq. Sabab: XSS hujumi (yomon JS kod kirgan bo'lsa) "
       "localStorage'dagi tokenni o'qiy oladi va o'g'irlashi mumkin. httpOnly cookie — "
       "JavaScript'ga ko'rinmaydi, faqat browser server'ga avtomatik yuboradi. "
       "Plyus: Secure flag (faqat HTTPS), SameSite (CSRF himoya). "
       "Lekin localStorage qulayroq SPA uchun — mobile app'larda token, web — cookie. "
       "Asosiy: XSS dan saqlanish (input sanitize), CSP, va tokenni TEZ EXPIRE qilish.",
       hint="XSS xavfi va browser security.",
       diff="Hard", pts=4),
]
L10_EX: list = [
    mc("`React.memo` qanday komponent uchun foydali?",
       ["Har bir komponent",
        "Bir xil props bilan tez-tez render bo'ladigan, qimmat komponent",
        "Faqat sinflar",
        "Faqat kichik komponent"],
       "B", explanation="Memo — qachon parent qayta render bo'lsa-yu, child propsi o'zgarmagan bo'lsa.",
       diff="Medium", pts=3),
    mc("`useMemo` nima qiladi?",
       ["Komponentni cache qiladi",
        "Qiymat hisoblashni cache qiladi — deps o'zgarmasa, eski natijani qaytaradi",
        "Funksiyani cache qiladi",
        "useState'ning yangi nomi"],
       "B", diff="Easy", pts=2),
    mc("`useCallback` qachon kerakli?",
       ["Har funksiyani o'rab olish uchun",
        "Funksiyani React.memo'li child'ga uzatganda yoki useEffect deps'iga qo'shganda",
        "Faqat async funksiyalar uchun",
        "Hech qachon"],
       "B", diff="Medium", pts=3),
    mc("'Premature optimization' xavfi nima?",
       ["Tez ishlamaslik",
        "Hech sekin bo'lmagan kodga memo/useMemo qo'shish — kod og'irligi, kichik foyda",
        "useEffect ishlamasligi",
        "Bug'lar"],
       "B", explanation="Avval profile qiling, sekin bo'lganda — optimallashtiring.",
       diff="Hard", pts=4),
    mc("Quyidagilardan qaysilari TO'G'RI optimizatsiya?",
       ["React DevTools Profiler ishlatib qaerda sekin ekanligini aniqlash",
        "10000+ qator ro'yxat uchun react-window",
        "Har component'ga React.memo",
        "Code splitting — React.lazy + Suspense",
        "useMemo'ni `a + b` kabi oddiy ifoda uchun"],
       "A,B,D", multi=True,
       hint="Har component'ga memo — yomon. useMemo oddiy ifoda uchun — overhead.",
       diff="Hard", pts=4),
    dd("useCallback bilan funksiya reference barqarorligi",
       ["const Parent = () => {",
        "    const [son, setSon] = useState(0);",
        "    const onSelect = useCallback((id) => {",
        "        alert(id);",
        "    }, []);",
        "    return <Child onSelect={onSelect} />;",
        "};"],
       diff="Medium", pts=3),
    ti("Nima uchun Context Provider value'ga useMemo qo'yish katta optimizatsiya?",
       "Provider value har render'da yangi obyekt bo'lsa (`{ x, setX }` literally), "
       "har consumer (useContext ishlatuvchi komponent) ham qayta render bo'ladi. "
       "Bu — ko'p komponent har gal Parent render bo'lganida render bo'lishi. "
       "useMemo bilan value reference barqaror — faqat haqiqatan x o'zgarganida consumerlar "
       "qayta render. Sotsial media (10000 komponentli) saytlarda — bu farq sezilarli. "
       "Bu — Context'ning eng katta performance jadi.",
       hint="Reference equality va consumer re-render.",
       diff="Hard", pts=4),
]
L11_EX: list = [
    mc("Recipe Finder loyihasida frontend va backend qanday ulanadi?",
       ["WebSocket bilan",
        "REST API — Flask JSON qaytaradi, React fetch bilan oladi",
        "Bevosita ulanadi",
        "ORM bilan"],
       "B", explanation="JSON API — frontend va backend orasidagi standart aloqa.",
       diff="Easy", pts=2),
    mc("Auth uchun token'ni qaerda saqlash mumkin?",
       ["localStorage",
        "httpOnly cookie",
        "Context state (xotirada)",
        "Hammasi mumkin — har birining yaxshi va yomon tomonlari bor"],
       "D", explanation="localStorage — qulay, lekin XSS xavfi. httpOnly cookie — xavfsizroq. Context — sahifa yuklanganda yo'qoladi.",
       diff="Hard", pts=4),
    mc("CORS nima va nima uchun kerak?",
       ["Faqat backend muammosi",
        "Browser security policy — domen X ning JS si domen Y ga API so'rov yuborishi cheklangan",
        "Faqat performance",
        "React'ning xususiyati"],
       "B", explanation="Flask: CORS(app, origins=['localhost:5173']).",
       diff="Medium", pts=3),
    mc("Bu loyihada qaysi custom hook eng foydali bo'ladi?",
       ["useFetch (har sahifada API'dan ma'lumot)",
        "useDebounce (qidiruv input)",
        "useLocalStorage (token, theme, favorites)",
        "useAuth (har komponentda foydalanuvchi tekshirish)",
        "Barchasi"],
       "E", multi=False, diff="Easy", pts=2),
    mc("Loyihada qaysi pattern'lar ishlatiladi?",
       ["Protected routes (Router + Context)",
        "Controlled forms (login/register)",
        "Lists + map + key (recipes)",
        "useEffect + AbortController (qidiruv)",
        "Inline styles bilan har joyda"],
       "A,B,C,D", multi=True,
       hint="Inline styles — kichik loyihada ok, lekin CSS/Tailwind kerak.",
       diff="Hard", pts=4),
    dd("Recipes ro'yxat sahifasini render qilish bosqichlari",
       ["const [params] = useSearchParams();",
        "const qidir = params.get('q') ?? '';",
        "const debounced = useDebounce(qidir, 300);",
        "const { recipes, yukla, xato } = useRecipes({ qidir: debounced });",
        "if (yukla) return <p>Yuklanmoqda...</p>;",
        "if (xato) return <p>{xato}</p>;",
        "if (recipes.length === 0) return <p>Topilmadi</p>;",
        "return <div>{recipes.map(r => <Link key={r.id} to={`/recipes/${r.id}`}>{r.nomi}</Link>)}</div>;"],
       diff="Hard", pts=4),
    ti("Recipe Finder yakuniy loyihasini tugatgandan keyin siz nimaga tayyorsiz?",
       "Real-world React loyihalariga: protected route'lar bilan SPA, JWT auth, "
       "Context bilan global state, fetch + custom hooks bilan API integratsiya, "
       "Router bilan multi-page, forms + validation. Plyus: backend integratsiya, "
       "CORS, JWT, deploy (Vercel + Railway). CV uchun real loyiha, suhbat mavzulari. "
       "Keyingi qadam: TypeScript, TanStack Query, Tailwind/shadcn, Next.js, testlar (Vitest). "
       "Asosiy — endi siz React ekosistemasini chuqur tushunasiz, kutubxonalar — vositalar.",
       hint="CV, suhbat, va keyingi qadamlar.",
       diff="Easy", pts=2),
]


LESSON_TASKS: dict = {
    0: {
        "title": "Birinchi React loyiha — Vite bilan",
        "description": (
            "Vite bilan React loyiha ochish va o'zingizning birinchi komponentingizni yozish."
        ),
        "requirements": (
            "• `npm create vite@latest` bilan React loyiha ochish\n"
            "• `npm install` + `npm run dev`\n"
            "• `App.jsx` o'zgartirish — o'zingizning komponent\n"
            "• Kamida 3 ta JS o'zgaruvchi JSX ichida (`{ifoda}`)\n"
            "• Ternary operator bilan conditional rendering\n"
            "• Hisoblangan ustun (masalan `2 + 2`)\n"
            "• Komment ham JSX ichida (`{/* ... */}`)\n"
            "• Screenshot — terminal va brauzer"
        ),
        "technologies": "React, Vite, JSX",
        "deadline_days": 3,
    },
    1: {
        "title": "Props bilan profil kartochkasi",
        "description": "Props orqali ma'lumot uzatib, qayta ishlatish mumkin kartochka komponentini yarating.",
        "requirements": (
            "• `Card({ sarlavha, matn, rang })` komponenti\n"
            "• Default props (rang = 'kok')\n"
            "• App ichida 3-4 ta turli Card\n"
            "• `children` prop bilan `Layout` komponenti\n"
            "• `Tugma({ label, onClick })` — funksiya prop bilan\n"
            "• Rest props bilan `Input({ label, ...rest })` wrapper\n"
            "• Screenshot — ko'p Card sayfada"
        ),
        "technologies": "React, Props, destructuring, children, callbacks",
        "deadline_days": 3,
    },
    2: {
        "title": "Counter va form bilan birinchi useState",
        "description": "useState bilan ishlovchi 3 ta kichik komponent yarating.",
        "requirements": (
            "• `Counter` — +/- /reset tugmalari\n"
            "• `DarkModeSwitch` — boolean toggle (useToggle pattern)\n"
            "• `SaloLogin` — input + 'Salom, X!' (controlled input)\n"
            "• `TodoOddiy` — input + add + ro'yxat (array state)\n"
            "• Functional update misoli: `setSon(s => s + 1)`\n"
            "• Object state misoli: spread bilan yangilash\n"
            "• Ataylab xato — `onClick={setSon(son + 1)}` ko'rsatish va sabab"
        ),
        "technologies": "React, useState, event handlers, controlled inputs",
        "deadline_days": 4,
    },
    3: {  # R1
        "title": "🔁 R1: Counter + Todo list",
        "description": (
            "Modul 1 takrorlash: JSX + Props + useState birga. State lifting va "
            "kompozitsiya pattern'lari bilan ishlash."
        ),
        "requirements": (
            "• 3 ta Counter komponenti (controlled — value + onChange)\n"
            "• TodoList — qo'shish/o'chirish/toggle (id bilan)\n"
            "• App ichida state lifting (Counter state App'da)\n"
            "• Jami va qolgan to'go'lar — derived from state\n"
            "• Bo'sh holat (empty state) — \"Hech narsa yo'q\" xabari\n"
            "• Bajarilgan todo — chiziq bilan kechib o'tilgan (CSS)\n"
            "• Enter key — yangi todo qo'shish\n"
            "• Tashqi CSS yoki inline styles — chiroyli ko'rinish"
        ),
        "technologies": "React, useState, state lifting, controlled, lists",
        "deadline_days": 5,
    },
    4: {
        "title": "Mahsulot ro'yxati (conditional + lists)",
        "description": "Filter va sort bilan ishlovchi mahsulot katalogi.",
        "requirements": (
            "• Kamida 10 ta mahsulot (id, nomi, narx, kategoriya, mavjud)\n"
            "• Kategoriya filteri (radio yoki dropdown)\n"
            "• Narx oraliq slideri (yoki min/max input)\n"
            "• Bo'sh holat: \"Topilmadi\"\n"
            "• Mavjud emas: opacity 0.4 yoki maxsus belgi\n"
            "• Key — har doim mahsulot.id (index emas!)\n"
            "• Early return bilan loading/error/data\n"
            "• Switch pattern bilan UI varianti"
        ),
        "technologies": "React, conditional, lists, key, filter, map",
        "deadline_days": 4,
    },
    5: {
        "title": "Ro'yxatdan o'tish formasi",
        "description": "To'liq controlled multi-input form validation bilan.",
        "requirements": (
            "• 5-6 maydon: ism, email, parol, parol2, yosh, jins, obuna\n"
            "• Har turli element: text, email, password, number, select, radio, checkbox, textarea\n"
            "• `name` attribute + bitta universal `ozgartir` funksiyasi\n"
            "• Real-time validatsiya (har klavishada)\n"
            "• Xato xabarlari faqat submit'dan keyin\n"
            "• Submit tugmasi disabled while invalid\n"
            "• Async submit imitatsiyasi (`setTimeout`)\n"
            "• Loading state (button 'Yuklanmoqda...')\n"
            "• Muvaffaqiyat xabarini ko'rsatish"
        ),
        "technologies": "React, forms, controlled inputs, validation",
        "deadline_days": 4,
    },
    6: {
        "title": "Real-time soat va onlayn user'lar",
        "description": "useEffect bilan timer, listener va fetch.",
        "requirements": (
            "• `Soat` — har sekundda yangilanadi (setInterval + cleanup)\n"
            "• `OynaOlchami` — window resize listener (cleanup)\n"
            "• `OnlaynUserlar` — har 5 sekundda fetch (poll)\n"
            "• `Profil({ id })` — id o'zgarsa qaytadan fetch\n"
            "• AbortController bilan race condition yechimi\n"
            "• 3 ta holat: loading/error/data\n"
            "• localStorage'da tema saqlash (useEffect bilan)\n"
            "• Console.log bilan har effect'ni kuzatish"
        ),
        "technologies": "React, useEffect, cleanup, AbortController, fetch",
        "deadline_days": 5,
    },
    7: {  # R2
        "title": "🔁 R2: Weather widget",
        "description": (
            "Modul 2 takrorlash: forms + lists + conditional + useEffect + fetch "
            "birga. Real Open-Meteo API bilan."
        ),
        "requirements": (
            "• 4+ shahar (lat/lon bilan)\n"
            "• Shahar dropdown (controlled select)\n"
            "• Open-Meteo API'dan ma'lumot olish (free, key'siz)\n"
            "• 3 ta holat: yuklanmoqda/xato/data\n"
            "• Joriy harorat + ob-havo ikonkasi (emoji)\n"
            "• 5 kunlik prognoz — ro'yxat (map + key)\n"
            "• Refresh tugmasi (incrementing state pattern)\n"
            "• AbortController bilan race condition\n"
            "• Stilllash — chiroyli kartochka ko'rinishi"
        ),
        "technologies": "React, fetch, forms, conditional, lists, useEffect, race condition",
        "deadline_days": 6,
    },
    8: {
        "title": "Custom hook'lar kutubxonasi",
        "description": "5+ ta foydali custom hook yozish va portfolio'da ishlatish.",
        "requirements": (
            "• `useToggle` — boolean toggle\n"
            "• `useLocalStorage` — generic localStorage saver\n"
            "• `useFetch` — universal API hook (loading/error/data + AbortController)\n"
            "• `useDebounce` — kechiktirilgan qiymat\n"
            "• `useOnClickOutside` — modal/dropdown uchun\n"
            "• `useMediaQuery` — responsive\n"
            "• Har biri alohida `.js` faylda (`hooks/` papka)\n"
            "• Har biriga JSDoc komment\n"
            "• Demo sahifa — har hook'ni ishlatish misoli"
        ),
        "technologies": "React, custom hooks, useState, useEffect, useRef",
        "deadline_days": 5,
    },
    9: {
        "title": "Multi-page sayt (React Router)",
        "description": "5+ sahifali sayt routing bilan.",
        "requirements": (
            "• 5+ sahifa: /, /kurslar, /kurslar/:id, /qidir, /profil, /404\n"
            "• `<Link>` (NavLink bilan active style)\n"
            "• `useParams` bilan dinamik parametr\n"
            "• `useSearchParams` bilan qidiruv (?q=, ?p=)\n"
            "• `useNavigate` — login keyin programmatic\n"
            "• Nested route + `<Outlet />`\n"
            "• 404 sahifasi (path=\"*\")\n"
            "• Protected route imitatsiyasi\n"
            "• Browser back/forward to'g'ri ishlasin"
        ),
        "technologies": "React Router, Routes, Link, useParams, useNavigate",
        "deadline_days": 6,
    },
    10: {
        "title": "Global state (Context) bilan e-shop",
        "description": "AuthContext + ThemeContext + CartContext bilan kichik e-shop.",
        "requirements": (
            "• `UserContext` — login/logout, localStorage saqlash\n"
            "• `ThemeContext` — yorug'/qorong'i (CSS variables)\n"
            "• `CartContext` — qo'shish/o'chirish/tozalash\n"
            "• Custom hook'lar: `useUser`, `useTheme`, `useCart`\n"
            "• Provider value — `useMemo` bilan barqaror\n"
            "• Header — bevosita context'lardan ma'lumot\n"
            "• Mahsulot kartochkasi — bevosita useCart\n"
            "• Savatcha sahifa — items + jami\n"
            "• Custom hook'lar Provider tashqarisida xato chiqarsin"
        ),
        "technologies": "React Context, Provider pattern, useMemo, custom hooks",
        "deadline_days": 6,
    },
    11: {  # R3
        "title": "🔁 R3: Auth flow + protected routes",
        "description": (
            "Modul 3 takrorlash: custom hooks + Context + Router birga. Real auth pattern."
        ),
        "requirements": (
            "• `useLocalStorage` hook\n"
            "• `AuthContext` (login, logout, useLocalStorage bilan persist)\n"
            "• Login form — controlled, validation, loading, error\n"
            "• `Protected` wrapper komponenti\n"
            "• `<Navigate state={{ dan: ... }} />` bilan return-to pattern\n"
            "• Public sahifalar: /, /kurslar\n"
            "• Private sahifalar: /profil, /sozlamalar\n"
            "• Header — auth state ga qarab ko'rinish\n"
            "• Sahifa qayta yuklanganda tizimda qolish\n"
            "• 404 sahifa"
        ),
        "technologies": "React, Context, Router, custom hooks, JWT pattern, localStorage",
        "deadline_days": 7,
    },
    12: {
        "title": "Performance optimizatsiya laboratoriyasi",
        "description": "Sekin app yarating va optimallashtiring (3x tezroq).",
        "requirements": (
            "• 1000+ qator ro'yxat\n"
            "• Qidiruv + filter + sort\n"
            "• React DevTools Profiler bilan o'lchov (avval)\n"
            "• `React.memo` — Card komponentlari\n"
            "• `useMemo` — qimmat filter/sort\n"
            "• `useCallback` — onClick handler'lar\n"
            "• `React.lazy` + Suspense bilan code splitting\n"
            "• Premature optimization xato misoli\n"
            "• Profile o'lchovi: avval va keyin (screenshot)\n"
            "• Hisobotda: nima va nima uchun tezlandi"
        ),
        "technologies": "React.memo, useMemo, useCallback, React.lazy, Suspense, Profiler",
        "deadline_days": 6,
    },
    13: {  # L11 — CAPSTONE
        "title": "🚀 CAPSTONE: Recipe Finder (React + Flask)",
        "description": (
            "Kursning yakuniy fullstack loyihasi: React frontend + Flask backend "
            "bilan to'liq ishlovchi resept qidiruv ilovasi. 3 hafta."
        ),
        "requirements": (
            "Frontend (React):\n"
            "• Vite + React + React Router\n"
            "• AuthContext (JWT, useLocalStorage)\n"
            "• 7+ sahifa (bosh, recipes, detail, favorites, profile, login, register, 404)\n"
            "• Protected routes\n"
            "• useFetch, useDebounce, useLocalStorage custom hooks\n"
            "• Controlled forms (login, register, comment)\n"
            "• Conditional rendering (loading/error/empty/data)\n"
            "• useEffect + AbortController\n"
            "• React.memo bilan optimizatsiya\n"
            "• Responsive (mobile/tablet/desktop)\n"
            "• Dark mode (Context)\n"
            "\n"
            "Backend (Flask):\n"
            "• /api/auth/{register, login} — JWT\n"
            "• /api/recipes — GET (filter, qidiruv, sahifalash)\n"
            "• /api/recipes/:id — GET\n"
            "• /api/favorites — GET/POST/DELETE (JWT)\n"
            "• /api/recipes/:id/comments — GET/POST (JWT)\n"
            "• PostgreSQL + SQLAlchemy\n"
            "• CORS sozlangan\n"
            "\n"
            "Bonus:\n"
            "• TanStack Query, Tailwind, Vitest testlar\n"
            "• Deploy: Vercel (FE) + Railway/Render (BE)\n"
            "• Hisobot: README + arxitektura diagrammasi"
        ),
        "technologies": (
            "React, Vite, React Router, Context, custom hooks, fetch, JWT, "
            "Flask, SQLAlchemy, PostgreSQL, CORS, deploy"
        ),
        "deadline_days": 21,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Lessons list
# ─────────────────────────────────────────────────────────────────────────────
LESSONS = [
    {"order": 0,  "title": "1-Vite + birinchi komponent (JSX)",
     "text": None, "code": None, "lang": "jsx",
     "video": "https://youtu.be/SqcY0GlETPk", "exercises": L1_EX, "_ref": "L1"},
    {"order": 1,  "title": "2-Props va kompozitsiya",
     "text": None, "code": None, "lang": "jsx",
     "video": "https://youtu.be/m7OWXtbiXX8", "exercises": L2_EX, "_ref": "L2"},
    {"order": 2,  "title": "3-useState va event handler'lar",
     "text": None, "code": None, "lang": "jsx",
     "video": "https://youtu.be/O6P86uwfdR0", "exercises": L3_EX, "_ref": "L3"},
    {"order": 3,  "title": "R1-Counter + Todo list (takrorlash)",
     "text": None, "code": None, "lang": "jsx",
     "video": "https://youtu.be/hQAHSlTtcmY", "exercises": R1_EX, "_ref": "R1"},
    {"order": 4,  "title": "4-Conditional rendering va lists (key)",
     "text": None, "code": None, "lang": "jsx",
     "video": "https://youtu.be/7lhWvJBYZ8c", "exercises": L4_EX, "_ref": "L4"},
    {"order": 5,  "title": "5-Forms va controlled inputs",
     "text": None, "code": None, "lang": "jsx",
     "video": "https://youtu.be/SdzMBWT2CDQ", "exercises": L5_EX, "_ref": "L5"},
    {"order": 6,  "title": "6-useEffect va lifecycle",
     "text": None, "code": None, "lang": "jsx",
     "video": "https://youtu.be/0ZJgIjIuY7U", "exercises": L6_EX, "_ref": "L6"},
    {"order": 7,  "title": "R2-Weather widget (takrorlash)",
     "text": None, "code": None, "lang": "jsx",
     "video": "https://youtu.be/eFGC_n_kVfg", "exercises": R2_EX, "_ref": "R2"},
    {"order": 8,  "title": "7-Custom hooks",
     "text": None, "code": None, "lang": "jsx",
     "video": "https://youtu.be/6ThXsUwLWvc", "exercises": L7_EX, "_ref": "L7"},
    {"order": 9,  "title": "8-React Router (sahifa navigatsiyasi)",
     "text": None, "code": None, "lang": "jsx",
     "video": "https://youtu.be/Ul3y1LXxzdU", "exercises": L8_EX, "_ref": "L8"},
    {"order": 10, "title": "9-Context API (global state)",
     "text": None, "code": None, "lang": "jsx",
     "video": "https://youtu.be/HYKDUF8X3qI", "exercises": L9_EX, "_ref": "L9"},
    {"order": 11, "title": "R3-Auth flow + protected routes (takrorlash)",
     "text": None, "code": None, "lang": "jsx",
     "video": "https://youtu.be/2UfbpJaNZx8", "exercises": R3_EX, "_ref": "R3"},
    {"order": 12, "title": "10-Performance: memo, useMemo, useCallback",
     "text": None, "code": None, "lang": "jsx",
     "video": "https://youtu.be/THL1OPn72vo", "exercises": L10_EX, "_ref": "L10"},
    {"order": 13, "title": "11-CAPSTONE: Recipe finder (React + Flask)",
     "text": None, "code": None, "lang": "jsx",
     "video": "https://youtu.be/bMknfKXIFA8", "exercises": L11_EX, "_ref": "L11"},
]


def _resolve_lessons() -> None:
    g = globals()
    for row in LESSONS:
        ref = row["_ref"]
        row["text"] = g[f"{ref}_TEXT"]
        row["code"] = g[f"{ref}_CODE"]


def _jdump(value):
    if value is None or value == "":
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_sections_json(lesson: dict, exercise_rows: list[Exercise]) -> str:
    sections = [
        {"id": f"t{lesson['order']}", "type": "text", "label": "Текст",
         "html": lesson["text"], "order": 0},
        {"id": f"c{lesson['order']}", "type": "code", "label": "Код",
         "code": lesson["code"], "lang": lesson["lang"], "order": 1},
        {"id": f"v{lesson['order']}", "type": "video", "label": "Видео",
         "videoUrl": lesson["video"], "order": 2},
        {"id": f"e{lesson['order']}", "type": "exercise", "label": "Упражнения",
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
         "order": 3},
    ]
    return json.dumps(sections, ensure_ascii=False)


async def seed(dry_run: bool = False) -> None:
    _resolve_lessons()

    async with AsyncSessionLocal() as db:
        existing = (
            await db.execute(select(Course).where(Course.title == COURSE["title"]))
        ).scalar_one_or_none()
        if existing:
            print(f"Course '{COURSE['title']}' already exists (id={existing.id}). "
                  f"Delete it first if you want to re-seed.")
            return

        course = Course(**COURSE)
        db.add(course)
        await db.flush()
        print(f"Created course: id={course.id}  title='{course.title}'")

        for ldata in LESSONS:
            task = LESSON_TASKS.get(ldata["order"], {})
            lesson = Lesson(
                course_id=course.id,
                title=ldata["title"],
                order=ldata["order"],
                points_reward=10,
                text_content=ldata["text"],
                code_content=ldata["code"],
                code_language=ldata["lang"],
                video_url=ldata["video"],
                sections_json=None,
                task_title=task.get("title"),
                task_description=task.get("description"),
                task_requirements=task.get("requirements"),
                task_technologies=task.get("technologies"),
                task_deadline_days=task.get("deadline_days"),
                is_active=True,
                is_published=True,
            )
            db.add(lesson)
            await db.flush()

            ex_rows: list[Exercise] = []
            for ex_order, ex in enumerate(ldata["exercises"]):
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

            lesson.sections_json = build_sections_json(ldata, ex_rows)
            print(f"  lesson order={lesson.order:>2} id={lesson.id:>3}  "
                  f"{lesson.title:<55}  exercises={len(ex_rows)}")

        if dry_run:
            await db.rollback()
            print("\nDRY RUN — rolled back, nothing written.")
        else:
            await db.commit()
            print(f"\nSeeded course '{COURSE['title']}' with "
                  f"{len(LESSONS)} lessons and "
                  f"{sum(len(l['exercises']) for l in LESSONS)} exercises.")

    await engine.dispose()


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    asyncio.run(seed(dry_run=dry))
