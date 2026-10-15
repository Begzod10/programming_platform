import React, { useEffect, useMemo, useState } from 'react';
import './StudentCoursePage.css';
import { useTranslation } from '../../../../i18n/useTranslation';
import AppHeader from '../../../../components/appheader/AppHeader';
import { Lock, Check, Play, ChevronLeft, Rocket, Clock, Users, CheckCircle2, Loader, Unlock, LockKeyhole } from 'lucide-react';

const prefersReduced = () =>
  typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function CountUp({ value, duration = 900 }) {
  const [v, setV] = useState(prefersReduced() ? value : 0);
  useEffect(() => {
    if (prefersReduced()) { setV(value); return; }
    let raf; const t0 = performance.now();
    const loop = (now) => {
      const t = Math.min(1, (now - t0) / duration);
      setV(Math.round(value * (1 - Math.pow(1 - t, 3))));
      if (t < 1) raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, [value, duration]);
  return <>{v}</>;
}

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

const DIFF_LABEL = {
  Beginner: { ru: 'НАЧИНАЮЩИЙ', uz: "BOSHLANG'ICH" },
  Intermediate: { ru: 'СРЕДНИЙ', uz: "O'RTA" },
  Advanced: { ru: 'ПРОДВИНУТЫЙ', uz: "ILG'OR" },
};

/* ── one lesson card ── */
function LessonCard({ node, ru, onOpen }) {
  const { l, status, index } = node;
  const hasVideo = l.sections?.some((s) => s.type === 'video');
  const hasProject = l.sections?.some((s) => s.type === 'project');
  const blocks = l.sections?.length || 0;
  const locked = status === 'locked';
  const pct = l.completed ? 100 : (l.progress_pct || 0);
  const thumb = l.image
    ? { backgroundImage: `url(${l.image})` }
    : { background: l.color || THUMB_COLORS[(index - 1) % THUMB_COLORS.length] };

  const statusChip =
    status === 'done' ? { cls: 'done', icon: <Check size={13} />, label: ru ? 'Пройдено' : "O'tildi" }
      : status === 'in_progress' ? { cls: 'prog', icon: <Loader size={13} />, label: ru ? 'В процессе' : 'Davom etmoqda' }
        : status === 'available' ? { cls: 'avail', icon: <Unlock size={13} />, label: ru ? 'Доступно' : 'Mavjud' }
          : { cls: 'locked', icon: <Lock size={13} />, label: ru ? 'Закрыто' : 'Bloklangan' };

  return (
    <button
      className={`scd-card scd-card--${status} scd-rise`}
      style={{ animationDelay: `${Math.min(index, 12) * 0.03}s` }}
      onClick={() => !locked && onOpen(l)}
      disabled={locked}>
      <div className="scd-card-thumb" style={thumb}>
        <div className="scd-card-thumb-dim" />
        <span className="scd-card-num">{index}</span>
        <span className={`scd-card-status scd-card-status--${statusChip.cls}`}>{statusChip.icon} {statusChip.label}</span>
        {locked ? (
          <span className="scd-card-lock"><Lock size={22} /></span>
        ) : (
          <span className="scd-card-play"><Play size={18} fill="currentColor" /></span>
        )}
      </div>
      <div className="scd-card-body">
        <div className="scd-card-title">{l.title}</div>
        <div className="scd-card-tags">
          <span className="scd-tag">{blocks} {ru ? 'блок' : 'blok'}</span>
          {hasVideo && <span className="scd-tag scd-tag--video"><Play size={10} fill="currentColor" /> {ru ? 'Видео' : 'Video'}</span>}
          {hasProject && <span className="scd-tag scd-tag--project"><Rocket size={10} /> {ru ? 'Проект' : 'Loyiha'}</span>}
        </div>
        <div className="scd-card-bar"><div className="scd-card-fill" style={{ width: `${pct}%` }} /></div>
      </div>
    </button>
  );
}

const StudentCoursePage = ({ course, onBack, onOpenLesson }) => {
  const { lang } = useTranslation();
  const ru = lang === 'ru';

  const lessons = useMemo(
    () => (course.lessons || []).filter((l) => l.is_published !== false),
    [course.lessons]
  );

  // Sequential status: done → first-open → locked.
  const nodes = useMemo(() => lessons.map((l, i) => {
    const prev = i > 0 ? lessons[i - 1] : null;
    const locked = prev && !prev.completed && !l.completed;
    let status;
    if (l.completed) status = 'done';
    else if (locked) status = 'locked';
    else status = (l.progress_pct || 0) > 0 ? 'in_progress' : 'available';
    return { l, status, index: i + 1 };
  }), [lessons]);

  const total = lessons.length;
  const counts = {
    done: nodes.filter((n) => n.status === 'done').length,
    in_progress: nodes.filter((n) => n.status === 'in_progress').length,
    available: nodes.filter((n) => n.status === 'available').length,
    locked: nodes.filter((n) => n.status === 'locked').length,
  };
  const progress = total > 0 ? Math.round((counts.done / total) * 100) : Math.round(course.progress_percentage || 0);
  const nextLesson = lessons.find((l) => !l.completed);
  const diffLabel = DIFF_LABEL[course.difficulty_level] ? (ru ? DIFF_LABEL[course.difficulty_level].ru : DIFF_LABEL[course.difficulty_level].uz) : course.difficulty_level;

  const R = 46, CIRC = 2 * Math.PI * R, off = CIRC * (1 - progress / 100);

  const stats = [
    { key: 'done', icon: <CheckCircle2 size={18} />, n: counts.done, label: ru ? 'завершено' : 'tugatildi', cls: 'done' },
    { key: 'prog', icon: <Loader size={18} />, n: counts.in_progress, label: ru ? 'в процессе' : 'davom etmoqda', cls: 'prog' },
    { key: 'avail', icon: <LockKeyhole size={18} />, n: counts.available, label: ru ? 'доступно' : 'mavjud', cls: 'avail' },
    { key: 'locked', icon: <Lock size={18} />, n: counts.locked, label: ru ? 'закрыто' : 'bloklangan', cls: 'locked' },
  ];

  return (
    <div className="scd-dark">
      <AppHeader />
      <div className="scd-shell">

        <button className="scd-back" onClick={onBack}>
          <ChevronLeft size={17} /> {ru ? 'Все курсы' : 'Barcha kurslar'}
        </button>

        {/* ── hero ── */}
        <div className="scd-hero scd-rise">
          {course.image && <img src={course.image} alt="" className="scd-hero-bg" />}
          <div className="scd-hero-dim" />
          <div className="scd-hero-body">
            <div className="scd-hero-left">
              {diffLabel && <span className="scd-hero-diff">{diffLabel}</span>}
              <h1 className="scd-hero-title">{course.title}</h1>
              {course.description && <p className="scd-hero-desc">{course.description}</p>}
              <div className="scd-hero-meta">
                {course.instructor_name && (
                  <span className="scd-hero-meta-item">
                    <span className="scd-hero-ava">{course.instructor_name.charAt(0).toUpperCase()}</span>
                    {course.instructor_name}
                  </span>
                )}
                <span className="scd-hero-meta-item"><Clock size={15} /> {total} {ru ? 'уроков' : 'dars'}</span>
                {course.students_count > 0 && <span className="scd-hero-meta-item"><Users size={15} /> {course.students_count} {ru ? 'студентов' : 'talaba'}</span>}
              </div>
              {nextLesson ? (
                <button className="scd-hero-cta" onClick={() => onOpenLesson(nextLesson)}>
                  <Rocket size={16} /> {counts.done > 0 ? (ru ? 'Продолжить' : 'Davom etish') : (ru ? 'Начать курс' : 'Kursni boshlash')}
                </button>
              ) : total > 0 ? (
                <span className="scd-hero-badge"><Check size={16} /> {ru ? 'Курс завершён!' : 'Kurs tugatildi!'}</span>
              ) : null}
            </div>
            <div className="scd-hero-ring">
              <svg viewBox="0 0 110 110" width="128" height="128">
                <defs>
                  <linearGradient id="scdRing" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0" stopColor="#7ef0a3" /><stop offset="1" stopColor="#22d3ee" />
                  </linearGradient>
                </defs>
                <circle cx="55" cy="55" r={R} fill="none" stroke="rgba(255,255,255,.12)" strokeWidth="8" />
                <circle cx="55" cy="55" r={R} fill="none" stroke="url(#scdRing)" strokeWidth="8" strokeLinecap="round"
                  strokeDasharray={CIRC} strokeDashoffset={off} transform="rotate(-90 55 55)"
                  style={{ transition: 'stroke-dashoffset 1.3s cubic-bezier(.2,.75,.25,1)', filter: 'drop-shadow(0 0 7px rgba(34,211,238,.5))' }} />
              </svg>
              <div className="scd-hero-ring-txt">
                <span className="scd-hero-ring-pct">{progress}%</span>
                <span className="scd-hero-ring-sub">{ru ? 'пройдено' : "o'tildi"}</span>
              </div>
            </div>
          </div>
        </div>

        {/* ── stats pills ── */}
        <div className="scd-stats">
          {stats.map((s, i) => (
            <div className={`scd-stat scd-stat--${s.cls} scd-rise`} style={{ animationDelay: `${0.05 + i * 0.07}s` }} key={s.key}>
              <span className="scd-stat-ic">{s.icon}</span>
              <span className="scd-stat-n"><CountUp value={s.n} /></span>
              <span className="scd-stat-lbl">{s.label}</span>
            </div>
          ))}
          <div className="scd-stat scd-stat--bar scd-rise" style={{ animationDelay: '.33s' }}>
            <div className="scd-stat-bar-track"><div className="scd-stat-bar-fill" style={{ width: `${progress}%` }} /></div>
            <span className="scd-stat-bar-pct"><CountUp value={progress} />%</span>
          </div>
        </div>

        {/* ── lessons ── */}
        <div className="scd-section-head">
          <h2 className="scd-section-title">{ru ? 'Программа курса' : 'Kurs dasturi'}</h2>
          {total > 0 && <span className="scd-section-sum">{counts.done}/{total} {ru ? 'пройдено' : "o'tildi"}</span>}
        </div>

        {total === 0 ? (
          <div className="scd-empty">📭 {ru ? 'Уроков пока нет' : "Darslar yo'q"}</div>
        ) : (
          <div className="scd-grid">
            {nodes.map((node) => (
              <LessonCard key={node.l.id} node={node} ru={ru} onOpen={onOpenLesson} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentCoursePage;
