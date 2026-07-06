import React, { useEffect, useState, useCallback, useRef } from 'react';
import { API_URL, API_URL_DOC } from '../../../api/search/base';
import axiosInstance from '../../../api/axiosInstance';
import './TeacherTeamGame.css';

const GAME_TYPE_LABELS = { quiz: 'Викторина', coding: 'Кодинг', project: 'Проект', custom: 'Другое' };
const STATUS_LABELS    = { pending: 'Ожидание', active: 'Активна', completed: 'Завершена' };

function wsUrl(sessionId) {
    const base = API_URL_DOC.replace(/^http/, 'ws').replace(/\/$/, '');
    const token = encodeURIComponent(localStorage.getItem('token') || '');
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
    const [form, setForm] = useState({ title: '', description: '', game_type: 'quiz', team_count: 2, course_id: '' });
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        axiosInstance.get(`${API_URL}v1/courses?is_active=true&limit=100`)
            .then(r => setCourses(r.data.courses || r.data || []))
            .catch(() => {});
    }, []);

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
                course_id: form.course_id ? Number(form.course_id) : null,
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
                        {Object.entries(GAME_TYPE_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                    </select>

                    <label>Курс (необязательно)</label>
                    <select value={form.course_id} onChange={e => setForm(f => ({ ...f, course_id: e.target.value }))}>
                        <option value="">— Все студенты —</option>
                        {courses.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}
                    </select>

                    <label>Количество команд (2–10)</label>
                    <input type="number" min={2} max={10} value={form.team_count}
                        onChange={e => setForm(f => ({ ...f, team_count: e.target.value }))} />

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

// ── Divide Teams Modal ────────────────────────────────────────────────────────
function DivideTeamsModal({ session, onClose, onStarted }) {
    const [students, setStudents] = useState([]);
    const [assignments, setAssignments] = useState({}); // studentId → teamId
    const [loading, setLoading] = useState(true);
    const [starting, setStarting] = useState(false);
    const [error, setError] = useState('');

    const teams = session.teams || [];

    // Fetch available students
    useEffect(() => {
        axiosInstance.get(`${API_URL}v1/game-sessions/${session.id}/students`)
            .then(r => {
                const list = Array.isArray(r.data) ? r.data : [];
                setStudents(list);
                // Pre-distribute randomly as default
                const map = {};
                list.forEach((s, i) => { map[s.id] = teams[i % teams.length]?.id; });
                setAssignments(map);
            })
            .catch(() => setError('Не удалось загрузить студентов'))
            .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [session.id]);

    const randomize = () => {
        const shuffled = [...students].sort(() => Math.random() - 0.5);
        const map = {};
        shuffled.forEach((s, i) => { map[s.id] = teams[i % teams.length]?.id; });
        setAssignments(map);
    };

    const setTeam = (studentId, teamId) => {
        setAssignments(prev => ({ ...prev, [studentId]: teamId }));
    };

    const start = async () => {
        setStarting(true);
        setError('');
        try {
            const assignmentList = teams.map(t => ({
                team_id: t.id,
                student_ids: students.filter(s => assignments[s.id] === t.id).map(s => s.id),
            }));
            await axiosInstance.post(`${API_URL}v1/game-sessions/${session.id}/start`, { assignments: assignmentList });
            onStarted();
            onClose();
        } catch (err) {
            const msg = err.response?.data?.detail || err.response?.data?.error?.message || 'Ошибка запуска';
            if (err.response?.status === 400 && msg.toLowerCase().includes('already started')) {
                onStarted();
                onClose();
                return;
            }
            setError(msg);
        } finally {
            setStarting(false);
        }
    };

    const counts = teams.map(t => students.filter(s => assignments[s.id] === t.id).length);
    const unassigned = students.filter(s => !assignments[s.id]).length;

    return (
        <div className="tg-modal-overlay" onClick={onClose}>
            <div className="tg-modal tg-divide-modal" onClick={e => e.stopPropagation()}>
                <div className="tg-divide-header">
                    <h2>Разделить на команды</h2>
                    <button className="tg-btn-secondary" onClick={randomize} title="Перемешать случайно">
                        🔀 Случайно
                    </button>
                </div>

                {error && <p className="tg-error">{error}</p>}

                {loading ? (
                    <div className="tg-loading">Загрузка студентов...</div>
                ) : (
                    <>
                        <div className="tg-divide-cols">
                            {teams.map((team, ti) => (
                                <div key={team.id} className="tg-divide-col">
                                    <div className="tg-divide-col-header" style={{ borderBottomColor: team.color }}>
                                        <span style={{ color: team.color, fontWeight: 700 }}>{team.name}</span>
                                        <span className="tg-divide-count">{counts[ti]}</span>
                                    </div>
                                    <div className="tg-divide-list">
                                        {students.filter(s => assignments[s.id] === team.id).map(s => (
                                            <div key={s.id} className="tg-divide-student">
                                                <span className="tg-divide-avatar" style={{ background: team.color }}>
                                                    {(s.full_name || s.username || '?')[0].toUpperCase()}
                                                </span>
                                                <span className="tg-divide-name">{s.full_name || s.username}</span>
                                                <div className="tg-divide-arrows">
                                                    {teams.filter(t => t.id !== team.id).map(other => (
                                                        <button
                                                            key={other.id}
                                                            className="tg-divide-move"
                                                            style={{ color: other.color, borderColor: other.color }}
                                                            onClick={() => setTeam(s.id, other.id)}
                                                            title={`Переместить в ${other.name}`}
                                                        >→ {other.name.replace('Team ', '')}</button>
                                                    ))}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                        {unassigned > 0 && (
                            <p className="tg-error">{unassigned} студентов без команды</p>
                        )}
                    </>
                )}

                <div className="tg-modal-actions">
                    <button className="tg-btn-secondary" onClick={onClose}>Отмена</button>
                    <button
                        className="tg-btn-primary"
                        disabled={starting || loading || unassigned > 0}
                        onClick={start}
                    >
                        {starting ? 'Запуск...' : '▶ Начать игру'}
                    </button>
                </div>
            </div>
        </div>
    );
}


// ── Quiz Question Manager ─────────────────────────────────────────────────────
const OPTION_LABELS = ['A', 'B', 'C', 'D'];

function ImportFromLessonModal({ session, onClose, onImported }) {
    const [lessons, setLessons] = useState([]);
    const [loading, setLoading] = useState(true);
    const [importing, setImporting] = useState(false);

    useEffect(() => {
        const url = session.course_id
            ? `${API_URL}v1/courses/${session.course_id}/lessons-with-questions`
            : `${API_URL}v1/lessons-with-questions`;
        axiosInstance.get(url)
            .then(r => setLessons(Array.isArray(r.data) ? r.data : []))
            .catch(() => {})
            .finally(() => setLoading(false));
    }, [session.course_id]);

    const importLesson = async (lessonId) => {
        setImporting(true);
        try {
            const res = await axiosInstance.post(
                `${API_URL}v1/game-sessions/${session.id}/import-questions?lesson_id=${lessonId}`
            );
            onImported(res.data.length);
            onClose();
        } catch (err) {
            alert(err.response?.data?.detail || 'Ошибка');
        } finally { setImporting(false); }
    };

    const importCourse = async () => {
        if (!session.course_id) return;
        setImporting(true);
        try {
            const res = await axiosInstance.post(
                `${API_URL}v1/game-sessions/${session.id}/import-questions?course_id=${session.course_id}`
            );
            onImported(res.data.length);
            onClose();
        } catch (err) {
            alert(err.response?.data?.detail || 'Ошибка');
        } finally { setImporting(false); }
    };

    return (
        <div className="tg-modal-overlay" onClick={onClose}>
            <div className="tg-modal" onClick={e => e.stopPropagation()}>
                <h2>📚 Импортировать вопросы</h2>
                {loading ? (
                    <p>Загрузка уроков...</p>
                ) : lessons.length === 0 ? (
                    <p style={{ color: '#6b7280' }}>Нет уроков с вопросами.</p>
                ) : (
                    <>
                        <p style={{ color: '#6b7280', marginBottom: '1rem' }}>Выберите урок для импорта:</p>
                        {session.course_id && (
                            <button
                                className="tg-btn-primary tg-import-all-btn"
                                disabled={importing}
                                onClick={importCourse}
                            >
                                🗂 Весь курс ({lessons.reduce((s, l) => s + l.question_count, 0)} вопросов)
                            </button>
                        )}
                        <div className="tg-import-lessons-list">
                            {lessons.map(l => (
                                <div key={l.id} className="tg-import-lesson-row">
                                    <div>
                                        <span className="tg-import-lesson-title">{l.title}</span>
                                        {l.course_title && !session.course_id && (
                                            <span className="tg-import-lesson-count" style={{ marginLeft: 6, color: '#9ca3af' }}>{l.course_title}</span>
                                        )}
                                        <span className="tg-import-lesson-count">{l.question_count} вопр.</span>
                                    </div>
                                    <button
                                        className="tg-btn-secondary tg-btn-sm"
                                        disabled={importing}
                                        onClick={() => importLesson(l.id)}
                                    >
                                        + Добавить
                                    </button>
                                </div>
                            ))}
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

    if (session.game_type !== 'quiz') return null;

    return (
        <div className="tg-quiz-manager">
            <div className="tg-quiz-header">
                <h4>📝 Вопросы викторины ({questions.length})</h4>
                {session.status !== 'completed' && (
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
                    onImported={(count) => { loadQuestions(); alert(`Импортировано ${count} вопросов!`); }}
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
                                {session.status === 'active' && (
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
function SessionCard({ initialSession }) {
    const [session, setSession] = useState(initialSession);
    const [actionLoading, setActionLoading] = useState(false);
    const [delta, setDelta] = useState({});
    const [showDivide, setShowDivide] = useState(false);

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

    const addScore = async (teamId) => {
        const d = Number(delta[teamId] || 0);
        if (!d) return;
        setDelta(prev => ({ ...prev, [teamId]: '' }));
        await act('/score', 'patch', { team_id: teamId, delta: d });
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
                        <button className="tg-btn-primary" disabled={actionLoading} onClick={() => setShowDivide(true)}>
                            ▶ Старт
                        </button>
                    )}
                    {session.status === 'active' && (
                        <button className="tg-btn-success" disabled={actionLoading} onClick={() => act('/complete')}>
                            ✓ Завершить
                        </button>
                    )}
                    <button className="tg-btn-danger" disabled={actionLoading} onClick={() => {
                        if (window.confirm('Удалить сессию?')) act('', 'delete');
                    }}>🗑</button>
                </div>
            </div>

            {session.description && <p className="tg-description">{session.description}</p>}

            {/* Compact scoreboard — always visible above questions */}
            {sortedTeams.length > 0 && (
                <div className="tg-score-strip">
                    {sortedTeams.map((team, idx) => {
                        const top = sortedTeams[0]?.score || 0;
                        return (
                            <div key={team.id} className="tg-score-strip-item">
                                <span className="tg-score-strip-rank">{idx === 0 ? '🥇' : idx === 1 ? '🥈' : '🥉'}</span>
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

            <QuizManager session={session} />

            <div className="tg-teams">
                {sortedTeams.map((team, idx) => (
                    <div key={team.id} className="tg-team" style={{ borderLeftColor: team.color }}>
                        <div className="tg-team-header">
                            <span className="tg-team-rank">#{idx + 1}</span>
                            <span className="tg-team-name" style={{ color: team.color }}>{team.name}</span>
                            <span className="tg-team-score">{team.score} очков</span>
                        </div>
                        <div className="tg-team-members">
                            {team.members.length === 0
                                ? <span className="tg-no-members">Нет участников</span>
                                : team.members.map(m => (
                                    <span key={m.id} className="tg-member-chip" title={m.username}>
                                        {m.full_name || m.username}
                                    </span>
                                ))
                            }
                        </div>
                        {session.status === 'active' && (
                            <div className="tg-score-ctrl">
                                <input
                                    type="number"
                                    placeholder="±очки"
                                    value={delta[team.id] ?? ''}
                                    onChange={e => setDelta(prev => ({ ...prev, [team.id]: e.target.value }))}
                                    onKeyDown={e => e.key === 'Enter' && addScore(team.id)}
                                />
                                <button onClick={() => addScore(team.id)} className="tg-btn-score">+Очки</button>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
        {showDivide && (
            <DivideTeamsModal
                session={session}
                onClose={() => setShowDivide(false)}
                onStarted={async () => {
                    setShowDivide(false);
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
                    {filtered.map(s => <SessionCard key={s.id} initialSession={s} />)}
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
