import React, { useEffect, useState } from 'react';
import './TeacherStatistics.css';

const API_URL = 'http://100.67.61.71:8000/api/v1/teacher/statistics';

function TeacherStatistics() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem('token'); // ✅ o'zi oladi

        if (!token) {
            setError('Token topilmadi. Qayta kiring.');
            setLoading(false);
            return;
        }

        fetch(API_URL, {
            headers: {
                'accept': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        })
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(setData)
            .catch(err => setError(err.message))
            .finally(() => setLoading(false));
    }, []); // ✅ bir marta ishga tushadi

    if (loading) return <div className="stats-loading">Загрузка статистики...</div>;
    if (error)   return <div className="stats-error">Ошибка: {error}</div>;
    if (!data)   return null;

    const maxVal = Math.max(...data.weekly_activity.map(i => i.value), 1);

    return (
        <section className="stats item-fade-in">
            <header className="stats-header">
                <h3>Статистика преподавателя</h3>
                <span className="stats-period">Текущий месяц</span>
            </header>

            <article className="stats-block">
                <h4>Общие показатели</h4>
                <ul className="stats-list">
                    <li><span>Всего студентов</span><b>{data.total_students}</b></li>
                    <li><span>Активные группы</span><b>{data.active_groups}</b></li>
                    <li><span>Средний балл</span><b>{data.average_points.toFixed(1)}</b></li>
                    <li><span>Проверено работ</span><b>{data.checked_works}</b></li>
                    <li><span>Продвинутые студенты</span><b>{data.advanced_students}</b></li>
                </ul>
            </article>

            <article className="stats-block">
                <h4>Динамика</h4>
                <ul className="stats-list compact">
                    {data.dynamics.map((item, i) => (
                        <li key={i}>
                            <span>{item.label}</span>
                            <b className={item.value.startsWith('-') ? 'negative' : 'positive'}>
                                {item.value}
                            </b>
                        </li>
                    ))}
                </ul>
            </article>

            <article className="stats-block">
                <h4>Активность по дням</h4>
                <div className="chart">
                    {data.weekly_activity.map((item, i) => (
                        <div key={i} className="chart-column">
                            <div
                                className="chart-bar"
                                style={{ height: `${(item.value / maxVal) * 100}%` }}
                            />
                            <span className="chart-label">{item.day}</span>
                        </div>
                    ))}
                </div>
            </article>
        </section>
    );
}

export default TeacherStatistics;