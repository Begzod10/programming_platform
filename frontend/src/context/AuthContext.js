import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';

// Centralized auth context — manages user state, login, logout.
// Token presence is tracked in React state (not read from localStorage on
// every render), so isAuthenticated correctly re-computes when the token
// is cleared from another tab or by the Axios refresh-token interceptor.
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
    const [token, setToken] = useState(() => {
        try {
            return localStorage.getItem('token');
        } catch {
            return null;
        }
    });

    const isAuthenticated = useMemo(() => !!user && !!token, [user, token]);

    // ── Login: store tokens + user in localStorage and state ──
    const login = useCallback((response) => {
        const accessToken = response.access_token || response.token || response.access;
        const refreshToken = response.refresh_token;
        const userData = response.user || response;

        if (accessToken) localStorage.setItem('token', accessToken);
        if (refreshToken) localStorage.setItem('refresh_token', refreshToken);
        localStorage.setItem('user', JSON.stringify(userData));

        setUser(userData);
        setToken(accessToken || null);
    }, []);

    // ── Logout: clear all auth data ──
    const logout = useCallback(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        localStorage.removeItem('activeTab');
        setUser(null);
        setToken(null);
    }, []);

    // ── Listen for forced logout from Axios interceptor + cross-tab token changes ──
    useEffect(() => {
        const handleForceLogout = () => logout();
        const handleStorage = (e) => {
            if (e.key === 'token') setToken(e.newValue);
            if (e.key === 'user') {
                try {
                    setUser(e.newValue ? JSON.parse(e.newValue) : null);
                } catch {
                    setUser(null);
                }
            }
        };
        window.addEventListener('auth:logout', handleForceLogout);
        window.addEventListener('storage', handleStorage);
        return () => {
            window.removeEventListener('auth:logout', handleForceLogout);
            window.removeEventListener('storage', handleStorage);
        };
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
