import React, { useState, useEffect, useRef } from 'react';
import './StudentRankings.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { Trophy, Star } from 'lucide-react';

const LIMIT = 50;

const PERIOD_OPTIONS = [
    { key: 'all',   label: 'Всё время' },
    { key: 'month', label: 'В этом месяце' },
    { key: 'week',  label: 'На неделе' },
    { key: 'day',   label: 'Сегодня' },
];

const PODIUM_COLORS = [
    { bg: '#FFD93D', text: '#7A5800', glow: 'rgba(255,217,61,0.4)',  medal: '🥇', ring: 'conic-gradient(#ffd700,#ffec6e,#f9ca24,#e6b800,#ffd700)' },
    { bg: '#B8C4CC', text: '#3A4A52', glow: 'rgba(184,196,204,0.4)', medal: '🥈', ring: 'conic-gradient(#b2bec3,#dfe6e9,#9eaab0,#cdd5da,#b2bec3)' },
    { bg: '#CD8B5A', text: '#5C3010', glow: 'rgba(205,139,90,0.4)',  medal: '🥉', ring: 'conic-gradient(#cd7f32,#e8a87c,#b8692a,#d4906a,#cd7f32)' },
];

function Avatar({ url, name, topIdx, size }) {
    const initials = name
        ? name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
        : '?';
    const colors = ['#6C5CE7','#00B894','#E17055','#0984E3','#E84393','#FDCB6E'];
    const color  = colors[(name?.charCodeAt(0) ?? 0) % colors.length];
    const c      = topIdx != null ? PODIUM_COLORS[topIdx] : null;

    return (
        <div
            className={`tsr-avatar ${size === 'lg' ? 'tsr-avatar--lg' : ''}`}
            style={c ? { borderColor: c.bg, boxShadow: `0 0 18px ${c.glow}` } : {}}
        >
            {url
                ? <img src={url} alt={name} />
                : <span style={{ background: color }}>{initials}</span>
            }
        </div>
    );
}

function PodiumSlot({ s, rank }) {
    const c      = PODIUM_COLORS[rank - 1];
    const name   = s?.full_name || s?.username || '—';
    const heights = { 1: 110, 2: 80, 3: 64 };

    if (!s) return (
        <div className="tsr-podium-slot tsr-podium-slot--empty">
            <div className="tsr-podium-bar" style={{ height: heights[rank], background: 'rgba(0,0,0,0.06)' }}>
                <span className="tsr-podium-rank-num">{rank}</span>
            </div>
        </div>
    );

    return (
        <div className={`tsr-podium-slot tsr-podium-slot--${rank}`}>
            <Avatar url={s.avatar_url} name={name} topIdx={rank - 1} size="lg" />
            <p className="tsr-podium-name">{name.split(' ')[0]}</p>
            <p className="tsr-podium-pts">
                {(s.total_points ?? 0).toLocaleString()}
                <span> pts</span>
            </p>
            {s.current_level && (
                <span className="tsr-podium-level">{s.current_level}</span>
            )}
            {s.best_course && (
                <span className="tsr-podium-best" title={s.best_course}>
                    <Star size={12} aria-hidden="true" /> {s.best_course.length > 14 ? s.best_course.slice(0, 14) + '…' : s.best_course}
                </span>
            )}
            <div className="tsr-podium-bar" style={{ height: heights[rank], background: c.bg }}>
                <span className="tsr-podium-medal">{c.medal}</span>
            </div>
        </div>
    );
}

export default function TeacherStudentsRankings() {
    const { request } = useHttp();

    const [items,   setItems]   = useState([]);
    const [total,   setTotal]   = useState(0);
    const [loading, setLoading] = useState(true);
    const [error,   setError]   = useState('');
    const [search,  setSearch]  = useState('');
    const [page,    setPage]    = useState(0);
    const [period,  setPeriod]  = useState('all');

    const searchTimer = useRef(null);
    const bodyRef     = useRef(null);

    const fetchData = (skip, searchVal, periodVal) => {
        setLoading(true);
        setError('');
        const q = searchVal ? `&search=${encodeURIComponent(searchVal)}` : '';
        const p = `&period=${encodeURIComponent(periodVal || 'all')}`;
        request(
            `${API_URL}v1/teacher/students/rankings?skip=${skip}&limit=${LIMIT}${q}${p}`,
            'GET', null, headers()
        )
            .then(res => { setItems(res.items || []); setTotal(res.total || 0); })
            .catch(() => { setItems([]); setTotal(0); setError('Не удалось загрузить рейтинг'); })
            .finally(() => setLoading(false));
    };

    useEffect(() => { fetchData(0, '', 'all'); }, []);

    const handleSearch = (e) => {
        const val = e.target.value;
        setSearch(val);
        setPage(0);
        clearTimeout(searchTimer.current);
        searchTimer.current = setTimeout(() => fetchData(0, val, period), 420);
    };

    const handlePeriod = (next) => {
        if (next === period) return;
        setPeriod(next);
        setPage(0);
        fetchData(0, search, next);
        bodyRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handlePage = (p) => {
        setPage(p);
        fetchData(p * LIMIT, search, period);
        bodyRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // When the teacher selects a time-period, use that period's points for
    // ranking display so the bar reflects the visible window — not lifetime.
    const ptsOf = (s) => period === 'all'
        ? (s.total_points ?? 0)
        : (s.period_points ?? 0);

    const top3 = items.slice(0, 3);
    const rest = items.slice(3);
    const podiumOrder = top3.length === 3
        ? [{ s: top3[1], rank: 2 }, { s: top3[0], rank: 1 }, { s: top3[2], rank: 3 }]
        : top3.map((s, i) => ({ s, rank: i + 1 }));

    const maxPts = ptsOf(items[0] || {}) || 1;
    // Hide the podium when filtering by a short window — too many ties at 0
    // make the gold/silver/bronze treatment misleading.
    const showPodium = period === 'all' && page === 0 && !search && top3.length >= 1;

    const pages = Math.ceil(total / LIMIT);
    const pageButtons = () => {
        if (pages <= 7) return Array.from({ length: pages }, (_, i) => i);
        const start = Math.max(0, Math.min(page - 3, pages - 7));
        return Array.from({ length: 7 }, (_, i) => start + i);
    };

    const listItems = showPodium ? rest : items;

    return (
        <div className="tsr-root">

            {/* ══ STICKY HEADER ══ */}
            <div className="tsr-header">
                <div className="tsr-header-inner">
                    <div className="tsr-title-block">
                        <span className="tsr-trophy" aria-hidden="true"><Trophy size={20} /></span>
                        <div>
                            <h2 className="tsr-title">Таблица лидеров</h2>
                            <p className="tsr-subtitle">
                                {total > 0 ? `${total} студентов · ${PERIOD_OPTIONS.find(p => p.key === period)?.label || ''}` : 'Рейтинг по баллам'}
                            </p>
                        </div>
                    </div>
                    <div className="tsr-search-wrap">
                        <span className="tsr-search-icon" aria-hidden="true">🔍</span>
                        <input
                            className="tsr-search"
                            type="text"
                            placeholder="Поиск студента…"
                            value={search}
                            onChange={handleSearch}
                        />
                        {search && (
                            <button className="tsr-search-clear" onClick={() => { setSearch(''); fetchData(0, '', period); setPage(0); }}>✕</button>
                        )}
                    </div>
                </div>
                <div className="tsr-period-row" role="tablist" aria-label="Период">
                    {PERIOD_OPTIONS.map(opt => (
                        <button
                            key={opt.key}
                            type="button"
                            role="tab"
                            aria-selected={period === opt.key}
                            className={`tsr-period-chip ${period === opt.key ? 'is-active' : ''}`}
                            onClick={() => handlePeriod(opt.key)}
                        >
                            {opt.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* ══ SCROLLABLE BODY ══ */}
            <div className="tsr-body" ref={bodyRef}>

                {loading && (
                    <div className="tsr-state">
                        <div className="tsr-spinner" />
                        <p>Загрузка рейтинга…</p>
                    </div>
                )}

                {!loading && error && (
                    <div className="tsr-state tsr-state--error">
                        <span className="tsr-state-icon">⚠️</span>
                        <p>{error}</p>
                        <button className="tsr-retry" onClick={() => fetchData(page * LIMIT, search, period)}>Повторить</button>
                    </div>
                )}

                {!loading && !error && items.length === 0 && (
                    <div className="tsr-state">
                        <span className="tsr-state-icon">📭</span>
                        <p>Студентов не найдено</p>
                    </div>
                )}

                {!loading && !error && items.length > 0 && (
                    <>
                        {/* ── PODIUM ── */}
                        {showPodium && (
                            <div className="tsr-podium">
                                {podiumOrder.map(({ s, rank }) => (
                                    <PodiumSlot key={s?.student_id ?? rank} s={s} rank={rank} />
                                ))}
                            </div>
                        )}

                        {/* ── LIST ── */}
                        <div className="tsr-list">
                            {listItems.map((s, idx) => {
                                // Always rank by this teacher's own visible-window points order.
                                // s.global_rank is the student's rank across the WHOLE platform
                                // (every teacher's students combined), so it's neither sequential
                                // nor even monotonic within one teacher's own list — e.g. a
                                // teacher's #4 student can easily be globally #52. Same reasoning
                                // already applied to the period-filtered case; it just didn't
                                // extend it to period === 'all'.
                                const rank = page * LIMIT + (showPodium ? idx + 4 : idx + 1);
                                const name   = s.full_name || s.username || 'Студент';
                                const pts    = ptsOf(s);
                                const pct    = Math.min(100, (pts / maxPts) * 100);
                                const bestPts = s.best_course_points;

                                return (
                                    <div
                                        key={s.student_id ?? idx}
                                        className="tsr-item"
                                        style={{ animationDelay: `${idx * 0.025}s` }}
                                    >
                                        {/* rank */}
                                        <span className="tsr-item-rank">{rank}</span>

                                        {/* avatar */}
                                        <Avatar url={s.avatar_url} name={name} topIdx={null} />

                                        {/* main info */}
                                        <div className="tsr-item-info">
                                            {/* row 1: name + points */}
                                            <div className="tsr-item-row tsr-item-row--top">
                                                <span className="tsr-item-name">{name}</span>
                                                <span className="tsr-item-pts">
                                                    {pts.toLocaleString()} <em>pts</em>
                                                </span>
                                            </div>

                                            {/* progress bar */}
                                            <div className="tsr-item-bar-wrap">
                                                <div className="tsr-item-bar" style={{ width: `${pct}%` }} />
                                            </div>

                                            {/* row 2: level + current_course + best_course */}
                                            <div className="tsr-item-row tsr-item-row--meta">
                                                {s.current_level && (
                                                    <span className="tsr-chip tsr-chip--level">
                                                        🎓 {s.current_level}
                                                    </span>
                                                )}
                                                {s.current_course && (
                                                    <span className="tsr-chip tsr-chip--course" title={s.current_course}>
                                                        📚 {s.current_course.length > 22 ? s.current_course.slice(0, 22) + '…' : s.current_course}
                                                    </span>
                                                )}
                                                {s.best_course && (
                                                    <span className="tsr-chip tsr-chip--best" title={s.best_course}>
                                                        <Star size={12} aria-hidden="true" /> {s.best_course.length > 18 ? s.best_course.slice(0, 18) + '…' : s.best_course}
                                                        {bestPts != null && (
                                                            <strong>+{bestPts.toLocaleString()}</strong>
                                                        )}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>

                        {/* ── PAGINATION ── */}
                        {pages > 1 && (
                            <div className="tsr-pagination">
                                <button className="tsr-page-btn" onClick={() => handlePage(page - 1)} disabled={page === 0}>‹</button>
                                {pageButtons().map(p => (
                                    <button
                                        key={p}
                                        className={`tsr-page-btn ${p === page ? 'active' : ''}`}
                                        onClick={() => handlePage(p)}
                                    >
                                        {p + 1}
                                    </button>
                                ))}
                                <button className="tsr-page-btn" onClick={() => handlePage(page + 1)} disabled={page >= pages - 1}>›</button>
                                <span className="tsr-page-info">стр. {page + 1} / {pages}</span>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}