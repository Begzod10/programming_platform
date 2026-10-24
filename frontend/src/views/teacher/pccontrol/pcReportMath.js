// Pure helpers for the allowlist and report tabs.
export const MAX_ENTRIES = 200;
const DASH = '—';

export function normalizeExe(raw, existing = []) {
    const v = String(raw ?? '').trim().toLowerCase();
    if (!v) return { ok: false, reason: 'empty' };
    if (v.includes('/') || v.includes('\\')) return { ok: false, reason: 'path' };
    if (!v.endsWith('.exe') || v.length <= 4) return { ok: false, reason: 'ext' };
    if (existing.some(e => String(e).toLowerCase() === v)) return { ok: false, reason: 'dup' };
    if (existing.length >= MAX_ENTRIES) return { ok: false, reason: 'max' };
    return { ok: true, value: v };
}

const p2 = (n) => String(n).padStart(2, '0');
export const toIsoDate = (d) => `${d.getFullYear()}-${p2(d.getMonth() + 1)}-${p2(d.getDate())}`;

export function defaultRange(now = new Date()) {
    const from = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 6);
    return { from: toIsoDate(from), to: toIsoDate(now) };
}

const parse = (s) => {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || '');
    return m ? Date.UTC(+m[1], +m[2] - 1, +m[3]) : NaN;
};

// Inclusive day count; negative when `to` is before `from`; NaN if invalid.
export function daysInclusive(from, to) {
    const diff = Math.round((parse(to) - parse(from)) / 86400000);
    return diff >= 0 ? diff + 1 : diff;
}

export function validateRange(from, to) {
    const n = daysInclusive(from, to);
    if (Number.isNaN(n)) return 'invalid';
    if (n < 1) return 'order';
    if (n > 31) return 'tooLong';
    return null;
}

export function sortRows(rows) {
    return [...(rows || [])].sort((a, b) => {
        if (a.date !== b.date) return a.date < b.date ? 1 : -1;
        return String(a.full_name || '').localeCompare(String(b.full_name || ''));
    });
}

export function summarizeByStudent(rows) {
    const map = new Map();
    for (const r of rows || []) {
        let s = map.get(r.student_id);
        if (!s) {
            s = { student_id: r.student_id, full_name: r.full_name, days: 0, metDays: 0, minutesLocked: 0, minutesUnlocked: 0 };
            map.set(r.student_id, s);
        }
        s.days += 1;
        if (r.quota_met) s.metDays += 1;
        s.minutesLocked += Number(r.minutes_locked) || 0;
        s.minutesUnlocked += Number(r.minutes_unlocked) || 0;
    }
    return [...map.values()]
        .map(s => ({ ...s, trend: `${s.metDays}/${s.days}` }))
        .sort((a, b) => String(a.full_name || '').localeCompare(String(b.full_name || '')));
}

export function summarizeAll(rows) {
    const list = rows || [];
    const metDays = list.filter(r => r.quota_met).length;
    const totalDays = list.length;
    return {
        students: new Set(list.map(r => r.student_id)).size,
        metDays,
        totalDays,
        percent: totalDays ? Math.round((metDays / totalDays) * 100) : 0,
    };
}

export const formatMinutes = (m) => (Number(m) || 0).toFixed(1);

export function formatTopApps(apps, minLabel) {
    if (!Array.isArray(apps) || !apps.length) return DASH;
    return apps.map(a => `${a.app} ${formatMinutes(a.minutes)} ${minLabel}`).join(', ');
}

export function formatTime(iso) {
    if (!iso) return DASH;
    const d = new Date(iso);
    return Number.isNaN(d.getTime()) ? DASH : `${p2(d.getHours())}:${p2(d.getMinutes())}`;
}
