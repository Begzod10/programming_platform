import React, { useState } from 'react';
import './ArithmeticActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { recordGuestCompletion } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

/** Completion flow shared by the newer play screens: call finish(stars) when
 * the round is won -> celebration -> POST (or guest localStorage) -> onComplete.
 * Same behaviour every older activity screen has inline. */
export function useActivityCompletion(activity, guest, onComplete) {
    const { request } = useHttp();
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const done = () => {
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

    return { celebration, finish: setCelebration, submitting, done };
}

/** Page chrome (back button, language toggle, character header, instruction,
 * celebration overlay) around a game body. */
export default function ActivityShell({
    activity, onBack, lang, toggleLang, t, emoji, completion, children, hideInstruction = false,
}) {
    const character = (activity.content || {}).character || {};
    return (
        <div className="aa-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={completion.submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="aa-character-header">
                <span className="aa-character-emoji">{character.emoji || emoji}</span>
                <h2>{character.label || activity.title}</h2>
            </div>

            {!hideInstruction && activity.instruction_text && <p className="aa-instruction">{activity.instruction_text}</p>}

            {children}

            {completion.celebration !== null && (
                <EarlyActivityCelebration stars={completion.celebration} onDone={completion.done} t={t} />
            )}
        </div>
    );
}
