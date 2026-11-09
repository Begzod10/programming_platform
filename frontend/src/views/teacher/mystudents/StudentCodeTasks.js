import React, { useCallback, useEffect, useMemo, useState } from 'react';
import './StudentCodeTasks.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import LazyCodeEditor from '../../../components/CodeEditor/LazyCodeEditor';

const LANGUAGES = ['python', 'javascript', 'html', 'css', 'sql', 'json', 'text'];
const LANGUAGE_NAME = { python: 'Python', javascript: 'JavaScript', html: 'HTML', css: 'CSS', sql: 'SQL', json: 'JSON', text: 'Text' };

const TXT = {
    uz: {
        newTask: 'Yangi vazifa', fTitle: 'Sarlavha', fDesc: 'Shart', fLang: 'Til', fStarter: "Boshlang'ich kod",
        fMax: "Eng ko'p ball", fDeadline: 'Muddat', give: 'Vazifa berish', cancel: 'Bekor qilish',
        empty: 'Hali vazifa berilmagan', loading: 'Yuklanmoqda…', loadErr: "Vazifalarni yuklab bo'lmadi.", retry: 'Qayta urinish',
        status: { assigned: 'Berildi', submitted: 'Tekshirishni kutmoqda', returned: 'Qaytarilgan', graded: 'Baholangan' },
        late: 'Kech topshirilgan', deadline: 'Muddat',
        attempt: (n) => `${n}-urinish`,
        aiPending: 'AI xulosa tayyorlanmoqda…', aiFailed: "AI xulosa tayyor bo'lmadi — o'zingiz ko'rib baholang.",
        aiTitle: 'AI dastlabki xulosa (maslahat)', aiSuggest: (p, m) => `AI tavsiyasi: ${p} / ${m}`,
        strengths: 'Yaxshi tomonlari', issues: 'Kamchiliklar', incomplete: "Vazifa to'liq bajarilmagan ko'rinadi",
        paste: (s, m) => `${s === null ? '' : `${s}% qo'yilgan (paste), `}${m} daq.`,
        points: 'Ball', feedback: 'Izoh', grade: 'Baholash', ret: 'Qaytarish',
        needFeedback: "Qaytarish uchun izoh yozing", badPoints: (m) => `Ball 0 dan ${m} gacha bo'lishi kerak`,
        gradedAs: (p, m) => `Baho: ${p}/${m}`, stateChanged: "Vazifa holati o'zgargan, ro'yxat yangilandi.", saveErr: "Saqlab bo'lmadi, qayta urinib ko'ring.",
    },
    ru: {
        newTask: 'Новое задание', fTitle: 'Название', fDesc: 'Условие', fLang: 'Язык', fStarter: 'Стартовый код',
        fMax: 'Макс. баллов', fDeadline: 'Срок', give: 'Выдать задание', cancel: 'Отмена',
        empty: 'Заданий пока нет', loading: 'Загрузка…', loadErr: 'Не удалось загрузить задания.', retry: 'Повторить',
        status: { assigned: 'Выдано', submitted: 'Ждёт проверки', returned: 'Возвращено', graded: 'Оценено' },
        late: 'Сдано с опозданием', deadline: 'Срок',
        attempt: (n) => `Попытка ${n}`,
        aiPending: 'AI-заключение готовится…', aiFailed: 'AI-заключение не получилось — проверьте сами.',
        aiTitle: 'Предварительное AI-заключение (подсказка)', aiSuggest: (p, m) => `Совет AI: ${p} / ${m}`,
        strengths: 'Сильные стороны', issues: 'Недочёты', incomplete: 'Похоже, задание выполнено не полностью',
        paste: (s, m) => `${s === null ? '' : `${s}% вставлено, `}${m} мин.`,
        points: 'Балл', feedback: 'Комментарий', grade: 'Оценить', ret: 'Вернуть',
        needFeedback: 'Напишите комментарий, чтобы вернуть', badPoints: (m) => `Балл должен быть от 0 до ${m}`,
        gradedAs: (p, m) => `Оценка: ${p}/${m}`, stateChanged: 'Статус задания изменился, список обновлён.', saveErr: 'Не удалось сохранить, попробуйте ещё раз.',
    },
};

/** Share (0-100) of the code that was pasted rather than typed; null when nothing was recorded. A client-reported hint. */
export const pasteShare = (s) => {
    const typed = s.typed_chars || 0, pasted = s.pasted_chars || 0;
    return typed + pasted ? Math.round((100 * pasted) / (typed + pasted)) : null;
};

const whenText = (iso) => (iso ? new Date(iso).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '');

const EMPTY_FORM = { title: '', description: '', language: 'python', starter: '', maxPoints: '20', deadline: '' };

/** "Vazifalar" tab of a student's profile: give a coding task, then review what came back next to the AI summary. */
export default function StudentCodeTasks({ studentId }) {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const ru = lang !== 'uz';
    const t = TXT[ru ? 'ru' : 'uz'];

    const [tasks, setTasks] = useState(null);
    const [error, setError] = useState(null);
    const [showForm, setShowForm] = useState(false);
    const [form, setForm] = useState(EMPTY_FORM);
    const [openId, setOpenId] = useState(null);
    const [detail, setDetail] = useState(null);
    const [attempt, setAttempt] = useState(null);
    const [points, setPoints] = useState('');
    const [note, setNote] = useState('');
    const [busy, setBusy] = useState(false);
    const [notice, setNotice] = useState(null);

    const base = `${API_URL}v1/teacher/code-tasks`;
    const loadList = useCallback(() => (
        request(`${base}/student/${studentId}`, 'GET', null, headers())
            .then((rows) => { setTasks(rows); setError(null); })
            .catch(() => setError(t.loadErr))
    ), [request, base, studentId, t.loadErr]);
    useEffect(() => { loadList(); }, [loadList]);

    const loadDetail = useCallback((id) => (
        request(`${base}/${id}`, 'GET', null, headers())
            .then((d) => { setDetail(d); setAttempt(d.submissions.length - 1); })
            .catch(() => setNotice(t.loadErr))
    ), [request, base, t.loadErr]);

    const open = (id) => {
        setOpenId(id); setDetail(null); setPoints(''); setNote(''); setNotice(null);
        loadDetail(id);
    };

    const fail = (e) => {
        if (e && e.status === 409) { setNotice(t.stateChanged); loadList(); if (openId) loadDetail(openId); }
        else setNotice(t.saveErr);
    };

    const create = async () => {
        setBusy(true); setNotice(null);
        try {
            await request(`${base}/`, 'POST', JSON.stringify({
                student_id: Number(studentId), title: form.title.trim(), description: form.description.trim(),
                language: form.language, starter_code: form.starter || null, max_points: Number(form.maxPoints) || 20,
                deadline: form.deadline ? new Date(form.deadline).toISOString() : null, lang: ru ? 'ru' : 'uz',
            }), headers());
            setForm(EMPTY_FORM); setShowForm(false);
            await loadList();
        } catch (e) { fail(e); } finally { setBusy(false); }
    };

    const verdict = async (kind) => {
        setBusy(true); setNotice(null);
        try {
            if (kind === 'grade') {
                const p = Number(points);
                if (points === '' || !Number.isInteger(p) || p < 0 || p > detail.max_points) { setNotice(t.badPoints(detail.max_points)); return; }
                await request(`${base}/${openId}/grade`, 'POST', JSON.stringify({ points: p, feedback: note }), headers());
            } else {
                await request(`${base}/${openId}/return`, 'POST', JSON.stringify({ feedback: note.trim() }), headers());
            }
            await Promise.all([loadList(), loadDetail(openId)]);
        } catch (e) { fail(e); } finally { setBusy(false); }
    };

    const sel = detail && attempt !== null ? detail.submissions[attempt] : null;
    const late = useMemo(() => Boolean(sel && detail && detail.deadline && new Date(sel.submitted_at) > new Date(detail.deadline)), [sel, detail]);
    const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

    if (error) return <div className="sct-empty"><p>{error}</p><button className="sct-btn" onClick={loadList}>{t.retry}</button></div>;
    if (!tasks) return <div className="sct-empty"><p>{t.loading}</p></div>;

    return (
        <div className="sct">
            <div className="sct-head">
                <button className="sct-btn sct-btn--accent" onClick={() => setShowForm((v) => !v)}>{t.newTask}</button>
            </div>

            {showForm && (
                <div className="sct-form">
                    <label className="sct-field">{t.fTitle}
                        <input value={form.title} onChange={set('title')} maxLength={200} />
                    </label>
                    <label className="sct-field">{t.fDesc}
                        <textarea rows={4} value={form.description} onChange={set('description')} />
                    </label>
                    <div className="sct-row2">
                        <label className="sct-field">{t.fLang}
                            <select value={form.language} onChange={set('language')}>
                                {LANGUAGES.map((l) => <option key={l} value={l}>{LANGUAGE_NAME[l]}</option>)}
                            </select>
                        </label>
                        <label className="sct-field">{t.fMax}
                            <input type="number" min="1" max="100" value={form.maxPoints} onChange={set('maxPoints')} />
                        </label>
                        <label className="sct-field">{t.fDeadline}
                            <input type="datetime-local" value={form.deadline} onChange={set('deadline')} />
                        </label>
                    </div>
                    <label className="sct-field">{t.fStarter}
                        <textarea rows={4} className="sct-mono" value={form.starter} onChange={set('starter')} />
                    </label>
                    <div className="sct-actions">
                        <button className="sct-btn sct-btn--accent" disabled={busy || !form.title.trim() || !form.description.trim()} onClick={create}>{t.give}</button>
                        <button className="sct-btn" onClick={() => setShowForm(false)}>{t.cancel}</button>
                    </div>
                </div>
            )}

            {notice && <p className="sct-notice" role="alert">{notice}</p>}

            {tasks.length === 0 ? <div className="sct-empty"><span>📝</span><p>{t.empty}</p></div> : (
                <ul className="sct-list">
                    {tasks.map((task) => (
                        <li key={task.id}>
                            <button className={`sct-item${openId === task.id ? ' is-open' : ''}`} onClick={() => open(task.id)}>
                                <span className="sct-title">{task.title}</span>
                                <span className="sct-chip">{LANGUAGE_NAME[task.language] || task.language}</span>
                                <span className={`sct-status sct-status--${task.status}`}>{t.status[task.status]}</span>
                                {task.status === 'graded' && <span className="sct-pts">{task.graded_points}/{task.max_points}</span>}
                            </button>
                        </li>
                    ))}
                </ul>
            )}

            {openId && detail && (
                <div className="sct-review">
                    <h3>{detail.title}</h3>
                    <p className="sct-desc">{detail.description}</p>
                    {detail.deadline && <p className="sct-meta">{t.deadline}: {whenText(detail.deadline)}</p>}

                    {detail.submissions.length > 1 && (
                        <div className="sct-attempts">
                            {detail.submissions.map((s, i) => (
                                <button key={s.attempt_no} className={`sct-btn sct-btn--sm${attempt === i ? ' is-on' : ''}`}
                                        onClick={() => setAttempt(i)}>{t.attempt(s.attempt_no)}</button>
                            ))}
                        </div>
                    )}

                    {sel && (
                        <>
                            <div className="sct-meta">
                                {whenText(sel.submitted_at)}
                                {late && <span className="sct-late">{t.late}</span>}
                                {' · '}<span>{t.paste(pasteShare(sel), Math.max(1, Math.round((sel.active_seconds || 0) / 60)))}</span>
                            </div>
                            <LazyCodeEditor value={sel.code} language={detail.language} readOnly minHeight="160px" />
                            <div className="sct-ai">
                                <strong>{t.aiTitle}</strong>
                                {sel.ai_status === 'pending' && <p>{t.aiPending}</p>}
                                {sel.ai_status === 'failed' && <p>{t.aiFailed}</p>}
                                {sel.ai_status === 'done' && sel.ai_review && (
                                    <>
                                        <p>{sel.ai_review.summary}</p>
                                        {sel.ai_review.strengths.length > 0 && (<><em>{t.strengths}</em><ul>{sel.ai_review.strengths.map((x, i) => <li key={i}>{x}</li>)}</ul></>)}
                                        {sel.ai_review.issues.length > 0 && (<><em>{t.issues}</em><ul>{sel.ai_review.issues.map((x, i) => <li key={i}>{x}</li>)}</ul></>)}
                                        {!sel.ai_review.looks_complete && <p>{t.incomplete}</p>}
                                        <p className="sct-suggest">{t.aiSuggest(sel.ai_review.suggested_points, detail.max_points)}</p>
                                    </>
                                )}
                            </div>
                        </>
                    )}

                    {detail.status === 'submitted' && (
                        <div className="sct-verdict">
                            <label className="sct-field">{t.points}
                                <input type="number" min="0" max={detail.max_points} value={points} onChange={(e) => setPoints(e.target.value)} />
                            </label>
                            <label className="sct-field">{t.feedback}
                                <textarea rows={3} value={note} onChange={(e) => setNote(e.target.value)} />
                            </label>
                            <div className="sct-actions">
                                <button className="sct-btn sct-btn--accent" disabled={busy} onClick={() => verdict('grade')}>{t.grade}</button>
                                <button className="sct-btn" disabled={busy || !note.trim()} title={note.trim() ? undefined : t.needFeedback}
                                        onClick={() => verdict('return')}>{t.ret}</button>
                            </div>
                        </div>
                    )}
                    {detail.status === 'graded' && (
                        <p className="sct-result">{t.gradedAs(detail.graded_points, detail.max_points)}{detail.teacher_feedback ? ` — ${detail.teacher_feedback}` : ''}</p>
                    )}
                </div>
            )}
        </div>
    );
}
