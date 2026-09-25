import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import './KeyboardActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { starsForWrongCount, WRONG_FLASH_MS, STREAK_THRESHOLD, recordGuestCompletion } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

const CORRECT_PULSE_MS = 450;

const ROWS = [
    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
    ['z', 'x', 'c', 'v', 'b', 'n', 'm'],
];

// Standard touch-typing finger zones. `hand` + `finger` index into the
// SVG hands below (finger 0 = pinky ... 3 = index, drawn outward-in).
const FINGER_OF = {
    q: ['L', 0], a: ['L', 0], z: ['L', 0],
    w: ['L', 1], s: ['L', 1], x: ['L', 1],
    e: ['L', 2], d: ['L', 2], c: ['L', 2],
    r: ['L', 3], f: ['L', 3], v: ['L', 3], t: ['L', 3], g: ['L', 3], b: ['L', 3],
    y: ['R', 3], h: ['R', 3], n: ['R', 3], u: ['R', 3], j: ['R', 3], m: ['R', 3],
    i: ['R', 2], k: ['R', 2],
    o: ['R', 1], l: ['R', 1],
    p: ['R', 0],
};

const FINGER_NAME = ['jimjiloq', 'nomsiz', "o'rta", "ko'rsatkich"];
const FINGER_COLORS = ['#ff8a80', '#ffb74d', '#81c784', '#64b5f6'];

function fingerLabel(key) {
    const f = FINGER_OF[key];
    if (!f) return '';
    return `${f[0] === 'L' ? "Chap" : "O'ng"} qo'l — ${FINGER_NAME[f[1]]} barmoq`;
}

function buildRounds(keys, count) {
    const pool = keys.length ? keys : ['f', 'j'];
    const out = [];
    let prev = null;
    for (let i = 0; i < count; i++) {
        let pick;
        let guard = 0;
        do {
            pick = pool[Math.floor(Math.random() * pool.length)];
            guard++;
        } while (pool.length > 1 && pick === prev && guard < 8);
        out.push(pick);
        prev = pick;
    }
    return out;
}

/** Touch-typing trainer round. activity.content shape (mode: "keyboard"):
 * { character: {emoji,label}, keys: ["f","j","d","k"], rounds_count: 10 }.
 * The kid presses the highlighted key on a real keyboard (window keydown)
 * or taps it on screen (tablet/phone). Scoring reuses starsForWrongCount
 * exactly like every sibling activity. */
export default function KeyboardActivity({ activity, onBack, onComplete, lang, toggleLang, t, guest = false }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const keys = (content.keys || []).map((k) => String(k).toLowerCase());
    const roundsCount = content.rounds_count || 10;

    const rounds = useMemo(
        () => buildRounds(keys, roundsCount),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [activity.id, activity.content]
    );

    const [roundIndex, setRoundIndex] = useState(0);
    const [wrongCount, setWrongCount] = useState(0);
    const [flash, setFlash] = useState(null); // { token, key } wrong key just pressed
    const [correctKey, setCorrectKey] = useState(null);
    const [locked, setLocked] = useState(false);
    const [, setStreak] = useState(0);
    const [streakFlash, setStreakFlash] = useState(null);
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const stateRef = useRef({});

    const target = rounds[roundIndex];
    stateRef.current = { target, locked, celebration, submitting, roundIndex, wrongCount };

    const handleKey = useCallback((pressed) => {
        const s = stateRef.current;
        if (!s.target || s.locked || s.celebration !== null || s.submitting) return;

        if (pressed === s.target) {
            setStreak((n) => {
                const next = n + 1;
                if (next % STREAK_THRESHOLD === 0) {
                    playSynth('coin');
                    const token = Date.now();
                    setStreakFlash({ token, count: next });
                    setTimeout(() => setStreakFlash((f) => (f?.token === token ? null : f)), 900);
                } else {
                    playSynth('chime');
                }
                return next;
            });
            setLocked(true);
            setCorrectKey(pressed);
            setTimeout(() => {
                setCorrectKey(null);
                setLocked(false);
                if (s.roundIndex + 1 < rounds.length) {
                    setRoundIndex((i) => i + 1);
                } else {
                    playSynth('fanfare');
                    setCelebration(starsForWrongCount(stateRef.current.wrongCount));
                }
            }, CORRECT_PULSE_MS);
        } else {
            playSynth('laser');
            setStreak(0);
            setWrongCount((c) => c + 1);
            const token = Date.now();
            setFlash({ token, key: pressed });
            setTimeout(() => setFlash((f) => (f?.token === token ? null : f)), WRONG_FLASH_MS);
        }
    }, [rounds.length]);

    useEffect(() => {
        const onKeyDown = (e) => {
            if (e.ctrlKey || e.metaKey || e.altKey) return;
            if (e.key.length !== 1) return;
            const k = e.key.toLowerCase();
            if (!FINGER_OF[k]) return;
            e.preventDefault();
            handleKey(k);
        };
        window.addEventListener('keydown', onKeyDown);
        return () => window.removeEventListener('keydown', onKeyDown);
    }, [handleKey]);

    const handleCelebrationDone = () => {
        const stars = celebration;
        if (guest) {
            onComplete(recordGuestCompletion(activity.id, stars));
            return;
        }
        setSubmitting(true);
        request(`${API_URL}v1/early-learning/activities/${activity.id}/complete`, 'POST', { stars }, headers())
            .then((result) => onComplete(result))
            .catch((err) => {
                console.error(err);
                onComplete({ stars_earned: stars, attempts: 1 });
            })
            .finally(() => setSubmitting(false));
    };

    if (!target) return null;

    return (
        <div className="kb-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="kb-character-header">
                <span className="kb-character-emoji">{character.emoji || '⌨️'}</span>
                <h2>{character.label || activity.title}</h2>
            </div>

            {activity.instruction_text && <p className="kb-instruction">{activity.instruction_text}</p>}

            {streakFlash && (
                <div className="kb-streak-badge" key={streakFlash.token}>🔥 {streakFlash.count}!</div>
            )}

            <div className="kb-target-wrap">
                <div className="kb-target" key={roundIndex}>{target.toUpperCase()}</div>
                <div className="kb-finger-label">{fingerLabel(target)}</div>
            </div>

            <div className="kb-board">
                {ROWS.map((row, ri) => (
                    <div key={ri} className={`kb-row kb-row--${ri}`}>
                        {row.map((k) => {
                            const isTarget = k === target;
                            const f = FINGER_OF[k];
                            const cls = [
                                'kb-key',
                                isTarget ? 'is-target' : '',
                                correctKey === k ? 'is-correct' : '',
                                flash?.key === k ? 'is-wrong' : '',
                            ].filter(Boolean).join(' ');
                            return (
                                <button
                                    key={k}
                                    type="button"
                                    className={cls}
                                    style={{ '--finger': FINGER_COLORS[f[1]] }}
                                    onClick={() => handleKey(k)}
                                    disabled={submitting}
                                    tabIndex={-1}
                                >
                                    {k.toUpperCase()}
                                </button>
                            );
                        })}
                    </div>
                ))}
            </div>

            <div className="kb-progress">{roundIndex + 1} / {rounds.length}</div>

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
