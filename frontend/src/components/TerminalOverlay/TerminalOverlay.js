import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../../context/StoreContext';
import { useAuth } from '../../context/AuthContext';
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

// Commands that aren't a route — handled specially in run(), but still
// need to appear in /help and the live autocomplete list below.
const EXTRA_COMMANDS = ['menu', 'clear', 'help', 'logout'];
const ALL_COMMANDS = [...Object.keys(ROUTES), ...EXTRA_COMMANDS];

const HELP_LINES = [
    'Mavjud buyruqlar:',
    ...Object.keys(ROUTES).map(c => `  /${c}`),
    '  /menu — yon menyuni ko\'rsatish/yashirish',
    '  /clear — ekranni tozalash',
    '  /logout — tizimdan chiqish',
    '  /help — shu ro\'yxat',
];

export default function TerminalOverlay() {
    const { equipped, terminalMenuHidden, toggleTerminalMenu } = useStore();
    const { logout } = useAuth();
    const navigate = useNavigate();
    const [open, setOpen] = useState(false);
    const [input, setInput] = useState('');
    const [log, setLog] = useState([`Xush kelibsiz. Buyruq yozing (masalan /course). "/help" — yordam.`]);
    const inputRef = useRef(null);
    const logRef = useRef(null);

    const active = !!equipped.theme?.terminal;

    // Backtick OR Ctrl+T toggles the terminal. Ctrl+T is intercepted at the
    // browser-chrome level in most desktop browsers (reserved for "new
    // tab") and preventDefault() can't override that — it still works here
    // whenever the browser does let a keydown through (embedded webviews,
    // some browsers/versions), and backtick is the reliable fallback.
    // Ignored while any real text input/textarea/contenteditable has focus
    // so it doesn't hijack normal typing (backtick is a legitimate
    // character in code exercises, Ctrl+T might be a real shortcut there).
    useEffect(() => {
        if (!active) return;
        const onKeyDown = (e) => {
            const isBacktick = e.key === '`';
            const isCtrlT = e.ctrlKey && !e.altKey && !e.shiftKey && e.key.toLowerCase() === 't';
            if (!isBacktick && !isCtrlT) return;
            const tag = document.activeElement?.tagName;
            const editable = document.activeElement?.isContentEditable;
            if ((tag === 'INPUT' || tag === 'TEXTAREA' || editable) && document.activeElement !== inputRef.current) return;
            e.preventDefault();
            setOpen(o => !o);
        };
        window.addEventListener('keydown', onKeyDown);
        return () => window.removeEventListener('keydown', onKeyDown);
    }, [active]);

    useEffect(() => {
        if (open) inputRef.current?.focus();
        else setInput('');
    }, [open]);

    useEffect(() => {
        if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
    }, [log]);

    // Live suggestions — commands whose name starts with whatever's typed
    // so far (leading slash stripped). Hidden once the input is empty or
    // already an exact match, so it doesn't linger after a useful typo fix.
    const suggestions = useMemo(() => {
        const typed = input.trim().replace(/^\//, '').toLowerCase();
        if (!typed) return [];
        const matches = ALL_COMMANDS.filter(c => c.startsWith(typed));
        return matches.includes(typed) ? [] : matches.slice(0, 6);
    }, [input]);

    const applySuggestion = (cmd) => {
        setInput(`/${cmd}`);
        inputRef.current?.focus();
    };

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
        if (cmd === 'menu') {
            toggleTerminalMenu();
            setLog(prev => [...prev, terminalMenuHidden ? 'Menyu ko\'rsatildi.' : 'Menyu yashirildi.']);
            return;
        }
        if (cmd === 'logout') {
            setLog(prev => [...prev, 'Chiqilmoqda…']);
            logout();
            navigate('/login');
            setOpen(false);
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
    }, [navigate, toggleTerminalMenu, terminalMenuHidden, logout]);

    const handleKeyDown = (e) => {
        // Tab completes to the top suggestion instead of moving focus away.
        if (e.key === 'Tab' && suggestions.length > 0) {
            e.preventDefault();
            applySuggestion(suggestions[0]);
        }
    };

    if (!active) return null;

    return (
        <>
            {!open && (
                <button
                    className="term-toggle"
                    onClick={() => setOpen(true)}
                    aria-label="Terminalni ochish"
                    title="Terminal (` yoki Ctrl+T)"
                >
                    &gt;_
                </button>
            )}
            {open && (
                <div className="term-panel term-panel--full" role="dialog" aria-label="Terminal">
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
                    <div className="term-input-wrap">
                        {suggestions.length > 0 && (
                            <div className="term-suggestions">
                                {suggestions.map(c => (
                                    <button
                                        key={c}
                                        type="button"
                                        className="term-suggestion"
                                        onClick={() => applySuggestion(c)}
                                    >
                                        /{c}
                                    </button>
                                ))}
                            </div>
                        )}
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
                                onKeyDown={handleKeyDown}
                                placeholder="/course"
                                autoComplete="off"
                                autoCorrect="off"
                                autoCapitalize="off"
                                spellCheck={false}
                            />
                        </form>
                    </div>
                </div>
            )}
        </>
    );
}
