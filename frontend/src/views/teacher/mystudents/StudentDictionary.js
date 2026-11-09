import React, { useEffect, useMemo, useRef, useState, useCallback } from 'react';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import './StudentDictionary.css';

/** A word the student keeps getting wrong is the one to ask first. */
export const hardness = (w) => (w.incorrect_count || 0) - (w.correct_count || 0);
export const isHard = (w) => hardness(w) > 0;

/** 'known' | 'unknown' | 'unchecked' — the teacher's latest oral verdict on a word. */
export const checkState = (w) => (w.last_check_knows === true ? 'known' : w.last_check_knows === false ? 'unknown' : 'unchecked');

/** Students sometimes save pieces of code from a lesson (README, contract_test.py, /api/admin/users, user_id, foo()) —
 *  not words a teacher can ask. A heuristic, only used to hide them from the list and the random card. */
export const looksLikeCode = (word) => {
    const w = (word || '').trim();
    if (!w) return false;
    return /[/\\_(){}<>=[\];:$@#`|*]/.test(w)           // path, snake_case, call, tag, operator characters
        || /\.[a-z]/i.test(w)                             // file extension / dotted name: app.py, os.path
        || /^[a-z]+[A-Z]/.test(w)                         // camelCase identifier
        || (/\d/.test(w) && /[a-z]/i.test(w));            // letters and digits mixed: utf8, h2
};

export const PAGE_SIZES = [20, 50, 100];

/** Slice bounds for page `page` (1-based) of `total` items; the page is clamped into range, so a list that shrank
 *  (a filter, a verdict that moves a word out of the current status) never leaves the teacher on an empty page. */
export const paginate = (total, page, size) => {
    const pages = Math.max(1, Math.ceil(total / size));
    const p = Math.min(Math.max(1, page || 1), pages);
    return { page: p, pages, from: (p - 1) * size, to: Math.min(total, p * size) };
};

/** Page numbers to show: the first, the last and the current page with its neighbours; `null` marks a gap (…). */
export const pageWindow = (page, pages) => {
    const keep = [...new Set([1, page - 1, page, page + 1, pages])].filter((n) => n >= 1 && n <= pages).sort((a, b) => a - b);
    const out = [];
    keep.forEach((n, i) => {
        const prev = keep[i - 1];
        if (prev && n - prev === 2) out.push(prev + 1);        // a gap of one page is shown, not hidden behind …
        else if (prev && n - prev > 2) out.push(null);
        out.push(n);
    });
    return out;
};

const STATE_LABEL = { known: 'biladi', unknown: 'bilmaydi', unchecked: "so'ralmagan" };

/** The student's saved words (lug'at): the teacher asks them out loud and records whether the student knows them. */
export default function StudentDictionary({ studentId }) {
    const { request } = useHttp();
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [query, setQuery] = useState('');
    const [course, setCourse] = useState('');
    const [lang, setLang] = useState('');
    const [hardFirst, setHardFirst] = useState(false);
    const [state, setState] = useState('');            // '' | known | unknown | unchecked
    const [hideCode, setHideCode] = useState(true);
    const [saving, setSaving] = useState(false);
    const [saveError, setSaveError] = useState(null);
    const [pickNote, setPickNote] = useState('');
    const lastVerdict = useRef(true);
    const [picked, setPicked] = useState(null);
    const [showContext, setShowContext] = useState(false);
    const [page, setPage] = useState(1);
    const [size, setSize] = useState(PAGE_SIZES[0]);
    const listRef = useRef(null);

    const load = useCallback(() => {
        setError(null);
        request(`${API_URL}v1/teacher/students/${studentId}/dictionary`, 'GET', null, headers())
            .then(setData)
            .catch(() => setError("Lug'atni yuklab bo'lmadi. Keyinroq urinib ko'ring."));
    }, [studentId, request]);
    useEffect(() => { load(); }, [load]);

    const words = useMemo(() => data?.words || [], [data]);
    const courses = useMemo(() => {
        const seen = new Map();
        words.forEach((w) => { if (w.course_id && !seen.has(w.course_id)) seen.set(w.course_id, w.course_title); });
        return [...seen.entries()];
    }, [words]);

    const shown = useMemo(() => {
        const q = query.trim().toLowerCase();
        let list = words.filter((w) => (
            (!q || w.word.toLowerCase().includes(q))
            && (!course || String(w.course_id) === course)
            && (!lang || w.lang === lang)
            && (!state || checkState(w) === state)
            && (!hideCode || !looksLikeCode(w.word))
        ));
        if (hardFirst) list = [...list].sort((a, b) => hardness(b) - hardness(a));
        return list;
    }, [words, query, course, lang, hardFirst, state, hideCode]);

    // A new search or filter starts again from the first page.
    useEffect(() => { setPage(1); }, [query, course, lang, hardFirst, state, hideCode, size]);
    const pg = paginate(shown.length, page, size);
    const pageWords = shown.slice(pg.from, pg.to);
    const goTo = (n) => {
        setPage(n);
        if (listRef.current && listRef.current.scrollIntoView) listRef.current.scrollIntoView({ block: 'start', behavior: 'smooth' });
    };

    const codeCount = useMemo(() => words.filter((w) => looksLikeCode(w.word)).length, [words]);

    // The chips count what the list can show: hidden code fragments are left out, so a chip's number matches
    // the words you get when you press it.
    const tally = useMemo(() => {
        const t = { all: 0, known: 0, unknown: 0, unchecked: 0 };
        words.forEach((w) => {
            if (hideCode && looksLikeCode(w.word)) return;
            t.all += 1;
            t[checkState(w)] += 1;
        });
        return t;
    }, [words, hideCode]);

    // The random card is for words not asked yet. Asked words come back only when the teacher picks a status
    // ("Bilmaydiganlar" to ask the ones the student did not know again, say).
    const askable = useMemo(
        () => (state ? shown : shown.filter((w) => checkState(w) === 'unchecked')),
        [shown, state],
    );
    const nothingToAsk = state
        ? "Bu holatda so'z yo'q."
        : "Hamma so'zlar so'ralgan 🎉 Qayta so'rash uchun yuqoridan «Bilmaydiganlar» holatini tanlang.";

    const pickFrom = (list, current) => {
        if (list.length === 0) { setPicked(null); setPickNote(nothingToAsk); return; }
        const pool = list.length > 1 ? list.filter((w) => !current || w.id !== current.id) : list;
        setPickNote('');
        setPicked(pool[Math.floor(Math.random() * pool.length)]);
        setShowContext(false);
    };
    const pickRandom = () => pickFrom(askable, picked);

    /** Save the teacher's verdict for a word, update it in place; from the random card, move on to the next word. */
    const record = async (word, knows, { next = false } = {}) => {
        lastVerdict.current = knows;
        setSaving(true);
        setSaveError(null);
        try {
            const updated = await request(
                `${API_URL}v1/teacher/students/${studentId}/dictionary/${word.id}/check`,
                'POST', JSON.stringify({ knows }), headers(),
            );
            setData((d) => ({ ...d, words: d.words.map((w) => (w.id === updated.id ? updated : w)) }));
            if (next) {
                const rest = askable.filter((w) => w.id !== word.id && (!state || state === checkState(updated)));
                pickFrom(rest, word);
            } else if (picked && picked.id === updated.id) {
                setPicked(updated);
            }
        } catch (e) {
            // say WHY (an HTTP status, or no answer at all = network / proxy) so a failure can be told apart next time
            const why = e?.status ? `server javobi ${e.status}` : "serverga yetib bo'lmadi (tarmoq xatosi)";
            setSaveError(`Natijani saqlab bo'lmadi (${why}). Qayta urinib ko'ring.`);
        } finally {
            setSaving(false);
        }
    };

    if (error) return (
        <div className="sdict-empty"><p>{error}</p><button className="sdict-btn" onClick={load}>Qayta urinish</button></div>
    );
    if (!data) return <div className="sdict-empty"><p>Yuklanmoqda…</p></div>;
    if (words.length === 0) return (
        <div className="sdict-empty"><span>📖</span><p>Bu o'quvchi hali lug'atga so'z qo'shmagan</p></div>
    );

    return (
        <div className="sdict">
            <div className="sdict-bar">
                <input className="sdict-input sdict-input--grow" placeholder="So'z qidirish…" value={query}
                       onChange={(e) => setQuery(e.target.value)} aria-label="So'z qidirish" />
                {courses.length > 1 && (
                    <select className="sdict-input" value={course} onChange={(e) => setCourse(e.target.value)} aria-label="Kurs">
                        <option value="">Hamma kurslar</option>
                        {courses.map(([id, title]) => <option key={id} value={String(id)}>{title}</option>)}
                    </select>
                )}
                <select className="sdict-input" value={lang} onChange={(e) => setLang(e.target.value)} aria-label="Til">
                    <option value="">UZ + RU</option>
                    <option value="uz">UZ</option>
                    <option value="ru">RU</option>
                </select>
                <button className="sdict-btn sdict-btn--accent" onClick={pickRandom} disabled={words.length === 0}>
                    🎲 Tasodifiy so'z
                </button>
            </div>
            <div className="sdict-bar sdict-bar--opts">
                <label className="sdict-check">
                    <input type="checkbox" checked={hardFirst} onChange={(e) => setHardFirst(e.target.checked)} />
                    Qiyinlari birinchi
                </label>
                {codeCount > 0 && (
                    <label className="sdict-check">
                        <input type="checkbox" checked={hideCode} onChange={(e) => setHideCode(e.target.checked)} />
                        Kod bo'laklarini yashirish ({codeCount})
                    </label>
                )}
                {codeCount > 0 && hideCode && <span className="sdict-hint">{codeCount} ta kod bo'lagi yashirilgan</span>}
            </div>

            {!picked && pickNote && <div className="sdict-picked sdict-picked--note" role="status">{pickNote}</div>}
            {picked && (
                <div className="sdict-picked" role="status">
                    <div className="sdict-picked-word">{picked.word}</div>
                    {picked.context && (
                        showContext
                            ? <p className="sdict-picked-ctx">{picked.context}</p>
                            : <button className="sdict-link" onClick={() => setShowContext(true)}>Kontekstni ko'rsatish</button>
                    )}
                    <div className="sdict-verdict">
                        <button className="sdict-btn sdict-btn--yes" disabled={saving} onClick={() => record(picked, true, { next: true })}>
                            ✓ Biladi
                        </button>
                        <button className="sdict-btn sdict-btn--no" disabled={saving} onClick={() => record(picked, false, { next: true })}>
                            ✗ Bilmaydi
                        </button>
                    </div>
                </div>
            )}
            {saveError && (
                <p className="sdict-error" role="alert">
                    {saveError}
                    {picked && <> <button className="sdict-link" onClick={() => record(picked, lastVerdict.current, { next: true })}>Qayta urinish</button></>}
                </p>
            )}

            <div className="sdict-tally" role="group" aria-label="Holat bo'yicha">
                {[['', 'Hammasi', tally.all, ''], ['known', 'Biladi', tally.known, 'yes'],
                  ['unknown', 'Bilmaydi', tally.unknown, 'no'], ['unchecked', "So'ralmagan", tally.unchecked, '']].map(([key, label, n, tone]) => (
                    <React.Fragment key={key || 'all'}>
                        <button type="button" aria-pressed={state === key}
                                className={`sdict-chip${tone ? ` sdict-chip--${tone}` : ''}${state === key ? ' is-on' : ''}`}
                                onClick={() => setState(key && state === key ? '' : key)}>
                            {label} {n}
                        </button>{' '}
                    </React.Fragment>
                ))}
            </div>
            <p className="sdict-count">{shown.length} / {data.total} so'z</p>
            {shown.length === 0 ? (
                <div className="sdict-empty"><p>Hech narsa topilmadi</p></div>
            ) : (
                <ul className="sdict-list" ref={listRef}>
                    {pageWords.map((w) => (
                        <li key={w.id} className={`sdict-item${isHard(w) ? ' sdict-item--hard' : ''}`}>
                            <div className="sdict-item-body">
                                <div className="sdict-item-main">
                                    <span className="sdict-word">{w.word}</span>
                                    <span className="sdict-lang">{(w.lang || 'uz').toUpperCase()}</span>
                                    {isHard(w) && <span className="sdict-hard">qiyin</span>}
                                </div>
                                {(w.lesson_title || w.course_title) && (
                                    <div className="sdict-meta" title={[w.course_title, w.lesson_title].filter(Boolean).join(' · ')}>{[w.course_title, w.lesson_title].filter(Boolean).join(' · ')}</div>
                                )}
                                <div className="sdict-stats">
                                    takror: {w.review_count} · ✓ {w.correct_count} · ✗ {w.incorrect_count}
                                </div>
                            </div>
                            <div className="sdict-check-row">
                                <span className={`sdict-state sdict-state--${checkState(w)}`}>
                                    {STATE_LABEL[checkState(w)]}
                                    {w.last_checked_at && ` · ${new Date(w.last_checked_at).toLocaleDateString('ru-RU')}`}
                                    {w.checks_count > 1 && ` · ${w.checks_count}x`}
                                </span>
                                <button className="sdict-mini sdict-mini--yes" disabled={saving} onClick={() => record(w, true)}
                                        aria-label={`${w.word}: biladi`}>✓</button>
                                <button className="sdict-mini sdict-mini--no" disabled={saving} onClick={() => record(w, false)}
                                        aria-label={`${w.word}: bilmaydi`}>✗</button>
                            </div>
                        </li>
                    ))}
                </ul>
            )}
            {shown.length > PAGE_SIZES[0] && (
                <div className="sdict-foot">
                    {pg.pages > 1 && (
                        <nav className="sdict-pager" aria-label="Sahifalash">
                            <button type="button" className="sdict-btn sdict-btn--sm" disabled={pg.page <= 1}
                                    onClick={() => goTo(pg.page - 1)}>‹ Oldingi</button>
                            {pageWindow(pg.page, pg.pages).map((n, i) => (n === null
                                ? <span key={`gap${i}`} className="sdict-gap" aria-hidden="true">…</span>
                                : <button key={n} type="button" aria-label={`${n}-sahifa`}
                                          aria-current={n === pg.page ? 'page' : undefined}
                                          className={`sdict-btn sdict-btn--sm sdict-page${n === pg.page ? ' is-on' : ''}`}
                                          onClick={() => goTo(n)}>{n}</button>))}
                            <button type="button" className="sdict-btn sdict-btn--sm" disabled={pg.page >= pg.pages}
                                    onClick={() => goTo(pg.page + 1)}>Keyingi ›</button>
                            <span className="sdict-range">{pg.from + 1}–{pg.to} / {shown.length} so'z</span>
                        </nav>
                    )}
                    <span className="sdict-size">
                        Sahifada
                        <select className="sdict-input sdict-input--sm" value={size} aria-label="Sahifada"
                                onChange={(e) => setSize(Number(e.target.value))}>
                            {PAGE_SIZES.map((n) => <option key={n} value={n}>{n}</option>)}
                        </select>
                    </span>
                </div>
            )}
        </div>
    );
}
