import React, { useCallback, useEffect, useRef, useState } from 'react';
import './WordChartActivity.css';
import ActivityShell, { useActivityCompletion } from './ActivityShell';
import { playSynth } from '../../../utils/soundSynth';

const SIZE = 4;
const rnd = (n) => Math.floor(Math.random() * n);

function emptyBoard() { return Array.from({ length: SIZE }, () => Array(SIZE).fill(0)); }

function addTile(board) {
    const free = [];
    board.forEach((row, r) => row.forEach((v, c) => { if (!v) free.push([r, c]); }));
    if (!free.length) return board;
    const [r, c] = free[rnd(free.length)];
    const next = board.map((row) => [...row]);
    next[r][c] = Math.random() < 0.85 ? 2 : 4;
    return next;
}

/** Slide one line toward index 0, merging equal neighbours once. */
function slideLine(line) {
    const nums = line.filter(Boolean);
    const out = [];
    let gained = 0;
    for (let i = 0; i < nums.length; i++) {
        if (nums[i] === nums[i + 1]) { out.push(nums[i] * 2); gained += nums[i] * 2; i++; } else out.push(nums[i]);
    }
    while (out.length < SIZE) out.push(0);
    return { out, gained };
}

function move(board, dir) {
    let moved = false;
    const next = emptyBoard();
    for (let i = 0; i < SIZE; i++) {
        const get = (j) => (dir === 'left' ? board[i][j] : dir === 'right' ? board[i][SIZE - 1 - j] : dir === 'up' ? board[j][i] : board[SIZE - 1 - j][i]);
        const { out } = slideLine(Array.from({ length: SIZE }, (_, j) => get(j)));
        for (let j = 0; j < SIZE; j++) {
            if (dir === 'left') next[i][j] = out[j];
            else if (dir === 'right') next[i][SIZE - 1 - j] = out[j];
            else if (dir === 'up') next[j][i] = out[j];
            else next[SIZE - 1 - j][i] = out[j];
        }
    }
    for (let r = 0; r < SIZE; r++) for (let c = 0; c < SIZE; c++) if (next[r][c] !== board[r][c]) moved = true;
    return { board: next, moved };
}

const canMove = (b) => ['left', 'right', 'up', 'down'].some((d) => move(b, d).moved);
const start = () => addTile(addTile(emptyBoard()));

const TILE_COLORS = { 2: '#ffe8a3', 4: '#ffd27a', 8: '#ffb066', 16: '#ff8e5c', 32: '#ff6b6b', 64: '#f06595', 128: '#cc5de8', 256: '#845ef7' };

/** 2048-style number merging. activity.content (mode: "merge"): { goal?: 64 }.
 * Reach the goal tile; stars by how few moves it took. A jammed board just
 * restarts (the move count keeps running). */
export default function MergeActivity(props) {
    const { activity, guest, onComplete, lang } = props;
    const goal = (activity.content || {}).goal || 64;
    const completion = useActivityCompletion(activity, guest, onComplete);
    const [board, setBoard] = useState(start);
    const [moves, setMoves] = useState(0);
    const [stuck, setStuck] = useState(false);
    const touch = useRef(null);

    const play = useCallback((dir) => {
        if (completion.celebration !== null || stuck) return;
        const res = move(board, dir);
        if (!res.moved) return;
        const nb = addTile(res.board);
        setBoard(nb);
        setMoves((m) => m + 1);
        playSynth('chime');
        if (nb.some((row) => row.some((v) => v >= goal))) {
            playSynth('fanfare');
            const total = moves + 1;
            completion.finish(total <= goal * 1.2 ? 3 : total <= goal * 2 ? 2 : 1);
        } else if (!canMove(nb)) {
            setStuck(true);
            playSynth('laser');
        }
    }, [board, completion, goal, moves, stuck]);

    useEffect(() => {
        const onKey = (e) => {
            const dir = { ArrowLeft: 'left', ArrowRight: 'right', ArrowUp: 'up', ArrowDown: 'down' }[e.key];
            if (dir) { e.preventDefault(); play(dir); }
        };
        window.addEventListener('keydown', onKey);
        return () => window.removeEventListener('keydown', onKey);
    }, [play]);

    const onTouchStart = (e) => { const t = e.touches[0]; touch.current = [t.clientX, t.clientY]; };
    const onTouchEnd = (e) => {
        if (!touch.current) return;
        const t = e.changedTouches[0];
        const dx = t.clientX - touch.current[0];
        const dy = t.clientY - touch.current[1];
        touch.current = null;
        if (Math.max(Math.abs(dx), Math.abs(dy)) < 24) return;
        play(Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'down' : 'up'));
    };

    return (
        <ActivityShell {...props} emoji="🔢" completion={completion}>
            <div className="wc-bubble-target">{lang === 'ru' ? 'Собери' : "Yig'"}: <b>{goal}</b> · {moves}</div>
            <div className="wc-merge" onTouchStart={onTouchStart} onTouchEnd={onTouchEnd}>
                {board.map((row, r) => row.map((v, c) => (
                    <div key={`${r}-${c}`} className={`wc-merge-cell ${v ? 'has' : ''}`} style={v ? { background: TILE_COLORS[v] || '#5c7cfa' } : undefined}>
                        {v || ''}
                    </div>
                )))}
            </div>
            {stuck ? (
                <button className="aa-option-btn" onClick={() => { setBoard(start()); setStuck(false); }}>
                    {lang === 'ru' ? 'Ещё раз' : 'Qayta boshlash'}
                </button>
            ) : (
                <div className="wc-pad">
                    <button onClick={() => play('up')}>⬆️</button>
                    <div>
                        <button onClick={() => play('left')}>⬅️</button>
                        <button onClick={() => play('down')}>⬇️</button>
                        <button onClick={() => play('right')}>➡️</button>
                    </div>
                </div>
            )}
        </ActivityShell>
    );
}
