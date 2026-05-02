import React, {useState, useEffect} from 'react';
import './StudentCourses.css';
import './Student exercise.css'
import StudentCoursePage from "../CoursePage/StudentCoursePage";
import StudentLessonPage from "../LessonPage/StudentLessonPage";
import {API_URL, useHttp, headers, resolveImageUrl} from '../../../../api/search/base';

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
    id:                 ex.id,
    title:              ex.title              || '',
    description:        ex.description        || '',
    exercise_type:      ex.exercise_type      || 'text_input',
    options:            parseListField(ex.options),
    drag_items:         parseListField(ex.drag_items),
    is_multiple_select: ex.is_multiple_select  || false,
    correct_answers:    ex.correct_answers     || '',
    correct_order:      ex.correct_order       || '',
    hint:               ex.hint                || '',
    explanation:        ex.explanation         || '',
    difficulty_level:   ex.difficulty_level   || '',
    points:             ex.points              || 0,
    order:              ex.order               || 0,
});

const apiToLesson = (l, isCompleted = false, exercises = []) => {
    const baseSections = [
        l.text_content ? {id: `t${l.id}`, type: 'text',  label: 'Текст', html: l.text_content} : null,
        l.code_content ? {id: `c${l.id}`, type: 'code',  label: 'Код',   lang: l.code_language || 'javascript', code: l.code_content} : null,
        l.video_url    ? {id: `v${l.id}`, type: 'video', label: 'Видео', videoUrl: l.video_url} : null,
        l.image_url    ? {id: `i${l.id}`, type: 'image', label: 'Фото',  imgUrl: l.image_url} : null,
        l.file_url     ? {id: `f${l.id}`, type: 'file',  label: 'Файл',  fileName: l.file_url} : null,
        (l.task_title || l.task_description || l.task_requirements || l.task_technologies || l.task_deadline_days) ? {
            id: `p${l.id}`, type: 'project',
            label:        l.task_title        || 'Loyiha',
            description:  l.task_description  || '',
            requirements: l.task_requirements || '',
            techStack:    l.task_technologies || '',
            deadline:     l.task_deadline_days || '',
        } : null,
    ].filter(Boolean);

    if (exercises.length > 0) {
        baseSections.push({
            id:        `e${l.id}`,
            type:      'exercise',
            label:     'Упражнения',
            exercises: exercises.map(apiToExercise),
        });
    }

    return {
        id:           l.id,
        title:        l.title,
        chapter:      l.chapter    || '',
        image:        l.image_url  || '',
        completed:    isCompleted,
        order:        l.order      || 0,
        is_published: l.is_published ?? true,
        sections:     baseSections,
    };
};

const getCourseProgress = (course) => {
    if (course.lessons && course.lessons.length > 0) {
        const done = course.lessons.filter(l => l.completed).length;
        return Math.round((done / course.lessons.length) * 100);
    }
    return Math.round(course.progress_percentage || 0);
};

const StudentCourses = () => {
    const {request} = useHttp();
    const [courses,       setCourses]      = useState([]);
    const [loading,       setLoading]      = useState(true);
    const [filter,        setFilter]       = useState('all');
    const [view,          setView]         = useState('courses');
    const [activeCourse,  setActiveCourse] = useState(null);
    const [activeLesson,  setActiveLesson] = useState(null);

    const fetchCourses = () => {
        setLoading(true);
        request(`${API_URL}v1/courses/?t=${Date.now()}`, 'GET', null, headers())
            .then(data => {
                const list = Array.isArray(data) ? data : [];
                setCourses(list
                    // Фильтруем неопубликованные курсы
                    .filter(c => c.is_published !== false)
                    .map(c => ({
                        ...c,
                        image:               c.image_url           || '',
                        teacher:             c.instructor_name     || "O'qituvchi",
                        studentsCount:       c.students_count      || 0,
                        lessonsCount:        c.lessons_count       || 0,
                        progress_percentage: c.progress_percentage || 0,
                        enrolled:            true,
                        lessons:             [],
                    })));
            })
            .catch(err => console.error('Courses load error:', err))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        fetchCourses();
    }, []);

    const loadLessons = async (courseId) => {
        try {
            const data = await request(`${API_URL}v1/courses/${courseId}/lessons?t=${Date.now()}`, 'GET', null, headers());
            const list = Array.isArray(data) ? data : [];

            // Фильтруем неопубликованные уроки сразу
            const publishedList = list.filter(l => l.is_published !== false);

            const lessonsBuilt = await Promise.all(publishedList.map(async (lesson) => {
                let isDone = false;
                try {
                    const s = await request(`${API_URL}v1/lessons/${lesson.id}/is-completed?t=${Date.now()}`, 'GET', null, headers());
                    isDone = s === true || s === 'true';
                } catch {}

                let exList = [];
                try {
                    const exData = await request(
                        `${API_URL}v1/courses/${courseId}/lessons/${lesson.id}/exercises?t=${Date.now()}`,
                        'GET', null, headers()
                    );
                    exList = Array.isArray(exData)
                        ? exData.filter(e => e.is_active !== false)
                        : [];
                } catch {}

                return apiToLesson(lesson, isDone, exList);
            }));

            const sorted = lessonsBuilt.sort((a, b) => (a.order || 0) - (b.order || 0));
            setCourses(cs => cs.map(c => c.id === courseId ? {...c, lessons: sorted} : c));
        } catch (e) {
            console.error('Lessons load error:', e);
        }
    };

    const markComplete = (lessonId) => {
        request(`${API_URL}v1/lessons/${lessonId}/complete`, 'POST', null, headers())
            .then(() => {
                setCourses(cs => cs.map(c => {
                    if (c.id !== activeCourse?.id) return c;
                    return {
                        ...c,
                        lessons: c.lessons.map(l => l.id === lessonId ? {...l, completed: true} : l),
                    };
                }));
            })
            .catch(err => console.error('Complete error:', err));
    };

    const currentCourse = activeCourse ? courses.find(c => c.id === activeCourse.id) || activeCourse : null;
    const filtered = courses.filter(c => {
        if (filter === 'enrolled')  return c.enrolled;
        if (filter === 'available') return !c.enrolled;
        return true;
    });

    /* ── Lesson view ── */
    if (view === 'lesson' && activeLesson && currentCourse) {
        const freshLesson = currentCourse.lessons.find(l => l.id === activeLesson.id) || activeLesson;
        return (
            <StudentLessonPage
                lesson={freshLesson}
                course={currentCourse}
                allLessons={currentCourse.lessons}
                onBack={(target) => {
                    if (target === 'courses') {
                        setView('courses');
                        setActiveCourse(null);
                        fetchCourses();
                    }
                    else setView('course');
                    setActiveLesson(null);
                }}
                onNavigate={(l) => setActiveLesson(l)}
                onComplete={() => markComplete(freshLesson.id)}
            />
        );
    }

    /* ── Course view ── */
    if (view === 'course' && currentCourse) {
        return (
            <StudentCoursePage
                course={currentCourse}
                onBack={() => {
                    setView('courses');
                    setActiveCourse(null);
                    fetchCourses();
                }}
                onOpenLesson={(lesson) => { setActiveLesson(lesson); setView('lesson'); }}
            />
        );
    }

    /* ── Courses list ── */
    return (
        <div className="sc-container item-fade-in">
            <div className="sc-header">
                <div>
                    <h2>Мои курсы</h2>
                    <p className="sc-subtitle">Изучайте курсы и развивайте свои навыки</p>
                </div>
                <div className="sc-filters">
                    {[['all','Все курсы'],['enrolled','Мои курсы'],['available','Доступные']].map(([v, l]) => (
                        <button key={v} className={`sc-filter-btn ${filter === v ? 'active' : ''}`}
                            onClick={() => setFilter(v)}>{l}</button>
                    ))}
                </div>
            </div>

            {loading ? (
                <div style={{textAlign:'center', padding:'60px', color:'rgba(26,26,46,0.4)'}}>Загрузка курсов...</div>
            ) : (
                <div className="sc-courses-grid">
                    {filtered.map(course => {
                        const progress = getCourseProgress(course);
                        const completedCount = course.lessons.length > 0
                            ? course.lessons.filter(l => l.completed).length
                            : Math.round((progress / 100) * (course.lessonsCount || 0));

                        return (
                            <div key={course.id} className={`sc-course-card ${course.enrolled ? 'enrolled' : ''}`}
                                onClick={() => {
                                    if (course.enrolled) {
                                        setActiveCourse(course);
                                        setView('course');
                                        loadLessons(course.id);
                                    }
                                }}>
                                <div className="sc-course-preview">
                                    <img src={resolveImageUrl(course.image)} alt={course.title}/>
                                    {course.enrolled && (
                                        <div className="sc-progress-badge">
                                            <div className="sc-progress-circle">
                                                <svg viewBox="0 0 36 36">
                                                    <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                                        fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="3"/>
                                                    <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                                        fill="none" stroke="#fff" strokeWidth="3"
                                                        strokeDasharray={`${progress}, 100`}/>
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
                                        <span className="sc-stat">📚 {course.lessonsCount || course.lessons.length} уроков</span>
                                        {course.enrolled && progress > 0 && (
                                            <span className="sc-stat completed">✓ {completedCount} пройдено</span>
                                        )}
                                    </div>
                                    {course.enrolled ? (<>
                                        <div className="sc-progress-bar-wrap">
                                            <div className="sc-progress-bar">
                                                <div className="sc-progress-fill" style={{width: `${progress}%`}}/>
                                            </div>
                                        </div>
                                        <button className="sc-open-btn" onClick={e => {
                                            e.stopPropagation();
                                            setActiveCourse(course);
                                            setView('course');
                                            loadLessons(course.id);
                                        }}>
                                            {progress === 100 ? '✓ Пересмотреть' : 'Продолжить →'}
                                        </button>
                                    </>) : (
                                        <button className="sc-enroll-btn" onClick={e => e.stopPropagation()}>
                                            Записаться
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