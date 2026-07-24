import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import {
    DndContext, closestCenter, PointerSensor, KeyboardSensor,
    useSensor, useSensors,
} from '@dnd-kit/core';
import {
    SortableContext, sortableKeyboardCoordinates,
    rectSortingStrategy, arrayMove,
} from '@dnd-kit/sortable';
import './TeacherCourses.css';
import LessonEditorPage from '../LessonEditor/LessonEditor';
import CourseDetailPage from '../CourseModal/CourseModal';
import LessonPage from '../LessonPage/LessonPage';
import AssignStudentsModal from '../AssignStudentsModal/AssignStudentsModal';
import { API_URL, useHttp, headers, getCurrentUser } from '../../../../api/search/base';
import { sameId, apiToLesson, lessonToApi, exerciseToApi } from './helpers';
import { ConfirmModal } from './ConfirmModal';
import { CategoriesModal } from './CategoriesModal';
import { SortableCourseCard } from './SortableCourseCard';
import { CategoryPicker } from './CategoryPicker';

// Category state is loaded from the backend (categories table). The previous
// hardcoded `INITIAL_CHAPTERS` list was removed in favor of real categories
// you can create, rename, and assign to courses.

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
    const [categories,       setCategories]       = useState([]);
    const [loading,          setLoading]          = useState(true);
    const [activeFilter,     setActiveFilter]     = useState('all');
    const [confirmCourse,    setConfirmCourse]    = useState(null);
    const [confirmLesson,    setConfirmLesson]    = useState(null);
    const [showCourseModal,  setShowCourseModal]  = useState(false);
    const [savingCourse,     setSavingCourse]     = useState(false);
    const [courseSaveError,  setCourseSaveError]  = useState('');
    const [showChapterModal, setShowChapterModal] = useState(false);
    const [editingCourse,    setEditingCourse]    = useState(null);
    const [assignCourse,     setAssignCourse]     = useState(null);
    const [newCourse,        setNewCourse]        = useState({
        title: '', description: '', image: '', difficulty_level: 'Beginner', duration_weeks: '4', max_points: '100', category_name: '',
    });

    // ФИКС: sameId для поиска курса и урока
    const activeCourse  = courseId ? courses.find(c => sameId(c.id, courseId)) || null : null;
    const activeLesson  = (lessonId && !isNew && activeCourse)
        ? activeCourse.lessons.find(l => sameId(l.id, lessonId)) || null
        : null;
    // Урок для редактора (edit mode)
    const editingLesson = isEdit ? activeLesson : null;

    /* ── Initial load ── */
    const loadCategories = () => {
        request(`${API_URL}v1/categories/`, 'GET', null, headers())
            .then(data => setCategories(Array.isArray(data) ? data : []))
            .catch(() => setCategories([]));
    };

    useEffect(() => {
        request(`${API_URL}v1/courses/my`, 'GET', null, headers())
            .then(data => {
                setCourses((Array.isArray(data) ? data : []).map(c => ({
                    ...c, image: c.image_url || '', studentsCount: c.students_count || 0, lessons: [],
                })));
            })
            .catch(() => setCourses([]))
            .finally(() => setLoading(false));
        loadCategories();
    }, []); // eslint-disable-line

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

    // Escape closes the course-create/edit modal (matching other modals in
    // this view). Guarded so a save in flight can't be interrupted.
    useEffect(() => {
        if (!showCourseModal) return;
        const onKey = (e) => {
            if (e.key === 'Escape' && !savingCourse) {
                setShowCourseModal(false);
                setCourseSaveError('');
            }
        };
        document.addEventListener('keydown', onKey);
        return () => document.removeEventListener('keydown', onKey);
    }, [showCourseModal, savingCourse]);

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

    const filteredCourses = courses.filter(c => {
        if (activeFilter === 'all') return true;
        if (activeFilter === 'uncategorized') return !c.category_id;
        return c.category_id === activeFilter;
    });

    // Reordering is always allowed, even with a category filter active — see
    // handleDragEnd, which reorders only the visible (filtered) subset and
    // splices it back into the full list at the same absolute slots, so
    // hidden courses from other categories never move.
    const canReorder = true;

    // dnd-kit sensors: PointerSensor with a small activation distance prevents
    // micro-drags from firing on a normal click (so clicking the card body
    // still navigates without triggering a reorder). KeyboardSensor gives us
    // accessibility for free (Space/Enter to grab, arrows to move).
    const sensors = useSensors(
        useSensor(PointerSensor, { activationConstraint: { distance: 6 } }),
        useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
    );

    const handleDragEnd = (event) => {
        if (!canReorder) return;
        const { active, over } = event;
        if (!over || active.id === over.id) return;

        // active/over ids come from the FILTERED subset (SortableContext is
        // built from filteredCourses). Reorder just that subset, then splice
        // the result back into the full `courses` array at the same absolute
        // slots those cards occupied — so courses hidden by the current
        // filter never move, only the visible ones swap among themselves.
        const oldIndex = filteredCourses.findIndex(c => String(c.id) === String(active.id));
        const newIndex = filteredCourses.findIndex(c => String(c.id) === String(over.id));
        if (oldIndex === -1 || newIndex === -1) return;

        const reorderedFiltered = arrayMove(filteredCourses, oldIndex, newIndex);
        const filteredIds = new Set(filteredCourses.map(c => String(c.id)));
        const slots = [];
        courses.forEach((c, i) => { if (filteredIds.has(String(c.id))) slots.push(i); });

        const prev = courses;
        const next = [...courses];
        slots.forEach((slotIndex, i) => { next[slotIndex] = reorderedFiltered[i]; });
        const withOrder = next.map((c, i) => ({ ...c, display_order: i }));
        setCourses(withOrder);  // optimistic — UI updates immediately

        const payload = {
            items: withOrder.map((c, i) => ({ id: Number(c.id), display_order: i })),
        };
        request(`${API_URL}v1/courses/reorder`, 'PUT', JSON.stringify(payload), headers())
            .catch(() => {
                // Server rejected (auth, ownership, network). Roll back the UI
                // so the teacher doesn't see a fake ordering that won't survive a refresh.
                setCourses(prev);
            });
    };

    /* ── Course CRUD ── */
    const openAddCourse = () => {
        setEditingCourse(null);
        setNewCourse({
            title: '', description: '', image: '',
            difficulty_level: 'Beginner', duration_weeks: '4', max_points: '100',
            category_name: '',
        });
        setShowCourseModal(true);
    };
    const openEditCourse = (course, e) => {
        e.stopPropagation();
        setEditingCourse(course);
        setNewCourse({
            title: course.title,
            description: course.description,
            image: course.image,
            difficulty_level: course.difficulty_level || 'Beginner',
            duration_weeks: course.duration_weeks || '4',
            max_points: course.max_points || '100',
            category_name: course.category_name || '',
        });
        setShowCourseModal(true);
    };
    const saveCourse = () => {
        if (savingCourse) return; // guard against double-click
        if (!newCourse.title.trim() || !newCourse.description.trim()) {
            setCourseSaveError('Заполните название и описание');
            return;
        }
        const user = getCurrentUser();
        const body = {
            title: newCourse.title,
            description: newCourse.description,
            image_url: newCourse.image,
            instructor_id: user.id,
            difficulty_level: newCourse.difficulty_level || 'Beginner',
            duration_weeks: Number(newCourse.duration_weeks) || 4,
            max_points: Number(newCourse.max_points) || 100,
            is_active: true,
            // Backend auto-creates the category if no row matches this name.
            // Empty string clears the assignment to "uncategorized".
            category_name: newCourse.category_name?.trim() || null,
        };
        setSavingCourse(true);
        setCourseSaveError('');
        const onErr = () => setCourseSaveError('Не удалось сохранить курс. Попробуйте ещё раз.');
        const finish = () => setSavingCourse(false);
        if (editingCourse) {
            request(`${API_URL}v1/courses/${editingCourse.id}`, 'PUT', JSON.stringify(body), headers())
                .then(res => {
                    setCourses(cs => cs.map(c => sameId(c.id, editingCourse.id) ? { ...c, ...res, image: res.image_url || '' } : c));
                    setShowCourseModal(false);
                    loadCategories();
                })
                .catch(onErr)
                .finally(finish);
        } else {
            request(`${API_URL}v1/courses/`, 'POST', JSON.stringify(body), headers())
                .then(res => {
                    setCourses(cs => [...cs, { ...res, image: res.image_url || '', studentsCount: 0, lessons: [] }]);
                    setShowCourseModal(false);
                    loadCategories();
                })
                .catch(onErr)
                .finally(finish);
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
                    chapters={categories.map(c => c.name)}
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
                    chapters={categories.map(c => c.name)}
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
                    <button className="tc-chapter-btn" onClick={() => setShowChapterModal(true)}>📚 Категории</button>
                    <button className="tc-add-btn" onClick={openAddCourse}>➕ Создать курс</button>
                </div>
            </div>

            <div className="tc-filter-bar">
                <span className="tc-filter-label">Фильтр:</span>
                <button
                    className={`tc-filter-chip ${activeFilter === 'all' ? 'active' : ''}`}
                    onClick={() => setActiveFilter('all')}
                >Все курсы</button>
                {categories.map(cat => (
                    <button
                        key={cat.id}
                        className={`tc-filter-chip ${activeFilter === cat.id ? 'active' : ''}`}
                        onClick={() => setActiveFilter(activeFilter === cat.id ? 'all' : cat.id)}
                    >
                        {cat.name}
                        {cat.courses_count > 0 && (
                            <span className="tc-filter-count">{cat.courses_count}</span>
                        )}
                    </button>
                ))}
                {courses.some(c => !c.category_id) && (
                    <button
                        className={`tc-filter-chip ${activeFilter === 'uncategorized' ? 'active' : ''}`}
                        onClick={() => setActiveFilter(activeFilter === 'uncategorized' ? 'all' : 'uncategorized')}
                    >
                        Без категории
                    </button>
                )}
            </div>

            {loading ? (
                <div className="tc-loading">Загрузка курсов...</div>
            ) : filteredCourses.length === 0 ? (
                <div className="tc-empty"><div className="tc-empty-icon">📭</div><p>Курсов пока нет</p></div>
            ) : (
                <>
                    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
                        <SortableContext items={filteredCourses.map(c => String(c.id))} strategy={rectSortingStrategy}>
                            <div className="tc-courses-grid">
                                {filteredCourses.map(course => (
                                    <SortableCourseCard
                                        key={course.id}
                                        course={course}
                                        canReorder={canReorder}
                                        currentUserId={getCurrentUser().id}
                                        navigate={navigate}
                                        onPublishToggle={toggleCoursePublish}
                                        onEdit={openEditCourse}
                                        onConfirmDelete={setConfirmCourse}
                                        onAssign={setAssignCourse}
                                    />
                                ))}
                            </div>
                        </SortableContext>
                    </DndContext>
                </>
            )}

            {showCourseModal && ReactDOM.createPortal(
                <div className="tc-modal-overlay" onClick={() => !savingCourse && setShowCourseModal(false)}>
                    <div className="tc-modal" onClick={e => e.stopPropagation()}>
                        <h3>{editingCourse ? '✏️ Редактировать курс' : '➕ Создать новый курс'}</h3>
                        <input placeholder="Название курса *" value={newCourse.title} onChange={e => setNewCourse(p => ({ ...p, title: e.target.value }))} />
                        <textarea placeholder="Описание курса *" value={newCourse.description} onChange={e => setNewCourse(p => ({ ...p, description: e.target.value }))} />
                        <input placeholder="URL изображения" value={newCourse.image} onChange={e => setNewCourse(p => ({ ...p, image: e.target.value }))} />
                        <CategoryPicker
                            categories={categories}
                            value={newCourse.category_name}
                            onChange={(v) => setNewCourse(p => ({ ...p, category_name: v }))}
                            placeholder="Категория (если её нет — создадим)"
                        />
                        <select value={newCourse.difficulty_level} onChange={e => setNewCourse(p => ({ ...p, difficulty_level: e.target.value }))}>
                            <option>Beginner</option><option>Intermediate</option><option>Advanced</option>
                        </select>
                        <input type="number" placeholder="Количество недель" value={newCourse.duration_weeks} onChange={e => setNewCourse(p => ({ ...p, duration_weeks: e.target.value }))} />
                        <input type="number" placeholder="Максимум баллов" value={newCourse.max_points} onChange={e => setNewCourse(p => ({ ...p, max_points: e.target.value }))} />
                        {courseSaveError && (
                            <div className="tc-modal-error" role="alert">⚠ {courseSaveError}</div>
                        )}
                        <div className="tc-modal-actions">
                            <button className="tc-cancel-btn" disabled={savingCourse} onClick={() => setShowCourseModal(false)}>Отмена</button>
                            <button className="tc-save-btn" disabled={savingCourse} onClick={saveCourse}>
                                {savingCourse ? 'Сохранение…' : (editingCourse ? 'Сохранить' : 'Создать')}
                            </button>
                        </div>
                    </div>
                </div>,
                document.body
            )}

            {showChapterModal && (
                <CategoriesModal
                    categories={categories}
                    onClose={() => setShowChapterModal(false)}
                    onChanged={loadCategories}
                    request={request}
                />
            )}
            {confirmCourse && <ConfirmModal title="Удалить курс?" text="Это действие нельзя отменить. Все уроки тоже будут удалены." onConfirm={() => doDeleteCourse(confirmCourse)} onClose={() => setConfirmCourse(null)} />}
            {assignCourse && (
                <AssignStudentsModal
                    course={assignCourse}
                    onClose={() => setAssignCourse(null)}
                    onChanged={() => { /* counts refresh on next page load */ }}
                />
            )}
        </div>
    );
};

export default TeacherCourses;
