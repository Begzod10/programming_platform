import React, { useState, useMemo } from 'react';
import './StudentCoursePage.css';
import { useTranslation } from '../../../../i18n/useTranslation';

const THUMB_COLORS = [
  'linear-gradient(135deg, #1a0b3e 0%, #2d1b69 100%)',
  'linear-gradient(135deg, #0d1b3e 0%, #1a3a6e 100%)',
  'linear-gradient(135deg, #0b2e1e 0%, #1a5c3a 100%)',
  'linear-gradient(135deg, #2a1a0b 0%, #5a3a1a 100%)',
  'linear-gradient(135deg, #1e0b2e 0%, #3d1a5c 100%)',
  'linear-gradient(135deg, #0b1e2e 0%, #1a3a5c 100%)',
  'linear-gradient(135deg, #2e0b1a 0%, #5c1a38 100%)',
  'linear-gradient(135deg, #1a1a0b 0%, #3a3a1a 100%)',
];

/* ═══════════════════════════════════════════
   LESSON CARD
═══════════════════════════════════════════ */
const LessonCard = ({ lesson, index, isLocked, onOpen, accentColor, t, lang }) => {
  const hasVideo   = lesson.sections?.some((s) => s.type === 'video');
  const hasProject = lesson.sections?.some((s) => s.type === 'project');
  const blockCount = lesson.sections?.length || 0;

  const accentGrad = accentColor
    ? `linear-gradient(135deg, ${accentColor}cc 0%, ${accentColor}55 100%)`
    : null;
  const thumbStyle = lesson.image
    ? {}
    : { background: lesson.color || accentGrad || THUMB_COLORS[(index - 1) % THUMB_COLORS.length] };

  const lockedLabel = isLocked ? t('locked_msg') : undefined;

  const blockLabel = (n) => {
    if (lang === 'uz') return `${n} blok`;
    if (n === 1) return `${n} блок`;
    if (n < 5)   return `${n} блока`;
    return `${n} блоков`;
  };

  return (
    <div
      className={`scp-lesson-card${lesson.completed ? ' is-done' : ''}${isLocked ? ' is-locked' : ''}`}
      onClick={isLocked ? undefined : onOpen}
      role="button"
      tabIndex={0}
      aria-disabled={isLocked || undefined}
      aria-label={lockedLabel}
      title={lockedLabel}
      onKeyDown={isLocked ? undefined : (e) => e.key === 'Enter' && onOpen()}
    >
      <div className="scp-card-thumb" style={thumbStyle}>
        {lesson.image ? (
          <img src={lesson.image} alt="" className="scp-card-thumb-img" />
        ) : (
          <div className="scp-card-thumb-placeholder">
            {lesson.icon || '📖'}
          </div>
        )}
        <div className="scp-card-thumb-overlay" />
        <div className="scp-card-num">{index}</div>
        {lesson.completed && (
          <div className="scp-card-done-badge">{t('done_badge')}</div>
        )}
        {isLocked && (
          <div className="scp-card-lock-overlay">🔒</div>
        )}
        {hasVideo && !isLocked && (
          <div className="scp-card-play" aria-hidden="true">
            <svg width="11" height="13" viewBox="0 0 11 13" fill="white">
              <path d="M0.5 1.13397C0.5 0.514903 1.18918 0.140562 1.7 0.5L10.3 6.36603C10.7804 6.70557 10.7804 7.42443 10.3 7.76397L1.7 13.5C1.18918 13.8594 0.5 13.4851 0.5 12.866V1.13397Z"/>
            </svg>
          </div>
        )}
      </div>

      <div className="scp-card-body">
        <h4 className="scp-card-title">{lesson.title}</h4>
        <div className="scp-card-tags">
          {blockCount > 0 && (
            <span className="scp-ctag">{blockLabel(blockCount)}</span>
          )}
          {hasVideo   && <span className="scp-ctag tag-video">{t('tag_video')}</span>}
          {hasProject && <span className="scp-ctag tag-project">{t('tag_project')}</span>}
        </div>
        <div className="scp-card-prog">
          <div
            className={`scp-card-prog-fill${lesson.completed ? ' done' : ''}`}
            style={{ width: lesson.completed ? '100%' : `${lesson.progress_pct || 0}%` }}
          />
        </div>
      </div>
    </div>
  );
};

/* ═══════════════════════════════════════════
   CHAPTER BLOCK
═══════════════════════════════════════════ */
const ChapterBlock = ({ title, lessons, startIndex, allLessons, onOpenLesson, accentColor, t, lang }) => {
  const [open, setOpen] = useState(true);
  const done  = lessons.filter((l) => l.completed).length;
  const total = lessons.length;
  const pct   = total > 0 ? Math.round((done / total) * 100) : 0;

  const lessonsCountLabel = lang === 'uz'
    ? `${total} dars`
    : total === 1 ? `${total} урок` : total < 5 ? `${total} урока` : `${total} уроков`;

  return (
    <div className="scp-chapter">
      <button className="scp-chapter-head" onClick={() => setOpen((o) => !o)}>
        <div className="scp-chapter-left">
          <div className="scp-chapter-icon">{open ? '▾' : '▸'}</div>
          <span className="scp-chapter-name">{title || t('lessons_label')}</span>
          <span className="scp-chapter-count">{lessonsCountLabel}</span>
        </div>
        <div className="scp-chapter-prog-wrap">
          <div className="scp-chapter-prog-track">
            <div className="scp-chapter-prog-fill" style={{ width: `${pct}%` }} />
          </div>
          <span className="scp-chapter-prog-label">{done}/{total}</span>
        </div>
      </button>

      {open && (
        <div className="scp-lessons-grid">
          {lessons.map((lesson, i) => {
            const globalIdx  = startIndex + i;
            const prevLesson = allLessons[globalIdx - 1];
            const isLocked   = !!prevLesson && !prevLesson.completed && !lesson.completed;
            return (
              <LessonCard
                key={lesson.id}
                lesson={lesson}
                index={globalIdx + 1}
                isLocked={isLocked}
                onOpen={() => onOpenLesson(lesson)}
                accentColor={accentColor}
                t={t}
                lang={lang}
              />
            );
          })}
        </div>
      )}
    </div>
  );
};

/* ═══════════════════════════════════════════
   MAIN
═══════════════════════════════════════════ */
const StudentCoursePage = ({ course, onBack, onOpenLesson }) => {
  const { t, lang } = useTranslation();

  const lessons = useMemo(
    () => (course.lessons || []).filter((l) => l.is_published !== false),
    [course.lessons]
  );

  const total     = lessons.length;
  const completed = lessons.filter((l) => l.completed).length;
  const progress  = total > 0
    ? Math.round((completed / total) * 100)
    : Math.round(course.progress_percentage || 0);

  const { groups } = useMemo(() => {
    const map = new Map();
    lessons.forEach((l) => {
      const key = l.chapter || '__none__';
      if (!map.has(key)) map.set(key, []);
      map.get(key).push(l);
    });
    const groups = [];
    let offset = 0;
    map.forEach((ls, key) => {
      groups.push({ title: key === '__none__' ? '' : key, lessons: ls, startIndex: offset });
      offset += ls.length;
    });
    return { groups };
  }, [lessons]);

  const R    = 44;
  const CIRC = 2 * Math.PI * R;
  const off  = CIRC * (1 - progress / 100);

  const nextLesson = lessons.find((l) => !l.completed);

  const totalLessonsLabel = lang === 'uz'
    ? `${total} dars`
    : total === 1 ? `${total} урок` : total < 5 ? `${total} урока` : `${total} уроков`;

  const progressSummary = lang === 'uz'
    ? `${completed} / ${total} dan o'tildi`
    : `${completed} ${t('of')} ${total} ${t('passed')}`;

  return (
    <div className="scp-root">

      <button className="scp-back" onClick={onBack}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        {t('all_courses')}
      </button>

      <div className="scp-hero">
        <div
          className="scp-hero-bg"
          style={course.color_accent ? {
            background: `linear-gradient(135deg, ${course.color_accent}22 0%, #0d0d2b 100%)`
          } : undefined}
        >
          {course.image && <img src={course.image} alt="" className="scp-hero-bg-img" />}
          <div
            className="scp-hero-bg-dim"
            style={course.color_accent ? {
              background: `linear-gradient(135deg, ${course.color_accent}33 0%, rgba(10,8,30,0.95) 60%)`
            } : undefined}
          />
          {course.color_accent && (
            <div style={{
              position: 'absolute', inset: 0,
              background: `radial-gradient(ellipse at 80% 50%, ${course.color_accent}18 0%, transparent 65%)`,
              pointerEvents: 'none',
            }} />
          )}
        </div>

        <div className="scp-hero-body">
          <div className="scp-hero-left">
            {course.difficulty_level && (
              <span className="scp-hero-diff">{course.difficulty_level}</span>
            )}
            <h1 className="scp-hero-title">{course.title}</h1>
            {course.description && (
              <p className="scp-hero-desc">{course.description}</p>
            )}

            <div className="scp-hero-meta">
              {course.instructor_name && (
                <div className="scp-hero-teacher">
                  <div className="scp-hero-teacher-av">
                    {course.instructor_name.charAt(0).toUpperCase()}
                  </div>
                  <span>{course.instructor_name}</span>
                </div>
              )}
              <div className="scp-hero-pill">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                </svg>
                {totalLessonsLabel}
              </div>
              <div className="scp-hero-pill">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
                {course.students_count || 0} {t('students_count')}
              </div>
            </div>

            {nextLesson && (
              <button className="scp-hero-cta" onClick={() => onOpenLesson(nextLesson)}>
                {completed > 0 ? t('continue_learning') : t('start_course')}
              </button>
            )}
            {!nextLesson && total > 0 && (
              <div className="scp-hero-done-badge">{t('course_done')}</div>
            )}
          </div>

          <div className="scp-hero-ring-wrap">
            <svg viewBox="0 0 100 100" className="scp-hero-ring">
              <circle cx="50" cy="50" r={R} fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth="7" />
              <circle
                cx="50" cy="50" r={R}
                fill="none"
                stroke={progress === 100 ? '#00d49e' : 'white'}
                strokeWidth="7"
                strokeLinecap="round"
                strokeDasharray={CIRC}
                strokeDashoffset={off}
                transform="rotate(-90 50 50)"
                style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1)' }}
              />
            </svg>
            <div className="scp-hero-ring-text">
              <span className="scp-ring-pct">{progress}%</span>
              <span className="scp-ring-sub">{t('passed')}</span>
            </div>
          </div>
        </div>

        <div className="scp-hero-prog">
          <div
            className={`scp-hero-prog-fill${progress === 100 ? ' done' : ''}`}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="scp-section-header">
        <h2 className="scp-section-title">{t('course_programme')}</h2>
        {total > 0 && (
          <span className="scp-section-summary">{progressSummary}</span>
        )}
      </div>

      {total === 0 ? (
        <div className="scp-no-lessons">
          <span className="scp-no-lessons-icon">📭</span>
          <p>{t('no_lessons')}</p>
        </div>
      ) : (
        <div className="scp-chapters">
          {groups.map((g, gi) => (
            <ChapterBlock
              key={gi}
              title={g.title}
              lessons={g.lessons}
              startIndex={g.startIndex}
              allLessons={lessons}
              onOpenLesson={onOpenLesson}
              accentColor={course.color_accent}
              t={t}
              lang={lang}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default StudentCoursePage;
