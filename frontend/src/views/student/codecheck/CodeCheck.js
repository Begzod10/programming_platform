import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './CodeCheck.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import AppHeader from '../../../components/appheader/AppHeader';
import { apiErrorMessage } from '../../../utils/apiError';

/**
 * A short quiz on the student's OWN submitted code. It never changes points by
 * itself — a wrong, late or "suspicious" result goes to the teacher, who talks to
 * the student. We count how often the student leaves this tab (a sign of asking
 * a chatbot) and say nothing about it on screen.
 */
export default function CodeCheck() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { request } = useHttp();
    const { lang } = useTranslation();
    const ru = lang === 'ru';

    const [phase, setPhase] = useState('intro');      // intro | loading | quiz | sending | done | error
    const [error, setError] = useState('');
    const [quiz, setQuiz] = useState(null);
    const [idx, setIdx] = useState(0);
    const [left, setLeft] = useState(0);
    const [result, setResult] = useState(null);

    const answers = useRef([]);
    const times = useRef([]);
    const blurs = useRef(0);
    const lastBlurAt = useRef(0);
    const shownAt = useRef(0);

    // Leaving the tab/window: visibilitychange and blur both fire for one switch, so count once per second.
    useEffect(() => {
        if (phase !== 'quiz') return undefined;
        const note = () => {
            const now = Date.now();
            if (now - lastBlurAt.current > 1000) { blurs.current += 1; lastBlurAt.current = now; }
        };
        const onVisibility = () => { if (document.hidden) note(); };
        document.addEventListener('visibilitychange', onVisibility);
        window.addEventListener('blur', note);
        return () => {
            document.removeEventListener('visibilitychange', onVisibility);
            window.removeEventListener('blur', note);
        };
    }, [phase]);

    const start = async () => {
        setPhase('loading');
        setError('');
        try {
            const data = await request(`${API_URL}v1/code-checks/${id}/start?lang=${ru ? 'ru' : 'uz'}`, 'POST', null, headers());
            answers.current = []; times.current = []; blurs.current = 0;
            setQuiz(data);
            setIdx(0);
            setLeft(data.seconds_per_question);
            shownAt.current = Date.now();
            setPhase('quiz');
        } catch (e) {
            setError(apiErrorMessage(e) || (ru ? 'Не удалось начать проверку' : "Tekshiruvni boshlab bo'lmadi"));
            setPhase('error');
        }
    };

    const submit = useCallback(async () => {
        setPhase('sending');
        try {
            const data = await request(`${API_URL}v1/code-checks/${id}/submit`, 'POST', JSON.stringify({
                answers: answers.current, blur_count: blurs.current, times_ms: times.current,
            }), headers());
            setResult(data);
            setPhase('done');
        } catch (e) {
            setError(apiErrorMessage(e) || (ru ? 'Не удалось отправить ответы' : "Javoblarni yuborib bo'lmadi"));
            setPhase('error');
        }
    }, [id, request, ru]);

    const advance = useCallback((choice) => {
        answers.current[idx] = choice;
        times.current[idx] = Date.now() - shownAt.current;
        if (quiz && idx + 1 < quiz.questions.length) {
            setIdx(idx + 1);
            setLeft(quiz.seconds_per_question);
            shownAt.current = Date.now();
        } else {
            submit();
        }
    }, [idx, quiz, submit]);

    // one tick per second; when the time is up the question counts as unanswered
    useEffect(() => {
        if (phase !== 'quiz') return undefined;
        const t = setTimeout(() => {
            if (left <= 1) advance(null);
            else setLeft(left - 1);
        }, 1000);
        return () => clearTimeout(t);
    }, [phase, left, advance]);

    const q = quiz?.questions?.[idx];
    const total = quiz?.questions?.length || 0;
    const ok = result?.status === 'passed';

    return (
        <div className="cc-root">
            <AppHeader />
            <div className="cc-shell">
                {phase === 'intro' && (
                    <div className="cc-card">
                        <div className="cc-emoji">📝</div>
                        <h1>{ru ? 'Подтвердите свой код' : 'Kodingizni tasdiqlang'}</h1>
                        <p>{ru
                            ? 'Вам будет задано несколько коротких вопросов по вашему же проекту. На каждый вопрос — 30 секунд. Отвечайте сами, не покидая эту страницу.'
                            : "Loyihangiz haqida bir nechta qisqa savol beriladi. Har bir savolga 30 soniya. O'zingiz javob bering va bu sahifadan chiqmang."}</p>
                        <button className="cc-btn" onClick={start}>{ru ? 'Начать' : 'Boshlash'}</button>
                        <button className="cc-link" onClick={() => navigate('/student/projects')}>{ru ? 'Позже' : 'Keyinroq'}</button>
                    </div>
                )}

                {(phase === 'loading' || phase === 'sending') && (
                    <div className="cc-card"><div className="cc-emoji">⏳</div>
                        <p>{phase === 'loading'
                            ? (ru ? 'Готовим вопросы по вашему коду…' : "Kodingiz bo'yicha savollar tayyorlanmoqda…")
                            : (ru ? 'Отправляем ответы…' : 'Javoblar yuborilmoqda…')}</p>
                    </div>
                )}

                {phase === 'quiz' && q && (
                    <div className="cc-card cc-quiz" onCopy={e => e.preventDefault()} onContextMenu={e => e.preventDefault()}>
                        <div className="cc-top">
                            <span>{idx + 1} / {total}</span>
                            <span className={`cc-timer ${left <= 10 ? 'cc-timer--low' : ''}`} aria-label="timer">{left}s</span>
                        </div>
                        <div className="cc-bar"><div className="cc-bar-fill" style={{ width: `${(left / quiz.seconds_per_question) * 100}%` }} /></div>
                        <h2 className="cc-q">{q.q}</h2>
                        <div className="cc-opts">
                            {q.options.map((o, i) => (
                                <button key={`${idx}-${i}`} className="cc-opt" onClick={() => advance(i)}>
                                    <span className="cc-letter">{'ABCD'[i]}</span><span>{o}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {phase === 'done' && (
                    <div className="cc-card">
                        <div className="cc-emoji">{ok ? '✅' : '📨'}</div>
                        <h1>{ok ? (ru ? 'Проверка пройдена' : "Tekshiruv o'tildi") : (ru ? 'Ответы приняты' : 'Javoblar qabul qilindi')}</h1>
                        <p>{ok
                            ? (ru ? 'Спасибо, вы подтвердили, что понимаете свой код.' : "Rahmat, kodingizni tushunishingiz tasdiqlandi.")
                            : (ru ? 'Результат передан преподавателю — он может поговорить с вами о вашем проекте.' : "Natija o'qituvchiga yuborildi — u loyihangiz haqida siz bilan suhbatlashishi mumkin.")}</p>
                        <button className="cc-btn" onClick={() => navigate('/student/projects')}>{ru ? 'К моим проектам' : 'Loyihalarimga'}</button>
                    </div>
                )}

                {phase === 'error' && (
                    <div className="cc-card">
                        <div className="cc-emoji">⚠️</div>
                        <p className="cc-error" role="alert">{error}</p>
                        <button className="cc-btn" onClick={() => navigate('/student/projects')}>{ru ? 'К моим проектам' : 'Loyihalarimga'}</button>
                    </div>
                )}
            </div>
        </div>
    );
}
