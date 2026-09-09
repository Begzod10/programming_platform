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
 * same "a kid who tried shouldn't score zero" floor. */
export function starsForCoverage(pct) {
    if (pct >= 0.85) return 3;
    if (pct >= 0.55) return 2;
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

/** Same upsert rule as the backend's complete_early_activity: attempts
 * always increments, stars_earned only ever moves up (replaying to improve
 * a score shouldn't be able to lower it). Returns the shape onComplete
 * expects ({stars_earned, attempts}), same as the server's response. */
export function recordGuestCompletion(activityId, stars) {
    const progress = getGuestProgress();
    const prev = progress[activityId];
    const next = {
        stars_earned: Math.max(prev?.stars_earned || 0, stars),
        attempts: (prev?.attempts || 0) + 1,
    };
    try {
        localStorage.setItem(
            GUEST_PROGRESS_KEY,
            JSON.stringify({ ...progress, [activityId]: next })
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
export function applyGuestModuleStars(modules) {
    const progress = getGuestProgress();
    return modules.map((m) => ({
        ...m,
        earned_stars: (m.activity_ids || []).reduce(
            (sum, id) => sum + (progress[id]?.stars_earned || 0), 0
        ),
    }));
}

/** Same idea as applyGuestModuleStars, one level down — patches a
 * /public/modules/:id detail's activities (always best_stars/attempts: 0)
 * with each activity's real localStorage progress, then re-sums the
 * module-level earned_stars from the patched activities. */
export function applyGuestActivityStars(moduleDetail) {
    const progress = getGuestProgress();
    const activities = moduleDetail.activities.map((a) => {
        const p = progress[a.id];
        return p ? { ...a, best_stars: p.stars_earned, attempts: p.attempts } : a;
    });
    return {
        ...moduleDetail,
        activities,
        earned_stars: activities.reduce((sum, a) => sum + a.best_stars, 0),
    };
}
