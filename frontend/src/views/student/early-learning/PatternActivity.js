import React, { useMemo, useState } from 'react';
import './PatternActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { shuffle, starsForWrongCount, WRONG_FLASH_MS, recordGuestCompletion } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

// Same "let the kid see the correct-tap feedback before moving on" pause as
// CountActivity's CORRECT_PULSE_MS — this screen is its closest sibling.
const CORRECT_PULSE_MS = 550;

/** One "what comes next?" round. activity.content shape (mode: "pattern"):
 * { character: {emoji,label}, rounds: [{sequence: [emoji,...], answer:
 * emoji, options: [emoji,...]}] }. `sequence` is shown as-is (already in
 * its repeating order) followed by a "?" slot; the kid taps the option
 * emoji that belongs there. Ninth sibling of MatchingActivity.js/
 * BuildActivity.js/TraceActivity.js/MazeActivity.js/PairsActivity.js/
 * CountActivity.js/SortActivity.js/SequenceActivity.js — structurally
 * almost identical to CountActivity.js (cycle `rounds`, tally wrongCount,
 * score at the end via starsForWrongCount unchanged), just swapping "tap
 * the number matching the count" for "tap the emoji matching the pattern".
 * No per-item label anywhere in this content shape (sequence/answer/options
 * are all just emoji, same as count's bare numbers) — see
 * _LOCALIZED_ITEM_KEYS's "pattern": () in early_learning.py.
 */
export default function PatternActivity({ activity, onBack, onComplete, lang, toggleLang, t, guest = false }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const rounds = content.rounds || [];

    const [roundIndex, setRoundIndex] = useState(0);
    const [wrongCount, setWrongCount] = useState(0);
    const [flash, setFlash] = useState(null); // { token, emoji } | null — a just-tapped wrong option
    const [correctEmoji, setCorrectEmoji] = useState(null); // briefly set on a correct tap, before advancing
    const [locked, setLocked] = useState(false); // true during the correct-tap pause — blocks further taps
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

    const handleTap = (emoji) => {
        if (celebration !== null || submitting || locked || !round) return;

        if (emoji === round.answer) {
            playSynth('chime');
            setLocked(true);
            setCorrectEmoji(emoji);
            setTimeout(() => {
                setCorrectEmoji(null);
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
            setFlash({ token, emoji });
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
        <div className="pt-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="pt-character-header">
                <span className="pt-character-emoji">{character.emoji || '🧩'}</span>
                <h2>{character.label || activity.title}</h2>
            </div>

            {activity.instruction_text && <p className="pt-instruction">{activity.instruction_text}</p>}

            <div className="pt-scene">
                {round.sequence.map((emoji, i) => (
                    <span key={`${roundIndex}-${i}`} className="pt-cell item-fade-in" style={{ '--delay': `${i * 60}ms` }}>
                        {emoji}
                    </span>
                ))}
                <span className="pt-cell pt-cell-blank">{correctEmoji || '?'}</span>
            </div>

            <div className="pt-options">
                {options.map((emoji, i) => {
                    const isFlashWrong = flash?.emoji === emoji;
                    const isCorrectPulse = correctEmoji === emoji;
                    return (
                        <button
                            key={`${emoji}-${i}`}
                            className={`pt-option-btn ${isFlashWrong ? 'pt-option-btn-wrong' : ''} ${isCorrectPulse ? 'pt-option-btn-correct' : ''}`}
                            style={{ '--i': i, animationDelay: `${i * 0.07}s` }}
                            onClick={() => handleTap(emoji)}
                            disabled={submitting || locked}
                        >
                            {emoji}
                        </button>
                    );
                })}
            </div>

            <div className="pt-progress">{roundIndex + 1} / {rounds.length}</div>

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
