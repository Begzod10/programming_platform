import React from 'react';
import { render, screen } from '@testing-library/react';
import { levelContent, levelActivity } from '../views/student/early-learning/levelContent';
import { starsForCoverage } from '../views/student/early-learning/earlyLearningUtils';
import MatchingActivity from '../views/student/early-learning/MatchingActivity';
import SequenceActivity from '../views/student/early-learning/SequenceActivity';
import translations from '../i18n/translations';

jest.mock('../api/search/base', () => ({
    useHttp: () => ({ request: jest.fn(() => Promise.resolve({})) }),
    API_URL: '/api/', API_URL_DOC: '/', headers: () => ({}),
}));
jest.mock('../utils/soundSynth', () => ({ playSynth: jest.fn(), playSoundAsset: jest.fn() }));
jest.mock('../views/student/early-learning/earlyVoice', () => ({
    cheer: jest.fn(() => true),
    cheerStars: jest.fn(() => true),
    playVoice: jest.fn(() => Promise.resolve(true)),
    stopVoice: jest.fn(),
    loadPhrases: jest.fn(() => Promise.resolve({})),
    currentLang: () => 'uz',
    isVoiceOn: () => true,
    setVoiceOn: jest.fn(),
}));

const t = (key) => translations.uz[key] || key;

const item = (id, label, emoji) => ({ id, label, emoji });
const select = () => ({
    mode: 'select',
    correct_items: [item('c0', 'Olma', '🍎'), item('c1', 'Nok', '🍐')],
    distractor_items: [item('d0', 'Mashina', '🚗'), item('d1', 'Uy', '🏠')],
});
const selectSiblings = () => [
    {
        mode: 'select',
        correct_items: [item('c0', 'Olma', '🍎'), item('c1', 'Mushuk', '🐱'), item('c2', 'It', '🐶')],
        distractor_items: [item('d0', 'Mashina', '🚗'), item('d1', 'Kitob', '📕'), item('d2', 'Qalam', '✏️')],
    },
    { mode: 'count', rounds: [{ emoji: '⭐', count: 3, options: [2, 3, 4] }] },
];

const EVERY_MODE = [
    select(),
    { mode: 'maze', grid: { rows: 4, cols: 4 }, start: [0, 0], end: [3, 3], walls: [[1, 1]] },
    { mode: 'count', rounds: [{ emoji: '⭐', count: 3, options: [2, 3, 4] }] },
    { mode: 'compare', max: 9 }, { mode: 'bubbles' }, { mode: 'arithmetic', operations: ['add'] },
    { mode: 'rounds', kind: 'clock', level: 'easy' },
    { mode: 'sort', bins: [{ id: 'f' }], items: [{ id: 'i', bin: 'f', label: 'a' }] },
    { mode: 'sequence', steps: [item('s1', 'a', '1'), item('s2', 'b', '2')] },
    { mode: 'pattern', rounds: [{ sequence: ['🔴', '🔵'], answer: '🔴', options: ['🔴', '🔵'] }] },
    { mode: 'cause_effect', rounds: [] }, { mode: 'build', slots: [], distractor_items: [] },
    { mode: 'trace', targets: [] }, { mode: 'pairs', cards: [] }, { mode: 'keyboard', keys: ['f'] },
    { mode: 'typing', words: ['olma'] }, { mode: 'wordbuild', words: [] }, { mode: 'hangman', words: [] },
    { mode: 'simon' }, { mode: 'merge' }, { mode: 'sudoku' }, { mode: 'chart' }, { mode: 'puzzle' },
    { character: { emoji: '🧺' }, correct_items: [], distractor_items: [] },
];

function pathExists({ grid, start, end, walls }) {
    const wall = new Set(walls.map(([r, c]) => `${r},${c}`));
    const seen = new Set([`${start[0]},${start[1]}`]);
    const queue = [start];
    while (queue.length) {
        const [r, c] = queue.shift();
        if (r === end[0] && c === end[1]) return true;
        for (const [dr, dc] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
            const nr = r + dr; const nc = c + dc; const k = `${nr},${nc}`;
            if (nr < 0 || nc < 0 || nr >= grid.rows || nc >= grid.cols || wall.has(k) || seen.has(k)) continue;
            seen.add(k); queue.push([nr, nc]);
        }
    }
    return false;
}

test('level 1 returns the content unchanged for every mode', () => {
    for (const content of EVERY_MODE) {
        expect(levelContent(content, 1, selectSiblings())).toBe(content);
    }
});

test('select doubles then triples distractors from siblings and hides labels at level 3', () => {
    const l2 = levelContent(select(), 2, selectSiblings());
    expect(l2.distractor_items).toHaveLength(4);
    expect(l2.hide_labels).toBeFalsy();
    const l3 = levelContent(select(), 3, selectSiblings());
    expect(l3.distractor_items).toHaveLength(6);
    expect(l3.hide_labels).toBe(true);
    expect(l3.correct_items).toEqual(select().correct_items);
});

test('select never adds a correct item as a distractor and never duplicates', () => {
    for (let seed = 0; seed < 20; seed += 1) {
        const l3 = levelContent(select(), 3, selectSiblings(), seed);
        const labels = l3.distractor_items.map((x) => x.label);
        expect(new Set(labels).size).toBe(labels.length);
        expect(labels).not.toContain('Olma');
        expect(labels).not.toContain('Nok');
        const ids = [...l3.correct_items, ...l3.distractor_items].map((x) => x.id);
        expect(new Set(ids).size).toBe(ids.length);
    }
});

test('maze grows and always keeps a path from start to end', () => {
    for (let seed = 0; seed < 50; seed += 1) {
        const base = { mode: 'maze', grid: { rows: 3 + (seed % 3), cols: 4 }, start: [0, 0], end: [2, 3],
            walls: [[0, 1], [1, 1], [1, 2]] };
        for (const level of [2, 3]) {
            const out = levelContent(base, level, [], seed);
            const grow = 2 * (level - 1);
            expect(out.grid.rows).toBe(Math.min(9, base.grid.rows + grow));
            expect(out.grid.cols).toBe(Math.min(9, base.grid.cols + grow));
            expect(out.end).toEqual([out.grid.rows - 1, out.grid.cols - 1]);
            expect(out.walls.length).toBeGreaterThan(base.walls.length);
            expect(pathExists(out)).toBe(true);
            for (const [r, c] of out.walls) {
                expect(r < out.grid.rows && c < out.grid.cols).toBe(true);
                expect(`${r},${c}`).not.toBe(`${out.end[0]},${out.end[1]}`);
                expect(`${r},${c}`).not.toBe('0,0');
            }
        }
    }
});

test('count adds wrong options without repeating the right count', () => {
    const base = { mode: 'count', rounds: [{ emoji: '⭐', count: 3, options: [2, 3, 4] }] };
    const sib = [{ mode: 'count', rounds: [{ emoji: '🍎', count: 5, options: [4, 5, 6] },
        { emoji: '🐟', count: 2, options: [1, 2, 3] }, { emoji: '⭐', count: 3, options: [3, 4] }] }];
    const l2 = levelContent(base, 2, sib);
    expect(l2.rounds).toHaveLength(3);
    const l3 = levelContent(base, 3, sib);
    expect(l3.rounds).toHaveLength(3); // only two new rounds exist to borrow
    for (const [level, out] of [[2, l2], [3, l3]]) {
        for (const round of out.rounds) {
            const extra = 2 * (level - 1);
            expect(round.options.filter((n) => n === round.count)).toHaveLength(1);
            expect(new Set(round.options).size).toBe(round.options.length);
            expect(round.options.every((n) => n >= 1 && n <= 10)).toBe(true);
            expect(round.options.length).toBeGreaterThanOrEqual(3 + extra - 1);
        }
        expect(out.rounds[0].options).toHaveLength(3 + 2 * (level - 1));
    }
});

test('merge goal 64 → 128 → 256; sudoku blanks capped at 10', () => {
    expect(levelContent({ mode: 'merge' }, 2, []).goal).toBe(128);
    expect(levelContent({ mode: 'merge', goal: 64 }, 3, []).goal).toBe(256);
    expect(levelContent({ mode: 'sudoku' }, 2, []).blanks).toBe(8);
    expect(levelContent({ mode: 'sudoku', blanks: 9 }, 3, []).blanks).toBe(10);
});

test('content with nothing to borrow still works at level 3', () => {
    for (const content of EVERY_MODE) {
        const out = levelContent(content, 3, []);
        expect(out).toBeTruthy();
        expect(out.mode).toBe(content.mode);
    }
    const count = levelContent({ mode: 'count', rounds: [{ emoji: '⭐', count: 3, options: [3] }] }, 3, []);
    expect(count.rounds).toHaveLength(1);
    expect(count.rounds[0].options).toHaveLength(5);
    const seq = levelContent({ mode: 'sequence', steps: [item('s1', 'a', '1')] }, 3, []);
    expect(seq.steps).toHaveLength(1);
    const sel = levelContent(select(), 3, []);
    expect(sel.distractor_items).toHaveLength(2);
    expect(levelContent({ mode: 'arithmetic' }, 3, []).max).toBe(30);
    expect(levelContent({ mode: 'arithmetic', operations: ['add'] }, 2, []).operations).toEqual(['add', 'subtract']);
});

test('input content object is not mutated', () => {
    const contents = [...EVERY_MODE.map((c) => JSON.parse(JSON.stringify(c)))];
    const siblings = selectSiblings();
    const before = JSON.stringify([contents, siblings]);
    for (const c of contents) {
        levelContent(c, 2, siblings);
        levelContent(c, 3, siblings);
    }
    expect(JSON.stringify([contents, siblings])).toBe(before);
});

test('levelActivity carries the level and the harder content', () => {
    const activity = { id: 3, title: 'x', content: { mode: 'merge' } };
    const out = levelActivity(activity, 2, []);
    expect(out.level).toBe(2);
    expect(out.content.goal).toBe(128);
    expect(activity.level).toBeUndefined();
    expect(levelActivity(activity, 1, []).content).toBe(activity.content);
});

test('starsForCoverage is stricter at higher levels', () => {
    expect(starsForCoverage(0.88)).toBe(3);
    expect(starsForCoverage(0.88, 1)).toBe(3);
    expect(starsForCoverage(0.88, 2)).toBe(2);
    expect(starsForCoverage(0.92, 3)).toBe(2);
    expect(starsForCoverage(0.95, 3)).toBe(3);
    expect(starsForCoverage(0.7, 3)).toBe(1);
});

test('MatchingActivity hides item labels when hide_labels is set', () => {
    const base = { onBack: jest.fn(), onComplete: jest.fn(), lang: 'uz', toggleLang: jest.fn(), t };
    const content = select();
    const { unmount } = render(<MatchingActivity activity={{ id: 1, title: 'M', content }} {...base} />);
    expect(screen.getByText('Mashina')).toBeInTheDocument();
    unmount();
    render(<MatchingActivity activity={{ id: 1, title: 'M', content: { ...content, hide_labels: true } }} {...base} />);
    expect(screen.queryByText('Mashina')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Mashina' })).toBeInTheDocument();
});

test('SequenceActivity shows distractor steps in the tray but not as slots', () => {
    const base = { onBack: jest.fn(), onComplete: jest.fn(), lang: 'uz', toggleLang: jest.fn(), t };
    const { container } = render(<SequenceActivity activity={{ id: 1, title: 'S', content: {
        mode: 'sequence',
        steps: [item('s1', 'Uyg\'on', '⏰'), item('s2', 'Yuvin', '🚿'), { ...item('x', 'Uxla', '😴'), distractor: true }],
    } }} {...base} />);
    expect(container.querySelectorAll('.sq-slot')).toHaveLength(2);
    expect(container.querySelectorAll('.sq-item')).toHaveLength(3);
});
