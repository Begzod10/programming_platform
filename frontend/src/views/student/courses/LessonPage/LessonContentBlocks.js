import React from 'react';
import { ClipboardList, Upload, Link, Clock, Wrench, Timer, BarChart2, Trophy, CheckCircle } from 'lucide-react';
import { SECTION_TYPES, getYTId } from '../../../../constants/courseUtils';
import StudentProjectFiles from '../StudentProjectPreview/StudentProjectPreview';
import SampleProject from './SampleProject';
import { ExerciseSection } from './LessonExercise';

export const SECTION_META = {
    text:     {icon: '📝', label: 'Текст',        color: '#6c5ce7'},
    code:     {icon: '💻', label: 'Код',           color: '#0f1117'},
    video:    {icon: '🎬', label: 'Видео',         color: '#e84393'},
    image:    {icon: '🖼', label: 'Изображение',   color: '#00b894'},
    file:     {icon: '📦', label: 'Файл',          color: '#fdcb6e'},
    exercise: {icon: '🎯', label: 'Задания',       color: '#a29bfe'},
    project:  {icon: '🚀', label: 'Проект',        color: '#00cec9'},
};

const meta = (type) => SECTION_META[type] || SECTION_TYPES.find(t => t.type === type) || {icon: '🎯', label: 'Секция'};

/* ═══════════════════════════════════════════════════════════
   CONTENT BLOCKS — renders all lesson section types
   Props:
     lesson, course
     activeSection, setActiveSection
     exerciseSubmissions, submissionsReady
     copiedId, copyCode
     downloadingFile, handleDownloadFile, fileDownloadError
     recordVideoWatch
     projectStatus  — { done, pending, failed, score, section,
                         loading, submission, passThreshold }
     onProjectOpen  — callback to open the project submit modal
═══════════════════════════════════════════════════════════ */
export const LessonContentBlocks = ({
    lesson,
    course,
    activeSection,
    setActiveSection,
    exerciseSubmissions,
    submissionsReady,
    copiedId,
    copyCode,
    downloadingFile,
    handleDownloadFile,
    fileDownloadError,
    recordVideoWatch,
    projectStatus,
    onProjectOpen,
}) => {
    const {
        done: projectDone,
        pending: projectPending,
        failed: projectFailed,
        score: projectScore,
        section: projectSection,
        loading: projectStatusLoading,
        submission: projectSubmission,
        passThreshold,
    } = projectStatus;

    if (!lesson.sections || lesson.sections.length === 0) {
        return (
            <div className="slp-empty">
                <div className="slp-empty-icon">📄</div>
                <p>Контент для этого урока ещё не добавлен</p>
            </div>
        );
    }

    return (
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
                                            {copiedId === section.id ? <><CheckCircle size={14} aria-hidden="true" /> Скопировано</> : <><ClipboardList size={14} aria-hidden="true" /> Копировать</>}
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
                                                      allowFullScreen title={section.label || 'Video'}
                                                      onLoad={() => recordVideoWatch(section.id)}/>
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
                                        {section.previewImageUrl && (
                                            <div className="slp-file-preview-wrap">
                                                <img
                                                    src={section.previewImageUrl}
                                                    alt="Loyiha ko'rinishi"
                                                    className="slp-file-preview-img"
                                                />
                                                <div className="slp-file-preview-badge">Natija shunday ko'rinadi</div>
                                            </div>
                                        )}
                                        <div className="slp-file-card-bottom">
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
                                    </div>
                                ) : <div className="slp-file-empty">Файл не добавлен</div>
                            )}
                            {section.type === 'file' && fileDownloadError && (
                                <div className="slp-file-error" role="alert">
                                    ⚠ {fileDownloadError}
                                </div>
                            )}

                            {section.type === 'exercise' && (
                                <ExerciseSection
                                    section={section}
                                    courseId={course.id}
                                    lessonId={lesson.id}
                                    submissions={exerciseSubmissions}
                                    submissionsReady={submissionsReady}
                                />
                            )}

                            {/* ══════════════════════════════════════════
                                PROJECT SECTION
                                — shows SampleProject (live preview)
                                  then the submit/status block below
                            ══════════════════════════════════════════ */}
                            {section.type === 'project' && (
                                <SampleProject lessonId={lesson?.id} />
                            )}
                            {section.type === 'project' && (
                                <div className={`slp-project-task ${projectDone ? 'done' : ''} ${projectFailed ? 'failed' : ''} ${projectPending ? 'pending' : ''}`}>
                                    <div className="slp-project-top">
                                        <div className="slp-project-icon-wrap">🚀</div>
                                        <div className="slp-project-info">
                                            <h4>{section.label || 'Практическое задание'}</h4>
                                            {section.description &&
                                                <p className="slp-project-desc">{section.description}</p>}
                                        </div>
                                        {projectDone && (
                                            <span className="slp-project-check" style={{background: '#16a34a', color: '#fff', padding: '6px 14px', borderRadius: 999, fontWeight: 600}}>
                                                <Trophy size={14} aria-hidden="true" /> {projectScore}/100 — Сдано
                                            </span>
                                        )}
                                        {projectPending && (
                                            <span className="slp-project-check" style={{background: '#fbbf24', color: '#451a03', padding: '6px 14px', borderRadius: 999, fontWeight: 600}}>
                                                <Clock size={14} aria-hidden="true" /> На проверке
                                            </span>
                                        )}
                                        {projectFailed && (
                                            <span className="slp-project-check" style={{
                                                background: projectScore >= 70 ? '#f59e0b' : '#dc2626',
                                                color: '#fff', padding: '6px 14px', borderRadius: 999, fontWeight: 600
                                            }}>
                                                {projectSubmission?.status === 'Rejected'
                                                    ? `✗ ${projectScore}/100 — Отклонено`
                                                    : <><BarChart2 size={14} aria-hidden="true" /> {projectScore}/100</>}
                                            </span>
                                        )}
                                    </div>

                                    {section.previewImage && (
                                        <div className="slp-project-preview">
                                            <div className="slp-reqs-title">🖼 Natija ko'rinishi</div>
                                            <img
                                                src={section.previewImage}
                                                alt="Loyiha natijasi"
                                                className="slp-project-preview-img"
                                            />
                                        </div>
                                    )}

                                    {section.requirements && (
                                        <div className="slp-project-reqs">
                                            <div className="slp-reqs-title"><ClipboardList size={14} aria-hidden="true" /> Требования</div>
                                            <div className="slp-reqs-text">{section.requirements}</div>
                                        </div>
                                    )}

                                    {section.techStack && (
                                        <div className="slp-project-tech">
                                            <span className="slp-reqs-title"><Wrench size={14} aria-hidden="true" /> Стек технологий</span>
                                            <div className="slp-tech-tags">
                                                {section.techStack.split(',').map((t, i) => (
                                                    <span key={i} className="slp-tech-tag">{t.trim()}</span>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {section.deadline && (
                                        <div className="slp-project-deadline">
                                            <Timer size={14} aria-hidden="true" /> Дедлайн: <strong>{section.deadline} дней</strong>
                                        </div>
                                    )}

                                    {/* ── Live preview files from API ── */}
                                    <StudentProjectFiles
                                        lessonId={lesson.id}
                                        courseId={course.id}
                                    />

                                    {/* Reviewer feedback */}
                                    {projectSubmission?.reviewed && (projectSubmission?.instructor_feedback || projectSubmission?.ai_bugs?.length > 0) && (
                                        <div className="slp-project-reqs" style={{marginTop: 12, borderLeft: `3px solid ${projectDone ? '#16a34a' : '#dc2626'}`, paddingLeft: 12}}>
                                            <div className="slp-reqs-title">💬 Отзыв преподавателя {projectSubmission?.grade ? `(${projectSubmission.grade})` : ''}</div>
                                            {projectSubmission.instructor_feedback && (
                                                <div className="slp-reqs-text">{projectSubmission.instructor_feedback}</div>
                                            )}
                                            {projectSubmission?.ai_strengths?.length > 0 && (
                                                <div style={{marginTop: 10}}>
                                                    <div style={{fontWeight: 600, color: '#16a34a', marginBottom: 4}}>✅ Yaxshi tomonlar:</div>
                                                    <ul style={{margin: 0, paddingLeft: 18}}>
                                                        {projectSubmission.ai_strengths.map((s, i) => <li key={i} style={{marginBottom: 2}}>{s}</li>)}
                                                    </ul>
                                                </div>
                                            )}
                                            {projectSubmission?.ai_bugs?.length > 0 && (
                                                <div style={{marginTop: 10}}>
                                                    <div style={{fontWeight: 600, color: '#dc2626', marginBottom: 4}}>🐛 Xatolar:</div>
                                                    <ul style={{margin: 0, paddingLeft: 18}}>
                                                        {projectSubmission.ai_bugs.map((b, i) => <li key={i} style={{marginBottom: 2, fontFamily: 'monospace', fontSize: 13}}>{b}</li>)}
                                                    </ul>
                                                </div>
                                            )}
                                            {projectSubmission?.ai_improvements?.length > 0 && (
                                                <div style={{marginTop: 10}}>
                                                    <div style={{fontWeight: 600, color: '#d97706', marginBottom: 4}}>💡 Yaxshilash kerak:</div>
                                                    <ul style={{margin: 0, paddingLeft: 18}}>
                                                        {projectSubmission.ai_improvements.map((imp, i) => <li key={i} style={{marginBottom: 2}}>{imp}</li>)}
                                                    </ul>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {/* Action area */}
                                    {projectStatusLoading ? (
                                        <div className="slp-project-deadline" style={{opacity: 0.6}}>Загрузка статуса...</div>
                                    ) : projectFailed ? (
                                        <>
                                            <div className="slp-project-deadline" style={{background: '#fef2f2', color: '#991b1b', borderLeft: '3px solid #dc2626', padding: '8px 12px'}}>
                                                ⚠️ Чтобы перейти к следующему уроку, нужно набрать минимум <strong>{passThreshold}/100</strong>. Загрузите проект заново.
                                            </div>
                                            <button className="slp-project-btn" onClick={onProjectOpen} style={{marginTop: 8}}>
                                                🔄 Загрузить заново
                                            </button>
                                        </>
                                    ) : projectPending ? (
                                        <div className="slp-project-submitted">
                                            <span aria-hidden="true"><Clock size={18} /></span>
                                            <span>Ожидание проверки преподавателя</span>
                                        </div>
                                    ) : projectDone ? (
                                        <div className="slp-project-submitted">
                                            <span aria-hidden="true"><Link size={18} /></span>
                                            {projectSubmission?.github_url
                                                ? <a href={projectSubmission.github_url} target="_blank" rel="noreferrer">{projectSubmission.github_url}</a>
                                                : <span>Проект сдан</span>}
                                        </div>
                                    ) : (
                                        <button className="slp-project-btn" onClick={onProjectOpen}>
                                            <Upload size={14} aria-hidden="true" /> Загрузить проект
                                        </button>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                );
            })}
        </div>
    );
};
