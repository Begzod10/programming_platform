import { useState } from 'react';
import './Login.css';
import { API_URL, useHttp } from '../../../api/search/base';

function Login({ onLogin, onGoRegister }) {
    const { request } = useHttp();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error,    setError]    = useState('');
    const [loading,  setLoading]  = useState(false);

    // Состояние для видимости пароля
    const [showPassword, setShowPassword] = useState(false);

    const handleLogin = () => {
        if (!username.trim() || !password.trim()) {
            setError('Введите логин и пароль');
            return;
        }
        setError('');
        setLoading(true);
        request(`${API_URL}v1/auth/login`, 'POST', JSON.stringify({ username, password }))
            .then(res => {
                const token = res.access_token || res.token || res.access;
                if (token) localStorage.setItem('token', token);
                const userData = res.user || res;
                localStorage.setItem('user', JSON.stringify(userData));
                onLogin(res);
            })
            .catch(() => setError('Неверный логин или пароль'))
            .finally(() => setLoading(false));
    };

    const handleKeyDown = (e) => { if (e.key === 'Enter') handleLogin(); };

    return (
        <div className="login-card">
            <div className="logo-wrapper">
                <img
                    src="https://play-lh.googleusercontent.com/xiJhv9DqAZaOq6htMaZSAQ5DBoH_v7fripUMYx04Kv-5iQnfWAFopqZIED6Sr7Q7wN0"
                    alt="Gennis"
                />
            </div>

            <h1>Добро пожаловать!</h1>
            <p className="subtitle">Войдите в свой аккаунт</p>

            <div className="login-field">
                <input
                    type="text"
                    placeholder="Логин"
                    value={username}
                    onChange={e => { setUsername(e.target.value); setError(''); }}
                    onKeyDown={handleKeyDown}
                    disabled={loading}
                    autoComplete="username"
                />
            </div>

            <div className="login-field password-field-wrapper">
                <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Пароль"
                    value={password}
                    onChange={e => { setPassword(e.target.value); setError(''); }}
                    onKeyDown={handleKeyDown}
                    disabled={loading}
                    autoComplete="current-password"
                />
                <span className="password-toggle-icon" onClick={() => setShowPassword(!showPassword)}>
                    <i className={showPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
                </span>
            </div>

            {error && <p className="login-error">{error}</p>}

            <button className="login-btn" onClick={handleLogin} disabled={loading}>
                {loading ? '⏳ Вход...' : 'Войти'}
            </button>

            {onGoRegister && (
                <>
                    <div className="login-divider">или</div>
                    <div className="toggle-text" onClick={onGoRegister}>
                        Нет аккаунта? <span>Зарегистрироваться</span>
                    </div>
                </>
            )}
        </div>
    );
}

export default Login;