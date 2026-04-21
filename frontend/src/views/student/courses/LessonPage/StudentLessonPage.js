import React, {useState} from 'react';
import ReactDOM from 'react-dom';
import './StudentLessonPage.css';
import {SECTION_TYPES, getYTId} from '../../../../constants/courseUtils';
import {API_URL, useHttp, headers} from '../../../../api/search/base';


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
/* ═══════════════════════════════════════════════════════════
   SINGLE EXERCISE CARD  (один exercise = одна карточка)
═══════════════════════════════════════════════════════════ */
const ExerciseCard = ({ex, courseId, lessonId}) => {
    const {request} = useHttp();

    /* ── state ── */
    const [textAnswer,    setTextAnswer]    = useState('');
    const [selected,      setSelected]      = useState([]);   // multiple_choice
    const [fillAnswers,   setFillAnswers]   = useState([]);   // fill_in_blank: массив по пропускам
    // Чистые массивы — на случай если пришли как JSON строка
    const cleanOptions   = parseListField(ex.options);
    const cleanDragItems = parseListField(ex.drag_items);

    const [dragAvailable, setDragAvailable] = useState(
        () => [...cleanDragItems].sort(() => Math.random() - 0.5)
    );
    const [dragDropped,   setDragDropped]   = useState([]);
    const [result,        setResult]        = useState(null); // null | 'correct' | 'wrong' | 'submitted'
    const [aiFeedback,    setAiFeedback]    = useState('');
    const [score,         setScore]         = useState(null);
    const [submitting,    setSubmitting]    = useState(false);
    const [showHint,      setShowHint]      = useState(false);

    const isDone    = result === 'correct' || result === 'submitted';
    const isWrong   = result === 'wrong';
    const exType    = ex.exercise_type;

    /* ── Build student_answer string ── */
    const buildAnswer = () => {
        if (exType === 'fill_in_blank') {
            return fillAnswers.join(',');
        }
        if (exType === 'drag_and_drop') {
            return JSON.stringify(dragDropped.map(s => s.trim()));
        }
        if (exType === 'multiple_choice') {
            return selected.join(',');
        }
        return textAnswer.trim();
    };

    /* ── Submit ── */
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
            if (res?.is_correct === true)       setResult('correct');
            else if (res?.is_correct === false) setResult('wrong');
            else                                setResult('submitted');

            if (res?.ai_feedback) setAiFeedback(res.ai_feedback);
            if (res?.score != null) setScore(res.score);
        } catch {
            setResult('wrong');
        } finally {
            setSubmitting(false);
        }
    };

    /* ── Reset ── */
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

    /* ── helpers ── */
    const DIFF_COLOR = {Easy: '#00b894', Medium: '#e17055', Hard: '#d63031'};
    const diffColor  = DIFF_COLOR[ex.difficulty_level] || '#6c5ce7';
    const optionsList = cleanOptions;

    return (
        <div className={`slp-ex-card ${result === 'correct' ? 'state-correct' : result === 'wrong' ? 'state-wrong' : result === 'submitted' ? 'state-submitted' : ''}`}>

            {/* ── Header ── */}
            <div className="slp-ex-card-head">
                <div className="slp-ex-card-meta">
                    {ex.difficulty_level && (
                        <span className="slp-ex-diff-badge" style={{color: diffColor, borderColor: diffColor, background: diffColor + '18'}}>
                            {ex.difficulty_level}
                        </span>
                    )}
                    {ex.points > 0 && (
                        <span className="slp-ex-pts-badge">⭐ {ex.points} pts</span>
                    )}
                    {score != null && (
                        <span className="slp-ex-score-badge">🏆 +{score} pts</span>
                    )}
                </div>
                {ex.title && <div className="slp-ex-card-title">{ex.title}</div>}
            </div>

            {/* ── Body ── */}
            <div className="slp-ex-card-body">

                {/* ── fill_in_blank ── */}
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

                {/* ── multiple_choice ── */}
                {exType === 'multiple_choice' && (
                    <>
                        {ex.description && <div className="slp-ex-question">{ex.description}</div>}
                        <div className="slp-ex-options">
                            {optionsList.map((opt, i) => {
                                const letter     = String.fromCharCode(65 + i);
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

                {/* ── drag_and_drop ── */}
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

                {/* ── text_input ── */}
                {exType === 'text_input' && (
                    <>
                        {ex.description && <div className="slp-ex-question">{ex.description}</div>}
                        <textarea
                            className="slp-ex-textarea"
                            placeholder="Напишите ваш ответ..."
                            disabled={isDone}
                            value={textAnswer}
                            rows={4}
                            onChange={e => {setTextAnswer(e.target.value); setResult(null);}}
                        />
                        <div className="slp-ex-ai-note">🤖 Ответ проверяется AI</div>
                    </>
                )}

                {/* ── Hint ── */}
                {ex.hint && (
                    <div className="slp-ex-hint-wrap">
                        <button className="slp-ex-hint-btn" onClick={() => setShowHint(h => !h)}>
                            💡 {showHint ? 'Скрыть подсказку' : 'Показать подсказку'}
                        </button>
                        {showHint && <div className="slp-ex-hint-text">{ex.hint}</div>}
                    </div>
                )}

                {/* ── Result feedback ── */}
                {result && (
                    <div className={`slp-ex-result-banner ${result}`}>
                        {result === 'correct'   && <><span className="slp-res-icon">🎉</span><div><strong>Правильно!</strong> Отличная работа!</div></>}
                        {result === 'wrong'     && <><span className="slp-res-icon">❌</span><div><strong>Неправильно.</strong> Попробуйте ещё раз.</div></>}
                        {result === 'submitted' && <><span className="slp-res-icon">✅</span><div><strong>Ответ отправлен!</strong></div></>}
                    </div>
                )}

                {/* ── AI Feedback ── */}
                {aiFeedback && (
                    <div className="slp-ex-ai-feedback">
                        <div className="slp-ex-ai-feedback-label">🤖 AI Feedback:</div>
                        <div className="slp-ex-ai-feedback-text">{aiFeedback}</div>
                    </div>
                )}

                {/* ── Footer buttons ── */}
                <div className="slp-ex-actions">
                    {!isDone && (
                        <button
                            className="slp-ex-submit-btn"
                            onClick={handleSubmit}
                            disabled={submitting || !buildAnswer()}
                        >
                            {submitting ? '⏳ Проверяем...' : '✅ Проверить ответ'}
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
   EXERCISE SECTION BLOCK  (список карточек)
═══════════════════════════════════════════════════════════ */
const ExerciseSection = ({section, courseId, lessonId}) => {
    const exercises = section.exercises || [];
    if (exercises.length === 0) return null;

    const totalPts = exercises.reduce((s, e) => s + (e.points || 0), 0);

    return (
        <div className="slp-ex-section">
            <div className="slp-ex-section-bar">
                <span className="slp-ex-section-count">🎯 {exercises.length} заданий</span>
                {totalPts > 0 && <span className="slp-ex-section-pts">🏆 {totalPts} pts</span>}
            </div>
            <div className="slp-ex-section-list">
                {exercises
                    .slice()
                    .sort((a, b) => (a.order || 0) - (b.order || 0))
                    .map((ex, i) => (
                        <ExerciseCard
                            key={ex.id || i}
                            ex={ex}
                            courseId={courseId}
                            lessonId={lessonId}
                        />
                    ))
                }
            </div>
        </div>
    );
};

/* ═══════════════════════════════════════════════════════════
   MAIN — StudentLessonPage
═══════════════════════════════════════════════════════════ */
const StudentLessonPage = ({lesson, course, allLessons, onBack, onNavigate, onComplete}) => {
    const {request} = useHttp();

    const [copiedId,      setCopiedId]      = useState(null);
    const [justCompleted, setJustCompleted] = useState(false);
    const [projectModal,  setProjectModal]  = useState(false);
    const [exitModal,     setExitModal]     = useState(false);
    const [projectForm,   setProjectForm]   = useState({github_url: '', live_demo_url: '', description: ''});
    const [projectDone,   setProjectDone]   = useState(
        () => localStorage.getItem(`project_done_lesson_${lesson.id}`) === 'true'
    );
    const [projectSaving, setProjectSaving] = useState(false);
    const [projectError,  setProjectError]  = useState('');

    const currentIndex  = allLessons.findIndex(l => l.id === lesson.id);
    const prevLesson    = currentIndex > 0 ? allLessons[currentIndex - 1] : null;
    const nextLesson    = currentIndex < allLessons.length - 1 ? allLessons[currentIndex + 1] : null;
    const projectSection = lesson.sections?.find(s => s.type === 'project');
    const nextBlocked   = !!projectSection && !projectDone;
    const isDone        = lesson.completed || justCompleted;

    const copyCode = (id, code) => {
        navigator.clipboard.writeText(code).then(() => {
            setCopiedId(id);
            setTimeout(() => setCopiedId(null), 2000);
        });
    };

    // ─── ИЗМЕНЕНО: handleComplete теперь async, вызывает check-and-earn на последнем уроке ───
    const handleComplete = async () => {
        if (!lesson.completed) {
            onComplete();
            setJustCompleted(true);

            // Если это последний урок курса — фиксируем сертификат
            const isLastLesson = currentIndex === allLessons.length - 1;
            if (isLastLesson && course.id) {
                try {
                    await fetch(
                        `${API_URL}v1/achievements/check-and-earn-certificate?course_id=${course.id}`,
                        { method: 'POST', headers: headers() }
                    );
                    console.log('=== check-and-earn-certificate called for course', course.id);
                } catch (e) {
                    // Не блокируем UX — сертификат можно будет выдать и вручную из Degrees
                    console.warn('check-and-earn-certificate failed:', e);
                }
            }
        }
    };

    const handleProjectSubmit = async () => {
        if (!projectForm.github_url.trim()) return;
        const descriptionRaw = projectForm.description.trim() || projectSection?.description || '';
        const description = descriptionRaw.length >= 10
            ? descriptionRaw
            : (descriptionRaw + ' (loyiha)').padEnd(10, '.');

        setProjectSaving(true);
        setProjectError('');
        try {
            const techList = projectSection?.techStack
                ? projectSection.techStack.split(',').map(t => t.trim()).filter(Boolean)
                : [];
            const created = await request(
                `${API_URL}v1/project/`, 'POST',
                JSON.stringify({
                    title: projectSection?.label || lesson.title,
                    description,
                    github_url: projectForm.github_url,
                    live_demo_url: projectForm.live_demo_url || '',
                    technologies_used: techList,
                    difficulty_level: 'Easy',
                    project_files: '',
                }),
                headers()
            );
            if (created?.id) {
                await request(`${API_URL}v1/project/${created.id}/submit`, 'POST', null, headers());
            }
            localStorage.setItem(`project_done_lesson_${lesson.id}`, 'true');
            setProjectDone(true);
            setProjectModal(false);

            if (!lesson.completed) {
                onComplete();
                setJustCompleted(true);

                // Проверяем сертификат и на последнем уроке с проектом
                const isLastLesson = currentIndex === allLessons.length - 1;
                if (isLastLesson && course.id) {
                    try {
                        await fetch(
                            `${API_URL}v1/achievements/check-and-earn-certificate?course_id=${course.id}`,
                            { method: 'POST', headers: headers() }
                        );
                        console.log('=== check-and-earn-certificate called after project submit for course', course.id);
                    } catch (e) {
                        console.warn('check-and-earn-certificate failed:', e);
                    }
                }
            }
        } catch (err) {
            setProjectError('Ошибка при отправке. Проверьте данные и попробуйте ещё раз.');
        } finally {
            setProjectSaving(false);
        }
    };

    const meta = (type) => SECTION_TYPES.find(t => t.type === type) || {icon: '🎯', label: 'Exercise'};

    return (
        <div className="slp-container">

            {/* Top bar */}
            <div className="slp-top-bar">
                <div className="slp-breadcrumb">
                    <button className="slp-bc-btn" onClick={() => onBack('courses')}>Курсы</button>
                    <span className="slp-bc-sep">›</span>
                    <button className="slp-bc-btn" onClick={() => onBack('course')}>{course.title}</button>
                    <span className="slp-bc-sep">›</span>
                    <span className="slp-bc-current">{lesson.title}</span>
                </div>
                <div className="slp-top-actions">
                    <div className="slp-nav-btns">
                        <button className="slp-nav-btn" onClick={() => prevLesson && onNavigate(prevLesson)} disabled={!prevLesson}>
                            ← Предыдущий
                        </button>
                        <button className="slp-nav-btn"
                            onClick={() => !nextBlocked && nextLesson && onNavigate(nextLesson)}
                            disabled={!nextLesson || nextBlocked}>
                            Следующий →
                        </button>
                    </div>
                    <button className="slp-exit-btn" onClick={() => setExitModal(true)}>✕ Выйти из урока</button>
                </div>
            </div>

            {/* Lesson header */}
            <div className="slp-lesson-header">
                <div className="slp-header-left">
                    {lesson.chapter && <span className="slp-chapter-badge">{lesson.chapter}</span>}
                    <h1>{lesson.title}</h1>
                    <p className="slp-lesson-num">Урок {currentIndex + 1} из {allLessons.length}</p>
                </div>
                {!projectSection && (
                    <button className={`slp-complete-btn ${isDone ? 'done' : ''}`} onClick={handleComplete} disabled={isDone}>
                        {isDone ? '✓ Урок пройден' : 'Отметить как пройденный'}
                    </button>
                )}
                {projectSection && isDone && (
                    <button className="slp-complete-btn done" disabled>✓ Урок пройден</button>
                )}
            </div>

            {/* Content blocks */}
            {!lesson.sections || lesson.sections.length === 0 ? (
                <div className="slp-empty">
                    <div className="slp-empty-icon">📄</div>
                    <p>Контент для этого урока ещё не добавлен</p>
                </div>
            ) : (
                <div className="slp-blocks">
                    {lesson.sections.map((section) => {
                        const blockMeta = meta(section.type);
                        const ytId = section.type === 'video' ? getYTId(section.videoUrl || '') : null;

                        return (
                            <div key={section.id} className="slp-block">
                                <div className="slp-block-header">
                                    <span className="slp-block-icon">{blockMeta?.icon}</span>
                                    <span className="slp-block-type">{blockMeta?.label}</span>
                                    {section.label && section.type !== 'exercise' && (
                                        <span className="slp-block-title">{section.label}</span>
                                    )}
                                </div>
                                <div className="slp-block-body">

                                    {/* TEXT */}
                                    {section.type === 'text' && (
                                        <div className="slp-text-content"
                                            dangerouslySetInnerHTML={{__html: section.html || '<p style="color:rgba(26,26,46,0.3)">Текст не добавлен</p>'}}/>
                                    )}

                                    {/* CODE */}
                                    {section.type === 'code' && (<>
                                        <div className="slp-code-header">
                                            <span className="slp-code-lang">{section.lang || 'code'}</span>
                                            <button className="slp-code-copy" onClick={() => copyCode(section.id, section.code || '')}>
                                                {copiedId === section.id ? '✅ Скопировано' : '📋 Копировать'}
                                            </button>
                                        </div>
                                        <pre className="slp-code-block">{section.code || '// Код не добавлен'}</pre>
                                    </>)}

                                    {/* VIDEO */}
                                    {section.type === 'video' && (<>
                                        <div className="slp-video-wrap">
                                            {ytId
                                                ? <iframe src={`https://www.youtube.com/embed/${ytId}`} allowFullScreen title={section.label || 'Video'}/>
                                                : <div className="slp-video-empty">Видео не добавлено</div>}
                                        </div>
                                        {section.videoUrl && (
                                            <a href={section.videoUrl} target="_blank" rel="noopener noreferrer" className="slp-video-link">
                                                🎥 Открыть на YouTube
                                            </a>
                                        )}
                                    </>)}

                                    {/* IMAGE */}
                                    {section.type === 'image' && (
                                        <div className="slp-img-block">
                                            {section.imgUrl
                                                ? <img src={section.imgUrl} alt={section.label || ''}/>
                                                : <div className="slp-img-empty">Изображение не добавлено</div>}
                                        </div>
                                    )}

                                    {/* FILE */}
                                    {section.type === 'file' && (
                                        section.fileName ? (
                                            <div className="slp-file-card">
                                                <span className="slp-file-icon">📦</span>
                                                <div className="slp-file-info">
                                                    <div className="slp-file-name">{section.fileName}</div>
                                                    {section.fileSize && <div className="slp-file-size">{section.fileSize}</div>}
                                                </div>
                                                <button className="slp-file-dl-btn">⬇ Скачать</button>
                                            </div>
                                        ) : <div className="slp-file-empty">Файл не добавлен</div>
                                    )}

                                    {/* EXERCISE */}
                                    {section.type === 'exercise' && (
                                        <ExerciseSection
                                            section={section}
                                            courseId={course.id}
                                            lessonId={lesson.id}
                                        />
                                    )}

                                    {/* PROJECT */}
                                    {section.type === 'project' && (
                                        <div className={`slp-project-task ${projectDone ? 'done' : ''}`}>
                                            <div className="slp-project-top">
                                                <div className="slp-project-icon">🚀</div>
                                                <div className="slp-project-info">
                                                    <h4>{section.label || 'Практическое задание'}</h4>
                                                    {section.description && <p className="slp-project-desc">{section.description}</p>}
                                                </div>
                                                {projectDone && <span className="slp-project-check">✅ Сдано</span>}
                                            </div>
                                            {section.requirements && (
                                                <div className="slp-project-reqs">
                                                    <div className="slp-reqs-title">📋 Требования:</div>
                                                    <div className="slp-reqs-text">{section.requirements}</div>
                                                </div>
                                            )}
                                            {section.techStack && (
                                                <div className="slp-project-tech">
                                                    <span className="slp-reqs-title">🛠 Стек:</span>
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
                                                        {projectForm.github_url}
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

            {/* Bottom nav */}
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
                    <button className="slp-bottom-btn done-label" disabled>✓ Курс завершён</button>
                ) : null}
            </div>

            {/* Exit modal */}
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

            {/* Project modal */}
            {projectModal && ReactDOM.createPortal(
                <div className="slp-overlay" onClick={() => setProjectModal(false)}>
                    <div className="slp-modal" onClick={e => e.stopPropagation()}>
                        <div className="slp-modal-header">
                            <h3>📤 Загрузить проект</h3>
                            <button className="slp-modal-close" onClick={() => setProjectModal(false)}>✕</button>
                        </div>
                        <div className="slp-modal-body">
                            <p className="slp-modal-task-name">🚀 {projectSection?.label || 'Практическое задание'}</p>
                            <div className="slp-modal-field">
                                <label>GitHub URL *</label>
                                <input placeholder="https://github.com/username/repo"
                                    value={projectForm.github_url}
                                    onChange={e => setProjectForm(f => ({...f, github_url: e.target.value}))}/>
                            </div>
                            <div className="slp-modal-field">
                                <label>Live Demo URL</label>
                                <input placeholder="https://myproject.com"
                                    value={projectForm.live_demo_url}
                                    onChange={e => setProjectForm(f => ({...f, live_demo_url: e.target.value}))}/>
                            </div>
                            <div className="slp-modal-field">
                                <label>Комментарий</label>
                                <textarea placeholder="Расскажите что сделали..." rows={3}
                                    value={projectForm.description}
                                    onChange={e => setProjectForm(f => ({...f, description: e.target.value}))}/>
                            </div>
                            {projectError && (
                                <div style={{color:'#e53e3e',fontSize:'13px',marginTop:'8px',padding:'8px 12px',background:'#fff5f5',borderRadius:'8px'}}>
                                    ⚠️ {projectError}
                                </div>
                            )}
                        </div>
                        <div className="slp-modal-footer">
                            <button className="slp-modal-cancel" onClick={() => { setProjectModal(false); setProjectError(''); }}>Отмена</button>
                            <button className="slp-modal-submit" onClick={handleProjectSubmit}
                                disabled={!projectForm.github_url.trim() || projectSaving}>
                                {projectSaving ? '⏳ Отправка...' : '✅ Отправить'}
                            </button>
                        </div>
                    </div>
                </div>,
                document.body
            )}

        </div>
    );
};

export default StudentLessonPage;