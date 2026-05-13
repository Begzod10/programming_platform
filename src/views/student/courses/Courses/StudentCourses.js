import React, { useState, useEffect, useCallback, useRef } from 'react';
import './StudentCourses.css';
import StudentCoursePage from '../CoursePage/StudentCoursePage';
import StudentLessonPage from '../LessonPage/StudentLessonPage';
import { API_URL, useHttp, headers } from '../../../../api/search/base';

/* ─── helpers ─── */
const parseListField = (val) => {
  if (!val) return [];
  if (Array.isArray(val)) return val.map((s) => String(s).trim()).filter(Boolean);
  if (typeof val === 'string') {
    const t = val.trim();
    if (t.startsWith('[')) {
      try {
        const p = JSON.parse(t);
        if (Array.isArray(p)) return p.map((s) => String(s).trim()).filter(Boolean);
      } catch {}
    }
    return t.split(',').map((s) => s.trim()).filter(Boolean);
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
  is_multiple_select: ex.is_multiple_select || false,
  correct_answers:    ex.correct_answers    || '',
  correct_order:      ex.correct_order      || '',
  hint:               ex.hint               || '',
  explanation:        ex.explanation        || '',
  difficulty_level:   ex.difficulty_level   || '',
  points:             ex.points             || 0,
  order:              ex.order              || 0,
});

const apiToLesson = (l, isCompleted = false, exercises = []) => {
  const sections = [
    l.text_content ? { id: `t${l.id}`, type: 'text',  label: 'Текст', html: l.text_content } : null,
    l.code_content ? { id: `c${l.id}`, type: 'code',  label: 'Код',   lang: l.code_language || 'javascript', code: l.code_content } : null,
    l.video_url    ? { id: `v${l.id}`, type: 'video', label: 'Видео', videoUrl: l.video_url } : null,
    l.image_url    ? { id: `i${l.id}`, type: 'image', label: 'Фото',  imgUrl: l.image_url }  : null,
    l.file_url     ? { id: `f${l.id}`, type: 'file',  label: 'Файл',  fileName: l.file_url } : null,
    (l.task_title || l.task_description || l.task_requirements || l.task_technologies || l.task_deadline_days)
      ? {
          id:           `p${l.id}`,
          type:         'project',
          label:        l.task_title         || 'Loyiha',
          description:  l.task_description   || '',
          requirements: l.task_requirements  || '',
          techStack:    l.task_technologies  || '',
          deadline:     l.task_deadline_days || '',
        }
      : null,
  ].filter(Boolean);

  if (exercises.length > 0) {
    sections.push({
      id:        `e${l.id}`,
      type:      'exercise',
      label:     'Упражнения',
      exercises: exercises.map(apiToExercise),
    });
  }

  return {
    id:                  l.id,
    title:               l.title,
    chapter:             l.chapter   || '',
    image:               l.image_url || '',
    completed:           isCompleted,
    progress_percentage: l.progress_percentage || 0,
    order:               l.order     || 0,
    is_published:        l.is_published ?? true,
    sections,
  };
};

/* ─── nav persistence ─── */
const NAV_KEY  = 'student_nav';
const saveNav  = (view, courseId = null, lessonId = null) =>
  localStorage.setItem(NAV_KEY, JSON.stringify({ view, courseId, lessonId }));
const loadNav  = () => {
  try { return JSON.parse(localStorage.getItem(NAV_KEY)) || { view: 'courses', courseId: null, lessonId: null }; }
  catch { return { view: 'courses', courseId: null, lessonId: null }; }
};
const clearNav = () => localStorage.removeItem(NAV_KEY);

/* ═══════════════════════════════════════════
   CARD SKELETON
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

/* ═══════════════════════════════════════════
   COURSE CARD
═══════════════════════════════════════════ */
const CourseCard = ({ course, onOpen }) => {
  const lessons      = course.lessons || [];
  const total        = lessons.length > 0 ? lessons.length : (course.lessons_count || 0);
  const completedCnt = lessons.filter((l) => l.completed).length;

  // Если уроки ещё не загружены — берём progress_percentage прямо из API
  const progress = lessons.length > 0
    ? Math.round((completedCnt / lessons.length) * 100)
    : Math.round(course.progress_percentage || 0);

  const circumference = 2 * Math.PI * 20;
  const dash          = (progress / 100) * circumference;

  return (
    <div className="sc-card" onClick={onOpen}>
      <div className="sc-card-img-wrap">
        {course.image
          ? <img src={course.image} alt={course.title} className="sc-card-img" />
          : <div className="sc-card-img-placeholder"><span>📚</span></div>
        }
        <div className="sc-card-img-overlay" />

        {course.difficulty_level && (
          <span className="sc-card-diff">{course.difficulty_level}</span>
        )}

        <div className="sc-ring-wrap">
          <svg viewBox="0 0 50 50" className="sc-ring-svg">
            <circle cx="25" cy="25" r="20" fill="none" stroke="rgba(255,255,255,0.18)" strokeWidth="4" />
            <circle
              cx="25" cy="25" r="20"
              fill="none"
              stroke={progress === 100 ? '#00d49e' : '#a29bfe'}
              strokeWidth="4"
              strokeLinecap="round"
              strokeDasharray={`${dash} ${circumference}`}
              transform="rotate(-90 25 25)"
              style={{ transition: 'stroke-dasharray 0.6s ease' }}
            />
          </svg>
          <span className="sc-ring-label">{progress}%</span>
        </div>
      </div>

      <div className="sc-card-body">
        <h3 className="sc-card-title">{course.title}</h3>

        {course.instructor_name && (
          <p className="sc-card-teacher">
            <span className="sc-teacher-avatar">
              {course.instructor_name.charAt(0).toUpperCase()}
            </span>
            {course.instructor_name}
          </p>
        )}

        <div className="sc-card-meta">
          <span className="sc-meta-pill">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
            {total} уроков
          </span>
          {completedCnt > 0 && (
            <span className="sc-meta-pill done">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              {completedCnt} пройдено
            </span>
          )}
        </div>

        <div className="sc-card-progress">
          <div className="sc-prog-track">
            <div
              className={`sc-prog-fill ${progress === 100 ? 'complete' : ''}`}
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="sc-prog-text">{completedCnt}/{total}</span>
        </div>

        <button className="sc-card-btn" onClick={(e) => { e.stopPropagation(); onOpen(); }}>
          {progress === 100 ? '↺ Повторить' : progress > 0 ? 'Продолжить →' : 'Начать →'}
        </button>
      </div>
    </div>
  );
};

/* ═══════════════════════════════════════════
   MAIN COMPONENT
═══════════════════════════════════════════ */
const StudentCourses = () => {
  const { request } = useHttp();

  const saved = loadNav();

  const [courses,         setCourses]         = useState([]);
  const [loading,         setLoading]         = useState(true);
  const [filter,          setFilter]          = useState('all');
  const [search,          setSearch]          = useState('');
  const [view,            setView]            = useState(saved.view);
  const [activeCourse,    setActiveCourse]    = useState(null);
  const [activeLesson,    setActiveLesson]    = useState(null);
  const [pendingCourseId, setPendingCourseId] = useState(saved.courseId);
  const [pendingLessonId, setPendingLessonId] = useState(saved.lessonId);

  const loadedRef = useRef(new Set());

  /* ── fetch courses ── */
  const fetchCourses = useCallback(() => {
    setLoading(true);
    request(`${API_URL}v1/courses/?t=${Date.now()}`, 'GET', null, headers())
      .then((data) => {
        const list = (Array.isArray(data) ? data : [])
          .filter((c) => c.is_published !== false)
          .map((c) => ({
            ...c,
            image:               c.image_url       || '',
            studentsCount:       c.students_count  || 0,
            progress_percentage: c.progress_percentage || 0,
            lessons:             [],
          }));

        loadedRef.current.clear();
        setCourses(list);

        if (saved.courseId) {
          const found = list.find((c) => c.id === saved.courseId);
          if (found) setActiveCourse(found);
          else { setView('courses'); clearNav(); }
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []); // eslint-disable-line

  useEffect(() => { fetchCourses(); }, []); // eslint-disable-line

  /* ── load lessons for a course ── */
  const loadLessons = useCallback(async (courseId) => {
    if (loadedRef.current.has(courseId)) return;
    loadedRef.current.add(courseId);

    try {
      const raw  = await request(`${API_URL}v1/courses/${courseId}/lessons?t=${Date.now()}`, 'GET', null, headers());
      const list = (Array.isArray(raw) ? raw : []).filter((l) => l.is_published !== false);

      const built = await Promise.all(
        list.map(async (lesson) => {
          // Сначала берём из самого урока
          let isDone = lesson.is_completed === true
            || lesson.completed === true
            || lesson.progress_percentage === 100;

          // Если не определилось — спрашиваем отдельный эндпоинт
          if (!isDone) {
            try {
              const s = await request(`${API_URL}v1/lessons/${lesson.id}/is-completed?t=${Date.now()}`, 'GET', null, headers());
              isDone = s === true || s === 'true';
            } catch {}
          }

          let exercises = [];
          try {
            const ex = await request(
              `${API_URL}v1/courses/${courseId}/lessons/${lesson.id}/exercises?t=${Date.now()}`,
              'GET', null, headers()
            );
            exercises = (Array.isArray(ex) ? ex : []).filter((e) => e.is_active !== false);
          } catch {}

          return apiToLesson(lesson, isDone, exercises);
        })
      );

      const sorted = built.sort((a, b) => (a.order || 0) - (b.order || 0));

      setCourses((cs) =>
        cs.map((c) => {
          if (c.id !== courseId) return c;
          const done     = sorted.filter((l) => l.completed).length;
          const progress = sorted.length > 0 ? Math.round((done / sorted.length) * 100) : 0;
          return { ...c, lessons: sorted, progress_percentage: progress };
        })
      );

      if (pendingLessonId) {
        const found = sorted.find((l) => l.id === pendingLessonId);
        if (found) setActiveLesson(found);
        else { setView('course'); saveNav('course', courseId, null); }
        setPendingLessonId(null);
      }
    } catch (e) {
      console.error(e);
      loadedRef.current.delete(courseId);
    }
  }, [pendingLessonId, request]); // eslint-disable-line

  useEffect(() => {
    if (activeCourse && (view === 'course' || view === 'lesson')) {
      loadLessons(activeCourse.id);
    }
  }, [activeCourse?.id]); // eslint-disable-line

  /* ── mark complete ── */
  const markComplete = useCallback((lessonId) => {
    setCourses((cs) => {
      const course = cs.find((c) => c.id === activeCourse?.id);
      if (!course) return cs;
      const lesson = course.lessons.find((l) => l.id === lessonId);
      if (lesson?.completed) return cs;

      const updated  = course.lessons.map((l) => l.id === lessonId ? { ...l, completed: true } : l);
      const done     = updated.filter((l) => l.completed).length;
      const progress = updated.length > 0 ? Math.round((done / updated.length) * 100) : 0;

      request(`${API_URL}v1/lessons/${lessonId}/complete`, 'POST', null, headers())
        .catch(() => {
          setCourses((prev) =>
            prev.map((c) => {
              if (c.id !== activeCourse?.id) return c;
              const rolled = c.lessons.map((l) => l.id === lessonId ? { ...l, completed: false } : l);
              const d = rolled.filter((l) => l.completed).length;
              return { ...c, lessons: rolled, progress_percentage: rolled.length > 0 ? Math.round((d / rolled.length) * 100) : 0 };
            })
          );
        });

      return cs.map((c) =>
        c.id !== activeCourse?.id ? c : { ...c, lessons: updated, progress_percentage: progress }
      );
    });
  }, [activeCourse?.id, request]);

  /* ── derived ── */
  const currentCourse = activeCourse
    ? courses.find((c) => c.id === activeCourse.id) || activeCourse
    : null;

  const displayed = courses.filter((c) => {
    if (filter === 'inProgress') {
      const p = c.progress_percentage || 0;
      return p > 0 && p < 100;
    }
    if (filter === 'done') return (c.progress_percentage || 0) === 100;
    return true;
  }).filter((c) =>
    !search || c.title?.toLowerCase().includes(search.toLowerCase())
  );

  /* ── navigation ── */
  const goToLesson = (lesson) => {
    setActiveLesson(lesson);
    setView('lesson');
    saveNav('lesson', currentCourse?.id || activeCourse?.id, lesson.id);
  };

  const goToCourse = (course) => {
    setActiveCourse(course);
    setView('course');
    setPendingCourseId(null);
    saveNav('course', course.id, null);
  };

  const goToCourses = () => {
    setView('courses');
    setActiveCourse(null);
    setActiveLesson(null);
    setPendingCourseId(null);
    setPendingLessonId(null);
    clearNav();
    loadedRef.current.clear();
    fetchCourses();
  };

  /* ═══ LESSON VIEW ═══ */
  if (view === 'lesson' && currentCourse) {
    const freshLesson = activeLesson
      ? (currentCourse.lessons.find((l) => l.id === activeLesson.id) || activeLesson)
      : null;

    if (!freshLesson) {
      return <FullLoader text="Загрузка урока…" />;
    }

    return (
      <StudentLessonPage
        lesson={freshLesson}
        course={currentCourse}
        allLessons={currentCourse.lessons}
        onBack={(target) => {
          if (target === 'courses') goToCourses();
          else { setView('course'); setActiveLesson(null); saveNav('course', currentCourse.id, null); }
        }}
        onNavigate={goToLesson}
        onComplete={() => markComplete(freshLesson.id)}
      />
    );
  }

  /* ═══ COURSE VIEW ═══ */
  if (view === 'course' && currentCourse) {
    return (
      <StudentCoursePage
        course={currentCourse}
        onBack={goToCourses}
        onOpenLesson={goToLesson}
      />
    );
  }

  /* ═══ LOADING (restored nav) ═══ */
  if ((view === 'course' || view === 'lesson') && loading) {
    return <FullLoader text="Загрузка…" />;
  }

  /* ═══ COURSES LIST ═══ */
  return (
    <div className="sc-root">
      {/* Header */}
      <div className="sc-header">
        <div className="sc-header-left">
          <h2 className="sc-title">Мои курсы</h2>
          <p className="sc-subtitle">Продолжайте обучение там, где остановились</p>
        </div>

        <div className="sc-header-right">
          <div className="sc-search-wrap">
            <svg className="sc-search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              className="sc-search"
              placeholder="Поиск курса…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            {search && (
              <button className="sc-search-clear" onClick={() => setSearch('')}>✕</button>
            )}
          </div>

          <div className="sc-filters">
            {[
              { key: 'all',        label: 'Все' },
              { key: 'inProgress', label: 'В процессе' },
              { key: 'done',       label: 'Завершённые' },
            ].map(({ key, label }) => (
              <button
                key={key}
                className={`sc-filter ${filter === key ? 'active' : ''}`}
                onClick={() => setFilter(key)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Stats bar */}
      {!loading && courses.length > 0 && (
        <div className="sc-stats-bar">
          <div className="sc-stat-item">
            <span className="sc-stat-num">{courses.length}</span>
            <span className="sc-stat-text">курсов</span>
          </div>
          <div className="sc-stat-divider" />
          <div className="sc-stat-item">
            <span className="sc-stat-num">
              {courses.filter((c) => (c.progress_percentage || 0) === 100).length}
            </span>
            <span className="sc-stat-text">завершено</span>
          </div>
          <div className="sc-stat-divider" />
          <div className="sc-stat-item">
            <span className="sc-stat-num">
              {courses.filter((c) => {
                const p = c.progress_percentage || 0;
                return p > 0 && p < 100;
              }).length}
            </span>
            <span className="sc-stat-text">в процессе</span>
          </div>
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="sc-grid">
          {[1,2,3,4,5,6].map((n) => <CardSkeleton key={n} />)}
        </div>
      ) : displayed.length === 0 ? (
        <div className="sc-empty">
          <div className="sc-empty-icon">
            {search ? '🔍' : '📚'}
          </div>
          <h3 className="sc-empty-title">
            {search ? 'Ничего не найдено' : 'Курсов пока нет'}
          </h3>
          <p className="sc-empty-sub">
            {search
              ? `По запросу «${search}» курсов не найдено`
              : 'Здесь появятся ваши курсы'}
          </p>
          {search && (
            <button className="sc-empty-reset" onClick={() => setSearch('')}>
              Сбросить поиск
            </button>
          )}
        </div>
      ) : (
        <div className="sc-grid">
          {displayed.map((course) => (
            <CourseCard
              key={course.id}
              course={course}
              onOpen={() => goToCourse(course)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

/* ─── Full-screen loader ─── */
const FullLoader = ({ text = 'Загрузка…' }) => (
  <div className="sc-full-loader">
    <div className="sc-spinner">
      <div className="sc-spinner-ring" />
    </div>
    <span>{text}</span>
  </div>
);

export default StudentCourses;