/* Statistics dashboard (Statistika) and session history (History) tabs. */

import { useState, useEffect } from 'react';
import { useHttp, headers } from '../../../api/search/base';
import { Flame } from 'lucide-react';
import { BASE, MODES } from './practiceUtils';
import { useTranslation } from '../../../i18n/useTranslation';


/* Small horizontal-bar list used by the Taqsimot panel. Keeps the
   render dumb so by_difficulty / by_part_of_speech share the same shape. */
function BreakdownBars({ items, total, palette }) {
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    const entries = Object.entries(items);
    if (!entries.length || total === 0) {
        return <div className="pr-breakdown-empty">{ru ? 'Нет' : "Yo'q"}</div>;
    }
    return (
        <div className="pr-breakdown-bars">
            {entries.map(([key, n], i) => {
                const pct = Math.round((n / total) * 100);
                return (
                    <div key={key} className="pr-breakdown-row">
                        <div className="pr-breakdown-row-head">
                            <span className="pr-breakdown-name">{key}</span>
                            <span className="pr-breakdown-count">
                                {n} <span className="pr-breakdown-pct">· {pct}%</span>
                            </span>
                        </div>
                        <div className="pr-breakdown-track">
                            <div
                                className="pr-breakdown-fill"
                                style={{
                                    width: `${pct}%`,
                                    background: palette[i % palette.length],
                                }}
                            />
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

export function Statistika() {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    const [stats, setStats]         = useState(null);
    const [needsReview, setNeedsReview] = useState({ items: [], total: 0 });
    const [breakdown, setBreakdown] = useState({ total: 0, by_difficulty: {}, by_part_of_speech: {} });
    const [loading, setLoading]     = useState(true);
    const [error, setError]         = useState('');

    useEffect(() => {
        let cancelled = false;
        setLoading(true);
        Promise.all([
            request(`${BASE}/stats`, 'GET', null, headers()),
            request(`${BASE}/needs-review?limit=10`, 'GET', null, headers()).catch(() => ({ items: [], total: 0 })),
            request(`${BASE}/breakdown`, 'GET', null, headers()).catch(() => ({ total: 0, by_difficulty: {}, by_part_of_speech: {} })),
        ])
            .then(([s, nr, br]) => {
                if (cancelled) return;
                setStats(s || null);
                setNeedsReview(nr || { items: [], total: 0 });
                setBreakdown(br || { total: 0, by_difficulty: {}, by_part_of_speech: {} });
                setError('');
            })
            .catch(() => {
                if (cancelled) return;
                setError(ru ? 'Не удалось загрузить статистику' : "Statistikani yuklab bo'lmadi");
            })
            .finally(() => { if (!cancelled) setLoading(false); });
        return () => { cancelled = true; };
    }, [request]);

    if (loading) {
        return <div className="pr-stats-loading">{ru ? 'Загрузка…' : 'Yuklanmoqda…'}</div>;
    }
    if (error || !stats) {
        return <div className="pr-error">{error || (ru ? 'Данные не найдены' : 'Maʼlumot topilmadi')}</div>;
    }

    const { streak, last_7_days, mode_breakdown, totals } = stats;

    // Scale the bar heights against the busiest day in the window so the
    // shape of the week reads correctly even on a light workload.
    const maxWordsDay = Math.max(1, ...last_7_days.map((d) => d.words));

    const dayLabel = (iso) => {
        const d = new Date(iso);
        // Local short weekday label — Uzbek shortcodes.
        const days = ru
            ? ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
            : ['Ya', 'Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh'];
        return days[d.getDay()];
    };

    return (
        <div className="pr-stats">
            {/* ── Streak hero ─────────────────────────────────────────── */}
            <div className={`pr-streak ${streak.current > 0 ? 'pr-streak--alive' : ''}`}>
                <div className="pr-streak-flame" aria-hidden="true"><Flame size={32} /></div>
                <div className="pr-streak-body">
                    <div className="pr-streak-num">{streak.current}</div>
                    <div className="pr-streak-lbl">
                        {streak.current === 0 ? (ru ? 'Начните сегодня' : 'Bugundan boshlang') : (ru ? 'дней подряд' : 'kunlik streak')}
                    </div>
                </div>
                <div className="pr-streak-meta">
                    <div>
                        <span className="pr-streak-meta-num">{streak.longest}</span>
                        <span className="pr-streak-meta-lbl">{ru ? 'рекорд' : 'eng uzun'}</span>
                    </div>
                    <div>
                        <span className="pr-streak-meta-num">
                            {streak.today_practised ? '✓' : '–'}
                        </span>
                        <span className="pr-streak-meta-lbl">{ru ? 'сегодня' : 'bugun'}</span>
                    </div>
                </div>
            </div>

            <div className="pr-row2">
            {/* ── 7-day activity bar chart ────────────────────────────── */}
            <section className="pr-section pr-week-sec">
                <h3 className="pr-section-title">{ru ? 'Последние 7 дней' : 'Oxirgi 7 kun'}</h3>
                <div className="pr-week">
                    {last_7_days.map((d) => {
                        const h = (d.words / maxWordsDay) * 100;
                        return (
                            <div key={d.date} className="pr-week-col">
                                <div className="pr-week-bar-wrap">
                                    <div
                                        className={`pr-week-bar ${d.words === 0 ? 'pr-week-bar--empty' : ''}`}
                                        style={{ height: `${Math.max(h, 4)}%` }}
                                        title={ru ? `${d.date}: ${d.words} слов · ${d.accuracy}%` : `${d.date}: ${d.words} so'z · ${d.accuracy}%`}
                                    />
                                </div>
                                <div className="pr-week-label">{dayLabel(d.date)}</div>
                                <div className="pr-week-num">{d.words || ''}</div>
                            </div>
                        );
                    })}
                </div>
            </section>

            {/* ── Mode-accuracy breakdown ─────────────────────────────── */}
            {mode_breakdown.length > 0 && (
                <section className="pr-section">
                    <h3 className="pr-section-title">{ru ? 'Точность по режимам' : "Rejimlar bo'yicha aniqlik"}</h3>
                    <div className="pr-modebars">
                        {mode_breakdown.map((m) => {
                            const meta = MODES.find((x) => x.key === m.mode);
                            return (
                                <div key={m.mode} className="pr-modebar">
                                    <div className="pr-modebar-head">
                                        <span className="pr-modebar-icon">{meta?.icon || '🔸'}</span>
                                        <span className="pr-modebar-name">{meta?.label || m.mode}</span>
                                        <span className="pr-modebar-pct">{m.accuracy}%</span>
                                    </div>
                                    <div className="pr-modebar-track">
                                        <div
                                            className="pr-modebar-fill"
                                            style={{ width: `${m.accuracy}%` }}
                                        />
                                    </div>
                                    <div className="pr-modebar-foot">
                                        {ru ? `${m.sessions} сессий · ${m.words} слов` : `${m.sessions} sessiya · ${m.words} so'z`}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </section>
            )}
            </div>

            {/* ── Totals card ─────────────────────────────────────────── */}
            <section className="pr-section">
                <h3 className="pr-section-title">{ru ? 'Итого' : 'Umumiy'}</h3>
                <div className="pr-totals">
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.words}</div>
                        <div className="pr-total-lbl">{ru ? 'всего слов' : "jami so'z"}</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.mastered}</div>
                        <div className="pr-total-lbl">{ru ? 'освоено' : "o'zlashtirilgan"}</div>
                        <div className="pr-total-sub">{totals.mastery_pct}%</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.sessions}</div>
                        <div className="pr-total-lbl">{ru ? 'сессий' : 'sessiya'}</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.drilled}</div>
                        <div className="pr-total-lbl">{ru ? 'практик' : 'mashq'}</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.accuracy}%</div>
                        <div className="pr-total-lbl">{ru ? 'средняя точность' : "o'rtacha aniqlik"}</div>
                    </div>
                </div>
            </section>

            {/* ── Taqsimot — by-difficulty + by-PoS ─────────────────── */}
            {breakdown.total > 0 && (
                <section className="pr-section">
                    <h3 className="pr-section-title">{ru ? 'Распределение' : 'Taqsimot'}</h3>
                    <div className="pr-breakdown">
                        <div className="pr-breakdown-col">
                            <div className="pr-breakdown-label">{ru ? 'Уровень' : 'Daraja'}</div>
                            <BreakdownBars
                                items={breakdown.by_difficulty}
                                total={breakdown.total}
                                palette={['#10b981', '#6c5ce7', '#f43f5e', '#0d9488', '#475569']}
                            />
                        </div>
                        <div className="pr-breakdown-col">
                            <div className="pr-breakdown-label">{ru ? 'Часть речи' : "So'z turi"}</div>
                            <BreakdownBars
                                items={breakdown.by_part_of_speech}
                                total={breakdown.total}
                                palette={['#6c5ce7', '#0d9488', '#f59e0b', '#f43f5e', '#475569']}
                            />
                        </div>
                    </div>
                </section>
            )}

            {/* ── Mashq qilingani yaxshi ── top-N words to study next ──
                Order matches the backend's ladder: never-reviewed first,
                then struggling, then long-time-no-see. */}
            {needsReview.items.length > 0 && (
                <section className="pr-section">
                    <div className="pr-section-head">
                        <h3 className="pr-section-title">{ru ? 'Стоит повторить' : 'Mashq qilingani yaxshi'}</h3>
                        {needsReview.total > needsReview.items.length && (
                            <span className="pr-section-more">
                                {ru ? `ещё ${needsReview.total - needsReview.items.length}` : `yana ${needsReview.total - needsReview.items.length}`}
                            </span>
                        )}
                    </div>
                    <div className="pr-needs">
                        {needsReview.items.map((w) => {
                            let tag, tagCls;
                            if (w.review_count === 0) {
                                tag = ru ? 'Новое' : 'Yangi'; tagCls = 'new';
                            } else if (w.accuracy !== null && w.accuracy < 70) {
                                tag = `${w.accuracy}%`; tagCls = 'low';
                            } else {
                                tag = ru ? 'Старое' : 'Eski'; tagCls = 'stale';
                            }
                            return (
                                <div key={w.id} className="pr-needs-row">
                                    <strong className="pr-needs-word">{w.word}</strong>
                                    {w.context && (
                                        <span className="pr-needs-ctx">{w.context}</span>
                                    )}
                                    <span className={`pr-needs-tag pr-needs-tag--${tagCls}`}>{tag}</span>
                                </div>
                            );
                        })}
                    </div>
                </section>
            )}
        </div>
    );
}


/* ═══════════════════════════════════════════════════════════════════════
   HISTORY — drill-results sub-tab with by-date / by-month / averages
   ═══════════════════════════════════════════════════════════════════════ */

function formatDateShort(iso, ru) {
    // "2026-06-10" → "10 Iyn"
    const months = ru
        ? ['янв', 'фев', 'мар', 'апр', 'мая', 'июн',
           'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
        : ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyn',
           'Iyl', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek'];
    const d = new Date(iso + 'T00:00:00');
    return `${d.getDate()} ${months[d.getMonth()]}`;
}

function formatMonth(key, ru) {
    // "2026-06" → "Iyun 2026"
    const months = ru
        ? ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
           'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
        : ['Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun',
           'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr'];
    const [y, m] = key.split('-');
    return `${months[Number(m) - 1]} ${y}`;
}

function formatDateTime(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    const pad = (n) => String(n).padStart(2, '0');
    return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function formatDuration(seconds, ru) {
    if (seconds == null) return '—';
    const uS = ru ? 'с' : 's';
    const uM = ru ? 'м' : 'm';
    if (seconds < 60) return `${seconds}${uS}`;
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return s ? `${m}${uM} ${s}${uS}` : `${m}${uM}`;
}

function Sparkline({ points, accessor = (d) => d.words, ariaLabel }) {
    // Compact inline SVG sparkline. Width is intrinsic via viewBox.
    if (!points.length) return null;
    const W = 600, H = 60, PAD = 4;
    const max = Math.max(1, ...points.map(accessor));
    const step = (W - PAD * 2) / Math.max(1, points.length - 1);
    const path = points
        .map((p, i) => {
            const x = PAD + i * step;
            const y = H - PAD - (accessor(p) / max) * (H - PAD * 2);
            return `${i === 0 ? 'M' : 'L'}${x.toFixed(2)},${y.toFixed(2)}`;
        })
        .join(' ');
    const area = `${path} L${PAD + (points.length - 1) * step},${H - PAD} L${PAD},${H - PAD} Z`;
    return (
        <svg
            viewBox={`0 0 ${W} ${H}`}
            className="pr-spark"
            preserveAspectRatio="none"
            aria-label={ariaLabel || ''}
        >
            <path d={area} className="pr-spark-fill" />
            <path d={path} className="pr-spark-line" />
        </svg>
    );
}

function PeriodBars({ points, accessor, labelFor }) {
    // Horizontal bars — one per period bucket. Picks the busiest bucket as
    // the 100% reference so quiet weeks still register visually.
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    const max = Math.max(1, ...points.map(accessor));
    return (
        <div className="pr-period">
            {points.map((p, i) => {
                const v = accessor(p);
                const w = (v / max) * 100;
                return (
                    <div key={i} className="pr-period-row">
                        <div className="pr-period-label">{labelFor(p)}</div>
                        <div className="pr-period-track">
                            <div
                                className={`pr-period-fill ${v === 0 ? 'pr-period-fill--empty' : ''}`}
                                style={{ width: `${Math.max(w, v > 0 ? 4 : 0)}%` }}
                            />
                        </div>
                        <div className="pr-period-val">
                            <span className="pr-period-val-num">{p.sessions}</span>
                            <span className="pr-period-val-sub">{ru ? `${p.words || 0} слов · ${p.accuracy || 0}%` : `${p.words || 0} so'z · ${p.accuracy || 0}%`}</span>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

export function History() {
    const { request } = useHttp();
    const { lang } = useTranslation();
    const ru = lang === 'ru';
    const [data, setData]     = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError]   = useState('');
    const [grain, setGrain]   = useState('day');   // 'day' | 'month'
    const [expanded, setExpanded] = useState(false);

    useEffect(() => {
        let cancelled = false;
        setLoading(true);
        request(`${BASE}/sessions-overview`, 'GET', null, headers())
            .then((d) => {
                if (cancelled) return;
                setData(d);
                setError('');
            })
            .catch(() => {
                if (cancelled) return;
                setError(ru ? 'Не удалось загрузить историю' : "Tarixni yuklab bo'lmadi");
            })
            .finally(() => { if (!cancelled) setLoading(false); });
        return () => { cancelled = true; };
    }, [request]);

    if (loading) return <div className="pr-stats-loading">{ru ? 'Загрузка…' : 'Yuklanmoqda…'}</div>;
    if (error || !data) return <div className="pr-error">{error || (ru ? 'Данные не найдены' : 'Maʼlumot topilmadi')}</div>;

    const { totals, averages, by_date, by_month, recent } = data;

    // For the by-day bars/sparkline we trim leading empty days so the chart
    // doesn't always start with a wall of zeros. We keep at least the last 14.
    const trimmedDays = (() => {
        const firstActive = by_date.findIndex((d) => d.sessions > 0);
        if (firstActive === -1) return by_date.slice(-14);
        const start = Math.min(firstActive, by_date.length - 14);
        return by_date.slice(Math.max(0, start));
    })();

    const visibleRecent = expanded ? recent : recent.slice(0, 5);

    return (
        <div className="pr-hist">
            {/* ── Averages row ────────────────────────────────────────── */}
            <section className="pr-section">
                <h3 className="pr-section-title">{ru ? 'Средние показатели' : "O'rtacha ko'rsatkichlar"}</h3>
                <div className="pr-avg-grid">
                    <div className="pr-avg">
                        <div className="pr-avg-num">{averages.per_session_accuracy}%</div>
                        <div className="pr-avg-lbl">{ru ? 'средняя точность' : "o'rtacha aniqlik"}</div>
                    </div>
                    <div className="pr-avg">
                        <div className="pr-avg-num">{averages.per_session_words}</div>
                        <div className="pr-avg-lbl">{ru ? 'слов / практика' : "so'z / mashq"}</div>
                    </div>
                    <div className="pr-avg">
                        <div className="pr-avg-num">
                            {averages.per_session_minutes || '—'}
                            {averages.per_session_minutes ? <span className="pr-avg-unit">{ru ? 'м' : 'm'}</span> : null}
                        </div>
                        <div className="pr-avg-lbl">{ru ? 'время / практика' : 'vaqt / mashq'}</div>
                    </div>
                    <div className="pr-avg">
                        <div className="pr-avg-num">{averages.sessions_per_week}</div>
                        <div className="pr-avg-lbl">{ru ? 'практик / неделя' : 'mashq / hafta'}</div>
                    </div>
                    <div className="pr-avg">
                        <div className="pr-avg-num">{averages.active_days_in_window}</div>
                        <div className="pr-avg-lbl">{ru ? `активных дней (${data.window.days}д)` : `faol kun (${data.window.days}d)`}</div>
                    </div>
                </div>
            </section>

            {/* ── Sparkline of activity ───────────────────────────────── */}
            {trimmedDays.length > 1 && (
                <section className="pr-section">
                    <h3 className="pr-section-title">{ru ? 'Динамика активности' : 'Faollik dinamikasi'}</h3>
                    <Sparkline points={trimmedDays} ariaLabel={ru ? 'Дневной объём слов' : "Kunlik so'z hajmi"} />
                    <div className="pr-spark-foot">
                        <span>{formatDateShort(trimmedDays[0].date, ru)}</span>
                        <span>{formatDateShort(trimmedDays[trimmedDays.length - 1].date, ru)}</span>
                    </div>
                </section>
            )}

            {/* ── Grain toggle + period bars ──────────────────────────── */}
            <section className="pr-section">
                <div className="pr-section-head">
                    <h3 className="pr-section-title">
                        {grain === 'day' ? (ru ? 'Результаты по дням' : "Kunlik natijalar") : (ru ? 'Результаты по месяцам' : "Oylik natijalar")}
                    </h3>
                    <div className="pr-grain">
                        <button
                            className={`pr-grain-btn ${grain === 'day' ? 'active' : ''}`}
                            onClick={() => setGrain('day')}
                        >
                            {ru ? 'День' : 'Kun'}
                        </button>
                        <button
                            className={`pr-grain-btn ${grain === 'month' ? 'active' : ''}`}
                            onClick={() => setGrain('month')}
                        >
                            {ru ? 'Месяц' : 'Oy'}
                        </button>
                    </div>
                </div>
                {grain === 'day' ? (
                    <PeriodBars
                        points={[...trimmedDays].reverse()}
                        accessor={(d) => d.sessions}
                        labelFor={(d) => formatDateShort(d.date, ru)}
                    />
                ) : (
                    <PeriodBars
                        points={[...by_month].reverse()}
                        accessor={(d) => d.sessions}
                        labelFor={(d) => formatMonth(d.month, ru)}
                    />
                )}
            </section>

            {/* ── Lifetime totals ──────────────────────────────────────── */}
            <section className="pr-section">
                <h3 className="pr-section-title">{ru ? 'Общий итог' : 'Umumiy hisob'}</h3>
                <div className="pr-totals">
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.sessions}</div>
                        <div className="pr-total-lbl">{ru ? 'практик' : 'mashqlar'}</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.words}</div>
                        <div className="pr-total-lbl">{ru ? 'всего слов' : "jami so'z"}</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.correct}</div>
                        <div className="pr-total-lbl">{ru ? 'верных ответов' : "to'g'ri javob"}</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.accuracy}%</div>
                        <div className="pr-total-lbl">{ru ? 'точность' : 'aniqlik'}</div>
                    </div>
                    <div className="pr-total">
                        <div className="pr-total-num">{totals.active_days}</div>
                        <div className="pr-total-lbl">{ru ? 'активных дней' : 'faol kun'}</div>
                    </div>
                    {totals.minutes > 0 && (
                        <div className="pr-total">
                            <div className="pr-total-num">
                                {totals.minutes >= 60
                                    ? (ru
                                        ? `${Math.floor(totals.minutes / 60)}ч ${totals.minutes % 60}м`
                                        : `${Math.floor(totals.minutes / 60)}s ${totals.minutes % 60}d`)
                                    : (ru ? `${totals.minutes}м` : `${totals.minutes}d`)}
                            </div>
                            <div className="pr-total-lbl">{ru ? 'всего времени' : 'jami vaqt'}</div>
                        </div>
                    )}
                </div>
            </section>

            {/* ── Recent sessions list ─────────────────────────────────── */}
            {recent.length > 0 && (
                <section className="pr-section">
                    <div className="pr-section-head">
                        <h3 className="pr-section-title">{ru ? 'Список практик' : "Mashqlar ro'yxati"}</h3>
                        {recent.length > 5 && (
                            <button
                                className="pr-section-more pr-section-more--btn"
                                onClick={() => setExpanded((v) => !v)}
                            >
                                {expanded ? (ru ? 'Меньше' : 'Kamroq') : (ru ? `Ещё ${recent.length - 5}` : `Yana ${recent.length - 5} ta`)}
                            </button>
                        )}
                    </div>
                    <div className="pr-sess-list">
                        {visibleRecent.map((s) => {
                            const meta = MODES.find((m) => m.key === s.mode);
                            const pct = s.accuracy;
                            const cls = pct >= 80 ? 'ok' : pct >= 50 ? 'mid' : 'bad';
                            return (
                                <div key={s.id} className="pr-sess-row">
                                    <div className="pr-sess-mode">
                                        <span className="pr-sess-mode-icon" aria-hidden>
                                            {meta?.icon || '🔸'}
                                        </span>
                                        <span className="pr-sess-mode-name">
                                            {meta?.label || s.mode}
                                        </span>
                                    </div>
                                    <div className="pr-sess-when">
                                        {formatDateTime(s.completed_at || s.started_at)}
                                    </div>
                                    <div className="pr-sess-dur">
                                        {formatDuration(s.duration_seconds, ru)}
                                    </div>
                                    <div className="pr-sess-score">
                                        {s.correct}/{s.total_words}
                                    </div>
                                    <div className={`pr-sess-pct pr-sess-pct--${cls}`}>
                                        {pct}%
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </section>
            )}
        </div>
    );
}
