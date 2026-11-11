import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import './EarlyLearning.css';
import { API_URL, useHttp, headers, getCurrentUser } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
import QuotaLockScreen from '../../../components/QuotaLockScreen';
import { useDailyQuota } from '../../../hooks/useDailyQuota';
import MatchingActivity from './MatchingActivity';
import BuildActivity from './BuildActivity';
import TraceActivity from './TraceActivity';
import MazeActivity from './MazeActivity';
import PairsActivity from './PairsActivity';
import CountActivity from './CountActivity';
import SortActivity from './SortActivity';
import SequenceActivity from './SequenceActivity';
import PatternActivity from './PatternActivity';
import CauseEffectActivity from './CauseEffectActivity';
import ArithmeticActivity from './ArithmeticActivity';
import TypingActivity from './TypingActivity';
import KeyboardActivity from './KeyboardActivity';
import CompareActivity from './CompareActivity';
import SimonActivity from './SimonActivity';
import WordBuildActivity from './WordBuildActivity';
import ChartActivity from './ChartActivity';
import RoundsActivity from './RoundsActivity';
import BubblesActivity from './BubblesActivity';
import HangmanActivity from './HangmanActivity';
import MergeActivity from './MergeActivity';
import SudokuActivity from './SudokuActivity';
import PicturePuzzleActivity from './PicturePuzzleActivity';
import LangToggle from './LangToggle';
import Sky from './Sky';
import StickerStrip from './StickerStrip';
import StickerReveal from './StickerReveal';
import ModuleCard from './ModuleCard';
import ContinueCard from './ContinueCard';
import ActivityPath from './ActivityPath';
import { pickContinue, pickNew, groupBySection, nextActivity } from './earlyHome';
import { getDaily, queueCompletion, flushCompletionQueue, applyGuestModuleStars, applyGuestActivityStars, elCacheKey, elCacheSet, elCacheGet, registerOfflineSw } from './earlyLearningUtils';
import { ArrowLeft, Star, Trophy, Sparkles } from 'lucide-react';

const MEDALS = ['🥇', '🥈', '🥉'];

/** Small inline "N / M" star badge — used for the whole-module progress on
 * the picker card, where M can be double digits (too many to render as
 * individual star icons, unlike a single activity's 0-3 best_stars). */
function StarBadge({ earned, max }) {
    return (
        <span className="el-star-badge">
            <Star size={14} fill="currentColor" />
            {earned} / {max}
        </span>
    );
}

/** "Today" star count — the resettable counterpart to StarBadge's permanent
 * all-time total. No `max` here on purpose: there's no fixed daily target,
 * just "how many did you earn today", which naturally goes back to 0 on a
 * new day server-side (see EarlyActivityDailyStars) without this component
 * needing to know or care about that. Distinct color from StarBadge so a
 * kid (or a parent glancing over) doesn't read it as the same number. */
function TodayStarBadge({ earned, t }) {
    return (
        <span className="el-star-badge el-star-badge-today">
            <Sparkles size={14} />
            {t('el.today')}: {earned}
        </span>
    );
}

/** Classmates ranked by total stars — scoped server-side to "whoever shares
 * a teacher with me" (see the backend's classmate_ids_subquery), never
 * platform-wide: a young kid doesn't know or care about a stranger three
 * schools over, and a global ranking would just be discouraging noise for
 * most of them. Shows a friendly empty state instead of a lonely
 * one-person list when the student has no class assigned yet. */
function Leaderboard({ entries, hasClass, period, onPeriod, t }) {
    if (!hasClass) {
        return (
            <div className="el-leaderboard el-leaderboard-empty">
                <Trophy size={28} />
                <p>{t('el.leaderboardEmpty')}</p>
            </div>
        );
    }
    return (
        <div className="el-leaderboard">
            <h2><Trophy size={20} /> {t('el.leaderboardTitle')}</h2>
            <div className="el-lb-tabs">
                {[['today', 'el.lbToday'], ['all_time', 'el.lbAll']].map(([value, key]) => (
                    <button
                        key={value}
                        type="button"
                        className={`el-lb-tab ${period === value ? 'el-lb-tab-active' : ''}`}
                        aria-pressed={period === value}
                        onClick={() => onPeriod(value)}
                    >
                        {t(key)}
                    </button>
                ))}
            </div>
            <div className="el-leaderboard-list">
                {entries.map((entry) => (
                    <div key={entry.student_id} className={`el-leaderboard-row ${entry.is_me ? 'el-leaderboard-me' : ''}`}>
                        <span className="el-leaderboard-rank">{MEDALS[entry.rank - 1] || `#${entry.rank}`}</span>
                        <span className="el-leaderboard-name">{entry.name}{entry.is_me ? ` ${t('el.you')}` : ''}</span>
                        <span className="el-leaderboard-stars"><Star size={14} fill="currentColor" /> {entry.total_stars}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}


// A request that hangs (dead DNS, captive wifi) should fall through to the
// offline cache after a few seconds instead of leaving "Yuklanmoqda…" up
// until the browser's own much longer network timeout.
function withTimeout(promise, ms = 8000) {
    return Promise.race([
        promise,
        new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), ms)),
    ]);
}

export default function EarlyLearning({ guest = false }) {
    const { moduleId } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const { request } = useHttp();
    const { t, lang, toggleLang } = useTranslation();
    // Daily-quota gate — only real students (not guest /play, not teacher preview).
    const quotaGated = !guest && !location.pathname.startsWith('/teacher');
    const quota = useDailyQuota({ enabled: quotaGated });

    // This view is mounted under /student/early-learning (kids playing),
    // /teacher/early-learning (a teacher checking what's live), AND — with
    // guest=true — the top-level /play route (no login at all, see
    // AppRouter.js). Same components either way; only the base path to
    // navigate within, and which API/storage backs star progress, differ.
    const basePath = guest ? '/play' : (location.pathname.startsWith('/teacher') ? '/teacher' : '/student');
    const routeBase = guest ? basePath : `${basePath}/early-learning`;
    // No sidebar exists on this full-bleed page (see the layout's
    // "isImmersive" branch) — the top-level list view's back button is the
    // only way out, so it exits to each role's normal home instead of
    // stepping up within the feature (there's nothing above the list). A
    // guest has no home to go back to — /login is the natural landing spot
    // for someone who just finished trying the games out.
    const exitPath = guest ? '/login' : (basePath === '/teacher' ? `${basePath}/profile` : `${basePath}/dashboard`);

    const [modules, setModules] = useState([]);
    const [modulesLoading, setModulesLoading] = useState(true);
    const [leaderboard, setLeaderboard] = useState(null);
    // "today" first: every kid starts from zero each morning, so a late
    // joiner can still win (the all-time board is one tab away).
    const [lbPeriod, setLbPeriod] = useState('today');
    // Sticker collection (signed-in students only) — the home strip's data,
    // and the stickers the game just finished earned, if any.
    const stickersEnabled = !guest && basePath === '/student';
    const [album, setAlbum] = useState(null);
    const [reveal, setReveal] = useState(null);

    const [moduleDetail, setModuleDetail] = useState(null);
    const [detailLoading, setDetailLoading] = useState(!!moduleId);

    const [playingActivityId, setPlayingActivityId] = useState(null);

    // Offline page load (see public/play-sw.js) — scoped to this feature's
    // own route only, registered once on first mount.
    useEffect(() => { registerOfflineSw(routeBase); }, [routeBase]);

    // Offline support: every successful fetch is mirrored into localStorage
    // (see elCacheKey in earlyLearningUtils.js) and shown FIRST on the next
    // visit (stale-while-revalidate) — so a dead/flaky connection never
    // leaves the games screen empty or stuck on "Yuklanmoqda…", and a slow
    // network still feels instant. The network fetch then refreshes it.
    const userId = getCurrentUser()?.id;
    const prefetchedRef = useRef('');

    // Warms the cache for every module's activities (once per language per
    // page load), a few at a time — one after another was slow enough that
    // turning wifi off soon after the list appeared left most modules
    // uncached.
    const prefetchAllModules = useCallback((list) => {
        if (prefetchedRef.current === lang || !Array.isArray(list)) return;
        prefetchedRef.current = lang;
        const queue = [...list];
        const worker = async () => {
            while (queue.length) {
                const m = queue.shift();
                try {
                    const detailUrl = guest
                        ? `${API_URL}v1/early-learning/public/modules/${m.id}?lang=${lang}`
                        : `${API_URL}v1/early-learning/modules/${m.id}?lang=${lang}`;
                    const detail = await withTimeout(request(detailUrl, 'GET', null, headers()), 15000);
                    elCacheSet(elCacheKey(guest, userId, 'module', lang, m.id), detail);
                } catch {
                    // One module failing (age-gated 404, timeout) shouldn't stop the rest.
                }
            }
        };
        Promise.all([worker(), worker(), worker(), worker(), worker()]);
    }, [request, lang, guest, userId]);

    const fetchModules = useCallback(() => {
        const listKey = elCacheKey(guest, userId, 'modules', lang);
        const url = guest
            ? `${API_URL}v1/early-learning/public/modules?lang=${lang}`
            : `${API_URL}v1/early-learning/modules?lang=${lang}`;
        const cached = elCacheGet(listKey);
        if (cached) {
            setModules(guest ? applyGuestModuleStars(cached) : cached);
            setModulesLoading(false);
        } else {
            setModulesLoading(true);
        }
        const offline = typeof navigator !== 'undefined' && navigator.onLine === false;
        if (!(offline && cached)) {
            withTimeout(request(url, 'GET', null, headers()))
                .then((data) => {
                    elCacheSet(listKey, data);
                    setModules(guest ? applyGuestModuleStars(data) : data);
                    prefetchAllModules(data);
                })
                .catch(console.error)
                .finally(() => setModulesLoading(false));
        }
    }, [request, lang, guest, userId, prefetchAllModules]);

    const fetchModuleDetail = useCallback((id) => {
        const detailKey = elCacheKey(guest, userId, 'module', lang, id);
        const url = guest
            ? `${API_URL}v1/early-learning/public/modules/${id}?lang=${lang}`
            : `${API_URL}v1/early-learning/modules/${id}?lang=${lang}`;
        const cached = elCacheGet(detailKey);
        if (cached) {
            setModuleDetail(guest ? applyGuestActivityStars(cached) : cached);
            setDetailLoading(false);
        } else {
            // Don't leave the previously opened module showing while this one loads.
            setModuleDetail(null);
            setDetailLoading(true);
        }
        const offline = typeof navigator !== 'undefined' && navigator.onLine === false;
        if (offline && cached) return;
        withTimeout(request(url, 'GET', null, headers()))
            .then((data) => {
                elCacheSet(detailKey, data);
                setModuleDetail(guest ? applyGuestActivityStars(data) : data);
            })
            .catch(console.error)
            .finally(() => setDetailLoading(false));
    }, [request, lang, guest, userId]);

    // Independent of the module list — a leaderboard or sticker fetch
    // failing must never block the games themselves. A guest has no account,
    // so neither applies; a teacher previewing gets the leaderboard only.
    // Names aren't translated (student profile data), so no ?lang there.
    const fetchLeaderboard = useCallback(() => {
        if (guest) return;
        request(`${API_URL}v1/early-learning/leaderboard?period=${lbPeriod}`, 'GET', null, headers())
            .then(setLeaderboard)
            .catch(console.error);
    }, [request, guest, lbPeriod]);

    const fetchAlbum = useCallback(() => {
        if (!stickersEnabled) return;
        request(`${API_URL}v1/early-learning/stickers?lang=${lang}`, 'GET', null, headers())
            .then(setAlbum)
            .catch(() => setAlbum(null));
    }, [request, stickersEnabled, lang]);

    useEffect(() => { if (!moduleId) fetchLeaderboard(); }, [moduleId, fetchLeaderboard]);
    useEffect(() => { if (!moduleId) fetchAlbum(); }, [moduleId, fetchAlbum]);

    useEffect(() => {
        if (!moduleId) {
            fetchModules();
        } else {
            fetchModuleDetail(moduleId);
        }
    }, [moduleId, fetchModules, fetchModuleDetail]);

    // "Continue" on the home page lands here with state.autoplay: open the
    // kid's next unplayed game straight away. Once per arrival — leaving the
    // game must show the path, not reopen the game.
    const autoplayedFor = useRef(null);
    useEffect(() => {
        if (!location.state?.autoplay || !moduleId || !moduleDetail) return;
        if (String(moduleDetail.id) !== String(moduleId) || autoplayedFor.current === moduleId) return;
        autoplayedFor.current = moduleId;
        const next = nextActivity(moduleDetail.activities);
        if (next) setPlayingActivityId(next.id);
    }, [location.state, moduleId, moduleDetail]);

    // Stars earned while offline are parked in localStorage (see below) and
    // sent as soon as the connection is back — on load and on the `online` event.
    useEffect(() => {
        if (guest) return undefined;
        const send = (id, stars) =>
            request(`${API_URL}v1/early-learning/activities/${id}/complete`, 'POST', { stars }, headers());
        const flush = () => { flushCompletionQueue(send); };
        flush();
        window.addEventListener('online', flush);
        return () => window.removeEventListener('online', flush);
    }, [guest, request]);

    const handleActivityComplete = (activityId, result) => {
        // A real server reply carries activity_id; the offline fallback in the
        // play screens does not, so that's the "didn't save" signal.
        if (!guest && result.activity_id === undefined) queueCompletion(activityId, result.stars_earned);
        setModuleDetail((prev) => {
            if (!prev) return prev;
            const activities = prev.activities.map((a) =>
                a.id === activityId ? { ...a, best_stars: result.stars_earned, attempts: result.attempts } : a
            );
            const earned_stars = activities.reduce((sum, a) => sum + a.best_stars, 0);
            return { ...prev, activities, earned_stars };
        });
        setPlayingActivityId(null);
        if (stickersEnabled && result.new_stickers?.length) setReveal(result.new_stickers);
    };

    // ── Daily-quota lock — block the whole kids' area until today's quota is met ──
    if (quotaGated && !quota.loading && !quota.unlocked) {
        return (
            <div className="el-shell">
                <Sky />
                <div style={{ position: 'relative', zIndex: 1 }}>
                    <QuotaLockScreen completed={quota.completed}
                        baseRequired={quota.baseRequired} remaining={quota.remaining}
                        nextLesson={quota.nextLesson} />
                </div>
            </div>
        );
    }

    // ── Playing a single activity ──
    if (moduleId && playingActivityId) {
        const activity = moduleDetail?.activities.find((a) => a.id === playingActivityId);
        if (activity) {
            // content.mode picks the mechanic: "build" drags pieces onto
            // their own spot (BuildActivity.js), "trace" draws a shape's
            // outline freehand (TraceActivity.js), "maze" walks a character
            // to a flag via arrow taps (MazeActivity.js), "pairs" flips
            // cards to find matches (PairsActivity.js), "count" taps the
            // number matching how many items you see (CountActivity.js),
            // "sort" taps an item then taps the bin it belongs in
            // (SortActivity.js), "sequence" taps steps in the right order
            // (SequenceActivity.js), "pattern" taps the emoji that
            // continues a repeating pattern (PatternActivity.js),
            // "cause_effect" taps the effect that follows a given cause
            // (CauseEffectActivity.js), "arithmetic" solves a randomly
            // generated single-digit +/− equation (ArithmeticActivity.js —
            // rounds are generated client-side each play, not authored in
            // content_json), "typing" types out a shown word letter-by-
            // letter, MonkeyType-style live feedback (TypingActivity.js —
            // words ARE authored in content_json, unlike arithmetic's
            // procedural rounds, since real vocabulary can't be generated),
            // "keyboard" is a touch-typing trainer (KeyboardActivity.js —
            // press the highlighted key, finger shown), "compare" picks <, = or >
            // (CompareActivity.js), "simon" repeats a growing colour/sound
            // sequence (SimonActivity.js), anything else (the shipped "select" mode, or an activity with
            // no mode yet) taps items out of a pool (MatchingActivity.js,
            // the original/default game).
            const mode = activity.content?.mode;
            const ActivityScreen =
                mode === 'trace' ? TraceActivity :
                mode === 'build' ? BuildActivity :
                mode === 'maze' ? MazeActivity :
                mode === 'pairs' ? PairsActivity :
                mode === 'count' ? CountActivity :
                mode === 'sort' ? SortActivity :
                mode === 'sequence' ? SequenceActivity :
                mode === 'pattern' ? PatternActivity :
                mode === 'cause_effect' ? CauseEffectActivity :
                mode === 'arithmetic' ? ArithmeticActivity :
                mode === 'typing' ? TypingActivity :
                mode === 'keyboard' ? KeyboardActivity :
                mode === 'compare' ? CompareActivity :
                mode === 'simon' ? SimonActivity :
                mode === 'wordbuild' ? WordBuildActivity :
                mode === 'chart' ? ChartActivity :
                mode === 'rounds' ? RoundsActivity :
                mode === 'bubbles' ? BubblesActivity :
                mode === 'hangman' ? HangmanActivity :
                mode === 'merge' ? MergeActivity :
                mode === 'sudoku' ? SudokuActivity :
                mode === 'puzzle' ? PicturePuzzleActivity :
                MatchingActivity;
            return (
                <div className="el-shell">
                    <Sky />
                    <ActivityScreen
                        activity={activity}
                        onBack={() => setPlayingActivityId(null)}
                        onComplete={(result) => handleActivityComplete(activity.id, result)}
                        lang={lang}
                        toggleLang={toggleLang}
                        t={t}
                        guest={guest}
                    />
                </div>
            );
        }
    }

    // ── One module's activity grid ──
    if (moduleId) {
        if (!moduleDetail) {
            return (
                <div className="el-shell">
                    <Sky />
                    <div className="el-page el-loading">
                        {detailLoading ? (t('loading') || 'Yuklanmoqda...') : (
                            <>
                                <p>{lang === 'ru'
                                    ? 'Нет интернета, а эта игра ещё не сохранена на устройстве.'
                                    : "Internet yo'q va bu o'yin qurilmada hali saqlanmagan."}</p>
                                <button className="el-back-btn" onClick={() => navigate(routeBase)}>
                                    <ArrowLeft size={18} /> {t('el.back')}
                                </button>
                            </>
                        )}
                    </div>
                </div>
            );
        }
        return (
            <div className="el-shell">
                <Sky />
                <div className="el-page">
                    <div className="el-page-topbar">
                        <button className="el-back-btn" onClick={() => navigate(routeBase)}>
                            <ArrowLeft size={18} /> {t('el.back')}
                        </button>
                        <LangToggle lang={lang} toggleLang={toggleLang} />
                    </div>
                    <div className="el-module-header" style={{ '--el-accent': moduleDetail.color_accent || '#7c5cff' }}>
                        <span className="el-module-emoji">{moduleDetail.icon_emoji}</span>
                        <div>
                            <h1>{moduleDetail.title}</h1>
                            {moduleDetail.description && <p>{moduleDetail.description}</p>}
                        </div>
                        <div className="el-badge-stack">
                            <StarBadge earned={moduleDetail.earned_stars} max={moduleDetail.max_stars} />
                            <TodayStarBadge earned={moduleDetail.earned_stars_today} t={t} />
                        </div>
                    </div>
                    <ActivityPath
                        activities={moduleDetail.activities}
                        moduleEmoji={moduleDetail.icon_emoji}
                        onPlay={setPlayingActivityId}
                        t={t}
                    />
                </div>
                {reveal && (
                    <StickerReveal
                        stickers={reveal}
                        lang={lang}
                        t={t}
                        onClose={() => setReveal(null)}
                        onOpenAlbum={() => { setReveal(null); navigate('/student/stickers'); }}
                    />
                )}
            </div>
        );
    }

    // ── Module picker ──
    if (modulesLoading) {
        return (
            <div className="el-shell">
                <Sky />
                <div className="el-page el-loading">{t('loading') || 'Yuklanmoqda...'}</div>
            </div>
        );
    }

    const totalEarned = modules.reduce((sum, m) => sum + m.earned_stars, 0);
    const totalMax = modules.reduce((sum, m) => sum + m.max_stars, 0);
    const totalEarnedToday = modules.reduce((sum, m) => sum + (m.earned_stars_today || 0), 0);
    const continuePick = pickContinue(modules);
    const newModules = pickNew(modules, continuePick?.module);
    const openModule = (m) => navigate(`${routeBase}/${m.id}`);

    return (
        <div className="el-shell">
            <Sky />
            <div className="el-page">
                <div className="el-page-topbar">
                    <button className="el-back-btn" onClick={() => navigate(exitPath)}>
                        <ArrowLeft size={18} /> {t('el.back')}
                    </button>
                    <LangToggle lang={lang} toggleLang={toggleLang} />
                </div>
                <div className="el-hero">
                    <h1>{t('early_learning')}</h1>
                    <p>{t('el.subtitle')}</p>
                    {totalMax > 0 && (
                        <div className="el-badge-stack">
                            <StarBadge earned={totalEarned} max={totalMax} />
                            <TodayStarBadge earned={totalEarnedToday} t={t} />
                        </div>
                    )}
                </div>
                {continuePick && (
                    <ContinueCard
                        pick={continuePick}
                        t={t}
                        onOpen={() => navigate(`${routeBase}/${continuePick.module.id}`, { state: { autoplay: true } })}
                    />
                )}
                {stickersEnabled && album && (
                    <StickerStrip album={album} t={t} onOpen={() => navigate('/student/stickers')} />
                )}
                {guest && (
                    <div className="stk-guest">
                        <span>🎁 {t('el.stickerGuest')}</span>
                        <button type="button" onClick={() => navigate('/login')}>{t('el.stickerLogin')}</button>
                    </div>
                )}
                {(guest || basePath === '/student') && (
                    <div className="el-entry-row">
                        <button className="el-duel-btn" onClick={() => navigate(guest ? '/play/duel' : '/student/duel')}>
                            ⚔️ {lang === 'ru' ? 'Гонка' : 'Poyga'}
                        </button>
                        <button className="el-duel-btn el-daily-btn" onClick={() => navigate(guest ? '/play/daily' : '/student/daily')}>
                            📅 {lang === 'ru' ? 'Задание дня' : 'Kunlik vazifa'} {guest && getDaily().streak > 0 ? `🔥${getDaily().streak}` : ''}
                        </button>
                    </div>
                )}
                {newModules.length > 0 && (
                    <section className="eh-section">
                        <h2 className="eh-section-title">✨ {t('el.homeNew')}</h2>
                        <div className="eh-new-row">
                            {newModules.map((module, i) => (
                                <ModuleCard key={module.id} module={module} index={i} t={t} onOpen={() => openModule(module)} />
                            ))}
                        </div>
                    </section>
                )}
                {groupBySection(modules).map((group) => (
                    <section key={group.key} className="eh-section">
                        <h2 className="eh-section-title">{group.emoji} {t(group.titleKey)}</h2>
                        <div className="el-module-grid">
                            {group.modules.map((module, i) => (
                                <ModuleCard key={module.id} module={module} index={i} t={t} onOpen={() => openModule(module)} />
                            ))}
                        </div>
                    </section>
                ))}
                {modules.length === 0 && (
                    <div className="el-empty">{t('el.empty')}</div>
                )}
                {leaderboard && (
                    <Leaderboard
                        entries={leaderboard.entries}
                        hasClass={leaderboard.has_class}
                        period={lbPeriod}
                        onPeriod={setLbPeriod}
                        t={t}
                    />
                )}
            </div>
        </div>
    );
}
