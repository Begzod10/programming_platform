import React from 'react';
import ReactDOM from 'react-dom';
import './EarlyHome.css';
import StarRow from './StarRow';
import { nextActivity } from './earlyHome';

// Sideways offset of each step, in units of --ep-step: a gentle snake.
const SHIFT = [0, 1, 2, 1, 0, -1, -2, -1];

/** A module's games as a winding path. Nothing is locked — every step is a
 * button — but the first unplayed one is bigger and pulses, and a sticky
 * button below starts it. The path ends at the module's badge, in colour
 * once every game has been played. */
export default function ActivityPath({ activities, moduleEmoji, onPlay, t }) {
    const steps = [...(activities || [])].sort((a, b) => (a.order || 0) - (b.order || 0) || a.id - b.id);
    const next = nextActivity(steps);
    const finished = steps.length > 0 && !next;
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
                                onClick={() => onPlay(activity.id)}
                            >
                                <span className="ep-circle">
                                    <span className="ep-emoji" aria-hidden="true">{character?.emoji || '🎲'}</span>
                                    <span className="ep-number">{i + 1}</span>
                                    {isNext && <span className="ep-play" aria-hidden="true">▶</span>}
                                </span>
                                <span className="ep-title">{character?.label || activity.title}</span>
                                <StarRow stars={activity.best_stars || 0} size={14} />
                            </button>
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
                <button type="button" className="ep-next-btn" onClick={() => onPlay(next.id)}>
                    {t('el.pathNext')}
                </button>,
                document.body
            )}
        </div>
    );
}
