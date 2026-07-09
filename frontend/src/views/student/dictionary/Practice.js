/* Practice (Mashq) — SM-2 SRS drill orchestrator.
   Mode components → PracticeModes.js
   Pre-drill widgets → PracticeWidgets.js
   Stats/History dashboards → PracticeStats.js
   Utilities, icons, fire streak → practiceUtils.js */

import { useCallback, useEffect, useState } from 'react';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import './Practice.css';
import {
    BASE, MODES, DEFAULT_COUNT, CHUNK_SIZE,
    fireLevelFor, useFireOverlay, FireBadge, Icon,
} from './practiceUtils';
import { FlashcardMode, QuizMode, SpellingMode, ListeningMode, ClozeMode } from './PracticeModes';
import { BucketsBar, LeechAlert, HistoryStrip, QueuePreview, ScopePicker } from './PracticeWidgets';
import { Statistika, History } from './PracticeStats';


/* ═══════════════════════════════════════════════════════════════════════
   ORCHESTRATOR — phases, chunked rounds, replay-missed pass
   ═══════════════════════════════════════════════════════════════════════ */

export default function Practice() {
    const { request } = useHttp();

    /* Top tab — 'drill' shows the pick/drill/recap phase machinery, 'stats'
       shows the read-only Statistika dashboard. The toggle is only visible
       on the pick phase so it doesn't compete for attention mid-drill. */
    const [tab,       setTab]       = useState('drill');  // 'drill' | 'stats' | 'hist'
    const [phase,     setPhase]     = useState('pick');   // 'pick' | 'drill' | 'recap'
    const [mode,      setMode]      = useState('flashcard');
    const [filter,    setFilter]    = useState('all');

    /* Scope — category/course/lesson narrowing. Mirrors life_tracker's
       folder/module ScopePicker; we use the category → course → lesson
       chain that already lives on the dictionary words. */
    const [scope,     setScope]     = useState({ category_id: null, course_id: null, lesson_id: null });
    const [scopeTree, setScopeTree] = useState([]); // [{id, name, courses:[{id, title, lessons:[...]}]}]
    const [counts,    setCounts]    = useState({ due: 0, fragile: 0, total: 0 });
    const [active,    setActive]    = useState(null);
    const [buckets,   setBuckets]   = useState({ fragile: 0, learning: 0, solid: 0, mastered: 0 });
    const [leeches,   setLeeches]   = useState([]);
    const [history,   setHistory]   = useState([]);
    const [preview,   setPreview]   = useState([]);

    /* Drill state — words is a queue of {word, originallyMissed} that the
       chunked-round + replay machinery walks through. */
    const [queue,     setQueue]     = useState([]);
    const [pos,       setPos]       = useState(0);
    const [correct,   setCorrect]   = useState(0);
    const [missed,    setMissed]    = useState([]); // word ids missed in current chunk
    const [round,     setRound]     = useState(1);

    /* Quiz+ two-pass state. life_tracker's design: MCQ over the whole queue
       first (recognition), then typed Spelling over the same queue (recall).
       A word counts as "correct" only if it passed BOTH passes. */
    const [qpPass,    setQpPass]    = useState('mcq'); // 'mcq' | 'spelling'
    const [qpMcqOk,   setQpMcqOk]   = useState([]);    // word ids passed MCQ pass
    const [qpSpellOk, setQpSpellOk] = useState([]);    // word ids passed Spelling pass

    /* In-drill fire streak — consecutive correct answers. Drives FireBadge
       + a full-screen overlay at higher levels. */
    const [fireStreak, setFireStreak] = useState(0);
    const fireLevel = phase === 'drill' ? fireLevelFor(fireStreak) : 0;
    useFireOverlay(fireLevel);
    const [sessionId, setSessionId] = useState(null);
    const [busy,      setBusy]      = useState(false);
    const [error,     setError]     = useState('');

    /* Serialise the scope into URL params reused everywhere. */
    const scopeQS = () => {
        const p = new URLSearchParams();
        if (scope.category_id) p.set('category_id', String(scope.category_id));
        if (scope.course_id)   p.set('course_id',   String(scope.course_id));
        if (scope.lesson_id)   p.set('lesson_id',   String(scope.lesson_id));
        return p;
    };

    /* ── load all pre-drill surfaces in parallel ── */
    const reloadAll = useCallback(() => {
        const wrap = (url) => request(`${BASE}${url}`, 'GET', null, headers()).catch(() => null);
        const sqs = scopeQS().toString();
        const q = sqs ? `?${sqs}` : '';
        Promise.all([
            wrap(`/due-counts${q}`),
            wrap('/session/active'),
            wrap(`/buckets${q}`),
            wrap('/leeches?limit=10'),
            wrap('/history?limit=5'),
        ]).then(([c, a, b, l, h]) => {
            if (c) setCounts(c);
            setActive(a || null);
            if (b) setBuckets(b);
            setLeeches(Array.isArray(l) ? l : []);
            setHistory(Array.isArray(h) ? h : []);
        });
    }, [request, scope]); // eslint-disable-line react-hooks/exhaustive-deps

    useEffect(() => { reloadAll(); }, [reloadAll]);

    /* ── build the scope tree from the dictionary list itself, so it only
       offers categories/courses/lessons the student actually has words in. */
    useEffect(() => {
        request(`${API_URL}v1/dictionary/?lang=${localStorage.getItem('lang') || 'uz'}`, 'GET', null, headers())
            .then((rows) => {
                if (!Array.isArray(rows)) { setScopeTree([]); return; }
                const cats = new Map(); // id → {id, name, courses: Map}
                for (const w of rows) {
                    if (!w.course_id) continue;
                    const cid = 0;
                    let cat = cats.get(cid);
                    if (!cat) {
                        cat = { id: null, name: 'Hammasi', courses: new Map() };
                        cats.set(cid, cat);
                    }
                    let course = cat.courses.get(w.course_id);
                    if (!course) {
                        course = { id: w.course_id, title: w.course_title || `Kurs #${w.course_id}`, lessons: new Map() };
                        cat.courses.set(w.course_id, course);
                    }
                    if (w.lesson_id && !course.lessons.has(w.lesson_id)) {
                        course.lessons.set(w.lesson_id, {
                            id: w.lesson_id,
                            title: w.lesson_title || `${w.lesson_id}-dars`,
                        });
                    }
                }
                const out = [...cats.values()].map((cat) => ({
                    id: cat.id,
                    name: cat.name,
                    courses: [...cat.courses.values()]
                        .map((c) => ({ ...c, lessons: [...c.lessons.values()].sort((a, b) => a.id - b.id) }))
                        .sort((a, b) => a.title.localeCompare(b.title)),
                }));
                setScopeTree(out);
            })
            .catch(() => setScopeTree([]));
    }, [request]);

    /* ── preview the queue when the filter / scope changes ── */
    useEffect(() => {
        const params = scopeQS();
        params.set('count', String(DEFAULT_COUNT));
        if (filter === 'due')  params.set('due_only',  'true');
        if (filter === 'weak') params.set('weak_only', 'true');
        request(`${BASE}/words?${params.toString()}`, 'GET', null, headers())
            .then((data) => setPreview(Array.isArray(data) ? data : []))
            .catch(() => setPreview([]));
    }, [filter, scope, request]); // eslint-disable-line react-hooks/exhaustive-deps

    /* ── start a fresh drill ── */
    const start = useCallback(async () => {
        if (busy) return;
        setBusy(true);
        setError('');
        try {
            const params = scopeQS();
            params.set('count', String(DEFAULT_COUNT));
            if (filter === 'due')  params.set('due_only',  'true');
            if (filter === 'weak') params.set('weak_only', 'true');
            const data = await request(
                `${BASE}/words?${params.toString()}`, 'GET', null, headers(),
            );
            if (!Array.isArray(data) || data.length === 0) {
                setError("Bu filtr bilan mashq qilish uchun so'z yo'q");
                return;
            }
            const s = await request(
                `${BASE}/session`, 'POST', JSON.stringify({ mode }), headers(),
            );
            setQueue(data.map((w) => ({ word: w, replay: false })));
            setPos(0);
            setCorrect(0);
            setMissed([]);
            setRound(1);
            setQpPass('mcq');
            setQpMcqOk([]);
            setQpSpellOk([]);
            setFireStreak(0);
            setSessionId(s.id);
            setPhase('drill');
        } catch {
            setError("Yuklab bo'lmadi — keyinroq urinib ko'ring");
        } finally {
            setBusy(false);
        }
    }, [busy, filter, mode, request, scope]); // eslint-disable-line react-hooks/exhaustive-deps

    /* ── resume an in-flight session ── */
    const resume = useCallback(async () => {
        if (!active?.progress) return;
        setBusy(true);
        try {
            const snap = active.progress;
            const ids = (snap.word_ids || []).join(',');
            const data = await request(`${BASE}/words?ids=${ids}`, 'GET', null, headers());
            if (!Array.isArray(data) || data.length === 0) throw new Error('empty');
            const idToWord = Object.fromEntries(data.map((w) => [w.id, w]));
            const restored = (snap.queue || data.map((w) => ({ id: w.id, replay: false })))
                .map((q) => ({ word: idToWord[q.id], replay: !!q.replay }))
                .filter((q) => !!q.word);
            setQueue(restored);
            setPos(Math.min(snap.pos || 0, restored.length - 1));
            setCorrect(snap.correct || 0);
            setMissed(snap.missed || []);
            setRound(snap.round || 1);
            setQpPass(snap.qpPass || 'mcq');
            setQpMcqOk(snap.qpMcqOk || []);
            setQpSpellOk(snap.qpSpellOk || []);
            setFireStreak(0);
            setSessionId(active.id);
            setMode(active.mode);
            setPhase('drill');
        } catch {
            setError("Sessiyani tiklab bo'lmadi");
        } finally {
            setBusy(false);
        }
    }, [active, request]);

    const discardActive = useCallback(async () => {
        if (!active?.id) return;
        try {
            await request(`${BASE}/session/${active.id}`, 'DELETE', null, headers());
            setActive(null);
        } catch {}
    }, [active, request]);

    /* ── persist progress mid-drill ── */
    useEffect(() => {
        if (phase !== 'drill' || !sessionId || queue.length === 0) return;
        const snap = {
            pos,
            correct,
            missed,
            round,
            qpPass,
            qpMcqOk,
            qpSpellOk,
            queue: queue.map((q) => ({ id: q.word.id, replay: q.replay })),
            // word_ids kept for backward compat with old resume snapshots
            word_ids: queue.map((q) => q.word.id),
        };
        request(
            `${BASE}/session/${sessionId}/progress`,
            'PUT',
            JSON.stringify({ progress: snap }),
            headers(),
        ).catch(() => {});
    }, [phase, sessionId, pos, correct, missed, round, qpPass, qpMcqOk, qpSpellOk, queue, request]);

    /* ── card answered ──
       Quiz+ branches here: instead of finalising on the first answer, we
       track per-pass correctness sets and finalise the word only after both
       passes have run over it. */
    const onAnswer = useCallback(async ({ grade, was_correct }) => {
        const item = queue[pos];
        if (!item) return;

        // Fire streak — consecutive correct counter. Resets on any wrong.
        setFireStreak((s) => was_correct ? s + 1 : 0);

        // Submit SRS update (fire-and-forget; the UI keeps moving). Quiz+
        // submits twice per word (once per pass) so the SRS sees both signals.
        request(
            `${BASE}/result`, 'POST',
            JSON.stringify({ word_id: item.word.id, grade, was_correct }),
            headers(),
        ).catch(() => {});

        /* ════ Quiz+ two-pass branch ════════════════════════════════════ */
        if (mode === 'quiz') {
            const newMcqOk   = qpPass === 'mcq'      && was_correct ? [...qpMcqOk, item.word.id]   : qpMcqOk;
            const newSpellOk = qpPass === 'spelling' && was_correct ? [...qpSpellOk, item.word.id] : qpSpellOk;
            if (qpPass === 'mcq')      setQpMcqOk(newMcqOk);
            if (qpPass === 'spelling') setQpSpellOk(newSpellOk);

            const nextPos = pos + 1;
            const endOfPass = nextPos >= queue.length;

            if (endOfPass && qpPass === 'mcq') {
                setQpPass('spelling');
                setPos(0);
                return;
            }

            if (endOfPass && qpPass === 'spelling') {
                const okSet = new Set(newMcqOk.filter((id) => newSpellOk.includes(id)));
                const chunkCorrect = okSet.size;
                const total = queue.length;
                try {
                    await request(
                        `${BASE}/session/${sessionId}/complete`,
                        'PUT',
                        JSON.stringify({ total_words: total, correct: chunkCorrect }),
                        headers(),
                    );
                } catch {}
                setCorrect(chunkCorrect);
                setActive(null);
                setPhase('recap');
                reloadAll();
                return;
            }

            setPos(nextPos);
            return;
        }

        /* ════ Other modes: chunked rounds + replay-missed ═══════════════ */
        const isReplayItem = item.replay;
        if (!isReplayItem && was_correct) setCorrect((c) => c + 1);

        let newMissed = missed;
        if (!isReplayItem && !was_correct) {
            newMissed = [...missed, item.word.id];
            setMissed(newMissed);
        }

        const nextPos = pos + 1;
        const endOfQueue = nextPos >= queue.length;
        const endOfChunk = !isReplayItem && nextPos % CHUNK_SIZE === 0;
        const finalChunkOfRun = nextPos === queue.filter((q) => !q.replay).length;

        if ((endOfChunk || finalChunkOfRun) && newMissed.length > 0) {
            const idToWord = Object.fromEntries(queue.map((q) => [q.word.id, q.word]));
            const replayItems = newMissed
                .map((id) => idToWord[id])
                .filter(Boolean)
                .map((word) => ({ word, replay: true }));
            const left  = queue.slice(0, nextPos);
            const right = queue.slice(nextPos);
            setQueue([...left, ...replayItems, ...right]);
            setMissed([]);
            setRound((r) => r + 1);
            setPos(nextPos);
            return;
        }

        if (endOfQueue) {
            try {
                await request(
                    `${BASE}/session/${sessionId}/complete`,
                    'PUT',
                    JSON.stringify({
                        total_words: queue.filter((q) => !q.replay).length,
                        correct: correct + (was_correct && !isReplayItem ? 1 : 0),
                    }),
                    headers(),
                );
            } catch {}
            setActive(null);
            setPhase('recap');
            reloadAll();
        } else {
            setPos(nextPos);
        }
    }, [queue, pos, correct, missed, sessionId, mode, qpPass, qpMcqOk, qpSpellOk, request, reloadAll]);

    const goPick = useCallback(() => {
        setPhase('pick');
        setQueue([]);
        setPos(0);
        setCorrect(0);
        setMissed([]);
        setRound(1);
        setQpPass('mcq');
        setQpMcqOk([]);
        setQpSpellOk([]);
        setFireStreak(0);
        setSessionId(null);
    }, []);


    /* ─────────────────────────── render ─────────────────────────── */

    if (phase === 'drill') {
        const item = queue[pos];
        if (!item) {
            return (
                <div className="pr-state pr-state--error" style={{ display:'flex', flexDirection:'column', gap:14, alignItems:'center', padding:'48px 24px', textAlign:'center' }}>
                    <span style={{ fontSize: 40 }}>🧭</span>
                    <h3 style={{ margin: 0 }}>Сессия прервана</h3>
                    <p style={{ margin: 0, color: 'rgba(0,0,0,0.55)' }}>
                        Что-то пошло не так с очередью практики. Вернитесь к выбору
                        режима и начните заново — ваш прогресс сохранён.
                    </p>
                    <button
                        className="pr-btn pr-btn--primary"
                        onClick={goPick}
                        style={{ marginTop: 6 }}
                    >
                        ← К выбору режима
                    </button>
                </div>
            );
        }
        const word = item.word;

        const isQuizPlus = mode === 'quiz';
        const total = isQuizPlus
            ? queue.length
            : queue.filter((q) => !q.replay).length;
        const done = isQuizPlus
            ? pos
            : queue.slice(0, pos).filter((q) => !q.replay).length;

        return (
            <div className="pr-root pr-root--drill">
                <FireBadge streak={fireStreak} />

                <header className="pr-drill-head">
                    <button className="pr-back" onClick={goPick}>← Chiqish</button>
                    <div className="pr-progress">
                        <div className="pr-progress-text">
                            {done + 1} / {total}
                            {isQuizPlus && (
                                <span className={`pr-pass-tag pr-pass-tag--${qpPass}`}>
                                    {' · '}{qpPass === 'mcq' ? 'Raund 1: MCQ' : 'Raund 2: Yozish'}
                                </span>
                            )}
                            {!isQuizPlus && item.replay && <span className="pr-replay-tag"> · qaytarish</span>}
                            {!isQuizPlus && round > 1 && !item.replay && <span className="pr-round-tag"> · raund {round}</span>}
                        </div>
                        <div className="pr-progress-bar">
                            <div
                                className="pr-progress-fill"
                                style={{ width: `${((done + 1) / total) * 100}%` }}
                            />
                        </div>
                    </div>
                    <div className="pr-score">
                        <Icon.Check /> {correct}
                    </div>
                </header>

                {mode === 'flashcard' && <FlashcardMode key={word.id} word={word} onAnswer={onAnswer} />}
                {mode === 'quiz'      && <QuizMode      key={`${word.id}-${qpPass}`} word={word} qpPass={qpPass} onAnswer={onAnswer} request={request} />}
                {mode === 'spelling'  && <SpellingMode  key={word.id} word={word} onAnswer={onAnswer} request={request} />}
                {mode === 'listening' && <ListeningMode key={word.id} word={word} onAnswer={onAnswer} request={request} />}
                {mode === 'cloze'     && <ClozeMode     key={word.id} word={word} onAnswer={onAnswer} request={request} />}
            </div>
        );
    }

    if (phase === 'recap') {
        const firstPassTotal = Math.max(queue.filter((q) => !q.replay).length, 1);
        const pct = Math.round((correct / firstPassTotal) * 100);
        return (
            <div className="pr-root pr-root--recap">
                <div className="pr-recap">
                    <div className="pr-recap-emoji">
                        {pct >= 80 ? '🎉' : pct >= 50 ? '👍' : '📚'}
                    </div>
                    <div className="pr-recap-title">
                        {pct >= 80 ? "Zo'r natija!" : pct >= 50 ? 'Yaxshi!' : 'Yana mashq qilamiz'}
                    </div>
                    <div className="pr-recap-stats">
                        <div className="pr-recap-stat">
                            <span className="pr-recap-num">{correct}</span>
                            <span className="pr-recap-lbl">to'g'ri</span>
                        </div>
                        <div className="pr-recap-divider" />
                        <div className="pr-recap-stat">
                            <span className="pr-recap-num">{firstPassTotal - correct}</span>
                            <span className="pr-recap-lbl">noto'g'ri</span>
                        </div>
                        <div className="pr-recap-divider" />
                        <div className="pr-recap-stat">
                            <span className="pr-recap-num">{pct}%</span>
                            <span className="pr-recap-lbl">aniqlik</span>
                        </div>
                    </div>
                    <div className="pr-recap-actions">
                        <button className="pr-btn pr-btn--ghost" onClick={goPick}>
                            Yana boshlash
                        </button>
                        <button className="pr-btn pr-btn--primary" onClick={() => { goPick(); setTimeout(start, 100); }}>
                            Davom etish
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    /* ── pick phase ── */
    return (
        <div className="pr-root pr-root--pick">
            <div className="pr-subtabs">
                <button
                    className={`pr-subtab ${tab === 'drill' ? 'active' : ''}`}
                    onClick={() => setTab('drill')}
                >
                    🎯 Boshlash
                </button>
                <button
                    className={`pr-subtab ${tab === 'stats' ? 'active' : ''}`}
                    onClick={() => setTab('stats')}
                >
                    📊 Statistika
                </button>
                <button
                    className={`pr-subtab ${tab === 'hist' ? 'active' : ''}`}
                    onClick={() => setTab('hist')}
                >
                    📜 Tarix
                </button>
            </div>

            {tab === 'stats' && <Statistika />}
            {tab === 'hist' && <History />}

            {tab === 'drill' && <>

            {error && (
                <div className="pr-error">
                    {error}
                    <button onClick={() => setError('')}>✕</button>
                </div>
            )}

            {active && (
                <div className="pr-resume">
                    <div className="pr-resume-head">
                        <span className="pr-resume-tag">Davom etish</span>
                        <span className="pr-resume-mode">{MODES.find(m => m.key === active.mode)?.label || active.mode}</span>
                    </div>
                    <div className="pr-resume-body">
                        Boshlagan mashqingiz bor —
                        {' '}{active.progress?.pos ?? active.progress?.idx ?? 0}
                        {' / '}
                        {(active.progress?.queue?.length) || (active.progress?.word_ids?.length) || 0}
                    </div>
                    <div className="pr-resume-actions">
                        <button className="pr-btn pr-btn--ghost" onClick={discardActive}>
                            Bekor qilish
                        </button>
                        <button className="pr-btn pr-btn--primary" onClick={resume}>
                            Davom etish →
                        </button>
                    </div>
                </div>
            )}

            <LeechAlert leeches={leeches} />

            <section className="pr-section">
                <h3 className="pr-section-title">1. Rejim tanlang</h3>
                <div className="pr-modes">
                    {MODES.map((m) => (
                        <button
                            key={m.key}
                            className={`pr-mode ${mode === m.key ? 'active' : ''}`}
                            onClick={() => setMode(m.key)}
                        >
                            <span className="pr-mode-icon" aria-hidden>{m.icon}</span>
                            <span className="pr-mode-text">
                                <span className="pr-mode-label">{m.label}</span>
                                <span className="pr-mode-desc">{m.desc}</span>
                            </span>
                            {mode === m.key && <span className="pr-mode-check"><Icon.Check /></span>}
                        </button>
                    ))}
                </div>
            </section>

            <section className="pr-section">
                <h3 className="pr-section-title">2. So'zlar to'plamini tanlang</h3>
                <div className="pr-filters">
                    <button
                        className={`pr-filter ${filter === 'all' ? 'active' : ''}`}
                        onClick={() => setFilter('all')}
                    >
                        Barchasi
                        {counts.total > 0 && <span className="pr-filter-count">{counts.total}</span>}
                    </button>
                    <button
                        className={`pr-filter pr-filter--due ${filter === 'due' ? 'active' : ''}`}
                        onClick={() => setFilter('due')}
                    >
                        <Icon.Clock /> Takrorlash vaqti
                        {counts.due > 0 && <span className="pr-filter-count">{counts.due}</span>}
                    </button>
                    <button
                        className={`pr-filter pr-filter--weak ${filter === 'weak' ? 'active' : ''}`}
                        onClick={() => setFilter('weak')}
                    >
                        <Icon.Warn /> Qiyin so'zlar
                        {counts.fragile > 0 && <span className="pr-filter-count">{counts.fragile}</span>}
                    </button>
                </div>
                <p className="pr-filter-hint">
                    {filter === 'due' && 'Takrorlash vaqti kelgan yoki yangi so\'zlar.'}
                    {filter === 'weak' && 'Bir necha marta unutgan yoki qiyin keladigan so\'zlar.'}
                    {filter === 'all' && 'Saqlangan barcha so\'zlardan random tanlanadi.'}
                </p>
            </section>

            <ScopePicker tree={scopeTree} scope={scope} onChange={setScope} />

            <QueuePreview words={preview} />

            <section className="pr-section">
                <h3 className="pr-section-title">Sizning vaziyatingiz</h3>
                <BucketsBar buckets={buckets} />
            </section>

            <HistoryStrip history={history} />

            <div className="pr-start-wrap">
                <button
                    className="pr-btn pr-btn--primary pr-btn--lg"
                    onClick={start}
                    disabled={busy || counts.total < 2}
                >
                    {counts.total < 2
                        ? "Mashq uchun kamida 2 ta so'z kerak"
                        : busy
                            ? 'Yuklanmoqda…'
                            : "Mashqni boshlash"}
                </button>
            </div>

            </>}
        </div>
    );
}
