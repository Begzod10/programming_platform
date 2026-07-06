import React, { useEffect, useState, useCallback, useRef } from 'react';
import { API_URL, API_URL_DOC, headers } from '../../../api/search/base';
import './StudentTeamGame.css';
import { Trophy } from 'lucide-react';

const GAME_TYPE_LABELS = { quiz: 'Викторина', coding: 'Кодинг', project: 'Проект', custom: 'Другое' };
const STATUS_LABELS    = { pending: 'Скоро начнётся', active: 'Идёт сейчас', completed: 'Завершена' };
const OPTION_LABELS    = ['A', 'B', 'C', 'D'];
const OPTION_COLORS    = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12'];

function wsUrl(sessionId) {
    const base = API_URL_DOC.replace(/^http/, 'ws').replace(/\/$/, '');
    const token = encodeURIComponent(localStorage.getItem('token') || '');
    return `${base}/api/v1/game-sessions/${sessionId}/ws?token=${token}`;
}

function useSessionSocket(sessionId, onUpdate, onDeleted, onMessage) {
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
                if (onMessage) onMessage(msg);
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
    }, [sessionId, onUpdate, onDeleted, onMessage]);

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

// ── Quiz Overlay ──────────────────────────────────────────────────────────────
function QuizOverlay({ question, sessionId, onDone }) {
    const [chosen, setChosen] = useState(null);
    const [result, setResult] = useState(null);  // {is_correct, points_earned}
    const [progress, setProgress] = useState(null);
    const [timeLeft, setTimeLeft] = useState(question.time_limit);
    const [submitting, setSubmitting] = useState(false);

    // Countdown
    useEffect(() => {
        const start = question.activated_at ? new Date(question.activated_at) : new Date();
        const tick = () => {
            const elapsed = (Date.now() - start.getTime()) / 1000;
            setTimeLeft(Math.max(0, Math.ceil(question.time_limit - elapsed)));
        };
        tick();
        const t = setInterval(tick, 250);
        return () => clearInterval(t);
    }, [question]);

    const submit = async (idx) => {
        if (chosen !== null || submitting) return;
        setChosen(idx);
        setSubmitting(true);
        try {
            const res = await fetch(`${API_URL}v1/game-sessions/${sessionId}/questions/${question.id}/answer`, {
                method: 'POST',
                headers: { ...headers(), 'Content-Type': 'application/json' },
                body: JSON.stringify({ chosen_option: idx }),
            });
            if (res.ok) {
                const data = await res.json();
                setResult(data);
            } else {
                // Question already revealed or closed — treat as wrong
                setResult({ is_correct: false, points_earned: 0 });
            }
        } finally { setSubmitting(false); }
    };

    const pct = question.time_limit > 0 ? (timeLeft / question.time_limit) * 100 : 0;
    const timerColor = pct > 50 ? '#2ecc71' : pct > 25 ? '#f39c12' : '#e74c3c';

    return (
        <div className="stg-quiz-overlay">
            <div className="stg-quiz-timer-bar-wrap">
                <div className="stg-quiz-timer-bar" style={{ width: `${pct}%`, background: timerColor }} />
                <span className="stg-quiz-timer-num" style={{ color: timerColor }}>{timeLeft}с</span>
            </div>

            <div className="stg-quiz-question">
                <div className="stg-quiz-points-badge">⭐ до {question.points} очков</div>
                <h2>{question.question_text}</h2>
            </div>

            <div className="stg-quiz-options">
                {question.options.map((opt, i) => {
                    let cls = 'stg-quiz-opt';
                    if (chosen === i) cls += ' stg-quiz-opt--chosen';
                    if (chosen !== null && chosen !== i) cls += ' stg-quiz-opt--faded';
                    return (
                        <button
                            key={i}
                            className={cls}
                            style={{ '--opt-color': OPTION_COLORS[i] }}
                            onClick={() => submit(i)}
                            disabled={chosen !== null}
                        >
                            <span className="stg-quiz-opt-letter">{OPTION_LABELS[i]}</span>
                            <span className="stg-quiz-opt-text">{opt}</span>
                        </button>
                    );
                })}
            </div>

            {chosen !== null && !result && (
                <div className="stg-quiz-waiting">
                    {progress
                        ? <p>✅ Ответили: {progress.answered_count} / {progress.total_players}</p>
                        : <p>⏳ Ждём ответов других игроков...</p>
                    }
                </div>
            )}

            {result && (
                <div className={`stg-quiz-result stg-quiz-result--${result.is_correct ? 'correct' : 'wrong'}`}>
                    {result.is_correct
                        ? <><span>✅ Правильно!</span><span className="stg-quiz-pts">+{result.points_earned} очков</span></>
                        : <span>❌ Неправильно</span>
                    }
                </div>
            )}

            {timeLeft === 0 && chosen === null && (
                <div className="stg-quiz-result stg-quiz-result--wrong" style={{ opacity: 0.7 }}>⏰ Время вышло — но попробуйте ответить!</div>
            )}
        </div>
    );
}


function MyTeamBanner({ session }) {
    const team = session.teams?.find(t => t.id === session.my_team_id);
    if (!team) return null;
    return (
        <div className="stg-my-banner" style={{ borderColor: team.color }}>
            <span className="stg-my-label">Ваша команда</span>
            <span className="stg-my-name" style={{ color: team.color }}>{team.name}</span>
            <span className="stg-my-score">{team.score} очков</span>
        </div>
    );
}

function ScoreBoard({ teams }) {
    const sorted = [...teams].sort((a, b) => b.score - a.score);
    const top = sorted[0]?.score || 0;
    return (
        <div className="stg-scoreboard">
            {sorted.map((team, idx) => (
                <div key={team.id} className="stg-sb-row">
                    <span className="stg-sb-rank">{idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${idx + 1}`}</span>
                    <span className="stg-sb-dot" style={{ background: team.color }} />
                    <span className="stg-sb-name">{team.name}</span>
                    <span className="stg-sb-score">{team.score}</span>
                    <div className="stg-sb-bar-wrap">
                        <div className="stg-sb-bar" style={{
                            background: team.color,
                            width: top > 0 ? `${(team.score / top) * 100}%` : '0%',
                        }} />
                    </div>
                </div>
            ))}
        </div>
    );
}

function SessionDetail({ initialSession, onBack }) {
    const [session, setSession] = useState(initialSession);
    const [gone, setGone] = useState(false);
    const [activeQuestion, setActiveQuestion] = useState(null);  // question_start payload
    const [lastResult, setLastResult] = useState(null);  // question_end payload

    const handleUpdate = useCallback((data) => setSession(data), []);
    const handleDeleted = useCallback(() => setGone(true), []);
    const handleMessage = useCallback((msg) => {
        if (msg.type === 'question_start') {
            setActiveQuestion(msg.data);
            setLastResult(null);
        }
        if (msg.type === 'question_end') {
            setActiveQuestion(null);
            setLastResult(msg.data);
        }
    }, []);
    useSessionSocket(session.id, handleUpdate, handleDeleted, handleMessage);

    if (gone) {
        return (
            <div className="stg-detail">
                <button className="stg-back-btn" onClick={onBack}>← Назад</button>
                <div className="stg-empty">
                    <div className="stg-empty-icon">🚫</div>
                    <h3>Сессия удалена</h3>
                    <p>Преподаватель удалил эту игровую сессию.</p>
                </div>
            </div>
        );
    }

    const sortedTeams = [...(session.teams || [])].sort((a, b) => b.score - a.score);

    return (
        <div className="stg-detail">
            {/* Full-screen quiz overlay when question is active */}
            {activeQuestion && session.game_type === 'quiz' && (
                <QuizOverlay
                    question={activeQuestion}
                    sessionId={session.id}
                    onDone={() => setActiveQuestion(null)}
                />
            )}

            <button className="stg-back-btn" onClick={onBack}>← Назад</button>
            <div className="stg-detail-header">
                <h2>{session.title}</h2>
                <span className={`stg-badge stg-badge--${session.status}`}>{STATUS_LABELS[session.status]}</span>
                <span className="stg-badge stg-badge--type">{GAME_TYPE_LABELS[session.game_type]}</span>
                <span className="stg-live-dot" title="Подключено в реальном времени" />
            </div>
            {session.description && <p className="stg-description">{session.description}</p>}

            <MyTeamBanner session={session} />

            {/* Show last question result between questions */}
            {lastResult && !activeQuestion && (
                <div className="stg-quiz-end-banner">
                    <h3>📊 Результаты вопроса</h3>
                    <div className="stg-quiz-end-opts">
                        {session.teams && session.teams[0]?.members.length > 0 && lastResult.answers && (
                            <p className="stg-quiz-end-stat">
                                ✅ Правильно ответили: {lastResult.answers.filter(a => a.is_correct).length} / {lastResult.answers.length}
                            </p>
                        )}
                    </div>
                    <p className="stg-quiz-end-hint">Ждите следующего вопроса...</p>
                </div>
            )}

            {session.status === 'pending' && (
                <div className="stg-pending-notice">
                    <span>⏳</span>
                    <p>Команды ещё не сформированы. Ждите, когда преподаватель запустит сессию — страница обновится автоматически.</p>
                </div>
            )}

            {sortedTeams.length > 0 && session.status !== 'pending' && (
                <>
                    <h3 className="stg-section-title">Таблица результатов</h3>
                    <ScoreBoard teams={sortedTeams} />
                </>
            )}

            <h3 className="stg-section-title">Команды</h3>
            <div className="stg-teams-grid">
                {sortedTeams.map(team => (
                    <div key={team.id}
                        className={`stg-team-card${team.id === session.my_team_id ? ' stg-team-card--mine' : ''}`}
                        style={{ borderColor: team.id === session.my_team_id ? team.color : undefined }}>
                        <div className="stg-team-title" style={{ color: team.color }}>
                            {team.name}
                            {team.id === session.my_team_id && <span className="stg-you-badge">Вы здесь</span>}
                        </div>
                        <div className="stg-team-score-big">{team.score} <span>очков</span></div>
                        <div className="stg-member-list">
                            {team.members.length === 0
                                ? <span className="stg-no-members">Ожидаем участников…</span>
                                : team.members.map(m => (
                                    <div key={m.id} className="stg-member">
                                        <span className="stg-avatar">{(m.full_name || m.username || '?')[0].toUpperCase()}</span>
                                        <span>{m.full_name || m.username}</span>
                                    </div>
                                ))
                            }
                        </div>
                    </div>
                ))}
            </div>

            {session.status === 'completed' && (
                <div className="stg-completed-banner">
                    <Trophy size={16} aria-hidden="true" /> Игра завершена! {sortedTeams[0] && `Победитель: ${sortedTeams[0].name} (${sortedTeams[0].score} очков)`}
                </div>
            )}
        </div>
    );
}

export default function StudentTeamGame() {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selected, setSelected] = useState(null);

    const load = useCallback((silent = false) => {
        if (!silent) setLoading(true);
        fetch(`${API_URL}v1/game-sessions`, { headers: headers() })
            .then(r => r.json())
            .then(d => setSessions(Array.isArray(d) ? d : []))
            .catch(() => {})
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => {
        load();
        const interval = setInterval(() => load(true), 10000);
        return () => clearInterval(interval);
    }, [load]);

    const openSession = async (id) => {
        try {
            const res = await fetch(`${API_URL}v1/game-sessions/${id}`, { headers: headers() });
            if (!res.ok) return;
            setSelected(await res.json());
        } catch {}
    };

    if (selected) {
        return <SessionDetail initialSession={selected} onBack={() => { setSelected(null); load(); }} />;
    }

    return (
        <div className="stg-page">
            <div className="stg-page-header">
                <h1>Командные игры</h1>
                <p className="stg-subtitle">Присоединяйтесь к активным сессиям и наблюдайте за результатами в реальном времени</p>
            </div>

            {loading ? (
                <div className="stg-loading">Загрузка...</div>
            ) : sessions.length === 0 ? (
                <div className="stg-empty">
                    <div className="stg-empty-icon">🎮</div>
                    <h3>Нет активных игр</h3>
                    <p>Преподаватель ещё не создал игровую сессию. Страница обновляется автоматически.</p>
                    <button className="stg-refresh-btn" onClick={() => load()}>Обновить</button>
                </div>
            ) : (
                <div className="stg-list">
                    {sessions.map(s => {
                        const myTeam = s.teams?.find(t => t.id === s.my_team_id);
                        return (
                            <div key={s.id} className={`stg-card stg-card--${s.status}`} onClick={() => openSession(s.id)}>
                                <div className="stg-card-top">
                                    <div>
                                        <h3>{s.title}</h3>
                                        {s.description && <p>{s.description}</p>}
                                    </div>
                                    <div className="stg-badges">
                                        <span className={`stg-badge stg-badge--${s.status}`}>{STATUS_LABELS[s.status]}</span>
                                        <span className="stg-badge stg-badge--type">{GAME_TYPE_LABELS[s.game_type]}</span>
                                    </div>
                                </div>
                                <div className="stg-card-bottom">
                                    <div className="stg-card-meta">
                                        <span>👥 {s.team_count} команды</span>
                                        {s.course_title && <span>📚 {s.course_title}</span>}
                                        {myTeam && (
                                            <span className="stg-my-team-pill" style={{ borderColor: myTeam.color, color: myTeam.color }}>
                                                Вы: {myTeam.name}
                                            </span>
                                        )}
                                    </div>
                                    {s.status === 'active' && (
                                        <button className="stg-join-btn" onClick={e => { e.stopPropagation(); openSession(s.id); }}>
                                            Войти в игру →
                                        </button>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
