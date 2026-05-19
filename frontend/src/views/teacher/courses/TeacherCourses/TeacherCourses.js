import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import './TeacherCourses.css';
import LessonEditorPage from '../LessonEditor/LessonEditor';
import CourseDetailPage from '../CourseModal/CourseModal';
import LessonPage from '../LessonPage/LessonPage';
import { API_URL, useHttp, headers } from '../../../../api/search/base';

const INITIAL_CHAPTERS = ['Basic', 'Advanced', 'Test'];

// ФИКС: сравниваем id через String() — бэкенд может вернуть number, useParams всегда string
const sameId = (a, b) => String(a) === String(b);

/* ─── helpers (без изменений) ─── */
const parseToComma = (val) => {
    if (!val) return '';
    if (Array.isArray(val)) return val.join(',');
    if (typeof val === 'string') {
        const trimmed = val.trim();
        if (trimmed.startsWith('[')) {
            try { const p = JSON.parse(trimmed); if (Array.isArray(p)) return p.join(','); } catch (_) { }
        }
        return trimmed;
    }
    return '';
};
const commaToJsonArray = (str) => {
    if (!str) return null;
    const arr = str.split(',').map(s => s.trim()).filter(Boolean);
    return arr.length === 0 ? null : JSON.stringify(arr);
};
const apiToExercise = (e) => ({
    _localId: e.id, id: e.id, title: e.title || '', description: e.description || '',
    exercise_type: e.exercise_type || 'text_input', correct_answers: e.correct_answers || '',
    drag_items: parseToComma(e.drag_items), correct_order: parseToComma(e.correct_order),
    options: parseToComma(e.options), is_multiple_select: e.is_multiple_select || false,
    expected_answer: e.expected_answer || '', hint: e.hint || '', explanation: e.explanation || '',
    difficulty_level: e.difficulty_level || 'Easy', points: e.points || 10, order: e.order || 0,
});
const exerciseToApi = (ex) => ({
    title: ex.title, description: ex.description, exercise_type: ex.exercise_type,
    correct_answers: ex.correct_answers || null, drag_items: commaToJsonArray(ex.drag_items),
    correct_order: commaToJsonArray(ex.correct_order), options: commaToJsonArray(ex.options),
    is_multiple_select: ex.is_multiple_select || false, expected_answer: ex.expected_answer || null,
    hint: ex.hint || null, explanation: ex.explanation || null,
    difficulty_level: ex.difficulty_level || 'Easy', points: ex.points || 10, order: ex.order || 0,
});
const apiToLesson = (l) => {
    if (l.sections_json) {
        try {
            const sections = JSON.parse(l.sections_json);
            return { id: l.id, title: l.title, chapter: l.chapter || '', image: l.image_url || '', completed: false, order: l.order || 0, is_published: l.is_published || false, sections };
        } catch (_) { }
    }
    return {
        id: l.id, title: l.title, chapter: l.chapter || '', image: l.image_url || '',
        completed: false, order: l.order || 0, is_published: l.is_published || false,
        sections: [
            l.text_content ? { id: `t${l.id}`, type: 'text',    label: 'Текст',  html: l.text_content } : null,
            l.code_content ? { id: `c${l.id}`, type: 'code',    label: 'Код',    lang: l.code_language || 'javascript', code: l.code_content } : null,
            l.video_url    ? { id: `v${l.id}`, type: 'video',   label: 'Видео',  videoUrl: l.video_url } : null,
            l.image_url    ? { id: `i${l.id}`, type: 'image',   label: 'Фото',   imgUrl: l.image_url } : null,
            l.file_url     ? { id: `f${l.id}`, type: 'file',    label: 'Файл',   fileName: l.file_url } : null,
            (l.task_title || l.task_description) ? { id: `p${l.id}`, type: 'project', label: l.task_title || 'Loyiha', description: l.task_description || '', requirements: l.task_requirements || '', techStack: l.task_technologies || '', deadline: l.task_deadline_days || '' } : null,
            Array.isArray(l.exercises) ? { id: `e${l.id}`, type: 'exercise', label: 'Упражнения', exercises: l.exercises.map(apiToExercise) } : null,
        ].filter(Boolean),
    };
};
const lessonToApi = (form) => {
    const project = form.sections?.find(s => s.type === 'project');
    const mashq   = form.sections?.find(s => s.type === 'mashq');
    return {
        title: form.title, order: Number(form.order) || 0, chapter: form.chapter || '',
        image_url: form.image || '',
        sections_json: JSON.stringify(form.sections || []),
        text_content: form.sections?.find(s => s.type === 'text')?.html || '',
        code_content: form.sections?.find(s => s.type === 'code')?.code || '',
        code_language: form.sections?.find(s => s.type === 'code')?.lang || '',
        video_url: form.sections?.find(s => s.type === 'video')?.videoUrl || '',
        file_url: form.sections?.find(s => s.type === 'file')?.fileName || '',
        mashq_type: mashq?.mashqType || null, mashq_question: mashq?.question || null,
        mashq_answer: mashq?.answer || null, mashq_words: mashq?.words?.join(',') || null,
        task_title: project ? (project.label || 'Loyiha') : null,
        task_description: project?.description || null, task_requirements: project?.requirements || null,
        task_technologies: project?.techStack || null,
        task_deadline_days: project?.deadline ? Number(project.deadline) : null,
    };
};

/* ─── Modals ─── */
const ConfirmModal = ({ title, text, onConfirm, onClose }) => {
    useEffect(() => {
        const h = e => { if (e.key === 'Escape') onClose(); };
        document.addEventListener('keydown', h);
        return () => document.removeEventListener('keydown', h);
    }, [onClose]);
    return ReactDOM.createPortal(
        <div className="tc-modal-overlay" onClick={onClose}>
            <div className="tc-confirm" onClick={e => e.stopPropagation()}>
                <span className="tc-confirm-icon">🗑️</span>
                <h4>{title}</h4>
                {text && <p>{text}</p>}
                <div className="tc-confirm-actions">
                    <button className="tc-cancel-btn" onClick={onClose}>Отмена</button>
                    <button className="tc-delete-btn" onClick={onConfirm}>🗑️ Удалить</button>
                </div>
            </div>
        </div>,
        document.body
    );
};
const ChaptersModal = ({ chapters, onSave, onClose }) => {
    const [list, setList] = useState([...chapters]);
    const [input, setInput] = useState('');
    useEffect(() => {
        const h = e => { if (e.key === 'Escape') onClose(); };
        document.addEventListener('keydown', h);
        return () => document.removeEventListener('keydown', h);
    }, [onClose]);
    const add = () => { const v = input.trim(); if (v && !list.includes(v)) { setList(l => [...l, v]); setInput(''); } };
    return ReactDOM.createPortal(
        <div className="tc-modal-overlay" onClick={onClose}>
            <div className="tc-modal" onClick={e => e.stopPropagation()}>
                <h3>📚 Управление разделами</h3>
                <div className="tc-chapter-list">
                    {list.length === 0 && <p className="tc-chapter-empty">Разделов пока нет</p>}
                    {list.map((ch, i) => (
                        <div key={i} className="tc-chapter-item">
                            <span>📁 {ch}</span>
                            <button className="tc-chapter-item-del" onClick={() => setList(l => l.filter((_, j) => j !== i))}>✕</button>
                        </div>
                    ))}
                </div>
                <div className="tc-chapter-add-row">
                    <input placeholder="Basic, Advanced..." value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && add()} />
                    <button className="tc-chapter-add-btn" onClick={add}>+ Добавить</button>
                </div>
                <div className="tc-modal-actions">
                    <button className="tc-cancel-btn" onClick={onClose}>Отмена</button>
                    <button className="tc-save-btn" onClick={() => { onSave(list); onClose(); }}>Сохранить</button>
                </div>
            </div>
        </div>,
        document.body
    );
};

/* ═══════════════════════════════════════════
   MAIN
═══════════════════════════════════════════ */
const TeacherCourses = () => {
    const { request }            = useHttp();
    const navigate               = useNavigate();
    const location               = useLocation();
    const { courseId, lessonId } = useParams();

    // ФИКС: определяем вид строго по pathname, не по lessonId значению
    // /teacher/courses                                   → 'list'
    // /teacher/courses/:courseId                         → 'course'
    // /teacher/courses/:courseId/lessons/new             → 'new'
    // /teacher/courses/:courseId/lessons/:id/edit        → 'edit'
    // /teacher/courses/:courseId/lessons/:id             → 'lesson'
    const path = location.pathname;
    const isNew  = path.endsWith('/lessons/new');
    const isEdit = !isNew && path.endsWith('/edit');
    const view   = !courseId ? 'list'
        : isNew              ? 'new'
        : isEdit             ? 'edit'
        : lessonId           ? 'lesson'
        :                      'course';

    const [courses,          setCourses]          = useState([]);
    const [chapters,         setChapters]         = useState(INITIAL_CHAPTERS);
    const [loading,          setLoading]          = useState(true);
    const [activeFilter,     setActiveFilter]     = useState('all');
    const [confirmCourse,    setConfirmCourse]    = useState(null);
    const [confirmLesson,    setConfirmLesson]    = useState(null);
    const [showCourseModal,  setShowCourseModal]  = useState(false);
    const [showChapterModal, setShowChapterModal] = useState(false);
    const [editingCourse,    setEditingCourse]    = useState(null);
    const [newCourse,        setNewCourse]        = useState({
        title: '', description: '', image: '', difficulty_level: 'Beginner', duration_weeks: '4', max_points: '100',
    });

    // ФИКС: sameId для поиска курса и урока
    const activeCourse  = courseId ? courses.find(c => sameId(c.id, courseId)) || null : null;
    const activeLesson  = (lessonId && !isNew && activeCourse)
        ? activeCourse.lessons.find(l => sameId(l.id, lessonId)) || null
        : null;
    // Урок для редактора (edit mode)
    const editingLesson = isEdit ? activeLesson : null;

    /* ── Initial load ── */
    useEffect(() => {
        request(`${API_URL}v1/courses/my`, 'GET', null, headers())
            .then(data => {
                setCourses((Array.isArray(data) ? data : []).map(c => ({
                    ...c, image: c.image_url || '', studentsCount: c.students_count || 0, lessons: [],
                })));
            })
            .catch(() => setCourses([]))
            .finally(() => setLoading(false));
    }, []);

    /* ── Load lessons when courseId changes ── */
    const loadLessons = (cId) => {
        request(`${API_URL}v1/courses/${cId}/lessons`, 'GET', null, headers())
            .then(data => {
                const lessons = (Array.isArray(data) ? data : [])
                    .sort((a, b) => (a.order || 0) - (b.order || 0))
                    .map(apiToLesson);
                // ФИКС: sameId
                setCourses(cs => cs.map(c => sameId(c.id, cId) ? { ...c, lessons } : c));
            })
            .catch(() => {});
    };

    useEffect(() => {
        if (courseId) loadLessons(courseId);
    }, [courseId]); // eslint-disable-line

    /* ── Exercise sync ── */
    const syncExercises = async (cId, lId, oldExercises, newExercises) => {
        const oldIds = oldExercises.map(e => e.id).filter(Boolean);
        const newIds = newExercises.map(e => e.id).filter(Boolean);
        for (const id of oldIds.filter(id => !newIds.includes(id))) {
            await fetch(`${API_URL}v1/courses/${cId}/lessons/${lId}/exercises/${id}`, { method: 'DELETE', mode: 'cors', headers: headers() }).catch(() => {});
        }
        for (const ex of newExercises) {
            const body = JSON.stringify(exerciseToApi(ex));
            if (ex.id && oldIds.includes(ex.id)) {
                await fetch(`${API_URL}v1/courses/${cId}/lessons/${lId}/exercises/${ex.id}`, { method: 'PUT', mode: 'cors', headers: headers(), body }).catch(() => {});
            } else {
                await fetch(`${API_URL}v1/courses/${cId}/lessons/${lId}/exercises`, { method: 'POST', mode: 'cors', headers: headers(), body }).catch(() => {});
            }
        }
    };

    const filteredCourses = courses.filter(c => activeFilter === 'all' || c.lessons.some(l => l.chapter === activeFilter));

    /* ── Course CRUD ── */
    const openAddCourse = () => {
        setEditingCourse(null);
        setNewCourse({ title: '', description: '', image: '', difficulty_level: 'Beginner', duration_weeks: '4', max_points: '100' });
        setShowCourseModal(true);
    };
    const openEditCourse = (course, e) => {
        e.stopPropagation();
        setEditingCourse(course);
        setNewCourse({ title: course.title, description: course.description, image: course.image, difficulty_level: course.difficulty_level || 'Beginner', duration_weeks: course.duration_weeks || '4', max_points: course.max_points || '100' });
        setShowCourseModal(true);
    };
    const saveCourse = () => {
        if (!newCourse.title.trim() || !newCourse.description.trim()) return;
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        const body = { title: newCourse.title, description: newCourse.description, image_url: newCourse.image, instructor_id: user.id, difficulty_level: newCourse.difficulty_level || 'Beginner', duration_weeks: Number(newCourse.duration_weeks) || 4, max_points: Number(newCourse.max_points) || 100, is_active: true };
        if (editingCourse) {
            request(`${API_URL}v1/courses/${editingCourse.id}`, 'PUT', JSON.stringify(body), headers())
                .then(res => { setCourses(cs => cs.map(c => sameId(c.id, editingCourse.id) ? { ...c, ...res, image: res.image_url || '' } : c)); setShowCourseModal(false); }).catch(() => {});
        } else {
            request(`${API_URL}v1/courses/`, 'POST', JSON.stringify(body), headers())
                .then(res => { setCourses(cs => [...cs, { ...res, image: res.image_url || '', studentsCount: 0, lessons: [] }]); setShowCourseModal(false); }).catch(() => {});
        }
    };
    const toggleCoursePublish = (course, e) => {
        e.stopPropagation();
        const newVal = !course.is_published;
        setCourses(cs => cs.map(c => sameId(c.id, course.id) ? { ...c, is_published: newVal } : c));
        request(`${API_URL}v1/courses/${course.id}`, 'PUT', JSON.stringify({ is_published: newVal }), headers())
            .catch(() => setCourses(cs => cs.map(c => sameId(c.id, course.id) ? { ...c, is_published: !newVal } : c)));
    };
    const doDeleteCourse = (id) => {
        fetch(`${API_URL}v1/courses/${id}`, { method: 'DELETE', mode: 'cors', headers: headers() })
            .then(() => {
                setCourses(cs => cs.filter(c => !sameId(c.id, id)));
                setConfirmCourse(null);
                if (sameId(courseId, id)) navigate('/teacher/courses');
            })
            .catch(() => setConfirmCourse(null));
    };

    /* ── Lesson CRUD ── */
    const saveLesson = async (formData) => {
        if (!activeCourse) return;
        const body   = lessonToApi(formData);
        const method = editingLesson ? 'PUT' : 'POST';
        const url    = editingLesson
            ? `${API_URL}v1/courses/${activeCourse.id}/lessons/${editingLesson.id}`
            : `${API_URL}v1/courses/${activeCourse.id}/lessons`;
        try {
            const savedLesson = await request(url, method, JSON.stringify({ ...body, is_active: true }), headers());
            const lId         = savedLesson?.id || editingLesson?.id;
            const exSection   = formData.sections?.find(s => s.type === 'exercise');
            if (lId && exSection) {
                const oldEx = editingLesson?.sections?.find(s => s.type === 'exercise')?.exercises || [];
                await syncExercises(activeCourse.id, lId, oldEx, exSection.exercises || []);
            }
            loadLessons(activeCourse.id);
            navigate(`/teacher/courses/${activeCourse.id}`);
        } catch (err) {
            console.error('saveLesson error:', err);
        }
    };
    const toggleLessonPublish = (lesson) => {
        if (!activeCourse) return;
        const newVal = !lesson.is_published;
        setCourses(cs => cs.map(c => !sameId(c.id, activeCourse.id) ? c : {
            ...c, lessons: c.lessons.map(l => sameId(l.id, lesson.id) ? { ...l, is_published: newVal } : l),
        }));
        request(`${API_URL}v1/courses/${activeCourse.id}/lessons/${lesson.id}`, 'PUT', JSON.stringify({ is_published: newVal }), headers())
            .catch(() => setCourses(cs => cs.map(c => !sameId(c.id, activeCourse.id) ? c : {
                ...c, lessons: c.lessons.map(l => sameId(l.id, lesson.id) ? { ...l, is_published: !newVal } : l),
            })));
    };
    const reorderLessons = async (reorderedLessons) => {
        if (!activeCourse) return;
        setCourses(cs => cs.map(c => sameId(c.id, activeCourse.id) ? { ...c, lessons: reorderedLessons } : c));
        await Promise.all(
            reorderedLessons.map((lesson, index) =>
                request(`${API_URL}v1/courses/${activeCourse.id}/lessons/${lesson.id}`, 'PUT', JSON.stringify({ order: index }), headers()).catch(() => {})
            )
        );
    };
    const doDeleteLesson = (lId) => {
        if (!activeCourse) return;
        fetch(`${API_URL}v1/courses/${activeCourse.id}/lessons/${lId}`, { method: 'DELETE', mode: 'cors', headers: headers() })
            .then(() => {
                setCourses(cs => cs.map(c => sameId(c.id, activeCourse.id) ? { ...c, lessons: c.lessons.filter(l => !sameId(l.id, lId)) } : c));
                setConfirmLesson(null);
                if (sameId(lessonId, lId)) navigate(`/teacher/courses/${activeCourse.id}`);
            })
            .catch(() => setConfirmLesson(null));
    };

    /* ═══════════ VIEWS ═══════════ */

    const Loader = () => <div style={{ textAlign: 'center', padding: '60px', color: 'rgba(26,26,46,0.4)' }}>Загрузка...</div>;

    if (loading && courseId) return <Loader />;

    /* ── Новый урок ── */
    if (view === 'new' && activeCourse) {
        return (
            <>
                <LessonEditorPage
                    course={activeCourse}
                    lesson={null}
                    chapters={chapters}
                    onSave={saveLesson}
                    onClose={() => navigate(`/teacher/courses/${activeCourse.id}`)}
                />
                {confirmLesson && <ConfirmModal title="Удалить урок?" text="Это действие нельзя отменить." onConfirm={() => doDeleteLesson(confirmLesson)} onClose={() => setConfirmLesson(null)} />}
            </>
        );
    }

    /* ── Редактирование урока ── */
    if (view === 'edit' && activeCourse) {
        if (!editingLesson) return <Loader />;
        return (
            <>
                <LessonEditorPage
                    course={activeCourse}
                    lesson={editingLesson}
                    chapters={chapters}
                    onSave={saveLesson}
                    onClose={() => navigate(`/teacher/courses/${activeCourse.id}`)}
                />
                {confirmLesson && <ConfirmModal title="Удалить урок?" text="Это действие нельзя отменить." onConfirm={() => doDeleteLesson(confirmLesson)} onClose={() => setConfirmLesson(null)} />}
            </>
        );
    }

    /* ── Просмотр урока (учитель) ── */
    if (view === 'lesson' && activeCourse) {
        if (!activeLesson) return <Loader />;
        return (
            <>
                <LessonPage
                    lesson={activeLesson}
                    course={activeCourse}
                    allLessons={activeCourse.lessons}
                    onBack={(target) => {
                        if (target === 'courses') navigate('/teacher/courses');
                        else navigate(`/teacher/courses/${activeCourse.id}`);
                    }}
                    onNavigate={(l) => navigate(`/teacher/courses/${activeCourse.id}/lessons/${l.id}`)}
                    onEdit={() => navigate(`/teacher/courses/${activeCourse.id}/lessons/${activeLesson.id}/edit`)}
                    onDelete={() => setConfirmLesson(activeLesson.id)}
                />
                {confirmLesson && (
                    <ConfirmModal
                        title="Удалить урок?" text="Это действие нельзя отменить."
                        onConfirm={() => doDeleteLesson(confirmLesson)}
                        onClose={() => setConfirmLesson(null)}
                    />
                )}
            </>
        );
    }

    /* ── Страница курса (список уроков) ── */
    if (view === 'course' && activeCourse) {
        return (
            <>
                <CourseDetailPage
                    course={activeCourse}
                    onBack={() => navigate('/teacher/courses')}
                    onOpenLesson={(lesson) => navigate(`/teacher/courses/${activeCourse.id}/lessons/${lesson.id}`)}
                    onAddLesson={() => navigate(`/teacher/courses/${activeCourse.id}/lessons/new`)}
                    onEditLesson={(lesson) => navigate(`/teacher/courses/${activeCourse.id}/lessons/${lesson.id}/edit`)}
                    onDeleteLesson={(id) => setConfirmLesson(id)}
                    onToggleLessonPublish={toggleLessonPublish}
                    onReorderLessons={reorderLessons}
                />
                {confirmLesson && (
                    <ConfirmModal
                        title="Удалить урок?" text="Это действие нельзя отменить."
                        onConfirm={() => doDeleteLesson(confirmLesson)}
                        onClose={() => setConfirmLesson(null)}
                    />
                )}
            </>
        );
    }

    /* ═══ Список курсов ═══ */
    return (
        <div className="tc-container item-fade-in">
            <div className="tc-header">
                <div>
                    <h2>Управление курсами</h2>
                    <p className="tc-subtitle">Создавайте курсы и добавляйте уроки для студентов</p>
                </div>
                <div className="tc-header-actions">
                    <button className="tc-chapter-btn" onClick={() => setShowChapterModal(true)}>📚 Разделы</button>
                    <button className="tc-add-btn" onClick={openAddCourse}>➕ Создать курс</button>
                </div>
            </div>

            <div className="tc-filter-bar">
                <span className="tc-filter-label">Фильтр:</span>
                <button className={`tc-filter-chip ${activeFilter === 'all' ? 'active' : ''}`} onClick={() => setActiveFilter('all')}>Все курсы</button>
                {chapters.map(ch => (
                    <button key={ch} className={`tc-filter-chip ${activeFilter === ch ? 'active' : ''}`} onClick={() => setActiveFilter(activeFilter === ch ? 'all' : ch)}>{ch}</button>
                ))}
            </div>

            {loading ? (
                <div className="tc-loading">Загрузка курсов...</div>
            ) : filteredCourses.length === 0 ? (
                <div className="tc-empty"><div className="tc-empty-icon">📭</div><p>Курсов пока нет</p></div>
            ) : (
                <div className="tc-courses-grid">
                    {filteredCourses.map(course => (
                        <div key={course.id} className="tc-course-card" onClick={() => navigate(`/teacher/courses/${course.id}`)}>
                            <div className="tc-course-preview">
                                <img src={course.image} alt={course.title} />
                                <div className="tc-course-overlay"><span className="tc-view-label">👁️ Открыть курс</span></div>
                            </div>
                            <div className="tc-course-info">
                                <div className="tc-course-header">
                                    <h3>{course.title}</h3>
                                    <div className="tc-course-actions">
                                        <button className={`tc-publish-btn ${course.is_published ? 'published' : 'draft'}`} onClick={e => toggleCoursePublish(course, e)}>
                                            <span className="tc-publish-dot" />{course.is_published ? 'Опубликован' : 'Черновик'}
                                        </button>
                                        <button className="tc-icon-btn tc-ediet-icon" onClick={e => openEditCourse(course, e)}>✏️</button>
                                        <button className="tc-icon-btn tc-delete-icon" onClick={e => { e.stopPropagation(); setConfirmCourse(course.id); }}>🗑️</button>
                                    </div>
                                </div>
                                <p>{course.description}</p>
                                <div className="tc-course-stats">
                                    <span className="tc-stat">📚 {course.lessons.length} уроков</span>
                                    <span className="tc-stat">👥 {course.studentsCount} студентов</span>
                                </div>
                                <button className="tc-open-course-btn" onClick={e => { e.stopPropagation(); navigate(`/teacher/courses/${course.id}`); }}>Открыть курс →</button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {showCourseModal && ReactDOM.createPortal(
                <div className="tc-modal-overlay" onClick={() => setShowCourseModal(false)}>
                    <div className="tc-modal" onClick={e => e.stopPropagation()}>
                        <h3>{editingCourse ? '✏️ Редактировать курс' : '➕ Создать новый курс'}</h3>
                        <input placeholder="Название курса *" value={newCourse.title} onChange={e => setNewCourse(p => ({ ...p, title: e.target.value }))} />
                        <textarea placeholder="Описание курса *" value={newCourse.description} onChange={e => setNewCourse(p => ({ ...p, description: e.target.value }))} />
                        <input placeholder="URL изображения" value={newCourse.image} onChange={e => setNewCourse(p => ({ ...p, image: e.target.value }))} />
                        <select value={newCourse.difficulty_level} onChange={e => setNewCourse(p => ({ ...p, difficulty_level: e.target.value }))}>
                            <option>Beginner</option><option>Intermediate</option><option>Advanced</option>
                        </select>
                        <input type="number" placeholder="Количество недель" value={newCourse.duration_weeks} onChange={e => setNewCourse(p => ({ ...p, duration_weeks: e.target.value }))} />
                        <input type="number" placeholder="Максимум баллов" value={newCourse.max_points} onChange={e => setNewCourse(p => ({ ...p, max_points: e.target.value }))} />
                        <div className="tc-modal-actions">
                            <button className="tc-cancel-btn" onClick={() => setShowCourseModal(false)}>Отмена</button>
                            <button className="tc-save-btn" onClick={saveCourse}>{editingCourse ? 'Сохранить' : 'Создать'}</button>
                        </div>
                    </div>
                </div>,
                document.body
            )}

            {showChapterModal && <ChaptersModal chapters={chapters} onSave={setChapters} onClose={() => setShowChapterModal(false)} />}
            {confirmCourse && <ConfirmModal title="Удалить курс?" text="Это действие нельзя отменить. Все уроки тоже будут удалены." onConfirm={() => doDeleteCourse(confirmCourse)} onClose={() => setConfirmCourse(null)} />}
        </div>
    );
};

export default TeacherCourses;