import React, { useEffect, useRef, useState } from 'react';
import { API_URL, headers } from '../../../../api/search/base';
import { useTranslation } from '../../../../i18n/useTranslation';
import './LessonVocabCard.css';

/** The definition in the reader's language: Russian when there is one, otherwise the Uzbek original. */
export function pickDefinition(word, ru) {
    const russian = (word.definition_ru || '').trim();
    return ru && russian ? russian : word.definition;
}

export default function LessonVocabCard({ courseId, lessonId, canAddAll = true }) {
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    const [words, setWords] = useState([]);
    const [known, setKnown] = useState({});   // vocab_id -> true/false
    const [added, setAdded] = useState({});   // vocab_id -> true (added to dict)
    const [loading, setLoading] = useState(true);
    // "add every word of this lesson": idle | busy | done, plus the line shown under the header
    const [allState, setAllState] = useState('idle');
    const [allNote, setAllNote] = useState(null);     // { ok, text }
    const allBusy = useRef(false);                    // a ref: a second click lands before React re-renders

    useEffect(() => {
        if (!lessonId) return;
        setLoading(true);
        fetch(`${API_URL}/courses/${courseId}/lessons/${lessonId}/vocabulary`, { headers: headers() })
            .then(r => r.ok ? r.json() : [])
            .then(data => { setWords(data); setLoading(false); })
            .catch(() => setLoading(false));
    }, [courseId, lessonId]);

    if (loading || words.length === 0) return null;

    const handleUnknown = async (vocab) => {
        if (added[vocab.id]) return;
        try {
            await fetch(
                `${API_URL}/courses/${courseId}/lessons/${lessonId}/vocabulary/${vocab.id}/add-to-dict?lang=${ru ? 'ru' : 'uz'}`,
                { method: 'POST', headers: headers() }
            );
            setAdded(prev => ({ ...prev, [vocab.id]: true }));
        } catch {}
        setKnown(prev => ({ ...prev, [vocab.id]: false }));
    };

    const handleAddAll = async () => {
        if (allBusy.current) return;
        allBusy.current = true;
        setAllState('busy');
        setAllNote(null);
        const failed = () => {
            setAllState('idle');
            setAllNote({ ok: false, text: ru ? 'Не удалось добавить, попробуйте ещё раз' : "Qo'shib bo'lmadi, qayta urinib ko'ring" });
        };
        try {
            const r = await fetch(
                `${API_URL}/courses/${courseId}/lessons/${lessonId}/vocabulary/add-all-to-dict?lang=${ru ? 'ru' : 'uz'}`,
                { method: 'POST', headers: headers() }
            );
            if (!r.ok) { failed(); return; }
            const { added = 0 } = await r.json();
            setAllState('done');
            setAllNote({
                ok: true,
                text: added > 0
                    ? (ru ? `Добавлено слов: ${added}` : `${added} ta so'z lug'atingizga qo'shildi`)
                    : (ru ? 'Все эти слова уже есть в вашем словаре' : "Bu so'zlarning hammasi lug'atingizda bor"),
            });
            // the lesson's side panel and the dictionary drawer listen for this and reload
            window.dispatchEvent(new CustomEvent('dict:word-added'));
        } catch {
            failed();
        } finally {
            allBusy.current = false;
        }
    };

    const handleKnown = (id) => {
        setKnown(prev => ({ ...prev, [id]: true }));
    };

    const doneCount = Object.keys(known).length;
    const allDone = doneCount === words.length;

    return (
        <div className={`lvc-card ${allDone ? 'lvc-card--done' : ''}`}>
            <div className="lvc-header">
                <span className="lvc-icon">📚</span>
                <div>
                    <div className="lvc-title">{ru ? 'Подготовка — Основные термины' : 'Tayyorgarlik — Asosiy atamalar'}</div>
                    <div className="lvc-subtitle">{doneCount}/{words.length} {ru ? 'проверено' : 'tekshirildi'}</div>
                </div>
                {allDone && <span className="lvc-badge-done">{ru ? '✓ Готово' : '✓ Tayyor'}</span>}
                {canAddAll && (
                    <button className="lvc-btn-all" onClick={handleAddAll} disabled={allState !== 'idle'}>
                        {allState === 'done'
                            ? (ru ? '✓ Добавлено' : "✓ Qo'shildi")
                            : allState === 'busy'
                                ? (ru ? 'Добавляем…' : "Qo'shilmoqda…")
                                : (ru ? '📚 Добавить все в словарь' : "📚 Hammasini lug'atimga qo'shish")}
                    </button>
                )}
            </div>
            {allNote && (
                <div className={`lvc-all-note ${allNote.ok ? 'lvc-all-note--ok' : 'lvc-all-note--bad'}`} role="status">
                    {allNote.text}
                </div>
            )}

            <div className="lvc-progress">
                <div className="lvc-progress-bar" style={{ width: `${(doneCount / words.length) * 100}%` }} />
            </div>

            <div className="lvc-list">
                {words.map(w => {
                    const status = known[w.id];
                    return (
                        <div key={w.id} className={`lvc-item ${status === true ? 'lvc-item--known' : status === false ? 'lvc-item--unknown' : ''}`}>
                            <div className="lvc-word-row">
                                <span className="lvc-word">{w.word}</span>
                                {status === undefined && (
                                    <div className="lvc-actions">
                                        <button className="lvc-btn lvc-btn--know" onClick={() => handleKnown(w.id)}>
                                            {ru ? '✓ Знаю' : '✓ Bilaman'}
                                        </button>
                                        <button className="lvc-btn lvc-btn--unknown" onClick={() => handleUnknown(w)}>
                                            {ru ? '+ В словарь' : "+ Lug'atga qo'sh"}
                                        </button>
                                    </div>
                                )}
                                {status === true && <span className="lvc-status-icon">✓</span>}
                                {status === false && (
                                    <span className="lvc-status-icon lvc-status-icon--added">
                                        {added[w.id] ? (ru ? '📖 Добавлено в словарь' : '📖 Lug\'atga qo\'shildi') : '✗'}
                                    </span>
                                )}
                            </div>
                            <div className="lvc-definition">{pickDefinition(w, ru)}</div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
