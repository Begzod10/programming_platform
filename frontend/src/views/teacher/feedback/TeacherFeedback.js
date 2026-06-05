import {useEffect, useMemo, useState} from 'react';
import {API_URL, useHttp, headers} from '../../../api/search/base';
import './TeacherFeedback.css';

/**
 * Teacher view: per-course lesson feedback dashboard.
 * Shows avg rating + response count + breakdown per lesson, with the
 * ability to drill into a lesson to read individual comments.
 */
function TeacherFeedback() {
    const {request} = useHttp();
    const [courses, setCourses] = useState([]);
    const [courseLoading, setCourseLoading] = useState(true);
    const [activeCourseId, setActiveCourseId] = useState(null);
    const [overview, setOverview] = useState(null);
    const [overviewLoading, setOverviewLoading] = useState(false);
    const [overviewError, setOverviewError] = useState('');
    const [expandedLessonId, setExpandedLessonId] = useState(null);
    const [comments, setComments] = useState({});
    const [commentsLoading, setCommentsLoading] = useState({});

    // Load teacher's own courses for the course picker.
    useEffect(() => {
        let cancelled = false;
        setCourseLoading(true);
        request(`${API_URL}v1/courses/my`, 'GET', null, headers())
            .then(data => {
                if (cancelled) return;
                const list = Array.isArray(data) ? data : (data?.items || []);
                setCourses(list);
                if (list.length && activeCourseId == null) {
                    setActiveCourseId(list[0].id);
                }
            })
            .catch(() => { if (!cancelled) setCourses([]); })
            .finally(() => { if (!cancelled) setCourseLoading(false); });
        return () => { cancelled = true; };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Whenever course changes, fetch its lesson-feedback overview.
    useEffect(() => {
        if (!activeCourseId) return;
        let cancelled = false;
        setOverviewLoading(true);
        setOverviewError('');
        setOverview(null);
        setExpandedLessonId(null);
        setComments({});
        request(
            `${API_URL}v1/teacher/courses/${activeCourseId}/lesson-feedback`,
            'GET',
            null,
            headers(),
        )
            .then(data => { if (!cancelled) setOverview(data); })
            .catch(e => {
                if (cancelled) return;
                setOverviewError(
                    e?.status === 403
                        ? 'Bu kurs sizga tegishli emas.'
                        : 'Ma\'lumotlarni yuklab bo\'lmadi.',
                );
            })
            .finally(() => { if (!cancelled) setOverviewLoading(false); });
        return () => { cancelled = true; };
    }, [activeCourseId, request]);

    const handleToggleLesson = async (lessonId) => {
        if (expandedLessonId === lessonId) {
            setExpandedLessonId(null);
            return;
        }
        setExpandedLessonId(lessonId);
        if (comments[lessonId] !== undefined) return;
        setCommentsLoading(prev => ({...prev, [lessonId]: true}));
        try {
            const data = await request(
                `${API_URL}v1/teacher/lessons/${lessonId}/feedback?limit=50`,
                'GET',
                null,
                headers(),
            );
            setComments(prev => ({...prev, [lessonId]: data || []}));
        } catch {
            setComments(prev => ({...prev, [lessonId]: []}));
        } finally {
            setCommentsLoading(prev => ({...prev, [lessonId]: false}));
        }
    };

    const totalResponses = overview?.total_responses || 0;
    const courseAvg = overview?.average_rating;
    const lessons = useMemo(() => overview?.lessons || [], [overview]);

    const sorted = useMemo(() => {
        // Worst-rated first (with enough responses) so the teacher sees
        // what needs attention. Lessons without responses go to the bottom.
        return [...lessons].sort((a, b) => {
            if (a.response_count === 0 && b.response_count === 0) {
                return a.lesson_order - b.lesson_order;
            }
            if (a.response_count === 0) return 1;
            if (b.response_count === 0) return -1;
            return (a.average_rating || 0) - (b.average_rating || 0);
        });
    }, [lessons]);

    return (
        <div className="tfb-root">
            <header className="tfb-header">
                <h1 className="tfb-title">📊 Darslar bo'yicha o'quvchilar bahosi</h1>
                <p className="tfb-subtitle">
                    Har bir dars bo'yicha o'rtacha yulduz, javoblar soni va izohlar.
                    Pastdagi reytingdagi darslarni qayta ko'rib chiqing.
                </p>
            </header>

            {courseLoading ? (
                <div className="tfb-empty">Yuklanmoqda...</div>
            ) : courses.length === 0 ? (
                <div className="tfb-empty">Sizda kurs yo'q.</div>
            ) : (
                <>
                    <div className="tfb-course-tabs">
                        {courses.map(c => (
                            <button
                                key={c.id}
                                className={`tfb-course-tab ${activeCourseId === c.id ? 'is-active' : ''}`}
                                onClick={() => setActiveCourseId(c.id)}
                                type="button"
                            >
                                {c.title}
                            </button>
                        ))}
                    </div>

                    {overviewLoading ? (
                        <div className="tfb-empty">Yuklanmoqda...</div>
                    ) : overviewError ? (
                        <div className="tfb-empty tfb-error">{overviewError}</div>
                    ) : !overview ? null : (
                        <>
                            <div className="tfb-summary">
                                <div className="tfb-summary-card">
                                    <div className="tfb-summary-label">Jami javoblar</div>
                                    <div className="tfb-summary-value">{totalResponses}</div>
                                </div>
                                <div className="tfb-summary-card">
                                    <div className="tfb-summary-label">Kurs o'rtacha</div>
                                    <div className="tfb-summary-value">
                                        {courseAvg != null
                                            ? <><span className="tfb-rating-star">★</span> {courseAvg.toFixed(2)}</>
                                            : <span className="tfb-muted">—</span>}
                                    </div>
                                </div>
                                <div className="tfb-summary-card">
                                    <div className="tfb-summary-label">Darslar</div>
                                    <div className="tfb-summary-value">{lessons.length}</div>
                                </div>
                            </div>

                            {totalResponses === 0 ? (
                                <div className="tfb-empty">
                                    Hozircha hech kim baho qo'ymagan. Talabalar dars oxirida baholashlari mumkin.
                                </div>
                            ) : (
                                <div className="tfb-lessons">
                                    {sorted.map(l => (
                                        <LessonRow
                                            key={l.lesson_id}
                                            lesson={l}
                                            expanded={expandedLessonId === l.lesson_id}
                                            onToggle={() => handleToggleLesson(l.lesson_id)}
                                            comments={comments[l.lesson_id]}
                                            commentsLoading={commentsLoading[l.lesson_id]}
                                        />
                                    ))}
                                </div>
                            )}
                        </>
                    )}
                </>
            )}
        </div>
    );
}

function LessonRow({lesson, expanded, onToggle, comments, commentsLoading}) {
    const {lesson_title, lesson_order, response_count, average_rating, rating_breakdown} = lesson;
    const maxBucket = Math.max(...Object.values(rating_breakdown || {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}));

    return (
        <div className={`tfb-lesson ${expanded ? 'is-expanded' : ''}`}>
            <button type="button" className="tfb-lesson-head" onClick={onToggle}>
                <div className="tfb-lesson-meta">
                    <span className="tfb-lesson-order">#{lesson_order + 1}</span>
                    <span className="tfb-lesson-title">{lesson_title}</span>
                </div>
                <div className="tfb-lesson-stats">
                    <div className="tfb-lesson-stat">
                        <span className="tfb-rating-star">★</span>
                        <strong>{average_rating != null ? average_rating.toFixed(2) : '—'}</strong>
                    </div>
                    <div className="tfb-lesson-stat tfb-lesson-count">
                        {response_count} javob
                    </div>
                    <div className="tfb-lesson-arrow">{expanded ? '▾' : '▸'}</div>
                </div>
            </button>

            {expanded && (
                <div className="tfb-lesson-body">
                    <div className="tfb-breakdown">
                        {[5, 4, 3, 2, 1].map(star => {
                            const count = rating_breakdown?.[star] || 0;
                            const pct = maxBucket ? Math.round((count / maxBucket) * 100) : 0;
                            return (
                                <div key={star} className="tfb-bar-row">
                                    <span className="tfb-bar-label">{star} ★</span>
                                    <div className="tfb-bar-track">
                                        <div className="tfb-bar-fill" style={{width: `${pct}%`}}/>
                                    </div>
                                    <span className="tfb-bar-count">{count}</span>
                                </div>
                            );
                        })}
                    </div>

                    <div className="tfb-comments">
                        <h4 className="tfb-comments-title">Oxirgi izohlar</h4>
                        {commentsLoading ? (
                            <div className="tfb-empty-soft">Yuklanmoqda...</div>
                        ) : !comments || comments.length === 0 ? (
                            <div className="tfb-empty-soft">Izohlar yo'q.</div>
                        ) : (
                            <ul className="tfb-comments-list">
                                {comments.map(c => (
                                    <li key={c.id} className="tfb-comment">
                                        <div className="tfb-comment-head">
                                            <span className="tfb-comment-rating">
                                                <span className="tfb-rating-star">★</span> {c.rating}
                                            </span>
                                            <span className="tfb-comment-name">
                                                {c.student_name || `#${c.student_id}`}
                                            </span>
                                            <span className="tfb-comment-date">
                                                {formatDate(c.updated_at)}
                                            </span>
                                        </div>
                                        {c.comment
                                            ? <p className="tfb-comment-text">{c.comment}</p>
                                            : <p className="tfb-comment-text tfb-muted">— izoh yo'q —</p>}
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

function formatDate(iso) {
    if (!iso) return '';
    try {
        const d = new Date(iso);
        return d.toLocaleDateString('uz-UZ', {year: 'numeric', month: 'short', day: 'numeric'});
    } catch {
        return iso;
    }
}

export default TeacherFeedback;
