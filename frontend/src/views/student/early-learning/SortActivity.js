import React, { useEffect, useMemo, useState } from 'react';
import './SortActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { shuffle, starsForWrongCount, WRONG_FLASH_MS, STREAK_THRESHOLD, recordGuestCompletion } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

/** One "which box does this belong in?" round. activity.content shape
 * (mode: "sort"): { character: {emoji,label}, bins: [{id,label,emoji}],
 * items: [{id,label,emoji,bin}] }. Seventh sibling of MatchingActivity.js/
 * BuildActivity.js/TraceActivity.js/MazeActivity.js/PairsActivity.js/
 * CountActivity.js — but input is tap-item-then-tap-bin rather than a true
 * pointer-drag. BuildActivity.js is the only sibling that actually drags
 * (a 1:1 piece-to-slot fit needs a visible drop position); a two-step tap
 * is more reliable across touch devices for "which of N buckets" and
 * matches the platform's dominant interaction pattern anyway — every
 * other sibling but Build is tap-based. A wrong placement is scored
 * exactly like a wrong tap everywhere else — reuses starsForWrongCount
 * as-is, no new scoring rule needed.
 */
export default function SortActivity({ activity, onBack, onComplete, lang, toggleLang, t, guest = false }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const bins = content.bins || [];

    // Depend on activity.content, not just activity.id — see
    // MatchingActivity.js's pool useMemo for why (lang toggle mid-play
    // re-fetches translated content; only the content reference actually
    // changes when that happens).
    const items = useMemo(() => shuffle(content.items || []),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [activity.id, activity.content]);

    const [selectedId, setSelectedId] = useState(null);
    const [placedByBin, setPlacedByBin] = useState({}); // { binId: [item, ...] }
    const [sortedIds, setSortedIds] = useState(() => new Set());
    const [wrongCount, setWrongCount] = useState(0);
    const [shakeBinId, setShakeBinId] = useState(null); // { token, binId } | null
    const [, setStreak] = useState(0); // consecutive correct placements, resets on any wrong bin — see STREAK_THRESHOLD's doc comment in earlyLearningUtils.js
    const [streakFlash, setStreakFlash] = useState(null); // { token, count } | null
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const tray = items.filter((i) => !sortedIds.has(i.id));

    // Fires once every item has landed in a bin — reading it from state
    // (rather than inline in handleTapBin) keeps this correct regardless
    // of how the last placement landed.
    useEffect(() => {
        if (celebration === null && items.length > 0 && sortedIds.size === items.length) {
            playSynth('fanfare');
            setCelebration(starsForWrongCount(wrongCount));
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [sortedIds]);

    const handleSelectItem = (item) => {
        if (celebration !== null || submitting) return;
        setSelectedId((prev) => (prev === item.id ? null : item.id));
    };

    const handleTapBin = (bin) => {
        if (celebration !== null || submitting || !selectedId) return;
        const item = tray.find((i) => i.id === selectedId);
        if (!item) return;

        if (item.bin === bin.id) {
            // See STREAK_THRESHOLD's doc comment — a brighter "coin" cue on
            // every Nth correct placement instead of the usual chime,
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
            setPlacedByBin((prev) => ({ ...prev, [bin.id]: [...(prev[bin.id] || []), item] }));
            setSortedIds((prev) => new Set(prev).add(item.id));
            setSelectedId(null);
        } else {
            playSynth('laser');
            setStreak(0);
            setWrongCount((c) => c + 1);
            setSelectedId(null);
            const token = Date.now();
            setShakeBinId({ token, binId: bin.id });
            setTimeout(() => setShakeBinId((f) => (f?.token === token ? null : f)), WRONG_FLASH_MS);
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
        <div className="so-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="so-character-header">
                <span className="so-character-emoji">{character.emoji || '🗂️'}</span>
                <h2>{character.label || activity.title}</h2>
            </div>

            {activity.instruction_text && <p className="so-instruction">{activity.instruction_text}</p>}

            {streakFlash && (
                <div className="so-streak-badge" key={streakFlash.token}>
                    🔥 {streakFlash.count}!
                </div>
            )}

            <div className="so-bins">
                {bins.map((bin) => {
                    const placed = placedByBin[bin.id] || [];
                    const shaking = shakeBinId?.binId === bin.id;
                    const canReceive = !!selectedId;
                    return (
                        <button
                            key={bin.id}
                            className={`so-bin ${shaking ? 'so-bin-wrong' : ''} ${canReceive ? 'so-bin-receiving' : ''}`}
                            onClick={() => handleTapBin(bin)}
                            disabled={submitting}
                        >
                            <span className="so-bin-emoji">{bin.emoji || '📦'}</span>
                            <span className="so-bin-label">{bin.label}</span>
                            <span className="so-bin-placed">
                                {placed.map((p) => (
                                    <span key={p.id} className="so-bin-placed-emoji">{p.emoji}</span>
                                ))}
                            </span>
                        </button>
                    );
                })}
            </div>

            <div className="so-tray">
                {tray.map((item, i) => (
                    <button
                        key={item.id}
                        className={`so-item ${selectedId === item.id ? 'so-item-selected' : ''}`}
                        style={{ '--i': i, animationDelay: `${i * 0.06}s` }}
                        onClick={() => handleSelectItem(item)}
                        disabled={submitting}
                    >
                        <span className="so-item-emoji">{item.emoji}</span>
                        <span className="so-item-label">{item.label}</span>
                    </button>
                ))}
            </div>

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
