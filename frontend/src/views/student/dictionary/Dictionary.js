import { useState, useEffect, useCallback } from 'react';
import './Dictionary.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';

const BASE = `${API_URL}v1/dictionary/`;

export default function Dictionary() {
    const { request } = useHttp();

    const [words,    setWords]    = useState([]);
    const [loading,  setLoading]  = useState(true);
    const [deleting, setDeleting] = useState(null);
    const [search,   setSearch]   = useState('');
    const [error,    setError]    = useState('');
    const [toast,    setToast]    = useState('');
    const [filter,   setFilter]   = useState('all');
    const [view,     setView]     = useState('grid'); // 'grid' | 'list'

    const showToast = useCallback((msg, type = 'success') => {
        setToast({ msg, type });
        setTimeout(() => setToast(''), 3000);
    }, []);

    // Слушаем событие из DictSelectionPopup → Dictionary уже добавил слово через API,
    // нам нужно только перезагрузить список
    useEffect(() => {
        const onWordAdded = () => {
            request(BASE, 'GET', null, headers())
                .then(setWords)
                .catch(() => {});
        };
        window.addEventListener('dict:word-added', onWordAdded);
        return () => window.removeEventListener('dict:word-added', onWordAdded);
    }, []);

    useEffect(() => {
        request(BASE, 'GET', null, headers())
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

    const lessons = [...new Set(words.map(w => w.lesson_id).filter(Boolean))].sort((a, b) => a - b);

    const filtered = words.filter(w => {
        const matchSearch =
            w.word.toLowerCase().includes(search.toLowerCase()) ||
            (w.context || '').toLowerCase().includes(search.toLowerCase());
        const matchLesson = filter === 'all' || String(w.lesson_id) === String(filter);
        return matchSearch && matchLesson;
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

            {/* ── Sidebar ── */}
            <aside className="d-sidebar">
                <div className="d-sidebar-logo">
                    <span className="d-sidebar-icon">📖</span>
                    <div>
                        <div className="d-sidebar-title">Lug'at</div>
                        <div className="d-sidebar-hint">Darsdan so'z qo'shing</div>
                    </div>
                </div>

                <div className="d-sidebar-counter">
                    <span className="d-counter-num">{words.length}</span>
                    <span className="d-counter-label">so'z saqlangan</span>
                </div>

                {/* Stats mini */}
                <div className="d-sidebar-stats">
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

                {/* Lesson filters */}
                {lessons.length > 0 && (
                    <div className="d-lessons-nav">
                        <div className="d-lessons-label">Darslar</div>
                        <button
                            className={`d-lesson-item ${filter === 'all' ? 'active' : ''}`}
                            onClick={() => setFilter('all')}
                        >
                            <span className="d-lesson-dot" />
                            Hammasi
                            <span className="d-lesson-count">{words.length}</span>
                        </button>
                        {lessons.map(lid => (
                            <button
                                key={lid}
                                className={`d-lesson-item ${String(filter) === String(lid) ? 'active' : ''}`}
                                onClick={() => setFilter(String(lid))}
                            >
                                <span className="d-lesson-dot" />
                                {lid}-dars
                                <span className="d-lesson-count">
                                    {words.filter(w => String(w.lesson_id) === String(lid)).length}
                                </span>
                            </button>
                        ))}
                    </div>
                )}

                <div className="d-sidebar-tip">
                    <div className="d-tip-icon">💡</div>
                    <p>Dars paytida matnni belgilab, <strong>«Lug'atga qo'shish»</strong> tugmasini bosing</p>
                </div>
            </aside>

            {/* ── Main ── */}
            <main className="d-main">

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
                                    ? "Darsda matnni belgilab lug'atga qo'shing"
                                    : ''}
                        </div>
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
                                        {item.lesson_id && (
                                            <span className="d-card-tag">{item.lesson_id}-dars</span>
                                        )}
                                    </div>
                                    {item.context && (
                                        <p className="d-card-ctx">"{item.context}"</p>
                                    )}
                                    <button
                                        className="d-card-del"
                                        onClick={() => handleDelete(item.id)}
                                        disabled={deleting === item.id}
                                    >
                                        {deleting === item.id
                                            ? <span className="d-spin" />
                                            : <svg viewBox="0 0 20 20" fill="none">
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
                                {item.lesson_id && (
                                    <span className="d-list-tag">{item.lesson_id}-dars</span>
                                )}
                                <button
                                    className="d-list-del"
                                    onClick={() => handleDelete(item.id)}
                                    disabled={deleting === item.id}
                                >
                                    {deleting === item.id ? <span className="d-spin" /> : '✕'}
                                </button>
                            </div>
                        ))}
                    </div>
                )}

            </main>
        </div>
    );
}