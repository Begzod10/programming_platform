import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL, headers, resolveImageUrl } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import AppHeader from '../../../components/appheader/AppHeader';
import './Notifications.css';
import {
    Bell, CheckCircle2, XCircle, Clock, Award, GraduationCap,
    CheckCheck, Inbox, ChevronRight, Sparkles,
} from 'lucide-react';

const UNREAD_KEY = 'notif:unread';
const POLL_MS = 25000;

/* Presentation per notification type — the heading is localized here so the
   server stays language-neutral (it only stores entity text). */
function present(n, ru) {
    const title = n.title || '';
    switch (n.type) {
        case 'project_approved':
            return {
                icon: CheckCircle2, tone: n.tone || 'ok',
                heading: ru ? 'Проект одобрен' : 'Loyiha tasdiqlandi',
                text: `«${title}»${n.extra ? ` · ${ru ? 'оценка' : 'baho'} ${n.extra}` : ''}`,
            };
        case 'project_rejected':
            return {
                icon: XCircle, tone: n.tone || 'bad',
                heading: ru ? 'Проект отклонён' : 'Loyiha qaytarildi',
                text: n.body ? `«${title}» — ${n.body}` : `«${title}» ${ru ? 'требует доработки.' : 'qayta ishlanishi kerak.'}`,
            };
        case 'project_submitted':
            return {
                icon: Clock, tone: n.tone || 'wait',
                heading: ru ? 'Проект на проверке' : 'Loyiha tekshirilmoqda',
                text: `«${title}» ${ru ? 'отправлен и ждёт проверки.' : 'yuborildi va tekshirilmoqda.'}`,
            };
        case 'achievement':
            return {
                icon: Award, tone: n.tone || 'star',
                heading: ru ? 'Новое достижение!' : 'Yangi yutuq!',
                text: `${title}${n.body ? ` — ${n.body}` : ''}`,
            };
        case 'certificate':
            return {
                icon: GraduationCap, tone: n.tone || 'cert',
                heading: ru ? 'Сертификат получен' : 'Sertifikat olindi',
                text: ru ? `Курс «${title}» завершён.` : `«${title}» kursi yakunlandi.`,
            };
        default:
            return { icon: Bell, tone: n.tone || 'ok', heading: title, text: n.body || '' };
    }
}

const KIND = (type) => (type || '').startsWith('project') ? 'project'
    : type === 'achievement' ? 'achievement'
    : type === 'certificate' ? 'certificate' : 'other';

function timeInfo(iso, ru) {
    const d = new Date(iso);
    const now = new Date();
    const diff = Math.max(0, now - d);
    const min = Math.floor(diff / 60000);
    const hr = Math.floor(min / 60);
    const day = Math.floor(hr / 24);

    let label;
    if (min < 1) label = ru ? 'только что' : 'hozirgina';
    else if (min < 60) label = ru ? `${min} мин назад` : `${min} daqiqa oldin`;
    else if (hr < 24) label = ru ? `${hr} ч назад` : `${hr} soat oldin`;
    else if (day < 7) label = ru ? `${day} дн назад` : `${day} kun oldin`;
    else label = d.toLocaleDateString(ru ? 'ru-RU' : 'uz-UZ', { day: 'numeric', month: 'short', year: 'numeric' });

    let bucket;
    if (day === 0) bucket = ru ? 'Сегодня' : 'Bugun';
    else if (day === 1) bucket = ru ? 'Вчера' : 'Kecha';
    else if (day < 7) bucket = ru ? 'На этой неделе' : 'Shu hafta';
    else bucket = ru ? 'Ранее' : 'Oldinroq';

    return { label, bucket };
}

const FILTERS = (ru) => [
    { id: 'all',         label: ru ? 'Все' : 'Hammasi' },
    { id: 'project',     label: ru ? 'Проекты' : 'Loyihalar' },
    { id: 'achievement', label: ru ? 'Достижения' : 'Yutuqlar' },
    { id: 'certificate', label: ru ? 'Сертификаты' : 'Sertifikatlar' },
];

export default function Notifications() {
    const navigate = useNavigate();
    const { lang } = useTranslation();
    const ru = lang === 'ru';

    const [me, setMe] = useState(null);
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const firstLoad = useRef(true);

    const load = async () => {
        try {
            const r = await fetch(`${API_URL}v1/notifications/?limit=100`, { headers: headers() });
            if (!r.ok) throw new Error(r.status);
            const data = await r.json();
            setItems(Array.isArray(data.items) ? data.items : []);
            try { localStorage.setItem(UNREAD_KEY, String(data.unread_count ?? 0)); } catch { /* ignore */ }
        } catch { /* keep previous items on a transient failure */ }
        finally { if (firstLoad.current) { setLoading(false); firstLoad.current = false; } }
    };

    useEffect(() => {
        fetch(`${API_URL}v1/student/me`, { headers: headers() })
            .then(r => r.ok ? r.json() : null).then(setMe).catch(() => {});
        load();
        const id = setInterval(load, POLL_MS);   // keep the feed live
        return () => clearInterval(id);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const unreadCount = useMemo(() => items.filter(n => !n.is_read).length, [items]);

    const shown = useMemo(
        () => (filter === 'all' ? items : items.filter(n => KIND(n.type) === filter)),
        [items, filter],
    );

    const groups = useMemo(() => {
        const out = [];
        const index = {};
        for (const n of shown) {
            const info = timeInfo(n.created_at, ru);
            if (!(info.bucket in index)) { index[info.bucket] = out.length; out.push({ bucket: info.bucket, items: [] }); }
            out[index[info.bucket]].items.push({ ...n, _time: info.label });
        }
        return out;
    }, [shown, ru]);

    const pushUnread = (list) => {
        try { localStorage.setItem(UNREAD_KEY, String(list.filter(n => !n.is_read).length)); } catch { /* ignore */ }
    };

    const markOne = async (id) => {
        setItems(prev => { const next = prev.map(n => n.id === id ? { ...n, is_read: true } : n); pushUnread(next); return next; });
        try { await fetch(`${API_URL}v1/notifications/${id}/read`, { method: 'POST', headers: headers() }); } catch { /* ignore */ }
    };
    const markAll = async () => {
        setItems(prev => { const next = prev.map(n => ({ ...n, is_read: true })); pushUnread(next); return next; });
        try { await fetch(`${API_URL}v1/notifications/read-all`, { method: 'POST', headers: headers() }); } catch { /* ignore */ }
    };
    const openNotif = (n) => { if (!n.is_read) markOne(n.id); if (n.link) navigate(n.link); };

    return (
        <div className="nt-page">
            <AppHeader me={me} />

            <div className="nt-shell">
                <div className="nt-head nt-rise">
                    <div className="nt-head-l">
                        <span className="nt-head-ico"><Bell size={22} /></span>
                        <div>
                            <h1>{ru ? 'Уведомления' : 'Bildirishnomalar'}</h1>
                            <p>
                                {unreadCount > 0
                                    ? (ru ? `${unreadCount} непрочитанных` : `${unreadCount} ta o'qilmagan`)
                                    : (ru ? 'Всё прочитано' : "Hammasi o'qilgan")}
                            </p>
                        </div>
                    </div>
                    {unreadCount > 0 && (
                        <button className="nt-markall" onClick={markAll}>
                            <CheckCheck size={16} /> {ru ? 'Прочитать всё' : "Barchasini o'qilgan deb belgilash"}
                        </button>
                    )}
                </div>

                <div className="nt-filters nt-rise" style={{ animationDelay: '.05s' }}>
                    {FILTERS(ru).map(f => {
                        const count = f.id === 'all' ? items.length : items.filter(n => KIND(n.type) === f.id).length;
                        return (
                            <button key={f.id}
                                className={`nt-filter ${filter === f.id ? 'active' : ''}`}
                                onClick={() => setFilter(f.id)}>
                                {f.label}
                                <span className="nt-filter-count">{count}</span>
                            </button>
                        );
                    })}
                </div>

                {loading ? (
                    <div className="nt-skel">
                        {[0, 1, 2, 3].map(i => <div key={i} className="nt-skel-row" style={{ animationDelay: `${i * 0.08}s` }} />)}
                    </div>
                ) : shown.length === 0 ? (
                    <div className="nt-empty nt-rise">
                        <span className="nt-empty-ico"><Inbox size={46} /></span>
                        <div className="nt-empty-title">{ru ? 'Пока пусто' : "Hozircha bo'sh"}</div>
                        <p>{ru
                            ? 'Здесь появятся результаты проверки проектов, достижения и сертификаты.'
                            : "Bu yerda loyiha natijalari, yutuqlar va sertifikatlar paydo bo'ladi."}</p>
                    </div>
                ) : (
                    <div className="nt-list">
                        {groups.map((g, gi) => (
                            <div className="nt-group" key={g.bucket}>
                                <div className="nt-group-title">{g.bucket}</div>
                                {g.items.map((n, i) => {
                                    const p = present(n, ru);
                                    const Icon = p.icon;
                                    const badge = n.icon ? resolveImageUrl(n.icon) : '';
                                    const unread = !n.is_read;
                                    return (
                                        <button key={n.id}
                                            className={`nt-card nt-tone-${p.tone} ${unread ? 'unread' : ''} nt-rise`}
                                            style={{ animationDelay: `${0.08 + (gi * 3 + i) * 0.04}s` }}
                                            onClick={() => openNotif(n)}>
                                            <span className="nt-card-ico">
                                                {badge
                                                    ? <img src={badge} alt="" onError={e => { e.target.style.display = 'none'; }} />
                                                    : <Icon size={20} />}
                                            </span>
                                            <span className="nt-card-body">
                                                <span className="nt-card-top">
                                                    <span className="nt-card-title">{p.heading}</span>
                                                    {n.points > 0 && (
                                                        <span className="nt-card-pts"><Sparkles size={12} /> +{n.points}</span>
                                                    )}
                                                </span>
                                                <span className="nt-card-text">{p.text}</span>
                                                <span className="nt-card-time">{n._time}</span>
                                            </span>
                                            {unread && <span className="nt-dot" aria-label={ru ? 'непрочитано' : "o'qilmagan"} />}
                                            <ChevronRight size={17} className="nt-card-arrow" />
                                        </button>
                                    );
                                })}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
