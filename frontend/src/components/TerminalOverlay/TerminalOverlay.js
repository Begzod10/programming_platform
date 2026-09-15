import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../../context/StoreContext';
import { useAuth } from '../../context/AuthContext';
import { API_URL, useHttp, headers, getCurrentUser } from '../../api/search/base';
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
    '  /course <nom> — kurslarni nomi bo\'yicha qidirish (masalan /course html)',
    '  /menu — yon menyuni ko\'rsatish/yashirish',
    '  /clear — ekranni tozalash',
    '  /logout — tizimdan chiqish',
    '  /help — shu ro\'yxat',
];

export default function TerminalOverlay() {
    const { equipped, terminalMenuHidden, toggleTerminalMenu } = useStore();
    const { logout } = useAuth();
    const { request } = useHttp();
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

    // Inline ghost-text autocomplete (shell/fish-style): the top command
    // matching whatever's typed so far renders right after the caret, in
    // the input itself, rather than a separate list elsewhere on screen.
    // topMatch stays raw (undashed slash handling done once here); ghostRest
    // is just the part of it not yet typed, so appending it to the real
    // input reproduces the full command exactly.
    const typedCmd = input.trim().replace(/^\//, '').toLowerCase();
    const topMatch = useMemo(() => {
        if (!typedCmd) return null;
        const m = ALL_COMMANDS.find(c => c.startsWith(typedCmd));
        return m && m !== typedCmd ? m : null;
    }, [typedCmd]);
    const ghostRest = topMatch ? topMatch.slice(typedCmd.length) : '';

    const acceptGhost = () => {
        if (!topMatch) return;
        setInput(`/${topMatch}`);
        inputRef.current?.focus();
    };

    const run = useCallback((raw) => {
        const stripped = raw.trim().replace(/^\//, '');
        if (!stripped) return;
        // "/course html" -> cmd="course", arg="html". Every other command
        // ignores arg entirely, so this doesn't change their behavior.
        const [cmdWord, ...argWords] = stripped.split(/\s+/);
        const cmd = cmdWord.toLowerCase();
        const arg = argWords.join(' ');
        setLog(prev => [...prev, `> /${stripped}`]);

        if ((cmd === 'course' || cmd === 'courses') && arg) {
            const loadingToken = `__loading_${Date.now()}__`;
            setLog(prev => [...prev, loadingToken]);
            const role = getCurrentUser()?.role === 'teacher' ? 'teacher' : 'student';
            const url = role === 'teacher'
                ? `${API_URL}v1/courses/my`
                : `${API_URL}v1/courses/?limit=100`;
            request(url, 'GET', null, headers())
                .then(rows => {
                    const list = Array.isArray(rows) ? rows : (rows?.items || []);
                    const needle = arg.toLowerCase();
                    const matches = list.filter(c => (c.title || '').toLowerCase().includes(needle));
                    setLog(prev => {
                        const withoutLoading = prev.filter(l => l !== loadingToken);
                        if (matches.length === 0) {
                            return [...withoutLoading, `"${arg}" bo'yicha kurs topilmadi.`];
                        }
                        return [
                            ...withoutLoading,
                            `${matches.length} ta kurs topildi:`,
                            ...matches.slice(0, 10).map(c => `__course__${c.id}__${c.title}`),
                        ];
                    });
                })
                .catch(() => {
                    setLog(prev => [...prev.filter(l => l !== loadingToken), 'Kurslarni yuklab bo\'lmadi.']);
                });
            return;
        }

        if (cmd === 'clear') {
            setLog([]);
            return;
        }
        if (cmd === 'help') {
            const loadingToken = `__loading_${Date.now()}__`;
            setLog(prev => [...prev, loadingToken]);
            // Brief "thinking" beat, then the loading line is swapped for
            // the real lines revealed one at a time — reads more like a
            // real terminal listing than an instant text dump.
            setTimeout(() => {
                setLog(prev => prev.filter(l => l !== loadingToken));
                HELP_LINES.forEach((line, i) => {
                    setTimeout(() => setLog(prev => [...prev, line]), i * 45);
                });
            }, 350);
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
    }, [navigate, toggleTerminalMenu, terminalMenuHidden, logout, request]);

    const handleKeyDown = (e) => {
        // Tab or → (when the caret's already at the end, so it's not just
        // moving the cursor through existing text) accepts the ghost
        // suggestion instead of its usual behavior.
        const atEnd = e.currentTarget.selectionStart === input.length;
        if (topMatch && (e.key === 'Tab' || (e.key === 'ArrowRight' && atEnd))) {
            e.preventDefault();
            acceptGhost();
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
                        {log.map((line, i) => {
                            if (line.startsWith('__loading_')) {
                                return <div key={i} className="term-line term-loading"><span /><span /><span /></div>;
                            }
                            const courseMatch = line.match(/^__course__(\d+)__([\s\S]*)$/);
                            if (courseMatch) {
                                const [, courseId, title] = courseMatch;
                                return (
                                    <button
                                        key={i}
                                        type="button"
                                        className="term-line term-result"
                                        onClick={() => {
                                            const role = getCurrentUser()?.role === 'teacher' ? 'teacher' : 'student';
                                            navigate(`/${role}/courses/${courseId}`);
                                            setOpen(false);
                                        }}
                                    >
                                        → {title}
                                    </button>
                                );
                            }
                            return <div key={i} className="term-line">{line}</div>;
                        })}
                    </div>
                    <div className="term-input-wrap">
                        <form
                            className="term-input-row"
                            onSubmit={e => { e.preventDefault(); run(input); setInput(''); }}
                        >
                            <span className="term-prompt">$</span>
                            <div className="term-input-stack">
                                <div className="term-ghost" aria-hidden="true">
                                    <span className="term-ghost-typed">{input}</span>
                                    <span className="term-ghost-rest">{ghostRest}</span>
                                </div>
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
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </>
    );
}
