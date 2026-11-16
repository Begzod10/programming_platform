import React, { useEffect, useMemo, useRef, useState } from 'react';
import { ArrowUp, ArrowDown, ArrowLeft, ArrowRight } from 'lucide-react';
import './ActiveGames.css';
import ActivityShell, { useActivityCompletion } from './ActivityShell';
import ItemPic from './ItemPic';
import { makeBoard } from './collectBoard';
import { playSynth } from '../../../utils/soundSynth';
import { cheer } from './earlyVoice';
import { starsForWrongCount, WRONG_FLASH_MS } from './earlyLearningUtils';

const DIRECTIONS = { up: [-1, 0], down: [1, 0], left: [0, -1], right: [0, 1] };
const KEYS = { ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right' };
const SWIPE_PX = 30;

/** Walk the field and pick up the right things (mode: "collect"). Plays
 * select content: { character, correct_items, distractor_items, grid_size? }.
 * Arrow buttons, keyboard arrows or a swipe move the hero one cell. A wall
 * or the edge just stops the walk; a wrong item is a mistake (the hero
 * stays where it was, the item shakes); stepping on a right item collects
 * it. Done when every right item is collected. */
export default function CollectActivity(props) {
    const { activity, guest, onComplete, t } = props;
    const content = activity.content || {};
    const completion = useActivityCompletion(activity, guest, onComplete);
    const character = content.character || {};

    const board = useMemo(
        () => makeBoard(content, (Number(activity.id) || 0) * 10 + (activity.level || 1)),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [activity.id, activity.level, activity.content]
    );
    const rightCount = board.items.filter((x) => x.ok).length;

    const [pos, setPos] = useState(board.start);
    const [collected, setCollected] = useState(() => new Set());
    const [wrong, setWrong] = useState(0);
    const [shake, setShake] = useState(null); // { token, index }
    const swipeFrom = useRef(null);

    const isWall = (r, c) => board.walls.some((w) => w[0] === r && w[1] === c);
    const itemAt = (r, c) => board.items.findIndex((x) => x.r === r && x.c === c);

    const move = (dir) => {
        if (completion.celebration !== null || completion.submitting) return;
        const [dr, dc] = DIRECTIONS[dir];
        const r = pos[0] + dr;
        const c = pos[1] + dc;
        if (r < 0 || c < 0 || r >= board.size || c >= board.size || isWall(r, c)) return;
        const index = itemAt(r, c);
        const found = index >= 0 ? board.items[index] : null;
        if (found && !found.ok) {
            playSynth('laser');
            cheer('wrong');
            setWrong((n) => n + 1);
            const token = Date.now() + Math.random();
            setShake({ token, index });
            setTimeout(() => setShake((s) => (s?.token === token ? null : s)), WRONG_FLASH_MS);
            return;
        }
        setPos([r, c]);
        if (found && !collected.has(index)) {
            const next = new Set(collected).add(index);
            setCollected(next);
            cheer('correct');
            if (next.size >= rightCount) {
                playSynth('fanfare');
                completion.finish(starsForWrongCount(wrong));
            } else {
                playSynth('chime');
            }
        }
    };

    // Keyboard arrows. Re-bound every render so `move` sees fresh state.
    useEffect(() => {
        const onKey = (e) => {
            const dir = KEYS[e.key];
            if (!dir) return;
            e.preventDefault();
            move(dir);
        };
        window.addEventListener('keydown', onKey);
        return () => window.removeEventListener('keydown', onKey);
    });

    const onPointerDown = (e) => { swipeFrom.current = { x: e.clientX, y: e.clientY }; };
    const onPointerUp = (e) => {
        const from = swipeFrom.current;
        swipeFrom.current = null;
        if (!from) return;
        const dx = (e.clientX || 0) - from.x;
        const dy = (e.clientY || 0) - from.y;
        if (Math.max(Math.abs(dx), Math.abs(dy)) < SWIPE_PX) return;
        if (Math.abs(dx) > Math.abs(dy)) move(dx > 0 ? 'right' : 'left');
        else move(dy > 0 ? 'down' : 'up');
    };

    const cells = [];
    for (let r = 0; r < board.size; r += 1) {
        for (let c = 0; c < board.size; c += 1) {
            const index = itemAt(r, c);
            const entry = index >= 0 ? board.items[index] : null;
            const done = entry && collected.has(index);
            const hero = pos[0] === r && pos[1] === c;
            const cls = ['ag-cell'];
            if (isWall(r, c)) cls.push('ag-cell-wall');
            if (done) cls.push('ag-cell-collected');
            if (shake?.index === index && entry) cls.push('ag-shake');
            cells.push(
                <div key={`${r},${c}`} className={cls.join(' ')}>
                    {entry && !done && (
                        <span className="ag-cell-item" aria-label={entry.item.label} title={entry.item.label}>
                            <ItemPic item={entry.item} size={24} />
                        </span>
                    )}
                    {hero && <span className="ag-hero" data-pos={`${r},${c}`}>{character.emoji || '🐭'}</span>}
                </div>
            );
        }
    }

    const pad = (dir, Icon, key) => (
        <button type="button" className={`ag-pad-btn ag-pad-${dir}`} aria-label={t(key)}
            onClick={() => move(dir)} disabled={completion.submitting}>
            <Icon size={22} />
        </button>
    );

    return (
        <ActivityShell {...props} emoji="🐭" completion={completion}>
            <div className="ag-counter" aria-live="polite">{`${collected.size} / ${rightCount}`}</div>
            <div
                className="ag-board"
                style={{ gridTemplateColumns: `repeat(${board.size}, 1fr)`, touchAction: 'none' }}
                onPointerDown={onPointerDown}
                onPointerUp={onPointerUp}
                onPointerCancel={() => { swipeFrom.current = null; }}
            >
                {cells}
            </div>
            <div className="ag-pad">
                {pad('up', ArrowUp, 'el.moveUp')}
                <div className="ag-pad-row">
                    {pad('left', ArrowLeft, 'el.moveLeft')}
                    {pad('right', ArrowRight, 'el.moveRight')}
                </div>
                {pad('down', ArrowDown, 'el.moveDown')}
            </div>
        </ActivityShell>
    );
}
