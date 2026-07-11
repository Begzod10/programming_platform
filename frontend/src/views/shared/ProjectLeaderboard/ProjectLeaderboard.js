import React, { useState, useEffect, useRef } from 'react';
// Reuse the teacher leaderboard's CSS verbatim — the visual contract is
// identical (sticky header, podium, list, pagination) so a second copy
// would just rot.
import '../../teacher/StudentRankings/StudentRankings.css';
import { Star } from 'lucide-react';
import './ProjectLeaderboard.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';

const LIMIT = 50;

const PERIOD_OPTIONS = [
    { key: 'all',   label: 'Всё время' },
    { key: 'month', label: 'В этом месяце' },
    { key: 'week',  label: 'На неделе' },
    { key: 'day',   label: 'Сегодня' },
];

const PODIUM_COLORS = [
    { bg: '#FFD93D', glow: 'rgba(255,217,61,0.4)',  medal: '🥇' },
    { bg: '#B8C4CC', glow: 'rgba(184,196,204,0.4)', medal: '🥈' },
    { bg: '#CD8B5A', glow: 'rgba(205,139,90,0.4)',  medal: '🥉' },
];

function Avatar({ url, name, topIdx, size }) {
    const initials = name
        ? name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
        : '?';
    const palette = ['#6C5CE7','#00B894','#E17055','#0984E3','#E84393','#FDCB6E'];
    const color   = palette[(name?.charCodeAt(0) ?? 0) % palette.length];
    const c       = topIdx != null ? PODIUM_COLORS[topIdx] : null;

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
    const c       = PODIUM_COLORS[rank - 1];
    const name    = s?.full_name || s?.username || '—';
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
                {(s.project_points ?? 0).toLocaleString()}<span> pts</span>
            </p>
            {s.current_level && <span className="tsr-podium-level">{s.current_level}</span>}
            <div className="tsr-podium-chips">
                {s.projects_count > 0 && (
                    <span className="tsr-chip tsr-chip--proj">
                        📁 {s.projects_count} {s.projects_count === 1 ? 'проект' : 'проектов'}
                    </span>
                )}
                {s.avg_grade > 0 && (
                    <span className="tsr-chip tsr-chip--course" title="Средний балл по проектам">
                        Ср. {s.avg_grade}
                    </span>
                )}
                {s.best_course && (
                    <span className="tsr-chip tsr-chip--best" title={s.best_course}>
                        ⭐ {s.best_course.length > 14 ? s.best_course.slice(0, 14) + '…' : s.best_course}
                        {s.best_course_points != null && (
                            <strong>+{s.best_course_points.toLocaleString()}</strong>
                        )}
                    </span>
                )}
            </div>
            <div className="tsr-podium-bar" style={{ height: heights[rank], background: c.bg }}>
                <span className="tsr-podium-medal">{c.medal}</span>
            </div>
        </div>
    );
}

export default function ProjectLeaderboard({ role = 'student' }) {
    const { request } = useHttp();

    const [items,   setItems]   = useState([]);
    const [total,   setTotal]   = useState(0);
    const [loading, setLoading] = useState(true);
    const [error,   setError]   = useState('');
    const [search,  setSearch]  = useState('');
    const [page,    setPage]    = useState(0);
    const [period,  setPeriod]  = useState('all');
    const [courseId, setCourseId] = useState('');
    const [courses, setCourses] = useState([]);
    const [groupId,   setGroupId]   = useState('');
    const [groups,    setGroups]    = useState([]);
    const [teacherId, setTeacherId] = useState('');
    const [teachers,  setTeachers]  = useState([]);

    const searchTimer = useRef(null);
    const bodyRef     = useRef(null);

    const fetchData = (skip, searchVal, periodVal, courseIdVal, groupIdVal, teacherIdVal) => {
        setLoading(true);
        setError('');
        const q  = searchVal    ? `&search=${encodeURIComponent(searchVal)}` : '';
        const p  = `&period=${encodeURIComponent(periodVal || 'all')}`;
        const c  = courseIdVal  ? `&course_id=${encodeURIComponent(courseIdVal)}` : '';
        const g  = groupIdVal   ? `&group_id=${encodeURIComponent(groupIdVal)}` : '';
        const t  = teacherIdVal ? `&teacher_id=${encodeURIComponent(teacherIdVal)}` : '';
        request(
            `${API_URL}v1/rankings/project-leaderboard?skip=${skip}&limit=${LIMIT}${q}${p}${c}${g}${t}`,
            'GET', null, headers()
        )
            .then(res => { setItems(res?.items || []); setTotal(res?.total || 0); })
            .catch(() => { setItems([]); setTotal(0); setError('Не удалось загрузить рейтинг'); })
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        request(`${API_URL}v1/rankings/project-leaderboard/courses`, 'GET', null, headers())
            .then(res => setCourses(Array.isArray(res) ? res : []))
            .catch(() => setCourses([]));
        request(`${API_URL}v1/rankings/groups`, 'GET', null, headers())
            .then(res => setGroups(Array.isArray(res) ? res : []))
            .catch(() => setGroups([]));
        request(`${API_URL}v1/rankings/teachers`, 'GET', null, headers())
            .then(res => setTeachers(Array.isArray(res) ? res : []))
            .catch(() => setTeachers([]));
        fetchData(0, '', 'all', '', '', '');
    }, []);  // eslint-disable-line

    const handleSearch = (e) => {
        const val = e.target.value;
        setSearch(val);
        setPage(0);
        clearTimeout(searchTimer.current);
        searchTimer.current = setTimeout(() => fetchData(0, val, period, courseId, groupId, teacherId), 420);
    };

    const handlePeriod = (next) => {
        if (next === period) return;
        setPeriod(next);
        setPage(0);
        fetchData(0, search, next, courseId, groupId, teacherId);
        bodyRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleCourse = (e) => {
        const next = e.target.value;
        setCourseId(next);
        setPage(0);
        fetchData(0, search, period, next, groupId, teacherId);
        bodyRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleGroup = (e) => {
        const next = e.target.value;
        setGroupId(next);
        setPage(0);
        fetchData(0, search, period, courseId, next, teacherId);
        bodyRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleTeacher = (e) => {
        const next = e.target.value;
        setTeacherId(next);
        setPage(0);
        fetchData(0, search, period, courseId, groupId, next);
        bodyRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handlePage = (p) => {
        setPage(p);
        fetchData(p * LIMIT, search, period, courseId, groupId, teacherId);
        bodyRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const top3 = items.slice(0, 3);
    const rest = items.slice(3);
    const podiumOrder = top3.length === 3
        ? [{ s: top3[1], rank: 2 }, { s: top3[0], rank: 1 }, { s: top3[2], rank: 3 }]
        : top3.map((s, i) => ({ s, rank: i + 1 }));

    const maxPts = (items[0]?.project_points) || 1;
    const showPodium = period === 'all' && page === 0 && !search && !courseId && !groupId && !teacherId && top3.length >= 1;

    const pages = Math.ceil(total / LIMIT);
    const pageButtons = () => {
        if (pages <= 7) return Array.from({ length: pages }, (_, i) => i);
        const start = Math.max(0, Math.min(page - 3, pages - 7));
        return Array.from({ length: 7 }, (_, i) => start + i);
    };

    const listItems = showPodium ? rest : items;

    const subtitle = (() => {
        const periodLabel = PERIOD_OPTIONS.find(p => p.key === period)?.label || '';
        const courseLabel = courseId
            ? (courses.find(c => String(c.id) === String(courseId))?.title || '')
            : '';
        const base = total > 0 ? `${total} студентов · ${periodLabel}` : 'Рейтинг по проектам';
        return courseLabel ? `${base} · ${courseLabel}` : base;
    })();

    return (
        <div className="tsr-root">

            {/* ══ STICKY HEADER ══ */}
            <div className="tsr-header">
                <div className="tsr-header-inner">
                    <div className="tsr-title-block">
                        <span className="tsr-trophy" aria-hidden="true">🏗️</span>
                        <div>
                            <h2 className="tsr-title">Топ проектов</h2>
                            <p className="tsr-subtitle">{subtitle}</p>
                        </div>
                    </div>
                    <div className="tsr-search-wrap">
                        <span className="tsr-search-icon" aria-hidden="true">🔍</span>
                        <input
                            className="tsr-search"
                            type="text"
                            placeholder={role === 'teacher' ? 'Поиск студента…' : 'Поиск…'}
                            value={search}
                            onChange={handleSearch}
                        />
                        {search && (
                            <button
                                className="tsr-search-clear"
                                onClick={() => { setSearch(''); fetchData(0, '', period, courseId, groupId, teacherId); setPage(0); }}
                            >✕</button>
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

                    {teachers.length > 0 && (
                        <select
                            className="tsr-course-select"
                            value={teacherId}
                            onChange={handleTeacher}
                            aria-label="Учитель"
                        >
                            <option value="">Все учителя</option>
                            {teachers.map(t => (
                                <option key={t.id} value={t.id}>{t.full_name || t.username}</option>
                            ))}
                        </select>
                    )}

                    {courses.length > 0 && (
                        <select
                            className="tsr-course-select"
                            value={courseId}
                            onChange={handleCourse}
                            aria-label="Курс"
                        >
                            <option value="">Все курсы</option>
                            {courses.map(c => (
                                <option key={c.id} value={c.id}>{c.title}</option>
                            ))}
                        </select>
                    )}
                    {groups.length > 0 && (
                        <select
                            className="tsr-course-select"
                            value={groupId}
                            onChange={handleGroup}
                            aria-label="Группа"
                        >
                            <option value="">Все группы</option>
                            {groups.map(g => (
                                <option key={g.id} value={g.id}>{g.name}</option>
                            ))}
                        </select>
                    )}
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
                        <button
                            className="tsr-retry"
                            onClick={() => fetchData(page * LIMIT, search, period, courseId)}
                        >Повторить</button>
                    </div>
                )}

                {!loading && !error && items.length === 0 && (
                    <div className="tsr-state">
                        <span className="tsr-state-icon">📭</span>
                        <p>Нет данных по проектам</p>
                    </div>
                )}

                {!loading && !error && items.length > 0 && (
                    <>
                        {showPodium && (
                            <div className="tsr-podium">
                                {podiumOrder.map(({ s, rank }) => (
                                    <PodiumSlot key={s?.student_id ?? rank} s={s} rank={rank} />
                                ))}
                            </div>
                        )}

                        <div className="tsr-list">
                            {listItems.map((s, idx) => {
                                const rank = s.rank ?? (page * LIMIT + (showPodium ? idx + 4 : idx + 1));
                                const name = s.full_name || s.username || 'Студент';
                                const pts  = s.project_points ?? 0;
                                const pct  = Math.min(100, (pts / maxPts) * 100);

                                return (
                                    <div
                                        key={s.student_id ?? idx}
                                        className="tsr-item"
                                        style={{ animationDelay: `${idx * 0.025}s` }}
                                    >
                                        <span className="tsr-item-rank">{rank}</span>

                                        <Avatar url={s.avatar_url} name={name} topIdx={null} />

                                        <div className="tsr-item-info">
                                            <div className="tsr-item-row tsr-item-row--top">
                                                <span className="tsr-item-name">{name}</span>
                                                <span className="tsr-item-pts">
                                                    {pts.toLocaleString()} <em>pts</em>
                                                </span>
                                            </div>

                                            <div className="tsr-item-bar-wrap">
                                                <div className="tsr-item-bar" style={{ width: `${pct}%` }} />
                                            </div>

                                            <div className="tsr-item-row tsr-item-row--meta">
                                                {s.current_level && (
                                                    <span className="tsr-chip tsr-chip--level">
                                                        🎓 {s.current_level}
                                                    </span>
                                                )}
                                                {s.projects_count > 0 && (
                                                    <span className="tsr-chip tsr-chip--course">
                                                        📁 {s.projects_count} {s.projects_count === 1 ? 'проект' : 'проектов'}
                                                    </span>
                                                )}
                                                {s.avg_grade > 0 && (
                                                    <span
                                                        className="tsr-chip tsr-chip--course"
                                                        title="Средний балл по проектам"
                                                    >
                                                        Ср. {s.avg_grade}
                                                    </span>
                                                )}
                                                {s.best_course && (
                                                    <span className="tsr-chip tsr-chip--best" title={s.best_course}>
                                                        <Star size={12} aria-hidden="true" /> {s.best_course.length > 18 ? s.best_course.slice(0, 18) + '…' : s.best_course}
                                                        {s.best_course_points != null && (
                                                            <strong>+{s.best_course_points.toLocaleString()}</strong>
                                                        )}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>

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
