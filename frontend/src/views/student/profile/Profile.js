import { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import './Profile.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';

function Profile({ user: initialUser, onLogout }) {
    const { request } = useHttp();

    const [profile,     setProfile]     = useState(null);
    const [loading,     setLoading]     = useState(true);
    const [editMode,    setEditMode]    = useState(false);
    const [deleteModal, setDeleteModal] = useState(false);
    const [saving,      setSaving]      = useState(false);
    const [deleting,    setDeleting]    = useState(false);
    const [error,       setError]       = useState('');
    const [success,     setSuccess]     = useState('');

    const [form, setForm] = useState({
        full_name:  '',
        bio:        '',
        avatar_url: '',
    });

    useEffect(() => {
        request(`${API_URL}v1/student/me`, 'GET', null, headers())
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
                setEditMode(false);
                setSuccess('Профиль обновлён ✅');
                setTimeout(() => setSuccess(''), 3000);
            })
            .catch(() => setError('Ошибка при сохранении'))
            .finally(() => setSaving(false));
    };

    const handleDelete = () => {
        setDeleting(true);
        request(`${API_URL}v1/auth/me`, 'DELETE', null, headers())
            .then(() => {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                onLogout && onLogout();
            })
            .catch(() => setError('Ошибка при удалении'))
            .finally(() => setDeleting(false));
    };

    if (loading) {
        return (
            <div className="profile-loading">
                <div className="profile-spinner" />
                <p>Загрузка профиля...</p>
            </div>
        );
    }

    const displayName   = profile?.full_name || profile?.username || '—';
    const displayEmail  = profile?.email || '—';
    const displayLevel  = profile?.current_level || 'Beginner';
    const displayPoints = profile?.total_points ?? 0;
    const displayBio    = profile?.bio || '';

    return (
        <div className="profile-full-view item-fade-in">
            <div className="profile-main-card">

                {/* Aside */}
                <div className="profile-aside">
                    <div className="insta-avatar-large fade-in">
                        {profile?.avatar_url
                            ? <img src={profile.avatar_url} alt="avatar" className="profile-avatar-img"/>
                            : '👤'}
                        <div className="level-badge">{displayLevel}</div>
                    </div>
                    <h2 className="profile-name">{displayName}</h2>
                    <p className="profile-email">{displayEmail}</p>
                    {displayBio && <p className="profile-bio">{displayBio}</p>}

                    <div className="profile-aside-actions">
                        <button className="edit-profile-btn"
                            onClick={() => { setEditMode(true); setError(''); }}>
                            ✏️ Редактировать
                        </button>
                        <button className="delete-profile-btn"
                            onClick={() => setDeleteModal(true)}>
                            🗑️ Удалить аккаунт
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="profile-content-rich fade-in">
                    {success && <div className="profile-success">{success}</div>}
                    {error   && <div className="profile-error">{error}</div>}

                    {editMode ? (
                        <div className="profile-edit-form">
                            <div className="profile-section-title">Редактировать профиль</div>
                            <div className="profile-edit-grid">
                                <div className="profile-field">
                                    <label>Полное имя</label>
                                    <input value={form.full_name} placeholder="Имя Фамилия"
                                        onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))}/>
                                </div>
                                <div className="profile-field">
                                    <label>Ссылка на аватар</label>
                                    <input value={form.avatar_url} placeholder="https://..."
                                        onChange={e => setForm(f => ({ ...f, avatar_url: e.target.value }))}/>
                                </div>
                                <div className="profile-field" style={{ gridColumn: '1 / -1' }}>
                                    <label>О себе</label>
                                    <textarea value={form.bio} rows={3} placeholder="Расскажите о себе..."
                                        onChange={e => setForm(f => ({ ...f, bio: e.target.value }))}/>
                                </div>
                            </div>
                            <div className="profile-edit-actions">
                                <button className="profile-cancel-btn"
                                    onClick={() => { setEditMode(false); setError(''); }}>
                                    Отмена
                                </button>
                                <button className="profile-save-btn" onClick={handleUpdate} disabled={saving}>
                                    {saving ? '⏳ Сохранение...' : '💾 Сохранить'}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <>
                            <div className="profile-section-title">Ваш прогресс</div>
                            <div className="progress-container">
                                <div className="progress-info">
                                    <span>Уровень: <strong>{displayLevel}</strong></span>
                                    <span>{displayPoints} очков</span>
                                </div>
                                <div className="progress-bar-bg">
                                    <div className="progress-bar-fill"
                                        style={{ width: `${Math.min((displayPoints / 1000) * 100, 100)}%` }}/>
                                </div>
                            </div>

                            <div className="stats-mini-grid">
                                <div className="mini-stat">
                                    <span className="stat-label">Username</span>
                                    <span className="stat-value">{profile?.username || '—'}</span>
                                </div>
                                <div className="mini-stat">
                                    <span className="stat-label">Очки</span>
                                    <span className="stat-value">{displayPoints} 🔥</span>
                                </div>
                                <div className="mini-stat">
                                    <span className="stat-label">Статус</span>
                                    <span className="stat-value">{profile?.is_active ? '✅ Активен' : '❌'}</span>
                                </div>
                            </div>

                            <div className="recent-activity">
                                <div className="profile-section-title">Информация</div>
                                <ul className="activity-list">
                                    <li><span>📧</span> Email: <strong>{displayEmail}</strong></li>
                                    <li><span>🎓</span> Уровень: <strong>{displayLevel}</strong></li>
                                    {displayBio && <li><span>📝</span> О себе: <strong>{displayBio}</strong></li>}
                                    <li><span>📅</span> Зарегистрирован: <strong>
                                        {profile?.created_at
                                            ? new Date(profile.created_at).toLocaleDateString('ru-RU')
                                            : '—'}
                                    </strong></li>
                                </ul>
                            </div>
                        </>
                    )}
                </div>
            </div>

            {/* ✅ PORTAL — рендерится прямо в document.body, поверх всего */}
            {deleteModal && ReactDOM.createPortal(
                <div className="profile-overlay" onClick={() => setDeleteModal(false)}>
                    <div className="profile-confirm" onClick={e => e.stopPropagation()}>
                        <span className="profile-confirm-icon">⚠️</span>
                        <h4>Удалить аккаунт?</h4>
                        <p>Это действие нельзя отменить. Все данные будут удалены.</p>
                        <div className="profile-confirm-actions">
                            <button className="profile-cancel-btn" onClick={() => setDeleteModal(false)}>
                                Отмена
                            </button>
                            <button className="profile-delete-btn" onClick={handleDelete} disabled={deleting}>
                                {deleting ? '⏳ Удаление...' : '🗑️ Удалить'}
                            </button>
                        </div>
                    </div>
                </div>,
                document.body
            )}
        </div>
    );
}

export default Profile;