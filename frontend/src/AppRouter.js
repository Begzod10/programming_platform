import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './views/auth/login/Login';
import Register from './views/auth/register/Register';
import StudentLayout from './layouts/StudentLayout';
import TeacherLayout from './layouts/TeacherLayout';
import NotFound from './views/NotFound';

// ── Student views ──
import StudentCourses from './views/student/courses/Courses/StudentCourses';
import Profile        from './views/student/profile/Profile';
import MyProjects     from './views/student/projects/MyProjects';
import Leaderboard    from './views/student/rankings/LeaderBoard';
import Degrees        from './views/student/degrees/DegreeCard';
import Dictionary     from './views/student/dictionary/Dictionary';

// ── Teacher views ──
import TeacherCourses        from './views/teacher/courses/TeacherCourses/TeacherCourses';
import TeacherProfile        from './views/teacher/profile/TeacherProfile';
import TeacherReview         from './views/teacher/teacherreview/TeacherReview';
import MyStudents            from './views/teacher/mystudents/MyStudents';
import StudentProfilePage    from './views/teacher/mystudents/StudentProfile'; // ← NEW
import TeacherStatistics     from './views/teacher/statistics/TeacherStatistics';
import TeacherCertificates   from './views/teacher/TeacherCertificates/Teachercertificates';

/* ─── helpers ─── */
function RootRedirect() {
    const { user, isAuthenticated } = useAuth();
    if (!isAuthenticated) return <Navigate to="/login" replace />;
    return user?.role === 'teacher'
        ? <Navigate to="/teacher" replace />
        : <Navigate to="/student" replace />;
}

function LoginPage() {
    const { login, isAuthenticated, user } = useAuth();
    if (isAuthenticated) {
        return user?.role === 'teacher'
            ? <Navigate to="/teacher" replace />
            : <Navigate to="/student" replace />;
    }
    return <div className="app"><Login onLogin={login} /></div>;
}

function RegisterPage() {
    const { login, isAuthenticated, user } = useAuth();
    if (isAuthenticated) {
        return user?.role === 'teacher'
            ? <Navigate to="/teacher" replace />
            : <Navigate to="/student" replace />;
    }
    return <div className="app"><Register onLogin={login} /></div>;
}

function StudentProfilePageWrapper() {
    const { user, logout } = useAuth();
    return <Profile user={user} onLogout={logout} />;
}

function TeacherProfilePage() {
    const { user } = useAuth();
    return <TeacherProfile user={user} />;
}

function AppRouter() {
    return (
        <Routes>
            {/* Auth */}
            <Route path="/login"    element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* ══════════ STUDENT ══════════ */}
            <Route
                path="/student"
                element={
                    <ProtectedRoute requiredRole="student">
                        <StudentLayout />
                    </ProtectedRoute>
                }
            >
                <Route index                                              element={<Navigate to="profile" replace />} />
                <Route path="profile"                                     element={<StudentProfilePageWrapper />} />
                <Route path="projects"                                    element={<MyProjects />} />
                <Route path="rankings"                                    element={<Leaderboard />} />
                <Route path="degrees"                                     element={<Degrees />} />
                <Route path="dictionary"                                  element={<Dictionary />} />

                {/* Курсы */}
                <Route path="courses"                                     element={<StudentCourses />} />
                <Route path="courses/:courseId"                           element={<StudentCourses />} />
                <Route path="courses/:courseId/lessons/:lessonId"         element={<StudentCourses />} />
            </Route>

            {/* ══════════ TEACHER ══════════ */}
            <Route
                path="/teacher"
                element={
                    <ProtectedRoute requiredRole="teacher">
                        <TeacherLayout />
                    </ProtectedRoute>
                }
            >
                <Route index                                              element={<Navigate to="profile" replace />} />
                <Route path="profile"                                     element={<TeacherProfilePage />} />
                <Route path="review"                                      element={<TeacherReview />} />
                <Route path="students"                                    element={<MyStudents />} />
                <Route path="students/:studentId"                         element={<StudentProfilePage />} /> {/* ← NEW */}
                <Route path="certificates"                                element={<TeacherCertificates />} />
                <Route path="statistics"                                  element={<TeacherStatistics />} />

                <Route path="courses"                                     element={<TeacherCourses />} />
                <Route path="courses/:courseId"                           element={<TeacherCourses />} />
                <Route path="courses/:courseId/lessons/new"               element={<TeacherCourses />} />
                <Route path="courses/:courseId/lessons/:lessonId/edit"    element={<TeacherCourses />} />
                <Route path="courses/:courseId/lessons/:lessonId"         element={<TeacherCourses />} />
            </Route>

            <Route path="/" element={<RootRedirect />} />
            <Route path="*" element={<NotFound />} />
        </Routes>
    );
}

export default AppRouter;