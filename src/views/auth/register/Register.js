import { useState } from 'react';
import './Register.css';
import { API_URL, useHttp } from '../../../api/search/base';

function Register({ onLogin, onGoLogin }) {
    const { request } = useHttp();

    const [form, setForm] = useState({
        name:            '',
        username:        '',
        email:           '',
        password:        '',
        confirmPassword: '',
    });
    const [errors,   setErrors]   = useState({});
    const [loading,  setLoading]  = useState(false);
    const [apiError, setApiError] = useState('');

    // Состояния для переключения видимости
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    const set = (key, value) => {
        setForm(f => ({ ...f, [key]: value }));
        setErrors(e => ({ ...e, [key]: '' }));
        setApiError('');
    };

    const validate = () => {
        const e = {};
        if (!form.name.trim())      e.name             = 'Введите имя';
        if (!form.username.trim()) e.username          = 'Введите логин';
        if (!form.email.trim())    e.email             = 'Введите email';
        else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'Неверный формат email';
        if (!form.password)        e.password          = 'Введите пароль';
        else if (form.password.length < 6) e.password = 'Минимум 6 символов';
        if (form.password !== form.confirmPassword) e.confirmPassword = 'Пароли не совпадают';
        setErrors(e);
        return Object.keys(e).length === 0;
    };

    const handleRegister = () => {
        if (!validate()) return;
        setLoading(true);
        setApiError('');

        request(`${API_URL}v1/auth/register`, 'POST', JSON.stringify({
            name:     form.name,
            username: form.username,
            email:    form.email,
            password: form.password,
        }))
            .then(res => {
                const token = res.access_token || res.token || res.access;
                if (token) localStorage.setItem('token', token);
                const userData = res.user || res;
                localStorage.setItem('user', JSON.stringify(userData));
                onLogin(res);
            })
            .catch(() => setApiError('Ошибка регистрации. Возможно, такой пользователь уже существует.'))
            .finally(() => setLoading(false));
    };

    const handleKeyDown = (e) => { if (e.key === 'Enter') handleRegister(); };

    return (
        <div className="register-card">
            <div className="logo-wrapper">
                <img src="https://play-lh.googleusercontent.com/xiJhv9DqAZaOq6htMaZSAQ5DBoH_v7fripUMYx04Kv-5iQnfWAFopqZIED6Sr7Q7wN0" alt="Gennis" />
            </div>

            <h1>Добро пожаловать!</h1>
            <p className="subtitle">Создайте новый аккаунт</p>

            <div className="register-field">
                <input type="text" placeholder="Имя" value={form.name}
                    onChange={e => set('name', e.target.value)} onKeyDown={handleKeyDown}
                    disabled={loading} className={errors.name ? 'input-error' : ''}
                    autoComplete="name"/>
                {errors.name && <span className="field-error">{errors.name}</span>}
            </div>

            <div className="register-field">
                <input type="text" placeholder="Логин" value={form.username}
                    onChange={e => set('username', e.target.value)} onKeyDown={handleKeyDown}
                    disabled={loading} className={errors.username ? 'input-error' : ''}
                    autoComplete="username"/>
                {errors.username && <span className="field-error">{errors.username}</span>}
            </div>

            <div className="register-field">
                <input type="email" placeholder="Email" value={form.email}
                    onChange={e => set('email', e.target.value)} onKeyDown={handleKeyDown}
                    disabled={loading} className={errors.email ? 'input-error' : ''}
                    autoComplete="email"/>
                {errors.email && <span className="field-error">{errors.email}</span>}
            </div>

            {/* Поле Пароля */}
            <div className="register-field password-field-wrapper">
                <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Пароль"
                    value={form.password}
                    onChange={e => set('password', e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={loading}
                    className={errors.password ? 'input-error' : ''}
                    autoComplete="new-password"
                />
                <span className="password-toggle-icon" onClick={() => setShowPassword(!showPassword)}>
                    <i className={showPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
                </span>
                {errors.password && <span className="field-error">{errors.password}</span>}
            </div>

            {/* Поле Подтверждения */}
            <div className="register-field password-field-wrapper">
                <input
                    type={showConfirmPassword ? "text" : "password"}
                    placeholder="Подтвердите пароль"
                    value={form.confirmPassword}
                    onChange={e => set('confirmPassword', e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={loading}
                    className={errors.confirmPassword ? 'input-error' : ''}
                    autoComplete="new-password"
                />
                <span className="password-toggle-icon" onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
                    <i className={showConfirmPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
                </span>
                {errors.confirmPassword && <span className="field-error">{errors.confirmPassword}</span>}
            </div>

            {apiError && <p className="register-api-error">{apiError}</p>}

            <button className="register-btn" onClick={handleRegister} disabled={loading}>
                {loading ? '⏳ Регистрация...' : 'Зарегистрироваться'}
            </button>

            {onGoLogin && (
                <div className="toggle-text" onClick={onGoLogin}>
                    Уже есть аккаунт? <span>Войти</span>
                </div>
            )}
        </div>
    );
}

export default Register;