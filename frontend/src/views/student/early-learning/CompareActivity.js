import React, { useMemo, useState } from 'react';
import './ArithmeticActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { starsForWrongCount, WRONG_FLASH_MS, STREAK_THRESHOLD, recordGuestCompletion } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

const CORRECT_PULSE_MS = 550;
const SIGNS = ['<', '=', '>'];

function randInt(max) { return Math.floor(Math.random() * (max + 1)); }

/** One "which sign goes between them" round — roughly one in six is an
 * equal pair so "=" is a real answer, not a distractor nobody needs. */
function makeRound(max) {
    const a = randInt(max);
    const b = Math.random() < 0.17 ? a : randInt(max);
    const answer = a < b ? '<' : a > b ? '>' : '=';
    return { a, b, answer };
}

/** Compare two numbers with <, = or >. activity.content shape (mode:
 * "compare"): { character: {emoji,label}, max: 9, rounds_count: 8 } —
 * everything optional, rounds are generated on the fly each play (same
 * approach as ArithmeticActivity.js, whose styles this reuses). */
export default function CompareActivity({ activity, onBack, onComplete, lang, toggleLang, t, guest = false }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const max = content.max || 9;
    const roundsCount = content.rounds_count || 8;

    const rounds = useMemo(
        () => Array.from({ length: roundsCount }, () => makeRound(max)),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [activity.id, activity.content]
    );

    const [roundIndex, setRoundIndex] = useState(0);
    const [wrongCount, setWrongCount] = useState(0);
    const [flash, setFlash] = useState(null);
    const [correctSign, setCorrectSign] = useState(null);
    const [locked, setLocked] = useState(false);
    const [, setStreak] = useState(0);
    const [streakFlash, setStreakFlash] = useState(null);
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const round = rounds[roundIndex];

    const handleTap = (sign) => {
        if (celebration !== null || submitting || locked || !round) return;

        if (sign === round.answer) {
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
            setCorrectSign(sign);
            setTimeout(() => {
                setCorrectSign(null);
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
            setFlash({ token, sign });
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
                <span className="aa-character-emoji">{character.emoji || '⚖️'}</span>
                <h2>{character.label || activity.title}</h2>
            </div>

            {activity.instruction_text && <p className="aa-instruction">{activity.instruction_text}</p>}

            {streakFlash && (
                <div className="aa-streak-badge" key={streakFlash.token}>🔥 {streakFlash.count}!</div>
            )}

            <div className="aa-equation">
                <span>{round.a}</span>
                <span className="aa-question-mark">?</span>
                <span>{round.b}</span>
            </div>

            <div className="aa-options">
                {SIGNS.map((sign, i) => (
                    <button
                        key={sign}
                        className={`aa-option-btn ${flash?.sign === sign ? 'aa-option-btn-wrong' : ''} ${correctSign === sign ? 'aa-option-btn-correct' : ''}`}
                        style={{ '--i': i, animationDelay: `${i * 0.07}s` }}
                        onClick={() => handleTap(sign)}
                        disabled={submitting || locked}
                    >
                        {sign}
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
