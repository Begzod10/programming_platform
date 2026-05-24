import { useState, useEffect, useRef, useCallback } from 'react';
import ReactDOM from 'react-dom';
import './MyProjects.css';
import ProjectCard from './ProjectCard';
import { API_URL, useHttp, headers } from '../../../api/search/base';

const DIFFICULTIES = ['Easy', 'Medium', 'Hard'];

const EMPTY = {
    title: '', description: '', github_url: '',
    live_demo_url: '', technologies_used: '', difficulty_level: 'Easy',
};

/* ── Modal Portal ── */
const Modal = ({ onClose, children, wide }) => ReactDOM.createPortal(
    <div className="mp-overlay" onClick={onClose}>
        <div className={`mp-modal ${wide ? 'mp-detail-modal' : ''}`} onClick={e => e.stopPropagation()}>
            {children}
        </div>
    </div>,
    document.body
);

/* ── ZIP Drop Zone ── */
const ZipDropZone = ({ selectedFile, onFileSelect, uploading, compact = false }) => {
    const fileInputRef = useRef(null);
    const [dragging, setDragging] = useState(false);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files[0];
        if (file && file.name.endsWith('.zip')) onFileSelect(file);
    }, [onFileSelect]);

    const handleDragOver = (e) => { e.preventDefault(); setDragging(true); };
    const handleDragLeave = () => setDragging(false);

    return (
        <div className={`mp-dropzone ${dragging ? 'mp-dropzone-drag' : ''} ${compact ? 'mp-dropzone-compact' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => !uploading && fileInputRef.current?.click()}
        >
            <input
                ref={fileInputRef}
                type="file"
                accept=".zip"
                style={{ display: 'none' }}
                onChange={e => {
                    const file = e.target.files[0];
                    if (file) { onFileSelect(file); e.target.value = ''; }
                }}
            />
            {selectedFile ? (
                <div className="mp-dropzone-selected">
                    <span className="mp-dropzone-icon">📦</span>
                    <div className="mp-dropzone-info">
                        <span className="mp-file-name">{selectedFile.name}</span>
                        <span className={`mp-file-size ${selectedFile.size > 15 * 1024 * 1024 ? 'mp-overlimit' : ''}`}>
                            {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                            {selectedFile.size > 15 * 1024 * 1024 && ' · ⚠️ Превышает 15MB'}
                        </span>
                    </div>
                    <button className="mp-dropzone-clear" onClick={e => { e.stopPropagation(); onFileSelect(null); }}>✕</button>
                </div>
            ) : (
                <div className="mp-dropzone-placeholder">
                    <span className="mp-dropzone-icon mp-dropzone-icon-empty">{dragging ? '🎯' : '📁'}</span>
                    <span className="mp-dropzone-text">
                        {dragging ? 'Отпустите файл' : compact ? 'Перетащите .zip или нажмите' : 'Перетащите .zip архив сюда или нажмите для выбора'}
                    </span>
                    {!compact && <span className="mp-dropzone-hint">Максимум 15 MB · только .zip</span>}
                </div>
            )}
            {selectedFile && (
                <div className="mp-file-bar-wrap">
                    <div className="mp-file-bar" style={{ width: `${Math.min((selectedFile.size / (15 * 1024 * 1024)) * 100, 100)}%` }} />
                </div>
            )}
        </div>
    );
};

/* ── Shared form fields ── */
const ProjectFormFields = ({ form, errors, set, zipFile, onZipSelect }) => (
    <>
        <div className="mp-field">
            <label>Название *</label>
            <input placeholder="E-commerce Backend" value={form.title}
                onChange={e => set('title', e.target.value)}
                className={errors.title ? 'mp-input-error' : ''} />
            {errors.title && <span className="mp-error">{errors.title}</span>}
        </div>
        <div className="mp-field">
            <label>Описание *</label>
            <textarea placeholder="Краткое описание..." value={form.description}
                onChange={e => set('description', e.target.value)}
                className={errors.description ? 'mp-input-error' : ''} rows={3} />
            {errors.description && <span className="mp-error">{errors.description}</span>}
        </div>
        <div className="mp-field">
            <label>GitHub URL *</label>
            <input placeholder="https://github.com/username/repo" value={form.github_url}
                onChange={e => set('github_url', e.target.value)}
                className={errors.github_url ? 'mp-input-error' : ''} />
            {errors.github_url && <span className="mp-error">{errors.github_url}</span>}
        </div>
        <div className="mp-field">
            <label>Live Demo URL</label>
            <input placeholder="https://myproject.com" value={form.live_demo_url}
                onChange={e => set('live_demo_url', e.target.value)} />
        </div>
        <div className="mp-field">
            <label>Технологии (через запятую)</label>
            <input placeholder="React, FastAPI, PostgreSQL" value={form.technologies_used}
                onChange={e => set('technologies_used', e.target.value)} />
        </div>
        <div className="mp-field">
            <label>Сложность</label>
            <select value={form.difficulty_level} onChange={e => set('difficulty_level', e.target.value)}>
                {DIFFICULTIES.map(d => <option key={d}>{d}</option>)}
            </select>
        </div>

        {/* ZIP upload in form */}
        <div className="mp-field">
            <label>📦 ZIP-архив <span className="mp-label-optional">(необязательно)</span></label>
            <ZipDropZone selectedFile={zipFile} onFileSelect={onZipSelect} compact />
        </div>
    </>
);

function MyProjects() {
    const { request } = useHttp();

    const [projects,   setProjects]   = useState([]);
    const [loading,    setLoading]    = useState(true);
    const [addModal,   setAddModal]   = useState(false);
    const [editModal,  setEditModal]  = useState(false);
    const [detail,     setDetail]     = useState(null);
    const [form,       setForm]       = useState({ ...EMPTY });
    const [errors,     setErrors]     = useState({});
    const [saving,     setSaving]     = useState(false);
    const [apiError,   setApiError]   = useState('');

    // ZIP upload state (detail modal)
    const [uploading,    setUploading]    = useState(false);
    const [uploadMsg,    setUploadMsg]    = useState('');
    const [selectedFile, setSelectedFile] = useState(null);

    // ZIP for create/edit form
    const [formZipFile, setFormZipFile] = useState(null);

    // File URL patch state
    const [fileUrlInput,   setFileUrlInput]   = useState('');
    const [fileUrlSaving,  setFileUrlSaving]  = useState(false);
    const [fileUrlMsg,     setFileUrlMsg]     = useState('');
    const [showFileUrlEdit, setShowFileUrlEdit] = useState(false);

    // AI Review state
    const [aiLoading,  setAiLoading]  = useState(false);
    const [aiResult,   setAiResult]   = useState('');

    useEffect(() => {
        request(`${API_URL}v1/project/my`, 'GET', null, headers())
            .then(data => setProjects(Array.isArray(data) ? data : []))
            .catch(() => setProjects([]))
            .finally(() => setLoading(false));
    }, []);

    const set = (k, v) => {
        setForm(f => ({ ...f, [k]: v }));
        setErrors(e => ({ ...e, [k]: '' }));
    };

    const validate = () => {
        const e = {};
        if (!form.title.trim())       e.title       = 'Введите название';
        if (!form.description.trim()) e.description = 'Введите описание';
        else if (form.description.trim().length < 10) e.description = 'Минимум 10 символов';
        if (!form.github_url.trim())  e.github_url  = 'Введите GitHub ссылку';
        setErrors(e);
        return !Object.keys(e).length;
    };

    const buildBody = () => ({
        title:             form.title,
        description:       form.description,
        github_url:        form.github_url,
        live_demo_url:     form.live_demo_url || '',
        technologies_used: form.technologies_used.split(',').map(t => t.trim()).filter(Boolean),
        difficulty_level:  form.difficulty_level,
        project_files:     '',
    });

    /* ── Upload ZIP helper ── */
    const uploadZipForProject = async (projectId, file) => {
        if (!file) return;
        if (file.size > 15 * 1024 * 1024) throw new Error('TOO_LARGE');
        const formData = new FormData();
        formData.append('file', file);
        const h = headers();
        delete h['Content-Type'];
        const r = await fetch(`${API_URL}v1/project/${projectId}/upload-zip`, {
            method: 'POST', headers: h, body: formData,
        });
        if (!r.ok) throw new Error('UPLOAD_FAILED');
    };

    /* ── CREATE ── */
    const handleCreate = async () => {
        if (!validate()) return;
        setSaving(true); setApiError('');
        try {
            const res = await request(`${API_URL}v1/project/`, 'POST', JSON.stringify(buildBody()), headers());
            // Upload ZIP if attached
            if (formZipFile) {
                try { await uploadZipForProject(res.id, formZipFile); } catch (_) { /* non-fatal */ }
            }
            setProjects(p => [res, ...p]);
            setAddModal(false);
            setForm({ ...EMPTY });
            setFormZipFile(null);
        } catch {
            setApiError('Ошибка при создании проекта');
        } finally {
            setSaving(false);
        }
    };

    /* ── UPDATE ── */
    const handleUpdate = async () => {
        if (!validate()) return;
        setSaving(true); setApiError('');
        try {
            const res = await request(`${API_URL}v1/project/${detail.id}`, 'PUT', JSON.stringify(buildBody()), headers());
            if (formZipFile) {
                try { await uploadZipForProject(res.id, formZipFile); } catch (_) { /* non-fatal */ }
            }
            setProjects(p => p.map(pr => pr.id === res.id ? res : pr));
            setDetail(res);
            setEditModal(false);
            setFormZipFile(null);
        } catch {
            setApiError('Ошибка при обновлении проекта');
        } finally {
            setSaving(false);
        }
    };

    /* ── SUBMIT ── */
    const handleSubmit = (projectId) => {
        request(`${API_URL}v1/project/${projectId}/submit`, 'POST', JSON.stringify({}), headers())
            .then(() => {
                setProjects(p => p.map(pr => pr.id === projectId ? { ...pr, status: 'Submitted' } : pr));
                setDetail(d => d ? { ...d, status: 'Submitted' } : d);
            })
            .catch(() => alert('Ошибка при отправке'));
    };

    /* ── DELETE ── */
    const handleDelete = (projectId) => {
        if (!window.confirm('Удалить проект?')) return;
        request(`${API_URL}v1/project/${projectId}`, 'DELETE', null, headers())
            .then(() => { setProjects(p => p.filter(pr => pr.id !== projectId)); setDetail(null); })
            .catch(() => alert('Ошибка при удалении'));
    };

    /* ── UPLOAD ZIP (detail) ── */
    const handleZipUpload = (projectId, file) => {
        if (!file) return;
        if (file.size > 15 * 1024 * 1024) {
            setUploadMsg('❌ Файл слишком большой (макс. 15MB)');
            return;
        }
        const formData = new FormData();
        formData.append('file', file);
        setUploading(true); setUploadMsg('');
        const h = headers();
        delete h['Content-Type'];
        fetch(`${API_URL}v1/project/${projectId}/upload-zip`, {
            method: 'POST', headers: h, body: formData,
        })
            .then(async r => {
                if (!r.ok) throw new Error();
                setUploadMsg('✅ ZIP загружен успешно');
                setSelectedFile(null);
                return request(`${API_URL}v1/project/${projectId}`, 'GET', null, headers());
            })
            .then(res => {
                if (res) {
                    setProjects(p => p.map(pr => pr.id === projectId ? res : pr));
                    setDetail(res);
                }
            })
            .catch(() => setUploadMsg('❌ Ошибка загрузки ZIP'))
            .finally(() => setUploading(false));
    };

    /* ── PATCH FILE URL ── */
    const handlePatchFileUrl = () => {
        if (!fileUrlInput.trim()) return;
        setFileUrlSaving(true); setFileUrlMsg('');
        request(
            `${API_URL}v1/project/${detail.id}/file`,
            'PATCH',
            JSON.stringify({ file_url: fileUrlInput.trim() }),
            headers()
        )
            .then(() => {
                const updated = { ...detail, project_files: fileUrlInput.trim() };
                setProjects(p => p.map(pr => pr.id === detail.id ? updated : pr));
                setDetail(updated);
                setFileUrlMsg('✅ Ссылка обновлена');
                setShowFileUrlEdit(false);
            })
            .catch(() => setFileUrlMsg('❌ Ошибка обновления ссылки'))
            .finally(() => setFileUrlSaving(false));
    };

    /* ── AI REVIEW ── */
    const handleAiReview = (projectId) => {
        setAiLoading(true); setAiResult('');
        request(`${API_URL}v1/project/${projectId}/ai-review`, 'POST', JSON.stringify({}), headers())
            .then(res => setAiResult(typeof res === 'string' ? res : JSON.stringify(res)))
            .catch(() => setAiResult('❌ Ошибка AI-проверки'))
            .finally(() => setAiLoading(false));
    };

    /* ── OPEN EDIT ── */
    const openEdit = () => {
        setForm({
            title:             detail.title || '',
            description:       detail.description || '',
            github_url:        detail.github_url || '',
            live_demo_url:     detail.live_demo_url || '',
            technologies_used: (detail.technologies_used || []).join(', '),
            difficulty_level:  detail.difficulty_level || 'Easy',
        });
        setFormZipFile(null);
        setErrors({}); setApiError('');
        setEditModal(true);
    };

    const openAdd = () => {
        setForm({ ...EMPTY }); setErrors({}); setApiError('');
        setFormZipFile(null);
        setAddModal(true);
    };

    const closeDetail = () => {
        setDetail(null);
        setSelectedFile(null);
        setUploadMsg('');
        setAiResult('');
        setFileUrlInput('');
        setFileUrlMsg('');
        setShowFileUrlEdit(false);
    };

    return (
        <div className="mp-container item-fade-in">

            {/* Header */}
            <div className="mp-header">
                <div>
                    <h2>Мои Проекты</h2>
                    <p className="mp-subtitle">Загружайте проекты и получайте очки</p>
                </div>
                <button className="mp-add-btn" onClick={openAdd}>➕ Загрузить проект</button>
            </div>

            {/* List */}
            {loading ? (
                <div className="mp-loading"><div className="mp-spinner" /><p>Загрузка...</p></div>
            ) : projects.length === 0 ? (
                <div className="mp-empty">
                    <span>📂</span>
                    <p>У вас пока нет проектов</p>
                    <button className="mp-add-btn" onClick={openAdd}>Загрузить первый</button>
                </div>
            ) : (
                <div className="projects-grid">
                    {projects.map(p => (
                        <ProjectCard
                            key={p.id}
                            title={p.title}
                            status={p.status}
                            difficulty={p.difficulty_level}
                            points={p.points_earned}
                            techStack={p.technologies_used || []}
                            grade={p.grade}
                            viewsCount={p.views_count || 0}
                            onDetails={() => { setAiResult(''); setUploadMsg(''); setDetail(p); }}
                        />
                    ))}
                </div>
            )}

            {/* ═══════════ ADD MODAL ═══════════ */}
            {addModal && (
                <Modal onClose={() => setAddModal(false)}>
                    <div className="mp-modal-header">
                        <h3>📁 Загрузить проект</h3>
                        <button className="mp-close" onClick={() => setAddModal(false)}>✕</button>
                    </div>
                    <div className="mp-modal-body">
                        {apiError && <div className="mp-api-error">{apiError}</div>}
                        <ProjectFormFields form={form} errors={errors} set={set} zipFile={formZipFile} onZipSelect={setFormZipFile} />
                    </div>
                    <div className="mp-modal-footer">
                        <button className="mp-btn-cancel" onClick={() => setAddModal(false)}>Отмена</button>
                        <button className="mp-btn-save" onClick={handleCreate} disabled={saving}>
                            {saving ? '⏳ Сохранение...' : '✅ Создать'}
                        </button>
                    </div>
                </Modal>
            )}

            {/* ═══════════ EDIT MODAL ═══════════ */}
            {editModal && (
                <Modal onClose={() => setEditModal(false)}>
                    <div className="mp-modal-header">
                        <h3>✏️ Редактировать проект</h3>
                        <button className="mp-close" onClick={() => setEditModal(false)}>✕</button>
                    </div>
                    <div className="mp-modal-body">
                        {apiError && <div className="mp-api-error">{apiError}</div>}
                        <ProjectFormFields form={form} errors={errors} set={set} zipFile={formZipFile} onZipSelect={setFormZipFile} />
                    </div>
                    <div className="mp-modal-footer">
                        <button className="mp-btn-cancel" onClick={() => setEditModal(false)}>Отмена</button>
                        <button className="mp-btn-save" onClick={handleUpdate} disabled={saving}>
                            {saving ? '⏳ Сохранение...' : '💾 Сохранить'}
                        </button>
                    </div>
                </Modal>
            )}

            {/* ═══════════ DETAIL MODAL ═══════════ */}
            {detail && (
                <Modal onClose={closeDetail} wide>
                    <div className="mp-modal-header">
                        <h3>📋 {detail.title}</h3>
                        <button className="mp-close" onClick={closeDetail}>✕</button>
                    </div>
                    <div className="mp-modal-body">

                        {/* Badges */}
                        <div className="mp-detail-badges">
                            <span className={`mp-diff ${
                                detail.difficulty_level === 'Easy' ? 'mp-diff-easy' :
                                detail.difficulty_level === 'Medium' ? 'mp-diff-medium' : 'mp-diff-hard'
                            }`}>{detail.difficulty_level}</span>
                            <span className={`mp-status ${
                                { Draft: 'mp-status-draft', Submitted: 'mp-status-pending',
                                  'Under Review': 'mp-status-pending', Approved: 'mp-status-approved',
                                  Rejected: 'mp-status-denied' }[detail.status] || ''
                            }`}>
                                {{ Draft: 'Черновик', Submitted: 'Отправлен', 'Under Review': 'На проверке',
                                   Approved: 'Одобрен', Rejected: 'Отклонён' }[detail.status] || detail.status}
                            </span>
                            {detail.grade && <span className={`mp-grade mp-grade-${detail.grade}`}>Оценка: {detail.grade}</span>}
                        </div>

                        {/* Stats row */}
                        <div className="mp-stats-row">
                            <div className="mp-stat">
                                <span className="mp-stat-icon">🏆</span>
                                <span className="mp-stat-val">{detail.points_earned ?? 0}</span>
                                <span className="mp-stat-label">очков</span>
                            </div>
                            <div className="mp-stat">
                                <span className="mp-stat-icon">👁️</span>
                                <span className="mp-stat-val">{detail.views_count ?? 0}</span>
                                <span className="mp-stat-label">просмотров</span>
                            </div>
                        </div>

                        {/* Description */}
                        <div className="mp-detail-row">
                            <span className="mp-detail-label">Описание</span>
                            <span className="mp-detail-value">{detail.description || '—'}</span>
                        </div>

                        {/* GitHub */}
                        {detail.github_url && (
                            <div className="mp-detail-row">
                                <span className="mp-detail-label">GitHub</span>
                                <a href={detail.github_url} target="_blank" rel="noreferrer" className="mp-link">{detail.github_url}</a>
                            </div>
                        )}

                        {/* Live Demo */}
                        {detail.live_demo_url && (
                            <div className="mp-detail-row">
                                <span className="mp-detail-label">Live Demo</span>
                                <a href={detail.live_demo_url} target="_blank" rel="noreferrer" className="mp-link">{detail.live_demo_url}</a>
                            </div>
                        )}

                        {/* Technologies */}
                        {(detail.technologies_used || []).length > 0 && (
                            <div className="mp-detail-row">
                                <span className="mp-detail-label">Технологии</span>
                                <div className="mp-card-techs">
                                    {detail.technologies_used.map((t, i) => <span key={i} className="mp-tech">{t}</span>)}
                                </div>
                            </div>
                        )}

                        {/* Instructor feedback */}
                        {detail.instructor_feedback && (
                            <div className="mp-feedback">
                                <span className="mp-detail-label">💬 Отзыв преподавателя</span>
                                <p>{detail.instructor_feedback}</p>
                            </div>
                        )}

                        {/* Dates */}
                        {detail.submitted_at && (
                            <div className="mp-detail-row">
                                <span className="mp-detail-label">Отправлен</span>
                                <span className="mp-detail-value">{new Date(detail.submitted_at).toLocaleDateString('ru-RU')}</span>
                            </div>
                        )}
                        {detail.reviewed_at && (
                            <div className="mp-detail-row">
                                <span className="mp-detail-label">Проверен</span>
                                <span className="mp-detail-value">{new Date(detail.reviewed_at).toLocaleDateString('ru-RU')}</span>
                            </div>
                        )}

                        {/* ── ZIP Upload ── */}
                        <div className="mp-section">
                            <span className="mp-detail-label">📦 ZIP-архив проекта</span>

                            {/* Current file link */}
                            {detail.project_files && (
                                <div className="mp-current-file">
                                    <span className="mp-current-file-label">Текущий файл:</span>
                                    <a href={detail.project_files} target="_blank" rel="noreferrer" className="mp-link mp-link-sm">
                                        📎 Открыть
                                    </a>
                                </div>
                            )}

                            <ZipDropZone
                                selectedFile={selectedFile}
                                onFileSelect={setSelectedFile}
                                uploading={uploading}
                            />

                            <div className="mp-zip-row">
                                <button
                                    className="mp-btn-zip-upload"
                                    onClick={() => handleZipUpload(detail.id, selectedFile)}
                                    disabled={uploading || !selectedFile || selectedFile?.size > 15 * 1024 * 1024}
                                >
                                    {uploading ? (
                                        <><span className="mp-btn-spinner" />Загрузка...</>
                                    ) : '📤 Загрузить ZIP'}
                                </button>
                                {uploadMsg && <span className={`mp-upload-msg ${uploadMsg.startsWith('✅') ? 'success' : 'error'}`}>{uploadMsg}</span>}
                            </div>
                        </div>

                        {/* ── File URL (PATCH) ── */}
                        <div className="mp-section">
                            <div className="mp-section-header">
                                <span className="mp-detail-label">🔗 Ссылка на файл</span>
                                <button
                                    className="mp-toggle-link"
                                    onClick={() => { setShowFileUrlEdit(v => !v); setFileUrlMsg(''); setFileUrlInput(detail.project_files || ''); }}
                                >
                                    {showFileUrlEdit ? 'Скрыть' : '✏️ Изменить'}
                                </button>
                            </div>

                            {!showFileUrlEdit && detail.project_files && (
                                <a href={detail.project_files} target="_blank" rel="noreferrer" className="mp-link mp-link-sm">
                                    {detail.project_files}
                                </a>
                            )}
                            {!showFileUrlEdit && !detail.project_files && (
                                <span className="mp-hint">Ссылка не указана</span>
                            )}

                            {showFileUrlEdit && (
                                <div className="mp-file-url-edit">
                                    <input
                                        className="mp-file-url-input"
                                        placeholder="https://drive.google.com/..."
                                        value={fileUrlInput}
                                        onChange={e => { setFileUrlInput(e.target.value); setFileUrlMsg(''); }}
                                    />
                                    <button
                                        className="mp-btn-save mp-btn-save-sm"
                                        onClick={handlePatchFileUrl}
                                        disabled={fileUrlSaving || !fileUrlInput.trim()}
                                    >
                                        {fileUrlSaving ? '⏳' : '💾 Сохранить'}
                                    </button>
                                </div>
                            )}
                            {fileUrlMsg && (
                                <span className={`mp-upload-msg ${fileUrlMsg.startsWith('✅') ? 'success' : 'error'}`}>{fileUrlMsg}</span>
                            )}
                        </div>

                        {/* ── AI Review ── */}
                        <div className="mp-section">
                            <span className="mp-detail-label">🤖 AI-проверка</span>
                            <button
                                className="mp-btn-ai"
                                onClick={() => handleAiReview(detail.id)}
                                disabled={aiLoading}
                            >
                                {aiLoading ? (
                                    <><span className="mp-btn-spinner mp-btn-spinner-pink" />Анализ...</>
                                ) : '✨ Запустить AI-проверку'}
                            </button>
                            {aiResult && (
                                <div className="mp-ai-result">
                                    <p>{aiResult}</p>
                                </div>
                            )}
                        </div>

                    </div>

                    <div className="mp-modal-footer">
                        <button className="mp-btn-delete" onClick={() => handleDelete(detail.id)}>🗑️ Удалить</button>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            {detail.status === 'Draft' && (
                                <>
                                    <button className="mp-btn-edit" onClick={openEdit}>✏️ Изменить</button>
                                    <button className="mp-btn-submit" onClick={() => handleSubmit(detail.id)}>
                                        🚀 Отправить на проверку
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                </Modal>
            )}
        </div>
    );
}

export default MyProjects;