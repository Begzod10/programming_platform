import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './TeacherNotifications.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { subscribeNotifications } from '../../../api/notificationsSocket';

const POLL_MS = 30000;

const ago = (iso) => {
    const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
    if (s < 60) return 'hozir';
    if (s < 3600) return `${Math.floor(s / 60)} daq. oldin`;
    if (s < 86400) return `${Math.floor(s / 3600)} soat oldin`;
    return new Date(iso).toLocaleDateString('uz-UZ', { day: '2-digit', month: '2-digit' });
};

/** The teacher's notifications (e.g. "a student's code check needs you"): live over the shared socket. */
export default function TeacherNotifications() {
    const { request } = useHttp();
    const navigate = useNavigate();
    const [items, setItems] = useState(null);
    const [error, setError] = useState(false);

    const load = useCallback(() => {
        request(`${API_URL}v1/notifications/?limit=100`, 'GET', null, headers())
            .then((d) => { setItems(Array.isArray(d?.items) ? d.items : []); setError(false); })
            .catch(() => { setItems((prev) => prev || []); setError(true); });
    }, [request]);

    useEffect(() => {
        load();
        const t = setInterval(load, POLL_MS);                      // safety net; the socket is the fast path
        const unsub = subscribeNotifications((msg) => {
            if (msg && msg.type === 'notification' && msg.notification) {
                setItems((prev) => (prev || []).some((n) => n.id === msg.notification.id) ? prev : [msg.notification, ...(prev || [])]);
            }
        });
        return () => { clearInterval(t); unsub(); };
    }, [load]);

    const unread = useMemo(() => (items || []).filter((n) => !n.is_read).length, [items]);

    const markOne = (id) => {
        setItems((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
        request(`${API_URL}v1/notifications/${id}/read`, 'POST', null, headers()).catch(() => {});
    };
    const markAll = () => {
        setItems((prev) => prev.map((n) => ({ ...n, is_read: true })));
        request(`${API_URL}v1/notifications/read-all`, 'POST', null, headers()).catch(() => {});
    };
    const open = (n) => { if (!n.is_read) markOne(n.id); if (n.link) navigate(n.link); };

    return (
        <div className="tn-page">
            <div className="tn-head">
                <h1>Bildirishnomalar</h1>
                {unread > 0 && <button className="tn-btn" onClick={markAll}>Hammasini o'qilgan qilish</button>}
            </div>
            <p className="tn-sub">{unread > 0 ? `${unread} ta o'qilmagan` : "Hammasi o'qilgan"}</p>
            {error && <p className="tn-err" role="alert">Yuklashda xatolik, qayta urinib ko'ramiz…</p>}
            {items === null && <p>Yuklanmoqda…</p>}
            {items && items.length === 0 && !error && <p className="tn-empty">Hozircha bildirishnoma yo'q.</p>}
            <ul className="tn-list">
                {(items || []).map((n) => (
                    <li key={n.id}>
                        <button className={`tn-item ${n.is_read ? '' : 'tn-item--unread'}`} onClick={() => open(n)}>
                            <span className="tn-ico" aria-hidden="true">{n.icon && n.icon.length <= 4 ? n.icon : '🔔'}</span>
                            <span className="tn-main">
                                <span className="tn-title">{n.title}</span>
                                {n.body && <span className="tn-body">{n.body}</span>}
                            </span>
                            <span className="tn-time">{ago(n.created_at)}</span>
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}
