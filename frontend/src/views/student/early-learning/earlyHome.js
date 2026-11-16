import { levelCountFor } from './levelContent';

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

/** ✓ — every game of the module was played at level 1. An empty module is
 * never done — there is nothing to finish. */
export function isDone(module) {
    return total(module) > 0 && done(module) >= total(module);
}

/** 👑 — every level of every game was played. This is what "finished"
 * means for sorting and "continue": a ✓ module still has levels 2-3 to
 * offer. A module from an old cache (no level counts) is never finished. */
export function isFinished(module) {
    const max = module?.max_level_plays || 0;
    return total(module) > 0 && max > 0 && (module.level_plays || 0) >= max;
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

export const UNLOCK_STARS = 2;
const byStep = (a, b) => (a.order || 0) - (b.order || 0) || a.id - b.id;

/** The levels of a game ({level, best_stars, attempts, unlocked}): three, or
 * one for a game that cannot get harder (levelCountFor).
 * An activity from an old cache has no `levels`: level 1 comes from its
 * own best_stars/attempts and levels 2-3 stay locked. */
export function levelsOf(activity) {
    if (Array.isArray(activity?.levels) && activity.levels.length >= 1) return activity.levels;
    const first = { level: 1, best_stars: activity?.best_stars || 0, attempts: activity?.attempts || 0, unlocked: true };
    if (levelCountFor(activity?.content?.mode) === 1) return [first];
    return [
        first,
        { level: 2, best_stars: 0, attempts: 0, unlocked: false },
        { level: 3, best_stars: 0, attempts: 0, unlocked: false },
    ];
}

/** What the path offers next, in this order (first matching game by order
 * at each stage):
 *  (a) a game whose level 1 was never played;
 *  (b) the lowest level that is open but not played yet;
 *  (c) a game whose next level is still locked because its last played
 *      level has fewer than UNLOCK_STARS stars — `unlockHint` names the
 *      level one more star would open.
 * null only once every level of every game has been played. */
export function nextStep(activities) {
    const sorted = [...(activities || [])].sort(byStep);
    for (const activity of sorted) {
        if (!levelsOf(activity)[0].attempts) return { activity, level: 1 };
    }
    for (const activity of sorted) {
        const open = levelsOf(activity).find((l) => l.unlocked && !l.attempts);
        if (open) return { activity, level: open.level };
    }
    for (const activity of sorted) {
        const levels = levelsOf(activity);
        const i = levels.findIndex((l, k) => k < levels.length - 1 && l.attempts && l.best_stars < UNLOCK_STARS && !levels[k + 1].unlocked);
        if (i >= 0) return { activity, level: levels[i].level, unlockHint: levels[i].level + 1 };
    }
    return null;
}

/** The level a tap on a game starts: the highest open level that does not
 * have three stars yet; once every open level has three stars, the highest
 * open one (3 when all three are open). */
export function startLevel(activity) {
    const levels = levelsOf(activity).filter((l) => l.unlocked);
    const open = levels.filter((l) => (l.best_stars || 0) < 3);
    const pick = open.length ? open : levels;
    return pick.length ? pick[pick.length - 1].level : 1;
}
