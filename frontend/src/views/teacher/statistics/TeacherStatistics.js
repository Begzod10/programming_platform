import React, { useState, useEffect, useCallback } from 'react';
import './TeacherStatistics.css';
import { API_URL, headers } from '../../../api/search/base';

const REFRESH_INTERVAL = 30000; // 30 seconds

function TeacherStatistics() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdated, setLastUpdated] = useState(null);

    const fetchStats = useCallback(async () => {
        try {
            const res = await fetch(`${API_URL}v1/teacher/statistics`, {
                method: 'GET',
                headers: headers(),
            });
            if (!res.ok) throw new Error(`Xatolik: ${res.status}`);
            const json = await res.json();
            setData(json);
            setLastUpdated(new Date());
            setError(null);
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchStats();
        const interval = setInterval(fetchStats, REFRESH_INTERVAL);
        return () => clearInterval(interval);
    }, [fetchStats]);

    // Compute max for chart scaling
    const maxActivity = data?.weekly_activity
        ? Math.max(...data.weekly_activity.map(d => d.value), 1)
        : 1;

    if (loading) {
        return (
            <section className="stats item-fade-in">
                <div className="stats-loading">
                    <div className="stats-spinner" />
                    <span>Yuklanmoqda...</span>
                </div>
            </section>
        );
    }

    if (error) {
        return (
            <section className="stats item-fade-in">
                <div className="stats-error">
                    <span>⚠️ {error}</span>
                    <button onClick={fetchStats} className="stats-retry-btn">Qayta urinish</button>
                </div>
            </section>
        );
    }

    return (
        <section className="stats item-fade-in">
            <header className="stats-header">
                <h3>O'qituvchi statistikasi</h3>
                <div className="stats-header-right">
                    <span className="stats-period">Joriy oy</span>
                    {lastUpdated && (
                        <span className="stats-updated">
                            Yangilandi: {lastUpdated.toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                        </span>
                    )}
                    <button className="stats-refresh-btn" onClick={fetchStats} title="Yangilash">⟳</button>
                </div>
            </header>

            {/* UMUMIY KO'RSATKICHLAR */}
            <article className="stats-block">
                <h4>Umumiy ko'rsatkichlar</h4>
                <ul className="stats-list">
                    <li><span>Jami talabalar</span><b>{data.total_students}</b></li>
                    <li><span>Faol guruhlar</span><b>{data.active_groups}</b></li>
                    <li><span>O'rtacha ball</span><b>{data.average_points} ⭐</b></li>
                    <li><span>Tekshirilgan ishlar</span><b>{data.checked_works}</b></li>
                </ul>
            </article>

            {/* DINAMIKA */}
            <article className="stats-block">
                <h4>Dinamika</h4>
                <ul className="stats-list compact">
                    {data.dynamics.map((item, i) => {
                        const isPositive = item.value.startsWith('+');
                        const isNegative = item.value.startsWith('-');
                        return (
                            <li key={i}>
                                <span>{item.label}</span>
                                <b className={isPositive ? 'positive' : isNegative ? 'negative' : ''}>
                                    {item.value}
                                </b>
                            </li>
                        );
                    })}
                </ul>
            </article>

            {/* GRAFIK */}
            <article className="stats-block">
                <h4>Kunlik aktivlik (tekshirilgan ishlar)</h4>
                <div className="chart">
                    {data.weekly_activity.map((item, i) => {
                        const heightPct = Math.round((item.value / maxActivity) * 100);
                        return (
                            <div key={i} className="chart-column">
                                <span className="chart-value">{item.value}</span>
                                <div
                                    className="chart-bar"
                                    style={{ height: `${Math.max(heightPct, item.value > 0 ? 5 : 0)}%` }}
                                />
                                <span className="chart-label">{item.day}</span>
                            </div>
                        );
                    })}
                </div>
            </article>
        </section>
    );
}

export default TeacherStatistics;
