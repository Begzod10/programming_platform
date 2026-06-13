import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './sidebar.css';
import { API_URL, useHttp, headers } from '../../api/search/base';
import { useTranslation } from '../../i18n/useTranslation';
import StreakBadge from './StreakBadge';

const COLLAPSED_KEY = 'sidebar:collapsed';

function ChevronIcon({ direction = 'left' }) {
    return (
        <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
                transform: direction === 'right' ? 'rotate(180deg)' : 'none',
                transition: 'transform 0.25s ease',
                width: '100%',
                height: '100%',
            }}
        >
            <polyline points="15 6 9 12 15 18" />
        </svg>
    );
}

function Sidebar({ activeTab, onLogout, role }) {
    const navigate = useNavigate();
    const { request } = useHttp();
    const { t, lang, toggleLang } = useTranslation();
    const [isOpen, setIsOpen] = useState(false);
    const [isCollapsed, setIsCollapsed] = useState(() => {
        try { return localStorage.getItem(COLLAPSED_KEY) === '1'; }
        catch { return false; }
    });

    // Force a remount of pages that fetched data before the toggle flipped
    // — the easiest way is to reload, since cached query state in many
    // pages is component-local. Cheap to do; the dev server / SW caches
    // bring the page back fast.
    const handleLangToggle = () => {
        toggleLang();
        // Defer reload until the languageChange event has dispatched and
        // localStorage is committed.
        setTimeout(() => { window.location.reload(); }, 30);
    };

    const menuItems = [
        { id: 'profile',        label: t('profile'),       icon: '👤',  section: 'main' },
        { id: 'projects',       label: t('my_projects'),   icon: '💻',  section: 'main' },
        { id: 'courses',        label: t('courses'),       icon: '📚',  section: 'main' },
        { id: 'dictionary',     label: t('dictionary'),    icon: '📖',  section: 'main' },
        { id: 'team-game',      label: t('team_game'),     icon: '🎮',  section: 'main' },
        { id: 'statistics',     label: t('statistics') || 'Статистика', icon: '📊',  section: 'insights' },
        { id: 'rankings',       label: t('rankings'),      icon: '🏆',  section: 'insights' },
        { id: 'project-rating', label: t('top_projects'),  icon: '🏗️', section: 'insights' },
        { id: 'degrees',        label: t('certificates'),  icon: '🎓',  section: 'achievements' },
    ];

    const sections = [
        { key: 'main',         title: t('section_learning') },
        { key: 'insights',     title: t('section_analytics') },
        { key: 'achievements', title: t('section_achievements') },
    ];

    const handleTabClick = (id) => {
        navigate(`/student/${id}`);
        setIsOpen(false);
    };

    const toggleCollapsed = () => {
        setIsCollapsed(prev => {
            const next = !prev;
            try { localStorage.setItem(COLLAPSED_KEY, next ? '1' : '0'); } catch {}
            return next;
        });
    };

    useEffect(() => {
        const onResize = () => { if (window.innerWidth > 600) setIsOpen(false); };
        window.addEventListener('resize', onResize);
        return () => window.removeEventListener('resize', onResize);
    }, []);

    const handleLogout = () => {
        request(`${API_URL}v1/auth/logout`, 'POST', JSON.stringify({}), headers())
            .catch(() => {})
            .finally(() => {
                localStorage.removeItem('token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('user');
                onLogout();
                navigate('/login');
            });
    };

    const sidebarClass = [
        'sidebar',
        isOpen ? 'open' : '',
        isCollapsed ? 'collapsed' : '',
    ].filter(Boolean).join(' ');

    return (
        <>
            <div className="sidebar-hamburger" onClick={() => setIsOpen(o => !o)}>
                <span style={{ transform: isOpen ? 'rotate(45deg) translate(5px, 5px)' : 'none' }} />
                <span style={{ opacity: isOpen ? 0 : 1 }} />
                <span style={{ transform: isOpen ? 'rotate(-45deg) translate(5px, -5px)' : 'none' }} />
            </div>
            <div className={`sidebar-overlay ${isOpen ? 'open' : ''}`} onClick={() => setIsOpen(false)} />
            <aside className={sidebarClass}>
                <button
                    type="button"
                    className="sidebar-toggle"
                    onClick={toggleCollapsed}
                    aria-label={isCollapsed ? 'Развернуть меню' : 'Свернуть меню'}
                    title={isCollapsed ? 'Развернуть' : 'Свернуть'}
                >
                    <ChevronIcon direction={isCollapsed ? 'right' : 'left'} />
                </button>

                <div className="sidebar-brand">
                    <div className="sidebar-brand__mark" aria-hidden="true">G</div>
                    <div className="sidebar-brand__text">
                        <span className="sidebar-brand__title">Gennis</span>
                        <span className="sidebar-brand__sub">IT Platform</span>
                    </div>
                </div>

                <StreakBadge collapsed={isCollapsed} />

                <nav className="sidebar-menu" aria-label="Главное меню">
                    {sections.map(sec => {
                        const items = menuItems.filter(m => m.section === sec.key);
                        if (items.length === 0) return null;
                        return (
                            <div key={sec.key} className="sidebar-section">
                                <div className="sidebar-section__label">{sec.title}</div>
                                <div className="sidebar-section__items">
                                    {items.map(item => {
                                        const isActive = activeTab === item.id;
                                        return (
                                            <button
                                                key={item.id}
                                                type="button"
                                                className={`menu-item ${isActive ? 'active' : ''}`}
                                                onClick={() => handleTabClick(item.id)}
                                                aria-current={isActive ? 'page' : undefined}
                                                title={isCollapsed ? item.label : undefined}
                                            >
                                                <span className="menu-item__rail" aria-hidden="true" />
                                                <span className="menu-item__icon" aria-hidden="true">{item.icon}</span>
                                                <span className="menu-item__label">{item.label}</span>
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>
                        );
                    })}
                </nav>

                <div className="sidebar-lang">
                    <button
                        type="button"
                        className={`sidebar-lang__pill ${lang === 'uz' ? 'is-active' : ''}`}
                        onClick={() => { if (lang !== 'uz') handleLangToggle(); }}
                        title="O'zbekcha"
                        aria-pressed={lang === 'uz'}
                    >
                        UZ
                    </button>
                    <button
                        type="button"
                        className={`sidebar-lang__pill ${lang === 'ru' ? 'is-active' : ''}`}
                        onClick={() => { if (lang !== 'ru') handleLangToggle(); }}
                        title="Русский"
                        aria-pressed={lang === 'ru'}
                    >
                        RU
                    </button>
                </div>

                <button
                    className="logout-btn-side"
                    onClick={handleLogout}
                    title={isCollapsed ? t('logout') : undefined}
                >
                    <span className="logout-btn-side__icon" aria-hidden="true">🚪</span>
                    <span className="logout-btn-side__label">{t('logout')}</span>
                </button>
            </aside>
        </>
    );
}

export default Sidebar;
