import React, { useEffect, useMemo, useReducer, useRef, useState } from 'react';
import './ActiveGames.css';
import ActivityShell, { useActivityCompletion } from './ActivityShell';
import ItemPic from './ItemPic';
import { playSynth } from '../../../utils/soundSynth';
import { cheer } from './earlyVoice';
import { shuffle, starsForWrongCount, WRONG_FLASH_MS } from './earlyLearningUtils';

const DRAG_PX = 8;

/** Draw a line from each right item to the character (mode: "connect").
 * Plays select content: { character, correct_items, distractor_items,
 * hide_labels? }. Pointer events, so mouse and finger both draw; the field
 * has touch-action: none so drawing never scrolls the page. A line that
 * ends on the character is checked: a right item stays connected, a wrong
 * one flashes red and is a mistake. A line that ends anywhere else just
 * disappears. Tapping an item and then the character does the same (and
 * works from the keyboard). Done when every right item is connected. */
export default function ConnectActivity(props) {
    const { activity, guest, onComplete } = props;
    const content = activity.content || {};
    const completion = useActivityCompletion(activity, guest, onComplete);
    const character = content.character || {};
    const hideLabels = !!content.hide_labels;

    // Keys are positions in the authored lists, so a language switch (new
    // labels, same lists) keeps what is already connected.
    const pieces = useMemo(() => shuffle([
        ...(content.correct_items || []).filter(Boolean).map((item, i) => ({ key: `c${i}`, item, ok: true })),
        ...(content.distractor_items || []).filter(Boolean).map((item, i) => ({ key: `d${i}`, item, ok: false })),
    ]),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [activity.id, activity.content]);
    const rightCount = pieces.filter((p) => p.ok).length;

    const [connected, setConnected] = useState(() => new Set());
    const [wrong, setWrong] = useState(0);
    const [drag, setDrag] = useState(null); // { key, x0, y0, x, y } in field coordinates
    const [bad, setBad] = useState(null); // { token, key }
    const [selected, setSelected] = useState(null);
    const fieldRef = useRef(null);
    const targetRef = useRef(null);
    const pieceRefs = useRef({});
    const justDragged = useRef(false);
    const [, remeasure] = useReducer((n) => n + 1, 0);

    useEffect(() => {
        window.addEventListener('resize', remeasure);
        return () => window.removeEventListener('resize', remeasure);
    }, []);

    const busy = completion.celebration !== null || completion.submitting;

    const judge = (key) => {
        const piece = pieces.find((p) => p.key === key);
        if (!piece || connected.has(key) || busy) return;
        if (piece.ok) {
            const next = new Set(connected).add(key);
            setConnected(next);
            cheer('correct');
            if (next.size >= rightCount) {
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
            setBad({ token, key });
            setTimeout(() => setBad((b) => (b?.token === token ? null : b)), WRONG_FLASH_MS);
        }
    };

    const fieldBox = () => fieldRef.current?.getBoundingClientRect() || { left: 0, top: 0 };
    const anchorOf = (key) => {
        const el = pieceRefs.current[key];
        if (!el) return null;
        const box = fieldBox();
        const r = el.getBoundingClientRect();
        return { x: r.left + r.width - box.left, y: r.top + r.height / 2 - box.top };
    };
    const targetAnchor = () => {
        const el = targetRef.current;
        if (!el) return null;
        const box = fieldBox();
        const r = el.getBoundingClientRect();
        return { x: r.left - box.left + 12, y: r.top + r.height / 2 - box.top };
    };
    const overTarget = (clientX, clientY) => {
        const r = targetRef.current?.getBoundingClientRect();
        return !!r && clientX >= r.left && clientX <= r.right && clientY >= r.top && clientY <= r.bottom;
    };

    const onPieceDown = (e, key) => {
        if (busy || connected.has(key)) return;
        const start = anchorOf(key) || { x: 0, y: 0 };
        const box = fieldBox();
        setDrag({ key, x0: start.x, y0: start.y, x: (e.clientX || 0) - box.left, y: (e.clientY || 0) - box.top, cx: e.clientX || 0, cy: e.clientY || 0, moved: false });
    };
    const onMove = (e) => {
        if (!drag) return;
        const box = fieldBox();
        const cx = e.clientX || 0;
        const cy = e.clientY || 0;
        const moved = drag.moved || Math.abs(cx - drag.cx) + Math.abs(cy - drag.cy) > DRAG_PX;
        setDrag({ ...drag, x: cx - box.left, y: cy - box.top, moved });
    };
    const onUp = (e) => {
        if (!drag) return;
        const { key, moved } = drag;
        setDrag(null);
        if (!moved) return; // a tap: the click handler selects the item
        justDragged.current = true;
        setTimeout(() => { justDragged.current = false; }, 400);
        if (overTarget(e.clientX || 0, e.clientY || 0)) judge(key);
    };

    const onPieceClick = (key) => {
        if (justDragged.current || busy || connected.has(key)) return;
        setSelected((s) => (s === key ? null : key));
    };
    const onTargetClick = () => {
        if (selected == null) return;
        judge(selected);
        setSelected(null);
    };

    const target = targetAnchor();
    const lines = [];
    if (target) {
        for (const key of connected) {
            const a = anchorOf(key);
            if (a) lines.push(<line key={key} className="ag-line ag-line-done" x1={a.x} y1={a.y} x2={target.x} y2={target.y} />);
        }
        if (bad) {
            const a = anchorOf(bad.key);
            if (a) lines.push(<line key="bad" className="ag-line ag-line-bad" x1={a.x} y1={a.y} x2={target.x} y2={target.y} />);
        }
    }
    if (drag) lines.push(<line key="drag" className="ag-line ag-line-live" x1={drag.x0} y1={drag.y0} x2={drag.x} y2={drag.y} />);

    return (
        <ActivityShell {...props} emoji="✏️" completion={completion}>
            <div
                ref={fieldRef}
                className="ag-connect"
                style={{ touchAction: 'none' }}
                onPointerMove={onMove}
                onPointerUp={onUp}
                onPointerCancel={() => setDrag(null)}
                onPointerLeave={(e) => { if (e.pointerType === 'mouse') setDrag(null); }}
            >
                <svg className="ag-lines" aria-hidden="true">{lines}</svg>
                <div className="ag-connect-items">
                    {pieces.map((p) => {
                        const cls = ['ag-piece'];
                        if (connected.has(p.key)) cls.push('ag-piece-done');
                        if (bad?.key === p.key) cls.push('ag-shake');
                        if (selected === p.key) cls.push('ag-piece-selected');
                        return (
                            <button
                                key={p.key}
                                type="button"
                                ref={(el) => { pieceRefs.current[p.key] = el; }}
                                className={cls.join(' ')}
                                aria-label={p.item.label}
                                aria-pressed={selected === p.key}
                                onPointerDown={(e) => onPieceDown(e, p.key)}
                                onClick={() => onPieceClick(p.key)}
                            >
                                <ItemPic item={p.item} size={30} />
                                {!hideLabels && <span className="ag-piece-label">{p.item.label}</span>}
                            </button>
                        );
                    })}
                </div>
                <button type="button" ref={targetRef} className="ag-connect-target" onClick={onTargetClick}
                    aria-label={character.label || activity.title}>
                    <span className="ag-target-emoji">{character.emoji || '🎯'}</span>
                    <span className="ag-target-label">{character.label}</span>
                </button>
            </div>
            <div className="ag-counter" aria-live="polite">{`${connected.size} / ${rightCount}`}</div>
        </ActivityShell>
    );
}
