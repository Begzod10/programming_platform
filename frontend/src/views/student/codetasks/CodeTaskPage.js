import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './CodeTasks.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import AppHeader from '../../../components/appheader/AppHeader';
import LazyCodeEditor from '../../../components/CodeEditor/LazyCodeEditor';

const AUTOSAVE_MS = 10000;
const TXT = {
    uz: {
        back: 'Orqaga', deadline: 'Muddat', submit: 'Topshirish', confirm: "Topshirilgandan keyin o'zgartirib bo'lmaydi. Topshiraymi?",
        yes: 'Ha, topshirish', no: "Yo'q", saving: 'Saqlanmoqda…', saved: (time) => `Saqlandi · ${time}`,
        saveErr: "Saqlab bo'lmadi (tarmoq xatosi).", retry: 'Qayta urinish',
        waiting: "Tekshirishni kutmoqda — o'qituvchi ko'rib chiqadi.", returned: "Qayta yozing. O'qituvchi izohi:",
        graded: (p, m) => `Baho: ${p}/${m}`, stateChanged: "Vazifa holati o'zgargan, sahifa yangilandi.",
        emptyCode: "Kod bo'sh bo'lmasligi kerak.", loadErr: "Vazifani yuklab bo'lmadi.", submitErr: "Topshirib bo'lmadi, qayta urinib ko'ring.",
    },
    ru: {
        back: 'Назад', deadline: 'Срок', submit: 'Сдать', confirm: 'После сдачи изменить нельзя. Сдать?',
        yes: 'Да, сдать', no: 'Нет', saving: 'Сохранение…', saved: (time) => `Сохранено · ${time}`,
        saveErr: 'Не удалось сохранить (ошибка сети).', retry: 'Повторить',
        waiting: 'Ждёт проверки — учитель посмотрит.', returned: 'Перепишите. Комментарий учителя:',
        graded: (p, m) => `Оценка: ${p}/${m}`, stateChanged: 'Статус задания изменился, страница обновлена.',
        emptyCode: 'Код не должен быть пустым.', loadErr: 'Не удалось загрузить задание.', submitErr: 'Не удалось сдать, попробуйте ещё раз.',
    },
};
const LANGUAGE_NAME = { python: 'Python', javascript: 'JavaScript', html: 'HTML', css: 'CSS', sql: 'SQL', json: 'JSON', text: 'Text' };
const clock = (d) => d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });

/** One coding task: the statement and a code editor. Drafts autosave; submitting asks first and sends how the code was
 *  written (typed vs pasted, active time) for the teacher only — nothing about it is shown here. */
export default function CodeTaskPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { request } = useHttp();
    const { lang } = useTranslation();
    const t = TXT[lang === 'uz' ? 'uz' : 'ru'];
    const base = `${API_URL}v1/code-tasks/${id}`;

    const [task, setTask] = useState(null);
    const [loadErr, setLoadErr] = useState(false);
    const [code, setCode] = useState('');
    const [savedCode, setSavedCode] = useState('');
    const [saveState, setSaveState] = useState('idle');           // idle | saving | saved | error
    const [savedAt, setSavedAt] = useState(null);
    const [confirming, setConfirming] = useState(false);
    const [busy, setBusy] = useState(false);
    const [notice, setNotice] = useState(null);

    const codeRef = useRef('');
    const telemetry = useRef({ typed: 0, pasted: 0, pasteEvents: 0, startedAt: null, active: 0 });

    const load = useCallback(() => (
        request(base, 'GET', null, headers())
            .then((x) => { setTask(x); setCode(x.code); codeRef.current = x.code; setSavedCode(x.code); setLoadErr(false); })
            .catch(() => setLoadErr(true))
    ), [request, base]);
    useEffect(() => { load(); }, [load]);

    const writable = Boolean(task && (task.status === 'assigned' || task.status === 'returned'));
    const dirty = writable && code !== savedCode;

    const change = (value) => { setCode(value); codeRef.current = value; };

    const save = useCallback(async () => {
        const sending = codeRef.current;
        setSaveState('saving');
        try {
            await request(`${base}/draft`, 'PUT', JSON.stringify({ code: sending }), headers());
            setSavedCode(sending); setSavedAt(new Date()); setSaveState('saved');
        } catch (e) {
            setSaveState('error');
        }
    }, [request, base]);

    // 10 seconds after the last change
    useEffect(() => {
        if (!dirty) return undefined;
        const timer = setTimeout(save, AUTOSAVE_MS);
        return () => clearTimeout(timer);
    }, [code, dirty, save]);

    useEffect(() => {
        if (!dirty) return undefined;
        const warn = (e) => { e.preventDefault(); e.returnValue = ''; };
        window.addEventListener('beforeunload', warn);
        return () => window.removeEventListener('beforeunload', warn);
    }, [dirty]);

    // time spent in the editor: only while this tab is visible
    useEffect(() => {
        if (!writable) return undefined;
        const tick = setInterval(() => { if (document.visibilityState === 'visible') telemetry.current.active += 1; }, 1000);
        return () => clearInterval(tick);
    }, [writable]);

    const onInsert = useCallback((kind, n) => {
        const m = telemetry.current;
        if (!m.startedAt) m.startedAt = new Date().toISOString();
        if (kind === 'pasted') { m.pasted += n; m.pasteEvents += 1; } else { m.typed += n; }
    }, []);

    const submit = async () => {
        setBusy(true); setNotice(null);
        const m = telemetry.current;
        try {
            const done = await request(`${base}/submit`, 'POST', JSON.stringify({
                code, active_seconds: m.active, typed_chars: m.typed, pasted_chars: m.pasted,
                paste_events: m.pasteEvents, started_at: m.startedAt,
            }), headers());
            setTask(done); setSavedCode(code); setConfirming(false);
        } catch (e) {
            setConfirming(false);
            if (e && e.status === 409) { setNotice(t.stateChanged); load(); }
            else if (e && e.status === 422) setNotice(t.emptyCode);
            else setNotice(t.submitErr);
        } finally { setBusy(false); }
    };

    if (loadErr) return <div className="ct-page"><AppHeader /><div className="ct-body ct-empty"><p>{t.loadErr}</p><button className="ct-btn" onClick={load}>{t.retry}</button></div></div>;
    if (!task) return <div className="ct-page"><AppHeader /><div className="ct-body ct-empty"><p>…</p></div></div>;

    return (
        <div className="ct-page">
            <AppHeader />
            <div className="ct-body">
                <button className="ct-link" onClick={() => navigate('/student/code-tasks')}>← {t.back}</button>
                <h1 className="ct-h1">{task.title}</h1>
                <div className="ct-meta">
                    <span className="ct-chip">{LANGUAGE_NAME[task.language] || task.language}</span>
                    {task.deadline && <span>{t.deadline}: {new Date(task.deadline).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}</span>}
                </div>
                <p className="ct-desc">{task.description}</p>

                {task.status === 'returned' && task.returned_feedback && (
                    <p className="ct-returned">{t.returned} {task.returned_feedback}</p>
                )}
                {task.status === 'submitted' && <p className="ct-info">{t.waiting}</p>}
                {task.status === 'graded' && (
                    <div className="ct-result">
                        <strong>{t.graded(task.graded_points, task.max_points)}</strong>
                        {task.teacher_feedback && <p>{task.teacher_feedback}</p>}
                    </div>
                )}

                <div onBlur={() => { if (dirty) save(); }}>
                    <LazyCodeEditor value={code} onChange={change} language={task.language} readOnly={!writable} onInsert={onInsert} />
                </div>

                {writable && (
                    <div className="ct-bar">
                        <span className="ct-saved">
                            {saveState === 'saving' && t.saving}
                            {saveState === 'saved' && !dirty && savedAt && t.saved(clock(savedAt))}
                        </span>
                        {saveState === 'error' && (
                            <span className="ct-error" role="alert">{t.saveErr}{' '}
                                <button className="ct-link" onClick={save}>{t.retry}</button></span>
                        )}
                        {!confirming ? (
                            <button className="ct-btn ct-btn--accent" disabled={busy || !code.trim()} onClick={() => setConfirming(true)}>{t.submit}</button>
                        ) : (
                            <span className="ct-confirm">
                                {t.confirm}{' '}
                                <button className="ct-btn ct-btn--accent" disabled={busy} onClick={submit}>{t.yes}</button>{' '}
                                <button className="ct-btn" disabled={busy} onClick={() => setConfirming(false)}>{t.no}</button>
                            </span>
                        )}
                    </div>
                )}
                {notice && <p className="ct-error" role="alert">{notice}</p>}
            </div>
        </div>
    );
}
