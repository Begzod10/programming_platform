import React from 'react';
import './TeacherStatistics.css';

function TeacherStatistics() {
    const overview = {
        students: 156,
        groups: 6,
        rating: 4.8,
        checkedWorks: 1240
    };

    const dynamics = [
        { label: 'Этот месяц', value: '+12%' },
        { label: 'Прошлый месяц', value: '+8%' },
        { label: 'Средний рост', value: '+10%' }
    ];

    const activity = [
        { day: 'Пн', value: 60 },
        { day: 'Вт', value: 90 },
        { day: 'Ср', value: 55 },
        { day: 'Чт', value: 90 },
        { day: 'Пт', value: 70 },
        { day: 'Сб', value: 40 },
        { day: 'Вс', value: 0 }
    ];

    return (
        <section className="stats item-fade-in">
            <header className="stats-header">
                <h3>Статистика преподавателя</h3>
                <span className="stats-period">Текущий месяц</span>
            </header>

            {/* ОБЩИЕ ПОКАЗАТЕЛИ */}
            <article className="stats-block">
                <h4>Общие показатели</h4>
                <ul className="stats-list">
                    <li><span>Всего студентов</span><b>{overview.students}</b></li>
                    <li><span>Активные группы</span><b>{overview.groups}</b></li>
                    <li><span>Средний рейтинг</span><b>{overview.rating} ⭐</b></li>
                    <li><span>Проверено работ</span><b>{overview.checkedWorks}</b></li>
                </ul>
            </article>

            {/* ДИНАМИКА */}
            <article className="stats-block">
                <h4>Динамика</h4>
                <ul className="stats-list compact">
                    {dynamics.map((item, i) => (
                        <li key={i}>
                            <span>{item.label}</span>
                            <b className="positive">{item.value}</b>
                        </li>
                    ))}
                </ul>
            </article>

            {/* ГРАФИК */}
            <article className="stats-block">
                <h4>Активность по дням</h4>

                <div className="chart">
                    {activity.map((item, i) => (
                        <div key={i} className="chart-column">
                            <div
                                className="chart-bar"
                                style={{ height: `${item.value}%` }}
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
