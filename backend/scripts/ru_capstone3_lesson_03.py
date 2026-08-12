"""Russian translation for Capstone 3: Flask + JavaScript + Telegram Bot, lesson order=2 (L3)."""
from __future__ import annotations
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from write_ru_translations import translate_lesson, translate_exercises  # noqa: E402

LESSON_ID = 762

TITLE_RU = "3-Vanilla JS frontend"

TEXT_RU = """\
<h2>Этап 3: Vanilla JS frontend — обслуживается через Flask</h2>

<pre class="mermaid">
flowchart LR
    HTML["templates/index.html"] -->|Flask render_template| BROWSER["Браузер"]
    BROWSER -->|fetch('/api/expenses')| SAMEORIGIN["Один origin - CORS не нужен!"]
    RENDER["Рендер списка"] -->|цикл с var| BUG["Все кнопки указывают на ПОСЛЕДНИЙ элемент"]
</pre>

<p>Как мы решили в уроке 1, vanilla JS не требует сборки — поэтому на этом этапе frontend обслуживается напрямую <strong>самим Flask</strong>. Это полностью устраняет проблему CORS, но вы познакомитесь с собственной, <strong>классической</strong> проблемой vanilla JS.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — показ статичной страницы в Flask</h4>
<pre><code># app/routes.py
from flask import render_template

@api.route('/')
def bosh_sahifa():
    return render_template('index.html')   # ❗ показывает templates/index.html

# app/templates/index.html
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
  &lt;link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"&gt;
&lt;/head&gt;
&lt;body&gt;
  &lt;ul id="xarajatlar-royxati"&gt;&lt;/ul&gt;
  &lt;script src="{{ url_for('static', filename='app.js') }}"&gt;&lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>

<h4>БЛОК 2 — получение и рендер данных через vanilla JS</h4>
<pre><code>// app/static/app.js
async function xarajatlarniYuklash() {
  const javob = await fetch('/api/expenses');       // ❗ ОТНОСИТЕЛЬНЫЙ адрес - CORS не нужен, один origin!
  const xarajatlar = await javob.json();

  const royxat = document.getElementById('xarajatlar-royxati');
  royxat.innerHTML = '';

  xarajatlar.forEach((x) => {                        // ❗ forEach - даёт каждому элементу свой 'x'
    const li = document.createElement('li');
    li.textContent = `${x.tavsif}: ${x.summa} so'm`;
    royxat.appendChild(li);
  });
}

xarajatlarniYuklash();</code></pre>

<h4>БЛОК 3 — добавление отдельной кнопки каждому элементу (ПРАВИЛЬНО с let)</h4>
<pre><code>function royxatniChizish(xarajatlar) {
  const royxat = document.getElementById('xarajatlar-royxati');
  royxat.innerHTML = '';

  for (let i = 0; i &lt; xarajatlar.length; i++) {      // ❗ 'let' - у каждой итерации СВОЙ 'i'
    const x = xarajatlar[i];
    const li = document.createElement('li');
    li.textContent = `${x.tavsif}: ${x.summa} so'm `;

    const ochirishTugmasi = document.createElement('button');
    ochirishTugmasi.textContent = "O'chirish";
    ochirishTugmasi.addEventListener('click', () => {
      xarajatniOchirish(x.id);                        // ❗ благодаря 'let' - КАЖДАЯ кнопка указывает на СВОЙ x.id
    });

    li.appendChild(ochirishTugmasi);
    royxat.appendChild(li);
  }
}</code></pre>

<h3>🐛 Намеренная ошибка — использование 'var' вместо 'let' для переменной цикла</h3>
<pre><code>function royxatniChizishXato(xarajatlar) {
  for (var i = 0; i &lt; xarajatlar.length; i++) {      // ❌ использован 'var'!
    const x = xarajatlar[i];
    const li = document.createElement('li');
    li.textContent = x.tavsif;

    const tugma = document.createElement('button');
    tugma.addEventListener('click', () => {
      console.log(i);   // ❌ при нажатии ЛЮБОЙ кнопки - всегда выводит ПОСЛЕДНЕЕ значение 'i'!
    });
    li.appendChild(tugma);
    royxat.appendChild(li);
  }
}
// Если 5 расходов, ВСЕ 5 кнопок выведут "4" (последний индекс) -
// хотя они находятся в разных строках!</code></pre>

<p><strong>Результат:</strong> переменная, объявленная через <code>var</code>, существует <strong>на уровне функции</strong> (function-scoped) &mdash; после завершения цикла остаётся <strong>одна</strong> переменная <code>i</code>, и она имеет <strong>последнее</strong> значение цикла. Все callback'и <code>addEventListener</code> "прилипают" (closure) к этой <strong>одной, общей</strong> <code>i</code>, поэтому независимо от того, когда нажата кнопка, все они видят <strong>последнее</strong> значение. <code>let</code> же создаёт <strong>новую, отдельную</strong> переменную для <strong>каждой итерации</strong> &mdash; поэтому каждый callback получает своё "замороженное" значение.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему на этот раз CORS не нужен?</h4>
<p>Frontend (<code>index.html</code>, <code>app.js</code>) и backend (<code>/api/expenses</code>) обслуживаются <strong>с одного</strong> сервера Flask, с <strong>одного</strong> origin (домен+порт). Same-Origin Policy браузера касается только запросов между <strong>разными</strong> origin — здесь такой разницы вообще нет.</p>

<h4>2. Что такое closure?</h4>
<p>Closure — свойство функции "запоминать" <strong>внешние переменные</strong> в момент своего создания. Каждая callback-функция, переданная в <code>addEventListener</code>, "запоминает" переменную <code>i</code> (или <code>x</code>) того момента, но <strong>какую именно</strong> <code>i</code> она запомнит, зависит от <code>var</code> или <code>let</code>.</p>

<h4>3. Почему <code>let</code> решает эту проблему?</h4>
<p><code>let</code> работает <strong>на уровне блока</strong> (block-scoped) &mdash; на каждой итерации цикла <code>for</code> <code>let i</code> создаёт <strong>новую копию</strong>. Поэтому каждый callback "прилипает" к своей <strong>отдельной</strong> копии <code>i</code>, а не к общему, последнему значению.</p>

<h4>4. Почему эта ошибка часто выглядит "случайной"?</h4>
<p>Код <strong>во время написания</strong> выглядит рабочим — список отрисовывается правильно, кнопки тоже видны. Проблема проявляется только когда пользователь <strong>нажимает кнопку</strong>, и результат всегда относится к <strong>последнему</strong> элементу — это усложняет отладку, так как ошибка проявляется не во время написания кода, а во время действия пользователя.</p>

<h4>5. Почему эта ошибка не возникает с <code>forEach</code>?</h4>
<p><code>x</code> в <code>forEach((x) => {...})</code> передаётся как <strong>новый</strong> параметр при каждом вызове (параметры функций JavaScript всегда работают так), поэтому с <code>forEach</code> эта проблема естественным образом не возникает. Проблема появляется только в написанном вручную цикле <code>for (var i = ...)</code>, когда напрямую обращаются к внешней переменной <code>i</code>.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Для frontend/backend, обслуживаемых с одного origin, CORS не нужен</li>
<li>✅ Closure — свойство функции "запоминать" внешние переменные</li>
<li>✅ <code>var</code> — function-scoped (одна общая копия), <code>let</code> — block-scoped (отдельная копия для каждой итерации)</li>
<li>✅ При работе с обработчиками событий в цикле <code>for</code> всегда нужно использовать <code>let</code>, а не <code>var</code></li>
<li>✅ В <code>forEach</code> эта проблема не возникает, так как параметр передаётся заново при каждом вызове</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 3: Vanilla JS frontend - обслуживается через Flask
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) app/static/app.js - получение и рендер данных
// ─────────────────────────────────────────────────────────────────────

async function xarajatlarniYuklash() {
  const javob = await fetch('/api/expenses');
  const xarajatlar = await javob.json();
  royxatniChizish(xarajatlar);
}

// ─────────────────────────────────────────────────────────────────────
// 2) ПРАВИЛЬНО: цикл с let - каждая кнопка указывает на свой x.id
// ─────────────────────────────────────────────────────────────────────

function royxatniChizish(xarajatlar) {
  const royxat = document.getElementById('xarajatlar-royxati');
  royxat.innerHTML = '';

  for (let i = 0; i < xarajatlar.length; i++) {
    const x = xarajatlar[i];
    const li = document.createElement('li');
    li.textContent = `${x.tavsif}: ${x.summa} so'm `;

    const ochirishTugmasi = document.createElement('button');
    ochirishTugmasi.textContent = "O'chirish";
    ochirishTugmasi.addEventListener('click', () => {
      xarajatniOchirish(x.id);
    });

    li.appendChild(ochirishTugmasi);
    royxat.appendChild(li);
  }
}

async function xarajatniOchirish(id) {
  await fetch(`/api/expenses/${id}`, { method: 'DELETE' });
  xarajatlarniYuklash();
}

xarajatlarniYuklash();

// ─────────────────────────────────────────────────────────────────────
// 3) Намеренная ошибка - цикл с 'var' (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// function royxatniChizishXato(xarajatlar) {
//   for (var i = 0; i < xarajatlar.length; i++) {   // использован var!
//     const tugma = document.createElement('button');
//     tugma.addEventListener('click', () => {
//       console.log(i);   // ВСЕГДА выводит последнее значение!
//     });
//   }
// }
"""

EX = {
    4414: {
        "title": "Почему на этот раз CORS не нужен?",
        "description": "Почему в MoneyLog между vanilla JS frontend и Flask API не нужно настраивать CORS?",
        "hint": "CORS нужен только между РАЗНЫМИ origin.",
        "explanation": "Так как frontend (index.html, app.js) и backend (/api/expenses) обслуживаются с одного и того же Flask-сервера, с одного origin, Same-Origin Policy к этому не применяется.",
    },
    4415: {
        "title": "Основная разница между var и let",
        "description": "В чём основная разница между использованием var и let в цикле for?",
        "hint": "Это создаёт большую разницу при работе с closure.",
        "explanation": "var является function-scoped, создавая одну общую переменную для всего цикла. let же является block-scoped, создавая новую, отдельную копию для каждой итерации.",
    },
    4416: {
        "title": "Расположите процесс работы royxatniChizish()",
        "description": "Расположите процесс от вызова xarajatlarniYuklash() до правильного рендера списка и кнопок.",
        "hint": "",
        "explanation": "",
    },
    4417: {
        "title": "Метод, при котором эта проблема не возникает",
        "description": "Какой метод массива вместо for (var i = ...) естественным образом предотвращает эту проблему closure? (напишите название)",
        "hint": "",
        "expected_answer": "forEach",
    },
    4418: {
        "title": "Почему с var все кнопки указывают на последнее значение?",
        "description": (
            "Если к каждой кнопке, созданной в цикле for (var i = 0; ...), "
            "добавить addEventListener('click', () => console.log(i)), "
            "почему ВСЕ кнопки при нажатии выводят одно и то же, "
            "ПОСЛЕДНЕЕ значение i? Объясните своими словами."
        ),
        "hint": "var является function-scoped - создаёт ли цикл НОВУЮ переменную на каждой итерации, или изменяет одну общую?",
        "expected_answer": "Переменная, объявленная ключевым словом var, является function-scoped, то есть существует на уровне всей функции (или глобально) — цикл не создаёт НОВУЮ i каждый раз, а изменяет одну, ОБЩУЮ переменную i. После завершения цикла эта единственная переменная i остаётся с последним значением. Callback-функция, переданная каждому addEventListener, через closure \"указывает\" именно на эту ОДНУ, общую переменную i (не копирует её, а хранит ссылку на неё). Поэтому какую бы кнопку ни нажал пользователь, все callback'и показывают одно и то же значение, оставшееся в конце цикла.",
    },
}


async def _run():
    async with AsyncSessionLocal() as db:
        lesson = (await db.execute(select(Lesson).where(Lesson.id == LESSON_ID))).scalar_one()
        ex_rows = (
            await db.execute(select(Exercise).where(Exercise.id.in_(EX.keys())))
        ).scalars().all()

        section_map = {"Текст": "Текст", "Код": "Код", "Упражнения": "Упражнения"}
        section_map[lesson.text_content] = TEXT_RU
        section_map[lesson.code_content] = CODE_RU
        TASK_TITLE_RU = "MoneyLog — Vanilla JS frontend подключён к Flask"
        TASK_DESCRIPTION_RU = (
            "Создайте templates/index.html и static/app.js. Покажите главную "
            "страницу через Flask, получите список расходов через fetch() и "
            "отрендерите в DOM. Правильно привяжите кнопку удаления к каждому "
            "расходу через let."
        )
        TASK_REQUIREMENTS_RU = (
            "• app/templates/index.html — CSS/JS подключены через url_for('static', ...)\n"
            "• app/static/app.js — получает данные через fetch('/api/expenses')\n"
            "• Список правильно рендерится в DOM (через innerHTML или createElement)\n"
            "• К каждому расходу добавлена кнопка удаления, ПРАВИЛЬНО привязанная к своему id через let\n"
            "• Отдельная настройка CORS ОТСУТСТВУЕТ (работает с одного origin)\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "HTML, CSS, Vanilla JavaScript, Flask (render_template)"
        if lesson.task_title:
            section_map[lesson.task_title] = TASK_TITLE_RU
        if lesson.task_description:
            section_map[lesson.task_description] = TASK_DESCRIPTION_RU
        for ex in ex_rows:
            for field_name, translated in EX[ex.id].items():
                source = getattr(ex, field_name)
                if source:
                    section_map[source] = translated

        await translate_lesson(
            db, LESSON_ID,
            flat_fields={
                "title": TITLE_RU,
                "text_content": TEXT_RU,
                "task_title": TASK_TITLE_RU,
                "task_description": TASK_DESCRIPTION_RU,
                "task_requirements": TASK_REQUIREMENTS_RU,
                "task_technologies": TASK_TECHNOLOGIES_RU,
            },
            section_translations=section_map,
        )
        await translate_exercises(db, EX)
        await db.commit()
        print(f"Lesson {LESSON_ID}: wrote {len(section_map)} section strings")


if __name__ == "__main__":
    asyncio.run(_run())
