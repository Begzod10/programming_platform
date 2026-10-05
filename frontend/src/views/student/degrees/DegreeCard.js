import { useState, useEffect, useMemo, useCallback } from 'react';
import './DegreeCard.css';
import { API_URL, useHttp, headers, resolveImageUrl } from '../../../api/search/base';
import axiosInstance from '../../../api/axiosInstance';
import { useTranslation } from '../../../i18n/useTranslation';
import AppHeader from '../../../components/appheader/AppHeader';
import {
    GraduationCap, Trophy, Lock, Download, Sparkles, CheckCircle2, Award, Loader2,
    Search, X, Target, TrendingUp, Flame,
} from 'lucide-react';

const prefersReduced = () =>
    typeof window !== 'undefined' && window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* Animated progress ring for the header. */
function HeaderRing({ pct }) {
    const r = 30, circ = 2 * Math.PI * r;
    const [off, setOff] = useState(circ);
    useEffect(() => {
        if (prefersReduced()) { setOff(circ - circ * pct / 100); return; }
        const id = setTimeout(() => setOff(circ - circ * pct / 100), 250);
        return () => clearTimeout(id);
    }, [pct, circ]);
    return (
        <div className="dg-ring">
            <svg width="72" height="72" viewBox="0 0 72 72">
                <circle cx="36" cy="36" r={r} fill="none" stroke="rgba(255,255,255,.08)" strokeWidth="7" />
                <circle cx="36" cy="36" r={r} fill="none" stroke="url(#dgGrad)" strokeWidth="7" strokeLinecap="round"
                    strokeDasharray={circ} strokeDashoffset={off}
                    transform="rotate(-90 36 36)"
                    style={{ transition: 'stroke-dashoffset 1.1s cubic-bezier(.2,.75,.25,1)', filter: 'drop-shadow(0 0 5px rgba(34,211,238,.5))' }} />
                <defs>
                    <linearGradient id="dgGrad" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0" stopColor="#67e8f9" /><stop offset="1" stopColor="#22d3ee" />
                    </linearGradient>
                </defs>
            </svg>
            <span className="dg-ring-pct">{pct}%</span>
        </div>
    );
}

function StatTile({ icon: Icon, value, label, tone }) {
    return (
        <div className={`dg-stat dg-stat--${tone}`}>
            <span className="dg-stat-ico"><Icon size={18} /></span>
            <div className="dg-stat-body">
                <div className="dg-stat-val">{value}</div>
                <div className="dg-stat-lbl">{label}</div>
            </div>
        </div>
    );
}

const Degrees = () => {
    const { request } = useHttp();
    const { t, lang } = useTranslation();
    const ru = lang === 'ru';

    const [progress, setProgress] = useState([]);
    const [earned, setEarned] = useState([]);
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState(false);
    const [downloading, setDownloading] = useState(null);
    const [error, setError] = useState(null);

    // controls
    const [filter, setFilter] = useState('all');   // all | earned | progress
    const [sort, setSort] = useState('recent');     // recent | points | progress
    const [query, setQuery] = useState('');

    const fetchDegrees = useCallback(() => {
        setLoading(true);
        setLoadError(false);
        Promise.all([
            request(`${API_URL}v1/achievements/my-progress`, 'GET', null, headers()),
            request(`${API_URL}v1/achievements/my`, 'GET', null, headers()),
        ])
        .then(([progressData, myData]) => {
            setProgress(Array.isArray(progressData) ? progressData : []);
            setEarned(Array.isArray(myData) ? myData : []);
        })
        .catch(() => setLoadError(true))
        .finally(() => setLoading(false));
    }, [request]);

    useEffect(() => { fetchDegrees(); }, [fetchDegrees]);

    const earnedMap = useMemo(() => new Map(earned.map(e => [e.achievement_name, e])), [earned]);

    const handleDownload = async (item) => {
        if (!item.is_earned) return;
        const earnedItem = earnedMap.get(item.name);
        const courseId = earnedItem?.course_id ?? earnedItem?.courseId ?? earnedItem?.course ?? item.course_id ?? null;

        setDownloading(item.achievement_id);
        setError(null);
        const downloadUrl = courseId
            ? `${API_URL}v1/achievements/course/${courseId}/download`
            : `${API_URL}v1/achievements/${item.achievement_id}/download`;
        try {
            if (courseId) {
                await request(`${API_URL}v1/achievements/check-and-earn-certificate?course_id=${courseId}`, 'POST', null, headers()).catch(() => {});
            }
            const res = await axiosInstance.get(downloadUrl, { responseType: 'blob', headers: { Accept: 'application/pdf' } });
            const url = URL.createObjectURL(res.data);
            const a = document.createElement('a');
            a.href = url; a.download = `${item.name || 'certificate'}.pdf`;
            document.body.appendChild(a); a.click(); a.remove();
            URL.revokeObjectURL(url);
        } catch (e) {
            console.error(e);
            setError(ru ? 'Не удалось скачать сертификат. Попробуйте позже.' : "Sertifikatni yuklab bo'lmadi. Keyinroq urinib ko'ring.");
        } finally {
            setDownloading(null);
        }
    };

    const totalAll = progress.length;
    const earnedList = useMemo(() => progress.filter(p => p.is_earned), [progress]);
    const lockedList = useMemo(() => progress.filter(p => !p.is_earned), [progress]);
    const totalEarned = earnedList.length;
    const pctAll = totalAll ? Math.round(totalEarned / totalAll * 100) : 0;
    const pointsEarned = earnedList.reduce((s, p) => s + (p.points_reward || 0), 0);

    // closest-to-complete locked cert (for the spotlight)
    const closest = useMemo(() => {
        const withProg = lockedList.filter(p => (p.progress ?? 0) > 0);
        if (!withProg.length) return null;
        return [...withProg].sort((a, b) => (b.progress ?? 0) - (a.progress ?? 0))[0];
    }, [lockedList]);

    const earnedAtOf = (item) => {
        const e = earnedMap.get(item.name);
        return e?.earned_at ? new Date(e.earned_at).getTime() : 0;
    };
    const sortList = useCallback((list) => {
        const arr = [...list];
        if (sort === 'points') arr.sort((a, b) => (b.points_reward || 0) - (a.points_reward || 0));
        else if (sort === 'progress') arr.sort((a, b) => (b.progress ?? 0) - (a.progress ?? 0));
        else arr.sort((a, b) => (earnedAtOf(b) - earnedAtOf(a)) || ((b.progress ?? 0) - (a.progress ?? 0)));
        return arr;
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [sort, earnedMap]);

    const matchesQuery = (p) => {
        const q = query.trim().toLowerCase();
        if (!q) return true;
        return (p.name || '').toLowerCase().includes(q) || (p.description || '').toLowerCase().includes(q);
    };

    const FILTERS = [
        { key: 'all',      label: ru ? 'Все' : 'Hammasi',     count: totalAll },
        { key: 'earned',   label: ru ? 'Полученные' : 'Olingan', count: totalEarned },
        { key: 'progress', label: ru ? 'В процессе' : 'Jarayonda', count: lockedList.length },
    ];
    const SORTS = [
        { key: 'recent',   label: ru ? 'Сначала новые' : 'Avval yangilari' },
        { key: 'points',   label: ru ? 'По баллам' : 'Ball bo\'yicha' },
        { key: 'progress', label: ru ? 'По прогрессу' : 'Jarayon bo\'yicha' },
    ];

    const sectioned = filter === 'all' && !query.trim();
    const fmtDate = (d) => new Date(d).toLocaleDateString(ru ? 'ru-RU' : 'uz-UZ', { day: '2-digit', month: 'long', year: 'numeric' });

    const renderCard = (item, i) => {
        const isUnlocked = item.is_earned;
        const pct = Math.min(100, Math.round(item.progress ?? 0));
        const earnedItem = earnedMap.get(item.name);
        const badge = item.badge_image_url ? resolveImageUrl(item.badge_image_url) : '';
        return (
            <div key={item.achievement_id}
                className={`dg-card ${isUnlocked ? 'dg-card--on' : 'dg-card--off'}`}
                style={prefersReduced() ? undefined : { animationDelay: `${Math.min(i, 12) * 0.05}s` }}>
                {isUnlocked && <span className="dg-ribbon"><CheckCircle2 size={12} /> {ru ? 'Получен' : 'Olingan'}</span>}
                <div className="dg-card-glow" aria-hidden="true" />

                <div className={`dg-badge ${isUnlocked ? '' : 'dg-badge--locked'}`}>
                    {isUnlocked && <span className="dg-badge-shine" aria-hidden="true" />}
                    {isUnlocked
                        ? (badge
                            ? <img src={badge} alt="" onError={e => { e.target.style.display = 'none'; }} />
                            : <Trophy size={34} />)
                        : <Lock size={28} />}
                </div>

                <div className="dg-name">{item.name}</div>
                <div className="dg-desc">{item.description}</div>

                <div className="dg-meta">
                    <span className="dg-pts"><Sparkles size={12} /> +{item.points_reward} {t('rating.pts')}</span>
                    {isUnlocked && earnedItem?.earned_at && (
                        <span className="dg-date">{ru ? 'Выдан' : 'Berildi'}: {fmtDate(earnedItem.earned_at)}</span>
                    )}
                </div>

                {!isUnlocked && (
                    <div className="dg-prog">
                        <div className="dg-prog-head">
                            <span>{ru ? 'Прогресс' : 'Jarayon'}</span>
                            <span className="dg-prog-frac">{item.current_value} / {item.criteria_value}</span>
                        </div>
                        <div className="dg-prog-track"><div className="dg-prog-fill" style={{ width: `${pct}%` }} /></div>
                    </div>
                )}

                <div className="dg-foot">
                    {isUnlocked ? (
                        <button className="dg-dl" onClick={() => handleDownload(item)} disabled={downloading === item.achievement_id}>
                            {downloading === item.achievement_id
                                ? <><Loader2 size={15} className="dg-spin" /> {ru ? 'Генерация…' : 'Tayyorlanmoqda…'}</>
                                : <><Download size={15} /> {ru ? 'Скачать PDF' : 'PDF yuklab olish'}</>}
                        </button>
                    ) : (
                        <div className="dg-lockbadge"><Lock size={13} /> {pct}% {ru ? 'выполнено' : 'bajarildi'}</div>
                    )}
                </div>
            </div>
        );
    };

    const renderGrid = (list, offset = 0) => (
        <div className="dg-grid">{list.map((it, i) => renderCard(it, i + offset))}</div>
    );

    // filtered flat list (used when not sectioned)
    const flat = useMemo(() => {
        let base = filter === 'earned' ? earnedList : filter === 'progress' ? lockedList : progress;
        base = base.filter(matchesQuery);
        return sortList(base);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [filter, query, sortList, earnedList, lockedList, progress]);

    return (
        <div className="dg-page">
            <AppHeader />

            <div className="dg-shell">
                {/* ── header ── */}
                <div className="dg-head">
                    <div className="dg-head-l">
                        <span className="dg-head-ico"><GraduationCap size={24} /></span>
                        <div>
                            <h1>{ru ? 'Мои сертификаты' : 'Mening sertifikatlarim'}</h1>
                            <p>{ru
                                ? <>Получено <b>{totalEarned}</b> из <b>{totalAll}</b></>
                                : <><b>{totalAll}</b> tadan <b>{totalEarned}</b> ta olingan</>}</p>
                        </div>
                    </div>
                    <HeaderRing pct={pctAll} />
                </div>

                {/* ── stats strip ── */}
                {!loading && !loadError && totalAll > 0 && (
                    <div className="dg-stats">
                        <StatTile icon={Award} tone="green" value={totalEarned}
                            label={ru ? 'Получено' : 'Olingan'} />
                        <StatTile icon={Sparkles} tone="amber" value={pointsEarned.toLocaleString('ru-RU').replace(/,/g, ' ')}
                            label={ru ? 'Баллов заработано' : 'Yig\'ilgan ball'} />
                        <StatTile icon={Target} tone="cyan" value={`${pctAll}%`}
                            label={ru ? 'Завершено' : 'Yakunlandi'} />
                        <StatTile icon={TrendingUp} tone="violet"
                            value={closest ? `${Math.round(closest.progress ?? 0)}%` : '—'}
                            label={ru ? 'Ближайший' : 'Eng yaqini'} />
                    </div>
                )}

                {error && <div className="dg-alert">⚠ {error}</div>}

                {/* ── controls ── */}
                {!loading && !loadError && totalAll > 0 && (
                    <div className="dg-controls">
                        <div className="dg-chips">
                            {FILTERS.map(f => (
                                <button key={f.key} className={`dg-chip ${filter === f.key ? 'dg-chip--active' : ''}`}
                                    onClick={() => setFilter(f.key)}>
                                    {f.label}<span className="dg-chip-count">{f.count}</span>
                                </button>
                            ))}
                        </div>
                        <div className="dg-controls-r">
                            <div className="dg-search">
                                <Search size={15} className="dg-search-ico" aria-hidden="true" />
                                <input type="text" value={query} onChange={e => setQuery(e.target.value)}
                                    placeholder={ru ? 'Поиск…' : 'Qidirish…'} />
                                {query && <button className="dg-search-x" onClick={() => setQuery('')} aria-label="clear"><X size={13} /></button>}
                            </div>
                            <select className="dg-sort" value={sort} onChange={e => setSort(e.target.value)}
                                aria-label={ru ? 'Сортировка' : 'Saralash'}>
                                {SORTS.map(s => <option key={s.key} value={s.key}>{s.label}</option>)}
                            </select>
                        </div>
                    </div>
                )}

                {loading ? (
                    <div className="dg-grid">
                        {[0, 1, 2, 3, 4, 5].map(i => <div key={i} className="dg-skel" style={{ animationDelay: `${i * 0.06}s` }} />)}
                    </div>
                ) : loadError ? (
                    <div className="dg-state">
                        <span className="dg-state-ico">⚠</span>
                        <p>{ru ? 'Не удалось загрузить сертификаты.' : "Sertifikatlarni yuklab bo'lmadi."}</p>
                        <button className="dg-retry" onClick={fetchDegrees}>{t('rating.retry')}</button>
                    </div>
                ) : progress.length === 0 ? (
                    <div className="dg-state">
                        <GraduationCap size={44} className="dg-state-trophy" />
                        <p className="dg-state-title">{ru ? 'Пока нет доступных сертификатов' : "Hozircha sertifikatlar yo'q"}</p>
                    </div>
                ) : sectioned ? (
                    <>
                        {/* ── spotlight: closest certificate ── */}
                        {closest && (
                            <div className="dg-spotlight">
                                <div className="dg-spot-glow" aria-hidden="true" />
                                <div className="dg-spot-badge">
                                    {closest.badge_image_url
                                        ? <img src={resolveImageUrl(closest.badge_image_url)} alt="" onError={e => { e.target.style.display = 'none'; }} />
                                        : <Trophy size={40} />}
                                </div>
                                <div className="dg-spot-body">
                                    <span className="dg-spot-tag"><Flame size={13} /> {ru ? 'Почти готово!' : 'Deyarli tayyor!'}</span>
                                    <div className="dg-spot-name">{closest.name}</div>
                                    <div className="dg-spot-desc">{closest.description}</div>
                                    <div className="dg-spot-prog">
                                        <div className="dg-prog-track"><div className="dg-prog-fill dg-prog-fill--cyan" style={{ width: `${Math.min(100, Math.round(closest.progress ?? 0))}%` }} /></div>
                                        <span className="dg-spot-frac">{closest.current_value} / {closest.criteria_value}</span>
                                    </div>
                                    <div className="dg-spot-hint">
                                        {ru
                                            ? <>Осталось <b>{Math.max(0, (closest.criteria_value || 0) - (closest.current_value || 0))}</b> до получения · <b>+{closest.points_reward}</b> {t('rating.pts')}</>
                                            : <>Olishga <b>{Math.max(0, (closest.criteria_value || 0) - (closest.current_value || 0))}</b> ta qoldi · <b>+{closest.points_reward}</b> {t('rating.pts')}</>}
                                    </div>
                                </div>
                            </div>
                        )}

                        {earnedList.length > 0 && (
                            <section className="dg-section">
                                <div className="dg-section-title"><Award size={16} /> {ru ? 'Полученные' : 'Olingan'} <span>{earnedList.length}</span></div>
                                {renderGrid(sortList(earnedList))}
                            </section>
                        )}
                        {lockedList.length > 0 && (
                            <section className="dg-section">
                                <div className="dg-section-title"><Lock size={15} /> {ru ? 'В процессе' : 'Jarayonda'} <span>{lockedList.length}</span></div>
                                {renderGrid(sortList(lockedList), earnedList.length)}
                            </section>
                        )}
                    </>
                ) : flat.length === 0 ? (
                    <div className="dg-state">
                        <Search size={40} className="dg-state-trophy" />
                        <p className="dg-state-title">{ru ? 'Ничего не найдено' : 'Hech narsa topilmadi'}</p>
                    </div>
                ) : (
                    renderGrid(flat)
                )}
            </div>
        </div>
    );
};

export default Degrees;
