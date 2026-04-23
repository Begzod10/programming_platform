import React, { useState } from 'react';
import './LessonPage.css';
import '../Exercise additions/Lessonpage exercise additions.css'
import { SECTION_TYPES, getYTId } from '../../../../constants/courseUtils';

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

/**
 * Парсим поле которое может быть:
 *   - JSON-строкой:  '["a","b"]'   → ['a','b']
 *   - CSV-строкой:   'a,b,c'       → ['a','b','c']
 *   - уже массивом:  ['a','b']     → ['a','b']
 *   - null/undefined               → []
 */
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
   Exercise Card
───────────────────────────────────────── */
const ExerciseCard = ({ ex, index }) => {
    const typeMeta  = EX_TYPE_META[ex.exercise_type] || { icon: '🎯', label: ex.exercise_type };
    const diffStyle = DIFF_STYLE[ex.difficulty_level] || DIFF_STYLE.Easy;

    const options   = parseList(ex.options);
    const dragItems = parseList(ex.drag_items);

    return (
        <div className="lp-ex-card">

            {/* Header */}
            <div className="lp-ex-card-head">
                <div className="lp-ex-num">{index + 1}</div>
                <span className="lp-ex-type-badge">{typeMeta.icon} {typeMeta.label}</span>
                <div className="lp-ex-head-right">
                    <span className="lp-ex-diff"
                        style={{ background: diffStyle.bg, color: diffStyle.color }}>
                        {diffStyle.label}
                    </span>
                    {ex.points > 0 && (
                        <span className="lp-ex-pts">🏆 {ex.points} pts</span>
                    )}
                </div>
            </div>

            {/* Body */}
            <div className="lp-ex-card-body">

                {ex.title && <div className="lp-ex-title">{ex.title}</div>}

                {/* text_input */}
                {ex.exercise_type === 'text_input' && (
                    <>
                        {ex.description && <div className="lp-ex-question">{ex.description}</div>}
                        <textarea className="lp-ex-textarea" disabled placeholder="Студент напишет ответ здесь..." />
                        <div className="lp-ex-ai-badge">🤖 AI проверяет ответ по смыслу</div>
                    </>
                )}

                {/* multiple_choice */}
                {ex.exercise_type === 'multiple_choice' && (
                    <>
                        {ex.description && <div className="lp-ex-question">{ex.description}</div>}
                        <div className="lp-ex-options">
                            {options.length > 0 ? options.map((opt, i) => (
                                <div key={i} className="lp-ex-option">
                                    <span className="lp-ex-option-letter">
                                        {String.fromCharCode(65 + i)}
                                    </span>
                                    <span>{opt}</span>
                                </div>
                            )) : (
                                <div className="lp-ex-no-content">Варианты не добавлены</div>
                            )}
                        </div>
                        {ex.is_multiple_select && (
                            <div className="lp-ex-note">⚡ Можно выбрать несколько ответов</div>
                        )}
                    </>
                )}

                {/* drag_and_drop */}
                {ex.exercise_type === 'drag_and_drop' && (
                    <>
                        {ex.description && <div className="lp-ex-question">{ex.description}</div>}
                        <div className="lp-ex-drag-items">
                            {dragItems.length > 0 ? dragItems.map((item, i) => (
                                <span key={i} className="lp-ex-drag-chip">⠿ {item}</span>
                            )) : (
                                <div className="lp-ex-no-content">Элементы не добавлены</div>
                            )}
                        </div>
                        <div className="lp-ex-note">🖱️ Студент перетащит элементы в правильный порядок</div>
                    </>
                )}

                {/* fill_in_blank */}
                {ex.exercise_type === 'fill_in_blank' && (
                    <>
                        {ex.description ? (
                            <div className="lp-ex-blank-text">
                                {ex.description.split('___').map((part, i, arr) => (
                                    <span key={i}>
                                        {part}
                                        {i < arr.length - 1 && (
                                            <span className="lp-ex-blank-slot" />
                                        )}
                                    </span>
                                ))}
                            </div>
                        ) : (
                            <div className="lp-ex-no-content">Текст не добавлен</div>
                        )}
                    </>
                )}

                {/* Hint */}
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
            {/* Stats bar */}
            <div className="lp-exercise-bar">
                <span className="lp-exercise-bar-count">🎯 {exercises.length} заданий</span>
                {totalPoints > 0 && (
                    <span className="lp-exercise-bar-pts">🏆 {totalPoints} pts</span>
                )}
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
                                            dangerouslySetInnerHTML={{ __html: section.html || '<p style="color:rgba(26,26,46,0.35)">Текст не добавлен</p>' }} />
                                    )}

                                    {/* CODE */}
                                    {section.type === 'code' && (<>
                                        <div className="lp-code-header">
                                            <span className="lp-code-lang-badge">{section.lang || 'code'}</span>
                                            <button className="lp-code-copy-btn" onClick={() => copyCode(section.id, section.code || '')}>
                                                {copiedId === section.id ? '✅ Скопировано' : '📋 Копировать'}
                                            </button>
                                        </div>
                                        <pre className="lp-code-block">{section.code || '// Код не добавлен'}</pre>
                                    </>)}

                                    {/* VIDEO */}
                                    {section.type === 'video' && (<>
                                        <div className="lp-video-wrapper">
                                            {ytId
                                                ? <iframe src={`https://www.youtube.com/embed/${ytId}`} allowFullScreen title={section.label || 'Video'} />
                                                : <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'rgba(255,255,255,0.3)', fontSize: 14 }}>Видео не добавлено</div>}
                                        </div>
                                        {section.videoUrl && (
                                            <a href={section.videoUrl} target="_blank" rel="noopener noreferrer" className="lp-video-link">
                                                🎥 Открыть на YouTube
                                            </a>
                                        )}
                                    </>)}

                                    {/* IMAGE */}
                                    {section.type === 'image' && (
                                        <div className="lp-image-block">
                                            {section.imgUrl
                                                ? <img src={section.imgUrl} alt={section.label || 'image'} />
                                                : <div style={{ padding: '32px', color: 'rgba(26,26,46,0.3)', fontSize: 13, textAlign: 'center' }}>Изображение не добавлено</div>}
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
                                    {section.type === 'exercise' && (
                                        <ExerciseBlock section={section} />
                                    )}

                                    {/* PROJECT */}
                                    {section.type === 'project' && (
                                        <div className="lp-project-block">
                                            <div className="lp-project-top">
                                                <span className="lp-project-icon">🚀</span>
                                                <div>
                                                    <div className="lp-project-title">{section.label || 'Loyiha'}</div>
                                                    {section.description && <div className="lp-project-desc">{section.description}</div>}
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