import React, { useCallback, useEffect, useState } from 'react';
import './TeacherSummative.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';

const errText = (e, fallback) => (e?.message || '').split(': ').pop() || fallback;

/** /teacher/summative — build a summative test by ticking questions from the
 * course question banks, assign it to one of your groups, see the results. */
export default function TeacherSummative() {
    const { request } = useHttp();
    const jsonHeaders = () => ({ ...headers(), 'Content-Type': 'application/json' });

    const [sets, setSets] = useState([]);
    const [groups, setGroups] = useState([]);
    const [mode, setMode] = useState('list'); // list | create
    const [msg, setMsg] = useState('');

    // create form
    const [groupId, setGroupId] = useState('');
    const [title, setTitle] = useState('');
    const [count, setCount] = useState(25);
    const [minutes, setMinutes] = useState(30);
    const [saving, setSaving] = useState(false);

    // results
    const [results, setResults] = useState(null);

    const loadSets = useCallback(() => {
        request(`${API_URL}v1/summative/teacher/sets`, 'GET', null, headers()).then(setSets).catch(() => {});
    }, [request]);

    useEffect(() => {
        loadSets();
        request(`${API_URL}v1/summative/teacher/groups`, 'GET', null, headers()).then(setGroups).catch(() => {});
    }, [request, loadSets]);

    // A group that already has a live test can't get a second one.
    const freeGroups = groups.filter((g) => !sets.some((x) => x.is_active && x.group_id === g.id));

    const save = async () => {
        setMsg('');
        if (!groupId) { setMsg('Sinfni (guruhni) tanlang.'); return; }
        setSaving(true);
        try {
            await request(`${API_URL}v1/summative/teacher/sets`, 'POST', JSON.stringify({
                group_id: Number(groupId), title: title.trim() || 'Summativ test',
                question_count: Number(count) || 25, minutes: Number(minutes) || 30,
            }), jsonHeaders());
            setTitle('');
            setMode('list');
            loadSets();
            setMsg("Test sinfga biriktirildi. Talabalar uni endi ko'radi.");
        } catch (e) {
            setMsg(errText(e, "Saqlab bo'lmadi."));
        } finally {
            setSaving(false);
        }
    };

    const setActive = async (s, on) => {
        try {
            await request(`${API_URL}v1/summative/teacher/sets/${s.id}`, 'PATCH', JSON.stringify({ is_active: on }), jsonHeaders());
            loadSets();
        } catch (e) { setMsg(errText(e, 'Xatolik.')); }
    };
    const remove = async (s) => {
        if (!window.confirm(`"${s.title}" testi o'chirilsinmi? Natijalar ham o'chadi.`)) return;
        try {
            await request(`${API_URL}v1/summative/teacher/sets/${s.id}`, 'DELETE', null, headers());
            loadSets();
        } catch (e) { setMsg(errText(e, 'Xatolik.')); }
    };
    const showResults = async (s) => {
        try {
            setResults(await request(`${API_URL}v1/summative/teacher/sets/${s.id}/results`, 'GET', null, headers()));
        } catch (e) { setMsg(errText(e, 'Xatolik.')); }
    };

    // ── results ──
    if (results) {
        const done = results.students.filter((s) => s.status === 'finished');
        return (
            <div className="tsm-page">
                <button className="tsm-link" onClick={() => setResults(null)}>← Orqaga</button>
                <h1>{results.title}</h1>
                <p className="tsm-muted">{results.count} ta savol · topshirgan: {done.length} / {results.students.length}</p>
                <div className="tsm-table">
                    <div className="tsm-tr tsm-th"><span>Talaba</span><span>Holati</span><span>To'g'ri</span><span>Ball</span><span>Qoidabuzarlik</span></div>
                    {results.students.map((s) => (
                        <div key={s.id} className="tsm-tr">
                            <span>{s.name}</span>
                            <span>{{ finished: 'Topshirdi', in_progress: 'Jarayonda', not_started: 'Boshlamagan' }[s.status]}
                                {s.finish_reason === 'violations' ? ' (qoidabuzarlik)' : s.finish_reason === 'time' ? ' (vaqt)' : ''}</span>
                            <span>{s.status === 'finished' ? `${s.correct} / ${s.total}` : '—'}</span>
                            <b className={s.score >= 60 ? 'is-pass' : s.score !== null ? 'is-fail' : ''}>{s.score !== null ? `${s.score}%` : '—'}</b>
                            <span>{s.violations || 0}</span>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    // ── create ──
    if (mode === 'create') {
        return (
            <div className="tsm-page">
                <button className="tsm-link" onClick={() => setMode('list')}>← Orqaga</button>
                <h1>Yangi summativ test</h1>
                {msg && <p className="tsm-note">{msg}</p>}
                <p className="tsm-muted">
                    Siz faqat savollar sonini belgilaysiz. Savollarni tizim o'zi tuzadi: har bir talaba uchun uning
                    shu chorakda tugatgan darslaridan (javoblar aralashtirilgan holda).
                </p>
                <div className="tsm-form">
                    <label>Sinf (guruh)
                        <select value={groupId} onChange={(e) => setGroupId(e.target.value)}>
                            <option value="">— tanlang —</option>
                            {freeGroups.map((g) => <option key={g.id} value={g.id}>{g.name} ({g.students} ta talaba)</option>)}
                        </select>
                    </label>
                    <label>Test nomi
                        <input value={title} maxLength={200} placeholder="Masalan: 1-chorak yakuniy" onChange={(e) => setTitle(e.target.value)} />
                    </label>
                </div>
                {groups.length > 0 && freeGroups.length === 0 && (
                    <p className="tsm-note">Hamma sinflarga test biriktirilgan. Yangisini yaratish uchun avval eskisini to'xtating yoki o'chiring.</p>
                )}
                <div className="tsm-form">
                    <label>Savollar soni
                        <input type="number" min={1} max={100} value={count} onChange={(e) => setCount(e.target.value)} />
                        <span className="tsm-quick">
                            {[10, 25, 50].map((n) => (
                                <button key={n} type="button" className={`tsm-chip ${Number(count) === n ? 'is-on' : ''}`} onClick={() => setCount(n)}>{n}</button>
                            ))}
                        </span>
                    </label>
                    <label>Vaqt (daqiqa)
                        <input type="number" min={5} max={180} value={minutes} onChange={(e) => setMinutes(e.target.value)} />
                    </label>
                </div>
                <button className="tsm-btn tsm-btn--primary" disabled={saving || !groupId} onClick={save}>
                    {saving ? 'Saqlanmoqda…' : 'Sinfga biriktirish'}
                </button>
            </div>
        );
    }

    // ── list ──
    return (
        <div className="tsm-page">
            <div className="tsm-head">
                <h1>Summativ testlar</h1>
                <button className="tsm-btn tsm-btn--primary" onClick={() => { setMsg(''); setMode('create'); }}>+ Yangi test</button>
            </div>
            <p className="tsm-muted">
                Siz sinf va savollar sonini belgilaysiz. Savollar har bir talaba uchun uning shu chorakda tugatgan
                darslaridan avtomatik tuziladi. Test to'liq ekran rejimida, bir marta topshiriladi.
            </p>
            {msg && <p className="tsm-note">{msg}</p>}
            {sets.length === 0 && <p className="tsm-muted">Hali test yaratilmagan.</p>}
            <div className="tsm-sets">
                {sets.map((s) => (
                    <div key={s.id} className={`tsm-set ${s.is_active ? '' : 'is-off'}`}>
                        <div className="tsm-set-main">
                            <b>{s.title}</b>
                            <span className="tsm-muted">
                                {s.group} · {s.count} ta savol · {s.minutes} daqiqa · topshirgan {s.finished}/{s.students}
                                {s.average !== null && ` · o'rtacha ${s.average}%`}
                            </span>
                        </div>
                        <span className={`tsm-badge ${s.is_active ? 'is-on' : ''}`}>{s.is_active ? 'Faol' : 'O\'chirilgan'}</span>
                        <button className="tsm-btn" onClick={() => showResults(s)}>Natijalar</button>
                        <button className="tsm-btn" onClick={() => setActive(s, !s.is_active)}>{s.is_active ? 'To\'xtatish' : 'Yoqish'}</button>
                        <button className="tsm-btn tsm-btn--danger" onClick={() => remove(s)}>O'chirish</button>
                    </div>
                ))}
            </div>
        </div>
    );
}
