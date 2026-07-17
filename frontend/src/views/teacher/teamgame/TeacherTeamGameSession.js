import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import axiosInstance from '../../../api/axiosInstance';
import { API_URL } from '../../../api/search/base';
import { SessionSummary } from './TeacherTeamGame';
import './TeacherTeamGame.css';

/**
 * Dedicated profile page for a single team-game session.
 *
 * Shows the full session metadata header (title, dates, teacher, game
 * type, course, teams roster) followed by the SessionSummary panel
 * (leaderboard, per-question stats, per-student answers, CSV export).
 *
 * Route: /teacher/team-game/:sessionId
 */
const GAME_TYPE_LABELS = { team: 'Командная', individual: 'Индивидуальная' };
const STATUS_LABELS = { pending: 'Ожидание', active: 'Активна', completed: 'Завершена' };


export default function TeacherTeamGameSession() {
    const { sessionId } = useParams();
    const [session, setSession] = useState(null);
    const [err, setErr] = useState(null);

    useEffect(() => {
        let cancelled = false;
        axiosInstance
            .get(`${API_URL}v1/game-sessions/${sessionId}`)
            .then(r => { if (!cancelled) setSession(r.data); })
            .catch(e => {
                if (!cancelled) {
                    setErr(e.response?.data?.detail || 'Сессия не найдена');
                }
            });
        return () => { cancelled = true; };
    }, [sessionId]);

    if (err) {
        return (
            <div className="tg-page">
                <Link to="/teacher/team-game" className="tg-back-link">← К списку сессий</Link>
                <div className="tg-summary-error" style={{ marginTop: '1rem' }}>{err}</div>
            </div>
        );
    }
    if (!session) {
        return (
            <div className="tg-page">
                <Link to="/teacher/team-game" className="tg-back-link">← К списку сессий</Link>
                <div className="tg-loading">Загрузка...</div>
            </div>
        );
    }

    const created = session.created_at
        ? new Date(session.created_at).toLocaleString('ru-RU')
        : '—';
    const updated = session.updated_at
        ? new Date(session.updated_at).toLocaleString('ru-RU')
        : '—';
    const teams = [...(session.teams || [])].sort((a, b) => b.score - a.score);
    const participantCount = teams.reduce(
        (n, t) => n + (t.members?.length || 0), 0,
    );

    return (
        <div className="tg-page">
            <Link to="/teacher/team-game" className="tg-back-link">← К списку сессий</Link>

            <div className="tg-profile-header">
                <div>
                    <h1 className="tg-profile-title">{session.title}</h1>
                    <div className="tg-profile-badges">
                        <span className="tg-tag">{GAME_TYPE_LABELS[session.game_type] || session.game_type}</span>
                        <span className={`tg-status tg-status--${session.status}`}>
                            {STATUS_LABELS[session.status] || session.status}
                        </span>
                        {session.auto_mode && <span className="tg-auto-badge">⚡ Авто режим</span>}
                        {session.course_title && (
                            <span className="tg-tag tg-tag--course">📚 {session.course_title}</span>
                        )}
                    </div>
                    {session.description && (
                        <p className="tg-profile-description">{session.description}</p>
                    )}
                </div>
            </div>

            <div className="tg-profile-meta">
                <div className="tg-profile-meta-item">
                    <span className="tg-profile-meta-label">Создана</span>
                    <span className="tg-profile-meta-value">{created}</span>
                </div>
                <div className="tg-profile-meta-item">
                    <span className="tg-profile-meta-label">Обновлена</span>
                    <span className="tg-profile-meta-value">{updated}</span>
                </div>
                <div className="tg-profile-meta-item">
                    <span className="tg-profile-meta-label">Участников</span>
                    <span className="tg-profile-meta-value">{participantCount}</span>
                </div>
                <div className="tg-profile-meta-item">
                    <span className="tg-profile-meta-label">Команд</span>
                    <span className="tg-profile-meta-value">{teams.length}</span>
                </div>
            </div>

            {teams.length > 0 && session.game_type === 'team' && (
                <section className="tg-summary-section">
                    <h4>👥 Команды и участники</h4>
                    <div className="tg-teams">
                        {teams.map((team, idx) => (
                            <div key={team.id} className="tg-team"
                                 style={{ '--team-color': team.color, borderTopColor: team.color }}>
                                <div className="tg-team-header">
                                    <span className="tg-team-medal">
                                        {['🥇','🥈','🥉'][idx] || `#${idx + 1}`}
                                    </span>
                                    <span className="tg-team-name" style={{ color: team.color }}>{team.name}</span>
                                    <span className="tg-team-score">{team.score} <small>очков</small></span>
                                </div>
                                <div className="tg-team-count">{team.members.length} участников</div>
                                <div className="tg-team-members">
                                    {team.members.length === 0
                                        ? <span className="tg-no-members">Нет участников</span>
                                        : team.members.map(m => {
                                            const name = m.full_name || m.username || '?';
                                            const initials = name.split(' ')
                                                .map(w => w[0]).slice(0, 2).join('').toUpperCase();
                                            return (
                                                <div key={m.id} className="tg-member-row" title={name}>
                                                    <span className="tg-member-avatar"
                                                          style={{ background: team.color + '22', color: team.color }}>
                                                        {initials}
                                                    </span>
                                                    <span className="tg-member-name">{name}</span>
                                                </div>
                                            );
                                        })
                                    }
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {/* Full results: leaderboard, per-question stats, per-student answers,
                CSV export. SessionSummary handles the completed / not-yet-completed
                distinction via its own error state. */}
            {session.status === 'completed' ? (
                <SessionSummary sessionId={Number(sessionId)} />
            ) : (
                <div className="tg-summary-error" style={{ marginTop: '1rem' }}>
                    ℹ️ Итоги появятся, когда сессия будет завершена.
                </div>
            )}
        </div>
    );
}
