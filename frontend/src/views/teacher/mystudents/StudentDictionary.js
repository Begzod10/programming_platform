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

    const codeCount = useMemo(() => words.filter((w) => looksLikeCode(w.word)).length, [words]);

    const tally = useMemo(() => {
        const t = { known: 0, unknown: 0, unchecked: 0 };
        words.forEach((w) => { t[checkState(w)] += 1; });
        return t;
    }, [words]);

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
                <input className="sdict-input" placeholder="So'z qidirish…" value={query}
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
                <select className="sdict-input" value={state} onChange={(e) => setState(e.target.value)} aria-label="Holat">
                    <option value="">Hamma so'zlar</option>
                    <option value="unknown">Bilmaydiganlar</option>
                    <option value="unchecked">So'ralmaganlar</option>
                    <option value="known">Biladiganlar</option>
                </select>
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
                <button className="sdict-btn sdict-btn--accent" onClick={pickRandom} disabled={words.length === 0}>
                    🎲 Tasodifiy so'z
                </button>
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

            <p className="sdict-tally">
                <span className="sdict-tally-yes">Biladi {tally.known}</span> ·{' '}
                <span className="sdict-tally-no">Bilmaydi {tally.unknown}</span> ·{' '}
                <span>So'ralmagan {tally.unchecked}</span>
            </p>
            <p className="sdict-count">{shown.length} / {data.total} so'z</p>
            {shown.length === 0 ? (
                <div className="sdict-empty"><p>Hech narsa topilmadi</p></div>
            ) : (
                <ul className="sdict-list">
                    {shown.map((w) => (
                        <li key={w.id} className={`sdict-item${isHard(w) ? ' sdict-item--hard' : ''}`}>
                            <div className="sdict-item-main">
                                <span className="sdict-word">{w.word}</span>
                                <span className="sdict-lang">{(w.lang || 'uz').toUpperCase()}</span>
                                {isHard(w) && <span className="sdict-hard">qiyin</span>}
                            </div>
                            {(w.lesson_title || w.course_title) && (
                                <div className="sdict-meta">{[w.course_title, w.lesson_title].filter(Boolean).join(' · ')}</div>
                            )}
                            <div className="sdict-stats">
                                takror: {w.review_count} · ✓ {w.correct_count} · ✗ {w.incorrect_count}
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
        </div>
    );
}
