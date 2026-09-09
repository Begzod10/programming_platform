import React, { useEffect, useMemo, useState } from 'react';
import './SequenceActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { shuffle, starsForWrongCount, WRONG_FLASH_MS, recordGuestCompletion } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

/** One "what comes next?" round. activity.content shape (mode:
 * "sequence"): { character: {emoji,label}, steps: [{id,emoji,label}] } —
 * `steps` is authored in the CORRECT order (the answer key); the tray
 * below shuffles it for display. Eighth sibling of MatchingActivity.js/
 * BuildActivity.js/TraceActivity.js/MazeActivity.js/PairsActivity.js/
 * CountActivity.js/SortActivity.js — input is tap-in-order rather than a
 * true drag-to-reorder, same "tap is more reliable on touch than drag"
 * reasoning as SortActivity.js. A correct tap locks into the next open
 * slot; a wrong one just shakes and waits for another try — nothing ever
 * moves on a wrong tap, so there's no drag-cancel/reorder-mid-gesture
 * edge case to get wrong. Scored exactly like a wrong tap everywhere
 * else — reuses starsForWrongCount as-is.
 */
export default function SequenceActivity({ activity, onBack, onComplete, lang, toggleLang, t, guest = false }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const steps = content.steps || []; // canonical (correct) order

    // Depend on activity.content, not just activity.id — see
    // MatchingActivity.js's pool useMemo for why (lang toggle mid-play
    // re-fetches translated content; only the content reference actually
    // changes when that happens).
    const shuffledSteps = useMemo(() => shuffle(steps),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [activity.id, activity.content]);

    // Ordered list of step ids placed so far — only ever grows by a
    // correct tap, so placedIds[i] === steps[i].id always holds; slots
    // render straight from `steps`, not by re-looking-up placedIds.
    const [placedIds, setPlacedIds] = useState([]);
    const [wrongId, setWrongId] = useState(null); // { token, id } | null
    const [wrongCount, setWrongCount] = useState(0);
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const tray = shuffledSteps.filter((s) => !placedIds.includes(s.id));

    // Fires once every step has been placed — reading it from state
    // (rather than inline in handleTap) keeps this correct regardless of
    // how the last placement landed.
    useEffect(() => {
        if (celebration === null && steps.length > 0 && placedIds.length === steps.length) {
            playSynth('fanfare');
            setCelebration(starsForWrongCount(wrongCount));
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [placedIds]);

    const handleTap = (step) => {
        if (celebration !== null || submitting) return;
        const expectedId = steps[placedIds.length]?.id;

        if (step.id === expectedId) {
            playSynth('chime');
            setPlacedIds((prev) => [...prev, step.id]);
        } else {
            playSynth('laser');
            setWrongCount((c) => c + 1);
            const token = Date.now();
            setWrongId({ token, id: step.id });
            setTimeout(() => setWrongId((f) => (f?.token === token ? null : f)), WRONG_FLASH_MS);
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

    return (
        <div className="sq-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="sq-character-header">
                <span className="sq-character-emoji">{character.emoji || '📋'}</span>
                <h2>{character.label || activity.title}</h2>
            </div>

            {activity.instruction_text && <p className="sq-instruction">{activity.instruction_text}</p>}

            <div className="sq-slots">
                {steps.map((step, i) => {
                    const filled = i < placedIds.length;
                    return (
                        <div key={step.id} className={`sq-slot ${filled ? 'sq-slot-filled' : ''}`}>
                            <span className="sq-slot-num">{i + 1}</span>
                            {filled && <span className="sq-slot-emoji">{step.emoji}</span>}
                        </div>
                    );
                })}
            </div>

            <div className="sq-tray">
                {tray.map((step) => (
                    <button
                        key={step.id}
                        className={`sq-item ${wrongId?.id === step.id ? 'sq-item-wrong' : ''}`}
                        onClick={() => handleTap(step)}
                        disabled={submitting}
                    >
                        <span className="sq-item-emoji">{step.emoji}</span>
                        <span className="sq-item-label">{step.label}</span>
                    </button>
                ))}
            </div>

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
