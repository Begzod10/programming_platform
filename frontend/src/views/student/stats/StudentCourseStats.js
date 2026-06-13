import React, { useEffect, useState } from 'react';
import { API_URL, headers } from '../../../api/search/base';
import './StudentCourseStats.css';

const LEVEL_META = {
    Beginner:     { label: 'Начинающий', color: '#c2410c', bg: '#fff7ed' },
    Intermediate: { label: 'Средний',    color: '#1d4ed8', bg: '#eff6ff' },
    Advanced:     { label: 'Продвинутый',color: '#166534', bg: '#f0fdf4' },
};

const DIFF_META = {
    Easy:     { label: 'Лёгкий',    color: '#16a34a' },
    Medium:   { label: 'Средний',   color: '#d97706' },
    Hard:     { label: 'Сложный',   color: '#dc2626' },
    Beginner: { label: 'Начальный', color: '#6366f1' },
};

function ProgressRing({ pct, size = 64, stroke = 6, color = '#6c5ce7' }) {
    const r = (size - stroke) / 2;
    const circ = 2 * Math.PI * r;
    const dash = (pct / 100) * circ;
    return (
        <svg width={size} height={size} className="progress-ring">
            <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#e2e8f0" strokeWidth={stroke} />
            <circle
                cx={size / 2} cy={size / 2} r={r} fill="none"
                stroke={color} strokeWidth={stroke}
                strokeDasharray={`${dash} ${circ - dash}`}
                strokeLinecap="round"
                transform={`rotate(-90 ${size / 2} ${size / 2})`}
                style={{ transition: 'stroke-dasharray 0.6s ease' }}
            />
            <text x="50%" y="50%" dominantBaseline="middle" textAnchor="middle"
                fill="#1e293b" fontSize={size * 0.22} fontWeight="700">
                {pct}%
            </text>
        </svg>
    );
}

function StatPill({ label, value, color }) {
    return (
        <div className="scs-pill">
            <span className="scs-pill-val" style={{ color }}>{value}</span>
            <span className="scs-pill-label">{label}</span>
        </div>
    );
}

function ProfileCard({ profile }) {
    const lvl = LEVEL_META[profile.level] || LEVEL_META.Beginner;
    return (
        <div className="scs-profile-card">
            <div className="scs-profile-left">
                <span className="scs-profile-level" style={{ color: lvl.color, background: lvl.bg }}>
                    {lvl.label}
                </span>
                <div className="scs-profile-pts">{profile.total_points.toLocaleString()}</div>
                <div className="scs-profile-pts-label">очков всего</div>
            </div>
            <div className="scs-profile-divider" />
            <div className="scs-profile-right">
                <div className="scs-streak-row">
                    <span className="scs-streak-icon">🔥</span>
                    <div>
                        <div className="scs-streak-val">{profile.current_streak} дней</div>
                        <div className="scs-streak-label">текущая серия</div>
                    </div>
                </div>
                <div className="scs-streak-row">
                    <span className="scs-streak-icon">⚡</span>
                    <div>
                        <div className="scs-streak-val">{profile.longest_streak} дней</div>
                        <div className="scs-streak-label">лучшая серия</div>
                    </div>
                </div>
                {profile.global_rank && (
                    <div className="scs-streak-row">
                        <span className="scs-streak-icon">🏆</span>
                        <div>
                            <div className="scs-streak-val">#{profile.global_rank}</div>
                            <div className="scs-streak-label">глобальный рейтинг</div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function OverallCard({ overall }) {
    const exPct = overall.exercises_pct;
    const projApproved = overall.projects_approved;
    const projTotal    = overall.projects_total;
    return (
        <div className="scs-overall-card">
            <h2 className="scs-section-title">Общая успеваемость</h2>
            <div className="scs-overall-grid">
                <div className="scs-overall-item">
                    <ProgressRing pct={exPct} color="#6c5ce7" />
                    <div className="scs-overall-meta">
                        <div className="scs-overall-label">Упражнения</div>
                        <div className="scs-overall-sub">
                            {overall.exercises_correct} / {overall.exercises_total} верно
                        </div>
                    </div>
                </div>
                <div className="scs-overall-divider" />
                <div className="scs-overall-pills">
                    <StatPill label="Проектов всего"    value={projTotal}          color="#1e293b" />
                    <StatPill label="Одобрено"          value={projApproved}       color="#16a34a" />
                    <StatPill label="На проверке"       value={overall.projects_submitted} color="#d97706" />
                    <StatPill label="Очков за проекты"  value={overall.total_points_from_projects.toLocaleString()} color="#6c5ce7" />
                </div>
            </div>
        </div>
    );
}

function CourseCard({ course }) {
    const diff = DIFF_META[course.difficulty_level] || { label: course.difficulty_level, color: '#64748b' };
    const ex = course.exercises_total;
    const exCorrect = course.exercises_correct;
    const exPct = course.exercises_pct;
    const subTotal    = course.submissions_total;
    const subApproved = course.submissions_approved;
    const subPending  = course.submissions_pending;
    const subRejected = course.submissions_rejected;

    return (
        <div className="scs-course-card" style={{ borderTopColor: course.color_accent }}>
            <div className="scs-course-header">
                {course.image_url
                    ? <img src={course.image_url} alt="" className="scs-course-img" />
                    : <div className="scs-course-img-placeholder" style={{ background: course.color_accent }} />
                }
                <div className="scs-course-meta">
                    <div className="scs-course-title">{course.title}</div>
                    <span className="scs-course-diff" style={{ color: diff.color }}>{diff.label}</span>
                </div>
            </div>

            {/* Exercise progress */}
            <div className="scs-course-section">
                <div className="scs-course-section-label">
                    Упражнения
                    <span className="scs-course-section-count">{exCorrect}/{ex}</span>
                </div>
                {ex > 0 ? (
                    <div className="scs-progress-track">
                        <div
                            className="scs-progress-fill"
                            style={{ width: `${exPct}%`, background: course.color_accent }}
                        />
                    </div>
                ) : (
                    <div className="scs-course-empty">Упражнений нет</div>
                )}
                {ex > 0 && <div className="scs-progress-pct" style={{ color: course.color_accent }}>{exPct}%</div>}
            </div>

            {/* Project submissions */}
            {subTotal > 0 && (
                <div className="scs-course-section">
                    <div className="scs-course-section-label">Проекты</div>
                    <div className="scs-sub-pills">
                        {subApproved > 0 && (
                            <span className="scs-sub-pill scs-sub-pill--ok">✓ {subApproved} одобрено</span>
                        )}
                        {subPending > 0 && (
                            <span className="scs-sub-pill scs-sub-pill--pending">⏳ {subPending} на проверке</span>
                        )}
                        {subRejected > 0 && (
                            <span className="scs-sub-pill scs-sub-pill--rej">✗ {subRejected} отклонено</span>
                        )}
                    </div>
                    {course.points_from_submissions > 0 && (
                        <div className="scs-course-pts">
                            +{course.points_from_submissions} очков
                        </div>
                    )}
                </div>
            )}

            {subTotal === 0 && ex === 0 && (
                <div className="scs-course-empty">Ещё нет активности по этому курсу</div>
            )}
        </div>
    );
}

export default function StudentCourseStats() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch(`${API_URL}v1/student/me/course-stats`, { headers: headers() })
            .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
            .then(setData)
            .catch(() => setError('Не удалось загрузить статистику'))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="scs-center">Загрузка статистики...</div>;
    if (error)   return <div className="scs-center scs-error">⚠ {error}</div>;
    if (!data)   return null;

    return (
        <div className="scs-page item-fade-in">
            <div className="scs-page-header">
                <h1>Моя статистика</h1>
                <p className="scs-subtitle">Прогресс по упражнениям и проектам во всех курсах</p>
            </div>

            <ProfileCard profile={data.profile} />
            <OverallCard overall={data.overall} />

            <h2 className="scs-section-title">По курсам ({data.courses.length})</h2>

            {data.courses.length === 0 ? (
                <div className="scs-empty">
                    <div className="scs-empty-icon">📚</div>
                    <p>Вы ещё не записаны ни на один курс</p>
                </div>
            ) : (
                <div className="scs-courses-grid">
                    {data.courses.map(c => <CourseCard key={c.id} course={c} />)}
                </div>
            )}
        </div>
    );
}
