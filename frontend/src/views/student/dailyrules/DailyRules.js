// Student-facing explainer for the daily learning-quota / games-lock system,
// with a teacher-only admin panel (shown only if GET /daily/config succeeds).
import { useEffect, useState, useCallback } from 'react';
import { API_URL, headers } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import AppHeader from '../../../components/appheader/AppHeader';
import {
    BookOpen, Lock, Gamepad2, AlertTriangle, Layers, Flame, CalendarClock, Settings,
} from 'lucide-react';
import './DailyRules.css';

export default function DailyRules({ chrome = true }) {
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    const [status, setStatus] = useState(null);
    const [cfg, setCfg] = useState(null);       // non-null → teacher (admin panel)
    const [saving, setSaving] = useState(false);

    const base = status?.base_required ?? cfg?.base_lessons ?? 2;
    const penalty = status?.penalty_per_lesson ?? cfg?.penalty_per_lesson ?? 100;
    const enforceFrom = status?.enforce_from ?? cfg?.enforce_from ?? null;
    const enabled = (cfg?.enabled ?? status?.enabled) ?? true;

    const load = useCallback(async () => {
        try {
            const r = await fetch(`${API_URL}v1/daily/status`, { headers: headers() });
            if (r.ok) setStatus(await r.json());
        } catch { /* ignore */ }
        try {
            const rc = await fetch(`${API_URL}v1/daily/config`, { headers: headers() });
            if (rc.ok) setCfg(await rc.json());   // only teachers get 200 here
        } catch { /* ignore */ }
    }, []);
    useEffect(() => { load(); }, [load]);

    const saveCfg = async (patch) => {
        setSaving(true);
        try {
            const r = await fetch(`${API_URL}v1/daily/config`, {
                method: 'PUT',
                headers: { ...headers(), 'Content-Type': 'application/json' },
                body: JSON.stringify(patch),
            });
            if (r.ok) setCfg(await r.json());
        } catch { /* ignore */ }
        finally { setSaving(false); }
    };

    const fmtDate = (iso) => {
        if (!iso) return ru ? 'сразу' : 'darhol';
        try { return new Date(iso).toLocaleDateString(ru ? 'ru-RU' : 'uz-UZ', { day: 'numeric', month: 'long' }); }
        catch { return iso; }
    };

    const rules = [
        {
            Icon: BookOpen, tone: 'green',
            title: ru ? 'Ежедневная норма' : 'Kunlik norma',
            body: ru
                ? <>Каждый день нужно завершить <b>{base} урока</b> — из любых твоих курсов.</>
                : <>Har kuni <b>{base} ta dars</b> yakunlashing kerak — istalgan kursingdan.</>,
        },
        {
            Icon: Gamepad2, tone: 'violet',
            title: ru ? 'Что блокируется' : 'Nima qulflanadi',
            body: ru
                ? <>Пока норма не выполнена, <b>«Для малышей»</b> и <b>«1 на 1»</b> закрыты 🔒. Выполни норму — и они откроются 🎮.</>
                : <><b>«Kichkinalar uchun»</b> va <b>«1 vs 1 poyga»</b> norma bajarilmaguncha yopiq 🔒. Normani bajar — ochiladi 🎮.</>,
        },
        {
            Icon: AlertTriangle, tone: 'red',
            title: ru ? 'Если не выполнить' : 'Bajarmasang',
            body: ru
                ? <>В конце дня за каждый невыполненный урок снимается <b>−{penalty} баллов</b>. Баланс не уходит в минус — минимум <b>0</b>.</>
                : <>Kun oxirida har bir bajarilmagan dars uchun <b>−{penalty} ball</b> yechiladi. Balans minusga tushmaydi — eng kami <b>0</b>.</>,
        },
        {
            Icon: Layers, tone: 'amber',
            title: ru ? 'Долг переносится' : "Qarz o'tadi",
            body: ru
                ? <>Невыполненные уроки переходят на завтра и <b>накапливаются</b>: 2 + 2 + 2 = <b>6</b> за 3 дня. Лимита нет — пока не закроешь.</>
                : <>Bajarilmagan darslar ertangi kunga o'tadi va <b>yig'iladi</b>: 2 + 2 + 2 = <b>6</b> (3 kunda). Limit yo'q — yopmaguningcha.</>,
        },
        {
            Icon: Flame, tone: 'green',
            title: ru ? 'Бонус за серию' : 'Seriya bonusi',
            body: ru
                ? <>Держи ежедневную серию — и получай <b>+0.1%</b> от баллов, заработанных за время серии.</>
                : <>Har kuni seriyani saqla — seriya davomida topgan balldan <b>+0.1%</b> bonus olasan.</>,
        },
        {
            Icon: CalendarClock, tone: 'cyan',
            title: ru ? 'Когда начинается' : 'Qachon boshlanadi',
            body: ru
                ? <>Штрафы начинаются с <b>{fmtDate(enforceFrom)}</b>. До этого — только знакомство, баллы не снимаются.</>
                : <>Jarimalar <b>{fmtDate(enforceFrom)}</b> dan boshlanadi. Undan oldin — faqat tanishuv, ball yechilmaydi.</>,
        },
    ];

    return (
        <div className={chrome ? 'dr-dark' : 'dr-embed'}>
            {chrome && <AppHeader />}
            <div className="dr-shell">
                <div className="dr-hero dr-rise">
                    <div className="dr-hero-ico"><Lock size={26} /></div>
                    <div>
                        <h1>{ru ? 'Ежедневная учебная норма' : "Kunlik o'quv normasi"}</h1>
                        <p>{ru
                            ? 'Сначала учёба, потом игры — короткие правила ниже.'
                            : "Avval o'qish, keyin o'yin — qoidalar quyida."}</p>
                    </div>
                    {status && (
                        <div className={`dr-today ${status.unlocked ? 'is-open' : 'is-locked'}`}>
                            {status.unlocked
                                ? <>🎮 {ru ? 'Открыто' : 'Ochildi'}</>
                                : <><Lock size={14} /> {status.completed}/{base}</>}
                        </div>
                    )}
                </div>

                <div className="dr-grid">
                    {rules.map((r, i) => (
                        <div className={`dr-card dr-tone-${r.tone} dr-rise`} key={i}
                            style={{ animationDelay: `${0.05 + i * 0.05}s` }}>
                            <div className="dr-card-ico"><r.Icon size={20} /></div>
                            <div className="dr-card-title">{r.title}</div>
                            <div className="dr-card-body">{r.body}</div>
                        </div>
                    ))}
                </div>

                {!enabled && (
                    <div className="dr-note">
                        {ru ? '⏸ Система сейчас выключена преподавателем.' : "⏸ Tizim hozir o'qituvchi tomonidan o'chirilgan."}
                    </div>
                )}

                {cfg && (
                    <div className="dr-admin dr-rise">
                        <div className="dr-admin-head"><Settings size={17} />
                            {ru ? 'Управление (преподаватель)' : "Boshqaruv (o'qituvchi)"}</div>

                        <label className="dr-row">
                            <span>{ru ? 'Система включена' : 'Tizim yoqilgan'}</span>
                            <button
                                className={`dr-switch ${cfg.enabled ? 'on' : ''}`}
                                disabled={saving}
                                onClick={() => saveCfg({ enabled: !cfg.enabled })}>
                                <span className="dr-knob" />
                            </button>
                        </label>

                        <label className="dr-row">
                            <span>{ru ? 'Штрафы с даты' : 'Jarimalar sanadan'}</span>
                            <input type="date" className="dr-input" disabled={saving}
                                value={cfg.enforce_from || ''}
                                onChange={(e) => saveCfg(e.target.value
                                    ? { enforce_from: e.target.value }
                                    : { clear_enforce_from: true })} />
                        </label>

                        <label className="dr-row">
                            <span>{ru ? 'Уроков в день' : 'Kunlik dars'}</span>
                            <input type="number" min="1" max="10" className="dr-input dr-input--sm"
                                disabled={saving} defaultValue={cfg.base_lessons}
                                onBlur={(e) => saveCfg({ base_lessons: Number(e.target.value) })} />
                        </label>

                        <label className="dr-row">
                            <span>{ru ? 'Штраф за урок' : 'Dars uchun jarima'}</span>
                            <input type="number" min="0" max="1000" step="10" className="dr-input dr-input--sm"
                                disabled={saving} defaultValue={cfg.penalty_per_lesson}
                                onBlur={(e) => saveCfg({ penalty_per_lesson: Number(e.target.value) })} />
                        </label>

                        <label className="dr-row">
                            <span>{ru ? 'Разблокировка' : 'Ochilish sharti'}</span>
                            <select className="dr-input" disabled={saving} value={cfg.unlock_mode}
                                onChange={(e) => saveCfg({ unlock_mode: e.target.value })}>
                                <option value="base">{ru ? `${cfg.base_lessons} урока (норма)` : `${cfg.base_lessons} dars (norma)`}</option>
                                <option value="full">{ru ? 'норма + весь долг' : "norma + butun qarz"}</option>
                            </select>
                        </label>
                        <div className="dr-admin-hint">
                            {ru ? 'Изменения применяются мгновенно для всех студентов.' : "O'zgarishlar barcha studentlarga darhol qo'llanadi."}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
