import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import CollectActivity from '../views/student/early-learning/CollectActivity';
import ConnectActivity from '../views/student/early-learning/ConnectActivity';
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
// Component tests pin the board; the makeBoard tests use the real one.
jest.mock('../views/student/early-learning/collectBoard', () => {
    const actual = jest.requireActual('../views/student/early-learning/collectBoard');
    return { ...actual, makeBoard: jest.fn(actual.makeBoard) };
});

const voice = require('../views/student/early-learning/earlyVoice');
const board = require('../views/student/early-learning/collectBoard');
const { makeBoard } = jest.requireActual('../views/student/early-learning/collectBoard');

const t = (key) => translations.uz[key] || key;
const base = { onBack: jest.fn(), onComplete: jest.fn(), lang: 'uz', toggleLang: jest.fn(), t, guest: true };

const item = (id, label, emoji) => ({ id, label, emoji });
const right = [item('a', 'Olma', '🍎'), item('b', 'Nok', '🍐')];
const wrong = [item('x', 'Mashina', '🚗')];
const game = (mode, over = {}) => ({
    id: 41, title: 'Savat', level: 1, instruction_text: 'Yig\'.',
    content: { mode, character: { emoji: '🧺', label: 'Savat' }, correct_items: right, distractor_items: wrong, ...over },
});

// jsdom has no PointerEvent: without one, fireEvent.pointer* drops clientX/Y.
if (!window.PointerEvent) {
    window.PointerEvent = class PointerEvent extends MouseEvent {
        constructor(type, init = {}) {
            super(type, init);
            this.pointerId = init.pointerId ?? 1;
            this.pointerType = init.pointerType || 'mouse';
        }
    };
}

beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
});

// ---- collect ----

function reachable({ size, start, walls }, blocked) {
    const block = new Set([...walls.map(([r, c]) => `${r},${c}`), ...blocked]);
    const seen = new Set([`${start[0]},${start[1]}`]);
    const queue = [start];
    while (queue.length) {
        const [r, c] = queue.shift();
        for (const [dr, dc] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
            const k = `${r + dr},${c + dc}`;
            if (r + dr < 0 || c + dc < 0 || r + dr >= size || c + dc >= size || block.has(k) || seen.has(k)) continue;
            seen.add(k);
            queue.push([r + dr, c + dc]);
        }
    }
    return seen;
}

test('makeBoard always leaves a path to every right item (200 seeds)', () => {
    const many = (n, p) => Array.from({ length: n }, (_, i) => item(`${p}${i}`, `${p}${i}`, '🙂'));
    for (const [size, nRight, nWrong] of [[5, 6, 4], [6, 6, 8], [7, 6, 12], [5, 2, 4]]) {
        for (let seed = 0; seed < 200; seed += 1) {
            const b = makeBoard({ grid_size: size === 5 ? undefined : size, correct_items: many(nRight, 'r'), distractor_items: many(nWrong, 'w') }, seed);
            expect(b.size).toBe(size);
            expect(b.start).toEqual([0, 0]);
            const cells = b.items.map(({ r, c }) => `${r},${c}`);
            expect(new Set(cells).size).toBe(cells.length);
            expect(cells).not.toContain('0,0');
            const wallSet = new Set(b.walls.map(([r, c]) => `${r},${c}`));
            for (const k of cells) expect(wallSet.has(k)).toBe(false);
            expect(b.items.filter((x) => x.ok)).toHaveLength(nRight);
            expect(b.items.filter((x) => !x.ok).length).toBeGreaterThan(0);
            const open = reachable(b, b.items.filter((x) => !x.ok).map(({ r, c }) => `${r},${c}`));
            for (const x of b.items.filter((y) => y.ok)) expect(open.has(`${x.r},${x.c}`)).toBe(true);
            expect(b.walls.length).toBeGreaterThan(0);
        }
    }
});

test('makeBoard is the same for the same seed', () => {
    const content = { correct_items: right, distractor_items: wrong };
    expect(makeBoard(content, 9)).toEqual(makeBoard(content, 9));
});

const PINNED = {
    size: 3, start: [0, 0], walls: [[1, 0]],
    items: [
        { r: 0, c: 1, item: right[0], ok: true },
        { r: 0, c: 2, item: wrong[0], ok: false },
        { r: 1, c: 1, item: right[1], ok: true },
    ],
};

const key = (k) => fireEvent.keyDown(window, { key: k });

test('collect: walking onto a right item collects it, onto a wrong one counts a mistake', () => {
    board.makeBoard.mockReturnValue(PINNED);
    const { container } = render(<CollectActivity activity={game('collect')} {...base} />);
    key('ArrowRight');
    expect(voice.cheer).toHaveBeenLastCalledWith('correct');
    expect(container.querySelectorAll('.ag-cell-collected')).toHaveLength(1);
    key('ArrowRight');
    expect(voice.cheer).toHaveBeenLastCalledWith('wrong');
    // the hero did not step onto the wrong item
    expect(container.querySelector('.ag-hero').dataset.pos).toBe('0,1');
    expect(container.querySelector('.ag-shake')).not.toBeNull();
});

test('collect: walls stop the walk without a mistake', () => {
    board.makeBoard.mockReturnValue(PINNED);
    const { container } = render(<CollectActivity activity={game('collect')} {...base} />);
    key('ArrowDown'); // wall
    key('ArrowUp'); // edge
    key('ArrowLeft'); // edge
    expect(voice.cheer).not.toHaveBeenCalled();
    expect(container.querySelector('.ag-hero').dataset.pos).toBe('0,0');
});

test('collect: arrow buttons and a swipe move the hero too', () => {
    board.makeBoard.mockReturnValue(PINNED);
    const { container } = render(<CollectActivity activity={game('collect')} {...base} />);
    fireEvent.click(screen.getByRole('button', { name: t('el.moveRight') }));
    expect(container.querySelector('.ag-hero').dataset.pos).toBe('0,1');
    const field = container.querySelector('.ag-board');
    fireEvent.pointerDown(field, { clientX: 100, clientY: 50 });
    fireEvent.pointerUp(field, { clientX: 102, clientY: 110 });
    expect(container.querySelector('.ag-hero').dataset.pos).toBe('1,1');
    // a short drag is not a swipe
    fireEvent.pointerDown(field, { clientX: 100, clientY: 50 });
    fireEvent.pointerUp(field, { clientX: 110, clientY: 55 });
    expect(container.querySelector('.ag-hero').dataset.pos).toBe('1,1');
});

test('collect finishes with stars by mistakes', () => {
    board.makeBoard.mockReturnValue(PINNED);
    render(<CollectActivity activity={game('collect')} {...base} />);
    key('ArrowRight'); // Olma
    key('ArrowRight'); // Mashina: mistake
    key('ArrowDown'); // Nok: last right item
    expect(voice.cheerStars).toHaveBeenCalledWith(2);
});

test('collect builds its board from the level content and seed', () => {
    board.makeBoard.mockReturnValue(PINNED);
    render(<CollectActivity activity={{ ...game('collect', { grid_size: 6 }), level: 2 }} {...base} />);
    const [content, seed] = board.makeBoard.mock.calls[0];
    expect(content.grid_size).toBe(6);
    expect(typeof seed).toBe('number');
});

// ---- connect ----

const rect = (left, top, width, height) => ({ left, top, width, height, right: left + width, bottom: top + height, x: left, y: top });

function mockRects() {
    return jest.spyOn(Element.prototype, 'getBoundingClientRect').mockImplementation(function () {
        if (this.classList.contains('ag-connect-target')) return rect(300, 0, 100, 300);
        if (this.classList.contains('ag-connect')) return rect(0, 0, 400, 300);
        return rect(10, 10, 60, 40);
    });
}

function drag(container, label, x, y) {
    const from = screen.getByRole('button', { name: label });
    const field = container.querySelector('.ag-connect');
    fireEvent.pointerDown(from, { clientX: 40, clientY: 30, pointerId: 1 });
    fireEvent.pointerMove(field, { clientX: x, clientY: y, pointerId: 1 });
    fireEvent.pointerUp(field, { clientX: x, clientY: y, pointerId: 1 });
}

test('connect: line to the character from a right item stays, from a wrong one is a mistake', () => {
    const spy = mockRects();
    const { container } = render(<ConnectActivity activity={game('connect')} {...base} />);
    drag(container, 'Olma', 350, 100);
    expect(voice.cheer).toHaveBeenLastCalledWith('correct');
    expect(container.querySelectorAll('.ag-line-done')).toHaveLength(1);
    drag(container, 'Mashina', 350, 100);
    expect(voice.cheer).toHaveBeenLastCalledWith('wrong');
    expect(container.querySelectorAll('.ag-line-done')).toHaveLength(1);
    drag(container, 'Nok', 340, 200);
    expect(voice.cheerStars).toHaveBeenCalledWith(2);
    spy.mockRestore();
});

test('connect: releasing away from the character is not a mistake', () => {
    const spy = mockRects();
    const { container } = render(<ConnectActivity activity={game('connect')} {...base} />);
    drag(container, 'Mashina', 150, 100);
    drag(container, 'Olma', 150, 100);
    expect(voice.cheer).not.toHaveBeenCalled();
    expect(container.querySelectorAll('.ag-line-done')).toHaveLength(0);
    expect(container.querySelector('.ag-connect').style.touchAction).toBe('none');
    spy.mockRestore();
});

test('connect: tapping an item and then the character connects it too', () => {
    const { container } = render(<ConnectActivity activity={game('connect')} {...base} />);
    fireEvent.click(screen.getByRole('button', { name: 'Olma' }));
    fireEvent.click(container.querySelector('.ag-connect-target'));
    expect(voice.cheer).toHaveBeenLastCalledWith('correct');
});

test('connect hides labels at level 3', () => {
    render(<ConnectActivity activity={game('connect', { hide_labels: true })} {...base} />);
    expect(screen.queryByText('Olma')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Olma' })).toBeInTheDocument();
});
