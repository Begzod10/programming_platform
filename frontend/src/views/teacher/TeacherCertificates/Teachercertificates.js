import React, {useState, useEffect, useCallback} from 'react';
import ReactDOM from 'react-dom';
import './Teachercertificates.css';
import {API_URL, useHttp, headers} from '../../../api/search/base';

const CRITERIA_TYPES = [
    {value: 'project_count',    label: '📁 Количество проектов'},
    {value: 'points_threshold', label: '⭐ Набранные очки'},
];

/* ── CertModal ── */
const CertModal = ({item, onSave, onClose, saving}) => {
    const isEdit = !!item;
    const [name,          setName]          = useState(item?.name || '');
    const [description,   setDescription]   = useState(item?.description || '');
    const [badgeUrl,      setBadgeUrl]       = useState(item?.badge_image_url || '');
    const [pointsReward,  setPointsReward]   = useState(item?.points_reward ?? 100);
    const [criteriaType,  setCriteriaType]   = useState(item?.criteria_type || 'project_count');
    const [criteriaValue, setCriteriaValue]  = useState(item?.criteria_value ?? 1);
    const [errors,        setErrors]         = useState({});

    const validate = () => {
        const e = {};
        if (!name.trim())        e.name     = 'Введите название';
        if (!description.trim()) e.description = 'Введите описание';
        if (pointsReward <= 0)   e.points   = 'Очки должны быть > 0';
        if (criteriaValue <= 0)  e.criteria = 'Значение должно быть > 0';
        setErrors(e);
        return !Object.keys(e).length;
    };

    const handleSave = () => {
        if (!validate()) return;
        onSave({
            name,
            description,
            badge_image_url: badgeUrl,
            points_reward:   pointsReward,
            criteria_type:   criteriaType,
            criteria_value:  criteriaValue,
        });
    };

    return ReactDOM.createPortal(
        <div className="tc-overlay" onClick={onClose}>
            <div className="tc-modal" onClick={e => e.stopPropagation()}>
                <div className="tc-modal-head">
                    <div className="tc-modal-head-icon">{isEdit ? '✏️' : '🏅'}</div>
                    <h3>{isEdit ? 'Редактировать сертификат' : 'Новый сертификат'}</h3>
                    <button className="tc-close" onClick={onClose}>✕</button>
                </div>

                <div className="tc-modal-body">
                    <div className="tc-field">
                        <label>Название *</label>
                        <input
                            value={name}
                            placeholder="Python Developer"
                            className={errors.name ? 'err' : ''}
                            onChange={e => { setName(e.target.value); setErrors(v => ({...v, name: ''})); }}
                        />
                        {errors.name && <span className="tc-err">{errors.name}</span>}
                    </div>

                    <div className="tc-field">
                        <label>Описание *</label>
                        <textarea
                            rows={3}
                            value={description}
                            placeholder="Условие получения сертификата..."
                            className={errors.description ? 'err' : ''}
                            onChange={e => { setDescription(e.target.value); setErrors(v => ({...v, description: ''})); }}
                        />
                        {errors.description && <span className="tc-err">{errors.description}</span>}
                    </div>

                    <div className="tc-field">
                        <label>URL иконки (необязательно)</label>
                        <input
                            value={badgeUrl}
                            placeholder="https://..."
                            onChange={e => setBadgeUrl(e.target.value)}
                        />
                    </div>

                    <div className="tc-row2">
                        <div className="tc-field">
                            <label>Очки *</label>
                            <input
                                type="number" min={1}
                                value={pointsReward}
                                className={errors.points ? 'err' : ''}
                                onChange={e => { setPointsReward(+e.target.value); setErrors(v => ({...v, points: ''})); }}
                            />
                            {errors.points && <span className="tc-err">{errors.points}</span>}
                        </div>

                        <div className="tc-field">
                            <label>Значение условия *</label>
                            <input
                                type="number" min={1}
                                value={criteriaValue}
                                className={errors.criteria ? 'err' : ''}
                                onChange={e => { setCriteriaValue(+e.target.value); setErrors(v => ({...v, criteria: ''})); }}
                            />
                            {errors.criteria && <span className="tc-err">{errors.criteria}</span>}
                        </div>
                    </div>

                    <div className="tc-field">
                        <label>Тип условия</label>
                        <select value={criteriaType} onChange={e => setCriteriaType(e.target.value)}>
                            {CRITERIA_TYPES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
                        </select>
                    </div>
                </div>

                <div className="tc-modal-foot">
                    <button className="tc-btn-cancel" onClick={onClose}>Отмена</button>
                    <button className="tc-btn-save" onClick={handleSave} disabled={saving}>
                        {saving ? '⏳ Сохранение...' : isEdit ? '💾 Сохранить' : '✅ Создать'}
                    </button>
                </div>
            </div>
        </div>,
        document.body
    );
};

/* ── AwardModal ── */
const AwardModal = ({cert, onClose, onAwardSuccess, showToast}) => {
    const {request} = useHttp();

    const [tab,           setTab]           = useState('not_awarded');
    const [withList,      setWithList]      = useState([]);
    const [withoutList,   setWithoutList]   = useState([]);
    const [loading,       setLoading]       = useState(true);
    const [selected,      setSelected]      = useState(new Set());
    const [search,        setSearch]        = useState('');
    const [awarding,      setAwarding]      = useState(false);
    const [revoking,      setRevoking]      = useState(null);
    const [confirmRevoke, setConfirmRevoke] = useState(null);

    useEffect(() => {
        setLoading(true);
        Promise.all([
            request(`${API_URL}v1/achievements/${cert.id}/students-with`,    'GET', null, headers()),
            request(`${API_URL}v1/achievements/${cert.id}/students-without`, 'GET', null, headers()),
        ])
        .then(([w, wo]) => {
            setWithList(Array.isArray(w)  ? w  : []);
            setWithoutList(Array.isArray(wo) ? wo : []);
        })
        .catch(() => {})
        .finally(() => setLoading(false));
    }, [cert.id]);

    const filteredWithout = withoutList.filter(s => {
        const q = search.toLowerCase();
        return (s.full_name || s.username || '').toLowerCase().includes(q)
            || (s.email || '').toLowerCase().includes(q);
    });

    const filteredWith = withList.filter(s => {
        const q = search.toLowerCase();
        return (s.full_name || s.username || '').toLowerCase().includes(q)
            || (s.email || '').toLowerCase().includes(q);
    });

    const toggle    = (id) => setSelected(prev => {
        const next = new Set(prev);
        next.has(id) ? next.delete(id) : next.add(id);
        return next;
    });

    const toggleAll = () => setSelected(
        selected.size === filteredWithout.length && filteredWithout.length > 0
            ? new Set()
            : new Set(filteredWithout.map(s => s.student_id))
    );

    const av = (s) => (s.full_name || s.username || '?')[0].toUpperCase();

    /* ── Выдать сертификат ── */
    const handleAward = async () => {
        if (selected.size === 0) return;
        setAwarding(true);
        let ok = 0;
        const awardedIds = [...selected];

        await Promise.all(awardedIds.map(sid => {
            const params = new URLSearchParams({student_id: sid, achievement_id: cert.id});
            return request(`${API_URL}v1/achievements/award?${params}`, 'POST', null, headers())
                .then(() => { ok++; })
                .catch(() => {});
        }));

        if (ok > 0) {
            const nowAwarded = withoutList.filter(s => awardedIds.includes(s.student_id));
            setWithList(prev => [...prev, ...nowAwarded.map(s => ({...s, earned_at: new Date().toISOString()}))]);
            setWithoutList(prev => prev.filter(s => !awardedIds.includes(s.student_id)));
            setSelected(new Set());
            onAwardSuccess(cert.id, awardedIds);
        }

        setAwarding(false);
        showToast(ok > 0 ? `🎖️ Выдано ${ok} студент${ok === 1 ? 'у' : 'ам'}!` : '❌ Ошибка выдачи');
    };

    /* ── Отозвать сертификат ── */
    const handleRevoke = async (student) => {
        setRevoking(student.student_id);
        try {
            await request(
                `${API_URL}v1/achievements/${cert.id}/revoke?student_id=${student.student_id}`,
                'DELETE', null, headers()
            );
            setWithList(prev => prev.filter(s => s.student_id !== student.student_id));
            setWithoutList(prev => [...prev, {...student, earned_at: undefined}]);
            setConfirmRevoke(null);
            showToast('🗑️ Сертификат отозван');
        } catch {
            showToast('❌ Ошибка при отзыве');
        } finally {
            setRevoking(null);
        }
    };

    const totalCount = withList.length + withoutList.length;
    const awardedPct = totalCount > 0 ? Math.round((withList.length / totalCount) * 100) : 0;

    return ReactDOM.createPortal(
        <div className="tc-overlay" onClick={onClose}>
            <div className="tc-modal award-modal" onClick={e => e.stopPropagation()}>

                {/* ── Header ── */}
                <div className="tc-award-header">
                    <div className="tc-award-cert-card">
                        <div className="tc-award-cert-icon">
                            {cert.badge_image_url
                                ? <img src={cert.badge_image_url} alt=""/>
                                : <span>🏆</span>}
                        </div>
                        <div className="tc-award-cert-info">
                            <div className="tc-award-cert-name">{cert.name}</div>
                            <div className="tc-award-cert-desc">{cert.description}</div>
                            <div className="tc-award-cert-pts">
                                <span className="pts-badge">+{cert.points_reward} очков</span>
                                <span className="criteria-badge">
                                    {CRITERIA_TYPES.find(c => c.value === cert.criteria_type)?.label}
                                </span>
                            </div>
                        </div>
                        <button className="tc-close-white" onClick={onClose}>✕</button>
                    </div>

                    {!loading && totalCount > 0 && (
                        <div className="tc-progress-section">
                            <div className="tc-progress-labels">
                                <span>Прогресс выдачи</span>
                                <span className="tc-progress-pct">
                                    {withList.length} / {totalCount} студентов ({awardedPct}%)
                                </span>
                            </div>
                            <div className="tc-progress-bar">
                                <div className="tc-progress-fill" style={{width: `${awardedPct}%`}}/>
                            </div>
                        </div>
                    )}
                </div>

                {/* ── Tabs ── */}
                <div className="tc-tabs">
                    <button
                        className={`tc-tab ${tab === 'not_awarded' ? 'active' : ''}`}
                        onClick={() => { setTab('not_awarded'); setSearch(''); setSelected(new Set()); }}
                    >
                        <span className="tc-tab-dot not-awarded"/>
                        Не получили
                        <span className="tc-tab-count">{withoutList.length}</span>
                    </button>
                    <button
                        className={`tc-tab ${tab === 'awarded' ? 'active' : ''}`}
                        onClick={() => { setTab('awarded'); setSearch(''); setSelected(new Set()); }}
                    >
                        <span className="tc-tab-dot awarded"/>
                        Получили
                        <span className="tc-tab-count awarded">{withList.length}</span>
                    </button>
                </div>

                {/* ── Body ── */}
                <div className="tc-modal-body award-body">
                    <div className="tc-search-wrap">
                        <span className="tc-search-icon">🔍</span>
                        <input
                            value={search}
                            placeholder={tab === 'not_awarded' ? 'Поиск студента...' : 'Поиск по получателям...'}
                            onChange={e => setSearch(e.target.value)}
                            className="tc-search-input"
                        />
                        {search && (
                            <button className="tc-search-clear" onClick={() => setSearch('')}>✕</button>
                        )}
                    </div>

                    {loading ? (
                        <div className="tc-award-loading">
                            <div className="tc-spinner-sm"/>
                            <span>Загрузка студентов...</span>
                        </div>
                    ) : tab === 'not_awarded' ? (
                        /* ── Не получили ── */
                        <div className="tc-student-section">
                            {filteredWithout.length > 0 && (
                                <div className="tc-list-toolbar">
                                    <span className="tc-list-count">{filteredWithout.length} студентов</span>
                                    <button className="tc-select-all" onClick={toggleAll}>
                                        {selected.size === filteredWithout.length && filteredWithout.length > 0
                                            ? 'Снять всё' : 'Выбрать всех'}
                                    </button>
                                </div>
                            )}
                            <div className="tc-student-list">
                                {filteredWithout.length === 0 ? (
                                    <div className="tc-empty-list">
                                        <span>🎉</span>
                                        <p>{search ? 'Студентов не найдено' : 'Все студенты уже получили сертификат!'}</p>
                                    </div>
                                ) : filteredWithout.map(s => (
                                    <div
                                        key={s.student_id}
                                        className={`tc-student-row ${selected.has(s.student_id) ? 'selected' : ''}`}
                                        onClick={() => toggle(s.student_id)}
                                    >
                                        <div className={`tc-checkbox ${selected.has(s.student_id) ? 'checked' : ''}`}>
                                            {selected.has(s.student_id) && <span>✓</span>}
                                        </div>
                                        <div className="tc-avatar">{av(s)}</div>
                                        <div className="tc-student-info">
                                            <span className="tc-student-name">{s.full_name || s.username}</span>
                                            {/* email может отсутствовать в students-without */}
                                            {s.email && <span className="tc-student-email">{s.email}</span>}
                                            {s.current_level && (
                                                <span className="tc-student-level">⚡ {s.current_level}</span>
                                            )}
                                        </div>
                                        {s.progress !== undefined && (
                                            <div className="tc-mini-progress">
                                                <div className="tc-mini-bar">
                                                    <div className="tc-mini-fill" style={{width: `${Math.min(100, s.progress)}%`}}/>
                                                </div>
                                                <span className="tc-mini-label">{s.progress}%</span>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        /* ── Получили ── */
                        <div className="tc-student-section">
                            {filteredWith.length > 0 && (
                                <div className="tc-list-toolbar">
                                    <span className="tc-list-count">{filteredWith.length} получателей</span>
                                </div>
                            )}
                            <div className="tc-student-list">
                                {filteredWith.length === 0 ? (
                                    <div className="tc-empty-list">
                                        <span>📭</span>
                                        <p>{search ? 'Не найдено' : 'Ещё никто не получил этот сертификат'}</p>
                                    </div>
                                ) : filteredWith.map(s => (
                                    <div key={s.student_id} className="tc-student-row awarded-row">
                                        <div className="tc-avatar awarded-av">{av(s)}</div>
                                        <div className="tc-student-info">
                                            <span className="tc-student-name">{s.full_name || s.username}</span>
                                            {s.email && <span className="tc-student-email">{s.email}</span>}
                                            {s.current_level && (
                                                <span className="tc-student-level">⚡ {s.current_level}</span>
                                            )}
                                            {s.earned_at && (
                                                <span className="tc-earned-date">
                                                    {new Date(s.earned_at).toLocaleDateString('ru-RU', {
                                                        day: 'numeric', month: 'short', year: 'numeric'
                                                    })}
                                                </span>
                                            )}
                                        </div>
                                        <div className="tc-awarded-right">
                                            {s.total_points !== undefined && (
                                                <span className="tc-points-badge">⭐ {s.total_points}</span>
                                            )}
                                            <span className="tc-awarded-tag">✓ Выдан</span>
                                            <button
                                                className="tc-revoke-btn"
                                                onClick={() => setConfirmRevoke(s)}
                                                disabled={revoking === s.student_id}
                                                title="Отозвать сертификат"
                                            >
                                                {revoking === s.student_id ? '⏳' : '🗑'}
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* ── Footer ── */}
                <div className="tc-modal-foot award-foot">
                    {tab === 'not_awarded' ? (
                        <>
                            <span className="tc-selected-count">
                                {selected.size > 0 ? `Выбрано: ${selected.size}` : ''}
                            </span>
                            <button className="tc-btn-cancel" onClick={onClose}>Отмена</button>
                            <button
                                className="tc-btn-award"
                                onClick={handleAward}
                                disabled={selected.size === 0 || awarding}
                            >
                                {awarding
                                    ? '⏳ Выдаём...'
                                    : `🎖️ Выдать${selected.size > 0 ? ` (${selected.size})` : ''}`}
                            </button>
                        </>
                    ) : (
                        <button className="tc-btn-cancel full-width" onClick={onClose}>Закрыть</button>
                    )}
                </div>
            </div>

            {/* ── Confirm Revoke ── */}
            {confirmRevoke && (
                <div className="tc-confirm-overlay" onClick={e => e.stopPropagation()}>
                    <div className="tc-confirm-revoke" onClick={e => e.stopPropagation()}>
                        <div className="tc-confirm-icon">⚠️</div>
                        <h4>Отозвать сертификат?</h4>
                        <p>
                            У <b>{confirmRevoke.full_name || confirmRevoke.username}</b> будет отозван сертификат
                            <br/><b>«{cert.name}»</b>
                        </p>
                        <div className="tc-confirm-btns">
                            <button className="tc-btn-cancel" onClick={() => setConfirmRevoke(null)}>Отмена</button>
                            <button
                                className="tc-btn-delete"
                                onClick={() => handleRevoke(confirmRevoke)}
                                disabled={!!revoking}
                            >
                                {revoking ? '⏳...' : '🗑️ Отозвать'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>,
        document.body
    );
};

/* ── Main: TeacherCertificates ── */
const TeacherCertificates = () => {
    const {request} = useHttp();
    const [certs,     setCerts]     = useState([]);
    const [loading,   setLoading]   = useState(true);
    const [modal,     setModal]     = useState(null);
    const [awardModal,setAwardModal]= useState(null);
    const [confirmId, setConfirmId] = useState(null);
    const [saving,    setSaving]    = useState(false);
    const [toast,     setToast]     = useState('');
    const [certStats, setCertStats] = useState({});

    const showToast = useCallback((msg) => {
        setToast(msg);
        setTimeout(() => setToast(''), 2800);
    }, []);

    useEffect(() => {
        // Используем новый эндпоинт /all
        request(`${API_URL}v1/achievements/all`, 'GET', null, headers())
            .then(c => setCerts(Array.isArray(c) ? c : []))
            .catch(() => {})
            .finally(() => setLoading(false));
    }, []);

    const handleSave = (form) => {
        setSaving(true);
        if (modal === 'add') {
            request(`${API_URL}v1/achievements/create`, 'POST', JSON.stringify(form), headers())
                .then(created => {
                    setCerts(c => [...c, created]);
                    setModal(null);
                    showToast('✅ Сертификат создан');
                })
                .catch(() => showToast('❌ Ошибка создания'))
                .finally(() => setSaving(false));
        } else {
            request(`${API_URL}v1/achievements/${modal.id}`, 'PUT', JSON.stringify(form), headers())
                .then(updated => {
                    setCerts(c => c.map(x => x.id === modal.id ? {...x, ...updated} : x));
                    setModal(null);
                    showToast('✅ Сохранено');
                })
                .catch(() => showToast('❌ Ошибка сохранения'))
                .finally(() => setSaving(false));
        }
    };

    const handleDelete = (id) => {
        fetch(`${API_URL}v1/achievements/${id}`, {method: 'DELETE', headers: headers(), mode: 'cors'})
            .then(() => {
                setCerts(c => c.filter(x => x.id !== id));
                setConfirmId(null);
                showToast('🗑️ Удалено');
            })
            .catch(() => setConfirmId(null));
    };

    const handleAwardSuccess = (certId, newStudentIds) => {
        setCertStats(prev => ({
            ...prev,
            [certId]: {awarded: (prev[certId]?.awarded || 0) + newStudentIds.length}
        }));
    };

    const criteriaLabel = (type) => CRITERIA_TYPES.find(c => c.value === type)?.label || type;

    return (
        <div className="tc-container">
            {toast && <div className={`tc-toast ${toast.startsWith('❌') ? 'err' : ''}`}>{toast}</div>}

            {/* ── Header ── */}
            <div className="tc-header">
                <div>
                    <h2 className="tc-title">Управление сертификатами</h2>
                    <p className="tc-sub">Создавайте сертификаты и выдавайте их студентам</p>
                </div>
                <div className="tc-header-right">
                    <div className="tc-stat">🏅 <b>{certs.length}</b> сертификатов</div>
                    <button className="tc-add-btn" onClick={() => setModal('add')}>+ Создать сертификат</button>
                </div>
            </div>

            {/* ── List ── */}
            {loading ? (
                <div className="tc-loading">
                    <div className="tc-spinner"/>
                    <p>Загрузка...</p>
                </div>
            ) : certs.length === 0 ? (
                <div className="tc-empty">
                    <span>🏅</span>
                    <h3>Нет сертификатов</h3>
                    <p>Создайте первый сертификат для студентов</p>
                    <button className="tc-add-btn" onClick={() => setModal('add')}>+ Создать</button>
                </div>
            ) : (
                <div className="tc-list">
                    {certs.map((cert, i) => {
                        const awardedCount = certStats[cert.id]?.awarded || 0;
                        return (
                            <div key={cert.id} className="tc-row" style={{animationDelay: `${i * 0.05}s`}}>
                                <div className="tc-row-icon">
                                    {cert.badge_image_url
                                        ? <img src={cert.badge_image_url} alt=""/>
                                        : <span>🏆</span>}
                                </div>
                                <div className="tc-row-info">
                                    <div className="tc-row-name">{cert.name}</div>
                                    <div className="tc-row-desc">{cert.description}</div>
                                    <div className="tc-row-meta">
                                        <span className="tc-chip purple">+{cert.points_reward} pts</span>
                                        <span className="tc-chip gray">{criteriaLabel(cert.criteria_type)}</span>
                                        <span className="tc-chip blue">📊 {cert.criteria_value}</span>
                                        {awardedCount > 0 && (
                                            <span className="tc-chip green">✅ {awardedCount} студ.</span>
                                        )}
                                    </div>
                                </div>
                                <div className="tc-row-actions">
                                    <button className="tc-row-btn award" onClick={() => setAwardModal(cert)}>
                                        🎖️ Управлять
                                    </button>
                                    <div className="take_place">
                                        <button className="tc-row-btn edit" onClick={() => setModal(cert)}>✏️</button>
                                        <button className="tc-row-btn del"  onClick={() => setConfirmId(cert.id)}>🗑️</button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* ── Modals ── */}
            {modal && (
                <CertModal
                    key={modal === 'add' ? '__new__' : `edit-${modal.id}`}
                    item={modal === 'add' ? null : modal}
                    onSave={handleSave}
                    onClose={() => setModal(null)}
                    saving={saving}
                />
            )}

            {awardModal && (
                <AwardModal
                    cert={awardModal}
                    onClose={() => setAwardModal(null)}
                    onAwardSuccess={handleAwardSuccess}
                    showToast={showToast}
                />
            )}

            {/* ── Confirm Delete ── */}
            {confirmId && ReactDOM.createPortal(
                <div className="tc-overlay" onClick={() => setConfirmId(null)}>
                    <div className="tc-confirm" onClick={e => e.stopPropagation()}>
                        <div style={{fontSize: 40, marginBottom: 10}}>🗑️</div>
                        <h4>Удалить сертификат?</h4>
                        <p>Это действие нельзя отменить</p>
                        <div className="tc-confirm-btns">
                            <button className="tc-btn-cancel" onClick={() => setConfirmId(null)}>Отмена</button>
                            <button className="tc-btn-delete" onClick={() => handleDelete(confirmId)}>Удалить</button>
                        </div>
                    </div>
                </div>,
                document.body
            )}
        </div>
    );
};

export default TeacherCertificates;