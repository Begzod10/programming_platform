import React, { useState, useEffect } from 'react';
import './StudentCourses.css';
import './Student exercise.css';
import StudentCoursePage from "../CoursePage/StudentCoursePage";
import StudentLessonPage from "../LessonPage/StudentLessonPage";
import { API_URL, useHttp, headers } from '../../../../api/search/base';
import { useTranslation } from 'react-i18next';

// --- Helpers ---
const parseListField = (val) => {
    if (!val) return [];
    if (Array.isArray(val)) return val.map(s => String(s).trim()).filter(Boolean);
    if (typeof val === 'string') {
        const trimmed = val.trim();
        if (trimmed.startsWith('[')) {
            try {
                const parsed = JSON.parse(trimmed);
                if (Array.isArray(parsed)) return parsed.map(s => String(s).trim()).filter(Boolean);
            } catch {}
        }
        return trimmed.split(',').map(s => s.trim()).filter(Boolean);
    }
    return [];
};

const apiToExercise = (ex) => ({
    id: ex.id,
    title: ex.title || '',
    description: ex.description || '',
    exercise_type: ex.exercise_type || 'text_input',
    options: parseListField(ex.options),
    drag_items: parseListField(ex.drag_items),
    is_multiple_select: ex.is_multiple_select || false,
    correct_answers: ex.correct_answers || '',
    correct_order: ex.correct_order || '',
    hint: ex.hint || '',
    explanation: ex.explanation || '',
    difficulty_level: ex.difficulty_level || '',
    points: ex.points || 0,
    order: ex.order || 0,
});

const apiToLesson = (l, isCompleted = false, exercises = []) => {
    const baseSections = [
        l.text_content ? { id: `t${l.id}`, type: 'text', label: 'Текст', html: l.text_content } : null,
        l.code_content ? { id: `c${l.id}`, type: 'code', label: 'Код', lang: l.code_language || 'javascript', code: l.code_content } : null,
        l.video_url ? { id: `v${l.id}`, type: 'video', label: 'Видео', videoUrl: l.video_url } : null,
        l.image_url ? { id: `i${l.id}`, type: 'image', label: 'Фото', imgUrl: l.image_url } : null,
        l.file_url ? { id: `f${l.id}`, type: 'file', label: 'Файл', fileName: l.file_url } : null,
        (l.task_title || l.task_description || l.task_requirements || l.task_technologies || l.task_deadline_days) ? {
            id: `p${l.id}`, type: 'project',
            label: l.task_title || 'Loyiha',
            description: l.task_description || '',
            requirements: l.task_requirements || '',
            techStack: l.task_technologies || '',
            deadline: l.task_deadline_days || '',
        } : null,
    ].filter(Boolean);

    if (exercises.length > 0) {
        baseSections.push({
            id: `e${l.id}`,
            type: 'exercise',
            label: 'Упражнения',
            exercises: exercises.map(apiToExercise),
        });
    }

    return {
        id: l.id,
        title: l.title,
        chapter: l.chapter || '',
        image: l.image_url || '',
        completed: isCompleted,
        order: l.order || 0,
        is_published: l.is_published ?? true,
        sections: baseSections,
    };
};

const getCourseProgress = (course) => {
    if (course.lessons && course.lessons.length > 0) {
        const done = course.lessons.filter(l => l.completed).length;
        return Math.round((done / course.lessons.length) * 100);
    }
    return Math.round(course.progress_percentage || 0);
};

// --- Navigation Persistence Helpers ---
const NAV_KEY = 'student_nav';

const saveNav = (view, courseId = null, lessonId = null) => {
    localStorage.setItem(NAV_KEY, JSON.stringify({ view, courseId, lessonId }));
};

const loadNav = () => {
    try {
        const raw = localStorage.getItem(NAV_KEY);
        return raw ? JSON.parse(raw) : { view: 'courses', courseId: null, lessonId: null };
    } catch {
        return { view: 'courses', courseId: null, lessonId: null };
    }
};

const clearNav = () => localStorage.removeItem(NAV_KEY);

const StudentCourses = () => {
    const { t } = useTranslation();
    const { request } = useHttp();
    
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');

    // Restore navigation state
    const savedNav = loadNav();
    const [view, setView] = useState(savedNav.view);
    const [activeCourse, setActiveCourse] = useState(null);
    const [activeLesson, setActiveLesson] = useState(null);
    const [pendingCourseId, setPendingCourseId] = useState(savedNav.courseId);
    const [pendingLessonId, setPendingLessonId] = useState(savedNav.lessonId);

    const fetchCourses = () => {
        setLoading(true);
        request(`${API_URL}v1/courses/?t=${Date.now()}`, 'GET', null, headers())
            .then(data => {
                const list = Array.isArray(data) ? data : [];
                const mapped = list
                    .filter(c => c.is_published !== false)
                    .map(c => ({
                        ...c,
                        image: c.image_url || '',
                        teacher: c.instructor_name || "O'qituvchi",
                        studentsCount: c.students_count || 0,
                        lessonsCount: c.lessons_count || 0,
                        progress_percentage: c.progress_percentage || 0,
                        enrolled: true,
                        lessons: [],
                    }));
                setCourses(mapped);

                if (pendingCourseId) {
                    const found = mapped.find(c => c.id === pendingCourseId);
                    if (found) {
                        setActiveCourse(found);
                    } else {
                        setView('courses');
                        clearNav();
                    }
                }
            })
            .catch(err => console.error('Courses load error:', err))
            .finally(() => setLoading(false));
    };

    const loadLessons = async (courseId) => {
        try {
            const data = await request(`${API_URL}v1/courses/${courseId}/lessons?t=${Date.now()}`, 'GET', null, headers());
            const list = Array.isArray(data) ? data : [];
            const publishedList = list.filter(l => l.is_published !== false);

            const lessonsBuilt = await Promise.all(publishedList.map(async (lesson) => {
                let isDone = false;
                try {
                    const s = await request(`${API_URL}v1/lessons/${lesson.id}/is-completed?t=${Date.now()}`, 'GET', null, headers());
                    isDone = s === true || s === 'true';
                } catch {}

                let exList = [];
                try {
                    const exData = await request(`${API_URL}v1/courses/${courseId}/lessons/${lesson.id}/exercises?t=${Date.now()}`, 'GET', null, headers());
                    exList = Array.isArray(exData) ? exData.filter(e => e.is_active !== false) : [];
                } catch {}

                return apiToLesson(lesson, isDone, exList);
            }));

            const sorted = lessonsBuilt.sort((a, b) => (a.order || 0) - (b.order || 0));
            setCourses(cs => cs.map(c => c.id === courseId ? { ...c, lessons: sorted } : c));

            if (pendingLessonId) {
                const foundLesson = sorted.find(l => l.id === pendingLessonId);
                if (foundLesson) {
                    setActiveLesson(foundLesson);
                } else {
                    setView('course');
                    saveNav('course', courseId, null);
                }
                setPendingLessonId(null);
            }
        } catch (e) {
            console.error('Lessons load error:', e);
        }
    };

    useEffect(() => {
        fetchCourses();
    }, []);

    useEffect(() => {
        if (activeCourse && (view === 'course' || view === 'lesson')) {
            loadLessons(activeCourse.id);
        }
    }, [activeCourse?.id]);

    const markComplete = (lessonId) => {
        request(`${API_URL}v1/lessons/${lessonId}/complete`, 'POST', null, headers())
            .then(() => {
                setCourses(cs => cs.map(c => {
                    if (c.id !== activeCourse?.id) return c;
                    return {
                        ...c,
                        lessons: c.lessons.map(l => l.id === lessonId ? { ...l, completed: true } : l),
                    };
                }));
            })
            .catch(err => console.error('Complete error:', err));
    };

    // Navigation Wrappers
    const goToLesson = (lesson) => {
        setActiveLesson(lesson);
        setView('lesson');
        saveNav('lesson', activeCourse?.id || pendingCourseId, lesson.id);
    };

    const goToCourse = (course) => {
        setActiveCourse(course);
        setView('course');
        setPendingCourseId(null);
        saveNav('course', course.id, null);
        loadLessons(course.id);
    };

    const goToCourses = () => {
        setView('courses');
        setActiveCourse(null);
        setActiveLesson(null);
        setPendingCourseId(null);
        setPendingLessonId(null);
        clearNav();
        fetchCourses();
    };

    const currentCourse = activeCourse ? courses.find(c => c.id === activeCourse.id) || activeCourse : null;
    
    const filtered = courses.filter(c => {
        if (filter === 'enrolled') return c.enrolled;
        if (filter === 'available') return !c.enrolled;
        return true;
    });

    // --- Render Logic ---

    if (view === 'lesson' && (activeLesson || pendingLessonId) && currentCourse) {
        const freshLesson = activeLesson 
            ? (currentCourse.lessons.find(l => l.id === activeLesson.id) || activeLesson)
            : null;

        if (!freshLesson) {
            return <div className="sc-loader">{t('loading_lesson')}...</div>;
        }

        return (
            <StudentLessonPage
                lesson={freshLesson}
                course={currentCourse}
                allLessons={currentCourse.lessons}
                onBack={(target) => {
                    if (target === 'courses') goToCourses();
                    else {
                        setView('course');
                        setActiveLesson(null);
                        saveNav('course', currentCourse.id, null);
                    }
                }}
                onNavigate={(l) => goToLesson(l)}
                onComplete={() => markComplete(freshLesson.id)}
            />
        );
    }

    if (view === 'course' && currentCourse) {
        return (
            <StudentCoursePage
                course={currentCourse}
                onBack={goToCourses}
                onOpenLesson={goToLesson}
            />
        );
    }

    return (
        <div className="sc-container item-fade-in">
            <div className="sc-header">
                <div>
                    <h2>{t('my_courses')}</h2>
                    <p className="sc-subtitle">{t('explore_courses_subtitle')}</p>
                </div>
                <div className="sc-filters">
                    {[['all', t('all_courses')], ['enrolled', t('my_courses')], ['available', t('available_courses')]].map(([v, l]) => (
                        <button key={v} className={`sc-filter-btn ${filter === v ? 'active' : ''}`}
                            onClick={() => setFilter(v)}>{l}</button>
                    ))}
                </div>
            </div>

            {loading ? (
                <div className="sc-loader">{t('loading_courses')}</div>
            ) : (
                <div className="sc-courses-grid">
                    {filtered.map(course => {
                        const progress = getCourseProgress(course);
                        const completedCount = course.lessons.length > 0
                            ? course.lessons.filter(l => l.completed).length
                            : Math.round((progress / 100) * (course.lessonsCount || 0));

                        return (
                            <div key={course.id} className={`sc-course-card ${course.enrolled ? 'enrolled' : ''}`}
                                onClick={() => { if (course.enrolled) goToCourse(course); }}>
                                <div className="sc-course-preview">
                                    <img src={course.image} alt={course.title} />
                                    {course.enrolled && (
                                        <div className="sc-progress-badge">
                                            <div className="sc-progress-circle">
                                                <svg viewBox="0 0 36 36">
                                                    <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                                        fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="3" />
                                                    <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                                        fill="none" stroke="#fff" strokeWidth="3"
                                                        strokeDasharray={`${progress}, 100`} />
                                                </svg>
                                                <span className="sc-progress-text">{progress}%</span>
                                            </div>
                                        </div>
                                    )}
                                </div>
                                <div className="sc-course-info">
                                    <h3>{course.title}</h3>
                                    <p className="sc-teacher">👨‍🏫 {course.teacher}</p>
                                    <div className="sc-course-stats">
                                        <span className="sc-stat">📚 {course.lessonsCount || course.lessons.length} {t('lessons')}</span>
                                        {course.enrolled && progress > 0 && (
                                            <span className="sc-stat completed">✓ {completedCount} {t('completed')}</span>
                                        )}
                                    </div>
                                    {course.enrolled ? (
                                        <>
                                            <div className="sc-progress-bar-wrap">
                                                <div className="sc-progress-bar">
                                                    <div className="sc-progress-fill" style={{ width: `${progress}%` }} />
                                                </div>
                                            </div>
                                            <button className="sc-open-btn" onClick={e => { e.stopPropagation(); goToCourse(course); }}>
                                                {progress === 100 ? `✓ ${t('review')}` : `${t('continue')} →`}
                                            </button>
                                        </>
                                    ) : (
                                        <button className="sc-enroll-btn" onClick={e => e.stopPropagation()}>
                                            {t('enroll')}
                                        </button>
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

export default StudentCourses;