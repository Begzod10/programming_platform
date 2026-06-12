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


/* Quiz+ — life_tracker's two-pass design: recognition pass (MCQ over the
   whole queue) followed by a recall pass (typed Spelling over the same
   queue). A word only counts as "correct" if it passed BOTH passes.
   The orchestrator drives which pass via the `qpPass` prop; the user
   doesn't toggle. */
function QuizMode({ word, qpPass, onAnswer, request }) {
    const isSpelling = qpPass === 'spelling';
    return (
        <div className="pr-card pr-quiz">
            <div className="pr-quiz-modeline pr-quiz-modeline--locked">
                <span className={`pr-sub ${!isSpelling ? 'active' : ''}`}>
                    1. Tanish (MCQ)
                </span>
                <span className={`pr-sub ${isSpelling ? 'active' : ''}`}>
                    2. Eslab qolish (Yozish)
                </span>
            </div>
            {isSpelling
                ? <TypedAnswer
                    word={word}
                    request={request}
                    onAnswer={onAnswer}
                    promptLabel="So'zni yozing — birinchi raundda ko'rdingiz"
                    showContext
                />
                : <MCQ word={word} onAnswer={onAnswer} />
            }
        </div>
    );
}

/* MCQ — show the word, ask the student to pick its meaning. This is the
   natural flashcard direction. For entries with no saved context we fall
   back to the old "context → pick word" direction so the card is still
   usable. */
function MCQ({ word, onAnswer }) {
    const [picked, setPicked] = useState(null);
    useEffect(() => { setPicked(null); }, [word.id]);

    // Decide direction once per word. Meaning-side MCQ needs a real context
    // AND at least one extra distractor to be a fair test.
    const ctxOpts = Array.isArray(word.context_options) ? word.context_options : [];
    const meaningMode =
        Boolean((word.context || '').trim()) &&
        ctxOpts.filter(o => (o || '').trim()).length >= 2;

    const prompt = meaningMode
        ? "Bu so'zning ma'nosi qaysi?"
        : "Bu ma'noga qaysi so'z mos keladi?";

    const center = meaningMode
        ? <span className="pr-quiz-word">{word.word}</span>
        : (word.context || <em>Konteskt yo'q — taxminan tanlang</em>);

    const opts = meaningMode ? ctxOpts : (word.options || []);
    const correctValue = meaningMode ? word.context : word.word;

    const pick = (opt) => {
        if (picked !== null) return;
        const correct = opt === correctValue;
        setPicked(opt);
        setTimeout(() => onAnswer({
            grade: correct ? 2 : 0,
            was_correct: correct,
        }), 650);
    };

    return (
        <>
            <div className="pr-quiz-prompt">{prompt}</div>
            <div className={`pr-quiz-ctx ${meaningMode ? 'pr-quiz-ctx--word' : ''}`}>
                {center}
            </div>
            <div className={`pr-quiz-opts ${meaningMode ? 'pr-quiz-opts--meanings' : ''}`}>
                {opts.map((opt, idx) => {
                    const isCorrect = opt === correctValue;
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
                            key={`${idx}-${opt}`}
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
   SCOPE PICKER — category/course/lesson narrowing
   Mirrors life_tracker's folder/module ScopePicker using the
   category → course → lesson chain that already lives on the words.
   ═══════════════════════════════════════════════════════════════════════ */

function ScopePicker({ tree, scope, onChange }) {
    if (!tree.length) return null;

    // Flatten the tree into select options for the two dropdowns. A more
    // elaborate tree-control would be overkill for the 1-3 courses most
    // students have words in.
    const allCourses = tree.flatMap((cat) => cat.courses);
    const activeCourse = allCourses.find((c) => c.id === scope.course_id);

    return (
        <section className="pr-section">
            <h3 className="pr-section-title">Doira (ixtiyoriy)</h3>
            <div className="pr-scope">
                <label className="pr-scope-field">
                    <span className="pr-scope-lbl">Kurs</span>
                    <select
                        className="pr-scope-select"
                        value={scope.course_id || ''}
                        onChange={(e) => {
                            const v = e.target.value;
                            onChange({
                                category_id: null,
                                course_id: v ? Number(v) : null,
                                lesson_id: null,
                            });
                        }}
                    >
                        <option value="">Barchasi</option>
                        {allCourses.map((c) => (
                            <option key={c.id} value={c.id}>{c.title}</option>
                        ))}
                    </select>
                </label>
                <label className="pr-scope-field">
                    <span className="pr-scope-lbl">Dars</span>
                    <select
                        className="pr-scope-select"
                        value={scope.lesson_id || ''}
                        onChange={(e) => {
                            const v = e.target.value;
                            onChange({
                                ...scope,
                                lesson_id: v ? Number(v) : null,
                            });
                        }}
                        disabled={!activeCourse}
                    >
                        <option value="">
                            {activeCourse ? 'Barcha darslar' : 'Avval kursni tanlang'}
                        </option>
                        {(activeCourse?.lessons || []).map((l) => (
                            <option key={l.id} value={l.id}>{l.title}</option>
                        ))}
                    </select>
                </label>
                {(scope.course_id || scope.lesson_id) && (
                    <button
                        type="button"
                        className="pr-scope-clear"
                        onClick={() => onChange({ category_id: null, course_id: null, lesson_id: null })}
                    >Tozalash</button>
                )}
            </div>
        </section>
    );
}


/* ═══════════════════════════════════════════════════════════════════════
   FIRE STREAK — in-drill gamification
   Consecutive correct answers grow a counter shown as a top-right badge.
   At level 1 (3-4), 2 (5-7), 3 (8+) a full-screen radial fire overlay
   activates behind the card. Resets on any wrong answer.
   ═══════════════════════════════════════════════════════════════════════ */

const FIRE_OVERLAY_ID = 'pr-fire-overlay';
const FIRE_KEYFRAMES_ID = 'pr-fire-keyframes';

const fireLevelFor = (streak) => {
    if (streak >= 8) return 3;
    if (streak >= 5) return 2;
    if (streak >= 3) return 1;
    return 0;
};

function ensureFireKeyframes() {
    if (typeof document === 'undefined') return;
    if (document.getElementById(FIRE_KEYFRAMES_ID)) return;
    const s = document.createElement('style');
    s.id = FIRE_KEYFRAMES_ID;
    s.textContent = `
        @keyframes pr-fire-pulse {
            0%, 100% { opacity: 0.85; transform: scaleY(1); }
            20%      { opacity: 1;    transform: scaleY(1.04); }
            50%      { opacity: 0.72; transform: scaleY(0.97); }
            75%      { opacity: 0.94; transform: scaleY(1.02); }
        }
        @keyframes pr-fire-wave {
            0%, 100% { transform: translateX(0)    scaleX(1);    opacity: 0.9; }
            33%      { transform: translateX(1.5%) scaleX(1.02); opacity: 1;   }
            66%      { transform: translateX(-1%)  scaleX(0.98); opacity: 0.8; }
        }
        @keyframes pr-fire-ember {
            0%, 100% { opacity: 0.45; }
            40%      { opacity: 0.8; }
            70%      { opacity: 0.55; }
        }
        @keyframes pr-fire-glow {
            0%, 100% { box-shadow: 0 0 18px 6px rgba(255, 50, 0, 0.65), 0 0 40px 14px rgba(255, 90, 0, 0.35); }
            50%      { box-shadow: 0 0 28px 10px rgba(255, 70, 0, 0.8), 0 0 55px 20px rgba(255, 120, 0, 0.45); }
        }
        @keyframes pr-fire-badge-in {
            from { transform: scale(0.7); opacity: 0; }
            to   { transform: scale(1);   opacity: 1; }
        }
    `;
    document.head.appendChild(s);
}

function useFireOverlay(level) {
    useEffect(() => {
        if (typeof document === 'undefined') return;
        ensureFireKeyframes();
        const existing = document.getElementById(FIRE_OVERLAY_ID);
        if (level === 0) {
            existing?.remove();
            return;
        }

        const el = existing || (() => {
            const d = document.createElement('div');
            d.id = FIRE_OVERLAY_ID;
            document.body.appendChild(d);
            return d;
        })();

        const a1 = Math.min(0.58 + level * 0.05, 0.78);
        const a2 = Math.min(0.32 + level * 0.04, 0.52);
        el.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:9998;';
        el.innerHTML = `
            <div style="position:absolute;inset:0;
                background:
                    radial-gradient(ellipse at 50% 120%, rgba(255,45,0,${a1}) 0%, rgba(255,105,0,${a2}) 24%, rgba(160,22,0,0.09) 52%, transparent 74%),
                    radial-gradient(ellipse at 18% 114%, rgba(255,60,0,${a2 * 0.8}) 0%, transparent 35%),
                    radial-gradient(ellipse at 82% 114%, rgba(255,60,0,${a2 * 0.8}) 0%, transparent 35%);
                animation: pr-fire-pulse 1.9s ease-in-out infinite;"></div>
            <div style="position:absolute;inset:0;
                background: radial-gradient(ellipse at 50% 118%, rgba(255,25,0,0.28) 0%, transparent 48%);
                animation: pr-fire-wave 2.4s ease-in-out infinite;"></div>
            <div style="position:absolute;bottom:0;left:0;right:0;height:40vh;
                background: linear-gradient(to top, rgba(200,15,0,0.55) 0%, rgba(255,70,0,0.22) 35%, transparent 80%);
                animation: pr-fire-ember 2.9s ease-in-out infinite;"></div>
            <div style="position:absolute;bottom:0;left:0;right:0;height:4px;
                background: rgba(255,35,0,0.95);
                animation: pr-fire-glow 1.7s ease-in-out infinite;"></div>
        `;

        return () => { document.getElementById(FIRE_OVERLAY_ID)?.remove(); };
    }, [level]);
}

function FireBadge({ streak }) {
    if (streak === 0) return null;
    return (
        <div className="pr-fire-badge" key={streak}>
            🔥 {streak}
        </div>
    );
}


/* ═══════════════════════════════════════════════════════════════════════
   STATISTIKA — read-only dashboard fed by /v1/dictionary/practice/stats
   ═══════════════════════════════════════════════════════════════════════ */

/* Small horizontal-bar list used by the Taqsimot panel. Keeps the
   render dumb so by_difficulty / by_part_of_speech share the same shape. */
function BreakdownBars({ items, total, palette }) {
    const entries = Object.entries(items);
    if (!entries.length || total === 0) {
        return <div className="pr-breakdown-empty">Yo'q</div>;
    }
    return (
        <div className="pr-breakdown-bars">
            {entries.map(([key, n], i) => {
                const pct = Math.round((n / total) * 100);
                return (
                    <div key={key} className="pr-breakdown-row">
                        <div className="pr-breakdown-row-head">
                            <span className="pr-breakdown-name">{key}</span>
                            <span className="pr-breakdown-count">
                                {n} <span className="pr-breakdown-pct">· {pct}%</span>
                            </span>
                        </div>
                        <div className="pr-breakdown-track">
                            <div
                                className="pr-breakdown-fill"
                                style={{
                                    width: `${pct}%`,
                                    background: palette[i % palette.length],
                                }}
                            />
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

function Statistika() {
    const { request } = useHttp();
    const [stats, setStats]         = useState(null);
    const [needsReview, setNeedsReview] = useState({ items: [], total: 0 });
    const [breakdown, setBreakdown] = useState({ total: 0, by_difficulty: {}, by_part_of_speech: {} });
    const [loading, setLoading]     = useState(true);
    const [error, setError]         = useState('');

    useEffect(() => {
        let cancelled = false;
        setLoading(true);
        Promise.all([
            request(`${BASE}/stats`, 'GET', null, headers()),
            request(`${BASE}/needs-review?limit=10`, 'GET', null, headers()).catch(() => ({ items: [], total: 0 })),
            request(`${BASE}/breakdown`, 'GET', null, headers()).catch(() => ({ total: 0, by_difficulty: {}, by_part_of_speech: {} })),
        ])
            .then(([s, nr, br]) => {
                if (cancelled) return;
                setStats(s || null);
                setNeedsReview(nr || { items: [], total: 0 });
                setBreakdown(br || { total: 0, by_difficulty: {}, by_part_of_speech: {} });
                setError('');
            })
            .catch(() => {
                if (cancelled) return;
                setError("Statistikani yuklab bo'lmadi");
            })
            .finally(() => { if (!cancelled) setLoading(false); });
        return () => { cancelled = true; };
    }, [request]);

    if (loading) {
        return <div className="pr-stats-loading">Yuklanmoqda…</div>;
    }
    if (error || !stats) {
        return <div className="pr-error">{error || 'Maʼlumot topilmadi'}</div>;
    }

    const { streak, last_7_days, mode_breakdown, totals } = stats;

    // Scale the bar heights against the busiest day in the window so the
    // shape of the week reads correctly even on a light workload.
    const maxWordsDay = Math.max(1, ...last_7_days.map((d) => d.words));

    const dayLabel = (iso) => {
        const d = new Date(iso);
        // Local short weekday label — Uzbek shortcodes.
        const days = ['Ya', 'Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh'];
        return days[d.getDay()];
    };

    return (
        <div className="pr-stats">
            {/* ── Streak hero ─────────────────────────────────────────── */}
            <div className={`pr-streak ${streak.current > 0 ? 'pr-streak--alive' : ''}`}>
                <div className="pr-streak-flame">🔥</div>
                <div className="pr-streak-body">
                    <div className="pr-streak-num">{streak.current}</div>
                    <div className="pr-streak-lbl">
                        {streak.current === 0 ? 'Bugundan boshlang' : 'kunlik streak'}
                    </div>
                </div>
                <div className="pr-streak-meta">
                    <div>
                        <span className="pr-streak-meta-num">{streak.longest}</span>
                        <span className="pr-streak-meta-lbl">eng uzun</span>
                    </div>
                    <div>
                        <span className="pr-streak-meta-num">
                            {streak.today_practised ? '✓' : '–'}
                        </span>
                        <span className="pr-streak-meta-lbl">bugun</span>
                    </div>
                </div>
            </div>

            {/* ── 7-day activity bar chart ────────────────────────────── */}
            <section className="pr-section">
                <h3 className="pr-section-title">Oxirgi 7 kun</h3>
                <div className="pr-week">
                    {last_7_days.map((d) => {
                        const h = (d.words / maxWordsDay) * 100;
                        return (
                            <div key={d.date} className="pr-week-col">
                                <div className="pr-week-bar-wrap">
                                    <div
                                        className={`pr-week-bar ${d.words === 0 ? 'pr-week-bar--empty' : ''}`}
                                        style={{ height: `${Math.max(h, 4)}%` }}
                                        title={`${d.date}: ${d.words} so'z · ${d.accuracy}%`}
                                    />
                                </div>
                                <div className="pr-week-label">{dayLabel(d.date)}</div>
                                <div className="pr-week-num">{d.words || ''}</div>
                            </div>
                        );
                    })}
                </div>
            </section>

            {/* ── Mode-accuracy breakdown ─────────────────────────────── */}
            {mode_breakdown.length > 0 && (
                <section className="pr-section">
                    <h3 className="pr-section-title">Rejimlar bo'yicha aniqlik</h3>
                    <div className="pr-modebars">
                        {mode_breakdown.map((m) => {
                            const meta = MODES.find((x) => x.key === m.mode);
                            return (
                                <div key={m.mode} className="pr-modebar">
                                    <div className="pr-modebar-head">
                                        <span className="pr-modebar-icon">{meta?.icon || '🔸'}</span>
                                        <span className="pr-modebar-name">{meta?.label || m.mode}</span>
                                        <span className="pr-modebar-pct">{m.accuracy}%</span>
                                    </div>
                                    <div className="pr-modebar-track">
                                        <div
                                            className="pr-modebar-fill"
                                            style={{ width: `${m.accuracy}%` }}
                                        />
                                    </div>
                                    <div className="pr-modebar-foot">
                                        {m.sessions} sessiya · {m.words} so'z
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </section>
            )}

            {/* ── Totals card ─────────────────────────────────────────── */}
            <section className="pr-section">
                <h3 className="pr-section-title">Umumiy</h3>
                <div className="pr-totals">
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.words}</div>
                        <div className="pr-total-lbl">jami so'z</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.mastered}</div>
                        <div className="pr-total-lbl">o'zlashtirilgan</div>
                        <div className="pr-total-sub">{totals.mastery_pct}%</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.sessions}</div>
                        <div className="pr-total-lbl">sessiya</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.drilled}</div>
                        <div className="pr-total-lbl">mashq</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.accuracy}%</div>
                        <div className="pr-total-lbl">o'rtacha aniqlik</div>
                    </div>
                </div>
            </section>

            {/* ── Taqsimot — by-difficulty + by-PoS ─────────────────── */}
            {breakdown.total > 0 && (
                <section className="pr-section">
                    <h3 className="pr-section-title">Taqsimot</h3>
                    <div className="pr-breakdown">
                        <div className="pr-breakdown-col">
                            <div className="pr-breakdown-label">Daraja</div>
                            <BreakdownBars
                                items={breakdown.by_difficulty}
                                total={breakdown.total}
                                palette={['#10b981', '#6c5ce7', '#f43f5e', '#0d9488', '#475569']}
                            />
                        </div>
                        <div className="pr-breakdown-col">
                            <div className="pr-breakdown-label">So'z turi</div>
                            <BreakdownBars
                                items={breakdown.by_part_of_speech}
                                total={breakdown.total}
                                palette={['#6c5ce7', '#0d9488', '#f59e0b', '#f43f5e', '#475569']}
                            />
                        </div>
                    </div>
                </section>
            )}

            {/* ── Mashq qilingani yaxshi ── top-N words to study next ──
                Order matches the backend's ladder: never-reviewed first,
                then struggling, then long-time-no-see. */}
            {needsReview.items.length > 0 && (
                <section className="pr-section">
                    <div className="pr-section-head">
                        <h3 className="pr-section-title">Mashq qilingani yaxshi</h3>
                        {needsReview.total > needsReview.items.length && (
                            <span className="pr-section-more">
                                yana {needsReview.total - needsReview.items.length}
                            </span>
                        )}
                    </div>
                    <div className="pr-needs">
                        {needsReview.items.map((w) => {
                            let tag, tagCls;
                            if (w.review_count === 0) {
                                tag = 'Yangi'; tagCls = 'new';
                            } else if (w.accuracy !== null && w.accuracy < 70) {
                                tag = `${w.accuracy}%`; tagCls = 'low';
                            } else {
                                tag = 'Eski'; tagCls = 'stale';
                            }
                            return (
                                <div key={w.id} className="pr-needs-row">
                                    <strong className="pr-needs-word">{w.word}</strong>
                                    {w.context && (
                                        <span className="pr-needs-ctx">{w.context}</span>
                                    )}
                                    <span className={`pr-needs-tag pr-needs-tag--${tagCls}`}>{tag}</span>
                                </div>
                            );
                        })}
                    </div>
                </section>
            )}
        </div>
    );
}


/* ═══════════════════════════════════════════════════════════════════════
   HISTORY — drill-results sub-tab with by-date / by-month / averages
   ═══════════════════════════════════════════════════════════════════════ */

function formatDateShort(iso) {
    // "2026-06-10" → "10 Iyn"
    const months = ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyn',
                    'Iyl', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek'];
    const d = new Date(iso + 'T00:00:00');
    return `${d.getDate()} ${months[d.getMonth()]}`;
}

function formatMonth(key) {
    // "2026-06" → "Iyun 2026"
    const months = ['Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun',
                    'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr'];
    const [y, m] = key.split('-');
    return `${months[Number(m) - 1]} ${y}`;
}

function formatDateTime(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    const pad = (n) => String(n).padStart(2, '0');
    return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function formatDuration(seconds) {
    if (seconds == null) return '—';
    if (seconds < 60) return `${seconds}s`;
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return s ? `${m}m ${s}s` : `${m}m`;
}

function Sparkline({ points, accessor = (d) => d.words, ariaLabel }) {
    // Compact inline SVG sparkline. Width is intrinsic via viewBox.
    if (!points.length) return null;
    const W = 600, H = 60, PAD = 4;
    const max = Math.max(1, ...points.map(accessor));
    const step = (W - PAD * 2) / Math.max(1, points.length - 1);
    const path = points
        .map((p, i) => {
            const x = PAD + i * step;
            const y = H - PAD - (accessor(p) / max) * (H - PAD * 2);
            return `${i === 0 ? 'M' : 'L'}${x.toFixed(2)},${y.toFixed(2)}`;
        })
        .join(' ');
    const area = `${path} L${PAD + (points.length - 1) * step},${H - PAD} L${PAD},${H - PAD} Z`;
    return (
        <svg
            viewBox={`0 0 ${W} ${H}`}
            className="pr-spark"
            preserveAspectRatio="none"
            aria-label={ariaLabel || ''}
        >
            <path d={area} className="pr-spark-fill" />
            <path d={path} className="pr-spark-line" />
        </svg>
    );
}

function PeriodBars({ points, accessor, labelFor }) {
    // Horizontal bars — one per period bucket. Picks the busiest bucket as
    // the 100% reference so quiet weeks still register visually.
    const max = Math.max(1, ...points.map(accessor));
    return (
        <div className="pr-period">
            {points.map((p, i) => {
                const v = accessor(p);
                const w = (v / max) * 100;
                return (
                    <div key={i} className="pr-period-row">
                        <div className="pr-period-label">{labelFor(p)}</div>
                        <div className="pr-period-track">
                            <div
                                className={`pr-period-fill ${v === 0 ? 'pr-period-fill--empty' : ''}`}
                                style={{ width: `${Math.max(w, v > 0 ? 4 : 0)}%` }}
                            />
                        </div>
                        <div className="pr-period-val">
                            <span className="pr-period-val-num">{p.sessions}</span>
                            <span className="pr-period-val-sub">{p.words || 0} so'z · {p.accuracy || 0}%</span>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

function History() {
    const { request } = useHttp();
    const [data, setData]     = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError]   = useState('');
    const [grain, setGrain]   = useState('day');   // 'day' | 'month'
    const [expanded, setExpanded] = useState(false);

    useEffect(() => {
        let cancelled = false;
        setLoading(true);
        request(`${BASE}/sessions-overview`, 'GET', null, headers())
            .then((d) => {
                if (cancelled) return;
                setData(d);
                setError('');
            })
            .catch(() => {
                if (cancelled) return;
                setError("Tarixni yuklab bo'lmadi");
            })
            .finally(() => { if (!cancelled) setLoading(false); });
        return () => { cancelled = true; };
    }, [request]);

    if (loading) return <div className="pr-stats-loading">Yuklanmoqda…</div>;
    if (error || !data) return <div className="pr-error">{error || 'Maʼlumot topilmadi'}</div>;

    const { totals, averages, by_date, by_month, recent } = data;

    // For the by-day bars/sparkline we trim leading empty days so the chart
    // doesn't always start with a wall of zeros. We keep at least the last 14.
    const trimmedDays = (() => {
        const firstActive = by_date.findIndex((d) => d.sessions > 0);
        if (firstActive === -1) return by_date.slice(-14);
        const start = Math.min(firstActive, by_date.length - 14);
        return by_date.slice(Math.max(0, start));
    })();

    const visibleRecent = expanded ? recent : recent.slice(0, 5);

    return (
        <div className="pr-hist">
            {/* ── Averages row ────────────────────────────────────────── */}
            <section className="pr-section">
                <h3 className="pr-section-title">O'rtacha ko'rsatkichlar</h3>
                <div className="pr-avg-grid">
                    <div className="pr-avg">
                        <div className="pr-avg-num">{averages.per_session_accuracy}%</div>
                        <div className="pr-avg-lbl">o'rtacha aniqlik</div>
                    </div>
                    <div className="pr-avg">
                        <div className="pr-avg-num">{averages.per_session_words}</div>
                        <div className="pr-avg-lbl">so'z / mashq</div>
                    </div>
                    <div className="pr-avg">
                        <div className="pr-avg-num">
                            {averages.per_session_minutes || '—'}
                            {averages.per_session_minutes ? <span className="pr-avg-unit">m</span> : null}
                        </div>
                        <div className="pr-avg-lbl">vaqt / mashq</div>
                    </div>
                    <div className="pr-avg">
                        <div className="pr-avg-num">{averages.sessions_per_week}</div>
                        <div className="pr-avg-lbl">mashq / hafta</div>
                    </div>
                    <div className="pr-avg">
                        <div className="pr-avg-num">{averages.active_days_in_window}</div>
                        <div className="pr-avg-lbl">faol kun ({data.window.days}d)</div>
                    </div>
                </div>
            </section>

            {/* ── Sparkline of activity ───────────────────────────────── */}
            {trimmedDays.length > 1 && (
                <section className="pr-section">
                    <h3 className="pr-section-title">Faollik dinamikasi</h3>
                    <Sparkline points={trimmedDays} ariaLabel="Kunlik so'z hajmi" />
                    <div className="pr-spark-foot">
                        <span>{formatDateShort(trimmedDays[0].date)}</span>
                        <span>{formatDateShort(trimmedDays[trimmedDays.length - 1].date)}</span>
                    </div>
                </section>
            )}

            {/* ── Grain toggle + period bars ──────────────────────────── */}
            <section className="pr-section">
                <div className="pr-section-head">
                    <h3 className="pr-section-title">
                        {grain === 'day' ? "Kunlik natijalar" : "Oylik natijalar"}
                    </h3>
                    <div className="pr-grain">
                        <button
                            className={`pr-grain-btn ${grain === 'day' ? 'active' : ''}`}
                            onClick={() => setGrain('day')}
                        >
                            Kun
                        </button>
                        <button
                            className={`pr-grain-btn ${grain === 'month' ? 'active' : ''}`}
                            onClick={() => setGrain('month')}
                        >
                            Oy
                        </button>
                    </div>
                </div>
                {grain === 'day' ? (
                    <PeriodBars
                        points={[...trimmedDays].reverse()}
                        accessor={(d) => d.sessions}
                        labelFor={(d) => formatDateShort(d.date)}
                    />
                ) : (
                    <PeriodBars
                        points={[...by_month].reverse()}
                        accessor={(d) => d.sessions}
                        labelFor={(d) => formatMonth(d.month)}
                    />
                )}
            </section>

            {/* ── Lifetime totals ──────────────────────────────────────── */}
            <section className="pr-section">
                <h3 className="pr-section-title">Umumiy hisob</h3>
                <div className="pr-totals">
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.sessions}</div>
                        <div className="pr-total-lbl">mashqlar</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.words}</div>
                        <div className="pr-total-lbl">jami so'z</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.correct}</div>
                        <div className="pr-total-lbl">to'g'ri javob</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.accuracy}%</div>
                        <div className="pr-total-lbl">aniqlik</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.active_days}</div>
                        <div className="pr-total-lbl">faol kun</div>
                    </div>
                    {totals.minutes > 0 && (
                        <div className="pr-total">
                            <div className="pr-total-num">
                                {totals.minutes >= 60
                                    ? `${Math.floor(totals.minutes / 60)}s ${totals.minutes % 60}d`
                                    : `${totals.minutes}d`}
                            </div>
                            <div className="pr-total-lbl">jami vaqt</div>
                        </div>
                    )}
                </div>
            </section>

            {/* ── Recent sessions list ─────────────────────────────────── */}
            {recent.length > 0 && (
                <section className="pr-section">
                    <div className="pr-section-head">
                        <h3 className="pr-section-title">Mashqlar ro'yxati</h3>
                        {recent.length > 5 && (
                            <button
                                className="pr-section-more pr-section-more--btn"
                                onClick={() => setExpanded((v) => !v)}
                            >
                                {expanded ? 'Kamroq' : `Yana ${recent.length - 5} ta`}
                            </button>
                        )}
                    </div>
                    <div className="pr-sess-list">
                        {visibleRecent.map((s) => {
                            const meta = MODES.find((m) => m.key === s.mode);
                            const pct = s.accuracy;
                            const cls = pct >= 80 ? 'ok' : pct >= 50 ? 'mid' : 'bad';
                            return (
                                <div key={s.id} className="pr-sess-row">
                                    <div className="pr-sess-mode">
                                        <span className="pr-sess-mode-icon" aria-hidden>
                                            {meta?.icon || '🔸'}
                                        </span>
                                        <span className="pr-sess-mode-name">
                                            {meta?.label || s.mode}
                                        </span>
                                    </div>
                                    <div className="pr-sess-when">
                                        {formatDateTime(s.completed_at || s.started_at)}
                                    </div>
                                    <div className="pr-sess-dur">
                                        {formatDuration(s.duration_seconds)}
                                    </div>
                                    <div className="pr-sess-score">
                                        {s.correct}/{s.total_words}
                                    </div>
                                    <div className={`pr-sess-pct pr-sess-pct--${cls}`}>
                                        {pct}%
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </section>
            )}
        </div>
    );
}


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
        request(`${API_URL}v1/dictionary/`, 'GET', null, headers())
            .then((rows) => {
                if (!Array.isArray(rows)) { setScopeTree([]); return; }
                const cats = new Map(); // id → {id, name, courses: Map}
                for (const w of rows) {
                    // Words can lack a course/category (manual entries). Skip
                    // them — they're scoped via the "All" choice anyway.
                    if (!w.course_id) continue;
                    // We don't have category info on the word; group all
                    // courses without a known category under "Boshqa".
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
            // Record the answer in the current pass set.
            const newMcqOk   = qpPass === 'mcq'      && was_correct ? [...qpMcqOk, item.word.id]   : qpMcqOk;
            const newSpellOk = qpPass === 'spelling' && was_correct ? [...qpSpellOk, item.word.id] : qpSpellOk;
            if (qpPass === 'mcq')      setQpMcqOk(newMcqOk);
            if (qpPass === 'spelling') setQpSpellOk(newSpellOk);

            const nextPos = pos + 1;
            const endOfPass = nextPos >= queue.length;

            if (endOfPass && qpPass === 'mcq') {
                // Switch to spelling pass; reset to the start of the queue.
                setQpPass('spelling');
                setPos(0);
                return;
            }

            if (endOfPass && qpPass === 'spelling') {
                // Both passes done — finalise. A word counts correct only
                // if it appeared in BOTH the MCQ and Spelling correct sets.
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
            // Position went out of bounds — usually because a stale queue
            // pointer survived a config change. Don't leave the student
            // staring at a blank screen; fall back to a recoverable state
            // with a clear way back to the picker.
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

        // Quiz+ pos/total reads against the queue itself per pass; other
        // modes hide replay items from the visible counter so accuracy
        // matches what the recap will show.
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
            {/* Sub-tabs — Boshlash (default) vs Statistika dashboard.
                Only rendered on the pick phase; drill / recap don't need it. */}
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
