import { useState, useEffect, useRef } from 'react';
import './LeaderBoard.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';

const TABS = [
    { key: 'all',     label: 'Barcha vaqt', icon: '∞' },
    { key: 'monthly', label: 'Oy',           icon: '◑' },
    { key: 'weekly',  label: 'Hafta',        icon: '◔' },
    { key: 'daily',   label: 'Bugun',        icon: '○' },
];

const PODIUM_COLORS = [
    { bg: '#FFD93D', text: '#7A5800', glow: 'rgba(255,217,61,0.4)',  medal: '🥇' },
    { bg: '#B8C4CC', text: '#3A4A52', glow: 'rgba(184,196,204,0.4)', medal: '🥈' },
    { bg: '#CD8B5A', text: '#5C3010', glow: 'rgba(205,139,90,0.4)',  medal: '🥉' },
];

function Avatar({ url, name, rank }) {
    const initials = name
        ? name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
        : '?';
    const colors = ['#6C5CE7','#00B894','#E17055','#0984E3','#E84393','#FDCB6E'];
    const color  = colors[(name?.charCodeAt(0) ?? 0) % colors.length];

    return (
        <div className={`lb-avatar ${rank <= 3 ? 'lb-avatar--top' : ''}`}
             style={rank <= 3 ? { borderColor: PODIUM_COLORS[rank-1].bg, boxShadow: `0 0 16px ${PODIUM_COLORS[rank-1].glow}` } : {}}>
            {url
                ? <img src={url} alt={name} />
                : <span style={{ background: color }}>{initials}</span>
            }
        </div>
    );
}

function PodiumBar({ student, rank, getPoints }) {
    const c      = PODIUM_COLORS[rank - 1];
    const name   = student?.full_name || student?.username || '—';
    const pts    = student ? getPoints(student) : 0;
    const heights = { 1: 110, 2: 80, 3: 64 };

    if (!student) return (
        <div className="lb-podium-slot lb-podium-slot--empty">
            <div className="lb-podium-bar" style={{ height: heights[rank], background: 'rgba(255,255,255,0.04)' }}>
                <span className="lb-podium-rank-num">{rank}</span>
            </div>
        </div>
    );

    return (
        <div className={`lb-podium-slot lb-podium-slot--${rank}`}>
            <Avatar url={student.avatar_url} name={name} rank={rank} />
            <p className="lb-podium-name">{name.split(' ')[0]}</p>
            <p className="lb-podium-pts">{pts} <span>pts</span></p>
            <div className="lb-podium-bar" style={{ height: heights[rank], background: c.bg }}>
                <span className="lb-podium-medal">{c.medal}</span>
            </div>
        </div>
    );
}

export default function Leaderboard() {
    const { request } = useHttp();
    const [activeTab, setActiveTab] = useState('all');
    const [data,      setData]      = useState([]);
    const [myRank,    setMyRank]    = useState(null);
    const [loading,   setLoading]   = useState(true);
    const [error,     setError]     = useState('');
    const listRef = useRef(null);

    const fetchRanking = (period) => {
        setLoading(true);
        setError('');
        request(`${API_URL}v1/rankings/leaderboard?period=${period}&limit=50`, 'GET', null, headers())
            .then(res => setData(Array.isArray(res) ? res : []))
            .catch(() => setError("Reytingni yuklab bo'lmadi"))
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
        listRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
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

    const top3   = data.slice(0, 3);
    const rest   = data.slice(3);

    return (
        <div className="lb">

            {/* ── HEADER (sticky) ── */}
            <div className="lb-header">
                <div className="lb-header-top">
                    <div className="lb-title-block">
                        <span className="lb-trophy">🏆</span>
                        <div>
                            <h2 className="lb-title">Reyting</h2>
                            <p className="lb-subtitle">{data.length} ta talaba</p>
                        </div>
                    </div>
                    <div className="lb-tabs">
                        {TABS.map(t => (
                            <button
                                key={t.key}
                                className={`lb-tab ${activeTab === t.key ? 'lb-tab--active' : ''}`}
                                onClick={() => setActiveTab(t.key)}
                            >
                                <span className="lb-tab-icon">{t.icon}</span>
                                <span className="lb-tab-label">{t.label}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* My rank band */}
                {myRank && (
                    <div className="lb-myrank">
                        <div className="lb-myrank-left">
                            <span className="lb-myrank-label">Mening o'rnim</span>
                            <span className="lb-myrank-pos">{getMyRankValue()}</span>
                        </div>
                        <div className="lb-myrank-right">
                            <span className="lb-myrank-pts">{getMyPoints()}</span>
                            <span className="lb-myrank-unit">PTS</span>
                        </div>
                    </div>
                )}
            </div>

            {/* ── SCROLLABLE BODY ── */}
            <div className="lb-body" ref={listRef}>

                {loading ? (
                    <div className="lb-state">
                        <div className="lb-spinner" />
                        <p>Yuklanmoqda…</p>
                    </div>
                ) : error ? (
                    <div className="lb-state lb-state--error">
                        <span className="lb-state-icon">⚠</span>
                        <p>{error}</p>
                        <button className="lb-retry" onClick={() => fetchRanking(activeTab)}>
                            Qayta urinish
                        </button>
                    </div>
                ) : data.length === 0 ? (
                    <div className="lb-state">
                        <span className="lb-state-icon">📭</span>
                        <p>Hozircha ma'lumot yo'q</p>
                    </div>
                ) : (
                    <>
                        {/* ── PODIUM (top 3) ── */}
                        {top3.length > 0 && (
                            <div className="lb-podium">
                                <PodiumBar student={top3[1]} rank={2} getPoints={getPoints} />
                                <PodiumBar student={top3[0]} rank={1} getPoints={getPoints} />
                                <PodiumBar student={top3[2]} rank={3} getPoints={getPoints} />
                            </div>
                        )}

                        {/* ── LIST (4+) ── */}
                        <div className="lb-list">
                            {rest.map((student, idx) => {
                                const rank = student.rank ?? idx + 4;
                                const name = student.full_name || student.username || 'Talaba';
                                const pts  = getPoints(student);
                                const pct  = data.length > 0 ? (pts / (getPoints(data[0]) || 1)) * 100 : 0;

                                return (
                                    <div
                                        key={student.student_id ?? idx}
                                        className="lb-item"
                                        style={{ animationDelay: `${idx * 0.03}s` }}
                                    >
                                        <span className="lb-item-rank">{rank}</span>

                                        <Avatar url={student.avatar_url} name={name} rank={rank} />

                                        <div className="lb-item-info">
                                            <div className="lb-item-top">
                                                <span className="lb-item-name">{name}</span>
                                                <span className="lb-item-pts">{pts} <em>pts</em></span>
                                            </div>
                                            <div className="lb-item-bar-wrap">
                                                <div
                                                    className="lb-item-bar"
                                                    style={{ width: `${pct}%` }}
                                                />
                                            </div>
                                            {(student.level || student.projects_completed > 0) && (
                                                <div className="lb-item-meta">
                                                    {student.level && <span className="lb-badge">{student.level}</span>}
                                                    {student.projects_completed > 0 && (
                                                        <span className="lb-badge lb-badge--dim">📁 {student.projects_completed} loyiha</span>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}