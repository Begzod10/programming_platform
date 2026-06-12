import { Outlet, useLocation } from 'react-router-dom';
import TeacherSidebar from '../components/sidebar/TeacherSidebar';
import { useAuth } from '../context/AuthContext';

const SCROLLABLE_SEGMENTS = ['students', 'review', 'statistics', 'courses', 'certificates', 'feedback'];

function TeacherLayout() {
    const { logout } = useAuth();
    const location = useLocation();

    // Определяем активный таб по URL: /teacher/courses/123 → 'courses'
    const segment = location.pathname.split('/')[2] || 'profile';

    const isScrollable = SCROLLABLE_SEGMENTS.includes(segment);

    return (
        <div className="main-layout">
            <TeacherSidebar activeTab={segment} onLogout={logout} />

            <main className="content-area">
                <div className={`page-container ${isScrollable ? 'scrollable' : ''}`}>
                    {/* Дочерний роут рендерится сюда */}
                    <Outlet />
                </div>
            </main>
        </div>
    );
}

export default TeacherLayout;