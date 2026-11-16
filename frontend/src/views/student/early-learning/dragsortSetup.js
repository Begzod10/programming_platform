/* Baskets and pieces of the drag-to-basket game (mode: "dragsort").
 *
 * makeBaskets(content, level) → { baskets: [{character, items}], pieces:
 * [{key, item, basket}] } or null when the game cannot be played as a sort
 * (no partner, or a basket with fewer than 2 pieces) — the games page then
 * plays it as connect.
 *
 * Baskets: the game's own character, `partner` (a game of ANOTHER module,
 * written by scripts/convert_select_modules.py) and at level 3 `partner2`.
 * A picture or name found in two baskets is dropped from all of them, so no
 * piece ever fits two baskets. Level 1 takes 3 pieces per basket.
 */

const LEVEL1_PER_BASKET = 3;
const MIN_PER_BASKET = 2;

const nameOf = (x) => String(x?.label || '').trim().toLowerCase();
const picsOf = (x) => [x?.emoji, x?.icon].filter(Boolean);

function basketOf(source) {
    if (!source || typeof source !== 'object' || !source.character || typeof source.character !== 'object') return null;
    return { character: source.character, items: (source.correct_items || []).filter(Boolean) };
}

function build(sources, perBasket) {
    const baskets = sources.map(basketOf);
    if (baskets.length < 2 || baskets.some((b) => !b)) return null;
    // Where each name / picture appears.
    const seen = new Map();
    baskets.forEach((b, i) => {
        for (const x of b.items) {
            for (const k of [`n:${nameOf(x)}`, ...picsOf(x).map((p) => `p:${p}`)]) {
                if (k === 'n:') continue;
                if (!seen.has(k)) seen.set(k, new Set());
                seen.get(k).add(i);
            }
        }
    });
    const shared = (x) => [`n:${nameOf(x)}`, ...picsOf(x).map((p) => `p:${p}`)]
        .some((k) => k !== 'n:' && seen.get(k)?.size > 1);
    const out = baskets.map((b) => {
        const items = b.items.filter((x) => !shared(x));
        return { ...b, items: perBasket ? items.slice(0, perBasket) : items };
    });
    if (out.some((b) => b.items.length < MIN_PER_BASKET)) return null;
    const pieces = out.flatMap((b, basket) => b.items.map((item, i) => ({ key: `${basket}-${i}`, item, basket })));
    return { baskets: out, pieces };
}

export function makeBaskets(content, level = 1) {
    const c = content || {};
    const perBasket = c.per_basket !== undefined ? c.per_basket : (level === 1 ? LEVEL1_PER_BASKET : null);
    const third = c.use_partner2 !== undefined ? c.use_partner2 : level === 3;
    if (third && c.partner2) {
        const three = build([c, c.partner, c.partner2], perBasket);
        if (three) return three;
    }
    // A third basket that does not work just leaves the two-basket game.
    return build([c, c.partner], perBasket);
}
