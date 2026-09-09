import React, { useEffect, useMemo, useState } from 'react';
import './PairsActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { shuffle, starsForWrongCount, recordGuestCompletion } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

// How long a matched/mismatched pair stays revealed before the board
// reacts (locks in as solved, or flips back down) — long enough for a
// 5-8 year old to actually look at both cards, short enough not to drag
// out a mismatch.
const RESOLVE_MS = 800;

/** One "flip two cards, find the match" round. activity.content shape
 * (mode: "pairs"): { character: {emoji,label}, cards: [{id,label,emoji}] }.
 * Fifth sibling of MatchingActivity.js/BuildActivity.js/TraceActivity.js/
 * MazeActivity.js — same completion flow, different input: each `cards`
 * entry becomes TWO face-down tiles (a matched pair), tapped one at a time
 * instead of a single correct/distractor pool. A mismatched flip is scored
 * exactly like a wrong tap/drop elsewhere — reuses starsForWrongCount as-is,
 * no new scoring rule needed.
 */
export default function PairsActivity({ activity, onBack, onComplete, lang, toggleLang, t, guest = false }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const cards = content.cards || [];

    // Two tiles per card (same id, distinct tileId), shuffled into one
    // board. Depend on activity.content, not just activity.id — see
    // MatchingActivity.js's pool useMemo for why (lang toggle mid-play
    // re-fetches translated content; depending on the object reference
    // itself, not a flag that changes synchronously before that fetch
    // resolves, is what actually catches the update).
    const tiles = useMemo(() => shuffle(
        cards.flatMap((c) => [
            { ...c, tileId: `${c.id}-a` },
            { ...c, tileId: `${c.id}-b` },
        ])
        // eslint-disable-next-line react-hooks/exhaustive-deps
    ), [activity.id, activity.content]);

    const [flippedIds, setFlippedIds] = useState([]); // tileIds currently face-up, pending resolution (max 2)
    const [matchedCardIds, setMatchedCardIds] = useState(() => new Set());
    const [wrongCount, setWrongCount] = useState(0);
    // tileIds of the current mismatched pair, shown red+shaking for the
    // RESOLVE_MS window before both flip back down — every OTHER activity
    // in this feature pairs a wrong answer with a visible shake/red flash,
    // not just a sound; Pairs originally only played the 'laser' cue and
    // silently reset, which a 5-8yo (or anyone with sound off/unnoticed)
    // reads as "I tapped and nothing happened" — reported live 2026-09-09.
    const [wrongTileIds, setWrongTileIds] = useState(() => new Set());
    const [resolving, setResolving] = useState(false); // true while a flipped pair is settling — blocks further taps
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    // Fires once every card has a matched pair — reading it from state
    // (rather than inline in handleTap) keeps this correct regardless of
    // how the last match landed.
    useEffect(() => {
        if (celebration === null && cards.length > 0 && matchedCardIds.size === cards.length) {
            playSynth('fanfare');
            setCelebration(starsForWrongCount(wrongCount));
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [matchedCardIds]);

    const handleTap = (tile) => {
        if (celebration !== null || submitting || resolving) return;
        if (matchedCardIds.has(tile.id) || flippedIds.includes(tile.tileId)) return;

        const next = [...flippedIds, tile.tileId];
        setFlippedIds(next);
        if (next.length < 2) return;

        const [firstTileId, secondTileId] = next;
        const first = tiles.find((tl) => tl.tileId === firstTileId);
        const second = tiles.find((tl) => tl.tileId === secondTileId);
        setResolving(true);

        if (first.id === second.id) {
            playSynth('chime');
            setTimeout(() => {
                setMatchedCardIds((prev) => new Set(prev).add(first.id));
                setFlippedIds([]);
                setResolving(false);
            }, RESOLVE_MS);
        } else {
            playSynth('laser');
            setWrongCount((c) => c + 1);
            setWrongTileIds(new Set([firstTileId, secondTileId]));
            setTimeout(() => {
                setFlippedIds([]);
                setWrongTileIds(new Set());
                setResolving(false);
            }, RESOLVE_MS);
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
        <div className="pa-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="pa-character-header">
                <span className="pa-character-emoji">{character.emoji || '🧠'}</span>
                <h2>{character.label || activity.title}</h2>
                {/* Pairs had no persistent progress indicator at all — every
                    other activity does (a "N / M" badge, a numbered slot
                    row, ...) — so "did my match actually count?" had no
                    lasting answer besides re-counting matched-looking tiles
                    by eye. Same visual language as MatchingActivity.js's
                    ma-progress-badge. */}
                <span className="pa-progress-badge">{matchedCardIds.size} / {cards.length}</span>
            </div>

            {activity.instruction_text && <p className="pa-instruction">{activity.instruction_text}</p>}

            <div className="pa-grid">
                {tiles.map((tile) => {
                    const matched = matchedCardIds.has(tile.id);
                    const faceUp = matched || flippedIds.includes(tile.tileId);
                    const wrong = wrongTileIds.has(tile.tileId);
                    return (
                        <button
                            key={tile.tileId}
                            className={`pa-tile ${faceUp ? 'pa-tile-up' : ''} ${matched ? 'pa-tile-matched' : ''} ${wrong ? 'pa-tile-wrong' : ''}`}
                            onClick={() => handleTap(tile)}
                            disabled={submitting || matched}
                            aria-label={faceUp ? (tile.label || tile.id) : t('el.pairsCardHidden') }
                        >
                            <span className="pa-tile-inner">
                                <span className="pa-tile-face pa-tile-back">❓</span>
                                <span className="pa-tile-face pa-tile-front">{tile.emoji || '❓'}</span>
                            </span>
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
