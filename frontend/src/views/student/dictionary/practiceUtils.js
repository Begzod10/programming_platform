/* Practice utilities — constants, scoring, icons, fire streak logic. */

import { useEffect } from 'react';
import { API_URL, headers } from '../../../api/search/base';
import { Flame } from 'lucide-react';

export const BASE = `${API_URL}v1/dictionary/practice`;

export const MODES = [
    { key: 'flashcard', label: 'Flashcard',  desc: 'Bilaman / Bilmayman', icon: '🃏' },
    { key: 'quiz',      label: 'Quiz+',      desc: '4 tadan birini tanlash yoki yozish', icon: '🎯' },
    { key: 'spelling',  label: 'Spelling',   desc: "So'zni yozing",       icon: '⌨️' },
    { key: 'listening', label: 'Listening',  desc: 'Eshitib yozish',      icon: '🎧' },
    { key: 'cloze',     label: 'Cloze',      desc: "Gapda bo'shliqni to'ldiring", icon: '✏️' },
];

export const DEFAULT_COUNT = 10;
export const CHUNK_SIZE = 10;

/* ─── Close-match scoring for typed-answer modes ────────────────────────
   Levenshtein: exact = grade 2, off by 1-2 chars on words >= 4 chars = grade 1,
   else 0. The AI judge runs as a last-resort tiebreaker for "no" verdicts so
   "qo'shimcha funksiyalar" doesn't get rejected against "qo'shimcha funksiya". */

// Uzbek o'/g' sounds get typed with whichever "apostrophe" the student's
// keyboard/IME happens to produce — plain '(U+0027), the curly '(U+2019),
// a backtick `(U+0060), or the proper Uzbek modifier letters ʻ/ʼ
// (U+02BB/U+02BC). These are NOT the same code point and NFKD does not fold
// them into each other, so without this they'd count as a real character
// mismatch (e.g. "o'zbek" vs "oʻzbek" costs 1 edit) even though the student
// wrote the exact right word. Fold them all to a plain ' before comparing.
const APOSTROPHE_VARIANTS = /[‘’ʻʼ`´]/g;

export const norm = (s) =>
    (s || '')
        .trim()
        .toLowerCase()
        .replace(APOSTROPHE_VARIANTS, "'")
        .normalize('NFKD')
        .replace(/[̀-ͯ]/g, '')
        .replace(/\s+/g, ' ');

export function editDistance(a, b) {
    if (a === b) return 0;
    const al = a.length, bl = b.length;
    if (!al) return bl;
    if (!bl) return al;
    const dp = Array(bl + 1).fill(0).map((_, i) => i);
    for (let i = 1; i <= al; i++) {
        let prev = dp[0];
        dp[0] = i;
        for (let j = 1; j <= bl; j++) {
            const tmp = dp[j];
            dp[j] = a[i - 1] === b[j - 1]
                ? prev
                : 1 + Math.min(prev, dp[j - 1], dp[j]);
            prev = tmp;
        }
    }
    return dp[bl];
}

export function judgeTyped(userInput, target) {
    const a = norm(userInput), b = norm(target);
    if (!a) return { ok: false, exact: false };
    if (a === b) return { ok: true, exact: true };
    const dist = editDistance(a, b);
    if (b.length >= 4 && dist <= 2) return { ok: true, exact: false };
    return { ok: false, exact: false };
}

/* ═══════════════════════════════════════════════════════════════════════
   ASYNC JUDGE: local Levenshtein first, AI fallback on a "no" verdict.
   Used by all three typed modes. The AI call is best-effort — if it
   times out, errors, or hits the unconfigured branch, we keep the local
   "no" so the student doesn't sit waiting on a black-hole request.
   ═══════════════════════════════════════════════════════════════════════ */

export const judgeTypedAsync = async (request, userInput, target, definition) => {
    const local = judgeTyped(userInput, target);
    if (local.ok) return { ...local, aiUsed: false };

    try {
        const aiTimeoutMs = 6000;
        const aiPromise = request(
            `${BASE}/judge-answer`,
            'POST',
            JSON.stringify({ user_input: userInput, target, definition }),
            headers(),
        );
        const timed = await Promise.race([
            aiPromise,
            new Promise((resolve) => setTimeout(() => resolve(null), aiTimeoutMs)),
        ]);
        if (timed && timed.ok) {
            return {
                ok: true,
                exact: timed.verdict === 'yes',
                aiUsed: true,
            };
        }
    } catch { /* fall through to local verdict */ }

    return { ...local, aiUsed: false };
};

/* ─── Inline SVG icons (consistent with the rest of the app) ──────────── */
export const Icon = {
    Check:  (p) => <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...p}><polyline points="20 6 9 17 4 12" /></svg>,
    X:      (p) => <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...p}><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>,
    Clock:  (p) => <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>,
    Warn:   (p) => <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>,
    Volume: (p) => <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" /><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" /></svg>,
    Sparkle:(p) => <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1" /></svg>,
    Skull:  (p) => <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="9" cy="11" r="1.5" fill="currentColor" /><circle cx="15" cy="11" r="1.5" fill="currentColor" /><path d="M4 13a8 8 0 1 1 16 0v4a2 2 0 0 1-2 2h-2v3h-2v-3h-4v3h-2v-3H6a2 2 0 0 1-2-2z" /></svg>,
};

/* ═══════════════════════════════════════════════════════════════════════
   FIRE STREAK — in-drill gamification
   Consecutive correct answers grow a counter shown as a top-right badge.
   At level 1 (3-4), 2 (5-7), 3 (8+) a full-screen radial fire overlay
   activates behind the card. Resets on any wrong answer.
   ═══════════════════════════════════════════════════════════════════════ */

export const FIRE_OVERLAY_ID = 'pr-fire-overlay';
export const FIRE_KEYFRAMES_ID = 'pr-fire-keyframes';

export const fireLevelFor = (streak) => {
    if (streak >= 8) return 3;
    if (streak >= 5) return 2;
    if (streak >= 3) return 1;
    return 0;
};

export function ensureFireKeyframes() {
    if (typeof document === 'undefined') return;
    if (document.getElementById(FIRE_KEYFRAMES_ID)) return;
    const s = document.createElement('style');
    s.id = FIRE_KEYFRAMES_ID;
    s.textContent = `
        @keyframes pr-fire-pulse {
            0%, 100% { opacity: 0.85; transform: scaleY(1); }
            20%      { opacity: 1;    transform: scaleY(1.04); }
            50%      { opacity: 0.72; transform: scaleY(0.97); }
            75%      { opacity: 0.94; transform: scaleY(1.02); }
        }
        @keyframes pr-fire-wave {
            0%, 100% { transform: translateX(0)    scaleX(1);    opacity: 0.9; }
            33%      { transform: translateX(1.5%) scaleX(1.02); opacity: 1;   }
            66%      { transform: translateX(-1%)  scaleX(0.98); opacity: 0.8; }
        }
        @keyframes pr-fire-ember {
            0%, 100% { opacity: 0.45; }
            40%      { opacity: 0.8; }
            70%      { opacity: 0.55; }
        }
        @keyframes pr-fire-glow {
            0%, 100% { box-shadow: 0 0 18px 6px rgba(255, 50, 0, 0.65), 0 0 40px 14px rgba(255, 90, 0, 0.35); }
            50%      { box-shadow: 0 0 28px 10px rgba(255, 70, 0, 0.8), 0 0 55px 20px rgba(255, 120, 0, 0.45); }
        }
        @keyframes pr-fire-badge-in {
            from { transform: scale(0.7); opacity: 0; }
            to   { transform: scale(1);   opacity: 1; }
        }
    `;
    document.head.appendChild(s);
}

export function useFireOverlay(level) {
    useEffect(() => {
        if (typeof document === 'undefined') return;
        ensureFireKeyframes();
        const existing = document.getElementById(FIRE_OVERLAY_ID);
        if (level === 0) {
            existing?.remove();
            return;
        }

        const el = existing || (() => {
            const d = document.createElement('div');
            d.id = FIRE_OVERLAY_ID;
            document.body.appendChild(d);
            return d;
        })();

        const a1 = Math.min(0.58 + level * 0.05, 0.78);
        const a2 = Math.min(0.32 + level * 0.04, 0.52);
        el.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:9998;';
        el.innerHTML = `
            <div style="position:absolute;inset:0;
                background:
                    radial-gradient(ellipse at 50% 120%, rgba(255,45,0,${a1}) 0%, rgba(255,105,0,${a2}) 24%, rgba(160,22,0,0.09) 52%, transparent 74%),
                    radial-gradient(ellipse at 18% 114%, rgba(255,60,0,${a2 * 0.8}) 0%, transparent 35%),
                    radial-gradient(ellipse at 82% 114%, rgba(255,60,0,${a2 * 0.8}) 0%, transparent 35%);
                animation: pr-fire-pulse 1.9s ease-in-out infinite;"></div>
            <div style="position:absolute;inset:0;
                background: radial-gradient(ellipse at 50% 118%, rgba(255,25,0,0.28) 0%, transparent 48%);
                animation: pr-fire-wave 2.4s ease-in-out infinite;"></div>
            <div style="position:absolute;bottom:0;left:0;right:0;height:40vh;
                background: linear-gradient(to top, rgba(200,15,0,0.55) 0%, rgba(255,70,0,0.22) 35%, transparent 80%);
                animation: pr-fire-ember 2.9s ease-in-out infinite;"></div>
            <div style="position:absolute;bottom:0;left:0;right:0;height:4px;
                background: rgba(255,35,0,0.95);
                animation: pr-fire-glow 1.7s ease-in-out infinite;"></div>
        `;

        return () => { document.getElementById(FIRE_OVERLAY_ID)?.remove(); };
    }, [level]);
}

export function FireBadge({ streak }) {
    if (streak === 0) return null;
    return (
        <div className="pr-fire-badge" key={streak}>
            <Flame size={14} aria-hidden="true" /> {streak}
        </div>
    );
}
