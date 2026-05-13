import React, { useState, useCallback, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
import './StudentLessonPage.css';
import { SECTION_TYPES, getYTId } from '../../../../constants/courseUtils';
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

/* ═══════════════════════════════════════════
   YOUTUBE PLAYER
═══════════════════════════════════════════ */
const YouTubePlayer = ({ ytId, onVideoComplete }) => {
  const containerId  = useRef(`yt-${ytId}-${Math.random().toString(36).slice(2)}`).current;
  const playerRef    = useRef(null);
  const playerObjRef = useRef(null);
  const completedRef = useRef(false);

  useEffect(() => {
    const init = () => {
      if (!playerRef.current) return;
      playerObjRef.current = new window.YT.Player(containerId, {
        videoId: ytId,
        playerVars: { rel: 0, modestbranding: 1 },
        events: {
          onStateChange: (e) => {
            if (e.data === 0 && !completedRef.current) {
              completedRef.current = true;
              onVideoComplete?.();
            }
          },
        },
      });
    };

    if (!window.YT) {
      const tag  = document.createElement('script');
      tag.src    = 'https://www.youtube.com/iframe_api';
      document.head.appendChild(tag);
    }

    if (window.YT?.Player) {
      init();
    } else {
      const prev                     = window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady = () => { prev?.(); init(); };
    }

    return () => {
      try { playerObjRef.current?.destroy(); } catch {}
    };
  }, [ytId]); // eslint-disable-line

  return (
    <div className="slp-yt-wrap">
      <div id={containerId} ref={playerRef} style={{ width: '100%', aspectRatio: '16/9', borderRadius: 14 }} />
    </div>
  );
};

/* ═══════════════════════════════════════════
   EXERCISE CARD
═══════════════════════════════════════════ */
const ExerciseCard = ({ ex, courseId, lessonId, index }) => {
  const { request } = useHttp();

  const opts     = parseListField(ex.options);
  const dragOrig = parseListField(ex.drag_items);

  const [text,       setText]       = useState('');
  const [selected,   setSelected]   = useState([]);
  const [fills,      setFills]      = useState([]);
  const [avail,      setAvail]      = useState(() => [...dragOrig].sort(() => Math.random() - 0.5));
  const [dropped,    setDropped]    = useState([]);
  const [result,     setResult]     = useState(null);
  const [aiFb,       setAiFb]       = useState('');
  const [score,      setScore]      = useState(null);
  const [busy,       setBusy]       = useState(false);
  const [hint,       setHint]       = useState(false);

  const isDone = result === 'correct' || result === 'submitted';
  const exType = ex.exercise_type;

  const buildAnswer = () => {
    if (exType === 'fill_in_blank')   return fills.join(',');
    if (exType === 'drag_and_drop')   return JSON.stringify(dropped.map((s) => s.trim()));
    if (exType === 'multiple_choice') return selected.join(',');
    return text.trim();
  };

  const handleSubmit = async () => {
    const ans = buildAnswer();
    if (!ans) return;
    setBusy(true); setAiFb(''); setScore(null);
    try {
      const res = await request(
        `${API_URL}v1/courses/${courseId}/lessons/${lessonId}/exercises/${ex.id}/submit`,
        'POST',
        JSON.stringify({ student_answer: ans }),
        headers()
      );
      setResult(res?.is_correct === true ? 'correct' : res?.is_correct === false ? 'wrong' : 'submitted');
      if (res?.ai_feedback) setAiFb(res.ai_feedback);
      if (res?.score != null) setScore(res.score);
    } catch {
      setResult('wrong');
    } finally {
      setBusy(false);
    }
  };

  const handleRetry = () => {
    setResult(null); setAiFb(''); setScore(null);
    setSelected([]); setText(''); setFills([]);
    setDropped([]); setAvail([...dragOrig].sort(() => Math.random() - 0.5));
  };

  const DIFF_COLOR = { Easy: '#00b894', Medium: '#e17055', Hard: '#d63031' };
  const dc = DIFF_COLOR[ex.difficulty_level] || '#6c5ce7';

  return (
    <div className={`ex-card ${result === 'correct' ? 'r-correct' : result === 'wrong' ? 'r-wrong' : result === 'submitted' ? 'r-submitted' : ''}`}>
      {/* head */}
      <div className="ex-head">
        <span className="ex-num">#{index}</span>
        {ex.difficulty_level && (
          <span className="ex-diff" style={{ color: dc, background: dc + '18', borderColor: dc + '55' }}>
            {ex.difficulty_level}
          </span>
        )}
        {ex.points > 0 && <span className="ex-pts">⭐ {ex.points} pts</span>}
        {score != null && <span className="ex-score">🏆 +{score}</span>}
      </div>

      {ex.title && <div className="ex-title">{ex.title}</div>}

      <div className="ex-body">

        {/* fill_in_blank */}
        {exType === 'fill_in_blank' && (
          <div className="ex-fill-text">
            {(ex.description || '').split('___').map((part, i, arr) => (
              <span key={i}>
                {part}
                {i < arr.length - 1 && (
                  <input
                    className={`ex-fill-input ${isDone ? (result === 'correct' ? 'ok' : 'err') : ''}`}
                    placeholder={String(i + 1)}
                    disabled={isDone}
                    value={fills[i] || ''}
                    onChange={(e) => {
                      const c = [...fills]; c[i] = e.target.value;
                      setFills(c); setResult(null);
                    }}
                  />
                )}
              </span>
            ))}
          </div>
        )}

        {/* multiple_choice */}
        {exType === 'multiple_choice' && (
          <>
            {ex.description && <p className="ex-question">{ex.description}</p>}
            <div className="ex-options">
              {opts.map((opt, i) => {
                const letter = String.fromCharCode(65 + i);
                const isSel  = selected.includes(letter);
                return (
                  <button
                    key={i}
                    className={`ex-opt ${isSel ? 'sel' : ''}`}
                    disabled={isDone}
                    onClick={() => {
                      setSelected(ex.is_multiple_select
                        ? isSel ? selected.filter((x) => x !== letter) : [...selected, letter]
                        : [letter]
                      );
                      setResult(null);
                    }}
                  >
                    <span className="ex-opt-letter">{letter}</span>
                    <span className="ex-opt-text">{opt}</span>
                    {isSel && <span className="ex-opt-check">✓</span>}
                  </button>
                );
              })}
              {ex.is_multiple_select && (
                <div className="ex-multi-hint">⚡ Можно выбрать несколько</div>
              )}
            </div>
          </>
        )}

        {/* drag_and_drop */}
        {exType === 'drag_and_drop' && (
          <>
            {ex.description && <p className="ex-question">{ex.description}</p>}
            <div className="ex-drag-section">
              <div className="ex-drop-label">Правильный порядок:</div>
              <div
                className="ex-dropzone"
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  if (isDone) return;
                  const word = e.dataTransfer.getData('word');
                  setDropped((d) => [...d, word]);
                  setAvail((a) => a.filter((w) => w !== word));
                  setResult(null);
                }}
              >
                {dropped.length === 0
                  ? <span className="ex-drop-hint">Перетащите сюда по порядку</span>
                  : dropped.map((w, i) => (
                      <span
                        key={i}
                        className="ex-dropped"
                        onClick={() => {
                          if (isDone) return;
                          setDropped((d) => d.filter((_, j) => j !== i));
                          setAvail((a) => [...a, w]);
                          setResult(null);
                        }}
                      >
                        <span className="ex-dropped-num">{i + 1}</span>
                        {w}
                        <span className="ex-dropped-del">✕</span>
                      </span>
                    ))
                }
              </div>
              <div className="ex-drag-words">
                {avail.map((w, i) => (
                  <span
                    key={i}
                    className="ex-drag-chip"
                    draggable={!isDone}
                    onDragStart={(e) => e.dataTransfer.setData('word', w)}
                  >{w}</span>
                ))}
              </div>
            </div>
          </>
        )}

        {/* text_input */}
        {exType === 'text_input' && (
          <>
            {ex.description && <p className="ex-question">{ex.description}</p>}
            <textarea
              className="ex-textarea"
              placeholder="Напишите ваш ответ..."
              disabled={isDone}
              value={text}
              rows={4}
              onChange={(e) => { setText(e.target.value); setResult(null); }}
            />
            <div className="ex-ai-badge">🤖 Проверяется AI</div>
          </>
        )}

        {/* hint */}
        {ex.hint && (
          <div className="ex-hint-wrap">
            <button className="ex-hint-btn" onClick={() => setHint((h) => !h)}>
              💡 {hint ? 'Скрыть подсказку' : 'Подсказка'}
            </button>
            {hint && <div className="ex-hint-text">{ex.hint}</div>}
          </div>
        )}

        {/* result */}
        {result && (
          <div className={`ex-result ${result}`}>
            {result === 'correct'   && <><span>🎉</span><div><strong>Правильно!</strong> Отличная работа!</div></>}
            {result === 'wrong'     && <><span>❌</span><div><strong>Неверно.</strong> Попробуйте ещё раз.</div></>}
            {result === 'submitted' && <><span>✅</span><div><strong>Ответ отправлен!</strong></div></>}
          </div>
        )}

        {aiFb && (
          <div className="ex-ai-fb">
            <div className="ex-ai-fb-label">🤖 Обратная связь от AI</div>
            <div className="ex-ai-fb-text">{aiFb}</div>
          </div>
        )}

        {/* actions */}
        <div className="ex-actions">
          {!isDone && (
            <button className="ex-submit" onClick={handleSubmit} disabled={busy || !buildAnswer()}>
              {busy ? '⏳ Проверяем…' : '✅ Проверить'}
            </button>
          )}
          {result === 'wrong' && (
            <button className="ex-retry" onClick={handleRetry}>🔄 Повторить</button>
          )}
          {isDone && result === 'correct' && (
            <div className="ex-done-tag">✓ Выполнено</div>
          )}
        </div>
      </div>
    </div>
  );
};

/* ═══════════════════════════════════════════
   EXERCISES SECTION
═══════════════════════════════════════════ */
const ExercisesSection = ({ section, courseId, lessonId }) => {
  const exs = (section.exercises || []).slice().sort((a, b) => (a.order || 0) - (b.order || 0));
  if (!exs.length) return null;
  const totalPts = exs.reduce((s, e) => s + (e.points || 0), 0);

  return (
    <div className="exs-wrap">
      <div className="exs-header">
        <span className="exs-count">🎯 {exs.length} заданий</span>
        {totalPts > 0 && <span className="exs-pts">🏆 {totalPts} pts</span>}
      </div>
      <div className="exs-list">
        {exs.map((ex, i) => (
          <ExerciseCard key={ex.id || i} ex={ex} courseId={courseId} lessonId={lessonId} index={i + 1} />
        ))}
      </div>
    </div>
  );
};

/* ═══════════════════════════════════════════
   MAIN — StudentLessonPage
═══════════════════════════════════════════ */
const StudentLessonPage = ({ lesson, course, allLessons, onBack, onNavigate, onComplete }) => {
  const { request } = useHttp();

  const [copiedId,      setCopiedId]      = useState(null);
  const [justCompleted, setJustCompleted] = useState(false);
  const [projectModal,  setProjectModal]  = useState(false);
  const [exitModal,     setExitModal]     = useState(false);
  const [projectForm,   setProjectForm]   = useState({ github_url: '', live_demo_url: '', description: '' });
  const [projectDone,   setProjectDone]   = useState(
    () => localStorage.getItem(`project_done_${lesson.id}`) === 'true'
  );
  const [projectSaving, setProjectSaving] = useState(false);
  const [projectError,  setProjectError]  = useState('');
  const [activeSection, setActiveSection] = useState(null);

  useEffect(() => {
    setJustCompleted(false);
    setProjectDone(localStorage.getItem(`project_done_${lesson.id}`) === 'true');
    setProjectForm({ github_url: '', live_demo_url: '', description: '' });
    setProjectError('');
    setActiveSection(null);
  }, [lesson.id]);

  const idx          = allLessons.findIndex((l) => l.id === lesson.id);
  const prevLesson   = idx > 0 ? allLessons[idx - 1] : null;
  const nextLesson   = idx < allLessons.length - 1 ? allLessons[idx + 1] : null;
  const projectSec   = lesson.sections?.find((s) => s.type === 'project');
  const isDone       = lesson.completed || justCompleted;
  const nextBlocked  = !!projectSec && !projectDone;

  const completedCount = allLessons.filter((l) => l.completed).length + (justCompleted && !lesson.completed ? 1 : 0);
  const progressPct    = allLessons.length > 0
    ? Math.round((completedCount / allLessons.length) * 100)
    : 0;

  const tryEarnCert = useCallback(async () => {
    if (!course.id) return;
    try {
      await fetch(
        `${API_URL}v1/achievements/check-and-earn-certificate?course_id=${course.id}`,
        { method: 'POST', headers: headers() }
      );
    } catch {}
  }, [course.id]);

  const handleComplete = useCallback(async () => {
    if (isDone) return;
    onComplete();
    setJustCompleted(true);
    if (idx === allLessons.length - 1) await tryEarnCert();
  }, [isDone, idx, allLessons.length, onComplete, tryEarnCert]);

  const handleVideoComplete = useCallback(() => {
    if (!isDone) handleComplete();
  }, [isDone, handleComplete]);

  const copyCode = (id, code) => {
    navigator.clipboard.writeText(code).then(() => {
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    });
  };

  const handleProjectSubmit = async () => {
    if (!projectForm.github_url.trim()) return;
    const rawDesc = projectForm.description.trim() || projectSec?.description || '';
    const desc    = rawDesc.length >= 10 ? rawDesc : (rawDesc + ' (loyiha)').padEnd(10, '.');

    setProjectSaving(true); setProjectError('');
    try {
      const techs   = projectSec?.techStack
        ? projectSec.techStack.split(',').map((t) => t.trim()).filter(Boolean)
        : [];
      const created = await request(
        `${API_URL}v1/project/`, 'POST',
        JSON.stringify({
          title:             projectSec?.label || lesson.title,
          description:       desc,
          github_url:        projectForm.github_url,
          live_demo_url:     projectForm.live_demo_url || '',
          technologies_used: techs,
          difficulty_level:  'Easy',
          project_files:     '',
        }),
        headers()
      );
      if (created?.id) {
        await request(`${API_URL}v1/project/${created.id}/submit`, 'POST', null, headers());
      }
      localStorage.setItem(`project_done_${lesson.id}`, 'true');
      setProjectDone(true);
      setProjectModal(false);
      if (!isDone) {
        onComplete(); setJustCompleted(true);
        if (idx === allLessons.length - 1) await tryEarnCert();
      }
    } catch {
      setProjectError('Ошибка при отправке. Проверьте данные и попробуйте ещё раз.');
    } finally {
      setProjectSaving(false);
    }
  };

  const sectionMeta = (type) => SECTION_TYPES.find((t) => t.type === type) || { icon: '🎯', label: 'Блок' };

  /* section tabs (if multiple sections) */
  const sections = lesson.sections || [];
  const hasMultiple = sections.length > 1;
  const currentSection = activeSection !== null ? sections[activeSection] : null;

  return (
    <div className="slp-root">

      {/* ── Top bar ── */}
      <div className="slp-topbar">
        <div className="slp-breadcrumb">
          <button className="slp-bc" onClick={() => onBack('courses')}>Курсы</button>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="9 18 15 12 9 6"/></svg>
          <button className="slp-bc" onClick={() => onBack('course')}>{course.title}</button>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="9 18 15 12 9 6"/></svg>
          <span className="slp-bc-cur">{lesson.title}</span>
        </div>

        <div className="slp-topbar-right">
          <div className="slp-nav-pair">
            <button className="slp-nav" disabled={!prevLesson} onClick={() => prevLesson && onNavigate(prevLesson)}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="15 18 9 12 15 6"/></svg>
              Пред.
            </button>
            <button className="slp-nav" disabled={!nextLesson || nextBlocked} onClick={() => !nextBlocked && nextLesson && onNavigate(nextLesson)}>
              След.
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
          </div>
          <button className="slp-exit" onClick={() => setExitModal(true)}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            Выйти
          </button>
        </div>
      </div>

      {/* ── Course progress bar ── */}
      <div className="slp-cprog">
        <div className="slp-cprog-track">
          <div className="slp-cprog-fill" style={{ width: `${progressPct}%` }} />
        </div>
        <span className="slp-cprog-label">{completedCount}/{allLessons.length}</span>
      </div>

      {/* ── Lesson header ── */}
      <div className="slp-lheader">
        <div className="slp-lheader-left">
          {lesson.chapter && <span className="slp-chapter-tag">{lesson.chapter}</span>}
          <h1 className="slp-ltitle">{lesson.title}</h1>
          <span className="slp-lnum">Урок {idx + 1} из {allLessons.length}</span>
        </div>

        <div className="slp-lheader-right">
          {!projectSec && (
            <button
              className={`slp-complete-btn ${isDone ? 'done' : ''}`}
              onClick={handleComplete}
              disabled={isDone}
            >
              {isDone
                ? <><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><polyline points="20 6 9 17 4 12"/></svg> Пройдено</>
                : 'Отметить как пройденный'
              }
            </button>
          )}
          {projectSec && isDone && (
            <div className="slp-complete-btn done">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><polyline points="20 6 9 17 4 12"/></svg>
              Пройдено
            </div>
          )}
        </div>
      </div>

      {/* ── Section tabs (if multiple) ── */}
      {hasMultiple && (
        <div className="slp-tabs">
          <button
            className={`slp-tab ${activeSection === null ? 'active' : ''}`}
            onClick={() => setActiveSection(null)}
          >
            Все блоки
          </button>
          {sections.map((sec, i) => {
            const m = sectionMeta(sec.type);
            return (
              <button
                key={sec.id}
                className={`slp-tab ${activeSection === i ? 'active' : ''}`}
                onClick={() => setActiveSection(i)}
              >
                <span>{m.icon}</span>
                {sec.label || m.label}
              </button>
            );
          })}
        </div>
      )}

      {/* ── Content ── */}
      {sections.length === 0 ? (
        <div className="slp-empty-content">
          <span className="slp-empty-icon">📄</span>
          <p>Контент для этого урока ещё не добавлен</p>
        </div>
      ) : (
        <div className="slp-blocks">
          {(currentSection ? [currentSection] : sections).map((section) => {
            const m    = sectionMeta(section.type);
            const ytId = section.type === 'video' ? getYTId(section.videoUrl || '') : null;

            return (
              <div key={section.id} className="slp-block">
                <div className="slp-block-head">
                  <span className="slp-block-icon">{m.icon}</span>
                  <span className="slp-block-type">{m.label}</span>
                  {section.label && section.type !== 'exercise' && (
                    <span className="slp-block-label">{section.label}</span>
                  )}
                </div>

                <div className="slp-block-body">

                  {/* TEXT */}
                  {section.type === 'text' && (
                    <div
                      className="slp-text"
                      dangerouslySetInnerHTML={{
                        __html: section.html || '<p style="color:rgba(15,13,30,0.3)">Текст не добавлен</p>',
                      }}
                    />
                  )}

                  {/* CODE */}
                  {section.type === 'code' && (
                    <div className="slp-code-wrap">
                      <div className="slp-code-bar">
                        <span className="slp-code-lang">{section.lang || 'code'}</span>
                        <button
                          className="slp-code-copy"
                          onClick={() => copyCode(section.id, section.code || '')}
                        >
                          {copiedId === section.id ? '✅ Скопировано' : '📋 Копировать'}
                        </button>
                      </div>
                      <pre className="slp-code">{section.code || '// Код не добавлен'}</pre>
                    </div>
                  )}

                  {/* VIDEO */}
                  {section.type === 'video' && (
                    <>
                      {ytId ? (
                        <>
                          <YouTubePlayer ytId={ytId} onVideoComplete={handleVideoComplete} />
                          {!isDone && (
                            <div className="slp-video-hint">
                              🎬 Досмотрите до конца — урок отметится автоматически
                            </div>
                          )}
                        </>
                      ) : (
                        <div className="slp-empty-block">Видео не добавлено</div>
                      )}
                      {section.videoUrl && (
                        <a href={section.videoUrl} target="_blank" rel="noopener noreferrer" className="slp-yt-link">
                          🎥 Открыть на YouTube
                        </a>
                      )}
                    </>
                  )}

                  {/* IMAGE */}
                  {section.type === 'image' && (
                    <div className="slp-img">
                      {section.imgUrl
                        ? <img src={section.imgUrl} alt={section.label || ''} />
                        : <div className="slp-empty-block">Изображение не добавлено</div>
                      }
                    </div>
                  )}

                  {/* FILE */}
                  {section.type === 'file' && (
                    section.fileName ? (
                      <div className="slp-file">
                        <span className="slp-file-icon">📦</span>
                        <div className="slp-file-info">
                          <div className="slp-file-name">{section.fileName}</div>
                        </div>
                        <button className="slp-file-dl">⬇ Скачать</button>
                      </div>
                    ) : (
                      <div className="slp-empty-block">Файл не добавлен</div>
                    )
                  )}

                  {/* EXERCISE */}
                  {section.type === 'exercise' && (
                    <ExercisesSection section={section} courseId={course.id} lessonId={lesson.id} />
                  )}

                  {/* PROJECT */}
                  {section.type === 'project' && (
                    <div className={`slp-project ${projectDone ? 'done' : ''}`}>
                      <div className="slp-project-top">
                        <div className="slp-project-icon">🚀</div>
                        <div className="slp-project-info">
                          <h4>{section.label || 'Практическое задание'}</h4>
                          {section.description && <p>{section.description}</p>}
                        </div>
                        {projectDone && <span className="slp-project-submitted-badge">✅ Сдано</span>}
                      </div>

                      {section.requirements && (
                        <div className="slp-project-reqs">
                          <div className="slp-project-reqs-label">📋 Требования</div>
                          <div className="slp-project-reqs-text">{section.requirements}</div>
                        </div>
                      )}

                      {section.techStack && (
                        <div className="slp-project-tech">
                          <span className="slp-project-tech-label">🛠 Стек:</span>
                          {section.techStack.split(',').map((t, i) => (
                            <span key={i} className="slp-tech-chip">{t.trim()}</span>
                          ))}
                        </div>
                      )}

                      {section.deadline && (
                        <div className="slp-project-deadline">
                          ⏰ Срок: <strong>{section.deadline} дней</strong>
                        </div>
                      )}

                      {!projectDone ? (
                        <button className="slp-project-btn" onClick={() => setProjectModal(true)}>
                          📤 Загрузить проект
                        </button>
                      ) : (
                        <div className="slp-project-link-row">
                          <span>🔗</span>
                          <span>{projectForm.github_url || 'Проект сдан'}</span>
                        </div>
                      )}
                    </div>
                  )}

                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ── Bottom nav ── */}
      <div className="slp-bottom">
        <button
          className="slp-bot-btn prev"
          disabled={!prevLesson}
          onClick={() => prevLesson && onNavigate(prevLesson)}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="15 18 9 12 15 6"/></svg>
          Предыдущий
        </button>

        <div className="slp-bot-center">
          {nextBlocked && (
            <div className="slp-locked-warn">🔒 Сначала сдайте проект</div>
          )}
          {!nextBlocked && !isDone && !projectSec && (
            <button className="slp-bot-btn complete" onClick={handleComplete}>
              ✓ Отметить и продолжить
            </button>
          )}
          {!nextBlocked && isDone && nextLesson && (
            <button className="slp-bot-btn next" onClick={() => onNavigate(nextLesson)}>
              Следующий
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
          )}
          {isDone && !nextLesson && (
            <div className="slp-course-done">🎉 Курс завершён!</div>
          )}
        </div>

        <button
          className="slp-bot-btn next"
          disabled={!nextLesson || nextBlocked}
          onClick={() => !nextBlocked && nextLesson && onNavigate(nextLesson)}
          style={{ visibility: 'hidden' }}
        >
          Следующий
        </button>
      </div>

      {/* ── Exit modal ── */}
      {exitModal && ReactDOM.createPortal(
        <div className="modal-overlay" onClick={() => setExitModal(false)}>
          <div className="exit-modal" onClick={(e) => e.stopPropagation()}>
            <div className="exit-modal-icon">📖</div>
            <h4>Выйти из урока?</h4>
            <p>Куда вы хотите перейти?</p>
            <div className="exit-modal-actions">
              <button className="exit-opt primary" onClick={() => { setExitModal(false); onBack('course'); }}>
                📚 К курсу «{course.title}»
              </button>
              <button className="exit-opt secondary" onClick={() => { setExitModal(false); onBack('courses'); }}>
                🏠 Ко всем курсам
              </button>
              <button className="exit-cancel" onClick={() => setExitModal(false)}>
                Остаться в уроке
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}

      {/* ── Project modal ── */}
      {projectModal && ReactDOM.createPortal(
        <div className="modal-overlay" onClick={() => setProjectModal(false)}>
          <div className="proj-modal" onClick={(e) => e.stopPropagation()}>
            <div className="proj-modal-head">
              <h3>📤 Загрузить проект</h3>
              <button className="proj-modal-close" onClick={() => setProjectModal(false)}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>
            <div className="proj-modal-body">
              <p className="proj-name">🚀 {projectSec?.label || 'Практическое задание'}</p>
              <div className="proj-field">
                <label>GitHub URL *</label>
                <input
                  placeholder="https://github.com/username/repo"
                  value={projectForm.github_url}
                  onChange={(e) => setProjectForm((f) => ({ ...f, github_url: e.target.value }))}
                />
              </div>
              <div className="proj-field">
                <label>Live Demo URL</label>
                <input
                  placeholder="https://myproject.com"
                  value={projectForm.live_demo_url}
                  onChange={(e) => setProjectForm((f) => ({ ...f, live_demo_url: e.target.value }))}
                />
              </div>
              <div className="proj-field">
                <label>Комментарий</label>
                <textarea
                  placeholder="Расскажите что сделали..."
                  rows={3}
                  value={projectForm.description}
                  onChange={(e) => setProjectForm((f) => ({ ...f, description: e.target.value }))}
                />
              </div>
              {projectError && <div className="proj-error">⚠️ {projectError}</div>}
            </div>
            <div className="proj-modal-foot">
              <button className="proj-cancel" onClick={() => { setProjectModal(false); setProjectError(''); }}>
                Отмена
              </button>
              <button
                className="proj-submit"
                onClick={handleProjectSubmit}
                disabled={!projectForm.github_url.trim() || projectSaving}
              >
                {projectSaving ? '⏳ Отправка…' : '✅ Отправить'}
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
};

export default StudentLessonPage;