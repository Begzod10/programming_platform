import { Navigate, useLocation } from 'react-router-dom';
import { DEMO_HOME } from '../constants/demo';
import { useAuth } from '../context/AuthContext';

// [REFACTOR] Route guard — redirects to /login if not authenticated, or to correct dashboard if wrong role
function ProtectedRoute({ children, requiredRole }) {
    const { user, isAuthenticated } = useAuth();
    const location = useLocation();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    // If a specific role is required and user has a different role, redirect to their dashboard
    if (requiredRole && user?.role !== requiredRole) {
        const redirectPath = user?.role === 'teacher' ? '/teacher' : '/student';
        return <Navigate to={redirectPath} replace />;
    }

    // A demo visitor may only use the course pages; everything else sends them back.
    if (user?.is_demo && requiredRole === 'student' && !location.pathname.startsWith('/student/courses')) {
        return <Navigate to={DEMO_HOME} replace />;
    }

    return children;
}

export default ProtectedRoute;
