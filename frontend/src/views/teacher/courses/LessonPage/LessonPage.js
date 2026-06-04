import React, { useState, useEffect } from 'react';
import mermaid from 'mermaid';
import './LessonPage.css';
import './LessonPage.additions.css'
import '../Exercise additions/Lessonpage exercise additions.css'
import { SECTION_TYPES, getYTId } from '../../../../constants/courseUtils';
import { sanitizeHtml } from '../../../../utils/sanitize';

mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    securityLevel: 'loose',
    flowchart: { useMaxWidth: false, htmlLabels: true },
    sequence: { useMaxWidth: false },
    themeVariables: {
        fontFamily:
            'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    },
});

/* ── Exercise meta ── */
const EX_TYPE_META = {
    fill_in_blank:   { icon: '✏️', label: 'Заполни пропуски' },
    multiple_choice: { icon: '☑️', label: 'Выбор ответа' },
    drag_and_drop:   { icon: '🔀', label: 'Расставь по порядку' },
    text_input:      { icon: '✍️', label: 'Свободный ответ' },
};

const DIFF_STYLE = {
    Easy:   { bg: 'rgba(0,184,148,0.1)',   color: '#00b894', label: 'Лёгкий'  },
    Medium: { bg: 'rgba(225,112,85,0.12)', color: '#e17055', label: 'Средний' },
    Hard:   { bg: 'rgba(214,48,49,0.1)',   color: '#d63031', label: 'Сложный' },
};

const parseList = (val) => {
    if (!val) return [];
    if (Array.isArray(val)) return val.map(String).filter(Boolean);
    if (typeof val === 'string') {
        const trimmed = val.trim();
        if (trimmed.startsWith('[')) {
            try {
                const parsed = JSON.parse(trimmed);
                if (Array.isArray(parsed)) return parsed.map(String).filter(Boolean);
            } catch (_) {}
        }
        return trimmed.split(',').map(s => s.trim()).filter(Boolean);
    }
    return [];
};

/* ─────────────────────────────────────────
   Inline code viewer for LessonPage (read-only, no edit)
───────────────────────────────────────────── */
const LANG_MAP_LP = {
    html: 'html', htm: 'html', css: 'css',
    js: 'javascript', jsx: 'jsx', ts: 'typescript', tsx: 'tsx',
    py: 'python', java: 'java', cpp: 'cpp', c: 'c',
    rs: 'rust', go: 'go', sql: 'sql', sh: 'bash', bash: 'bash',
    json: 'json', md: 'markdown', xml: 'xml', yaml: 'yaml', yml: 'yaml',
    php: 'php', rb: 'ruby', swift: 'swift', kt: 'kotlin',
};
const LANG_COLORS_LP = {
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
    default:    { bg: 'rgba(108,92,231,0.10)',   color: '#6c5ce7',  icon: '📄' },
};
const getExtLP = (filename) => (filename || '').split('.').pop().toLowerCase();
const getLangLP = (filename) => LANG_MAP_LP[getExtLP(filename)] || getExtLP(filename);
const getLangMetaLP = (lang) => LANG_COLORS_LP[lang] || LANG_COLORS_LP.default;

const PREVIEW_EXTS_LP = ['html', 'htm'];

const ProjectFileViewer = ({ file, index }) => {
    const [copied, setCopied] = useState(false);
    const [expanded, setExpanded] = useState(index === 0);
    const [view, setView] = useState('code'); // 'code' | 'preview'

    const filename = file.filename || file.name || `file_${index + 1}`;
    const lang = getLangLP(filename);
    const meta = getLangMetaLP(lang);
    const code = file.code || file.code_content || file.content || '';
    const lines = code.split('\n');
    const canPreview = PREVIEW_EXTS_LP.includes(getExtLP(filename));

    const copy = () => {
        navigator.clipboard.writeText(code).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    };

    return (
        <div className="lp-project-file-viewer">
            <div className="lp-project-file-head">
                <div className="lp-project-file-head-left">
                    <span className="lp-project-file-lang-icon" style={{ background: meta.bg, color: meta.color }}>
                        {meta.icon}
                    </span>
                    <span className="lp-project-file-name">{filename}</span>
                    {file.label && <span className="lp-project-file-label">{file.label}</span>}
                    <span className="lp-project-file-meta">{lines.length} строк</span>
                </div>
                <div className="lp-project-file-head-right">
                    {/* Code / Preview toggle — only for HTML files */}
                    {canPreview && expanded && (
                        <div className="lp-project-file-view-toggle">
                            <button
                                className={`lp-project-file-view-btn ${view === 'code' ? 'active' : ''}`}
                                onClick={() => setView('code')}
                            >
                                &lt;/&gt; Код
                            </button>
                            <button
                                className={`lp-project-file-view-btn ${view === 'preview' ? 'active' : ''}`}
                                onClick={() => setView('preview')}
                            >
                                🖥️ Превью
                            </button>
                        </div>
                    )}
                    <button className="lp-project-file-copy" onClick={copy} title="Копировать">
                        {copied ? '✅' : '📋'}
                    </button>
                    <button className="lp-project-file-toggle" onClick={() => setExpanded(e => !e)}>
                        {expanded ? '▲' : '▼'}
                    </button>
                </div>
            </div>

            {expanded && (
                <>
                    {view === 'code' ? (
                        <div className="lp-project-file-body">
                            <div className="lp-project-file-linenums" aria-hidden>
                                {lines.map((_, i) => (
                                    <div key={i} className="lp-project-file-linenum">{i + 1}</div>
                                ))}
                            </div>
                            <pre className="lp-project-file-pre">{code || '// Файл пустой'}</pre>
                        </div>
                    ) : (
                        /* srcdoc — no cross-origin errors */
                        <div className="lp-project-file-preview-wrap">
                            <iframe
                                className="lp-project-file-iframe"
                                sandbox="allow-scripts"
                                title={`preview-${filename}`}
                                srcDoc={code}
                            />
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

/* ─────────────────────────────────────────
   Exercise Card
───────────────────────────────────────── */
const ExerciseCard = ({ ex, index }) => {
    const typeMeta  = EX_TYPE_META[ex.exercise_type] || { icon: '🎯', label: ex.exercise_type };
    const diffStyle = DIFF_STYLE[ex.difficulty_level] || DIFF_STYLE.Easy;
    const options   = parseList(ex.options);
    const dragItems = parseList(ex.drag_items);

    return (
        <div className="lp-ex-card">
            <div className="lp-ex-card-head">
                <div className="lp-ex-num">{index + 1}</div>
                <span className="lp-ex-type-badge">{typeMeta.icon} {typeMeta.label}</span>
                <div className="lp-ex-head-right">
                    <span className="lp-ex-diff" style={{ background: diffStyle.bg, color: diffStyle.color }}>
                        {diffStyle.label}
                    </span>
                    {ex.points > 0 && <span className="lp-ex-pts">🏆 {ex.points} pts</span>}
                </div>
            </div>
            <div className="lp-ex-card-body">
                {ex.title && <div className="lp-ex-title">{ex.title}</div>}

                {ex.exercise_type === 'text_input' && (
                    <>
                        {ex.description && <div className="lp-ex-question">{ex.description}</div>}
                        <textarea className="lp-ex-textarea" disabled placeholder="Студент напишет ответ здесь..." />
                        <div className="lp-ex-ai-badge">🤖 AI проверяет ответ по смыслу</div>
                    </>
                )}

                {ex.exercise_type === 'multiple_choice' && (
                    <>
                        {ex.description && <div className="lp-ex-question">{ex.description}</div>}
                        <div className="lp-ex-options">
                            {options.length > 0 ? options.map((opt, i) => (
                                <div key={i} className="lp-ex-option">
                                    <span className="lp-ex-option-letter">{String.fromCharCode(65 + i)}</span>
                                    <span>{opt}</span>
                                </div>
                            )) : <div className="lp-ex-no-content">Варианты не добавлены</div>}
                        </div>
                        {ex.is_multiple_select && (
                            <div className="lp-ex-note">⚡ Можно выбрать несколько ответов</div>
                        )}
                    </>
                )}

                {ex.exercise_type === 'drag_and_drop' && (
                    <>
                        {ex.description && <div className="lp-ex-question">{ex.description}</div>}
                        <div className="lp-ex-drag-items">
                            {dragItems.length > 0 ? dragItems.map((item, i) => (
                                <span key={i} className="lp-ex-drag-chip">⠿ {item}</span>
                            )) : <div className="lp-ex-no-content">Элементы не добавлены</div>}
                        </div>
                        <div className="lp-ex-note">🖱️ Студент перетащит элементы в правильный порядок</div>
                    </>
                )}

                {ex.exercise_type === 'fill_in_blank' && (
                    <>
                        {ex.description ? (
                            <div className="lp-ex-blank-text">
                                {ex.description.split('___').map((part, i, arr) => (
                                    <span key={i}>
                                        {part}
                                        {i < arr.length - 1 && <span className="lp-ex-blank-slot" />}
                                    </span>
                                ))}
                            </div>
                        ) : <div className="lp-ex-no-content">Текст не добавлен</div>}
                    </>
                )}

                {ex.hint && (
                    <div className="lp-ex-hint">
                        💡 <strong>Подсказка:</strong> {ex.hint}
                    </div>
                )}
            </div>
        </div>
    );
};

/* ─────────────────────────────────────────
   Exercise Block
───────────────────────────────────────── */
const ExerciseBlock = ({ section }) => {
    const exercises   = section.exercises || [];
    const totalPoints = exercises.reduce((sum, e) => sum + (Number(e.points) || 0), 0);
    const sorted      = exercises.slice().sort((a, b) => (a.order || 0) - (b.order || 0));

    return (
        <div className="lp-exercise-block">
            <div className="lp-exercise-bar">
                <span className="lp-exercise-bar-count">🎯 {exercises.length} заданий</span>
                {totalPoints > 0 && <span className="lp-exercise-bar-pts">🏆 {totalPoints} pts</span>}
            </div>
            {exercises.length === 0 ? (
                <div className="lp-exercise-empty">
                    <span>📭</span>
                    <p>Задания ещё не добавлены</p>
                </div>
            ) : (
                <div className="lp-exercise-list">
                    {sorted.map((ex, i) => (
                        <ExerciseCard key={ex.id || ex._localId || i} ex={ex} index={i} />
                    ))}
                </div>
            )}
        </div>
    );
};

/* ═══════════════════════════════════════════
   Main LessonPage
═══════════════════════════════════════════ */
const LessonPage = ({ lesson, course, allLessons, onBack, onNavigate, onEdit, onDelete }) => {
    const [copiedId, setCopiedId] = useState(null);

    useEffect(() => {
        if (!lesson?.id) return;
        let cancelled = false;
        let running = false;
        let scheduled = null;
        const runMermaid = () => {
            scheduled = null;
            if (cancelled || running) return;
            const nodes = document.querySelectorAll(
                'pre.mermaid:not([data-processed="true"])',
            );
            if (nodes.length === 0) return;
            running = true;
            mermaid
                .run({ nodes: Array.from(nodes) })
                .catch(() => {})
                .finally(() => {
                    running = false;
                });
        };
        const schedule = () => {
            if (scheduled || cancelled) return;
            scheduled = setTimeout(runMermaid, 50);
        };
        schedule();
        const target = document.querySelector('.lp-blocks') || document.body;
        const observer = new MutationObserver(schedule);
        observer.observe(target, { childList: true, subtree: true });
        return () => {
            cancelled = true;
            observer.disconnect();
            if (scheduled) clearTimeout(scheduled);
        };
    }, [lesson?.id]);

    const currentIndex = allLessons.findIndex(l => l.id === lesson.id);
    const prevLesson   = currentIndex > 0 ? allLessons[currentIndex - 1] : null;
    const nextLesson   = currentIndex < allLessons.length - 1 ? allLessons[currentIndex + 1] : null;

    const copyCode = (id, code) => {
        navigator.clipboard.writeText(code).then(() => {
            setCopiedId(id);
            setTimeout(() => setCopiedId(null), 2000);
        });
    };

    const meta = (type) => SECTION_TYPES.find(t => t.type === type);

    return (
        <div className="lp-container">
            {/* Top bar */}
            <div className="lp-top-bar">
                <div className="lp-breadcrumb">
                    <button className="lp-breadcrumb-btn" onClick={() => onBack('courses')}>Курсы</button>
                    <span className="lp-breadcrumb-sep">›</span>
                    <button className="lp-breadcrumb-btn" onClick={() => onBack('course')}>{course.title}</button>
                    <span className="lp-breadcrumb-sep">›</span>
                    <span className="lp-breadcrumb-current">{lesson.title}</span>
                </div>
                <div className="lp-top-actions">
                    <div className="lp-lesson-action-btns">
                        <button className="lp-edit-btn" onClick={onEdit}>✏️ Редактировать</button>
                        <button className="lp-delete-btn" onClick={onDelete}>🗑️ Удалить</button>
                    </div>
                    <div className="lp-nav-btns">
                        <button className="lp-nav-btn" onClick={() => prevLesson && onNavigate(prevLesson)} disabled={!prevLesson}>
                            ← Предыдущий
                        </button>
                        <button className="lp-nav-btn" onClick={() => nextLesson && onNavigate(nextLesson)} disabled={!nextLesson}>
                            Следующий →
                        </button>
                    </div>
                </div>
            </div>

            {/* Lesson header */}
            <div className="lp-lesson-header">
                {lesson.chapter && <span className="lp-chapter-badge">{lesson.chapter}</span>}
                <h1>{lesson.title}</h1>
            </div>

            {/* Content */}
            {!lesson.sections || lesson.sections.length === 0 ? (
                <div className="lp-empty-blocks">
                    <div className="lp-empty-icon">📄</div>
                    <p>Контент для этого урока ещё не добавлен</p>
                </div>
            ) : (
                <div className="lp-blocks">
                    {lesson.sections.map((section) => {
                        const blockMeta = meta(section.type);
                        const ytId = section.type === 'video' ? getYTId(section.videoUrl || '') : null;

                        return (
                            <div key={section.id} className="lp-block">
                                <div className="lp-block-header">
                                    <span className="lp-block-icon">{blockMeta?.icon}</span>
                                    <span className="lp-block-label">{blockMeta?.label}</span>
                                    {section.label && <span className="lp-block-title">{section.label}</span>}
                                </div>

                                <div className="lp-block-body">

                                    {/* TEXT */}
                                    {section.type === 'text' && (
                                        <div className="lp-text-content"
                                            dangerouslySetInnerHTML={{ __html: sanitizeHtml(section.html) || '<p style="color:rgba(26,26,46,0.35)">Текст не добавлен</p>' }} />
                                    )}

                                    {/* CODE */}
                                    {section.type === 'code' && (
                                        <>
                                            <div className="lp-code-header">
                                                <span className="lp-code-lang-badge">{section.lang || 'code'}</span>
                                                <button className="lp-code-copy-btn" onClick={() => copyCode(section.id, section.code || '')}>
                                                    {copiedId === section.id ? '✅ Скопировано' : '📋 Копировать'}
                                                </button>
                                            </div>
                                            <pre className="lp-code-block">{section.code || '// Код не добавлен'}</pre>
                                        </>
                                    )}

                                    {/* VIDEO */}
                                    {section.type === 'video' && (
                                        <>
                                            <div className="lp-video-wrapper">
                                                {ytId
                                                    ? <iframe src={`https://www.youtube.com/embed/${ytId}`} allowFullScreen title={section.label || 'Video'} />
                                                    : <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'rgba(255,255,255,0.3)', fontSize: 14 }}>Видео не добавлено</div>
                                                }
                                            </div>
                                            {section.videoUrl && (
                                                <a href={section.videoUrl} target="_blank" rel="noopener noreferrer" className="lp-video-link">
                                                    🎥 Открыть на YouTube
                                                </a>
                                            )}
                                        </>
                                    )}

                                    {/* IMAGE */}
                                    {section.type === 'image' && (
                                        <div className="lp-image-block">
                                            {section.imgUrl
                                                ? <img src={section.imgUrl} alt={section.label || 'image'} />
                                                : <div style={{ padding: '32px', color: 'rgba(26,26,46,0.3)', fontSize: 13, textAlign: 'center' }}>Изображение не добавлено</div>
                                            }
                                        </div>
                                    )}

                                    {/* FILE */}
                                    {section.type === 'file' && (
                                        section.fileName ? (
                                            <div className="lp-file-card">
                                                <span className="lp-file-icon">📦</span>
                                                <div className="lp-file-info">
                                                    <div className="lp-file-name">{section.fileName}</div>
                                                    {section.fileSize && <div className="lp-file-size">{section.fileSize}</div>}
                                                </div>
                                                <button className="lp-file-download-btn">⬇ Скачать</button>
                                            </div>
                                        ) : (
                                            <div style={{ color: 'rgba(26,26,46,0.3)', fontSize: 13 }}>Файл не добавлен</div>
                                        )
                                    )}

                                    {/* EXERCISE */}
                                    {section.type === 'exercise' && <ExerciseBlock section={section} />}

                                    {/* ══════════════════════════════════════════
                                        PROJECT (Loyiha) — показываем всё содержимое
                                    ══════════════════════════════════════════ */}
                                    {section.type === 'project' && (
                                        <div className="lp-project-block">
                                            <div className="lp-project-top">
                                                <span className="lp-project-icon">🚀</span>
                                                <div>
                                                    <div className="lp-project-title">{section.label || 'Loyiha'}</div>
                                                    {section.description && (
                                                        <div className="lp-project-desc">{section.description}</div>
                                                    )}
                                                </div>
                                            </div>

                                            {section.requirements && (
                                                <div className="lp-project-section">
                                                    <div className="lp-project-label">📋 Требования:</div>
                                                    <div className="lp-project-text">{section.requirements}</div>
                                                </div>
                                            )}

                                            {section.techStack && (
                                                <div className="lp-project-section">
                                                    <div className="lp-project-label">🛠 Стек технологий:</div>
                                                    <div className="lp-project-tags">
                                                        {section.techStack.split(',').map((t, i) => (
                                                            <span key={i} className="lp-project-tag">{t.trim()}</span>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            {section.deadline && (
                                                <div className="lp-project-deadline">
                                                    ⏰ Дедлайн: <strong>{section.deadline} дней</strong>
                                                </div>
                                            )}

                                            {/* ── Файлы кода проекта ── */}
                                            {Array.isArray(section.projectFiles) && section.projectFiles.length > 0 && (
                                                <div className="lp-project-files-section">
                                                    <div className="lp-project-files-header">
                                                        <span className="lp-project-files-title">
                                                            🗂️ Файлы кода
                                                        </span>
                                                        <span className="lp-project-files-count">
                                                            {section.projectFiles.length} файл{section.projectFiles.length === 1 ? '' : section.projectFiles.length < 5 ? 'а' : 'ов'}
                                                        </span>
                                                    </div>
                                                    <div className="lp-project-files-list">
                                                        {section.projectFiles.map((file, idx) => (
                                                            <ProjectFileViewer
                                                                key={file.id || file._localId || idx}
                                                                file={file}
                                                                index={idx}
                                                            />
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {/* ── MASHQ ── */}
                                    {section.type === 'mashq' && (
                                        <div className="lp-mashq-block">
                                            <span className="lp-mashq-type-badge">
                                                {section.mashqType === 'word_sort' ? '🔀 Сортировка слов' : '✍️ Свободный ответ'}
                                            </span>

                                            {section.question && (
                                                <div className="lp-mashq-question">{section.question}</div>
                                            )}

                                            {section.mashqType === 'word_sort' ? (
                                                <div className="lp-mashq-words">
                                                    {(Array.isArray(section.words) ? section.words : []).map((word, i) => (
                                                        <span key={i} className="lp-mashq-word drag_drop">{word}</span>
                                                    ))}
                                                </div>
                                            ) : (
                                                <textarea
                                                    className="lp-mashq-textarea"
                                                    disabled
                                                    placeholder="Студент напишет ответ здесь..."
                                                />
                                            )}

                                            {section.answer && (
                                                <div className="lp-mashq-answer-preview">
                                                    ✅ Правильный ответ: <strong>{section.answer}</strong>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default LessonPage;