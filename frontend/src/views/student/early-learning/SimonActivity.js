import React, { useEffect, useMemo, useRef, useState } from 'react';
import './ArithmeticActivity.css';
import './SimonActivity.css';
import EarlyActivityCelebration from './EarlyActivityCelebration';
import LangToggle from './LangToggle';
import { API_URL, useHttp, headers } from '../../../api/search/base';
import { playSynth } from '../../../utils/soundSynth';
import { starsForWrongCount, recordGuestCompletion } from './earlyLearningUtils';
import { ArrowLeft } from 'lucide-react';

const PADS = [
    { color: '#ff6b6b', freq: 261.6 },
    { color: '#51cf66', freq: 329.6 },
    { color: '#4dabf7', freq: 392.0 },
    { color: '#ffd43b', freq: 523.3 },
];

const SHOW_MS = 450;
const STEP_MS = 750;

// One short sine beep per pad. Best-effort: a browser without WebAudio (or
// one that blocks it before a user gesture) just plays silently.
let audioCtx = null;
function playTone(freq) {
    try {
        const Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) return;
        audioCtx = audioCtx || new Ctx();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.0001, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.25, audioCtx.currentTime + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.4);
        osc.connect(gain).connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.42);
    } catch {
        // ignore
    }
}

/** Simon-style memory game. activity.content shape (mode: "simon"):
 * { character: {emoji,label}, rounds_count: 5 } — rounds_count is the
 * sequence length to reach. Each level replays the whole sequence (one pad
 * longer than last time) and the kid repeats it; a wrong pad counts a
 * mistake and replays the same level. Scoring reuses starsForWrongCount. */
export default function SimonActivity({ activity, onBack, onComplete, lang, toggleLang, t, guest = false }) {
    const { request } = useHttp();
    const content = activity.content || {};
    const character = content.character || {};
    const target = content.rounds_count || 5;

    const sequence = useMemo(
        () => Array.from({ length: target }, () => Math.floor(Math.random() * 4)),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [activity.id, activity.content]
    );

    const [level, setLevel] = useState(1);
    const [phase, setPhase] = useState('show'); // show | input | wait
    const [inputIdx, setInputIdx] = useState(0);
    const [activePad, setActivePad] = useState(null);
    const [wrongPad, setWrongPad] = useState(null);
    const [wrongCount, setWrongCount] = useState(0);
    const [replayToken, setReplayToken] = useState(0);
    const [celebration, setCelebration] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const timers = useRef([]);

    const later = (fn, ms) => {
        const id = setTimeout(fn, ms);
        timers.current.push(id);
        return id;
    };

    // Show phase: play the first `level` pads, then hand over to the kid.
    useEffect(() => {
        setPhase('show');
        setInputIdx(0);
        const ids = [];
        let at = 600;
        for (let i = 0; i < level; i++) {
            const pad = sequence[i];
            ids.push(setTimeout(() => { setActivePad(pad); playTone(PADS[pad].freq); }, at));
            ids.push(setTimeout(() => setActivePad(null), at + SHOW_MS));
            at += STEP_MS;
        }
        ids.push(setTimeout(() => setPhase('input'), at));
        return () => ids.forEach(clearTimeout);
    }, [level, replayToken, sequence]);

    useEffect(() => () => timers.current.forEach(clearTimeout), []);

    const press = (pad) => {
        if (phase !== 'input' || celebration !== null || submitting) return;
        setActivePad(pad);
        playTone(PADS[pad].freq);
        later(() => setActivePad(null), 220);

        if (pad === sequence[inputIdx]) {
            const next = inputIdx + 1;
            if (next < level) {
                setInputIdx(next);
                return;
            }
            setPhase('wait');
            if (level >= target) {
                later(() => {
                    playSynth('fanfare');
                    setCelebration(starsForWrongCount(wrongCount));
                }, 500);
            } else {
                later(() => { playSynth('chime'); }, 250);
                later(() => setLevel((l) => l + 1), 900);
            }
        } else {
            playSynth('laser');
            setWrongPad(pad);
            later(() => setWrongPad(null), 500);
            setWrongCount((c) => c + 1);
            setPhase('wait');
            later(() => setReplayToken((n) => n + 1), 1000);
        }
    };

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

    const status = phase === 'show'
        ? (lang === 'ru' ? 'Смотри…' : 'Qara…')
        : phase === 'input'
            ? (lang === 'ru' ? 'Повтори!' : 'Takrorla!')
            : '';

    return (
        <div className="aa-page">
            <div className="el-page-topbar">
                <button className="el-back-btn" onClick={onBack} disabled={submitting}>
                    <ArrowLeft size={18} /> {t('el.back')}
                </button>
                <LangToggle lang={lang} toggleLang={toggleLang} />
            </div>

            <div className="aa-character-header">
                <span className="aa-character-emoji">{character.emoji || '🧠'}</span>
                <h2>{character.label || activity.title}</h2>
            </div>

            {activity.instruction_text && <p className="aa-instruction">{activity.instruction_text}</p>}

            <div className="sm-status">{status}&nbsp;</div>

            <div className="sm-board">
                {PADS.map((p, i) => (
                    <button
                        key={i}
                        type="button"
                        className={`sm-pad ${activePad === i ? 'is-lit' : ''} ${wrongPad === i ? 'is-wrong' : ''}`}
                        style={{ '--pad': p.color }}
                        onClick={() => press(i)}
                        disabled={submitting}
                        aria-label={`pad ${i + 1}`}
                    />
                ))}
            </div>

            <div className="aa-progress">{level} / {target}</div>

            {celebration !== null && (
                <EarlyActivityCelebration stars={celebration} onDone={handleCelebrationDone} t={t} />
            )}
        </div>
    );
}
