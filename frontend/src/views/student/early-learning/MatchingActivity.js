import React, { useEffect, useMemo, useState } from 'react';
import * as Icons from 'lucide-react';
import { ArrowLeft, HelpCircle } from 'lucide-react';
import './MatchingActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { shuffle, starsForWrongCount, WRONG_FLASH_MS } from './earlyLearningUtils';

/** Emoji is the primary visual — many kids this age (5-8) can't reliably
 * read yet, in either language, so a small monochrome lucide line-glyph
 * plus a text label they can't read isn't enough to identify an item at a
 * glance. Emoji are colorful and kids recognize them without reading.
 * `icon` (a lucide name) is only a fallback for the rare item without one. */
function ItemIcon({ emoji, icon, size = 32 }) {
    if (emoji) {
        return <span className="ma-item-emoji" style={{ fontSize: size }}>{emoji}</span>;
    }
    const Icon = Icons[icon] || HelpCircle;
    return <Icon size={size} />;
}

/** One "select the correct items for this character" round.
 * activity.content shape (mode: "select"):
 *   { character: {emoji,label}, correct_items: [{id,label,icon,emoji}], distractor_items: [...] }
 */
export default function MatchingActivity({ activity, onBack, onComplete, lang, toggleLang, t }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const correctItems = content.correct_items || [];
    const distractorItems = content.distractor_items || [];
    const totalCorrect = correctItems.length;

    const pool = useMemo(() => {
        const tagged = [
            ...correctItems.map((it) => ({ ...it, isCorrect: true })),
            ...distractorItems.map((it) => ({ ...it, isCorrect: false })),
        ];
        return shuffle(tagged);
        // Depend on activity.content, not lang directly — see
        // BuildActivity.js's identical fix for why: lang flips
        // synchronously while the re-fetch it triggers is async, so
        // depending on lang re-ran this memo too early (still against the
        // pre-fetch content) and then never again once the translated
        // content actually arrived. activity.content only changes
        // reference when a fresh fetch actually replaces it.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [activity.id, activity.content]);

    const [found, setFound] = useState(() => new Set());
    const [wrongCount, setWrongCount] = useState(0);
    const [flash, setFlash] = useState(null); // { id, message } | null
    const [celebration, setCelebration] = useState(null); // stars earned, once round is done
    const [submitting, setSubmitting] = useState(false);

    const handleTap = (item) => {
        if (found.has(item.id) || celebration !== null) return;

        if (item.isCorrect) {
            playSynth('chime');
            // Functional update — two correct taps landing in the same React
            // batch (an excited 5-8 year old double-tapping is routine) must
            // not both compute their `next` Set from the same stale `found`
            // and silently drop one of them.
            setFound((prev) => {
                const next = new Set(prev);
                next.add(item.id);
                return next;
            });
        } else {
            playSynth('laser');
            setWrongCount((c) => c + 1);
            // Uzbek's postposition ("X" Y uchun mos emas) and Russian's
            // preposition (Ой! «X» не подходит для Y) put the character
            // name on opposite sides of the verb — not a fill-in-the-blank
            // template t() can express with fixed slot order, so this one
            // sentence is branched directly rather than composed from keys.
            const charLabel = character.label || '';
            const message = lang === 'ru'
                ? `Ой! «${item.label}» не подходит для: ${charLabel}.`
                : `Oh-oh! "${item.label}" ${charLabel} uchun mos emas.`;
            setFlash({ id: item.id, message });
            setTimeout(() => setFlash((f) => (f?.id === item.id ? null : f)), WRONG_FLASH_MS);
        }
    };

    // Fires once `found` actually reaches the full correct set — reading it
    // from state (rather than inline in handleTap) keeps this correct even
    // when the last couple of taps land in the same batch as each other.
    useEffect(() => {
        if (celebration === null && totalCorrect > 0 && found.size === totalCorrect) {
            playSynth('fanfare');
            setCelebration(starsForWrongCount(wrongCount));
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [found]);

    const handleCelebrationDone = () => {
        const stars = celebration;
        setSubmitting(true);
        request(`${API_URL}v1/early-learning/activities/${activity.id}/complete`, 'POST', { stars }, headers())
            .then((result) => onComplete(result))
            .catch((err) => {
                console.error(err);
                // Still let the child close the round locally — losing the
                // star-save on a flaky request shouldn't trap the kid on
                // this screen; best_stars just won't have updated server-side.
                onComplete({ stars_earned: stars, attempts: 1 });
            })
            .finally(() => setSubmitting(false));
    };

    return (
        <div className="ma-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="ma-character">
                <span className="ma-character-emoji">{character.emoji || '🎲'}</span>
                <h2>{character.label || activity.title}</h2>
                <span className="ma-progress-badge">{found.size} / {totalCorrect}</span>
            </div>

            {flash && <div className="ma-error-banner">{flash.message}</div>}

            <div className="ma-progress-bar">
                <div className="ma-progress-fill" style={{ width: `${(found.size / totalCorrect) * 100}%` }} />
            </div>

            <div className="ma-item-grid">
                {pool.map((item) => {
                    const isFound = found.has(item.id);
                    const isFlashing = flash?.id === item.id;
                    return (
                        <button
                            key={item.id}
                            className={`ma-item-card ${isFound ? 'ma-item-found' : ''} ${isFlashing ? 'ma-item-wrong' : ''}`}
                            onClick={() => handleTap(item)}
                            disabled={isFound}
                        >
                            <span className="ma-item-icon">
                                {isFlashing
                                    ? <span className="ma-item-sad" aria-hidden="true">😕</span>
                                    : <ItemIcon emoji={item.emoji} icon={item.icon} size={40} />}
                            </span>
                            <span className="ma-item-label">{item.label}</span>
                            {isFound && <span className="ma-item-check" aria-hidden="true">✓</span>}
                        </button>
                    );
                })}
            </div>

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
