import React, {useState, useRef, useCallback} from 'react';
import ReactDOM from 'react-dom';
import './StudentLessonPage.css';
import {SECTION_TYPES, getYTId} from '../../../../constants/courseUtils';
import {API_URL, useHttp, headers} from '../../../../api/search/base';
import DictSelectionPopup from '../LessonPage/Dictselectionpopup';

/* ─────────────────────────────────────────
   Умный парсер → всегда возвращает чистый массив строк
───────────────────────────────────────── */
const parseListField = (val) => {
    if (!val) return [];
    if (Array.isArray(val)) return val.map(s => String(s).trim()).filter(Boolean);
    if (typeof val === "string") {
        const trimmed = val.trim();
        if (trimmed.startsWith("[")) {
            try {
                const parsed = JSON.parse(trimmed);
                if (Array.isArray(parsed)) return parsed.map(s => String(s).trim()).filter(Boolean);
            } catch {}
        }
        return trimmed.split(",").map(s => s.trim()).filter(Boolean);
    }
    return [];
};

/* ─────────────────────────────────────────
   Upload Method Selector
───────────────────────────────────────── */
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

/* ─────────────────────────────────────────
   ZIP Drop Zone
───────────────────────────────────────── */
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
   SINGLE EXERCISE CARD
═══════════════════════════════════════════════════════════ */
const ExerciseCard = ({ex, courseId, lessonId, index}) => {
    const {request} = useHttp();

    const [textAnswer, setTextAnswer] = useState('');
    const [selected, setSelected] = useState([]);
    const [fillAnswers, setFillAnswers] = useState([]);
    const cleanOptions = parseListField(ex.options);
    const cleanDragItems = parseListField(ex.drag_items);

    const [dragAvailable, setDragAvailable] = useState(
        () => [...cleanDragItems].sort(() => Math.random() - 0.5)
    );
    const [dragDropped, setDragDropped] = useState([]);
    const [result, setResult] = useState(null);
    const [aiFeedback, setAiFeedback] = useState('');
    const [score, setScore] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const [showHint, setShowHint] = useState(false);

    const isDone = result === 'correct' || result === 'submitted';
    const isWrong = result === 'wrong';
    const exType = ex.exercise_type;

    const buildAnswer = () => {
        if (exType === 'fill_in_blank') return fillAnswers.join(',');
        if (exType === 'drag_and_drop') return JSON.stringify(dragDropped.map(s => s.trim()));
        if (exType === 'multiple_choice') return selected.join(',');
        return textAnswer.trim();
    };

    const handleSubmit = async () => {
        const answer = buildAnswer();
        if (!answer) return;
        setSubmitting(true);
        setAiFeedback('');
        setScore(null);
        try {
            const res = await request(
                `${API_URL}v1/courses/${courseId}/lessons/${lessonId}/exercises/${ex.id}/submit`,
                'POST',
                JSON.stringify({student_answer: answer}),
                headers()
            );
            if (res?.is_correct === true) setResult('correct');
            else if (res?.is_correct === false) setResult('wrong');
            else setResult('submitted');
            if (res?.ai_feedback) setAiFeedback(res.ai_feedback);
            if (res?.score != null) setScore(res.score);
        } catch {
            setResult('wrong');
        } finally {
            setSubmitting(false);
        }
    };

    const handleRetry = () => {
        setResult(null);
        setAiFeedback('');
        setScore(null);
        setSelected([]);
        setTextAnswer('');
        setFillAnswers([]);
        setDragDropped([]);
        setDragAvailable([...cleanDragItems].sort(() => Math.random() - 0.5));
    };

    const DIFF_COLOR = {Easy: '#00b894', Medium: '#e17055', Hard: '#d63031'};
    const diffColor = DIFF_COLOR[ex.difficulty_level] || '#6c5ce7';

    const stateClass = result === 'correct' ? 'state-correct'
        : result === 'wrong' ? 'state-wrong'
            : result === 'submitted' ? 'state-submitted' : '';

    return (
        <div className={`slp-ex-card ${stateClass}`} style={{animationDelay: `${index * 0.07}s`}}>
            <div className="slp-ex-card-head">
                <div className="slp-ex-card-meta">
                    <span className="slp-ex-num">#{index + 1}</span>
                    {ex.difficulty_level && (
                        <span className="slp-ex-diff-badge"
                              style={{color: diffColor, borderColor: diffColor + '55', background: diffColor + '15'}}>
                            {ex.difficulty_level}
                        </span>
                    )}
                    {ex.points > 0 && <span className="slp-ex-pts-badge">⭐ {ex.points} pts</span>}
                    {score != null && <span className="slp-ex-score-badge">🏆 +{score} pts</span>}
                    <span className="slp-ex-type-label">
                        {{
                            fill_in_blank: '✏️ Заполни пропуск',
                            multiple_choice: '🔘 Выбор ответа',
                            drag_and_drop: '↕️ Расставь порядок',
                            text_input: '📝 Свободный ответ',
                        }[exType] || '❓ Задание'}
                    </span>
                </div>
                {ex.title && <div className="slp-ex-card-title">{ex.title}</div>}
            </div>

            <div className="slp-ex-card-body">
                {exType === 'fill_in_blank' && (
                    <div className="slp-ex-fill-wrap">
                        <div className="slp-ex-fill-text">
                            {(ex.description || '').split('___').map((part, i, arr) => (
                                <span key={i}>
                                    {part}
                                    {i < arr.length - 1 && (
                                        <input
                                            className={`slp-ex-fill-input ${isDone ? (result === 'correct' ? 'correct' : 'wrong') : ''}`}
                                            placeholder={`${i + 1}`}
                                            disabled={isDone}
                                            value={fillAnswers[i] || ''}
                                            onChange={e => {
                                                const copy = [...fillAnswers];
                                                copy[i] = e.target.value;
                                                setFillAnswers(copy);
                                                setResult(null);
                                            }}
                                        />
                                    )}
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {exType === 'multiple_choice' && (
                    <>
                        {ex.description && <div className="slp-ex-question">{ex.description}</div>}
                        <div className="slp-ex-options">
                            {cleanOptions.map((opt, i) => {
                                const letter = String.fromCharCode(65 + i);
                                const isSelected = selected.includes(letter);
                                return (
                                    <button
                                        key={i}
                                        className={`slp-ex-option-btn ${isSelected ? 'selected' : ''}`}
                                        disabled={isDone}
                                        onClick={() => {
                                            if (ex.is_multiple_select) {
                                                setSelected(s => isSelected ? s.filter(x => x !== letter) : [...s, letter]);
                                            } else {
                                                setSelected([letter]);
                                            }
                                            setResult(null);
                                        }}
                                    >
                                        <span className="slp-ex-opt-letter">{letter}</span>
                                        <span className="slp-ex-opt-text">{opt}</span>
                                        {isSelected && <span className="slp-ex-opt-check">✓</span>}
                                    </button>
                                );
                            })}
                            {ex.is_multiple_select && (
                                <div className="slp-ex-multi-hint">⚡ Можно выбрать несколько ответов</div>
                            )}
                        </div>
                    </>
                )}

                {exType === 'drag_and_drop' && (
                    <>
                        {ex.description && <div className="slp-ex-question">{ex.description}</div>}
                        <div className="slp-ex-drag-wrap">
                            <div className="slp-ex-dropzone-label">Правильный порядок:</div>
                            <div
                                className="slp-ex-dropzone"
                                onDragOver={e => e.preventDefault()}
                                onDrop={e => {
                                    if (isDone) return;
                                    const word = e.dataTransfer.getData('word');
                                    setDragDropped(d => [...d, word]);
                                    setDragAvailable(a => a.filter(w => w !== word));
                                    setResult(null);
                                }}
                            >
                                {dragDropped.length === 0
                                    ? <span className="slp-drop-hint">Перетащите элементы сюда по порядку</span>
                                    : dragDropped.map((w, i) => (
                                        <span key={i} className="slp-ex-dropped-chip"
                                              onClick={() => {
                                                  if (isDone) return;
                                                  setDragDropped(d => d.filter((_, j) => j !== i));
                                                  setDragAvailable(a => [...a, w]);
                                                  setResult(null);
                                              }}>
                                            <span className="slp-dropped-num">{i + 1}</span>
                                            {w}
                                            <span className="slp-dropped-del">✕</span>
                                        </span>
                                    ))
                                }
                            </div>
                            <div className="slp-ex-drag-chips-label">Доступные элементы:</div>
                            <div className="slp-ex-drag-words">
                                {dragAvailable.map((w, i) => (
                                    <span
                                        key={i}
                                        className="slp-ex-drag-chip"
                                        draggable={!isDone}
                                        onDragStart={e => e.dataTransfer.setData('word', w)}
                                    >
                                        {w}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </>
                )}

                {exType === 'text_input' && (
                    <>
                        {ex.description && <div className="slp-ex-question">{ex.description}</div>}
                        <textarea
                            className="slp-ex-textarea"
                            placeholder="Напишите ваш ответ..."
                            disabled={isDone}
                            value={textAnswer}
                            rows={4}
                            onChange={e => { setTextAnswer(e.target.value); setResult(null); }}
                        />
                        <div className="slp-ex-ai-note">
                            <span className="slp-ai-dot"/>
                            Ответ будет проверен AI
                        </div>
                    </>
                )}

                {ex.hint && (
                    <div className="slp-ex-hint-wrap">
                        <button className="slp-ex-hint-btn" onClick={() => setShowHint(h => !h)}>
                            💡 {showHint ? 'Скрыть подсказку' : 'Показать подсказку'}
                        </button>
                        {showHint && <div className="slp-ex-hint-text">{ex.hint}</div>}
                    </div>
                )}

                {result && (
                    <div className={`slp-ex-result-banner ${result}`}>
                        <span className="slp-res-icon">
                            {result === 'correct' ? '🎉' : result === 'wrong' ? '❌' : '✅'}
                        </span>
                        <div>
                            {result === 'correct' && <><strong>Правильно!</strong> Отличная работа!</>}
                            {result === 'wrong' && <><strong>Неправильно.</strong> Попробуйте ещё раз.</>}
                            {result === 'submitted' && <><strong>Ответ отправлен!</strong> AI проверит его.</>}
                        </div>
                    </div>
                )}

                {aiFeedback && (
                    <div className="slp-ex-ai-feedback">
                        <div className="slp-ex-ai-feedback-label">
                            <span className="slp-ai-pulse-dot"/>
                            AI Feedback
                        </div>
                        <div className="slp-ex-ai-feedback-text">{aiFeedback}</div>
                    </div>
                )}

                <div className="slp-ex-actions">
                    {!isDone && (
                        <button
                            className="slp-ex-submit-btn"
                            onClick={handleSubmit}
                            disabled={submitting || !buildAnswer()}
                        >
                            {submitting
                                ? <><span className="slp-btn-spin"/>Проверяем...</>
                                : '✅ Проверить ответ'
                            }
                        </button>
                    )}
                    {isWrong && (
                        <button className="slp-ex-retry-btn" onClick={handleRetry}>
                            🔄 Попробовать снова
                        </button>
                    )}
                    {isDone && result === 'correct' && (
                        <div className="slp-ex-done-label">✓ Выполнено</div>
                    )}
                </div>
            </div>
        </div>
    );
};

/* ═══════════════════════════════════════════════════════════
   EXERCISE SECTION BLOCK
═══════════════════════════════════════════════════════════ */
const ExerciseSection = ({section, courseId, lessonId}) => {
    const exercises = section.exercises || [];
    if (exercises.length === 0) return null;
    const totalPts = exercises.reduce((s, e) => s + (e.points || 0), 0);
    return (
        <div className="slp-ex-section">
            <div className="slp-ex-section-bar">
                <div className="slp-ex-section-left">
                    <span className="slp-ex-section-icon">🎯</span>
                    <span className="slp-ex-section-count">{exercises.length} заданий</span>
                </div>
                {totalPts > 0 && (
                    <span className="slp-ex-section-pts">🏆 {totalPts} pts всего</span>
                )}
            </div>
            <div className="slp-ex-section-list">
                {exercises
                    .slice()
                    .sort((a, b) => (a.order || 0) - (b.order || 0))
                    .map((ex, i) => (
                        <ExerciseCard key={ex.id || i} ex={ex} courseId={courseId} lessonId={lessonId} index={i}/>
                    ))
                }
            </div>
        </div>
    );
};

const SECTION_META = {
    text:     {icon: '📝', label: 'Текст',        color: '#6c5ce7'},
    code:     {icon: '💻', label: 'Код',           color: '#0f1117'},
    video:    {icon: '🎬', label: 'Видео',         color: '#e84393'},
    image:    {icon: '🖼', label: 'Изображение',   color: '#00b894'},
    file:     {icon: '📦', label: 'Файл',          color: '#fdcb6e'},
    exercise: {icon: '🎯', label: 'Задания',       color: '#a29bfe'},
    project:  {icon: '🚀', label: 'Проект',        color: '#00cec9'},
};

/* ═══════════════════════════════════════════════════════════
   MAIN — StudentLessonPage
═══════════════════════════════════════════════════════════ */
const StudentLessonPage = ({lesson, course, allLessons, onBack, onNavigate, onComplete}) => {
    const {request} = useHttp();

    const [copiedId, setCopiedId] = useState(null);
    const [justCompleted, setJustCompleted] = useState(false);
    const [projectModal, setProjectModal] = useState(false);
    const [exitModal, setExitModal] = useState(false);
    const [projectForm, setProjectForm] = useState({github_url: '', live_demo_url: '', description: ''});
    const [projectDone, setProjectDone] = useState(
        () => localStorage.getItem(`project_done_lesson_${lesson.id}`) === 'true'
    );
    const [projectSaving, setProjectSaving] = useState(false);
    const [projectError, setProjectError] = useState('');
    const [downloadingFile, setDownloadingFile] = useState(null);
    const [activeSection, setActiveSection] = useState(null);

    // Upload method: 'github' | 'zip'
    const [uploadMethod, setUploadMethod] = useState('github');
    const [zipFile, setZipFile] = useState(null);
    const [zipUploading, setZipUploading] = useState(false);
    const [zipMsg, setZipMsg] = useState('');
    const [formErrors, setFormErrors] = useState({});

    const currentIndex = allLessons.findIndex(l => l.id === lesson.id);
    const prevLesson = currentIndex > 0 ? allLessons[currentIndex - 1] : null;
    const nextLesson = currentIndex < allLessons.length - 1 ? allLessons[currentIndex + 1] : null;
    const projectSection = lesson.sections?.find(s => s.type === 'project');
    const nextBlocked = !!projectSection && !projectDone;
    const isDone = lesson.completed || justCompleted;

    const totalSections = (lesson.sections || []).filter(s => s.type !== 'project').length;

    const copyCode = (id, code) => {
        navigator.clipboard.writeText(code).then(() => {
            setCopiedId(id);
            setTimeout(() => setCopiedId(null), 2000);
        });
    };

    const handleDownloadFile = async (lessonId, fileName) => {
        if (!fileName) return;
        setDownloadingFile(fileName);
        try {
            const token = headers()?.Authorization || headers()?.authorization || '';
            const url = `${API_URL}v1/courses/${course.id}/lessons/${lessonId}/download?file_name=${encodeURIComponent(fileName)}`;
            const response = await fetch(url, {
                method: 'GET',
                headers: {...(token ? {Authorization: token} : {}), 'Content-Type': 'application/json'},
            });
            if (!response.ok) throw new Error('Download failed');
            const blob = await response.blob();
            const blobUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = blobUrl;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(blobUrl);
        } catch {
            alert('Ошибка при скачивании файла.');
        } finally {
            setDownloadingFile(null);
        }
    };

    const uploadZip = async (projectId, file) => {
        if (!file) return;
        if (file.size === 0) throw new Error('EMPTY_FILE');
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

    const handleComplete = async () => {
        if (!lesson.completed) {
            onComplete();
            setJustCompleted(true);
            const isLastLesson = currentIndex === allLessons.length - 1;
            if (isLastLesson && course.id) {
                try {
                    await fetch(
                        `${API_URL}v1/achievements/check-and-earn-certificate?course_id=${course.id}`,
                        {method: 'POST', headers: headers()}
                    );
                } catch (e) {
                    console.warn('check-and-earn-certificate failed:', e);
                }
            }
        }
    };

    /* ── Validate project form ── */
    const validateProject = () => {
        const e = {};
        if (uploadMethod === 'github') {
            if (!projectForm.github_url.trim()) e.github_url = 'Введите GitHub ссылку';
        } else {
            if (!zipFile) {
                e.zip = 'Выберите ZIP-файл';
            } else if (zipFile.size === 0) {
                e.zip = 'ZIP-файл пустой — выберите другой файл';
            } else if (zipFile.size > 15 * 1024 * 1024) {
                e.zip = 'Файл превышает 15MB';
            }
        }
        setFormErrors(e);
        return !Object.keys(e).length;
    };

    const handleProjectSubmit = async () => {
        if (!validateProject()) return;

        const descriptionRaw = (projectForm.description.trim() || projectSection?.description || '').trim();
        // Backend strips before length check, so an appended fixed phrase
        // (>10 chars) guarantees the post-strip length passes validation.
        const description = descriptionRaw.length >= 10
            ? descriptionRaw
            : `${descriptionRaw} loyiha topshirig'i`.trim();

        setProjectSaving(true);
        setProjectError('');
        setZipMsg('');
        try {
            const techList = projectSection?.techStack
                ? projectSection.techStack.split(',').map(t => t.trim()).filter(Boolean)
                : [];
            const created = await request(
                `${API_URL}v1/project/`, 'POST',
                JSON.stringify({
                    title: projectSection?.label || lesson.title,
                    description,
                    github_url: uploadMethod === 'github' ? projectForm.github_url : '',
                    live_demo_url: projectForm.live_demo_url || '',
                    technologies_used: techList,
                    difficulty_level: 'Easy',
                    project_files: '',
                }),
                headers()
            );

            if (created?.id && uploadMethod === 'zip' && zipFile) {
                setZipUploading(true);
                try {
                    await uploadZip(created.id, zipFile);
                    setZipMsg('✅ ZIP загружен успешно');
                } catch (err) {
                    if (err.message === 'EMPTY_FILE') {
                        setZipMsg('❌ ZIP-файл пустой — загрузка отменена');
                    } else {
                        setZipMsg('⚠️ Проект создан, но ZIP не загрузился');
                    }
                } finally {
                    setZipUploading(false);
                }
            }

            if (created?.id) {
                await request(`${API_URL}v1/project/${created.id}/submit`, 'POST', null, headers());
            }

            localStorage.setItem(`project_done_lesson_${lesson.id}`, 'true');
            setProjectDone(true);
            setProjectModal(false);

            if (!lesson.completed) {
                onComplete();
                setJustCompleted(true);
                const isLastLesson = currentIndex === allLessons.length - 1;
                if (isLastLesson && course.id) {
                    try {
                        await fetch(
                            `${API_URL}v1/achievements/check-and-earn-certificate?course_id=${course.id}`,
                            {method: 'POST', headers: headers()}
                        );
                    } catch (e) {
                        console.warn('check-and-earn-certificate failed:', e);
                    }
                }
            }
        } catch {
            setProjectError('Ошибка при отправке. Проверьте данные и попробуйте ещё раз.');
        } finally {
            setProjectSaving(false);
        }
    };

    const handleMethodChange = (method) => {
        setUploadMethod(method);
        setFormErrors(e => ({...e, github_url: '', zip: ''}));
        if (method === 'github') setZipFile(null);
        if (method === 'zip') setProjectForm(f => ({...f, github_url: ''}));
    };

    const closeProjectModal = () => {
        setProjectModal(false);
        setProjectError('');
        setZipFile(null);
        setZipMsg('');
        setFormErrors({});
        setUploadMethod('github');
    };

    const isSubmitDisabled = () => {
        if (projectSaving) return true;
        if (uploadMethod === 'github') return !projectForm.github_url.trim();
        if (!zipFile) return true;
        if (zipFile.size === 0) return true;
        if (zipFile.size > 15 * 1024 * 1024) return true;
        return false;
    };

    const meta = (type) => SECTION_META[type] || SECTION_TYPES.find(t => t.type === type) || {icon: '🎯', label: 'Секция'};

    return (
        <div className="slp-container">

            {/* ──────────── TOP BAR ──────────── */}
            <div className="slp-top-bar">
                <div className="slp-breadcrumb">
                    <button className="slp-bc-btn" onClick={() => onBack('courses')}>🏠 Курсы</button>
                    <span className="slp-bc-sep">›</span>
                    <button className="slp-bc-btn" onClick={() => onBack('course')}>{course.title}</button>
                    <span className="slp-bc-sep">›</span>
                    <span className="slp-bc-current">{lesson.title}</span>
                </div>
                <div className="slp-top-actions">
                    <div className="slp-nav-btns">
                        <button className="slp-nav-btn" onClick={() => prevLesson && onNavigate(prevLesson)} disabled={!prevLesson}>
                            ← Пред.
                        </button>
                        <button className="slp-nav-btn"
                                onClick={() => !nextBlocked && nextLesson && onNavigate(nextLesson)}
                                disabled={!nextLesson || nextBlocked}
                                title={nextBlocked ? 'Сначала сдайте проект' : ''}>
                            След. →
                        </button>
                    </div>
                    <button className="slp-exit-btn" onClick={() => setExitModal(true)}>✕ Выйти</button>
                </div>
            </div>

            {/* ──────────── LESSON HEADER ──────────── */}
            <div className="slp-lesson-hero">
                <div className="slp-hero-left">
                    {lesson.chapter && <span className="slp-chapter-badge">{lesson.chapter}</span>}
                    <h1>{lesson.title}</h1>
                    <div className="slp-hero-meta">
                        <span className="slp-lesson-progress-text">Урок {currentIndex + 1} из {allLessons.length}</span>
                        {totalSections > 0 && <span className="slp-sections-count">· {totalSections} раздела</span>}
                        {isDone && <span className="slp-hero-done-badge">✓ Пройден</span>}
                    </div>
                    <div className="slp-lesson-progress-bar-wrap">
                        <div className="slp-lesson-progress-bar"
                             style={{width: `${((currentIndex + (isDone ? 1 : 0)) / allLessons.length) * 100}%`}}/>
                    </div>
                </div>
                <div className="slp-hero-right">
                    {!projectSection && (
                        <button className={`slp-complete-btn ${isDone ? 'done' : ''}`} onClick={handleComplete} disabled={isDone}>
                            {isDone ? '✓ Урок пройден' : 'Отметить как пройденный'}
                        </button>
                    )}
                    {projectSection && isDone && (
                        <button className="slp-complete-btn done" disabled>✓ Урок пройден</button>
                    )}
                </div>
            </div>

            {/* ──────────── CONTENT BLOCKS ──────────── */}
            {!lesson.sections || lesson.sections.length === 0 ? (
                <div className="slp-empty">
                    <div className="slp-empty-icon">📄</div>
                    <p>Контент для этого урока ещё не добавлен</p>
                </div>
            ) : (
                <div className="slp-blocks">
                    {lesson.sections.map((section, sIdx) => {
                        const blockMeta = meta(section.type);
                        const ytId = section.type === 'video' ? getYTId(section.videoUrl || '') : null;
                        const isActive = activeSection === section.id;

                        return (
                            <div key={section.id} className={`slp-block slp-block-${section.type}`}
                                 style={{animationDelay: `${sIdx * 0.06}s`}}>
                                <div className="slp-block-header"
                                     onClick={() => setActiveSection(isActive ? null : section.id)}
                                     style={{'--accent': blockMeta.color || '#6c5ce7'}}>
                                    <div className="slp-block-header-left">
                                        <span className="slp-block-icon-wrap"
                                              style={{background: (blockMeta.color || '#6c5ce7') + '18'}}>
                                            {blockMeta?.icon}
                                        </span>
                                        <div className="slp-block-labels">
                                            <span className="slp-block-type">{blockMeta?.label}</span>
                                            {section.label && section.type !== 'exercise' && (
                                                <span className="slp-block-title">{section.label}</span>
                                            )}
                                        </div>
                                    </div>
                                    <span className="slp-block-num">#{sIdx + 1}</span>
                                </div>

                                <div className="slp-block-body">
                                    {section.type === 'text' && (
                                        <div className="slp-text-content"
                                             dangerouslySetInnerHTML={{__html: section.html || '<p style="opacity:0.3">Текст не добавлен</p>'}}/>
                                    )}

                                    {section.type === 'code' && (
                                        <>
                                            <div className="slp-code-header">
                                                <div className="slp-code-dots"><span/><span/><span/></div>
                                                <span className="slp-code-lang">{section.lang || 'code'}</span>
                                                <button className="slp-code-copy"
                                                        onClick={() => copyCode(section.id, section.code || '')}>
                                                    {copiedId === section.id ? '✅ Скопировано' : '📋 Копировать'}
                                                </button>
                                            </div>
                                            <pre className="slp-code-block">{section.code || '// Код не добавлен'}</pre>
                                        </>
                                    )}

                                    {section.type === 'video' && (
                                        <>
                                            <div className="slp-video-wrap">
                                                {ytId
                                                    ? <iframe src={`https://www.youtube.com/embed/${ytId}`}
                                                              allowFullScreen title={section.label || 'Video'}/>
                                                    : <div className="slp-video-empty">🎬 Видео не добавлено</div>}
                                            </div>
                                            {section.videoUrl && (
                                                <a href={section.videoUrl} target="_blank" rel="noopener noreferrer"
                                                   className="slp-video-link">
                                                    🎥 Открыть на YouTube ↗
                                                </a>
                                            )}
                                        </>
                                    )}

                                    {section.type === 'image' && (
                                        <div className="slp-img-block">
                                            {section.imgUrl
                                                ? <img src={section.imgUrl} alt={section.label || ''}/>
                                                : <div className="slp-img-empty">🖼 Изображение не добавлено</div>}
                                        </div>
                                    )}

                                    {section.type === 'file' && (
                                        section.fileName ? (
                                            <div className="slp-file-card">
                                                <div className="slp-file-icon-wrap">📦</div>
                                                <div className="slp-file-info">
                                                    <div className="slp-file-name">{section.fileName}</div>
                                                    {section.fileSize && <div className="slp-file-size">{section.fileSize}</div>}
                                                </div>
                                                <button
                                                    className={`slp-file-dl-btn ${downloadingFile === section.fileName ? 'loading' : ''}`}
                                                    disabled={downloadingFile === section.fileName}
                                                    onClick={() => handleDownloadFile(lesson.id, section.fileName)}
                                                >
                                                    {downloadingFile === section.fileName
                                                        ? <><span className="slp-btn-spin"/>Загружаю...</>
                                                        : '⬇ Скачать'}
                                                </button>
                                            </div>
                                        ) : <div className="slp-file-empty">Файл не добавлен</div>
                                    )}

                                    {section.type === 'exercise' && (
                                        <ExerciseSection section={section} courseId={course.id} lessonId={lesson.id}/>
                                    )}

                                    {section.type === 'project' && (
                                        <div className={`slp-project-task ${projectDone ? 'done' : ''}`}>
                                            <div className="slp-project-top">
                                                <div className="slp-project-icon-wrap">🚀</div>
                                                <div className="slp-project-info">
                                                    <h4>{section.label || 'Практическое задание'}</h4>
                                                    {section.description &&
                                                        <p className="slp-project-desc">{section.description}</p>}
                                                </div>
                                                {projectDone && <span className="slp-project-check">✅ Сдано</span>}
                                            </div>

                                            {section.requirements && (
                                                <div className="slp-project-reqs">
                                                    <div className="slp-reqs-title">📋 Требования</div>
                                                    <div className="slp-reqs-text">{section.requirements}</div>
                                                </div>
                                            )}

                                            {section.techStack && (
                                                <div className="slp-project-tech">
                                                    <span className="slp-reqs-title">🛠 Стек технологий</span>
                                                    <div className="slp-tech-tags">
                                                        {section.techStack.split(',').map((t, i) => (
                                                            <span key={i} className="slp-tech-tag">{t.trim()}</span>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            {section.deadline && (
                                                <div className="slp-project-deadline">
                                                    ⏰ Дедлайн: <strong>{section.deadline} дней</strong>
                                                </div>
                                            )}

                                            {!projectDone ? (
                                                <button className="slp-project-btn" onClick={() => setProjectModal(true)}>
                                                    📤 Загрузить проект
                                                </button>
                                            ) : (
                                                <div className="slp-project-submitted">
                                                    <span>🔗</span>
                                                    <a href={projectForm.github_url} target="_blank" rel="noreferrer">
                                                        {projectForm.github_url || 'Проект сдан'}
                                                    </a>
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

            {/* ──────────── BOTTOM NAV ──────────── */}
            <div className="slp-bottom-nav">
                <button className="slp-bottom-btn prev" onClick={() => prevLesson && onNavigate(prevLesson)} disabled={!prevLesson}>
                    ← Предыдущий урок
                </button>
                {nextBlocked ? (
                    <div className="slp-next-locked">🔒 Сначала сдайте проект</div>
                ) : isDone && nextLesson ? (
                    <button className="slp-bottom-btn next primary" onClick={() => onNavigate(nextLesson)}>
                        Следующий урок →
                    </button>
                ) : !isDone && !projectSection ? (
                    <button className="slp-bottom-btn complete" onClick={handleComplete}>
                        ✓ Отметить и продолжить
                    </button>
                ) : isDone && !nextLesson ? (
                    <button className="slp-bottom-btn done-label" disabled>🎉 Курс завершён!</button>
                ) : null}
            </div>

            {/* ──────────── EXIT MODAL ──────────── */}
            {exitModal && ReactDOM.createPortal(
                <div className="slp-overlay" onClick={() => setExitModal(false)}>
                    <div className="slp-exit-modal" onClick={e => e.stopPropagation()}>
                        <div className="slp-exit-icon">📖</div>
                        <h4>Выйти из урока?</h4>
                        <p>Куда вы хотите перейти?</p>
                        <div className="slp-exit-actions">
                            <button className="slp-exit-opt course" onClick={() => { setExitModal(false); onBack('course'); }}>
                                📚 К курсу «{course.title}»
                            </button>
                            <button className="slp-exit-opt courses" onClick={() => { setExitModal(false); onBack('courses'); }}>
                                🏠 Ко всем курсам
                            </button>
                            <button className="slp-exit-cancel" onClick={() => setExitModal(false)}>
                                Остаться в уроке
                            </button>
                        </div>
                    </div>
                </div>,
                document.body
            )}

            {/* ──────────── PROJECT MODAL ──────────── */}
            {projectModal && ReactDOM.createPortal(
                <div className="slp-overlay" onClick={closeProjectModal}>
                    <div className="slp-modal slp-modal-wide" onClick={e => e.stopPropagation()}>
                        <div className="slp-modal-header">
                            <div className="slp-modal-header-inner">
                                <div className="slp-modal-header-icon">🚀</div>
                                <div>
                                    <h3>Загрузить проект</h3>
                                    <p className="slp-modal-header-sub">Отправьте ссылку и дождитесь проверки</p>
                                </div>
                            </div>
                            <button className="slp-modal-close" onClick={closeProjectModal}>✕</button>
                        </div>

                        <div className="slp-modal-body">
                            <div className="slp-modal-task-banner">
                                <span className="slp-modal-task-icon">📌</span>
                                <span>{projectSection?.label || 'Практическое задание'}</span>
                            </div>

                            {/* ── Upload Method Selector ── */}
                            <div className="slp-modal-field">
                                <label>Способ загрузки кода <span className="slp-field-required">*</span></label>
                                <UploadMethodSelector method={uploadMethod} onChange={handleMethodChange}/>
                            </div>

                            {/* ── GitHub panel ── */}
                            <div className={`slp-source-panel ${uploadMethod === 'github' ? 'slp-source-panel-visible' : ''}`}>
                                <div className="slp-modal-field">
                                    <label>GitHub URL</label>
                                    <div className={`slp-input-wrap ${formErrors.github_url ? 'slp-input-error' : ''}`}>
                                        <span className="slp-input-prefix">🔗</span>
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

                            {/* ── ZIP panel ── */}
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
                                />
                            </div>

                            {zipMsg && (
                                <div className={`slp-zip-msg ${zipMsg.startsWith('✅') ? 'success' : 'warn'}`}>
                                    {zipMsg}
                                </div>
                            )}
                            {projectError && (
                                <div className="slp-project-error">⚠️ {projectError}</div>
                            )}
                        </div>

                        <div className="slp-modal-footer">
                            <button className="slp-modal-cancel" onClick={closeProjectModal}>Отмена</button>
                            <button
                                className="slp-modal-submit"
                                onClick={handleProjectSubmit}
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
            )}

            <DictSelectionPopup lessonId={lesson.id}/>
        </div>
    );
};

export default StudentLessonPage;