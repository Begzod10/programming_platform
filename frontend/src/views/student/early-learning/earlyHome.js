/* Pure selection logic for the kids' games home and the module path — what
 * to continue, what is new for this kid, how modules group into sections,
 * which game is next. No React, no I/O.
 *
 * Every function tolerates items missing the newer fields (`section`,
 * `completed_count`, `last_played_at`): the home can be drawn from a module
 * list cached offline before those fields existed. */

export const SECTIONS = [
    { key: 'world', emoji: '🌍', titleKey: 'el.homeWorld' },
    { key: 'logic', emoji: '🔢', titleKey: 'el.homeLogic' },
    { key: 'make', emoji: '✏️', titleKey: 'el.homeMake' },
    { key: 'letters', emoji: '⌨️', titleKey: 'el.homeLetters' },
];
const DEFAULT_SECTION = 'world';
const SECTION_KEYS = new Set(SECTIONS.map((s) => s.key));

const total = (m) => m?.activities_count || 0;
const done = (m) => m?.completed_count || 0;
const byOrder = (a, b) => (a.display_order || 0) - (b.display_order || 0) || a.id - b.id;

/** Every game of the module was played at least once. An empty module is
 * never "finished" — there is nothing to finish. */
export function isFinished(module) {
    return total(module) > 0 && done(module) >= total(module);
}

const playable = (m) => total(m) > 0 && !isFinished(m);

/** The module the "continue" card points at, or null when there is nothing
 * left to play. `started` is false only when the kid has not begun the
 * chosen module (the card then says "start"). */
export function pickContinue(modules) {
    const open = (modules || []).filter(playable);
    if (!open.length) return null;

    const recent = open
        .filter((m) => m.last_played_at)
        .sort((a, b) => new Date(b.last_played_at) - new Date(a.last_played_at))[0];
    if (recent) return { module: recent, started: true };

    const sorted = [...open].sort(byOrder);
    // Guests have no timestamps — any module they have begun will do.
    const begun = sorted.find((m) => done(m) > 0);
    if (begun) return { module: begun, started: true };

    return { module: sorted[0], started: false };
}

/** Modules this kid has never opened, newest first. Empty for a kid who has
 * not played anything yet (everything is new to them — the row would just
 * repeat the whole page). */
export function pickNew(modules, continueModule, limit = 6) {
    const list = modules || [];
    if (!list.some((m) => done(m) > 0)) return [];
    return list
        .filter((m) => total(m) > 0 && done(m) === 0 && m.id !== continueModule?.id)
        .sort((a, b) => b.id - a.id)
        .slice(0, limit);
}

/** Non-empty sections in display order; inside each, unfinished modules
 * first, finished ones sink to the end. */
export function groupBySection(modules) {
    const list = modules || [];
    const keyOf = (m) => (SECTION_KEYS.has(m.section) ? m.section : DEFAULT_SECTION);
    return SECTIONS
        .map((section) => {
            const mine = list.filter((m) => keyOf(m) === section.key);
            return {
                ...section,
                modules: [
                    ...mine.filter((m) => !isFinished(m)).sort(byOrder),
                    ...mine.filter(isFinished).sort(byOrder),
                ],
            };
        })
        .filter((group) => group.modules.length > 0);
}

/** The first game (by order) the kid has not played yet, or null. */
export function nextActivity(activities) {
    return [...(activities || [])]
        .sort((a, b) => (a.order || 0) - (b.order || 0) || a.id - b.id)
        .find((a) => !a.attempts) || null;
}
