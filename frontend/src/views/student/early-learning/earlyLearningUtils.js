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

/** Consecutive-correct-tap threshold for the little "streak" flourish (a
 * brighter sound + a fleeting "🔥 N!" badge) used by MatchingActivity.js,
 * CountActivity.js, and SortActivity.js — screens where every tap gives
 * the exact same feedback regardless of how well the round is going,
 * which read flattest in the 2026-09-09 mechanic review. Picked at 3: frequent enough
 * to land at least once in a typical 6-8 item round, not so frequent it
 * fires on every other tap and stops feeling like a bonus. Purely a
 * presentation layer — never touches wrongCount/starsForWrongCount, so
 * scoring and the completion API are unaffected. */
export const STREAK_THRESHOLD = 3;

/** 3 stars for a clean round, 2 for a few slip-ups, 1 for a rough one —
 * same thresholds for every activity type so a kid's sense of "how well
 * did I do" stays consistent across the whole feature. */
export function starsForWrongCount(wrongCount) {
    if (wrongCount === 0) return 3;
    if (wrongCount <= 2) return 2;
    return 1;
}

/** Same idea as starsForWrongCount, for TraceActivity.js's coverage-based
 * scoring (% of a shape's outline actually traced) — never below 1 star,
 * same "a kid who tried shouldn't score zero" floor. Game levels 2 and 3
 * ask for a neater trace (the shapes themselves stay the same). */
const COVERAGE_BARS = { 1: [0.85, 0.55], 2: [0.9, 0.65], 3: [0.94, 0.75] };
export function starsForCoverage(pct, level = 1) {
    const [three, two] = COVERAGE_BARS[level] || COVERAGE_BARS[1];
    if (pct >= three) return 3;
    if (pct >= two) return 2;
    return 1;
}

/* ── Guest mode (no login, /play) ──────────────────────────────────────
 * A guest plays the exact same content as a logged-in student, but there's
 * no Student row to attach an EarlyActivityCompletion to, so nothing gets
 * POSTed to the backend at all (see the "public" endpoints in
 * early_learning.py — read-only, no /complete route). Stars live entirely
 * in this browser's localStorage instead, shaped identically to how the
 * server stores them ({stars_earned, attempts} per activity id) so the
 * rest of EarlyLearning.js/the 4 activity screens can treat a guest
 * completion result exactly like a server one. */
const GUEST_PROGRESS_KEY = 'el_guest_progress';

export function getGuestProgress() {
    try {
        const raw = localStorage.getItem(GUEST_PROGRESS_KEY);
        return raw ? JSON.parse(raw) : {};
    } catch {
        // Private-mode/quota-exceeded localStorage, or corrupted JSON from a
        // previous version — treat as "no progress yet" rather than crash
        // the whole picker screen over a lost star count.
        return {};
    }
}

/** Guest progress key: level 1 keeps the plain activity id (as before game
 * levels existed), levels 2-3 are "{id}:2" / "{id}:3". */
const guestKey = (activityId, level = 1) => (level > 1 ? `${activityId}:${level}` : String(activityId));

/** Same upsert rule as the backend's complete_early_activity: attempts
 * always increments, stars_earned only ever moves up (replaying to improve
 * a score shouldn't be able to lower it). Returns the shape onComplete
 * expects ({stars_earned, attempts}), same as the server's response. */
export function recordGuestCompletion(activityId, stars, level = 1) {
    const progress = getGuestProgress();
    const key = guestKey(activityId, level);
    const prev = progress[key];
    const next = {
        stars_earned: Math.max(prev?.stars_earned || 0, stars),
        attempts: (prev?.attempts || 0) + 1,
    };
    try {
        localStorage.setItem(
            GUEST_PROGRESS_KEY,
            JSON.stringify({ ...progress, [key]: next })
        );
    } catch {
        // Falls back to celebrating locally without persisting — see
        // getGuestProgress's catch above.
    }
    return next;
}

/** Patches a /public/modules list (always earned_stars: 0 — no server-side
 * completions to sum for a guest) with each module's real earned_stars,
 * computed from localStorage via the activity_ids the public endpoint
 * exposes just for this. */
const LEVELS = [1, 2, 3];

/** A guest's three levels of one game, same shape as the server's
 * EarlyLevelOut: a level opens once the one below has 2+ stars. With
 * localStorage unavailable this is level 1 open, nothing played. */
export function guestLevels(activityId, progress = getGuestProgress()) {
    let prevBest = 0;
    return LEVELS.map((level) => {
        const p = progress[guestKey(activityId, level)];
        const row = {
            level,
            best_stars: p?.stars_earned || 0,
            attempts: p?.attempts || 0,
            unlocked: level === 1 || prevBest >= 2,
        };
        prevBest = row.best_stars;
        return row;
    });
}

export function applyGuestModuleStars(modules) {
    const progress = getGuestProgress();
    return modules.map((m) => {
        const ids = m.activity_ids || [];
        const keys = ids.flatMap((id) => LEVELS.map((level) => guestKey(id, level)));
        return {
            ...m,
            earned_stars: keys.reduce((sum, k) => sum + (progress[k]?.stars_earned || 0), 0),
            // Lets the home's "continue" card and finished marks work for a
            // guest too (see earlyHome.js) — the public endpoint always says 0.
            completed_count: ids.filter((id) => progress[guestKey(id)]).length,
            level_plays: keys.filter((k) => progress[k]).length,
            max_level_plays: m.max_level_plays || ids.length * LEVELS.length,
        };
    });
}

/** Same idea as applyGuestModuleStars, one level down — patches a
 * /public/modules/:id detail's activities (always best_stars/attempts: 0)
 * with each activity's real localStorage progress, then re-sums the
 * module-level earned_stars from the patched activities. */
export function applyGuestActivityStars(moduleDetail) {
    const progress = getGuestProgress();
    const activities = moduleDetail.activities.map((a) => {
        const levels = guestLevels(a.id, progress);
        return { ...a, best_stars: levels[0].best_stars, attempts: levels[0].attempts, levels };
    });
    const all = activities.flatMap((a) => a.levels);
    return {
        ...moduleDetail,
        activities,
        earned_stars: all.reduce((sum, l) => sum + l.best_stars, 0),
        level_plays: all.filter((l) => l.attempts).length,
    };
}

/* ── Offline cache ─────────────────────────────────────────────────────
 * The module list and every module's activities (content included) are
 * mirrored into localStorage after each successful fetch, so a dropped
 * wifi connection doesn't empty the games screen — EarlyLearning.js falls
 * back to whatever was last cached. Keys carry the language (content is
 * localized server-side) and, for logged-in users, the user id (the
 * payload includes that student's own star progress, which must never be
 * shown to whoever logs in next on a shared device). Raw server data is
 * cached — guest stars are re-applied from their own localStorage on read. */
const EL_CACHE_PREFIX = 'el_cache_v1:';

export function elCacheKey(guest, userId, kind, lang, id) {
    return `${EL_CACHE_PREFIX}${guest ? 'guest' : `u${userId ?? 'x'}`}:${kind}:${lang}${id != null ? `:${id}` : ''}`;
}

export function elCacheSet(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify({ savedAt: Date.now(), data }));
    } catch {
        // Quota exceeded / storage disabled — caching is best-effort only.
    }
}

export function elCacheGet(key) {
    try {
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw).data : null;
    } catch {
        return null;
    }
}

/** Registers /play-sw.js (public/play-sw.js) scoped to just the given
 * early-learning route, so its offline page/asset caching never applies to
 * the rest of the app. Production only — a service worker under the dev
 * server just fights hot reloading. Failure to register is silent: the
 * games still work online, this only adds the offline page load. */
export function registerOfflineSw(scope) {
    if (process.env.NODE_ENV !== 'production') return;
    if (typeof navigator === 'undefined' || !('serviceWorker' in navigator)) return;
    navigator.serviceWorker.register('/play-sw.js', { scope }).catch(() => {});
}

/* ── Daily challenge streak (localStorage, per browser) ─────────────────── */
const DAILY_KEY = 'el_daily_v1';
const dayStr = (d = new Date()) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

export function getDaily() {
    try {
        const raw = JSON.parse(localStorage.getItem(DAILY_KEY) || 'null') || {};
        const today = dayStr();
        const yesterday = dayStr(new Date(Date.now() - 86400000));
        const alive = raw.last === today || raw.last === yesterday; // a missed day breaks the streak
        return { streak: alive ? raw.streak || 0 : 0, doneToday: raw.last === today, best: raw.best || 0 };
    } catch {
        return { streak: 0, doneToday: false, best: 0 };
    }
}

/** Call once a daily challenge is finished; only the first one of a day counts. */
export function recordDaily() {
    const cur = getDaily();
    if (cur.doneToday) return cur;
    const streak = cur.streak + 1;
    const best = Math.max(cur.best, streak);
    try { localStorage.setItem(DAILY_KEY, JSON.stringify({ last: dayStr(), streak, best })); } catch { /* ignore */ }
    return { streak, doneToday: true, best };
}

/** Same questions for everyone on a given day (seeded from the date). */
export function dailySeed() {
    let h = 2166136261;
    for (const ch of dayStr()) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); }
    return h >>> 0;
}

/* ── Offline star queue: completions that could not reach the server ────── */
const QUEUE_KEY = 'el_star_queue_v1';

/** One entry per (activity, level); entries queued before game levels
 * existed have no `level` and mean level 1. */
export function queueCompletion(activityId, stars, level = 1) {
    try {
        const q = JSON.parse(localStorage.getItem(QUEUE_KEY) || '[]');
        const i = q.findIndex((x) => x.activityId === activityId && (x.level || 1) === level);
        if (i >= 0) q[i].stars = Math.max(q[i].stars, stars); else q.push({ activityId, stars, level });
        localStorage.setItem(QUEUE_KEY, JSON.stringify(q.slice(-100)));
    } catch { /* ignore */ }
}

/** Try to send every queued completion; keeps the ones that still fail. */
export async function flushCompletionQueue(send) {
    let q;
    try { q = JSON.parse(localStorage.getItem(QUEUE_KEY) || '[]'); } catch { return 0; }
    if (!q.length) return 0;
    const left = [];
    for (const item of q) {
        try { await send(item.activityId, item.stars, item.level || 1); } catch { left.push(item); }
    }
    try { localStorage.setItem(QUEUE_KEY, JSON.stringify(left)); } catch { /* ignore */ }
    return q.length - left.length;
}

/** What a play screen hands onComplete when the completion POST failed. No
 * activity_id means "not saved" (EarlyLearning.js queues it); `locked`
 * marks the server's 409 level_locked — the level was not open (an old
 * cache, say), so it is not queued: the module is quietly reloaded. */
export function completionFallback(err, stars) {
    const locked = err?.status === 409;
    return locked ? { stars_earned: stars, attempts: 1, locked: true } : { stars_earned: stars, attempts: 1 };
}
