"""Russian translation for Capstone 6: Accessibility va Brauzer API, lesson order=5 (L6)."""
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

LESSON_ID = 810

TITLE_RU = "6-Service Worker + PWA"

TEXT_RU = """\
<h2>Этап 6: Service Worker + PWA — ошибка "исправлено, но никто не увидит"</h2>

<pre class="mermaid">
flowchart LR
    FIX["Команда ИСПРАВЛЯЕТ ошибку div/button со 2-го урока, деплоит в production"] --> SW{"Изменилась ли версия кэша Service Worker?"}
    SW -->|"Нет - имя кэша не изменилось"| STALE["Пользователи с установленным PWA ПРОДОЛЖАЮТ видеть СТАРУЮ, неисправленную версию"]
    SW -->|"Да - версия увеличена"| FRESH["Пользователи получают новую, исправленную версию"]
</pre>

<p>В курсе JavaScript: Brauzer API вы уже изучили Service Worker и PWA. На этом уроке вы делаете AccessBoard устанавливаемым, работающим офлайн PWA-приложением. Но на этот раз ошибка — даже если вы <strong>правильно</strong> исправили ВСЕ ошибки доступности из уроков 2-5, <strong>никто может никогда этого не увидеть</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — регистрация Service Worker</h4>
<pre><code>// app.js
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}</code></pre>

<h4>БЛОК 2 — manifest.json: делаем приложение устанавливаемым</h4>
<pre><code>{
  "name": "AccessBoard",
  "short_name": "AccessBoard",
  "start_url": "/",
  "display": "standalone",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" }
  ]
}</code></pre>

<h4>БЛОК 3 — ПРАВИЛЬНОЕ версионирование кэша: имя, меняющееся при каждом деплое</h4>
<pre><code>// sw.js
const CACHE_VERSION = 'accessboard-v3';   // ❗ УВЕЛИЧИВАЕТСЯ при КАЖДОМ деплое

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();   // ❗ новый Service Worker активируется НЕМЕДЛЕННО
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k))
      )
    )   // ❗ кэши СТАРЫХ версий ОЧИЩАЮТСЯ
  );
});</code></pre>

<h3>🐛 Намеренная ошибка — имя кэша никогда не меняется, стратегия cache-first</h3>
<pre><code>// sw.js - НЕПРАВИЛЬНАЯ версия
const CACHE_NAME = 'accessboard-cache';   // ❌ НИКОГДА не меняется!

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
    // ❌ Если запрошенный файл ЕСТЬ в кэше, он НИКОГДА не проверяет
    // новую версию из сети!
  );
});</code></pre>
<pre><code>// Сценарий:
// 1. Команда исправляет ошибку <div onclick> со 2-го урока - теперь
//    используется <button>. Новый index.html/app.js деплоится в production.
// 2. Пользователь, УСТАНОВИВШИЙ AccessBoard как PWA, открывает приложение.
// 3. Браузер направляет запрос fetch в Service Worker.
// 4. Service Worker: "index.html ЕСТЬ в кэше" - вообще НЕ обращается
//    к сети, возвращает СТАРУЮ, неисправленную версию.
//
// ❌ Этот пользователь НИКОГДА не увидит ИСПРАВЛЕНИЯ доступности - он
//    продолжает использовать СТАРУЮ версию с <div onclick>, не
//    работающую с клавиатуры, хотя fix УЖЕ развёрнут в production!</code></pre>

<p><strong>Результат:</strong> если имя кэша никогда не меняется, браузер считает "этот файл уже есть в кэше" и <strong>никогда</strong> не запрашивает новую версию из сети. Это — <strong>самая обманчивая</strong> ситуация для пользователей, установивших PWA: вы <strong>правильно</strong> исправили production-код, деплой прошёл <strong>успешно</strong>, но пользователи, уже установившие приложение, <strong>никогда</strong> этого не увидят — пока вручную не очистят кэш браузера или не переустановят приложение.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему важно версионировать имя кэша (например <code>v2</code>, <code>v3</code>)?</h4>
<p><code>caches.open(CACHE_VERSION)</code> — если это имя <strong>не меняется</strong>, браузер считает это "тем же самым кэшем" и не пересоздаёт его. Изменение имени (например с <code>v2</code> на <code>v3</code>) даёт браузеру сигнал "это <strong>новый</strong> кэш, нужно заново загрузить старые файлы".</p>

<h4>2. Зачем нужна очистка старых кэшей в событии <code>activate</code>?</h4>
<p>После установки новой версии кэш <strong>старой</strong> версии может остаться в памяти браузера. Удаление всех старых кэшей, не соответствующих текущей версии, в событии <code>activate</code> нужно для экономии памяти и обеспечения использования только <strong>текущей</strong> версии.</p>

<h4>3. Почему эта ошибка считается особенно "обманчивой"?</h4>
<p>В отличие от других ошибок, здесь разработчик сделал <strong>всё правильно</strong>: ошибку доступности верно исправил, код написан правильно, деплой прошёл успешно. Проблема находится на <strong>совершенно другом</strong> уровне - в стратегии кэширования браузера, - и этот уровень кажется <strong>никак</strong> не связанным с содержанием самих исправлений доступности.</p>

<h4>4. Что делает <code>self.skipWaiting()</code>?</h4>
<p>Обычно новый Service Worker находится в состоянии "ожидания" - он активируется только после закрытия всех открытых вкладок. <code>skipWaiting()</code> пропускает это ожидание, активируя новый Service Worker <strong>немедленно</strong> - это обеспечивает более быстрое получение обновлений.</p>

<h4>5. Какое место занимает этот урок в capstone?</h4>
<p>Это - самая "мета" ошибка в capstone: на этот раз проблема не в какой-то <strong>новой</strong> недоработке доступности, а в том, что <strong>уже правильно сделанные</strong> исправления из предыдущих уроков могут <strong>никогда не дойти</strong> до реальных пользователей. Это напоминание, что "написать правильный код" и "донести этот код до пользователя" - два <strong>отдельных</strong> вопроса.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Версионирование имени кэша - способ дать браузеру сигнал "это новый кэш"</li>
<li>✅ Очистка старых кэшей в событии activate обеспечивает использование только текущей версии</li>
<li>✅ Неизменное имя кэша + стратегия cache-first может навсегда удержать установленных пользователей на СТАРОЙ версии</li>
<li>✅ skipWaiting() немедленно активирует новый Service Worker, ускоряя обновление</li>
<li>✅ Написание правильного кода и его реальное достижение до пользователя - два отдельных вопроса</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 6: Service Worker + PWA
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) app.js - регистрация Service Worker
// ─────────────────────────────────────────────────────────────────────

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}

// ─────────────────────────────────────────────────────────────────────
// 2) sw.js - с ПРАВИЛЬНЫМ версионированием
// ─────────────────────────────────────────────────────────────────────

const CACHE_VERSION = 'accessboard-v3';
const ASSETS = ['/', '/index.html', '/style.css', '/app.js'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k))
      )
    )
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});

// ─────────────────────────────────────────────────────────────────────
// 3) Намеренная ошибка - невersионированный кэш (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// const CACHE_NAME = 'accessboard-cache';   // никогда не меняется!
//
// self.addEventListener('install', (event) => {
//   event.waitUntil(
//     caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
//   );
// });
// // Очистки старого кэша в activate НЕТ, skipWaiting() НЕТ
//
// Установленные пользователи НИКОГДА не увидят исправления
// доступности - service worker навсегда возвращает старые,
// закэшированные файлы.
"""

EX = {
    4654: {
        "title": "Почему важно версионировать имя кэша?",
        "description": "Почему важно менять название CACHE_VERSION в sw.js при каждом деплое (например с v2 на v3)?",
        "hint": "Как браузер отличает 'новый кэш' от 'старого, того же самого кэша'?",
        "explanation": "Если имя кэша не меняется, браузер считает это тем же самым, уже существующим кэшем и не пересоздаёт его. Изменение имени даёт браузеру сигнал, что это новый кэш и старые файлы нужно перезагрузить.",
    },
    4655: {
        "title": "Почему опасны неversionированный кэш + стратегия cache-first?",
        "description": "Почему опасен Service Worker, чьё имя кэша никогда не меняется, а событие fetch всегда сначала проверяет кэш?",
        "hint": "Если запрошенный файл найден в кэше, обращается ли Service Worker к сети вообще?",
        "explanation": "Если имя кэша не меняется и обработчик fetch всегда возвращает данные из кэша, Service Worker никогда не запрашивает новую версию из сети - установленные пользователи никогда не получают развёрнутые исправления.",
    },
    4656: {
        "title": "Расположите процесс того, как исправление доступности не доходит до пользователя",
        "description": "Расположите процесс того, как после исправления командой ошибки div/button со 2-го урока, из-за невersionированного кэша это исправление не доходит до установленного пользователя.",
        "hint": "",
        "explanation": "",
    },
    4657: {
        "title": "Метод немедленной активации нового Service Worker",
        "description": "Какой метод вызывается в событии install, чтобы пропустить этап 'ожидания' нового Service Worker и НЕМЕДЛЕННО его активировать? (например: self.xxx())",
        "hint": "Означает 'пропустить ожидание'.",
        "expected_answer": "skipWaiting",
    },
    4658: {
        "title": "Почему эта ошибка считается более 'обманчивой', чем другие?",
        "description": (
            "Почему ошибка невersionированного кэша считается особенно "
            "'обманчивой' по сравнению с другими ошибками доступности "
            "из предыдущих уроков - проблема возникает независимо от "
            "того, что сделал разработчик? Объясните своими словами."
        ),
        "hint": "На этот раз проблема ВНУТРИ кода, или на другом уровне МЕЖДУ кодом и пользователем?",
        "expected_answer": "В ошибках предыдущих уроков проблема обычно была в самом коде - неверный элемент, непроверенное состояние и т.д. Здесь же разработчик сделал ВСЁ правильно: правильно исправил ошибку доступности, код написан верно, деплой прошёл успешно. Проблема находится на СОВЕРШЕННО ДРУГОМ уровне - в стратегии кэширования браузера - и этот уровень кажется никак не связанным с содержанием самих исправлений доступности. Поэтому эта ошибка особенно обманчива: с полным основанием думая 'я всё сделал правильно', реальный пользователь всё равно продолжает видеть старую, неисправленную версию.",
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
        TASK_TITLE_RU = "AccessBoard — Service Worker + PWA (с правильным версионированием)"
        TASK_DESCRIPTION_RU = (
            "Сделайте AccessBoard устанавливаемым, работающим офлайн "
            "PWA: manifest.json, Service Worker (sw.js). Версионируйте "
            "имя кэша при каждом деплое, очищайте старые кэши в событии "
            "activate, и немедленно активируйте новую версию через "
            "skipWaiting()."
        )
        TASK_REQUIREMENTS_RU = (
            "• manifest.json: заполнены name, short_name, start_url, display, icons\n"
            "• sw.js: версионирован через переменную CACHE_VERSION (НЕ статичное, неизменное имя)\n"
            "• В событии activate удаляются старые кэши, не соответствующие текущей версии\n"
            "• В событии install вызывается self.skipWaiting()\n"
            "• README.md: объяснено, как увеличивать версию кэша при каждом деплое, обновлён чеклист статуса"
        )
        TASK_TECHNOLOGIES_RU = "HTML, CSS, JavaScript, Service Worker, PWA, Cache API"
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
