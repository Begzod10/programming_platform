import {
    normalizeExe, toIsoDate, defaultRange, daysInclusive, validateRange,
    sortRows, summarizeByStudent, summarizeAll, formatMinutes, formatTopApps, formatTime, MAX_ENTRIES,
} from '../views/teacher/pccontrol/pcReportMath';

describe('normalizeExe', () => {
    it('trims and lower-cases', () => {
        expect(normalizeExe('  Notepad.EXE ', [])).toEqual({ ok: true, value: 'notepad.exe' });
    });
    it('rejects empty', () => {
        expect(normalizeExe('   ', [])).toEqual({ ok: false, reason: 'empty' });
    });
    it('rejects a wrong extension', () => {
        expect(normalizeExe('a.txt', [])).toEqual({ ok: false, reason: 'ext' });
        expect(normalizeExe('.exe', [])).toEqual({ ok: false, reason: 'ext' });
    });
    it('rejects paths', () => {
        expect(normalizeExe('C:\\x\\a.exe', [])).toEqual({ ok: false, reason: 'path' });
        expect(normalizeExe('x/a.exe', [])).toEqual({ ok: false, reason: 'path' });
    });
    it('rejects duplicates', () => {
        expect(normalizeExe('A.exe', ['a.exe'])).toEqual({ ok: false, reason: 'dup' });
    });
    it('rejects past the maximum', () => {
        const many = Array.from({ length: MAX_ENTRIES }, (_, i) => `a${i}.exe`);
        expect(normalizeExe('new.exe', many)).toEqual({ ok: false, reason: 'max' });
    });
});

describe('dates', () => {
    it('toIsoDate uses local date parts', () => {
        expect(toIsoDate(new Date(2026, 9, 5, 23, 59))).toBe('2026-10-05');
    });
    it('defaultRange is the last 7 days ending today', () => {
        expect(defaultRange(new Date(2026, 9, 24, 12))).toEqual({ from: '2026-10-18', to: '2026-10-24' });
    });
    it('daysInclusive', () => {
        expect(daysInclusive('2026-10-18', '2026-10-24')).toBe(7);
        expect(daysInclusive('2026-10-18', '2026-10-18')).toBe(1);
        expect(daysInclusive('2026-10-24', '2026-10-18')).toBe(-6);
        expect(daysInclusive('2026-09-24', '2026-10-24')).toBe(31);
    });
    it('validateRange', () => {
        expect(validateRange('2026-10-18', '2026-10-24')).toBeNull();
        expect(validateRange('2026-09-24', '2026-10-24')).toBeNull();
        expect(validateRange('2026-09-23', '2026-10-24')).toBe('tooLong');
        expect(validateRange('2026-10-24', '2026-10-18')).toBe('order');
        expect(validateRange('', '2026-10-18')).toBe('invalid');
    });
});

const row = (o) => ({
    student_id: 1, full_name: 'Ali', date: '2026-10-20', quota_met: true, unlocked_at: null,
    minutes_locked: 10, minutes_unlocked: 20, top_apps: [], ...o,
});

describe('summaries', () => {
    const rows = [
        row({ date: '2026-10-20' }),
        row({ date: '2026-10-21', quota_met: false, minutes_locked: 5.5, minutes_unlocked: 1.25 }),
        row({ student_id: 2, full_name: 'Bobur', date: '2026-10-21' }),
    ];
    it('sortRows: date desc then name', () => {
        const s = sortRows(rows);
        expect(s.map(r => `${r.date}|${r.full_name}`)).toEqual([
            '2026-10-21|Ali', '2026-10-21|Bobur', '2026-10-20|Ali',
        ]);
        expect(rows[0].date).toBe('2026-10-20'); // input not mutated
    });
    it('summarizeByStudent', () => {
        expect(summarizeByStudent(rows)).toEqual([
            { student_id: 1, full_name: 'Ali', days: 2, metDays: 1, minutesLocked: 15.5, minutesUnlocked: 21.25, trend: '1/2' },
            { student_id: 2, full_name: 'Bobur', days: 1, metDays: 1, minutesLocked: 10, minutesUnlocked: 20, trend: '1/1' },
        ]);
    });
    it('summarizeAll', () => {
        expect(summarizeAll(rows)).toEqual({ students: 2, metDays: 2, totalDays: 3, percent: 67 });
    });
    it('zero rows', () => {
        expect(summarizeByStudent([])).toEqual([]);
        expect(summarizeAll([])).toEqual({ students: 0, metDays: 0, totalDays: 0, percent: 0 });
    });
});

describe('formatting', () => {
    it('formatMinutes uses one decimal', () => {
        expect(formatMinutes(42)).toBe('42.0');
        expect(formatMinutes(1.25)).toBe('1.3');
        expect(formatMinutes(null)).toBe('0.0');
    });
    it('formatTopApps', () => {
        expect(formatTopApps([{ app: 'code.exe', minutes: 42 }, { app: 'chrome.exe', minutes: 3.14 }], 'min'))
            .toBe('code.exe 42.0 min, chrome.exe 3.1 min');
        expect(formatTopApps([], 'min')).toBe('—');
        expect(formatTopApps(undefined, 'min')).toBe('—');
    });
    it('formatTime is HH:MM local or a dash', () => {
        expect(formatTime(new Date(2026, 9, 20, 9, 5).toISOString())).toBe('09:05');
        expect(formatTime(null)).toBe('—');
        expect(formatTime('garbage')).toBe('—');
    });
});
