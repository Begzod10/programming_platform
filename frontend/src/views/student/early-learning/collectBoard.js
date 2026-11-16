/* The field of the collect game ("walk the maze, pick up the right things").
 *
 * makeBoard(content, seed) is pure and seeded: the same game at the same
 * level always gets the same field (a language switch re-fetches the
 * content but the items keep their places).
 *
 * Every right item stays reachable from the start without stepping on a
 * wall or a wrong item: right items are placed first, then each wrong item
 * and each wall is only kept where that still holds (BFS check).
 */
import { rng, shuffled } from './levelContent';

const WALL_SHARE = 0.2;
const MIN_SIZE = 3;
const MAX_SIZE = 9;

const cellKey = (r, c) => `${r},${c}`;

function reachableFrom(size, start, blocked) {
    const seen = new Set([cellKey(start[0], start[1])]);
    const queue = [start];
    while (queue.length) {
        const [r, c] = queue.shift();
        for (const [dr, dc] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
            const nr = r + dr;
            const nc = c + dc;
            const k = cellKey(nr, nc);
            if (nr < 0 || nc < 0 || nr >= size || nc >= size || blocked.has(k) || seen.has(k)) continue;
            seen.add(k);
            queue.push([nr, nc]);
        }
    }
    return seen;
}

/** {size, start, walls: [[r,c]], items: [{r, c, item, ok}]} */
export function makeBoard(content, seed = 0) {
    const c = content || {};
    const size = Math.max(MIN_SIZE, Math.min(MAX_SIZE, Math.round(Number(c.grid_size)) || 5));
    const start = [0, 0];
    const rand = rng((Number(seed) || 0) * 31 + size * 977 + 5);
    const free = shuffled(
        Array.from({ length: size * size }, (_, i) => [Math.floor(i / size), i % size])
            .filter(([r, col]) => r !== start[0] || col !== start[1]),
        rand,
    );

    const right = (c.correct_items || []).filter(Boolean).slice(0, free.length);
    const items = right.map((item, i) => ({ r: free[i][0], c: free[i][1], item, ok: true }));
    let rest = free.slice(right.length);
    const blocked = new Set();
    const allRightOpen = () => {
        const open = reachableFrom(size, start, blocked);
        return items.every((x) => !x.ok || open.has(cellKey(x.r, x.c)));
    };

    // Wrong items: the first free cell (in seeded order) that keeps every right item reachable.
    for (const item of (c.distractor_items || []).filter(Boolean)) {
        const at = rest.findIndex(([r, col]) => {
            blocked.add(cellKey(r, col));
            const ok = allRightOpen();
            blocked.delete(cellKey(r, col));
            return ok;
        });
        if (at < 0) continue;
        const [r, col] = rest[at];
        blocked.add(cellKey(r, col));
        items.push({ r, c: col, item, ok: false });
        rest = [...rest.slice(0, at), ...rest.slice(at + 1)];
    }

    const walls = [];
    const wantWalls = Math.round(size * size * WALL_SHARE);
    for (const [r, col] of rest) {
        if (walls.length >= wantWalls) break;
        blocked.add(cellKey(r, col));
        if (allRightOpen()) walls.push([r, col]);
        else blocked.delete(cellKey(r, col));
    }
    return { size, start, walls, items };
}
