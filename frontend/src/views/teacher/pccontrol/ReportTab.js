import React, { useState, useRef, useEffect } from 'react';
import { useHttp } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import { getReport } from './pcApi';
import { errorMessage } from './pcErrors';
import { pcStrings } from './pcStrings';
import {
    defaultRange, validateRange, sortRows, summarizeByStudent, summarizeAll,
    formatMinutes, formatTopApps, formatTime,
} from './pcReportMath';
import useMyGroups from './useMyGroups';

const RANGE_KEYS = { tooLong: 'rangeTooLong', order: 'rangeOrder', invalid: 'rangeInvalid' };

export default function ReportTab() {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const t = pcStrings(lang);
    const groups = useMyGroups(request);

    const [range, setRange] = useState(() => defaultRange());
    const [groupId, setGroupId] = useState('');
    const [rows, setRows] = useState(null);      // null = not loaded yet
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const seq = useRef(0);
    const alive = useRef(true);
    useEffect(() => () => { alive.current = false; }, []);

    const onLoad = async () => {
        const bad = validateRange(range.from, range.to);
        if (bad) { setError(t[RANGE_KEYS[bad]]); return; }
        const id = ++seq.current;
        setError(null);
        setLoading(true);
        try {
            const data = await getReport(request, {
                from: range.from, to: range.to, groupId: groupId === '' ? null : Number(groupId),
            });
            if (!alive.current || id !== seq.current) return;
            setRows(Array.isArray(data) ? data : []);
        } catch (e) {
            if (!alive.current || id !== seq.current) return;
            setRows(null);
            setError(errorMessage(e, t.reportError));
        } finally {
            if (alive.current && id === seq.current) setLoading(false);
        }
    };

    const sorted = rows ? sortRows(rows) : [];
    const all = summarizeAll(rows);
    const perStudent = summarizeByStudent(rows);

    return (
        <div className="pc-devices">
            <section className="pc-panel">
                <div className="pc-form-row">
                    <label className="pc-field-label">{t.dateFrom}
                        <input type="date" className="pc-input" aria-label={t.dateFrom} value={range.from}
                            onChange={e => setRange({ ...range, from: e.target.value })} />
                    </label>
                    <label className="pc-field-label">{t.dateTo}
                        <input type="date" className="pc-input" aria-label={t.dateTo} value={range.to}
                            onChange={e => setRange({ ...range, to: e.target.value })} />
                    </label>
                </div>
                <p className="pc-muted">{t.tzNote}</p>
                <div className="pc-form-row">
                    <select className="pc-select" aria-label={t.groupScope} value={groupId}
                        onChange={e => setGroupId(e.target.value)}>
                        <option value="">{t.allMyStudents}</option>
                        {groups.map(g => <option key={g.id} value={String(g.id)}>{g.name}</option>)}
                    </select>
                    <button type="button" className="pc-btn primary" disabled={loading} onClick={onLoad}>{t.load}</button>
                </div>
            </section>

            {error && <p className="pc-notice err" role="alert">{error}</p>}
            {loading && <p className="pc-muted" role="status">{t.loading}</p>}
            {rows && rows.length === 0 && !loading && <p className="pc-muted">{t.reportEmpty}</p>}

            {rows && rows.length > 0 && (
                <>
                    <section className="pc-panel pc-summary" data-testid="pc-report-summary">
                        <span>{t.sumStudents}: <strong>{all.students}</strong></span>
                        <span>{t.sumQuota}: <strong>{all.metDays}/{all.totalDays}</strong> ({all.percent}%)</span>
                    </section>

                    <section className="pc-panel">
                        <h3>{t.perStudent}</h3>
                        <div className="pc-trends">
                            {perStudent.map(s => (
                                <div key={s.student_id} className="pc-trend" data-testid={`pc-trend-${s.student_id}`}>
                                    <strong>{s.full_name}</strong>
                                    <span>{t.sumQuota}: <strong>{s.trend}</strong></span>
                                    <span className="pc-muted">
                                        {t.colLocked}: {formatMinutes(s.minutesLocked)} · {t.colUnlocked}: {formatMinutes(s.minutesUnlocked)}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </section>

                    <div className="pc-table-wrap">
                        <table className="pc-table" data-testid="pc-report-table">
                            <thead>
                                <tr>
                                    <th scope="col">{t.colDate}</th><th scope="col">{t.student}</th><th scope="col">{t.colQuota}</th><th scope="col">{t.colUnlock}</th>
                                    <th scope="col">{t.colLocked}</th><th scope="col">{t.colUnlocked}</th><th scope="col">{t.colApps}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {sorted.map(r => (
                                    <tr key={`${r.student_id}-${r.date}`} data-testid="pc-report-row">
                                        <td>{r.date}</td>
                                        <td>{r.full_name}</td>
                                        <td>
                                            {r.quota_met
                                                ? <span className="pc-ok" role="img" aria-label={t.quotaMetShort}>✓</span>
                                                : <span className="pc-no" role="img" aria-label={t.quotaMissed}>✗</span>}
                                        </td>
                                        <td>{formatTime(r.unlocked_at)}</td>
                                        <td>{formatMinutes(r.minutes_locked)}</td>
                                        <td>{formatMinutes(r.minutes_unlocked)}</td>
                                        <td>{formatTopApps(r.top_apps, t.min)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </>
            )}
        </div>
    );
}
