import React, { useEffect, useMemo, useRef, useState } from 'react';
import './ActiveGames.css';
import ActivityShell, { useActivityCompletion } from './ActivityShell';
import ItemPic from './ItemPic';
import { LANES, startFalling, stepFalling } from './catchGame';
import { CATCH_FALL_MS, rng, shuffled } from './levelContent';
import { playSynth } from '../../../utils/soundSynth';
import { cheer } from './earlyVoice';
import { starsForWrongCount } from './earlyLearningUtils';

const REDUCED_MOTION_SLOWER = 1.5;
const MAX_FRAME_MS = 100;

function reducedMotion() {
    try {
        return !!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    } catch (e) {
        return false;
    }
}

const nextFrame = (fn) => (window.requestAnimationFrame ? window.requestAnimationFrame(fn) : setTimeout(() => fn(Date.now()), 16));
const cancelFrame = (id) => (window.cancelAnimationFrame ? window.cancelAnimationFrame(id) : clearTimeout(id));

/** Catch the right things in the basket (mode: "catch"). Plays select
 * content: { character, correct_items, distractor_items, fall_ms? }. Items
 * fall slowly down three lanes (at most two at once, see catchGame.js);
 * the basket moves by tapping a lane, dragging along the field or with the
 * arrow keys. A caught right item is collected, a caught wrong one is a
 * mistake; a missed right item falls again later. No timer. Done when every
 * right item is caught. */
export default function CatchActivity(props) {
    const { activity, guest, onComplete, t } = props;
    const content = activity.content || {};
    const completion = useActivityCompletion(activity, guest, onComplete);

    const pieces = useMemo(() => shuffled([
        ...(content.correct_items || []).filter(Boolean).map((item, i) => ({ key: `c${i}`, item, ok: true })),
        ...(content.distractor_items || []).filter(Boolean).map((item, i) => ({ key: `d${i}`, item, ok: false })),
    ], rng((Number(activity.id) || 0) * 13 + (activity.level || 1))),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [activity.id, activity.level, activity.content]);
    const rightCount = pieces.filter((p) => p.ok).length;
    const fallMs = (content.fall_ms || CATCH_FALL_MS[0]) * (reducedMotion() ? REDUCED_MOTION_SLOWER : 1);

    const [game, setGame] = useState(() => startFalling(pieces, fallMs));
    const gameRef = useRef(game);
    const wrongRef = useRef(0);
    const doneRef = useRef(false);
    const fieldRef = useRef(null);
    const dragging = useRef(false);

    const commit = (next) => {
        gameRef.current = next;
        setGame(next);
    };

    // A language switch brings new labels for the same lists: keep the game, swap the items.
    useEffect(() => {
        const byKey = new Map(pieces.map((p) => [p.key, p]));
        const swap = (p) => byKey.get(p.key) || p;
        const g = gameRef.current;
        commit({ ...g, queue: g.queue.map(swap), falling: g.falling.map((f) => ({ ...f, piece: swap(f.piece) })) });
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [pieces]);

    useEffect(() => {
        let frame = null;
        let last = null;
        const tick = (now) => {
            if (doneRef.current) return;
            const dt = last === null ? 0 : Math.min(MAX_FRAME_MS, Math.max(0, now - last));
            last = now;
            const next = stepFalling(gameRef.current, dt);
            for (const e of next.events) {
                if (e.type === 'caught') {
                    cheer('correct');
                    playSynth('chime');
                } else if (e.type === 'mistake') {
                    wrongRef.current += 1;
                    cheer('wrong');
                    playSynth('laser');
                }
            }
            commit(next);
            if (rightCount > 0 && next.caught >= rightCount) {
                doneRef.current = true;
                playSynth('fanfare');
                completion.finish(starsForWrongCount(wrongRef.current));
                return;
            }
            frame = nextFrame(tick);
        };
        frame = nextFrame(tick);
        return () => cancelFrame(frame);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const moveTo = (lane) => {
        const l = Math.max(0, Math.min(LANES - 1, lane));
        if (l !== gameRef.current.basketLane) commit({ ...gameRef.current, basketLane: l });
    };

    useEffect(() => {
        const onKey = (e) => {
            if (e.key === 'ArrowLeft') { e.preventDefault(); moveTo(gameRef.current.basketLane - 1); }
            if (e.key === 'ArrowRight') { e.preventDefault(); moveTo(gameRef.current.basketLane + 1); }
        };
        window.addEventListener('keydown', onKey);
        return () => window.removeEventListener('keydown', onKey);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const laneAt = (clientX) => {
        const r = fieldRef.current?.getBoundingClientRect();
        if (!r || !r.width) return null;
        return Math.floor(((clientX - r.left) / r.width) * LANES);
    };
    const onDown = () => { dragging.current = true; };
    const onMove = (e) => {
        if (!dragging.current) return;
        const lane = laneAt(e.clientX || 0);
        if (lane !== null) moveTo(lane);
    };
    const stopDrag = () => { dragging.current = false; };

    return (
        <ActivityShell {...props} emoji="🧺" completion={completion}>
            <div className="ag-counter" aria-live="polite">{`${game.caught} / ${rightCount}`}</div>
            <div
                ref={fieldRef}
                className="ag-catch"
                style={{ touchAction: 'none' }}
                onPointerDown={onDown}
                onPointerMove={onMove}
                onPointerUp={stopDrag}
                onPointerCancel={stopDrag}
                onPointerLeave={stopDrag}
            >
                {Array.from({ length: LANES }, (_, lane) => (
                    <button key={lane} type="button" className="ag-lane" style={{ left: `${(lane / LANES) * 100}%` }}
                        aria-label={`${t('el.lane')} ${lane + 1}`} onClick={() => moveTo(lane)} />
                ))}
                {game.falling.map((f) => (
                    <span
                        key={f.id}
                        className="ag-fall"
                        data-lane={f.lane}
                        data-y={f.y.toFixed(3)}
                        aria-label={f.piece.item.label}
                        style={{ left: `${((f.lane + 0.5) / LANES) * 100}%`, top: `${f.y * 82}%` }}
                    >
                        <ItemPic item={f.piece.item} size={34} />
                        <span className="ag-fall-label">{f.piece.item.label}</span>
                    </span>
                ))}
                <span className="ag-basket" data-lane={game.basketLane}
                    style={{ left: `${((game.basketLane + 0.5) / LANES) * 100}%` }} aria-hidden="true">🧺</span>
            </div>
        </ActivityShell>
    );
}
