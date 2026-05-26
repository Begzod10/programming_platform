import { useState, useEffect, useRef, useCallback } from 'react';
import ReactDOM from 'react-dom';
import './MyProjects.css';
import ProjectCard from './ProjectCard';
import { API_URL, useHttp, headers } from '../../../api/search/base';

const DIFFICULTIES = ['Easy', 'Medium', 'Hard'];

/* ── Modal Portal ── */
const Modal = ({ onClose, children, wide }) => ReactDOM.createPortal(
    <div className="mp-overlay" onClick={onClose}>
        <div className={`mp-modal ${wide ? 'mp-detail-modal' : ''}`} onClick={e => e.stopPropagation()}>
            {children}
        </div>
    </div>,
    document.body
);

/* ── Upload Method Selector ── */
const UploadMethodSelector = ({ method, onChange }) => (
    <div className="mp-method-selector">
        <button
            type="button"
            className={`mp-method-btn ${method === 'github' ? 'mp-method-active' : ''}`}
            onClick={() => onChange('github')}
        >
            <span className="mp-method-icon">
                <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
                </svg>
            </span>
            <span className="mp-method-label">
                <span className="mp-method-title">GitHub</span>
                <span className="mp-method-sub">Ссылка на репозиторий</span>
            </span>
            {method === 'github' && <span className="mp-method-check">✓</span>}
        </button>
        <div className="mp-method-divider">
            <span>или</span>
        </div>
        <button
            type="button"
            className={`mp-method-btn ${method === 'zip' ? 'mp-method-active mp-method-active-zip' : ''}`}
            onClick={() => onChange('zip')}
        >
            <span className="mp-method-icon mp-method-icon-zip">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" width="20" height="20">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
            </span>
            <span className="mp-method-label">
                <span className="mp-method-title">ZIP-архив</span>
                <span className="mp-method-sub">Загрузить файл до 15MB</span>
            </span>
            {method === 'zip' && <span className="mp-method-check">✓</span>}
        </button>
    </div>
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

    const isOverLimit = selectedFile && selectedFile.size > 15 * 1024 * 1024;
    const isEmpty = selectedFile && selectedFile.size === 0;

    return (
        <div
            className={`mp-dropzone ${dragging ? 'mp-dropzone-drag' : ''} ${compact ? 'mp-dropzone-compact' : ''}`}
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
                    <span className="mp-dropzone-icon">{isEmpty ? '⚠️' : '📦'}</span>
                    <div className="mp-dropzone-info">
                        <span className="mp-file-name">{selectedFile.name}</span>
                        <span className={`mp-file-size ${isOverLimit || isEmpty ? 'mp-overlimit' : ''}`}>
                            {isEmpty
                                ? '⚠️ Файл пустой — выберите другой'
                                : `${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB${isOverLimit ? ' · ⚠️ Превышает 15MB' : ''}`
                            }
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
            {selectedFile && !isEmpty && (
                <div className="mp-file-bar-wrap">
                    <div className="mp-file-bar" style={{ width: `${Math.min((selectedFile.size / (15 * 1024 * 1024)) * 100, 100)}%` }} />
                </div>
            )}
        </div>
    );
};

/* ── Form Fields for Edit ── */
const ProjectFormFields = ({ form, errors, set, zipFile, onZipSelect, uploadMethod, onMethodChange }) => (
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
            <label>Способ загрузки кода *</label>
            <UploadMethodSelector method={uploadMethod} onChange={onMethodChange} />
            {errors.source && <span className="mp-error">{errors.source}</span>}
        </div>

        <div className={`mp-source-panel ${uploadMethod === 'github' ? 'mp-source-panel-visible' : ''}`}>
            <div className="mp-field">
                <label>GitHub URL</label>
                <input placeholder="https://github.com/username/repo" value={form.github_url}
                    onChange={e => set('github_url', e.target.value)}
                    className={errors.github_url ? 'mp-input-error' : ''} />
                {errors.github_url && <span className="mp-error">{errors.github_url}</span>}
            </div>
        </div>

        <div className={`mp-source-panel ${uploadMethod === 'zip' ? 'mp-source-panel-visible' : ''}`}>
            <div className="mp-field">
                <label>ZIP-архив</label>
                <ZipDropZone selectedFile={zipFile} onFileSelect={onZipSelect} compact />
                {errors.zip && <span className="mp-error">{errors.zip}</span>}
            </div>
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
    </>
);

function MyProjects() {
    const { request } = useHttp();

    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editModal, setEditModal] = useState(false);
    const [detail, setDetail] = useState(null);

    const [form, setForm] = useState({
        title: '', description: '', github_url: '',
        live_demo_url: '', technologies_used: '', difficulty_level: 'Easy',
    });
    const [errors, setErrors] = useState({});
    const [saving, setSaving] = useState(false);
    const [apiError, setApiError] = useState('');

    const [uploadMethod, setUploadMethod] = useState('github');
    const [formZipFile, setFormZipFile] = useState(null);

    // Detail modal states
    const [uploading, setUploading] = useState(false);
    const [uploadMsg, setUploadMsg] = useState('');
    const [selectedFile, setSelectedFile] = useState(null);

    const [fileUrlInput, setFileUrlInput] = useState('');
    const [fileUrlSaving, setFileUrlSaving] = useState(false);
    const [fileUrlMsg, setFileUrlMsg] = useState('');
    const [showFileUrlEdit, setShowFileUrlEdit] = useState(false);

    const [aiLoading, setAiLoading] = useState(false);
    const [aiResult, setAiResult] = useState('');

    // Load projects
    useEffect(() => {
        request(`${API_URL}v1/project/my`, 'GET', null, headers())
            .then(data => setProjects(Array.isArray(data) ? data : []))
            .catch(() => setProjects([]))
            .finally(() => setLoading(false));
    }, [request]);

    const setField = (k, v) => {
        setForm(f => ({ ...f, [k]: v }));
        setErrors(e => ({ ...e, [k]: '' }));
    };

    const validate = () => {
        const e = {};
        if (!form.title.trim()) e.title = 'Введите название';
        if (!form.description.trim()) e.description = 'Введите описание';
        else if (form.description.trim().length < 10) e.description = 'Минимум 10 символов';

        if (uploadMethod === 'github') {
            if (!form.github_url.trim()) e.github_url = 'Введите GitHub ссылку';
        } else if (!formZipFile) {
            e.zip = 'Выберите ZIP-файл';
        } else if (formZipFile.size === 0) {
            e.zip = 'ZIP-файл пустой';
        } else if (formZipFile.size > 15 * 1024 * 1024) {
            e.zip = 'Файл превышает 15MB';
        }

        setErrors(e);
        return Object.keys(e).length === 0;
    };

    const buildBody = () => ({
        title: form.title,
        description: form.description,
        github_url: uploadMethod === 'github' ? form.github_url : '',
        live_demo_url: form.live_demo_url || '',
        technologies_used: form.technologies_used.split(',').map(t => t.trim()).filter(Boolean),
        difficulty_level: form.difficulty_level,
    });

    /* ── UPDATE ── */
    const handleUpdate = async () => {
        if (!validate()) return;
        setSaving(true);
        setApiError('');

        try {
            const res = await request(`${API_URL}v1/project/${detail.id}`, 'PUT', JSON.stringify(buildBody()), headers());

            if (uploadMethod === 'zip' && formZipFile) {
                try {
                    await uploadZipForProject(res.id, formZipFile);
                } catch (_) {}
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

    /* ── ZIP Upload Helper ── */
    const uploadZipForProject = async (projectId, file) => {
        const formData = new FormData();
        formData.append('file', file);
        const h = headers();
        delete h['Content-Type'];

        const r = await fetch(`${API_URL}v1/project/${projectId}/upload-zip`, {
            method: 'POST', headers: h, body: formData,
        });
        if (!r.ok) throw new Error('Upload failed');
    };

    /* ── Other handlers ── */
    const handleSubmit = (projectId) => {
        request(`${API_URL}v1/project/${projectId}/submit`, 'POST', JSON.stringify({}), headers())
            .then(() => {
                setProjects(p => p.map(pr => pr.id === projectId ? { ...pr, status: 'Submitted' } : pr));
                setDetail(d => d ? { ...d, status: 'Submitted' } : d);
            })
            .catch(() => alert('Ошибка при отправке'));
    };

    const handleDelete = (projectId) => {
        if (!window.confirm('Удалить проект?')) return;
        request(`${API_URL}v1/project/${projectId}`, 'DELETE', null, headers())
            .then(() => {
                setProjects(p => p.filter(pr => pr.id !== projectId));
                setDetail(null);
            })
            .catch(() => alert('Ошибка при удалении'));
    };

    const handleZipUpload = (projectId, file) => {
        if (!file || file.size === 0 || file.size > 15 * 1024 * 1024) {
            setUploadMsg('❌ Некорректный файл');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        setUploading(true);
        setUploadMsg('');

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
            .catch(() => setUploadMsg('❌ Ошибка загрузки'))
            .finally(() => setUploading(false));
    };

    const handlePatchFileUrl = () => {
        if (!fileUrlInput.trim()) return;
        setFileUrlSaving(true);
        setFileUrlMsg('');

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
            .catch(() => setFileUrlMsg('❌ Ошибка обновления'))
            .finally(() => setFileUrlSaving(false));
    };

    const handleAiReview = (projectId) => {
        setAiLoading(true);
        setAiResult('');
        request(`${API_URL}v1/project/${projectId}/ai-review`, 'POST', JSON.stringify({}), headers())
            .then(res => setAiResult(typeof res === 'string' ? res : JSON.stringify(res)))
            .catch(() => setAiResult('❌ Ошибка AI-проверки'))
            .finally(() => setAiLoading(false));
    };

    const openEdit = () => {
        setForm({
            title: detail.title || '',
            description: detail.description || '',
            github_url: detail.github_url || '',
            live_demo_url: detail.live_demo_url || '',
            technologies_used: (detail.technologies_used || []).join(', '),
            difficulty_level: detail.difficulty_level || 'Easy',
        });
        setUploadMethod(detail.github_url ? 'github' : 'zip');
        setFormZipFile(null);
        setErrors({});
        setApiError('');
        setEditModal(true);
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

    const handleMethodChange = (method) => {
        setUploadMethod(method);
        setErrors(e => ({ ...e, github_url: '', zip: '', source: '' }));
        if (method === 'github') setFormZipFile(null);
        if (method === 'zip') setField('github_url', '');
    };

    return (
        <div className="mp-container item-fade-in">
            <div className="mp-header">
                <div>
                    <h2>Мои Проекты</h2>
                    <p className="mp-subtitle">Управление вашими проектами</p>
                </div>
            </div>

            {loading ? (
                <div className="mp-loading">
                    <div className="mp-spinner" />
                    <p>Загрузка...</p>
                </div>
            ) : projects.length === 0 ? (
                <div className="mp-empty">
                    <span>📂</span>
                    <p>У вас пока нет проектов</p>
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
                            onDetails={() => {
                                setAiResult('');
                                setUploadMsg('');
                                setDetail(p);
                            }}
                        />
                    ))}
                </div>
            )}

            {/* EDIT MODAL */}
            {editModal && (
                <Modal onClose={() => setEditModal(false)}>
                    <div className="mp-modal-header">
                        <h3>✏️ Редактировать проект</h3>
                        <button className="mp-close" onClick={() => setEditModal(false)}>✕</button>
                    </div>
                    <div className="mp-modal-body">
                        {apiError && <div className="mp-api-error">{apiError}</div>}
                        <ProjectFormFields
                            form={form}
                            errors={errors}
                            set={setField}
                            zipFile={formZipFile}
                            onZipSelect={setFormZipFile}
                            uploadMethod={uploadMethod}
                            onMethodChange={handleMethodChange}
                        />
                    </div>
                    <div className="mp-modal-footer">
                        <button className="mp-btn-cancel" onClick={() => setEditModal(false)}>Отмена</button>
                        <button className="mp-btn-save" onClick={handleUpdate} disabled={saving}>
                            {saving ? '⏳ Сохранение...' : '💾 Сохранить'}
                        </button>
                    </div>
                </Modal>
            )}

            {/* DETAIL MODAL */}
            {detail && (
                <Modal onClose={closeDetail} wide>
                    <div className="mp-modal-header">
                        <h3>📋 {detail.title}</h3>
                        <button className="mp-close" onClick={closeDetail}>✕</button>
                    </div>
                    <div className="mp-modal-body">
                        {/* Badges */}
                        <div className="mp-detail-badges">
                            <span className={`mp-diff ${detail.difficulty_level === 'Easy' ? 'mp-diff-easy' : detail.difficulty_level === 'Medium' ? 'mp-diff-medium' : 'mp-diff-hard'}`}>
                                {detail.difficulty_level}
                            </span>
                            <span className={`mp-status ${{
                                Draft: 'mp-status-draft',
                                Submitted: 'mp-status-pending',
                                'Under Review': 'mp-status-pending',
                                Approved: 'mp-status-approved',
                                Rejected: 'mp-status-denied'
                            }[detail.status] || ''}`}>
                                {{
                                    Draft: 'Черновик',
                                    Submitted: 'Отправлен',
                                    'Under Review': 'На проверке',
                                    Approved: 'Одобрен',
                                    Rejected: 'Отклонён'
                                }[detail.status] || detail.status}
                            </span>
                            {detail.grade && <span className={`mp-grade mp-grade-${detail.grade}`}>Оценка: {detail.grade}</span>}
                        </div>

                        {/* Stats */}
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

                        {/* Description, Links, Technologies, etc. */}
                        <div className="mp-detail-row">
                            <span className="mp-detail-label">Описание</span>
                            <span className="mp-detail-value">{detail.description || '—'}</span>
                        </div>

                        {detail.github_url && (
                            <div className="mp-detail-row">
                                <span className="mp-detail-label">GitHub</span>
                                <a href={detail.github_url} target="_blank" rel="noreferrer" className="mp-link">{detail.github_url}</a>
                            </div>
                        )}

                        {detail.live_demo_url && (
                            <div className="mp-detail-row">
                                <span className="mp-detail-label">Live Demo</span>
                                <a href={detail.live_demo_url} target="_blank" rel="noreferrer" className="mp-link">{detail.live_demo_url}</a>
                            </div>
                        )}

                        {(detail.technologies_used || []).length > 0 && (
                            <div className="mp-detail-row">
                                <span className="mp-detail-label">Технологии</span>
                                <div className="mp-card-techs">
                                    {detail.technologies_used.map((t, i) => <span key={i} className="mp-tech">{t}</span>)}
                                </div>
                            </div>
                        )}

                        {detail.instructor_feedback && (
                            <div className="mp-feedback">
                                <span className="mp-detail-label">💬 Отзыв преподавателя</span>
                                <p>{detail.instructor_feedback}</p>
                            </div>
                        )}

                        {/* ZIP Upload Section */}
                        <div className="mp-section">
                            <span className="mp-detail-label">📦 ZIP-архив проекта</span>
                            {detail.project_files && (
                                <div className="mp-current-file">
                                    <span className="mp-current-file-label">Текущий файл:</span>
                                    <a href={detail.project_files} target="_blank" rel="noreferrer" className="mp-link mp-link-sm">📎 Открыть</a>
                                </div>
                            )}
                            <ZipDropZone selectedFile={selectedFile} onFileSelect={setSelectedFile} uploading={uploading} />
                            <div className="mp-zip-row">
                                <button className="mp-btn-zip-upload" onClick={() => handleZipUpload(detail.id, selectedFile)}
                                    disabled={uploading || !selectedFile}>
                                    {uploading ? <>Загрузка...</> : '📤 Загрузить ZIP'}
                                </button>
                                {uploadMsg && <span className={`mp-upload-msg ${uploadMsg.startsWith('✅') ? 'success' : 'error'}`}>{uploadMsg}</span>}
                            </div>
                        </div>

                        {/* File URL */}
                        <div className="mp-section">
                            <div className="mp-section-header">
                                <span className="mp-detail-label">🔗 Ссылка на файл</span>
                                <button className="mp-toggle-link" onClick={() => { setShowFileUrlEdit(v => !v); setFileUrlMsg(''); setFileUrlInput(detail.project_files || ''); }}>
                                    {showFileUrlEdit ? 'Скрыть' : '✏️ Изменить'}
                                </button>
                            </div>
                            {showFileUrlEdit ? (
                                <div className="mp-file-url-edit">
                                    <input className="mp-file-url-input" placeholder="https://..." value={fileUrlInput} onChange={e => setFileUrlInput(e.target.value)} />
                                    <button className="mp-btn-save mp-btn-save-sm" onClick={handlePatchFileUrl} disabled={fileUrlSaving || !fileUrlInput.trim()}>
                                        {fileUrlSaving ? '⏳' : 'Сохранить'}
                                    </button>
                                </div>
                            ) : detail.project_files ? (
                                <a href={detail.project_files} target="_blank" rel="noreferrer" className="mp-link">{detail.project_files}</a>
                            ) : <span className="mp-hint">Ссылка не указана</span>}
                            {fileUrlMsg && <span className={`mp-upload-msg ${fileUrlMsg.startsWith('✅') ? 'success' : 'error'}`}>{fileUrlMsg}</span>}
                        </div>

                        {/* AI Review */}
                        <div className="mp-section">
                            <span className="mp-detail-label">🤖 AI-проверка</span>
                            <button className="mp-btn-ai" onClick={() => handleAiReview(detail.id)} disabled={aiLoading}>
                                {aiLoading ? 'Анализ...' : '✨ Запустить AI-проверку'}
                            </button>
                            {aiResult && <div className="mp-ai-result"><p>{aiResult}</p></div>}
                        </div>
                    </div>

                    <div className="mp-modal-footer">
                        <button className="mp-btn-delete" onClick={() => handleDelete(detail.id)}>🗑️ Удалить</button>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            {detail.status === 'Draft' && (
                                <>
                                    <button className="mp-btn-edit" onClick={openEdit}>✏️ Изменить</button>
                                    <button className="mp-btn-submit" onClick={() => handleSubmit(detail.id)}>🚀 Отправить на проверку</button>
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