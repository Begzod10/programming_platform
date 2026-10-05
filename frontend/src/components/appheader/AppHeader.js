import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL, headers, resolveImageUrl, useHttp } from '../../api/search/base';
import { useTranslation } from '../../i18n/useTranslation';
import { useAuth } from '../../context/AuthContext';
import './AppHeader.css';
import {
    Bell, LayoutGrid, X, LogOut, User, BarChart3,
    LayoutDashboard, BookOpen, Map, Monitor, BookMarked, Gamepad2, Users2,
    HelpCircle, Zap, Puzzle, Trophy, Construction, GraduationCap, Award,
} from 'lucide-react';

const LEVEL_META = {
    Beginner:     { ru: 'Начинающий', uz: "Boshlang'ich" },
    Intermediate: { ru: 'Средний',    uz: "O'rta" },
    Advanced:     { ru: 'Продвинутый', uz: "Ilg'or" },
};

const NAV_GROUPS = (ru, earlyEligible) => [
    {
        title: ru ? 'Обучение' : "Ta'lim",
        items: [
            { id: 'dashboard',     Icon: LayoutDashboard, ru: 'Главная',         uz: 'Bosh sahifa' },
            { id: 'courses',       Icon: BookOpen,        ru: 'Курсы',           uz: 'Kurslar' },
            { id: 'roadmap',       Icon: Map,             ru: 'Дорожная карта',  uz: "Yo'l xaritasi" },
            { id: 'projects',      Icon: Monitor,         ru: 'Мои проекты',     uz: 'Mening loyihalarim' },
            { id: 'dictionary',    Icon: BookMarked,      ru: 'Словарь',         uz: "Lug'at" },
            { id: 'team-game',     Icon: Gamepad2,        ru: 'Командные игры',  uz: "Jamoa o'yinlari" },
            { id: 'team-projects', Icon: Users2,          ru: 'Команд. проекты', uz: 'Jamoaviy loyihalar' },
            { id: 'quiz',          Icon: HelpCircle,      ru: 'Викторина',       uz: 'Viktorina' },
            { id: 'duel',          Icon: Zap,             ru: '1 на 1',          uz: '1 vs 1 poyga' },
            ...(earlyEligible ? [{ id: 'early-learning', Icon: Puzzle, ru: 'Для малышей', uz: 'Kichkinalar uchun' }] : []),
        ],
    },
    {
        title: ru ? 'Аналитика' : 'Tahlil',
        items: [
            { id: 'statistics',     Icon: BarChart3,    ru: 'Статистика',  uz: 'Statistika' },
            { id: 'rankings',       Icon: Trophy,       ru: 'Рейтинг',     uz: 'Reyting' },
            { id: 'project-rating', Icon: Construction, ru: 'Топ проекты', uz: 'Top loyihalar' },
        ],
    },
    {
        title: ru ? 'Достижения' : 'Yutuqlar',
        items: [
            { id: 'degrees',      Icon: GraduationCap, ru: 'Сертификаты', uz: 'Sertifikatlar' },
            { id: 'achievements', Icon: Award,         ru: 'Достижения',  uz: 'Yutuqlar' },
        ],
    },
];

/**
 * Shared platform chrome — the dark sticky top bar with the app launcher
 * and avatar menu that replaced the sidebar. Used on every full-bleed
 * student page (dashboard, profile, …) so navigation stays consistent.
 */
export default function AppHeader({ me: meProp }) {
    const navigate = useNavigate();
    const { lang, toggleLang } = useTranslation();
    const { logout } = useAuth();
    const { request } = useHttp();
    const [menuOpen, setMenuOpen] = useState(false);
    const [avatarOpen, setAvatarOpen] = useState(false);
    const [meFetched, setMeFetched] = useState(null);
    const ru = lang === 'ru';

    // Notifications bell: live unread count. Seed instantly from the last
    // value the notifications page cached, then poll the lightweight
    // unread-count endpoint so the dot stays current on every page.
    const [unread, setUnread] = useState(() => {
        const v = typeof localStorage !== 'undefined' ? localStorage.getItem('notif:unread') : null;
        return v === null ? 0 : Number(v) || 0;
    });
    // Goes through useHttp (axios) like every other call, not a bare fetch():
    // the axios interceptor refreshes an expired token, fetch() would just 401.
    useEffect(() => {
        let alive = true;
        const poll = async () => {
            try {
                const d = await request(`${API_URL}v1/notifications/unread-count`, 'GET', null, headers());
                if (!alive || !d) return;
                const c = d.unread_count || 0;
                setUnread(c);
                try { localStorage.setItem('notif:unread', String(c)); } catch { /* ignore */ }
            } catch { /* ignore — the badge is cosmetic */ }
        };
        poll();
        const id = setInterval(poll, 25000);
        return () => { alive = false; clearInterval(id); };
    }, [request]);

    // Pages that don't already have the user object can let the header
    // fetch its own lightweight copy for the avatar / menu.
    useEffect(() => {
        if (meProp) return;
        let alive = true;
        (async () => {
            try {
                const d = await request(`${API_URL}v1/student/me`, 'GET', null, headers());
                if (alive) setMeFetched(d || null);
            } catch { /* ignore — falls back to initials */ }
        })();
        return () => { alive = false; };
    }, [meProp, request]);

    const me = meProp || meFetched;

    useEffect(() => {
        const onKey = (e) => { if (e.key === 'Escape') { setMenuOpen(false); setAvatarOpen(false); } };
        window.addEventListener('keydown', onKey);
        return () => window.removeEventListener('keydown', onKey);
    }, []);

    const go = (id) => { setMenuOpen(false); setAvatarOpen(false); navigate(`/student/${id}`); };
    const handleLogout = () => { setAvatarOpen(false); logout(); navigate('/login'); };

    const displayName = me?.full_name || me?.username || '';
    const firstName = (displayName || 'U').trim().split(/\s+/)[0];
    const avatarSrc = resolveImageUrl(me?.avatar_url);
    const earlyEligible = me?.early_learning_eligible !== false;
    const lvl = LEVEL_META[me?.current_level] || LEVEL_META.Beginner;
    const points = (me?.total_points || 0).toLocaleString('ru-RU').replace(/,/g, ' ');
    const navGroups = NAV_GROUPS(ru, earlyEligible);

    return (
        <>
            <div className="db-topbar">
                <button className="db-brand" onClick={() => go('dashboard')}>
                    <span className="db-logo">
                        <img src="https://play-lh.googleusercontent.com/xiJhv9DqAZaOq6htMaZSAQ5DBoH_v7fripUMYx04Kv-5iQnfWAFopqZIED6Sr7Q7wN0" alt="GENNIS" />
                    </span>
                    <span className="db-brand-name">GENNIS <span>IT Platform</span></span>
                </button>
                <div className="db-topbar-actions">
                    <div className="db-lang" role="group" aria-label="Til / Язык">
                        <button type="button" className={`db-lang-btn ${!ru ? 'db-lang-btn--active' : ''}`}
                            aria-pressed={!ru} onClick={() => { if (ru) toggleLang(); }}>UZ</button>
                        <button type="button" className={`db-lang-btn ${ru ? 'db-lang-btn--active' : ''}`}
                            aria-pressed={ru} onClick={() => { if (!ru) toggleLang(); }}>RU</button>
                    </div>
                    <div className="db-menu-anchor">
                        <button className={`db-ticon ${menuOpen ? 'active' : ''}`} aria-label={ru ? 'Меню' : 'Menyu'}
                            aria-expanded={menuOpen} onClick={() => { setMenuOpen(o => !o); setAvatarOpen(false); }}>
                            <LayoutGrid size={20} />
                        </button>
                        {menuOpen && (
                            <div className="db-launcher" role="menu">
                                <div className="db-launcher-head">
                                    <span>{ru ? 'Навигация' : 'Navigatsiya'}</span>
                                    <button className="db-launcher-x" onClick={() => setMenuOpen(false)} aria-label="Close"><X size={16} /></button>
                                </div>
                                {navGroups.map(group => (
                                    <div className="db-launcher-group" key={group.title}>
                                        <div className="db-launcher-title">{group.title}</div>
                                        <div className="db-launcher-grid">
                                            {group.items.map(item => (
                                                <button key={item.id} className="db-launcher-item" role="menuitem" onClick={() => go(item.id)}>
                                                    <span className="db-launcher-ico"><item.Icon size={18} /></span>
                                                    <span className="db-launcher-lbl">{ru ? item.ru : item.uz}</span>
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                    <button className="db-ticon" aria-label={ru ? 'Уведомления' : 'Bildirishnomalar'}
                        onClick={() => go('notifications')}>
                        <Bell size={20} />
                        {unread > 0 && <span className="db-badge">{unread > 9 ? '9+' : unread}</span>}
                    </button>
                    <div className="db-menu-anchor">
                        <button className="db-avatar" onClick={() => { setAvatarOpen(o => !o); setMenuOpen(false); }} aria-label="Profile">
                            {avatarSrc ? <img src={avatarSrc} alt="" /> : (firstName[0] || 'U').toUpperCase()}
                        </button>
                        {avatarOpen && (
                            <div className="db-avatar-menu" role="menu">
                                <div className="db-avatar-head">
                                    <div className="db-avatar-name">{displayName}</div>
                                    <div className="db-avatar-sub">{ru ? lvl.ru : lvl.uz} · ★ {points}</div>
                                </div>
                                <button className="db-avatar-mi" onClick={() => go('profile')}><User size={16} /> {ru ? 'Профиль' : 'Profil'}</button>
                                <button className="db-avatar-mi" onClick={() => go('statistics')}><BarChart3 size={16} /> {ru ? 'Статистика' : 'Statistika'}</button>
                                <button className="db-avatar-mi db-avatar-mi--danger" onClick={handleLogout}><LogOut size={16} /> {ru ? 'Выйти' : 'Chiqish'}</button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {(menuOpen || avatarOpen) && (
                <div className="db-backdrop" onClick={() => { setMenuOpen(false); setAvatarOpen(false); }} />
            )}
        </>
    );
}
