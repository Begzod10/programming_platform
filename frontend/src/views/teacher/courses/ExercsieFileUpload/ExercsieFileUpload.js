import React, { useState, useRef, useEffect, useCallback } from 'react';
import { highlight } from '../../../../utils/highlight';
import './ExercsieFileUpload.css';
import './ExercsieFileUpload.additions.css'

/* ─────────────────────────────────────────────
   CONSTANTS
───────────────────────────────────────────── */
const LANG_MAP = {
  html: 'html', htm: 'html',
  css: 'css',
  js: 'javascript', jsx: 'jsx', ts: 'typescript', tsx: 'tsx',
  py: 'python', python: 'python',
  java: 'java',
  cpp: 'cpp', c: 'c',
  rs: 'rust',
  go: 'go',
  sql: 'sql',
  sh: 'bash', bash: 'bash',
  json: 'json',
  md: 'markdown',
  xml: 'xml',
  yaml: 'yaml', yml: 'yaml',
  php: 'php',
  rb: 'ruby',
  swift: 'swift',
  kt: 'kotlin',
};

const PREVIEW_SUPPORTED = ['html', 'htm'];

const LANG_COLORS = {
  html:       { bg: 'rgba(231,76,60,0.12)',   color: '#e74c3c',  icon: '🌐' },
  css:        { bg: 'rgba(52,152,219,0.12)',   color: '#3498db',  icon: '🎨' },
  javascript: { bg: 'rgba(241,196,15,0.12)',   color: '#c0922b',  icon: '⚡' },
  jsx:        { bg: 'rgba(97,218,251,0.12)',   color: '#00b8d9',  icon: '⚛️' },
  typescript: { bg: 'rgba(49,120,198,0.12)',   color: '#3178c6',  icon: '🔷' },
  tsx:        { bg: 'rgba(49,120,198,0.12)',   color: '#3178c6',  icon: '⚛️' },
  python:     { bg: 'rgba(55,118,171,0.12)',   color: '#3776ab',  icon: '🐍' },
  java:       { bg: 'rgba(176,114,25,0.12)',   color: '#b07219',  icon: '☕' },
  rust:       { bg: 'rgba(222,165,132,0.12)',  color: '#ce422b',  icon: '⚙️' },
  go:         { bg: 'rgba(0,173,216,0.12)',    color: '#00add8',  icon: '🐹' },
  sql:        { bg: 'rgba(255,102,0,0.12)',    color: '#ff6600',  icon: '🗄️' },
  bash:       { bg: 'rgba(26,26,46,0.08)',     color: '#4a4a6a',  icon: '💻' },
  json:       { bg: 'rgba(150,150,150,0.12)',  color: '#888',     icon: '{}' },
  default:    { bg: 'rgba(108,92,231,0.10)',   color: '#6c5ce7',  icon: '📄' },
};

const getLangMeta = (lang) => LANG_COLORS[lang] || LANG_COLORS.default;
const getExt = (filename) => (filename || '').split('.').pop().toLowerCase();
const getLang = (filename) => LANG_MAP[getExt(filename)] || getExt(filename);
const formatSize = (bytes) =>
  bytes < 1024 ? `${bytes} B` :
  bytes < 1048576 ? `${(bytes / 1024).toFixed(1)} KB` :
  `${(bytes / 1048576).toFixed(2)} MB`;

/* ─────────────────────────────────────────────
   CODE VIEWER / EDITOR (toggleable)
───────────────────────────────────────────── */
const CodeViewer = ({ code, lang, filename, onCodeChange, saving }) => {
  const [copied, setCopied] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [localCode, setLocalCode] = useState(code || '');
  const textareaRef = useRef(null);

  // Sync if parent code changes (e.g. after save)
  useEffect(() => {
    if (!editMode) setLocalCode(code || '');
  }, [code, editMode]);

  const lines = (localCode).split('\n');
  const highlighted = highlight(localCode, lang);
  const highlightedLines = highlighted.split('\n');
  const meta = getLangMeta(lang);

  const copy = () => {
    navigator.clipboard.writeText(localCode).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleSave = () => {
    onCodeChange && onCodeChange(localCode);
    setEditMode(false);
  };

  const handleCancel = () => {
    setLocalCode(code || '');
    setEditMode(false);
  };

  // Auto-indent on Tab key in textarea
  const handleKeyDown = (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const ta = textareaRef.current;
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      const newVal = localCode.substring(0, start) + '  ' + localCode.substring(end);
      setLocalCode(newVal);
      requestAnimationFrame(() => {
        ta.selectionStart = ta.selectionEnd = start + 2;
      });
    }
    if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSave();
    }
  };

  return (
    <div className="efu-code-viewer">
      <div className="efu-code-topbar">
        <div className="efu-code-topbar-left">
          <div className="efu-traffic">
            <span className="efu-dot efu-dot--red" />
            <span className="efu-dot efu-dot--yellow" />
            <span className="efu-dot efu-dot--green" />
          </div>
          <span className="efu-code-filename">{filename}</span>
          <span className="efu-lang-pill" style={{ background: meta.bg, color: meta.color }}>
            {meta.icon} {lang}
          </span>
        </div>
        <div className="efu-code-topbar-right">
          <span className="efu-line-count">{lines.length} строк</span>
          {!editMode ? (
            <>
              <button className="efu-copy-btn" onClick={copy}>
                {copied ? '✅ Скопировано' : '📋 Копировать'}
              </button>
              {onCodeChange && (
                <button className="efu-edit-toggle-btn" onClick={() => setEditMode(true)}>
                  ✏️ Редактировать
                </button>
              )}
            </>
          ) : (
            <>
              <button className="efu-save-code-btn" onClick={handleSave} disabled={saving}>
                {saving ? '⏳ Сохранение...' : '💾 Сохранить'}
              </button>
              <button className="efu-cancel-code-btn" onClick={handleCancel}>
                ✕ Отмена
              </button>
            </>
          )}
        </div>
      </div>

      {editMode ? (
        <div className="efu-editor-wrap">
          {/* Line numbers synced with textarea */}
          <div className="efu-line-nums efu-line-nums--edit" aria-hidden>
            {lines.map((_, i) => (
              <div key={i} className="efu-line-num">{i + 1}</div>
            ))}
          </div>
          <textarea
            ref={textareaRef}
            className="efu-code-textarea"
            value={localCode}
            onChange={e => setLocalCode(e.target.value)}
            onKeyDown={handleKeyDown}
            spellCheck={false}
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
          />
        </div>
      ) : (
        <div className="efu-code-body">
          <div className="efu-line-nums" aria-hidden>
            {lines.map((_, i) => (
              <div key={i} className="efu-line-num">{i + 1}</div>
            ))}
          </div>
          <pre className="efu-code-pre">
            {highlightedLines.map((line, i) => (
              <div key={i} className="efu-code-line" dangerouslySetInnerHTML={{ __html: line || ' ' }} />
            ))}
          </pre>
        </div>
      )}
      {editMode && (
        <div className="efu-editor-hint">
          💡 Tab — отступ · Ctrl+S — сохранить
        </div>
      )}
    </div>
  );
};

/* ─────────────────────────────────────────────
   HTML PREVIEW — uses srcdoc to avoid cross-origin error
───────────────────────────────────────────── */
const HtmlPreview = ({ code }) => {
  return (
    <div className="efu-preview-wrap">
      <div className="efu-preview-bar">
        <span className="efu-preview-label">🖥️ Живой предпросмотр</span>
        <div className="efu-browser-dots">
          <span /><span /><span />
        </div>
      </div>
      {/* srcdoc avoids cross-origin issues entirely — no contentDocument access needed */}
      <iframe
        className="efu-preview-iframe"
        sandbox="allow-scripts"
        title="HTML Preview"
        srcDoc={code || ''}
      />
    </div>
  );
};

/* ─────────────────────────────────────────────
   FILE CARD
───────────────────────────────────────────── */
const FileCard = ({ file, onDelete, onCodeSaved, onPreviewUpdated, apiBaseUrl, lessonId }) => {
  const [view, setView] = useState('code');
  const [expanded, setExpanded] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [previewUrl, setPreviewUrl] = useState(file.preview_image_url || null);
  const [uploadingPreview, setUploadingPreview] = useState(false);
  const previewInputRef = useRef(null);

  const lang = getLang(file.filename || file.name || '');
  const meta = getLangMeta(lang);
  const canPreview = PREVIEW_SUPPORTED.includes(getExt(file.filename || file.name || ''));
  const code = file.code || file.content || '';

  const handleDelete = async () => {
    if (!window.confirm('Удалить файл?')) return;
    setDeleting(true);
    try {
      if (apiBaseUrl && lessonId && file.id) {
        await fetch(`${apiBaseUrl}/${lessonId}/files/${file.id}`, { method: 'DELETE' });
      }
      onDelete(file.id || file._localId);
    } catch {
      setErrorMsg('Не удалось удалить файл. Попробуйте ещё раз.');
      setTimeout(() => setErrorMsg(''), 5000);
      setDeleting(false);
    }
  };

  const handlePreviewUpload = async (e) => {
    const imgFile = e.target.files?.[0];
    if (!imgFile || !apiBaseUrl || !lessonId || !file.id) return;
    setUploadingPreview(true);
    setErrorMsg('');
    try {
      const formData = new FormData();
      formData.append('image', imgFile);
      const resp = await fetch(`${apiBaseUrl}/${lessonId}/files/${file.id}/preview`, {
        method: 'POST',
        body: formData,
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      setPreviewUrl(data.preview_image_url);
      onPreviewUpdated && onPreviewUpdated(file.id, data.preview_image_url);
    } catch {
      setErrorMsg('Rasmni yuklashda xato yuz berdi.');
      setTimeout(() => setErrorMsg(''), 5000);
    } finally {
      setUploadingPreview(false);
      e.target.value = '';
    }
  };

  const handlePreviewDelete = async () => {
    if (!apiBaseUrl || !lessonId || !file.id) return;
    try {
      await fetch(`${apiBaseUrl}/${lessonId}/files/${file.id}/preview`, { method: 'DELETE' });
      setPreviewUrl(null);
      onPreviewUpdated && onPreviewUpdated(file.id, null);
    } catch {
      setErrorMsg('Rasmni o\'chirishda xato.');
      setTimeout(() => setErrorMsg(''), 5000);
    }
  };

  const handleCodeChange = async (newCode) => {
    setSaving(true);
    setErrorMsg('');
    try {
      if (apiBaseUrl && lessonId && file.id) {
        const resp = await fetch(`${apiBaseUrl}/${lessonId}/files/${file.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ label: file.label || '', code_content: newCode }),
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const updated = await resp.json();
        onCodeSaved && onCodeSaved(file.id || file._localId, newCode, updated);
      } else {
        // Offline mode — just propagate locally
        onCodeSaved && onCodeSaved(file.id || file._localId, newCode, null);
      }
    } catch {
      setErrorMsg('Не удалось сохранить код. Изменения остались только локально.');
      setTimeout(() => setErrorMsg(''), 6000);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className={`efu-file-card ${expanded ? '' : 'efu-file-card--collapsed'}`}>
      {errorMsg && (
        <div
          role="alert"
          style={{
            margin: '10px 14px 0',
            padding: '8px 12px',
            borderRadius: 8,
            background: 'rgba(239, 68, 68, 0.08)',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            color: '#b42323',
            fontSize: 12.5,
            fontWeight: 600,
          }}
        >
          ⚠ {errorMsg}
        </div>
      )}
      <div className="efu-file-card-head">
        <div className="efu-file-card-head-left">
          <span className="efu-file-lang-icon" style={{ background: meta.bg, color: meta.color }}>
            {meta.icon}
          </span>
          <div className="efu-file-card-info">
            <span className="efu-file-card-name">{file.filename || file.name}</span>
            <span className="efu-file-card-meta">
              {file.size ? formatSize(file.size) : ''}
              {file.size ? ' · ' : ''}
              {code.split('\n').length} строк
            </span>
          </div>
          {file.label && <span className="efu-file-label-badge">{file.label}</span>}
        </div>
        <div className="efu-file-card-head-right">
          {canPreview && expanded && (
            <div className="efu-view-toggle">
              <button
                className={`efu-view-toggle-btn ${view === 'code' ? 'active' : ''}`}
                onClick={() => setView('code')}
              >
                &lt;/&gt; Код
              </button>
              <button
                className={`efu-view-toggle-btn ${view === 'preview' ? 'active' : ''}`}
                onClick={() => setView('preview')}
              >
                🖥️ Превью
              </button>
            </div>
          )}
          <button className="efu-file-collapse-btn" onClick={() => setExpanded(e => !e)}>
            {expanded ? '▲' : '▼'}
          </button>
          <button
            className="efu-file-del-btn"
            onClick={handleDelete}
            disabled={deleting}
            title="Удалить файл"
          >
            {deleting ? '⏳' : '✕'}
          </button>
        </div>
      </div>

      {expanded && (
        <div className="efu-file-card-body">
          {view === 'code' ? (
            <CodeViewer
              code={code}
              lang={lang}
              filename={file.filename || file.name}
              onCodeChange={handleCodeChange}
              saving={saving}
            />
          ) : (
            <HtmlPreview code={code} />
          )}

          {/* ── Preview image section ── */}
          <div className="efu-preview-img-section">
            <span className="efu-preview-img-label">🖼 Loyiha ko'rinishi (preview rasm)</span>
            {previewUrl ? (
              <div className="efu-preview-img-wrap">
                <img
                  src={`${(apiBaseUrl || '').replace('/lessons', '').replace('/api/v1', '')}${previewUrl}`}
                  alt="preview"
                  className="efu-preview-img"
                />
                <div className="efu-preview-img-actions">
                  <label className="efu-preview-img-btn" title="Rasmni almashtirish">
                    {uploadingPreview ? '⏳' : '🔄 Almashtirish'}
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/webp,image/gif"
                      style={{ display: 'none' }}
                      onChange={handlePreviewUpload}
                    />
                  </label>
                  <button className="efu-preview-img-del-btn" onClick={handlePreviewDelete} title="O'chirish">
                    🗑 O'chirish
                  </button>
                </div>
              </div>
            ) : (
              <label className="efu-preview-img-upload-btn">
                {uploadingPreview ? '⏳ Yuklanmoqda...' : '📷 Rasm yuklash'}
                <input
                  ref={previewInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp,image/gif"
                  style={{ display: 'none' }}
                  onChange={handlePreviewUpload}
                  disabled={uploadingPreview}
                />
              </label>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

/* ─────────────────────────────────────────────
   UPLOAD ZONE
───────────────────────────────────────────── */
const UploadZone = ({ onFiles, uploading }) => {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [rejectedNames, setRejectedNames] = useState([]);

  const ACCEPTED = '.html,.htm,.css,.js,.jsx,.ts,.tsx,.py,.java,.cpp,.c,.rs,.go,.sql,.sh,.json,.md,.xml,.yaml,.yml,.php,.rb,.swift,.kt';

  const handleFiles = (fileList) => {
    const incoming = Array.from(fileList);
    const accepted = [];
    const rejected = [];
    for (const f of incoming) {
      const ext = getExt(f.name);
      if (Object.keys(LANG_MAP).includes(ext)) accepted.push(f);
      else rejected.push(f.name);
    }
    if (rejected.length) {
      setRejectedNames(rejected);
      // Self-clear after a beat so the warning doesn't stick once the
      // teacher has had a chance to read it.
      setTimeout(() => setRejectedNames([]), 6000);
    } else {
      setRejectedNames([]);
    }
    if (accepted.length) onFiles(accepted);
  };

  return (
    <div
      className={`efu-upload-zone ${dragOver ? 'efu-upload-zone--over' : ''} ${uploading ? 'efu-upload-zone--loading' : ''}`}
      onClick={() => !uploading && inputRef.current?.click()}
      onDragOver={e => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={e => { e.preventDefault(); setDragOver(false); handleFiles(e.dataTransfer.files); }}
    >
      <input
        ref={inputRef}
        type="file"
        multiple
        accept={ACCEPTED}
        style={{ display: 'none' }}
        onChange={e => handleFiles(e.target.files)}
      />
      {uploading ? (
        <div className="efu-upload-loading">
          <div className="efu-upload-spinner" />
          <span>Загрузка и чтение файлов...</span>
        </div>
      ) : (
        <>
          <div className="efu-upload-icon">{dragOver ? '📂' : '📁'}</div>
          <div className="efu-upload-text">
            <strong>{dragOver ? 'Отпустите файлы' : 'Перетащите файлы или нажмите'}</strong>
            <span>HTML · CSS · JS · JSX · TS · TSX · Python · Java · C · C++ · Rust · Go · SQL · Bash и др.</span>
          </div>
          <div className="efu-upload-hint-chips">
            {['HTML', 'CSS', 'JS', 'Python', 'SQL', 'Go'].map(l => (
              <span key={l} className="efu-hint-chip">{l}</span>
            ))}
            <span className="efu-hint-chip efu-hint-chip--more">+ещё</span>
          </div>
          {rejectedNames.length > 0 && (
            <div
              className="efu-upload-reject"
              role="alert"
              onClick={e => e.stopPropagation()}
              style={{
                marginTop: 14,
                padding: '10px 14px',
                borderRadius: 10,
                background: 'rgba(239, 68, 68, 0.08)',
                border: '1px solid rgba(239, 68, 68, 0.25)',
                color: '#b42323',
                fontSize: 13,
                fontWeight: 600,
                textAlign: 'left',
              }}
            >
              ⚠ Эти файлы не поддерживаются и были пропущены:&nbsp;
              {rejectedNames.slice(0, 3).join(', ')}
              {rejectedNames.length > 3 && ` и ещё ${rejectedNames.length - 3}`}
            </div>
          )}
        </>
      )}
    </div>
  );
};

/* ─────────────────────────────────────────────
   MAIN: ExerciseFileUpload
───────────────────────────────────────────── */
const ExerciseFileUpload = ({ lessonId, apiBaseUrl = '/api/v1', files = [], onChange }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  /* Load existing files from backend on mount */
  useEffect(() => {
    if (!lessonId || !apiBaseUrl) return;
    fetch(`${apiBaseUrl}/${lessonId}/files`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          onChange(data);
        }
      })
      .catch(() => {});
  }, [lessonId]);

  const handleUpload = async (fileList) => {
    setError(null);
    setUploading(true);
    const results = [];

    for (const file of fileList) {
      try {
        const content = await new Promise((res, rej) => {
          const reader = new FileReader();
          reader.onload = e => res(e.target.result);
          reader.onerror = () => rej(new Error('Read error'));
          reader.readAsText(file);
        });

        if (apiBaseUrl && lessonId) {
          const fd = new FormData();
          fd.append('file', file);
          const resp = await fetch(`${apiBaseUrl}/${lessonId}/files`, {
            method: 'POST',
            body: fd,
          });
          if (resp.ok) {
            const saved = await resp.json();
            results.push({
              ...saved,
              content,
              code: saved.code_content || content,
              _localId: Date.now() + Math.random(),
            });
          } else {
            throw new Error(`HTTP ${resp.status}`);
          }
        } else {
          results.push({
            _localId: Date.now() + Math.random(),
            id: null,
            filename: file.name,
            name: file.name,
            size: file.size,
            content,
            code: content,
            label: '',
          });
        }
      } catch (err) {
        setError(`Ошибка при загрузке ${file.name}: ${err.message}`);
      }
    }

    onChange([...files, ...results]);
    setUploading(false);
  };

  const handleDelete = (idOrLocalId) => {
    onChange(files.filter(f => (f.id || f._localId) !== idOrLocalId));
  };

  // Called when user saves edited code — update the file in parent state
  const handleCodeSaved = useCallback((idOrLocalId, newCode) => {
    onChange(files.map(f =>
      (f.id || f._localId) === idOrLocalId
        ? { ...f, code: newCode, content: newCode, code_content: newCode }
        : f
    ));
  }, [files, onChange]);

  const handlePreviewUpdated = useCallback((idOrLocalId, newUrl) => {
    onChange(files.map(f =>
      (f.id || f._localId) === idOrLocalId
        ? { ...f, preview_image_url: newUrl }
        : f
    ));
  }, [files, onChange]);

  const totalLines = files.reduce((sum, f) =>
    sum + ((f.code || f.content || '').split('\n').length), 0);

  return (
    <div className="efu-root">
      <div className="efu-header">
        <div className="efu-header-left">
          <span className="efu-header-icon">🗂️</span>
          <div>
            <div className="efu-header-title">Файлы упражнения</div>
            <div className="efu-header-sub">
              Прикрепите код-файлы — студенты увидят их с подсветкой синтаксиса
            </div>
          </div>
        </div>
        {files.length > 0 && (
          <div className="efu-header-stats">
            <span className="efu-stat-chip">
              📦 {files.length} файл{files.length === 1 ? '' : files.length < 5 ? 'а' : 'ов'}
            </span>
            <span className="efu-stat-chip">📝 {totalLines.toLocaleString()} строк</span>
          </div>
        )}
      </div>

      {error && (
        <div className="efu-error">
          ⚠️ {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <UploadZone onFiles={handleUpload} uploading={uploading} />

      {files.length > 0 && (
        <div className="efu-files-list">
          {files.map((file) => (
            <FileCard
              key={file.id || file._localId}
              file={file}
              onDelete={handleDelete}
              onCodeSaved={handleCodeSaved}
              onPreviewUpdated={handlePreviewUpdated}
              apiBaseUrl={apiBaseUrl}
              lessonId={lessonId}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default ExerciseFileUpload;