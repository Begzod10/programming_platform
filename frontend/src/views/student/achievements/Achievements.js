import { useEffect, useMemo, useState } from 'react';
import { API_URL, headers, resolveImageUrl } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import AppHeader from '../../../components/appheader/AppHeader';
import './Achievements.css';
import {
    Trophy, Award, Lock, Sparkles, Target, TrendingUp, Flame,
    Search, X, CheckCircle2, BookOpen, FolderGit2, BookMarked, Star,
} from 'lucide-react';

const prefersReduced = () =>
    typeof window !== 'undefined' && window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const normaliseCategory = (raw) => (raw ? raw.toLowerCase() : 'general');

const CAT_META = {
    learning:   { Icon: BookOpen },
    projects:   { Icon: FolderGit2 },
    vocabulary: { Icon: BookMarked },
    points:     { Icon: Star },
    general:    { Icon: Trophy },
};

/* Animated header ring. */
function HeaderRing({ pct }) {
    const r = 30, circ = 2 * Math.PI * r;
    const [off, setOff] = useState(circ);
    useEffect(() => {
        if (prefersReduced()) { setOff(circ - circ * pct / 100); return; }
        const id = setTimeout(() => setOff(circ - circ * pct / 100), 250);
        return () => clearTimeout(id);
    }, [pct, circ]);
    return (
        <div className="ach-ring">
            <svg width="72" height="72" viewBox="0 0 72 72">
                <circle cx="36" cy="36" r={r} fill="none" stroke="rgba(255,255,255,.08)" strokeWidth="7" />
                <circle cx="36" cy="36" r={r} fill="none" stroke="url(#achGrad)" strokeWidth="7" strokeLinecap="round"
                    strokeDasharray={circ} strokeDashoffset={off} transform="rotate(-90 36 36)"
                    style={{ transition: 'stroke-dashoffset 1.1s cubic-bezier(.2,.75,.25,1)', filter: 'drop-shadow(0 0 5px rgba(251,191,36,.5))' }} />
                <defs>
                    <linearGradient id="achGrad" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0" stopColor="#fde68a" /><stop offset="1" stopColor="#fbbf24" />
                    </linearGradient>
                </defs>
            </svg>
            <span className="ach-ring-pct">{pct}%</span>
        </div>
    );
}

function StatTile({ icon: Icon, value, label, tone }) {
    return (
        <div className={`ach-stat ach-stat--${tone}`}>
            <span className="ach-stat-ico"><Icon size={18} /></span>
            <div>
                <div className="ach-stat-val">{value}</div>
                <div className="ach-stat-lbl">{label}</div>
            </div>
        </div>
    );
}

export default function Achievements() {
    const { t, lang } = useTranslation();
    const ru = lang === 'ru';

    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [cat, setCat] = useState('all');
    const [sort, setSort] = useState('recent');
    const [query, setQuery] = useState('');

    useEffect(() => {
        setLoading(true); setError(null);
        fetch(`${API_URL}v1/achievements/my-progress`, { headers: headers() })
            .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
            .then(data => setItems(Array.isArray(data) ? data : []))
            .catch(e => setError(e.message))
            .finally(() => setLoading(false));
    }, []);

    const earnedList = useMemo(() => items.filter(i => i.is_earned), [items]);
    const lockedList = useMemo(() => items.filter(i => !i.is_earned), [items]);
    const totalAll = items.length;
    const earnedCount = earnedList.length;
    const pctAll = totalAll ? Math.round(earnedCount / totalAll * 100) : 0;
    const totalPoints = earnedList.reduce((s, i) => s + (i.points_reward || 0), 0);

    const closest = useMemo(() => {
        const withProg = lockedList.filter(p => (p.progress ?? 0) > 0);
        if (!withProg.length) return null;
        return [...withProg].sort((a, b) => (b.progress ?? 0) - (a.progress ?? 0))[0];
    }, [lockedList]);

    // category chips with live counts
    const CATS = useMemo(() => {
        const base = [
            { key: 'all',        label: ru ? 'Все' : 'Hammasi' },
            { key: 'learning',   label: ru ? 'Учёба' : "O'qish" },
            { key: 'projects',   label: ru ? 'Проекты' : 'Loyihalar' },
            { key: 'vocabulary', label: ru ? 'Словарь' : "Lug'at" },
            { key: 'points',     label: ru ? 'Баллы' : 'Ballar' },
        ];
        const count = (k) => k === 'all' ? totalAll : items.filter(i => normaliseCategory(i.category) === k).length;
        return base.map(c => ({ ...c, count: count(c.key) })).filter(c => c.key === 'all' || c.count > 0);
    }, [items, totalAll, ru]);

    const SORTS = [
        { key: 'recent',   label: ru ? 'Сначала полученные' : 'Avval olinganlar' },
        { key: 'points',   label: ru ? 'По баллам' : "Ball bo'yicha" },
        { key: 'progress', label: ru ? 'По прогрессу' : 'Jarayon bo\'yicha' },
    ];

    const matchesQuery = (p) => {
        const q = query.trim().toLowerCase();
        if (!q) return true;
        return (p.name || '').toLowerCase().includes(q) || (p.description || '').toLowerCase().includes(q);
    };
    const inCat = (p) => cat === 'all' || normaliseCategory(p.category) === cat;
    const sortList = (list) => {
        const arr = [...list];
        if (sort === 'points') arr.sort((a, b) => (b.points_reward || 0) - (a.points_reward || 0));
        else if (sort === 'progress') arr.sort((a, b) => (b.progress ?? 0) - (a.progress ?? 0));
        else arr.sort((a, b) => Number(b.is_earned) - Number(a.is_earned) || (b.progress ?? 0) - (a.progress ?? 0));
        return arr;
    };

    const sectioned = cat === 'all' && !query.trim();
    const catEarned = sortList(earnedList.filter(inCat).filter(matchesQuery));
    const catLocked = sortList(lockedList.filter(inCat).filter(matchesQuery));
    const flat = sortList(items.filter(inCat).filter(matchesQuery));

    const renderCard = (item, i) => {
        const isEarned = item.is_earned;
        const pct = Math.min(100, Math.max(0, Math.round(item.progress ?? 0)));
        const emoji = item.icon;
        const badge = item.badge_image_url ? resolveImageUrl(item.badge_image_url) : '';
        return (
            <div key={item.achievement_id}
                className={`ach-card ${isEarned ? 'ach-card--on' : 'ach-card--off'}`}
                style={prefersReduced() ? undefined : { animationDelay: `${Math.min(i, 12) * 0.05}s` }}>
                {isEarned && <span className="ach-ribbon"><CheckCircle2 size={12} /> {ru ? 'Получено' : 'Olingan'}</span>}
                <div className="ach-card-glow" aria-hidden="true" />

                <div className={`ach-badge ${isEarned ? '' : 'ach-badge--locked'}`}>
                    {isEarned && <span className="ach-badge-shine" aria-hidden="true" />}
                    {isEarned
                        ? (emoji
                            ? <span className="ach-badge-emoji">{emoji}</span>
                            : badge
                                ? <img src={badge} alt="" onError={e => { e.target.style.display = 'none'; }} />
                                : <Trophy size={32} />)
                        : <Lock size={26} />}
                </div>

                <div className="ach-name">{item.name}</div>
                <div className="ach-desc">{item.description}</div>

                <div className="ach-meta">
                    <span className="ach-pts"><Sparkles size={12} /> +{item.points_reward} {t('rating.pts')}</span>
                </div>

                {!isEarned && (
                    <div className="ach-prog">
                        <div className="ach-prog-head">
                            <span>{ru ? 'Прогресс' : 'Jarayon'}</span>
                            <span className="ach-prog-frac">{item.current_value} / {item.criteria_value}</span>
                        </div>
                        <div className="ach-prog-track"><div className="ach-prog-fill" style={{ width: `${pct}%` }} /></div>
                        <span className="ach-prog-pct">{pct}%</span>
                    </div>
                )}
            </div>
        );
    };

    const renderGrid = (list, off = 0) => <div className="ach-grid">{list.map((it, i) => renderCard(it, i + off))}</div>;

    return (
        <div className="ach-page">
            <AppHeader />

            <div className="ach-shell">
                {/* ── header ── */}
                <div className="ach-head">
                    <div className="ach-head-l">
                        <span className="ach-head-ico"><Trophy size={24} /></span>
                        <div>
                            <h1>{ru ? 'Достижения' : 'Yutuqlar'}</h1>
                            <p>{ru
                                ? <>Получено <b>{earnedCount}</b> из <b>{totalAll}</b></>
                                : <><b>{totalAll}</b> tadan <b>{earnedCount}</b> ta qo'lga kiritildi</>}</p>
                        </div>
                    </div>
                    <HeaderRing pct={pctAll} />
                </div>

                {/* ── stats strip ── */}
                {!loading && !error && totalAll > 0 && (
                    <div className="ach-stats">
                        <StatTile icon={Award} tone="amber" value={earnedCount} label={ru ? 'Получено' : 'Qo\'lga kiritildi'} />
                        <StatTile icon={Sparkles} tone="green" value={totalPoints.toLocaleString('ru-RU').replace(/,/g, ' ')} label={ru ? 'Баллов' : 'Yig\'ilgan ball'} />
                        <StatTile icon={Target} tone="cyan" value={`${pctAll}%`} label={ru ? 'Завершено' : 'Yakunlandi'} />
                        <StatTile icon={TrendingUp} tone="violet" value={closest ? `${Math.round(closest.progress ?? 0)}%` : '—'} label={ru ? 'Ближайшее' : 'Eng yaqini'} />
                    </div>
                )}

                {error && <div className="ach-alert">⚠ {ru ? 'Ошибка загрузки' : 'Yuklashda xatolik'}: {error}</div>}

                {/* ── controls ── */}
                {!loading && !error && totalAll > 0 && (
                    <div className="ach-controls">
                        <div className="ach-chips">
                            {CATS.map(c => {
                                const M = CAT_META[c.key] || CAT_META.general;
                                return (
                                    <button key={c.key} className={`ach-chip ${cat === c.key ? 'ach-chip--active' : ''}`} onClick={() => setCat(c.key)}>
                                        {c.key !== 'all' && <M.Icon size={14} />}
                                        {c.label}<span className="ach-chip-count">{c.count}</span>
                                    </button>
                                );
                            })}
                        </div>
                        <div className="ach-controls-r">
                            <div className="ach-search">
                                <Search size={15} className="ach-search-ico" aria-hidden="true" />
                                <input type="text" value={query} onChange={e => setQuery(e.target.value)}
                                    placeholder={ru ? 'Поиск…' : 'Qidirish…'} />
                                {query && <button className="ach-search-x" onClick={() => setQuery('')} aria-label="clear"><X size={13} /></button>}
                            </div>
                            <select className="ach-sort" value={sort} onChange={e => setSort(e.target.value)} aria-label={ru ? 'Сортировка' : 'Saralash'}>
                                {SORTS.map(s => <option key={s.key} value={s.key}>{s.label}</option>)}
                            </select>
                        </div>
                    </div>
                )}

                {loading ? (
                    <div className="ach-grid">
                        {[0, 1, 2, 3, 4, 5].map(i => <div key={i} className="ach-skel" style={{ animationDelay: `${i * 0.06}s` }} />)}
                    </div>
                ) : error ? (
                    <div className="ach-state">
                        <span className="ach-state-ico">⚠</span>
                        <p>{ru ? 'Не удалось загрузить достижения.' : "Yutuqlarni yuklab bo'lmadi."}</p>
                    </div>
                ) : totalAll === 0 ? (
                    <div className="ach-state">
                        <Trophy size={44} className="ach-state-trophy" />
                        <p className="ach-state-title">{ru ? 'Пока нет достижений' : "Hali yutuqlar yo'q"}</p>
                        <p className="ach-state-sub">{ru ? 'Продолжайте — награды близко!' : "Davom eting — mukofotlar yaqin!"}</p>
                    </div>
                ) : sectioned ? (
                    <>
                        {closest && (
                            <div className="ach-spotlight">
                                <div className="ach-spot-glow" aria-hidden="true" />
                                <div className="ach-spot-badge">
                                    {closest.icon
                                        ? <span className="ach-badge-emoji">{closest.icon}</span>
                                        : closest.badge_image_url
                                            ? <img src={resolveImageUrl(closest.badge_image_url)} alt="" onError={e => { e.target.style.display = 'none'; }} />
                                            : <Trophy size={40} />}
                                </div>
                                <div className="ach-spot-body">
                                    <span className="ach-spot-tag"><Flame size={13} /> {ru ? 'Почти готово!' : 'Deyarli tayyor!'}</span>
                                    <div className="ach-spot-name">{closest.name}</div>
                                    <div className="ach-spot-desc">{closest.description}</div>
                                    <div className="ach-spot-prog">
                                        <div className="ach-prog-track"><div className="ach-prog-fill ach-prog-fill--violet" style={{ width: `${Math.min(100, Math.round(closest.progress ?? 0))}%` }} /></div>
                                        <span className="ach-spot-frac">{closest.current_value} / {closest.criteria_value}</span>
                                    </div>
                                    <div className="ach-spot-hint">
                                        {ru
                                            ? <>Осталось <b>{Math.max(0, (closest.criteria_value || 0) - (closest.current_value || 0))}</b> · <b>+{closest.points_reward}</b> {t('rating.pts')}</>
                                            : <>Yana <b>{Math.max(0, (closest.criteria_value || 0) - (closest.current_value || 0))}</b> ta qoldi · <b>+{closest.points_reward}</b> {t('rating.pts')}</>}
                                    </div>
                                </div>
                            </div>
                        )}

                        {catEarned.length > 0 && (
                            <section className="ach-section">
                                <div className="ach-section-title"><Award size={16} /> {ru ? 'Полученные' : "Qo'lga kiritilgan"} <span>{catEarned.length}</span></div>
                                {renderGrid(catEarned)}
                            </section>
                        )}
                        {catLocked.length > 0 && (
                            <section className="ach-section">
                                <div className="ach-section-title"><Lock size={15} /> {ru ? 'В процессе' : 'Jarayonda'} <span>{catLocked.length}</span></div>
                                {renderGrid(catLocked, catEarned.length)}
                            </section>
                        )}
                    </>
                ) : flat.length === 0 ? (
                    <div className="ach-state">
                        <Search size={40} className="ach-state-trophy" />
                        <p className="ach-state-title">{ru ? 'Ничего не найдено' : 'Hech narsa topilmadi'}</p>
                    </div>
                ) : (
                    renderGrid(flat)
                )}
            </div>
        </div>
    );
}
