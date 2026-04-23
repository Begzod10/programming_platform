import React, { useState, useEffect } from 'react';
import './DegreeCard.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';

const Degrees = () => {
    const { request } = useHttp();
    const [progress,    setProgress]    = useState([]);
    const [earned,      setEarned]      = useState([]);
    const [loading,     setLoading]     = useState(true);
    const [downloading, setDownloading] = useState(null);
    const [error,       setError]       = useState(null);

    useEffect(() => {
        Promise.all([
            request(`${API_URL}v1/achievements/my-progress`, 'GET', null, headers()),
            request(`${API_URL}v1/achievements/my`, 'GET', null, headers()),
        ])
        .then(([progressData, myData]) => {
            console.log('=== my[0] FULL ===', JSON.stringify(myData[0]));
            setProgress(Array.isArray(progressData) ? progressData : []);
            setEarned(Array.isArray(myData) ? myData : []);
        })
        .catch(() => {})
        .finally(() => setLoading(false));
    }, []);

    // earnedMap по achievement_name → объект с course_id
    const earnedMap = new Map(earned.map(e => [e.achievement_name, e]));

    const handleDownload = async (item) => {
        if (!item.is_earned) return;

        const earnedItem = earnedMap.get(item.name);

        // Попробуй все возможные поля — уточни у бэкендщика какое именно
        const courseId = earnedItem?.course_id
            ?? earnedItem?.courseId
            ?? earnedItem?.course
            ?? item.course_id
            ?? null;

        console.log('earnedItem full:', JSON.stringify(earnedItem));
        console.log('courseId resolved:', courseId);

        if (!courseId) {
            setError('Не удалось определить курс. Проверь консоль → earnedItem full.');
            return;
        }

        setDownloading(item.achievement_id);
        setError(null);

        try {
            // check-and-earn на всякий случай (идемпотентный — безопасно вызывать повторно)
            await fetch(
                `${API_URL}v1/achievements/check-and-earn-certificate?course_id=${courseId}`,
                { method: 'POST', headers: headers() }
            ).catch(() => {}); // не блокируем скачивание если уже выдан

            // Скачиваем PDF
            const res = await fetch(
                `${API_URL}v1/achievements/course/${courseId}/download`,
                {
                    method: 'GET',
                    headers: { ...headers(), Accept: 'application/pdf' },
                }
            );

            console.log('=== download status ===', res.status);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const blob = await res.blob();
            const url  = URL.createObjectURL(blob);
            const a    = document.createElement('a');
            a.href     = url;
            a.download = `${item.name || 'certificate'}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);

        } catch (e) {
            console.error(e);
            setError('Не удалось скачать сертификат. Попробуйте позже.');
        } finally {
            setDownloading(null);
        }
    };

    const totalAll    = progress.length;
    const totalEarned = progress.filter(p => p.is_earned).length;

    if (loading) return (
        <div className="deg-loading">
            <div className="deg-spinner" />
            <p>Загрузка сертификатов...</p>
        </div>
    );

    return (
        <div className="deg-container">
            <div className="deg-header">
                <div>
                    <h2 className="deg-title">Мои Сертификаты</h2>
                    <p className="deg-sub">
                        Получено <b>{totalEarned}</b> из <b>{totalAll}</b> сертификатов
                    </p>
                </div>
                <div className="deg-progress-ring-wrap">
                    <svg width="64" height="64" viewBox="0 0 64 64">
                        <circle cx="32" cy="32" r="26" fill="none" stroke="rgba(108,92,231,0.12)" strokeWidth="6"/>
                        <circle cx="32" cy="32" r="26" fill="none"
                            stroke="url(#degGrad)" strokeWidth="6"
                            strokeDasharray={2 * Math.PI * 26}
                            strokeDashoffset={2 * Math.PI * 26 * (1 - (totalAll ? totalEarned / totalAll : 0))}
                            strokeLinecap="round"
                            style={{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%', transition: '1s ease' }}
                        />
                        <defs>
                            <linearGradient id="degGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stopColor="#6c5ce7"/>
                                <stop offset="100%" stopColor="#a29bfe"/>
                            </linearGradient>
                        </defs>
                        <text x="32" y="37" textAnchor="middle" fontSize="13" fontWeight="800" fill="#1a1a2e">
                            {totalAll ? Math.round(totalEarned / totalAll * 100) : 0}%
                        </text>
                    </svg>
                </div>
            </div>

            {error && (
                <div className="deg-error">
                    ⚠️ {error}
                </div>
            )}

            {progress.length === 0 ? (
                <div className="deg-empty">
                    <span>🎓</span>
                    <p>Пока нет доступных сертификатов</p>
                </div>
            ) : (
                <div className="deg-list">
                    {progress.map((item, i) => {
                        const isUnlocked = item.is_earned;
                        const pct        = Math.min(100, Math.round(item.progress ?? 0));
                        const earnedItem = earnedMap.get(item.name);

                        return (
                            <div
                                key={item.achievement_id}
                                className={`deg-card ${isUnlocked ? 'unlocked' : 'locked'}`}
                                style={{ animationDelay: `${i * 0.06}s` }}
                            >
                                <div className="deg-card-accent" />

                                <div className={`deg-icon-wrap ${isUnlocked ? '' : 'locked-icon'}`}>
                                    {isUnlocked
                                        ? (item.badge_image_url
                                            ? <img src={item.badge_image_url} alt="" />
                                            : <span>🏆</span>)
                                        : <span>🔒</span>
                                    }
                                </div>

                                <div className="deg-info">
                                    <div className="deg-name">{item.name}</div>
                                    <div className="deg-desc">{item.description}</div>
                                    <div className="deg-meta">
                                        <span className="deg-pts">+{item.points_reward} pts</span>

                                        {isUnlocked && earnedItem?.earned_at && (
                                            <span className="deg-date">
                                                Выдан: {new Date(earnedItem.earned_at).toLocaleDateString('ru-RU', {
                                                    day: '2-digit', month: 'long', year: 'numeric'
                                                })}
                                            </span>
                                        )}

                                        {!isUnlocked && (
                                            <span className="deg-locked-hint">
                                                Прогресс: {item.current_value} / {item.criteria_value}
                                            </span>
                                        )}
                                    </div>

                                    {!isUnlocked && (
                                        <div className="deg-progress-wrap">
                                            <div className="deg-progress-bar">
                                                <div
                                                    className="deg-progress-fill"
                                                    style={{ width: `${pct}%` }}
                                                />
                                            </div>
                                            <span className="deg-progress-label">{pct}%</span>
                                        </div>
                                    )}
                                </div>

                                <div className="deg-action">
                                    {isUnlocked ? (
                                        <>
                                            <div className="deg-certified-stamp">CERTIFIED</div>
                                            <button
                                                className={`deg-download-btn ${downloading === item.achievement_id ? 'loading' : ''}`}
                                                onClick={() => handleDownload(item)}
                                                disabled={downloading === item.achievement_id}
                                            >
                                                {downloading === item.achievement_id
                                                    ? <><span className="deg-btn-spin" /> Генерация...</>
                                                    : <>↓ Скачать PDF</>
                                                }
                                            </button>
                                        </>
                                    ) : (
                                        <div className="deg-lock-badge">
                                            {pct}% выполнено
                                        </div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default Degrees;