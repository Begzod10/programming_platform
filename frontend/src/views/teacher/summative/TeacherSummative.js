import React, { useCallback, useEffect, useMemo, useState } from 'react';
import './TeacherSummative.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';

const errText = (e, fallback) => (e?.message || '').split(': ').pop() || fallback;
const LETTERS = ['A', 'B', 'C', 'D', 'E', 'F'];

/** /teacher/summative — build a summative test by ticking questions from the
 * course question banks, assign it to one of your groups, see the results. */
export default function TeacherSummative() {
    const { request } = useHttp();
    const jsonHeaders = () => ({ ...headers(), 'Content-Type': 'application/json' });

    const [sets, setSets] = useState([]);
    const [groups, setGroups] = useState([]);
    const [courses, setCourses] = useState([]);
    const [mode, setMode] = useState('list'); // list | create
    const [msg, setMsg] = useState('');

    // create form
    const [groupId, setGroupId] = useState('');
    const [title, setTitle] = useState('');
    const [minutes, setMinutes] = useState(30);
    const [courseId, setCourseId] = useState('');
    const [lessons, setLessons] = useState([]);
    const [loadingQs, setLoadingQs] = useState(false);
    const [picked, setPicked] = useState({}); // id -> question text (survives switching course)
    const [search, setSearch] = useState('');
    const [open, setOpen] = useState({}); // question ids with options expanded
    const [saving, setSaving] = useState(false);

    // results
    const [results, setResults] = useState(null);

    const loadSets = useCallback(() => {
        request(`${API_URL}v1/summative/teacher/sets`, 'GET', null, headers()).then(setSets).catch(() => {});
    }, [request]);

    useEffect(() => {
        loadSets();
        request(`${API_URL}v1/summative/teacher/groups`, 'GET', null, headers()).then(setGroups).catch(() => {});
        request(`${API_URL}v1/summative/teacher/courses`, 'GET', null, headers()).then(setCourses).catch(() => {});
    }, [request, loadSets]);

    useEffect(() => {
        if (!courseId) { setLessons([]); return; }
        setLoadingQs(true);
        request(`${API_URL}v1/summative/teacher/questions?course_id=${courseId}&lang=uz`, 'GET', null, headers())
            .then(setLessons)
            .catch(() => setLessons([]))
            .finally(() => setLoadingQs(false));
    }, [courseId, request]);

    const pickedCount = Object.keys(picked).length;

    const toggle = (q) => setPicked((p) => {
        const n = { ...p };
        if (n[q.id]) delete n[q.id]; else n[q.id] = q.text;
        return n;
    });
    const toggleLesson = (l, on) => setPicked((p) => {
        const n = { ...p };
        l.questions.forEach((q) => { if (on) n[q.id] = q.text; else delete n[q.id]; });
        return n;
    });

    const needle = search.trim().toLowerCase();
    const shown = useMemo(() => lessons
        .map((l) => ({ ...l, questions: needle ? l.questions.filter((q) => q.text.toLowerCase().includes(needle)) : l.questions }))
        .filter((l) => l.questions.length > 0), [lessons, needle]);

    const resetForm = () => {
        setTitle(''); setMinutes(30); setPicked({}); setSearch(''); setOpen({});
    };

    const save = async () => {
        setMsg('');
        if (!groupId) { setMsg('Guruhni tanlang.'); return; }
        if (!pickedCount) { setMsg('Kamida bitta savol belgilang.'); return; }
        setSaving(true);
        try {
            await request(`${API_URL}v1/summative/teacher/sets`, 'POST', JSON.stringify({
                group_id: Number(groupId), title: title.trim() || 'Summativ test',
                question_ids: Object.keys(picked).map(Number), minutes: Number(minutes) || 30,
            }), jsonHeaders());
            resetForm();
            setMode('list');
            loadSets();
            setMsg('Test guruhga biriktirildi. Talabalar uni endi ko\'radi.');
        } catch (e) {
            setMsg(errText(e, 'Saqlab bo\'lmadi.'));
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

                <div className="tsm-form">
                    <label>Guruh
                        <select value={groupId} onChange={(e) => setGroupId(e.target.value)}>
                            <option value="">— tanlang —</option>
                            {groups.map((g) => <option key={g.id} value={g.id}>{g.name} ({g.students} ta talaba)</option>)}
                        </select>
                    </label>
                    <label>Test nomi
                        <input value={title} maxLength={200} placeholder="Masalan: 1-chorak yakuniy" onChange={(e) => setTitle(e.target.value)} />
                    </label>
                    <label>Vaqt (daqiqa)
                        <input type="number" min={5} max={180} value={minutes} onChange={(e) => setMinutes(e.target.value)} />
                    </label>
                </div>

                <div className="tsm-form">
                    <label>Kurs (savollar banki)
                        <select value={courseId} onChange={(e) => setCourseId(e.target.value)}>
                            <option value="">— kursni tanlang —</option>
                            {courses.map((c) => <option key={c.id} value={c.id}>{c.title} ({c.questions} ta savol)</option>)}
                        </select>
                    </label>
                    <label>Qidirish
                        <input value={search} placeholder="Savol matnidan qidiring" onChange={(e) => setSearch(e.target.value)} />
                    </label>
                </div>
                <p className="tsm-muted">Savollarni bir necha kursdan ham belgilash mumkin: belgilanganlar kurs almashganda saqlanadi.</p>

                {loadingQs && <p className="tsm-muted">Yuklanmoqda…</p>}
                {!loadingQs && courseId && shown.length === 0 && <p className="tsm-muted">Savol topilmadi.</p>}

                <div className="tsm-lessons">
                    {shown.map((l) => {
                        const all = l.questions.every((q) => picked[q.id]);
                        return (
                            <div key={l.lesson_id} className="tsm-lesson">
                                <label className="tsm-lesson-head">
                                    <input type="checkbox" checked={all} onChange={(e) => toggleLesson(l, e.target.checked)} />
                                    <b>{l.title}</b>
                                    <span className="tsm-muted">{l.questions.filter((q) => picked[q.id]).length} / {l.questions.length}</span>
                                </label>
                                {l.questions.map((q) => (
                                    <div key={q.id} className={`tsm-q ${picked[q.id] ? 'is-on' : ''}`}>
                                        <label className="tsm-q-main">
                                            <input type="checkbox" checked={!!picked[q.id]} onChange={() => toggle(q)} />
                                            <span>{q.text}</span>
                                        </label>
                                        <button className="tsm-link" onClick={() => setOpen((o) => ({ ...o, [q.id]: !o[q.id] }))}>
                                            {open[q.id] ? 'Yopish' : 'Javoblar'}
                                        </button>
                                        {open[q.id] && (
                                            <ol className="tsm-opts">
                                                {q.options.map((o, i) => (
                                                    <li key={i} className={i === q.correct ? 'is-right' : ''}>{LETTERS[i]}. {o}</li>
                                                ))}
                                            </ol>
                                        )}
                                    </div>
                                ))}
                            </div>
                        );
                    })}
                </div>

                <div className="tsm-bar">
                    <span><b>{pickedCount}</b> ta savol belgilangan</span>
                    {pickedCount > 0 && <button className="tsm-link" onClick={() => setPicked({})}>Tozalash</button>}
                    <button className="tsm-btn tsm-btn--primary" disabled={saving || !pickedCount || !groupId} onClick={save}>
                        {saving ? 'Saqlanmoqda…' : 'Guruhga biriktirish'}
                    </button>
                </div>
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
                Savollarni o'zingiz belgilaysiz. Guruhdagi har bir talaba belgilangan savollarning hammasiga javob beradi
                (to'liq ekran rejimida, bir marta).
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
