import React, { useEffect, useState } from 'react';
import { API_URL, headers } from '../../../../api/search/base';
import './LessonVocabCard.css';

export default function LessonVocabCard({ courseId, lessonId }) {
    const [words, setWords] = useState([]);
    const [known, setKnown] = useState({});   // vocab_id -> true/false
    const [added, setAdded] = useState({});   // vocab_id -> true (added to dict)
    const [loading, setLoading] = useState(true);

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
                `${API_URL}/courses/${courseId}/lessons/${lessonId}/vocabulary/${vocab.id}/add-to-dict`,
                { method: 'POST', headers: headers() }
            );
            setAdded(prev => ({ ...prev, [vocab.id]: true }));
        } catch {}
        setKnown(prev => ({ ...prev, [vocab.id]: false }));
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
                    <div className="lvc-title">Tayyorgarlik — Asosiy atamalar</div>
                    <div className="lvc-subtitle">{doneCount}/{words.length} tekshirildi</div>
                </div>
                {allDone && <span className="lvc-badge-done">✓ Tayyor</span>}
            </div>

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
                                            ✓ Bilaman
                                        </button>
                                        <button className="lvc-btn lvc-btn--unknown" onClick={() => handleUnknown(w)}>
                                            + Lug'atga qo'sh
                                        </button>
                                    </div>
                                )}
                                {status === true && <span className="lvc-status-icon">✓</span>}
                                {status === false && (
                                    <span className="lvc-status-icon lvc-status-icon--added">
                                        {added[w.id] ? '📖 Lug\'atga qo\'shildi' : '✗'}
                                    </span>
                                )}
                            </div>
                            <div className="lvc-definition">{w.definition}</div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
