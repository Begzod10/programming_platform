import React, {useState, useRef, useCallback, useEffect} from 'react';
import ReactDOM from 'react-dom';
import mermaid from 'mermaid';
import './StudentLessonPage.css';
import {API_URL, useHttp, headers} from '../../../../api/search/base';
import {useTranslation} from '../../../../i18n/useTranslation';
import DictSelectionPopup from '../LessonPage/Dictselectionpopup';
import LessonDictionaryDrawer from './LessonDictionaryDrawer';
import LessonVocabCard from './LessonVocabCard';
import CelebrationOverlay from './CelebrationOverlay';
import { Lock } from 'lucide-react';
import { LessonFeedbackWidget } from './LessonFeedback';
import { LessonProjectModal } from './LessonProjectModal';
import { LessonContentBlocks } from './LessonContentBlocks';

// One-time Mermaid init at module load. startOnLoad:false because we trigger
// run() manually after each lesson's text section mounts.
mermaid.initialize({
    startOnLoad: false,
    theme: 'base',
    securityLevel: 'loose',
    flowchart: {useMaxWidth: true, htmlLabels: true},
    themeVariables: {
        fontFamily: 'system-ui, -apple-system, "Segoe UI", sans-serif',
        primaryColor: '#ede9ff',
        primaryTextColor: '#3c2ca8',
        primaryBorderColor: '#6c5ce7',
        lineColor: '#6c5ce7',
        secondaryColor: '#f0f0ff',
        tertiaryColor: '#f8f7ff',
        background: '#ffffff',
        mainBkg: '#ede9ff',
        nodeBorder: '#6c5ce7',
        clusterBkg: '#f8f7ff',
        titleColor: '#1a1a2e',
        edgeLabelBackground: '#ffffff',
    },
});

/* ═══════════════════════════════════════════════════════════
   MAIN — StudentLessonPage
═══════════════════════════════════════════════════════════ */
const StudentLessonPage = ({lesson, course, allLessons, onBack, onNavigate, onComplete}) => {
    const {request} = useHttp();
    const {t, lang} = useTranslation();

    // AI review feedback is authored in Uzbek; the backend translates it on
    // read when we say which language the student is reading in.
    const langParam = lang && lang !== 'uz' ? `?lang=${lang}` : '';

    const [copiedId, setCopiedId] = useState(null);
    const [justCompleted, setJustCompleted] = useState(false);
    const [projectModal, setProjectModal] = useState(false);
    const [exitModal, setExitModal] = useState(false);
    const [showCelebration, setShowCelebration] = useState(false);
    const [projectForm, setProjectForm] = useState({github_url: '', live_demo_url: '', description: ''});
    const [projectSubmission, setProjectSubmission] = useState(null);
    const [projectStatusLoading, setProjectStatusLoading] = useState(false);
    // Daily AI-review budget { used_today, limit, remaining, can_submit }.
    // Drives the disabled state of the project-submit button so a student
    // can't submit once the cap is hit (the auto-review would be skipped
    // and the project left pending). null until the first fetch resolves.
    const [aiQuota, setAiQuota] = useState(null);
    const [projectSaving, setProjectSaving] = useState(false);
    const [projectError, setProjectError] = useState('');
    const [downloadingFile, setDownloadingFile] = useState(null);
    const [fileDownloadError, setFileDownloadError] = useState('');
    const [completing, setCompleting] = useState(false);
    const [activeSection, setActiveSection] = useState(null);
    // Map of exercise_id -> latest submission { is_correct, score, ai_feedback,
    // student_answer, submitted_at }. Hydrates ExerciseCard state after a
    // page refresh so the student sees their previous score + checkmark.
    const [exerciseSubmissions, setExerciseSubmissions] = useState({});
    // Flipped to true once the fetch resolves (success or fail). Drives the
    // ExerciseCard key suffix so cards remount with hydrated initial state.
    const [submissionsReady, setSubmissionsReady] = useState(false);

    useEffect(() => {
        if (!lesson?.id) return;
        let cancelled = false;
        let running = false;
        let scheduled = null;
        const schedule = (delay = 100) => {
            if (scheduled || cancelled) return;
            scheduled = setTimeout(runMermaid, delay);
        };
        const runMermaid = () => {
            scheduled = null;
            if (cancelled) return;
            // If a run is already in flight, retry after it finishes
            if (running) { schedule(120); return; }
            const nodes = document.querySelectorAll(
                'pre.mermaid:not([data-processed="true"])',
            );
            if (nodes.length === 0) return;
            running = true;
            mermaid
                .run({nodes: Array.from(nodes)})
                .catch(() => {})
                .finally(() => {
                    running = false;
                    // Pick up any nodes that appeared while we were running
                    if (!cancelled) {
                        const pending = document.querySelectorAll(
                            'pre.mermaid:not([data-processed="true"])',
                        );
                        if (pending.length > 0) schedule(50);
                    }
                });
        };
        schedule();
        const target =
            document.querySelector('.slp-blocks') || document.body;
        const observer = new MutationObserver(() => schedule(100));
        observer.observe(target, {childList: true, subtree: true});
        return () => {
            cancelled = true;
            observer.disconnect();
            if (scheduled) clearTimeout(scheduled);
        };
    }, [lesson?.id]);

    const watchedSectionsRef = useRef(new Set());
    const recordVideoWatch = useCallback((sectionId) => {
        if (!sectionId || !course?.id || !lesson?.id) return;
        const key = `${lesson.id}:${sectionId}`;
        if (watchedSectionsRef.current.has(key)) return;
        watchedSectionsRef.current.add(key);
        request(
            `${API_URL}v1/courses/${course.id}/lessons/${lesson.id}/sections/${sectionId}/watch`,
            'POST',
            null,
            headers(),
        ).catch(() => {
            watchedSectionsRef.current.delete(key);
        });
    }, [course?.id, lesson?.id, request]);

    const [uploadMethod, setUploadMethod] = useState('github');
    const [zipFile, setZipFile] = useState(null);
    const [zipUploading, setZipUploading] = useState(false);
    const [zipMsg, setZipMsg] = useState('');
    const [formErrors, setFormErrors] = useState({});

    // ── Anti-cheat tracking ──────────────────────────────────────────────────
    const projectOpenedAtRef = useRef(null);
    const keystrokeCountRef  = useRef(0);
    const pasteCountRef      = useRef(0);

    // Record when the project modal opens
    const handleProjectModalOpen = () => {
        // Daily AI-review cap reached → don't even open the modal; the
        // submit would be skipped and the project stranded in "pending".
        if (quotaExhausted) return;
        if (!projectOpenedAtRef.current) {
            projectOpenedAtRef.current = Date.now();
        }
        keystrokeCountRef.current = 0;
        pasteCountRef.current = 0;
        setProjectModal(true);
    };

    // Explanation modal state
    const [explanationModal, setExplanationModal]     = useState(false);
    const [explanationProjectId, setExplanationProjectId] = useState(null);
    const [explanationText, setExplanationText]       = useState('');
    const [explanationSaving, setExplanationSaving]   = useState(false);

    const currentIndex = allLessons.findIndex(l => l.id === lesson.id);
    const prevLesson = currentIndex > 0 ? allLessons[currentIndex - 1] : null;
    const nextLesson = currentIndex < allLessons.length - 1 ? allLessons[currentIndex + 1] : null;
    const projectSection = lesson.sections?.find(s => s.type === 'project');

    const passThreshold = projectSubmission?.pass_threshold ?? 90;
    const projectDone = !!projectSubmission?.passed;
    const projectPending = !!projectSubmission?.submitted && !projectSubmission?.reviewed;
    const projectFailed = !!projectSubmission?.reviewed && !projectSubmission?.passed;
    const projectScore = projectSubmission?.points_earned ?? 0;
    const nextBlocked = !!projectSection && !projectDone;
    const isDone = lesson.completed || justCompleted;

    // Show celebration once when project is approved with 75+ points
    useEffect(() => {
        if (!projectDone || projectScore < 75 || !lesson?.id) return;
        const key = `project_celebrated_${lesson.id}`;
        if (localStorage.getItem(key)) return;
        localStorage.setItem(key, '1');
        setShowCelebration(true);
    }, [projectDone, projectScore, lesson?.id]);

    useEffect(() => {
        if (!projectSection || !course?.id || !lesson?.id) {
            setProjectSubmission(null);
            return;
        }
        let cancelled = false;
        setProjectStatusLoading(true);
        request(
            `${API_URL}v1/courses/${course.id}/lessons/${lesson.id}/submission${langParam}`,
            'GET',
            null,
            headers(),
        )
            .then(res => {
                if (cancelled || !res) return;
                setProjectSubmission(res);
                if (res.submitted) {
                    setProjectForm(f => ({
                        ...f,
                        github_url: res.github_url || '',
                        live_demo_url: res.live_demo_url || '',
                        description: res.description || '',
                    }));
                }
            })
            .catch(() => {
                if (!cancelled) setProjectSubmission({submitted: false, pass_threshold: 90});
            })
            .finally(() => { if (!cancelled) setProjectStatusLoading(false); });
        return () => { cancelled = true; };
        // langParam is a dependency so flipping UZ/RU refetches the verdict
        // in the newly selected language instead of leaving the old text.
    }, [projectSection, course?.id, lesson?.id, request, langParam]);

    // Fetch the student's remaining AI-review budget for the day, but only
    // on lessons that actually have a project to submit. Refetched via
    // refreshAiQuota() after a submit so the button reflects the review
    // just consumed.
    const refreshAiQuota = useCallback(() => {
        if (!projectSection) return;
        request(`${API_URL}v1/ai/quota`, 'GET', null, headers())
            .then(res => { if (res) setAiQuota(res); })
            .catch(() => { /* leave button enabled if the check fails */ });
    }, [projectSection, request]);

    useEffect(() => {
        if (!projectSection) { setAiQuota(null); return; }
        refreshAiQuota();
    }, [projectSection, lesson?.id, refreshAiQuota]);

    const quotaExhausted = aiQuota != null && aiQuota.can_submit === false;
    const quotaMessage = aiQuota
        ? t('lcb.quotaExhausted').replace('{limit}', aiQuota.limit)
        : '';

    // Hydrate exercise submissions on lesson load so a refresh restores the
    // student's previous answers + checkmarks. The student can still resubmit.
    useEffect(() => {
        if (!lesson?.id) {
            setExerciseSubmissions({});
            setSubmissionsReady(false);
            return;
        }
        let cancelled = false;
        setSubmissionsReady(false);
        setExerciseSubmissions({});
        request(
            `${API_URL}v1/lessons/${lesson.id}/my-exercise-submissions`,
            'GET',
            null,
            headers(),
        )
            .then(rows => {
                if (cancelled) return;
                const map = {};
                if (Array.isArray(rows)) {
                    for (const r of rows) {
                        if (r && r.exercise_id != null) map[r.exercise_id] = r;
                    }
                }
                setExerciseSubmissions(map);
            })
            .catch(() => { if (!cancelled) setExerciseSubmissions({}); })
            .finally(() => { if (!cancelled) setSubmissionsReady(true); });
        return () => { cancelled = true; };
    }, [lesson?.id, request]);

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
            setFileDownloadError('Не удалось скачать файл. Попробуйте ещё раз.');
            // Auto-clear so a transient error doesn't stick around forever.
            setTimeout(() => setFileDownloadError(''), 5000);
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
        // Guard against double-click: the user can rapid-fire the button
        // while onComplete()'s optimistic API call is still in flight.
        if (completing || lesson.completed || justCompleted) return;
        setCompleting(true);
        try {
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
        } finally {
            setCompleting(false);
        }
    };

    const validateProject = () => {
        const e = {};
        if (uploadMethod === 'github') {
            const url = projectForm.github_url.trim();
            if (!url) {
                e.github_url = 'Введите GitHub ссылку';
            } else if (!/^https:\/\/github\.com\/[^/]+\/[^/]+/.test(url)) {
                e.github_url = 'Введите корректную ссылку GitHub: https://github.com/ваш_логин/репозиторий';
            } else if (/\/(username|your.?username|user|owner|имя_пользователя|ваш_логин|sizning_username|foydalanuvchi_nomi)\//i.test(url)) {
                e.github_url = 'Пожалуйста, введите вашу реальную GitHub ссылку, а не пример';
            }
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

        const elapsedSeconds = projectOpenedAtRef.current
            ? Math.floor((Date.now() - projectOpenedAtRef.current) / 1000)
            : 0;

        const descriptionRaw = (projectForm.description.trim() || projectSection?.description || '').trim();
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
                    lesson_id: lesson.id,
                    time_spent_seconds: elapsedSeconds,
                    keystroke_count: keystrokeCountRef.current,
                    paste_count: pasteCountRef.current,
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

            // ZIP uploads already run the full AI review pipeline inside
            // upload_project_zip_by_id; calling submit again would reset
            // the AI-reviewed status back to "Submitted".
            if (created?.id && uploadMethod !== 'zip') {
                await request(`${API_URL}v1/project/${created.id}/submit`, 'POST', null, headers());
            }

            let fresh = null;
            try {
                fresh = await request(
                    `${API_URL}v1/courses/${course.id}/lessons/${lesson.id}/submission${langParam}`,
                    'GET', null, headers(),
                );
                if (fresh) setProjectSubmission(fresh);
            } catch { /* fall through */ }
            // The submit (or ZIP upload) just consumed one AI review — refresh
            // the budget so the button disables the moment the cap is reached.
            refreshAiQuota();
            setProjectModal(false);
            // ── Code explanation step ────────────────────────────────────────
            if (created?.id) {
                setExplanationProjectId(created.id);
                setExplanationText('');
                setExplanationModal(true);
            }

            // Unlock next lesson ONLY when the project actually passed
            // (backend AI review or teacher review sets passed=true when
            // points_earned >= pass_threshold and status == "Approved").
            // A submitted-but-not-yet-reviewed or Rejected project must NOT
            // create a LessonCompletion — the student has to re-submit.
            if (!lesson.completed && fresh?.passed === true) {
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
        if (quotaExhausted) return true;
        if (projectSaving) return true;
        if (uploadMethod === 'github') return !projectForm.github_url.trim();
        if (!zipFile) return true;
        if (zipFile.size === 0) return true;
        if (zipFile.size > 15 * 1024 * 1024) return true;
        return false;
    };

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
                                title={
                                    !nextBlocked ? ''
                                    : projectPending ? 'Ожидание проверки проекта'
                                    : projectFailed ? `Нужно ${passThreshold}/100 (сейчас ${projectScore})`
                                    : 'Сначала сдайте проект'
                                }>
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
                {!isDone && !projectSection && (
                    <div className="slp-hero-right">
                        <button
                            className="slp-complete-btn"
                            onClick={handleComplete}
                            disabled={completing}
                        >
                            {completing ? 'Сохранение…' : 'Отметить как пройденный'}
                        </button>
                    </div>
                )}
            </div>

            {/* ──────────── VOCABULARY PREP CARD ──────────── */}
            <LessonVocabCard courseId={lesson.course_id} lessonId={lesson.id} />

            {/* ──────────── CONTENT BLOCKS ──────────── */}
            <LessonContentBlocks
                lesson={lesson}
                course={course}
                activeSection={activeSection}
                setActiveSection={setActiveSection}
                exerciseSubmissions={exerciseSubmissions}
                submissionsReady={submissionsReady}
                copiedId={copiedId}
                copyCode={copyCode}
                downloadingFile={downloadingFile}
                handleDownloadFile={handleDownloadFile}
                fileDownloadError={fileDownloadError}
                recordVideoWatch={recordVideoWatch}
                projectStatus={{
                    done: projectDone,
                    pending: projectPending,
                    failed: projectFailed,
                    score: projectScore,
                    section: projectSection,
                    loading: projectStatusLoading,
                    submission: projectSubmission,
                    passThreshold,
                    quotaExhausted,
                    quotaMessage,
                }}
                onProjectOpen={handleProjectModalOpen}
            />

            {/* ──────────── LESSON FEEDBACK ──────────── */}
            {lesson?.id && <LessonFeedbackWidget lessonId={lesson.id}/>}

            {/* ──────────── BOTTOM NAV ──────────── */}
            <div className="slp-bottom-nav">
                <button className="slp-bottom-btn prev" onClick={() => prevLesson && onNavigate(prevLesson)} disabled={!prevLesson}>
                    ← Предыдущий урок
                </button>
                {nextBlocked ? (
                    <div className="slp-next-locked">
                        {projectPending
                            ? <><Lock size={14} aria-hidden="true" /> Ожидание проверки проекта</>
                            : projectFailed
                                ? <><Lock size={14} aria-hidden="true" /> Нужно набрать {passThreshold}/100 — текущий {projectScore}</>
                                : <><Lock size={14} aria-hidden="true" /> Сначала сдайте проект</>}
                    </div>
                ) : isDone && nextLesson ? (
                    <button className="slp-bottom-btn next primary" onClick={() => onNavigate(nextLesson)}>
                        Следующий урок →
                    </button>
                ) : !isDone && !projectSection ? (
                    <button
                        className="slp-bottom-btn complete"
                        onClick={handleComplete}
                        disabled={completing}
                    >
                        {completing ? '⏳ Сохранение…' : '✓ Отметить и продолжить'}
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
            <LessonProjectModal
                isOpen={projectModal}
                onClose={closeProjectModal}
                projectSection={projectSection}
                uploadMethod={uploadMethod}
                onMethodChange={handleMethodChange}
                projectForm={projectForm}
                setProjectForm={setProjectForm}
                formErrors={formErrors}
                setFormErrors={setFormErrors}
                zipFile={zipFile}
                setZipFile={setZipFile}
                zipUploading={zipUploading}
                zipMsg={zipMsg}
                projectError={projectError}
                projectSaving={projectSaving}
                isSubmitDisabled={isSubmitDisabled}
                onSubmit={handleProjectSubmit}
                quotaExhausted={quotaExhausted}
                quotaMessage={quotaMessage}
                keystrokeCountRef={keystrokeCountRef}
                pasteCountRef={pasteCountRef}
            />

            {/* ── Code explanation modal ─────────────────────────────────── */}
            {explanationModal && ReactDOM.createPortal(
                <div className="slp-modal-overlay" onClick={() => setExplanationModal(false)}>
                    <div className="slp-modal-box" onClick={e => e.stopPropagation()} style={{maxWidth: 520}}>
                        <div className="slp-modal-header">
                            <h3>Kodni tushuntiring</h3>
                            <button className="slp-modal-close" onClick={() => setExplanationModal(false)}>✕</button>
                        </div>
                        <div className="slp-modal-body">
                            <p style={{marginBottom: 12, color: '#555', fontSize: 14}}>
                                Loyihangizni muvaffaqiyatli topshirdingiz! O'qituvchiga kodni yaxshiroq tushunishi uchun — nima qilganingizni va qanday ishlashini qisqacha tushuntiring.
                            </p>
                            <label style={{fontWeight: 600, fontSize: 13, display: 'block', marginBottom: 6}}>
                                Kodingizni o'z so'zlaringiz bilan tushuntiring:
                            </label>
                            <textarea
                                rows={6}
                                style={{width:'100%', padding:'10px', borderRadius: 8, border:'1px solid #ddd', fontSize: 14, resize: 'vertical'}}
                                placeholder="Masalan: Men counter.js faylida click hodisasini ushlash uchun addEventListener ishlatdim. Har safar tugma bosilganda count o'zgaruvchisi 1 ga ortadi va innerHTML orqali ekranga chiqaradi..."
                                value={explanationText}
                                onChange={e => setExplanationText(e.target.value)}
                            />
                        </div>
                        <div className="slp-modal-footer">
                            <button className="slp-modal-cancel" onClick={() => setExplanationModal(false)}>
                                O'tkazib yuborish
                            </button>
                            <button
                                className="slp-modal-submit"
                                disabled={explanationSaving || explanationText.trim().length < 20}
                                onClick={async () => {
                                    if (!explanationProjectId || explanationText.trim().length < 20) return;
                                    setExplanationSaving(true);
                                    try {
                                        await fetch(
                                            `${API_URL}v1/project/${explanationProjectId}/explanation`,
                                            { method: 'PATCH', headers: {...headers(), 'Content-Type':'application/json'}, body: JSON.stringify({explanation: explanationText.trim()}) }
                                        );
                                    } catch { /* best-effort */ }
                                    setExplanationSaving(false);
                                    setExplanationModal(false);
                                }}
                            >
                                {explanationSaving ? 'Saqlanmoqda...' : 'Yuborish'}
                            </button>
                        </div>
                    </div>
                </div>,
                document.body
            )}

            <DictSelectionPopup lessonId={lesson.id}/>
            <LessonDictionaryDrawer lessonId={lesson.id}/>

            {showCelebration && (
                <CelebrationOverlay
                    score={projectScore}
                    onDone={() => setShowCelebration(false)}
                />
            )}
        </div>
    );
};

export default StudentLessonPage;
