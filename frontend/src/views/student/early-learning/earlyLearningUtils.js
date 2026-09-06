/** Small helpers shared by every early-learning play screen
 * (MatchingActivity.js, BuildActivity.js) — pulled out here once a second
 * screen needed the exact same shuffle/scoring rules, rather than
 * duplicating them. */

/** How long a wrong-attempt flash/banner stays up before clearing itself. */
export const WRONG_FLASH_MS = 1200;

/** Fisher-Yates shuffle — used to randomize a round's item/piece tray so
 * it isn't in the same order every time a kid replays it. */
export function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
}

/** 3 stars for a clean round, 2 for a few slip-ups, 1 for a rough one —
 * same thresholds for every activity type so a kid's sense of "how well
 * did I do" stays consistent across the whole feature. */
export function starsForWrongCount(wrongCount) {
    if (wrongCount === 0) return 3;
    if (wrongCount <= 2) return 2;
    return 1;
}
