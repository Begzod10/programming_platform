import React, { useState, useEffect, useCallback } from 'react';
import ReactDOM from 'react-dom';
import './MyGroups.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';

const COLORS = ['#6c5ce7','#00b894','#0984e3','#e17055','#fdcb6e','#a29bfe','#fd79a8','#00cec9'];

/* ── Lock body scroll ── */
const useLockBodyScroll = () => {
    useEffect(() => {
        document.body.style.overflow = 'hidden';
        return () => { document.body.style.overflow = ''; };
    }, []);
};

/* ── Group Form Modal ── */
const GroupModal = ({ group, onSave, onClose, saving }) => {
    const isEdit = !!group;
    const [form,  setForm]  = useState({ name: group?.name || '', description: group?.description || '' });
    const [error, setError] = useState('');

    useLockBodyScroll();

    useEffect(() => {
        const handleKey = (e) => { if (e.key === 'Escape') onClose(); };
        document.addEventListener('keydown', handleKey);
        return () => document.removeEventListener('keydown', handleKey);
    }, [onClose]);

    const handleSave = () => {
        if (!form.name.trim()) { setError('Введите название группы'); return; }
        onSave(form);
    };

    return ReactDOM.createPortal(
        <div className="mg-overlay" onClick={onClose}>
            <div className="mg-modal" onClick={e => e.stopPropagation()}>
                <div className="mg-modal-header">
                    <div className="mg-modal-header-icon">{isEdit ? '✏️' : '➕'}</div>
                    <h3>{isEdit ? 'Редактировать группу' : 'Создать группу'}</h3>
                    <button className="mg-modal-close" onClick={onClose}>✕</button>
                </div>
                <div className="mg-modal-body">
                    <div className="mg-field">
                        <label>Название группы *</label>
                        <input
                            placeholder="React - Группа 1"
                            value={form.name}
                            onChange={e => { setForm(f => ({ ...f, name: e.target.value })); setError(''); }}
                            className={error ? 'error' : ''}
                        />
                        {error && <span className="mg-error">{error}</span>}
                    </div>
                    <div className="mg-field">
                        <label>Описание</label>
                        <textarea
                            placeholder="Краткое описание группы..."
                            rows={3}
                            value={form.description}
                            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                        />
                    </div>
                </div>
                <div className="mg-modal-footer">
                    <button className="mg-btn-cancel" onClick={onClose}>Отмена</button>
                    <button className="mg-btn-save" onClick={handleSave} disabled={saving}>
                        {saving ? '⏳ Сохранение...' : isEdit ? '💾 Сохранить' : '✅ Создать'}
                    </button>
                </div>
            </div>
        </div>,
        document.body
    );
};

/* ── Group Detail Modal — полностью переработанный ── */
const GroupDetailModal = ({ group, onClose, allStudents, setAllStudents }) => {
    const { request } = useHttp();

    const [tab,           setTab]           = useState('in_group');  // 'in_group' | 'not_in_group'
    const [search,        setSearch]        = useState('');
    const [adding,        setAdding]        = useState(null);   // studentId
    const [removing,      setRemoving]      = useState(null);   // studentId
    const [confirmRemove, setConfirmRemove] = useState(null);   // student obj
    const [toast,         setToast]         = useState('');

    useLockBodyScroll();

    useEffect(() => {
        const handleKey = (e) => { if (e.key === 'Escape') onClose(); };
        document.addEventListener('keydown', handleKey);
        return () => document.removeEventListener('keydown', handleKey);
    }, [onClose]);

    const showToast = useCallback((msg) => {
        setToast(msg);
        setTimeout(() => setToast(''), 2500);
    }, []);

    /* Разбивка студентов */
    const inGroup    = allStudents.filter(s => s.group_id === group.id);
    const notInGroup = allStudents.filter(s => s.group_id !== group.id);

    const filteredIn  = inGroup.filter(s => {
        const q = search.toLowerCase();
        return (s.full_name || s.username || '').toLowerCase().includes(q)
            || (s.email || '').toLowerCase().includes(q);
    });
    const filteredOut = notInGroup.filter(s => {
        const q = search.toLowerCase();
        return (s.full_name || s.username || '').toLowerCase().includes(q)
            || (s.email || '').toLowerCase().includes(q);
    });

    /* Добавить студента */
    const handleAdd = async (student) => {
        setAdding(student.id);
        try {
            await request(
                `${API_URL}v1/groups/${group.id}/add-student/${student.id}`,
                'PATCH', JSON.stringify({}), headers()
            );
            setAllStudents(prev => prev.map(s => s.id === student.id ? { ...s, group_id: group.id } : s));
            showToast(`✅ ${student.full_name || student.username} добавлен`);
        } catch {
            showToast('❌ Ошибка добавления');
        } finally {
            setAdding(null);
        }
    };

    /* Убрать студента */
    const handleRemove = async (student) => {
        setRemoving(student.id);
        try {
            await request(
                `${API_URL}v1/groups/${group.id}/remove-student/${student.id}`,
                'PATCH', JSON.stringify({}), headers()
            );
            setAllStudents(prev => prev.map(s => s.id === student.id ? { ...s, group_id: null } : s));
            setConfirmRemove(null);
            showToast(`🗑️ ${student.full_name || student.username} убран из группы`);
        } catch {
            // оптимистичное обновление
            setAllStudents(prev => prev.map(s => s.id === student.id ? { ...s, group_id: null } : s));
            setConfirmRemove(null);
        } finally {
            setRemoving(null);
        }
    };

    const av = (s) => (s.full_name || s.username || '?')[0].toUpperCase();

    const totalStudents = allStudents.length;
    const inGroupPct    = totalStudents > 0 ? Math.round((inGroup.length / totalStudents) * 100) : 0;

    return ReactDOM.createPortal(
        <div className="mg-overlay" onClick={onClose}>
            <div className="mg-detail-modal" onClick={e => e.stopPropagation()}>

                {/* ── Header ── */}
                <div className="mg-detail-header" style={{ background: `linear-gradient(145deg, ${group.color}22 0%, ${group.color}08 100%)`, borderBottom: `3px solid ${group.color}` }}>
                    <div className="mg-detail-hero">
                        <div className="mg-detail-badge" style={{ background: group.color }}>
                            👥
                        </div>
                        <div className="mg-detail-meta">
                            <h3>{group.name}</h3>
                            {group.description && <p>{group.description}</p>}
                            <div className="mg-detail-chips">
                                <span className="mg-detail-chip" style={{ color: group.color, background: `${group.color}15`, border: `1px solid ${group.color}30` }}>
                                    👥 {inGroup.length} студентов
                                </span>
                                {group.created_at && (
                                    <span className="mg-detail-chip neutral">
                                        📅 {new Date(group.created_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })}
                                    </span>
                                )}
                            </div>
                        </div>
                        <button className="mg-modal-close" onClick={onClose}>✕</button>
                    </div>

                    {/* Progress bar — % студентов из всех в этой группе */}
                    {totalStudents > 0 && (
                        <div className="mg-detail-progress">
                            <div className="mg-detail-progress-labels">
                                <span>Заполненность группы</span>
                                <span style={{ color: group.color }}>{inGroup.length} / {totalStudents} ({inGroupPct}%)</span>
                            </div>
                            <div className="mg-detail-progress-track">
                                <div
                                    className="mg-detail-progress-fill"
                                    style={{ width: `${inGroupPct}%`, background: `linear-gradient(90deg, ${group.color}, ${group.color}aa)` }}
                                />
                            </div>
                        </div>
                    )}
                </div>

                {/* ── Tabs ── */}
                <div className="mg-tabs">
                    <button
                        className={`mg-tab ${tab === 'in_group' ? 'active' : ''}`}
                        style={tab === 'in_group' ? { color: group.color, borderBottomColor: group.color } : {}}
                        onClick={() => { setTab('in_group'); setSearch(''); }}
                    >
                        <span className="mg-tab-dot" style={{ background: tab === 'in_group' ? group.color : 'rgba(26,26,46,0.2)' }}/>
                        В группе
                        <span className="mg-tab-count" style={tab === 'in_group' ? { background: `${group.color}15`, color: group.color } : {}}>
                            {inGroup.length}
                        </span>
                    </button>
                    <button
                        className={`mg-tab ${tab === 'not_in_group' ? 'active' : ''}`}
                        style={tab === 'not_in_group' ? { color: group.color, borderBottomColor: group.color } : {}}
                        onClick={() => { setTab('not_in_group'); setSearch(''); }}
                    >
                        <span className="mg-tab-dot" style={{ background: tab === 'not_in_group' ? group.color : 'rgba(26,26,46,0.2)' }}/>
                        Не в группе
                        <span className="mg-tab-count" style={tab === 'not_in_group' ? { background: `${group.color}15`, color: group.color } : {}}>
                            {notInGroup.length}
                        </span>
                    </button>
                </div>

                {/* ── Body ── */}
                <div className="mg-detail-body">
                    {/* Search */}
                    <div className="mg-search-wrap">
                        <span className="mg-search-icon">🔍</span>
                        <input
                            value={search}
                            placeholder={tab === 'in_group' ? 'Поиск в группе...' : 'Поиск студентов...'}
                            onChange={e => setSearch(e.target.value)}
                            className="mg-search-input"
                        />
                        {search && (
                            <button className="mg-search-clear" onClick={() => setSearch('')}>✕</button>
                        )}
                    </div>

                    {/* IN GROUP tab */}
                    {tab === 'in_group' && (
                        <div className="mg-student-section">
                            {filteredIn.length > 0 && (
                                <div className="mg-list-toolbar">
                                    <span className="mg-list-count">{filteredIn.length} студентов</span>
                                </div>
                            )}
                            <div className="mg-members-list">
                                {filteredIn.length === 0 ? (
                                    <div className="mg-empty-list">
                                        <span>{search ? '🔍' : '📭'}</span>
                                        <p>{search ? 'Студентов не найдено' : 'В группе пока нет студентов'}</p>
                                        {!search && (
                                            <button
                                                className="mg-tab-switch-hint"
                                                onClick={() => setTab('not_in_group')}
                                            >
                                                Добавить студентов →
                                            </button>
                                        )}
                                    </div>
                                ) : filteredIn.map(s => (
                                    <div key={s.id} className="mg-member-row in-row">
                                        <div className="mg-member-avatar-wrap" style={{ background: `${group.color}18` }}>
                                            {s.avatar_url
                                                ? <img src={s.avatar_url} alt="" className="mg-member-avatar-img"/>
                                                : <span className="mg-member-av-letter" style={{ color: group.color }}>{av(s)}</span>
                                            }
                                        </div>
                                        <div className="mg-member-info">
                                            <span className="mg-member-name">{s.full_name || s.username}</span>
                                            <span className="mg-member-email">{s.email}</span>
                                        </div>
                                        {s.current_level && (
                                            <span className={`mg-level-badge ${(s.current_level || 'beginner').toLowerCase()}`}>
                                                {s.current_level}
                                            </span>
                                        )}
                                        <button
                                            className="mg-remove-btn"
                                            onClick={() => setConfirmRemove(s)}
                                            disabled={removing === s.id}
                                            title="Убрать из группы"
                                        >
                                            {removing === s.id ? '⏳' : '✕'}
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* NOT IN GROUP tab */}
                    {tab === 'not_in_group' && (
                        <div className="mg-student-section">
                            {filteredOut.length > 0 && (
                                <div className="mg-list-toolbar">
                                    <span className="mg-list-count">{filteredOut.length} доступных</span>
                                </div>
                            )}
                            <div className="mg-members-list">
                                {filteredOut.length === 0 ? (
                                    <div className="mg-empty-list">
                                        <span>{search ? '🔍' : '🎉'}</span>
                                        <p>{search ? 'Не найдено' : 'Все студенты уже в группах!'}</p>
                                    </div>
                                ) : filteredOut.map(s => (
                                    <div key={s.id} className="mg-member-row out-row">
                                        <div className="mg-member-avatar-wrap">
                                            {s.avatar_url
                                                ? <img src={s.avatar_url} alt="" className="mg-member-avatar-img"/>
                                                : <span className="mg-member-av-letter">{av(s)}</span>
                                            }
                                        </div>
                                        <div className="mg-member-info">
                                            <span className="mg-member-name">{s.full_name || s.username}</span>
                                            <span className="mg-member-email">{s.email}</span>
                                            {s.group_id && (
                                                <span className="mg-member-other-group">Уже в другой группе</span>
                                            )}
                                        </div>
                                        {s.current_level && (
                                            <span className={`mg-level-badge ${(s.current_level || 'beginner').toLowerCase()}`}>
                                                {s.current_level}
                                            </span>
                                        )}
                                        <button
                                            className="mg-add-btn-sm"
                                            style={{ background: `linear-gradient(135deg, ${group.color}, ${group.color}cc)` }}
                                            onClick={() => handleAdd(s)}
                                            disabled={adding === s.id}
                                        >
                                            {adding === s.id ? '⏳' : '+ Добавить'}
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* ── Footer ── */}
                <div className="mg-detail-foot">
                    <button className="mg-btn-cancel full" onClick={onClose}>Закрыть</button>
                </div>

                {/* ── Confirm Remove ── */}
                {confirmRemove && (
                    <div className="mg-confirm-overlay" onClick={() => setConfirmRemove(null)}>
                        <div className="mg-confirm-popup" onClick={e => e.stopPropagation()}>
                            <div className="mg-confirm-icon-big">⚠️</div>
                            <h4>Убрать из группы?</h4>
                            <p>
                                <b>{confirmRemove.full_name || confirmRemove.username}</b> будет убран из группы
                                <br/><b>«{group.name}»</b>
                            </p>
                            <div className="mg-confirm-actions">
                                <button className="mg-btn-cancel" onClick={() => setConfirmRemove(null)}>Отмена</button>
                                <button
                                    className="mg-btn-delete"
                                    onClick={() => handleRemove(confirmRemove)}
                                    disabled={!!removing}
                                >
                                    {removing ? '⏳...' : '✕ Убрать'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Toast внутри модалки */}
                {toast && (
                    <div className={`mg-inner-toast ${toast.startsWith('❌') ? 'err' : ''}`}>{toast}</div>
                )}
            </div>
        </div>,
        document.body
    );
};

/* ── Main ── */
const MyGroups = () => {
    const { request } = useHttp();

    const [groups,          setGroups]         = useState([]);
    const [allStudents,     setAllStudents]     = useState([]);
    const [loading,         setLoading]         = useState(true);
    const [loadingStudents, setLoadingStudents] = useState(true);
    const [modal,           setModal]           = useState(null);
    const [detailGroupId,   setDetailGroupId]   = useState(null);
    const [confirmId,       setConfirmId]       = useState(null);
    const [saving,          setSaving]          = useState(false);

    /* Load groups */
    useEffect(() => {
        request(`${API_URL}v1/groups/`, 'GET', null, headers())
            .then(data => {
                const list = Array.isArray(data) ? data : [];
                setGroups(list.map((g, i) => ({ ...g, color: COLORS[i % COLORS.length] })));
            })
            .catch(() => setGroups([]))
            .finally(() => setLoading(false));
    }, []);

    /* Load all students once */
    useEffect(() => {
        request(`${API_URL}v1/student/?limit=100`, 'GET', null, headers())
            .then(data => setAllStudents(Array.isArray(data) ? data : []))
            .catch(() => setAllStudents([]))
            .finally(() => setLoadingStudents(false));
    }, []);

    /* Save group */
    const handleSave = (form) => {
        setSaving(true);
        if (modal === 'add') {
            request(`${API_URL}v1/groups/`, 'POST', JSON.stringify(form), headers())
                .then(created => {
                    setGroups(gs => [...gs, { ...created, color: COLORS[gs.length % COLORS.length] }]);
                    setModal(null);
                })
                .catch(() => {})
                .finally(() => setSaving(false));
        } else {
            request(`${API_URL}v1/groups/${modal.id}`, 'PUT', JSON.stringify(form), headers())
                .then(updated => {
                    setGroups(gs => gs.map(g => g.id === modal.id ? { ...g, ...updated } : g));
                    setModal(null);
                })
                .catch(() => {})
                .finally(() => setSaving(false));
        }
    };

    /* Delete group */
    const handleDelete = (id) => {
        fetch(`${API_URL}v1/groups/${id}`, { method: 'DELETE', mode: 'cors', headers: headers() })
            .then(() => {
                setGroups(gs => gs.filter(g => g.id !== id));
                setConfirmId(null);
                if (detailGroupId === id) setDetailGroupId(null);
            })
            .catch(() => setConfirmId(null));
    };

    const detailGroup = detailGroupId ? groups.find(g => g.id === detailGroupId) || null : null;

    return (
        <div className="mg-container">
            <div className="mg-header">
                <div>
                    <h2>Мои Группы</h2>
                    <p className="mg-subtitle">Управляйте группами и студентами</p>
                </div>
                <button className="mg-add-btn" onClick={() => setModal('add')}>
                    <span>➕</span>
                    <span>Создать группу</span>
                </button>
            </div>

            <div className="mg-stats-row">
                <div className="mg-stat-chip">📚 Групп: <b>{groups.length}</b></div>
                {!loadingStudents && (
                    <div className="mg-stat-chip">👥 Студентов: <b>{allStudents.length}</b></div>
                )}
            </div>

            {loading ? (
                <div className="mg-empty">
                    <div className="mg-empty-icon">⏳</div>
                    <p>Загрузка групп...</p>
                </div>
            ) : groups.length === 0 ? (
                <div className="mg-empty">
                    <div className="mg-empty-icon">📭</div>
                    <h3>Групп пока нет</h3>
                    <p>Создайте первую группу и добавьте студентов</p>
                    <button className="mg-add-btn" onClick={() => setModal('add')}>➕ Создать группу</button>
                </div>
            ) : (
                <div className="mg-grid">
                    {groups.map(group => {
                        const count = allStudents.filter(s => s.group_id === group.id).length;
                        return (
                            <div key={group.id} className="mg-card" onClick={() => setDetailGroupId(group.id)}>
                                <div className="mg-card-banner" style={{ background: `linear-gradient(135deg, ${group.color}, ${group.color}bb)` }}>
                                    <div className="mg-card-banner-icon">👥</div>
                                </div>
                                <div className="mg-card-body">
                                    <div className="mg-card-top">
                                        <div className="mg-card-title-wrap">
                                            <h3>{group.name}</h3>
                                            {group.description && <p className="mg-card-desc">{group.description}</p>}
                                        </div>
                                        <div className="mg-card-actions">
                                            <button
                                                className="mg-icon-btn edit"
                                                aria-label="Редактировать"
                                                onClick={e => { e.stopPropagation(); setModal(group); }}
                                            >✏️</button>
                                            <button
                                                className="mg-icon-btn del"
                                                aria-label="Удалить"
                                                onClick={e => { e.stopPropagation(); setConfirmId(group.id); }}
                                            >🗑️</button>
                                        </div>
                                    </div>
                                    <div className="mg-card-stats">
                                        <span className="mg-card-stat">👥 {count} студентов</span>
                                        <span className="mg-card-stat">
                                            📅 {group.created_at ? new Date(group.created_at).toLocaleDateString('ru-RU') : '—'}
                                        </span>
                                    </div>
                                    <button
                                        className="mg-card-open-btn"
                                        style={{ background: `linear-gradient(135deg, ${group.color}, ${group.color}cc)` }}
                                        onClick={e => { e.stopPropagation(); setDetailGroupId(group.id); }}
                                    >
                                        Управлять группой →
                                    </button>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {modal && (
                <GroupModal
                    group={modal === 'add' ? null : modal}
                    onSave={handleSave}
                    onClose={() => setModal(null)}
                    saving={saving}
                />
            )}

            {detailGroup && (
                <GroupDetailModal
                    group={detailGroup}
                    onClose={() => setDetailGroupId(null)}
                    allStudents={allStudents}
                    setAllStudents={setAllStudents}
                />
            )}

            {confirmId && ReactDOM.createPortal(
                <div className="mg-overlay" onClick={() => setConfirmId(null)}>
                    <div className="mg-confirm" onClick={e => e.stopPropagation()}>
                        <div className="mg-confirm-icon">🗑️</div>
                        <h4>Удалить группу?</h4>
                        <p>Это действие нельзя отменить</p>
                        <div className="mg-confirm-actions">
                            <button className="mg-btn-cancel" onClick={() => setConfirmId(null)}>Отмена</button>
                            <button className="mg-btn-delete" onClick={() => handleDelete(confirmId)}>Удалить</button>
                        </div>
                    </div>
                </div>,
                document.body
            )}
        </div>
    );
};

export default MyGroups;