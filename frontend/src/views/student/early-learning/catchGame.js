/* The catch game's falling items, as a pure step function so it can be
 * tested without animation frames.
 *
 * state: { queue: [piece], falling: [{id, piece, lane, y}], fallMs,
 *          basketLane, spawned, caught }
 * piece: { key, item, ok }. y runs 0 (top) → 1 (the basket line); an item
 * takes fallMs to fall the whole way. At most two items fall at once, the
 * second one starting when the first is halfway down.
 *
 * At the basket line: in the basket's lane → "caught" (a right item, caught
 * += 1) or "mistake" (a wrong item). Elsewhere → "missed": a right item
 * goes to the back of the queue (it will fall again — no penalty, no time
 * limit), a wrong item is simply gone.
 */

export const LANES = 3;
export const MAX_FALLING = 2;
const SPAWN_GAP = 0.5;
// Lanes the items fall in, in turn: varied, but never random in tests.
const LANE_ORDER = [1, 0, 2, 2, 0, 1, 0, 2, 1];

export function startFalling(pieces, fallMs) {
    return { queue: [...pieces], falling: [], fallMs, basketLane: 1, spawned: 0, caught: 0, events: [] };
}

export function stepFalling(state, dtMs) {
    const events = [];
    const speed = dtMs / Math.max(1, state.fallMs || 5000);
    let queue = [...state.queue];
    let caught = state.caught || 0;
    const falling = [];
    for (const f of state.falling) {
        const y = f.y + speed;
        if (y < 1) {
            falling.push({ ...f, y });
            continue;
        }
        if (f.lane === state.basketLane) {
            if (f.piece.ok) {
                caught += 1;
                events.push({ type: 'caught', piece: f.piece });
            } else {
                events.push({ type: 'mistake', piece: f.piece });
            }
        } else {
            events.push({ type: 'missed', piece: f.piece });
            if (f.piece.ok) queue = [...queue, f.piece];
        }
    }
    let spawned = state.spawned || 0;
    if (falling.length < MAX_FALLING && queue.length && falling.every((f) => f.y >= SPAWN_GAP)) {
        const [next, ...rest] = queue;
        queue = rest;
        falling.push({ id: spawned + 1, piece: next, lane: LANE_ORDER[spawned % LANE_ORDER.length], y: 0 });
        spawned += 1;
    }
    return { ...state, queue, falling, caught, spawned, events };
}
