import { useState, useEffect, useRef } from 'react';
import './Profile.css';
import { API_URL, useHttp, headers, headersImg, resolveImageUrl } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import AppHeader from '../../../components/appheader/AppHeader';
import { Camera, Share2, Globe, Loader2, Check, ShieldCheck } from 'lucide-react';

const prefersReduced = () =>
    typeof window !== 'undefined' && window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const LEVEL_LABEL = {
    Beginner:     { ru: 'Начинающий', uz: "Boshlang'ich" },
    Intermediate: { ru: 'Средний',    uz: "O'rta" },
    Advanced:     { ru: 'Продвинутый', uz: "Ilg'or" },
};

/* ── Avatar upload / delete modal (kept from the previous profile) ── */
function AvatarModal({ onClose, onUpload, onDelete, hasAvatar, ru }) {
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
        setErr('');
        const formData = new FormData();
        formData.append('file', file);
        try {
            const res = await fetch(`${API_URL}v1/student/me/avatar`, {
                method: 'PATCH', headers: headersImg(), body: formData,
            });
            const text = await res.text();
            let url = null;
            try {
                const parsed = JSON.parse(text);
                if (typeof parsed === 'string') url = parsed;
                else if (parsed && typeof parsed === 'object')
                    url = parsed.avatar_url || parsed.url || parsed.path || parsed.file_url || parsed.filename
                        || Object.values(parsed).find(v => typeof v === 'string') || null;
            } catch { url = text.trim(); }
            onUpload(url || '');
            onClose();
        } catch {
            setErr(ru ? 'Произошла ошибка. Попробуйте снова.' : "Xatolik yuz berdi. Qayta urinib ko'ring.");
        } finally { setUploading(false); }
    };

    const handleDelete = async () => {
        setDeleting(true);
        setErr('');
        try {
            const res = await fetch(`${API_URL}v1/student/me/avatar`, { method: 'DELETE', headers: headersImg() });
            if (!res.ok) throw new Error(res.status);
            onDelete();
            onClose();
        } catch {
            setErr(ru ? 'Ошибка при удалении.' : "O'chirishda xatolik.");
        } finally { setDeleting(false); }
    };

    return (
        <div className="av-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
            <div className="av-modal">
                <button className="av-close" onClick={onClose}>✕</button>
                <div className="av-modal-title">{ru ? 'Фото профиля' : 'Profil fotosi'}</div>
                {err && <div className="av-modal-err">{err}</div>}

                {preview ? (
                    <div className="av-preview-wrap">
                        <img src={preview} alt="preview" className="av-preview-img" />
                        <div className="av-preview-actions">
                            <button className="av-btn av-btn-ghost" onClick={() => { setPreview(null); setFile(null); }}>
                                ↩ {ru ? 'Другое' : 'Boshqa'}
                            </button>
                            <button className="av-btn av-btn-primary" onClick={handleUpload} disabled={uploading}>
                                {uploading ? <><span className="av-spinner" /> {ru ? 'Загрузка…' : 'Yuklanmoqda…'}</> : `✓ ${ru ? 'Сохранить' : 'Saqlash'}`}
                            </button>
                        </div>
                    </div>
                ) : (
                    <>
                        <div className={`av-drop-zone ${dragOver ? 'av-drop-active' : ''}`}
                            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                            onDragLeave={() => setDragOver(false)}
                            onDrop={handleDrop}
                            onClick={() => fileInputRef.current?.click()}>
                            <div className="av-drop-icon">🖼️</div>
                            <div className="av-drop-text">{ru ? 'Перетащи фото сюда' : "Rasmni shu yerga tashlang"}</div>
                            <div className="av-drop-sub">{ru ? 'или нажми чтобы выбрать' : "yoki tanlash uchun bosing"}</div>
                        </div>
                        <div className="av-divider"><span>{ru ? 'или' : 'yoki'}</span></div>
                        <button className="av-camera-btn" onClick={() => cameraInputRef.current?.click()}>
                            <span className="av-camera-icon">📸</span> {ru ? 'Сделать фото' : 'Kameradan olish'}
                        </button>
                        {hasAvatar && (
                            <button className="av-delete-btn" onClick={handleDelete} disabled={deleting}>
                                {deleting ? <><span className="av-spinner av-spinner-red" /> {ru ? 'Удаление…' : "O'chirilmoqda…"}</> : `🗑 ${ru ? 'Удалить фото' : "Fotoni o'chirish"}`}
                            </button>
                        )}
                    </>
                )}

                <input ref={fileInputRef} type="file" accept="image/*" style={{ display: 'none' }}
                    onChange={e => pickFile(e.target.files[0])} />
                <input ref={cameraInputRef} type="file" accept="image/*" capture="user" style={{ display: 'none' }}
                    onChange={e => pickFile(e.target.files[0])} />
            </div>
        </div>
    );
}

/* ── Decorative progress ring drawn around the avatar ── */
function AvatarRing({ pct }) {
    const size = 168, stroke = 6, r = (size - stroke) / 2, circ = 2 * Math.PI * r;
    const [offset, setOffset] = useState(circ);
    useEffect(() => {
        if (prefersReduced()) { setOffset(circ - circ * pct / 100); return; }
        const id = setTimeout(() => setOffset(circ - circ * pct / 100), 250);
        return () => clearTimeout(id);
    }, [pct, circ]);
    return (
        <svg className="pf-avatar-ring" width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
            <defs>
                <linearGradient id="pfRing" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0" stopColor="#7ef0a3" /><stop offset="1" stopColor="#2bc45a" />
                </linearGradient>
            </defs>
            <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,.08)" strokeWidth={stroke} />
            <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="url(#pfRing)" strokeWidth={stroke}
                strokeLinecap="round" strokeDasharray={circ} strokeDashoffset={offset}
                transform={`rotate(-90 ${size / 2} ${size / 2})`}
                style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(.2,.75,.25,1)', filter: 'drop-shadow(0 0 6px rgba(54,224,107,.5))' }} />
        </svg>
    );
}

const POINTS_GOAL = 5000; // ring fills toward this "mastery" milestone

/** The text of an API error: the app wraps FastAPI errors as {error: {message}}. */
export const apiErrorMessage = (e) => {
    const body = e?.response?.data;
    const msg = body?.error?.message ?? body?.detail;
    return typeof msg === 'string' ? msg : '';
};

function Profile({ user: initialUser }) {
    const { request } = useHttp();
    const { lang, toggleLang } = useTranslation();
    const ru = lang === 'ru';

    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showAvatar, setShowAvatar] = useState(false);
    const [toast, setToast] = useState('');
    const toastTimer = useRef(null);

    // Personal info form
    const [info, setInfo] = useState({ full_name: '', phone: '' });
    const [savingInfo, setSavingInfo] = useState(false);
    const [infoErr, setInfoErr] = useState('');

    // Security form
    const [pwd, setPwd] = useState({ current: '', next: '', confirm: '' });
    const [savingPwd, setSavingPwd] = useState(false);
    const [pwdErr, setPwdErr] = useState('');

    useEffect(() => () => clearTimeout(toastTimer.current), []);
    const flash = (msg) => { setToast(msg); clearTimeout(toastTimer.current); toastTimer.current = setTimeout(() => setToast(''), 3000); };

    const loadMe = () =>
        request(`${API_URL}v1/student/me`, 'GET', null, headers())
            .then(data => {
                setProfile(data);
                setInfo({ full_name: data.full_name || '', phone: data.phone || '' });
                return data;
            });

    useEffect(() => {
        loadMe().catch(() => setProfile(initialUser || null)).finally(() => setLoading(false));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const dirtyInfo = profile && (
        (!profile.identity_managed && info.full_name !== (profile.full_name || '')) ||
        info.phone !== (profile.phone || '')
    );

    const saveInfo = () => {
        setSavingInfo(true);
        setInfoErr('');
        request(`${API_URL}v1/student/me`, 'PUT',
            JSON.stringify(managed ? { phone: info.phone } : { full_name: info.full_name, phone: info.phone }), headers())
            .then(updated => {
                setProfile(p => ({ ...p, ...updated }));
                flash(ru ? 'Данные сохранены ✓' : "Ma'lumotlar saqlandi ✓");
            })
            .catch(e => setInfoErr(apiErrorMessage(e) || (ru ? 'Не удалось сохранить' : "Saqlab bo'lmadi")))
            .finally(() => setSavingInfo(false));
    };

    const updatePassword = () => {
        setPwdErr('');
        if (pwd.next.length < 6) { setPwdErr(ru ? 'Новый пароль минимум 6 символов' : "Yangi parol kamida 6 belgi"); return; }
        if (pwd.next !== pwd.confirm) { setPwdErr(ru ? 'Пароли не совпадают' : "Parollar mos kelmadi"); return; }
        setSavingPwd(true);
        request(`${API_URL}v1/student/me/password`, 'PUT',
            JSON.stringify({ current_password: pwd.current, new_password: pwd.next }), headers())
            .then(() => {
                setPwd({ current: '', next: '', confirm: '' });
                flash(ru ? 'Пароль обновлён ✓' : 'Parol yangilandi ✓');
            })
            .catch(e => setPwdErr(apiErrorMessage(e) || (ru ? 'Неверный текущий пароль' : "Joriy parol noto'g'ri")))
            .finally(() => setSavingPwd(false));
    };

    const handleAvatarUploaded = (url) => {
        if (!url) { loadMe().catch(() => {}); }
        else setProfile(p => ({ ...p, avatar_url: resolveImageUrl(url) }));
        flash(ru ? 'Фото обновлено ✓' : 'Foto yangilandi ✓');
    };
    const handleAvatarDeleted = () => { setProfile(p => ({ ...p, avatar_url: null })); flash(ru ? 'Фото удалено' : "Foto o'chirildi"); };

    const sharePublic = () => {
        if (!profile?.username) return;
        const url = `${window.location.origin}/u/${profile.username}`;
        navigator.clipboard?.writeText(url)
            .then(() => flash(ru ? 'Ссылка скопирована' : "Havola nusxalandi"))
            .catch(() => {});
    };

    if (loading) {
        return (
            <div className="pf-dark">
                <AppHeader me={profile} />
                <div className="pf-state"><Loader2 className="pf-spin" size={26} /> {ru ? 'Загрузка…' : 'Yuklanmoqda…'}</div>
            </div>
        );
    }

    const displayName = profile?.full_name || profile?.username || '—';
    const level = profile?.current_level || 'Beginner';
    const levelLabel = (LEVEL_LABEL[level] || LEVEL_LABEL.Beginner)[ru ? 'ru' : 'uz'];
    const points = profile?.total_points ?? 0;
    const avatarSrc = resolveImageUrl(profile?.avatar_url);
    // Name and photo come from turon-v2 / gennis-v2: read-only here.
    const managed = !!profile?.identity_managed;
    const regDate = profile?.created_at
        ? new Date(profile.created_at).toLocaleDateString(ru ? 'ru-RU' : 'uz-UZ', { year: 'numeric', month: '2-digit', day: '2-digit' })
        : '—';
    const ringPct = Math.min(100, Math.round((points / POINTS_GOAL) * 100));
    const balance = profile?.balance ?? 0;
    const achCount = Array.isArray(profile?.achievements) ? profile.achievements.length : 0;
    const memberYear = profile?.created_at ? new Date(profile.created_at).getFullYear() : '—';

    return (
        <div className="pf-dark">
            {showAvatar && (
                <AvatarModal ru={ru}
                    onClose={() => setShowAvatar(false)}
                    onUpload={handleAvatarUploaded}
                    onDelete={handleAvatarDeleted}
                    hasAvatar={!!profile?.avatar_url} />
            )}

            <AppHeader me={profile} />

            {toast && <div className="pf-toast">{toast}</div>}

            <div className="pf-shell">
                <div className="pf-grid">

                    {/* ── Profile Summary ── */}
                    <section className="pf-card pf-summary pf-rise">
                        <div className="pf-card-title">{ru ? 'Сводка профиля' : 'Profil ma\'lumoti'}</div>

                        <div className="pf-avatar-wrap" onClick={managed ? undefined : () => setShowAvatar(true)}
                            style={managed ? { cursor: 'default' } : undefined}
                            title={managed ? undefined : (ru ? 'Изменить фото' : "Fotoni o'zgartirish")}>
                            <AvatarRing pct={ringPct} />
                            <div className="pf-avatar-photo">
                                {avatarSrc ? <img src={avatarSrc} alt="avatar" /> : <span className="pf-avatar-initials">{(displayName[0] || 'U').toUpperCase()}</span>}
                            </div>
                            {!managed && <div className="pf-avatar-cam"><Camera size={18} /></div>}
                        </div>

                        <h1 className="pf-name">{displayName}</h1>
                        <div className="pf-sublabel">{ru ? 'Полное имя' : "To'liq ism"}</div>

                        <div className="pf-field-label">{ru ? 'Уровень знаний' : 'Bilim darajasi'}</div>
                        <span className="pf-level-badge">{levelLabel}</span>

                        <div className="pf-divider" />

                        <div className="pf-field-label">{ru ? 'Всего баллов обучения' : "Jami o'quv ballari"}</div>
                        <div className="pf-points">{points.toLocaleString('ru-RU').replace(/,/g, ' ')}</div>
                        <div className="pf-sublabel">{ru ? 'баллов заработано' : 'ball to\'plangan'}</div>

                        <div className="pf-mini-stats">
                            <div className="pf-mini"><div className="pf-mini-val">{balance.toLocaleString('ru-RU').replace(/,/g, ' ')}</div><div className="pf-mini-lbl">{ru ? 'Баланс' : 'Balans'}</div></div>
                            <div className="pf-mini"><div className="pf-mini-val">{achCount}</div><div className="pf-mini-lbl">{ru ? 'Награды' : 'Yutuqlar'}</div></div>
                            <div className="pf-mini"><div className="pf-mini-val">{memberYear}</div><div className="pf-mini-lbl">{ru ? 'С нами' : "A'zo"}</div></div>
                        </div>

                        <div className="pf-summary-actions">
                            {profile?.username && (
                                <button className="pf-ghost-btn" onClick={sharePublic}><Share2 size={15} /> {ru ? 'Поделиться' : 'Ulashish'}</button>
                            )}
                            <button className="pf-ghost-btn" onClick={toggleLang}><Globe size={15} /> {ru ? "O'zbekcha" : 'Русский'}</button>
                        </div>
                    </section>

                    {/* ── Right column ── */}
                    <div className="pf-right">

                        {/* Personal Information */}
                        <section className="pf-card pf-rise" style={{ animationDelay: '.06s' }}>
                            <div className="pf-card-title">{ru ? 'Личная информация' : "Shaxsiy ma'lumot"}</div>
                            {infoErr && <div className="pf-err">{infoErr}</div>}
                            {managed && (
                                <div className="pf-hint" style={{ fontSize: 13, opacity: .7, marginBottom: 10 }}>
                                    {ru
                                        ? 'Имя, фамилия и фото берутся из системы Gennis/Turon и здесь не меняются.'
                                        : "Ism, familiya va rasm Gennis/Turon tizimidan olinadi va bu yerda o'zgartirilmaydi."}
                                </div>
                            )}

                            <label className="pf-input-group">
                                <span>{ru ? 'Полное имя' : "To'liq ism"}</span>
                                <input value={info.full_name} placeholder={ru ? 'Имя Фамилия' : 'Ism Familiya'}
                                    readOnly={managed} className={managed ? 'pf-input-readonly' : undefined}
                                    onChange={e => setInfo(f => ({ ...f, full_name: e.target.value }))} />
                            </label>
                            <label className="pf-input-group">
                                <span>{ru ? 'Номер телефона' : 'Telefon raqami'}</span>
                                <input value={info.phone} placeholder="+998 ..."
                                    onChange={e => setInfo(f => ({ ...f, phone: e.target.value }))} />
                            </label>
                            <label className="pf-input-group">
                                <span>{ru ? 'Логин (username)' : 'Username (login)'}</span>
                                <input value={profile?.username || ''} readOnly className="pf-input-readonly" />
                            </label>
                            <label className="pf-input-group">
                                <span>{ru ? 'Дата регистрации' : "Ro'yxatdan o'tgan sana"}</span>
                                <input value={regDate} readOnly className="pf-input-readonly" />
                            </label>

                            <button className="pf-save-btn" onClick={saveInfo} disabled={!dirtyInfo || savingInfo}>
                                {savingInfo ? <><Loader2 className="pf-spin" size={16} /> {ru ? 'Сохранение…' : 'Saqlanmoqda…'}</>
                                    : <><Check size={16} /> {ru ? 'Сохранить изменения' : "O'zgarishlarni saqlash"}</>}
                            </button>
                        </section>

                        {/* Security */}
                        <section className="pf-card pf-rise" style={{ animationDelay: '.12s' }}>
                            <div className="pf-card-title">{ru ? 'Безопасность' : 'Xavfsizlik'}</div>
                            {pwdErr && <div className="pf-err">{pwdErr}</div>}

                            <input className="pf-input" type="password" autoComplete="current-password"
                                placeholder={ru ? 'Текущий пароль' : 'Joriy parol'}
                                value={pwd.current} onChange={e => setPwd(p => ({ ...p, current: e.target.value }))} />
                            <input className="pf-input" type="password" autoComplete="new-password"
                                placeholder={ru ? 'Новый пароль' : 'Yangi parol'}
                                value={pwd.next} onChange={e => setPwd(p => ({ ...p, next: e.target.value }))} />
                            <input className="pf-input" type="password" autoComplete="new-password"
                                placeholder={ru ? 'Подтвердите новый пароль' : 'Yangi parolni tasdiqlang'}
                                value={pwd.confirm} onChange={e => setPwd(p => ({ ...p, confirm: e.target.value }))} />

                            <button className="pf-update-pwd-btn" onClick={updatePassword}
                                disabled={savingPwd || !pwd.current || !pwd.next || !pwd.confirm}>
                                {savingPwd ? <><Loader2 className="pf-spin" size={18} /> {ru ? 'Обновление…' : 'Yangilanmoqda…'}</>
                                    : <><ShieldCheck size={18} /> {ru ? 'Обновить пароль' : 'Parolni yangilash'}</>}
                            </button>
                        </section>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Profile;
