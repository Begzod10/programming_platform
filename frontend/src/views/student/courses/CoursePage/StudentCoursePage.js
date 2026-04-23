import React from 'react';
import './StudentCoursePage.css';

const StudentCoursePage = ({ course, onBack, onOpenLesson }) => {
  // Используем актуальные данные из пропса course
  // Если массив уроков пуст, берем процент из объекта курса (для подстраховки)
  const total = course.lessons ? course.lessons.length : (course.lessonsCount || 0);
  const completedLessons = course.lessons ? course.lessons.filter(l => l.completed).length : 0;

  // РАСЧЕТ ПРОГРЕССА:
  // Если уроки загружены, считаем по ним. Если нет — верим цифре из бэкенда.
  const progress = (course.lessons && course.lessons.length > 0)
    ? Math.round((completedLessons / total) * 100)
    : Math.round(course.progress_percentage || 0);

  /* Группировка по главам */
  const lessonsArray = course.lessons || [];
  const noChapter = lessonsArray.filter(l => !l.chapter);
  const byChapter = {};

  lessonsArray.forEach(l => {
    if (l.chapter) {
      if (!byChapter[l.chapter]) byChapter[l.chapter] = [];
      byChapter[l.chapter].push(l);
    }
  });
  const chapterKeys = Object.keys(byChapter);

  /* Глобальный индекс уроков */
  const lessonIdx = {};
  lessonsArray.forEach((l, i) => { lessonIdx[l.id] = i + 1; });

  return (
    <div className="scp-container">

      {/* Top bar */}
      <div className="scp-top-bar">
        <button className="scp-back-btn" onClick={onBack}>← Назад к курсам</button>
      </div>

      {/* Banner */}
      <div className="scp-banner">
        <img src={course.image} alt={course.title} className="scp-banner-img" />
        <div className="scp-banner-overlay">
          <div className="scp-banner-content">
            <h1>{course.title}</h1>
            <p className="scp-banner-desc">{course.description}</p>
            <p className="scp-banner-teacher">👨‍🏫 {course.teacher}</p>
            <div className="scp-banner-stats">
              <span>📚 {total} уроков</span>
              <span>👥 {course.studentsCount || 0} студентов</span>
              {completedLessons > 0 && <span>✓ {completedLessons} пройдено</span>}
            </div>
          </div>

          {/* Progress ring */}
          <div className="scp-progress-ring-wrap">
            <svg viewBox="0 0 100 100" className="scp-progress-ring">
              <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth="8"/>
              <circle
                cx="50" cy="50" r="42"
                fill="none" stroke="white" strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 42}`}
                strokeDashoffset={`${2 * Math.PI * 42 * (1 - progress / 100)}`}
                transform="rotate(-90 50 50)"
                style={{ transition: 'stroke-dashoffset 1s ease' }}
              />
            </svg>
            <div className="scp-progress-ring-text">
              <span className="scp-progress-pct">{progress}%</span>
              <span className="scp-progress-label">пройдено</span>
            </div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="scp-banner-progress">
          <div className="scp-banner-progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {/* Lessons */}
      <h2 className="scp-section-title">📖 Уроки курса</h2>

      {total === 0 ? (
        <div className="scp-no-lessons">
          <div className="scp-no-lessons-icon">📭</div>
          <p>В этом курсе пока нет уроков</p>
        </div>
      ) : (
        <>
          {/* По главам */}
          {chapterKeys.map(ch => (
            <div key={ch} className="scp-chapter-group">
              <div className="scp-chapter-label">
                <span className="scp-chapter-name">{ch}</span>
                <span className="scp-chapter-count">{byChapter[ch].length} уроков</span>
              </div>
              <div className="scp-lessons-grid">
                {byChapter[ch].map(l => (
                  <LessonCard
                    key={l.id}
                    lesson={l}
                    index={lessonIdx[l.id]}
                    onOpen={() => onOpenLesson(l)}
                  />
                ))}
              </div>
            </div>
          ))}

          {/* Без раздела */}
          {noChapter.length > 0 && (
            <div className="scp-chapter-group">
              {chapterKeys.length > 0 && (
                <div className="scp-chapter-label">
                  <span className="scp-chapter-name">Без раздела</span>
                  <span className="scp-chapter-count">{noChapter.length} уроков</span>
                </div>
              )}
              <div className="scp-lessons-grid">
                {noChapter.map(l => (
                  <LessonCard
                    key={l.id}
                    lesson={l}
                    index={lessonIdx[l.id]}
                    onOpen={() => onOpenLesson(l)}
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
const LessonCard = ({ lesson, index, onOpen }) => {
  const blockCount = lesson.sections?.length || 0;

  return (
    <div className={`scp-lesson-card ${lesson.completed ? 'done' : ''}`} onClick={onOpen}>
      <div className="scp-lesson-preview">
        {lesson.image
          ? <img src={lesson.image} alt={lesson.title} />
          : <div className="scp-lesson-no-img">📹</div>
        }

        <span className="scp-lesson-num">{index}</span>

        {lesson.completed && (
          <span className="scp-lesson-done-badge">✓</span>
        )}

        <div className="scp-lesson-play-overlay">
          <div className="scp-play-circle">
            {lesson.completed ? '↺' : '▶'}
          </div>
        </div>
      </div>

      <div className="scp-lesson-info">
        <h4>{lesson.title}</h4>
        <div className="scp-lesson-meta">
          {blockCount > 0 && (
            <span className="scp-blocks-count">
              {blockCount} {blockCount === 1 ? 'блок' : blockCount < 5 ? 'блока' : 'блоков'}
            </span>
          )}
          {lesson.completed && (
            <span className="scp-completed-label">Пройдено</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudentCoursePage;