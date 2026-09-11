import React, { useMemo, useState } from 'react';
import './ArithmeticActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { shuffle, starsForWrongCount, WRONG_FLASH_MS, STREAK_THRESHOLD, recordGuestCompletion } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

const CORRECT_PULSE_MS = 550;

/** Generates one single-digit (0-9 each operand) add/subtract round.
 * Subtraction is always built so the result stays >= 0 (bigger operand
 * first) — a kid at this level hasn't met negative numbers yet. */
function randInt(max) { return Math.floor(Math.random() * (max + 1)); }

function makeRound(operations) {
    const op = operations[randInt(operations.length - 1)];
    let a = randInt(9);
    let b = randInt(9);
    let answer;
    if (op === 'subtract') {
        if (a < b) [a, b] = [b, a]; // keep it non-negative
        answer = a - b;
    } else {
        answer = a + b;
    }
    const sign = op === 'subtract' ? '−' : '+';

    // 3 distinct wrong options near the answer, all non-negative.
    const wrongs = new Set();
    const spread = [1, -1, 2, -2, 3, -3];
    for (const d of spread) {
        if (wrongs.size >= 3) break;
        const candidate = answer + d;
        if (candidate >= 0 && candidate !== answer) wrongs.add(candidate);
    }
    while (wrongs.size < 3) {
        const candidate = randInt(18);
        if (candidate !== answer) wrongs.add(candidate);
    }

    return {
        text: `${a} ${sign} ${b}`,
        answer,
        options: shuffle([answer, ...Array.from(wrongs)]),
    };
}

/** One "solve the equation" round. activity.content shape (mode:
 * "arithmetic"): { character: {emoji,label}, operations: ["add","subtract"],
 * rounds_count: 8 } — everything optional, rounds are generated on the fly
 * (not authored) so every play-through is a fresh set of problems. Sibling
 * of CountActivity.js, same round-cycle/scoring/celebration shape, only the
 * "what am I solving" and "what do the options mean" parts differ. */
export default function ArithmeticActivity({ activity, onBack, onComplete, lang, toggleLang, t, guest = false }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const operations = content.operations?.length ? content.operations : ['add', 'subtract'];
    const roundsCount = content.rounds_count || 8;

    const rounds = useMemo(
        () => Array.from({ length: roundsCount }, () => makeRound(operations)),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [activity.id, activity.content]
    );

    const [roundIndex, setRoundIndex] = useState(0);
    const [wrongCount, setWrongCount] = useState(0);
    const [flash, setFlash] = useState(null);
    const [correctNum, setCorrectNum] = useState(null);
    const [locked, setLocked] = useState(false);
    const [, setStreak] = useState(0);
    const [streakFlash, setStreakFlash] = useState(null);
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const round = rounds[roundIndex];

    const handleTap = (num) => {
        if (celebration !== null || submitting || locked || !round) return;

        if (num === round.answer) {
            setStreak((s) => {
                const next = s + 1;
                if (next % STREAK_THRESHOLD === 0) {
                    playSynth('coin');
                    const token = Date.now();
                    setStreakFlash({ token, count: next });
                    setTimeout(() => setStreakFlash((f) => (f?.token === token ? null : f)), 900);
                } else {
                    playSynth('chime');
                }
                return next;
            });
            setLocked(true);
            setCorrectNum(num);
            setTimeout(() => {
                setCorrectNum(null);
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
            setStreak(0);
            setWrongCount((c) => c + 1);
            const token = Date.now();
            setFlash({ token, num });
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

    return (
        <div className="aa-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="aa-character-header">
                <span className="aa-character-emoji">{character.emoji || '🧮'}</span>
                <h2>{character.label || activity.title}</h2>
            </div>

            {activity.instruction_text && <p className="aa-instruction">{activity.instruction_text}</p>}

            {streakFlash && (
                <div className="aa-streak-badge" key={streakFlash.token}>
                    🔥 {streakFlash.count}!
                </div>
            )}

            <div className="aa-equation">
                <span>{round.text}</span>
                <span className="aa-equals">=</span>
                <span className="aa-question-mark">?</span>
            </div>

            <div className="aa-options">
                {round.options.map((num, i) => {
                    const isFlashWrong = flash?.num === num;
                    const isCorrectPulse = correctNum === num;
                    return (
                        <button
                            key={num}
                            className={`aa-option-btn ${isFlashWrong ? 'aa-option-btn-wrong' : ''} ${isCorrectPulse ? 'aa-option-btn-correct' : ''}`}
                            style={{ '--i': i, animationDelay: `${i * 0.07}s` }}
                            onClick={() => handleTap(num)}
                            disabled={submitting || locked}
                        >
                            {num}
                        </button>
                    );
                })}
            </div>

            <div className="aa-progress">{roundIndex + 1} / {rounds.length}</div>

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
