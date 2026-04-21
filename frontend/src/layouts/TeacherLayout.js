import React from 'react';
import TeacherSidebar from '../components/sidebar/TeacherSidebar';
import TeacherProfile from '../views/teacher/profile/TeacherProfile';
import TeacherReview from '../views/teacher/teacherreview/TeacherReview';
import MyStudents from '../views/teacher/mystudents/MyStudents';
import MyGroups from '../views/teacher/mygroups/MyGroups';
import TeacherStatistics from '../views/teacher/statistics/TeacherStatistics';
import TeacherCourses from '../views/teacher/courses/TeacherCourses/TeacherCourses';
import TeacherCertificates from '../views/teacher/TeacherCertificates/Teachercertificates';

const SCROLLABLE_TABS = ['students_list', 'groups', 'review', 'statistics', 'courses', 'certificates'];

function TeacherLayout({ user, activeTab, setActiveTab, onLogout }) {
    const isScrollable = SCROLLABLE_TABS.includes(activeTab);

    return (
        <div className="main-layout">
            <TeacherSidebar
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                onLogout={onLogout}
            />
            <main className="content-area">
                <header className="main-header">
                    <h1>Добро пожаловать, {user.name || user.username}!</h1>
                </header>
                <div className={`page-container ${isScrollable ? 'scrollable' : ''}`}>
                    {activeTab === 'profile'       && <TeacherProfile user={user} />}
                    {activeTab === 'review'        && <TeacherReview />}
                    {activeTab === 'students_list' && <MyStudents />}
                    {activeTab === 'groups'        && <MyGroups />}
                    {activeTab === 'statistics'    && <TeacherStatistics />}
                    {activeTab === 'courses'       && <TeacherCourses />}
                    {activeTab === 'certificates'  && <TeacherCertificates />}
                </div>
            </main>
        </div>
    );
}

export default TeacherLayout;