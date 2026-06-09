import { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from '../components/sidebar/sidebar';
import StatsCard from '../views/student/stats/StatsCard';
import { useAuth } from '../context/AuthContext';
import { API_URL, useHttp, headers } from '../api/search/base';

// Tabs where the welcome banner + stats grid get out of the way so the
// page's own header can lead the eye. Match by prefix.
const NO_HEADER_PATHS = ['/student/courses', '/student/dictionary'];

function StudentLayout() {
    const { user, logout } = useAuth();
    const location = useLocation();
    const { request } = useHttp();
    const [stats, setStats] = useState({ points: null, rank: null, approved: null });

    // Определяем активный таб по URL
    const path = location.pathname; // например /student/courses/123/lessons/456
    const segment = path.split('/')[2] || 'profile'; // 'courses', 'projects', 'rankings' и т.д.

    const hideHeader = NO_HEADER_PATHS.some((p) => path.startsWith(p));

    useEffect(() => {
        Promise.all([
            request(`${API_URL}v1/rankings/my-stats`, 'GET', null, headers()).catch(() => null),
            request(`${API_URL}v1/rankings/me`, 'GET', null, headers()).catch(() => null),
        ]).then(([myStats, projects]) => {
            const points  = myStats?.total_points ?? '—';
            const rank    = (myStats?.global_rank && myStats.global_rank !== '-')
                ? myStats.global_rank : '—';
            const approved = myStats?.projects_completed ?? (
                Array.isArray(projects)
                    ? projects.filter(p => p.status === 'Approved').length
                    : '—'
            );
            setStats({ points, rank, approved });
        });
    }, []); // eslint-disable-line

    return (
        <div className="main-layout">
            <Sidebar activeTab={segment} onLogout={logout} role="student" />

            <main className="content-area">
                {!hideHeader && (
                    <>
                        <header className="main-header">
                            <h1>Добро пожаловать, {user?.name || user?.username}!</h1>
                        </header>
                        <section className="stats-grid">
                            <StatsCard
                                title="Баллы"
                                value={stats.points !== null ? stats.points : '...'}
                                icon="⭐" color="#ffcc00"
                            />
                            <StatsCard
                                title="Место"
                                value={stats.rank !== null ? `${stats.rank}` : '...'}
                                icon="🏆" color="#00c2ff"
                            />
                            <StatsCard
                                title="Проекты"
                                value={stats.approved !== null ? stats.approved : '...'}
                                icon="📁" color="#4caf50"
                            />
                        </section>
                    </>
                )}

                <div className={`page-container ${segment === 'profile' ? '' : 'scrollable'}`}>
                    {/* Дочерний роут рендерится сюда */}
                    <Outlet />
                </div>
            </main>
        </div>
    );
}

export default StudentLayout;