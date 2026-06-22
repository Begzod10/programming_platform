import { useEffect, useState } from 'react';
import { API_URL, headers, useHttp } from '../../../api/search/base';
import './Achievements.css';
import { Trophy } from 'lucide-react';

const TABS = [
    { key: 'all',        label: 'Hammasi' },
    { key: 'learning',   label: "O'qish" },
    { key: 'projects',   label: 'Loyihalar' },
    { key: 'vocabulary', label: "Lug'at" },
    { key: 'points',     label: 'Ballar' },
];

function normaliseCategory(raw) {
    if (!raw) return 'general';
    return raw.toLowerCase();
}

function SkeletonCard() {
    return (
        <div className="ach-card ach-card--skeleton" aria-hidden="true">
            <div className="ach-skeleton-icon" />
            <div className="ach-skeleton-line ach-skeleton-line--title" />
            <div className="ach-skeleton-line ach-skeleton-line--desc" />
            <div className="ach-skeleton-line ach-skeleton-line--desc short" />
            <div className="ach-skeleton-bar" />
        </div>
    );
}

function AchievementCard({ item }) {
    const icon = item.icon || null;
    const category = normaliseCategory(item.category);
    const progress = Math.min(100, Math.max(0, item.progress ?? 0));

    return (
        <div className={`ach-card ${item.is_earned ? 'ach-card--earned' : 'ach-card--locked'}`}>
            {item.is_earned && (
                <span className="ach-check" title="Earned" aria-label="Earned">✓</span>
            )}

            <div className="ach-card-top">
                <span className={`ach-icon ${item.is_earned ? '' : 'ach-icon--locked'}`} role="img" aria-label={item.name}>
                    {icon ? icon : <Trophy size={20} />}
                </span>
                {item.is_earned && (
                    <span className="ach-pts">+{item.points_reward} pts</span>
                )}
            </div>

            <p className="ach-name">{item.name}</p>
            <p className="ach-desc">{item.description}</p>

            {!item.is_earned && (
                <div className="ach-progress-wrap" title={`${progress}%`}>
                    <div className="ach-progress-bar">
                        <div
                            className="ach-progress-fill"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                    <span className="ach-progress-label">{progress}%</span>
                </div>
            )}
        </div>
    );
}

function EmptyState({ activeTab }) {
    const tabLabel = TABS.find(t => t.key === activeTab)?.label ?? activeTab;
    return (
        <div className="ach-empty">
            <span className="ach-empty-icon">🎯</span>
            <p className="ach-empty-title">
                {activeTab === 'all'
                    ? 'Hali yutuqlar yo\'q'
                    : `"${tabLabel}" bo'yicha yutuqlar topilmadi`}
            </p>
            <p className="ach-empty-sub">Davom eting — mukofotlar yaqin!</p>
        </div>
    );
}

export default function Achievements() {
    const { request } = useHttp();
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('all');

    useEffect(() => {
        setLoading(true);
        setError(null);
        fetch(`${API_URL}v1/achievements/my-progress`, { headers: headers() })
            .then(r => {
                if (!r.ok) throw new Error(`HTTP ${r.status}`);
                return r.json();
            })
            .then(data => setItems(Array.isArray(data) ? data : []))
            .catch(e => setError(e.message))
            .finally(() => setLoading(false));
    }, []);

    const filtered = items.filter(item => {
        if (activeTab === 'all') return true;
        return normaliseCategory(item.category) === activeTab;
    });

    const earnedCount = items.filter(i => i.is_earned).length;
    const totalPoints = items.filter(i => i.is_earned).reduce((sum, i) => sum + (i.points_reward || 0), 0);

    return (
        <div className="ach-page">
            <header className="ach-header">
                <h1 className="ach-title">Yutuqlar</h1>
                <p className="ach-subtitle">
                    Jami <strong>{earnedCount}</strong> ta yutuq qo'lga kiritildi
                    {totalPoints > 0 && (
                        <span className="ach-total-pts"> · {totalPoints} ball</span>
                    )}
                </p>
            </header>

            <nav className="ach-tabs" role="tablist" aria-label="Achievement categories">
                {TABS.map(tab => (
                    <button
                        key={tab.key}
                        role="tab"
                        aria-selected={activeTab === tab.key}
                        className={`ach-tab ${activeTab === tab.key ? 'ach-tab--active' : ''}`}
                        onClick={() => setActiveTab(tab.key)}
                    >
                        {tab.label}
                    </button>
                ))}
            </nav>

            {error && (
                <div className="ach-error" role="alert">
                    Ma'lumotlarni yuklashda xatolik: {error}
                </div>
            )}

            {loading ? (
                <div className="ach-grid" aria-busy="true">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <SkeletonCard key={i} />
                    ))}
                </div>
            ) : filtered.length === 0 ? (
                <EmptyState activeTab={activeTab} />
            ) : (
                <div className="ach-grid" role="tabpanel">
                    {filtered.map(item => (
                        <AchievementCard key={item.achievement_id} item={item} />
                    ))}
                </div>
            )}
        </div>
    );
}
