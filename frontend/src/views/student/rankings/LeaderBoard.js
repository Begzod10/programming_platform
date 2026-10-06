import { useState, useEffect } from 'react';
import './LeaderBoard.css';
import { API_URL, useHttp, headers, resolveImageUrl } from '../../../api/search/base';
import { useAuth } from '../../../context/AuthContext';
import { useTranslation } from '../../../i18n/useTranslation';
import AppHeader from '../../../components/appheader/AppHeader';
import {
    Trophy, Crown, Medal, Infinity as InfinityIcon,
    CalendarDays, Calendar, Sun,
} from 'lucide-react';

const TABS = [
    { key: 'all',     labelKey: 'rating.periods.all',   Icon: InfinityIcon },
    { key: 'monthly', labelKey: 'rating.periods.month', Icon: CalendarDays },
    { key: 'weekly',  labelKey: 'rating.periods.week',  Icon: Calendar },
    { key: 'daily',   labelKey: 'rating.periods.today', Icon: Sun },
];

// Display order on the podium: silver (2), gold (1), bronze (3)
const PODIUM_RANKS = [2, 1, 3];
const AVATAR_PALETTE = ['#8b7bf2', '#36e06b', '#e17055', '#22d3ee', '#e84393', '#fbbf24'];

const prefersReduced = () =>
    typeof window !== 'undefined' && window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function formatPoints(value) {
    if (typeof value !== 'number' || Number.isNaN(value)) return '—';
    return value.toLocaleString('ru-RU').replace(/,/g, ' ');
}
function initialsOf(name) {
    if (!name) return '?';
    return name.split(' ').filter(Boolean).map(w => w[0]).join('').slice(0, 2).toUpperCase();
}

function Avatar({ url, name, size, ring }) {
    const initials = initialsOf(name);
    const color = AVATAR_PALETTE[(name?.charCodeAt(0) ?? 0) % AVATAR_PALETTE.length];
    const src = resolveImageUrl(url);
    return (
        <div className={`lb-avatar ${ring ? `lb-avatar--${ring}` : ''}`} style={{ width: size, height: size }}>
            {src
                ? <img src={src} alt={name} onError={e => { e.target.style.display = 'none'; }} />
                : <span style={{ background: color }}>{initials}</span>}
        </div>
    );
}

/* ── Podium column (avatar + crown on top, glass block below) ── */
function PodiumColumn({ student, rank, getPoints, isMe, t }) {
    const empty = !student;
    const name = student ? (student.full_name || student.username || '—') : '—';
    const pts  = student ? getPoints(student) : 0;

    return (
        <div className={`lb-pcol lb-pcol--${rank} ${empty ? 'lb-pcol--empty' : ''}`}>
            {!empty && (
                <div className="lb-pcol-top">
                    <span className={`lb-crown lb-crown--${rank}`} aria-hidden="true"><Crown size={rank === 1 ? 26 : 20} /></span>
                    <Avatar url={student.avatar_url} name={name} size={rank === 1 ? 92 : 76}
                        ring={rank === 1 ? 'gold' : rank === 2 ? 'silver' : 'bronze'} />
                    <p className="lb-pcol-name">
                        {name.split(' ')[0]}
                        {isMe && <span className="lb-chip-you">{t('rating.you')}</span>}
                    </p>
                    <p className="lb-pcol-pts">{formatPoints(pts)} <span>{t('rating.pts')}</span></p>
                </div>
            )}
            <div className={`lb-block lb-block--${rank} ${isMe ? 'lb-block--me' : ''}`}>
                <span className="lb-block-glow" aria-hidden="true" />
                {rank === 1
                    ? <Crown size={26} className="lb-block-ico" aria-hidden="true" />
                    : <Medal size={22} className="lb-block-ico" aria-hidden="true" />}
                <span className="lb-block-num">{rank}</span>
            </div>
        </div>
    );
}

function SkeletonPodium() {
    return (
        <div className="lb-podium" aria-hidden="true">
            {PODIUM_RANKS.map(rank => (
                <div key={rank} className={`lb-pcol lb-pcol--${rank}`}>
                    <div className="lb-pcol-top">
                        <div className="lb-skel lb-skel-avatar" />
                        <div className="lb-skel lb-skel-line" style={{ width: 64 }} />
                        <div className="lb-skel lb-skel-line" style={{ width: 48 }} />
                    </div>
                    <div className={`lb-block lb-block--${rank} lb-block--skeleton`} />
                </div>
            ))}
        </div>
    );
}

function SkeletonRows() {
    return (
        <ol className="lb-list" aria-hidden="true">
            {Array.from({ length: 6 }).map((_, i) => (
                <li key={i} className="lb-row lb-row--skeleton">
                    <span className="lb-skel lb-skel-rank" />
                    <span className="lb-skel lb-skel-avatar-sm" />
                    <div className="lb-row-info">
                        <div className="lb-skel lb-skel-line" style={{ width: '42%' }} />
                        <div className="lb-skel lb-row-bar-wrap" />
                    </div>
                </li>
            ))}
        </ol>
    );
}

export default function Leaderboard() {
    const { request } = useHttp();
    const { user } = useAuth();
    const { t, lang } = useTranslation();
    const ru = lang === 'ru';
    const [activeTab, setActiveTab] = useState('all');
    const [data, setData] = useState([]);
    const [myRank, setMyRank] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [myRankError, setMyRankError] = useState('');
    const [groups, setGroups] = useState([]);
    const [groupId, setGroupId] = useState('');

    const fetchRanking = (period, groupIdVal) => {
        setLoading(true);
        setError('');
        const g = groupIdVal ? `&group_id=${encodeURIComponent(groupIdVal)}` : '';
        request(`${API_URL}v1/rankings/leaderboard?period=${period}&limit=50${g}`, 'GET', null, headers())
            .then(res => setData(Array.isArray(res) ? res : []))
            .catch(() => setError(t('rating.loadError')))
            .finally(() => setLoading(false));
    };
    const fetchMyRank = (period) => {
        setMyRankError('');
        request(`${API_URL}v1/rankings/me?period=${period}`, 'GET', null, headers())
            .then(res => setMyRank(res))
            .catch(() => setMyRankError(t('rating.loadError')));
    };

    useEffect(() => {
        request(`${API_URL}v1/rankings/my-groups`, 'GET', null, headers())
            .then(res => setGroups(Array.isArray(res) ? res : []))
            .catch(() => setGroups([]));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => {
        fetchRanking(activeTab, groupId);
        fetchMyRank(activeTab);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [activeTab]);

    const handleGroupChange = (e) => { const next = e.target.value; setGroupId(next); fetchRanking(activeTab, next); };

    const getPoints = (student) => {
        switch (activeTab) {
            case 'daily':   return student.daily_points   ?? student.points ?? 0;
            case 'weekly':  return student.weekly_points  ?? student.points ?? 0;
            case 'monthly': return student.monthly_points ?? student.points ?? 0;
            default:        return student.points ?? 0;
        }
    };
    const getMyPoints = () => {
        if (!myRank) return null;
        switch (activeTab) {
            case 'daily':   return myRank.daily_points   ?? null;
            case 'weekly':  return myRank.weekly_points  ?? null;
            case 'monthly': return myRank.monthly_points ?? null;
            default:        return myRank.total_points   ?? null;
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

    const isCurrentUser = (student) => {
        if (!student || !user) return false;
        if (student.student_id != null && user.id != null && Number(student.student_id) === Number(user.id)) return true;
        if (student.username && user.username) return student.username === user.username;
        return false;
    };

    const top3 = data.slice(0, 3);
    const rest = data.slice(3);
    const leaderPoints = data.length > 0 ? getPoints(data[0]) : 0;

    return (
        <div className="lb-page">
            <AppHeader />

            <div className="lb-shell">
                {/* ── my-rank band + period tabs ── */}
                <div className="lb-top">
                    {myRankError && !myRank ? (
                        // A failed my-rank request must say so (with a retry) — a silent
                        // "—" left students unable to tell an error from "no rank yet".
                        <div className="lb-myband lb-myrank lb-myrank--error">
                            <span className="lb-myrank-error-text">{myRankError}</span>
                            <button type="button" className="lb-retry lb-retry--sm"
                                onClick={() => fetchMyRank(activeTab)}>
                                {t('rating.retry')}
                            </button>
                        </div>
                    ) : (
                    <div className="lb-myband lb-myrank">
                        <div className="lb-myband-l">
                            <span className="lb-myband-ico" aria-hidden="true"><Trophy size={18} /></span>
                            <span className="lb-myband-label">{t('rating.myPlace')}</span>
                            <span className="lb-myband-pos">{getMyRankValue()}</span>
                        </div>
                        <div className="lb-myband-r">
                            <span className="lb-myband-pts">{formatPoints(getMyPoints())}</span>
                            <span className="lb-myband-unit">{t('rating.pts')}</span>
                        </div>
                    </div>
                    )}

                    <div className="lb-controls">
                        <div className="lb-tabs">
                            {TABS.map(tab => {
                                const Icon = tab.Icon;
                                const active = activeTab === tab.key;
                                return (
                                    <button key={tab.key} type="button"
                                        className={`lb-tab ${active ? 'lb-tab--active' : ''}`}
                                        aria-pressed={active} onClick={() => setActiveTab(tab.key)}>
                                        <Icon size={14} aria-hidden="true" />
                                        <span className="lb-tab-label">{t(tab.labelKey)}</span>
                                    </button>
                                );
                            })}
                        </div>
                        {groups.length > 0 && (
                            <select className="lb-group-select" value={groupId} onChange={handleGroupChange}
                                aria-label={ru ? 'Фильтр по классу' : "Sinf bo'yicha filtrlash"}>
                                <option value="">{ru ? 'Все классы' : 'Barcha sinflar'}</option>
                                {groups.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
                            </select>
                        )}
                    </div>
                </div>

                {loading ? (
                    <>
                        <SkeletonPodium />
                        <SkeletonRows />
                    </>
                ) : error ? (
                    <div className="lb-state lb-state--error">
                        <span className="lb-state-icon" aria-hidden="true">⚠</span>
                        <p>{error}</p>
                        <button type="button" className="lb-retry" onClick={() => fetchRanking(activeTab, groupId)}>
                            {t('rating.retry')}
                        </button>
                    </div>
                ) : data.length === 0 ? (
                    <div className="lb-state lb-state--empty">
                        <Trophy size={40} className="lb-state-trophy" aria-hidden="true" />
                        <p className="lb-state-title">{t('rating.emptyTitle')}</p>
                        <p className="lb-state-hint">{t('rating.emptyHint')}</p>
                    </div>
                ) : (
                    <>
                        {/* ── PODIUM ── */}
                        {top3.length > 0 && (
                            <div className="lb-podium">
                                <span className="lb-trophy lb-trophy--l" aria-hidden="true"><Trophy size={64} /></span>
                                {PODIUM_RANKS.map(rank => (
                                    <PodiumColumn key={rank} rank={rank} student={top3[rank - 1]}
                                        getPoints={getPoints} isMe={isCurrentUser(top3[rank - 1])} t={t} />
                                ))}
                                <span className="lb-trophy lb-trophy--r" aria-hidden="true"><Trophy size={64} /></span>
                            </div>
                        )}

                        {/* ── LIST (4+) ── */}
                        {rest.length > 0 && (
                            <ol className="lb-list">
                                {rest.map((student, idx) => {
                                    const rank = student.rank ?? idx + 4;
                                    const name = student.full_name || student.username || '—';
                                    const pts  = getPoints(student);
                                    const pct  = leaderPoints > 0 ? Math.max(3, Math.round((pts / leaderPoints) * 100)) : 0;
                                    const mine = isCurrentUser(student);
                                    return (
                                        <li key={student.student_id ?? idx} className={`lb-row ${mine ? 'lb-row--me' : ''}`}
                                            style={prefersReduced() ? undefined : { animationDelay: `${Math.min(idx, 10) * 0.045}s` }}>
                                            <span className="lb-row-rank">{rank}</span>
                                            <Avatar url={student.avatar_url} name={name} size={46} />
                                            <div className="lb-row-info">
                                                <span className="lb-row-name">
                                                    <span className="lb-row-name-txt">{name}</span>
                                                    {mine && <span className="lb-chip-you">{t('rating.you')}</span>}
                                                </span>
                                                <div className="lb-row-bar-wrap">
                                                    <div className="lb-row-bar" style={{ width: `${pct}%` }} />
                                                </div>
                                            </div>
                                            <div className="lb-row-right">
                                                <span className="lb-row-pts">{formatPoints(pts)}</span>
                                                <span className="lb-row-unit">{t('rating.pts')}</span>
                                            </div>
                                        </li>
                                    );
                                })}
                            </ol>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
