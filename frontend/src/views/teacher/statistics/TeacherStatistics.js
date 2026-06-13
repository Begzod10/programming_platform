import React, { useEffect, useState } from 'react';
import './TeacherStatistics.css';
import { API_URL, headers } from '../../../api/search/base';

const DAYS_ORDER = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
const DAY_FULL = {
    Пн: 'Понедельник',
    Вт: 'Вторник',
    Ср: 'Среда',
    Чт: 'Четверг',
    Пт: 'Пятница',
    Сб: 'Суббота',
};
const JS_DAY_TO_SHORT = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];

const LEVEL_COLORS = {
    Beginner:     { bg: '#fff7ed', text: '#c2410c', label: 'Начинающий' },
    Intermediate: { bg: '#eff6ff', text: '#1d4ed8', label: 'Средний' },
    Advanced:     { bg: '#f0fdf4', text: '#166534', label: 'Продвинутый' },
};

const GRADE_COLORS = {
    '5': '#22c55e', '4': '#3b82f6', '3': '#f59e0b', '2': '#ef4444',
};

function WeekRange() {
    const now = new Date();
    const day = now.getDay();
    const diffToMon = day === 0 ? -6 : 1 - day;
    const mon = new Date(now);
    mon.setDate(now.getDate() + diffToMon);
    const sat = new Date(mon);
    sat.setDate(mon.getDate() + 5);
    const fmt = (d) =>
        d.getDate() + '.' + String(d.getMonth() + 1).padStart(2, '0') + '.' + d.getFullYear();
    return (
        <span className="stats-week-range">
            {fmt(mon)} — {fmt(sat)}
        </span>
    );
}

function ActivityChart({ weeklyActivity }) {
    const todayShort = JS_DAY_TO_SHORT[new Date().getDay()];
    const dataMap = Object.fromEntries(weeklyActivity.map((i) => [i.day, i.value]));
    const ordered = DAYS_ORDER.map((d) => ({ day: d, value: dataMap[d] ?? 0 }));
    const maxVal = Math.max(...ordered.map((i) => i.value), 1);
    const peakDay = ordered.reduce((a, b) => (a.value > b.value ? a : b));

    return (
        <article className="stats-block">
            <div className="chart-header">
                <h4>Активность по дням</h4>
                <span className="peak-badge">
                    Пик: {DAY_FULL[peakDay.day]} · {peakDay.value}
                </span>
            </div>
            <div className="chart">
                {ordered.map((item) => {
                    const isToday = item.day === todayShort;
                    const heightPct = (item.value / maxVal) * 100;
                    return (
                        <div key={item.day} className={`chart-column ${isToday ? 'today' : ''}`}>
                            <div className="bar-wrap">
                                <div
                                    className={`chart-bar${heightPct < 20 ? ' small-bar' : ''}`}
                                    style={{ height: `${Math.max(heightPct, 3)}%` }}
                                >
                                    <span className="bar-value">{item.value}</span>
                                </div>
                            </div>
                            <span className="chart-label">{item.day}</span>
                            {isToday && <div className="today-dot" />}
                        </div>
                    );
                })}
            </div>
        </article>
    );
}

function LevelBreakdown({ breakdown, total }) {
    const levels = [
        { key: 'beginner',     ...LEVEL_COLORS.Beginner },
        { key: 'intermediate', ...LEVEL_COLORS.Intermediate },
        { key: 'advanced',     ...LEVEL_COLORS.Advanced },
    ];
    return (
        <article className="stats-block">
            <h4>Уровни студентов</h4>
            <div className="level-bars">
                {levels.map(({ key, bg, text, label }) => {
                    const count = breakdown[key] || 0;
                    const pct = total > 0 ? Math.round((count / total) * 100) : 0;
                    return (
                        <div key={key} className="level-row">
                            <span className="level-label">{label}</span>
                            <div className="level-track">
                                <div
                                    className="level-fill"
                                    style={{ width: `${pct}%`, background: text, opacity: 0.85 }}
                                />
                            </div>
                            <span className="level-count" style={{ color: text, background: bg }}>
                                {count}
                            </span>
                        </div>
                    );
                })}
            </div>
        </article>
    );
}

function TopStudents({ students }) {
    if (!students || students.length === 0) return null;
    const medals = ['🥇', '🥈', '🥉'];
    return (
        <article className="stats-block">
            <h4>Топ студентов</h4>
            <div className="top-students">
                {students.map((s, idx) => {
                    const lvl = LEVEL_COLORS[s.level] || LEVEL_COLORS.Beginner;
                    return (
                        <div key={s.id} className="top-student-row">
                            <span className="top-student-rank">
                                {medals[idx] || `#${idx + 1}`}
                            </span>
                            <span className="top-student-name">{s.name}</span>
                            <span
                                className="top-student-level"
                                style={{ color: lvl.text, background: lvl.bg }}
                            >
                                {lvl.label}
                            </span>
                            <span className="top-student-pts">
                                {s.points.toLocaleString()} очков
                            </span>
                        </div>
                    );
                })}
            </div>
        </article>
    );
}

function GradeDistribution({ grades }) {
    if (!grades || grades.length === 0) return null;
    const total = grades.reduce((s, g) => s + g.count, 0);
    return (
        <article className="stats-block">
            <h4>Распределение оценок</h4>
            <div className="grade-bars">
                {grades.map(({ grade, count }) => {
                    const pct = total > 0 ? Math.round((count / total) * 100) : 0;
                    const color = GRADE_COLORS[grade] || '#94a3b8';
                    return (
                        <div key={grade} className="grade-row">
                            <span className="grade-label" style={{ color }}>Оценка {grade}</span>
                            <div className="grade-track">
                                <div
                                    className="grade-fill"
                                    style={{ width: `${pct}%`, background: color }}
                                />
                            </div>
                            <span className="grade-count">
                                {count} <span className="grade-pct">({pct}%)</span>
                            </span>
                        </div>
                    );
                })}
            </div>
        </article>
    );
}

function TeacherStatistics() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            setError('Сессия истекла. Войдите заново.');
            setLoading(false);
            return;
        }
        fetch(`${API_URL}v1/teacher/statistics`, { headers: headers() })
            .then((res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(setData)
            .catch(() => setError('Не удалось загрузить статистику'))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="stats-loading">Загрузка статистики...</div>;
    if (error) return (
        <div className="stats-error">
            <p>⚠ {error}</p>
            <button onClick={() => window.location.reload()}>Повторить</button>
        </div>
    );
    if (!data) return null;

    return (
        <section className="stats item-fade-in">
            <header className="stats-header">
                <h3>Статистика преподавателя</h3>
                <div className="stats-header-right">
                    <WeekRange />
                    <span className="stats-period">Текущий месяц</span>
                </div>
            </header>

            <article className="stats-block">
                <h4>Общие показатели</h4>
                <ul className="stats-list">
                    <li>
                        <span>Всего студентов</span>
                        <b>{data.total_students}</b>
                    </li>
                    <li>
                        <span>Активные группы</span>
                        <b>{data.active_groups}</b>
                    </li>
                    <li>
                        <span>Средний балл</span>
                        <b>{(data.average_points ?? 0).toFixed(1)}</b>
                    </li>
                    <li>
                        <span>Проверено работ</span>
                        <b>{data.checked_works}</b>
                    </li>
                    <li>
                        <span>Ожидают проверки</span>
                        <b className={data.pending_works > 0 ? 'pending-alert' : ''}>
                            {data.pending_works}
                        </b>
                    </li>
                    <li>
                        <span>Продвинутые студенты</span>
                        <b>{data.advanced_students}</b>
                    </li>
                </ul>
            </article>

            <article className="stats-block">
                <h4>Динамика проверок</h4>
                <ul className="stats-list compact">
                    {(data.dynamics || []).map((item, i) => (
                        <li key={i}>
                            <span>{item.label}</span>
                            <b className={
                                item.value === 'N/A' ? 'neutral' :
                                item.value.startsWith('-') ? 'negative' : 'positive'
                            }>
                                {item.value}
                            </b>
                        </li>
                    ))}
                </ul>
            </article>

            <ActivityChart weeklyActivity={data.weekly_activity} />

            {data.level_breakdown && (
                <LevelBreakdown breakdown={data.level_breakdown} total={data.total_students} />
            )}

            <TopStudents students={data.top_students} />

            <GradeDistribution grades={data.grade_distribution} />
        </section>
    );
}

export default TeacherStatistics;
