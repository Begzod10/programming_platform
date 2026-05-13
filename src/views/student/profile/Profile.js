import { useState, useEffect } from 'react';
import './Profile.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';

function Profile({ user: initialUser, onLogout }) {
    const { request } = useHttp();
    const { t, lang, toggleLang } = useTranslation();

    const [profile,     setProfile]     = useState(null);
    const [loading,     setLoading]     = useState(true);
    const [editMode,    setEditMode]    = useState(false);
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
                setSuccess(t('profile_updated'));
                setTimeout(() => setSuccess(''), 3000);
            })
            .catch(() => setError(t('save_error')))
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
            .catch(() => setError('O\'chirishda xatolik'))
            .finally(() => setDeleting(false));
    };

    if (loading) {
        return (
            <div className="profile-loading">
                <div className="profile-spinner" />
                <p>{t('loading')}</p>
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
                            ✏️ {t('edit')}
                        </button>
                        <button className="lang-toggle-btn" onClick={toggleLang}>
                            🌐 {lang === 'uz' ? 'Русский' : "O'zbekcha"}
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="profile-content-rich fade-in">
                    {success && <div className="profile-success">{success}</div>}
                    {error   && <div className="profile-error">{error}</div>}

                    {editMode ? (
                        <div className="profile-edit-form">
                            <div className="profile-section-title">{t('edit_profile')}</div>
                            <div className="profile-edit-grid">
                                <div className="profile-field">
                                    <label>{t('full_name')}</label>
                                    <input value={form.full_name} placeholder="Ism Familiya"
                                        onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))}/>
                                </div>
                                <div className="profile-field">
                                    <label>{t('avatar_url')}</label>
                                    <input value={form.avatar_url} placeholder="https://..."
                                        onChange={e => setForm(f => ({ ...f, avatar_url: e.target.value }))}/>
                                </div>
                                <div className="profile-field" style={{ gridColumn: '1 / -1' }}>
                                    <label>{t('bio')}</label>
                                    <textarea value={form.bio} rows={3} placeholder="..."
                                        onChange={e => setForm(f => ({ ...f, bio: e.target.value }))}/>
                                </div>
                            </div>
                            <div className="profile-edit-actions">
                                <button className="profile-cancel-btn"
                                    onClick={() => { setEditMode(false); setError(''); }}>
                                    {t('cancel')}
                                </button>
                                <button className="profile-save-btn" onClick={handleUpdate} disabled={saving}>
                                    {saving ? '⏳ ...' : `💾 ${t('save')}`}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <>
                            <div className="profile-section-title">Sizning natijangiz</div>
                            <div className="progress-container">
                                <div className="progress-info">
                                    <span>Daraja: <strong>{displayLevel}</strong></span>
                                    <span>{displayPoints} ball</span>
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
                                    <span className="stat-label">Ballar</span>
                                    <span className="stat-value">{displayPoints} 🔥</span>
                                </div>
                                <div className="mini-stat">
                                    <span className="stat-label">Holat</span>
                                    <span className="stat-value">{profile?.is_active ? '✅ Faol' : '❌'}</span>
                                </div>
                            </div>

                            <div className="recent-activity">
                                <div className="profile-section-title">{t('profile')}</div>
                                <ul className="activity-list">
                                    <li><span>📧</span> {t('email')}: <strong>{displayEmail}</strong></li>
                                    <li><span>🎓</span> {t('level')}: <strong>{displayLevel}</strong></li>
                                    {displayBio && <li><span>📝</span> {t('bio')}: <strong>{displayBio}</strong></li>}
                                    <li><span>📅</span> {t('reg_year')}: <strong>
                                        {profile?.created_at
                                            ? new Date(profile.created_at).toLocaleDateString(lang === 'uz' ? 'uz-UZ' : 'ru-RU')
                                            : '—'}
                                    </strong></li>
                                </ul>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Profile;