import React, { useMemo, useState } from 'react';
import './ArithmeticActivity.css';
import './WordChartActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { starsForWrongCount, WRONG_FLASH_MS, recordGuestCompletion } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

const CORRECT_PULSE_MS = 600;
const EMOJI = ['🍎', '🍌', '🍇', '🍓', '🐶', '🐱', '🐰', '⚽', '🚗', '⭐'];
const COLORS = ['#ff6b6b', '#ffd43b', '#51cf66', '#4dabf7', '#b197fc'];

const TEXT = {
    uz: {
        most: 'Qaysi biri eng ko\'p?',
        least: 'Qaysi biri eng kam?',
        howMany: (e) => `${e} nechta?`,
        diff: (a, b) => `${a} ${b} dan nechta ortiq?`,
        total: 'Hammasi nechta bo\'ladi?',
    },
    ru: {
        most: 'Каких больше всего?',
        least: 'Каких меньше всего?',
        howMany: (e) => `Сколько ${e}?`,
        diff: (a, b) => `На сколько ${a} больше, чем ${b}?`,
        total: 'Сколько всего?',
    },
};

function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
}

function numberOptions(answer, max) {
    const set = new Set([answer]);
    for (const d of shuffle([1, -1, 2, -2, 3])) {
        const v = answer + d;
        if (v >= 0 && v <= max && set.size < 4) set.add(v);
    }
    let n = 0;
    while (set.size < 4) set.add(n++);
    return shuffle([...set]);
}

/** One chart + one question. Values are distinct so "most/least" has a
 * single right answer. `hard` adds the difference/total questions. */
function makeRound(hard) {
    const count = hard ? 4 : 3;
    const emojis = shuffle(EMOJI).slice(0, count);
    const values = shuffle(Array.from({ length: hard ? 10 : 8 }, (_, i) => i + 1)).slice(0, count);
    const bars = emojis.map((emoji, i) => ({ emoji, value: values[i], color: COLORS[i] }));
    const kinds = hard ? ['most', 'least', 'howMany', 'diff', 'total'] : ['most', 'least', 'howMany'];
    const kind = kinds[Math.floor(Math.random() * kinds.length)];
    const sorted = [...bars].sort((a, b) => a.value - b.value);
    const max = hard ? 30 : 10;
    if (kind === 'most') return { bars, kind, answer: sorted[sorted.length - 1].emoji, options: bars.map((b) => b.emoji) };
    if (kind === 'least') return { bars, kind, answer: sorted[0].emoji, options: bars.map((b) => b.emoji) };
    if (kind === 'howMany') {
        const b = bars[Math.floor(Math.random() * bars.length)];
        return { bars, kind, target: b.emoji, answer: b.value, options: numberOptions(b.value, max) };
    }
    if (kind === 'diff') {
        const hi = sorted[sorted.length - 1];
        const lo = sorted[0];
        return { bars, kind, hi: hi.emoji, lo: lo.emoji, answer: hi.value - lo.value, options: numberOptions(hi.value - lo.value, max) };
    }
    const total = bars.reduce((s, b) => s + b.value, 0);
    return { bars, kind, answer: total, options: numberOptions(total, max) };
}

/** Read a bar chart and answer a question. activity.content shape (mode:
 * "chart"): { character: {emoji,label}, rounds_count: 6, hard: false } —
 * charts are generated on the fly. Same scoring/celebration flow as
 * CompareActivity (starsForWrongCount), styles from ArithmeticActivity.css. */
export default function ChartActivity({ activity, onBack, onComplete, lang, toggleLang, t, guest = false }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const roundsCount = content.rounds_count || 6;
    const L = TEXT[lang === 'ru' ? 'ru' : 'uz'];

    const rounds = useMemo(
        () => Array.from({ length: roundsCount }, () => makeRound(!!content.hard)),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [activity.id, activity.content]
    );

    const [roundIndex, setRoundIndex] = useState(0);
    const [wrongCount, setWrongCount] = useState(0);
    const [flash, setFlash] = useState(null);
    const [correct, setCorrect] = useState(null);
    const [locked, setLocked] = useState(false);
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const round = rounds[roundIndex];

    const tap = (opt) => {
        if (celebration !== null || submitting || locked || !round) return;
        if (opt === round.answer) {
            playSynth('chime');
            setLocked(true);
            setCorrect(opt);
            setTimeout(() => {
                setCorrect(null);
                setLocked(false);
                if (roundIndex + 1 < rounds.length) {
                    setRoundIndex((i) => i + 1);
                } else {
                    playSynth('fanfare');
                    setCelebration(starsForWrongCount(wrongCount));
                }
            }, CORRECT_PULSE_MS);
        } else {
            playSynth('laser');
            setWrongCount((c) => c + 1);
            const token = Date.now();
            setFlash({ token, opt });
            setTimeout(() => setFlash((f) => (f?.token === token ? null : f)), WRONG_FLASH_MS);
        }
    };

    const handleCelebrationDone = () => {
        const stars = celebration;
        if (guest) {
            onComplete(recordGuestCompletion(activity.id, stars));
            return;
        }
        setSubmitting(true);
        request(`${API_URL}v1/early-learning/activities/${activity.id}/complete`, 'POST', { stars }, headers())
            .then((result) => onComplete(result))
            .catch((err) => {
                console.error(err);
                onComplete({ stars_earned: stars, attempts: 1 });
            })
            .finally(() => setSubmitting(false));
    };

    if (!round) return null;

    const maxValue = Math.max(...round.bars.map((b) => b.value));
    const question =
        round.kind === 'howMany' ? L.howMany(round.target) :
        round.kind === 'diff' ? L.diff(round.hi, round.lo) :
        L[round.kind];

    return (
        <div className="aa-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="aa-character-header">
                <span className="aa-character-emoji">{character.emoji || '📊'}</span>
                <h2>{character.label || activity.title}</h2>
            </div>

            <div className="wc-chart">
                {round.bars.map((b) => (
                    <div className="wc-bar-col" key={b.emoji}>
                        <span className="wc-bar-value">{b.value}</span>
                        <div className="wc-bar" style={{ height: `${(b.value / maxValue) * 100}%`, background: b.color }} />
                        <span className="wc-bar-emoji">{b.emoji}</span>
                    </div>
                ))}
            </div>

            <p className="aa-instruction wc-question">{question}</p>

            <div className="aa-options">
                {round.options.map((opt, i) => (
                    <button
                        key={`${roundIndex}-${opt}`}
                        className={`aa-option-btn ${flash?.opt === opt ? 'aa-option-btn-wrong' : ''} ${correct === opt ? 'aa-option-btn-correct' : ''}`}
                        style={{ '--i': i, animationDelay: `${i * 0.07}s` }}
                        onClick={() => tap(opt)}
                        disabled={submitting || locked}
                    >
                        {opt}
                    </button>
                ))}
            </div>

            <div className="aa-progress">{roundIndex + 1} / {rounds.length}</div>

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
