import { useState, useEffect } from 'react';
import './sidebar.css';
import { API_URL, useHttp, headers } from '../../api/search/base';
import { useTranslation } from '../../i18n/useTranslation';

function TeacherSidebar({ activeTab, setActiveTab, onLogout }) {
    const { request } = useHttp();
    const { t } = useTranslation();
    const [isOpen, setIsOpen] = useState(false);

    const teacherMenuItems = [
        { id: 'profile',       label: t('profile'),         icon: '👨‍🏫' },
        { id: 'review',        label: t('review'),  icon: '📥' },
        { id: 'students_list', label: t('my_students'),    icon: '👥' },
        { id: 'courses',       label: t('courses'),           icon: '📚' },
        { id: 'certificates',  label: t('certificates'),     icon: '🏅' },
        { id: 'statistics',    label: t('statistics'),      icon: '📈' },
    ];

    const handleTabClick = (id) => {
        setActiveTab(id);
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
                localStorage.removeItem('user');
                onLogout();
            });
    };

    return (
        <>
            <div className="sidebar-hamburger" onClick={() => setIsOpen(o => !o)}>
                <span style={{ transform: isOpen ? 'rotate(45deg) translate(5px, 5px)' : 'none' }}/>
                <span style={{ opacity: isOpen ? 0 : 1 }}/>
                <span style={{ transform: isOpen ? 'rotate(-45deg) translate(5px, -5px)' : 'none' }}/>
            </div>

            <div className={`sidebar-overlay ${isOpen ? 'open' : ''}`} onClick={() => setIsOpen(false)}/>

            <div className={`sidebar ${isOpen ? 'open' : ''}`}>
                <div className="sidebar-logo">
                    <h2>Gennis IT Platform</h2>
                </div>
                <nav className="sidebar-menu">
                    {teacherMenuItems.map(item => (
                        <div
                            key={item.id}
                            className={`menu-item ${activeTab === item.id ? 'active' : ''}`}
                            onClick={() => handleTabClick(item.id)}
                        >
                            <span className="icon">{item.icon}</span>
                            <span className="label">{item.label}</span>
                        </div>
                    ))}
                </nav>
                <button className="logout-btn-side" onClick={handleLogout}>
                    {t('logout_btn')} 🚪
                </button>
            </div>
        </>
    );
}

export default TeacherSidebar;