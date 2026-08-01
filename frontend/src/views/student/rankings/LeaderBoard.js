import { useState, useEffect, useRef } from 'react';
import './LeaderBoard.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { useAuth } from '../../../context/AuthContext';
import { useTranslation } from '../../../i18n/useTranslation';
import {
    Trophy,
    Crown,
    Medal,
    Infinity as InfinityIcon,
    CalendarDays,
    Calendar,
    Sun,
} from 'lucide-react';

const TABS = [
    { key: 'all',     labelKey: 'rating.periods.all',   Icon: InfinityIcon },
    { key: 'monthly', labelKey: 'rating.periods.month', Icon: CalendarDays },
    { key: 'weekly',  labelKey: 'rating.periods.week',  Icon: Calendar },
    { key: 'daily',   labelKey: 'rating.periods.today', Icon: Sun },
];

// Display order on the podium: silver, gold, bronze
const PODIUM_RANKS = [2, 1, 3];

const AVATAR_PALETTE = ['#6C5CE7', '#00B894', '#E17055', '#0984E3', '#E84393', '#FDCB6E'];

function formatPoints(value) {
    if (typeof value !== 'number' || Number.isNaN(value)) return '—';
    return value.toLocaleString('ru-RU');
}

function initialsOf(name) {
    if (!name) return '?';
    return name.split(' ').filter(Boolean).map(w => w[0]).join('').slice(0, 2).toUpperCase();
}

function Avatar({ url, name, size, ring }) {
    const initials = initialsOf(name);
    const color = AVATAR_PALETTE[(name?.charCodeAt(0) ?? 0) % AVATAR_PALETTE.length];

    return (
        <div
            className={`lb-avatar ${ring ? `lb-avatar--${ring}` : ''}`}
            style={{ width: size, height: size }}
        >
            {url
                ? <img src={url} alt={name} />
                : <span style={{ background: color }}>{initials}</span>}
        </div>
    );
}

function PodiumColumn({ student, rank, getPoints, isMe, t }) {
    const empty = !student;
    const name = student ? (student.full_name || student.username || '—') : '—';
    const pts  = student ? getPoints(student) : 0;
    const Icon = rank === 1 ? Crown : Medal;

    return (
        <div className={`lb-podium-col lb-podium-col--${rank} ${empty ? 'lb-podium-col--empty' : ''}`}>
            {!empty && (
                <>
                    <Avatar
                        url={student.avatar_url}
                        name={name}
                        size={rank === 1 ? 66 : 56}
                        ring={rank === 1 ? 'gold' : 'white'}
                    />
                    <p className="lb-podium-name">
                        {name.split(' ')[0]}
                        {isMe && <span className="lb-chip-you">{t('rating.you')}</span>}
                    </p>
                    <p className="lb-podium-pts">
                        {formatPoints(pts)} <span>{t('rating.pts')}</span>
                    </p>
                </>
            )}
            <div className={`lb-podium-block lb-podium-block--${rank} ${isMe ? 'lb-podium-block--me' : ''}`}>
                <Icon size={18} className="lb-podium-icon" aria-hidden="true" />
                <span className="lb-podium-num">{rank}</span>
            </div>
        </div>
    );
}

function SkeletonPodium() {
    return (
        <div className="lb-podium" aria-hidden="true">
            {PODIUM_RANKS.map(rank => (
                <div key={rank} className={`lb-podium-col lb-podium-col--${rank}`}>
                    <div className="lb-skel lb-skel-avatar" />
                    <div className="lb-skel lb-skel-line" style={{ width: 56 }} />
                    <div className="lb-skel lb-skel-line" style={{ width: 40 }} />
                    <div className={`lb-podium-block lb-podium-block--${rank} lb-podium-block--skeleton`} />
                </div>
            ))}
        </div>
    );
}

function SkeletonRows() {
    return (
        <ol className="lb-list" aria-hidden="true">
            {Array.from({ length: 5 }).map((_, i) => (
                <li key={i} className="lb-item lb-item--skeleton">
                    <span className="lb-skel lb-skel-rank" />
                    <span className="lb-skel lb-skel-avatar-sm" />
                    <div className="lb-item-info">
                        <div className="lb-skel lb-skel-line" style={{ width: '48%' }} />
                        <div className="lb-skel lb-item-bar-wrap" />
                    </div>
                </li>
            ))}
        </ol>
    );
}

export default function Leaderboard() {
    const { request } = useHttp();
    const { user } = useAuth();
    const { t } = useTranslation();
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
            .catch(() => setError(t('rating.loadError')))
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
    }, [activeTab]); // eslint-disable-line

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

    // MyRankingRead has no student_id/username — match the current user against
    // list rows via the auth user's id (Ranking.student_id references the same
    // students table row as the logged-in user), with username as a fallback.
    const isCurrentUser = (student) => {
        if (!student || !user) return false;
        if (student.student_id != null && user.id != null
            && Number(student.student_id) === Number(user.id)) return true;
        if (student.username && user.username) return student.username === user.username;
        return false;
    };

    const top3 = data.slice(0, 3);
    const rest = data.slice(3);
    const leaderPoints = data.length > 0 ? getPoints(data[0]) : 0;

    return (
        <div className="lb">

            {/* ── HEADER ── */}
            <div className="lb-header">
                <div className="lb-header-top">
                    <div className="lb-title-block">
                        <span className="lb-trophy-chip" aria-hidden="true"><Trophy size={18} /></span>
                        <div>
                            <h1 className="lb-title">{t('rating.title')}</h1>
                            <p className="lb-subtitle">
                                {t('rating.students').replace('{count}', data.length.toLocaleString('ru-RU'))}
                            </p>
                        </div>
                    </div>

                    <div className="lb-tabs">
                        {TABS.map(tab => {
                            const Icon = tab.Icon;
                            const active = activeTab === tab.key;
                            return (
                                <button
                                    key={tab.key}
                                    type="button"
                                    className={`lb-tab ${active ? 'lb-tab--active' : ''}`}
                                    aria-pressed={active}
                                    onClick={() => setActiveTab(tab.key)}
                                >
                                    <Icon size={13} className="lb-tab-icon" aria-hidden="true" />
                                    <span className="lb-tab-label">{t(tab.labelKey)}</span>
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* My rank band — always anchors the current user, even on the podium */}
                {myRank && (
                    <div className="lb-myrank">
                        <div className="lb-myrank-left">
                            <span className="lb-myrank-label">{t('rating.myPlace')}</span>
                            <span className="lb-myrank-pos">{getMyRankValue()}</span>
                        </div>
                        <div className="lb-myrank-right">
                            <span className="lb-myrank-pts">{formatPoints(getMyPoints())}</span>
                            <span className="lb-myrank-unit">{t('rating.pts')}</span>
                        </div>
                    </div>
                )}
            </div>

            {/* ── SCROLLABLE BODY ── */}
            <div className="lb-body" ref={listRef}>

                {loading ? (
                    <>
                        <SkeletonPodium />
                        <SkeletonRows />
                    </>
                ) : error ? (
                    <div className="lb-state lb-state--error">
                        <span className="lb-state-icon" aria-hidden="true">⚠</span>
                        <p>{error}</p>
                        <button type="button" className="lb-retry" onClick={() => fetchRanking(activeTab)}>
                            {t('rating.retry')}
                        </button>
                    </div>
                ) : data.length === 0 ? (
                    <div className="lb-state lb-state--empty">
                        <Trophy size={34} className="lb-state-trophy" aria-hidden="true" />
                        <p className="lb-state-title">{t('rating.emptyTitle')}</p>
                        <p className="lb-state-hint">{t('rating.emptyHint')}</p>
                    </div>
                ) : (
                    <>
                        {/* ── PODIUM (top 3) ── */}
                        {top3.length > 0 && (
                            <div className="lb-podium">
                                {PODIUM_RANKS.map(rank => (
                                    <PodiumColumn
                                        key={rank}
                                        rank={rank}
                                        student={top3[rank - 1]}
                                        getPoints={getPoints}
                                        isMe={isCurrentUser(top3[rank - 1])}
                                        t={t}
                                    />
                                ))}
                            </div>
                        )}

                        {/* ── LIST (4+) ── */}
                        {rest.length > 0 && (
                            <>
                                <div className="lb-list-caption">{t('rating.barCaption')}</div>
                                <ol className="lb-list">
                                    {rest.map((student, idx) => {
                                        const rank = student.rank ?? idx + 4;
                                        const name = student.full_name || student.username || '—';
                                        const pts  = getPoints(student);
                                        const pct  = leaderPoints > 0 ? Math.round((pts / leaderPoints) * 100) : 0;
                                        const mine = isCurrentUser(student);

                                        return (
                                            <li
                                                key={student.student_id ?? idx}
                                                className={`lb-item ${mine ? 'lb-item--me' : ''}`}
                                            >
                                                <span className="lb-item-rank">{rank}</span>

                                                <Avatar url={student.avatar_url} name={name} size={38} />

                                                <div className="lb-item-info">
                                                    <span className="lb-item-name">
                                                        {name}
                                                        {mine && <span className="lb-chip-you">{t('rating.you')}</span>}
                                                    </span>
                                                    <div className="lb-item-bar-wrap">
                                                        <div className="lb-item-bar" style={{ width: `${pct}%` }} />
                                                    </div>
                                                </div>

                                                <div className="lb-item-right">
                                                    <span className="lb-item-pts">
                                                        {formatPoints(pts)} <em>{t('rating.pts')}</em>
                                                    </span>
                                                    <span className="lb-item-pct">{pct}%</span>
                                                </div>
                                            </li>
                                        );
                                    })}
                                </ol>
                            </>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
