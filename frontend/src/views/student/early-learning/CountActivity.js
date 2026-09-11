import React, { useMemo, useState } from 'react';
import './CountActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { shuffle, starsForWrongCount, WRONG_FLASH_MS, STREAK_THRESHOLD, recordGuestCompletion } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

// How long a correct tap stays highlighted before the round advances —
// same "let the kid actually see the feedback" reasoning as PairsActivity's
// RESOLVE_MS, just shorter since there's only one thing to look at here
// (one number lighting up), not two cards to compare.
const CORRECT_PULSE_MS = 550;

/** One "how many do you see?" round. activity.content shape (mode:
 * "count"): { character: {emoji,label}, rounds: [{emoji, count, options}] }.
 * Sixth sibling of MatchingActivity.js/BuildActivity.js/TraceActivity.js/
 * MazeActivity.js/PairsActivity.js — cycles through `rounds` the same way
 * TraceActivity.js cycles through `targets` (one round at a time, tally
 * wrongCount across all of them, score at the very end), but the input
 * here is "tap the number button matching how many emoji you count" rather
 * than a drawn stroke. A wrong tap is scored exactly like a wrong tap
 * everywhere else — reuses starsForWrongCount as-is, no new scoring rule
 * needed. Numbers need no translation, so unlike every sibling this mode
 * carries no per-item label at all (see _LOCALIZED_ITEM_KEYS's
 * "count": () in early_learning.py).
 */
export default function CountActivity({ activity, onBack, onComplete, lang, toggleLang, t, guest = false }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const rounds = content.rounds || [];

    const [roundIndex, setRoundIndex] = useState(0);
    const [wrongCount, setWrongCount] = useState(0);
    const [flash, setFlash] = useState(null); // { token } | null — a just-tapped wrong number
    const [correctNum, setCorrectNum] = useState(null); // briefly set on a correct tap, before advancing
    const [locked, setLocked] = useState(false); // true during the correct-tap pause — blocks further taps
    const [, setStreak] = useState(0); // consecutive correctly-solved rounds, resets on any wrong tap — only the setter is used, the count itself is read via streakFlash
    const [streakFlash, setStreakFlash] = useState(null); // { token, count } | null
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const round = rounds[roundIndex];

    // Depend on activity.content (not just activity.id) — see
    // MatchingActivity.js's pool useMemo for why (lang toggle mid-play
    // re-fetches translated content; only the content reference actually
    // changes when that happens). roundIndex is also a dep since each
    // round has its own options to shuffle.
    const options = useMemo(
        () => shuffle(round?.options || []),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [activity.id, activity.content, roundIndex]
    );

    const handleTap = (num) => {
        if (celebration !== null || submitting || locked || !round) return;

        if (num === round.count) {
            // See STREAK_THRESHOLD's doc comment — a brighter "coin" cue on
            // every Nth correctly-solved round instead of the usual chime,
            // purely presentational (wrongCount/scoring untouched).
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
        // Guest (/play, no login): record straight to localStorage — see
        // MatchingActivity.js's identical branch for why.
        if (guest) {
            onComplete(recordGuestCompletion(activity.id, stars));
            return;
        }
        setSubmitting(true);
        request(`${API_URL}v1/early-learning/activities/${activity.id}/complete`, 'POST', { stars }, headers())
            .then((result) => onComplete(result))
            .catch((err) => {
                console.error(err);
                // Still let the child close the round locally — losing the
                // star-save on a flaky request shouldn't trap the kid here.
                onComplete({ stars_earned: stars, attempts: 1 });
            })
            .finally(() => setSubmitting(false));
    };

    if (!round) return null;

    return (
        <div className="ca-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="ca-character-header">
                <span className="ca-character-emoji">{character.emoji || '🔢'}</span>
                <h2>{character.label || activity.title}</h2>
            </div>

            {activity.instruction_text && <p className="ca-instruction">{activity.instruction_text}</p>}

            {streakFlash && (
                <div className="ca-streak-badge" key={streakFlash.token}>
                    🔥 {streakFlash.count}!
                </div>
            )}

            <div className="ca-scene">
                {Array.from({ length: round.count }, (_, i) => (
                    <span
                        key={`${roundIndex}-${i}`}
                        className="ca-item item-fade-in"
                        style={{ '--delay': `${i * 60}ms` }}
                    >
                        {round.emoji}
                    </span>
                ))}
            </div>

            <div className="ca-options">
                {options.map((num, i) => {
                    const isFlashWrong = flash?.num === num;
                    const isCorrectPulse = correctNum === num;
                    return (
                        <button
                            key={num}
                            className={`ca-option-btn ${isFlashWrong ? 'ca-option-btn-wrong' : ''} ${isCorrectPulse ? 'ca-option-btn-correct' : ''}`}
                            style={{ '--i': i, animationDelay: `${i * 0.07}s` }}
                            onClick={() => handleTap(num)}
                            disabled={submitting || locked}
                        >
                            {num}
                        </button>
                    );
                })}
            </div>

            <div className="ca-progress">{roundIndex + 1} / {rounds.length}</div>

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
