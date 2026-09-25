import React, { useMemo, useState } from 'react';
import './WordChartActivity.css';
import ActivityShell, { useActivityCompletion } from './ActivityShell';
import { playSynth } from '../../../utils/soundSynth';
import { shuffle, starsForWrongCount, WRONG_FLASH_MS } from './earlyLearningUtils';

// A valid 4x4 solution (2x2 boxes); shuffling digits, rows-in-band and
// columns-in-stack keeps it valid, so every game is a fresh puzzle.
const BASE = [[1, 2, 3, 4], [3, 4, 1, 2], [2, 3, 4, 1], [4, 1, 2, 3]];

function makePuzzle(blanks) {
    const digits = shuffle([1, 2, 3, 4]);
    const rowOrder = [...shuffle([0, 1]), ...shuffle([2, 3])];
    const colOrder = [...shuffle([0, 1]), ...shuffle([2, 3])];
    const solution = rowOrder.map((r) => colOrder.map((c) => digits[BASE[r][c] - 1]));
    const hidden = new Set(shuffle(Array.from({ length: 16 }, (_, i) => i)).slice(0, blanks));
    const cells = solution.flat().map((v, i) => (hidden.has(i) ? 0 : v));
    return { solution: solution.flat(), cells };
}

/** 4x4 Sudoku. activity.content (mode: "sudoku"): { blanks?: 6 }. Pick a
 * cell, pick a digit; a wrong digit is refused and counts a mistake. */
export default function SudokuActivity(props) {
    const { activity, guest, onComplete } = props;
    const blanks = (activity.content || {}).blanks || 6;
    const completion = useActivityCompletion(activity, guest, onComplete);
    const puzzle = useMemo(() => makePuzzle(blanks), [activity.id, blanks]); // eslint-disable-line react-hooks/exhaustive-deps
    const [cells, setCells] = useState(puzzle.cells);
    const [sel, setSel] = useState(null);
    const [wrongCount, setWrongCount] = useState(0);
    const [flash, setFlash] = useState(null);

    const put = (d) => {
        if (sel === null || completion.celebration !== null) return;
        if (puzzle.solution[sel] === d) {
            playSynth('chime');
            const next = cells.map((v, i) => (i === sel ? d : v));
            setCells(next);
            setSel(null);
            if (next.every((v, i) => v === puzzle.solution[i])) {
                playSynth('fanfare');
                completion.finish(starsForWrongCount(wrongCount));
            }
        } else {
            playSynth('laser');
            setWrongCount((c) => c + 1);
            const token = Date.now();
            setFlash({ token, i: sel });
            setTimeout(() => setFlash((f) => (f?.token === token ? null : f)), WRONG_FLASH_MS / 2);
        }
    };

    return (
        <ActivityShell {...props} emoji="🧮" completion={completion}>
            <div className="wc-sudoku">
                {cells.map((v, i) => (
                    <button
                        key={i}
                        className={`wc-sudoku-cell ${puzzle.cells[i] ? 'is-given' : ''} ${sel === i ? 'is-sel' : ''} ${flash?.i === i ? 'is-wrong' : ''} ${i % 4 === 1 ? 'box-r' : ''} ${Math.floor(i / 4) === 1 ? 'box-b' : ''}`}
                        onClick={() => !puzzle.cells[i] && !v && setSel(i)}
                    >
                        {v || ''}
                    </button>
                ))}
            </div>
            <div className="wc-numpad">
                {[1, 2, 3, 4].map((d) => (
                    <button key={d} className="aa-option-btn" disabled={sel === null || completion.submitting} onClick={() => put(d)}>{d}</button>
                ))}
            </div>
        </ActivityShell>
    );
}
