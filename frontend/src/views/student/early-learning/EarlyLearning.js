import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import './EarlyLearning.css';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { useTranslation } from '../../../i18n/useTranslation';
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
import LangToggle from './LangToggle';
import { applyGuestModuleStars, applyGuestActivityStars } from './earlyLearningUtils';
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

/** Three-star row for one activity's best score — filled up to `stars`. */
function StarRow({ stars, size = 16 }) {
    return (
        <span className="el-star-row">
            {[0, 1, 2].map((i) => (
                <Star key={i} size={size} fill={i < stars ? 'currentColor' : 'none'} className={i < stars ? 'el-star-filled' : 'el-star-empty'} />
            ))}
        </span>
    );
}

/** Classmates ranked by total stars — scoped server-side to "whoever shares
 * a teacher with me" (see the backend's classmate_ids_subquery), never
 * platform-wide: a young kid doesn't know or care about a stranger three
 * schools over, and a global ranking would just be discouraging noise for
 * most of them. Shows a friendly empty state instead of a lonely
 * one-person list when the student has no class assigned yet. */
function Leaderboard({ entries, hasClass, t }) {
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


/** Decorative sky background — sun, drifting clouds, a paper plane — the
 * whole feature runs full-bleed with no sidebar (see StudentLayout.js /
 * TeacherLayout.js "isImmersive" branch), so this owns the entire
 * backdrop instead of the app's usual glass-panel chrome. Purely
 * decorative (aria-hidden), same spirit as the reference kids' game. */
function Sky() {
    return (
        <div className="el-sky" aria-hidden="true">
            <span className="el-sun" />
            <span className="el-cloud el-cloud-1">☁️</span>
            <span className="el-cloud el-cloud-2">☁️</span>
            <span className="el-cloud el-cloud-3">☁️</span>
            <span className="el-plane">🛩️</span>
            <span className="el-kite">🪁</span>
        </div>
    );
}

export default function EarlyLearning({ guest = false }) {
    const { moduleId } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const { request } = useHttp();
    const { t, lang, toggleLang } = useTranslation();

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

    const [moduleDetail, setModuleDetail] = useState(null);
    const [detailLoading, setDetailLoading] = useState(false);

    const [playingActivityId, setPlayingActivityId] = useState(null);

    const fetchModules = useCallback(() => {
        setModulesLoading(true);
        const url = guest
            ? `${API_URL}v1/early-learning/public/modules?lang=${lang}`
            : `${API_URL}v1/early-learning/modules?lang=${lang}`;
        request(url, 'GET', null, headers())
            .then((data) => setModules(guest ? applyGuestModuleStars(data) : data))
            .catch(console.error)
            .finally(() => setModulesLoading(false));
        // A guest has no classmates (no account at all) to rank against —
        // skip the fetch entirely rather than hitting the authed endpoint
        // and eating an avoidable 401. leaderboard stays null, which the
        // render below already treats as "don't show the section".
        if (guest) return;
        // Independent of the module list — a leaderboard fetch failing
        // shouldn't block the games themselves from loading. Names aren't
        // translated (they're student profile data), so no ?lang here.
        request(`${API_URL}v1/early-learning/leaderboard`, 'GET', null, headers())
            .then(setLeaderboard)
            .catch(console.error);
    }, [request, lang, guest]);

    const fetchModuleDetail = useCallback((id) => {
        setDetailLoading(true);
        const url = guest
            ? `${API_URL}v1/early-learning/public/modules/${id}?lang=${lang}`
            : `${API_URL}v1/early-learning/modules/${id}?lang=${lang}`;
        request(url, 'GET', null, headers())
            .then((data) => setModuleDetail(guest ? applyGuestActivityStars(data) : data))
            .catch(console.error)
            .finally(() => setDetailLoading(false));
    }, [request, lang, guest]);

    useEffect(() => {
        if (!moduleId) {
            fetchModules();
        } else {
            fetchModuleDetail(moduleId);
        }
    }, [moduleId, fetchModules, fetchModuleDetail]);

    const handleActivityComplete = (activityId, result) => {
        setModuleDetail((prev) => {
            if (!prev) return prev;
            const activities = prev.activities.map((a) =>
                a.id === activityId ? { ...a, best_stars: result.stars_earned, attempts: result.attempts } : a
            );
            const earned_stars = activities.reduce((sum, a) => sum + a.best_stars, 0);
            return { ...prev, activities, earned_stars };
        });
        setPlayingActivityId(null);
        if (guest) return;
        // Refresh the leaderboard so a completion shows up right away
        // instead of only after the next full page load.
        request(`${API_URL}v1/early-learning/leaderboard`, 'GET', null, headers())
            .then(setLeaderboard)
            .catch(console.error);
    };

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
            // (CauseEffectActivity.js), anything else (the shipped "select"
            // mode, or an activity with no mode yet) taps items out of a
            // pool (MatchingActivity.js, the original/default game).
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
        if (detailLoading || !moduleDetail) {
            return (
                <div className="el-shell">
                    <Sky />
                    <div className="el-page el-loading">{t('loading') || 'Yuklanmoqda...'}</div>
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
                    <div className="el-activity-grid">
                        {moduleDetail.activities.map((activity, i) => {
                            const character = activity.content?.character;
                            return (
                                <button
                                    key={activity.id}
                                    className="el-activity-card"
                                    style={{ animationDelay: `${i * 0.05}s` }}
                                    onClick={() => setPlayingActivityId(activity.id)}
                                >
                                    <span className="el-activity-emoji">{character?.emoji || '🎲'}</span>
                                    <span className="el-activity-title">{character?.label || activity.title}</span>
                                    <StarRow stars={activity.best_stars} />
                                </button>
                            );
                        })}
                    </div>
                </div>
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
                <div className="el-module-grid">
                    {modules.map((module, i) => (
                        <button
                            key={module.id}
                            className="el-module-card"
                            style={{ '--el-accent': module.color_accent || '#7c5cff', animationDelay: `${i * 0.08}s` }}
                            onClick={() => navigate(`${routeBase}/${module.id}`)}
                        >
                            <span className="el-module-card-emoji">{module.icon_emoji}</span>
                            <span className="el-module-card-title">{module.title}</span>
                            {module.description && <span className="el-module-card-desc">{module.description}</span>}
                            <StarBadge earned={module.earned_stars} max={module.max_stars} />
                        </button>
                    ))}
                    {modules.length === 0 && (
                        <div className="el-empty">{t('el.empty')}</div>
                    )}
                </div>
                {leaderboard && <Leaderboard entries={leaderboard.entries} hasClass={leaderboard.has_class} t={t} />}
            </div>
        </div>
    );
}
