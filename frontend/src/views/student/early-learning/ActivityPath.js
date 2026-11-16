import React from 'react';
import ReactDOM from 'react-dom';
import './EarlyHome.css';
import StarRow from './StarRow';
import { nextStep, startLevel } from './earlyHome';

// Sideways offset of each step, in units of --ep-step: a gentle snake.
const SHIFT = [0, 1, 2, 1, 0, -1, -2, -1];

/** The three levels under a path node: each open level is a small button
 * (number + its stars) that replays that level; a locked one is a grey 🔒.
 * An activity from an old cache has no levels — just its level-1 stars. */
function LevelRows({ activity, onPlay, t }) {
    if (!Array.isArray(activity.levels) || activity.levels.length !== 3) {
        return <StarRow stars={activity.best_stars || 0} size={14} />;
    }
    return (
        <span className="ep-levels">
            {activity.levels.map((l) => (l.unlocked ? (
                <button
                    key={l.level}
                    type="button"
                    className={`ep-level ${l.attempts ? 'ep-level-played' : ''}`}
                    aria-label={t('el.level').replace('{n}', l.level)}
                    onClick={() => onPlay(activity, l.level)}
                >
                    <span className="ep-level-num" aria-hidden="true">{l.level}</span>
                    <StarRow stars={l.best_stars || 0} size={11} />
                </button>
            ) : (
                <button key={l.level} type="button" className="ep-level ep-level-locked" aria-label={t('el.locked')} disabled>
                    <span className="ep-level-num" aria-hidden="true">{l.level}</span>
                    <span aria-hidden="true">🔒</span>
                </button>
            )))}
        </span>
    );
}

/** A module's games as a winding path. Every game is a button (it starts
 * the highest open level that has no three stars yet, see startLevel), and
 * under it each level can be replayed. The game nextStep picks is bigger and
 * pulses, and a sticky button below starts it at that level. The path ends
 * at the module's badge, in colour once every game has been played. */
export default function ActivityPath({ activities, moduleEmoji, onPlay, t }) {
    const steps = [...(activities || [])].sort((a, b) => (a.order || 0) - (b.order || 0) || a.id - b.id);
    const step = nextStep(steps);
    const next = step?.activity || null;
    // The badge is the module sticker, which is earned at level 1.
    const finished = steps.length > 0 && steps.every((a) => a.attempts);
    return (
        <div className="ep-wrap">
            <ol className="ep-path">
                {steps.map((activity, i) => {
                    const character = activity.content?.character;
                    const isNext = next?.id === activity.id;
                    return (
                        <li key={activity.id} className="ep-step" style={{ '--ep-shift': SHIFT[i % SHIFT.length] }}>
                            <button
                                type="button"
                                className={`ep-node ${isNext ? 'ep-next' : ''} ${activity.attempts ? 'ep-played' : ''}`}
                                onClick={() => onPlay(activity, startLevel(activity))}
                            >
                                <span className="ep-circle">
                                    <span className="ep-emoji" aria-hidden="true">{character?.emoji || '🎲'}</span>
                                    <span className="ep-number">{i + 1}</span>
                                    {isNext && <span className="ep-play" aria-hidden="true">▶</span>}
                                </span>
                                <span className="ep-title">{character?.label || activity.title}</span>
                            </button>
                            <LevelRows activity={activity} onPlay={onPlay} t={t} />
                            {isNext && step.unlockHint && (
                                <span className="ep-hint">{t('el.unlockHint').replace('{n}', step.unlockHint)}</span>
                            )}
                        </li>
                    );
                })}
                <li className="ep-step ep-step-badge" style={{ '--ep-shift': SHIFT[steps.length % SHIFT.length] }}>
                    <span className={`ep-badge ${finished ? 'ep-badge-owned' : ''}`} aria-hidden="true">{moduleEmoji || '🏅'}</span>
                </li>
            </ol>
            {/* Pinned to the viewport. Portalled to <body>: the page wrapper
                is neither the scroll container (so `sticky` never sticks)
                nor transform-free (so `fixed` would not be viewport-fixed). */}
            {next && ReactDOM.createPortal(
                <button type="button" className="ep-next-btn" onClick={() => onPlay(step.activity, step.level)}>
                    {t('el.pathNext')}
                </button>,
                document.body
            )}
        </div>
    );
}
