import React, { createContext, useContext, useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import '../courses/LessonPage/CelebrationOverlay.css';
import './EarlyActivityCelebration.css';
import { Star } from 'lucide-react';
import { cheerStars } from './earlyVoice';

// Same confetti-piece system as CelebrationOverlay — duplicated rather than
// imported since CelebrationOverlay doesn't export PIECES, and the two
// components are meant to stay independent (see file docstring below).
const COLORS = ['#7c3aed', '#10b981', '#f59e0b', '#ef4444', '#3b82f6', '#ec4899', '#14b8a6'];
const PIECES = Array.from({ length: 40 }, (_, i) => ({
    id: i,
    color: COLORS[i % COLORS.length],
    left: Math.random() * 100,
    delay: Math.random() * 0.8,
    duration: 2.4 + Math.random() * 1.4,
    size: 7 + Math.random() * 8,
    rotate: Math.random() * 720,
    shape: i % 3 === 0 ? 'circle' : i % 3 === 1 ? 'square' : 'rect',
}));

/** Game levels: the play wrapper (EarlyLearning.js) says which level this
 * play would open (`nextLevel`, null when none) and how to start it. Given
 * through context so none of the game screens has to pass it along. */
export const LevelUnlockContext = createContext({ nextLevel: null, onPlayNext: null });

/**
 * Kids' star-based sibling of CelebrationOverlay — that component is
 * score-shaped (0-100, 3 message tiers) which doesn't map cleanly onto a
 * 0-3 star model, so this reuses its confetti CSS classes/structure but
 * renders 3 stars instead of a numeric score.
 */
const EarlyActivityCelebration = ({ stars, onDone, t }) => {
    const [visible, setVisible] = useState(true);
    const unlock = useContext(LevelUnlockContext);
    // 2+ stars open the next level — offer it, and wait for the kid's choice.
    const unlockedLevel = unlock?.nextLevel && stars >= 2 ? unlock.nextLevel : null;

    // Say the matching star phrase once, when the overlay opens.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(() => { cheerStars(stars); }, []);

    useEffect(() => {
        if (unlockedLevel) return undefined;
        const timer = setTimeout(() => {
            setVisible(false);
            setTimeout(onDone, 400);
        }, 3200);
        return () => clearTimeout(timer);
    }, [onDone, unlockedLevel]);

    const messages = stars === 3
        ? [t('el.star3Title'), t('el.star3Sub')]
        : stars === 2
        ? [t('el.star2Title'), t('el.star2Sub')]
        : [t('el.star1Title'), t('el.star1Sub')];

    const close = () => { setVisible(false); setTimeout(onDone, 400); };
    const playNext = () => { unlock.onPlayNext?.(); close(); };

    return ReactDOM.createPortal(
        <div className={`cel-overlay ${visible ? 'cel-visible' : 'cel-hidden'}`} onClick={close}>
            {PIECES.map((p) => (
                <span
                    key={p.id}
                    className={`cel-piece cel-${p.shape}`}
                    style={{
                        left: `${p.left}%`,
                        background: p.color,
                        width: `${p.size}px`,
                        height: p.shape === 'rect' ? `${p.size * 2.2}px` : `${p.size}px`,
                        animationDelay: `${p.delay}s`,
                        animationDuration: `${p.duration}s`,
                        '--rotate': `${p.rotate}deg`,
                    }}
                />
            ))}
            <div className="cel-card" onClick={(e) => e.stopPropagation()}>
                <div className="eac-stars" aria-hidden="true">
                    {[0, 1, 2].map((i) => (
                        <Star key={i} size={44} fill={i < stars ? '#f59e0b' : 'none'} color={i < stars ? '#f59e0b' : '#d1d5db'} />
                    ))}
                </div>
                <div className="cel-headline">{messages[0]}</div>
                <div className="cel-sub">{messages[1]}</div>
                {unlockedLevel && (
                    <div className="eac-unlock">{t('el.levelUnlocked').replace('{n}', unlockedLevel)}</div>
                )}
                {unlockedLevel && (
                    <button className="cel-btn eac-play-next" onClick={playNext}>{t('el.playNext')}</button>
                )}
                <button className="cel-btn" onClick={close}>{t('el.continueBtn')}</button>
            </div>
        </div>,
        document.body
    );
};

export default EarlyActivityCelebration;
