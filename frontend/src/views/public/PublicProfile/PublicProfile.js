import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { API_URL, resolveImageUrl } from '../../../api/search/base';
import './PublicProfile.css';
import { Flame, Trophy } from 'lucide-react';

const LEVEL_PALETTE = {
    Beginner:     { bg: 'rgba(108,92,231,0.16)', fg: '#6c5ce7', border: 'rgba(108,92,231,0.28)' },
    Intermediate: { bg: 'rgba(0,184,148,0.16)',  fg: '#00795b', border: 'rgba(0,184,148,0.28)' },
    Advanced:     { bg: 'rgba(248,113,113,0.16)',fg: '#a13030', border: 'rgba(248,113,113,0.28)' },
};

function initials(name) {
    if (!name) return '?';
    return name.split(/\s+/).map(w => w[0]).join('').slice(0, 2).toUpperCase();
}

function timeAgo(iso) {
    if (!iso) return '';
    const ms = Date.now() - new Date(iso).getTime();
    const day = 86400000;
    const days = Math.floor(ms / day);
    if (days < 1) return 'сегодня';
    if (days < 30) return `${days} дн назад`;
    const months = Math.floor(days / 30);
    if (months < 12) return `${months} мес назад`;
    const years = Math.floor(months / 12);
    return `${years} г назад`;
}

export default function PublicProfile() {
    const { username } = useParams();
    const navigate = useNavigate();
    const [data, setData]       = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError]     = useState('');
    const [copied, setCopied]   = useState(false);

    useEffect(() => {
        setLoading(true);
        setError('');
        fetch(`${API_URL}v1/student/public/${encodeURIComponent(username)}`)
            .then(async r => {
                if (!r.ok) throw new Error(r.status === 404 ? 'not_found' : 'fetch_failed');
                return r.json();
            })
            .then(setData)
            .catch(e => setError(e.message))
            .finally(() => setLoading(false));
    }, [username]);

    useEffect(() => {
        if (!data) return;
        const name = data.full_name || data.username;
        document.title = `${name} — Gennis IT Platform`;
    }, [data]);

    const shareUrl = typeof window !== 'undefined' ? window.location.href : '';

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(shareUrl);
            setCopied(true);
            setTimeout(() => setCopied(false), 1800);
        } catch {}
    };

    const handleTelegramShare = () => {
        if (!data) return;
        const name = data.full_name || data.username;
        const text = `${name} — ${data.total_points} ball, ${data.certificates.length} sertifikat. Gennis IT Platform`;
        const url  = `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(text)}`;
        window.open(url, '_blank', 'noopener,noreferrer');
    };

    if (loading) return (
        <div className="pp-shell pp-shell--state">
            <div className="pp-spinner" />
        </div>
    );

    if (error === 'not_found') return (
        <div className="pp-shell pp-shell--state">
            <div className="pp-empty">
                <div className="pp-empty__big">404</div>
                <div className="pp-empty__title">Студент не найден</div>
                <div className="pp-empty__sub">Профиль @{username} не существует или скрыт.</div>
                <button className="pp-cta pp-cta--ghost" onClick={() => navigate('/login')}>
                    На главную
                </button>
            </div>
        </div>
    );

    if (error) return (
        <div className="pp-shell pp-shell--state">
            <div className="pp-empty">
                <div className="pp-empty__title">Не удалось загрузить</div>
                <button className="pp-cta pp-cta--ghost" onClick={() => window.location.reload()}>
                    Попробовать снова
                </button>
            </div>
        </div>
    );

    const lvl = LEVEL_PALETTE[data.current_level] || LEVEL_PALETTE.Beginner;
    const name = data.full_name || data.username;

    return (
        <div className="pp-shell">
            {/* Soft ambient orbs anchored to the hero — pulled into the bg layer */}
            <div className="pp-bg" aria-hidden="true">
                <div className="pp-bg__orb pp-bg__orb--a" />
                <div className="pp-bg__orb pp-bg__orb--b" />
            </div>

            <header className="pp-topbar">
                <a href="/" className="pp-brand">
                    <span className="pp-brand__mark">G</span>
                    <span className="pp-brand__text">Gennis</span>
                </a>
                <div className="pp-topbar__cta">
                    <a className="pp-link" href="/login">Войти</a>
                    <a className="pp-link pp-link--filled" href="/register">Учиться бесплатно →</a>
                </div>
            </header>

            <section className="pp-hero">
                <div className="pp-hero__avatar">
                    {data.avatar_url
                        ? <img src={resolveImageUrl(data.avatar_url)} alt={name} />
                        : <span>{initials(name)}</span>
                    }
                    {data.current_streak > 0 && (
                        <div className="pp-streak-badge" title="Daily streak">
                            <span aria-hidden="true"><Flame size={14} /></span>{data.current_streak}
                        </div>
                    )}
                </div>

                <div className="pp-hero__body">
                    <div className="pp-hero__name-row">
                        <h1 className="pp-hero__name">{name}</h1>
                        <span
                            className="pp-hero__level"
                            style={{ background: lvl.bg, color: lvl.fg, borderColor: lvl.border }}
                        >
                            {data.current_level}
                        </span>
                    </div>
                    <div className="pp-hero__handle">@{data.username}</div>
                    <div className="pp-hero__joined">На платформе с {new Date(data.joined_at).toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' })}</div>

                    <div className="pp-hero__share">
                        <button className="pp-cta" onClick={handleCopy}>
                            {copied ? '✓ Скопировано' : '🔗 Скопировать ссылку'}
                        </button>
                        <button className="pp-cta pp-cta--ghost" onClick={handleTelegramShare}>
                            <span style={{ marginRight: 6 }}>✈</span> Поделиться в Telegram
                        </button>
                    </div>
                </div>

                <div className="pp-hero__stats">
                    <Stat label="Баллы"    value={data.total_points.toLocaleString()} accent="violet" />
                    <Stat label="Проекты"  value={data.projects_approved}              accent="green"  />
                    <Stat label="Сертиф."  value={data.certificates.length}            accent="gold"   />
                    <Stat label="Лучший streak" value={data.longest_streak}            accent="orange" />
                </div>
            </section>

            <section className="pp-section">
                <h2 className="pp-section__title">Сертификаты</h2>
                {data.certificates.length === 0 ? (
                    <div className="pp-empty-row">Пока нет завершённых курсов</div>
                ) : (
                    <div className="pp-cert-grid">
                        {data.certificates.map((c, i) => (
                            <div key={i} className="pp-cert">
                                <div className="pp-cert__ribbon">🎓</div>
                                <div className="pp-cert__title">{c.course_title}</div>
                                <div className="pp-cert__date">{timeAgo(c.issued_at)}</div>
                            </div>
                        ))}
                    </div>
                )}
            </section>

            <section className="pp-section">
                <h2 className="pp-section__title">Достижения</h2>
                {data.achievements.length === 0 ? (
                    <div className="pp-empty-row">Пока нет полученных значков</div>
                ) : (
                    <div className="pp-ach-grid">
                        {data.achievements.map((a, i) => (
                            <div key={i} className="pp-ach">
                                <div className="pp-ach__badge">
                                    {a.badge_image_url
                                        ? <img src={resolveImageUrl(a.badge_image_url)} alt="" />
                                        : <span aria-hidden="true"><Trophy size={20} /></span>
                                    }
                                </div>
                                <div className="pp-ach__body">
                                    <div className="pp-ach__name">{a.name}</div>
                                    {a.description && <div className="pp-ach__desc">{a.description}</div>}
                                    <div className="pp-ach__meta">
                                        <span className="pp-ach__pts">+{a.points_reward} pts</span>
                                        <span className="pp-ach__date">{timeAgo(a.earned_at)}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </section>

            <footer className="pp-footer">
                <span>Gennis IT Platform — учись программированию с нуля.</span>
                <a className="pp-footer__cta" href="/register">Начать свой путь →</a>
            </footer>
        </div>
    );
}

function Stat({ label, value, accent }) {
    return (
        <div className={`pp-stat pp-stat--${accent}`}>
            <div className="pp-stat__value">{value}</div>
            <div className="pp-stat__label">{label}</div>
        </div>
    );
}
