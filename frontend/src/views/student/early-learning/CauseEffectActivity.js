import React, { useMemo, useState } from 'react';
import './CauseEffectActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { shuffle, starsForWrongCount, WRONG_FLASH_MS, recordGuestCompletion } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

// Same "let the kid see the correct-tap feedback before moving on" pause as
// CountActivity's/PatternActivity's CORRECT_PULSE_MS — this screen is their
// closest sibling, just with real text options instead of bare numbers/emoji.
const CORRECT_PULSE_MS = 550;

/** One "what happens next?" round. activity.content shape (mode:
 * "cause_effect"): { character: {emoji,label}, rounds: [{cause:
 * {emoji,label}, answer: id, options: [{id,emoji,label}]}] }. Tenth
 * sibling of MatchingActivity.js/BuildActivity.js/TraceActivity.js/
 * MazeActivity.js/PairsActivity.js/CountActivity.js/SortActivity.js/
 * SequenceActivity.js/PatternActivity.js — structurally the same "cycle
 * rounds, tally wrongCount, score via starsForWrongCount at the end" shape
 * as CountActivity.js/PatternActivity.js, but each option here carries a
 * real everyday-reasoning sentence (not a bare number/emoji), so options
 * render as label+emoji cards rather than plain buttons — closer to
 * SortActivity.js's item cards in look, matched-by-tap in behavior.
 */
export default function CauseEffectActivity({ activity, onBack, onComplete, lang, toggleLang, t, guest = false }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const rounds = content.rounds || [];

    const [roundIndex, setRoundIndex] = useState(0);
    const [wrongCount, setWrongCount] = useState(0);
    const [flash, setFlash] = useState(null); // { token, id } | null — a just-tapped wrong option
    const [correctId, setCorrectId] = useState(null); // briefly set on a correct tap, before advancing
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

    const handleTap = (option) => {
        if (celebration !== null || submitting || locked || !round) return;

        if (option.id === round.answer) {
            playSynth('chime');
            setLocked(true);
            setCorrectId(option.id);
            setTimeout(() => {
                setCorrectId(null);
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
            setFlash({ token, id: option.id });
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
    const cause = round.cause || {};

    return (
        <div className="ce-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="ce-character-header">
                <span className="ce-character-emoji">{character.emoji || '🔗'}</span>
                <h2>{character.label || activity.title}</h2>
            </div>

            {activity.instruction_text && <p className="ce-instruction">{activity.instruction_text}</p>}

            <div className="ce-cause">
                <span className="ce-cause-emoji">{cause.emoji}</span>
                <span className="ce-cause-label">{cause.label}</span>
            </div>

            <div className="ce-options">
                {options.map((option) => {
                    const isFlashWrong = flash?.id === option.id;
                    const isCorrectPulse = correctId === option.id;
                    return (
                        <button
                            key={option.id}
                            className={`ce-option-card ${isFlashWrong ? 'ce-option-card-wrong' : ''} ${isCorrectPulse ? 'ce-option-card-correct' : ''}`}
                            onClick={() => handleTap(option)}
                            disabled={submitting || locked}
                        >
                            <span className="ce-option-emoji">{option.emoji}</span>
                            <span className="ce-option-label">{option.label}</span>
                        </button>
                    );
                })}
            </div>

            <div className="ce-progress">{roundIndex + 1} / {rounds.length}</div>

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
