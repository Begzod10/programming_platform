import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './CodeTasks.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import AppHeader from '../../../components/appheader/AppHeader';

const TXT = {
    uz: { title: 'Kod vazifalari', todo: 'Yozish kerak', wait: 'Tekshirilmoqda', done: 'Baholangan',
          empty: "Hali vazifa yo'q", loading: 'Yuklanmoqda…', err: "Vazifalarni yuklab bo'lmadi.", retry: 'Qayta urinish', returned: 'Qaytarilgan' },
    ru: { title: 'Задания по коду', todo: 'Нужно выполнить', wait: 'На проверке', done: 'Оценено',
          empty: 'Заданий пока нет', loading: 'Загрузка…', err: 'Не удалось загрузить задания.', retry: 'Повторить', returned: 'Возвращено' },
};
const GROUPS = [['todo', ['assigned', 'returned']], ['wait', ['submitted']], ['done', ['graded']]];
const LANGUAGE_NAME = { python: 'Python', javascript: 'JavaScript', html: 'HTML', css: 'CSS', sql: 'SQL', json: 'JSON', text: 'Text' };

/** The student's coding tasks, grouped by what they need to do next. */
export default function CodeTasks() {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const t = TXT[lang === 'uz' ? 'uz' : 'ru'];
    const navigate = useNavigate();
    const [tasks, setTasks] = useState(null);
    const [error, setError] = useState(false);

    const load = () => {
        setError(false);
        request(`${API_URL}v1/code-tasks/`, 'GET', null, headers()).then(setTasks).catch(() => setError(true));
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(load, []);

    return (
        <div className="ct-page">
            <AppHeader />
            <div className="ct-body">
                <h1 className="ct-h1">{t.title}</h1>
                {error && <div className="ct-empty"><p>{t.err}</p><button className="ct-btn" onClick={load}>{t.retry}</button></div>}
                {!error && !tasks && <div className="ct-empty"><p>{t.loading}</p></div>}
                {tasks && tasks.length === 0 && <div className="ct-empty"><span>📝</span><p>{t.empty}</p></div>}
                {tasks && GROUPS.map(([key, statuses]) => {
                    const rows = tasks.filter((x) => statuses.includes(x.status));
                    if (!rows.length) return null;
                    return (
                        <section key={key} className="ct-group">
                            <h2 className="ct-h2">{t[key]}</h2>
                            <ul className="ct-list">
                                {rows.map((x) => (
                                    <li key={x.id}>
                                        <button className="ct-item" onClick={() => navigate(`/student/code-tasks/${x.id}`)}>
                                            <span className="ct-name">{x.title}</span>
                                            <span className="ct-chip">{LANGUAGE_NAME[x.language] || x.language}</span>
                                            {x.status === 'returned' && <span className="ct-flag">{t.returned}</span>}
                                            {x.status === 'graded' && <span className="ct-pts">{x.graded_points}/{x.max_points}</span>}
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </section>
                    );
                })}
            </div>
        </div>
    );
}
