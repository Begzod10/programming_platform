import { useLocation } from 'react-router-dom';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/sidebar/sidebar';
import { useAuth } from '../context/AuthContext';

function StudentLayout() {
    const { logout } = useAuth();
    const location = useLocation();

    const path = location.pathname;
    const segment = path.split('/')[2] || 'profile';

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