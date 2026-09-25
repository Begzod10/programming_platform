import React, { useEffect, useMemo, useState } from 'react';
import './WordChartActivity.css';
import ActivityShell, { useActivityCompletion } from './ActivityShell';
import { playSynth } from '../../../utils/soundSynth';
import { shuffle, starsForWrongCount, WRONG_FLASH_MS } from './earlyLearningUtils';

const PULSE_MS = 600;
const rnd = (lo, hi) => Math.floor(Math.random() * (hi - lo + 1)) + lo;

/** 4 shuffled options: the answer + 3 distinct others from `pool`. */
function pickOptions(answer, pool) {
    const others = shuffle(pool.filter((p) => p.key !== answer.key)).slice(0, 3);
    return shuffle([answer, ...others]);
}

function numOptions(answer, max) {
    const set = new Set([answer]);
    for (const d of shuffle([1, -1, 2, -2, 3, -3, 10, -10])) {
        const v = answer + d;
        if (v >= 0 && v <= max && set.size < 4) set.add(v);
    }
    let n = 0;
    while (set.size < 4) set.add(n++);
    return shuffle([...set]).map((v) => ({ key: String(v), label: String(v) }));
}

/* ── clock ── */
function Clock({ h, m }) {
    const hourDeg = (h % 12) * 30 + m * 0.5;
    const minDeg = m * 6;
    return (
        <svg className="wc-clock" viewBox="0 0 100 100" aria-hidden="true">
            <circle cx="50" cy="50" r="46" fill="#fff" stroke="#6C5CE7" strokeWidth="4" />
            {Array.from({ length: 12 }, (_, i) => (
                <line key={i} x1="50" y1="8" x2="50" y2={i % 3 === 0 ? 16 : 13} stroke="#2d2d3f" strokeWidth={i % 3 === 0 ? 3 : 1.5}
                    transform={`rotate(${i * 30} 50 50)`} />
            ))}
            <line x1="50" y1="50" x2="50" y2="26" stroke="#2d2d3f" strokeWidth="5" strokeLinecap="round" transform={`rotate(${hourDeg} 50 50)`} />
            <line x1="50" y1="50" x2="50" y2="14" stroke="#e53935" strokeWidth="3" strokeLinecap="round" transform={`rotate(${minDeg} 50 50)`} />
            <circle cx="50" cy="50" r="3.5" fill="#2d2d3f" />
        </svg>
    );
}

const fmt = (h, m) => `${h}:${String(m).padStart(2, '0')}`;

function makeClock(level) {
    const h = rnd(1, 12);
    const m = level === 'easy' ? 0 : level === 'medium' ? rnd(0, 1) * 30 : rnd(0, 11) * 5;
    const answer = { key: fmt(h, m), label: fmt(h, m) };
    const pool = [];
    for (let i = 0; i < 12; i++) {
        const hh = rnd(1, 12);
        const mm = level === 'easy' ? 0 : level === 'medium' ? rnd(0, 1) * 30 : rnd(0, 11) * 5;
        pool.push({ key: fmt(hh, mm), label: fmt(hh, mm) });
    }
    // near-misses make the hard level honest: same hour other minutes, and vice versa
    pool.push({ key: fmt(h, (m + 30) % 60), label: fmt(h, (m + 30) % 60) });
    pool.push({ key: fmt(h % 12 + 1, m), label: fmt(h % 12 + 1, m) });
    return { visual: <Clock h={h} m={m} />, answer: answer.key, options: pickOptions(answer, pool) };
}

/* ── times table ── */
function makeMult(max) {
    const a = rnd(2, max);
    const b = rnd(2, 9);
    const ans = a * b;
    return {
        visual: <div className="aa-equation"><span>{a}</span><span className="aa-question-mark">×</span><span>{b}</span><span className="aa-question-mark">=</span><span>?</span></div>,
        answer: String(ans),
        options: numOptions(ans, max * 9 + 10),
    };
}

/* ── shapes & colours ── */
const SHAPES = [
    { emoji: '🔴', uz: 'qizil doira', ru: 'красный круг' }, { emoji: '🔵', uz: "ko'k doira", ru: 'синий круг' },
    { emoji: '🟢', uz: 'yashil doira', ru: 'зелёный круг' }, { emoji: '🟡', uz: 'sariq doira', ru: 'жёлтый круг' },
    { emoji: '🟥', uz: 'qizil kvadrat', ru: 'красный квадрат' }, { emoji: '🟦', uz: "ko'k kvadrat", ru: 'синий квадрат' },
    { emoji: '🟩', uz: 'yashil kvadrat', ru: 'зелёный квадрат' }, { emoji: '🟨', uz: 'sariq kvadrat', ru: 'жёлтый квадрат' },
    { emoji: '🔺', uz: 'qizil uchburchak', ru: 'красный треугольник' }, { emoji: '🔷', uz: "ko'k romb", ru: 'синий ромб' },
    { emoji: '⭐', uz: 'sariq yulduz', ru: 'жёлтая звезда' }, { emoji: '❤️', uz: 'qizil yurak', ru: 'красное сердце' },
    { emoji: '🟣', uz: 'binafsha doira', ru: 'фиолетовый круг' }, { emoji: '🟠', uz: 'zarg\'aldoq doira', ru: 'оранжевый круг' },
];

function makeShape(lang) {
    const answerShape = SHAPES[rnd(0, SHAPES.length - 1)];
    const answer = { key: answerShape.emoji, label: answerShape.emoji };
    const options = pickOptions(answer, SHAPES.map((s) => ({ key: s.emoji, label: s.emoji })));
    const name = lang === 'ru' ? answerShape.ru : answerShape.uz;
    return {
        visual: <div className="wc-prompt-text">{lang === 'ru' ? `Где ${name}?` : `Qaysi biri ${name}?`}</div>,
        answer: answer.key, options, bigOptions: true,
    };
}

/* ── listen & pick (speech synthesis) ── */
const LETTERS = "ABDEFGHIJKLMNOPQRSTUVXYZ".split('');
// Spoken forms. A bare "B" or "7" would be read in whatever language the
// browser's default voice is (English on most PCs) — so say the Uzbek/Russian
// NAME of the letter/number instead, phonetically spelled.
const UZ_LETTER = {
    A: 'a', B: 'be', D: 'de', E: 'e', F: 'ef', G: 'ge', H: 'ha', I: 'i', J: 'je', K: 'ka', L: 'el', M: 'em',
    N: 'en', O: 'o', P: 'pe', Q: 'qe', R: 'er', S: 'es', T: 'te', U: 'u', V: 've', X: 'xe', Y: 'ye', Z: 'ze',
};
const UZ_NUM = ['nol', 'bir', 'ikki', 'uch', "to'rt", 'besh', 'olti', 'yetti', 'sakkiz', "to'qqiz"];
const RU_NUM = ['ноль', 'один', 'два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять'];

let voicesCache = [];
function loadVoices() {
    try { voicesCache = window.speechSynthesis.getVoices() || []; } catch { voicesCache = []; }
    return voicesCache;
}
if (typeof window !== 'undefined' && window.speechSynthesis) {
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
}

/** Best available voice: real Uzbek if the device has one (Android/Google
 * does), else Turkish (Latin script, near-identical letter/number sounds),
 * else Russian. Returns null when the device has no matching voice at all. */
function pickVoice(lang) {
    const voices = voicesCache.length ? voicesCache : loadVoices();
    const find = (prefix) => voices.find((v) => v.lang && v.lang.toLowerCase().startsWith(prefix));
    if (lang === 'ru') return find('ru') || null;
    return find('uz') || find('tr') || find('ru') || null;
}

function speak(text, lang) {
    try {
        if (!window.speechSynthesis) return false;
        const isNum = /^\d$/.test(text);
        const spoken = lang === 'ru' && isNum ? RU_NUM[+text] : isNum ? UZ_NUM[+text] : (UZ_LETTER[text] || text);
        const voice = pickVoice(lang);
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(spoken);
        if (voice) { u.voice = voice; u.lang = voice.lang; } else { u.lang = lang === 'ru' ? 'ru-RU' : 'uz-UZ'; }
        u.rate = 0.8;
        window.speechSynthesis.speak(u);
        return true;
    } catch {
        return false;
    }
}

function makeListen(set) {
    const pool = set === 'numbers' ? Array.from({ length: 10 }, (_, i) => String(i)) : LETTERS;
    const ans = pool[rnd(0, pool.length - 1)];
    const answer = { key: ans, label: ans };
    return { speakText: ans, answer: ans, options: pickOptions(answer, pool.map((p) => ({ key: p, label: p }))), bigOptions: true };
}

/* ── money ── */
const COINS = [100, 200, 500, 1000];
function makeMoney(max) {
    const chips = Array.from({ length: rnd(2, 4) }, () => COINS[rnd(0, COINS.length - 1)]);
    let total = chips.reduce((s, c) => s + c, 0);
    if (total > max) { chips.length = 2; total = chips[0] + chips[1]; }
    const answer = { key: String(total), label: `${total}` };
    const pool = [];
    for (const d of [-100, 100, -200, 200, 500, -500, 1000]) if (total + d > 0) pool.push({ key: String(total + d), label: `${total + d}` });
    return {
        visual: (
            <div className="wc-coins">
                {chips.map((c, i) => <span key={i} className={`wc-coin wc-coin--${c}`}>{c}</span>)}
            </div>
        ),
        answer: answer.key, options: pickOptions(answer, pool),
    };
}

const TITLES = {
    clock: { uz: 'Soat nechchi?', ru: 'Сколько времени?', emoji: '🕒' },
    mult: { uz: "Ko'paytir!", ru: 'Умножь!', emoji: '✖️' },
    shape: { uz: 'Shaklni top', ru: 'Найди фигуру', emoji: '🔷' },
    listen: { uz: 'Eshit va top', ru: 'Послушай и найди', emoji: '🔊' },
    money: { uz: "Necha so'm?", ru: 'Сколько сумов?', emoji: '💰' },
};

/** Generic "one question per round, tap the right option" screen. activity.content
 * (mode: "rounds"): { kind: "clock"|"mult"|"shape"|"listen"|"money", level?: "easy|medium|hard",
 * max?: number, set?: "letters|numbers", rounds_count?: number }. Generated on the fly. */
export default function RoundsActivity(props) {
    const { activity, lang, guest, onComplete } = props;
    const content = activity.content || {};
    const kind = content.kind || 'mult';
    const roundsCount = content.rounds_count || 8;
    const completion = useActivityCompletion(activity, guest, onComplete);

    const rounds = useMemo(() => Array.from({ length: roundsCount }, () => {
        if (kind === 'clock') return makeClock(content.level || 'easy');
        if (kind === 'shape') return makeShape(lang);
        if (kind === 'listen') return makeListen(content.set);
        if (kind === 'money') return makeMoney(content.max || 2000);
        return makeMult(content.max || 5);
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [activity.id, activity.content, lang]);

    const [idx, setIdx] = useState(0);
    const [wrongCount, setWrongCount] = useState(0);
    const [flash, setFlash] = useState(null);
    const [correct, setCorrect] = useState(null);
    const [locked, setLocked] = useState(false);
    const [noVoice, setNoVoice] = useState(false);
    const round = rounds[idx];

    useEffect(() => {
        if (round?.speakText && !speak(round.speakText, lang)) setNoVoice(true);
    }, [round, lang]);

    const tap = (key) => {
        if (completion.celebration !== null || completion.submitting || locked) return;
        if (key === round.answer) {
            playSynth('chime');
            setLocked(true);
            setCorrect(key);
            setTimeout(() => {
                setCorrect(null);
                setLocked(false);
                if (idx + 1 < rounds.length) setIdx((i) => i + 1);
                else { playSynth('fanfare'); completion.finish(starsForWrongCount(wrongCount)); }
            }, PULSE_MS);
        } else {
            playSynth('laser');
            setWrongCount((c) => c + 1);
            const token = Date.now();
            setFlash({ token, key });
            setTimeout(() => setFlash((f) => (f?.token === token ? null : f)), WRONG_FLASH_MS);
        }
    };

    if (!round) return null;
    const title = TITLES[kind] || TITLES.mult;

    return (
        <ActivityShell {...props} emoji={title.emoji} completion={completion}>
            {round.visual}
            {round.speakText && (
                <div className="wc-listen">
                    <button className="wc-listen-btn" onClick={() => speak(round.speakText, lang)}>🔊</button>
                    {noVoice && <div className="wc-prompt-text">{round.speakText}</div>}
                </div>
            )}
            <div className={`aa-options ${round.bigOptions ? 'wc-big-options' : ''}`}>
                {round.options.map((o, i) => (
                    <button
                        key={`${idx}-${o.key}`}
                        className={`aa-option-btn ${flash?.key === o.key ? 'aa-option-btn-wrong' : ''} ${correct === o.key ? 'aa-option-btn-correct' : ''}`}
                        style={{ '--i': i, animationDelay: `${i * 0.07}s` }}
                        onClick={() => tap(o.key)}
                        disabled={completion.submitting || locked}
                    >
                        {o.label}
                    </button>
                ))}
            </div>
            <div className="aa-progress">{idx + 1} / {rounds.length}</div>
        </ActivityShell>
    );
}
