import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import CollectActivity from '../views/student/early-learning/CollectActivity';
import ConnectActivity from '../views/student/early-learning/ConnectActivity';
import CatchActivity from '../views/student/early-learning/CatchActivity';
import DragSortActivity from '../views/student/early-learning/DragSortActivity';
import { stepFalling } from '../views/student/early-learning/catchGame';
import { makeBaskets } from '../views/student/early-learning/dragsortSetup';
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

// ---- catch ----

const piece = (id, ok) => ({ key: id, item: item(id, id, '🙂'), ok });
const fallState = (over) => ({
    queue: [], falling: [], fallMs: 1000, basketLane: 1, spawned: 0, caught: 0, ...over,
});

test('stepFalling: a missed right item goes back to the queue, a missed wrong one is dropped', () => {
    const s0 = fallState({
        queue: [piece('q', true)],
        falling: [{ id: 1, piece: piece('r', true), lane: 0, y: 0.95 }, { id: 2, piece: piece('w', false), lane: 2, y: 0.95 }],
    });
    const s1 = stepFalling(s0, 100);
    expect(s1.falling.map((f) => f.piece.key)).not.toContain('r');
    expect(s1.falling.map((f) => f.piece.key)).not.toContain('w');
    expect(s1.queue.map((p) => p.key)).toEqual(['q', 'r'].filter((k) => !s1.falling.some((f) => f.piece.key === k)));
    expect([...s1.queue, ...s1.falling.map((f) => f.piece)].map((p) => p.key).sort()).toEqual(['q', 'r']);
    expect(s1.events.map((e) => e.type).sort()).toEqual(['missed', 'missed']);
    expect(s0.falling).toHaveLength(2); // pure
});

test('stepFalling: the basket lane catches; at most two items fall at once; speed follows fallMs', () => {
    const s = stepFalling(fallState({
        falling: [{ id: 1, piece: piece('r', true), lane: 1, y: 0.99 }, { id: 2, piece: piece('w', false), lane: 1, y: 0.2 }],
        queue: [piece('a', true), piece('b', true)],
    }), 50);
    expect(s.events).toEqual([{ type: 'caught', piece: piece('r', true) }]);
    expect(s.caught).toBe(1);
    let t = fallState({ queue: [piece('a', true), piece('b', true), piece('c', true), piece('d', true)], basketLane: 5 });
    for (let i = 0; i < 40; i += 1) {
        t = stepFalling(t, 50);
        expect(t.falling.length).toBeLessThanOrEqual(2);
    }
    const one = stepFalling(fallState({ falling: [{ id: 1, piece: piece('r', true), lane: 0, y: 0 }] }), 250);
    expect(one.falling[0].y).toBeCloseTo(0.25);
    const caughtWrong = stepFalling(fallState({ falling: [{ id: 1, piece: piece('w', false), lane: 1, y: 0.99 }] }), 50);
    expect(caughtWrong.events).toEqual([{ type: 'mistake', piece: piece('w', false) }]);
});

function playCatch(container) {
    // Always put the basket under the lowest falling item: every item gets caught.
    for (let i = 0; i < 400 && !voice.cheerStars.mock.calls.length; i += 1) {
        const falling = [...container.querySelectorAll('.ag-fall')];
        if (falling.length) {
            const lowest = falling.reduce((a, b) => (Number(a.dataset.y) > Number(b.dataset.y) ? a : b));
            fireEvent.click(screen.getByRole('button', { name: `${t('el.lane')} ${Number(lowest.dataset.lane) + 1}` }));
        }
        act(() => { jest.advanceTimersByTime(50); });
    }
}

test('catch: catching a right item collects it, a wrong one is a mistake, finishes when all right items are caught', () => {
    jest.useFakeTimers();
    const { container } = render(<CatchActivity activity={game('catch', { fall_ms: 1000 })} {...base} />);
    playCatch(container);
    expect(voice.cheer.mock.calls.filter(([k]) => k === 'correct')).toHaveLength(2);
    expect(voice.cheer.mock.calls.filter(([k]) => k === 'wrong').length).toBeLessThanOrEqual(1);
    const mistakes = voice.cheer.mock.calls.filter(([k]) => k === 'wrong').length;
    expect(voice.cheerStars).toHaveBeenCalledWith(mistakes ? 2 : 3);
    jest.useRealTimers();
});

test('catch: keyboard arrows move the basket', () => {
    jest.useFakeTimers();
    const { container } = render(<CatchActivity activity={game('catch')} {...base} />);
    expect(container.querySelector('.ag-basket').dataset.lane).toBe('1');
    fireEvent.keyDown(window, { key: 'ArrowLeft' });
    expect(container.querySelector('.ag-basket').dataset.lane).toBe('0');
    fireEvent.keyDown(window, { key: 'ArrowLeft' });
    expect(container.querySelector('.ag-basket').dataset.lane).toBe('0');
    fireEvent.keyDown(window, { key: 'ArrowRight' });
    fireEvent.keyDown(window, { key: 'ArrowRight' });
    expect(container.querySelector('.ag-basket').dataset.lane).toBe('2');
    jest.useRealTimers();
});

// ---- dragsort ----

const named = (p, n, emojis) => Array.from({ length: n }, (_, i) => item(`${p}${i}`, `${p}${i}`, emojis[i]));
const sortContent = (over = {}) => ({
    mode: 'dragsort',
    character: { emoji: '👨‍🍳', label: 'Oshpaz' },
    correct_items: [...named('osh', 4, ['🍲', '🥄', '🔪', '🍳']), item('shared', 'Xalat', '🥼')],
    distractor_items: [],
    partner: { character: { emoji: '👩‍⚕️', label: 'Shifokor' }, correct_items: [...named('vrach', 4, ['💉', '💊', '🩺', '🩹']), item('s2', 'Oq xalat', '🥼')] },
    partner2: { character: { emoji: '👨‍✈️', label: 'Uchuvchi' }, correct_items: named('uch', 3, ['✈️', '🧭', '🛫']) },
    ...over,
});

test('makeBaskets drops shared pictures and picks 3 per basket at level 1, all at level 2, three baskets at level 3', () => {
    const l1 = makeBaskets(sortContent(), 1);
    expect(l1.baskets.map((b) => b.character.label)).toEqual(['Oshpaz', 'Shifokor']);
    expect(l1.baskets.map((b) => b.items.length)).toEqual([3, 3]);
    expect(l1.pieces).toHaveLength(6);
    const emojis = l1.pieces.map((p) => p.item.emoji);
    expect(emojis).not.toContain('🥼');
    const l2 = makeBaskets({ ...sortContent(), per_basket: null, use_partner2: false }, 2);
    expect(l2.baskets.map((b) => b.items.length)).toEqual([4, 4]);
    expect(l2.pieces.every((p) => l2.baskets[p.basket].items.includes(p.item))).toBe(true);
    const l3 = makeBaskets({ ...sortContent(), per_basket: null, use_partner2: true }, 3);
    expect(l3.baskets.map((b) => b.character.label)).toEqual(['Oshpaz', 'Shifokor', 'Uchuvchi']);
    expect(l3.pieces).toHaveLength(11);
    // same name in two baskets is dropped too
    const byName = makeBaskets(sortContent({ partner: { character: { label: 'B' }, correct_items: [item('z', 'osh0', '🧪'), ...named('v', 3, ['💉', '💊', '🩺'])] } }), 2);
    expect(byName.pieces.map((p) => p.item.label)).not.toContain('osh0');
});

test('makeBaskets returns null without a partner or with fewer than 2 pieces in a basket', () => {
    expect(makeBaskets(sortContent({ partner: undefined }), 1)).toBeNull();
    expect(makeBaskets(sortContent({ partner: { correct_items: [] } }), 1)).toBeNull();
    const thin = { character: { label: 'B' }, correct_items: [item('a', 'Xalat', '🥼'), item('b', 'Igna', '🪡')] };
    expect(makeBaskets(sortContent({ partner: thin }), 2)).toBeNull();
    // a thin third basket does not spoil level 3: it plays with two baskets
    const l3 = makeBaskets(sortContent({ partner2: thin, use_partner2: true }), 3);
    expect(l3.baskets).toHaveLength(2);
});

function mockBasketRects() {
    return jest.spyOn(Element.prototype, 'getBoundingClientRect').mockImplementation(function () {
        const i = this.dataset?.basket;
        if (i !== undefined) return rect(Number(i) * 150, 0, 140, 100);
        return rect(0, 300, 60, 60);
    });
}

function dropOn(label, x, y) {
    const from = screen.getByRole('button', { name: label });
    fireEvent.pointerDown(from, { clientX: 30, clientY: 330, pointerId: 1 });
    fireEvent.pointerMove(from, { clientX: x, clientY: y, pointerId: 1 });
    fireEvent.pointerUp(from, { clientX: x, clientY: y, pointerId: 1 });
}

test('dragsort: a piece dropped on the wrong basket returns and counts a mistake', () => {
    const spy = mockBasketRects();
    const { container } = render(<DragSortActivity activity={{ ...game('dragsort'), content: sortContent() }} {...base} />);
    dropOn('osh0', 200, 50); // Shifokor's basket
    expect(voice.cheer).toHaveBeenLastCalledWith('wrong');
    expect(screen.getByRole('button', { name: 'osh0' })).toBeInTheDocument();
    dropOn('osh0', 50, 50);
    expect(voice.cheer).toHaveBeenLastCalledWith('correct');
    expect(container.querySelectorAll('.ag-basket-drop')[0]).toHaveTextContent('🍲');
    dropOn('vrach0', 600, 50); // nowhere: no mistake
    expect(voice.cheer).toHaveBeenCalledTimes(2);
    for (const label of ['osh1', 'osh2']) dropOn(label, 50, 50);
    for (const label of ['vrach0', 'vrach1', 'vrach2']) dropOn(label, 200, 50);
    expect(voice.cheerStars).toHaveBeenCalledWith(2);
    spy.mockRestore();
});

test('dragsort: tapping a piece and then a basket places it too', () => {
    render(<DragSortActivity activity={{ ...game('dragsort'), content: sortContent() }} {...base} />);
    fireEvent.click(screen.getByRole('button', { name: 'osh0' }));
    fireEvent.click(screen.getByRole('button', { name: 'Oshpaz' }));
    expect(voice.cheer).toHaveBeenLastCalledWith('correct');
});
