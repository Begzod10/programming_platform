import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL, headers } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import AppHeader from '../../../components/appheader/AppHeader';
import './StudentDashboard.css';
import { BookOpen, Trophy, Award, Medal, Flame, ArrowRight } from 'lucide-react';

const LEVEL_META = {
    Beginner:     { ru: 'Начинающий', uz: "Boshlang'ich" },
    Intermediate: { ru: 'Средний',    uz: "O'rta" },
    Advanced:     { ru: 'Продвинутый', uz: "Ilg'or" },
};

const QUIZ_DAILY_LIMIT = 2;

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
function ProgressRing({ pct, size = 200, stroke = 14, gradId = 'dbRingGrad', children, delay = 300 }) {
    const r = (size - stroke) / 2;
    const circ = 2 * Math.PI * r;
    const [offset, setOffset] = useState(circ);
    useEffect(() => {
        if (prefersReduced()) { setOffset(circ - (circ * (pct || 0)) / 100); return; }
        const id = setTimeout(() => setOffset(circ - (circ * (pct || 0)) / 100), delay);
        return () => clearTimeout(id);
    }, [pct, circ, delay]);
    return (
        <div className="db-ring" style={{ width: size, height: size }}>
            <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
                <circle cx={size / 2} cy={size / 2} r={r} fill="none"
                    stroke="rgba(255,255,255,.07)" strokeWidth={stroke} />
                <circle cx={size / 2} cy={size / 2} r={r} fill="none"
                    stroke={`url(#${gradId})`} strokeWidth={stroke} strokeLinecap="round"
                    strokeDasharray={circ} strokeDashoffset={offset}
                    transform={`rotate(-90 ${size / 2} ${size / 2})`}
                    style={{ transition: 'stroke-dashoffset 1.3s cubic-bezier(.2,.75,.25,1)', filter: 'drop-shadow(0 0 6px rgba(54,224,107,.45))' }} />
            </svg>
            <div className="db-ring-center">{children}</div>
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
        <div className="db-bars">
            {bars.map((b, i) => (
                <div className="db-bar-col" key={i}>
                    <div className={`db-bar-val ${on ? 'on' : ''}`}>{b.value}</div>
                    <div className="db-bar-track"
                        style={{
                            height: on ? `${Math.max(4, (b.value / max) * 100)}%` : 0,
                            background: b.color,
                            transitionDelay: `${i * 110}ms`,
                        }} />
                    <div className="db-bar-name">{b.name}</div>
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
        const cells = gridRef.current.querySelectorAll('.db-cell');
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
        <div className="db-heat">
            <div className="db-heat-grid" ref={gridRef}>
                {days.map((d, i) => (
                    <div key={i}
                        className={`db-cell db-cell-l${level(d.count)}`}
                        style={{ transitionDelay: `${(i % 7) * 10}ms` }}
                        title={`${d.date} · ${d.count} ${ru ? 'действий' : 'ta faollik'}`} />
                ))}
            </div>
            <div className="db-heat-months"
                 style={{ gridTemplateColumns: `repeat(${weeks}, 1fr)` }}>
                {monthCols.map((m, i) => (
                    <span key={i} style={{ gridColumn: m.w + 1 }}>{m.label}</span>
                ))}
            </div>
        </div>
    );
}

/* ── Skill radar ───────────────────────────────────────────────── */
function shortSkill(title) {
    const t = (title || '').trim();
    if (t.length <= 12) return t;
    const words = t.split(/[\s/]+/).filter(Boolean);
    if (words[0].length <= 12) return words[0];
    return words[0].slice(0, 11) + '…';
}

function SkillRadar({ skills }) {
    const [on, setOn] = useState(false);
    useEffect(() => {
        if (prefersReduced()) { setOn(true); return; }
        const id = setTimeout(() => setOn(true), 600);
        return () => clearTimeout(id);
    }, []);
    const W = 320, H = 280, cx = W / 2, cy = 128, R = 78, n = skills.length;
    const pt = (i, rr) => {
        const a = (Math.PI * 2 * i) / n - Math.PI / 2;
        return [cx + Math.cos(a) * rr, cy + Math.sin(a) * rr];
    };
    const collapsed = skills.map(() => `${cx},${cy}`).join(' ');
    const full = skills.map((s, i) => pt(i, (R * Math.max(4, s.pct)) / 100).join(',')).join(' ');
    return (
        <svg className="db-radar" viewBox={`0 0 ${W} ${H}`} width="100%" preserveAspectRatio="xMidYMid meet">
            {[0.25, 0.5, 0.75, 1].map((f, i) => (
                <polygon key={i} fill="none" stroke="rgba(255,255,255,.08)" strokeWidth="1"
                    points={skills.map((_, j) => pt(j, R * f).join(',')).join(' ')} />
            ))}
            {skills.map((_, i) => {
                const [x, y] = pt(i, R);
                return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="rgba(255,255,255,.08)" />;
            })}
            <polygon points={on ? full : collapsed}
                fill="url(#dbRadarFill)" stroke="#36e06b" strokeWidth="2"
                style={{ transition: 'all 1.1s cubic-bezier(.2,.75,.25,1)', filter: 'drop-shadow(0 0 8px rgba(54,224,107,.4))' }} />
            {skills.map((s, i) => {
                const [vx, vy] = pt(i, (R * Math.max(4, s.pct)) / 100);
                const [lx, ly] = pt(i, R + 16);
                const anchor = Math.abs(lx - cx) < 8 ? 'middle' : (lx > cx ? 'start' : 'end');
                return (
                    <g key={i}>
                        <circle cx={on ? vx : cx} cy={on ? vy : cy} r="3" fill="#7ef0a3"
                            style={{ transition: 'all 1.1s cubic-bezier(.2,.75,.25,1)' }} />
                        <text x={lx} y={ly} fill="#9aa3c7" fontSize="10.5" fontWeight="600"
                            textAnchor={anchor} dominantBaseline="middle">
                            {shortSkill(s.name)}
                        </text>
                    </g>
                );
            })}
        </svg>
    );
}

/* ── Shared SVG gradient defs ──────────────────────────────────── */
function SvgDefs() {
    return (
        <svg width="0" height="0" style={{ position: 'absolute' }} aria-hidden="true">
            <defs>
                <linearGradient id="dbRingGrad" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0" stopColor="#7ef0a3" /><stop offset="1" stopColor="#2bc45a" />
                </linearGradient>
                <radialGradient id="dbRadarFill">
                    <stop offset="0" stopColor="#7ef0a3" stopOpacity=".5" />
                    <stop offset="1" stopColor="#36e06b" stopOpacity=".16" />
                </radialGradient>
            </defs>
        </svg>
    );
}

export default function StudentDashboard() {
    const navigate = useNavigate();
    const { lang } = useTranslation();
    const [me, setMe] = useState(null);
    const [stats, setStats] = useState(null);
    const [dictStatus, setDictStatus] = useState(null);
    const [dictWords, setDictWords] = useState([]);
    const [activity, setActivity] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const ru = lang === 'ru';

    useEffect(() => {
        Promise.all([
            fetch(`${API_URL}v1/student/me`, { headers: headers() }).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
            fetch(`${API_URL}v1/student/me/course-stats`, { headers: headers() }).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
            fetch(`${API_URL}v1/dictionary/quiz/status`, { headers: headers() }).then(r => r.ok ? r.json() : null).catch(() => null),
            fetch(`${API_URL}v1/dictionary/?lang=${localStorage.getItem('lang') || 'uz'}`, { headers: headers() }).then(r => r.ok ? r.json() : []).catch(() => []),
            fetch(`${API_URL}v1/student/me/activity`, { headers: headers() }).then(r => r.ok ? r.json() : null).catch(() => null),
        ]).then(([meData, statsData, dictStatusData, dictWordsData, activityData]) => {
            setMe(meData);
            setStats(statsData);
            setDictStatus(dictStatusData);
            setDictWords(Array.isArray(dictWordsData) ? dictWordsData : []);
            setActivity(activityData);
        }).catch(e => setError(e.message)).finally(() => setLoading(false));
    }, []);

    const go = (id) => navigate(`/student/${id}`);

    if (loading) return <div className="db-dark"><div className="db-state">⏳ {ru ? 'Загрузка...' : 'Yuklanmoqda...'}</div></div>;
    if (error || !me || !stats) return <div className="db-dark"><div className="db-state db-error">⚠️ {ru ? 'Ошибка загрузки данных' : "Ma'lumot yuklanmadi"}</div></div>;

    const profile = stats.profile || {};
    const overall = stats.overall || {};
    const courses = stats.courses || [];
    const lvl = LEVEL_META[profile.level] || LEVEL_META.Beginner;

    // Dictionary stats
    const totalWords = dictWords.length;
    const totalCorrect = dictWords.reduce((s, w) => s + (w.correct_count || 0), 0);
    const totalAttempts = dictWords.reduce((s, w) => s + (w.correct_count || 0) + (w.incorrect_count || 0), 0);
    const accuracyPct = totalAttempts > 0 ? Math.round((totalCorrect / totalAttempts) * 100) : 0;
    const practicedWords = dictWords.filter(w => (w.correct_count || 0) + (w.incorrect_count || 0) > 0).length;
    const playedToday = dictStatus?.played_today ?? 0;
    const allDone = playedToday >= QUIZ_DAILY_LIMIT;

    // Project bars + metrics
    const bars = [
        { name: ru ? 'Всего' : 'Jami',       value: overall.projects_total || 0,     color: 'linear-gradient(180deg,#b7adfb,#8b7bf2)' },
        { name: ru ? 'Одобр.' : 'Tasdiq',    value: overall.projects_approved || 0,  color: 'linear-gradient(180deg,#7ef0a3,#2bc45a)' },
        { name: ru ? 'Провер.' : 'Tekshir',  value: overall.projects_submitted || 0, color: 'linear-gradient(180deg,#fcd34d,#f59e0b)' },
        { name: ru ? 'Откл.' : 'Rad etildi', value: overall.projects_rejected || 0,  color: 'linear-gradient(180deg,#f0556b,#c0392b)' },
    ];

    // Skill radar from course mastery (top courses by exercise count, de-duped by title)
    const seen = new Set();
    const skills = courses
        .filter(c => (c.exercises_total || 0) > 0)
        .filter(c => { const k = (c.title || '').trim(); if (seen.has(k)) return false; seen.add(k); return true; })
        .slice(0, 6)
        .map(c => ({ name: c.title, pct: c.exercises_pct || 0 }));

    const courseColor = (pct) => pct >= 80 ? '#36e06b' : pct >= 40 ? '#8b7bf2' : '#f0556b';

    const features = [
        { title: ru ? 'Мои курсы' : 'Mening kurslarim',     Icon: BookOpen, glow: 'rgba(54,224,107,.5)',  path: 'courses' },
        { title: ru ? 'Рейтинг' : 'Reyting',      Icon: Trophy,   glow: 'rgba(139,123,242,.5)', path: 'rankings' },
        { title: ru ? 'Сертификаты' : 'Sertifikatlar', Icon: Award,    glow: 'rgba(54,224,107,.5)',  path: 'degrees' },
        { title: ru ? 'Достижения' : 'Yutuqlar',  Icon: Medal,    glow: 'rgba(139,123,242,.5)', path: 'achievements' },
    ];

    return (
        <div className="db-dark">
            <SvgDefs />
            <AppHeader me={me} />

            <div className="db-shell">
                {/* ── status chips ── */}
                <div className="db-welcome db-rise" style={{ animationDelay: '.04s' }}>
                    <div className="db-welcome-meta">
                        <span className="db-level">{ru ? lvl.ru : lvl.uz}</span>
                        {(profile.current_streak > 0) && (
                            <span className="db-streak"><Flame size={13} /> {profile.current_streak} {ru ? 'дн.' : 'kun'}</span>
                        )}
                        <span className="db-points">★ <CountUp value={profile.total_points || 0} group /> {ru ? 'очков' : 'ball'}</span>
                    </div>
                </div>

                {/* ── feature cards ── */}
                <div className="db-features">
                    {features.map((f, i) => (
                        <button key={f.path} className="db-feature db-rise"
                            style={{ animationDelay: `${0.08 + i * 0.05}s` }}
                            onClick={() => go(f.path)}>
                            <span className="db-f-glow" style={{ background: `radial-gradient(circle, ${f.glow}, transparent 70%)` }} />
                            <span className="db-f-top">
                                <span className="db-f-title">{f.title}</span>
                                <span className="db-f-icon"><f.Icon size={34} /></span>
                            </span>
                            <span className="db-f-more">{ru ? 'Подробнее' : 'Batafsil'} <ArrowRight size={15} /></span>
                        </button>
                    ))}
                </div>

                {/* ── analytics row ── */}
                <div className="db-grid-main">

                    {/* progress + bars */}
                    <div className="db-card db-p-progress db-rise" style={{ animationDelay: '.28s' }}>
                        <div className="db-panel-head">
                            <div className="db-panel-title">{ru ? 'Общий прогресс' : 'Umumiy progress'}</div>
                        </div>
                        <div className="db-progress-body">
                            <ProgressRing pct={overall.exercises_pct || 0}>
                                <div className="db-ring-pct"><CountUp value={overall.exercises_pct || 0} duration={1300} suffix="%" /></div>
                                <div className="db-ring-lbl">{ru ? 'Упражнения' : 'Mashqlar'}</div>
                                <div className="db-ring-sub">{overall.exercises_correct || 0}/{overall.exercises_total || 0} {ru ? 'верно' : "to'g'ri"}</div>
                            </ProgressRing>
                            <BarChart bars={bars} />
                        </div>
                        <div className="db-metrics">
                            <div className="db-metric"><div className="db-m-val" style={{ color: '#f0556b' }}><CountUp value={overall.projects_total || 0} /></div><div className="db-m-lbl">{ru ? 'Проектов всего' : 'Loyihalar jami'}</div></div>
                            <div className="db-metric"><div className="db-m-val" style={{ color: '#fbbf24' }}><CountUp value={overall.projects_approved || 0} /></div><div className="db-m-lbl">{ru ? 'Одобрено' : 'Tasdiqlangan'}</div></div>
                            <div className="db-metric"><div className="db-m-val" style={{ color: '#f0556b' }}><CountUp value={overall.projects_submitted || 0} /></div><div className="db-m-lbl">{ru ? 'На проверке' : 'Tekshirilmoqda'}</div></div>
                            <div className="db-metric"><div className="db-m-val" style={{ color: '#36e06b' }}><CountUp value={overall.total_points_from_projects || 0} group /></div><div className="db-m-lbl">{ru ? 'Очков за проекты' : 'Loyihadan ball'}</div></div>
                        </div>
                    </div>

                    {/* heatmap */}
                    <div className="db-card db-p-heat db-rise" style={{ animationDelay: '.32s' }}>
                        <div className="db-panel-head">
                            <div className="db-panel-title">{ru ? 'Карта активности' : 'Faollik xaritasi'}</div>
                            <div className="db-chip">{ru ? '6 месяцев' : "So'nggi 6 oy"}</div>
                        </div>
                        {activity && activity.days?.length ? (
                            <>
                                <Heatmap days={activity.days} ru={ru} />
                                <div className="db-heat-foot">
                                    <span><b>{activity.active_days}</b> {ru ? 'актив. дней' : 'faol kun'} · {ru ? 'серия' : 'seriya'} <b>{activity.longest_streak}</b></span>
                                    <span className="db-heat-legend">
                                        {ru ? 'Меньше' : 'Kam'}
                                        <i className="db-cell db-cell-l0 in" />
                                        <i className="db-cell db-cell-l1 in" />
                                        <i className="db-cell db-cell-l2 in" />
                                        <i className="db-cell db-cell-l3 in" />
                                        <i className="db-cell db-cell-l4 in" />
                                        {ru ? 'Больше' : "Ko'p"}
                                    </span>
                                </div>
                            </>
                        ) : (
                            <div className="db-heat-empty">{ru ? 'Данные активности появятся по мере занятий' : "Faollik ma'lumotlari mashqlar bilan to'planadi"}</div>
                        )}
                    </div>

                    {/* radar */}
                    <div className="db-card db-p-radar db-rise" style={{ animationDelay: '.36s' }}>
                        <div className="db-panel-head"><div className="db-panel-title">{ru ? 'Карта навыков' : "Ko'nikmalar xaritasi"}</div></div>
                        <div className="db-radar-wrap">
                            {skills.length >= 3
                                ? <SkillRadar skills={skills} />
                                : <div className="db-heat-empty">{ru ? 'Начните курсы, чтобы увидеть профиль навыков' : "Ko'nikma profilini ko'rish uchun kurslarni boshlang"}</div>}
                        </div>
                    </div>
                </div>

                {/* ── bottom row ── */}
                <div className="db-grid-bottom">

                    {/* dictionary */}
                    <div className="db-card db-p-dict db-rise" style={{ animationDelay: '.4s' }}>
                        <div className="db-panel-head">
                            <div className="db-panel-title">{ru ? 'Словарь и практика' : "Lug'at va mashq"}</div>
                            <button className="db-chip" onClick={() => go('dictionary')}>{ru ? 'Сегодня' : 'Bugun'}</button>
                        </div>
                        <div className="db-dict-body">
                            <div className="db-dict-nums">
                                <div className="db-dict-stat"><div className="db-d-big"><CountUp value={totalWords} /></div><div className="db-d-lbl">{ru ? 'слов в словаре' : "so'z lug'atda"}</div></div>
                                <div className="db-dict-stat"><div className="db-d-big"><CountUp value={practicedWords} /></div><div className="db-d-lbl">{ru ? 'отработано' : 'mashq qilingan'}</div></div>
                            </div>
                            <div className="db-dict-acc">
                                <ProgressRing pct={accuracyPct} size={118} stroke={9} delay={500}>
                                    <div className="db-acc-pct"><CountUp value={accuracyPct} duration={1100} suffix="%" /></div>
                                    <div className="db-acc-sub">{totalCorrect}/{totalAttempts}</div>
                                </ProgressRing>
                                <div className="db-acc-lbl">{ru ? 'Точность' : 'Aniqlik'}{allDone ? ' ✓' : ''}</div>
                            </div>
                        </div>
                    </div>

                    {/* courses */}
                    <div className="db-card db-p-courses db-rise" style={{ animationDelay: '.44s' }}>
                        <div className="db-panel-head">
                            <div className="db-panel-title">{ru ? 'Мои курсы' : 'Mening kurslarim'}</div>
                            <button className="db-see-all" onClick={() => go('courses')}>{ru ? 'Все курсы' : 'Barcha kurslar'} <ArrowRight size={14} /></button>
                        </div>
                        {courses.length === 0 ? (
                            <div className="db-heat-empty">{ru ? 'Пока нет активных курсов' : "Faol kurslar yo'q"}</div>
                        ) : (
                            <div className="db-course-list">
                                {courses.map((c, i) => {
                                    const col = courseColor(c.exercises_pct || 0);
                                    return (
                                        <div className="db-course-row" key={c.id ?? i}
                                            role="button" tabIndex={0}
                                            onClick={() => navigate(`/student/courses/${c.id}`)}
                                            onKeyDown={e => e.key === 'Enter' && navigate(`/student/courses/${c.id}`)}>
                                            <div className="db-course-top">
                                                <span className="db-course-name">{c.title}</span>
                                                <span className="db-course-pts">{c.exercises_correct || 0}/{c.exercises_total || 0}</span>
                                            </div>
                                            <div className="db-course-track">
                                                <CourseFill pct={c.exercises_pct || 0} color={col} index={i} />
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

function CourseFill({ pct, color, index }) {
    const [w, setW] = useState(0);
    useEffect(() => {
        if (prefersReduced()) { setW(pct); return; }
        const id = setTimeout(() => setW(pct), 900 + index * 70);
        return () => clearTimeout(id);
    }, [pct, index]);
    return <div className="db-course-fill" style={{ width: `${w}%`, background: `linear-gradient(90deg, ${color}, ${color}bb)` }} />;
}
