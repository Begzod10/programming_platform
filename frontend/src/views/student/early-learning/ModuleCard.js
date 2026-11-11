import React from 'react';
import './EarlyHome.css';
import { isFinished } from './earlyHome';

/** One module on the games home: big emoji, title and a star progress bar.
 * No description on purpose — a five-year-old picks by picture, and the
 * text is still on the module's own page. */
export default function ModuleCard({ module, onOpen, index = 0, t }) {
    const earned = module.earned_stars || 0;
    const max = module.max_stars || 0;
    const pct = max > 0 ? Math.round((Math.min(earned, max) / max) * 100) : 0;
    return (
        <button
            type="button"
            className={`el-module-card eh-card ${isFinished(module) ? 'eh-card-done' : ''}`}
            style={{ '--el-accent': module.color_accent || '#7c5cff', animationDelay: `${Math.min(index, 8) * 0.06}s` }}
            onClick={onOpen}
        >
            {isFinished(module) && <span className="eh-done" role="img" aria-label={t('el.homeDone')}>✓</span>}
            <span className="el-module-card-emoji" aria-hidden="true">{module.icon_emoji || '🎲'}</span>
            <span className="el-module-card-title">{module.title}</span>
            <span className="eh-progress">
                <span className="eh-bar" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={pct} aria-label={module.title}>
                    <span className="eh-bar-fill" style={{ width: `${pct}%` }} />
                </span>
                <span className="eh-progress-text">{earned} / {max}</span>
            </span>
        </button>
    );
}
