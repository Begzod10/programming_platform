import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL, headers, resolveImageUrl } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import './StudentDashboard.css';

const LEVEL_META = {
    Beginner:     { ru: 'Начинающий', uz: "Boshlang'ich", color: '#c2410c', bg: '#fff7ed' },
    Intermediate: { ru: 'Средний',    uz: "O'rta",        color: '#1d4ed8', bg: '#eff6ff' },
    Advanced:     { ru: 'Продвинутый',uz: "Ilg'or",       color: '#166534', bg: '#f0fdf4' },
};

function ProgressRing({ pct, size = 60, stroke = 6, color = '#6c5ce7' }) {
    const r = (size - stroke) / 2;
    const circ = 2 * Math.PI * r;
    const dash = (pct / 100) * circ;
    return (
        <svg width={size} height={size} className="db-ring">
            <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#e2e8f0" strokeWidth={stroke} />
            <circle
                cx={size/2} cy={size/2} r={r} fill="none"
                stroke={color} strokeWidth={stroke}
                strokeDasharray={`${dash} ${circ - dash}`}
                strokeLinecap="round"
                transform={`rotate(-90 ${size/2} ${size/2})`}
                style={{ transition: 'stroke-dasharray 0.6s ease' }}
            />
            <text x="50%" y="50%" dominantBaseline="middle" textAnchor="middle"
                fill="#1e293b" fontSize={size * 0.22} fontWeight="700">
                {pct}%
            </text>
        </svg>
    );
}

export default function StudentDashboard() {
    const navigate = useNavigate();
    const { lang } = useTranslation();
    const [me, setMe] = useState(null);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const ru = lang === 'ru';

    useEffect(() => {
        Promise.all([
            fetch(`${API_URL}v1/student/me`, { headers: headers() }).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
            fetch(`${API_URL}v1/student/me/course-stats`, { headers: headers() }).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }),
        ]).then(([meData, statsData]) => {
            setMe(meData);
            setStats(statsData);
        }).catch(e => setError(e.message)).finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="db-state db-loading">⏳ {ru ? 'Загрузка...' : 'Yuklanmoqda...'}</div>;
    if (error || !me || !stats) return <div className="db-state db-error">⚠️ {ru ? 'Ошибка загрузки данных' : 'Ma\'lumot yuklanmadi'}</div>;

    const profile = stats.profile || {};
    const overall = stats.overall || {};
    const courses = stats.courses || [];
    const lvl = LEVEL_META[profile.level] || LEVEL_META.Beginner;
    const displayName = me.full_name || me.username || '';
    const avatarSrc = resolveImageUrl(me.avatar_url);

    return (
        <div className="db-page">

            {/* ── Welcome header ── */}
            <div className="db-welcome item-fade-in">
                <div className="db-welcome-avatar">
                    {avatarSrc
                        ? <img src={avatarSrc} alt="" className="db-avatar-img" />
                        : <div className="db-avatar-initials">{(displayName || 'U')[0].toUpperCase()}</div>
                    }
                </div>
                <div className="db-welcome-body">
                    <h1 className="db-welcome-title">
                        {ru ? 'Добро пожаловать' : 'Xush kelibsiz'}, <span className="db-welcome-name">{displayName}</span>!
                    </h1>
                    <div className="db-welcome-meta">
                        <span className="db-level-badge" style={{ color: lvl.color, background: lvl.bg }}>
                            {ru ? lvl.ru : lvl.uz}
                        </span>
                        {me.current_streak > 0 && (
                            <span className="db-streak-chip">🔥 {me.current_streak} {ru ? 'дн.' : 'kun'}</span>
                        )}
                    </div>
                </div>
            </div>

            {/* ── Quick stats row ── */}
            <div className="db-stats-grid item-fade-in">
                <div className="db-stat-card">
                    <span className="db-stat-icon">⭐</span>
                    <span className="db-stat-val">{(profile.total_points || 0).toLocaleString()}</span>
                    <span className="db-stat-label">{ru ? 'Очков' : 'Ball'}</span>
                </div>
                <div className="db-stat-card">
                    <span className="db-stat-icon">🏆</span>
                    <span className="db-stat-val">{profile.global_rank ? `#${profile.global_rank}` : '—'}</span>
                    <span className="db-stat-label">{ru ? 'Рейтинг' : 'Reyting'}</span>
                </div>
                <div className="db-stat-card">
                    <span className="db-stat-icon">🔥</span>
                    <span className="db-stat-val">{profile.current_streak || 0}</span>
                    <span className="db-stat-label">{ru ? 'Дней подряд' : 'Ketma-ket kun'}</span>
                </div>
                <div className="db-stat-card">
                    <span className="db-stat-icon">✅</span>
                    <span className="db-stat-val">{overall.projects_approved || 0}</span>
                    <span className="db-stat-label">{ru ? 'Проектов сдано' : 'Loyiha topshirilgan'}</span>
                </div>
            </div>

            {/* ── Overall progress ── */}
            <div className="db-section item-fade-in">
                <h2 className="db-section-title">{ru ? 'Общий прогресс' : 'Umumiy progress'}</h2>
                <div className="db-overall-card">
                    <div className="db-overall-left">
                        <ProgressRing pct={overall.exercises_pct || 0} color="#6c5ce7" />
                        <div className="db-overall-text">
                            <div className="db-overall-label">{ru ? 'Упражнения' : 'Mashqlar'}</div>
                            <div className="db-overall-sub">
                                {overall.exercises_correct || 0}/{overall.exercises_total || 0} {ru ? 'верно' : 'to\'g\'ri'}
                            </div>
                        </div>
                    </div>
                    <div className="db-overall-divider" />
                    <div className="db-overall-pills">
                        <div className="db-pill">
                            <span className="db-pill-val" style={{ color: '#6c5ce7' }}>{overall.projects_total || 0}</span>
                            <span className="db-pill-label">{ru ? 'Проектов всего' : 'Loyihalar jami'}</span>
                        </div>
                        <div className="db-pill">
                            <span className="db-pill-val" style={{ color: '#16a34a' }}>{overall.projects_approved || 0}</span>
                            <span className="db-pill-label">{ru ? 'Одобрено' : 'Tasdiqlangan'}</span>
                        </div>
                        <div className="db-pill">
                            <span className="db-pill-val" style={{ color: '#d97706' }}>{overall.projects_submitted || 0}</span>
                            <span className="db-pill-label">{ru ? 'На проверке' : 'Tekshirilmoqda'}</span>
                        </div>
                        <div className="db-pill">
                            <span className="db-pill-val" style={{ color: '#6c5ce7' }}>{(overall.total_points_from_projects || 0).toLocaleString()}</span>
                            <span className="db-pill-label">{ru ? 'Очков за проекты' : 'Loyihadan ball'}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* ── My courses ── */}
            <div className="db-section item-fade-in">
                <div className="db-section-header">
                    <h2 className="db-section-title">{ru ? 'Мои курсы' : 'Mening kurslarim'}</h2>
                    <button className="db-see-all" onClick={() => navigate('/student/courses')}>
                        {ru ? 'Все курсы →' : 'Barcha kurslar →'}
                    </button>
                </div>
                {courses.length === 0 ? (
                    <div className="db-empty">
                        <span className="db-empty-icon">📚</span>
                        <p>{ru ? 'Пока нет активных курсов' : "Faol kurslar yo'q"}</p>
                        <button className="db-cta" onClick={() => navigate('/student/courses')}>
                            {ru ? 'Начать обучение' : "O'qishni boshlash"}
                        </button>
                    </div>
                ) : (
                    <div className="db-courses-grid">
                        {courses.map(course => (
                            <div
                                key={course.id}
                                className="db-course-card"
                                style={{ borderTopColor: course.color_accent || '#6c5ce7' }}
                                onClick={() => navigate(`/student/courses/${course.id}`)}
                                role="button"
                                tabIndex={0}
                                onKeyDown={e => e.key === 'Enter' && navigate(`/student/courses/${course.id}`)}
                            >
                                <div className="db-course-title">{course.title}</div>
                                <div className="db-course-track">
                                    <div
                                        className="db-course-fill"
                                        style={{
                                            width: `${course.exercises_pct || 0}%`,
                                            background: course.color_accent || '#6c5ce7',
                                        }}
                                    />
                                </div>
                                <div className="db-course-meta">
                                    <span>{course.exercises_correct || 0}/{course.exercises_total || 0} {ru ? 'упр.' : 'mashq'}</span>
                                    <span style={{ color: course.color_accent || '#6c5ce7', fontWeight: 700 }}>
                                        {course.exercises_pct || 0}%
                                    </span>
                                </div>
                                {(course.submissions_pending > 0) && (
                                    <div className="db-course-badge db-course-badge--pending">
                                        ⏳ {course.submissions_pending} {ru ? 'на проверке' : 'tekshirilmoqda'}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* ── Quick navigation ── */}
            <div className="db-section item-fade-in">
                <h2 className="db-section-title">{ru ? 'Быстрый доступ' : 'Tezkor kirish'}</h2>
                <div className="db-quick-links">
                    {[
                        { icon: '💻', ru: 'Проекты',     uz: 'Loyihalar',    path: '/student/projects' },
                        { icon: '🏆', ru: 'Рейтинг',     uz: 'Reyting',      path: '/student/rankings' },
                        { icon: '📖', ru: 'Словарь',     uz: "Lug'at",       path: '/student/dictionary' },
                        { icon: '📊', ru: 'Статистика',  uz: 'Statistika',   path: '/student/statistics' },
                        { icon: '🎓', ru: 'Сертификаты', uz: 'Sertifikatlar',path: '/student/degrees' },
                        { icon: '🎮', ru: 'Игры',        uz: "O'yinlar",     path: '/student/team-game' },
                    ].map(link => (
                        <button
                            key={link.path}
                            className="db-qlink"
                            onClick={() => navigate(link.path)}
                        >
                            <span className="db-qlink-icon">{link.icon}</span>
                            <span className="db-qlink-label">{ru ? link.ru : link.uz}</span>
                        </button>
                    ))}
                </div>
            </div>

        </div>
    );
}
