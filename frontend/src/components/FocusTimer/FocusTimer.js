import { useCallback, useEffect, useRef, useState } from 'react';
import { useStore } from '../../context/StoreContext';
import { playSynth } from '../../utils/soundSynth';
import './FocusTimer.css';

const WORK_SECONDS = 25 * 60;
const SHORT_BREAK_SECONDS = 5 * 60;
const LONG_BREAK_SECONDS = 15 * 60;
const SESSIONS_PER_CYCLE = 4;

const MODE_LABEL = {
    work: 'Ish vaqti',
    short_break: 'Qisqa tanaffus',
    long_break: 'Uzoq tanaffus',
};

function durationFor(mode) {
    if (mode === 'work') return WORK_SECONDS;
    if (mode === 'long_break') return LONG_BREAK_SECONDS;
    return SHORT_BREAK_SECONDS;
}

function fmt(totalSeconds) {
    const m = Math.floor(totalSeconds / 60);
    const s = totalSeconds % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

/** Pomodoro widget unlocked by the "Focus Mode" theme (asset_ref.focus:
 * true) — sibling of TerminalOverlay.js's terminal:true gate, same
 * self-mounted-in-App.js / self-gated-on-equipped-theme shape. Unlike the
 * terminal, this doesn't hide any chrome or need a functional flag beyond
 * its own presence — the theme's own calm color tokens (applied globally
 * by StoreContext's applyTheme) already do the "simplified, low-
 * distraction" part; this widget is the one genuinely new capability. */
export default function FocusTimer() {
    const { equipped } = useStore();
    const active = !!equipped.theme?.focus;

    const [collapsed, setCollapsed] = useState(false);
    const [mode, setMode] = useState('work');
    const [secondsLeft, setSecondsLeft] = useState(WORK_SECONDS);
    const [running, setRunning] = useState(false);
    const [completedSessions, setCompletedSessions] = useState(0);
    const intervalRef = useRef(null);

    // Runs when the countdown hits zero. Reads `mode`/`completedSessions`
    // from the render closure (both captured fresh via the effect's own
    // dependency array below) rather than functional setState updaters,
    // since the next mode depends on BOTH pieces of state together and
    // two separate updater callbacks can't see each other's result
    // synchronously.
    const finishInterval = useCallback(() => {
        if (mode === 'work') {
            const nextCompleted = completedSessions + 1;
            setCompletedSessions(nextCompleted);
            const nextMode = nextCompleted % SESSIONS_PER_CYCLE === 0 ? 'long_break' : 'short_break';
            playSynth('fanfare');
            setMode(nextMode);
            setSecondsLeft(durationFor(nextMode));
        } else {
            playSynth('chime');
            setMode('work');
            setSecondsLeft(WORK_SECONDS);
        }
    }, [mode, completedSessions]);

    useEffect(() => {
        if (!active || !running) {
            clearInterval(intervalRef.current);
            return;
        }
        intervalRef.current = setInterval(() => {
            setSecondsLeft(s => {
                if (s <= 1) {
                    finishInterval();
                    return 0;
                }
                return s - 1;
            });
        }, 1000);
        return () => clearInterval(intervalRef.current);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [active, running, mode, completedSessions]);

    const toggleRunning = () => setRunning(r => !r);
    const reset = () => {
        setRunning(false);
        setSecondsLeft(durationFor(mode));
    };

    if (!active) return null;

    const total = durationFor(mode);
    const pct = Math.round(((total - secondsLeft) / total) * 100);

    if (collapsed) {
        return (
            <button
                className="ft-toggle"
                onClick={() => setCollapsed(false)}
                aria-label="Focus taymerni ochish"
                title="Focus Timer"
            >
                {fmt(secondsLeft)}
            </button>
        );
    }

    return (
        <div className="ft-widget" role="complementary" aria-label="Pomodoro taymer">
            <div className="ft-head">
                <span className={`ft-mode ft-mode--${mode}`}>{MODE_LABEL[mode]}</span>
                <button className="ft-collapse" onClick={() => setCollapsed(true)} aria-label="Yig'ish">–</button>
            </div>
            <div className="ft-ring-wrap">
                <svg viewBox="0 0 100 100" className="ft-ring">
                    <circle className="ft-ring-track" cx="50" cy="50" r="44" />
                    <circle
                        className="ft-ring-fill"
                        cx="50" cy="50" r="44"
                        style={{ strokeDasharray: 276.5, strokeDashoffset: 276.5 * (1 - pct / 100) }}
                    />
                </svg>
                <span className="ft-time">{fmt(secondsLeft)}</span>
            </div>
            <div className="ft-dots">
                {Array.from({ length: SESSIONS_PER_CYCLE }, (_, i) => (
                    <span key={i} className={`ft-dot ${i < completedSessions % SESSIONS_PER_CYCLE ? 'is-done' : ''}`} />
                ))}
            </div>
            <div className="ft-actions">
                <button className="ft-btn ft-btn--primary" onClick={toggleRunning}>
                    {running ? 'Pauza' : 'Boshlash'}
                </button>
                <button className="ft-btn" onClick={reset}>Qayta</button>
            </div>
        </div>
    );
}
