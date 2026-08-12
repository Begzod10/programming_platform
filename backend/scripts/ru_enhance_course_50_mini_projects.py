"""Russian translations for the enhance_course_50_mini_projects.py content additions."""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))  # noqa: E402

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402
from write_ru_translations import _write  # noqa: E402

MARKER_RU = "🐛 Намеренная ошибка"

BUG_HTML_RU = {
    480: f"""<h3>{MARKER_RU}</h3>
<p>Ученик делает таблицу, но забывает про <code>border-collapse</code>:</p>
<pre><code class="lang-css">table, th, td {{ border: 1px solid black; }}</code></pre>
<p><strong>Результат:</strong> границы таблицы выглядят <strong>двойными</strong> (каждая ячейка рисует свою границу отдельно, между ними остаётся зазор) — вместо ожидаемых единых линий получается странный эффект "двойной линии".</p>
<p><strong>Правильное решение:</strong> добавить <code>table {{ border-collapse: collapse; }}</code> — это объединяет границы соседних ячеек в <strong>одну линию</strong>.</p>""",
    481: f"""<h3>{MARKER_RU}</h3>
<p>Ученик добавляет <code>backdrop-filter: blur()</code>, но эффект не виден:</p>
<pre><code class="lang-css">.karta {{
  backdrop-filter: blur(10px);
  background-color: white;
}}</code></pre>
<p><strong>Результат:</strong> никакого эффекта "матового стекла" (glassmorphism) не видно — фон остаётся обычным белым! Причина: <code>backdrop-filter</code> размывает то, что находится ЗА элементом, но если собственный фон элемента <strong>полностью непрозрачный</strong> (здесь — <code>white</code>, 100% сплошной цвет), размытый фон <strong>не виден</strong>, потому что его перекрывает сплошной белый цвет сверху.</p>
<p><strong>Правильное решение:</strong> сделать фон <strong>полупрозрачным</strong>: <code>background-color: rgba(255, 255, 255, 0.3);</code>.</p>""",
    482: f"""<h3>{MARKER_RU}</h3>
<p>Ученик прикрепляет навигацию через <code>position: sticky</code>:</p>
<pre><code class="lang-css">.nav {{ position: sticky; top: 0; }}</code></pre>
<p>Но родитель nav написан так: <code>.header-wrapper {{ overflow: hidden; }}</code></p>
<p><strong>Результат:</strong> при скролле nav <strong>не прилипает</strong>, а исчезает наверху как обычный элемент! Причина: <code>position: sticky</code> работает только если ни у одного из родительских элементов нет <code>overflow: hidden</code>, <code>auto</code> или <code>scroll</code> — эти свойства ограничивают "область прилипания" sticky-элемента, превращая его в обычный элемент.</p>
<p><strong>Правильное решение:</strong> убрать <code>overflow</code> у родительских элементов, либо, если он нужен для другой цели, перенести sticky-элемент в другой контейнер без overflow.</p>""",
    483: f"""<h3>{MARKER_RU}</h3>
<p>Ученик добавляет тень (shadow) карточке:</p>
<pre><code class="lang-css">.karta {{ box-shadow: 0 4px 12px rgba(0,0,0,0.2); }}
.karta-konteyner {{ overflow: hidden; }}</code></pre>
<p><strong>Результат:</strong> тень карточки <strong>обрезается</strong> — видна только сверху и слева, снизу и справа исчезает! Причина: <code>box-shadow</code> визуально выходит <strong>за границы</strong> элемента, но если у родительского контейнера <code>overflow: hidden</code>, всё, что выходит за его границы (в том числе тень), <strong>обрезается</strong>.</p>
<p><strong>Правильное решение:</strong> если overflow не нужен — уберите его. Если нужен для другой цели (например, скругления углов изображения), дайте тень <strong>отдельному, внешнему</strong> элементу.</p>""",
    484: f"""<h3>{MARKER_RU}</h3>
<p>Ученик размещает 3 карточки разной высоты во flex-ряд:</p>
<pre><code class="lang-css">.konteyner {{ display: flex; }}</code></pre>
<p><strong>Результат:</strong> все карточки — независимо от количества текста — <strong>растягиваются до одинаковой</strong> (самой высокой) высоты, хотя этого никто не просил! Причина: стандартное значение <code>align-items</code> у flex-контейнера — <code>stretch</code> — оно <strong>растягивает все flex-элементы</strong> до одинаковой высоты, если не указано иное.</p>
<p><strong>Правильное решение:</strong> если карточки должны сохранять свою естественную высоту, нужно задать <code>align-items: flex-start;</code>.</p>""",
    485: f"""<h3>{MARKER_RU}</h3>
<p>Ученик размещает ценник поверх изображения через <code>position: absolute</code>:</p>
<pre><code class="lang-css">.narx-yorlik {{ position: absolute; top: 10px; right: 10px; }}</code></pre>
<p><strong>Результат:</strong> ценник оказывается не в углу изображения, а <strong>в правом верхнем углу всей страницы</strong>! Причина: <code>position: absolute</code> позиционирует элемент относительно ближайшего <strong>positioned</strong> (то есть с <code>position: relative/absolute/fixed</code>) родителя. Если такого родителя нет, элемент позиционируется относительно <code>&lt;body&gt;</code>.</p>
<p><strong>Правильное решение:</strong> дать контейнеру изображения <code>position: relative;</code> — тогда absolute-ценник будет позиционироваться именно относительно него.</p>""",
    486: f"""<h3>{MARKER_RU}</h3>
<p>Ученик задаёт значок (badge) поверх карточки через <code>z-index</code>:</p>
<pre><code class="lang-css">.badge {{ z-index: 999; top: -10px; right: -10px; }}</code></pre>
<p><strong>Результат:</strong> badge всё равно остаётся "скрытым" под карточкой, хотя <code>z-index: 999</code> — очень большое значение! Причина: свойство <code>z-index</code> работает <strong>только</strong> если элементу задано свойство <code>position</code> (<code>relative</code>, <code>absolute</code>, <code>fixed</code> или <code>sticky</code>). При <code>position: static</code> (значение по умолчанию) <code>z-index</code> не оказывает никакого эффекта.</p>
<p><strong>Правильное решение:</strong> <code>.badge {{ position: absolute; z-index: 999; ... }}</code> — обязательно указать <code>position</code>.</p>""",
    487: f"""<h3>{MARKER_RU}</h3>
<p>Ученик создаёт кнопку, которая должна всегда быть видна вверху страницы:</p>
<pre><code class="lang-css">.card-wrapper {{ transform: translateY(0); }}  /* для анимации */
.tugma {{ position: fixed; top: 20px; right: 20px; }}</code></pre>
<p><strong>Результат:</strong> вместо "прилипания" к экрану при скролле, <code>.tugma</code> двигается как обычный элемент <strong>внутри</strong> <code>.card-wrapper</code>! Причина: если у родительского элемента применён <code>transform</code> (даже такое "ничего не делающее" значение, как <code>translateY(0)</code>!), он создаёт <strong>новый containing block</strong> — и <code>position: fixed</code> теперь считается не относительно viewport, а относительно этого самого родителя.</p>
<p><strong>Правильное решение:</strong> убрать <code>transform</code> у родителей fixed-элемента, либо вынести fixed-элемент в совершенно другой контейнер (без transform).</p>""",
    488: f"""<h3>{MARKER_RU}</h3>
<p>Ученик пишет <code>&lt;label&gt;</code> и <code>&lt;input&gt;</code> в форме логина так:</p>
<pre><code class="lang-html">&lt;label&gt;Имя пользователя&lt;/label&gt;
&lt;input type="text" id="username"&gt;</code></pre>
<p><strong>Результат:</strong> при клике на текст label фокус на поле ввода <strong>не переходит</strong> — пользователь обязан кликнуть именно на сам input. Это небольшая, но реальная проблема UX/доступности: для пользователей скринридеров эти два элемента тоже считаются несвязанными.</p>
<p><strong>Правильное решение:</strong> <code>&lt;label for="username"&gt;</code> — указать атрибут <code>for</code>, соответствующий <code>id</code> input'а. Тогда клик по label автоматически ставит фокус на поле.</p>""",
    489: f"""<h3>{MARKER_RU}</h3>
<p>Ученик пишет форму регистрации так:</p>
<pre><code class="lang-html">&lt;input type="email" id="email" placeholder="Email"&gt;
&lt;input type="password" id="password" placeholder="Parol"&gt;
&lt;button type="submit"&gt;Зарегистрироваться&lt;/button&gt;</code></pre>
<p><strong>Результат:</strong> при отправке формы сервер не получает никаких данных — <code>request.form</code> приходит пустым! Причина: у обоих <code>&lt;input&gt;</code> <strong>нет атрибута <code>name</code></strong>. При отправке формы браузер отправляет на сервер только поля с атрибутом <code>name</code> — <code>id</code> нужен только для frontend/CSS/JS, на сервер он <strong>вообще не передаётся</strong>.</p>
<p><strong>Правильное решение:</strong> добавить атрибут <code>name</code> каждому input: <code>&lt;input type="email" id="email" name="email"&gt;</code>.</p>""",
    490: f"""<h3>{MARKER_RU}</h3>
<p>Ученик хочет анимировать высоту при открытии/закрытии меню:</p>
<pre><code class="lang-css">.menu {{ height: 0; overflow: hidden; transition: height 0.3s; }}
.menu.ochiq {{ height: auto; }}</code></pre>
<p><strong>Результат:</strong> меню открывается <strong>не плавно, а скачком</strong> — transition как будто вообще не работает! Причина: CSS <code>transition</code> может плавно анимировать только между двумя <strong>конкретными числовыми</strong> значениями. <code>height: auto</code> — не конкретное число, а значение, "вычисляемое по контенту", поэтому браузер не может анимировать переход от/к нему — он происходит мгновенно (скачком).</p>
<p><strong>Правильное решение:</strong> задать примерную конкретную высоту (<code>max-height: 500px;</code> с достаточно большим значением) или через JavaScript измерить реальный <code>scrollHeight</code> и анимировать его как точное значение в пикселях.</p>""",
    491: f"""<h3>{MARKER_RU}</h3>
<p>Ученик добавляет карточке одновременно анимацию вращения и увеличение при hover:</p>
<pre><code class="lang-css">@keyframes aylanish {{
  from {{ transform: rotate(0deg); }}
  to {{ transform: rotate(360deg); }}
}}
.karta {{ animation: aylanish 3s linear infinite; }}
.karta:hover {{ transform: scale(1.2); }}</code></pre>
<p><strong>Результат:</strong> при наведении карточка <strong>увеличивается, но вращение останавливается</strong>! Причина: свойство <code>transform</code> может принимать <strong>только одно значение</strong> одновременно. <code>transform: scale(1.2)</code> в <code>:hover</code> полностью <strong>заменяет</strong> значение <code>rotate()</code>, вычисляемое анимацией в каждом кадре, они не складываются.</p>
<p><strong>Правильное решение:</strong> объединить оба эффекта в одном месте, например через JavaScript с CSS custom property, либо задать анимацию отдельному wrapper-элементу, а scale — внутреннему элементу.</p>""",
    492: f"""<h3>{MARKER_RU}</h3>
<p>Ученик делает parallax-страницу через <code>background-attachment: fixed</code> и проверяет её на телефоне:</p>
<pre><code class="lang-css">.parallax-seksiya {{
  background-attachment: fixed;
  background-size: cover;
}}</code></pre>
<p><strong>Результат:</strong> на десктопе всё работает отлично, но <strong>в iOS Safari (iPhone/iPad) эффект parallax вообще не работает</strong> — фон двигается как при обычном скролле! Причина: мобильные браузеры Safari <strong>из соображений производительности</strong> не поддерживают <code>background-attachment: fixed</code> — это известная проблема, из-за которой многие разработчики задаются вопросом "почему мой сайт ломается только на iPhone".</p>
<p><strong>Правильное решение:</strong> для мобильных устройств нужен альтернативный подход — например, JS-библиотека parallax на основе <code>transform: translateZ()</code>, либо полностью отключить parallax на мобильных экранах через media query, заменив его статичным фоном.</p>""",
}

NEW_EXERCISES_RU = {
    480: {
        "uz_title": "border-collapse: collapse yozilmasa, jadval chegaralari nega qo'sh chiziq bo'lib ko'rinadi?",
        "title": "Почему без border-collapse: collapse границы таблицы выглядят двойными?",
        "description": "table, th, td { border: 1px solid black; } написано, но border-collapse не используется. Почему линии таблицы выглядят двойными?",
        "expected_answer": "По умолчанию каждая ячейка (th/td) рисует свою границу отдельно, у соседних ячеек границы удваиваются с зазором между ними. border-collapse: collapse объединяет соседние границы в одну общую линию.",
        "hint": "По умолчанию каждая ячейка рисует свою границу отдельно, или делит её с соседом?",
        "explanation": "border-collapse: separate (значение по умолчанию) даёт каждой ячейке отдельную границу. Значение collapse объединяет соседние границы, создавая единые профессионально выглядящие линии.",
    },
    481: {
        "uz_title": "backdrop-filter: blur(10px) qo'yilgan, lekin background-color: white bo'lsa, nega effekt ko'rinmaydi?",
        "title": "Почему при backdrop-filter: blur(10px) и background-color: white эффект не виден?",
        "description": ".karta { backdrop-filter: blur(10px); background-color: white; } — ожидался эффект glassmorphism, но на экране обычная белая карточка. Почему?",
        "options": '["backdrop-filter не работает в Safari", "background-color полностью непрозрачный, поэтому размытый фон перекрывается сплошным цветом сверху", "Значение blur(10px) слишком маленькое", "backdrop-filter работает только с изображениями"]',
        "correct_answers": "B",
        "hint": "Что именно размывает backdrop-filter — сам элемент или то, что за ним? Каким должен быть фон элемента, чтобы это было видно?",
        "explanation": "backdrop-filter размывает только то, что находится ЗА элементом. Если собственный фон элемента не полупрозрачный (например white), размытый фон не виден — его перекрывает сплошной цвет. Нужна прозрачность через rgba().",
    },
    482: {
        "uz_title": ".header-wrapper{overflow:hidden;} bo'lsa, nega ichidagi position:sticky nav ishlamaydi?",
        "title": "Почему position:sticky у nav не работает, если родитель имеет overflow:hidden?",
        "description": ".nav{position:sticky; top:0;} задан, но у его родителя есть overflow:hidden. При скролле nav не прилипает. Почему?",
        "expected_answer": "position: sticky корректно работает только если ни у одного из родительских элементов нет overflow:hidden/auto/scroll. Если у родителя есть overflow:hidden, область прилипания sticky-элемента ограничивается этим родителем, и sticky перестаёт работать. Решение: убрать overflow у родителя.",
        "hint": "Какого одного CSS-свойства не должно быть ни у одного из родительских элементов, чтобы sticky работал?",
        "explanation": "overflow: hidden/auto/scroll у родителя заставляет браузер считать sticky-элемент 'заключённым' внутри этого родителя и ограничивает область его прилипания — в результате sticky-эффект пропадает.",
    },
    483: {
        "uz_title": "karta-konteyner{overflow:hidden} bo'lsa, nega box-shadow to'liq ko'rinmaydi?",
        "title": "Почему box-shadow виден не полностью, если у karta-konteyner есть overflow:hidden?",
        "description": ".karta{box-shadow: 0 4px 12px rgba(0,0,0,0.2);} находится внутри родителя .karta-konteyner{overflow:hidden;}. Почему тень видна не полностью?",
        "options": '["Значение box-shadow написано неверно", "box-shadow выходит за границы элемента, а overflow:hidden обрезает всё, что выходит за границы", "Неверный цвет rgba", "box-shadow работает только для элемента button"]',
        "correct_answers": "B",
        "hint": "box-shadow рисуется ВНУТРИ элемента или ЗА его границами? Что обрезает overflow:hidden?",
        "explanation": "box-shadow визуально выходит за границы элемента. overflow:hidden обрезает ВСЁ, что выходит за границы родительского контейнера — включая и дочерние элементы, и их тень.",
    },
    484: {
        "uz_title": "display:flex berilgan konteynerda, nega turli miqdordagi matnli kartalar bir xil balandlikka cho'ziladi?",
        "title": "Почему в display:flex-контейнере карточки с разным объёмом текста растягиваются до одинаковой высоты?",
        "description": ".konteyner{display:flex;} содержит 3 карточки с разной длиной текста. Все они одинаковой (самой большой) высоты. Почему, если height нигде явно не задан?",
        "expected_answer": "Стандартное значение align-items у flex-контейнера — stretch — оно растягивает все flex-элементы до одинаковой высоты (высоты контейнера), если не указано иное. Если это нежелательно, нужно задать align-items: flex-start.",
        "hint": "Каково значение по умолчанию у свойства align-items?",
        "explanation": "align-items: stretch — состояние Flexbox по умолчанию. Оно растягивает все flex-элементы по поперечной оси до одинакового размера, если у них самих явно не задана высота.",
    },
    485: {
        "uz_title": ".narx-yorlik{position:absolute} rasm konteyneriga nisbatan emas, butun sahifaga nisbatan joylashib qoladi — nega?",
        "title": "Почему .narx-yorlik{position:absolute} позиционируется не относительно контейнера изображения, а относительно всей страницы?",
        "description": "Ценник поверх изображения задан через position:absolute; top:10px; right:10px;, но он оказывается не в углу изображения, а в углу всей страницы. В чём причина?",
        "options": '["Неверные значения top и right", "absolute-элемент позиционируется относительно ближайшего POSITIONED родителя, а при его отсутствии — относительно body", "position:absolute работает только внутри изображений", "Не хватает z-index"]',
        "correct_answers": "B",
        "hint": "Каким свойством должен обладать родительский элемент, 'относительно' которого позиционируется absolute-элемент?",
        "explanation": "position: absolute позиционирует элемент относительно ближайшего 'positioned' родителя (с position:relative/absolute/fixed/sticky). Если такого родителя нет, элемент позиционируется относительно всего документа (body/html).",
    },
    486: {
        "uz_title": "z-index: 999 berilgan, lekin badge hamon orqada qolib ketadi — nima yetishmayapti?",
        "title": "Чего не хватает, если z-index: 999 задан, а badge всё равно остаётся позади?",
        "description": ".badge { z-index: 999; top: -10px; right: -10px; } написано, но свойство position не задано. Почему badge остаётся под карточкой?",
        "correct_answers": "position",
        "hint": "На какие элементы z-index вообще не оказывает влияния, если у них не задано определённое свойство?",
        "explanation": "z-index влияет только на элементы с position, отличным от static (то есть relative, absolute, fixed или sticky). Если position не задан (элемент остаётся в состоянии static по умолчанию), z-index полностью игнорируется.",
    },
    487: {
        "uz_title": "Ota elementda transform: translateY(0) bo'lsa, nega ichidagi position:fixed element ekranga yopishmaydi?",
        "title": "Почему position:fixed элемент не прилипает к экрану, если у родителя есть transform: translateY(0)?",
        "description": ".card-wrapper{transform: translateY(0);} содержит .tugma{position:fixed;}. Кнопка должна была прилипать к экрану при скролле, но она двигается как обычный элемент внутри wrapper. Почему?",
        "expected_answer": "Применение transform к родительскому элементу (даже такого визуально нейтрального значения, как translateY(0)) создаёт новый containing block. Из-за этого вложенный position:fixed элемент теперь позиционируется не относительно всего viewport, а относительно этого transform-родителя. Решение: убрать transform у родителей fixed-элемента.",
        "hint": "Относительно чего обычно позиционируется position:fixed, и как transform меняет это правило?",
        "explanation": "По спецификации CSS, ненулевое значение transform (как и filter, perspective) у элемента создаёт новый containing block. Это полностью меняет 'точку отсчёта' для вложенных fixed/absolute элементов — одна из самых неожиданных ловушек CSS.",
    },
    488: {
        "uz_title": "<label>Foydalanuvchi nomi</label> ustiga bosilganda nega input maydoni fokus olmaydi?",
        "title": "Почему клик по <label>Имя пользователя</label> не переводит фокус на поле ввода?",
        "description": "<label>Имя пользователя</label> и <input type=\"text\" id=\"username\"> написаны отдельно, между ними нет связывающего атрибута. Почему клик по тексту label не переводит фокус на input?",
        "correct_answers": "for",
        "hint": "Какой атрибут связывает label и input, соответствуя атрибуту id у input?",
        "explanation": "Элементу label нужно задать атрибут for=\"username\", соответствующий id=\"username\" у input. Только тогда клик по тексту label переводит фокус на поле (это важно и для доступности).",
    },
    489: {
        "uz_title": "input'larda faqat id bor, name yo'q — forma yuborilganda server nega bo'sh ma'lumot oladi?",
        "title": "Почему сервер получает пустые данные, если у input есть только id, но нет name?",
        "description": "<input type=\"email\" id=\"email\" placeholder=\"Email\"> — у этого input есть id, но нет name. Почему сервер вообще не видит это поле при отправке формы?",
        "options": '["Значение placeholder должно было отправляться на сервер", "Форма отправляет на сервер только поля с атрибутом name, id используется только на frontend", "type=\\"email\\" написан неверно", "Это проблема возникает только при POST-запросах"]',
        "correct_answers": "B",
        "hint": "Под каким именем браузер отправляет каждое поле на сервер при отправке формы — под id или под другим атрибутом?",
        "explanation": "В HTML-формах на сервер отправляются как часть данных формы только input'ы с атрибутом name. id — это лишь уникальный идентификатор внутри страницы для CSS-селекторов или JavaScript, он никак не связан с протоколом отправки формы.",
    },
    490: {
        "uz_title": "height: 0 dan height: auto ga transition berilsa, nega animatsiya silliq ishlamaydi?",
        "title": "Почему transition между height: 0 и height: auto не работает плавно?",
        "description": ".menu{height:0; transition:height 0.3s;} .menu.ochiq{height:auto;} — меню открывается скачком, а не плавно. Почему transition не работает?",
        "expected_answer": "CSS transition может плавно анимировать только между двумя конкретными числовыми значениями. auto — неопределённое значение, вычисляемое по контенту, браузер не может рассчитать плавный переход к нему/от него, поэтому изменение происходит мгновенно (скачком). Решение: задать max-height с достаточно большим конкретным значением, либо измерить scrollHeight через JS и анимировать точное значение в пикселях.",
        "hint": "Между какими значениями может работать CSS transition — только между конкретными числами, или и с вычисляемыми значениями вроде 'auto' тоже?",
        "explanation": "Браузеру нужно рассчитать промежуточные шаги между начальным и конечным значением для transition. 'auto' — не конкретное число, поэтому такой расчёт невозможен — браузер просто мгновенно переключается в конечное состояние.",
    },
    491: {
        "uz_title": "Kartochka doim aylanayotgan bo'lsa, hover'da scale(1.2) berilsa, nega aylanish to'xtab qoladi?",
        "title": "Почему вращение останавливается, если карточка постоянно вращается, а при hover задан scale(1.2)?",
        "description": ".karta{animation: aylanish 3s linear infinite;} .karta:hover{transform: scale(1.2);} — при наведении карточка увеличивается, но вращение останавливается. Почему они не работают вместе?",
        "options": '["animation и transition нельзя использовать одновременно", "Свойство transform может иметь только одно значение одновременно, scale() в hover заменяет rotate() из анимации", "@keyframes не работает в состоянии hover", "scale(1.2) — неверный синтаксис"]',
        "correct_answers": "B",
        "hint": "transform: rotate() и transform: scale() — это два отдельных свойства, или два разных значения одного и того же свойства?",
        "explanation": "transform — одно CSS-свойство, и любое новое присвоенное ему значение ПОЛНОСТЬЮ ЗАМЕНЯЕТ предыдущее, они не складываются. transform: scale(1.2) в правиле :hover полностью отменяет значение rotate(), которое в этот момент вычисляет анимация.",
    },
    492: {
        "uz_title": "background-attachment: fixed desktop'da ishlaydi, lekin iPhone'da nega parallax butunlay yo'qoladi?",
        "title": "Почему background-attachment: fixed работает на десктопе, но parallax полностью пропадает на iPhone?",
        "description": ".parallax-seksiya{background-attachment:fixed;} отлично работает в десктопных браузерах. В iOS Safari (iPhone) же фон двигается как при обычном скролле, эффекта parallax нет. Почему?",
        "expected_answer": "Мобильный Safari (iOS) намеренно не поддерживает background-attachment: fixed из соображений производительности — это осознанное ограничение. Решение: отключить parallax на мобильных экранах через media query, заменив статичным фоном, либо использовать JS-библиотеку parallax на основе transform.",
        "hint": "Есть ли уверенность, что это CSS-свойство одинаково поддерживается во всех браузерах/устройствах, особенно на мобильных?",
        "explanation": "Это реальная, распространённая проблема 'ломается только на мобильном устройстве'. iOS Safari намеренно не поддерживает background-attachment:fixed (ради экономии батареи/производительности), поэтому кросс-девайсное тестирование всегда обязательно.",
    },
}


async def main() -> None:
    async with AsyncSessionLocal() as db:
        for lesson_id, bug_html_ru in BUG_HTML_RU.items():
            lesson = (await db.execute(select(Lesson).where(Lesson.id == lesson_id))).scalar_one()

            old_ru_text = (await db.execute(select(TranslationCache).where(
                TranslationCache.entity_type == "lesson", TranslationCache.entity_id == lesson_id,
                TranslationCache.lang == "ru", TranslationCache.field_name == "text_content",
            ))).scalar_one().translated_text
            old_ru_sections = (await db.execute(select(TranslationCache).where(
                TranslationCache.entity_type == "lesson", TranslationCache.entity_id == lesson_id,
                TranslationCache.lang == "ru", TranslationCache.field_name == "sections_json",
            ))).scalar_one().translated_text

            new_ru_text = old_ru_text + "\n\n" + bug_html_ru
            await _write(db, "lesson", lesson_id, "text_content", lesson.text_content, new_ru_text)

            ru_tree = json.loads(old_ru_sections)
            uz_tree = json.loads(lesson.sections_json)
            uz_text_sections = [s for s in uz_tree if s["type"] == "text"]
            ru_text_sections = [s for s in ru_tree if s["type"] == "text"]
            assert len(uz_text_sections) == len(ru_text_sections)
            ru_text_sections[-1]["html"] = (ru_text_sections[-1].get("html") or "") + "\n\n" + bug_html_ru

            uz_exercise_section = next(s for s in uz_tree if s["type"] == "exercise")
            ru_exercise_section = next(s for s in ru_tree if s["type"] == "exercise")
            spec = NEW_EXERCISES_RU[lesson_id]
            uz_ex_dict = next(e for e in uz_exercise_section["exercises"] if e["title"] == spec["uz_title"])
            ex_id = uz_ex_dict["id"]
            ru_ex_dict = dict(uz_ex_dict)
            ru_ex_dict["title"] = spec["title"]
            ru_ex_dict["description"] = spec["description"]
            ru_ex_dict["hint"] = spec["hint"]
            ru_ex_dict["explanation"] = spec.get("explanation", "")
            if "expected_answer" in spec:
                ru_ex_dict["expected_answer"] = spec["expected_answer"]
            ru_exercise_section["exercises"].append(ru_ex_dict)

            new_ru_sections_json = json.dumps(ru_tree, ensure_ascii=False)
            await _write(db, "lesson", lesson_id, "sections_json", lesson.sections_json, new_ru_sections_json)

            ex = (await db.execute(select(Exercise).where(Exercise.id == ex_id))).scalar_one()
            await _write(db, "exercise", ex_id, "title", ex.title, spec["title"])
            await _write(db, "exercise", ex_id, "description", ex.description, spec["description"])
            await _write(db, "exercise", ex_id, "hint", ex.hint or "", spec["hint"])
            await _write(db, "exercise", ex_id, "explanation", ex.explanation or "", spec.get("explanation", ""))
            if ex.expected_answer:
                await _write(db, "exercise", ex_id, "expected_answer", ex.expected_answer, spec.get("expected_answer", ""))

            print(f"lesson {lesson_id}: RU translation written (exercise {ex_id})")

        await db.commit()
        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
