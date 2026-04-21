import React, {useState} from 'react';
import './CourseModal.css';

const CourseDetailPage = ({course, onBack, onOpenLesson, onAddLesson, onEditLesson, onDeleteLesson}) => {
    /* Group lessons by chapter */
    const groupedLessons = () => {
        const noChapter = course.lessons.filter(l => !l.chapter);
        const withChapter = {};
        course.lessons.forEach(l => {
            if (l.chapter) {
                if (!withChapter[l.chapter]) withChapter[l.chapter] = [];
                withChapter[l.chapter].push(l);
            }
        });
        return {withChapter, noChapter};
    };

    const {withChapter, noChapter} = groupedLessons();
    const chapterKeys = Object.keys(withChapter);
    const allEmpty = course.lessons.length === 0;

    /* Lesson index across all lessons (for numbering) */
    const lessonIndex = {};
    course.lessons.forEach((l, i) => { lessonIndex[l.id] = i + 1; });

    return (
        <div className="cdp-container">

            {/* Top bar */}
            <div className="cdp-top-bar">
                <button className="cdp-back-btn" onClick={onBack}>
                    ← Назад к курсам
                </button>
                <button className="cdp-add-lesson-btn" onClick={onAddLesson}>
                    ➕ Добавить урок
                </button>
            </div>

            {/* Banner */}
            <div className="cdp-banner">
                <img src={course.image} alt={course.title} className="cdp-banner-img"/>
                <div className="cdp-banner-overlay">
                    <div className="cdp-banner-content">
                        <h1>{course.title}</h1>
                        <p>{course.description}</p>
                        <div className="cdp-banner-stats">
                            <span>📚 {course.lessons.length} уроков</span>
                            <span>👥 {course.studentsCount} студентов</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Lessons */}
            <h2 className="cdp-section-title">📖 Уроки курса</h2>

            {allEmpty ? (
                <div className="cdp-no-lessons">
                    <div className="cdp-no-lessons-icon">📭</div>
                    <p>В этом курсе пока нет уроков</p>
                </div>
            ) : (
                <>
                    {/* Chapters */}
                    {chapterKeys.map(chapter => (
                        <div key={chapter} className="cdp-chapter-group">
                            <div className="cdp-chapter-label">
                                <span className="cdp-chapter-name">{chapter}</span>
                                <span className="cdp-chapter-count">{withChapter[chapter].length} уроков</span>
                            </div>
                            <div className="cdp-lessons-grid">
                                {withChapter[chapter].map(lesson => (
                                    <LessonCard
                                        key={lesson.id}
                                        lesson={lesson}
                                        index={lessonIndex[lesson.id]}
                                        onOpen={() => onOpenLesson(lesson)}
                                        onEdit={() => onEditLesson(lesson)}
                                        onDelete={() => onDeleteLesson(lesson.id)}
                                    />
                                ))}
                            </div>
                        </div>
                    ))}

                    {/* No-chapter lessons */}
                    {noChapter.length > 0 && (
                        <div className="cdp-chapter-group">
                            {chapterKeys.length > 0 && (
                                <div className="cdp-chapter-label">
                                    <span className="cdp-chapter-name">Без раздела</span>
                                    <span className="cdp-chapter-count">{noChapter.length} уроков</span>
                                </div>
                            )}
                            <div className="cdp-lessons-grid">
                                {noChapter.map(lesson => (
                                    <LessonCard
                                        key={lesson.id}
                                        lesson={lesson}
                                        index={lessonIndex[lesson.id]}
                                        onOpen={() => onOpenLesson(lesson)}
                                        onEdit={() => onEditLesson(lesson)}
                                        onDelete={() => onDeleteLesson(lesson.id)}
                                    />
                                ))}
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

/* ─── Lesson Card ─── */
const LessonCard = ({lesson, index, onOpen, onEdit, onDelete}) => {
    const blockCount = lesson.sections?.length || 0;

    return (
        <div className="cdp-lesson-card" onClick={onOpen}>
            <div className="cdp-lesson-preview">
                {lesson.image
                    ? <img src={lesson.image} alt={lesson.title}/>
                    : <div className="cdp-lesson-no-img">📹</div>
                }
                <span className="cdp-lesson-num-badge">Урок {index}</span>

                {/* Action buttons — передаём onDelete напрямую, confirm в родителе */}
                <div className="cdp-lesson-card-actions" onClick={e => e.stopPropagation()}>
                    <button
                        className="cdp-lesson-action-btn edit"
                        onClick={e => { e.stopPropagation(); onEdit(); }}
                        aria-label="Редактировать урок"
                    >✏️</button>
                    <button
                        className="cdp-lesson-action-btn del"
                        onClick={e => { e.stopPropagation(); onDelete(); }}
                        aria-label="Удалить урок"
                    >🗑️</button>
                </div>

                <div className="cdp-lesson-play-overlay">
                    <div className="cdp-lesson-play-circle">▶</div>
                </div>
            </div>

            <div className="cdp-lesson-info">
                <h4>{lesson.title}</h4>
                <div className="cdp-lesson-meta">
                    {blockCount > 0 && (
                        <span className="cdp-lesson-blocks-count">
                            {blockCount} {blockCount === 1 ? 'блок' : blockCount < 5 ? 'блока' : 'блоков'}
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CourseDetailPage;