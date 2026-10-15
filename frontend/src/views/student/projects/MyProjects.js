import { useState, useEffect, useRef, useCallback } from 'react';
import ReactDOM from 'react-dom';
import './MyProjects.css';
import ProjectCard from './ProjectCard';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { ConfirmModal } from '../../teacher/courses/TeacherCourses/ConfirmModal';
import { Trophy, Search } from 'lucide-react';
import AppHeader from '../../../components/appheader/AppHeader';
import CodeCheckBanner from '../codecheck/CodeCheckBanner';
import { useTranslation } from '../../../i18n/useTranslation';

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
const UploadMethodSelector = ({ method, onChange }) => {
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    return (
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
                <span className="mp-method-sub">{ru ? 'Ссылка на репозиторий' : 'Repozitoriy havolasi'}</span>
            </span>
            {method === 'github' && <span className="mp-method-check">✓</span>}
        </button>
        <div className="mp-method-divider">
            <span>{ru ? 'или' : 'yoki'}</span>
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
                <span className="mp-method-title">{ru ? 'ZIP-архив' : 'ZIP-arxiv'}</span>
                <span className="mp-method-sub">{ru ? 'Загрузить файл до 15MB' : '15MB gacha fayl yuklash'}</span>
            </span>
            {method === 'zip' && <span className="mp-method-check">✓</span>}
        </button>
    </div>
    );
};

/* ── ZIP Drop Zone ── */
const ZipDropZone = ({ selectedFile, onFileSelect, uploading, compact = false }) => {
    const { lang } = useTranslation();
    const ru = lang === 'ru';
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
                                ? (ru ? '⚠️ Файл пустой — выберите другой' : "⚠️ Fayl bo'sh — boshqasini tanlang")
                                : `${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB${isOverLimit ? (ru ? ' · ⚠️ Превышает 15MB' : ' · ⚠️ 15MB dan oshadi') : ''}`
                            }
                        </span>
                    </div>
                    <button className="mp-dropzone-clear" onClick={e => { e.stopPropagation(); onFileSelect(null); }}>✕</button>
                </div>
            ) : (
                <div className="mp-dropzone-placeholder">
                    <span className="mp-dropzone-icon mp-dropzone-icon-empty">{dragging ? '🎯' : '📁'}</span>
                    <span className="mp-dropzone-text">
                        {dragging
                            ? (ru ? 'Отпустите файл' : 'Faylni qo‘yib yuboring')
                            : compact
                                ? (ru ? 'Перетащите .zip или нажмите' : '.zip faylni tashlang yoki bosing')
                                : (ru ? 'Перетащите .zip архив сюда или нажмите для выбора' : '.zip arxivni shu yerga tashlang yoki tanlash uchun bosing')}
                    </span>
                    {!compact && <span className="mp-dropzone-hint">{ru ? 'Максимум 15 MB · только .zip' : 'Maksimum 15 MB · faqat .zip'}</span>}
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

/* ── AI Review result panel ──
   Renders the structured response from POST /v1/ai/{id}/ai-review.
   Three shapes coexist:
     - null / ''             → nothing rendered (initial state)
     - { error: "...", ... } → red error card (network failure / 4xx/5xx)
     - { grade, points, ... } → full success panel with provider badge
*/
const PROVIDER_META = {
    groq:   { label: 'Groq',    sub: 'Llama 3.3 70B',  className: 'mp-prov-groq'   },
    gemini: { label: 'Gemini',  sub: '2.5 Flash',      className: 'mp-prov-gemini' },
    openai: { label: 'OpenAI',  sub: 'GPT-4.1 mini',   className: 'mp-prov-openai' },
};

const GRADE_TONE = {
    A: 'mp-grade-a', B: 'mp-grade-b', C: 'mp-grade-c', D: 'mp-grade-d', F: 'mp-grade-f',
};

const AuthorshipBadges = ({ authorship }) => {
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    if (!authorship || !authorship.available) return null;
    const badges = [];

    if (authorship.is_fork) {
        badges.push({
            key: 'fork',
            tone: 'danger',
            label: ru ? '⚠️ Это форк' : '⚠️ Bu fork',
            title: authorship.parent_repo
                ? (ru
                    ? `Форк репозитория ${authorship.parent_repo} — оценка ограничена`
                    : `${authorship.parent_repo} repozitoriysining fork'i — baholash cheklangan`)
                : (ru
                    ? 'Репозиторий — форк. Оценка ограничена.'
                    : "Repozitoriy — fork. Baholash cheklangan."),
        });
    }
    if (authorship.commit_count === 1) {
        badges.push({
            key: 'single-commit',
            tone: 'warn',
            label: ru ? '⚠️ 1 коммит' : '⚠️ 1 ta commit',
            title: ru
                ? 'Только один коммит — нет поэтапной работы'
                : "Faqat bitta commit — bosqichma-bosqich ish yo'q",
        });
    } else if (typeof authorship.commit_count === 'number' && authorship.commit_count >= 3) {
        badges.push({
            key: 'commits',
            tone: 'ok',
            label: ru ? `✓ ${authorship.commit_count} коммитов` : `✓ ${authorship.commit_count} ta commit`,
            title: ru
                ? 'Несколько коммитов — видна поэтапная работа'
                : "Bir nechta commit — bosqichma-bosqich ish ko'rinadi",
        });
    }
    if (authorship.owner_is_contributor === false) {
        badges.push({
            key: 'not-owner',
            tone: 'danger',
            label: ru ? '⚠️ Владелец не среди авторов' : '⚠️ Egasi mualliflar orasida yo‘q',
            title: ru
                ? 'Коммиты сделаны не владельцем репозитория'
                : "Commitlar repozitoriy egasi tomonidan qilinmagan",
        });
    }

    if (badges.length === 0) return null;
    return (
        <div className="mp-ai-authorship">
            {badges.map(b => (
                <span key={b.key} className={`mp-author-badge mp-author-${b.tone}`} title={b.title}>
                    {b.label}
                </span>
            ))}
        </div>
    );
};

const AiReviewResult = ({ data }) => {
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    if (!data) return null;

    if (data.error) {
        return (
            <div className="mp-ai-result mp-ai-error">
                <p>❌ {data.errorMessage || (ru ? 'AI-проверка не удалась' : 'AI-tekshiruv muvaffaqiyatsiz tugadi')}</p>
                {data.errorStatus && <p className="mp-ai-meta">HTTP {data.errorStatus}</p>}
            </div>
        );
    }

    const prov = PROVIDER_META[data.provider] || { label: data.provider || '?', sub: '', className: '' };
    const gradeTone = GRADE_TONE[(data.grade || '').toUpperCase()] || 'mp-grade-c';
    const sourceLabel = data.source === 'zip' ? '📦 ZIP' : data.source === 'github' ? '🐙 GitHub' : '';

    return (
        <div className="mp-ai-result">
            <div className="mp-ai-head">
                <span className={`mp-ai-provider ${prov.className}`} title={`Provider: ${prov.label}`}>
                    ✨ {prov.label}{prov.sub && <span className="mp-ai-provider-sub"> · {prov.sub}</span>}
                </span>
                <span className={`mp-ai-grade ${gradeTone}`}>
                    {data.grade || '?'} · {data.points ?? 0} {ru ? 'баллов' : 'ball'}
                </span>
            </div>

            <div className="mp-ai-meta">
                {sourceLabel && <span>{sourceLabel}</span>}
                {Array.isArray(data.files_reviewed) && data.files_reviewed.length > 0 && (
                    <span>{data.files_reviewed.length} {ru ? 'файлов проверено' : 'ta fayl tekshirildi'}</span>
                )}
                {typeof data.reviews_remaining_today === 'number' && (
                    <span>{ru ? 'Осталось сегодня' : 'Bugun qoldi'}: {data.reviews_remaining_today}</span>
                )}
                {typeof data.old_points === 'number' && data.old_points > 0 && data.old_points !== data.new_points && (
                    <span>{ru ? 'было' : 'oldin'}: {data.old_points}</span>
                )}
            </div>

            <AuthorshipBadges authorship={data.authorship} />

            {data.summary && <p className="mp-ai-summary">{data.summary}</p>}

            {Array.isArray(data.strengths) && data.strengths.length > 0 && (
                <div className="mp-ai-list mp-ai-strengths">
                    <span className="mp-ai-list-title">{ru ? '✅ Сильные стороны' : '✅ Kuchli tomonlari'}</span>
                    <ul>{data.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </div>
            )}

            {Array.isArray(data.improvements) && data.improvements.length > 0 && (
                <div className="mp-ai-list mp-ai-improvements">
                    <span className="mp-ai-list-title">{ru ? '💡 Что улучшить' : '💡 Nimani yaxshilash kerak'}</span>
                    <ul>{data.improvements.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </div>
            )}

            {data.feedback && (
                <details className="mp-ai-details">
                    <summary>{ru ? 'Подробнее' : 'Batafsil'}</summary>
                    <p>{data.feedback}</p>
                </details>
            )}

            {Array.isArray(data.files_reviewed) && data.files_reviewed.length > 0 && (
                <details className="mp-ai-details">
                    <summary>{ru ? 'Проверенные файлы' : 'Tekshirilgan fayllar'} ({data.files_reviewed.length})</summary>
                    <ul className="mp-ai-files">
                        {data.files_reviewed.map((f, i) => <li key={i}><code>{f}</code></li>)}
                    </ul>
                </details>
            )}
        </div>
    );
};

/* ── Form Fields for Edit ── */
const ProjectFormFields = ({ form, errors, set, zipFile, onZipSelect, uploadMethod, onMethodChange }) => {
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    return (
    <>
        <div className="mp-field">
            <label>{ru ? 'Название *' : 'Nomi *'}</label>
            <input placeholder="E-commerce Backend" value={form.title}
                onChange={e => set('title', e.target.value)}
                className={errors.title ? 'mp-input-error' : ''} />
            {errors.title && <span className="mp-error">{errors.title}</span>}
        </div>
        <div className="mp-field">
            <label>{ru ? 'Описание *' : 'Tavsif *'}</label>
            <textarea placeholder={ru ? 'Краткое описание...' : 'Qisqacha tavsif...'} value={form.description}
                onChange={e => set('description', e.target.value)}
                className={errors.description ? 'mp-input-error' : ''} rows={3} />
            {errors.description && <span className="mp-error">{errors.description}</span>}
        </div>

        <div className="mp-field">
            <label>{ru ? 'Способ загрузки кода *' : 'Kodni yuklash usuli *'}</label>
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
                <label>{ru ? 'ZIP-архив' : 'ZIP-arxiv'}</label>
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
            <label>{ru ? 'Технологии (через запятую)' : 'Texnologiyalar (vergul bilan)'}</label>
            <input placeholder="React, FastAPI, PostgreSQL" value={form.technologies_used}
                onChange={e => set('technologies_used', e.target.value)} />
        </div>
        <div className="mp-field">
            <label>{ru ? 'Сложность' : 'Murakkablik'}</label>
            <select value={form.difficulty_level} onChange={e => set('difficulty_level', e.target.value)}>
                {DIFFICULTIES.map(d => <option key={d}>{d}</option>)}
            </select>
        </div>
    </>
    );
};

function MyProjects() {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const ru = lang === 'ru';

    const [projects, setProjects] = useState([]);
    const [search, setSearch] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
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
    const [aiResult, setAiResult] = useState(null);

    // Delete confirmation (replaces window.confirm — blocked/no-op in some
    // embedded webviews, and visually inconsistent with the rest of the app).
    const [confirmDeleteId, setConfirmDeleteId] = useState(null);

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
        if (!form.title.trim()) e.title = ru ? 'Введите название' : 'Nomini kiriting';
        if (!form.description.trim()) e.description = ru ? 'Введите описание' : 'Tavsifni kiriting';
        else if (form.description.trim().length < 10) e.description = ru ? 'Минимум 10 символов' : 'Kamida 10 ta belgi';

        if (uploadMethod === 'github') {
            if (!form.github_url.trim()) e.github_url = ru ? 'Введите GitHub ссылку' : 'GitHub havolasini kiriting';
        } else if (!formZipFile) {
            e.zip = ru ? 'Выберите ZIP-файл' : 'ZIP-faylni tanlang';
        } else if (formZipFile.size === 0) {
            e.zip = ru ? 'ZIP-файл пустой' : "ZIP-fayl bo'sh";
        } else if (formZipFile.size > 15 * 1024 * 1024) {
            e.zip = ru ? 'Файл превышает 15MB' : '15MB dan oshadi';
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

            // The project metadata save is the primary action; ZIP upload is
            // a separate request. Don't silently swallow ZIP failures — the
            // student needs to know the file didn't go through.
            let zipUploadFailed = false;
            if (uploadMethod === 'zip' && formZipFile) {
                try {
                    await uploadZipForProject(res.id, formZipFile);
                } catch (_) {
                    zipUploadFailed = true;
                }
            }

            setProjects(p => p.map(pr => pr.id === res.id ? res : pr));
            setDetail(res);
            setEditModal(false);
            setFormZipFile(null);

            if (zipUploadFailed) {
                setUploadMsg(ru ? '⚠️ Проект сохранён, но ZIP не загрузился. Загрузите файл ещё раз.' : '⚠️ Loyiha saqlandi, lekin ZIP yuklanmadi. Faylni qayta yuklang.');
                setTimeout(() => setUploadMsg(''), 6000);
            }
        } catch {
            setApiError(ru ? 'Ошибка при обновлении проекта' : 'Loyihani yangilashda xatolik');
        } finally {
            setSaving(false);
        }
    };

    /* ── ZIP Upload Helper ── */
    const uploadZipForProject = async (projectId, file) => {
        const formData = new FormData();
        formData.append('file', file);
        await request(`${API_URL}v1/project/${projectId}/upload-zip`, 'POST', formData, headers());
    };

    /* ── Other handlers ── */
    const handleSubmit = (projectId) => {
        request(`${API_URL}v1/project/${projectId}/submit`, 'POST', JSON.stringify({}), headers())
            .then(() => {
                setProjects(p => p.map(pr => pr.id === projectId ? { ...pr, status: 'Submitted' } : pr));
                setDetail(d => d ? { ...d, status: 'Submitted' } : d);
                setUploadMsg(ru ? '✅ Проект отправлен на проверку' : '✅ Loyiha tekshiruvga yuborildi');
                setTimeout(() => setUploadMsg(''), 4000);
            })
            .catch(() => {
                setUploadMsg(ru ? '❌ Не удалось отправить. Попробуйте ещё раз.' : '❌ Yuborib bo‘lmadi. Qayta urinib ko‘ring.');
                setTimeout(() => setUploadMsg(''), 5000);
            });
    };

    const handleDelete = (projectId) => {
        setConfirmDeleteId(projectId);
    };

    const doDeleteProject = (projectId) => {
        setConfirmDeleteId(null);
        request(`${API_URL}v1/project/${projectId}`, 'DELETE', null, headers())
            .then(() => {
                setProjects(p => p.filter(pr => pr.id !== projectId));
                setDetail(null);
                setUploadMsg(ru ? '✅ Проект удалён' : '✅ Loyiha o‘chirildi');
                setTimeout(() => setUploadMsg(''), 4000);
            })
            .catch(() => {
                setUploadMsg(ru ? '❌ Не удалось удалить. Попробуйте ещё раз.' : '❌ O‘chirib bo‘lmadi. Qayta urinib ko‘ring.');
                setTimeout(() => setUploadMsg(''), 5000);
            });
    };

    const handleZipUpload = (projectId, file) => {
        if (!file || file.size === 0 || file.size > 15 * 1024 * 1024) {
            setUploadMsg(ru ? '❌ Некорректный файл' : '❌ Noto‘g‘ri fayl');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        setUploading(true);
        setUploadMsg('');

        request(`${API_URL}v1/project/${projectId}/upload-zip`, 'POST', formData, headers())
            .then(() => {
                setUploadMsg(ru ? '✅ ZIP загружен успешно' : '✅ ZIP muvaffaqiyatli yuklandi');
                setSelectedFile(null);
                return request(`${API_URL}v1/project/${projectId}`, 'GET', null, headers());
            })
            .then(res => {
                if (res) {
                    setProjects(p => p.map(pr => pr.id === projectId ? res : pr));
                    setDetail(res);
                }
            })
            .catch(() => setUploadMsg(ru ? '❌ Ошибка загрузки' : '❌ Yuklashda xatolik'))
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
                setFileUrlMsg(ru ? '✅ Ссылка обновлена' : '✅ Havola yangilandi');
                setShowFileUrlEdit(false);
            })
            .catch(() => setFileUrlMsg(ru ? '❌ Ошибка обновления' : '❌ Yangilashda xatolik'))
            .finally(() => setFileUrlSaving(false));
    };

    const handleAiReview = (projectId) => {
        setAiLoading(true);
        setAiResult(null);
        // Router mount is /ai (not /project) — see backend/app/api/v1/router.py
        request(`${API_URL}v1/ai/${projectId}/ai-review`, 'POST', JSON.stringify({}), headers())
            .then(res => {
                // Server already returns a structured object; defensively
                // handle the legacy string path too.
                if (typeof res === 'string') {
                    try { setAiResult(JSON.parse(res)); }
                    catch { setAiResult({ error: 'parse_failed', errorMessage: res }); }
                } else {
                    setAiResult(res);
                }
            })
            .catch(e => {
                const status = e?.status;
                // FastAPI puts the human message in response.data.detail.
                const detail = e?.response?.data?.detail
                    || e?.message
                    || (ru ? 'AI-проверка не удалась' : 'AI-tekshiruv muvaffaqiyatsiz tugadi');
                setAiResult({
                    error: 'request_failed',
                    errorStatus: status,
                    errorMessage: detail,
                });
            })
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

    const STATUS_GROUP = (s) =>
        /approved|reviewed/i.test(s) ? 'approved'
        : /submitted|under review/i.test(s) ? 'review'
        : /rejected/i.test(s) ? 'rejected' : 'draft';
    const filtered = projects.filter(p =>
        (!search || (p.title || '').toLowerCase().includes(search.toLowerCase())) &&
        (statusFilter === 'all' || STATUS_GROUP(p.status) === statusFilter)
    );
    const statusOptions = [
        { v: 'all', label: ru ? 'Все статусы' : 'Barcha holatlar' },
        { v: 'approved', label: ru ? 'Одобренные' : 'Tasdiqlangan' },
        { v: 'review', label: ru ? 'На проверке' : 'Tekshiruvda' },
        { v: 'rejected', label: ru ? 'Отклонённые' : 'Rad etilgan' },
        { v: 'draft', label: ru ? 'Черновики' : 'Qoralama' },
    ];

    return (
        <div className="mpx-dark">
            <AppHeader />
            <div className="mpx-shell">
                <CodeCheckBanner />
                <div className="mpx-header">
                    <h1 className="mpx-title">{ru ? 'Мои проекты' : 'Mening loyihalarim'}</h1>
                    <div className="mpx-tools">
                        <div className="mpx-search">
                            <Search size={16} className="mpx-search-ic" />
                            <input value={search} onChange={e => setSearch(e.target.value)}
                                placeholder={ru ? 'Поиск...' : 'Qidirish...'} />
                        </div>
                        <select className="mpx-select" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
                            {statusOptions.map(o => <option key={o.v} value={o.v}>{o.label}</option>)}
                        </select>
                    </div>
                </div>

                {loading ? (
                    <div className="mpx-state"><div className="mpx-spinner" /> {ru ? 'Загрузка...' : 'Yuklanmoqda...'}</div>
                ) : filtered.length === 0 ? (
                    <div className="mpx-state">📂 {projects.length === 0
                        ? (ru ? 'У вас пока нет проектов' : "Hali loyihalaringiz yo'q")
                        : (ru ? 'Ничего не найдено' : 'Hech narsa topilmadi')}</div>
                ) : (
                    <div className="mpx-grid">
                        {filtered.map(p => (
                            <ProjectCard
                                key={p.id}
                                ru={ru}
                                title={p.title}
                                status={p.status}
                                difficulty={p.difficulty_level}
                                points={p.points_earned}
                                techStack={p.technologies_used || []}
                                grade={p.grade}
                                githubUrl={p.github_url}
                                onViewCode={(url) => window.open(url, '_blank', 'noopener')}
                                onDetails={() => {
                                    setAiResult('');
                                    setUploadMsg('');
                                    setDetail(p);
                                }}
                            />
                        ))}
                    </div>
                )}
            </div>

            {/* EDIT MODAL */}
            {editModal && (
                <Modal onClose={() => setEditModal(false)}>
                    <div className="mp-modal-header">
                        <h3>{ru ? '✏️ Редактировать проект' : '✏️ Loyihani tahrirlash'}</h3>
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
                        <button className="mp-btn-cancel" onClick={() => setEditModal(false)}>{ru ? 'Отмена' : 'Bekor qilish'}</button>
                        <button className="mp-btn-save" onClick={handleUpdate} disabled={saving}>
                            {saving ? (ru ? '⏳ Сохранение...' : '⏳ Saqlanmoqda...') : (ru ? '💾 Сохранить' : '💾 Saqlash')}
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
                                {(ru ? {
                                    Draft: 'Черновик',
                                    Submitted: 'Отправлен',
                                    'Under Review': 'На проверке',
                                    Approved: 'Одобрен',
                                    Rejected: 'Отклонён'
                                } : {
                                    Draft: 'Qoralama',
                                    Submitted: 'Yuborilgan',
                                    'Under Review': 'Tekshiruvda',
                                    Approved: 'Tasdiqlangan',
                                    Rejected: 'Rad etilgan'
                                })[detail.status] || detail.status}
                            </span>
                            {detail.grade && <span className={`mp-grade mp-grade-${detail.grade}`}>{ru ? 'Оценка' : 'Baho'}: {detail.grade}</span>}
                        </div>

                        {/* Stats */}
                        <div className="mp-stats-row">
                            <div className="mp-stat">
                                <span className="mp-stat-icon" aria-hidden="true"><Trophy size={16} /></span>
                                <span className="mp-stat-val">{detail.points_earned ?? 0}</span>
                                <span className="mp-stat-label">{ru ? 'очков' : 'ball'}</span>
                            </div>
                            <div className="mp-stat">
                                <span className="mp-stat-icon">👁️</span>
                                <span className="mp-stat-val">{detail.views_count ?? 0}</span>
                                <span className="mp-stat-label">{ru ? 'просмотров' : 'ko‘rishlar'}</span>
                            </div>
                        </div>

                        {/* Description, Links, Technologies, etc. */}
                        <div className="mp-detail-row">
                            <span className="mp-detail-label">{ru ? 'Описание' : 'Tavsif'}</span>
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
                                <span className="mp-detail-label">{ru ? 'Технологии' : 'Texnologiyalar'}</span>
                                <div className="mp-card-techs">
                                    {detail.technologies_used.map((t, i) => <span key={i} className="mp-tech">{t}</span>)}
                                </div>
                            </div>
                        )}

                        {detail.instructor_feedback && (
                            <div className="mp-feedback">
                                <span className="mp-detail-label">{ru ? '💬 Отзыв преподавателя' : '💬 O‘qituvchi izohi'}</span>
                                <p>{detail.instructor_feedback}</p>
                            </div>
                        )}

                        {/* ZIP Upload Section */}
                        <div className="mp-section">
                            <span className="mp-detail-label">{ru ? '📦 ZIP-архив проекта' : '📦 Loyiha ZIP-arxivi'}</span>
                            {detail.project_files && (
                                <div className="mp-current-file">
                                    <span className="mp-current-file-label">{ru ? 'Текущий файл:' : 'Joriy fayl:'}</span>
                                    <a href={detail.project_files} target="_blank" rel="noreferrer" className="mp-link mp-link-sm">{ru ? '📎 Открыть' : '📎 Ochish'}</a>
                                </div>
                            )}
                            <ZipDropZone selectedFile={selectedFile} onFileSelect={setSelectedFile} uploading={uploading} />
                            <div className="mp-zip-row">
                                <button className="mp-btn-zip-upload" onClick={() => handleZipUpload(detail.id, selectedFile)}
                                    disabled={uploading || !selectedFile}>
                                    {uploading ? <>{ru ? 'Загрузка...' : 'Yuklanmoqda...'}</> : (ru ? '📤 Загрузить ZIP' : '📤 ZIP yuklash')}
                                </button>
                                {uploadMsg && <span className={`mp-upload-msg ${uploadMsg.startsWith('✅') ? 'success' : 'error'}`}>{uploadMsg}</span>}
                            </div>
                        </div>

                        {/* File URL */}
                        <div className="mp-section">
                            <div className="mp-section-header">
                                <span className="mp-detail-label">{ru ? '🔗 Ссылка на файл' : '🔗 Fayl havolasi'}</span>
                                <button className="mp-toggle-link" onClick={() => { setShowFileUrlEdit(v => !v); setFileUrlMsg(''); setFileUrlInput(detail.project_files || ''); }}>
                                    {showFileUrlEdit ? (ru ? 'Скрыть' : 'Yashirish') : (ru ? '✏️ Изменить' : '✏️ O‘zgartirish')}
                                </button>
                            </div>
                            {showFileUrlEdit ? (
                                <div className="mp-file-url-edit">
                                    <input className="mp-file-url-input" placeholder="https://..." value={fileUrlInput} onChange={e => setFileUrlInput(e.target.value)} />
                                    <button className="mp-btn-save mp-btn-save-sm" onClick={handlePatchFileUrl} disabled={fileUrlSaving || !fileUrlInput.trim()}>
                                        {fileUrlSaving ? '⏳' : (ru ? 'Сохранить' : 'Saqlash')}
                                    </button>
                                </div>
                            ) : detail.project_files ? (
                                <a href={detail.project_files} target="_blank" rel="noreferrer" className="mp-link">{detail.project_files}</a>
                            ) : <span className="mp-hint">{ru ? 'Ссылка не указана' : 'Havola ko‘rsatilmagan'}</span>}
                            {fileUrlMsg && <span className={`mp-upload-msg ${fileUrlMsg.startsWith('✅') ? 'success' : 'error'}`}>{fileUrlMsg}</span>}
                        </div>

                        {/* AI Review */}
                        <div className="mp-section">
                            <span className="mp-detail-label">{ru ? '🤖 AI-проверка' : '🤖 AI-tekshiruv'}</span>
                            <button className="mp-btn-ai" onClick={() => handleAiReview(detail.id)} disabled={aiLoading}>
                                {aiLoading ? (ru ? 'Анализ...' : 'Tahlil qilinmoqda...') : (ru ? '✨ Запустить AI-проверку' : '✨ AI-tekshiruvni ishga tushirish')}
                            </button>
                            <AiReviewResult data={aiResult} />
                        </div>
                    </div>

                    <div className="mp-modal-footer">
                        <button className="mp-btn-delete" onClick={() => handleDelete(detail.id)}>{ru ? '🗑️ Удалить' : '🗑️ O‘chirish'}</button>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            {detail.status === 'Draft' && (
                                <>
                                    <button className="mp-btn-edit" onClick={openEdit}>{ru ? '✏️ Изменить' : '✏️ O‘zgartirish'}</button>
                                    <button className="mp-btn-submit" onClick={() => handleSubmit(detail.id)}>{ru ? '🚀 Отправить на проверку' : '🚀 Tekshiruvga yuborish'}</button>
                                </>
                            )}
                        </div>
                    </div>
                </Modal>
            )}

            {confirmDeleteId && (
                <ConfirmModal
                    title={ru ? 'Удалить проект?' : 'Loyiha o‘chirilsinmi?'}
                    onConfirm={() => doDeleteProject(confirmDeleteId)}
                    onClose={() => setConfirmDeleteId(null)}
                />
            )}
        </div>
    );
}

export default MyProjects;