import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './StudentCourses.css';
import StudentCoursePage from '../CoursePage/StudentCoursePage';
import StudentLessonPage from '../LessonPage/StudentLessonPage';
import { API_URL, useHttp, headers, resolveImageUrl } from '../../../../api/search/base';
import axiosInstance from '../../../../api/axiosInstance';
import { useTranslation } from '../../../../i18n/useTranslation';
import { Lock, Award, Search, Map, X } from 'lucide-react';
import AppHeader from '../../../../components/appheader/AppHeader';
import { useIsDemo } from '../../../../context/AuthContext';
import { debtMessage } from '../../../../utils/certificateDebt';
import { ensureSectionIds } from '../../../../utils/lessonSections';
import { DEMO_COURSE_ID } from '../../../../constants/demo';

/* ── tech category visual config ── */
const TECH_META = {
    'html-css':      { label: 'HTML & CSS',     color: '#e34c26', bg: '#fff4f1', icon: '🌐' },
    'javascript':    { label: 'JavaScript',      color: '#f0db4f', bg: '#fffef0', icon: '⚡' },
    'python':        { label: 'Python',          color: '#3776ab', bg: '#f0f7ff', icon: '🐍' },
    'react':         { label: 'React',           color: '#61dafb', bg: '#f0fdff', icon: '⚛️' },
    'sql':           { label: 'SQL',             color: '#336791', bg: '#f0f5ff', icon: '🗄️' },
    'git':           { label: 'Git',             color: '#f05032', bg: '#fff4f0', icon: '🔀' },
    'telegram-bot':  { label: 'Telegram Bot',    color: '#2ca5e0', bg: '#f0faff', icon: '🤖' },
};

const getTechMeta = (slug) => TECH_META[slug] || { label: slug, color: '#6c5ce7', bg: '#f5f3ff', icon: '📦' };

/* Black or white, whichever reads better on a given category color — the
   cert badge's white Award icon was near-invisible on light colors like
   React's #61dafb / JavaScript's #f0db4f without this. */
const readableTextColor = (hexColor) => {
    const h = hexColor.replace('#', '');
    const r = parseInt(h.slice(0, 2), 16) / 255;
    const g = parseInt(h.slice(2, 4), 16) / 255;
    const b = parseInt(h.slice(4, 6), 16) / 255;
    const luminance = 0.299 * r + 0.587 * g + 0.114 * b;
    return luminance > 0.55 ? '#0f0d1e' : '#fff';
};

/* ─── helpers ─── */
// ФИКС: сравниваем id через String() потому что бэкенд может вернуть number, а useParams всегда string
const sameId = (a, b) => String(a) === String(b);

const parseListField = (val) => {
    if (!val) return [];
    if (Array.isArray(val)) return val.map((s) => String(s).trim()).filter(Boolean);
    if (typeof val === 'string') {
        const t = val.trim();
        if (t.startsWith('[')) {
            try { const p = JSON.parse(t); if (Array.isArray(p)) return p.map((s) => String(s).trim()).filter(Boolean); } catch { }
        }
        return t.split(',').map((s) => s.trim()).filter(Boolean);
    }
    return [];
};

const apiToExercise = (ex) => ({
    id: ex.id, title: ex.title || '', description: ex.description || '',
    exercise_type: ex.exercise_type || 'text_input',
    options: parseListField(ex.options), drag_items: parseListField(ex.drag_items),
    is_multiple_select: ex.is_multiple_select || false,
    correct_answers: ex.correct_answers || '', correct_order: ex.correct_order || '',
    hint: ex.hint || '', explanation: ex.explanation || '',
    difficulty_level: ex.difficulty_level || '', points: ex.points || 0, order: ex.order || 0,
});

const apiToLesson = (l, isCompleted = false, exercises = []) => {
    // Prefer sections_json (which includes previewImageUrl enrichment from backend)
    if (l.sections_json) {
        try {
            const sections = JSON.parse(l.sections_json);
            ensureSectionIds(l.id, sections);
            if (exercises.length > 0 && !sections.find(s => s.type === 'exercise')) {
                sections.push({ id: `e${l.id}`, type: 'exercise', label: 'Упражнения', exercises: exercises.map(apiToExercise) });
            }
            // sections_json may not include the project block — append from task fields if missing
            if (!sections.find(s => s.type === 'project') &&
                (l.task_title || l.task_description || l.task_requirements || l.task_technologies || l.task_deadline_days)) {
                sections.push({ id: `p${l.id}`, type: 'project', label: l.task_title || 'Loyiha', description: l.task_description || '', requirements: l.task_requirements || '', techStack: l.task_technologies || '', deadline: l.task_deadline_days || '', previewImage: l.image_url || '' });
            }
            return {
                id: l.id, title: l.title, chapter: l.chapter || '',
                image: l.image_url || '', completed: isCompleted,
                progress_percentage: l.progress_percentage || 0,
                order: l.order || 0, is_published: l.is_published ?? true, sections,
            };
        } catch (_) { }
    }

    const sections = [
        l.text_content ? { id: `t${l.id}`, type: 'text',    label: 'Текст',  html: l.text_content } : null,
        l.code_content ? { id: `c${l.id}`, type: 'code',    label: 'Код',    lang: l.code_language || 'javascript', code: l.code_content } : null,
        l.video_url    ? { id: `v${l.id}`, type: 'video',   label: 'Видео',  videoUrl: l.video_url } : null,
        l.image_url    ? { id: `i${l.id}`, type: 'image',   label: 'Фото',   imgUrl: l.image_url } : null,
        l.file_url     ? { id: `f${l.id}`, type: 'file',    label: 'Файл',   fileName: l.file_url } : null,
        (l.task_title || l.task_description || l.task_requirements || l.task_technologies || l.task_deadline_days)
            ? { id: `p${l.id}`, type: 'project', label: l.task_title || 'Loyiha', description: l.task_description || '', requirements: l.task_requirements || '', techStack: l.task_technologies || '', deadline: l.task_deadline_days || '', previewImage: l.image_url || '' }
            : null,
    ].filter(Boolean);

    if (exercises.length > 0) {
        sections.push({ id: `e${l.id}`, type: 'exercise', label: 'Упражнения', exercises: exercises.map(apiToExercise) });
    }

    return {
        id: l.id, title: l.title, chapter: l.chapter || '',
        image: l.image_url || '', completed: isCompleted,
        progress_percentage: l.progress_percentage || 0,
        order: l.order || 0, is_published: l.is_published ?? true, sections,
    };
};

/* ═══════════════════════════════════════════
   UI helpers
═══════════════════════════════════════════ */
const CardSkeleton = () => (
    <div className="sc-skeleton">
        <div className="sc-skeleton-img" />
        <div className="sc-skeleton-body">
            <div className="sc-skeleton-line w70" />
            <div className="sc-skeleton-line w45" />
            <div className="sc-skeleton-line w90" />
        </div>
    </div>
);

const CourseCard = ({ course, onOpen }) => {
    const lessons      = course.lessons || [];
    const total        = lessons.length > 0 ? lessons.length : (course.lessons_count || 0);
    const completedCnt = lessons.filter((l) => l.completed).length;
    const progress     = lessons.length > 0
        ? Math.round((completedCnt / lessons.length) * 100)
        : Math.round(course.progress_percentage || 0);
    const circumference = 2 * Math.PI * 20;
    const dash = (progress / 100) * circumference;

    // Project totals (course-level loyiha o'rtacha foizi). Backend already
    // returns a default-true is_passed for courses without project-lessons,
    // so the chip just hides itself when there are no projects to grade.
    const proj = course.project_progress || {};
    const hasProjects     = (proj.lessons_with_project || 0) > 0;
    const projectAvg      = Math.round(proj.average_points || 0);
    const projectPassed   = !!proj.is_passed;
    const projectThreshold = proj.threshold || 90;

    // Two different "locked" reasons:
    //   1) Teacher hasn't enrolled the student (existing hard-lock).
    //   2) Prerequisite course's project average is below the gate.
    // Default is_locked to false when the field is missing — old payloads
    // and instructor views don't carry it.
    const enrollLocked = course.is_enrolled === false;
    const prereqLocked = course.is_locked === true;
    const isLocked     = enrollLocked || prereqLocked;
    const prereqAvg    = course.prerequisite_average_points;

    const handleOpen = (e) => {
        if (isLocked) {
            e?.stopPropagation?.();
            return;
        }
        onOpen();
    };

    const lockTitle = enrollLocked
        ? "Bu kursga kirish ruxsati yo'q — o'qituvchidan so'rang"
        : prereqLocked
            ? `Oldingi kursni tugating: loyihalar o'rtachasi ≥${projectThreshold}% bo'lishi kerak`
                + (prereqAvg != null ? ` (hozir ${prereqAvg}%)` : '')
            : undefined;

    return (
        <div
            className={`sc-card${isLocked ? ' sc-card--locked' : ''}${prereqLocked ? ' sc-card--prereq-locked' : ''}`}
            onClick={handleOpen}
            aria-disabled={isLocked || undefined}
            title={lockTitle}
        >
            <div className="sc-card-img-wrap">
                {course.image
                    ? <img src={course.image} alt={course.title} className="sc-card-img" />
                    : <div className="sc-card-img-placeholder"><span>📚</span></div>
                }
                <div className="sc-card-img-overlay" />
                {course.difficulty_level && <span className="sc-card-diff">{course.difficulty_level}</span>}
                {isLocked && (
                    <div className="sc-lock-badge" aria-label="Yopiq">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4">
                            <rect x="4" y="11" width="16" height="10" rx="2" />
                            <path d="M8 11V7a4 4 0 0 1 8 0v4" />
                        </svg>
                        <span>{prereqLocked ? 'Oldingi kursni tugating' : 'Yopiq'}</span>
                    </div>
                )}
                {!isLocked && (
                    <div className="sc-ring-wrap">
                        <svg viewBox="0 0 50 50" className="sc-ring-svg">
                            <circle cx="25" cy="25" r="20" fill="none" stroke="rgba(255,255,255,0.18)" strokeWidth="4" />
                            <circle cx="25" cy="25" r="20" fill="none"
                                stroke={progress === 100 ? '#00d49e' : '#a29bfe'} strokeWidth="4" strokeLinecap="round"
                                strokeDasharray={`${dash} ${circumference}`} transform="rotate(-90 25 25)"
                                style={{ transition: 'stroke-dasharray 0.6s ease' }} />
                        </svg>
                        <span className="sc-ring-label">{progress}%</span>
                    </div>
                )}
            </div>
            <div className="sc-card-body">
                <h3 className="sc-card-title">{course.title}</h3>
                {course.instructor_name && (
                    <p className="sc-card-teacher">
                        <span className="sc-teacher-avatar">{course.instructor_name.charAt(0).toUpperCase()}</span>
                        {course.instructor_name}
                    </p>
                )}
                <div className="sc-card-meta">
                    <span className="sc-meta-pill">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" /></svg>
                        {total} уроков
                    </span>
                    {!isLocked && completedCnt > 0 && (
                        <span className="sc-meta-pill done">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12" /></svg>
                            {completedCnt} пройдено
                        </span>
                    )}
                    {!isLocked && hasProjects && (
                        <span
                            className={`sc-meta-pill sc-meta-pill--proj ${projectPassed ? 'done' : projectAvg > 0 ? 'partial' : ''}`}
                            title={`Loyihalar o'rtachasi: ${projectAvg}% · o'tish chegarasi ≥${projectThreshold}%`}
                        >
                            🎯 Loyiha: {projectAvg}%
                        </span>
                    )}
                </div>

                {/* Prerequisite-locked hint — shows the prior course's score so
                    the student knows exactly what's gating them. */}
                {prereqLocked && (
                    <div className="sc-prereq-hint">
                        <span className="sc-prereq-icon" aria-hidden="true"><Lock size={14} /></span>
                        <span className="sc-prereq-text">
                            Oldingi kurs loyihalari o'rtacha
                            {' '}<strong>{prereqAvg != null ? `${prereqAvg}%` : '—'}</strong>
                            {' '}— kerak ≥<strong>{projectThreshold}%</strong>
                        </span>
                    </div>
                )}
                {!isLocked && (
                    <div className="sc-card-progress">
                        <div className="sc-prog-track">
                            <div className={`sc-prog-fill ${progress === 100 ? 'complete' : ''}`} style={{ width: `${progress}%` }} />
                        </div>
                        <span className="sc-prog-text">{completedCnt}/{total}</span>
                    </div>
                )}
                {isLocked ? (
                    <button
                        className="sc-card-btn sc-card-btn--locked"
                        onClick={(e) => e.stopPropagation()}
                        disabled
                    >
                        {prereqLocked
                            ? <><Lock size={14} aria-hidden="true" /> Oldin kursni tugating (≥{projectThreshold}%)</>
                            : <><Lock size={14} aria-hidden="true" /> Ruxsat kerak</>}
                    </button>
                ) : (
                    <button className="sc-card-btn" onClick={(e) => { e.stopPropagation(); onOpen(); }}>
                        {progress === 100 ? '↺ Повторить' : progress > 0 ? 'Продолжить →' : 'Начать →'}
                    </button>
                )}
            </div>
        </div>
    );
};

const FullLoader = ({ text = 'Загрузка…' }) => (
    <div className="sc-full-loader">
        <div className="sc-spinner"><div className="sc-spinner-ring" /></div>
        <span>{text}</span>
    </div>
);

/* ═══════════════════════════════════════════
   MAIN
═══════════════════════════════════════════ */
/* ── Animated progress ring for the dark courses list ── */
const CxRing = ({ pct, size = 64, stroke = 6, gradId = 'cxGreen', children }) => {
    const r = (size - stroke) / 2, circ = 2 * Math.PI * r;
    const [off, setOff] = useState(circ);
    useEffect(() => {
        const id = setTimeout(() => setOff(circ - circ * (pct || 0) / 100), 200);
        return () => clearTimeout(id);
    }, [pct, circ]);
    return (
        <div className="cx-ring" style={{ width: size, height: size }}>
            <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
                <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,.08)" strokeWidth={stroke} />
                <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={`url(#${gradId})`} strokeWidth={stroke}
                    strokeLinecap="round" strokeDasharray={circ} strokeDashoffset={off}
                    transform={`rotate(-90 ${size / 2} ${size / 2})`}
                    style={{ transition: 'stroke-dashoffset 1.1s cubic-bezier(.2,.75,.25,1)', filter: 'drop-shadow(0 0 5px rgba(54,224,107,.4))' }} />
            </svg>
            <div className="cx-ring-center">{children}</div>
        </div>
    );
};

const StudentCourses = () => {
    const { request }              = useHttp();
    const { lang }                 = useTranslation();
    const isDemo                   = useIsDemo();
    const navigate                 = useNavigate();
    const { courseId, lessonId }   = useParams(); // всегда строки или undefined

    // Определяем вид по URL, не по state
    // /student/courses                        → view = 'list'
    // /student/courses/:courseId              → view = 'course'
    // /student/courses/:courseId/lessons/:id  → view = 'lesson'
    const view = lessonId ? 'lesson' : courseId ? 'course' : 'list';

    const [courses,    setCourses]    = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading,    setLoading]    = useState(true);
    const [filter,     setFilter]     = useState('all');
    const [categoryFilter, setCategoryFilter] = useState('all');
    const [search,     setSearch]     = useState('');
    const [downloadingCategoryId, setDownloadingCategoryId] = useState(null);
    const [certDownloadError, setCertDownloadError] = useState('');
    const [overall, setOverall] = useState(null); // exercises totals for the hero "Mashqlar" ring
    const [lessonsError, setLessonsError] = useState(null); // 'locked' | 'error' | null

    const loadedRef = useRef(new Set());

    const ru = lang === 'ru';

    // Overall exercise stats power the hero "Mashqlar" ring (list view only).
    useEffect(() => {
        if (view !== 'list') return;
        fetch(`${API_URL}v1/student/me/course-stats`, { headers: headers() })
            .then(r => r.ok ? r.json() : null)
            .then(d => setOverall(d?.overall || null))
            .catch(() => {});
    }, [view]);

    /* ── category certificate download ──
       Mirrors DegreeCard.js's handleDownload: an idempotent check-and-earn
       call first (in case the auto-award hook hasn't run yet), then the
       actual PDF as a blob via axiosInstance (useHttp's request() always
       parses JSON, no way to ask it for a Blob). */
    const handleDownloadCategoryCertificate = useCallback(async (cat) => {
        setDownloadingCategoryId(cat.id);
        setCertDownloadError('');
        try {
            await request(
                `${API_URL}v1/achievements/check-and-earn-certificate-category?category_id=${cat.id}`,
                'POST', null, headers()
            ).catch(() => {});

            const res = await axiosInstance.get(
                `${API_URL}v1/achievements/category/${cat.id}/download`,
                { responseType: 'blob', headers: { Accept: 'application/pdf' } }
            );

            const blob = res.data;
            const url  = URL.createObjectURL(blob);
            const a    = document.createElement('a');
            a.href     = url;
            a.download = `${cat.name || 'certificate'}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        } catch (e) {
            console.error(e);
            const debt = await debtMessage(e, lang === 'ru' ? 'ru' : 'uz');
            setCertDownloadError(debt || (lang === 'ru'
                ? 'Не удалось скачать сертификат. Попробуйте позже.'
                : 'Sertifikatni yuklab bo\'lmadi. Birozdan keyin qayta urinib ko\'ring.'));
        } finally {
            setDownloadingCategoryId(null);
        }
    }, [request, lang]);

    /* ── fetch all courses ── */
    const fetchCourses = useCallback(() => {
        setLoading(true);
        request(`${API_URL}v1/courses/?limit=100&t=${Date.now()}`, 'GET', null, headers())
            .then((data) => {
                const list = (Array.isArray(data) ? data : [])
                    .filter((c) => c.is_published !== false)
                    .filter((c) => !isDemo || sameId(c.id, DEMO_COURSE_ID))
                    .map((c) => ({
                        ...c,
                        image: c.image_url || '',
                        studentsCount: c.students_count || 0,
                        progress_percentage: c.progress_percentage || 0,
                        is_enrolled: c.is_enrolled !== false,
                        lessons: [],
                    }));
                // Preserve already-loaded lessons so a slow fetchCourses response
                // does not wipe lessons that loadLessons already populated.
                setCourses((prev) =>
                    list.map((c) => {
                        const existing = prev.find((p) => sameId(p.id, c.id));
                        if (existing && existing.lessons.length > 0) {
                            return { ...c, lessons: existing.lessons, progress_percentage: existing.progress_percentage };
                        }
                        return c;
                    })
                );
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, [request, isDemo]);

    useEffect(() => { fetchCourses(); }, [fetchCourses]);

    /* ── fetch categories so the chip row matches the teacher page ── */
    useEffect(() => {
        request(`${API_URL}v1/categories/`, 'GET', null, headers())
            .then((data) => setCategories(Array.isArray(data) ? data : []))
            .catch(() => setCategories([]));
    }, [request]);

    /* ── load lessons for a course ── */
    const loadLessons = useCallback(async (cId) => {
        // cId — строка из URL; курс в стейте может иметь number id
        if (loadedRef.current.has(String(cId))) return;
        loadedRef.current.add(String(cId));

        const langParam = lang && lang !== 'uz' ? `&lang=${lang}` : '';

        try {
            const raw  = await request(`${API_URL}v1/courses/${cId}/lessons?t=${Date.now()}${langParam}`, 'GET', null, headers());
            const list = (Array.isArray(raw) ? raw : []).filter((l) => l.is_published !== false);

            const built = await Promise.all(
                list.map(async (lesson) => {
                    // progress_percentage counts a project as "done" the moment
                    // it's submitted, regardless of score/status (backend fix
                    // pending — see _calc_lesson_progress). Until then, don't
                    // trust it as a completion signal for project lessons: a
                    // pending/rejected/low-score submission must NOT unlock the
                    // next lesson. is_completed/completed are backed by
                    // LessonCompletion, which is only ever created after the
                    // project passes review, so those stay authoritative.
                    const hasProject = !!(lesson.task_title && String(lesson.task_title).trim());
                    let isDone = lesson.is_completed === true
                        || lesson.completed === true
                        || (!hasProject && lesson.progress_percentage === 100);

                    if (!isDone) {
                        try {
                            // Endpoint returns {lesson_id, is_completed, completed_at} —
                            // not a bare boolean. This fallback silently never fired
                            // before, since `s` (the object) can never equal true/'true'.
                            const s = await request(`${API_URL}v1/lessons/${lesson.id}/is-completed?t=${Date.now()}`, 'GET', null, headers());
                            isDone = s?.is_completed === true;
                        } catch { }
                    }

                    let exercises = [];
                    try {
                        const ex = await request(
                            `${API_URL}v1/courses/${cId}/lessons/${lesson.id}/exercises?t=${Date.now()}${langParam}`,
                            'GET', null, headers()
                        );
                        exercises = (Array.isArray(ex) ? ex : []).filter((e) => e.is_active !== false);
                    } catch { }

                    return apiToLesson(lesson, isDone, exercises);
                })
            );

            const sorted = built.sort((a, b) => (a.order || 0) - (b.order || 0));

            // ФИКС: используем sameId для сравнения, чтобы не зависеть от типа
            setCourses((cs) =>
                cs.map((c) => {
                    if (!sameId(c.id, cId)) return c;
                    const done     = sorted.filter((l) => l.completed).length;
                    const progress = sorted.length > 0 ? Math.round((done / sorted.length) * 100) : 0;
                    return { ...c, lessons: sorted, progress_percentage: progress };
                })
            );
        } catch (e) {
            console.error(e);
            // Keep the loadedRef entry so we don't retry forever; surface a
            // proper "locked / not enrolled" state instead of an endless loader.
            const locked = e?.status === 403 || /ruxsat|access/i.test(e?.message || '');
            setLessonsError(locked ? 'locked' : 'error');
        }
    }, [request, lang]);

    // Грузим уроки когда courseId появляется в URL или меняется язык
    useEffect(() => {
        if (courseId) {
            setLessonsError(null);
            loadedRef.current.delete(String(courseId));
            loadLessons(courseId);
        }
    }, [courseId, lang, loadLessons]);

    /* ── mark complete ── */
    const markComplete = useCallback((lId) => {
        setCourses((cs) => {
            const course = cs.find((c) => sameId(c.id, courseId));
            if (!course) return cs;
            const lesson = course.lessons.find((l) => sameId(l.id, lId));
            if (lesson?.completed) return cs;

            const updated  = course.lessons.map((l) => sameId(l.id, lId) ? { ...l, completed: true } : l);
            const done     = updated.filter((l) => l.completed).length;
            const progress = updated.length > 0 ? Math.round((done / updated.length) * 100) : 0;

            request(`${API_URL}v1/lessons/${lId}/complete`, 'POST', null, headers())
                .catch(() => {
                    setCourses((prev) =>
                        prev.map((c) => {
                            if (!sameId(c.id, courseId)) return c;
                            const rolled = c.lessons.map((l) => sameId(l.id, lId) ? { ...l, completed: false } : l);
                            const d = rolled.filter((l) => l.completed).length;
                            return { ...c, lessons: rolled, progress_percentage: rolled.length > 0 ? Math.round((d / rolled.length) * 100) : 0 };
                        })
                    );
                });

            return cs.map((c) => sameId(c.id, courseId) ? { ...c, lessons: updated, progress_percentage: progress } : c);
        });
    }, [courseId, request]);

    /* ── navigation ── */
    const goToLesson  = (lesson) => navigate(`/student/courses/${courseId}/lessons/${lesson.id}`);
    const goToCourse  = (course) => navigate(`/student/courses/${course.id}`);
    const goToCourses = () => {
        loadedRef.current.clear();
        fetchCourses();
        navigate('/student/courses');
    };

    /* ── derived data ── */
    // ФИКС: sameId для поиска курса и урока
    const currentCourse = courseId ? courses.find((c) => sameId(c.id, courseId)) || null : null;
    const currentLesson = (lessonId && currentCourse)
        ? currentCourse.lessons.find((l) => sameId(l.id, lessonId)) || null
        : null;

    const displayed = courses
        .filter((c) => {
            if (filter === 'inProgress') { const p = c.progress_percentage || 0; return p > 0 && p < 100; }
            if (filter === 'done') return (c.progress_percentage || 0) === 100;
            return true;
        })
        .filter((c) => {
            if (categoryFilter === 'all') return true;
            if (categoryFilter === 'uncategorized') return !c.category_id;
            return c.category_id === categoryFilter;
        })
        .filter((c) => !search || c.title?.toLowerCase().includes(search.toLowerCase()));

    // Hero "current active course": the in-progress course with the most
    // progress; fall back to any started course, then the first course.
    const activeCourse =
        [...courses].filter((c) => { const p = c.progress_percentage || 0; return p > 0 && p < 100; })
            .sort((a, b) => (b.progress_percentage || 0) - (a.progress_percentage || 0))[0]
        || [...courses].filter((c) => (c.progress_percentage || 0) > 0)
            .sort((a, b) => (b.progress_percentage || 0) - (a.progress_percentage || 0))[0]
        || courses[0] || null;

    /* Live category course counts — only count published courses the student
       can actually see, so a chip never claims more than the list shows.
       done_count/is_complete drive the certificate badge below: the same
       100%-progress rule the stats bar already uses for "завершено". */
    const categoryCounts = categories.map((cat) => {
        const catCourses = courses.filter((c) => c.category_id === cat.id);
        const done_count = catCourses.filter((c) => (c.progress_percentage || 0) === 100).length;
        return {
            ...cat,
            live_count: catCourses.length,
            done_count,
            is_complete: catCourses.length > 0 && done_count === catCourses.length,
        };
    }).filter((cat) => cat.live_count > 0);

    /* ══ LESSON VIEW ══ */
    if (view === 'lesson') {
        if (!currentCourse || currentCourse.lessons.length === 0) return <FullLoader text="Загрузка урока…" />;
        if (!currentLesson) return <FullLoader text="Загрузка урока…" />;

        return (
            <StudentLessonPage
                lesson={currentLesson}
                course={currentCourse}
                allLessons={currentCourse.lessons}
                onBack={(target) => {
                    if (target === 'courses') goToCourses();
                    else navigate(`/student/courses/${courseId}`);
                }}
                onNavigate={goToLesson}
                onComplete={() => markComplete(currentLesson.id)}
            />
        );
    }

    /* ══ COURSE VIEW ══ */
    if (view === 'course') {
        // Locked / not-enrolled course → clear dark message (no endless loader).
        if (lessonsError) {
            return (
                <div className="cx-dark">
                    <AppHeader />
                    <div className="cx-course-state">
                        <div className={`cx-course-state-ic ${lessonsError === 'locked' ? 'locked' : 'err'}`}>
                            {lessonsError === 'locked' ? <Lock size={30} /> : '⚠️'}
                        </div>
                        <h3>{lessonsError === 'locked'
                            ? (ru ? 'Курс закрыт' : 'Bu kurs yopiq')
                            : (ru ? 'Не удалось загрузить' : "Yuklab bo'lmadi")}</h3>
                        <p>{lessonsError === 'locked'
                            ? (ru ? 'У вас нет доступа к этому курсу. Обратитесь к преподавателю, чтобы он вас добавил.'
                                  : "Bu kursga kirish ruxsati yo'q. O'qituvchi sizni qo'shishi kerak.")
                            : (ru ? 'Попробуйте позже.' : "Birozdan keyin qayta urinib ko'ring.")}</p>
                        <button className="cx-continue" onClick={goToCourses}>{ru ? 'Все курсы' : 'Barcha kurslar'}</button>
                    </div>
                </div>
            );
        }

        // Still loading — dark loader (course chrome is full-bleed/dark now).
        if (!currentCourse || (currentCourse.lessons.length === 0 && !loadedRef.current.has(String(courseId)))) {
            return (
                <div className="cx-dark">
                    <AppHeader />
                    <div className="cx-course-state">
                        <div className="cx-course-spinner" />
                        <p>{ru ? 'Загрузка уроков…' : 'Darslar yuklanmoqda…'}</p>
                    </div>
                </div>
            );
        }

        return (
            <StudentCoursePage
                course={currentCourse}
                onBack={goToCourses}
                onOpenLesson={goToLesson}
            />
        );
    }

    /* ══ COURSES LIST (dark, full-bleed) ══ */
    const activeImg = activeCourse ? resolveImageUrl(activeCourse.image) : '';
    const activePct = Math.round(activeCourse?.progress_percentage || 0);
    const exPct = overall?.exercises_pct ?? activePct;
    const exCorrect = overall?.exercises_correct ?? 0;
    const exTotal = overall?.exercises_total ?? 0;

    return (
        <div className="cx-dark">
            <AppHeader />
            <svg width="0" height="0" style={{ position: 'absolute' }} aria-hidden="true">
                <defs>
                    <linearGradient id="cxGreen" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0" stopColor="#7ef0a3" /><stop offset="1" stopColor="#2bc45a" />
                    </linearGradient>
                    <linearGradient id="cxBlue" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0" stopColor="#7ef0a3" /><stop offset="1" stopColor="#3b82f6" />
                    </linearGradient>
                </defs>
            </svg>

            <div className="cx-shell">
                {loading ? (
                    <div className="cx-grid">{[1, 2, 3, 4, 5, 6].map((n) => <div key={n} className="cx-card cx-card-skel" />)}</div>
                ) : courses.length === 0 ? (
                    <div className="cx-empty">
                        <div className="cx-empty-icon">📚</div>
                        <h3>{ru ? 'Курсов пока нет' : "Kurslar yo'q"}</h3>
                        <p>{ru ? 'Здесь появятся ваши курсы' : "Bu yerda kurslaringiz paydo bo'ladi"}</p>
                    </div>
                ) : (
                    <>
                        {activeCourse && (
                            <div className="cx-hero cx-rise">
                                <div className="cx-hero-left">
                                    <CxRing pct={activePct} size={168} stroke={8} gradId="cxGreen">
                                        <div className="cx-hero-icon">
                                            {activeImg ? <img src={activeImg} alt="" /> : <span>{(activeCourse.title || '📘')[0]}</span>}
                                        </div>
                                    </CxRing>
                                    <div className="cx-hero-info">
                                        <div className="cx-hero-label">{ru ? 'Текущий активный курс' : 'Joriy faol kurs'}</div>
                                        <div className="cx-hero-title">{activeCourse.title}</div>
                                        <div className="cx-hero-sub">{activePct}% {ru ? 'завершено' : 'bajarildi'}</div>
                                        <div className="cx-hero-bar"><div className="cx-hero-fill" style={{ width: `${activePct}%` }} /></div>
                                    </div>
                                </div>
                                <div className="cx-hero-divider" />
                                <div className="cx-hero-right">
                                    <CxRing pct={exPct} size={92} stroke={7} gradId="cxBlue">
                                        <span className="cx-hero-ex-pct">{exPct}%</span>
                                    </CxRing>
                                    <div className="cx-hero-ex-info">
                                        <div className="cx-hero-ex-title">{ru ? 'Упражнения' : 'Mashqlar'}</div>
                                        <div className="cx-hero-ex-sub">{exCorrect}/{exTotal} {ru ? 'верно' : "to'g'ri"}</div>
                                    </div>
                                    <button className="cx-continue" onClick={() => goToCourse(activeCourse)}>
                                        {ru ? 'Продолжить обучение' : 'Davom etish'}
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* ── toolbar: title + stats + search + roadmap ── */}
                        <div className="cx-toolbar">
                            <div className="cx-toolbar-left">
                                <div className="cx-section-title">{ru ? 'Все курсы' : 'Barcha kurslar'}</div>
                                <div className="cx-stats">
                                    <span className="cx-stat"><b>{courses.length}</b> {ru ? 'курсов' : 'kurs'}</span>
                                    <span className="cx-stat cx-stat-green"><b>{courses.filter((c) => (c.progress_percentage || 0) === 100).length}</b> {ru ? 'завершено' : 'tugallandi'}</span>
                                    <span className="cx-stat cx-stat-violet"><b>{courses.filter((c) => { const p = c.progress_percentage || 0; return p > 0 && p < 100; }).length}</b> {ru ? 'в процессе' : 'jarayonda'}</span>
                                </div>
                            </div>
                            <div className="cx-toolbar-right">
                                <div className="cx-search">
                                    <Search size={16} className="cx-search-icon" />
                                    <input value={search} onChange={(e) => setSearch(e.target.value)}
                                        placeholder={ru ? 'Поиск курса…' : 'Kurs qidirish…'} />
                                    {search && <button className="cx-search-clear" onClick={() => setSearch('')} aria-label="Clear"><X size={14} /></button>}
                                </div>
                                <button className="cx-roadmap" onClick={() => navigate('/student/roadmap')}>
                                    <Map size={16} /> {ru ? 'Карта' : "Yo'l xaritasi"}
                                </button>
                            </div>
                        </div>

                        {/* ── status filter pills ── */}
                        <div className="cx-filters">
                            {[
                                { key: 'all', label: ru ? 'Все' : 'Barchasi' },
                                { key: 'inProgress', label: ru ? 'В процессе' : 'Jarayonda' },
                                { key: 'done', label: ru ? 'Завершённые' : 'Tugallangan' },
                            ].map(({ key, label }) => (
                                <button key={key} className={`cx-pill ${filter === key ? 'active' : ''}`} onClick={() => setFilter(key)}>
                                    {label}
                                </button>
                            ))}
                        </div>

                        {/* ── direction (category) chips with certificate download ── */}
                        {categoryCounts.length > 0 && (
                            <div className="cx-cats">
                                {categoryFilter !== 'all' && (
                                    <button className="cx-cat cx-cat-reset" onClick={() => setCategoryFilter('all')}>
                                        ✕ {ru ? 'Все направления' : "Barcha yo'nalishlar"}
                                    </button>
                                )}
                                {categoryCounts.map((cat) => {
                                    const meta = getTechMeta(cat.slug);
                                    const active = categoryFilter === cat.id;
                                    const catPct = cat.live_count > 0 ? Math.round((cat.done_count / cat.live_count) * 100) : 0;
                                    const isDownloading = downloadingCategoryId === cat.id;
                                    return (
                                        <div key={cat.id} role="button" tabIndex={0}
                                            className={`cx-cat ${active ? 'active' : ''}`}
                                            style={{ '--cat-color': meta.color }}
                                            onClick={() => setCategoryFilter(active ? 'all' : cat.id)}
                                            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setCategoryFilter(active ? 'all' : cat.id); } }}>
                                            <span className="cx-cat-icon">{meta.icon}</span>
                                            <span className="cx-cat-name">{cat.name}</span>
                                            <span className="cx-cat-count">{cat.done_count}/{cat.live_count}</span>
                                            {cat.is_complete ? (
                                                <button className="cx-cat-cert" disabled={isDownloading}
                                                    title={ru ? 'Скачать сертификат' : 'Sertifikatni yuklab olish'}
                                                    onClick={(e) => { e.stopPropagation(); handleDownloadCategoryCertificate(cat); }}>
                                                    {isDownloading ? <span className="cx-cat-spinner" /> : <Award size={13} strokeWidth={2.5} />}
                                                </button>
                                            ) : (
                                                <span className="cx-cat-pct">{catPct}%</span>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                        {certDownloadError && <p className="cx-cat-error">{certDownloadError}</p>}

                        {/* ── grid ── */}
                        {displayed.length === 0 ? (
                            <div className="cx-empty">
                                <div className="cx-empty-icon">🔍</div>
                                <h3>{ru ? 'Ничего не найдено' : 'Hech narsa topilmadi'}</h3>
                                <p>{ru ? 'Попробуйте изменить фильтр или поиск' : "Filtr yoki qidiruvni o'zgartiring"}</p>
                            </div>
                        ) : (
                            <div className="cx-grid">
                                {displayed.map((course, i) => {
                                    const pct = Math.round(course.progress_percentage || 0);
                                    const img = resolveImageUrl(course.image);
                                    const locked = course.is_enrolled === false || course.is_locked === true;
                                    const lessonsCount = course.lessons_count || (course.lessons ? course.lessons.length : 0);
                                    return (
                                        <button key={course.id} className="cx-card cx-rise" style={{ animationDelay: `${i * 0.04}s` }}
                                            onClick={() => goToCourse(course)}>
                                            <div className="cx-card-icon">
                                                {img ? <img src={img} alt="" /> : <span>{(course.title || '📘')[0]}</span>}
                                                {locked && <span className="cx-card-lock"><Lock size={13} /></span>}
                                            </div>
                                            <div className="cx-card-body">
                                                <div className="cx-card-top">
                                                    {course.instructor_name && <span className="cx-card-teacher">{course.instructor_name}</span>}
                                                    {course.difficulty_level && <span className="cx-card-diff">{course.difficulty_level}</span>}
                                                </div>
                                                <div className="cx-card-title">{course.title}</div>
                                                <div className="cx-card-meta">
                                                    {lessonsCount > 0 && <span className="cx-card-lessons">{lessonsCount} {ru ? 'уроков' : 'dars'}</span>}
                                                    <span className="cx-card-pct" style={{ color: pct === 100 ? '#36e06b' : pct > 0 ? '#b7adfb' : '#6b7399' }}>{pct}%</span>
                                                </div>
                                                <div className="cx-card-bar"><div className="cx-card-fill" style={{ width: `${pct}%` }} /></div>
                                            </div>
                                        </button>
                                    );
                                })}
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

export default StudentCourses;