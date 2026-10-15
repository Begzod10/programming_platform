import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';

/** Shown on "My projects" while a code-check quiz is waiting for the student. */
export default function CodeCheckBanner() {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const navigate = useNavigate();
    const ru = lang === 'ru';
    const [checks, setChecks] = useState([]);

    useEffect(() => {
        let alive = true;
        request(`${API_URL}v1/code-checks/mine`, 'GET', null, headers())
            .then((d) => { if (alive && Array.isArray(d)) setChecks(d); })
            .catch(() => { /* the banner is a convenience: the notification links to the quiz as well */ });
        return () => { alive = false; };
    }, [request]);

    if (!checks.length) return null;
    const c = checks[0];
    return (
        <div role="alert" style={{
            background: '#fff7e0', color: '#6b4e00', border: '1px solid #f0d98a', borderRadius: 12,
            padding: '12px 16px', margin: '0 0 16px', display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap',
        }}>
            <span style={{ flex: 1, minWidth: 220 }}>
                📝 {ru
                    ? `Подтвердите свой код: «${c.project_title}» — ${c.total_questions} вопроса по 30 секунд.`
                    : `Kodingizni tasdiqlang: «${c.project_title}» — ${c.total_questions} ta savol, har biriga 30 soniya.`}
            </span>
            <button onClick={() => navigate(`/student/code-check/${c.id}`)} style={{
                background: '#6c5ce7', color: '#fff', border: 0, borderRadius: 10, padding: '8px 16px', fontWeight: 700, cursor: 'pointer',
            }}>{ru ? 'Пройти' : "O'tish"}</button>
        </div>
    );
}
