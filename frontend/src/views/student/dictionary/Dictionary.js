import { useState, useEffect, useCallback } from 'react';
import './Dictionary.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import Practice from './Practice';
import AppHeader from '../../../components/appheader/AppHeader';
import { useTranslation } from '../../../i18n/useTranslation';
import { Search, Plus, X, Trash2, Target, BookOpen, ChevronLeft, LayoutGrid, List } from 'lucide-react';

const BASE = `${API_URL}v1/dictionary/`;
const langParam = () => `?lang=${localStorage.getItem('lang') || 'uz'}`;

export default function Dictionary() {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const ru = lang === 'ru';

    const [words,    setWords]    = useState([]);
    const [loading,  setLoading]  = useState(true);
    const [deleting, setDeleting] = useState(null);
    const [search,   setSearch]   = useState('');
    const [error,    setError]    = useState('');
    const [toast,    setToast]    = useState('');
    const [filter,   setFilter]   = useState('all');
    const [view,     setView]     = useState('grid');
    const [expandedId, setExpandedId] = useState(null);
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
            .catch(() => setError(ru ? 'Ошибка при загрузке слов' : "So'zlarni yuklashda xatolik"))
            .finally(() => setLoading(false));
    }, []);

    const handleDelete = (id) => {
        setDeleting(id);
        request(`${BASE}${id}`, 'DELETE', null, headers())
            .then(() => {
                setWords(w => w.filter(x => x.id !== id));
                showToast(ru ? 'Удалено' : "O'chirildi", 'warn');
            })
            .catch(() => setError(ru ? 'Ошибка при удалении' : "O'chirishda xatolik"))
            .finally(() => setDeleting(null));
    };

    // ✅ Ruchnoy so'z qo'shish
    const handleAddWord = async () => {
        if (!form.word.trim()) {
            setFormError(ru ? 'Введите слово!' : "So'z kiriting!");
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
            showToast(ru ? 'Слово добавлено ✓' : "So'z qo'shildi ✓");
        } catch (e) {
            // Surface the actual backend reason (length / word count / dup /
            // schema validation) instead of a generic "xatolik" — the popup
            // path already does this; the manual dialog was hiding it.
            const detail = e?.response?.data?.detail;
            let msg = ru ? 'Произошла ошибка, попробуйте ещё раз' : "Xatolik yuz berdi, qayta urinib ko'ring";
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
                    title: w.course_title || (cid ? (ru ? `Курс #${cid}` : `Kurs #${cid}`) : (ru ? 'Старые уроки' : 'Eski darslar')),
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
                    title: w.lesson_title || (ru ? `Урок ${w.lesson_id}` : `${w.lesson_id}-dars`),
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
            <p>{ru ? 'Загрузка...' : 'Yuklanmoqda...'}</p>
        </div>
    );

    return (
        <div className="dx-dark">
            <AppHeader />

            {/* Toast */}
            {toast && (
                <div className={`d-toast ${toast.type === 'warn' ? 'warn' : ''}`}>
                    <span className="d-toast-dot" />
                    {toast.msg}
                </div>
            )}

            {/* ✅ Add-word Modal */}
            {showModal && (
                <div className="d-modal-overlay" onClick={closeModal}>
                    <div className="d-modal" onClick={e => e.stopPropagation()}>
                        <div className="d-modal-header">
                            <span className="d-modal-icon">✏️</span>
                            <div>
                                <div className="d-modal-title">{ru ? 'Добавить слово' : "So'z qo'shish"}</div>
                                <div className="d-modal-sub">{ru ? 'Добавьте новое слово в свой словарь' : "Lug'atingizga yangi so'z qo'shing"}</div>
                            </div>
                            <button className="d-modal-close" onClick={closeModal}>✕</button>
                        </div>
                        <div className="d-modal-body">
                            <div className="d-field">
                                <label className="d-label">{ru ? 'Слово' : "So'z"} <span className="d-required">*</span></label>
                                <input
                                    className={`d-input ${formError && !form.word.trim() ? 'error' : ''}`}
                                    placeholder={ru ? 'Например: flexbox, margin, gap...' : 'Masalan: flexbox, margin, gap...'}
                                    value={form.word}
                                    onChange={e => { setForm(f => ({ ...f, word: e.target.value })); setFormError(''); }}
                                    onKeyDown={e => e.key === 'Enter' && handleAddWord()}
                                    autoFocus
                                />
                            </div>
                            <div className="d-field">
                                <label className="d-label">{ru ? 'Пояснение' : 'Izoh'} <span className="d-optional">{ru ? 'необязательно' : 'ixtiyoriy'}</span></label>
                                <textarea
                                    className="d-textarea"
                                    placeholder={ru ? 'Значение этого слова или пример...' : "Bu so'zning ma'nosi yoki misol..."}
                                    value={form.context}
                                    onChange={e => setForm(f => ({ ...f, context: e.target.value }))}
                                    rows={3}
                                />
                            </div>
                            {formError && <div className="d-form-error">⚠️ {formError}</div>}
                        </div>
                        <div className="d-modal-footer">
                            <button className="d-btn-cancel" onClick={closeModal}>{ru ? 'Отмена' : 'Bekor qilish'}</button>
                            <button className="d-btn-add" onClick={handleAddWord} disabled={adding}>
                                {adding ? <><span className="d-spin-white" /> {ru ? 'Добавление...' : "Qo'shilmoqda..."}</> : <><span>+</span> {ru ? 'Добавить' : "Qo'shish"}</>}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {tab === 'practice' ? (
                <div className="dx-shell">
                    <button className="dx-back" onClick={() => setTab('words')}><ChevronLeft size={17} /> {ru ? 'Словарь' : "Lug'at"}</button>
                    <Practice />
                </div>
            ) : (
                <div className="dx-layout">
                    {/* ── left filter sidebar ── */}
                    <aside className="dx-aside">
                        <div className="dx-aside-head">
                            <span className="dx-aside-ic"><BookOpen size={20} /></span>
                            <div>
                                <div className="dx-aside-title">{ru ? 'Словарь' : "Lug'at"}</div>
                                <div className="dx-aside-sub">{ru ? 'Добавляйте слова с урока' : "Darsdan so'z qo'shing"}</div>
                            </div>
                        </div>
                        <div className="dx-aside-stats">
                            <div className="dx-ast"><span className="dx-ast-n">{words.length}</span><span className="dx-ast-k">{ru ? 'слов' : "so'z"}</span></div>
                            <div className="dx-ast-div" />
                            <div className="dx-ast"><span className="dx-ast-n">{lessons.length}</span><span className="dx-ast-k">{ru ? 'урок' : 'dars'}</span></div>
                            <div className="dx-ast-div" />
                            <div className="dx-ast"><span className="dx-ast-n">{filtered.length}</span><span className="dx-ast-k">{ru ? 'результат' : 'natija'}</span></div>
                        </div>
                        {(scopeTree.courses.length > 0 || scopeTree.manual > 0) && (
                            <nav className="dx-tree">
                                <div className="dx-tree-label">{ru ? 'Курсы и уроки' : 'Kurslar va darslar'}</div>
                                <button className={`dx-tree-item ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>
                                    <span className="dx-tree-dot" /><span className="dx-tree-name">{ru ? 'Все' : 'Hammasi'}</span><span className="dx-tree-n">{words.length}</span>
                                </button>
                                {scopeTree.manual > 0 && (
                                    <button className={`dx-tree-item ${filter === 'manual' ? 'active' : ''}`} onClick={() => setFilter('manual')}>
                                        <span className="dx-tree-dot" /><span className="dx-tree-name">{ru ? 'Добавлено вручную' : "Qo'lda qo'shilgan"}</span><span className="dx-tree-n">{scopeTree.manual}</span>
                                    </button>
                                )}
                                {scopeTree.courses.map((c) => (
                                    <div key={c.id} className="dx-tree-group">
                                        <button className={`dx-tree-item dx-tree-course ${filter === `c:${c.id}` ? 'active' : ''}`}
                                            onClick={() => setFilter(`c:${c.id}`)} title={c.title}>
                                            <span className="dx-tree-dot" /><span className="dx-tree-name">{c.title}</span><span className="dx-tree-n">{c.total}</span>
                                        </button>
                                        {c.lessons.map((l) => (
                                            <button key={l.id} className={`dx-tree-item dx-tree-lesson ${filter === `l:${l.id}` ? 'active' : ''}`}
                                                onClick={() => setFilter(`l:${l.id}`)} title={l.title}>
                                                <span className="dx-tree-dot" /><span className="dx-tree-name">{l.title}</span><span className="dx-tree-n">{l.count}</span>
                                            </button>
                                        ))}
                                    </div>
                                ))}
                            </nav>
                        )}
                        <div className="dx-aside-tip">
                            <span className="dx-tip-ic">💡</span>
                            <p>{ru ? <>Во время урока выделите текст и нажмите кнопку <strong>«Добавить в словарь»</strong></> : <>Dars paytida matnni belgilab, <strong>«Lug'atga qo'shish»</strong> tugmasini bosing</>}</p>
                        </div>
                    </aside>

                    {/* ── right content ── */}
                    <div className="dx-content">
                        <div className="dx-ctabs">
                            <button className="dx-ctab active"><BookOpen size={15} /> {ru ? 'Слова' : "So'zlar"}</button>
                            <button className="dx-ctab" onClick={() => setTab('practice')}><Target size={15} /> {ru ? 'Практика' : 'Mashq'}</button>
                        </div>

                        <div className="dx-content-tools">
                            <div className="dx-search dx-search--full">
                                <Search size={16} className="dx-search-ic" />
                                <input placeholder={ru ? 'Поиск слова...' : "So'z qidirish..."} value={search} onChange={e => setSearch(e.target.value)} />
                                {search && <button className="dx-search-clear" onClick={() => setSearch('')}><X size={14} /></button>}
                            </div>
                            <button className="dx-add" onClick={() => setShowModal(true)}><Plus size={16} /> {ru ? 'Слово' : "So'z"}</button>
                            <div className="dx-viewtoggle">
                                <button className={`dx-vbtn ${view === 'grid' ? 'active' : ''}`} onClick={() => setView('grid')} title={ru ? 'Плитки' : 'Katak'} aria-label="Grid"><LayoutGrid size={16} /></button>
                                <button className={`dx-vbtn ${view === 'list' ? 'active' : ''}`} onClick={() => setView('list')} title={ru ? 'Список' : "Ro'yxat"} aria-label="List"><List size={16} /></button>
                            </div>
                        </div>

                        {error && <div className="d-error">{error}<button onClick={() => setError('')}>✕</button></div>}

                        {filtered.length === 0 ? (
                            <div className="dx-empty">
                                <div className="dx-empty-ic">{search ? '🔎' : words.length === 0 ? '📭' : '🗂️'}</div>
                                <h3>{search ? (ru ? `«${search}» не найдено` : `«${search}» topilmadi`) : words.length === 0 ? (ru ? 'Словарь пока пуст' : "Lug'at hali bo'sh") : (ru ? 'В этом разделе нет слов' : "Bu bo'limda so'z yo'q")}</h3>
                                {words.length === 0 && !search && <button className="dx-add" onClick={() => setShowModal(true)}><Plus size={16} /> {ru ? 'Добавить слово' : "So'z qo'shish"}</button>}
                                {search && <button className="dx-chip-btn" onClick={() => setSearch('')}>{ru ? 'Очистить' : 'Tozalash'}</button>}
                                {!search && filter !== 'all' && <button className="dx-chip-btn" onClick={() => setFilter('all')}>{ru ? 'Показать все' : "Barchasini ko'rish"}</button>}
                            </div>
                        ) : view === 'list' ? (
                            <div className="dx-list">
                                {filtered.map((item, i) => {
                                    const exp = expandedId === item.id;
                                    return (
                                        <div className={`dx-lrow ${exp ? 'expanded' : ''}`} key={item.id}
                                            onClick={() => setExpandedId(exp ? null : item.id)}>
                                            <span className="dx-lrow-num">{i + 1}</span>
                                            <code className="dx-lrow-word">{item.word}</code>
                                            {item.context && <span className="dx-lrow-ctx">{item.context}</span>}
                                            <div className="dx-lrow-end">
                                                {item.lesson_id
                                                    ? <span className="dx-wtag">{ru ? `Урок ${item.lesson_id}` : `${item.lesson_id}-dars`}</span>
                                                    : <span className="dx-wtag dx-wtag--manual">{ru ? '✍️ вручную' : "✍️ qo'lda"}</span>}
                                                <button className="dx-card-del" onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }}
                                                    disabled={deleting === item.id} title={ru ? 'Удалить' : "O'chirish"} aria-label={ru ? 'Удалить' : "O'chirish"}>
                                                    {deleting === item.id ? <span className="dx-spin" /> : <Trash2 size={15} />}
                                                </button>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="dx-grid">
                                {filtered.map((item, i) => {
                                    const exp = expandedId === item.id;
                                    const longCtx = (item.context || '').length > 90;
                                    return (
                                        <div className={`dx-card ${exp ? 'expanded' : ''}`} key={item.id} style={{ '--delay': `${Math.min(i * 0.035, 0.4)}s` }}
                                            onClick={() => longCtx && setExpandedId(exp ? null : item.id)}>
                                            <div className="dx-card-code"><code>{item.word}</code></div>
                                            {item.context && <p className="dx-card-desc">{item.context}</p>}
                                            {longCtx && <span className="dx-card-more">{exp ? (ru ? '▲ меньше' : '▲ kamroq') : (ru ? '▾ больше' : '▾ ko\'proq')}</span>}
                                            <div className="dx-card-foot">
                                                <div className="dx-card-tags">
                                                    {item.lesson_id
                                                        ? <span className="dx-wtag">{ru ? `Урок ${item.lesson_id}` : `${item.lesson_id}-dars`}</span>
                                                        : <span className="dx-wtag dx-wtag--manual">{ru ? '✍️ вручную' : "✍️ qo'lda"}</span>}
                                                    {item.course_title && <span className="dx-wtag dx-wtag--course">{item.course_title}</span>}
                                                </div>
                                                <button className="dx-card-del" onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }}
                                                    disabled={deleting === item.id} title={ru ? 'Удалить' : "O'chirish"} aria-label={ru ? 'Удалить' : "O'chirish"}>
                                                    {deleting === item.id ? <span className="dx-spin" /> : <Trash2 size={15} />}
                                                </button>
                                            </div>
                                            <div className="dx-card-glow" />
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
