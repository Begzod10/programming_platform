import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

/* ═══════════════════════════════════════════
   SortableCourseCard — single card wired to dnd-kit's useSortable.
   Extracted so each card calls the hook independently (a hook can't
   live inside .map()'s callback otherwise).

   Key points to keep the drag smooth:
     • `transform` and `transition` come from useSortable — they go on
       `style`, NOT on a CSS class. The library updates them per frame.
     • While dragging this card, we also bump opacity for visual cue
       and disable pointer events on inner clickables so the navigation
       click doesn't fire on drag-release.
═══════════════════════════════════════════ */
export const SortableCourseCard = ({ course, canReorder, currentUserId, navigate, onPublishToggle, onEdit, onDelete, onConfirmDelete, onAssign }) => {
    const isOwner = currentUserId && Number(course.instructor_id) === Number(currentUserId);
    const {
        attributes, listeners, setNodeRef,
        transform, transition, isDragging,
    } = useSortable({ id: String(course.id), disabled: !canReorder || !isOwner });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.6 : 1,
        zIndex: isDragging ? 10 : 'auto',
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            className={`tc-course-card${isDragging ? ' tc-course-card--dragging' : ''}`}
            onClick={() => { if (!isDragging) navigate(`/teacher/courses/${course.id}`); }}
            {...attributes}
        >
            {canReorder && isOwner && (
                <div
                    className="tc-drag-handle"
                    title="Удерживайте и перетащите, чтобы изменить порядок"
                    onClick={e => e.stopPropagation()}
                    {...listeners}
                >
                    ⋮⋮
                </div>
            )}
            <div className="tc-course-preview">
                <img src={course.image} alt={course.title} />
                <div className="tc-course-overlay"><span className="tc-view-label">👁️ Открыть курс</span></div>
            </div>
            <div className="tc-course-info">
                <div className="tc-course-header">
                    <h3>{course.title}</h3>
                    <div className="tc-course-actions">
                        {isOwner ? (
                            <>
                                <button className={`tc-publish-btn ${course.is_published ? 'published' : 'draft'}`} onClick={e => onPublishToggle(course, e)}>
                                    <span className="tc-publish-dot" />{course.is_published ? 'Опубликован' : 'Черновик'}
                                </button>
                                <button className="tc-icon-btn tc-ediet-icon" onClick={e => onEdit(course, e)}>✏️</button>
                                <button className="tc-icon-btn tc-delete-icon" onClick={e => { e.stopPropagation(); onConfirmDelete(course.id); }}>🗑️</button>
                            </>
                        ) : (
                            <span className={`tc-publish-btn ${course.is_published ? 'published' : 'draft'}`} style={{ pointerEvents: 'none' }}>
                                <span className="tc-publish-dot" />{course.is_published ? 'Опубликован' : 'Черновик'}
                            </span>
                        )}
                    </div>
                </div>
                <p>{course.description}</p>
                <div className="tc-course-stats">
                    <span className="tc-stat">📚 {course.lessons.length} уроков</span>
                    <span className="tc-stat">👥 {course.studentsCount} студентов</span>
                </div>
                <div className="tc-course-cta">
                    <button
                        className="tc-assign-btn"
                        onClick={e => { e.stopPropagation(); onAssign?.(course); }}
                    >
                        👥 Talabalarni boshqarish
                    </button>
                    <button className="tc-open-course-btn" onClick={e => { e.stopPropagation(); navigate(`/teacher/courses/${course.id}`); }}>Открыть курс →</button>
                </div>
            </div>
        </div>
    );
};
