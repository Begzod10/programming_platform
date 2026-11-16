/* Game levels 2 and 3: a harder version of an activity's own content,
 * built in the browser so no new content has to be written.
 *
 * levelContent(content, level, siblings, seed) returns a NEW object (the
 * input is never touched). Level 1 returns the input itself. `siblings` are
 * the other activities' contents of the same module; extra items are only
 * borrowed from siblings of the same mode (or, for the select family —
 * select and the active games built from select content — of any family
 * mode). Randomness is seeded (activity
 * id + level), so the same level of the same game looks the same every
 * time it is built — e.g. after a language switch re-fetches the module,
 * the maze walls do not move under the kid's character.
 */

const HOME_ROW = 'asdfghjkl'.split('');
/** How long one catch item takes to cross the field, per level (ms). */
export const CATCH_FALL_MS = [5000, 4000, 3300];
const MAZE_MAX = 9;

export function rng(seed) {
    // mulberry32
    let a = (seed >>> 0) || 1;
    return () => {
        a = (a + 0x6D2B79F5) >>> 0;
        let x = a;
        x = Math.imul(x ^ (x >>> 15), x | 1);
        x ^= x + Math.imul(x ^ (x >>> 7), x | 61);
        return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
    };
}

export function shuffled(list, rand) {
    const out = [...list];
    for (let i = out.length - 1; i > 0; i -= 1) {
        const j = Math.floor(rand() * (i + 1));
        [out[i], out[j]] = [out[j], out[i]];
    }
    return out;
}

/** What makes two items "the same thing" across activities: ids are only
 * unique inside one activity, so compare what the kid sees. */
function itemKey(x) {
    if (x == null) return '';
    if (typeof x !== 'object') return String(x).toLowerCase();
    return String(x.label || x.uz || x.emoji || x.icon || x.id || JSON.stringify(x)).toLowerCase();
}

/** select and the active games that play select content another way
 * (no mode = select). Their items are one pool: a module mixed by
 * scripts/convert_select_modules.py keeps borrowing as before. */
export const SELECT_FAMILY = new Set(['select', 'collect', 'connect', 'catch', 'dragsort']);

/** Does sibling `sib` count as the same kind of game as `mode`? */
function sameKind(sib, mode) {
    if (SELECT_FAMILY.has(mode)) return SELECT_FAMILY.has(sib.mode || 'select');
    return sib.mode === mode;
}

/** Items under `key` in same-mode siblings, without repeats and without
 * anything whose key is in `exclude` (a Set of itemKey values). */
function pool(siblings, mode, key, exclude) {
    const seen = new Set(exclude);
    const out = [];
    for (const sib of siblings || []) {
        if (!sib || !sameKind(sib, mode) || !Array.isArray(sib[key])) continue;
        for (const x of sib[key]) {
            const k = itemKey(x);
            if (!k || seen.has(k)) continue;
            seen.add(k);
            out.push(x);
        }
    }
    return out;
}

const keysOf = (...lists) => new Set(lists.flat().filter(Boolean).map(itemKey));

/** A borrowed item gets a fresh id so it can never collide with (or be
 * mistaken for) one of this game's own items. */
const borrow = (x, level, i) => (x && typeof x === 'object' ? { ...x, id: `lv${level}-${i}-${x.id ?? ''}` } : x);

function take(list, n) {
    return n > 0 ? list.slice(0, n) : [];
}

/** Pictures (emoji / icon) of a list — a borrowed item that looks like one
 * of these would be the same picture as a game's own piece. */
const picturesOf = (...lists) => new Set(lists.flat().filter(Boolean).flatMap((x) => [x.emoji, x.icon]).filter(Boolean));

/** Drop borrowed items whose name or picture matches anything in `lists`. */
function unlike(items, ...lists) {
    const names = keysOf(...lists);
    const pics = picturesOf(...lists);
    return items.filter((x) => !names.has(itemKey(x)) && !(x.emoji && pics.has(x.emoji)) && !(x.icon && pics.has(x.icon)));
}

function harderSelect(c, level, m, siblings, rand) {
    const correct = c.correct_items || [];
    const distractors = c.distractor_items || [];
    const base = distractors.length || correct.length;
    const want = base * m;
    const mode = c.mode || 'select';
    // Only things that are a wrong answer everywhere in the module: games of
    // one module share a theme, so another game's right answer (or the same
    // picture under another name — a "white cloud" next to this game's
    // "cloud") would very likely be right here too.
    const rightAnywhere = (siblings || [])
        .filter((s) => s && sameKind(s, mode))
        .flatMap((s) => s.correct_items || []);
    const fromD = unlike(pool(siblings, mode, 'distractor_items', keysOf(correct, distractors)),
        correct, distractors, rightAnywhere);
    const extra = shuffled(fromD, rand).slice(0, want).map((x, i) => borrow(x, level, i));
    const out = { ...c, distractor_items: [...distractors, ...extra] };
    const all = [...correct, ...out.distractor_items];
    // Pictures only — but never for a game whose items have nothing to show.
    if (level === 3 && all.length && all.every((x) => x && (x.emoji || x.icon))) out.hide_labels = true;
    return out;
}

function mazePath(rows, cols, start, end, walls) {
    const wall = new Set(walls.map(([r, c]) => `${r},${c}`));
    const seen = new Set([`${start[0]},${start[1]}`]);
    const queue = [start];
    while (queue.length) {
        const [r, c] = queue.shift();
        if (r === end[0] && c === end[1]) return true;
        for (const [dr, dc] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
            const nr = r + dr;
            const nc = c + dc;
            const k = `${nr},${nc}`;
            if (nr < 0 || nc < 0 || nr >= rows || nc >= cols || wall.has(k) || seen.has(k)) continue;
            seen.add(k);
            queue.push([nr, nc]);
        }
    }
    return false;
}

function harderMaze(c, m, rand) {
    const rows0 = c.grid?.rows || 1;
    const cols0 = c.grid?.cols || 1;
    const rows = Math.min(MAZE_MAX, Math.max(rows0, rows0 + 2 * m));
    const cols = Math.min(MAZE_MAX, Math.max(cols0, cols0 + 2 * m));
    const start = c.start || [0, 0];
    // The corner farthest from the start.
    const corners = [[0, 0], [0, cols - 1], [rows - 1, 0], [rows - 1, cols - 1]];
    const dist = ([r, col]) => Math.abs(r - start[0]) + Math.abs(col - start[1]);
    const end = corners.reduce((best, k) => (dist(k) > dist(best) ? k : best), corners[0]);
    const same = (a, b) => a[0] === b[0] && a[1] === b[1];
    let walls = (c.walls || []).filter(
        (w) => w[0] < rows && w[1] < cols && !same(w, start) && !same(w, end)
    );
    if (!mazePath(rows, cols, start, end, walls)) walls = [];
    const taken = new Set(walls.map(([r, col]) => `${r},${col}`));
    const free = [];
    for (let r = 0; r < rows; r += 1) {
        for (let col = 0; col < cols; col += 1) {
            const cell = [r, col];
            if (!same(cell, start) && !same(cell, end) && !taken.has(`${r},${col}`)) free.push(cell);
        }
    }
    // Roughly a quarter of the new board as walls, a few more each level.
    const target = walls.length + Math.max(2 * m, Math.round((rows * cols - rows0 * cols0) * 0.25) + m);
    for (const cell of shuffled(free, rand)) {
        if (walls.length >= target) break;
        const next = [...walls, cell];
        if (mazePath(rows, cols, start, end, next)) walls = next;
    }
    return { ...c, grid: { ...(c.grid || {}), rows, cols }, start, end, walls };
}

function harderCount(c, level, m, siblings, rand) {
    const own = c.rounds || [];
    const extra = (siblings || [])
        .filter((s) => s && s.mode === 'count')
        .flatMap((s) => s.rounds || [])
        .filter((r) => r && Number.isFinite(r.count));
    const roundKey = (r) => `${r.emoji}:${r.count}`;
    const seen = new Set(own.map(roundKey));
    const borrowed = [];
    for (const r of shuffled(extra, rand)) {
        if (borrowed.length >= 2 * m) break;
        if (seen.has(roundKey(r))) continue;
        seen.add(roundKey(r));
        borrowed.push(r);
    }
    const rounds = [...own, ...borrowed].map((r) => {
        const options = [...new Set(r.options || [])];
        const wrong = shuffled(
            Array.from({ length: 10 }, (_, i) => i + 1).filter((n) => n !== r.count && !options.includes(n)),
            rand,
        );
        return { ...r, options: [...options, ...take(wrong, 2 * m)] };
    });
    return { ...c, rounds };
}

/** pattern / cause_effect: more rounds from siblings, one more wrong option per round. */
function harderOptionRounds(c, level, m, siblings, rand) {
    const own = c.rounds || [];
    const roundKey = (r) => JSON.stringify([r.sequence, r.cause?.label, r.cause?.emoji, r.answer]);
    const seen = new Set(own.map(roundKey));
    const borrowed = [];
    for (const sib of siblings || []) {
        if (!sib || sib.mode !== c.mode) continue;
        for (const r of sib.rounds || []) {
            if (r && !seen.has(roundKey(r))) {
                seen.add(roundKey(r));
                borrowed.push(r);
            }
        }
    }
    const allRounds = [...own, ...borrowed];
    const rounds = [...own, ...take(shuffled(borrowed, rand), 2 * m)].map((r, ri) => {
        const options = r.options || [];
        const answerKey = c.mode === 'pattern' ? itemKey(r.answer) : null;
        const have = keysOf(options);
        const candidates = [];
        const candSeen = new Set();
        for (const other of allRounds) {
            for (const o of other.options || []) {
                const k = itemKey(o);
                if (!k || have.has(k) || candSeen.has(k) || k === answerKey) continue;
                if (c.mode === 'cause_effect' && o && o.id === r.answer) continue;
                candSeen.add(k);
                candidates.push(o);
            }
        }
        const pick = take(shuffled(candidates, rand), 1).map((o) => borrow(o, level, ri));
        return { ...r, options: [...options, ...pick] };
    });
    return { ...c, rounds };
}

function harderSort(c, level, m, siblings, rand) {
    const items = c.items || [];
    const bins = new Set((c.bins || []).map((b) => b.id));
    const extra = pool(siblings, 'sort', 'items', keysOf(items)).filter((x) => x && bins.has(x.bin));
    return { ...c, items: [...items, ...take(shuffled(extra, rand), 2 * m).map((x, i) => borrow(x, level, i))] };
}

function harderSequence(c, level, m, siblings, rand) {
    const steps = c.steps || [];
    const extra = unlike(pool(siblings, 'sequence', 'steps', keysOf(steps)).filter((x) => x && !x.distractor), steps);
    const decoys = take(shuffled(extra, rand), m).map((x, i) => ({ ...borrow(x, level, i), distractor: true }));
    return decoys.length ? { ...c, steps: [...steps, ...decoys] } : { ...c };
}

function harderBuild(c, level, m, siblings, rand) {
    const distractors = c.distractor_items || [];
    const base = distractors.length || (c.slots || []).length;
    const extra = unlike(pool(siblings, 'build', 'distractor_items', keysOf(distractors, c.slots || [])),
        distractors, c.slots || []);
    return {
        ...c,
        distractor_items: [...distractors, ...take(shuffled(extra, rand), base * m).map((x, i) => borrow(x, level, i))],
    };
}

function harderPairs(c, level, m, siblings, rand) {
    const cards = c.cards || [];
    const extra = pool(siblings, 'pairs', 'cards', keysOf(cards));
    return { ...c, cards: [...cards, ...take(shuffled(extra, rand), 2 * m).map((x, i) => borrow(x, level, i))] };
}

function harderWords(c, m, siblings, rand, defaultRounds) {
    const words = c.words || [];
    const extra = pool(siblings, c.mode, 'words', keysOf(words));
    const out = { ...c, words: [...words, ...take(shuffled(extra, rand), 2 * m)] };
    if (defaultRounds) out.rounds_count = (c.rounds_count || defaultRounds) + 2 * m;
    return out;
}

const plusRounds = (c, m, def, step = 2) => ({ ...c, rounds_count: (c.rounds_count || def) + step * m });

/** Game types whose levels 2-3 really are harder (content below, or trace's
 * stricter scoring). Every other type keeps level 1 only — replaying the
 * same game must not earn extra stars. Keep in step with LEVELED_MODES in
 * backend/app/services/early_levels.py. */
export const LEVELED_MODES = new Set([
    'select', 'maze', 'count', 'compare', 'bubbles', 'arithmetic', 'rounds', 'keyboard',
    'hangman', 'simon', 'merge', 'sudoku', 'chart', 'trace', 'pattern', 'cause_effect',
    'collect', 'connect', 'catch', 'dragsort',
]);

/** 3 for a game that gets harder, else 1. No mode = select. */
export function levelCountFor(mode) {
    return LEVELED_MODES.has(mode || 'select') ? 3 : 1;
}

export function levelContent(content, level, siblings = [], seed = 0) {
    if (!content || typeof content !== 'object' || !(level === 2 || level === 3)) return content;
    const m = level - 1;
    const rand = rng(seed * 7 + level * 7919 + 1);
    const c = content;
    switch (c.mode) {
    case undefined:
    case null:
    case 'select':
        return harderSelect(c, level, m, siblings, rand);
    case 'connect':
        return harderSelect(c, level, m, siblings, rand);
    case 'collect': {
        // Pictures-only is connect's level 3; walking and catching keep names.
        const { hide_labels: _h, ...out } = harderSelect(c, level, m, siblings, rand);
        return { ...out, grid_size: 5 + m };
    }
    case 'catch': {
        const { hide_labels: _h, ...out } = harderSelect(c, level, m, siblings, rand);
        return { ...out, fall_ms: CATCH_FALL_MS[m] };
    }
    case 'dragsort':
        // Level 1 = 3 pieces per basket (see dragsortSetup.js), 2 = all, 3 = a third basket.
        return { ...c, per_basket: m === 0 ? 3 : null, use_partner2: level === 3 };
    case 'maze':
        return harderMaze(c, m, rand);
    case 'count':
        return harderCount(c, level, m, siblings, rand);
    case 'compare':
        return { ...plusRounds(c, m, 8), max: (c.max || 9) * (1 + m) };
    case 'bubbles':
        return { ...plusRounds(c, m, 6), max: (c.max || 10) * (1 + m) };
    case 'arithmetic': {
        const ops = c.operations?.length ? c.operations : ['add', 'subtract'];
        const operations = ops.length === 1
            ? [...ops, ops[0] === 'subtract' ? 'add' : 'subtract']
            : ops;
        return { ...plusRounds(c, m, 8), operations, max: 10 * (1 + m) };
    }
    case 'rounds': {
        const steps = ['easy', 'medium', 'hard'];
        const at = Math.max(0, steps.indexOf(c.level || 'easy'));
        const out = { ...plusRounds(c, m, 8), level: steps[Math.min(2, at + m)] };
        const kind = c.kind || 'mult';
        if (kind === 'mult') out.max = (c.max || 5) * (1 + m);
        if (kind === 'money') out.max = (c.max || 2000) * (1 + m);
        return out;
    }
    case 'sort': {
        // Borrowed items only fit when another sort game has the same bins,
        // which authored content rarely does — so level 3 is also pictures only.
        const out = harderSort(c, level, m, siblings, rand);
        const items = out.items || [];
        if (level === 3 && items.length && items.every((x) => x && x.emoji)) out.hide_labels = true;
        return out;
    }
    case 'sequence':
        return harderSequence(c, level, m, siblings, rand);
    case 'pattern':
    case 'cause_effect':
        return harderOptionRounds(c, level, m, siblings, rand);
    case 'build':
        return harderBuild(c, level, m, siblings, rand);
    case 'pairs':
        return harderPairs(c, level, m, siblings, rand);
    case 'keyboard': {
        const keys = (c.keys || []).map((k) => String(k).toLowerCase());
        const base = keys.length ? keys : ['f', 'j'];
        const extra = HOME_ROW.filter((k) => !base.includes(k));
        return { ...plusRounds(c, m, 10, 4), keys: [...base, ...take(extra, 2 * m)] };
    }
    case 'typing':
        return harderWords(c, m, siblings, rand, 0);
    case 'wordbuild':
        return harderWords(c, m, siblings, rand, 5);
    case 'hangman':
        // Fewer wrong letters allowed: harder even when no new words exist.
        return { ...harderWords(c, m, siblings, rand, 4), lives: 6 - m };
    case 'simon':
        return plusRounds(c, m, 5);
    case 'merge':
        return { ...c, goal: (c.goal || 64) * 2 ** m };
    case 'sudoku':
        return { ...c, blanks: Math.min(10, (c.blanks || 6) + 2 * m) };
    case 'chart':
        return { ...plusRounds(c, m, 6), hard: true };
    default:
        // trace (stricter scoring instead, see starsForCoverage), puzzle
        // (fixed 3x3) and unknown modes play as they are.
        return { ...c };
    }
}

export function levelActivity(activity, level, siblings = []) {
    const lv = level === 2 || level === 3 ? level : 1;
    return {
        ...activity,
        level: lv,
        content: levelContent(activity.content, lv, siblings, Number(activity.id) || 0),
    };
}
