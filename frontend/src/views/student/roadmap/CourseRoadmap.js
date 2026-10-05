import { useEffect, useMemo, useRef, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL, headers, resolveImageUrl } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import AppHeader from '../../../components/appheader/AppHeader';
import './CourseRoadmap.css';
import { BookOpen, Check, Lock, Clock, Users, Rocket, ArrowRight, Loader2, ChevronLeft, ChevronRight, PlayCircle } from 'lucide-react';

const DIFF_META = {
    Beginner:     { ru: 'НАЧИНАЮЩИЙ', uz: "BOSHLANG'ICH" },
    Intermediate: { ru: 'СРЕДНИЙ',    uz: "O'RTA" },
    Advanced:     { ru: 'ПРОДВИНУТЫЙ', uz: "ILG'OR" },
};

const DIFF_RANK = { Beginner: 0, Intermediate: 1, Advanced: 2 };
const byLearningOrder = (a, b) =>
    ((DIFF_RANK[a.difficulty_level] ?? 3) - (DIFF_RANK[b.difficulty_level] ?? 3))
    || ((a.order || 0) - (b.order || 0))
    || String(a.title || '').localeCompare(String(b.title || ''));

const TRACK_ICON = { 'html-css': '🌐', javascript: '⚡', python: '🐍', react: '⚛️', sql: '🗄️', git: '🔀', 'telegram-bot': '🤖' };
const trackIcon = (slug) => TRACK_ICON[slug] || '📦';

const hasProject = (l) =>
    !!(l.task_title || l.task_description || l.task_requirements || l.task_technologies || l.task_deadline_days);
const lessonDone = (l) =>
    l.is_completed === true || l.completed === true || (!hasProject(l) && l.progress_percentage === 100);
const blokCount = (l) => {
    if (l.sections_json) { try { const s = JSON.parse(l.sections_json); if (Array.isArray(s)) return s.length; } catch { /* ignore */ } }
    let n = 0;
    ['text_content', 'code_content', 'video_url', 'image_url', 'file_url'].forEach((k) => { if (l[k]) n++; });
    if (hasProject(l)) n++;
    return n;
};
const courseStatus = (c) => {
    if (c.is_enrolled === false || c.is_locked === true) return 'locked';
    const p = c.progress_percentage || 0;
    if (p >= 100) return 'done';
    if (p > 0) return 'current';
    return 'available';
};

/* ── reusable horizontal scroller: drag + wheel + arrows + edge fade ── */
function useHScroll(dep, enableWheel = false) {
    const ref = useRef(null);
    const [canLeft, setCanLeft] = useState(false);
    const [canRight, setCanRight] = useState(false);
    const drag = useRef({ down: false, startX: 0, startScroll: 0, moved: false });

    const update = useCallback(() => {
        const el = ref.current; if (!el) return;
        setCanLeft(el.scrollLeft > 20);
        setCanRight(el.scrollLeft < el.scrollWidth - el.clientWidth - 8);
    }, []);

    useEffect(() => {
        const id = setTimeout(update, 60);
        window.addEventListener('resize', update);
        return () => { clearTimeout(id); window.removeEventListener('resize', update); };
    }, [dep, update]);

    useEffect(() => {
        if (!enableWheel) return; // only the single lesson timeline opts in
        const el = ref.current; if (!el) return;
        const onWheel = (e) => {
            const d = Math.abs(e.deltaY) >= Math.abs(e.deltaX) ? e.deltaY : e.deltaX;
            if (!d) return;
            const atStart = el.scrollLeft <= 0;
            const atEnd = el.scrollLeft >= el.scrollWidth - el.clientWidth - 1;
            // Only capture the wheel when the strip can still scroll that way;
            // at either end the page scrolls normally.
            if ((d > 0 && !atEnd) || (d < 0 && !atStart)) { el.scrollLeft += d; e.preventDefault(); }
        };
        el.addEventListener('wheel', onWheel, { passive: false });
        return () => el.removeEventListener('wheel', onWheel);
    }, [dep, enableWheel]);

    const scrollByDir = (dir) => {
        const el = ref.current; if (!el) return;
        el.scrollBy({ left: dir * Math.max(320, el.clientWidth * 0.75), behavior: 'smooth' });
    };
    const onMouseDown = (e) => {
        const el = ref.current; if (!el) return;
        drag.current = { down: true, startX: e.clientX, startScroll: el.scrollLeft, moved: false };
    };
    const onMouseMove = (e) => {
        const el = ref.current; if (!el || !drag.current.down) return;
        const dx = e.clientX - drag.current.startX;
        if (Math.abs(dx) > 5) drag.current.moved = true;
        el.scrollLeft = drag.current.startScroll - dx;
    };
    const onMouseUp = () => { drag.current.down = false; };
    const consumedDrag = () => { if (drag.current.moved) { drag.current.moved = false; return true; } return false; };

    const m = canLeft && canRight
        ? 'linear-gradient(to right, transparent, #000 56px, #000 calc(100% - 56px), transparent)'
        : canRight ? 'linear-gradient(to right, #000 calc(100% - 64px), transparent)'
        : canLeft ? 'linear-gradient(to right, transparent, #000 56px)'
        : 'none';
    const maskStyle = { WebkitMaskImage: m, maskImage: m };

    return { ref, canLeft, canRight, update, scrollByDir, onMouseDown, onMouseMove, onMouseUp, consumedDrag, maskStyle };
}

/* ── animated hero ring ── */
function HeroRing({ pct, ru }) {
    const size = 150, stroke = 10, r = (size - stroke) / 2, circ = 2 * Math.PI * r;
    const [off, setOff] = useState(circ);
    useEffect(() => {
        const id = setTimeout(() => setOff(circ - circ * (pct || 0) / 100), 250);
        return () => clearTimeout(id);
    }, [pct, circ]);
    return (
        <div className="rd-hero-ring">
            <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
                <defs>
                    <linearGradient id="rdRing" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0" stopColor="#22d3ee" /><stop offset="1" stopColor="#36e06b" />
                    </linearGradient>
                </defs>
                <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,.08)" strokeWidth={stroke} />
                <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="url(#rdRing)" strokeWidth={stroke}
                    strokeLinecap="round" strokeDasharray={circ} strokeDashoffset={off}
                    transform={`rotate(-90 ${size / 2} ${size / 2})`}
                    style={{ transition: 'stroke-dashoffset 1.3s cubic-bezier(.2,.75,.25,1)', filter: 'drop-shadow(0 0 8px rgba(34,211,238,.5))' }} />
            </svg>
            <div className="rd-hero-ring-center">
                <div className="rd-hero-ring-pct">{Math.round(pct)}%</div>
                <div className="rd-hero-ring-lbl">{pct >= 100 ? (ru ? 'Пройдено' : "O'tildi") : (ru ? 'Прогресс' : 'Progress')}</div>
            </div>
        </div>
    );
}

/* ── one track (category) = a connected roadmap row of its courses ── */
function TrackRow({ cat, courses, ru, onOpen }) {
    const hs = useHScroll(courses.length, true);
    const done = courses.filter((c) => (c.progress_percentage || 0) >= 100).length;
    const statusLabel = { done: ru ? 'Пройден' : 'Tugatildi', current: ru ? 'В процессе' : 'Jarayonda', available: ru ? 'Открыт' : 'Ochiq', locked: ru ? 'Закрыт' : 'Yopiq' };
    return (
        <div className="rd-track-section rd-rise">
            <div className="rd-track-head">
                <div className="rd-track-id">
                    <span className="rd-track-icon">{trackIcon(cat.slug)}</span>
                    <span className="rd-track-name">{cat.name}</span>
                    <span className="rd-track-count">{done}/{courses.length} {ru ? 'курсов' : 'kurs'}</span>
                </div>
                {(hs.canLeft || hs.canRight) && (
                    <div className="rd-nav">
                        <button className="rd-nav-btn" disabled={!hs.canLeft} onClick={() => hs.scrollByDir(-1)} aria-label="Prev"><ChevronLeft size={18} /></button>
                        <button className="rd-nav-btn" disabled={!hs.canRight} onClick={() => hs.scrollByDir(1)} aria-label="Next"><ChevronRight size={18} /></button>
                    </div>
                )}
            </div>
            <div className="rd-track-wrap">
                <div className="rd-track" ref={hs.ref} onScroll={hs.update}
                    onMouseDown={hs.onMouseDown} onMouseMove={hs.onMouseMove} onMouseUp={hs.onMouseUp} onMouseLeave={hs.onMouseUp}
                    style={hs.maskStyle}>
                    {courses.map((c, i) => {
                        const status = courseStatus(c);
                        const pct = Math.round(c.progress_percentage || 0);
                        const img = resolveImageUrl(c.image_url);
                        const prevDone = i > 0 && (courses[i - 1].progress_percentage || 0) >= 100;
                        return (
                            <div className="rd-node-wrap" key={c.id}>
                                {i > 0 && <span className={`rd-connector ${prevDone && status === 'done' ? 'lit' : ''}`} />}
                                <button className={`rd-cnode rd-node--${status}`} onClick={() => { if (!hs.consumedDrag()) onOpen(c); }}>
                                    <div className="rd-cnode-top">
                                        <span className="rd-cnode-icon">
                                            {img ? <img src={img} alt="" /> : <span>{(c.title || '?')[0]}</span>}
                                            {status === 'locked' && <span className="rd-cnode-lock"><Lock size={11} /></span>}
                                        </span>
                                        <span className={`rd-node-status rd-node-status--${status}`}>
                                            {status === 'done' && <Check size={12} />} {statusLabel[status]}
                                        </span>
                                    </div>
                                    <div className="rd-cnode-title">{c.title}</div>
                                    <div className="rd-cnode-bar"><div className="rd-cnode-fill" style={{ width: `${pct}%` }} /></div>
                                    <div className="rd-cnode-foot">
                                        <span>{c.lessons_count || 0} {ru ? 'уроков' : 'dars'}</span>
                                        <span className="rd-cnode-pct">{pct}%</span>
                                    </div>
                                </button>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}

export default function CourseRoadmap() {
    const navigate = useNavigate();
    const { lang } = useTranslation();
    const ru = lang === 'ru';

    const [courses, setCourses] = useState([]);
    const [categories, setCategories] = useState([]);
    const [activeId, setActiveId] = useState(null);
    const [lessons, setLessons] = useState([]);
    const [loading, setLoading] = useState(true);
    const [lessonsLoading, setLessonsLoading] = useState(false);

    const lessonScroll = useHScroll(lessons.length, true); // wheel-scroll enabled

    useEffect(() => {
        Promise.all([
            fetch(`${API_URL}v1/courses/?limit=100`, { headers: headers() }).then((r) => (r.ok ? r.json() : [])),
            fetch(`${API_URL}v1/categories/`, { headers: headers() }).then((r) => (r.ok ? r.json() : [])),
        ]).then(([cData, catData]) => {
            const list = (Array.isArray(cData) ? cData : []).filter((c) => c.is_published !== false);
            setCourses(list);
            setCategories(Array.isArray(catData) ? catData : []);
            const active =
                [...list].filter((c) => { const p = c.progress_percentage || 0; return p > 0 && p < 100; })
                    .sort((a, b) => (b.progress_percentage || 0) - (a.progress_percentage || 0))[0]
                || [...list].filter((c) => (c.progress_percentage || 0) > 0)[0]
                || null;
            setActiveId(active ? active.id : null);
        }).catch(() => {}).finally(() => setLoading(false));
    }, []);

    useEffect(() => {
        if (!activeId) { setLessons([]); return; }
        setLessonsLoading(true);
        const langParam = lang && lang !== 'uz' ? `&lang=${lang}` : '';
        fetch(`${API_URL}v1/courses/${activeId}/lessons?t=${Date.now()}${langParam}`, { headers: headers() })
            .then((r) => (r.ok ? r.json() : []))
            .then((raw) => setLessons((Array.isArray(raw) ? raw : []).filter((l) => l.is_published !== false).sort((a, b) => (a.order || 0) - (b.order || 0))))
            .catch(() => setLessons([]))
            .finally(() => setLessonsLoading(false));
    }, [activeId, lang]);

    const activeCourse = courses.find((c) => String(c.id) === String(activeId)) || null;

    const lessonNodes = useMemo(() => {
        let locked = false;
        return lessons.map((l) => {
            const d = lessonDone(l);
            let status;
            if (d) status = 'done';
            else if (!locked) { status = 'current'; locked = true; }
            else status = 'locked';
            return { lesson: l, status };
        });
    }, [lessons]);
    const currentLesson = lessonNodes.find((n) => n.status === 'current');
    const doneLessons = lessonNodes.filter((n) => n.status === 'done').length;

    // Group courses into tracks (categories with ≥1 course), ordered inside by level.
    const tracks = useMemo(() => {
        const out = categories
            .map((cat) => ({ cat, list: courses.filter((c) => c.category_id === cat.id).sort(byLearningOrder) }))
            .filter((t) => t.list.length > 0);
        const uncategorized = courses.filter((c) => !c.category_id).sort(byLearningOrder);
        if (uncategorized.length) out.push({ cat: { id: 'none', name: ru ? 'Другое' : 'Boshqa', slug: '' }, list: uncategorized });
        return out;
    }, [categories, courses, ru]);

    const openCourse = (c) => navigate(`/student/courses/${c.id}`);
    const openLesson = (lesson, status) => {
        if (lessonScroll.consumedDrag()) return;
        if (status === 'locked') return;
        navigate(`/student/courses/${activeId}/lessons/${lesson.id}`);
    };

    if (loading) {
        return (<div className="rd-dark"><AppHeader /><div className="rd-state"><Loader2 className="rd-spin" size={26} /> {ru ? 'Загрузка…' : 'Yuklanmoqda…'}</div></div>);
    }

    return (
        <div className="rd-dark">
            <AppHeader />
            <div className="rd-shell">

                {/* ── hero: current course ── */}
                {activeCourse && (() => {
                    const pct = Math.round(activeCourse.progress_percentage || 0);
                    const diff = DIFF_META[activeCourse.difficulty_level];
                    const diffLabel = diff ? (ru ? diff.ru : diff.uz) : activeCourse.difficulty_level;
                    const lessonsCount = activeCourse.lessons_count || lessons.length;
                    const completed = pct >= 100;
                    return (
                        <div className="rd-hero rd-rise">
                            <div className="rd-hero-main">
                                {diffLabel && <span className="rd-hero-diff">{diffLabel}</span>}
                                <h1 className="rd-hero-title">{activeCourse.title}</h1>
                                <div className="rd-hero-meta">
                                    {activeCourse.instructor_name && (
                                        <span className="rd-hero-meta-item">
                                            <span className="rd-hero-teacher-ava">{activeCourse.instructor_name[0]?.toUpperCase()}</span>
                                            {activeCourse.instructor_name}
                                        </span>
                                    )}
                                    <span className="rd-hero-meta-item"><Clock size={15} /> {lessonsCount} {ru ? 'уроков' : 'dars'}</span>
                                    {activeCourse.students_count > 0 && (
                                        <span className="rd-hero-meta-item"><Users size={15} /> {activeCourse.students_count} {ru ? 'студентов' : 'talaba'}</span>
                                    )}
                                </div>
                                <div className="rd-hero-actions">
                                    {completed ? (
                                        <span className="rd-hero-badge"><Check size={16} /> {ru ? 'Курс завершён!' : 'Kurs tugatildi!'}</span>
                                    ) : currentLesson ? (
                                        <button className="rd-hero-continue" onClick={() => openLesson(currentLesson.lesson, 'current')}>
                                            <Rocket size={16} /> {ru ? 'Продолжить' : 'Davom etish'} <ArrowRight size={15} />
                                        </button>
                                    ) : (
                                        <button className="rd-hero-continue" onClick={() => openCourse(activeCourse)}>
                                            <PlayCircle size={16} /> {ru ? 'Начать' : 'Boshlash'}
                                        </button>
                                    )}
                                    {lessonsCount > 0 && <span className="rd-hero-progress-txt">{doneLessons}/{lessonsCount} {ru ? 'пройдено' : 'tugatildi'}</span>}
                                </div>
                            </div>
                            <HeroRing pct={pct} ru={ru} />
                        </div>
                    );
                })()}

                {/* ── active course lesson timeline ── */}
                {activeCourse && (
                    <>
                        <div className="rd-section-head">
                            <div className="rd-section-title">{ru ? 'Путь обучения' : "O'quv yo'li"}</div>
                            {!lessonsLoading && lessonNodes.length > 0 && (lessonScroll.canLeft || lessonScroll.canRight) && (
                                <div className="rd-nav">
                                    <button className="rd-nav-btn" disabled={!lessonScroll.canLeft} onClick={() => lessonScroll.scrollByDir(-1)} aria-label="Prev"><ChevronLeft size={18} /></button>
                                    <button className="rd-nav-btn" disabled={!lessonScroll.canRight} onClick={() => lessonScroll.scrollByDir(1)} aria-label="Next"><ChevronRight size={18} /></button>
                                </div>
                            )}
                        </div>
                        {lessonsLoading ? (
                            <div className="rd-state"><Loader2 className="rd-spin" size={22} /> {ru ? 'Загрузка уроков…' : 'Darslar yuklanmoqda…'}</div>
                        ) : lessonNodes.length === 0 ? (
                            <div className="rd-state">{ru ? 'В этом курсе пока нет уроков' : "Bu kursda hali darslar yo'q"}</div>
                        ) : (
                            <div className="rd-track-wrap">
                                <div className="rd-track" ref={lessonScroll.ref} onScroll={lessonScroll.update}
                                    onMouseDown={lessonScroll.onMouseDown} onMouseMove={lessonScroll.onMouseMove}
                                    onMouseUp={lessonScroll.onMouseUp} onMouseLeave={lessonScroll.onMouseUp}
                                    style={lessonScroll.maskStyle}>
                                    {lessonNodes.map(({ lesson, status }, i) => {
                                        const blocks = blokCount(lesson);
                                        const project = hasProject(lesson);
                                        const prevDone = i > 0 && lessonNodes[i - 1].status === 'done';
                                        return (
                                            <div className="rd-node-wrap" key={lesson.id}>
                                                {i > 0 && <span className={`rd-connector ${prevDone && status === 'done' ? 'lit' : ''}`} />}
                                                <button className={`rd-node rd-node--${status}`} onClick={() => openLesson(lesson, status)} disabled={status === 'locked'}>
                                                    <div className="rd-node-head">
                                                        <span className={`rd-node-icon rd-node-icon--${status}`}>
                                                            {status === 'locked' ? <Lock size={18} /> : <BookOpen size={18} />}
                                                        </span>
                                                        <span className={`rd-node-status rd-node-status--${status}`}>
                                                            {status === 'done' ? <><Check size={13} /> {ru ? 'Пройдено' : "O'tildi"}</>
                                                                : status === 'current' ? (ru ? 'Текущий' : 'Joriy') : (ru ? 'Закрыто' : 'Yopiq')}
                                                        </span>
                                                    </div>
                                                    <div className="rd-node-title">{lesson.title}</div>
                                                    <div className="rd-node-foot">
                                                        <span className="rd-node-blocks">{blocks} {ru ? 'блок' : 'blok'}</span>
                                                        {project && <span className="rd-node-tag">{ru ? 'Проект' : 'Loyiha'}</span>}
                                                    </div>
                                                </button>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}
                    </>
                )}

                {/* ── all courses grouped by track ── */}
                <div className="rd-section-title rd-tracks-title">{ru ? 'Все направления' : "Barcha yo'nalishlar"}</div>
                {tracks.map((t) => (
                    <TrackRow key={t.cat.id} cat={t.cat} courses={t.list} ru={ru} onOpen={openCourse} />
                ))}
            </div>
        </div>
    );
}
