import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// [REFACTOR] Route guard — redirects to /login if not authenticated, or to correct dashboard if wrong role
function ProtectedRoute({ children, requiredRole }) {
    const { user, isAuthenticated } = useAuth();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    // If a specific role is required and user has a different role, redirect to their dashboard
    if (requiredRole && user?.role !== requiredRole) {
        const redirectPath = user?.role === 'teacher' ? '/teacher' : '/student';
        return <Navigate to={redirectPath} replace />;
    }

    return children;
}

export default ProtectedRoute;
