/**
 * Practice (Mashq) — SM-2 SRS drill over the student's saved dictionary.
 *
 * Ported from life_tracker's /learning/practice page. The 5 mode components
 * are inlined as helpers because they share the same phase state,
 * scoreboard, and SRS round-trip — splitting them adds prop-drilling
 * without separation of concerns.
 *
 * Phases:
 *   'pick'   — mode picker + filter chips + Resume + buckets + leeches + history
 *   'drill'  — one of the 5 mode components, looping over `words`
 *              · chunked (10 words / round) with a replay pass over misses
 *              · Quiz+ lets the student switch MCQ ↔ Spelling mid-drill
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
    { key: 'quiz',      label: 'Quiz+',      desc: '4 tadan birini tanlash yoki yozish', icon: '🎯' },
    { key: 'spelling',  label: 'Spelling',   desc: "So'zni yozing",       icon: '⌨️' },
    { key: 'listening', label: 'Listening',  desc: 'Eshitib yozish',      icon: '🎧' },
    { key: 'cloze',     label: 'Cloze',      desc: "Gapda bo'shliqni to'ldiring", icon: '✏️' },
];

const DEFAULT_COUNT = 10;
const CHUNK_SIZE = 10;          // words per round before the replay pass


/* ─── Close-match scoring for typed-answer modes ────────────────────────
   Levenshtein: exact = grade 2, off by 1-2 chars on words >= 4 chars = grade 1,
   else 0. The AI judge runs as a last-resort tiebreaker for "no" verdicts so
   "qo'shimcha funksiyalar" doesn't get rejected against "qo'shimcha funksiya". */
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
    Sparkle:(p) => <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1" /></svg>,
    Skull:  (p) => <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="9" cy="11" r="1.5" fill="currentColor" /><circle cx="15" cy="11" r="1.5" fill="currentColor" /><path d="M4 13a8 8 0 1 1 16 0v4a2 2 0 0 1-2 2h-2v3h-2v-3h-4v3h-2v-3H6a2 2 0 0 1-2-2z" /></svg>,
};


/* ═══════════════════════════════════════════════════════════════════════
   ASYNC JUDGE: local Levenshtein first, AI fallback on a "no" verdict.
   Used by all three typed modes. The AI call is best-effort — if it
   times out, errors, or hits the unconfigured branch, we keep the local
   "no" so the student doesn't sit waiting on a black-hole request.
   ═══════════════════════════════════════════════════════════════════════ */

const judgeTypedAsync = async (request, userInput, target, definition) => {
    const local = judgeTyped(userInput, target);
    if (local.ok) return { ...local, aiUsed: false };

    try {
        const aiTimeoutMs = 6000;
        const aiPromise = request(
            `${BASE}/judge-answer`,
            'POST',
            JSON.stringify({ user_input: userInput, target, definition }),
            headers(),
        );
        const timed = await Promise.race([
            aiPromise,
            new Promise((resolve) => setTimeout(() => resolve(null), aiTimeoutMs)),
        ]);
        if (timed && timed.ok) {
            return {
                ok: true,
                exact: timed.verdict === 'yes',
                aiUsed: true,
            };
        }
    } catch { /* fall through to local verdict */ }

    return { ...local, aiUsed: false };
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


/* Quiz+ mode — MCQ by default, but the student can toggle to typed
   "Spelling" sub-mode mid-drill if they want a harder check on a given
   card. Sub-mode is sticky for the rest of the drill until toggled back. */
function QuizMode({ word, subMode, onSubModeChange, onAnswer, request }) {
    const isSpelling = subMode === 'spelling';
    return (
        <div className="pr-card pr-quiz">
            <div className="pr-quiz-modeline">
                <button
                    className={`pr-sub ${!isSpelling ? 'active' : ''}`}
                    onClick={() => onSubModeChange('quiz')}
                    type="button"
                >MCQ</button>
                <button
                    className={`pr-sub ${isSpelling ? 'active' : ''}`}
                    onClick={() => onSubModeChange('spelling')}
                    type="button"
                >Yozish</button>
            </div>
            {isSpelling
                ? <TypedAnswer
                    word={word}
                    request={request}
                    onAnswer={onAnswer}
                    promptLabel="Ma'no:"
                    showContext
                />
                : <MCQ word={word} onAnswer={onAnswer} />
            }
        </div>
    );
}

/* MCQ — extracted so Quiz+ can mount it conditionally without duplicating
   the option-grid markup. */
function MCQ({ word, onAnswer }) {
    const [picked, setPicked] = useState(null);
    useEffect(() => { setPicked(null); }, [word.id]);

    const pick = (opt) => {
        if (picked !== null) return;
        const correct = opt === word.word;
        setPicked(opt);
        setTimeout(() => onAnswer({
            grade: correct ? 2 : 0,
            was_correct: correct,
        }), 650);
    };

    return (
        <>
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
        </>
    );
}


/* TypedAnswer — shared by Spelling, Listening, Cloze, and Quiz+ spelling
   sub-mode. Local Levenshtein first; AI judge runs as a tiebreaker for
   non-exact rejections so paraphrases / missing function words can pass. */
function TypedAnswer({ word, request, onAnswer, promptLabel, showContext, header }) {
    const [value, setValue] = useState('');
    const [verdict, setVerdict] = useState(null);
    const [judging, setJudging] = useState(false);
    const inputRef = useRef(null);

    useEffect(() => {
        setValue('');
        setVerdict(null);
        setJudging(false);
        setTimeout(() => inputRef.current?.focus(), 60);
    }, [word.id]);

    const submit = async (e) => {
        e?.preventDefault?.();
        if (verdict || judging) return;
        setJudging(true);
        const v = await judgeTypedAsync(request, value, word.word, word.context);
        setVerdict(v);
        setJudging(false);
        const grade = v.exact ? 2 : v.ok ? 1 : 0;
        setTimeout(() => onAnswer({ grade, was_correct: v.ok }), 900);
    };

    return (
        <>
            {header}
            {promptLabel && <div className="pr-typed-hint">{promptLabel}</div>}
            {showContext && (
                <div className="pr-typed-ctx">
                    {word.context || <em>Konteskt yo'q</em>}
                </div>
            )}
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
                    disabled={!!verdict || judging}
                />
                <button
                    type="submit"
                    className="pr-btn pr-btn--primary"
                    disabled={!!verdict || judging || !value.trim()}
                >
                    {judging ? 'Tekshirilmoqda…' : 'Tekshirish'}
                </button>
            </form>
            {verdict && (
                <div className={`pr-typed-feedback ${verdict.ok ? (verdict.exact ? 'ok' : 'close') : 'bad'}`}>
                    {verdict.ok && verdict.exact && <><Icon.Check /> To'g'ri!</>}
                    {verdict.ok && !verdict.exact && (
                        <>
                            <Icon.Warn /> Yaqin — to'g'risi: <strong>{word.word}</strong>
                            {verdict.aiUsed && <span className="pr-ai-tag"><Icon.Sparkle /> AI</span>}
                        </>
                    )}
                    {!verdict.ok && <><Icon.X /> To'g'risi: <strong>{word.word}</strong></>}
                </div>
            )}
        </>
    );
}


function SpellingMode({ word, onAnswer, request }) {
    return (
        <div className="pr-card pr-typed">
            <TypedAnswer
                word={word}
                request={request}
                onAnswer={onAnswer}
                promptLabel="Ma'no:"
                showContext
            />
        </div>
    );
}


function ListeningMode({ word, onAnswer, request }) {
    const speak = useCallback(() => {
        if (typeof window === 'undefined' || !window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(word.word);
        u.rate = 0.85;
        u.lang = 'en-US';
        window.speechSynthesis.speak(u);
    }, [word.word]);
    useEffect(() => { speak(); }, [speak]);

    return (
        <div className="pr-card pr-typed">
            <TypedAnswer
                word={word}
                request={request}
                onAnswer={onAnswer}
                promptLabel="Eshitganingizni yozing"
                header={
                    <button type="button" className="pr-listen-btn" onClick={speak} title="Qayta eshitish">
                        <Icon.Volume /> <span>Eshitish</span>
                    </button>
                }
            />
        </div>
    );
}


function ClozeMode({ word, onAnswer, request }) {
    const blanked = useMemo(() => {
        const ctx = word.context || '';
        if (!ctx) return null;
        const re = new RegExp(`\\b${word.word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
        if (!re.test(ctx)) return null;
        return ctx.replace(re, '_____');
    }, [word]);

    if (!blanked) {
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
            <TypedAnswer
                word={word}
                request={request}
                onAnswer={onAnswer}
                promptLabel="Bo'shliqni to'ldiring:"
                header={<div className="pr-cloze-ctx">{blanked}</div>}
            />
        </div>
    );
}


/* ═══════════════════════════════════════════════════════════════════════
   PRE-DRILL SURFACES — buckets, leeches, history, queue preview
   ═══════════════════════════════════════════════════════════════════════ */

function BucketsBar({ buckets }) {
    const total = Object.values(buckets).reduce((a, b) => a + b, 0);
    if (total === 0) return null;
    const cfg = [
        { key: 'fragile',  label: 'Qiyin',     color: '#f43f5e' },
        { key: 'learning', label: "O'rganish", color: '#6c5ce7' },
        { key: 'solid',    label: 'Mustahkam', color: '#10b981' },
        { key: 'mastered', label: 'O\'zlashtirilgan', color: '#0d9488' },
    ];
    return (
        <div className="pr-buckets">
            <div className="pr-buckets-bar">
                {cfg.map((b) => {
                    const n = buckets[b.key] || 0;
                    if (n === 0) return null;
                    const pct = (n / total) * 100;
                    return (
                        <div
                            key={b.key}
                            className="pr-buckets-seg"
                            style={{ width: `${pct}%`, background: b.color }}
                            title={`${b.label}: ${n}`}
                        />
                    );
                })}
            </div>
            <div className="pr-buckets-legend">
                {cfg.map((b) => (
                    <div key={b.key} className="pr-buckets-lg">
                        <span className="pr-buckets-dot" style={{ background: b.color }} />
                        <span>{b.label}</span>
                        <strong>{buckets[b.key] || 0}</strong>
                    </div>
                ))}
            </div>
        </div>
    );
}

function LeechAlert({ leeches }) {
    if (!leeches.length) return null;
    return (
        <div className="pr-leech">
            <div className="pr-leech-head">
                <Icon.Skull />
                <span>Ko'p marta unutgan so'zlar ({leeches.length})</span>
            </div>
            <div className="pr-leech-list">
                {leeches.slice(0, 5).map((w) => (
                    <div key={w.id} className="pr-leech-row">
                        <strong>{w.word}</strong>
                        <span className="pr-leech-meta">
                            {w.lapses}× unutilgan
                        </span>
                    </div>
                ))}
            </div>
            <p className="pr-leech-hint">
                Bu so'zlarni qayta yozib chiqing yoki tushuntirishni o'zgartiring — eski yondashuv ishlamayapti.
            </p>
        </div>
    );
}

function HistoryStrip({ history }) {
    if (!history.length) return null;
    return (
        <div className="pr-history">
            <div className="pr-history-label">So'nggi mashqlar</div>
            <div className="pr-history-rows">
                {history.slice(0, 5).map((s) => {
                    const pct = s.total_words > 0
                        ? Math.round((s.correct / s.total_words) * 100)
                        : 0;
                    return (
                        <div key={s.id} className="pr-history-row">
                            <div className="pr-history-mode">
                                {MODES.find(m => m.key === s.mode)?.icon}
                                {' '}
                                {MODES.find(m => m.key === s.mode)?.label || s.mode}
                            </div>
                            <div className="pr-history-score">
                                {s.correct}/{s.total_words}
                            </div>
                            <div
                                className={`pr-history-pct ${pct >= 80 ? 'ok' : pct >= 50 ? 'mid' : 'bad'}`}
                            >{pct}%</div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

function QueuePreview({ words }) {
    if (!words.length) return null;
    return (
        <div className="pr-queue">
            <div className="pr-queue-label">Navbatdagi so'zlar (birinchi 5 ta)</div>
            <div className="pr-queue-list">
                {words.slice(0, 5).map((w) => {
                    let tag = 'Yangi';
                    let tagCls = 'new';
                    if ((w.review_count || 0) > 0) {
                        if ((w.lapses || 0) >= 2 || (w.ease_factor || 2.5) < 2.0) {
                            tag = 'Qiyin'; tagCls = 'weak';
                        } else if ((w.interval_days || 0) > 21) {
                            tag = "O'zlashtirilgan"; tagCls = 'master';
                        } else if ((w.interval_days || 0) > 7) {
                            tag = 'Mustahkam'; tagCls = 'solid';
                        } else {
                            tag = "O'rganish"; tagCls = 'learn';
                        }
                    }
                    return (
                        <div key={w.id} className="pr-queue-row">
                            <strong className="pr-queue-word">{w.word}</strong>
                            <span className={`pr-queue-tag pr-queue-tag--${tagCls}`}>{tag}</span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}


/* ═══════════════════════════════════════════════════════════════════════
   ORCHESTRATOR — phases, chunked rounds, replay-missed pass
   ═══════════════════════════════════════════════════════════════════════ */

export default function Practice() {
    const { request } = useHttp();

    const [phase,     setPhase]     = useState('pick');   // 'pick' | 'drill' | 'recap'
    const [mode,      setMode]      = useState('flashcard');
    const [subMode,   setSubMode]   = useState('quiz');   // Quiz+ only
    const [filter,    setFilter]    = useState('all');
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
    const [sessionId, setSessionId] = useState(null);
    const [busy,      setBusy]      = useState(false);
    const [error,     setError]     = useState('');

    /* ── load all pre-drill surfaces in parallel ── */
    const reloadAll = useCallback(() => {
        const wrap = (url) => request(`${BASE}${url}`, 'GET', null, headers()).catch(() => null);
        Promise.all([
            wrap('/due-counts'),
            wrap('/session/active'),
            wrap('/buckets'),
            wrap('/leeches?limit=10'),
            wrap('/history?limit=5'),
        ]).then(([c, a, b, l, h]) => {
            if (c) setCounts(c);
            setActive(a || null);
            if (b) setBuckets(b);
            setLeeches(Array.isArray(l) ? l : []);
            setHistory(Array.isArray(h) ? h : []);
        });
    }, [request]);

    useEffect(() => { reloadAll(); }, [reloadAll]);

    /* ── preview the queue when the filter changes (or on mount) ── */
    useEffect(() => {
        const params = new URLSearchParams({ count: String(DEFAULT_COUNT) });
        if (filter === 'due')  params.set('due_only',  'true');
        if (filter === 'weak') params.set('weak_only', 'true');
        request(`${BASE}/words?${params.toString()}`, 'GET', null, headers())
            .then((data) => setPreview(Array.isArray(data) ? data : []))
            .catch(() => setPreview([]));
    }, [filter, request]);

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
            setQueue(data.map((w) => ({ word: w, replay: false })));
            setPos(0);
            setCorrect(0);
            setMissed([]);
            setRound(1);
            setSessionId(s.id);
            setSubMode('quiz');
            setPhase('drill');
        } catch {
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
            setSessionId(active.id);
            setMode(active.mode);
            setSubMode(snap.subMode || 'quiz');
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
            subMode,
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
    }, [phase, sessionId, pos, correct, missed, round, subMode, queue, request]);

    /* ── card answered ── */
    const onAnswer = useCallback(async ({ grade, was_correct }) => {
        const item = queue[pos];
        if (!item) return;
        const wasMiss = !was_correct;

        // Only count toward score on the FIRST attempt (round 1, non-replay).
        const isReplayItem = item.replay;
        if (!isReplayItem && was_correct) {
            setCorrect((c) => c + 1);
        }

        // Track miss for end-of-chunk replay (only first-pass misses; replay
        // misses go back through normal SRS but don't trigger another loop).
        let newMissed = missed;
        if (!isReplayItem && wasMiss) {
            newMissed = [...missed, item.word.id];
            setMissed(newMissed);
        }

        // Submit SRS update (fire-and-forget; the UI keeps moving).
        request(
            `${BASE}/result`, 'POST',
            JSON.stringify({ word_id: item.word.id, grade, was_correct }),
            headers(),
        ).catch(() => {});

        const nextPos = pos + 1;
        const endOfQueue = nextPos >= queue.length;

        // End of a chunk (every CHUNK_SIZE words on the FIRST pass) → splice
        // the missed cards back in as a replay round before continuing.
        const endOfChunk = !isReplayItem && nextPos % CHUNK_SIZE === 0;
        const finalChunkOfRun = nextPos === queue.filter((q) => !q.replay).length;

        if ((endOfChunk || finalChunkOfRun) && newMissed.length > 0) {
            const idToWord = Object.fromEntries(queue.map((q) => [q.word.id, q.word]));
            const replayItems = newMissed
                .map((id) => idToWord[id])
                .filter(Boolean)
                .map((word) => ({ word, replay: true }));
            // Insert replays right after the current chunk boundary.
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
    }, [queue, pos, correct, missed, sessionId, request, reloadAll]);

    const goPick = useCallback(() => {
        setPhase('pick');
        setQueue([]);
        setPos(0);
        setCorrect(0);
        setMissed([]);
        setRound(1);
        setSessionId(null);
    }, []);


    /* ─────────────────────────── render ─────────────────────────── */

    if (phase === 'drill') {
        const item = queue[pos];
        if (!item) return null;
        const word = item.word;
        const firstPassTotal = queue.filter((q) => !q.replay).length;
        const firstPassDone  = queue.slice(0, pos).filter((q) => !q.replay).length;

        return (
            <div className="pr-root pr-root--drill">
                <header className="pr-drill-head">
                    <button className="pr-back" onClick={goPick}>← Chiqish</button>
                    <div className="pr-progress">
                        <div className="pr-progress-text">
                            {firstPassDone + 1} / {firstPassTotal}
                            {item.replay && <span className="pr-replay-tag"> · qaytarish</span>}
                            {round > 1 && !item.replay && <span className="pr-round-tag"> · raund {round}</span>}
                        </div>
                        <div className="pr-progress-bar">
                            <div
                                className="pr-progress-fill"
                                style={{ width: `${((firstPassDone + 1) / firstPassTotal) * 100}%` }}
                            />
                        </div>
                    </div>
                    <div className="pr-score">
                        <Icon.Check /> {correct}
                    </div>
                </header>

                {mode === 'flashcard' && <FlashcardMode key={word.id} word={word} onAnswer={onAnswer} />}
                {mode === 'quiz'      && <QuizMode      key={word.id} word={word} subMode={subMode} onSubModeChange={setSubMode} onAnswer={onAnswer} request={request} />}
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
        </div>
    );
}
