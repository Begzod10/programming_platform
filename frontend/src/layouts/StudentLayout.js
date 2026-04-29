import {useState, useEffect} from 'react';
import Sidebar from '../components/sidebar/sidebar';
import { useTranslation } from '../i18n/useTranslation';
import StatsCard from '../views/student/stats/StatsCard';
import MyProjects from '../views/student/projects/MyProjects';
import Leaderboard from '../views/student/rankings/LeaderBoard';
import Degrees from '../views/student/degrees/DegreeCard';
import Profile from '../views/student/profile/Profile';
import StudentCourses from '../views/student/courses/Courses/StudentCourses';
import {API_URL, useHttp, headers} from '../api/search/base';

function StudentLayout({user, activeTab, setActiveTab, onLogout}) {
    const {request} = useHttp();
    const { t } = useTranslation();
    const [stats, setStats] = useState({points: null, rank: null, approved: null});

    useEffect(() => {
        Promise.all([
            request(`${API_URL}v1/rankings/my-stats`, 'GET', null, headers()).catch(() => null),
            request(`${API_URL}v1/rankings/me`, 'GET', null, headers()).catch(() => null),
        ]).then(([myStats, projects]) => {
            const points = myStats?.total_points ?? '—';
            const rank = (myStats?.global_rank && myStats.global_rank !== '-')
                ? myStats.global_rank
                : '—';
            const approved = myStats?.projects_completed ?? (
                Array.isArray(projects)
                    ? projects.filter(p => p.status === 'Approved').length
                    : '—'
            );
            setStats({points, rank, approved});
        });
    }, []);

    return (
        <div className="main-layout">
            <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} onLogout={onLogout} role="student"/>
            <main className="content-area">
                <header className="main-header">
                    <h1>{t('welcome')} {user.name || user.username}!</h1>
                </header>
                {activeTab !== 'courses' && (
                    <section className="stats-grid">
                        <StatsCard
                            title={t('points')}
                            value={stats.points !== null ? stats.points : '...'}
                            icon="⭐" color="#ffcc00"
                        />
                        <StatsCard
                            title={t('my_rank')}
                            value={stats.rank !== null ? `${stats.rank}` : '...'}
                            icon="🏆" color="#00c2ff"
                        />
                        <StatsCard
                            title={t('my_projects')}
                            value={stats.approved !== null ? stats.approved : '...'}
                            icon="📁" color="#4caf50"
                        />
                    </section>
                )}
                <div className={`page-container ${activeTab === 'profile' ? '' : 'scrollable'}`}>
                    {activeTab === 'profile' && <Profile user={user} onLogout={onLogout}/>}
                    {activeTab === 'projects' && <MyProjects/>}
                    {activeTab === 'courses' && <StudentCourses/>}
                    {activeTab === 'rankings' && <div className="item-fade-in"><Leaderboard/></div>}
                    {activeTab === 'degrees' && <Degrees/>}
                </div>
            </main>
        </div>
    );
}

export default StudentLayout;