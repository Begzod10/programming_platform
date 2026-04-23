import React, { useState, useEffect } from 'react';
import './TeacherProfile.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';

function TeacherProfile({ user: initialUser }) {
    const { request } = useHttp();

    const [profile,  setProfile]  = useState(null);
    const [loading,  setLoading]  = useState(true);
    const [editMode,  setEditMode]  = useState(false);
    const [editClose, setEditClose] = useState(false);

    const closeEdit = () => {
        setEditClose(true);
        setTimeout(() => { setEditMode(false); setEditClose(false); setError(''); }, 280);
    };
    const [saving,   setSaving]   = useState(false);
    const [success,  setSuccess]  = useState('');
    const [error,    setError]    = useState('');

    const [form, setForm] = useState({
        full_name:  '',
        bio:        '',
        avatar_url: '',
    });

    /* ── Load profile ── */
    useEffect(() => {
        request(`${API_URL}v1/auth/me`, 'GET', null, headers())
            .then(data => {
                setProfile(data);
                setForm({
                    full_name:  data.full_name  || '',
                    bio:        data.bio        || '',
                    avatar_url: data.avatar_url || '',
                });
            })
            .catch(() => setProfile(initialUser))
            .finally(() => setLoading(false));
    }, []);

    /* ── Update ── */
    const handleUpdate = () => {
        setSaving(true);
        setError('');
        request(
            `${API_URL}v1/student/${profile.id}`,
            'PUT',
            JSON.stringify({ full_name: form.full_name, bio: form.bio, avatar_url: form.avatar_url }),
            headers()
        )
            .then(updated => {
                setProfile(p => ({ ...p, ...updated }));
                closeEdit();
                setSuccess('Профиль обновлён ✅');
                setTimeout(() => setSuccess(''), 3000);
            })
            .catch(() => setError('Ошибка при сохранении'))
            .finally(() => setSaving(false));
    };

    if (loading) {
        return (
            <div className="tp-loading">
                <div className="tp-spinner" />
                <p>Загрузка профиля...</p>
            </div>
        );
    }

    const displayName  = profile?.full_name || profile?.username || initialUser?.name || '—';
    const displayEmail = profile?.email     || initialUser?.email || '—';
    const displayBio   = profile?.bio       || '';
    const avatarUrl    = profile?.avatar_url || '';

    return (
        <div className="teacher-profile-container item-fade-in">

            {/* Header card */}
            <div className="tp-header-card">
                <div className="tp-avatar-box">
                    {avatarUrl
                        ? <img src={avatarUrl} alt="avatar" className="tp-avatar-img" />
                        : <span className="tp-emoji">👨‍🏫</span>
                    }
                    <div className="tp-status-online" />
                </div>
                <div className="tp-main-info">
                    <h2>{displayName}</h2>
                    <p className="tp-email">{displayEmail}</p>
                    {displayBio && <p className="tp-bio">{displayBio}</p>}
                    <div className="tp-tags">
                        <span className="tag-pro">Teacher</span>
                        <span className="tag-group">Mentor</span>
                        {profile?.is_active && <span className="tag-active">Активен</span>}
                    </div>
                </div>
                <button className="tp-edit-btn" onClick={() => { editMode ? closeEdit() : setEditMode(true); setError(''); }}>
                    {editMode ? '✕ Отмена' : '✏️ Редактировать'}
                </button>
            </div>

            {/* Success / Error */}
            {success && <div className="tp-success">{success}</div>}
            {error   && <div className="tp-error">{error}</div>}

            {/* Edit form */}
            {editMode && (
                <div className={`tp-edit-form ${editClose ? 'tp-edit-closing' : ''}`}>
                    <h3>Редактировать профиль</h3>
                    <div className="tp-edit-grid">
                        <div className="tp-field">
                            <label>Полное имя</label>
                            <input placeholder="Имя Фамилия" value={form.full_name}
                                onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))} />
                        </div>
                        <div className="tp-field">
                            <label>Ссылка на аватар</label>
                            <input placeholder="https://example.com/avatar.jpg" value={form.avatar_url}
                                onChange={e => setForm(f => ({ ...f, avatar_url: e.target.value }))} />
                        </div>
                        <div className="tp-field tp-field-full">
                            <label>О себе</label>
                            <textarea rows={3} placeholder="Расскажите о себе..." value={form.bio}
                                onChange={e => setForm(f => ({ ...f, bio: e.target.value }))} />
                        </div>
                    </div>
                    <div className="tp-edit-actions">
                        <button className="tp-cancel-btn" onClick={closeEdit}>Отмена</button>
                        <button className="tp-save-btn" onClick={handleUpdate} disabled={saving}>
                            {saving ? '⏳ Сохранение...' : '💾 Сохранить'}
                        </button>
                    </div>
                </div>
            )}

            {/* Stats grid */}
            <div className="tp-stats-grid">
                <div className="tp-stat-card">
                    <h3>{profile?.total_points ?? 0}</h3>
                    <p>Всего баллов</p>
                </div>
                <div className="tp-stat-card">
                    <h3>{profile?.current_level || '—'}</h3>
                    <p>Уровень</p>
                </div>
                <div className="tp-stat-card">
                    <h3>{profile?.created_at ? new Date(profile.created_at).getFullYear() : '—'}</h3>
                    <p>Год регистрации</p>
                </div>
            </div>

            {/* Info section */}
            <div className="tp-info-section">
                <h3>Информация</h3>
                <div className="tp-info-list">
                    <div className="tp-info-row">
                        <span className="tp-info-label">📧 Email</span>
                        <span className="tp-info-value">{displayEmail}</span>
                    </div>
                    <div className="tp-info-row">
                        <span className="tp-info-label">👤 Username</span>
                        <span className="tp-info-value">{profile?.username || '—'}</span>
                    </div>
                    <div className="tp-info-row">
                        <span className="tp-info-label">🎓 Роль</span>
                        <span className="tp-info-value">Teacher</span>
                    </div>
                    <div className="tp-info-row">
                        <span className="tp-info-label">📅 Зарегистрирован</span>
                        <span className="tp-info-value">
                            {profile?.created_at ? new Date(profile.created_at).toLocaleDateString('ru-RU') : '—'}
                        </span>
                    </div>
                    {displayBio && (
                        <div className="tp-info-row">
                            <span className="tp-info-label">📝 О себе</span>
                            <span className="tp-info-value">{displayBio}</span>
                        </div>
                    )}
                </div>
            </div>

        </div>
    );
}

export default TeacherProfile;