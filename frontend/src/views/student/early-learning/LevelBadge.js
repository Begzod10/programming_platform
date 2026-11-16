import React from 'react';
import './EarlyHome.css';

/** "2-daraja" next to a game's title while a harder level is played. Level 1
 * is the game as it always was, so it shows nothing. */
export default function LevelBadge({ level, t }) {
    if (!level || level <= 1) return null;
    return <span className="el-level-badge">{t('el.level').replace('{n}', level)}</span>;
}
