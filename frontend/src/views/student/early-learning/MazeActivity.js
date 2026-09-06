import React, { useEffect, useState } from 'react';
import './MazeActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { starsForWrongCount, WRONG_FLASH_MS } from './earlyLearningUtils';
import { ArrowLeft, ArrowUp, ArrowDown, ArrowLeft as ArrowLeftIcon, ArrowRight, Flag } from 'lucide-react';

const DIRECTIONS = {
    up: [-1, 0],
    down: [1, 0],
    left: [0, -1],
    right: [0, 1],
};

const wrongMessage = (lang) => (lang === 'ru' ? 'Ой! Там стена.' : 'Oh-oh! Bu yerda devor bor.');

/** One "walk the character to the flag" round. activity.content shape
 * (mode: "maze"): { character: {emoji,label}, grid: {rows,cols}, start:
 * [row,col], end: [row,col], walls: [[row,col], ...] }. Fourth sibling of
 * MatchingActivity.js/BuildActivity.js/TraceActivity.js — same completion
 * flow, different input: tap an arrow to attempt a one-cell move, hit-tested
 * against the grid bounds and wall list instead of a pool/slot/checkpoint.
 * A wall bump is scored exactly like a wrong tap/drop elsewhere — reuses
 * starsForWrongCount as-is, no new scoring rule needed.
 */
export default function MazeActivity({ activity, onBack, onComplete, lang, toggleLang, t }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const rows = content.grid?.rows || 1;
    const cols = content.grid?.cols || 1;
    const start = content.start || [0, 0];
    const end = content.end || [0, 0];
    const walls = content.walls || [];

    const isWall = (r, c) => walls.some((w) => w[0] === r && w[1] === c);
    const inBounds = (r, c) => r >= 0 && r < rows && c >= 0 && c < cols;

    const [pos, setPos] = useState(start);
    const [wrongCount, setWrongCount] = useState(0);
    const [flash, setFlash] = useState(null); // { token, message } | null — token guards against an older bump's timeout clearing a newer one
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const atEnd = pos[0] === end[0] && pos[1] === end[1];

    // Fires once the character actually reaches the end — reading it from
    // state (rather than inline in handleMove) keeps this correct
    // regardless of how the position got there.
    useEffect(() => {
        if (celebration === null && atEnd) {
            playSynth('fanfare');
            setCelebration(starsForWrongCount(wrongCount));
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [pos]);

    const handleMove = (dir) => {
        if (celebration !== null || submitting) return;
        const [dr, dc] = DIRECTIONS[dir];
        const target = [pos[0] + dr, pos[1] + dc];

        if (inBounds(target[0], target[1]) && !isWall(target[0], target[1])) {
            playSynth('coin');
            setPos(target);
        } else {
            playSynth('laser');
            setWrongCount((c) => c + 1);
            const token = Date.now();
            setFlash({ token, message: wrongMessage(lang) });
            setTimeout(() => setFlash((f) => (f?.token === token ? null : f)), WRONG_FLASH_MS);
        }
    };

    const handleCelebrationDone = () => {
        const stars = celebration;
        setSubmitting(true);
        request(`${API_URL}v1/early-learning/activities/${activity.id}/complete`, 'POST', { stars }, headers())
            .then((result) => onComplete(result))
            .catch((err) => {
                console.error(err);
                // Still let the child close the round locally — losing the
                // star-save on a flaky request shouldn't trap the kid here.
                onComplete({ stars_earned: stars, attempts: 1 });
            })
            .finally(() => setSubmitting(false));
    };

    return (
        <div className="mz-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="mz-character-header">
                <span className="mz-character-emoji">{character.emoji || '🦸'}</span>
                <h2>{character.label || activity.title}</h2>
            </div>

            {activity.instruction_text && <p className="mz-instruction">{activity.instruction_text}</p>}
            {flash && <div className="mz-error-banner">{flash.message}</div>}

            <div className={`mz-scene ${flash ? 'mz-scene-bump' : ''}`}>
                <div
                    className="mz-grid"
                    style={{ gridTemplateColumns: `repeat(${cols}, 1fr)`, gridTemplateRows: `repeat(${rows}, 1fr)` }}
                >
                    {Array.from({ length: rows * cols }, (_, i) => {
                        const r = Math.floor(i / cols);
                        const c = i % cols;
                        const wall = isWall(r, c);
                        const isEnd = r === end[0] && c === end[1];
                        return (
                            <div key={i} className={`mz-cell ${wall ? 'mz-cell-wall' : ''}`}>
                                {!wall && isEnd && <Flag size={18} className="mz-flag" />}
                            </div>
                        );
                    })}
                </div>
                <div
                    className="mz-avatar"
                    style={{ left: `${((pos[1] + 0.5) / cols) * 100}%`, top: `${((pos[0] + 0.5) / rows) * 100}%` }}
                >
                    {character.emoji || '🦸'}
                </div>
            </div>

            <div className="mz-pad">
                <button className="mz-pad-btn mz-pad-up" onClick={() => handleMove('up')} disabled={submitting}>
                    <ArrowUp size={22} />
                </button>
                <div className="mz-pad-row">
                    <button className="mz-pad-btn" onClick={() => handleMove('left')} disabled={submitting}>
                        <ArrowLeftIcon size={22} />
                    </button>
                    <button className="mz-pad-btn" onClick={() => handleMove('right')} disabled={submitting}>
                        <ArrowRight size={22} />
                    </button>
                </div>
                <button className="mz-pad-btn mz-pad-down" onClick={() => handleMove('down')} disabled={submitting}>
                    <ArrowDown size={22} />
                </button>
            </div>

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
