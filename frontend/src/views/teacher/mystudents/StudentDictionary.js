import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import './StudentDictionary.css';

/** A word the student keeps getting wrong is the one to ask first. */
export const hardness = (w) => (w.incorrect_count || 0) - (w.correct_count || 0);
export const isHard = (w) => hardness(w) > 0;

/** The student's saved words (lug'at), read-only: the teacher asks them out loud. */
export default function StudentDictionary({ studentId }) {
    const { request } = useHttp();
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [query, setQuery] = useState('');
    const [course, setCourse] = useState('');
    const [lang, setLang] = useState('');
    const [hardFirst, setHardFirst] = useState(false);
    const [picked, setPicked] = useState(null);
    const [showContext, setShowContext] = useState(false);

    const load = useCallback(() => {
        setError(null);
        request(`${API_URL}v1/teacher/students/${studentId}/dictionary`, 'GET', null, headers())
            .then(setData)
            .catch(() => setError("Lug'atni yuklab bo'lmadi. Keyinroq urinib ko'ring."));
    }, [studentId, request]);
    useEffect(() => { load(); }, [load]);

    const words = data?.words || [];
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
        ));
        if (hardFirst) list = [...list].sort((a, b) => hardness(b) - hardness(a));
        return list;
    }, [words, query, course, lang, hardFirst]);

    const pickRandom = () => {
        if (shown.length === 0) return;
        const pool = shown.length > 1 ? shown.filter((w) => !picked || w.id !== picked.id) : shown;
        setPicked(pool[Math.floor(Math.random() * pool.length)]);
        setShowContext(false);
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
                <label className="sdict-check">
                    <input type="checkbox" checked={hardFirst} onChange={(e) => setHardFirst(e.target.checked)} />
                    Qiyinlari birinchi
                </label>
                <button className="sdict-btn sdict-btn--accent" onClick={pickRandom} disabled={shown.length === 0}>
                    🎲 Tasodifiy so'z
                </button>
            </div>

            {picked && (
                <div className="sdict-picked" role="status">
                    <div className="sdict-picked-word">{picked.word}</div>
                    {picked.context && (
                        showContext
                            ? <p className="sdict-picked-ctx">{picked.context}</p>
                            : <button className="sdict-link" onClick={() => setShowContext(true)}>Kontekstni ko'rsatish</button>
                    )}
                </div>
            )}

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
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
