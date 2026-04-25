import { useState, useEffect, useRef } from 'react';
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

/* ── Shared form fields ── */
const ProjectFormFields = ({ form, errors, set }) => (
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
    </>
);

function MyProjects() {
    const { request } = useHttp();
    const fileInputRef = useRef(null);

    const [projects,   setProjects]   = useState([]);
    const [loading,    setLoading]    = useState(true);
    const [addModal,   setAddModal]   = useState(false);
    const [editModal,  setEditModal]  = useState(false);
    const [detail,     setDetail]     = useState(null);
    const [form,       setForm]       = useState({ ...EMPTY });
    const [errors,     setErrors]     = useState({});
    const [saving,     setSaving]     = useState(false);
    const [apiError,   setApiError]   = useState('');

    // ZIP upload state
    const [uploading,    setUploading]    = useState(false);
    const [uploadMsg,    setUploadMsg]    = useState('');
    const [selectedFile, setSelectedFile] = useState(null);

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

    /* ── CREATE ── */
    const handleCreate = () => {
        if (!validate()) return;
        setSaving(true); setApiError('');
        request(`${API_URL}v1/project/`, 'POST', JSON.stringify(buildBody()), headers())
            .then(res => {
                setProjects(p => [res, ...p]);
                setAddModal(false);
                setForm({ ...EMPTY });
            })
            .catch(() => setApiError('Ошибка при создании проекта'))
            .finally(() => setSaving(false));
    };

    /* ── UPDATE ── */
    const handleUpdate = () => {
        if (!validate()) return;
        setSaving(true); setApiError('');
        request(`${API_URL}v1/project/${detail.id}`, 'PUT', JSON.stringify(buildBody()), headers())
            .then(res => {
                setProjects(p => p.map(pr => pr.id === res.id ? res : pr));
                setDetail(res);
                setEditModal(false);
            })
            .catch(() => setApiError('Ошибка при обновлении проекта'))
            .finally(() => setSaving(false));
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

    /* ── UPLOAD ZIP ── */
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
            method: 'POST',
            headers: h,
            body: formData,
        })
            .then(async r => {
                if (!r.ok) throw new Error();
                setUploadMsg('✅ ZIP загружен успешно');
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
        setErrors({}); setApiError('');
        setEditModal(true);
    };

    const openAdd = () => {
        setForm({ ...EMPTY }); setErrors({}); setApiError('');
        setAddModal(true);
    };

    const closeDetail = () => {
        setDetail(null);
        setSelectedFile(null);
        setUploadMsg('');
        setAiResult('');
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
                        <ProjectFormFields form={form} errors={errors} set={set} />
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
                        <ProjectFormFields form={form} errors={errors} set={set} />
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
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept=".zip"
                                style={{ display: 'none' }}
                                onChange={e => {
                                    const file = e.target.files[0];
                                    if (!file) return;
                                    setSelectedFile(file);
                                    setUploadMsg('');
                                }}
                            />
                            {selectedFile && (
                                <div className={`mp-file-preview ${selectedFile.size > 15 * 1024 * 1024 ? 'too-large' : 'ok'}`}>
                                    <div className="mp-file-info">
                                        <span className="mp-file-name">📄 {selectedFile.name}</span>
                                        <span className="mp-file-size">
                                            {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                                        </span>
                                    </div>
                                    <div className="mp-file-bar-wrap">
                                        <div
                                            className="mp-file-bar"
                                            style={{ width: `${Math.min((selectedFile.size / (15 * 1024 * 1024)) * 100, 100)}%` }}
                                        />
                                    </div>
                                    <div className="mp-file-bar-labels">
                                        <span>0 MB</span>
                                        <span className={selectedFile.size > 15 * 1024 * 1024 ? 'mp-overlimit' : ''}>
                                            {selectedFile.size > 15 * 1024 * 1024
                                                ? '⚠️ Превышает лимит 15MB!'
                                                : `${((1 - selectedFile.size / (15 * 1024 * 1024)) * 100).toFixed(0)}% свободно`}
                                        </span>
                                        <span>15 MB</span>
                                    </div>
                                </div>
                            )}
                            <div className="mp-zip-row">
                                <button
                                    className="mp-btn-zip"
                                    onClick={() => { setSelectedFile(null); setUploadMsg(''); fileInputRef.current?.click(); }}
                                    disabled={uploading}
                                >
                                    📁 Выбрать файл
                                </button>
                                <button
                                    className="mp-btn-zip-upload"
                                    onClick={() => handleZipUpload(detail.id, selectedFile)}
                                    disabled={uploading || !selectedFile || selectedFile.size > 15 * 1024 * 1024}
                                >
                                    {uploading ? '⏳ Загрузка...' : '📤 Загрузить'}
                                </button>
                                {uploadMsg && <span className={`mp-upload-msg ${uploadMsg.startsWith('✅') ? 'success' : 'error'}`}>{uploadMsg}</span>}
                            </div>
                            <p className="mp-hint">Максимальный размер: 15 MB · только .zip</p>
                        </div>

                        {/* ── AI Review ── */}
                        <div className="mp-section">
                            <span className="mp-detail-label">🤖 AI-проверка</span>
                            <button
                                className="mp-btn-ai"
                                onClick={() => handleAiReview(detail.id)}
                                disabled={aiLoading}
                            >
                                {aiLoading ? '🔄 Анализ...' : '✨ Запустить AI-проверку'}
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