import React, { useCallback, useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import './Summative.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';

const TEXT = {
    uz: {
        title: 'Chorak yakuniy testi',
        sub: "Test siz tugatgan darslardan tuziladi. Javoblar har safar aralash joylashadi.",
        plan: (l, n, m) => `Shu chorakda ${l} ta dars tugatgansiz. Test shu darslardan tuziladi: ${n} ta savol · ${m} daqiqa.`,
        notEnough: (min) => `Test uchun kamida ${min} ta savol kerak. Ko'proq dars tugating.`,
        rules: 'Qoidalar',
        rulesList: [
            "Test boshlanganda ekran avtomatik to'liq ekran rejimiga o'tadi.",
            "To'liq ekrandan chiqish, boshqa oyna yoki sahifaga o'tish qoidabuzarlik hisoblanadi.",
            "3 ta qoidabuzarlikdan keyin test avtomatik tugaydi va shu paytgacha bergan javoblaringiz hisoblanadi.",
            "Nusxa olish, kontekst menyu va F12 o'chirilgan. Vaqt tugasa test o'zi yopiladi.",
        ],
        start: 'Testni boshlash',
        resume: 'Davom ettirish',
        starting: 'Tayyorlanmoqda…',
        history: 'Oldingi natijalar',
        back: 'Orqaga',
        noHistory: "Hali test topshirmagansiz.",
        q: (i, n) => `Savol ${i} / ${n}`,
        prev: 'Oldingi',
        next: 'Keyingi',
        finish: 'Testni yakunlash',
        finishTitle: 'Testni yakunlaysizmi?',
        cancel: 'Bekor qilish',
        finishYes: 'Ha, yakunlash',
        confirmFinish: (left) => (left > 0 ? `${left} ta savolga javob bermadingiz. Baribir yakunlaysizmi?` : "Barcha savollarga javob berdingiz. Yakunlaymizmi?"),
        left: 'Qoldi',
        warnTitle: 'Test ekranidan chiqdingiz!',
        warnText: (n, max) => `Qoidabuzarlik: ${n} / ${max}. ${max} ga yetsa test tugaydi.`,
        warnBtn: "To'liq ekranga qaytish",
        result: 'Natija',
        correct: "To'g'ri",
        yourAnswer: 'Sizning javobingiz',
        rightAnswer: "To'g'ri javob",
        noAnswer: 'Javob berilmagan',
        reasons: { submitted: '', time: "Vaqt tugadi", violations: "Qoidabuzarliklar sababli tugatildi" },
        error: "Xatolik yuz berdi. Qayta urinib ko'ring.",
        status: { in_progress: 'Tugallanmagan', finished: 'Tugagan' },
        review: "Xatolar tahlili",
        showAll: 'Hammasini ko\'rsatish',
        onlyWrong: "Faqat xatolar",
    },
    ru: {
        title: 'Итоговый тест четверти',
        sub: 'Тест составляется из пройденных вами уроков. Порядок ответов каждый раз случайный.',
        plan: (l, n, m) => `В этой четверти вы прошли уроков: ${l}. Тест составляется из них: ${n} вопросов · ${m} минут.`,
        notEnough: (min) => `Нужно минимум ${min} вопросов. Пройдите больше уроков.`,
        rules: 'Правила',
        rulesList: [
            'При старте экран автоматически переходит в полноэкранный режим.',
            'Выход из полного экрана, переход в другое окно или вкладку — нарушение.',
            'После 3 нарушений тест завершается автоматически, засчитываются ответы, данные к этому моменту.',
            'Копирование, контекстное меню и F12 отключены. По окончании времени тест закроется сам.',
        ],
        start: 'Начать тест',
        resume: 'Продолжить',
        starting: 'Подготовка…',
        history: 'Прошлые результаты',
        back: 'Назад',
        noHistory: 'Вы ещё не сдавали тест.',
        q: (i, n) => `Вопрос ${i} / ${n}`,
        prev: 'Назад',
        next: 'Далее',
        finish: 'Завершить тест',
        finishTitle: 'Завершить тест?',
        cancel: 'Отмена',
        finishYes: 'Да, завершить',
        confirmFinish: (left) => (left > 0 ? `Вы не ответили на ${left} вопр. Всё равно завершить?` : 'Вы ответили на все вопросы. Завершаем?'),
        left: 'Осталось',
        warnTitle: 'Вы покинули экран теста!',
        warnText: (n, max) => `Нарушение: ${n} / ${max}. При ${max} тест завершится.`,
        warnBtn: 'Вернуться в полный экран',
        result: 'Результат',
        correct: 'Верно',
        yourAnswer: 'Ваш ответ',
        rightAnswer: 'Верный ответ',
        noAnswer: 'Нет ответа',
        reasons: { submitted: '', time: 'Время вышло', violations: 'Завершён из-за нарушений' },
        error: 'Произошла ошибка. Попробуйте ещё раз.',
        status: { in_progress: 'Не завершён', finished: 'Завершён' },
        review: 'Разбор ошибок',
        showAll: 'Показать все',
        onlyWrong: 'Только ошибки',
    },
};

const fmtTime = (s) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
const LETTERS = ['A', 'B', 'C', 'D', 'E', 'F'];

const fsSupported = () => !!(document.documentElement.requestFullscreen && document.fullscreenEnabled);
const enterFs = () => {
    try {
        const p = document.documentElement.requestFullscreen?.({ navigationUI: 'hide' });
        if (p && p.then) {
            // Chromium: capture Esc so a quick tap no longer leaves fullscreen
            // (the browser then needs Esc held for ~2s). The little ✕ the
            // browser draws at the top is its own UI and can't be removed —
            // using it is counted as a violation like any other exit.
            p.then(() => navigator.keyboard?.lock?.(['Escape']).catch(() => {})).catch(() => {});
        }
    } catch { /* ignore */ }
};
const exitFs = () => {
    try { navigator.keyboard?.unlock?.(); } catch { /* ignore */ }
    try { if (document.fullscreenElement) document.exitFullscreen?.(); } catch { /* ignore */ }
};

/** /student/summative — lobby, the fullscreen test, and the result review. */
export default function Summative() {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const navigate = useNavigate();
    const L = TEXT[lang === 'ru' ? 'ru' : 'uz'];
    const apiLang = lang === 'ru' ? 'ru' : 'uz';

    const [info, setInfo] = useState(null);
    const [history, setHistory] = useState([]);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState('');

    const [attempt, setAttempt] = useState(null); // running test
    const [result, setResult] = useState(null);
    const [answers, setAnswers] = useState([]);
    const [idx, setIdx] = useState(0);
    const [remaining, setRemaining] = useState(0);
    const [violations, setViolations] = useState(0);
    const [away, setAway] = useState(false);
    const [onlyWrong, setOnlyWrong] = useState(true);
    const [confirmOpen, setConfirmOpen] = useState(false);

    const attemptRef = useRef(null);
    const answersRef = useRef([]);
    const finishingRef = useRef(false);
    const awayRef = useRef(false);
    attemptRef.current = attempt;
    answersRef.current = answers;

    const json = (o) => JSON.stringify(o);
    const jsonHeaders = () => ({ ...headers(), 'Content-Type': 'application/json' });

    const loadLobby = useCallback(() => {
        request(`${API_URL}v1/summative/available?lang=${apiLang}`, 'GET', null, headers()).then(setInfo).catch(() => {});
        request(`${API_URL}v1/summative/history`, 'GET', null, headers()).then(setHistory).catch(() => {});
    }, [request, apiLang]);

    useEffect(() => { loadLobby(); }, [loadLobby]);

    const begin = (payload) => {
        finishingRef.current = false;
        awayRef.current = false;
        setAway(false);
        setResult(null);
        setAttempt(payload);
        setAnswers(Array(payload.total).fill(null));
        setIdx(0);
        setRemaining(payload.remaining_seconds);
        setViolations(payload.violations || 0);
    };

    const start = async () => {
        setBusy(true);
        setError('');
        enterFs(); // must happen inside this click (user gesture)
        try {
            const payload = await request(`${API_URL}v1/summative/start`, 'POST',
                json({ lang: apiLang }), jsonHeaders());
            begin(payload);
        } catch (e) {
            exitFs();
            setError((e?.message || '').split(': ').pop() || L.error);
        } finally {
            setBusy(false);
        }
    };

    const finish = useCallback(async () => {
        const a = attemptRef.current;
        if (!a || finishingRef.current) return;
        finishingRef.current = true;
        try {
            const res = await request(`${API_URL}v1/summative/${a.id}/submit`, 'POST',
                json({ answers: answersRef.current }), jsonHeaders());
            setResult(res);
        } catch {
            finishingRef.current = false;
            setError(L.error);
            return;
        }
        setAttempt(null);
        exitFs();
        loadLobby();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [request, loadLobby]);

    // countdown (server-given remaining time; auto-submit at 0)
    useEffect(() => {
        if (!attempt) return undefined;
        const t = setInterval(() => {
            setRemaining((r) => {
                if (r <= 1) { clearInterval(t); setTimeout(finish, 0); return 0; }
                return r - 1;
            });
        }, 1000);
        return () => clearInterval(t);
    }, [attempt, finish]);

    // violations: leaving fullscreen / the tab / the window
    const reportViolation = useCallback(async () => {
        const a = attemptRef.current;
        if (!a || awayRef.current || finishingRef.current) return;
        awayRef.current = true;
        setAway(true);
        try {
            const res = await request(`${API_URL}v1/summative/${a.id}/violation`, 'POST',
                json({ reason: 'left' }), jsonHeaders());
            setViolations(res.violations);
            if (res.status === 'finished') {
                const full = await request(`${API_URL}v1/summative/${a.id}`, 'GET', null, headers());
                finishingRef.current = true;
                setResult(full);
                setAttempt(null);
                setAway(false);
                exitFs();
                loadLobby();
            }
        } catch { /* offline: the local warning still shows */ }
    }, [request, loadLobby]);

    useEffect(() => {
        if (!attempt) return undefined;
        const onFs = () => { if (fsSupported() && !document.fullscreenElement) reportViolation(); };
        const onVis = () => { if (document.hidden) reportViolation(); };
        const onBlur = () => { if (!document.fullscreenElement || document.hidden) reportViolation(); };
        const block = (e) => e.preventDefault();
        const onKey = (e) => {
            const k = e.key;
            const ctrl = e.ctrlKey || e.metaKey;
            if (
                k === 'F12' || k === 'F11' || k === 'F5' || k === 'PrintScreen'
                || (ctrl && ['c', 'v', 'x', 'u', 'p', 's', 'f', 'a', 'r', 'w', 't', 'n', 'l', 'k', 'e'].includes(k.toLowerCase()))
                || (ctrl && e.shiftKey && ['i', 'j', 'c', 'k', 'n', 't'].includes(k.toLowerCase()))
                || (e.altKey && ['ArrowLeft', 'ArrowRight', 'Tab'].includes(k))
            ) {
                e.preventDefault();
                e.stopPropagation();
            }
        };
        const onUnload = (e) => { e.preventDefault(); e.returnValue = ''; };
        document.addEventListener('fullscreenchange', onFs);
        document.addEventListener('visibilitychange', onVis);
        window.addEventListener('blur', onBlur);
        document.addEventListener('contextmenu', block);
        document.addEventListener('copy', block);
        document.addEventListener('cut', block);
        document.addEventListener('paste', block);
        document.addEventListener('selectstart', block);
        document.addEventListener('dragstart', block);
        window.addEventListener('keydown', onKey, true);
        window.addEventListener('beforeunload', onUnload);
        return () => {
            document.removeEventListener('fullscreenchange', onFs);
            document.removeEventListener('visibilitychange', onVis);
            window.removeEventListener('blur', onBlur);
            document.removeEventListener('contextmenu', block);
            document.removeEventListener('copy', block);
            document.removeEventListener('cut', block);
            document.removeEventListener('paste', block);
            document.removeEventListener('selectstart', block);
            document.removeEventListener('dragstart', block);
            window.removeEventListener('keydown', onKey, true);
            window.removeEventListener('beforeunload', onUnload);
        };
    }, [attempt, reportViolation]);

    // leaving this page mid-test (router) also exits fullscreen
    useEffect(() => () => exitFs(), []);

    const returnToTest = () => {
        enterFs();
        awayRef.current = false;
        setAway(false);
    };

    const pick = (qi, oi) => {
        setAnswers((prev) => {
            const next = [...prev];
            next[qi] = oi;
            const a = attemptRef.current;
            if (a) {
                request(`${API_URL}v1/summative/${a.id}/save`, 'POST', json({ answers: next }), jsonHeaders()).catch(() => {});
            }
            return next;
        });
    };

    // ── running test ──
    if (attempt) {
        const q = attempt.questions[idx];
        const unanswered = answers.filter((a) => a === null).length;
        // Portal to <body>: a transformed/filtered ancestor in the app layout
        // would otherwise turn this "fixed" layer into a box inside the page
        // and let the sidebar show through.
        return createPortal(
            <div className="sm-test" onContextMenu={(e) => e.preventDefault()}>
                <div className="sm-test-bar">
                    <span className="sm-q-count">{L.q(idx + 1, attempt.total)}</span>
                    <span className={`sm-timer ${remaining < 60 ? 'is-low' : ''}`}>⏱ {fmtTime(remaining)}</span>
                    <span className="sm-viol">⚠ {violations}/{attempt.max_violations}</span>
                </div>
                <div className="sm-test-body">
                    <div className="sm-question">{q.text}</div>
                    <div className="sm-options">
                        {q.options.map((opt, oi) => (
                            <button
                                key={`${idx}-${oi}`}
                                className={`sm-option ${answers[idx] === oi ? 'is-picked' : ''}`}
                                onClick={() => pick(idx, oi)}
                            >
                                <b>{LETTERS[oi]}</b><span>{opt}</span>
                            </button>
                        ))}
                    </div>
                    <div className="sm-nav">
                        <button className="sm-btn" disabled={idx === 0} onClick={() => setIdx(idx - 1)}>← {L.prev}</button>
                        {idx < attempt.total - 1 ? (
                            <button className="sm-btn sm-btn--primary" onClick={() => setIdx(idx + 1)}>{L.next} →</button>
                        ) : (
                            <button
                                className="sm-btn sm-btn--danger"
                                onClick={() => setConfirmOpen(true)}
                            >
                                {L.finish}
                            </button>
                        )}
                    </div>
                    <div className="sm-map">
                        {attempt.questions.map((_, i) => (
                            <button
                                key={i}
                                className={`sm-dot ${answers[i] !== null ? 'is-done' : ''} ${i === idx ? 'is-cur' : ''}`}
                                onClick={() => setIdx(i)}
                            >
                                {i + 1}
                            </button>
                        ))}
                    </div>
                    <button
                        className="sm-link"
                        onClick={() => setConfirmOpen(true)}
                    >
                        {L.finish}
                    </button>
                </div>
                {confirmOpen && (
                    <div className="sm-away sm-confirm">
                        <div className="sm-away-card sm-confirm-card">
                            <h2>{L.finishTitle}</h2>
                            <p>{L.confirmFinish(unanswered)}</p>
                            <div className="sm-row sm-confirm-row">
                                <button className="sm-btn" onClick={() => setConfirmOpen(false)}>{L.cancel}</button>
                                <button className="sm-btn sm-btn--danger" onClick={() => { setConfirmOpen(false); finish(); }}>{L.finishYes}</button>
                            </div>
                        </div>
                    </div>
                )}
                {away && (
                    <div className="sm-away">
                        <div className="sm-away-card">
                            <h2>⚠ {L.warnTitle}</h2>
                            <p>{L.warnText(violations, attempt.max_violations)}</p>
                            <button className="sm-btn sm-btn--primary" onClick={returnToTest}>{L.warnBtn}</button>
                        </div>
                    </div>
                )}
            </div>,
            document.body
        );
    }

    // ── result ──
    if (result) {
        const review = result.review || [];
        const shown = onlyWrong ? review.filter((r) => r.chosen !== r.correct) : review;
        return createPortal(
            <div className="sm-page">
                <div className="sm-card">
                    <h1>{L.result}</h1>
                    <div className={`sm-score ${result.score >= 60 ? 'is-pass' : 'is-fail'}`}>{result.score}%</div>
                    <p className="sm-sub">{L.correct}: {result.correct} / {result.total}</p>
                    {L.reasons[result.finish_reason] && <p className="sm-warn">{L.reasons[result.finish_reason]}</p>}
                    <div className="sm-row">
                        <button className="sm-btn" onClick={() => setOnlyWrong(!onlyWrong)}>{onlyWrong ? L.showAll : L.onlyWrong}</button>
                        <button className="sm-btn sm-btn--primary" onClick={() => { setResult(null); loadLobby(); }}>{L.back}</button>
                    </div>
                    <h3>{L.review}</h3>
                    <div className="sm-review">
                        {shown.map((r, i) => (
                            <div key={i} className={`sm-rev ${r.chosen === r.correct ? 'is-ok' : 'is-bad'}`}>
                                <div className="sm-rev-q">{r.text}</div>
                                <div className="sm-rev-a">
                                    {L.yourAnswer}: <b>{r.chosen === null || r.chosen === undefined ? L.noAnswer : r.options[r.chosen]}</b>
                                </div>
                                {r.chosen !== r.correct && (
                                    <div className="sm-rev-a sm-rev-right">{L.rightAnswer}: <b>{r.options[r.correct]}</b></div>
                                )}
                                {r.explanation && <div className="sm-rev-exp">{r.explanation}</div>}
                            </div>
                        ))}
                    </div>
                </div>
            </div>,
            document.body
        );
    }

    // ── lobby ──
    const enough = info && info.questions >= (info.min_questions || 10);
    return createPortal(
        <div className="sm-page">
            <div className="sm-card">
                <button className="sm-link" onClick={() => navigate('/student/dashboard')}>← {L.back}</button>
                <h1>📝 {L.title}</h1>
                <p className="sm-sub">{L.sub}</p>

                {info && <p className="sm-plan">{L.plan(info.lessons, info.planned, info.minutes)}</p>}
                {info && !enough && <p className="sm-warn">{L.notEnough(info.min_questions)}</p>}

                <div className="sm-rules">
                    <b>{L.rules}</b>
                    <ul>{L.rulesList.map((r) => <li key={r}>{r}</li>)}</ul>
                </div>

                {error && <p className="sm-warn">{error}</p>}
                <button className="sm-btn sm-btn--primary sm-start" disabled={busy || (!enough && !info?.in_progress)} onClick={start}>
                    {busy ? L.starting : info?.in_progress ? L.resume : L.start}
                </button>

                <h3>{L.history}</h3>
                {history.length === 0 && <p className="sm-sub">{L.noHistory}</p>}
                <div className="sm-history">
                    {history.map((h) => (
                        <div key={h.id} className="sm-hist-row">
                            <span>{new Date(h.started_at).toLocaleDateString()}</span>
                            <span>{h.total} ta</span>
                            <b className={h.score >= 60 ? 'is-pass' : 'is-fail'}>
                                {h.status === 'finished' ? `${h.score}%` : L.status[h.status]}
                            </b>
                            {h.status === 'finished' && (
                                <button
                                    className="sm-link"
                                    onClick={async () => {
                                        try { setResult(await request(`${API_URL}v1/summative/${h.id}`, 'GET', null, headers())); } catch { setError(L.error); }
                                    }}
                                >
                                    {L.review}
                                </button>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>,
        document.body
    );
}
