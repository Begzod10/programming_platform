import { useState, useEffect, useRef } from 'react';
import './ProjectRating.css';
import { API_URL, useHttp, headers, resolveImageUrl } from '../../../api/search/base';
import { useAuth } from '../../../context/AuthContext';
import { useTranslation } from '../../../i18n/useTranslation';
import AppHeader from '../../../components/appheader/AppHeader';
import {
    Trophy, Crown, Medal, Search, X, Star, FolderGit2, GraduationCap, Target,
    ChevronLeft, ChevronRight,
} from 'lucide-react';

const LIMIT = 50;
const PODIUM_RANKS = [2, 1, 3];
const AVATAR_PALETTE = ['#8b7bf2', '#36e06b', '#e17055', '#22d3ee', '#e84393', '#fbbf24'];

const prefersReduced = () =>
    typeof window !== 'undefined' && window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const PERIODS = (ru) => [
    { key: 'all',   label: ru ? 'Всё время'      : 'Barcha vaqt' },
    { key: 'month', label: ru ? 'В этом месяце'  : 'Shu oy' },
    { key: 'week',  label: ru ? 'На неделе'      : 'Shu hafta' },
    { key: 'day',   label: ru ? 'Сегодня'        : 'Bugun' },
];

function fmt(v) {
    if (typeof v !== 'number' || Number.isNaN(v)) return '0';
    return v.toLocaleString('ru-RU').replace(/,/g, ' ');
}
function initialsOf(name) {
    if (!name) return '?';
    return name.split(' ').filter(Boolean).map(w => w[0]).join('').slice(0, 2).toUpperCase();
}

function Avatar({ url, name, size, ring }) {
    const color = AVATAR_PALETTE[(name?.charCodeAt(0) ?? 0) % AVATAR_PALETTE.length];
    const src = resolveImageUrl(url);
    return (
        <div className={`tpr-avatar ${ring ? `tpr-avatar--${ring}` : ''}`} style={{ width: size, height: size }}>
            {src
                ? <img src={src} alt={name} onError={e => { e.target.style.display = 'none'; }} />
                : <span style={{ background: color }}>{initialsOf(name)}</span>}
        </div>
    );
}

function Chip({ icon: Icon, children, title, kind }) {
    return (
        <span className={`tpr-chip ${kind ? `tpr-chip--${kind}` : ''}`} title={title}>
            {Icon && <Icon size={12} aria-hidden="true" />} {children}
        </span>
    );
}

function PodiumColumn({ s, rank, ru, t }) {
    const empty = !s;
    const name = s ? (s.full_name || s.username || '—') : '—';
    const pts = s ? (s.project_points ?? 0) : 0;
    return (
        <div className={`tpr-pcol tpr-pcol--${rank} ${empty ? 'tpr-pcol--empty' : ''}`}>
            {!empty && (
                <div className="tpr-pcol-top">
                    <span className={`tpr-crown tpr-crown--${rank}`} aria-hidden="true"><Crown size={rank === 1 ? 26 : 20} /></span>
                    <Avatar url={s.avatar_url} name={name} size={rank === 1 ? 92 : 76}
                        ring={rank === 1 ? 'gold' : rank === 2 ? 'silver' : 'bronze'} />
                    <p className="tpr-pcol-name">{name.split(' ')[0]}</p>
                    <p className="tpr-pcol-pts">{fmt(pts)} <span>{t('rating.pts')}</span></p>
                    <div className="tpr-pcol-chips">
                        {s.projects_count > 0 && <Chip icon={FolderGit2}>{s.projects_count}</Chip>}
                        {s.avg_grade > 0 && <Chip icon={Target} title={ru ? 'Средний балл' : "O'rtacha baho"}>{s.avg_grade}</Chip>}
                    </div>
                </div>
            )}
            <div className={`tpr-block tpr-block--${rank}`}>
                <span className="tpr-block-glow" aria-hidden="true" />
                {rank === 1
                    ? <Crown size={26} className="tpr-block-ico" aria-hidden="true" />
                    : <Medal size={22} className="tpr-block-ico" aria-hidden="true" />}
                <span className="tpr-block-num">{rank}</span>
            </div>
        </div>
    );
}

export default function ProjectRating() {
    const { request } = useHttp();
    const { user } = useAuth();
    const { t, lang } = useTranslation();
    const ru = lang === 'ru';

    const [items, setItems] = useState([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(0);
    const [period, setPeriod] = useState('all');
    const [courseId, setCourseId] = useState('');
    const [courses, setCourses] = useState([]);
    const searchTimer = useRef(null);

    const fetchData = (skip, searchVal, periodVal, courseIdVal) => {
        setLoading(true);
        setError('');
        const q = searchVal ? `&search=${encodeURIComponent(searchVal)}` : '';
        const p = `&period=${encodeURIComponent(periodVal || 'all')}`;
        const c = courseIdVal ? `&course_id=${encodeURIComponent(courseIdVal)}` : '';
        request(`${API_URL}v1/rankings/project-leaderboard?skip=${skip}&limit=${LIMIT}${q}${p}${c}`, 'GET', null, headers())
            .then(res => { setItems(res?.items || []); setTotal(res?.total || 0); })
            .catch(() => { setItems([]); setTotal(0); setError(ru ? 'Не удалось загрузить рейтинг' : "Reytingni yuklab bo'lmadi"); })
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        request(`${API_URL}v1/rankings/project-leaderboard/courses`, 'GET', null, headers())
            .then(res => setCourses(Array.isArray(res) ? res : []))
            .catch(() => setCourses([]));
        fetchData(0, '', 'all', '');
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleSearch = (e) => {
        const val = e.target.value;
        setSearch(val); setPage(0);
        clearTimeout(searchTimer.current);
        searchTimer.current = setTimeout(() => fetchData(0, val, period, courseId), 420);
    };
    const handlePeriod = (next) => { if (next === period) return; setPeriod(next); setPage(0); fetchData(0, search, next, courseId); };
    const handleCourse = (e) => { const next = e.target.value; setCourseId(next); setPage(0); fetchData(0, search, period, next); };
    const handlePage = (p) => { setPage(p); fetchData(p * LIMIT, search, period, courseId); };

    const isMe = (s) => {
        if (!s || !user) return false;
        if (s.student_id != null && user.id != null && Number(s.student_id) === Number(user.id)) return true;
        return s.username && user.username ? s.username === user.username : false;
    };

    const top3 = items.slice(0, 3);
    const maxPts = (items[0]?.project_points) || 1;
    const showPodium = period === 'all' && page === 0 && !search && !courseId && top3.length >= 1;
    const listItems = showPodium ? items.slice(3) : items;
    const pages = Math.ceil(total / LIMIT);
    const pageButtons = () => {
        if (pages <= 7) return Array.from({ length: pages }, (_, i) => i);
        const start = Math.max(0, Math.min(page - 3, pages - 7));
        return Array.from({ length: 7 }, (_, i) => start + i);
    };

    const periodLabel = PERIODS(ru).find(p => p.key === period)?.label || '';
    const subtitle = total > 0
        ? `${total} ${ru ? 'студентов' : 'talaba'} · ${periodLabel}`
        : (ru ? 'Рейтинг по проектам' : 'Loyihalar bo\'yicha reyting');

    return (
        <div className="tpr-page">
            <AppHeader />

            <div className="tpr-shell">
                {/* ── header ── */}
                <div className="tpr-head">
                    <div className="tpr-title-block">
                        <span className="tpr-title-ico" aria-hidden="true"><Trophy size={20} /></span>
                        <div>
                            <h1>{ru ? 'Топ проектов' : 'Top loyihalar'}</h1>
                            <p>{subtitle}</p>
                        </div>
                    </div>
                    <div className="tpr-search">
                        <Search size={16} className="tpr-search-ico" aria-hidden="true" />
                        <input type="text" value={search} onChange={handleSearch}
                            placeholder={ru ? 'Поиск…' : 'Qidirish…'} />
                        {search && (
                            <button className="tpr-search-x" onClick={() => { setSearch(''); setPage(0); fetchData(0, '', period, courseId); }}
                                aria-label="clear"><X size={14} /></button>
                        )}
                    </div>
                </div>

                {/* ── controls ── */}
                <div className="tpr-controls">
                    <div className="tpr-tabs">
                        {PERIODS(ru).map(opt => (
                            <button key={opt.key} type="button"
                                className={`tpr-tab ${period === opt.key ? 'tpr-tab--active' : ''}`}
                                aria-pressed={period === opt.key} onClick={() => handlePeriod(opt.key)}>
                                {opt.label}
                            </button>
                        ))}
                    </div>
                    {courses.length > 0 && (
                        <select className="tpr-course-select" value={courseId} onChange={handleCourse}
                            aria-label={ru ? 'Курс' : 'Kurs'}>
                            <option value="">{ru ? 'Все курсы' : 'Barcha kurslar'}</option>
                            {courses.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}
                        </select>
                    )}
                </div>

                {loading ? (
                    <div className="tpr-state"><div className="tpr-spinner" /><p>{ru ? 'Загрузка…' : 'Yuklanmoqda…'}</p></div>
                ) : error ? (
                    <div className="tpr-state tpr-state--error">
                        <span className="tpr-state-ico">⚠</span><p>{error}</p>
                        <button className="tpr-retry" onClick={() => fetchData(page * LIMIT, search, period, courseId)}>
                            {ru ? 'Повторить' : 'Qayta urinish'}
                        </button>
                    </div>
                ) : items.length === 0 ? (
                    <div className="tpr-state">
                        <Trophy size={40} className="tpr-state-trophy" aria-hidden="true" />
                        <p className="tpr-state-title">{ru ? 'Нет данных по проектам' : "Loyihalar bo'yicha ma'lumot yo'q"}</p>
                    </div>
                ) : (
                    <>
                        {showPodium && top3.length > 0 && (
                            <div className="tpr-podium">
                                <span className="tpr-trophy tpr-trophy--l" aria-hidden="true"><Trophy size={60} /></span>
                                {PODIUM_RANKS.map(rank => (
                                    <PodiumColumn key={rank} rank={rank} s={top3[rank - 1]} ru={ru} t={t} />
                                ))}
                                <span className="tpr-trophy tpr-trophy--r" aria-hidden="true"><Trophy size={60} /></span>
                            </div>
                        )}

                        <ol className="tpr-list">
                            {listItems.map((s, idx) => {
                                const rank = s.rank ?? (page * LIMIT + (showPodium ? idx + 4 : idx + 1));
                                const name = s.full_name || s.username || (ru ? 'Студент' : 'Talaba');
                                const pts = s.project_points ?? 0;
                                const pct = maxPts > 0 ? Math.max(3, Math.round((pts / maxPts) * 100)) : 0;
                                const mine = isMe(s);
                                return (
                                    <li key={s.student_id ?? idx} className={`tpr-row ${mine ? 'tpr-row--me' : ''}`}
                                        style={prefersReduced() ? undefined : { animationDelay: `${Math.min(idx, 12) * 0.04}s` }}>
                                        <span className="tpr-row-rank">{rank}</span>
                                        <Avatar url={s.avatar_url} name={name} size={46} />
                                        <div className="tpr-row-info">
                                            <div className="tpr-row-line">
                                                <span className="tpr-row-name">
                                                    {name}
                                                    {mine && <span className="tpr-chip-you">{t('rating.you')}</span>}
                                                </span>
                                                <span className="tpr-row-pts">{fmt(pts)} <em>{t('rating.pts')}</em></span>
                                            </div>
                                            <div className="tpr-row-bar-wrap">
                                                <div className="tpr-row-bar" style={{ width: `${pct}%` }} />
                                            </div>
                                            <div className="tpr-row-meta">
                                                {s.current_level && <Chip icon={GraduationCap} kind="level">{s.current_level}</Chip>}
                                                {s.projects_count > 0 && <Chip icon={FolderGit2}>{s.projects_count} {ru ? 'проектов' : 'loyiha'}</Chip>}
                                                {s.avg_grade > 0 && <Chip icon={Target} title={ru ? 'Средний балл' : "O'rtacha baho"}>{ru ? 'Ср.' : "O'rt."} {s.avg_grade}</Chip>}
                                                {s.best_course && (
                                                    <Chip icon={Star} kind="best" title={s.best_course}>
                                                        {s.best_course.length > 18 ? s.best_course.slice(0, 18) + '…' : s.best_course}
                                                        {s.best_course_points != null && <strong>+{fmt(s.best_course_points)}</strong>}
                                                    </Chip>
                                                )}
                                            </div>
                                        </div>
                                    </li>
                                );
                            })}
                        </ol>

                        {pages > 1 && (
                            <div className="tpr-pagination">
                                <button className="tpr-page-btn" onClick={() => handlePage(page - 1)} disabled={page === 0}><ChevronLeft size={16} /></button>
                                {pageButtons().map(p => (
                                    <button key={p} className={`tpr-page-btn ${p === page ? 'active' : ''}`} onClick={() => handlePage(p)}>{p + 1}</button>
                                ))}
                                <button className="tpr-page-btn" onClick={() => handlePage(page + 1)} disabled={page >= pages - 1}><ChevronRight size={16} /></button>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
