import { createContext, useContext, useState, useEffect, useCallback } from 'react';

// [REFACTOR] Centralized auth context — manages user state, login, logout
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(() => {
        try {
            const saved = localStorage.getItem('user');
            return saved ? JSON.parse(saved) : null;
        } catch {
            return null;
        }
    });

    const isAuthenticated = !!user && !!localStorage.getItem('token');

    // ── Login: store tokens + user in localStorage and state ──
    const login = useCallback((response) => {
        const accessToken = response.access_token || response.token || response.access;
        const refreshToken = response.refresh_token;
        const userData = response.user || response;

        if (accessToken) localStorage.setItem('token', accessToken);
        if (refreshToken) localStorage.setItem('refresh_token', refreshToken);
        localStorage.setItem('user', JSON.stringify(userData));

        setUser(userData);
    }, []);

    // ── Logout: clear all auth data ──
    const logout = useCallback(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        localStorage.removeItem('activeTab');
        setUser(null);
    }, []);

    // ── Listen for forced logout from Axios interceptor ──
    useEffect(() => {
        const handleForceLogout = () => {
            logout();
        };
        window.addEventListener('auth:logout', handleForceLogout);
        return () => window.removeEventListener('auth:logout', handleForceLogout);
    }, [logout]);

    return (
        <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}

export default AuthContext;
