import React from 'react';
import { render, screen } from '@testing-library/react';
import { levelContent, levelActivity, levelCountFor } from '../views/student/early-learning/levelContent';
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
        distractor_items: [item('d0', 'Mashina', '🚗'), item('d1', 'Kitob', '📕'), item('d2', 'Qalam', '✏️'),
            item('d3', 'Stul', '🪑'), item('d4', 'Soat', '⏰')],
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

// ---- final review fixes ----------------------------------------------------

test('select never borrows an item that is a right answer anywhere in the module', () => {
    // A module of colour games: a white cloud is a right answer in the "white" game,
    // so it must never come back as a wrong answer there (or anywhere it fits).
    const white = { mode: 'select', correct_items: [item('c0', 'Bulut', '☁️'), item('c1', 'Qor', '❄️')],
        distractor_items: [item('d0', 'Olma', '🍎')] };
    const siblings = [
        { mode: 'select', correct_items: [item('c0', 'Oq bulut', '☁️'), item('c1', 'Qor to\'pi', '⛄')],
            distractor_items: [item('d0', 'Mashina', '🚗'), item('d1', 'Bulutcha', '☁️')] },
        { mode: 'select', correct_items: [item('c0', 'Pomidor', '🍅')],
            distractor_items: [item('d0', 'Kit', '🐳'), item('d1', 'Pomidorcha', '🍅'), item('d2', 'Uy', '🏠')] },
    ];
    for (let seed = 0; seed < 20; seed += 1) {
        for (const level of [2, 3]) {
            const out = levelContent(white, level, siblings, seed);
            const borrowed = out.distractor_items.slice(1);
            const emojis = borrowed.map((x) => x.emoji);
            expect(emojis).not.toContain('☁️');
            expect(emojis).not.toContain('⛄');
            expect(emojis).not.toContain('🍅');
            expect(borrowed).toHaveLength(level === 2 ? 1 : 2);
            for (const x of borrowed) expect(['🚗', '🐳', '🏠']).toContain(x.emoji);
        }
    }
});

test('build and sequence never borrow a piece that looks like one of the game\'s own', () => {
    const build = { mode: 'build', slots: [item('s0', 'Tom', '🔺'), item('s1', 'Devor', '🧱')], distractor_items: [item('d0', 'Baliq', '🐟')] };
    const bsib = [{ mode: 'build', slots: [item('s0', 'Tom', '🔺')], distractor_items: [item('d0', 'Qizil tom', '🔺'), item('d1', 'Gul', '🌸')] }];
    const b3 = levelContent(build, 3, bsib);
    expect(b3.distractor_items.map((x) => x.emoji)).toEqual(['🐟', '🌸']);
    const seq = { mode: 'sequence', steps: [item('a', 'Uyg\'on', '⏰'), item('b', 'Yuvin', '🚿')] };
    const ssib = [{ mode: 'sequence', steps: [item('a', 'Turish', '⏰'), item('b', 'Uxla', '😴')] }];
    const s3 = levelContent(seq, 3, ssib);
    expect(s3.steps.filter((x) => x.distractor).map((x) => x.emoji)).toEqual(['😴']);
});

test('sort and hangman get harder at level 3 even with nothing to borrow', () => {
    const sort = { mode: 'sort', bins: [{ id: 'katta', label: 'Katta', emoji: '🐘' }],
        items: [{ id: 'i', bin: 'katta', label: 'Fil', emoji: '🐘' }] };
    expect(levelContent(sort, 2, []).hide_labels).toBeFalsy();
    expect(levelContent(sort, 3, []).hide_labels).toBe(true);
    expect(levelContent({ mode: 'hangman', words: [] }, 2, []).lives).toBe(5);
    expect(levelContent({ mode: 'hangman', words: [] }, 3, []).lives).toBe(4);
});

// ---- Active games (collect, connect, catch, dragsort): the select family ----

const familySiblings = () => ['collect', 'connect', 'catch', 'dragsort'].map((mode, i) => ({
    mode,
    correct_items: [item(`c${i}`, `Right${i}`, ['🦊', '🦁', '🐯', '🐻'][i])],
    distractor_items: [item(`d${i}`, `Wrong${i}`, ['🚀', '🎸', '🧲', '🪁'][i])],
}));

test('select levels still borrow distractors after the module is mixed', () => {
    const l2 = levelContent(select(), 2, familySiblings(), 1);
    expect(l2.distractor_items).toHaveLength(4);
    const l3 = levelContent(select(), 3, familySiblings(), 1);
    expect(l3.distractor_items).toHaveLength(6);
    for (const x of l3.distractor_items.slice(2)) expect(['🚀', '🎸', '🧲', '🪁']).toContain(x.emoji);
});

test('a right answer of any family game is never borrowed as a wrong one', () => {
    const sibs = [
        { mode: 'connect', correct_items: [item('c', 'Tulki', '🦊')], distractor_items: [] },
        { mode: 'select', correct_items: [], distractor_items: [item('d', 'Tulki', '🦊'), item('e', 'Raketa', '🚀')] },
    ];
    for (let seed = 0; seed < 10; seed += 1) {
        const l3 = levelContent(select(), 3, sibs, seed);
        const emojis = l3.distractor_items.map((x) => x.emoji);
        expect(emojis).not.toContain('🦊');
        expect(emojis).toContain('🚀');
    }
});

test('collect grows the grid and borrows distractors', () => {
    const base = { ...select(), mode: 'collect' };
    const l2 = levelContent(base, 2, familySiblings(), 3);
    expect(l2.grid_size).toBe(6);
    expect(l2.distractor_items).toHaveLength(4);
    const l3 = levelContent(base, 3, familySiblings(), 3);
    expect(l3.grid_size).toBe(7);
    expect(l3.distractor_items).toHaveLength(6);
    expect(levelContent(base, 1, familySiblings())).toBe(base);
});

test('connect borrows distractors and hides labels at level 3', () => {
    const base = { ...select(), mode: 'connect' };
    expect(levelContent(base, 2, familySiblings(), 2).distractor_items).toHaveLength(4);
    expect(levelContent(base, 2, familySiblings(), 2).hide_labels).toBeFalsy();
    expect(levelContent(base, 3, familySiblings(), 2).hide_labels).toBe(true);
});

test('catch falls faster each level', () => {
    const base = { ...select(), mode: 'catch' };
    expect(levelContent(base, 2, familySiblings()).fall_ms).toBe(4000);
    expect(levelContent(base, 3, familySiblings()).fall_ms).toBe(3300);
    expect(levelContent(base, 3, familySiblings()).distractor_items).toHaveLength(6);
});

test('dragsort level settings', () => {
    const base = { ...select(), mode: 'dragsort', partner: { character: { label: 'B' }, correct_items: [] } };
    const l2 = levelContent(base, 2, familySiblings());
    expect(l2.per_basket).toBeNull();
    expect(l2.use_partner2).toBe(false);
    expect(l2.distractor_items).toEqual(base.distractor_items);
    const l3 = levelContent(base, 3, familySiblings());
    expect(l3.per_basket).toBeNull();
    expect(l3.use_partner2).toBe(true);
});

test('new modes are leveled', () => {
    for (const mode of ['collect', 'connect', 'catch', 'dragsort']) expect(levelCountFor(mode)).toBe(3);
});
