import React, { useState, useEffect, useMemo, useRef } from 'react';
import './TeacherPenalties.css';
import { API_URL, useHttp, headers, resolveImageUrl } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import { PENALTY_TYPES, penaltyLabel } from '../../../constants/penaltyTypes';
import {
    Gavel, Search, AlertTriangle, Check, X, Loader2, History,
} from 'lucide-react';

const QUICK = [10, 25, 50, 100];

const initials = (name, username) =>
    (name || username || '?').trim().split(/\s+/).slice(0, 2).map(w => w[0]).join('').toUpperCase();

function timeAgo(iso, ru) {
    const d = new Date(iso);
    const min = Math.max(0, Math.floor((Date.now() - d) / 60000));
    if (min < 1) return ru ? 'только что' : 'hozirgina';
    if (min < 60) return ru ? `${min} мин назад` : `${min} daq oldin`;
    const hr = Math.floor(min / 60);
    if (hr < 24) return ru ? `${hr} ч назад` : `${hr} soat oldin`;
    const day = Math.floor(hr / 24);
    if (day < 7) return ru ? `${day} дн назад` : `${day} kun oldin`;
    return d.toLocaleDateString(ru ? 'ru-RU' : 'uz-UZ', { day: 'numeric', month: 'short' });
}

export default function TeacherPenalties() {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const ru = lang !== 'uz';   // teacher UI is Russian-first

    const [students, setStudents] = useState([]);
    const [history, setHistory] = useState([]);
    const [loadingHistory, setLoadingHistory] = useState(true);

    const [search, setSearch] = useState('');
    const [picked, setPicked] = useState(null);
    const [showList, setShowList] = useState(false);
    const [type, setType] = useState('rule_violation');
    const [amount, setAmount] = useState('');
    const [comment, setComment] = useState('');
    const [confirming, setConfirming] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [msg, setMsg] = useState(null);     // { ok, text }
    const [onlyPicked, setOnlyPicked] = useState(false);
    const boxRef = useRef(null);

    const loadStudents = () =>
        request(`${API_URL}v1/teacher/penalties/students`, 'GET', null, headers())
            .then(d => setStudents(Array.isArray(d) ? d : []))
            .catch(() => { /* picker degrades to empty */ });

    const loadHistory = (sid) => {
        setLoadingHistory(true);
        const qs = sid ? `?student_id=${sid}&limit=100` : '?limit=100';
        return request(`${API_URL}v1/teacher/penalties${qs}`, 'GET', null, headers())
            .then(d => setHistory(Array.isArray(d) ? d : []))
            .catch(() => { /* keep previous */ })
            .finally(() => setLoadingHistory(false));
    };

    useEffect(() => {
        loadStudents();
        loadHistory(null);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // History scope follows the "only this student" toggle.
    useEffect(() => {
        loadHistory(onlyPicked && picked ? picked.student_id : null);
        /* eslint-disable-next-line */
    }, [onlyPicked, picked?.student_id]);

    // Close the dropdown on outside click.
    useEffect(() => {
        const onDoc = (e) => { if (boxRef.current && !boxRef.current.contains(e.target)) setShowList(false); };
        document.addEventListener('mousedown', onDoc);
        return () => document.removeEventListener('mousedown', onDoc);
    }, []);

    const filtered = useMemo(() => {
        const q = search.trim().toLowerCase();
        const list = !q ? students
            : students.filter(s =>
                (s.full_name || '').toLowerCase().includes(q) ||
                (s.username || '').toLowerCase().includes(q));
        return list.slice(0, 40);
    }, [students, search]);

    const amt = Math.max(0, parseInt(amount, 10) || 0);
    const canSubmit = picked && amt >= 1 && !submitting;
    const after = picked ? Math.max(0, (picked.rating_points || 0) - amt) : 0;

    const pick = (s) => { setPicked(s); setShowList(false); setSearch(''); setConfirming(false); setMsg(null); };

    const apply = async () => {
        if (!canSubmit) return;
        setSubmitting(true); setMsg(null);
        try {
            const res = await request(
                `${API_URL}v1/teacher/penalties`, 'POST',
                JSON.stringify({ student_id: picked.student_id, amount: amt, penalty_type: type, comment: comment.trim() || null }),
                headers(),
            );
            const newRating = res?.rating_points ?? after;
            // refresh the picked student's balance + the list in place
            setPicked(p => p ? { ...p, rating_points: newRating } : p);
            setStudents(list => list.map(s => s.student_id === picked.student_id ? { ...s, rating_points: newRating } : s));
            if (res?.penalty) setHistory(h => [res.penalty, ...h]);
            setMsg({ ok: true, text: ru
                ? `Готово: −${amt} у «${picked.full_name || picked.username}». Осталось ${newRating}.`
                : `Bajarildi: «${picked.full_name || picked.username}» dan −${amt}. Qoldi ${newRating}.` });
            setAmount(''); setComment(''); setConfirming(false);
        } catch (e) {
            const detail = e?.response?.data?.detail || e?.response?.data?.error?.message;
            setMsg({ ok: false, text: detail || (ru ? 'Не удалось применить штраф' : 'Jarima qoʻllanmadi') });
            setConfirming(false);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="pen-page">
            <div className="pen-head">
                <span className="pen-head-ico"><Gavel size={24} /></span>
                <div>
                    <h1>{ru ? 'Штрафы' : 'Jarimalar'}</h1>
                    <p>{ru
                        ? 'Снимите баллы с рейтинга ученика как дисциплинарное взыскание. Ученик получит уведомление с причиной.'
                        : "O'quvchi reytingidan intizomiy jarima sifatida ball yeching. O'quvchiga sabab bilan bildirishnoma boradi."}</p>
                </div>
            </div>

            <div className="pen-grid">
                {/* ── Apply form ── */}
                <section className="pen-card pen-form">
                    <h2 className="pen-card-title">{ru ? 'Новый штраф' : 'Yangi jarima'}</h2>

                    {/* Student picker */}
                    <label className="pen-label">{ru ? 'Ученик' : "O'quvchi"}</label>
                    {picked ? (
                        <div className="pen-picked">
                            <span className="pen-ava">
                                {picked.avatar_url
                                    ? <img src={resolveImageUrl(picked.avatar_url)} alt="" onError={e => { e.target.style.display = 'none'; }} />
                                    : initials(picked.full_name, picked.username)}
                            </span>
                            <div className="pen-picked-info">
                                <div className="pen-picked-name">{picked.full_name || picked.username}</div>
                                <div className="pen-picked-bal">
                                    {ru ? 'Рейтинг' : 'Reyting'}: <b>{picked.rating_points}</b> {ru ? 'очков' : 'ball'}
                                </div>
                            </div>
                            <button className="pen-change" onClick={() => { setPicked(null); setShowList(true); }}>
                                {ru ? 'Сменить' : "O'zgartirish"}
                            </button>
                        </div>
                    ) : (
                        <div className="pen-picker" ref={boxRef}>
                            <span className="pen-picker-ico"><Search size={16} /></span>
                            <input
                                className="pen-input"
                                placeholder={ru ? 'Поиск ученика…' : "O'quvchini qidirish…"}
                                value={search}
                                onChange={e => { setSearch(e.target.value); setShowList(true); }}
                                onFocus={() => setShowList(true)}
                            />
                            {showList && (
                                <div className="pen-drop">
                                    {filtered.length === 0 ? (
                                        <div className="pen-drop-empty">{ru ? 'Никого не найдено' : 'Hech kim topilmadi'}</div>
                                    ) : filtered.map(s => (
                                        <button key={s.student_id} className="pen-drop-row" onClick={() => pick(s)}>
                                            <span className="pen-ava sm">
                                                {s.avatar_url
                                                    ? <img src={resolveImageUrl(s.avatar_url)} alt="" onError={e => { e.target.style.display = 'none'; }} />
                                                    : initials(s.full_name, s.username)}
                                            </span>
                                            <span className="pen-drop-name">{s.full_name || s.username}</span>
                                            <span className="pen-drop-bal">{s.rating_points}</span>
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Penalty type */}
                    <label className="pen-label">{ru ? 'Тип нарушения' : 'Buzilish turi'}</label>
                    <div className="pen-types">
                        {PENALTY_TYPES.map(t => (
                            <button
                                key={t.key}
                                className={`pen-type ${type === t.key ? 'active' : ''}`}
                                onClick={() => setType(t.key)}
                                type="button"
                            >
                                <span className="pen-type-emoji">{t.emoji}</span>
                                <span>{ru ? t.ru : t.uz}</span>
                            </button>
                        ))}
                    </div>

                    {/* Amount */}
                    <label className="pen-label">{ru ? 'Сумма штрафа (баллы)' : 'Jarima miqdori (ball)'}</label>
                    <div className="pen-amount">
                        <input
                            className="pen-input"
                            type="number" min="1" inputMode="numeric"
                            placeholder={ru ? 'например, 100' : 'masalan, 100'}
                            value={amount}
                            onChange={e => { setAmount(e.target.value); setConfirming(false); }}
                        />
                        <div className="pen-quick">
                            {QUICK.map(q => (
                                <button key={q} type="button" className="pen-quick-btn"
                                    onClick={() => { setAmount(String((parseInt(amount, 10) || 0) + q)); setConfirming(false); }}>
                                    +{q}
                                </button>
                            ))}
                            <button type="button" className="pen-quick-btn pen-quick-clear"
                                onClick={() => { setAmount(''); setConfirming(false); }}>✕</button>
                        </div>
                    </div>

                    {/* Comment */}
                    <label className="pen-label">{ru ? 'Комментарий (необязательно)' : 'Izoh (ixtiyoriy)'}</label>
                    <textarea
                        className="pen-textarea"
                        rows={2}
                        placeholder={ru ? 'За что именно…' : 'Aynan nima uchun…'}
                        value={comment}
                        onChange={e => setComment(e.target.value)}
                    />

                    {/* Confirm + submit */}
                    {msg && (
                        <div className={`pen-msg ${msg.ok ? 'ok' : 'err'}`}>
                            {msg.ok ? <Check size={16} /> : <AlertTriangle size={16} />} {msg.text}
                        </div>
                    )}

                    {confirming && canSubmit ? (
                        <div className="pen-confirm">
                            <div className="pen-confirm-txt">
                                {ru
                                    ? <>Снять <b>{amt}</b> очков у <b>{picked.full_name || picked.username}</b>? Останется <b>{after}</b>.</>
                                    : <><b>{picked.full_name || picked.username}</b> dan <b>{amt}</b> ball yechilsinmi? <b>{after}</b> qoladi.</>}
                            </div>
                            <div className="pen-confirm-actions">
                                <button className="pen-btn ghost" onClick={() => setConfirming(false)} disabled={submitting}>
                                    <X size={16} /> {ru ? 'Отмена' : 'Bekor'}
                                </button>
                                <button className="pen-btn danger" onClick={apply} disabled={submitting}>
                                    {submitting ? <Loader2 size={16} className="pen-spin" /> : <Gavel size={16} />}
                                    {ru ? 'Подтвердить' : 'Tasdiqlash'}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <button
                            className="pen-btn danger pen-submit"
                            disabled={!canSubmit}
                            onClick={() => { setMsg(null); setConfirming(true); }}
                        >
                            <Gavel size={16} /> {ru ? 'Оштрафовать' : 'Jarima berish'}
                            {canSubmit && <span className="pen-submit-amt">−{amt}</span>}
                        </button>
                    )}
                </section>

                {/* ── History ── */}
                <section className="pen-card pen-history">
                    <div className="pen-history-head">
                        <h2 className="pen-card-title"><History size={18} /> {ru ? 'История штрафов' : 'Jarimalar tarixi'}</h2>
                        {picked && (
                            <label className="pen-only">
                                <input type="checkbox" checked={onlyPicked} onChange={e => setOnlyPicked(e.target.checked)} />
                                {ru ? 'только этот ученик' : "faqat shu o'quvchi"}
                            </label>
                        )}
                    </div>

                    {loadingHistory ? (
                        <div className="pen-hist-skel">{[0, 1, 2].map(i => <div key={i} className="pen-hist-skel-row" />)}</div>
                    ) : history.length === 0 ? (
                        <div className="pen-empty">{ru ? 'Штрафов пока нет' : 'Hali jarimalar yoʻq'}</div>
                    ) : (
                        <div className="pen-hist-list">
                            {history.map(h => (
                                <div className="pen-hist-row" key={h.id}>
                                    <div className="pen-hist-main">
                                        <div className="pen-hist-top">
                                            <span className="pen-hist-name">{h.student_name || `#${h.student_id}`}</span>
                                            <span className="pen-hist-amt">−{h.amount}</span>
                                        </div>
                                        <div className="pen-hist-sub">
                                            <span className="pen-hist-reason">{penaltyLabel(h.penalty_type, ru)}</span>
                                            {h.comment && <span className="pen-hist-comment">— {h.comment}</span>}
                                        </div>
                                        <div className="pen-hist-meta">
                                            <span>{h.points_before} → {h.points_after}</span>
                                            {h.teacher_name && <span>· {h.teacher_name}</span>}
                                            <span>· {timeAgo(h.created_at, ru)}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </section>
            </div>
        </div>
    );
}
