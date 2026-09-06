import React, { useEffect, useMemo, useRef, useState } from 'react';
import ReactDOM from 'react-dom';
import './BuildActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { shuffle, starsForWrongCount, WRONG_FLASH_MS } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

/** Non-interactive silhouette for content.scene === "snowman" — plain CSS
 * circles, not an image, since this app has no illustration pipeline (see
 * MatchingActivity.js's ItemIcon docstring). */
function SnowmanBase() {
    return (
        <div className="ba-snowman" aria-hidden="true">
            <span className="ba-snowman-circle ba-snowman-bottom" />
            <span className="ba-snowman-circle ba-snowman-middle" />
            <span className="ba-snowman-circle ba-snowman-top" />
        </div>
    );
}

/** Non-interactive silhouette for content.scene === "house" — a plain CSS
 * rectangle (walls) plus a clip-path triangle (roof), same no-image
 * reasoning as SnowmanBase above. clip-path is used instead of the classic
 * border-triangle trick because border-width is fixed px/em and won't scale
 * with this container's percentage-based sizing; clip-path does. */
function HouseBase() {
    return (
        <div className="ba-house" aria-hidden="true">
            <span className="ba-house-roof" />
            <span className="ba-house-wall" />
        </div>
    );
}

const SCENES = { snowman: SnowmanBase, house: HouseBase };

/** One "drag each piece onto its own spot" round.
 * activity.content shape (mode: "build"):
 *   { scene, character: {emoji,label}, slots: [{id,label,emoji,x,y,w,h}], distractor_items: [...] }
 * Sibling of MatchingActivity.js's tap-to-select mechanic — same scoring/
 * sound/celebration rules (see earlyLearningUtils.js), different input:
 * pointer-drag instead of tap, hit-tested against each slot's own
 * drop-zone rectangle instead of a flat item pool.
 */
export default function BuildActivity({ activity, onBack, onComplete, lang, toggleLang, t }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const slots = content.slots || [];
    const distractorItems = content.distractor_items || [];
    const Scene = SCENES[content.scene] || null;

    const pool = useMemo(() => {
        const tagged = [
            ...slots.map((s) => ({ ...s, isCorrect: true })),
            ...distractorItems.map((d) => ({ ...d, isCorrect: false })),
        ];
        return shuffle(tagged);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [activity.id]);

    // Two separate sets, not one: a slot's own id (which *scene position*
    // is visually filled — drives the picture + the completion check) is
    // not always the same id as the piece that filled it. Most pieces are
    // unique (hat only fits the hat slot, matchGroup unset → must equal
    // targetId), but slots can opt into a `matchGroup` (see the 3 identical
    // snowman buttons in _seed_early_learning.py) so any piece sharing that
    // group can fill any of that group's still-empty slots — a kid has no
    // way to tell three plain black buttons apart, so requiring the exact
    // button1↔button1 pairing would reject perfectly correct answers.
    const [filledSlotIds, setFilledSlotIds] = useState(() => new Set());
    const [usedPieceIds, setUsedPieceIds] = useState(() => new Set());
    const [wrongCount, setWrongCount] = useState(0);
    const [flash, setFlash] = useState(null); // { id, message } | null
    const [draggingId, setDraggingId] = useState(null);
    const [dragPos, setDragPos] = useState(null); // {x,y} | null, viewport coords
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const draggingPieceRef = useRef(null);
    const slotElsRef = useRef({});

    const hitTestSlot = (x, y) => {
        for (const [id, el] of Object.entries(slotElsRef.current)) {
            if (!el) continue;
            const r = el.getBoundingClientRect();
            if (x >= r.left && x <= r.right && y >= r.top && y <= r.bottom) return id;
        }
        return null;
    };

    const wrongMessage = (label) => (lang === 'ru' ? `Ой! «${label}» сюда не подходит.` : `Oh-oh! "${label}" bu yerga mos emas.`);

    const resolveDrop = (piece, x, y) => {
        const targetId = hitTestSlot(x, y);
        // Dropped on empty background — an imprecise drag from a 5-8 year
        // old shouldn't be scored the same as a deliberate wrong placement,
        // so this just returns the piece to the tray silently.
        if (targetId === null) return;

        const targetSlot = slots.find((s) => s.id === targetId);
        const isMatch = piece.isCorrect && targetSlot && !filledSlotIds.has(targetId) && (
            targetId === piece.id || (piece.matchGroup && piece.matchGroup === targetSlot.matchGroup)
        );

        if (isMatch) {
            playSynth('chime');
            setFilledSlotIds((prev) => new Set(prev).add(targetId));
            setUsedPieceIds((prev) => new Set(prev).add(piece.id));
        } else {
            playSynth('laser');
            setWrongCount((c) => c + 1);
            setFlash({ id: piece.id, message: wrongMessage(piece.label) });
            setTimeout(() => setFlash((f) => (f?.id === piece.id ? null : f)), WRONG_FLASH_MS);
        }
    };

    const beginDrag = (e, piece) => {
        if (celebration !== null || submitting) return;
        e.preventDefault();
        draggingPieceRef.current = piece;
        setDraggingId(piece.id);
        setDragPos({ x: e.clientX, y: e.clientY });
    };

    // One subscription per drag gesture (start→end), not per pointermove —
    // the effect only re-runs when dragging starts/stops, since handleMove
    // always writes a fresh {x,y} rather than reading stale state.
    useEffect(() => {
        if (!dragPos) return undefined;
        const handleMove = (e) => setDragPos({ x: e.clientX, y: e.clientY });
        const handleUp = (e) => {
            const piece = draggingPieceRef.current;
            draggingPieceRef.current = null;
            setDraggingId(null);
            setDragPos(null);
            if (piece) resolveDrop(piece, e.clientX, e.clientY);
        };
        window.addEventListener('pointermove', handleMove);
        window.addEventListener('pointerup', handleUp, { once: true });
        return () => {
            window.removeEventListener('pointermove', handleMove);
            window.removeEventListener('pointerup', handleUp);
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [!!dragPos]);

    // Fires once every slot is actually filled — reading it from state
    // (rather than inline in resolveDrop) keeps this correct even if two
    // drops somehow land in the same React batch.
    useEffect(() => {
        if (celebration === null && slots.length > 0 && filledSlotIds.size === slots.length) {
            playSynth('fanfare');
            setCelebration(starsForWrongCount(wrongCount));
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [filledSlotIds]);

    const handleCelebrationDone = () => {
        const stars = celebration;
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

    const tray = pool.filter((p) => !usedPieceIds.has(p.id));

    return (
        <div className="ba-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="ba-character">
                <span className="ba-character-emoji">{character.emoji || '🧩'}</span>
                <h2>{character.label || activity.title}</h2>
                <span className="ba-progress-badge">{filledSlotIds.size} / {slots.length}</span>
            </div>

            {flash && <div className="ba-error-banner">{flash.message}</div>}

            <div className="ba-scene">
                {Scene && <Scene />}
                {slots.map((slot) => {
                    const filled = filledSlotIds.has(slot.id);
                    return (
                        <div
                            key={slot.id}
                            ref={(el) => { slotElsRef.current[slot.id] = el; }}
                            className={`ba-slot ${filled ? 'ba-slot-filled' : ''}`}
                            style={{ left: `${slot.x}%`, top: `${slot.y}%`, width: `${slot.w}%`, height: `${slot.h}%` }}
                        >
                            <span className="ba-slot-emoji">{slot.emoji}</span>
                        </div>
                    );
                })}
            </div>

            <div className="ba-tray">
                {tray.map((piece) => (
                    <div
                        key={piece.id}
                        className={`ba-piece ${draggingId === piece.id ? 'ba-piece-dragging' : ''} ${flash?.id === piece.id ? 'ba-piece-wrong' : ''}`}
                        onPointerDown={(e) => beginDrag(e, piece)}
                    >
                        <span className="ba-piece-emoji">{flash?.id === piece.id ? '😕' : piece.emoji}</span>
                        <span className="ba-piece-label">{piece.label}</span>
                    </div>
                ))}
            </div>

            {dragPos && draggingPieceRef.current && ReactDOM.createPortal(
                // Portalled straight to <body> — .ba-page has a lingering
                // `animation: ... both` transform (see BuildActivity.css),
                // and ANY non-`none` transform on an ancestor becomes the
                // containing block for a `position: fixed` descendant, which
                // silently offset this ghost from the real cursor position
                // by however far .ba-page sits from the viewport's corner.
                <div className="ba-drag-ghost" style={{ left: dragPos.x, top: dragPos.y }}>
                    <span className="ba-piece-emoji">{draggingPieceRef.current.emoji}</span>
                </div>,
                document.body
            )}

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
