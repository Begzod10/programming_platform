import {useState, useEffect, useRef} from 'react';
import './Profile.css';
import {API_URL, useHttp, headers, headersImg, resolveImageUrl} from '../../../api/search/base';
import {useTranslation} from '../../../i18n/useTranslation';

function AvatarModal({onClose, onUpload, onDelete, hasAvatar}) {
    const fileInputRef = useRef(null);
    const cameraInputRef = useRef(null);
    const [preview, setPreview] = useState(null);
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [deleting, setDeleting] = useState(false);
    const [dragOver, setDragOver] = useState(false);
    const [err, setErr] = useState('');

    const pickFile = (f) => {
        if (!f) return;
        setErr('');
        setFile(f);
        const reader = new FileReader();
        reader.onload = e => setPreview(e.target.result);
        reader.readAsDataURL(f);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        const f = e.dataTransfer.files[0];
        if (f && f.type.startsWith('image/')) pickFile(f);
    };

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        setErr("");
        const formData = new FormData();
        formData.append("file", file);
        try {
            const res = await fetch(`${API_URL}v1/student/me/avatar`, {
                method: "PATCH",
                headers: headersImg(),
                body: formData,
            });

            const text = await res.text();
            console.log('Avatar upload status:', res.status, 'response:', text);

            // Сервер может вернуть: строку, JSON-строку, или объект
            let url = null;
            try {
                const parsed = JSON.parse(text);
                // Если объект — ищем поле с URL
                if (typeof parsed === 'string') {
                    url = parsed;
                } else if (parsed && typeof parsed === 'object') {
                    // Пробуем все возможные поля
                    url = parsed.avatar_url || parsed.url || parsed.path || parsed.file_url || parsed.filename || null;
                    // Если не нашли поле — берём первое строковое значение
                    if (!url) {
                        const firstStr = Object.values(parsed).find(v => typeof v === 'string');
                        url = firstStr || null;
                    }
                }
            } catch {
                // Не JSON — берём как есть
                url = text.trim();
            }

            console.log('Resolved avatar url:', url);

            // Даже если url пустой/null — считаем успехом (сервер сохранил файл)
            onUpload(url || '');
            onClose();

        } catch (e) {
            console.error('Upload error:', e);
            setErr("Xatolik yuz berdi. Qayta urinib ko'ring.");
        } finally {
            setUploading(false);
        }
    };

    const handleDelete = async () => {
        setDeleting(true);
        setErr('');
        try {
            const res = await fetch(`${API_URL}v1/student/me/avatar`, {
                method: 'DELETE',
                headers: headersImg(),
            });
            if (!res.ok) throw new Error(res.status);
            onDelete();
            onClose();
        } catch {
            setErr("O'chirishda xatolik.");
        } finally {
            setDeleting(false);
        }
    };

    return (
        <div className="av-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
            <div className="av-modal">
                <button className="av-close" onClick={onClose}>✕</button>
                <div className="av-modal-title">Фото профиля</div>

                {err && <div className="av-modal-err">{err}</div>}

                {preview ? (
                    <div className="av-preview-wrap">
                        <img src={preview} alt="preview" className="av-preview-img"/>
                        <div className="av-preview-actions">
                            <button className="av-btn av-btn-ghost"
                                    onClick={() => { setPreview(null); setFile(null); }}>
                                ↩ Выбрать другое
                            </button>
                            <button className="av-btn av-btn-primary"
                                    onClick={handleUpload} disabled={uploading}>
                                {uploading
                                    ? <><span className="av-spinner"/> Загрузка…</>
                                    : '✓ Сохранить'}
                            </button>
                        </div>
                    </div>
                ) : (
                    <>
                        <div
                            className={`av-drop-zone ${dragOver ? 'av-drop-active' : ''}`}
                            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                            onDragLeave={() => setDragOver(false)}
                            onDrop={handleDrop}
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <div className="av-drop-icon">🖼️</div>
                            <div className="av-drop-text">Перетащи фото сюда</div>
                            <div className="av-drop-sub">или нажми чтобы выбрать из галереи</div>
                        </div>

                        <div className="av-divider"><span>или</span></div>

                        <button className="av-camera-btn"
                                onClick={() => cameraInputRef.current?.click()}>
                            <span className="av-camera-icon">📸</span>
                            Сделать фото с камеры
                        </button>

                        {hasAvatar && (
                            <button className="av-delete-btn"
                                    onClick={handleDelete} disabled={deleting}>
                                {deleting
                                    ? <><span className="av-spinner av-spinner-red"/> Удаление…</>
                                    : '🗑 Удалить фото'}
                            </button>
                        )}
                    </>
                )}

                <input ref={fileInputRef} type="file" accept="image/*"
                       style={{display: 'none'}}
                       onChange={e => pickFile(e.target.files[0])}/>
                <input ref={cameraInputRef} type="file" accept="image/*"
                       capture="user" style={{display: 'none'}}
                       onChange={e => pickFile(e.target.files[0])}/>
            </div>
        </div>
    );
}

function Profile({user: initialUser, onLogout}) {
    const {request} = useHttp();
    const {t, lang, toggleLang} = useTranslation();

    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [editMode, setEditMode] = useState(false);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [showAvatar, setShowAvatar] = useState(false);

    const [form, setForm] = useState({
        full_name: '',
        bio: '',
        avatar_url: '',
    });

    useEffect(() => {
        request(`${API_URL}v1/student/me`, 'GET', null, headers())
            .then(data => {
                setProfile(data);
                setForm({
                    full_name: data.full_name || '',
                    bio: data.bio || '',
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
            JSON.stringify({full_name: form.full_name, bio: form.bio, avatar_url: form.avatar_url}),
            headers()
        )
            .then(updated => {
                setProfile(p => ({...p, ...updated}));
                setEditMode(false);
                setSuccess(t('profile_updated'));
                setTimeout(() => setSuccess(''), 3000);
            })
            .catch(() => setError(t('save_error')))
            .finally(() => setSaving(false));
    };

    const handleAvatarUploaded = (url) => {
        // Если сервер вернул пустую строку — перезапрашиваем профиль чтобы получить актуальный avatar_url
        if (!url) {
            request(`${API_URL}v1/student/me`, 'GET', null, headers())
                .then(data => {
                    setProfile(data);
                    setForm(f => ({...f, avatar_url: data.avatar_url || ''}));
                })
                .catch(() => {});
        } else {
            const resolved = resolveImageUrl(url);
            setProfile(p => ({...p, avatar_url: resolved}));
            setForm(f => ({...f, avatar_url: resolved}));
        }
        setSuccess('Фото профиля обновлено ✓');
        setTimeout(() => setSuccess(''), 3000);
    };

    const handleAvatarDeleted = () => {
        setProfile(p => ({...p, avatar_url: null}));
        setForm(f => ({...f, avatar_url: ''}));
        setSuccess('Фото профиля удалено');
        setTimeout(() => setSuccess(''), 3000);
    };

    if (loading) {
        return (
            <div className="profile-loading">
                <div className="profile-spinner"/>
                <p>{t('loading')}</p>
            </div>
        );
    }

    const displayName = profile?.full_name || profile?.username || '—';
    const displayEmail = profile?.email || '—';
    const displayLevel = profile?.current_level || 'Beginner';
    const displayPoints = profile?.total_points ?? 0;
    const displayBio = profile?.bio || '';
    const avatarSrc = resolveImageUrl(profile?.avatar_url);

    return (
        <>
            {showAvatar && (
                <AvatarModal
                    onClose={() => setShowAvatar(false)}
                    onUpload={handleAvatarUploaded}
                    onDelete={handleAvatarDeleted}
                    hasAvatar={!!profile?.avatar_url}
                />
            )}

            <div className="profile-full-view item-fade-in">
                <div className="profile-main-card">

                    <div className="profile-aside">
                        <div
                            className="insta-avatar-large fade-in av-trigger"
                            onClick={() => setShowAvatar(true)}
                            title="Изменить фото"
                        >
                            {avatarSrc
                                ? <img src={avatarSrc} alt="avatar" className="profile-avatar-img"/>
                                : '👤'}
                            <div className="av-hover-overlay">
                                <span className="av-camera-hint">📷</span>
                            </div>
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

                    <div className="profile-content-rich fade-in">
                        {success && <div className="profile-success">{success}</div>}
                        {error && <div className="profile-error">{error}</div>}

                        {editMode ? (
                            <div className="profile-edit-form">
                                <div className="profile-section-title">{t('edit_profile')}</div>

                                <div className="edit-avatar-row">
                                    <div
                                        className="edit-avatar-thumb av-trigger"
                                        onClick={() => setShowAvatar(true)}
                                        title="Изменить фото"
                                    >
                                        {avatarSrc
                                            ? <img src={avatarSrc} alt="avatar" className="profile-avatar-img"/>
                                            : '👤'}
                                        <div className="av-hover-overlay">
                                            <span className="av-camera-hint" style={{fontSize: 16}}>📷</span>
                                        </div>
                                    </div>
                                    <div className="edit-avatar-info">
                                        <div className="edit-avatar-label">Фото профиля</div>
                                        <button
                                            className="edit-avatar-change-btn"
                                            onClick={() => setShowAvatar(true)}
                                            type="button"
                                        >
                                            📁 Галерея / 📸 Камера
                                        </button>
                                        <div className="edit-avatar-hint">или вставь ссылку ниже</div>
                                    </div>
                                </div>

                                <div className="profile-edit-grid">
                                    <div className="profile-field">
                                        <label>{t('full_name')}</label>
                                        <input value={form.full_name} placeholder="Ism Familiya"
                                               onChange={e => setForm(f => ({...f, full_name: e.target.value}))}/>
                                    </div>
                                    <div className="profile-field">
                                        <label>{t('avatar_url')} (ссылка)</label>
                                        <input value={form.avatar_url} placeholder="https://..."
                                               onChange={e => setForm(f => ({...f, avatar_url: e.target.value}))}/>
                                    </div>
                                    <div className="profile-field" style={{gridColumn: '1 / -1'}}>
                                        <label>{t('bio')}</label>
                                        <textarea value={form.bio} rows={3} placeholder="..."
                                                  onChange={e => setForm(f => ({...f, bio: e.target.value}))}/>
                                    </div>
                                </div>

                                <div className="profile-edit-actions">
                                    <button className="profile-cancel-btn"
                                            onClick={() => { setEditMode(false); setError(''); }}>
                                        {t('cancel')}
                                    </button>
                                    <button
                                        className="profile-save-btn"
                                        onClick={handleUpdate}
                                        disabled={saving}
                                        type="button"
                                    >
                                        {saving
                                            ? <><span className="av-spinner"/> Сохранение…</>
                                            : `💾 ${t('save')}`}
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
                                             style={{width: `${Math.min((displayPoints / 1000) * 100, 100)}%`}}/>
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
                                        {displayBio &&
                                            <li><span>📝</span> {t('bio')}: <strong>{displayBio}</strong></li>}
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
        </>
    );
}

export default Profile;