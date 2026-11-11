import React from 'react';
import './EarlyHome.css';

/** The one big button at the top of the games home: carry on where the kid
 * stopped (or start, for a first visit). `pick` comes from pickContinue. */
export default function ContinueCard({ pick, onOpen, t }) {
    const { module, started } = pick;
    const done = module.completed_count || 0;
    const total = module.activities_count || 0;
    const pct = total > 0 ? Math.round((Math.min(done, total) / total) * 100) : 0;
    const games = t('el.homeGames').replace('{a}', done).replace('{b}', total);
    return (
        <button type="button" className="eh-continue" style={{ '--el-accent': module.color_accent || '#ff8a5c' }} onClick={onOpen}>
            <span className="eh-continue-emoji" aria-hidden="true">{module.icon_emoji || '🎲'}</span>
            <span className="eh-continue-body">
                <span className="eh-continue-label">
                    <span aria-hidden="true">▶ </span>
                    <span>{started ? t('el.homeContinue') : t('el.homeStart')}</span>
                </span>
                <span className="eh-continue-title">{module.title}</span>
                <span className="eh-continue-progress">
                    <span className="eh-continue-bar"><span style={{ width: `${pct}%` }} /></span>
                    <span>{games}</span>
                </span>
            </span>
        </button>
    );
}
