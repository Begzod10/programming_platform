import React, { useEffect, useState } from 'react';
import './TeacherStatistics.css';

const API_URL = 'http://100.67.61.71:8000/api/v1/teacher/statistics';

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

function WeekRange() {
    const now = new Date();
    const day = now.getDay();
    const diffToMon = day === 0 ? -6 : 1 - day;
    const mon = new Date(now);
    mon.setDate(now.getDate() + diffToMon);
    const sat = new Date(mon);
    sat.setDate(mon.getDate() + 5);
    const fmt = (d) =>
        d.getDate() +
        '.' +
        String(d.getMonth() + 1).padStart(2, '0') +
        '.' +
        d.getFullYear();
    return (
        <span className="stats-week-range">
            {fmt(mon)} — {fmt(sat)}
        </span>
    );
}

function ActivityChart({ weeklyActivity }) {
    const todayShort = JS_DAY_TO_SHORT[new Date().getDay()];

    const dataMap = Object.fromEntries(
        weeklyActivity.map((i) => [i.day, i.value])
    );

    const ordered = DAYS_ORDER.map((d) => ({
        day: d,
        value: dataMap[d] ?? 0,
    }));

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
                        <div
                            key={item.day}
                            className={`chart-column ${isToday ? 'today' : ''}`}
                        >
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

function TeacherStatistics() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            setError('Token topilmadi. Qayta kiring.');
            setLoading(false);
            return;
        }

        fetch(API_URL, {
            headers: {
                accept: 'application/json',
                Authorization: `Bearer ${token}`,
            },
        })
            .then((res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(setData)
            .catch((err) => setError(err.message))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="stats-loading">Загрузка статистики...</div>;
    if (error) return <div className="stats-error">Ошибка: {error}</div>;
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
                        <b>{data.average_points.toFixed(1)}</b>
                    </li>
                    <li>
                        <span>Проверено работ</span>
                        <b>{data.checked_works}</b>
                    </li>
                    <li>
                        <span>Продвинутые студенты</span>
                        <b>{data.advanced_students}</b>
                    </li>
                </ul>
            </article>

            <article className="stats-block">
                <h4>Динамика</h4>
                <ul className="stats-list compact">
                    {data.dynamics.map((item, i) => (
                        <li key={i}>
                            <span>{item.label}</span>
                            <b
                                className={
                                    item.value.startsWith('-')
                                        ? 'negative'
                                        : 'positive'
                                }
                            >
                                {item.value}
                            </b>
                        </li>
                    ))}
                </ul>
            </article>

            <ActivityChart weeklyActivity={data.weekly_activity} />
        </section>
    );
}

export default TeacherStatistics;