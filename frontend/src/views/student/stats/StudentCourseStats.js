import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL, headers, resolveImageUrl } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import AppHeader from '../../../components/appheader/AppHeader';
import './StudentCourseStats.css';
import {
    Flame, Trophy, Award, Code2, ChevronRight, BookMarked, Target,
} from 'lucide-react';

const LEVEL_META = {
    Beginner:     { ru: 'Начинающий',  uz: "Boshlang'ich" },
    Intermediate: { ru: 'Средний',     uz: "O'rta" },
    Advanced:     { ru: 'Продвинутый', uz: "Ilg'or" },
};

const prefersReduced = () =>
    typeof window !== 'undefined' &&
    window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ── Count-up number ───────────────────────────────────────────── */
function useCountUp(target, duration = 1200) {
    const [val, setVal] = useState(prefersReduced() ? target : 0);
    useEffect(() => {
        if (prefersReduced()) { setVal(target); return; }
        let raf;
        const t0 = performance.now();
        const loop = (now) => {
            const t = Math.min(1, (now - t0) / duration);
            const eased = 1 - Math.pow(1 - t, 3);
            setVal(Math.round(target * eased));
            if (t < 1) raf = requestAnimationFrame(loop);
        };
        raf = requestAnimationFrame(loop);
        return () => cancelAnimationFrame(raf);
    }, [target, duration]);
    return val;
}

function CountUp({ value, duration, suffix = '', group = false }) {
    const v = useCountUp(value || 0, duration);
    const text = group ? v.toLocaleString('ru-RU').replace(/,/g, ' ') : v;
    return <>{text}{suffix}</>;
}

/* ── Animated progress ring ────────────────────────────────────── */
function ProgressRing({ pct, size = 200, stroke = 14, gradId = 'stRingGrad', children, delay = 300 }) {
    const r = (size - stroke) / 2;
    const circ = 2 * Math.PI * r;
    const [offset, setOffset] = useState(circ);
    useEffect(() => {
        if (prefersReduced()) { setOffset(circ - (circ * (pct || 0)) / 100); return; }
        const id = setTimeout(() => setOffset(circ - (circ * (pct || 0)) / 100), delay);
        return () => clearTimeout(id);
    }, [pct, circ, delay]);
    return (
        <div className="st-ring" style={{ width: size, height: size }}>
            <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
                <circle cx={size / 2} cy={size / 2} r={r} fill="none"
                    stroke="rgba(255,255,255,.07)" strokeWidth={stroke} />
                <circle cx={size / 2} cy={size / 2} r={r} fill="none"
                    stroke={`url(#${gradId})`} strokeWidth={stroke} strokeLinecap="round"
                    strokeDasharray={circ} strokeDashoffset={offset}
                    transform={`rotate(-90 ${size / 2} ${size / 2})`}
                    style={{ transition: 'stroke-dashoffset 1.3s cubic-bezier(.2,.75,.25,1)', filter: 'drop-shadow(0 0 6px rgba(54,224,107,.45))' }} />
            </svg>
            <div className="st-ring-center">{children}</div>
        </div>
    );
}

/* ── Project bar chart ─────────────────────────────────────────── */
function BarChart({ bars }) {
    const [on, setOn] = useState(false);
    useEffect(() => {
        if (prefersReduced()) { setOn(true); return; }
        const id = setTimeout(() => setOn(true), 450);
        return () => clearTimeout(id);
    }, []);
    const max = Math.max(1, ...bars.map(b => b.value));
    return (
        <div className="st-bars">
            {bars.map((b, i) => (
                <div className="st-bar-col" key={i}>
                    <div className={`st-bar-val ${on ? 'on' : ''}`}>{b.value}</div>
                    <div className="st-bar-track"
                        style={{
                            height: on ? `${Math.max(4, (b.value / max) * 100)}%` : 0,
                            background: b.color,
                            transitionDelay: `${i * 110}ms`,
                        }} />
                    <div className="st-bar-name">{b.name}</div>
                </div>
            ))}
        </div>
    );
}

/* ── Contribution heatmap ──────────────────────────────────────── */
function Heatmap({ days, ru }) {
    const gridRef = useRef(null);
    useEffect(() => {
        if (!gridRef.current || prefersReduced()) return;
        const cells = gridRef.current.querySelectorAll('.st-cell');
        cells.forEach((c, i) => {
            const col = Math.floor(i / 7);
            setTimeout(() => c.classList.add('in'), 550 + col * 22 + (i % 7) * 6);
        });
    }, [days]);

    const max = Math.max(1, ...days.map(d => d.count));
    const level = (c) => {
        if (c <= 0) return 0;
        const q = c / max;
        if (q > 0.66) return 4;
        if (q > 0.33) return 3;
        if (q > 0.12) return 2;
        return 1;
    };

    const monthNames = ru
        ? ['Янв','Фев','Мар','Апр','Май','Июн','Июл','Авг','Сен','Окт','Ноя','Дек']
        : ['Yan','Fev','Mar','Apr','May','Iyn','Iyl','Avg','Sen','Okt','Noy','Dek'];
    const weeks = Math.ceil(days.length / 7);
    const monthCols = [];
    let lastMonth = -1;
    for (let w = 0; w < weeks; w++) {
        const d = days[w * 7];
        if (!d) continue;
        const m = new Date(d.date).getMonth();
        if (m !== lastMonth) { monthCols.push({ w, label: monthNames[m] }); lastMonth = m; }
    }

    return (
        <div className="st-heat">
            <div className="st-heat-grid" ref={gridRef}>
                {days.map((d, i) => (
                    <div key={i}
                        className={`st-cell st-cell-l${level(d.count)}`}
                        style={{ transitionDelay: `${(i % 7) * 10}ms` }}
                        title={`${d.date} · ${d.count} ${ru ? 'действий' : 'ta faollik'}`} />
                ))}
            </div>
            <div className="st-heat-months"
                 style={{ gridTemplateColumns: `repeat(${weeks}, 1fr)` }}>
                {monthCols.map((m, i) => (
                    <span key={i} style={{ gridColumn: m.w + 1 }}>{m.label}</span>
                ))}
            </div>
        </div>
    );
}

/* ── Shared SVG gradient defs ──────────────────────────────────── */
function SvgDefs() {
    return (
        <svg width="0" height="0" style={{ position: 'absolute' }} aria-hidden="true">
            <defs>
                <linearGradient id="stRingGrad" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0" stopColor="#7ef0a3" /><stop offset="1" stopColor="#2bc45a" />
                </linearGradient>
                <linearGradient id="stAccPurple" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0" stopColor="#b7adfb" /><stop offset="1" stopColor="#7b6bf0" />
                </linearGradient>
            </defs>
        </svg>
    );
}

/* ── Animated horizontal bar ───────────────────────────────────── */
function Bar({ pct, delay = 300, color = 'linear-gradient(90deg,#2bc45a,#7ef0a3)' }) {
    const [w, setW] = useState(0);
    useEffect(() => {
        if (prefersReduced()) { setW(pct); return; }
        const id = setTimeout(() => setW(pct), delay);
        return () => clearTimeout(id);
    }, [pct, delay]);
    return (
        <div className="st-bar2-track">
            <div className="st-bar2-fill" style={{ width: `${Math.max(0, Math.min(100, w))}%`, background: color }} />
        </div>
    );
}

/* ── Per-course exercise-mastery card (top strip) ──────────────── */
function CourseExCard({ course, index, ru }) {
    const navigate = useNavigate();
    const pct = course.exercises_pct || 0;
    const col = course.color_accent || '#36e06b';
    const img = resolveImageUrl(course.image_url);
    return (
        <button className="st-card st-exc st-rise" style={{ animationDelay: `${0.12 + index * 0.05}s` }}
            onClick={() => navigate(`/student/courses/${course.id}`)}>
            <div className="st-exc-head">
                {img
                    ? <img className="st-exc-ico" src={img} alt="" onError={e => { e.target.style.display = 'none'; }} />
                    : <span className="st-exc-ico st-exc-ico--ph" style={{ background: `${col}22`, color: col }}><Code2 size={18} /></span>}
                <span className="st-exc-title">{course.title}</span>
            </div>
            <div className="st-exc-pctrow">
                <span className="st-exc-pct"><CountUp value={pct} suffix="%" /></span>
                <span className="st-exc-frac">{course.exercises_correct || 0}/{course.exercises_total || 0}</span>
            </div>
            <Bar pct={pct} delay={400 + index * 120}
                color={pct >= 80 ? 'linear-gradient(90deg,#2bc45a,#7ef0a3)'
                    : pct >= 40 ? 'linear-gradient(90deg,#7b6bf0,#b7adfb)'
                    : 'linear-gradient(90deg,#c0392b,#f0556b)'} />
        </button>
    );
}

/* ── Per-course project card (right column) ────────────────────── */
function MiniProjectCard({ course, index, ru }) {
    const navigate = useNavigate();
    const exPct = course.exercises_pct || 0;
    const total = course.submissions_total || 0;
    const approved = course.submissions_approved || 0;
    const col = course.color_accent || '#36e06b';
    const img = resolveImageUrl(course.image_url);
    return (
        <button className="st-card st-mini st-rise" style={{ animationDelay: `${0.4 + index * 0.06}s` }}
            onClick={() => navigate(`/student/courses/${course.id}`)}>
            <div className="st-mini-head">
                {img
                    ? <img className="st-mini-ico" src={img} alt="" onError={e => { e.target.style.display = 'none'; }} />
                    : <span className="st-mini-ico st-mini-ico--ph" style={{ background: `${col}22`, color: col }}><Code2 size={16} /></span>}
                <span className="st-mini-title">{course.title}</span>
                <ChevronRight size={15} className="st-mini-arrow" />
            </div>
            <div className="st-mini-barrow">
                <Bar pct={exPct} delay={500 + index * 120} />
                <span className="st-mini-barpct">{exPct}%</span>
            </div>
            <div className="st-mini-foot">
                <div className="st-mini-stat">
                    <span className="st-mini-num" style={{ color: 'var(--st-green-soft)' }}>{approved}/{total}</span>
                    <span className="st-mini-lbl">{ru ? 'проектов' : 'loyiha'}</span>
                </div>
                <div className="st-mini-stat st-mini-stat--r">
                    <span className="st-mini-num" style={{ color: 'var(--st-amber)' }}>+{(course.points_from_submissions || 0).toLocaleString('ru-RU').replace(/,/g, ' ')}</span>
                    <span className="st-mini-lbl">{ru ? 'баллов' : 'ball'}</span>
                </div>
            </div>
        </button>
    );
}

export default function StudentCourseStats() {
    const navigate = useNavigate();
    const { lang } = useTranslation();
    const ru = lang === 'ru';

    const [me, setMe] = useState(null);
    const [data, setData] = useState(null);
    const [dictWords, setDictWords] = useState([]);
    const [activity, setActivity] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        Promise.all([
            fetch(`${API_URL}v1/student/me`, { headers: headers() }).then(r => r.ok ? r.json() : null).catch(() => null),
            fetch(`${API_URL}v1/student/me/course-stats`, { headers: headers() }).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
            fetch(`${API_URL}v1/dictionary/?lang=${localStorage.getItem('lang') || 'uz'}`, { headers: headers() }).then(r => r.ok ? r.json() : []).catch(() => []),
            fetch(`${API_URL}v1/student/me/activity`, { headers: headers() }).then(r => r.ok ? r.json() : null).catch(() => null),
        ]).then(([meData, statsData, dictData, activityData]) => {
            setMe(meData);
            setData(statsData);
            setDictWords(Array.isArray(dictData) ? dictData : []);
            setActivity(activityData);
        }).catch(() => setError(ru ? 'Не удалось загрузить статистику' : "Statistikani yuklab bo'lmadi"))
          .finally(() => setLoading(false));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    if (loading) return <div className="st-page"><div className="st-state">⏳ {ru ? 'Загрузка статистики...' : 'Statistika yuklanmoqda...'}</div></div>;
    if (error || !data) return <div className="st-page"><div className="st-state st-error">⚠️ {error || (ru ? 'Нет данных' : "Ma'lumot yo'q")}</div></div>;

    const profile = data.profile || {};
    const overall = data.overall || {};
    const courses = data.courses || [];
    const lvl = LEVEL_META[profile.level] || LEVEL_META.Beginner;
    const displayName = me?.full_name || me?.username || (ru ? 'Студент' : 'Talaba');

    // Dictionary metrics
    const totalWords = dictWords.length;
    const totalCorrect = dictWords.reduce((s, w) => s + (w.correct_count || 0), 0);
    const totalAttempts = dictWords.reduce((s, w) => s + (w.correct_count || 0) + (w.incorrect_count || 0), 0);
    const accuracyPct = totalAttempts > 0 ? Math.round((totalCorrect / totalAttempts) * 100) : 0;
    const practicedWords = dictWords.filter(w => (w.correct_count || 0) + (w.incorrect_count || 0) > 0).length;

    // Project bars
    const bars = [
        { name: ru ? 'Всего' : 'Jami',      value: overall.projects_total || 0,     color: 'linear-gradient(180deg,#b7adfb,#8b7bf2)' },
        { name: ru ? 'Одобр.' : 'Tasdiq',   value: overall.projects_approved || 0,  color: 'linear-gradient(180deg,#7ef0a3,#2bc45a)' },
        { name: ru ? 'Провер.' : 'Tekshir', value: overall.projects_submitted || 0, color: 'linear-gradient(180deg,#fcd34d,#f59e0b)' },
        { name: ru ? 'Откл.' : 'Rad',       value: overall.projects_rejected || 0,  color: 'linear-gradient(180deg,#f0556b,#c0392b)' },
    ];

    // Top courses by exercise activity for the top strip (de-duped by title)
    const seen = new Set();
    const topCourses = courses
        .filter(c => (c.exercises_total || 0) > 0)
        .filter(c => { const k = (c.title || '').trim(); if (seen.has(k)) return false; seen.add(k); return true; })
        .slice(0, 2);

    // Courses with any project work for the mini-project column
    const projCourses = courses.filter(c => (c.submissions_total || 0) > 0).slice(0, 4);
    const miniCourses = projCourses.length ? projCourses : courses.slice(0, 3);

    return (
        <div className="st-page">
            <SvgDefs />
            <AppHeader me={me} />

            <div className="st-shell">
                <div className="st-head st-rise">
                    <div>
                        <h1>{ru ? 'Статистика' : 'Statistika'}</h1>
                        <p>{ru ? 'Полный обзор вашего прогресса на платформе' : "Platformadagi barcha yutuqlaringizning to'liq ko'rinishi"}</p>
                    </div>
                </div>

                <div className="st-bento">

                    {/* ── Profile summary ── */}
                    <div className="st-card st-profile st-rise" style={{ animationDelay: '.06s' }}>
                        <span className="st-profile-glow" aria-hidden="true" />
                        <button className="st-profile-head" onClick={() => navigate('/student/profile')}>
                            <span className="st-profile-av">
                                {resolveImageUrl(me?.avatar_url)
                                    ? <img src={resolveImageUrl(me.avatar_url)} alt="" onError={e => { e.target.style.display = 'none'; }} />
                                    : (displayName[0] || 'U').toUpperCase()}
                            </span>
                            <span className="st-profile-id">
                                <span className="st-profile-name">{displayName}</span>
                                <span className="st-profile-lvl">{ru ? lvl.ru : lvl.uz}</span>
                            </span>
                            <ChevronRight size={20} className="st-profile-arrow" />
                        </button>
                        <div className="st-profile-stats">
                            <div className="st-ps">
                                <span className="st-ps-ico"><Trophy size={17} /></span>
                                <span className="st-ps-lbl">{ru ? 'Рейтинг' : 'Reyting'}</span>
                                <span className="st-ps-val">#{profile.global_rank || '—'}</span>
                            </div>
                            <div className="st-ps">
                                <span className="st-ps-ico st-ps-ico--amber"><Flame size={17} /></span>
                                <span className="st-ps-lbl">{ru ? 'Серия' : 'Joriy seriya'}</span>
                                <span className="st-ps-val st-ps-val--amber"><CountUp value={profile.current_streak || 0} /> {ru ? 'дн.' : 'kun'}</span>
                            </div>
                            <div className="st-ps">
                                <span className="st-ps-ico st-ps-ico--amber"><Award size={17} /></span>
                                <span className="st-ps-lbl">{ru ? 'Лучшая' : 'Eng yaxshi'}</span>
                                <span className="st-ps-val st-ps-val--amber"><CountUp value={profile.longest_streak || 0} /> {ru ? 'дн.' : 'kun'}</span>
                            </div>
                        </div>
                    </div>

                    {/* ── top exercise cards ── */}
                    <div className="st-strip">
                        {topCourses.length > 0
                            ? topCourses.map((c, i) => <CourseExCard key={c.id ?? i} course={c} index={i} ru={ru} />)
                            : <div className="st-card st-empty-strip st-rise">{ru ? 'Пока нет упражнений' : "Hozircha mashqlar yo'q"}</div>}
                    </div>

                    {/* ── Umumiy progress ── */}
                    <div className="st-card st-prog st-rise" style={{ animationDelay: '.24s' }}>
                        <div className="st-panel-head">
                            <div className="st-panel-title">{ru ? 'Общий прогресс' : 'Umumiy progress'}</div>
                            <div className="st-chip">{ru ? 'Упражнения' : 'Mashqlar'}</div>
                        </div>
                        <div className="st-prog-body">
                            <ProgressRing pct={overall.exercises_pct || 0}>
                                <div className="st-ring-pct"><CountUp value={overall.exercises_pct || 0} duration={1300} suffix="%" /></div>
                                <div className="st-ring-lbl">{ru ? 'Упражнения' : 'Mashqlar'}</div>
                                <div className="st-ring-sub">{overall.exercises_correct || 0}/{overall.exercises_total || 0} {ru ? 'верно' : "to'g'ri"}</div>
                            </ProgressRing>
                            <BarChart bars={bars} />
                        </div>
                        <div className="st-metrics">
                            <div className="st-metric"><div className="st-m-val" style={{ color: 'var(--st-violet-soft)' }}><CountUp value={overall.projects_total || 0} /></div><div className="st-m-lbl">{ru ? 'Проектов всего' : 'Loyihalar jami'}</div></div>
                            <div className="st-metric"><div className="st-m-val" style={{ color: 'var(--st-green-soft)' }}><CountUp value={overall.projects_approved || 0} /></div><div className="st-m-lbl">{ru ? 'Одобрено' : 'Tasdiqlangan'}</div></div>
                            <div className="st-metric"><div className="st-m-val" style={{ color: 'var(--st-amber)' }}><CountUp value={overall.projects_submitted || 0} /></div><div className="st-m-lbl">{ru ? 'На проверке' : 'Tekshirilmoqda'}</div></div>
                            <div className="st-metric"><div className="st-m-val" style={{ color: 'var(--st-green)' }}><CountUp value={overall.total_points_from_projects || 0} group /></div><div className="st-m-lbl">{ru ? 'Очков за проекты' : 'Loyihadan ball'}</div></div>
                        </div>
                    </div>

                    {/* ── Contribution matrix ── */}
                    <div className="st-card st-matrix st-rise" style={{ animationDelay: '.3s' }}>
                        <div className="st-panel-head">
                            <div className="st-panel-title">{ru ? 'Карта активности' : 'Faollik xaritasi'}</div>
                            <div className="st-chip">{ru ? '6 мес.' : "6 oy"}</div>
                        </div>
                        {activity && activity.days?.length ? (
                            <>
                                <Heatmap days={activity.days} ru={ru} />
                                <div className="st-heat-foot">
                                    <span><b>{activity.active_days}</b> {ru ? 'актив. дней' : 'faol kun'} · {ru ? 'серия' : 'seriya'} <b>{activity.longest_streak}</b></span>
                                    <span className="st-heat-legend">
                                        {ru ? 'Меньше' : 'Kam'}
                                        <i className="st-cell st-cell-l0 in" />
                                        <i className="st-cell st-cell-l1 in" />
                                        <i className="st-cell st-cell-l2 in" />
                                        <i className="st-cell st-cell-l3 in" />
                                        <i className="st-cell st-cell-l4 in" />
                                        {ru ? 'Больше' : "Ko'p"}
                                    </span>
                                </div>
                            </>
                        ) : (
                            <div className="st-heat-empty">{ru ? 'Данные появятся по мере занятий' : "Faollik ma'lumotlari to'planib boradi"}</div>
                        )}
                    </div>

                    {/* ── Mini-project column ── */}
                    <div className="st-mini-col">
                        <div className="st-mini-coltitle"><Code2 size={16} /> {ru ? 'Проекты по курсам' : 'Kurs loyihalari'}</div>
                        {miniCourses.length > 0
                            ? miniCourses.map((c, i) => <MiniProjectCard key={c.id ?? i} course={c} index={i} ru={ru} />)
                            : <div className="st-card st-empty-strip">{ru ? 'Пока нет проектов' : "Hozircha loyihalar yo'q"}</div>}
                    </div>

                    {/* ── Dictionary & practice ── */}
                    <div className="st-card st-dict st-rise" style={{ animationDelay: '.44s' }}>
                        <div className="st-panel-head">
                            <div className="st-panel-title"><BookMarked size={16} style={{ verticalAlign: '-3px', marginRight: 7 }} />{ru ? 'Словарь и практика' : "Lug'at va mashq"}</div>
                            <button className="st-chip" onClick={() => navigate('/student/dictionary')}>{ru ? 'Открыть' : 'Ochish'}</button>
                        </div>
                        <div className="st-dict-body">
                            <div className="st-dict-nums">
                                <div className="st-dict-stat"><div className="st-d-big"><CountUp value={totalWords} /></div><div className="st-d-lbl">{ru ? 'слов в словаре' : "so'z lug'atda"}</div></div>
                                <div className="st-dict-stat"><div className="st-d-big"><CountUp value={practicedWords} /></div><div className="st-d-lbl">{ru ? 'отработано' : 'mashq qilingan'}</div></div>
                            </div>
                            <div className="st-dict-acc">
                                <ProgressRing pct={accuracyPct} size={118} stroke={9} delay={500}>
                                    <div className="st-acc-pct"><CountUp value={accuracyPct} duration={1100} suffix="%" /></div>
                                    <div className="st-acc-sub">{totalCorrect}/{totalAttempts}</div>
                                </ProgressRing>
                                <div className="st-acc-lbl"><Target size={13} style={{ verticalAlign: '-2px', marginRight: 4 }} />{ru ? 'Точность' : 'Aniqlik'}</div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
}
