import React, { useMemo, useState } from 'react';
import './WordChartActivity.css';
import './EarlyLearning.css';
import { useNavigate } from 'react-router-dom';
import ActivityShell, { useActivityCompletion } from './ActivityShell';
import { useTranslation } from '../../../i18n/useTranslation';
import { playSynth } from '../../../utils/soundSynth';
import { dailySeed, getDaily, recordDaily, starsForWrongCount, WRONG_FLASH_MS } from './earlyLearningUtils';

// mulberry32: tiny seeded PRNG so every kid gets the same 5 questions today.
function rng(seed) {
    let a = seed;
    return () => {
        a |= 0; a = (a + 0x6D2B79F5) | 0;
        let t = Math.imul(a ^ (a >>> 15), 1 | a);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}

function build(seed) {
    const r = rng(seed);
    const int = (lo, hi) => Math.floor(r() * (hi - lo + 1)) + lo;
    const shuf = (arr) => {
        const a = [...arr];
        for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
        return a;
    };
    const nums = (ans, hi) => {
        const set = new Set([ans]);
        for (const d of shuf([1, -1, 2, -2, 3, -3])) if (ans + d >= 0 && ans + d <= hi && set.size < 4) set.add(ans + d);
        let n = 0;
        while (set.size < 4) set.add(n++);
        return shuf([...set]).map(String);
    };
    const make = [
        () => { const a = int(3, 15); const b = int(2, 9); return { q: `${a} + ${b} = ?`, a: String(a + b), o: nums(a + b, 30) }; },
        () => { const a = int(10, 20); const b = int(1, 9); return { q: `${a} − ${b} = ?`, a: String(a - b), o: nums(a - b, 30) }; },
        () => { const a = int(0, 30); const b = int(0, 30); return { q: `${a} ? ${b}`, a: a < b ? '<' : a > b ? '>' : '=', o: ['<', '=', '>'] }; },
        () => { const s = int(1, 8); const st = int(2, 5); return { q: `${s}, ${s + st}, ${s + 2 * st}, ?`, a: String(s + 3 * st), o: nums(s + 3 * st, 40) }; },
        () => { const e = ['🍎', '⭐', '🐟', '🎈'][int(0, 3)]; const n = int(3, 9); return { q: e.repeat(n), a: String(n), o: nums(n, 12), emoji: true }; },
        () => { const a = int(2, 9); const b = int(2, 9); return { q: `${a} × ${b} = ?`, a: String(a * b), o: nums(a * b, 90) }; },
    ];
    return shuf(make).slice(0, 5).map((f) => f());
}

const FIRE = (n) => (n > 0 ? `🔥 ${n}` : '');

/** Today's 5 questions with a day streak. Served at /play/daily (guest) and
 * /student/daily; the streak lives in localStorage (see getDaily). */
export default function DailyChallenge() {
    const navigate = useNavigate();
    const { t, lang, toggleLang } = useTranslation();
    const activity = useMemo(() => ({
        id: 'daily',
        title: lang === 'ru' ? 'Задание дня' : 'Kunlik vazifa',
        instruction_text: lang === 'ru' ? '5 вопросов каждый день — держи серию!' : 'Har kuni 5 ta savol — seriyani saqla!',
        content: { character: { emoji: '📅', label: lang === 'ru' ? 'Задание дня' : 'Kunlik vazifa' } },
    }), [lang]);
    const back = () => navigate(-1);

    const [result, setResult] = useState(null);
    const completion = useActivityCompletion(activity, true, () => setResult(recordDaily()));
    const questions = useMemo(() => build(dailySeed()), []);
    const [idx, setIdx] = useState(0);
    const [wrong, setWrong] = useState(0);
    const [flash, setFlash] = useState(null);
    const [before] = useState(getDaily);

    const tap = (o) => {
        if (completion.celebration !== null || result) return;
        const q = questions[idx];
        if (o === q.a) {
            playSynth('chime');
            if (idx + 1 < questions.length) setIdx(idx + 1);
            else { playSynth('fanfare'); completion.finish(starsForWrongCount(wrong)); }
        } else {
            playSynth('laser');
            setWrong((w) => w + 1);
            const token = Date.now();
            setFlash({ token, o });
            setTimeout(() => setFlash((f) => (f?.token === token ? null : f)), WRONG_FLASH_MS);
        }
    };

    const q = questions[idx];
    return (
        <div className="el-shell">
            <ActivityShell activity={activity} onBack={back} lang={lang} toggleLang={toggleLang} t={t} emoji="📅" completion={completion}>
                {result ? (
                    <div className="wc-daily-done">
                        <div className="wc-picture">🎉</div>
                        <div className="wc-prompt-text">{FIRE(result.streak)} {lang === 'ru' ? 'дней подряд!' : 'kun ketma-ket!'}</div>
                        <button className="el-duel-btn" onClick={back}>{lang === 'ru' ? 'Готово' : 'Tayyor'}</button>
                    </div>
                ) : (
                    <>
                        <div className="wc-bubble-target">
                            {FIRE(before.streak)} {before.doneToday ? (lang === 'ru' ? '· сегодня уже сыграно' : '· bugun bajarilgan') : ''}
                        </div>
                        <div className={`wc-prompt-text ${q.emoji ? 'is-emoji' : ''}`}>{q.q}</div>
                        <div className="aa-options">
                            {q.o.map((o, i) => (
                                <button
                                    key={`${idx}-${o}`}
                                    className={`aa-option-btn ${flash?.o === o ? 'aa-option-btn-wrong' : ''}`}
                                    style={{ '--i': i, animationDelay: `${i * 0.07}s` }}
                                    onClick={() => tap(o)}
                                >
                                    {o}
                                </button>
                            ))}
                        </div>
                        <div className="aa-progress">{idx + 1} / {questions.length}</div>
                    </>
                )}
            </ActivityShell>
        </div>
    );
}
