import { useState, useEffect } from 'react';
import './LeaderBoard.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';

const TABS = [
    { key: 'all',     label: 'Все время' },
    { key: 'monthly', label: 'Месяц'     },
    { key: 'weekly',  label: 'Неделя'    },
    { key: 'daily',   label: 'Сегодня'   },
];

function Leaderboard() {
    const { request } = useHttp();
    const [activeTab, setActiveTab] = useState('all');
    const [data,      setData]      = useState([]);
    const [myRank,    setMyRank]    = useState(null);
    const [loading,   setLoading]   = useState(true);
    const [error,     setError]     = useState('');

    const fetchRanking = (period) => {
        setLoading(true);
        setError('');
        request(`${API_URL}v1/rankings/leaderboard?period=${period}&limit=50`, 'GET', null, headers())
            .then(res => setData(Array.isArray(res) ? res : []))
            .catch(() => setError('Не удалось загрузить рейтинг'))
            .finally(() => setLoading(false));
    };

    const fetchMyRank = (period) => {
        request(`${API_URL}v1/rankings/me?period=${period}`, 'GET', null, headers())
            .then(res => setMyRank(res))
            .catch(() => {});
    };

    useEffect(() => {
        fetchRanking(activeTab);
        fetchMyRank(activeTab);
    }, [activeTab]);

    const getPoints = (student) => {
        switch (activeTab) {
            case 'daily':   return student.daily_points   ?? student.points ?? 0;
            case 'weekly':  return student.weekly_points  ?? student.points ?? 0;
            case 'monthly': return student.monthly_points ?? student.points ?? 0;
            default:        return student.points ?? 0;
        }
    };

    const getMyPoints = () => {
        if (!myRank) return '—';
        switch (activeTab) {
            case 'daily':   return myRank.daily_points   ?? '—';
            case 'weekly':  return myRank.weekly_points  ?? '—';
            case 'monthly': return myRank.monthly_points ?? '—';
            default:        return myRank.total_points   ?? '—';
        }
    };

    const getMyRankValue = () => {
        if (!myRank) return '—';
        let rank;
        switch (activeTab) {
            case 'daily':   rank = myRank.daily_rank;   break;
            case 'weekly':  rank = myRank.weekly_rank;  break;
            case 'monthly': rank = myRank.monthly_rank; break;
            default:        rank = myRank.global_rank;  break;
        }
        return (rank && rank !== '-') ? `#${rank}` : '—';
    };

    const getRankIcon = (rank) => {
        if (rank === 1) return '🥇';
        if (rank === 2) return '🥈';
        if (rank === 3) return '🥉';
        return rank;
    };

    return (
        <div className="leaderboard-container">

            {/* Header */}
            <div className="leaderboard-header">
                <h2>Рейтинг</h2>
                <div className="filter-tabs">
                    {TABS.map(t => (
                        <span
                            key={t.key}
                            className={activeTab === t.key ? 'active' : ''}
                            onClick={() => setActiveTab(t.key)}
                        >
                            {t.label}
                        </span>
                    ))}
                </div>
            </div>

            {/* Моя позиция */}
            {myRank && (
                <div className="lb-my-rank">
                    <div className="lb-my-rank-left">
                        <span className="lb-my-label">Моя позиция</span>
                        <span className="lb-my-pos">{getMyRankValue()}</span>
                    </div>
                    <div className="lb-my-rank-right">
                        <span className="lb-my-pts">{getMyPoints()}</span>
                        <span className="lb-my-pts-label">PTS</span>
                    </div>
                </div>
            )}

            {/* List */}
            <div className="ranking-list same-with-header">
                {loading ? (
                    <div className="lb-loading">
                        <div className="lb-spinner"/>
                        <p>Загрузка...</p>
                    </div>
                ) : error ? (
                    <div className="lb-error">
                        <p>{error}</p>
                        <button onClick={() => fetchRanking(activeTab)}>Повторить</button>
                    </div>
                ) : data.length === 0 ? (
                    <div className="lb-empty">Данных пока нет</div>
                ) : data.map((student, idx) => {
                    const rank = student.rank ?? idx + 1;
                    const name = student.full_name || student.username || 'Студент';
                    const pts  = getPoints(student);

                    return (
                        <div
                            key={student.student_id ?? idx}
                            className={`ranking-item ${rank <= 3 ? 'top-three' : ''}`}
                            style={{ animationDelay: `${idx * 0.04}s` }}
                        >
                            <div className="rank-number">{getRankIcon(rank)}</div>
                            <div className="student-info">
                                <div className="student-avatar">
                                    {student.avatar_url
                                        ? <img src={student.avatar_url} alt={name} className="lb-avatar-img"/>
                                        : <span className="lb-avatar-emoji">👤</span>
                                    }
                                </div>
                                <div className="name-box">
                                    <span className="student-name">{name}</span>
                                    <div className="lb-meta">
                                        {student.level && (
                                            <span className="student-level">{student.level}</span>
                                        )}
                                        {student.projects_completed > 0 && (
                                            <span className="lb-projects">📁 {student.projects_completed}</span>
                                        )}
                                    </div>
                                </div>
                            </div>
                            <div className="student-points">
                                <strong>{pts}</strong>
                                <span>PTS</span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

export default Leaderboard;