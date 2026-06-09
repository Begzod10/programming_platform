/**
 * Practice (Mashq) — SM-2 SRS drill over the student's saved dictionary.
 *
 * Ported from life_tracker's /learning/practice page. Kept in a single
 * file (with the 5 mode components inlined as helpers) because they all
 * share the same phase state, scoreboard, and SRS round-trip — splitting
 * them out adds prop-drilling without separation of concerns.
 *
 * Phases:
 *   'pick'   — mode picker + filter chips + Resume card
 *   'drill'  — one of the 5 mode components, looping over `words`
 *   'recap'  — score summary at the end
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import './Practice.css';

const BASE = `${API_URL}v1/dictionary/practice`;

// Visual metadata for the mode picker. Keep this list of 5 in sync with the
// backend `ALLOWED_MODES` set in practice.py.
const MODES = [
    { key: 'flashcard', label: 'Flashcard',  desc: 'Bilaman / Bilmayman', icon: '🃏' },
    { key: 'quiz',      label: 'Quiz',       desc: '4 tadan birini tanlash', icon: '🎯' },
    { key: 'spelling',  label: 'Spelling',   desc: "So'zni yozing",       icon: '⌨️' },
    { key: 'listening', label: 'Listening',  desc: 'Eshitib yozish',      icon: '🎧' },
    { key: 'cloze',     label: 'Cloze',      desc: "Gapda bo'shliqni to'ldiring", icon: '✏️' },
];

const DEFAULT_COUNT = 10;


/* ─── Close-match scoring for typed-answer modes ────────────────────────
   Levenshtein-style: exact = grade 2, off by 1-2 chars = grade 1, else 0.
   Trim, lowercase, strip diacritics so accidents don't punish the student. */
const norm = (s) =>
    (s || '')
        .trim()
        .toLowerCase()
        .normalize('NFKD')
        .replace(/[̀-ͯ]/g, '');

function editDistance(a, b) {
    if (a === b) return 0;
    const al = a.length, bl = b.length;
    if (!al) return bl;
    if (!bl) return al;
    const dp = Array(bl + 1).fill(0).map((_, i) => i);
    for (let i = 1; i <= al; i++) {
        let prev = dp[0];
        dp[0] = i;
        for (let j = 1; j <= bl; j++) {
            const tmp = dp[j];
            dp[j] = a[i - 1] === b[j - 1]
                ? prev
                : 1 + Math.min(prev, dp[j - 1], dp[j]);
            prev = tmp;
        }
    }
    return dp[bl];
}

function judgeTyped(userInput, target) {
    const a = norm(userInput), b = norm(target);
    if (!a) return { ok: false, exact: false };
    if (a === b) return { ok: true, exact: true };
    const dist = editDistance(a, b);
    // 1-2 character edits on words 4+ chars long counts as "close" — grade 1.
    if (b.length >= 4 && dist <= 2) return { ok: true, exact: false };
    return { ok: false, exact: false };
}


/* ─── Inline SVG icons (consistent with the rest of the app) ──────────── */
const Icon = {
    Check:  (p) => <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...p}><polyline points="20 6 9 17 4 12" /></svg>,
    X:      (p) => <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...p}><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>,
    Clock:  (p) => <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>,
    Warn:   (p) => <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>,
    Volume: (p) => <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" /><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" /></svg>,
};


/* ═══════════════════════════════════════════════════════════════════════
   MODE COMPONENTS
   Each one calls `onAnswer({ grade, was_correct })` exactly once per card.
   ═══════════════════════════════════════════════════════════════════════ */

function FlashcardMode({ word, onAnswer }) {
    const [flipped, setFlipped] = useState(false);
    useEffect(() => { setFlipped(false); }, [word.id]);

    return (
        <div className="pr-card pr-flash">
            <button
                className={`pr-flash-card ${flipped ? 'flipped' : ''}`}
                onClick={() => setFlipped(f => !f)}
                aria-label="Aylantirish"
            >
                <div className="pr-flash-face pr-flash-front">
                    <div className="pr-flash-hint">So'z</div>
                    <div className="pr-flash-word">{word.word}</div>
                    <div className="pr-flash-tap">Ma'nosini ko'rish uchun bosing</div>
                </div>
                <div className="pr-flash-face pr-flash-back">
                    <div className="pr-flash-hint">Ma'no</div>
                    <div className="pr-flash-ctx">
                        {word.context || <em>Konteskt yo'q — ezma o'qib eslab qoling</em>}
                    </div>
                </div>
            </button>

            {flipped && (
                <div className="pr-flash-actions">
                    <button
                        className="pr-btn pr-btn--bad"
                        onClick={() => onAnswer({ grade: 0, was_correct: false })}
                    >
                        <Icon.X /> Bilmayman
                    </button>
                    <button
                        className="pr-btn pr-btn--good"
                        onClick={() => onAnswer({ grade: 2, was_correct: true })}
                    >
                        <Icon.Check /> Bilaman
                    </button>
                </div>
            )}
        </div>
    );
}


function QuizMode({ word, onAnswer }) {
    const [picked, setPicked] = useState(null);

    // Reset locally-held state when the word changes
    useEffect(() => { setPicked(null); }, [word.id]);

    const pick = (opt) => {
        if (picked !== null) return;
        const correct = opt === word.word;
        setPicked(opt);
        // Brief delay so the student sees the correctness colour before advance
        setTimeout(() => onAnswer({
            grade: correct ? 2 : 0,
            was_correct: correct,
        }), 650);
    };

    return (
        <div className="pr-card pr-quiz">
            <div className="pr-quiz-prompt">Bu ma'noga qaysi so'z mos keladi?</div>
            <div className="pr-quiz-ctx">
                {word.context || <em>Konteskt yo'q — taxminan tanlang</em>}
            </div>
            <div className="pr-quiz-opts">
                {(word.options || []).map((opt) => {
                    const isCorrect = opt === word.word;
                    const isPicked = opt === picked;
                    const cls = picked === null
                        ? ''
                        : isCorrect
                            ? 'pr-opt--ok'
                            : isPicked
                                ? 'pr-opt--bad'
                                : 'pr-opt--dim';
                    return (
                        <button
                            key={opt}
                            className={`pr-opt ${cls}`}
                            onClick={() => pick(opt)}
                            disabled={picked !== null}
                        >
                            <span>{opt}</span>
                            {picked !== null && isCorrect && <Icon.Check />}
                            {picked !== null && isPicked && !isCorrect && <Icon.X />}
                        </button>
                    );
                })}
            </div>
        </div>
    );
}


function SpellingMode({ word, onAnswer }) {
    const [value, setValue] = useState('');
    const [verdict, setVerdict] = useState(null); // null | {ok, exact}
    const inputRef = useRef(null);

    useEffect(() => {
        setValue('');
        setVerdict(null);
        // Re-focus on each new card so a fast typer doesn't lose flow
        setTimeout(() => inputRef.current?.focus(), 60);
    }, [word.id]);

    const submit = (e) => {
        e?.preventDefault?.();
        if (verdict) return;
        const v = judgeTyped(value, word.word);
        setVerdict(v);
        const grade = v.exact ? 2 : v.ok ? 1 : 0;
        setTimeout(() => onAnswer({ grade, was_correct: v.ok }), 900);
    };

    return (
        <div className="pr-card pr-typed">
            <div className="pr-typed-hint">Ma'no:</div>
            <div className="pr-typed-ctx">
                {word.context || <em>Konteskt yo'q</em>}
            </div>
            <form className="pr-typed-form" onSubmit={submit}>
                <input
                    ref={inputRef}
                    type="text"
                    autoComplete="off"
                    autoCorrect="off"
                    spellCheck={false}
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    placeholder="So'zni yozing…"
                    className={`pr-typed-input ${verdict ? (verdict.ok ? 'ok' : 'bad') : ''}`}
                    disabled={!!verdict}
                />
                <button
                    type="submit"
                    className="pr-btn pr-btn--primary"
                    disabled={!!verdict || !value.trim()}
                >
                    Tekshirish
                </button>
            </form>
            {verdict && (
                <div className={`pr-typed-feedback ${verdict.ok ? (verdict.exact ? 'ok' : 'close') : 'bad'}`}>
                    {verdict.ok && verdict.exact && <><Icon.Check /> To'g'ri!</>}
                    {verdict.ok && !verdict.exact && <><Icon.Warn /> Yaqin — to'g'risi: <strong>{word.word}</strong></>}
                    {!verdict.ok && <><Icon.X /> To'g'risi: <strong>{word.word}</strong></>}
                </div>
            )}
        </div>
    );
}


function ListeningMode({ word, onAnswer }) {
    // SpeechSynthesis works offline in modern browsers. Pick a Latin-alphabet
    // voice if available (Uzbek isn't supported widely; English voices speak
    // the spelling close enough for drill purposes).
    const speak = useCallback(() => {
        if (typeof window === 'undefined' || !window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(word.word);
        u.rate = 0.85;
        u.lang = 'en-US';
        window.speechSynthesis.speak(u);
    }, [word.word]);

    useEffect(() => { speak(); }, [speak]);

    const [value, setValue] = useState('');
    const [verdict, setVerdict] = useState(null);
    const inputRef = useRef(null);
    useEffect(() => {
        setValue('');
        setVerdict(null);
        setTimeout(() => inputRef.current?.focus(), 60);
    }, [word.id]);

    const submit = (e) => {
        e?.preventDefault?.();
        if (verdict) return;
        const v = judgeTyped(value, word.word);
        setVerdict(v);
        const grade = v.exact ? 2 : v.ok ? 1 : 0;
        setTimeout(() => onAnswer({ grade, was_correct: v.ok }), 900);
    };

    return (
        <div className="pr-card pr-typed">
            <button type="button" className="pr-listen-btn" onClick={speak} title="Qayta eshitish">
                <Icon.Volume /> <span>Eshitish</span>
            </button>
            <div className="pr-typed-hint">Eshitganingizni yozing</div>
            <form className="pr-typed-form" onSubmit={submit}>
                <input
                    ref={inputRef}
                    type="text"
                    autoComplete="off"
                    spellCheck={false}
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    placeholder="So'zni yozing…"
                    className={`pr-typed-input ${verdict ? (verdict.ok ? 'ok' : 'bad') : ''}`}
                    disabled={!!verdict}
                />
                <button
                    type="submit"
                    className="pr-btn pr-btn--primary"
                    disabled={!!verdict || !value.trim()}
                >
                    Tekshirish
                </button>
            </form>
            {verdict && (
                <div className={`pr-typed-feedback ${verdict.ok ? (verdict.exact ? 'ok' : 'close') : 'bad'}`}>
                    {verdict.ok && verdict.exact && <><Icon.Check /> To'g'ri!</>}
                    {verdict.ok && !verdict.exact && <><Icon.Warn /> Yaqin — to'g'risi: <strong>{word.word}</strong></>}
                    {!verdict.ok && <><Icon.X /> To'g'risi: <strong>{word.word}</strong></>}
                </div>
            )}
        </div>
    );
}


function ClozeMode({ word, onAnswer }) {
    // Replace the target word in `context` with a blank. If the context
    // doesn't contain the word, fall back to a generic prompt.
    const blanked = useMemo(() => {
        const ctx = word.context || '';
        if (!ctx) return null;
        const re = new RegExp(`\\b${word.word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
        if (!re.test(ctx)) return null;
        return ctx.replace(re, '_____');
    }, [word]);

    const [value, setValue] = useState('');
    const [verdict, setVerdict] = useState(null);
    const inputRef = useRef(null);
    useEffect(() => {
        setValue('');
        setVerdict(null);
        setTimeout(() => inputRef.current?.focus(), 60);
    }, [word.id]);

    const submit = (e) => {
        e?.preventDefault?.();
        if (verdict) return;
        const v = judgeTyped(value, word.word);
        setVerdict(v);
        const grade = v.exact ? 2 : v.ok ? 1 : 0;
        setTimeout(() => onAnswer({ grade, was_correct: v.ok }), 900);
    };

    if (!blanked) {
        // Cloze needs the source sentence — skip cleanly if absent so the
        // student doesn't see an empty box. Treat as "neutral skip" (grade 1).
        return (
            <div className="pr-card pr-typed">
                <div className="pr-typed-hint">
                    Bu so'z uchun gap kontekstida saqlanmagan.
                </div>
                <div className="pr-typed-ctx">«{word.word}»</div>
                <button
                    className="pr-btn pr-btn--primary"
                    onClick={() => onAnswer({ grade: 1, was_correct: true })}
                >
                    O'tkazib yuborish
                </button>
            </div>
        );
    }

    return (
        <div className="pr-card pr-typed">
            <div className="pr-typed-hint">Bo'shliqni to'ldiring:</div>
            <div className="pr-cloze-ctx">{blanked}</div>
            <form className="pr-typed-form" onSubmit={submit}>
                <input
                    ref={inputRef}
                    type="text"
                    autoComplete="off"
                    spellCheck={false}
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    placeholder="Yo'qolgan so'z…"
                    className={`pr-typed-input ${verdict ? (verdict.ok ? 'ok' : 'bad') : ''}`}
                    disabled={!!verdict}
                />
                <button
                    type="submit"
                    className="pr-btn pr-btn--primary"
                    disabled={!!verdict || !value.trim()}
                >
                    Tekshirish
                </button>
            </form>
            {verdict && (
                <div className={`pr-typed-feedback ${verdict.ok ? (verdict.exact ? 'ok' : 'close') : 'bad'}`}>
                    {verdict.ok && verdict.exact && <><Icon.Check /> To'g'ri!</>}
                    {verdict.ok && !verdict.exact && <><Icon.Warn /> Yaqin — to'g'risi: <strong>{word.word}</strong></>}
                    {!verdict.ok && <><Icon.X /> To'g'risi: <strong>{word.word}</strong></>}
                </div>
            )}
        </div>
    );
}


/* ═══════════════════════════════════════════════════════════════════════
   ORCHESTRATOR
   ═══════════════════════════════════════════════════════════════════════ */

export default function Practice() {
    const { request } = useHttp();

    const [phase,     setPhase]     = useState('pick');   // 'pick' | 'drill' | 'recap'
    const [mode,      setMode]      = useState('flashcard');
    const [filter,    setFilter]    = useState('all');    // 'all' | 'due' | 'weak'
    const [counts,    setCounts]    = useState({ due: 0, fragile: 0, total: 0 });
    const [active,    setActive]    = useState(null);     // resume candidate
    const [words,     setWords]     = useState([]);
    const [idx,       setIdx]       = useState(0);
    const [correct,   setCorrect]   = useState(0);
    const [sessionId, setSessionId] = useState(null);
    const [busy,      setBusy]      = useState(false);
    const [error,     setError]     = useState('');

    /* ── initial load: counts + resume candidate ── */
    useEffect(() => {
        request(`${BASE}/due-counts`, 'GET', null, headers())
            .then(setCounts)
            .catch(() => {});
        request(`${BASE}/session/active`, 'GET', null, headers())
            .then(setActive)
            .catch(() => {});
    }, [request]);

    const reloadCounts = useCallback(() => {
        request(`${BASE}/due-counts`, 'GET', null, headers())
            .then(setCounts)
            .catch(() => {});
    }, [request]);

    /* ── start a fresh drill ── */
    const start = useCallback(async () => {
        if (busy) return;
        setBusy(true);
        setError('');
        try {
            const params = new URLSearchParams({ count: String(DEFAULT_COUNT) });
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
            setWords(data);
            setIdx(0);
            setCorrect(0);
            setSessionId(s.id);
            setPhase('drill');
        } catch (e) {
            setError("Yuklab bo'lmadi — keyinroq urinib ko'ring");
        } finally {
            setBusy(false);
        }
    }, [busy, filter, mode, request]);

    /* ── resume an in-flight session ── */
    const resume = useCallback(async () => {
        if (!active?.progress) return;
        setBusy(true);
        try {
            const snap = active.progress;
            const ids = (snap.word_ids || []).join(',');
            const data = await request(
                `${BASE}/words?ids=${ids}`, 'GET', null, headers(),
            );
            if (!Array.isArray(data) || data.length === 0) {
                throw new Error('empty');
            }
            setWords(data);
            setIdx(Math.min(snap.idx || 0, data.length - 1));
            setCorrect(snap.correct || 0);
            setSessionId(active.id);
            setMode(active.mode);
            setPhase('drill');
        } catch (e) {
            setError("Sessiyani tiklab bo'lmadi");
        } finally {
            setBusy(false);
        }
    }, [active, request]);

    /* ── discard the active session ── */
    const discardActive = useCallback(async () => {
        if (!active?.id) return;
        try {
            await request(`${BASE}/session/${active.id}`, 'DELETE', null, headers());
            setActive(null);
        } catch {}
    }, [active, request]);

    /* ── persist progress whenever it changes mid-drill ── */
    useEffect(() => {
        if (phase !== 'drill' || !sessionId || words.length === 0) return;
        const snap = {
            idx,
            correct,
            word_ids: words.map((w) => w.id),
        };
        // Fire-and-forget; resume tolerates missing snapshots
        request(
            `${BASE}/session/${sessionId}/progress`,
            'PUT',
            JSON.stringify({ progress: snap }),
            headers(),
        ).catch(() => {});
    }, [phase, sessionId, idx, correct, words, request]);

    /* ── card answered ── */
    const onAnswer = useCallback(async ({ grade, was_correct }) => {
        const word = words[idx];
        if (!word) return;
        // Optimistically advance — submit SRS update in the background
        const nextCorrect = correct + (was_correct ? 1 : 0);
        setCorrect(nextCorrect);

        request(
            `${BASE}/result`, 'POST',
            JSON.stringify({ word_id: word.id, grade, was_correct }),
            headers(),
        ).catch(() => {});

        if (idx + 1 >= words.length) {
            // End of drill — finalise the session and show recap
            try {
                await request(
                    `${BASE}/session/${sessionId}/complete`,
                    'PUT',
                    JSON.stringify({
                        total_words: words.length,
                        correct: nextCorrect,
                    }),
                    headers(),
                );
            } catch {}
            setActive(null);
            setPhase('recap');
            reloadCounts();
        } else {
            setIdx(i => i + 1);
        }
    }, [words, idx, correct, sessionId, request, reloadCounts]);

    /* ── recap → back to picker ── */
    const goPick = useCallback(() => {
        setPhase('pick');
        setWords([]);
        setIdx(0);
        setCorrect(0);
        setSessionId(null);
    }, []);


    /* ─────────────────────────── render ─────────────────────────── */

    if (phase === 'drill') {
        const word = words[idx];
        if (!word) return null;
        return (
            <div className="pr-root pr-root--drill">
                <header className="pr-drill-head">
                    <button className="pr-back" onClick={async () => {
                        // Save progress snapshot already happened — just bail
                        goPick();
                    }}>← Chiqish</button>
                    <div className="pr-progress">
                        <div className="pr-progress-text">
                            {idx + 1} / {words.length}
                        </div>
                        <div className="pr-progress-bar">
                            <div
                                className="pr-progress-fill"
                                style={{ width: `${((idx + 1) / words.length) * 100}%` }}
                            />
                        </div>
                    </div>
                    <div className="pr-score">
                        <Icon.Check /> {correct}
                    </div>
                </header>

                {mode === 'flashcard' && <FlashcardMode key={word.id} word={word} onAnswer={onAnswer} />}
                {mode === 'quiz'      && <QuizMode      key={word.id} word={word} onAnswer={onAnswer} />}
                {mode === 'spelling'  && <SpellingMode  key={word.id} word={word} onAnswer={onAnswer} />}
                {mode === 'listening' && <ListeningMode key={word.id} word={word} onAnswer={onAnswer} />}
                {mode === 'cloze'     && <ClozeMode     key={word.id} word={word} onAnswer={onAnswer} />}
            </div>
        );
    }

    if (phase === 'recap') {
        const total = words.length || 1;
        const pct = Math.round((correct / total) * 100);
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
                            <span className="pr-recap-num">{total - correct}</span>
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
                        {' '}{active.progress?.idx ?? 0} / {active.progress?.word_ids?.length ?? 0}
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
        </div>
    );
}
