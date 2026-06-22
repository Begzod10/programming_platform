import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL, headers, resolveImageUrl } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import './CourseRoadmap.css';
import { Check, Lock, Trophy } from 'lucide-react';

const DIFF_META = {
    Beginner:     { ru: 'Начальный',   uz: 'Boshlang\'ich', color: '#6366f1' },
    Intermediate: { ru: 'Средний',     uz: 'O\'rta',        color: '#d97706' },
    Advanced:     { ru: 'Продвинутый', uz: 'Ilg\'or',       color: '#dc2626' },
    Expert:       { ru: 'Эксперт',     uz: 'Ekspert',       color: '#7c3aed' },
};

const STATUS_META = {
    completed:   { color: '#16a34a', bg: '#f0fdf4', border: '#bbf7d0', dotBg: '#16a34a', icon: '✓' },
    in_progress: { color: '#6c5ce7', bg: '#f5f3ff', border: '#ddd6fe', dotBg: '#6c5ce7', icon: '▶' },
    available:   { color: '#0ea5e9', bg: '#f0f9ff', border: '#bae6fd', dotBg: '#0ea5e9', icon: '○' },
    locked:      { color: '#94a3b8', bg: '#f8fafc', border: '#e2e8f0', dotBg: '#cbd5e1', icon: '🔒' },
};

function getStatus(course) {
    if (course.is_enrolled === false || course.is_locked === true) return 'locked';
    const pct = Math.round(course.progress_percentage || 0);
    if (pct >= 100) return 'completed';
    if (pct > 0) return 'in_progress';
    return 'available';
}

function ProgressBar({ pct, color }) {
    return (
        <div className="rm-prog-track">
            <div
                className="rm-prog-fill"
                style={{ width: `${pct}%`, background: color }}
            />
        </div>
    );
}

function CourseNode({ course, index, ru, onClick }) {
    const status = getStatus(course);
    const meta = STATUS_META[status];
    const diff = DIFF_META[course.difficulty_level] || { ru: course.difficulty_level, uz: course.difficulty_level, color: '#64748b' };
    const pct = Math.round(course.progress_percentage || 0);
    const imgSrc = resolveImageUrl(course.image_url);
    const isEven = index % 2 === 1;

    const statusLabel = {
        completed:   { ru: 'Завершён',    uz: 'Tugatildi' },
        in_progress: { ru: 'В процессе',  uz: 'Davom etmoqda' },
        available:   { ru: 'Доступен',    uz: 'Mavjud' },
        locked:      { ru: 'Заблокирован',uz: 'Bloklangan' },
    }[status];

    return (
        <div className={`rm-node ${isEven ? 'rm-node--reverse' : ''}`}>
            {/* Card side */}
            <div
                className={`rm-card rm-card--${status}`}
                style={{ borderColor: meta.border, background: meta.bg }}
                onClick={status !== 'locked' ? onClick : undefined}
                role={status !== 'locked' ? 'button' : undefined}
                tabIndex={status !== 'locked' ? 0 : undefined}
                onKeyDown={e => status !== 'locked' && e.key === 'Enter' && onClick()}
                aria-label={course.title}
            >
                <div className="rm-card-header">
                    {imgSrc ? (
                        <img src={imgSrc} alt="" className="rm-card-img" />
                    ) : (
                        <div className="rm-card-img-placeholder" style={{ background: course.color_accent || meta.color }} />
                    )}
                    <div className="rm-card-info">
                        <div className="rm-card-num" style={{ color: meta.color }}>
                            {ru ? 'Курс' : 'Kurs'} {index + 1}
                        </div>
                        <div className="rm-card-title">{course.title}</div>
                        <div className="rm-card-tags">
                            {course.difficulty_level && (
                                <span className="rm-tag" style={{ color: diff.color, background: diff.color + '18' }}>
                                    {ru ? diff.ru : diff.uz}
                                </span>
                            )}
                            <span className="rm-tag rm-tag--neutral">
                                {course.lessons_count || 0} {ru ? 'уроков' : 'dars'}
                            </span>
                        </div>
                    </div>
                </div>

                {status === 'in_progress' && (
                    <div className="rm-card-progress">
                        <ProgressBar pct={pct} color={meta.color} />
                        <span className="rm-card-pct" style={{ color: meta.color }}>{pct}%</span>
                    </div>
                )}

                <div className="rm-card-footer">
                    <span className="rm-status-chip" style={{ color: meta.color, background: meta.color + '18' }}>
                        {meta.icon} {ru ? statusLabel.ru : statusLabel.uz}
                    </span>
                    {status === 'in_progress' && (
                        <span className="rm-card-action" style={{ color: meta.color }}>
                            {ru ? 'Продолжить →' : 'Davom →'}
                        </span>
                    )}
                    {status === 'available' && (
                        <span className="rm-card-action" style={{ color: meta.color }}>
                            {ru ? 'Начать →' : 'Boshlash →'}
                        </span>
                    )}
                    {status === 'completed' && (
                        <span className="rm-card-action" style={{ color: meta.color }}>
                            {ru ? 'Повторить →' : "Ko'rish →"}
                        </span>
                    )}
                </div>
            </div>

            {/* Center connector */}
            <div className="rm-connector">
                <div
                    className={`rm-dot rm-dot--${status}`}
                    style={{ background: meta.dotBg }}
                >
                    <span className="rm-dot-icon">
                        {status === 'completed' ? <Check size={14} aria-hidden="true" /> : status === 'locked' ? <Lock size={14} aria-hidden="true" /> : index + 1}
                    </span>
                </div>
            </div>

            {/* Empty spacer on other side */}
            <div className="rm-spacer" />
        </div>
    );
}

export default function CourseRoadmap() {
    const navigate = useNavigate();
    const { lang } = useTranslation();
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const ru = lang === 'ru';

    useEffect(() => {
        fetch(`${API_URL}v1/courses/?limit=100`, { headers: headers() })
            .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
            .then(data => {
                const sorted = [...data]
                    .filter(c => c.is_published !== false && c.is_active !== false)
                    .sort((a, b) => (a.display_order || 0) - (b.display_order || 0));
                setCourses(sorted);
            })
            .catch(e => setError(e.message))
            .finally(() => setLoading(false));
    }, []);

    const completed  = courses.filter(c => getStatus(c) === 'completed').length;
    const inProgress = courses.filter(c => getStatus(c) === 'in_progress').length;
    const available  = courses.filter(c => getStatus(c) === 'available').length;
    const locked     = courses.filter(c => getStatus(c) === 'locked').length;

    if (loading) return (
        <div className="rm-page">
            <div className="rm-loading">
                <div className="rm-loading-spinner" />
                <p>{ru ? 'Загрузка маршрута...' : "Yo'l yuklanmoqda..."}</p>
            </div>
        </div>
    );

    if (error) return (
        <div className="rm-page">
            <div className="rm-error">⚠️ {ru ? 'Не удалось загрузить курсы' : "Kurslarni yuklab bo'lmadi"}</div>
        </div>
    );

    return (
        <div className="rm-page">

            {/* ── Header ── */}
            <div className="rm-header">
                <div>
                    <h1 className="rm-title">{ru ? 'Карта обучения' : "O'quv yo'lxaritasi"}</h1>
                    <p className="rm-subtitle">
                        {ru
                            ? 'Ваш путь от основ до экспертного уровня'
                            : "Boshlang'ichdan ekspert darajasiga yo'lingiz"}
                    </p>
                </div>
                <button className="rm-courses-link" onClick={() => navigate('/student/courses')}>
                    {ru ? '⊞ Список курсов' : '⊞ Kurslar ro\'yhati'}
                </button>
            </div>

            {/* ── Summary chips ── */}
            <div className="rm-summary">
                <div className="rm-summary-chip rm-summary-chip--completed">
                    <span className="rm-summary-val">{completed}</span>
                    <span className="rm-summary-label">{ru ? 'завершено' : 'tugatildi'}</span>
                </div>
                <div className="rm-summary-chip rm-summary-chip--progress">
                    <span className="rm-summary-val">{inProgress}</span>
                    <span className="rm-summary-label">{ru ? 'в процессе' : 'davom etmoqda'}</span>
                </div>
                <div className="rm-summary-chip rm-summary-chip--available">
                    <span className="rm-summary-val">{available}</span>
                    <span className="rm-summary-label">{ru ? 'доступно' : 'mavjud'}</span>
                </div>
                <div className="rm-summary-chip rm-summary-chip--locked">
                    <span className="rm-summary-val">{locked}</span>
                    <span className="rm-summary-label">{ru ? 'заблокировано' : 'bloklangan'}</span>
                </div>
            </div>

            {/* ── Overall progress bar ── */}
            {courses.length > 0 && (
                <div className="rm-overall">
                    <div className="rm-overall-bar">
                        <div
                            className="rm-overall-fill"
                            style={{ width: `${Math.round((completed / courses.length) * 100)}%` }}
                        />
                    </div>
                    <span className="rm-overall-label">
                        {completed}/{courses.length} {ru ? 'курсов завершено' : 'kurs tugatildi'}
                        {' — '}{Math.round((completed / courses.length) * 100)}%
                    </span>
                </div>
            )}

            {/* ── Start cap ── */}
            {courses.length > 0 && (
                <div className="rm-cap rm-cap--start">
                    <span>{ru ? '🚀 Старт' : '🚀 Boshlash'}</span>
                </div>
            )}

            {/* ── Zigzag path ── */}
            <div className="rm-path">
                {courses.map((course, i) => (
                    <CourseNode
                        key={course.id}
                        course={course}
                        index={i}
                        ru={ru}
                        onClick={() => navigate(`/student/courses/${course.id}`)}
                    />
                ))}
            </div>

            {/* ── Finish cap ── */}
            {courses.length > 0 && (
                <div className={`rm-cap rm-cap--finish ${completed === courses.length ? 'rm-cap--done' : ''}`}>
                    <span>{completed === courses.length ? <><Trophy size={16} aria-hidden="true" />{' '}</> : ''}
                        {ru ? 'Финиш' : 'Finish'}
                        {completed === courses.length ? (ru ? ' — Молодец!' : ' — Barakalla!') : ''}
                    </span>
                </div>
            )}

            {courses.length === 0 && (
                <div className="rm-empty">
                    <span className="rm-empty-icon">📚</span>
                    <p>{ru ? 'Курсы пока не добавлены' : "Kurslar hali qo'shilmagan"}</p>
                </div>
            )}
        </div>
    );
}
