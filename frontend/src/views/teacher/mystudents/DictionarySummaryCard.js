import React, { useEffect, useState } from 'react';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import './StudentDictionary.css';

const fmtDate = (iso) => (iso ? new Date(iso).toLocaleDateString('ru-RU') : null);

/** How well the student knows their saved words, from the teacher's oral checks (Lug'at tab) — for the profile overview.
 *  The percentage is over the words that were actually asked; the ones nobody asked yet are shown separately. */
export default function DictionarySummaryCard({ studentId, onOpen }) {
    const { request } = useHttp();
    const [summary, setSummary] = useState(null);
    const [failed, setFailed] = useState(false);

    useEffect(() => {
        let alive = true;
        setFailed(false);
        request(`${API_URL}v1/teacher/students/${studentId}/dictionary/summary`, 'GET', null, headers())
            .then((d) => alive && setSummary(d))
            .catch(() => alive && setFailed(true));
        return () => { alive = false; };
    }, [studentId, request]);

    if (failed || !summary) return null;               // the overview must not break because of this card
    const { total, known, unknown, unchecked, checked, percent_known: percent, last_checked_at: last } = summary;
    if (total === 0) return null;

    return (
        <div className="spp-section sdsum">
            <p className="spp-section-lbl">📖 Lug'at</p>
            {percent === null ? (
                <p className="sdsum-empty">
                    {total} ta so'z saqlangan, hali birortasi so'ralmagan.{' '}
                    <button className="sdict-link" onClick={onOpen}>So'rashni boshlash →</button>
                </p>
            ) : (
                <>
                    <div className="sdsum-head">
                        <span className="sdsum-percent">{percent}%</span>
                        <span className="sdsum-text">
                            {checked} ta so'raldi, {known} tasini biladi, {unknown} tasini bilmaydi
                        </span>
                    </div>
                    <div className="sdsum-bar" role="progressbar" aria-valuenow={percent} aria-valuemin={0} aria-valuemax={100}>
                        <div className="sdsum-bar-fill" style={{ width: `${percent}%` }} />
                    </div>
                    <p className="sdsum-meta">
                        So'ralmagan: {unchecked} / {total}
                        {last && ` · oxirgi tekshiruv ${fmtDate(last)}`}
                        {' · '}<button className="sdict-link" onClick={onOpen}>Lug'atni ochish →</button>
                    </p>
                </>
            )}
        </div>
    );
}
