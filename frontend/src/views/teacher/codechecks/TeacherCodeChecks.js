import { useCallback, useEffect, useState } from 'react';
import './TeacherCodeChecks.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { apiErrorMessage } from '../../../utils/apiError';

const STATUS = {
    failed:      { label: "Noto'g'ri javob", tone: 'bad' },
    suspicious:  { label: "To'g'ri, lekin boshqa oynaga o'tgan", tone: 'warn' },
    expired:     { label: 'Topshirilmadi / vaqt tugadi', tone: 'warn' },
    unavailable: { label: "Savol tuzib bo'lmadi", tone: 'warn' },
    pending:     { label: 'Kutilmoqda', tone: 'wait' },
    passed:      { label: "O'tdi", tone: 'ok' },
    reviewed:    { label: "Ko'rib chiqilgan", tone: 'ok' },
};
const REASON = { pace: 'Juda tez topshirilgan', random: 'Tasodifiy tanlov' };
const LOW = "Tez topshirilgan, lekin testdan o'tgan";

const fmtDate = (iso) => (iso ? new Date(iso).toLocaleString('uz-UZ', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—');

function Row({ c, onResolved }) {
    const { request } = useHttp();
    const [open, setOpen] = useState(false);
    const [confirm, setConfirm] = useState(null);       // 'dismiss' | 'revoke_points'
    const [note, setNote] = useState('');
    const [busy, setBusy] = useState(false);
    const [err, setErr] = useState('');
    const st = c.low_priority ? { label: LOW, tone: 'wait' } : (STATUS[c.status] || { label: c.status, tone: 'wait' });

    const resolve = async () => {
        setBusy(true); setErr('');
        try {
            const updated = await request(`${API_URL}v1/teacher/code-checks/${c.id}/resolve`, 'POST',
                JSON.stringify({ action: confirm, note: note.trim() || null }), headers());
            onResolved(updated);
        } catch (e) {
            setErr(apiErrorMessage(e) || "Saqlab bo'lmadi");
        } finally { setBusy(false); }
    };

    return (
        <article className={`tcc-card ${c.low_priority ? 'tcc-card--low' : ''}`}>
            <header className="tcc-head">
                <div>
                    <h3>{c.student.full_name || c.student.username} <small>@{c.student.username}</small></h3>
                    <p>{c.project.title} · {c.project.points_earned} ball{c.project.grade ? ` (${c.project.grade})` : ''}</p>
                </div>
                <span className={`tcc-badge tcc-${st.tone}`}>{st.label}</span>
            </header>
            <ul className="tcc-facts">
                <li><b>{REASON[c.reason] || c.reason}</b></li>
                <li>{c.code_lines} qator{c.gap_minutes != null ? `, oldingi loyihadan ${c.gap_minutes} daq. keyin` : ''}{c.pace ? ` (${c.pace} qator/daq)` : ''}</li>
                {c.correct != null && <li>To'g'ri javob: {c.correct}/{c.total}</li>}
                {c.duration_seconds != null && <li>Vaqt: {c.duration_seconds} soniya</li>}
                <li className={c.blur_count > 1 ? 'tcc-flag' : ''}>Boshqa oynaga o'tishlar: {c.blur_count}</li>
                <li>Yuborilgan: {fmtDate(c.created_at)}</li>
            </ul>

            {c.questions.length > 0 && (
                <>
                    <button className="tcc-link" onClick={() => setOpen(!open)}>{open ? 'Savollarni yashirish' : 'Savollar va javoblar (suhbat uchun)'}</button>
                    {open && c.questions.map((q, i) => (
                        <div key={i} className="tcc-q">
                            <p>{i + 1}. {q.q}</p>
                            <ol type="A">
                                {q.options.map((o, k) => (
                                    <li key={k} className={`${k === q.correct ? 'tcc-right' : ''} ${k === q.answer ? 'tcc-picked' : ''}`}>
                                        {o}{k === q.correct ? ' ✓' : ''}{k === q.answer ? ' ← javobi' : ''}
                                    </li>
                                ))}
                            </ol>
                            {q.answer == null && <em>Javob bermagan</em>}
                        </div>
                    ))}
                </>
            )}

            {err && <p className="tcc-err" role="alert">{err}</p>}
            {!confirm ? (
                <div className="tcc-actions">
                    <button className="tcc-btn" onClick={() => setConfirm('dismiss')}>Hammasi joyida</button>
                    <button className="tcc-btn tcc-danger" onClick={() => setConfirm('revoke_points')}>Ballni bekor qilish</button>
                </div>
            ) : (
                <div className="tcc-confirm">
                    <p>{confirm === 'revoke_points'
                        ? `${c.project.points_earned} ball bekor qilinadi (loyiha holati o'zgarmaydi). Tasdiqlaysizmi?`
                        : "Tekshiruv tugallandi deb belgilanadi, ball o'zgarmaydi."}</p>
                    <textarea placeholder="Izoh (ixtiyoriy): suhbat natijasi" value={note} maxLength={1000} onChange={e => setNote(e.target.value)} />
                    <div className="tcc-actions">
                        <button className="tcc-btn" disabled={busy} onClick={() => { setConfirm(null); setErr(''); }}>Bekor</button>
                        <button className={`tcc-btn ${confirm === 'revoke_points' ? 'tcc-danger' : ''}`} disabled={busy} onClick={resolve}>
                            {busy ? 'Saqlanmoqda…' : 'Tasdiqlash'}
                        </button>
                    </div>
                </div>
            )}
        </article>
    );
}

/** Quizzes on the student's own code that need a teacher: failed, not taken, unavailable, or answered right
 *  after leaving the tab. The teacher talks to the student and either clears it or revokes the project's points. */
export default function TeacherCodeChecks() {
    const { request } = useHttp();
    const [items, setItems] = useState(null);
    const [all, setAll] = useState(false);
    const [error, setError] = useState('');

    const load = useCallback(() => {
        setError('');
        request(`${API_URL}v1/teacher/code-checks?all=${all}`, 'GET', null, headers())
            .then(d => setItems(Array.isArray(d) ? d : []))
            .catch(e => { setItems([]); setError(apiErrorMessage(e) || "Yuklab bo'lmadi"); });
    }, [request, all]);

    useEffect(() => { load(); }, [load]);

    const onResolved = (u) => setItems(list => (all ? list.map(x => (x.id === u.id ? u : x)) : list.filter(x => x.id !== u.id)));

    return (
        <div className="tcc-page">
            <div className="tcc-title">
                <h1>Kod tekshiruvlari</h1>
                <label><input type="checkbox" checked={all} onChange={e => setAll(e.target.checked)} /> Hammasini ko'rsatish</label>
            </div>
            <p className="tcc-lead">Juda tez topshirilgan (yoki tasodifiy tanlangan) loyihalar uchun o'quvchi o'z kodidan 3 savollik test topshiradi.
                Quyidagilar sizning e'tiboringizni kutmoqda: avval noto'g'ri/gumonli javoblar, pastda tez topshirilgan, lekin testdan o'tganlar (yengil belgi). Test isbot emas, faqat kimni suhbatga chaqirishni ko'rsatadi.</p>
            {error && <p className="tcc-err" role="alert">{error}</p>}
            {items === null && <p>Yuklanmoqda…</p>}
            {items && items.length === 0 && !error && <p className="tcc-empty">Hozircha e'tibor talab qiladigan tekshiruv yo'q ✅</p>}
            {items && items.map(c => <Row key={c.id} c={c} onResolved={onResolved} />)}
        </div>
    );
}
