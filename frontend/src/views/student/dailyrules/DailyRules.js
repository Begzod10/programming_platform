// Student-facing explainer for the daily learning-quota / games-lock system,
// with a teacher-only admin panel (shown only if GET /daily/config succeeds).
import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL, headers } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import AppHeader from '../../../components/appheader/AppHeader';
import {
    BookOpen, Lock, Gamepad2, AlertTriangle, Layers, Flame, CalendarClock, Settings,
    CheckCircle2, ArrowRight, Target, Coffee,
} from 'lucide-react';
import './DailyRules.css';

const DAY_LABELS = {
    uz: ['Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh', 'Ya'],
    ru: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
};

export default function DailyRules({ chrome = true }) {
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    const navigate = useNavigate();
    const [status, setStatus] = useState(null);
    const [cfg, setCfg] = useState(null);       // non-null → teacher (admin panel)
    const [saving, setSaving] = useState(false);
    const [penalties, setPenalties] = useState([]);
    const [streak, setStreak] = useState(null);

    const base = status?.base_required ?? cfg?.base_lessons ?? 2;
    const penalty = status?.penalty_per_lesson ?? cfg?.penalty_per_lesson ?? 100;
    const enforceFrom = status?.enforce_from ?? cfg?.enforce_from ?? null;
    const enabled = (cfg?.enabled ?? status?.enabled) ?? true;

    // personal stats
    const currentDebt = status?.carried_in ?? 0;
    const totalFined = penalties.reduce((s, p) => s + (p.points_deducted || 0), 0);
    const totalMissed = penalties.reduce((s, p) => s + (p.lessons_missed || 0), 0);
    const streakLen = status?.streak?.length ?? streak?.length ?? 0;
    const totalYield = (streak?.bonus_history || []).reduce((s, b) => s + (b.bonus_points || 0), 0);
    const fmtNum = (n) => (n || 0).toLocaleString('ru-RU').replace(/,/g, ' ');

    // today / enforcement state
    const bonus = status?.completion_bonus ?? cfg?.completion_bonus ?? 20;
    const todayLocal = status?.quota_date ?? new Date().toISOString().slice(0, 10);
    const restDay = !!status?.rest_day;
    // has-data guard avoids a sub-second "active" flash before /status resolves
    const enforcing = enabled && (!!status || !!cfg) && !restDay
        && (!enforceFrom || enforceFrom <= todayLocal);
    const completed = status?.completed ?? 0;
    const remaining = status?.remaining ?? 0;
    // EOD penalty basis = required − completed (includes carried-in debt), NOT remaining
    const pendingMiss = Math.max(0, (status?.required ?? 0) - completed);
    const nextLesson = status?.next_lesson ?? null;
    const pct = Math.min(100, Math.round((completed / Math.max(1, base)) * 100));
    const startNextLesson = () => navigate(nextLesson
        ? `/student/courses/${nextLesson.course_id}/lessons/${nextLesson.lesson_id}`
        : '/student/courses');
    const restSet = new Set((cfg?.rest_days || '').split(',').map(x => x.trim()).filter(Boolean).map(Number));

    const load = useCallback(async () => {
        try {
            const r = await fetch(`${API_URL}v1/daily/status`, { headers: headers() });
            if (r.ok) setStatus(await r.json());
        } catch { /* ignore */ }
        try {
            const rc = await fetch(`${API_URL}v1/daily/config`, { headers: headers() });
            if (rc.ok) setCfg(await rc.json());   // only teachers get 200 here
        } catch { /* ignore */ }
        try {
            const rp = await fetch(`${API_URL}v1/daily/penalties?limit=60`, { headers: headers() });
            if (rp.ok) setPenalties((await rp.json()).items || []);
        } catch { /* ignore */ }
        try {
            const rs = await fetch(`${API_URL}v1/daily/streak`, { headers: headers() });
            if (rs.ok) setStreak(await rs.json());
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
            Icon: Target, tone: 'green',
            title: ru ? 'Награда' : 'Mukofot',
            body: ru
                ? <>Выполни норму — получишь <b>+{bonus} баллов</b> 🎯 и откроются игры.</>
                : <>Normani bajar — <b>+{bonus} ball</b> 🎯 olasan va o'yinlar ochiladi.</>,
        },
        {
            Icon: Flame, tone: 'green',
            title: ru ? 'Бонус за серию' : 'Seriya bonusi',
            body: ru
                ? <>Держи ежедневную серию — и получай <b>+0.1%</b> от баллов, заработанных за время серии.</>
                : <>Har kuni seriyani saqla — seriya davomida topgan balldan <b>+0.1%</b> bonus olasan.</>,
        },
        {
            Icon: Coffee, tone: 'cyan',
            title: ru ? 'Выходные' : 'Dam olish kunlari',
            body: ru
                ? <>В выходные <b>штрафов нет</b> — отдыхай, серия не сгорает 😌.</>
                : <>Dam olish kunlari <b>jarima yo'q</b> — dam ol, seriya buzilmaydi 😌.</>,
        },
        enforcing
            ? {
                Icon: CheckCircle2, tone: 'green',
                title: ru ? '✅ Система активна' : '✅ Tizim faol',
                body: ru
                    ? <>Норма действует — <b>каждый день {base} урока</b>. Выполни — и откроются игры 🎮.</>
                    : <>Norma kuchda — <b>har kuni {base} dars</b>. Bajar — o'yinlar ochiladi 🎮.</>,
            }
            : {
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
                    {status && chrome && (
                        <div className={`dr-today ${status.unlocked ? 'is-open' : 'is-locked'}`}>
                            {status.unlocked
                                ? <>🎮 {ru ? 'Открыто' : 'Ochildi'}</>
                                : <><Lock size={14} /> {status.completed}/{base}</>}
                        </div>
                    )}
                </div>

                {chrome && status && (
                    <div className="dr-today-panel dr-rise">
                        {restDay ? (
                            <div className="dr-rest">
                                ☕ {ru
                                    ? 'Сегодня выходной — учёба по желанию, штрафов нет 😌'
                                    : "Bugun dam olish kuni — o'qish ixtiyoriy, jarima yo'q 😌"}
                            </div>
                        ) : (
                            <>
                                <div className="dr-tp-head">
                                    <span className="dr-tp-title">{ru ? 'Сегодняшнее задание' : 'Bugungi vazifa'}</span>
                                    <span className={`dr-tp-badge ${status.unlocked ? 'is-open' : 'is-locked'}`}>
                                        {status.unlocked
                                            ? <>🎮 {ru ? 'Открыто' : 'Ochildi'}</>
                                            : <><Lock size={13} /> {completed}/{base}</>}
                                    </span>
                                </div>
                                <div className="dr-tp-bar"><span style={{ width: `${pct}%` }} /></div>
                                <div className="dr-tp-sub">
                                    {remaining > 0
                                        ? (ru
                                            ? <>Осталось <b>{remaining}</b> до разблокировки</>
                                            : <>Ochilishiga yana <b>{remaining}</b> ta dars</>)
                                        : (ru ? '✅ Норма выполнена!' : '✅ Norma bajarildi!')}
                                </div>
                                {enforcing && pendingMiss > 0 && penalty > 0 && (
                                    <div className="dr-warn">
                                        <AlertTriangle size={16} />
                                        <span>{ru
                                            ? <>⚠ Если не успеть сегодня: <b>−{fmtNum(pendingMiss * penalty)} баллов</b></>
                                            : <>⚠ Bugun tugamasa: <b>−{fmtNum(pendingMiss * penalty)} ball</b></>}</span>
                                    </div>
                                )}
                                <button className="dr-tp-cta" onClick={startNextLesson}>
                                    <BookOpen size={17} />
                                    {status.unlocked
                                        ? (ru ? 'Продолжить обучение' : "O'qishni davom ettirish")
                                        : (ru ? 'Начать следующий урок' : "Keyingi darsni boshlash")}
                                    <ArrowRight size={17} />
                                </button>
                                {nextLesson?.title && <div className="dr-tp-next">{nextLesson.title}</div>}
                            </>
                        )}
                    </div>
                )}

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

                {chrome && (
                    <div className="dr-mystatus dr-rise">
                        <div className="dr-ms-head">📊 {ru ? 'Моя статистика' : 'Mening holatim'}</div>
                        <div className="dr-ms-tiles">
                            <div className="dr-ms-tile dr-ms-amber">
                                <div className="dr-ms-val">{currentDebt}</div>
                                <div className="dr-ms-lbl">{ru ? 'Текущий долг (уроков)' : 'Joriy qarz (dars)'}</div>
                            </div>
                            <div className="dr-ms-tile dr-ms-red">
                                <div className="dr-ms-val">−{fmtNum(totalFined)}</div>
                                <div className="dr-ms-lbl">{ru ? 'Всего штрафов (баллы)' : 'Jami jarima (ball)'}</div>
                            </div>
                            <div className="dr-ms-tile dr-ms-violet">
                                <div className="dr-ms-val">{penalties.length}</div>
                                <div className="dr-ms-lbl">{ru ? 'Дней со штрафом' : 'Jarimali kunlar'}</div>
                            </div>
                            <div className="dr-ms-tile dr-ms-green">
                                <div className="dr-ms-val">🔥 {streakLen}</div>
                                <div className="dr-ms-lbl">{ru ? 'Серия (дней)' : 'Seriya (kun)'}</div>
                            </div>
                        </div>

                        {totalYield > 0 && (
                            <div className="dr-ms-yield">
                                {ru ? 'Бонус за серию получено: ' : 'Seriya bonusi olingan: '}
                                <b>+{fmtNum(totalYield)}</b> {ru ? 'баллов' : 'ball'}
                            </div>
                        )}

                        {penalties.length > 0 ? (
                            <div className="dr-ms-history">
                                <div className="dr-ms-hist-title">
                                    {ru ? 'История штрафов' : 'Jarimalar tarixi'}
                                    <span className="dr-ms-hist-sum">
                                        {totalMissed} {ru ? 'уроков пропущено' : 'dars o‘tkazildi'}
                                    </span>
                                </div>
                                {penalties.map((p, i) => (
                                    <div className="dr-ms-row" key={i}>
                                        <span className="dr-ms-date">{fmtDate(p.quota_date)}</span>
                                        <span className="dr-ms-miss">{p.lessons_missed} {ru ? 'уроков' : 'dars'}</span>
                                        <span className="dr-ms-amt">−{p.points_deducted} {ru ? 'б' : 'ball'}</span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="dr-ms-empty">
                                {ru ? 'Штрафов пока нет — так держать! 💪' : "Hali jarima yo'q — shunday davom et! 💪"}
                            </div>
                        )}
                    </div>
                )}

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

                        <label className="dr-row">
                            <span>{ru ? 'Бонус за норму' : 'Norma uchun bonus'}</span>
                            <input type="number" min="0" max="1000" step="5" className="dr-input dr-input--sm"
                                disabled={saving} defaultValue={cfg.completion_bonus}
                                onBlur={(e) => saveCfg({ completion_bonus: Number(e.target.value) })} />
                        </label>

                        <div className="dr-row dr-row--wrap">
                            <span>{ru ? 'Выходные (без штрафа)' : "Dam kunlari (jarimasiz)"}</span>
                            <div className="dr-days">
                                {DAY_LABELS[ru ? 'ru' : 'uz'].map((lbl, d) => (
                                    <button key={d} type="button" disabled={saving}
                                        className={`dr-day ${restSet.has(d) ? 'on' : ''}`}
                                        onClick={() => {
                                            const s = new Set(restSet);
                                            if (s.has(d)) s.delete(d); else s.add(d);
                                            saveCfg({ rest_days: [...s].sort((a, b) => a - b).join(',') });
                                        }}>{lbl}</button>
                                ))}
                            </div>
                        </div>

                        <div className="dr-admin-hint">
                            {ru ? 'Изменения применяются мгновенно для всех студентов.' : "O'zgarishlar barcha studentlarga darhol qo'llanadi."}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
