import React, { useEffect, useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { API_URL } from '../../../api/search/base';
import axiosInstance from '../../../api/axiosInstance';
import { useSessionSocket } from '../../../hooks/useSessionSocket';
import './TeacherTeamGame.css';

const GAME_TYPE_LABELS = { team: 'Командная', individual: 'Индивидуальная' };
const STATUS_LABELS    = { pending: 'Ожидание', active: 'Активна', completed: 'Завершена' };

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
const OPTION_LABELS = ['A', 'B', 'C', 'D', 'E', 'F'];

function ImportFromLessonModal({ session, onClose, onImported, addedLessonIds, onLessonAdded }) {
    const [lessons, setLessons] = useState([]);
    const [loading, setLoading] = useState(true);
    const [importingId, setImportingId] = useState(null);
    const [importingCourse, setImportingCourse] = useState(false);
    const [successMsg, setSuccessMsg] = useState('');
    const [selectedCourseId, setSelectedCourseId] = useState(session.course_id || '');
    const [kindFilter, setKindFilter] = useState(''); // '' = all, 'quiz', 'bug_hunt'

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

    // quiz_count isn't sent by the API — it's just question_count minus the
    // bug_hunt ones already returned, so no backend round-trip is needed.
    const countForKind = (l) => {
        if (kindFilter === 'bug_hunt') return l.bug_count || 0;
        if (kindFilter === 'quiz') return l.question_count - (l.bug_count || 0);
        return l.question_count;
    };

    const visibleLessons = (selectedCourseId
        ? lessons.filter(l => l.course_id === Number(selectedCourseId))
        : lessons
    ).filter(l => countForKind(l) > 0);

    const kindQuery = kindFilter ? `&question_kind=${kindFilter}` : '';

    const importLesson = async (lessonId) => {
        if (addedLessonIds.has(lessonId)) return;
        setImportingId(lessonId);
        setSuccessMsg('');
        try {
            const res = await axiosInstance.post(
                `${API_URL}v1/game-sessions/${session.id}/import-questions?lesson_id=${lessonId}${kindQuery}`
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
                `${API_URL}v1/game-sessions/${session.id}/import-questions?course_id=${courseId}${kindQuery}`
            );
            visibleLessons.forEach(l => onLessonAdded(l.id));
            onImported(res.data.length);
            setSuccessMsg(`+${res.data.length} вопросов добавлено из курса`);
        } catch (err) {
            alert(err.response?.data?.detail || 'Ошибка');
        } finally { setImportingCourse(false); }
    };

    const selectedCourseTotal = visibleLessons.reduce((s, l) => s + countForKind(l), 0);
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
                        <div className="tg-kind-filter" style={{ marginBottom: '0.75rem' }}>
                            {[
                                { value: '', label: 'Все' },
                                { value: 'quiz', label: '📝 Вопросы' },
                                { value: 'bug_hunt', label: '🐛 Баги' },
                            ].map(opt => (
                                <button
                                    key={opt.value}
                                    type="button"
                                    className={`tg-kind-filter-btn ${kindFilter === opt.value ? 'tg-kind-filter-active' : ''}`}
                                    onClick={() => setKindFilter(opt.value)}
                                >
                                    {opt.label}
                                </button>
                            ))}
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
                                            <span className="tg-import-lesson-count">
                                                {kindFilter === 'bug_hunt'
                                                    ? `${l.bug_count} баг(ов)`
                                                    : kindFilter === 'quiz'
                                                        ? `${l.question_count - (l.bug_count || 0)} вопр.`
                                                        : (
                                                            <>
                                                                {l.question_count} вопр.
                                                                {l.bug_count > 0 && (
                                                                    <span className="tg-import-lesson-bugcount" title={`${l.bug_count} из них — баги для поиска`}>
                                                                        {' '}(🐛 {l.bug_count})
                                                                    </span>
                                                                )}
                                                            </>
                                                        )}
                                            </span>
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
    const [showImport, setShowImport] = useState(false);
    const [addedLessonIds, setAddedLessonIds] = useState(new Set());
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

            {loading ? <div className="tg-quiz-loading">Загрузка...</div> : (
                <div className="tg-quiz-list">
                    {questions.length === 0 && (
                        <p className="tg-quiz-empty">Нет вопросов. Добавьте хотя бы один перед запуском!</p>
                    )}
                    {questions.map((q, idx) => {
                        const prog = progress[q.id];
                        return (
                            <div key={q.id} className={`tg-quiz-item tg-quiz-item--${q.status}`}>
                                <div className="tg-quiz-item-header">
                                    <span className="tg-quiz-num">#{idx + 1}{q.question_kind === 'bug_hunt' ? ' 🐛' : ''}</span>
                                    <span className="tg-quiz-text">{q.question_text}</span>
                                    <div className="tg-quiz-item-meta">
                                        <span>⏱{q.time_limit}с</span>
                                        <span>⭐{q.points}</span>
                                        <span className={`tg-quiz-status tg-quiz-status--${q.status}`}>
                                            {q.status === 'pending' ? '○ Ожидание' : q.status === 'active' ? '● Активен' : '✓ Раскрыт'}
                                        </span>
                                    </div>
                                </div>
                                {q.question_kind === 'bug_hunt' && q.code_snippet && (
                                    <pre className="tg-quiz-code-preview">
                                        {q.code_snippet.split('\n').slice(0, 3).join('\n')}
                                        {q.code_snippet.split('\n').length > 3 ? '\n…' : ''}
                                    </pre>
                                )}
                                <div className="tg-quiz-opts-preview">
                                    {q.options.map((opt, i) => (
                                        <span key={i} className={`tg-quiz-opt-chip${i === q.correct_option ? ' tg-quiz-opt-chip--correct' : ''}`}>
                                            {OPTION_LABELS[i]}: {q.question_kind === 'bug_hunt' ? `строка ${opt}` : opt}
                                        </span>
                                    ))}
                                </div>
                                {q.question_kind === 'bug_hunt' && (q.bug_explanation_ru || q.bug_explanation) && (
                                    <p className="tg-quiz-bug-explain">💡 {q.bug_explanation_ru || q.bug_explanation}</p>
                                )}
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


// ── Post-completion summary panel ─────────────────────────────────────────────
// Exported so TeacherTeamGameSession (the dedicated profile page) can reuse it.
export function SessionSummary({ sessionId }) {
    const [data, setData] = useState(null);
    const [err, setErr] = useState(null);
    const [downloading, setDownloading] = useState(false);
    // Old snapshots padded the leaderboard with every registered team member,
    // even those who never answered — that turned real sessions into a wall
    // of 0-score rows. Default the summary to real participants only; teachers
    // can opt in to the padded view.
    const [showZero, setShowZero] = useState(false);

    useEffect(() => {
        let cancelled = false;
        axiosInstance
            .get(`${API_URL}v1/game-sessions/${sessionId}/summary`)
            .then(r => { if (!cancelled) setData(r.data); })
            .catch(e => {
                if (!cancelled) setErr(e.response?.data?.detail || 'Не удалось загрузить итоги');
            });
        return () => { cancelled = true; };
    }, [sessionId]);

    const downloadCsv = async () => {
        setDownloading(true);
        try {
            const res = await axiosInstance.get(
                `${API_URL}v1/game-sessions/${sessionId}/export.csv`,
                { responseType: 'blob' },
            );
            const blob = new Blob([res.data], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `session-${sessionId}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (e) {
            alert(e.response?.data?.detail || 'Не удалось скачать CSV');
        } finally {
            setDownloading(false);
        }
    };

    if (err) return <div className="tg-summary-error">{err}</div>;
    if (!data) return <div className="tg-quiz-loading">Загрузка итогов...</div>;

    const { leaderboard = [], questions = [], answers = [], totals = {}, completed_at } = data;
    const completedDate = completed_at ? new Date(completed_at).toLocaleString('ru-RU') : '—';
    const answersByQ = answers.reduce((acc, a) => {
        (acc[a.question_id] ||= []).push(a);
        return acc;
    }, {});
    const activeLeaders = leaderboard.filter(r => (r.answered_count || 0) > 0);
    const skippedCount = leaderboard.length - activeLeaders.length;
    const visibleLeaders = showZero ? leaderboard : activeLeaders;

    return (
        <div className="tg-summary">
            <div className="tg-summary-header">
                <div className="tg-summary-meta">
                    <span>✅ Завершено: <b>{completedDate}</b></span>
                    <span>👥 Участников: <b>{activeLeaders.length}</b></span>
                    <span>❓ Вопросов: <b>{totals.questions ?? questions.length}</b></span>
                    <span>📝 Ответов: <b>{totals.total_answers ?? answers.length}</b></span>
                </div>
                <button className="tg-btn-primary tg-btn-sm" disabled={downloading} onClick={downloadCsv}>
                    {downloading ? 'Готовим CSV…' : '⬇ Скачать CSV'}
                </button>
            </div>

            <section className="tg-summary-section">
                <div className="tg-summary-section-head">
                    <h4>🏆 Итоговый рейтинг</h4>
                    {skippedCount > 0 && (
                        <button className="tg-summary-toggle" onClick={() => setShowZero(v => !v)}>
                            {showZero
                                ? `Скрыть не участвовавших (${skippedCount})`
                                : `Показать не участвовавших (${skippedCount})`}
                        </button>
                    )}
                </div>
                <div className="tg-summary-table-wrap">
                    <table className="tg-summary-table">
                        <thead>
                            <tr>
                                <th>#</th><th>Студент</th><th>Команда</th>
                                <th>Очки</th><th>Верно</th><th>Неверно</th><th>Ответов</th>
                            </tr>
                        </thead>
                        <tbody>
                            {visibleLeaders.map(r => (
                                <tr key={r.student_id} className={(r.answered_count || 0) === 0 ? 'tg-summary-row-empty' : ''}>
                                    <td>{r.rank}</td>
                                    <td>{r.full_name}</td>
                                    <td>
                                        {r.team_name
                                            ? <span style={{ color: r.team_color || '#666' }}>● {r.team_name}</span>
                                            : '—'}
                                    </td>
                                    <td><b>{r.total_points}</b></td>
                                    <td>{r.correct_count}</td>
                                    <td>{r.wrong_count}</td>
                                    <td>{r.answered_count}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </section>

            <section className="tg-summary-section">
                <h4>❓ Вопросы</h4>
                <div className="tg-summary-questions">
                    {questions.map(q => {
                        const stats = q.stats || {};
                        const options = q.options || [];
                        const counts = stats.option_counts || [];
                        const total = stats.total_answers || 0;
                        const isBugHunt = q.question_kind === 'bug_hunt';
                        const optLabel = (opt) => isBugHunt ? `строка ${opt}` : opt;
                        return (
                            <div key={q.id} className="tg-summary-question">
                                <div className="tg-summary-question-head">
                                    <span className="tg-quiz-num">#{q.order_index + 1}{isBugHunt ? ' 🐛' : ''}</span>
                                    <span className="tg-summary-qtext">{q.question_text}</span>
                                    <span className="tg-summary-qstats">
                                        {stats.correct_answers ?? 0}/{total} верно
                                    </span>
                                </div>
                                {isBugHunt && q.code_snippet && (
                                    <pre className="tg-quiz-code-preview">
                                        {q.code_snippet.split('\n').map((line, i) => {
                                            const lineNum = i + 1;
                                            const isBugLine = lineNum === q.bug_line;
                                            return (
                                                <div key={i} className={isBugLine ? 'tg-code-bug-line' : undefined}>
                                                    {String(lineNum).padStart(3, ' ')}  {line}{isBugLine ? '  ← баг' : ''}
                                                </div>
                                            );
                                        })}
                                    </pre>
                                )}
                                <div className="tg-summary-options">
                                    {options.map((opt, i) => {
                                        const cnt = counts[i] || 0;
                                        const pct = total > 0 ? Math.round((cnt / total) * 100) : 0;
                                        const isCorrect = i === q.correct_option;
                                        return (
                                            <div key={i} className={`tg-summary-option${isCorrect ? ' tg-summary-option--correct' : ''}`}>
                                                <div className="tg-summary-option-label">
                                                    <span>{OPTION_LABELS[i]}: {optLabel(opt)}</span>
                                                    <span>{cnt} ({pct}%){isCorrect ? ' ✓' : ''}</span>
                                                </div>
                                                <div className="tg-summary-option-bar-wrap">
                                                    <div className="tg-summary-option-bar" style={{ width: `${pct}%` }} />
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                                {isBugHunt && (q.bug_explanation_ru || q.bug_explanation) && (
                                    <p className="tg-quiz-bug-explain">💡 {q.bug_explanation_ru || q.bug_explanation}</p>
                                )}
                                {(answersByQ[q.id] || []).length > 0 && (
                                    <details className="tg-summary-answers">
                                        <summary>Ответы студентов ({(answersByQ[q.id] || []).length})</summary>
                                        <ul>
                                            {(answersByQ[q.id] || []).map(a => (
                                                <li key={`${a.question_id}-${a.student_id}`}
                                                    className={a.is_correct ? 'ok' : 'bad'}>
                                                    <span>{a.student_name}</span>
                                                    <span>{options[a.chosen_option] != null ? optLabel(options[a.chosen_option]) : '—'}</span>
                                                    <span>{a.is_correct ? '✓' : '✗'} +{a.points_earned}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </details>
                                )}
                            </div>
                        );
                    })}
                </div>
            </section>
        </div>
    );
}


// ── Session Card ──────────────────────────────────────────────────────────────
// Exported so TeacherTeamGameSession (the profile page) can render the
// live board for pending/active sessions.
export function SessionCard({ initialSession, onDeleted }) {
    const [session, setSession] = useState(initialSession);
    const [actionLoading, setActionLoading] = useState(false);
    const [showStart, setShowStart] = useState(false);
    const [view, setView] = useState(initialSession.status === 'completed' ? 'summary' : 'questions');

    const handleWsUpdate = useCallback((data) => {
        setSession(prev => {
            // Auto-switch to the summary tab the moment the session flips to
            // completed — the teacher just clicked Завершить and expects to
            // see the frozen recap, not the now-stale live board.
            if (prev.status !== 'completed' && data.status === 'completed') {
                setView('summary');
            }
            return data;
        });
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
                    {session.status === 'completed' && (
                        <button
                            className={`tg-view-tab${view === 'summary' ? ' tg-view-tab--active' : ''}`}
                            onClick={() => setView('summary')}
                        >📊 Итоги</button>
                    )}
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

            {/* Summary view — completed sessions only */}
            {view === 'summary' && session.status === 'completed' && (
                <SessionSummary sessionId={session.id} />
            )}

            {/* Questions view (also the fallback when no teams have joined yet) */}
            {(view === 'questions' || (!sortedTeams.length && view !== 'summary')) && (
                <QuizManager session={session} />
            )}

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

// Unified compact row for the session list — works for every status.
// Clicking opens the dedicated profile page at /teacher/team-game/:id.
// For pending/active sessions the profile page renders the live board;
// for completed sessions it renders the frozen summary + CSV export.
function SessionListRow({ session }) {
    const topThree = [...(session.teams || [])]
        .sort((a, b) => b.score - a.score)
        .slice(0, 3);
    // Prefer updated_at (last state change) — for completed sessions
    // that's the finish time; for pending/active sessions it's the
    // creation or last-modified time, which is what teachers want to
    // scan by. Falls back to created_at then a dash if both missing.
    const stamp = session.updated_at || session.created_at;
    const stampFmt = stamp
        ? new Date(stamp).toLocaleString('ru-RU', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit',
        })
        : '—';
    const participantCount = (session.teams || []).reduce(
        (n, t) => n + (t.members?.length || 0), 0,
    );
    // Show the podium only when at least one team has scored — for
    // pending/active-with-no-answers-yet sessions it would be a wall
    // of zeros and steal horizontal space from the meta chips.
    const podiumHasScore = topThree.some(t => (t.score || 0) > 0);
    return (
        <Link to={`/teacher/team-game/${session.id}`} className="tg-fin-row-link">
            <div className="tg-fin-row">
                <div className="tg-fin-row-head">
                    <span className="tg-fin-row-caret">▸</span>
                    <span className="tg-fin-row-title">
                        {session.title}
                        <span className={`tg-fin-row-status tg-fin-row-status--${session.status}`}>
                            {session.status === 'pending' && '○ Ожидание'}
                            {session.status === 'active' && '● Активна'}
                            {session.status === 'completed' && '✓ Завершена'}
                        </span>
                        {session.auto_mode && (
                            <span className="tg-fin-row-auto">⚡ Авто</span>
                        )}
                    </span>
                    <span className="tg-fin-row-meta">
                        <span>📅 {stampFmt}</span>
                        <span>👥 {participantCount}</span>
                        {session.course_title && <span>📚 {session.course_title}</span>}
                    </span>
                    {podiumHasScore && (
                        <span className="tg-fin-row-podium">
                            {topThree.map((t, i) => (
                                <span key={t.id} className="tg-fin-row-medal" style={{ color: t.color }}>
                                    {['🥇','🥈','🥉'][i]} {t.name} <b>{t.score}</b>
                                </span>
                            ))}
                        </span>
                    )}
                </div>
            </div>
        </Link>
    );
}


// Local-date (not UTC) 'YYYY-MM-DD' — matches what a <input type="date">
// expects and what the teacher sees in their own timezone.
const toLocalDateStr = (d) => {
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
};

const sessionDateStr = (session) => {
    const stamp = session.updated_at || session.created_at;
    return stamp ? toLocalDateStr(new Date(stamp)) : null;
};

export default function TeacherTeamGame() {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);
    const [filter, setFilter] = useState('all');
    // Default to today only — the list otherwise shows the entire session
    // history, which is rarely what the teacher wants when checking on a
    // game they just ran.
    const [dateFrom, setDateFrom] = useState(() => toLocalDateStr(new Date()));
    const [dateTo, setDateTo] = useState(() => toLocalDateStr(new Date()));

    const load = useCallback(() => {
        setLoading(true);
        axiosInstance.get(`${API_URL}v1/game-sessions`)
            .then(r => setSessions(Array.isArray(r.data) ? r.data : []))
            .catch(() => setSessions([]))
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => { load(); }, [load]);

    const navigate = useNavigate();
    const handleCreated = useCallback((newSession) => {
        setSessions(prev => [newSession, ...prev]);
        // Jump straight into the new session's profile page — teacher's
        // next step is always to configure/start it, and the profile
        // page hosts that UI now.
        if (newSession?.id) navigate(`/teacher/team-game/${newSession.id}`);
    }, [navigate]);

    const showAllDates = () => { setDateFrom(''); setDateTo(''); };
    const showToday = () => { const t = toLocalDateStr(new Date()); setDateFrom(t); setDateTo(t); };

    const filtered = sessions.filter(s => {
        if (filter !== 'all' && s.status !== filter) return false;
        const ds = sessionDateStr(s);
        if (dateFrom && (!ds || ds < dateFrom)) return false;
        if (dateTo && (!ds || ds > dateTo)) return false;
        return true;
    });

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

            <div className="tg-date-filters">
                <label className="tg-date-filter-field">
                    <span>От</span>
                    <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} />
                </label>
                <label className="tg-date-filter-field">
                    <span>До</span>
                    <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} />
                </label>
                <button type="button" className="tg-btn-secondary tg-date-filter-btn" onClick={showToday}>Сегодня</button>
                <button type="button" className="tg-btn-secondary tg-date-filter-btn" onClick={showAllDates}>Все даты</button>
            </div>

            {loading ? (
                <div className="tg-loading">Загрузка...</div>
            ) : filtered.length === 0 ? (
                <div className="tg-empty">
                    <p>Нет сессий. Создайте первую!</p>
                </div>
            ) : (
                <div className="tg-fin-list">
                    {filtered.map(s => (
                        <SessionListRow key={s.id} session={s} />
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
