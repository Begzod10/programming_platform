import React, { useCallback, useEffect, useMemo, useState } from 'react';
import './TeacherTelegram.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import { Send, Plus, Users, Check, X, Loader2, ExternalLink, RefreshCw, Trash2, AlertTriangle } from 'lucide-react';

const BOT_USERNAME = 'gennis_parent_bot';
const BASE = `${API_URL}v1/teacher/telegram`;

export default function TeacherTelegram() {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const ru = lang !== 'uz';   // teacher UI is Russian-first

    const [chats, setChats] = useState([]);
    const [loading, setLoading] = useState(true);
    const [codeInfo, setCodeInfo] = useState(null);       // { url, expires_at }
    const [creating, setCreating] = useState(false);
    const [students, setStudents] = useState(null);        // null = not loaded yet
    const [editingId, setEditingId] = useState(null);
    const [picked, setPicked] = useState(new Set());
    const [search, setSearch] = useState('');
    const [saving, setSaving] = useState(false);
    const [confirmId, setConfirmId] = useState(null);
    const [msg, setMsg] = useState(null);                   // { ok, text }

    const loadChats = useCallback(() => {
        setLoading(true);
        return request(`${BASE}/chats`, 'GET', null, headers())
            .then(d => setChats(Array.isArray(d) ? d : []))
            .catch(() => { /* keep what we have */ })
            .finally(() => setLoading(false));
    }, [request]);

    useEffect(() => { loadChats(); }, [loadChats]);

    const addGroup = async () => {
        setCreating(true); setMsg(null);
        try {
            const d = await request(`${BASE}/link-code`, 'POST', null, headers());
            setCodeInfo(d);
        } catch {
            setMsg({ ok: false, text: ru ? 'Не удалось создать ссылку' : 'Havola yaratib bo\'lmadi' });
        } finally {
            setCreating(false);
        }
    };

    const openSelect = async (chat) => {
        setEditingId(chat.id); setSearch(''); setMsg(null);
        setPicked(new Set(chat.students.map(s => s.id)));
        if (students === null) {
            try {
                const d = await request(`${BASE}/students`, 'GET', null, headers());
                setStudents(Array.isArray(d) ? d : []);
            } catch {
                setStudents([]);
                setMsg({ ok: false, text: ru ? 'Не удалось загрузить учеников' : 'O\'quvchilarni yuklab bo\'lmadi' });
            }
        }
    };

    const toggle = (id) => setPicked(prev => {
        const next = new Set(prev);
        if (next.has(id)) next.delete(id); else next.add(id);
        return next;
    });

    const classNames = useMemo(() => {
        const set = new Set();
        (students || []).forEach(s => s.classes.forEach(c => set.add(c)));
        return [...set].sort();
    }, [students]);

    const tickClass = (name) => setPicked(prev => {
        const next = new Set(prev);
        (students || []).filter(s => s.classes.includes(name)).forEach(s => next.add(s.id));
        return next;
    });

    const visible = useMemo(() => {
        const q = search.trim().toLowerCase();
        return (students || []).filter(s => !q || s.name.toLowerCase().includes(q));
    }, [students, search]);

    const save = async (chat) => {
        setSaving(true); setMsg(null);
        try {
            const res = await request(`${BASE}/chats/${chat.id}/students`, 'PUT',
                JSON.stringify({ student_ids: [...picked] }), headers());
            setChats(list => list.map(c => c.id === chat.id ? { ...c, students: res?.students || [] } : c));
            setEditingId(null);
            setMsg({ ok: true, text: ru ? 'Сохранено' : 'Saqlandi' });
        } catch (e) {
            const detail = e?.response?.data?.detail;
            setMsg({ ok: false, text: detail || (ru ? 'Не удалось сохранить' : 'Saqlab bo\'lmadi') });
        } finally {
            setSaving(false);
        }
    };

    const disconnect = async (chat) => {
        try {
            await request(`${BASE}/chats/${chat.id}`, 'DELETE', null, headers());
            setChats(list => list.filter(c => c.id !== chat.id));
            if (editingId === chat.id) setEditingId(null);
        } catch {
            setMsg({ ok: false, text: ru ? 'Не удалось отключить' : 'Uzib bo\'lmadi' });
        } finally {
            setConfirmId(null);
        }
    };

    return (
        <div className="tg-page">
            <div className="tg-head">
                <span className="tg-head-ico"><Send size={24} /></span>
                <div>
                    <h1>{ru ? 'Telegram бот' : 'Telegram bot'}</h1>
                    <p>{ru
                        ? 'Подключите бота к Telegram-группе и выберите учеников, чьи результаты он будет присылать каждый день в 20:00 одним общим сообщением.'
                        : "Botni Telegram guruhga ulang va qaysi o'quvchilarning natijasi har kuni 20:00 da bitta umumiy xabar bo'lib kelishini tanlang."}</p>
                    <p className="tg-parents">
                        {ru ? 'Для родителей (личный чат): ' : "Ota-onalar uchun (shaxsiy chat): "}
                        <a href={`https://t.me/${BOT_USERNAME}`} target="_blank" rel="noreferrer">@{BOT_USERNAME}</a>
                    </p>
                </div>
            </div>

            {msg && (
                <div className={`tg-msg ${msg.ok ? 'ok' : 'err'}`}>
                    {msg.ok ? <Check size={16} /> : <AlertTriangle size={16} />} {msg.text}
                </div>
            )}

            <section className="tg-card">
                <div className="tg-card-head">
                    <h2>{ru ? 'Мои группы' : 'Mening guruhlarim'}</h2>
                    <button className="tg-btn primary" onClick={addGroup} disabled={creating}>
                        {creating ? <Loader2 size={16} className="tg-spin" /> : <Plus size={16} />}
                        {ru ? 'Добавить группу' : "Guruh qo'shish"}
                    </button>
                </div>

                {codeInfo && (
                    <div className="tg-code">
                        <a className="tg-btn open" href={codeInfo.url} target="_blank" rel="noreferrer">
                            <ExternalLink size={16} /> {ru ? 'Открыть в Telegram' : 'Telegramda ochish'}
                        </a>
                        <button className="tg-btn ghost" onClick={loadChats}>
                            <RefreshCw size={16} /> {ru ? 'Обновить' : 'Yangilash'}
                        </button>
                        <p>{ru
                            ? 'Откройте ссылку, выберите группу и добавьте бота. Ссылка действует 1 час.'
                            : "Havolani oching, guruhni tanlang va botni qo'shing. Havola 1 soat amal qiladi."}</p>
                    </div>
                )}

                {loading ? (
                    <div className="tg-empty">…</div>
                ) : chats.length === 0 ? (
                    <div className="tg-empty">{ru ? 'Группы пока не подключены' : "Hali guruh ulanmagan"}</div>
                ) : chats.map(c => (
                    <div key={c.id} className={`tg-chat ${c.is_active ? '' : 'off'}`}>
                        <div className="tg-chat-top">
                            <div>
                                <div className="tg-chat-title">{c.title || `#${c.id}`}</div>
                                <div className="tg-chat-meta">
                                    <Users size={14} /> {ru ? `Учеников: ${c.students.length}` : `${c.students.length} ta o'quvchi`}
                                    {!c.is_active && (
                                        <span className="tg-flag">{ru ? 'Бот удалён из группы' : 'Bot guruhdan chiqarilgan'}</span>
                                    )}
                                </div>
                            </div>
                            <div className="tg-chat-actions">
                                <button className="tg-btn" onClick={() => openSelect(c)}>
                                    {ru ? 'Выбрать учеников' : "O'quvchilarni tanlash"}
                                </button>
                                {confirmId === c.id ? (
                                    <>
                                        <button className="tg-btn danger" onClick={() => disconnect(c)}>
                                            {ru ? 'Да, отключить' : 'Ha, uzish'}
                                        </button>
                                        <button className="tg-btn ghost" onClick={() => setConfirmId(null)}>
                                            <X size={14} /> {ru ? 'Нет' : "Yo'q"}
                                        </button>
                                    </>
                                ) : (
                                    <button className="tg-btn ghost" onClick={() => setConfirmId(c.id)}>
                                        <Trash2 size={14} /> {ru ? 'Отключить' : 'Uzish'}
                                    </button>
                                )}
                            </div>
                        </div>

                        {editingId === c.id && (
                            <div className="tg-select">
                                <input className="tg-input" placeholder={ru ? 'Поиск ученика…' : "O'quvchini qidirish…"}
                                    value={search} onChange={e => setSearch(e.target.value)} />
                                <div className="tg-classes">
                                    {classNames.map(n => (
                                        <button key={n} className="tg-chip" onClick={() => tickClass(n)}>
                                            {ru ? `Отметить класс: ${n}` : `Sinfni belgilash: ${n}`}
                                        </button>
                                    ))}
                                </div>
                                <div className="tg-list">
                                    {students === null ? <div className="tg-empty">…</div> : visible.map(s => (
                                        <div key={s.id} className="tg-row">
                                            <input type="checkbox" aria-label={s.name} checked={picked.has(s.id)}
                                                onChange={() => toggle(s.id)} />
                                            <span>{s.name}</span>
                                            <small>{s.classes.join(', ')}</small>
                                        </div>
                                    ))}
                                </div>
                                <div className="tg-select-foot">
                                    <span>{ru ? `Выбрано: ${picked.size}` : `Tanlandi: ${picked.size}`}</span>
                                    <button className="tg-btn ghost" onClick={() => setEditingId(null)}>{ru ? 'Отмена' : 'Bekor'}</button>
                                    <button className="tg-btn primary" onClick={() => save(c)} disabled={saving}>
                                        {saving ? <Loader2 size={16} className="tg-spin" /> : <Check size={16} />}
                                        {ru ? 'Сохранить' : 'Saqlash'}
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </section>
        </div>
    );
}
