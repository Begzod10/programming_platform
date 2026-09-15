import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../../context/StoreContext';
import { getCurrentUser } from '../../api/search/base';
import './TerminalOverlay.css';

// Command -> path suffix (mounted under /student or /teacher depending on
// role — most of these routes exist for both, a few are student- or
// teacher-only and just 404 gracefully via NotFound if typed on the wrong
// role, same as clicking a stale bookmark would).
const ROUTES = {
    dashboard: 'dashboard',
    course: 'courses', courses: 'courses',
    rankings: 'rankings', reyting: 'rankings',
    store: 'store', dokon: 'store',
    profile: 'profile',
    quiz: 'quiz',
    'team-projects': 'team-projects', projects: 'team-projects',
    'team-game': 'team-game',
    achievements: 'achievements', yutuqlar: 'achievements',
    statistics: 'statistics',
    groups: 'groups', guruhlar: 'groups',
    students: 'students',
};

const HELP_LINES = [
    'Mavjud buyruqlar:',
    ...Object.keys(ROUTES).map(c => `  /${c}`),
    '  /clear — ekranni tozalash',
    '  /help — shu ro\'yxat',
];

export default function TerminalOverlay() {
    const { equipped } = useStore();
    const navigate = useNavigate();
    const [open, setOpen] = useState(false);
    const [input, setInput] = useState('');
    const [log, setLog] = useState([`Xush kelibsiz. Buyruq yozing (masalan /course). "/help" — yordam.`]);
    const inputRef = useRef(null);
    const logRef = useRef(null);

    const active = !!equipped.theme?.terminal;

    // Backtick toggles the terminal — ignored while any real text input/
    // textarea/contenteditable has focus so it doesn't hijack normal typing
    // (a backtick is a legitimate character in code exercises etc.).
    useEffect(() => {
        if (!active) return;
        const onKeyDown = (e) => {
            if (e.key !== '`') return;
            const tag = document.activeElement?.tagName;
            const editable = document.activeElement?.isContentEditable;
            if (tag === 'INPUT' || tag === 'TEXTAREA' || editable) return;
            e.preventDefault();
            setOpen(o => !o);
        };
        window.addEventListener('keydown', onKeyDown);
        return () => window.removeEventListener('keydown', onKeyDown);
    }, [active]);

    useEffect(() => {
        if (open) inputRef.current?.focus();
    }, [open]);

    useEffect(() => {
        if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
    }, [log]);

    const run = useCallback((raw) => {
        const cmd = raw.trim().replace(/^\//, '').toLowerCase();
        if (!cmd) return;
        setLog(prev => [...prev, `> /${cmd}`]);

        if (cmd === 'clear') {
            setLog([]);
            return;
        }
        if (cmd === 'help') {
            setLog(prev => [...prev, ...HELP_LINES]);
            return;
        }
        const path = ROUTES[cmd];
        if (!path) {
            setLog(prev => [...prev, `Noma'lum buyruq: /${cmd} — "/help" yozing.`]);
            return;
        }
        const role = getCurrentUser()?.role === 'teacher' ? 'teacher' : 'student';
        navigate(`/${role}/${path}`);
        setLog(prev => [...prev, `→ /${role}/${path}`]);
        setOpen(false);
    }, [navigate]);

    if (!active) return null;

    return (
        <>
            {!open && (
                <button
                    className="term-toggle"
                    onClick={() => setOpen(true)}
                    aria-label="Terminalni ochish"
                    title="Terminal (`)"
                >
                    &gt;_
                </button>
            )}
            {open && (
                <div className="term-panel" role="dialog" aria-label="Terminal">
                    <div className="term-titlebar">
                        <span className="term-dot term-dot--r" />
                        <span className="term-dot term-dot--y" />
                        <span className="term-dot term-dot--g" />
                        <span className="term-title">guest@student-platform:~$</span>
                        <button className="term-close" onClick={() => setOpen(false)}>✕</button>
                    </div>
                    <div className="term-log" ref={logRef}>
                        {log.map((line, i) => <div key={i} className="term-line">{line}</div>)}
                    </div>
                    <form
                        className="term-input-row"
                        onSubmit={e => { e.preventDefault(); run(input); setInput(''); }}
                    >
                        <span className="term-prompt">$</span>
                        <input
                            ref={inputRef}
                            className="term-input"
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            placeholder="/course"
                            autoComplete="off"
                            autoCorrect="off"
                            autoCapitalize="off"
                            spellCheck={false}
                        />
                    </form>
                </div>
            )}
        </>
    );
}
