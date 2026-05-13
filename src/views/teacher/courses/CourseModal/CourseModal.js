import React, { useState, useRef, useCallback, useEffect } from 'react';
import './CourseModal.css';

/* ─────────────────────────────────────────
   useDragToReorder — mouse + touch support
───────────────────────────────────────── */
function useDragToReorder(items, onReorder) {
    const [order, setOrder]         = useState(() => items.map(l => l.id));
    const [dragId, setDragId]       = useState(null);
    const [overId, setOverId]       = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const [hasUnsaved, setHasUnsaved] = useState(false);
    const [isSaving, setIsSaving]   = useState(false);
    const [savedOk, setSavedOk]     = useState(false);

    // Sync when items change from outside (e.g. after fetch)
    useEffect(() => {
        setOrder(items.map(l => l.id));
        setHasUnsaved(false);
    }, [items]);

    const orderedItems = order
        .map(id => items.find(l => l.id === id))
        .filter(Boolean);

    // Called when user clicks "Сохранить порядок"
    const saveOrder = useCallback(async () => {
        const reordered = order
            .map(id => items.find(l => l.id === id))
            .filter(Boolean);
        setIsSaving(true);
        try {
            await onReorder?.(reordered);
            setHasUnsaved(false);
            setSavedOk(true);
            setTimeout(() => setSavedOk(false), 2000);
        } catch (e) {
            // keep hasUnsaved = true so user can retry
        } finally {
            setIsSaving(false);
        }
    }, [order, items, onReorder]);

    /* ── commit reorder locally only (no auto-save) ── */
    const commitReorder = useCallback((fromId, toId) => {
        if (!fromId || !toId || fromId === toId) return;
        setOrder(prev => {
            const arr  = [...prev];
            const from = arr.indexOf(fromId);
            const to   = arr.indexOf(toId);
            if (from === -1 || to === -1) return prev;
            arr.splice(from, 1);
            arr.splice(to, 0, fromId);
            return arr;
        });
        setHasUnsaved(true);
    }, []);

    /* ══════════ MOUSE ══════════ */
    const handleMouseDown = useCallback((e, id) => {
        if (e.button !== 0) return;
        e.preventDefault();
        setDragId(id);
        setIsDragging(true);
    }, []);

    const handleMouseEnter = useCallback((id) => {
        if (!dragId) return;
        setOverId(id);
    }, [dragId]);

    const handleMouseUp = useCallback((targetId) => {
        if (!dragId) return;
        commitReorder(dragId, targetId);
        setDragId(null);
        setOverId(null);
        setIsDragging(false);
    }, [dragId, commitReorder]);

    // safety: release on window mouseup (card missed)
    useEffect(() => {
        if (!dragId) return;
        const onUp = () => {
            setDragId(null);
            setOverId(null);
            setIsDragging(false);
        };
        window.addEventListener('mouseup', onUp);
        return () => window.removeEventListener('mouseup', onUp);
    }, [dragId]);

    /* ══════════ TOUCH ══════════ */
    const touchDragId  = useRef(null);
    const touchOverId  = useRef(null);
    const touchOverlay = useRef(null); // visual ghost element

    const createGhost = useCallback((cardEl, touch) => {
        const rect  = cardEl.getBoundingClientRect();
        const ghost = cardEl.cloneNode(true);
        ghost.style.cssText = `
            position: fixed;
            left: ${rect.left}px;
            top: ${rect.top}px;
            width: ${rect.width}px;
            height: ${rect.height}px;
            opacity: 0.85;
            pointer-events: none;
            z-index: 9999;
            transform: scale(1.04) rotate(1.5deg);
            box-shadow: 0 24px 60px rgba(108,92,231,0.35), 0 8px 24px rgba(0,0,0,0.18);
            border-radius: 18px;
            transition: none;
        `;
        ghost.classList.add('cdp-touch-ghost');
        document.body.appendChild(ghost);
        return ghost;
    }, []);

    const handleTouchStart = useCallback((e, id, cardEl) => {
        if (e.touches.length !== 1) return;
        touchDragId.current = id;
        setDragId(id);
        setIsDragging(true);

        const touch = e.touches[0];
        touchOverlay.current = createGhost(cardEl, touch);
        touchOverlay.current._offsetX = touch.clientX - cardEl.getBoundingClientRect().left;
        touchOverlay.current._offsetY = touch.clientY - cardEl.getBoundingClientRect().top;
    }, [createGhost]);

    const handleTouchMove = useCallback((e) => {
        if (!touchDragId.current) return;
        e.preventDefault(); // prevent page scroll during drag

        const touch = e.touches[0];

        // move ghost
        if (touchOverlay.current) {
            touchOverlay.current.style.left = `${touch.clientX - touchOverlay.current._offsetX}px`;
            touchOverlay.current.style.top  = `${touch.clientY - touchOverlay.current._offsetY}px`;
        }

        // find card under finger
        touchOverlay.current && (touchOverlay.current.style.display = 'none');
        const el   = document.elementFromPoint(touch.clientX, touch.clientY);
        touchOverlay.current && (touchOverlay.current.style.display = '');

        const card = el?.closest('[data-lesson-id]');
        const id   = card?.dataset?.lessonId ?? null;
        if (id !== touchOverId.current) {
            touchOverId.current = id;
            setOverId(id);
        }
    }, []);

    const handleTouchEnd = useCallback(() => {
        if (touchDragId.current && touchOverId.current) {
            commitReorder(touchDragId.current, touchOverId.current);
        }
        // cleanup ghost
        if (touchOverlay.current) {
            touchOverlay.current.style.transition = 'opacity 0.2s, transform 0.2s';
            touchOverlay.current.style.opacity    = '0';
            touchOverlay.current.style.transform  = 'scale(0.95)';
            setTimeout(() => touchOverlay.current?.remove(), 200);
            touchOverlay.current = null;
        }
        touchDragId.current = null;
        touchOverId.current = null;
        setDragId(null);
        setOverId(null);
        setIsDragging(false);
    }, [commitReorder]);

    return {
        orderedItems,
        dragId, overId, isDragging,
        hasUnsaved, isSaving, savedOk, saveOrder,
        handleMouseDown, handleMouseEnter, handleMouseUp,
        handleTouchStart, handleTouchMove, handleTouchEnd,
    };
}

/* ─────────────────────────────────────────
   CourseModal
───────────────────────────────────────── */
const CourseModal = ({
    course,
    onBack,
    onOpenLesson,
    onAddLesson,
    onEditLesson,
    onDeleteLesson,
    onToggleLessonPublish,
    onReorderLessons,
}) => {
    const {
        orderedItems, dragId, overId, isDragging,
        hasUnsaved, isSaving, savedOk, saveOrder,
        handleMouseDown, handleMouseEnter, handleMouseUp,
        handleTouchStart, handleTouchMove, handleTouchEnd,
    } = useDragToReorder(course.lessons ?? [], onReorderLessons);

    const allEmpty = orderedItems.length === 0;

    // build lesson index map
    const lessonIndex = {};
    orderedItems.forEach((l, i) => { lessonIndex[l.id] = i + 1; });

    // group by chapter
    const withChapter = {};
    const noChapter   = [];
    orderedItems.forEach(l => {
        if (l.chapter) {
            if (!withChapter[l.chapter]) withChapter[l.chapter] = [];
            withChapter[l.chapter].push(l);
        } else {
            noChapter.push(l);
        }
    });
    const chapterKeys = Object.keys(withChapter);

    const renderLesson = (lesson) => (
        <LessonCard
            key={lesson.id}
            lesson={lesson}
            index={lessonIndex[lesson.id]}
            isDragging={dragId === lesson.id}
            isOver={overId === lesson.id && dragId !== lesson.id}
            onOpen={() => { if (!isDragging) onOpenLesson(lesson); }}
            onEdit={() => onEditLesson(lesson)}
            onDelete={() => onDeleteLesson(lesson.id)}
            onTogglePublish={() => onToggleLessonPublish(lesson)}
            onDragHandleMouseDown={(e) => { e.stopPropagation(); handleMouseDown(e, lesson.id); }}
            onMouseEnter={() => handleMouseEnter(lesson.id)}
            onMouseUp={() => handleMouseUp(lesson.id)}
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
        />
    );

    return (
        <div
            className={`cdp-container${isDragging ? ' cdp-is-dragging' : ''}`}
            onMouseUp={() => handleMouseUp(null)}
        >
            {/* Top bar */}
            <div className="cdp-top-bar">
                <button className="cdp-back-btn" onClick={onBack}>
                    ← Назад к курсам
                </button>
                <div className="cdp-top-bar-right">
                    {hasUnsaved && (
                        <button
                            className={`cdp-save-order-btn${isSaving ? ' cdp-save-order-btn--saving' : ''}`}
                            onClick={saveOrder}
                            disabled={isSaving}
                        >
                            {isSaving ? <><span className="cdp-save-spinner" /> Сохранение...</> : '💾 Сохранить порядок'}
                        </button>
                    )}
                    {savedOk && !hasUnsaved && (
                        <span className="cdp-save-ok">✅ Порядок сохранён</span>
                    )}
                    <button className="cdp-add-lesson-btn" onClick={onAddLesson}>
                        ➕ Добавить урок
                    </button>
                </div>
            </div>

            {/* Banner */}
            <div className="cdp-banner">
                <img src={course.image} alt={course.title} className="cdp-banner-img" />
                <div className="cdp-banner-overlay">
                    <div className="cdp-banner-content">
                        <h1>{course.title}</h1>
                        <p>{course.description}</p>
                        <div className="cdp-banner-stats">
                            <span>📚 {orderedItems.length} уроков</span>
                            <span>👥 {course.studentsCount} студентов</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Section header */}
            <div className="cdp-section-header">
                <h2 className="cdp-section-title">📖 Уроки курса</h2>
                {!allEmpty && (
                    <div className="cdp-dnd-hint">
                        <span className="cdp-dnd-hint-icon">⠿</span>
                        Зажми ⠿ и перетащи урок
                    </div>
                )}
            </div>

            {/* Content */}
            {allEmpty ? (
                <div className="cdp-no-lessons">
                    <div className="cdp-no-lessons-icon">📭</div>
                    <p>В этом курсе пока нет уроков</p>
                </div>
            ) : (
                <>
                    {chapterKeys.map(chapter => (
                        <div key={chapter} className="cdp-chapter-group">
                            <div className="cdp-chapter-label">
                                <span className="cdp-chapter-name">{chapter}</span>
                                <span className="cdp-chapter-count">{withChapter[chapter].length} уроков</span>
                            </div>
                            <div className="cdp-lessons-grid">
                                {withChapter[chapter].map(renderLesson)}
                            </div>
                        </div>
                    ))}

                    {noChapter.length > 0 && (
                        <div className="cdp-chapter-group">
                            {chapterKeys.length > 0 && (
                                <div className="cdp-chapter-label">
                                    <span className="cdp-chapter-name">Без раздела</span>
                                    <span className="cdp-chapter-count">{noChapter.length} уроков</span>
                                </div>
                            )}
                            <div className="cdp-lessons-grid">
                                {noChapter.map(renderLesson)}
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

/* ─────────────────────────────────────────
   LessonCard
───────────────────────────────────────── */
const LessonCard = ({
    lesson, index,
    onOpen, onEdit, onDelete, onTogglePublish,
    isDragging, isOver,
    onDragHandleMouseDown,
    onMouseEnter, onMouseUp,
    onTouchStart, onTouchMove, onTouchEnd,
}) => {
    const cardRef    = useRef(null);
    const blockCount = lesson.sections?.length ?? 0;

    const handleTouchStartCard = useCallback((e) => {
        // Only start drag from the handle
        if (!e.target.closest('.cdp-drag-handle')) return;
        onTouchStart(e, lesson.id, cardRef.current);
    }, [lesson.id, onTouchStart]);

    return (
        <div
            ref={cardRef}
            data-lesson-id={lesson.id}
            className={[
                'cdp-lesson-card',
                isDragging ? 'cdp-lesson-dragging' : '',
                isOver     ? 'cdp-lesson-drop-over' : '',
            ].filter(Boolean).join(' ')}
            onClick={onOpen}
            onMouseEnter={onMouseEnter}
            onMouseUp={onMouseUp}
            onTouchStart={handleTouchStartCard}
            onTouchMove={onTouchMove}
            onTouchEnd={onTouchEnd}
        >
            {/* Drag handle */}
            <div
                className="cdp-drag-handle"
                onMouseDown={onDragHandleMouseDown}
                onClick={e => e.stopPropagation()}
                title="Зажми и перетащи"
            >
                <span className="cdp-drag-dots">⠿</span>
            </div>

            {/* Preview */}
            <div className="cdp-lesson-preview">
                {lesson.image
                    ? <img src={lesson.image} alt={lesson.title} draggable={false} />
                    : <div className="cdp-lesson-no-img">📹</div>
                }
                <span className="cdp-lesson-num-badge">Урок {index}</span>

                <div className="cdp-lesson-card-actions" onClick={e => e.stopPropagation()}>
                    <button
                        className="cdp-lesson-action-btn edit"
                        onMouseDown={e => e.stopPropagation()}
                        onClick={e => { e.stopPropagation(); onEdit(); }}
                        aria-label="Редактировать урок"
                    >✏️</button>
                    <button
                        className="cdp-lesson-action-btn del"
                        onMouseDown={e => e.stopPropagation()}
                        onClick={e => { e.stopPropagation(); onDelete(); }}
                        aria-label="Удалить урок"
                    >🗑️</button>
                </div>

                <div className="cdp-lesson-play-overlay">
                    <div className="cdp-lesson-play-circle">▶</div>
                </div>
            </div>

            {/* Info */}
            <div className="cdp-lesson-info">
                <h4>{lesson.title}</h4>
                <div className="cdp-lesson-meta">
                    {blockCount > 0 && (
                        <span className="cdp-lesson-blocks-count">
                            {blockCount} {blockCount === 1 ? 'блок' : blockCount < 5 ? 'блока' : 'блоков'}
                        </span>
                    )}
                    <button
                        className={`cdp-lesson-publish-btn ${lesson.is_published ? 'published' : 'draft'}`}
                        onMouseDown={e => e.stopPropagation()}
                        onClick={e => { e.stopPropagation(); onTogglePublish(); }}
                        title={lesson.is_published ? 'Скрыть от студентов' : 'Опубликовать урок'}
                    >
                        <span className="cdp-publish-dot" />
                        {lesson.is_published ? 'Опубликован' : 'Черновик'}
                    </button>
                </div>
            </div>

            {isOver && <div className="cdp-drop-indicator" />}
        </div>
    );
};

export default CourseModal;