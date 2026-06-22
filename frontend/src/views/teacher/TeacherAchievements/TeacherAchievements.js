import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL, useHttp, headers, resolveImageUrl } from '../../../api/search/base';
import './TeacherAchievements.css';

const CATEGORIES = [
    { value: '',           label: 'Barcha' },
    { value: 'learning',   label: '📖 O\'qish' },
    { value: 'projects',   label: '🚀 Loyihalar' },
    { value: 'vocabulary', label: '📝 Lug\'at' },
    { value: 'points',     label: '⭐ Ball' },
];

const AchievementPill = ({ a }) => (
    <span className="ta-pill" title={`${a.name} — ${a.earned_at ? new Date(a.earned_at).toLocaleDateString('uz-UZ') : ''}`}>
        <span className="ta-pill-icon">{a.icon || '🏆'}</span>
        <span className="ta-pill-name">{a.name}</span>
    </span>
);

const StudentRow = ({ s, navigate }) => {
    const initials = (s.full_name || s.username || '?')
        .split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();

    return (
        <div className="ta-row" onClick={() => navigate(`/teacher/students/${s.student_id}`)}>
            <div className="ta-row-left">
                {s.avatar_url
                    ? <img src={resolveImageUrl(s.avatar_url)} alt={s.username} className="ta-avatar" />
                    : <div className="ta-avatar ta-avatar-init">{initials}</div>
                }
                <div className="ta-info">
                    <span className="ta-name">{s.full_name || s.username}</span>
                    <span className="ta-username">@{s.username}</span>
                </div>
            </div>

            <div className="ta-row-mid">
                {s.achievements.length === 0
                    ? <span className="ta-empty-badges">Yutuq yo'q</span>
                    : s.achievements.map((a, i) => <AchievementPill key={i} a={a} />)
                }
            </div>

            <div className="ta-row-right">
                <span className="ta-count">{s.achievement_count}</span>
                <span className="ta-pts">{s.total_points.toLocaleString()} ball</span>
            </div>
        </div>
    );
};

const TeacherAchievements = () => {
    const { request } = useHttp();
    const navigate = useNavigate();

    const [data,     setData]     = useState([]);
    const [loading,  setLoading]  = useState(true);
    const [search,   setSearch]   = useState('');
    const [category, setCategory] = useState('');

    const load = useCallback(async () => {
        setLoading(true);
        try {
            const res = await request(
                `${API_URL}v1/teacher/students/achievements/overview`,
                'GET', null, headers()
            );
            setData(res || []);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    }, [request]);

    useEffect(() => { load(); }, [load]);

    const filtered = data.filter(s => {
        const matchSearch = !search ||
            s.username.toLowerCase().includes(search.toLowerCase()) ||
            (s.full_name || '').toLowerCase().includes(search.toLowerCase());
        const matchCat = !category ||
            s.achievements.some(a => a.category === category);
        return matchSearch && matchCat;
    });

    const totalStudentsWithAny = data.filter(s => s.achievement_count > 0).length;
    const totalAwarded = data.reduce((sum, s) => sum + s.achievement_count, 0);

    return (
        <div className="ta-page">
            <div className="ta-header">
                <div className="ta-title-row">
                    <h1 className="ta-title">🏅 Yutuqlar</h1>
                    <div className="ta-stats-row">
                        <div className="ta-stat">
                            <span className="ta-stat-val">{data.length}</span>
                            <span className="ta-stat-lbl">student</span>
                        </div>
                        <div className="ta-stat">
                            <span className="ta-stat-val">{totalStudentsWithAny}</span>
                            <span className="ta-stat-lbl">yutuq olgan</span>
                        </div>
                        <div className="ta-stat">
                            <span className="ta-stat-val">{totalAwarded}</span>
                            <span className="ta-stat-lbl">jami berilgan</span>
                        </div>
                    </div>
                </div>

                <div className="ta-filters">
                    <input
                        className="ta-search"
                        placeholder="Student qidirish..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                    />
                    <div className="ta-cat-tabs">
                        {CATEGORIES.map(c => (
                            <button
                                key={c.value}
                                className={`ta-cat-btn ${category === c.value ? 'active' : ''}`}
                                onClick={() => setCategory(c.value)}
                            >
                                {c.label}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {loading ? (
                <div className="ta-loading">Yuklanmoqda...</div>
            ) : filtered.length === 0 ? (
                <div className="ta-empty">
                    <span>🏅</span>
                    <p>{search || category ? 'Hech narsa topilmadi' : 'Hali yutuq berilmagan'}</p>
                </div>
            ) : (
                <div className="ta-table">
                    <div className="ta-thead">
                        <span>Student</span>
                        <span>Yutuqlar</span>
                        <span>Jami</span>
                    </div>
                    <div className="ta-tbody">
                        {filtered.map(s => (
                            <StudentRow key={s.student_id} s={s} navigate={navigate} />
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default TeacherAchievements;
