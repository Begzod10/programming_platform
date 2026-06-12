import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './sidebar.css';
import { API_URL, useHttp, headers } from '../../api/search/base';

function Sidebar({ activeTab, onLogout, role }) {
    const navigate = useNavigate();
    const { request } = useHttp();
    const [isOpen, setIsOpen] = useState(false);

    const menuItems = [
        { id: 'profile',    label: 'Профиль',     icon: '👤', section: 'main' },
        { id: 'projects',   label: 'Мои Проекты', icon: '💻', section: 'main' },
        { id: 'courses',    label: 'Курсы',       icon: '📚', section: 'main' },
        { id: 'rankings',   label: 'Рейтинг',     icon: '🏆', section: 'main' },
        { id: 'degrees',    label: 'Сертификаты', icon: '🎓', section: 'achievements' },
        { id: 'dictionary', label: 'Словарь',     icon: '📖', section: 'achievements' },
    ];

    const sections = [
        { key: 'main',         title: 'Обучение' },
        { key: 'achievements', title: 'Достижения' },
    ];

    const handleTabClick = (id) => {
        navigate(`/student/${id}`);
        setIsOpen(false);
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

    return (
        <>
            <div className="sidebar-hamburger" onClick={() => setIsOpen(o => !o)}>
                <span style={{ transform: isOpen ? 'rotate(45deg) translate(5px, 5px)' : 'none' }} />
                <span style={{ opacity: isOpen ? 0 : 1 }} />
                <span style={{ transform: isOpen ? 'rotate(-45deg) translate(5px, -5px)' : 'none' }} />
            </div>
            <div className={`sidebar-overlay ${isOpen ? 'open' : ''}`} onClick={() => setIsOpen(false)} />
            <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
                <div className="sidebar-brand">
                    <div className="sidebar-brand__mark" aria-hidden="true">G</div>
                    <div className="sidebar-brand__text">
                        <span className="sidebar-brand__title">Gennis</span>
                        <span className="sidebar-brand__sub">IT Platform</span>
                    </div>
                </div>

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

                <button className="logout-btn-side" onClick={handleLogout}>
                    <span className="logout-btn-side__icon" aria-hidden="true">🚪</span>
                    <span className="logout-btn-side__label">Выйти</span>
                </button>
            </aside>
        </>
    );
}

export default Sidebar;
