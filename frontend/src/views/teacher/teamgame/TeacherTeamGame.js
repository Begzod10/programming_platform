import React, { useEffect, useState, useCallback, useRef } from 'react';
import { API_URL, API_URL_DOC, getToken } from '../../../api/search/base';
import axiosInstance from '../../../api/axiosInstance';
import './TeacherTeamGame.css';

const GAME_TYPE_LABELS = { team: 'Командная', individual: 'Индивидуальная' };
const STATUS_LABELS    = { pending: 'Ожидание', active: 'Активна', completed: 'Завершена' };

function wsUrl(sessionId) {
    const base = API_URL_DOC.replace(/^http/, 'ws').replace(/\/$/, '');
    const token = encodeURIComponent(getToken() || '');
    return `${base}/api/v1/game-sessions/${sessionId}/ws?token=${token}`;
}

// Keeps a WS alive for the given sessionId, calls onUpdate(data) on every push
function useSessionSocket(sessionId, onUpdate, onDeleted, onRawMessage) {
    const wsRef = useRef(null);
    const pingRef = useRef(null);
    const mountedRef = useRef(true);
    const reconnectRef = useRef(null);

    const connect = useCallback(() => {
        if (!sessionId || !mountedRef.current) return;
        const ws = new WebSocket(wsUrl(sessionId));
        wsRef.current = ws;

        ws.onmessage = (e) => {
            try {
                const msg = JSON.parse(e.data);
                if (msg.type === 'session_update') onUpdate(msg.data);
                if (msg.type === 'session_deleted' && onDeleted) onDeleted();
                if (onRawMessage) onRawMessage(msg);
            } catch {}
        };

        ws.onopen = () => {
            clearTimeout(reconnectRef.current);
            pingRef.current = setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) ws.send('ping');
            }, 25000);
        };

        ws.onclose = () => {
            clearInterval(pingRef.current);
            if (mountedRef.current) {
                reconnectRef.current = setTimeout(connect, 3000);
            }
        };

        ws.onerror = () => ws.close();
    }, [sessionId, onUpdate]);

    useEffect(() => {
        mountedRef.current = true;
        connect();
        return () => {
            mountedRef.current = false;
            clearTimeout(reconnectRef.current);
            clearInterval(pingRef.current);
            const ws = wsRef.current;
            wsRef.current = null;
            if (ws) ws.close();
        };
    }, [connect]);
}

function CreateSessionModal({ onClose, onCreated }) {
    const [form, setForm] = useState({ title: '', description: '', game_type: 'team', team_count: 2 });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const submit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            const res = await axiosInstance.post(`${API_URL}v1/game-sessions`, {
                title: form.title,
                description: form.description || null,
                game_type: form.game_type,
                team_count: Number(form.team_count),
            });
            onCreated(res.data);
            onClose();
        } catch (err) {
            setError(err.response?.data?.detail || err.response?.data?.error?.message || 'Ошибка');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="tg-modal-overlay" onClick={onClose}>
            <div className="tg-modal" onClick={e => e.stopPropagation()}>
                <h2>Новая игровая сессия</h2>
                {error && <p className="tg-error">{error}</p>}
                <form onSubmit={submit} className="tg-form">
                    <label>Название *</label>
                    <input required value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="Название сессии" />

                    <label>Описание</label>
                    <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} rows={2} placeholder="Необязательно" />

                    <label>Тип игры</label>
                    <select value={form.game_type} onChange={e => setForm(f => ({ ...f, game_type: e.target.value }))}>
                        <option value="team">👥 Командная</option>
                        <option value="individual">🧑 Индивидуальная</option>
                    </select>

                    {form.game_type === 'team' && (
                        <>
                            <label>Количество команд (2–10)</label>
                            <input type="number" min={2} max={10} value={form.team_count}
                                onChange={e => setForm(f => ({ ...f, team_count: e.target.value }))} />
                        </>
                    )}

                    <div className="tg-modal-actions">
                        <button type="button" className="tg-btn-secondary" onClick={onClose}>Отмена</button>
                        <button type="submit" className="tg-btn-primary" disabled={loading}>
                            {loading ? 'Создаём...' : 'Создать'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}



// ── Start Session Modal (student picker + team assignment) ────────────────────
function StartModal({ session, onClose, onStarted }) {
    const [step, setStep] = useState(1); // 1 = pick students, 2 = assign teams
    const [students, setStudents] = useState([]);
    const [selected, setSelected] = useState(new Set());
    const [loading, setLoading] = useState(true);
    const [starting, setStarting] = useState(false);
    const [error, setError] = useState('');
    const [filterGroup, setFilterGroup] = useState('');
    // Step 2: teamId -> student objects
    const [assignments, setAssignments] = useState({});

    useEffect(() => {
        axiosInstance.get(`${API_URL}v1/game-sessions/${session.id}/students`)
            .then(r => {
                const list = Array.isArray(r.data) ? r.data : [];
                setStudents(list);
                setSelected(new Set(list.map(s => s.id)));
            })
            .catch(() => setError('Не удалось загрузить студентов'))
            .finally(() => setLoading(false));
    }, [session.id]);

    // When group filter changes, update selection to only that group
    useEffect(() => {
        if (!students.length) return;
        if (filterGroup) {
            const ids = students.filter(s => s.group_id === Number(filterGroup)).map(s => s.id);
            setSelected(new Set(ids));
        } else {
            setSelected(new Set(students.map(s => s.id)));
        }
    }, [filterGroup]); // eslint-disable-line react-hooks/exhaustive-deps

    const groups = students.reduce((acc, s) => {
        if (s.group_id && !acc.find(g => g.id === s.group_id)) {
            acc.push({ id: s.group_id, name: s.group_name });
        }
        return acc;
    }, []);

    const visible = filterGroup
        ? students.filter(s => s.group_id === Number(filterGroup))
        : students;

    const toggle = (id) => setSelected(prev => {
        const next = new Set(prev);
        next.has(id) ? next.delete(id) : next.add(id);
        return next;
    });

    const toggleVisible = () => {
        const visibleIds = visible.map(s => s.id);
        const allChecked = visibleIds.every(id => selected.has(id));
        setSelected(prev => {
            const next = new Set(prev);
            if (allChecked) visibleIds.forEach(id => next.delete(id));
            else visibleIds.forEach(id => next.add(id));
            return next;
        });
    };

    const visibleAllChecked = visible.length > 0 && visible.every(s => selected.has(s.id));

    // Build auto-distributed assignments and go to step 2
    const goToAssign = () => {
        if (selected.size === 0) { setError('Выберите хотя бы одного студента'); return; }
        setError('');
        const selectedStudents = students.filter(s => selected.has(s.id));
        const teams = session.teams;
        const init = {};
        teams.forEach(t => { init[t.id] = []; });
        selectedStudents.forEach((s, i) => { init[teams[i % teams.length].id].push(s); });
        setAssignments(init);
        setStep(2);
    };

    const moveStudent = (studentId, toTeamId) => {
        setAssignments(prev => {
            const next = {};
            Object.keys(prev).forEach(tid => { next[Number(tid)] = prev[tid].filter(s => s.id !== studentId); });
            const student = students.find(s => s.id === studentId);
            if (student) next[toTeamId] = [...(next[toTeamId] || []), student];
            return next;
        });
    };

    const shuffleAssignments = () => {
        const all = Object.values(assignments).flat().sort(() => Math.random() - 0.5);
        const teams = session.teams;
        const next = {};
        teams.forEach(t => { next[t.id] = []; });
        all.forEach((s, i) => { next[teams[i % teams.length].id].push(s); });
        setAssignments(next);
    };

    const start = async (overrideBody) => {
        setStarting(true); setError('');
        try {
            const body = overrideBody || {
                team_assignments: session.teams.map(t => ({
                    team_id: t.id,
                    student_ids: (assignments[t.id] || []).map(s => s.id),
                })),
            };
            await axiosInstance.post(`${API_URL}v1/game-sessions/${session.id}/start`, body);
            onStarted();
            onClose();
        } catch (err) {
            const msg = err.response?.data?.detail || 'Ошибка запуска';
            if (err.response?.status === 400 && msg.toLowerCase().includes('already started')) { onStarted(); onClose(); return; }
            setError(msg);
        } finally { setStarting(false); }
    };

    // Individual games don't split students into teams — each student plays alone.
    const startIndividual = () => {
        if (selected.size === 0) { setError('Выберите хотя бы одного студента'); return; }
        start({ student_ids: Array.from(selected) });
    };

    const isIndividual = session.game_type === 'individual';

    // ── Step 1: pick students ──
    if (step === 1) return (
        <div className="tg-modal-overlay" onClick={onClose}>
            <div className="tg-modal tg-start-modal" onClick={e => e.stopPropagation()}>
                <div className="tg-divide-header">
                    <h2>Выбор студентов</h2>
                    <button className="tg-btn-secondary" onClick={toggleVisible}>
                        {visibleAllChecked ? 'Снять все' : 'Выбрать все'}
                    </button>
                </div>
                {groups.length > 0 && (
                    <div style={{ marginBottom: '0.75rem' }}>
                        <select
                            className="tg-course-filter-select"
                            value={filterGroup}
                            onChange={e => setFilterGroup(e.target.value)}
                        >
                            <option value="">— Все группы ({students.length} студ.) —</option>
                            {groups.map(g => (
                                <option key={g.id} value={g.id}>
                                    {g.name} ({students.filter(s => s.group_id === g.id).length} студ.)
                                </option>
                            ))}
                        </select>
                    </div>
                )}
                {error && <p className="tg-error">{error}</p>}
                {loading ? (
                    <div className="tg-loading">Загрузка...</div>
                ) : (
                    <div className="tg-student-pick-list">
                        {visible.map(s => {
                            const name = s.full_name || s.username || '?';
                            const checked = selected.has(s.id);
                            return (
                                <label key={s.id} className={`tg-student-pick-row${checked ? ' tg-student-pick-row--on' : ''}`}>
                                    <input type="checkbox" checked={checked} onChange={() => toggle(s.id)} />
                                    <span className="tg-student-pick-avatar">{name[0].toUpperCase()}</span>
                                    <span className="tg-student-pick-name">{name}</span>
                                </label>
                            );
                        })}
                    </div>
                )}
                <div className="tg-modal-actions">
                    <span className="tg-pick-count">{selected.size} выбрано</span>
                    <button className="tg-btn-secondary" onClick={onClose}>Отмена</button>
                    {isIndividual ? (
                        <button className="tg-btn-primary" disabled={loading || starting || selected.size === 0} onClick={startIndividual}>
                            {starting ? 'Запуск...' : '▶ Начать игру'}
                        </button>
                    ) : (
                        <button className="tg-btn-primary" disabled={loading || selected.size === 0} onClick={goToAssign}>
                            Распределить по командам →
                        </button>
                    )}
                </div>
            </div>
        </div>
    );

    // ── Step 2: assign to teams (team games only) ──
    const teams = session.teams;
    const totalAssigned = Object.values(assignments).reduce((s, arr) => s + arr.length, 0);
    return (
        <div className="tg-modal-overlay" onClick={onClose}>
            <div className="tg-modal tg-assign-modal" onClick={e => e.stopPropagation()}>
                <div className="tg-divide-header">
                    <h2>Распределение по командам</h2>
                    <button className="tg-btn-secondary" onClick={shuffleAssignments}>🔀 Случайно</button>
                </div>
                {error && <p className="tg-error">{error}</p>}
                <div className="tg-team-assign-grid">
                    {teams.map(team => {
                        const members = assignments[team.id] || [];
                        return (
                            <div key={team.id} className="tg-team-assign-col" style={{ borderTopColor: team.color }}>
                                <div className="tg-team-assign-col-head" style={{ color: team.color }}>
                                    {team.name} <span className="tg-team-count">({members.length})</span>
                                </div>
                                <div className="tg-team-assign-members">
                                    {members.map(s => {
                                        const name = s.full_name || s.username || '?';
                                        return (
                                            <div key={s.id} className="tg-team-assign-member">
                                                <span className="tg-student-pick-avatar tg-student-pick-avatar--sm">{name[0].toUpperCase()}</span>
                                                <span className="tg-team-assign-name">{name}</span>
                                                <select
                                                    className="tg-team-move-select"
                                                    value={team.id}
                                                    onChange={e => moveStudent(s.id, parseInt(e.target.value))}
                                                >
                                                    {teams.map(t => (
                                                        <option key={t.id} value={t.id}>{t.name}</option>
                                                    ))}
                                                </select>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        );
                    })}
                </div>
                <div className="tg-modal-actions">
                    <span className="tg-pick-count">{totalAssigned} студ.</span>
                    <button className="tg-btn-secondary" onClick={() => setStep(1)}>← Назад</button>
                    <button className="tg-btn-primary" disabled={starting || totalAssigned === 0} onClick={start}>
                        {starting ? 'Запуск...' : '▶ Начать игру'}
                    </button>
                </div>
            </div>
        </div>
    );
}

// ── Quiz Question Manager ─────────────────────────────────────────────────────
const OPTION_LABELS = ['A', 'B', 'C', 'D'];

function ImportFromLessonModal({ session, onClose, onImported, addedLessonIds, onLessonAdded }) {
    const [lessons, setLessons] = useState([]);
    const [loading, setLoading] = useState(true);
    const [importingId, setImportingId] = useState(null);
    const [importingCourse, setImportingCourse] = useState(false);
    const [successMsg, setSuccessMsg] = useState('');
    const [selectedCourseId, setSelectedCourseId] = useState(session.course_id || '');

    useEffect(() => {
        axiosInstance.get(`${API_URL}v1/lessons-with-questions`)
            .then(r => {
                const data = Array.isArray(r.data) ? r.data : [];
                setLessons(data);
            })
            .catch(() => {})
            .finally(() => setLoading(false));
    }, []);

    const courses = lessons.reduce((acc, l) => {
        if (l.course_id && !acc.find(c => c.id === l.course_id)) {
            acc.push({ id: l.course_id, title: l.course_title });
        }
        return acc;
    }, []);

    const visibleLessons = selectedCourseId
        ? lessons.filter(l => l.course_id === Number(selectedCourseId))
        : lessons;

    const importLesson = async (lessonId) => {
        if (addedLessonIds.has(lessonId)) return;
        setImportingId(lessonId);
        setSuccessMsg('');
        try {
            const res = await axiosInstance.post(
                `${API_URL}v1/game-sessions/${session.id}/import-questions?lesson_id=${lessonId}`
            );
            onLessonAdded(lessonId);
            onImported(res.data.length);
            setSuccessMsg(`+${res.data.length} вопросов добавлено`);
        } catch (err) {
            alert(err.response?.data?.detail || 'Ошибка');
        } finally { setImportingId(null); }
    };

    const importCourse = async (courseId) => {
        setImportingCourse(true);
        setSuccessMsg('');
        try {
            const res = await axiosInstance.post(
                `${API_URL}v1/game-sessions/${session.id}/import-questions?course_id=${courseId}`
            );
            visibleLessons.forEach(l => onLessonAdded(l.id));
            onImported(res.data.length);
            setSuccessMsg(`+${res.data.length} вопросов добавлено из курса`);
        } catch (err) {
            alert(err.response?.data?.detail || 'Ошибка');
        } finally { setImportingCourse(false); }
    };

    const selectedCourseTotal = visibleLessons.reduce((s, l) => s + l.question_count, 0);
    const isImporting = importingId !== null || importingCourse;

    return (
        <div className="tg-modal-overlay" onClick={onClose}>
            <div className="tg-modal" onClick={e => e.stopPropagation()}>
                <h2>📚 Импортировать вопросы</h2>
                {successMsg && (
                    <p className="tg-import-success">{successMsg}</p>
                )}
                {loading ? (
                    <p>Загрузка уроков...</p>
                ) : lessons.length === 0 ? (
                    <p style={{ color: '#6b7280' }}>Нет уроков с вопросами.</p>
                ) : (
                    <>
                        <div style={{ marginBottom: '0.75rem' }}>
                            <select
                                className="tg-course-filter-select"
                                value={selectedCourseId}
                                onChange={e => setSelectedCourseId(e.target.value)}
                            >
                                <option value="">— Все курсы —</option>
                                {courses.map(c => (
                                    <option key={c.id} value={c.id}>{c.title}</option>
                                ))}
                            </select>
                        </div>
                        {selectedCourseId && (
                            <button
                                className="tg-btn-primary tg-import-all-btn"
                                disabled={isImporting}
                                onClick={() => importCourse(selectedCourseId)}
                            >
                                🗂 Весь курс ({selectedCourseTotal} вопросов)
                            </button>
                        )}
                        <p style={{ color: '#6b7280', marginBottom: '0.5rem', fontSize: '0.85rem' }}>
                            Выберите урок для импорта:
                        </p>
                        <div className="tg-import-lessons-list">
                            {visibleLessons.map(l => {
                                const already = addedLessonIds.has(l.id);
                                return (
                                    <div key={l.id} className="tg-import-lesson-row">
                                        <div>
                                            <span className="tg-import-lesson-title">{l.title}</span>
                                            {!selectedCourseId && l.course_title && (
                                                <span className="tg-import-lesson-course">{l.course_title}</span>
                                            )}
                                            <span className="tg-import-lesson-count">{l.question_count} вопр.</span>
                                        </div>
                                        {already ? (
                                            <span className="tg-import-added-badge">✓ Добавлено</span>
                                        ) : (
                                            <button
                                                className="tg-btn-secondary tg-btn-sm"
                                                disabled={isImporting}
                                                onClick={() => importLesson(l.id)}
                                            >
                                                {importingId === l.id ? '...' : '+ Добавить'}
                                            </button>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </>
                )}
                <div className="tg-modal-actions">
                    <button className="tg-btn-secondary" onClick={onClose}>Закрыть</button>
                </div>
            </div>
        </div>
    );
}

function QuizManager({ session }) {
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAdd, setShowAdd] = useState(false);
    const [showImport, setShowImport] = useState(false);
    const [addedLessonIds, setAddedLessonIds] = useState(new Set());
    const [form, setForm] = useState({ question_text: '', options: ['', '', '', ''], correct_option: 0, time_limit: 30, points: 1000 });
    const [saving, setSaving] = useState(false);
    const [actionId, setActionId] = useState(null);
    const [progress, setProgress] = useState({}); // question_id → {answered, total}

    const loadQuestions = useCallback(() => {
        axiosInstance.get(`${API_URL}v1/game-sessions/${session.id}/questions`)
            .then(r => setQuestions(Array.isArray(r.data) ? r.data : []))
            .catch(() => {})
            .finally(() => setLoading(false));
    }, [session.id]);

    useEffect(() => { loadQuestions(); }, [loadQuestions]);

    // Listen for progress updates on existing WS connection
    useEffect(() => {
        const handler = (e) => {
            try {
                const msg = JSON.parse(e.data);
                if (msg.type === 'question_progress') {
                    setProgress(prev => ({ ...prev, [msg.data.question_id]: msg.data }));
                }
                if (msg.type === 'question_end') {
                    loadQuestions();
                    setProgress(prev => { const n = { ...prev }; delete n[msg.data.question_id]; return n; });
                }
            } catch {}
        };
        window.addEventListener('tg_ws_message', handler);
        return () => window.removeEventListener('tg_ws_message', handler);
    }, [loadQuestions]);

    const saveQuestion = async (e) => {
        e.preventDefault();
        if (form.options.some(o => !o.trim())) { alert('Заполните все варианты'); return; }
        setSaving(true);
        try {
            await axiosInstance.post(`${API_URL}v1/game-sessions/${session.id}/questions`, {
                ...form, options: form.options.map(o => o.trim()),
            });
            setShowAdd(false);
            setForm({ question_text: '', options: ['', '', '', ''], correct_option: 0, time_limit: 30, points: 1000 });
            loadQuestions();
        } catch (err) {
            alert(err.response?.data?.detail || 'Ошибка');
        } finally { setSaving(false); }
    };

    const deleteQuestion = async (qid) => {
        if (!window.confirm('Удалить вопрос?')) return;
        await axiosInstance.delete(`${API_URL}v1/game-sessions/${session.id}/questions/${qid}`).catch(() => {});
        loadQuestions();
    };

    const activateQuestion = async (qid) => {
        setActionId(qid);
        try {
            await axiosInstance.post(`${API_URL}v1/game-sessions/${session.id}/questions/${qid}/activate`);
            loadQuestions();
        } catch (err) {
            alert(err.response?.data?.detail || 'Ошибка');
        } finally { setActionId(null); }
    };

    const revealQuestion = async (qid) => {
        setActionId(qid);
        try {
            await axiosInstance.post(`${API_URL}v1/game-sessions/${session.id}/questions/${qid}/reveal`);
            loadQuestions();
        } catch (err) {
            alert(err.response?.data?.detail || 'Ошибка');
        } finally { setActionId(null); }
    };

    const setOption = (idx, val) => setForm(f => { const opts = [...f.options]; opts[idx] = val; return { ...f, options: opts }; });

    return (
        <div className="tg-quiz-manager">
            {session.auto_mode && (
                <div className="tg-auto-info-banner">
                    ⚡ Авто режим активен — студенты проходят вопросы самостоятельно в своём случайном порядке. Следите за счётом на вкладке «Лидеры».
                </div>
            )}
            <div className="tg-quiz-header">
                <h4>📝 Вопросы ({questions.length})</h4>
                {session.status !== 'completed' && !session.auto_mode && (
                    <div style={{ display: 'flex', gap: '0.4rem' }}>
                        <button className="tg-btn-secondary tg-btn-sm" onClick={() => setShowImport(true)}>
                            📚 Из урока
                        </button>
                        <button className="tg-btn-secondary tg-btn-sm" onClick={() => setShowAdd(v => !v)}>
                            {showAdd ? '✕ Отмена' : '+ Вопрос'}
                        </button>
                    </div>
                )}
            </div>

            {showImport && (
                <ImportFromLessonModal
                    session={session}
                    onClose={() => setShowImport(false)}
                    onImported={(count) => { loadQuestions(); }}
                    addedLessonIds={addedLessonIds}
                    onLessonAdded={(lessonId) => setAddedLessonIds(prev => new Set([...prev, lessonId]))}
                />
            )}

            {showAdd && (
                <form className="tg-quiz-add-form" onSubmit={saveQuestion}>
                    <textarea
                        required placeholder="Текст вопроса"
                        value={form.question_text}
                        onChange={e => setForm(f => ({ ...f, question_text: e.target.value }))}
                        rows={2}
                    />
                    <div className="tg-quiz-options-grid">
                        {form.options.map((opt, i) => (
                            <div key={i} className={`tg-quiz-option-row${form.correct_option === i ? ' tg-quiz-option-row--correct' : ''}`}>
                                <button type="button" className="tg-quiz-letter" onClick={() => setForm(f => ({ ...f, correct_option: i }))}>
                                    {OPTION_LABELS[i]}
                                </button>
                                <input
                                    required placeholder={`Вариант ${OPTION_LABELS[i]}`}
                                    value={opt} onChange={e => setOption(i, e.target.value)}
                                />
                            </div>
                        ))}
                    </div>
                    <div className="tg-quiz-meta-row">
                        <label>⏱ {form.time_limit}с
                            <input type="range" min={5} max={120} step={5} value={form.time_limit}
                                onChange={e => setForm(f => ({ ...f, time_limit: Number(e.target.value) }))} />
                        </label>
                        <label>⭐ {form.points} очков
                            <input type="range" min={100} max={5000} step={100} value={form.points}
                                onChange={e => setForm(f => ({ ...f, points: Number(e.target.value) }))} />
                        </label>
                    </div>
                    <div className="tg-modal-actions">
                        <button type="submit" className="tg-btn-primary" disabled={saving}>{saving ? 'Сохранение...' : '💾 Сохранить'}</button>
                    </div>
                </form>
            )}

            {loading ? <div className="tg-quiz-loading">Загрузка...</div> : (
                <div className="tg-quiz-list">
                    {questions.length === 0 && !showAdd && (
                        <p className="tg-quiz-empty">Нет вопросов. Добавьте хотя бы один перед запуском!</p>
                    )}
                    {questions.map((q, idx) => {
                        const prog = progress[q.id];
                        return (
                            <div key={q.id} className={`tg-quiz-item tg-quiz-item--${q.status}`}>
                                <div className="tg-quiz-item-header">
                                    <span className="tg-quiz-num">#{idx + 1}</span>
                                    <span className="tg-quiz-text">{q.question_text}</span>
                                    <div className="tg-quiz-item-meta">
                                        <span>⏱{q.time_limit}с</span>
                                        <span>⭐{q.points}</span>
                                        <span className={`tg-quiz-status tg-quiz-status--${q.status}`}>
                                            {q.status === 'pending' ? '○ Ожидание' : q.status === 'active' ? '● Активен' : '✓ Раскрыт'}
                                        </span>
                                    </div>
                                </div>
                                <div className="tg-quiz-opts-preview">
                                    {q.options.map((opt, i) => (
                                        <span key={i} className={`tg-quiz-opt-chip${i === q.correct_option ? ' tg-quiz-opt-chip--correct' : ''}`}>
                                            {OPTION_LABELS[i]}: {opt}
                                        </span>
                                    ))}
                                </div>
                                {prog && (
                                    <div className="tg-quiz-progress">
                                        <div className="tg-quiz-progress-bar" style={{ width: `${prog.total_players ? (prog.answered_count / prog.total_players) * 100 : 0}%` }} />
                                        <span>{prog.answered_count}/{prog.total_players} ответили</span>
                                    </div>
                                )}
                                {session.status === 'active' && !session.auto_mode && (
                                    <div className="tg-quiz-item-actions">
                                        {q.status === 'pending' && (
                                            <button className="tg-btn-primary tg-btn-sm" disabled={actionId === q.id}
                                                onClick={() => activateQuestion(q.id)}>▶ Запустить</button>
                                        )}
                                        {q.status === 'active' && (
                                            <button className="tg-btn-success tg-btn-sm" disabled={actionId === q.id}
                                                onClick={() => revealQuestion(q.id)}>🔍 Раскрыть ответ</button>
                                        )}
                                        {q.status === 'revealed' && <span className="tg-quiz-done">✓ Завершён</span>}
                                    </div>
                                )}
                                {session.status !== 'completed' && q.status === 'pending' && (
                                    <button className="tg-quiz-delete" onClick={() => deleteQuestion(q.id)} title="Удалить">🗑</button>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}


// ── Session Card ──────────────────────────────────────────────────────────────
function SessionCard({ initialSession, onDeleted }) {
    const [session, setSession] = useState(initialSession);
    const [actionLoading, setActionLoading] = useState(false);
    const [showStart, setShowStart] = useState(false);
    const [view, setView] = useState('questions');

    const handleWsUpdate = useCallback((data) => {
        setSession(data);
    }, []);

    // Relay raw WS messages so QuizManager can listen; also apply score updates here
    const handleWsRaw = useCallback((msg) => {
        window.dispatchEvent(new MessageEvent('tg_ws_message', { data: JSON.stringify(msg) }));
        if (msg.type === 'question_end' && msg.data?.team_scores) {
            setSession(prev => ({
                ...prev,
                teams: (prev.teams || []).map(t => {
                    const ts = msg.data.team_scores.find(s => s.team_id === t.id);
                    return ts ? { ...t, score: ts.score } : t;
                }),
            }));
        }
        if (msg.type === 'auto_score_update' && msg.data?.team_scores) {
            setSession(prev => ({
                ...prev,
                teams: (prev.teams || []).map(t => {
                    const ts = msg.data.team_scores.find(s => s.team_id === t.id);
                    return ts ? { ...t, score: ts.score } : t;
                }),
            }));
        }
    }, []);

    useSessionSocket(session.id, handleWsUpdate, null, handleWsRaw);

    const act = async (path, method = 'post', body = null) => {
        setActionLoading(true);
        try {
            await axiosInstance({ method, url: `${API_URL}v1/game-sessions/${session.id}${path}`, data: body || undefined });
        } catch (err) {
            alert(err.response?.data?.detail || err.response?.data?.error?.message || 'Ошибка');
        } finally {
            setActionLoading(false);
        }
    };

    const sortedTeams = [...(session.teams || [])].sort((a, b) => b.score - a.score);

    return (
        <>
        <div className={`tg-card tg-card--${session.status}`}>
            <div className="tg-card-header">
                <div>
                    <h3>
                        {session.title}
                        <span className="tg-live-dot" title="Подключено в реальном времени" />
                    </h3>
                    <span className="tg-tag">{GAME_TYPE_LABELS[session.game_type]}</span>
                    <span className={`tg-status tg-status--${session.status}`}>{STATUS_LABELS[session.status]}</span>
                    {session.course_title && <span className="tg-tag tg-tag--course">📚 {session.course_title}</span>}
                </div>
                <div className="tg-card-actions">
                    {session.status === 'pending' && (
                        <button className="tg-btn-primary" disabled={actionLoading} onClick={() => setShowStart(true)}>
                            ▶ Старт
                        </button>
                    )}
                    {session.status === 'active' && !session.auto_mode && (
                        <button className="tg-btn-auto" disabled={actionLoading} onClick={async () => {
                            if (window.confirm('Включить авто режим? Каждый студент получит вопросы в случайном порядке и будет отвечать независимо.')) {
                                await act('/activate-auto');
                            }
                        }}>
                            ⚡ Авто режим
                        </button>
                    )}
                    {session.auto_mode && (
                        <span className="tg-auto-badge">⚡ Авто режим</span>
                    )}
                    {session.status === 'active' && (
                        <button className="tg-btn-success" disabled={actionLoading} onClick={() => act('/complete')}>
                            ✓ Завершить
                        </button>
                    )}
                    <button className="tg-btn-danger" disabled={actionLoading} onClick={async () => {
                        if (window.confirm('Удалить сессию?')) {
                            await act('', 'delete');
                            onDeleted(session.id);
                        }
                    }}>🗑</button>
                </div>
            </div>

            {session.description && <p className="tg-description">{session.description}</p>}

            {/* Tab switcher — always shown when there are participants */}
            {sortedTeams.length > 0 && (
                <div className="tg-view-tabs">
                    <button
                        className={`tg-view-tab${view === 'questions' ? ' tg-view-tab--active' : ''}`}
                        onClick={() => setView('questions')}
                    >📝 Вопросы ({(session.questions_count ?? 0) || 0})</button>
                    <button
                        className={`tg-view-tab${view === 'students' ? ' tg-view-tab--active' : ''}`}
                        onClick={() => setView('students')}
                    >{session.game_type === 'team' ? '👥 Команды' : '🏆 Лидеры'} ({sortedTeams.length})</button>
                </div>
            )}

            {/* Questions view */}
            {(!sortedTeams.length || view === 'questions') && <QuizManager session={session} />}

            {/* Students / Teams view */}
            {view === 'students' && sortedTeams.length > 0 && (
                <div className="tg-score-strip tg-score-strip--panel">
                    {sortedTeams.map((team, idx) => {
                        const top = sortedTeams[0]?.score || 0;
                        return (
                            <div key={team.id} className="tg-score-strip-item">
                                <span className="tg-score-strip-rank">{idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `${idx + 1}`}</span>
                                <span className="tg-score-strip-name" style={{ color: team.color }}>{team.name}</span>
                                <span className="tg-score-strip-val">{team.score}</span>
                                <div className="tg-score-strip-bar-wrap">
                                    <div className="tg-score-strip-bar" style={{
                                        width: top > 0 ? `${(team.score / top) * 100}%` : '0%',
                                        background: team.color,
                                    }} />
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Team members detail — team games only */}
            {view === 'students' && session.game_type === 'team' && sortedTeams.length > 0 && (
                <div className="tg-teams">
                    {sortedTeams.map((team, idx) => (
                        <div key={team.id} className="tg-team" style={{ '--team-color': team.color, borderTopColor: team.color }}>
                            <div className="tg-team-header">
                                <span className="tg-team-medal">{idx === 0 ? '🥇' : idx === 1 ? '🥈' : '🥉'}</span>
                                <span className="tg-team-name" style={{ color: team.color }}>{team.name}</span>
                                <span className="tg-team-score">{team.score} <small>очков</small></span>
                            </div>
                            <div className="tg-team-count">{team.members.length} участников</div>
                            <div className="tg-team-members">
                                {team.members.length === 0
                                    ? <span className="tg-no-members">Нет участников</span>
                                    : team.members.map(m => {
                                        const name = m.full_name || m.username || '?';
                                        const initials = name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase();
                                        return (
                                            <div key={m.id} className="tg-member-row" title={name}>
                                                <span className="tg-member-avatar" style={{ background: team.color + '22', color: team.color }}>{initials}</span>
                                                <span className="tg-member-name">{name}</span>
                                            </div>
                                        );
                                    })
                                }
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
        {showStart && (
            <StartModal
                session={session}
                onClose={() => setShowStart(false)}
                onStarted={async () => {
                    setShowStart(false);
                    try {
                        const res = await axiosInstance.get(`${API_URL}v1/game-sessions/${session.id}`);
                        setSession(res.data);
                    } catch {}
                }}
            />
        )}
        </>
    );
}

export default function TeacherTeamGame() {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);
    const [filter, setFilter] = useState('all');

    const load = useCallback(() => {
        setLoading(true);
        axiosInstance.get(`${API_URL}v1/game-sessions`)
            .then(r => setSessions(Array.isArray(r.data) ? r.data : []))
            .catch(() => setSessions([]))
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => { load(); }, [load]);

    const handleCreated = useCallback((newSession) => {
        setSessions(prev => [newSession, ...prev]);
    }, []);

    const filtered = filter === 'all' ? sessions : sessions.filter(s => s.status === filter);

    return (
        <div className="tg-page">
            <div className="tg-page-header">
                <div>
                    <h1>Командные игры</h1>
                    <p className="tg-subtitle">Создайте сессию — система случайно разобьёт студентов по командам. Обновления в реальном времени.</p>
                </div>
                <button className="tg-btn-primary tg-btn-lg" onClick={() => setShowCreate(true)}>
                    + Новая сессия
                </button>
            </div>

            <div className="tg-filters">
                {[['all', 'Все'], ['pending', 'Ожидание'], ['active', 'Активные'], ['completed', 'Завершённые']].map(([val, label]) => (
                    <button
                        key={val}
                        className={`tg-filter-btn${filter === val ? ' tg-filter-btn--active' : ''}`}
                        onClick={() => setFilter(val)}
                    >{label}</button>
                ))}
            </div>

            {loading ? (
                <div className="tg-loading">Загрузка...</div>
            ) : filtered.length === 0 ? (
                <div className="tg-empty">
                    <p>Нет сессий. Создайте первую!</p>
                </div>
            ) : (
                <div className="tg-sessions">
                    {filtered.map(s => (
                        <SessionCard
                            key={s.id}
                            initialSession={s}
                            onDeleted={(id) => setSessions(prev => prev.filter(x => x.id !== id))}
                        />
                    ))}
                </div>
            )}

            {showCreate && (
                <CreateSessionModal
                    onClose={() => setShowCreate(false)}
                    onCreated={handleCreated}
                />
            )}
        </div>
    );
}
