import { useState, useEffect, useCallback } from 'react';
import './Dictionary.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import Practice from './Practice';

const BASE = `${API_URL}v1/dictionary/`;
const langParam = () => `?lang=${localStorage.getItem('lang') || 'uz'}`;

export default function Dictionary() {
    const { request } = useHttp();

    const [words,    setWords]    = useState([]);
    const [loading,  setLoading]  = useState(true);
    const [deleting, setDeleting] = useState(null);
    const [search,   setSearch]   = useState('');
    const [error,    setError]    = useState('');
    const [toast,    setToast]    = useState('');
    const [filter,   setFilter]   = useState('all');
    const [view,     setView]     = useState('grid');
    const [tab,      setTab]      = useState('words'); // 'words' | 'practice'

    // ✅ Modal state
    const [showModal, setShowModal] = useState(false);
    const [adding,    setAdding]    = useState(false);
    const [form,      setForm]      = useState({ word: '', context: '' });
    const [formError, setFormError] = useState('');

    const showToast = useCallback((msg, type = 'success') => {
        setToast({ msg, type });
        setTimeout(() => setToast(''), 3000);
    }, []);

    useEffect(() => {
        const onWordAdded = () => {
            request(BASE + langParam(), 'GET', null, headers())
                .then(setWords)
                .catch(() => {});
        };
        window.addEventListener('dict:word-added', onWordAdded);
        return () => window.removeEventListener('dict:word-added', onWordAdded);
    }, []);

    useEffect(() => {
        request(BASE + langParam(), 'GET', null, headers())
            .then(setWords)
            .catch(() => setError("So'zlarni yuklashda xatolik"))
            .finally(() => setLoading(false));
    }, []);

    const handleDelete = (id) => {
        setDeleting(id);
        request(`${BASE}${id}`, 'DELETE', null, headers())
            .then(() => {
                setWords(w => w.filter(x => x.id !== id));
                showToast("O'chirildi", 'warn');
            })
            .catch(() => setError("O'chirishda xatolik"))
            .finally(() => setDeleting(null));
    };

    // ✅ Ruchnoy so'z qo'shish
    const handleAddWord = async () => {
        if (!form.word.trim()) {
            setFormError("So'z kiriting!");
            return;
        }
        setAdding(true);
        setFormError('');
        try {
            const newWord = await request(BASE, 'POST', {
                word: form.word.trim(),
                context: form.context.trim() || null,
                lesson_id: null,
                lang: localStorage.getItem('lang') || 'uz',
            }, headers());

            setWords(w => [newWord, ...w]);
            setShowModal(false);
            setForm({ word: '', context: '' });
            showToast("So'z qo'shildi ✓");
        } catch (e) {
            // Surface the actual backend reason (length / word count / dup /
            // schema validation) instead of a generic "xatolik" — the popup
            // path already does this; the manual dialog was hiding it.
            const detail = e?.response?.data?.detail;
            let msg = "Xatolik yuz berdi, qayta urinib ko'ring";
            if (typeof detail === 'string' && detail.trim()) {
                msg = detail;
            } else if (Array.isArray(detail) && detail[0]?.msg) {
                msg = detail[0].msg;
            }
            setFormError(msg);
        } finally {
            setAdding(false);
        }
    };

    const closeModal = () => {
        setShowModal(false);
        setForm({ word: '', context: '' });
        setFormError('');
    };

    /* ── Scope tree ──
       Build a course → lessons hierarchy from the words themselves so
       the sidebar reflects exactly what the student has saved (no extra
       round-trip to /courses or /lessons just to render the filter). */
    const scopeTree = (() => {
        const byCourse = new Map();   // course_id → { id, title, total, lessons: Map }
        let manual = 0;
        for (const w of words) {
            if (!w.lesson_id) { manual += 1; continue; }
            const cid = w.course_id || 0;
            let course = byCourse.get(cid);
            if (!course) {
                course = {
                    id: cid,
                    title: w.course_title || (cid ? `Kurs #${cid}` : 'Eski darslar'),
                    total: 0,
                    lessons: new Map(),
                };
                byCourse.set(cid, course);
            }
            course.total += 1;
            let lesson = course.lessons.get(w.lesson_id);
            if (!lesson) {
                lesson = {
                    id: w.lesson_id,
                    title: w.lesson_title || `${w.lesson_id}-dars`,
                    count: 0,
                };
                course.lessons.set(w.lesson_id, lesson);
            }
            lesson.count += 1;
        }
        // Sort courses by title, lessons by id (preserves curriculum order).
        const courses = [...byCourse.values()]
            .map(c => ({ ...c, lessons: [...c.lessons.values()].sort((a, b) => a.id - b.id) }))
            .sort((a, b) => a.title.localeCompare(b.title));
        return { courses, manual };
    })();

    const lessons = scopeTree.courses.flatMap(c => c.lessons.map(l => l.id));

    /* Filter encoding:
         'all'              — no scope filter
         'manual'           — words with no lesson_id
         'c:<course_id>'    — every word in that course
         'l:<lesson_id>'    — single lesson (preserves the original UX)            */
    const matchesScope = (w) => {
        if (filter === 'all') return true;
        if (filter === 'manual') return !w.lesson_id;
        if (filter.startsWith('c:')) {
            const cid = Number(filter.slice(2));
            return Number(w.course_id || 0) === cid;
        }
        if (filter.startsWith('l:')) {
            return String(w.lesson_id) === filter.slice(2);
        }
        // Legacy bare lesson id ("13") — kept so old links still work
        return String(w.lesson_id) === String(filter);
    };

    const filtered = words.filter(w => {
        const matchSearch =
            w.word.toLowerCase().includes(search.toLowerCase()) ||
            (w.context || '').toLowerCase().includes(search.toLowerCase());
        return matchSearch && matchesScope(w);
    });

    if (loading) return (
        <div className="d-loading">
            <div className="d-loader-ring">
                <div /><div /><div /><div />
            </div>
            <p>Yuklanmoqda...</p>
        </div>
    );

    return (
        <div className="d-wrap">

            {/* Toast */}
            {toast && (
                <div className={`d-toast ${toast.type === 'warn' ? 'warn' : ''}`}>
                    <span className="d-toast-dot" />
                    {toast.msg}
                </div>
            )}

            {/* ✅ Modal */}
            {showModal && (
                <div className="d-modal-overlay" onClick={closeModal}>
                    <div className="d-modal" onClick={e => e.stopPropagation()}>
                        <div className="d-modal-header">
                            <span className="d-modal-icon">✏️</span>
                            <div>
                                <div className="d-modal-title">So'z qo'shish</div>
                                <div className="d-modal-sub">Lug'atingizga yangi so'z qo'shing</div>
                            </div>
                            <button className="d-modal-close" onClick={closeModal}>✕</button>
                        </div>

                        <div className="d-modal-body">
                            <div className="d-field">
                                <label className="d-label">So'z <span className="d-required">*</span></label>
                                <input
                                    className={`d-input ${formError && !form.word.trim() ? 'error' : ''}`}
                                    placeholder="Masalan: flexbox, margin, gap..."
                                    value={form.word}
                                    onChange={e => {
                                        setForm(f => ({ ...f, word: e.target.value }));
                                        setFormError('');
                                    }}
                                    onKeyDown={e => e.key === 'Enter' && handleAddWord()}
                                    autoFocus
                                />
                            </div>

                            <div className="d-field">
                                <label className="d-label">
                                    Izoh
                                    <span className="d-optional">ixtiyoriy</span>
                                </label>
                                <textarea
                                    className="d-textarea"
                                    placeholder="Bu so'zning ma'nosi yoki misol..."
                                    value={form.context}
                                    onChange={e => setForm(f => ({ ...f, context: e.target.value }))}
                                    rows={3}
                                />
                            </div>

                            {formError && (
                                <div className="d-form-error">⚠️ {formError}</div>
                            )}
                        </div>

                        <div className="d-modal-footer">
                            <button className="d-btn-cancel" onClick={closeModal}>
                                Bekor qilish
                            </button>
                            <button
                                className="d-btn-add"
                                onClick={handleAddWord}
                                disabled={adding}
                            >
                                {adding
                                    ? <><span className="d-spin-white" /> Qo'shilmoqda...</>
                                    : <><span>+</span> Qo'shish</>
                                }
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* ── Sidebar ── */}
            <aside className="d-sidebar">
                <div className="d-sidebar-logo">
                    <span className="d-sidebar-icon">📖</span>
                    <div>
                        <div className="d-sidebar-title">Lug'at</div>
                        <div className="d-sidebar-hint">Darsdan so'z qo'shing</div>
                    </div>
                </div>

                {/* Single compact stat strip — the big counter pill was redundant
                    with the "Hammasi N" lesson filter directly below it, and the
                    sidebar "+ So'z qo'shish" duplicated the topbar action. Kept
                    a tighter mini-stats row so dars/natija counts stay visible. */}
                <div className="d-sidebar-stats">
                    <div className="d-sstat">
                        <span className="d-sstat-val">{words.length}</span>
                        <span className="d-sstat-key">so'z</span>
                    </div>
                    <div className="d-sstat-div" />
                    <div className="d-sstat">
                        <span className="d-sstat-val">{lessons.length}</span>
                        <span className="d-sstat-key">dars</span>
                    </div>
                    <div className="d-sstat-div" />
                    <div className="d-sstat">
                        <span className="d-sstat-val">{filtered.length}</span>
                        <span className="d-sstat-key">natija</span>
                    </div>
                </div>

                {/* Scope filter — Hammasi / Qo'lda / Course → Lessons hierarchy.
                    Course headers filter every lesson in that course at once;
                    individual lessons drill down further. */}
                {(scopeTree.courses.length > 0 || scopeTree.manual > 0) && (
                    <div className="d-lessons-nav">
                        <div className="d-lessons-label">Kurslar va darslar</div>
                        <button
                            className={`d-lesson-item ${filter === 'all' ? 'active' : ''}`}
                            onClick={() => setFilter('all')}
                        >
                            <span className="d-lesson-dot" />
                            Hammasi
                            <span className="d-lesson-count">{words.length}</span>
                        </button>
                        {scopeTree.manual > 0 && (
                            <button
                                className={`d-lesson-item ${filter === 'manual' ? 'active' : ''}`}
                                onClick={() => setFilter('manual')}
                            >
                                <span className="d-lesson-dot" />
                                Qo'lda qo'shilgan
                                <span className="d-lesson-count">{scopeTree.manual}</span>
                            </button>
                        )}
                        {scopeTree.courses.map((c) => {
                            const courseKey = `c:${c.id}`;
                            return (
                                <div key={c.id} className="d-course-group">
                                    <button
                                        className={`d-lesson-item d-course-item ${filter === courseKey ? 'active' : ''}`}
                                        onClick={() => setFilter(courseKey)}
                                        title={c.title}
                                    >
                                        <span className="d-lesson-dot" />
                                        <span className="d-course-name">{c.title}</span>
                                        <span className="d-lesson-count">{c.total}</span>
                                    </button>
                                    {c.lessons.map((l) => {
                                        const lessonKey = `l:${l.id}`;
                                        return (
                                            <button
                                                key={l.id}
                                                className={`d-lesson-item d-lesson-child ${filter === lessonKey ? 'active' : ''}`}
                                                onClick={() => setFilter(lessonKey)}
                                                title={l.title}
                                            >
                                                <span className="d-lesson-dot" />
                                                <span className="d-lesson-child-name">{l.title}</span>
                                                <span className="d-lesson-count">{l.count}</span>
                                            </button>
                                        );
                                    })}
                                </div>
                            );
                        })}
                    </div>
                )}

                <div className="d-sidebar-tip">
                    <div className="d-tip-icon">💡</div>
                    <p>Dars paytida matnni belgilab, <strong>«Lug'atga qo'shish»</strong> tugmasini bosing</p>
                </div>
            </aside>

            {/* ── Main ── */}
            <main className="d-main">

                {/* Tab strip — "So'zlar" (existing) | "Mashq" (SRS practice) */}
                <div className="d-tabs">
                    <button
                        className={`d-tab ${tab === 'words' ? 'active' : ''}`}
                        onClick={() => setTab('words')}
                    >
                        📒 So'zlar
                    </button>
                    <button
                        className={`d-tab ${tab === 'practice' ? 'active' : ''}`}
                        onClick={() => setTab('practice')}
                    >
                        🎯 Mashq
                    </button>
                </div>

                {tab === 'practice' ? <Practice /> : <>

                {/* Top bar */}
                <div className="d-topbar">
                    <div className="d-search-wrap">
                        <svg className="d-search-icon" viewBox="0 0 20 20" fill="none">
                            <circle cx="9" cy="9" r="6" stroke="currentColor" strokeWidth="1.8"/>
                            <path d="M13.5 13.5L17 17" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
                        </svg>
                        <input
                            className="d-search"
                            placeholder="So'z qidirish..."
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                        />
                        {search && (
                            <button className="d-search-clear" onClick={() => setSearch('')}>✕</button>
                        )}
                    </div>

                    {/* ✅ Topbar da ham qo'shish tugmasi */}
                    <button className="d-topbar-add" onClick={() => setShowModal(true)}>
                        <span>+</span> So'z qo'shish
                    </button>

                    <div className="d-view-toggle">
                        <button
                            className={`d-vbtn ${view === 'grid' ? 'active' : ''}`}
                            onClick={() => setView('grid')}
                            title="Grid"
                        >
                            <svg viewBox="0 0 16 16" fill="currentColor">
                                <rect x="1" y="1" width="6" height="6" rx="1.5"/>
                                <rect x="9" y="1" width="6" height="6" rx="1.5"/>
                                <rect x="1" y="9" width="6" height="6" rx="1.5"/>
                                <rect x="9" y="9" width="6" height="6" rx="1.5"/>
                            </svg>
                        </button>
                        <button
                            className={`d-vbtn ${view === 'list' ? 'active' : ''}`}
                            onClick={() => setView('list')}
                            title="List"
                        >
                            <svg viewBox="0 0 16 16" fill="currentColor">
                                <rect x="1" y="2" width="14" height="2.5" rx="1.25"/>
                                <rect x="1" y="6.75" width="14" height="2.5" rx="1.25"/>
                                <rect x="1" y="11.5" width="14" height="2.5" rx="1.25"/>
                            </svg>
                        </button>
                    </div>
                </div>

                {error && (
                    <div className="d-error">
                        {error}
                        <button onClick={() => setError('')}>✕</button>
                    </div>
                )}

                {/* Empty state */}
                {filtered.length === 0 && (
                    <div className="d-empty">
                        <div className="d-empty-visual">
                            {search ? '🔎' : words.length === 0 ? '📭' : '🗂️'}
                        </div>
                        <div className="d-empty-title">
                            {search
                                ? `«${search}» topilmadi`
                                : words.length === 0
                                    ? "Lug'at hali bo'sh"
                                    : "Bu darsda so'z yo'q"}
                        </div>
                        <div className="d-empty-sub">
                            {search
                                ? "Boshqa kalit so'z bilan qidiring"
                                : words.length === 0
                                    ? "Quyidagi tugma orqali so'z qo'shing"
                                    : ''}
                        </div>
                        {words.length === 0 && !search && (
                            <button className="d-empty-reset" onClick={() => setShowModal(true)}>
                                + So'z qo'shish
                            </button>
                        )}
                        {search && (
                            <button className="d-empty-reset" onClick={() => setSearch('')}>
                                Tozalash
                            </button>
                        )}
                        {!search && filter !== 'all' && (
                            <button className="d-empty-reset" onClick={() => setFilter('all')}>
                                Barchasini ko'rish
                            </button>
                        )}
                    </div>
                )}

                {/* Grid view */}
                {filtered.length > 0 && view === 'grid' && (
                    <div className="d-grid">
                        {filtered.map((item, i) => (
                            <div
                                className="d-card"
                                key={item.id}
                                style={{ '--delay': `${Math.min(i * 0.04, 0.35)}s` }}
                            >
                                <div className="d-card-inner">
                                    <div className="d-card-top">
                                        <span className="d-card-word">{item.word}</span>
                                        {item.lesson_id
                                            ? <span className="d-card-tag">{item.lesson_id}-dars</span>
                                            : <span className="d-card-tag manual">✍️ qo'lda</span>
                                        }
                                    </div>
                                    {item.context && (
                                        <p className="d-card-ctx">"{item.context}"</p>
                                    )}
                                    <button
                                        className="d-card-del"
                                        onClick={() => handleDelete(item.id)}
                                        disabled={deleting === item.id}
                                        aria-label={`Удалить слово ${item.word}`}
                                        title="Удалить слово"
                                    >
                                        {deleting === item.id
                                            ? <span className="d-spin" />
                                            : <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
                                                <path d="M7 4h6M4 7h12M6 7l1 9h6l1-9" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
                                              </svg>
                                        }
                                    </button>
                                </div>
                                <div className="d-card-accent" />
                            </div>
                        ))}
                    </div>
                )}

                {/* List view */}
                {filtered.length > 0 && view === 'list' && (
                    <div className="d-list">
                        {filtered.map((item, i) => (
                            <div
                                className="d-list-row"
                                key={item.id}
                                style={{ '--delay': `${Math.min(i * 0.03, 0.3)}s` }}
                            >
                                <div className="d-list-index">{i + 1}</div>
                                <div className="d-list-word">{item.word}</div>
                                <div className="d-list-ctx">{item.context || '—'}</div>
                                {item.lesson_id
                                    ? <span className="d-list-tag">Урок {item.lesson_id}</span>
                                    : <span className="d-list-tag manual">✍️ вручную</span>
                                }
                                <button
                                    className="d-list-del"
                                    onClick={() => handleDelete(item.id)}
                                    disabled={deleting === item.id}
                                    aria-label={`Удалить слово ${item.word}`}
                                    title="Удалить слово"
                                >
                                    {deleting === item.id ? <span className="d-spin" aria-hidden="true" /> : '✕'}
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                </>}
            </main>
        </div>
    );
}