import { useLocation } from 'react-router-dom';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/sidebar/sidebar';
import { useAuth } from '../context/AuthContext';

function StudentLayout() {
    const { logout, user } = useAuth();
    const location = useLocation();

    const path = location.pathname;
    const parts = path.split('/').filter(Boolean); // ['student', 'courses', ...]
    const segment = parts[1] || 'dashboard';
    // The whole courses area (list, detail, and the lesson page itself) is
    // full-bleed like the new home — no sidebar anywhere.
    const isCourseArea = segment === 'courses';

    // The kids' early-learning game runs full-bleed with its own sky
    // backdrop — no sidebar, no glass-panel chrome. It provides its own
    // "Qaytish" exit button since there's no sidebar to navigate away from.
    //
    // The main dashboard is the new "home" of the platform: it runs
    // full-bleed too, with navigation built into its own top bar (app
    // launcher + avatar menu) instead of a persistent sidebar.
    if (segment === 'early-learning' || segment === 'dashboard' || segment === 'profile'
        || segment === 'roadmap' || segment === 'projects' || segment === 'dictionary'
        || segment === 'statistics' || segment === 'notifications' || segment === 'rankings'
        || segment === 'project-rating' || segment === 'degrees' || segment === 'achievements'
        || segment === 'team-game' || segment === 'team-projects'
        || segment === 'quiz' || segment === 'duel' || isCourseArea) {
        return <Outlet />;
    }

    return (
        <div className="main-layout">
            <Sidebar activeTab={segment} onLogout={logout} role="student" earlyLearningEligible={user?.early_learning_eligible !== false} />

            <main className="content-area">
                <div className={`page-container ${segment === 'profile' ? '' : 'scrollable'}`}>
                    <Outlet />
                </div>
            </main>
        </div>
    );
}

export default StudentLayout;