import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import './StudentCourses.css';
import StudentCoursePage from '../CoursePage/StudentCoursePage';
import StudentLessonPage from '../LessonPage/StudentLessonPage';
import { API_URL, useHttp, headers } from '../../../../api/search/base';
import { useTranslation } from '../../../../i18n/useTranslation';

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
            if (exercises.length > 0) {
                sections.push({ id: `e${l.id}`, type: 'exercise', label: 'Упражнения', exercises: exercises.map(apiToExercise) });
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
            ? { id: `p${l.id}`, type: 'project', label: l.task_title || 'Loyiha', description: l.task_description || '', requirements: l.task_requirements || '', techStack: l.task_technologies || '', deadline: l.task_deadline_days || '' }
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
                        <span className="sc-prereq-icon">🔒</span>
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
                            ? `🔒 Oldin kursni tugating (≥${projectThreshold}%)`
                            : '🔒 Ruxsat kerak'}
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
const StudentCourses = () => {
    const { request }              = useHttp();
    const { lang }                 = useTranslation();
    const navigate                 = useNavigate();
    const location                 = useLocation();
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

    const loadedRef = useRef(new Set());

    /* ── fetch all courses ── */
    const fetchCourses = useCallback(() => {
        setLoading(true);
        request(`${API_URL}v1/courses/?limit=100&t=${Date.now()}`, 'GET', null, headers())
            .then((data) => {
                const list = (Array.isArray(data) ? data : [])
                    .filter((c) => c.is_published !== false)
                    .map((c) => ({
                        ...c,
                        image: c.image_url || '',
                        studentsCount: c.students_count || 0,
                        progress_percentage: c.progress_percentage || 0,
                        is_enrolled: c.is_enrolled !== false,
                        lessons: [],
                    }));
                loadedRef.current.clear();
                setCourses(list);
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []); // eslint-disable-line

    useEffect(() => { fetchCourses(); }, []); // eslint-disable-line

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
                    let isDone = lesson.is_completed === true
                        || lesson.completed === true
                        || lesson.progress_percentage === 100;

                    if (!isDone) {
                        try {
                            const s = await request(`${API_URL}v1/lessons/${lesson.id}/is-completed?t=${Date.now()}`, 'GET', null, headers());
                            isDone = s === true || s === 'true';
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
            loadedRef.current.delete(String(cId));
        }
    }, [request, lang]);

    // Грузим уроки когда courseId появляется в URL или меняется язык
    useEffect(() => {
        if (courseId) {
            loadedRef.current.delete(String(courseId));
            loadLessons(courseId);
        }
    }, [courseId, lang]); // eslint-disable-line

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

    /* Live category course counts — only count published courses the student
       can actually see, so a chip never claims more than the list shows. */
    const categoryCounts = categories.map((cat) => ({
        ...cat,
        live_count: courses.filter((c) => c.category_id === cat.id).length,
    })).filter((cat) => cat.live_count > 0);
    const uncategorizedCount = courses.filter((c) => !c.category_id).length;

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
        // Курс нашли но уроки ещё грузятся — показываем лоадер
        if (!currentCourse) return <FullLoader text="Загрузка курса…" />;

        // Уроки грузятся — ждём (loadedRef ещё не добавил courseId, значит запрос в процессе)
        if (currentCourse.lessons.length === 0 && !loadedRef.current.has(String(courseId))) {
            return <FullLoader text="Загрузка уроков…" />;
        }

        return (
            <StudentCoursePage
                course={currentCourse}
                onBack={goToCourses}
                onOpenLesson={goToLesson}
            />
        );
    }

    /* ══ COURSES LIST ══ */
    return (
        <div className="sc-root">
            <div className="sc-header">
                <div className="sc-header-left">
                    <h2 className="sc-title">Мои курсы</h2>
                    <p className="sc-subtitle">Продолжайте обучение там, где остановились</p>
                </div>
                <div className="sc-header-right">
                    <button
                        className="sc-filter"
                        style={{ borderColor: '#6c5ce7', color: '#6c5ce7', background: '#f5f3ff' }}
                        onClick={() => navigate('/student/roadmap')}
                    >
                        🗺️ Карта обучения
                    </button>
                    <div className="sc-search-wrap">
                        <svg className="sc-search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                            <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
                        </svg>
                        <input className="sc-search" placeholder="Поиск курса…" value={search} onChange={(e) => setSearch(e.target.value)} />
                        {search && <button className="sc-search-clear" onClick={() => setSearch('')}>✕</button>}
                    </div>
                    <div className="sc-filters">
                        {[{ key: 'all', label: 'Все' }, { key: 'inProgress', label: 'В процессе' }, { key: 'done', label: 'Завершённые' }]
                            .map(({ key, label }) => (
                                <button key={key} className={`sc-filter ${filter === key ? 'active' : ''}`} onClick={() => setFilter(key)}>
                                    {label}
                                </button>
                            ))}
                    </div>
                </div>
            </div>

            {!loading && categoryCounts.length > 0 && (
                <div className="sc-category-bar">
                    <span className="sc-category-label">Категория:</span>
                    <button
                        className={`sc-category-chip ${categoryFilter === 'all' ? 'active' : ''}`}
                        onClick={() => setCategoryFilter('all')}
                    >Все</button>
                    {categoryCounts.map((cat) => (
                        <button
                            key={cat.id}
                            className={`sc-category-chip ${categoryFilter === cat.id ? 'active' : ''}`}
                            onClick={() => setCategoryFilter(categoryFilter === cat.id ? 'all' : cat.id)}
                        >
                            {cat.name}
                            <span className="sc-category-count">{cat.live_count}</span>
                        </button>
                    ))}
                    {uncategorizedCount > 0 && (
                        <button
                            className={`sc-category-chip ${categoryFilter === 'uncategorized' ? 'active' : ''}`}
                            onClick={() => setCategoryFilter(categoryFilter === 'uncategorized' ? 'all' : 'uncategorized')}
                        >
                            Без категории
                            <span className="sc-category-count">{uncategorizedCount}</span>
                        </button>
                    )}
                </div>
            )}

            {!loading && courses.length > 0 && (
                <div className="sc-stats-bar">
                    <div className="sc-stat-item"><span className="sc-stat-num">{courses.length}</span><span className="sc-stat-text">курсов</span></div>
                    <div className="sc-stat-divider" />
                    <div className="sc-stat-item">
                        <span className="sc-stat-num">{courses.filter((c) => (c.progress_percentage || 0) === 100).length}</span>
                        <span className="sc-stat-text">завершено</span>
                    </div>
                    <div className="sc-stat-divider" />
                    <div className="sc-stat-item">
                        <span className="sc-stat-num">{courses.filter((c) => { const p = c.progress_percentage || 0; return p > 0 && p < 100; }).length}</span>
                        <span className="sc-stat-text">в процессе</span>
                    </div>
                </div>
            )}

            {loading ? (
                <div className="sc-grid">{[1, 2, 3, 4, 5, 6].map((n) => <CardSkeleton key={n} />)}</div>
            ) : displayed.length === 0 ? (
                <div className="sc-empty">
                    <div className="sc-empty-icon">{search ? '🔍' : '📚'}</div>
                    <h3 className="sc-empty-title">{search ? 'Ничего не найдено' : 'Курсов пока нет'}</h3>
                    <p className="sc-empty-sub">{search ? `По запросу «${search}» курсов не найдено` : 'Здесь появятся ваши курсы'}</p>
                    {search && <button className="sc-empty-reset" onClick={() => setSearch('')}>Сбросить поиск</button>}
                </div>
            ) : (
                <div className="sc-grid">
                    {displayed.map((course) => (
                        <CourseCard key={course.id} course={course} onOpen={() => goToCourse(course)} />
                    ))}
                </div>
            )}
        </div>
    );
};

export default StudentCourses;