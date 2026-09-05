import { useLocation } from 'react-router-dom';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/sidebar/sidebar';
import { useAuth } from '../context/AuthContext';

function StudentLayout() {
    const { logout } = useAuth();
    const location = useLocation();

    const path = location.pathname;
    const segment = path.split('/')[2] || 'dashboard';

    // The kids' early-learning game runs full-bleed with its own sky
    // backdrop — no sidebar, no glass-panel chrome. It provides its own
    // "Qaytish" exit button since there's no sidebar to navigate away from.
    if (segment === 'early-learning') {
        return <Outlet />;
    }

    return (
        <div className="main-layout">
            <Sidebar activeTab={segment} onLogout={logout} role="student" />

            <main className="content-area">
                <div className={`page-container ${segment === 'profile' ? '' : 'scrollable'}`}>
                    <Outlet />
                </div>
            </main>
        </div>
    );
}

export default StudentLayout;