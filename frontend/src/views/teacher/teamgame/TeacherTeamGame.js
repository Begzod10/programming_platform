import React, { useEffect, useState, useCallback, useRef } from 'react';
import { API_URL, API_URL_DOC, headers } from '../../../api/search/base';
import './TeacherTeamGame.css';

const GAME_TYPE_LABELS = { quiz: 'Викторина', coding: 'Кодинг', project: 'Проект', custom: 'Другое' };
const STATUS_LABELS    = { pending: 'Ожидание', active: 'Активна', completed: 'Завершена' };

function wsUrl(sessionId) {
    const base = API_URL_DOC.replace(/^http/, 'ws').replace(/\/$/, '');
    const token = encodeURIComponent(localStorage.getItem('token') || '');
    return `${base}/api/v1/game-sessions/${sessionId}/ws?token=${token}`;
}

// Keeps a WS alive for the given sessionId, calls onUpdate(data) on every push
function useSessionSocket(sessionId, onUpdate) {
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
        fetch(`${API_URL}v1/courses?is_active=true`, { headers: headers() })
            .then(r => r.json())
            .then(d => setCourses(d.courses || d || []))
            .catch(() => {});
    }, []);

    const submit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            const res = await fetch(`${API_URL}v1/game-sessions`, {
                method: 'POST',
                headers: { ...headers(), 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: form.title,
                    description: form.description || null,
                    game_type: form.game_type,
                    team_count: Number(form.team_count),
                    course_id: form.course_id ? Number(form.course_id) : null,
                }),
            });
            if (!res.ok) throw new Error((await res.json()).detail || 'Ошибка');
            onCreated(await res.json());
            onClose();
        } catch (err) {
            setError(err.message);
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

function SessionCard({ initialSession }) {
    const [session, setSession] = useState(initialSession);
    const [actionLoading, setActionLoading] = useState(false);
    const [delta, setDelta] = useState({});

    const handleWsUpdate = useCallback((data) => setSession(data), []);
    useSessionSocket(session.id, handleWsUpdate);

    const act = async (path, method = 'POST', body = null) => {
        setActionLoading(true);
        try {
            const opts = { method, headers: { ...headers(), 'Content-Type': 'application/json' } };
            if (body) opts.body = JSON.stringify(body);
            const res = await fetch(`${API_URL}v1/game-sessions/${session.id}${path}`, opts);
            if (!res.ok) {
                const d = await res.json();
                alert(d.detail || 'Ошибка');
            }
            // No need to refetch — WS broadcast will update state
        } finally {
            setActionLoading(false);
        }
    };

    const addScore = async (teamId) => {
        const d = Number(delta[teamId] || 0);
        if (!d) return;
        setDelta(prev => ({ ...prev, [teamId]: '' }));
        await act('/score', 'PATCH', { team_id: teamId, delta: d });
    };

    const sortedTeams = [...(session.teams || [])].sort((a, b) => b.score - a.score);

    return (
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
                        <button className="tg-btn-primary" disabled={actionLoading} onClick={() => act('/start')}>
                            ▶ Старт
                        </button>
                    )}
                    {session.status === 'active' && (
                        <button className="tg-btn-success" disabled={actionLoading} onClick={() => act('/complete')}>
                            ✓ Завершить
                        </button>
                    )}
                    <button className="tg-btn-danger" disabled={actionLoading} onClick={() => {
                        if (window.confirm('Удалить сессию?')) act('', 'DELETE');
                    }}>🗑</button>
                </div>
            </div>

            {session.description && <p className="tg-description">{session.description}</p>}

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
    );
}

export default function TeacherTeamGame() {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);
    const [filter, setFilter] = useState('all');

    const load = useCallback(() => {
        setLoading(true);
        fetch(`${API_URL}v1/game-sessions`, { headers: headers() })
            .then(r => r.json())
            .then(data => setSessions(Array.isArray(data) ? data : []))
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
