import { useState, useEffect, useMemo } from 'react';
import './ActivityAnalytics.css';
import { API_URL, headers } from '../../../api/search/base';

/* ── helpers ─────────────────────────────────────────────── */
const fmtTime = (sec) => {
    if (sec == null) return '—';
    if (sec < 60) return `${sec}s`;
    const m = Math.floor(sec / 60), s = sec % 60;
    return `${m}m ${s}s`;
};
const fmtMs = (ms) => {
    if (ms == null) return '—';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
};
const fmtDate = (iso) => {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
};

// Returns 'ok' | 'warn' | 'sus'
const projectFlag = (p) => {
    const t = p.time_spent_seconds ?? 9999;
    const paste = p.paste_count ?? 0;
    const keys  = p.keystroke_count ?? 9999;
    if (t < 60 || (paste > 3 && keys < 30)) return 'sus';
    if (t < 120 || (paste > 1 && keys < 80)) return 'warn';
    return 'ok';
};
const exerciseFlag = (e) => {
    const ms = e.time_spent_ms ?? 9999999;
    if (e.is_correct && ms < 3000) return 'sus';
    if (e.is_correct && ms < 8000) return 'warn';
    return 'ok';
};

const flagBadge = (flag) => {
    if (flag === 'sus')  return <span className="aa-badge aa-badge-red">⚠ Shubhali</span>;
    if (flag === 'warn') return <span className="aa-badge aa-badge-yellow">⚡ Tez</span>;
    return <span className="aa-badge aa-badge-green">✓ Normal</span>;
};

const timeColor = (sec, warnAt, badAt) => {
    if (sec == null) return '';
    if (sec < badAt)  return 'bad';
    if (sec < warnAt) return 'warn';
    return 'good';
};

/* ── Projects tab ────────────────────────────────────────── */
function ProjectsTab({ data }) {
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState('all');
    const [expanded, setExpanded] = useState({});

    const toggle = (id) => setExpanded(p => ({ ...p, [id]: !p[id] }));

    const rows = useMemo(() => {
        let r = data;
        if (search) {
            const q = search.toLowerCase();
            r = r.filter(p =>
                (p.student_name || '').toLowerCase().includes(q) ||
                (p.course_title || '').toLowerCase().includes(q) ||
                (p.lesson_title || '').toLowerCase().includes(q)
            );
        }
        if (filter !== 'all') r = r.filter(p => projectFlag(p) === filter);
        return r;
    }, [data, search, filter]);

    const counts = useMemo(() => ({
        total: data.length,
        sus:  data.filter(p => projectFlag(p) === 'sus').length,
        warn: data.filter(p => projectFlag(p) === 'warn').length,
        ok:   data.filter(p => projectFlag(p) === 'ok').length,
    }), [data]);

    return (
        <>
            <div className="aa-summary">
                <div className="aa-summary-card"><div className="val">{counts.total}</div><div className="lbl">Jami topshirilgan</div></div>
                <div className="aa-summary-card danger"><div className="val">{counts.sus}</div><div className="lbl">Shubhali</div></div>
                <div className="aa-summary-card warn"><div className="val">{counts.warn}</div><div className="lbl">Tez topshirilgan</div></div>
                <div className="aa-summary-card"><div className="val">{counts.ok}</div><div className="lbl">Normal</div></div>
            </div>

            <div className="aa-filters">
                <input
                    className="aa-search"
                    placeholder="Talaba yoki kurs qidirish..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                />
                <select className="aa-filter-select" value={filter} onChange={e => setFilter(e.target.value)}>
                    <option value="all">Barchasi</option>
                    <option value="sus">Shubhali</option>
                    <option value="warn">Tez topshirilgan</option>
                    <option value="ok">Normal</option>
                </select>
                <span className="aa-count">{rows.length} ta natija</span>
            </div>

            {rows.length === 0 ? (
                <div className="aa-empty">Ma'lumot topilmadi</div>
            ) : (
                <div className="aa-table-wrap">
                    <table className="aa-table">
                        <thead>
                            <tr>
                                <th>Talaba</th>
                                <th>Status</th>
                                <th>Vaqt</th>
                                <th>Klavish</th>
                                <th>Paste</th>
                                <th>Baholash</th>
                                <th>Tushuntirish</th>
                                <th>Sana</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map(p => {
                                const flag = projectFlag(p);
                                return (
                                    <tr key={p.project_id} className={`aa-row-${flag}`}>
                                        <td>
                                            <div className="aa-student">{p.student_name || '—'}</div>
                                            <div className="aa-course">{p.course_title} › {p.lesson_title}</div>
                                        </td>
                                        <td>
                                            <span className={`aa-badge ${p.status === 'Approved' ? 'aa-badge-green' : p.status === 'Rejected' ? 'aa-badge-red' : 'aa-badge-gray'}`}>
                                                {p.status}
                                            </span>
                                            {p.grade && <span className="aa-badge aa-badge-purple" style={{marginLeft: 4}}>{p.grade}</span>}
                                        </td>
                                        <td>
                                            <span className={`aa-metric-val ${timeColor(p.time_spent_seconds, 120, 60)}`}>
                                                {fmtTime(p.time_spent_seconds)}
                                            </span>
                                        </td>
                                        <td>
                                            <span className={`aa-metric-val ${p.keystroke_count != null && p.keystroke_count < 50 ? 'bad' : 'good'}`}>
                                                {p.keystroke_count ?? '—'}
                                            </span>
                                        </td>
                                        <td>
                                            <span className={`aa-metric-val ${p.paste_count > 2 ? 'bad' : p.paste_count > 0 ? 'warn' : 'good'}`}>
                                                {p.paste_count ?? '—'}
                                            </span>
                                        </td>
                                        <td>{flagBadge(flag)}</td>
                                        <td>
                                            {p.code_explanation ? (
                                                <>
                                                    <button className="aa-expand-btn" onClick={() => toggle(p.project_id)}>
                                                        {expanded[p.project_id] ? 'Yopish' : 'Ko\'rish'}
                                                    </button>
                                                    {expanded[p.project_id] && (
                                                        <div className="aa-explanation-box">{p.code_explanation}</div>
                                                    )}
                                                </>
                                            ) : <span style={{color:'rgba(0,0,0,0.3)', fontSize:12}}>Yo'q</span>}
                                        </td>
                                        <td className="aa-time">{fmtDate(p.submitted_at)}</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}
        </>
    );
}

/* ── Exercises tab ───────────────────────────────────────── */
function ExercisesTab({ data }) {
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState('all');

    const rows = useMemo(() => {
        let r = data;
        if (search) {
            const q = search.toLowerCase();
            r = r.filter(e =>
                (e.student_name || '').toLowerCase().includes(q) ||
                (e.course_title || '').toLowerCase().includes(q) ||
                (e.question || '').toLowerCase().includes(q)
            );
        }
        if (filter !== 'all') r = r.filter(e => exerciseFlag(e) === filter);
        return r;
    }, [data, search, filter]);

    const counts = useMemo(() => ({
        total: data.length,
        sus:  data.filter(e => exerciseFlag(e) === 'sus').length,
        warn: data.filter(e => exerciseFlag(e) === 'warn').length,
        ok:   data.filter(e => exerciseFlag(e) === 'ok').length,
    }), [data]);

    const msColor = (ms) => {
        if (ms == null) return '';
        if (ms < 3000)  return 'bad';
        if (ms < 8000)  return 'warn';
        return 'good';
    };

    return (
        <>
            <div className="aa-summary">
                <div className="aa-summary-card"><div className="val">{counts.total}</div><div className="lbl">Kuzatilgan javoblar</div></div>
                <div className="aa-summary-card danger"><div className="val">{counts.sus}</div><div className="lbl">Juda tez to'g'ri (&lt;3s)</div></div>
                <div className="aa-summary-card warn"><div className="val">{counts.warn}</div><div className="lbl">Tez (&lt;8s)</div></div>
                <div className="aa-summary-card"><div className="val">{counts.ok}</div><div className="lbl">Normal</div></div>
            </div>

            <div className="aa-filters">
                <input
                    className="aa-search"
                    placeholder="Talaba yoki savol qidirish..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                />
                <select className="aa-filter-select" value={filter} onChange={e => setFilter(e.target.value)}>
                    <option value="all">Barchasi</option>
                    <option value="sus">Shubhali (&lt;3s to'g'ri)</option>
                    <option value="warn">Tez (&lt;8s)</option>
                    <option value="ok">Normal</option>
                </select>
                <span className="aa-count">{rows.length} ta natija</span>
            </div>

            {rows.length === 0 ? (
                <div className="aa-empty">Ma'lumot topilmadi</div>
            ) : (
                <div className="aa-table-wrap">
                    <table className="aa-table">
                        <thead>
                            <tr>
                                <th>Talaba</th>
                                <th>Savol</th>
                                <th>Kurs</th>
                                <th>Tur</th>
                                <th>Sarflangan vaqt</th>
                                <th>To'g'ri?</th>
                                <th>Baholash</th>
                                <th>Sana</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map(e => {
                                const flag = exerciseFlag(e);
                                return (
                                    <tr key={e.submission_id} className={`aa-row-${flag}`}>
                                        <td>
                                            <div className="aa-student">{e.student_name || '—'}</div>
                                        </td>
                                        <td style={{maxWidth: 220}}>
                                            <div style={{fontSize:12, color:'#333', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', maxWidth:220}} title={e.question}>
                                                {e.question || '—'}
                                            </div>
                                        </td>
                                        <td>
                                            <div className="aa-course" style={{fontSize:12}}>{e.course_title || '—'}</div>
                                            <div style={{fontSize:11, color:'rgba(26,26,46,0.35)'}}>{e.lesson_title || ''}</div>
                                        </td>
                                        <td>
                                            <span className="aa-badge aa-badge-gray" style={{fontSize:10}}>
                                                {e.exercise_type?.replace('_', ' ') || '—'}
                                            </span>
                                        </td>
                                        <td>
                                            <span className={`aa-metric-val aa-time ${msColor(e.time_spent_ms)}`}>
                                                {fmtMs(e.time_spent_ms)}
                                            </span>
                                        </td>
                                        <td>
                                            {e.is_correct === true
                                                ? <span className="aa-badge aa-badge-green">✓ To'g'ri</span>
                                                : e.is_correct === false
                                                    ? <span className="aa-badge aa-badge-red">✗ Xato</span>
                                                    : <span className="aa-badge aa-badge-gray">—</span>
                                            }
                                        </td>
                                        <td>{flagBadge(flag)}</td>
                                        <td className="aa-time">{fmtDate(e.submitted_at)}</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}
        </>
    );
}

/* ── Main component ──────────────────────────────────────── */
export default function ActivityAnalytics() {
    const [tab, setTab]           = useState('projects');
    const [projects, setProjects] = useState([]);
    const [exercises, setExercises] = useState([]);
    const [loading, setLoading]   = useState(true);
    const [error, setError]       = useState('');

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            setError('');
            try {
                const [pRes, eRes] = await Promise.all([
                    fetch(`${API_URL}v1/teacher/activity/`, { headers: headers() }),
                    fetch(`${API_URL}v1/teacher/activity/exercises`, { headers: headers() }),
                ]);
                if (!pRes.ok || !eRes.ok) throw new Error('Server xatosi');
                const [pData, eData] = await Promise.all([pRes.json(), eRes.json()]);
                setProjects(Array.isArray(pData) ? pData : []);
                setExercises(Array.isArray(eData) ? eData : []);
            } catch (e) {
                setError("Ma'lumotlarni yuklashda xatolik: " + e.message);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    return (
        <div className="aa-page">
            <div className="aa-header">
                <div>
                    <h2>Faollik tahlili</h2>
                    <p>Loyihalar va mashqlar bo'yicha AI ishlatish ko'rsatkichlari</p>
                </div>
            </div>

            <div className="aa-tabs">
                <button className={`aa-tab ${tab === 'projects' ? 'active' : ''}`} onClick={() => setTab('projects')}>
                    📁 Loyihalar
                    {!loading && <span style={{marginLeft:6, opacity:0.7, fontSize:12}}>({projects.length})</span>}
                </button>
                <button className={`aa-tab ${tab === 'exercises' ? 'active' : ''}`} onClick={() => setTab('exercises')}>
                    📝 Mashqlar
                    {!loading && <span style={{marginLeft:6, opacity:0.7, fontSize:12}}>({exercises.length})</span>}
                </button>
            </div>

            {loading ? (
                <div className="aa-loading">⏳ Ma'lumotlar yuklanmoqda...</div>
            ) : error ? (
                <div className="aa-loading" style={{color:'#d63031'}}>{error}</div>
            ) : tab === 'projects' ? (
                <ProjectsTab data={projects} />
            ) : (
                <ExercisesTab data={exercises} />
            )}
        </div>
    );
}
