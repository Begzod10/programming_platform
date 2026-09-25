import React, { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
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

// Standard touch-typing finger zones: [hand, finger] where finger
// 0 = pinky, 1 = ring, 2 = middle, 3 = index.
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

function fingerLabel(key) {
    const f = FINGER_OF[key];
    if (!f) return '';
    return `${f[0] === 'L' ? 'Chap' : "O'ng"} qo'l — ${FINGER_NAME[f[1]]} barmoq`;
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

const SKIN = '#f6d3b3';
const SKIN_EDGE = '#c99a76';
const GLOW = '#60a5fa';
const GLOW_EDGE = '#1d4ed8';

/** Two hands resting on the home row, drawn over the keyboard from measured
 * key positions (so it lines up at any screen size). Every finger is a thick
 * round-capped line from a base under the keyboard to a fingertip; a finger
 * sits on its home key until it's the one the current key needs, then it
 * stretches to that key and glows blue. */
function Hands({ geo, target }) {
    const { keys, step, w, h, kbBottom } = geo;
    const need = FINGER_OF[target];
    const homeR = [
        { cx: keys.l.cx + step, cy: keys.l.cy },
        keys.l, keys.k, keys.j,
    ];
    const homeL = [keys.a, keys.s, keys.d, keys.f];
    const baseY = kbBottom + step * 1.5;
    const fw = step * 0.62;

    const renderHand = (side) => {
        const home = side === 'L' ? homeL : homeR;
        const palmCx = home.reduce((sum, k) => sum + k.cx, 0) / 4 + (side === 'L' ? step * 0.7 : -step * 0.7);
        const fingers = home.map((hk, idx) => {
            const isActive = need && need[0] === side && need[1] === idx;
            const tip = isActive ? keys[target] : hk;
            return {
                idx, isActive,
                x1: hk.cx + (palmCx - hk.cx) * 0.3, y1: baseY,
                x2: tip.cx, y2: tip.cy + step * 0.12,
            };
        }).sort((a, b) => Number(a.isActive) - Number(b.isActive)); // active drawn last
        const dir = side === 'L' ? 1 : -1;
        const thumb = {
            x1: palmCx + dir * step * 1.0, y1: baseY + step * 0.2,
            x2: palmCx + dir * step * 1.9, y2: kbBottom + step * 0.35,
        };
        return (
            <g key={side}>
                <ellipse cx={palmCx} cy={baseY + step * 0.3} rx={step * 2.5} ry={step * 1.5} fill={SKIN} stroke={SKIN_EDGE} strokeWidth="2" />
                <line {...thumb} stroke={SKIN_EDGE} strokeWidth={fw + 3} strokeLinecap="round" />
                <line {...thumb} stroke={SKIN} strokeWidth={fw} strokeLinecap="round" />
                {fingers.map((f) => (
                    <g key={f.idx} className={f.isActive ? 'kb-finger is-active' : 'kb-finger'}>
                        <line x1={f.x1} y1={f.y1} x2={f.x2} y2={f.y2} stroke={f.isActive ? GLOW_EDGE : SKIN_EDGE} strokeWidth={fw + 3} strokeLinecap="round" />
                        <line x1={f.x1} y1={f.y1} x2={f.x2} y2={f.y2} stroke={f.isActive ? GLOW : SKIN} strokeWidth={fw} strokeLinecap="round" />
                        <circle cx={f.x2} cy={f.y2 - fw * 0.15} r={fw * 0.28} fill="#ffffff" opacity="0.35" />
                    </g>
                ))}
            </g>
        );
    };

    return (
        <svg className="kb-hands" viewBox={`0 0 ${w} ${h}`} width={w} height={h} aria-hidden="true">
            <g opacity="0.94">{renderHand('L')}{renderHand('R')}</g>
        </svg>
    );
}

/** Touch-typing trainer round. activity.content shape (mode: "keyboard"):
 * { character: {emoji,label}, keys: ["f","j","d","k"], rounds_count: 10 }.
 * The kid presses the lit key on a real keyboard (window keydown) or taps
 * it on screen (tablet/phone). The stage shows the letter in a blue band, a
 * glowing beam down to its key, and two hands whose right finger reaches
 * for it. Scoring reuses starsForWrongCount like every sibling activity. */
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
    const [flash, setFlash] = useState(null);
    const [correctKey, setCorrectKey] = useState(null);
    const [locked, setLocked] = useState(false);
    const [, setStreak] = useState(0);
    const [streakFlash, setStreakFlash] = useState(null);
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const [geo, setGeo] = useState(null);
    const stateRef = useRef({});
    const stageRef = useRef(null);
    const bandRef = useRef(null);
    const keyRefs = useRef({});

    const target = rounds[roundIndex];
    stateRef.current = { target, locked, celebration, submitting, roundIndex, wrongCount };

    // Measure key positions with offset* (relative to the positioned stage,
    // unaffected by the page's entrance scale animation) so the beam,
    // letter tile and hands line up at any screen size.
    const measure = useCallback(() => {
        const stage = stageRef.current;
        const band = bandRef.current;
        if (!stage || !band) return;
        const pos = {};
        Object.entries(keyRefs.current).forEach(([k, el]) => {
            if (!el) return;
            pos[k] = {
                cx: el.offsetLeft + el.offsetWidth / 2,
                cy: el.offsetTop + el.offsetHeight / 2,
                top: el.offsetTop,
                w: el.offsetWidth,
                h: el.offsetHeight,
            };
        });
        if (!pos.a || !pos.s || !pos.l || !pos.k || !pos.j || !pos.d || !pos.f) return;
        setGeo({
            keys: pos,
            step: pos.s.cx - pos.a.cx,
            w: stage.offsetWidth,
            h: stage.offsetHeight,
            bandBottom: band.offsetTop + band.offsetHeight,
            kbBottom: Math.max(...Object.values(pos).map((p) => p.top + p.h)),
        });
    }, []);

    useLayoutEffect(() => {
        measure();
        if (typeof ResizeObserver === 'undefined' || !stageRef.current) return undefined;
        const ro = new ResizeObserver(measure);
        ro.observe(stageRef.current);
        return () => ro.disconnect();
    }, [measure]);

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

    const tk = geo?.keys[target];
    const tileStyle = tk ? { left: tk.cx } : { left: '50%' };
    const beamStyle = tk ? {
        left: tk.cx,
        top: geo.bandBottom,
        height: Math.max(0, tk.top - geo.bandBottom),
        width: tk.w * 0.9,
    } : { display: 'none' };

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

            <div className="kb-stage" ref={stageRef}>
                <div className="kb-band" ref={bandRef}>
                    <div className="kb-tile" style={tileStyle} key={roundIndex}>{target.toUpperCase()}</div>
                </div>
                <div className="kb-beam" style={beamStyle} />

                <div className="kb-board">
                    {ROWS.map((row, ri) => (
                        <div key={ri} className={`kb-row kb-row--${ri}`}>
                            {row.map((k) => {
                                const cls = [
                                    'kb-key',
                                    k === target ? 'is-target' : '',
                                    correctKey === k ? 'is-correct' : '',
                                    flash?.key === k ? 'is-wrong' : '',
                                ].filter(Boolean).join(' ');
                                return (
                                    <button
                                        key={k}
                                        ref={(el) => { keyRefs.current[k] = el; }}
                                        type="button"
                                        className={cls}
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

                {geo && <Hands geo={geo} target={target} />}
            </div>

            <div className="kb-finger-label">{fingerLabel(target)}</div>
            <div className="kb-progress">{roundIndex + 1} / {rounds.length}</div>

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
