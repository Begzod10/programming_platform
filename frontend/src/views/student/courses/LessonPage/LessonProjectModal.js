import React, { useState, useRef, useCallback } from 'react';
import ReactDOM from 'react-dom';
import { Link } from 'lucide-react';

/* ─────────────────────────────────────────────────────────────
   Upload Method Selector
───────────────────────────────────────────────────────────── */
const UploadMethodSelector = ({ method, onChange }) => (
    <div className="slp-method-selector">
        <button
            type="button"
            className={`slp-method-btn ${method === 'github' ? 'slp-method-active' : ''}`}
            onClick={() => onChange('github')}
        >
            <span className="slp-method-icon">
                <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
                    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
                </svg>
            </span>
            <span className="slp-method-label">
                <span className="slp-method-title">GitHub</span>
                <span className="slp-method-sub">Ссылка на репозиторий</span>
            </span>
            {method === 'github' && <span className="slp-method-check">✓</span>}
        </button>

        <div className="slp-method-divider"><span>или</span></div>

        <button
            type="button"
            className={`slp-method-btn ${method === 'zip' ? 'slp-method-active slp-method-active-zip' : ''}`}
            onClick={() => onChange('zip')}
        >
            <span className="slp-method-icon slp-method-icon-zip">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" width="18" height="18">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
            </span>
            <span className="slp-method-label">
                <span className="slp-method-title">ZIP-архив</span>
                <span className="slp-method-sub">Загрузить файл до 15MB</span>
            </span>
            {method === 'zip' && <span className="slp-method-check">✓</span>}
        </button>
    </div>
);

/* ─────────────────────────────────────────────────────────────
   ZIP Drop Zone
───────────────────────────────────────────────────────────── */
const ZipDropZone = ({selectedFile, onFileSelect, uploading}) => {
    const fileInputRef = useRef(null);
    const [dragging, setDragging] = useState(false);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files[0];
        if (file && file.name.endsWith('.zip')) onFileSelect(file);
    }, [onFileSelect]);

    const isOverLimit = selectedFile && selectedFile.size > 15 * 1024 * 1024;
    const isEmpty     = selectedFile && selectedFile.size === 0;

    return (
        <div
            className={`slp-dropzone ${dragging ? 'slp-dropzone-drag' : ''}`}
            onDrop={handleDrop}
            onDragOver={e => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onClick={() => !uploading && fileInputRef.current?.click()}
        >
            <input
                ref={fileInputRef}
                type="file"
                accept=".zip"
                style={{display: 'none'}}
                onChange={e => {
                    const file = e.target.files[0];
                    if (file) { onFileSelect(file); e.target.value = ''; }
                }}
            />
            {selectedFile ? (
                <>
                    <div className="slp-dropzone-selected">
                        <div className="slp-dz-file-icon">{isEmpty ? '⚠️' : '📦'}</div>
                        <div className="slp-dropzone-info">
                            <span className="slp-dropzone-name">{selectedFile.name}</span>
                            <span className={`slp-dropzone-size ${isOverLimit || isEmpty ? 'over' : ''}`}>
                                {isEmpty
                                    ? '⚠️ Файл пустой — выберите другой'
                                    : `${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB${isOverLimit ? ' · ⚠️ Превышает 15MB' : ''}`
                                }
                            </span>
                        </div>
                        <button className="slp-dropzone-clear" onClick={e => {
                            e.stopPropagation();
                            onFileSelect(null);
                        }}>✕</button>
                    </div>
                    {!isEmpty && (
                        <div className="slp-dz-bar-wrap">
                            <div
                                className={`slp-dz-bar ${isOverLimit ? 'over' : ''}`}
                                style={{width: `${Math.min((selectedFile.size / (15 * 1024 * 1024)) * 100, 100)}%`}}
                            />
                        </div>
                    )}
                </>
            ) : (
                <div className="slp-dropzone-empty">
                    <div className={`slp-dz-icon ${dragging ? 'drag' : ''}`}>
                        {dragging ? '🎯' : '📁'}
                    </div>
                    <span className="slp-dropzone-text">
                        {dragging ? 'Отпустите файл здесь' : 'Перетащите .zip или нажмите для выбора'}
                    </span>
                    <span className="slp-dropzone-hint">Максимум 15 MB · только .zip</span>
                </div>
            )}
        </div>
    );
};

/* ═══════════════════════════════════════════════════════════
   PROJECT SUBMIT MODAL
═══════════════════════════════════════════════════════════ */
export const LessonProjectModal = ({
    isOpen,
    onClose,
    projectSection,
    uploadMethod,
    onMethodChange,
    projectForm,
    setProjectForm,
    formErrors,
    setFormErrors,
    zipFile,
    setZipFile,
    zipUploading,
    zipMsg,
    projectError,
    projectSaving,
    isSubmitDisabled,
    onSubmit,
    quotaExhausted,
    quotaMessage,
    keystrokeCountRef,
    pasteCountRef,
}) => {
    if (!isOpen) return null;

    return ReactDOM.createPortal(
        <div className="slp-overlay" onClick={onClose}>
            <div className="slp-modal slp-modal-wide" onClick={e => e.stopPropagation()}>
                <div className="slp-modal-header">
                    <div className="slp-modal-header-inner">
                        <div className="slp-modal-header-icon">🚀</div>
                        <div>
                            <h3>Загрузить проект</h3>
                            <p className="slp-modal-header-sub">Отправьте ссылку и дождитесь проверки</p>
                        </div>
                    </div>
                    <button className="slp-modal-close" onClick={onClose}>✕</button>
                </div>

                <div className="slp-modal-body">
                    <div className="slp-modal-task-banner">
                        <span className="slp-modal-task-icon">📌</span>
                        <span>{projectSection?.label || 'Практическое задание'}</span>
                    </div>

                    <div className="slp-modal-field">
                        <label>Способ загрузки кода <span className="slp-field-required">*</span></label>
                        <UploadMethodSelector method={uploadMethod} onChange={onMethodChange}/>
                    </div>

                    <div className={`slp-source-panel ${uploadMethod === 'github' ? 'slp-source-panel-visible' : ''}`}>
                        <div className="slp-modal-field">
                            <label>GitHub URL</label>
                            <div className={`slp-input-wrap ${formErrors.github_url ? 'slp-input-error' : ''}`}>
                                <span className="slp-input-prefix" aria-hidden="true"><Link size={14} /></span>
                                <input
                                    placeholder="https://github.com/username/repo"
                                    value={projectForm.github_url}
                                    onChange={e => {
                                        setProjectForm(f => ({...f, github_url: e.target.value}));
                                        setFormErrors(e2 => ({...e2, github_url: ''}));
                                    }}
                                />
                            </div>
                            {formErrors.github_url && <span className="slp-field-error">{formErrors.github_url}</span>}
                        </div>
                    </div>

                    <div className={`slp-source-panel ${uploadMethod === 'zip' ? 'slp-source-panel-visible' : ''}`}>
                        <div className="slp-modal-field">
                            <label>ZIP-архив</label>
                            <ZipDropZone
                                selectedFile={zipFile}
                                onFileSelect={f => { setZipFile(f); setFormErrors(e => ({...e, zip: ''})); }}
                                uploading={zipUploading}
                            />
                            {formErrors.zip && <span className="slp-field-error">{formErrors.zip}</span>}
                        </div>
                    </div>

                    <div className="slp-modal-field">
                        <label>
                            Live Demo URL
                            <span className="slp-label-opt">необязательно</span>
                        </label>
                        <div className="slp-input-wrap">
                            <span className="slp-input-prefix">🌐</span>
                            <input
                                placeholder="https://myproject.com"
                                value={projectForm.live_demo_url}
                                onChange={e => setProjectForm(f => ({...f, live_demo_url: e.target.value}))}
                            />
                        </div>
                    </div>

                    <div className="slp-modal-field">
                        <label>
                            Комментарий
                            <span className="slp-label-opt">необязательно</span>
                        </label>
                        <textarea
                            placeholder="Расскажите что реализовали, какие технологии использовали..."
                            rows={3}
                            value={projectForm.description}
                            onChange={e => setProjectForm(f => ({...f, description: e.target.value}))}
                            onKeyDown={() => { keystrokeCountRef.current += 1; }}
                            onPaste={() => { pasteCountRef.current += 1; }}
                        />
                    </div>

                    {zipMsg && (
                        <div className={`slp-zip-msg ${zipMsg.startsWith('✅') ? 'success' : 'warn'}`}>
                            {zipMsg}
                        </div>
                    )}
                    {quotaExhausted && (
                        <div className="slp-project-error" style={{background: '#fffbeb', color: '#92400e', border: '1px solid #f59e0b'}}>⏳ {quotaMessage}</div>
                    )}
                    {projectError && (
                        <div className="slp-project-error">⚠️ {projectError}</div>
                    )}
                </div>

                <div className="slp-modal-footer">
                    <button className="slp-modal-cancel" onClick={onClose}>Отмена</button>
                    <button
                        className="slp-modal-submit"
                        onClick={onSubmit}
                        disabled={isSubmitDisabled()}
                    >
                        {projectSaving
                            ? <><span className="slp-btn-spin"/>{zipUploading ? 'Загрузка ZIP...' : 'Отправка...'}</>
                            : '🚀 Отправить проект'
                        }
                    </button>
                </div>
            </div>
        </div>,
        document.body
    );
};
