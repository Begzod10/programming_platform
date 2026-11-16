import React, { useMemo, useRef, useState } from 'react';
import './ActiveGames.css';
import ActivityShell, { useActivityCompletion } from './ActivityShell';
import ItemPic from './ItemPic';
import { makeBaskets } from './dragsortSetup';
import { playSynth } from '../../../utils/soundSynth';
import { cheer } from './earlyVoice';
import { shuffle, starsForWrongCount, WRONG_FLASH_MS } from './earlyLearningUtils';

const DRAG_PX = 8;

/** Drag each thing into the right character's basket (mode: "dragsort").
 * Baskets come from makeBaskets (dragsortSetup.js): the game's own
 * character, a partner from another module and, at level 3, a second
 * partner. The games page only opens this screen when makeBaskets returns
 * baskets (otherwise the game plays as connect). Pointer drag for mouse and
 * finger (touch-action: none), or tap a piece then a basket. A drop on the
 * wrong basket sends the piece back and is a mistake; a drop anywhere else
 * just sends it back. Done when every piece is in its basket. */
export default function DragSortActivity(props) {
    const { activity, guest, onComplete } = props;
    const completion = useActivityCompletion(activity, guest, onComplete);

    const setup = useMemo(() => makeBaskets(activity.content, activity.level || 1),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [activity.id, activity.level, activity.content]);
    const baskets = setup?.baskets || [];
    const pieces = useMemo(() => shuffle(setup?.pieces || []), [setup]);

    const [placed, setPlaced] = useState(() => new Set());
    const [wrong, setWrong] = useState(0);
    const [drag, setDrag] = useState(null); // { key, sx, sy, dx, dy, moved }
    const [shake, setShake] = useState(null); // { token, basket }
    const [selected, setSelected] = useState(null);
    const basketRefs = useRef([]);
    const justDragged = useRef(false);

    const busy = completion.celebration !== null || completion.submitting;

    const judge = (key, basket) => {
        const piece = pieces.find((p) => p.key === key);
        if (!piece || placed.has(key) || busy) return;
        if (piece.basket === basket) {
            const next = new Set(placed).add(key);
            setPlaced(next);
            cheer('correct');
            if (next.size >= pieces.length) {
                playSynth('fanfare');
                completion.finish(starsForWrongCount(wrong));
            } else {
                playSynth('chime');
            }
        } else {
            playSynth('laser');
            cheer('wrong');
            setWrong((n) => n + 1);
            const token = Date.now() + Math.random();
            setShake({ token, basket });
            setTimeout(() => setShake((s) => (s?.token === token ? null : s)), WRONG_FLASH_MS);
        }
    };

    const basketAt = (x, y) => basketRefs.current.findIndex((el) => {
        const r = el?.getBoundingClientRect();
        return !!r && x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
    });

    const onDown = (e, key) => {
        if (busy || placed.has(key)) return;
        setDrag({ key, sx: e.clientX || 0, sy: e.clientY || 0, dx: 0, dy: 0, moved: false });
    };
    const onMove = (e) => {
        if (!drag) return;
        const dx = (e.clientX || 0) - drag.sx;
        const dy = (e.clientY || 0) - drag.sy;
        setDrag({ ...drag, dx, dy, moved: drag.moved || Math.abs(dx) + Math.abs(dy) > DRAG_PX });
    };
    const onUp = (e) => {
        if (!drag) return;
        const { key, moved } = drag;
        setDrag(null);
        if (!moved) return; // a tap: the click handler selects the piece
        justDragged.current = true;
        setTimeout(() => { justDragged.current = false; }, 400);
        const basket = basketAt(e.clientX || 0, e.clientY || 0);
        if (basket >= 0) judge(key, basket);
    };

    const onPieceClick = (key) => {
        if (justDragged.current || busy || placed.has(key)) return;
        setSelected((s) => (s === key ? null : key));
    };
    const onBasketClick = (basket) => {
        if (selected == null) return;
        judge(selected, basket);
        setSelected(null);
    };

    return (
        <ActivityShell {...props} emoji="🗂️" completion={completion}>
            <div
                className="ag-sort"
                style={{ touchAction: 'none' }}
                onPointerMove={onMove}
                onPointerUp={onUp}
                onPointerCancel={() => setDrag(null)}
                onPointerLeave={(e) => { if (e.pointerType === 'mouse') setDrag(null); }}
            >
                <div className="ag-baskets" style={{ gridTemplateColumns: `repeat(${baskets.length}, minmax(0, 1fr))` }}>
                    {baskets.map((b, i) => (
                        <button
                            key={i}
                            type="button"
                            ref={(el) => { basketRefs.current[i] = el; }}
                            data-basket={i}
                            className={`ag-basket-drop ${shake?.basket === i ? 'ag-shake' : ''}`}
                            aria-label={b.character.label}
                            onClick={() => onBasketClick(i)}
                        >
                            <span className="ag-basket-hero">{b.character.emoji || '🧺'}</span>
                            <span className="ag-basket-name">{b.character.label}</span>
                            <span className="ag-basket-in">
                                {pieces.filter((p) => p.basket === i && placed.has(p.key)).map((p) => (
                                    <ItemPic key={p.key} item={p.item} size={20} />
                                ))}
                            </span>
                        </button>
                    ))}
                </div>
                <div className="ag-tray">
                    {pieces.filter((p) => !placed.has(p.key)).map((p) => {
                        // Only a real drag lifts the piece (pointer-events: none): a press
                        // that never moves must stay a click on the button.
                        const moving = drag?.key === p.key && drag.moved;
                        return (
                            <button
                                key={p.key}
                                type="button"
                                className={`ag-piece ${moving ? 'ag-piece-dragging' : ''} ${selected === p.key ? 'ag-piece-selected' : ''}`}
                                style={moving ? { transform: `translate(${drag.dx}px, ${drag.dy}px)` } : undefined}
                                aria-label={p.item.label}
                                aria-pressed={selected === p.key}
                                onPointerDown={(e) => onDown(e, p.key)}
                                onClick={() => onPieceClick(p.key)}
                            >
                                <ItemPic item={p.item} size={30} />
                                <span className="ag-piece-label">{p.item.label}</span>
                            </button>
                        );
                    })}
                </div>
            </div>
            <div className="ag-counter" aria-live="polite">{`${placed.size} / ${pieces.length}`}</div>
        </ActivityShell>
    );
}
