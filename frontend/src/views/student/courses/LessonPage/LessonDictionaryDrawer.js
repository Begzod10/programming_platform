import { useState, useEffect, useMemo, useCallback } from 'react';
import { createPortal } from 'react-dom';
import './LessonDictionaryDrawer.css';
import { API_URL, useHttp, headers } from '../../../../api/search/base';

const BASE = `${API_URL}v1/dictionary/`;
const langParam = () => `?lang=${localStorage.getItem('lang') || 'uz'}`;

function ChevronIcon() {
    return (
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor"
             strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="6 9 12 15 18 9" />
        </svg>
    );
}

function CloseIcon() {
    return (
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"
             strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="6" y1="6" x2="18" y2="18" />
            <line x1="18" y1="6" x2="6" y2="18" />
        </svg>
    );
}

function SearchIcon() {
    return (
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor"
             strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="7" />
            <line x1="20" y1="20" x2="16.65" y2="16.65" />
        </svg>
    );
}

function TrashIcon() {
    return (
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor"
             strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="3 6 5 6 21 6" />
            <path d="M19 6l-2 14a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L5 6" />
            <line x1="10" y1="11" x2="10" y2="17" />
            <line x1="14" y1="11" x2="14" y2="17" />
        </svg>
    );
}

function BookIcon() {
    return (
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor"
             strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 5a2 2 0 0 1 2-2h13v18H6a2 2 0 0 0-2 2V5z" />
            <path d="M8 8h7" />
            <path d="M8 12h5" />
        </svg>
    );
}

export default function LessonDictionaryDrawer({ lessonId }) {
    const { request } = useHttp();
    const [isOpen, setIsOpen] = useState(false);
    const [words, setWords] = useState([]);
    const [loading, setLoading] = useState(false);
    const [search, setSearch] = useState('');
    const [scope, setScope] = useState('lesson'); // 'lesson' | 'all'
    const [expandedId, setExpandedId] = useState(null);
    const [deletingId, setDeletingId] = useState(null);

    const fetchWords = useCallback(() => {
        setLoading(true);
        request(BASE + langParam(), 'GET', null, headers())
            .then((data) => Array.isArray(data) ? setWords(data) : setWords([]))
            .catch(() => setWords([]))
            .finally(() => setLoading(false));
    }, [request]);

    // Load once on open, and whenever a new word is added anywhere in the app.
    useEffect(() => {
        if (!isOpen) return;
        fetchWords();
    }, [isOpen, fetchWords]);

    useEffect(() => {
        const onAdded = () => {
            // Refresh in background — only matters if drawer is open
            if (isOpen) fetchWords();
        };
        window.addEventListener('dict:word-added', onAdded);
        return () => window.removeEventListener('dict:word-added', onAdded);
    }, [isOpen, fetchWords]);

    // Esc to close
    useEffect(() => {
        if (!isOpen) return;
        const onKey = (e) => { if (e.key === 'Escape') setIsOpen(false); };
        window.addEventListener('keydown', onKey);
        return () => window.removeEventListener('keydown', onKey);
    }, [isOpen]);

    const lessonWords = useMemo(
        () => words.filter(w => w.lesson_id === lessonId),
        [words, lessonId]
    );

    const visibleWords = useMemo(() => {
        const pool = scope === 'lesson' ? lessonWords : words;
        const q = search.trim().toLowerCase();
        if (!q) return pool;
        return pool.filter(w =>
            (w.word || '').toLowerCase().includes(q) ||
            (w.context || '').toLowerCase().includes(q)
        );
    }, [scope, lessonWords, words, search]);

    const handleDelete = (id) => {
        setDeletingId(id);
        request(`${BASE}${id}`, 'DELETE', null, headers())
            .then(() => setWords(prev => prev.filter(w => w.id !== id)))
            .catch(() => {})
            .finally(() => setDeletingId(null));
    };

    const triggerBadge = lessonWords.length;

    return createPortal(
        <>
            {/* Floating trigger */}
            <button
                type="button"
                className={`ldd-fab ${isOpen ? 'ldd-fab--active' : ''}`}
                onClick={() => setIsOpen(v => !v)}
                aria-label="Lug'at"
                title="Lug'at"
            >
                <BookIcon />
                {triggerBadge > 0 && !isOpen && (
                    <span className="ldd-fab__badge">{triggerBadge > 99 ? '99+' : triggerBadge}</span>
                )}
            </button>

            {/* Backdrop — lets the lesson keep scrolling but dims & catches outside-click */}
            {isOpen && (
                <div
                    className="ldd-backdrop"
                    onClick={() => setIsOpen(false)}
                    aria-hidden="true"
                />
            )}

            {/* Drawer */}
            <aside className={`ldd-drawer ${isOpen ? 'ldd-drawer--open' : ''}`}
                   aria-hidden={!isOpen}
                   aria-label="Lug'at darsi">
                <header className="ldd-head">
                    <div className="ldd-head__title">
                        <span className="ldd-head__icon"><BookIcon /></span>
                        <div>
                            <div className="ldd-head__h1">Mening lug'atim</div>
                            <div className="ldd-head__sub">
                                {scope === 'lesson'
                                    ? `Ushbu darsdan: ${lessonWords.length}`
                                    : `Jami: ${words.length}`}
                            </div>
                        </div>
                    </div>
                    <button
                        type="button"
                        className="ldd-close"
                        onClick={() => setIsOpen(false)}
                        aria-label="Yopish"
                    >
                        <CloseIcon />
                    </button>
                </header>

                <div className="ldd-scope">
                    <button
                        type="button"
                        className={`ldd-scope__btn ${scope === 'lesson' ? 'is-active' : ''}`}
                        onClick={() => setScope('lesson')}
                    >
                        Ushbu dars
                        <span className="ldd-scope__count">{lessonWords.length}</span>
                    </button>
                    <button
                        type="button"
                        className={`ldd-scope__btn ${scope === 'all' ? 'is-active' : ''}`}
                        onClick={() => setScope('all')}
                    >
                        Hammasi
                        <span className="ldd-scope__count">{words.length}</span>
                    </button>
                </div>

                <div className="ldd-search">
                    <span className="ldd-search__icon"><SearchIcon /></span>
                    <input
                        type="text"
                        placeholder="So'z yoki ma'no bo'yicha qidirish…"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                    {search && (
                        <button
                            type="button"
                            className="ldd-search__clear"
                            onClick={() => setSearch('')}
                            aria-label="Tozalash"
                        >
                            <CloseIcon />
                        </button>
                    )}
                </div>

                <div className="ldd-list">
                    {loading && words.length === 0 ? (
                        <div className="ldd-state">
                            <div className="ldd-spinner" />
                            <div>Yuklanmoqda…</div>
                        </div>
                    ) : visibleWords.length === 0 ? (
                        <div className="ldd-state">
                            {search ? (
                                <>
                                    <div className="ldd-state__title">Hech narsa topilmadi</div>
                                    <div className="ldd-state__hint">"{search}" bo'yicha so'z yo'q</div>
                                </>
                            ) : scope === 'lesson' ? (
                                <>
                                    <div className="ldd-state__title">Bu darsdan so'z qo'shilmagan</div>
                                    <div className="ldd-state__hint">
                                        Darsda matnni belgilab, "Lug'atga qo'shish" tugmasini bosing
                                    </div>
                                </>
                            ) : (
                                <>
                                    <div className="ldd-state__title">Lug'at bo'sh</div>
                                    <div className="ldd-state__hint">
                                        Darsda matnni belgilab, so'zlar to'plang
                                    </div>
                                </>
                            )}
                        </div>
                    ) : (
                        visibleWords.map((w) => {
                            const isExpanded = expandedId === w.id;
                            const isThisLesson = w.lesson_id === lessonId;
                            return (
                                <div
                                    key={w.id}
                                    className={`ldd-item ${isExpanded ? 'is-expanded' : ''} ${isThisLesson ? 'is-current' : ''}`}
                                >
                                    <button
                                        type="button"
                                        className="ldd-item__head"
                                        onClick={() => setExpandedId(isExpanded ? null : w.id)}
                                    >
                                        <span className="ldd-item__word">{w.word}</span>
                                        <span className="ldd-item__meta">
                                            {scope === 'all' && w.lesson_id && (
                                                <span className="ldd-item__tag">
                                                    {isThisLesson ? 'shu dars' : `${w.lesson_id}-dars`}
                                                </span>
                                            )}
                                            <span className={`ldd-item__chev ${isExpanded ? 'is-up' : ''}`}>
                                                <ChevronIcon />
                                            </span>
                                        </span>
                                    </button>
                                    {isExpanded && (
                                        <div className="ldd-item__body">
                                            {w.context ? (
                                                <p className="ldd-item__ctx">"{w.context}"</p>
                                            ) : (
                                                <p className="ldd-item__ctx ldd-item__ctx--empty">
                                                    Ma'no saqlanmagan
                                                </p>
                                            )}
                                            <button
                                                type="button"
                                                className="ldd-item__del"
                                                onClick={() => handleDelete(w.id)}
                                                disabled={deletingId === w.id}
                                            >
                                                <TrashIcon />
                                                <span>{deletingId === w.id ? "O'chirilmoqda…" : "O'chirish"}</span>
                                            </button>
                                        </div>
                                    )}
                                </div>
                            );
                        })
                    )}
                </div>
            </aside>
        </>,
        document.body
    );
}
