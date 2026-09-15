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
const EXTRA_COMMANDS = ['menu', 'clear', 'help', 'logout', 'cd', 'history', 'whoami', 'student', 'theme', 'search'];
const ALL_COMMANDS = [...Object.keys(ROUTES), ...EXTRA_COMMANDS];

const HELP_LINES = [
    'Mavjud buyruqlar:',
    ...Object.keys(ROUTES).map(c => `  /${c}`),
    '  /course <nom> — kurslarni nomi bo\'yicha qidirish (masalan /course html)',
    '  /cd course [nom] — kurslar ro\'yxati, nom bersa to\'g\'ridan-to\'g\'ri kirish',
    '  /cd .. — course/ ichidan chiqib, asosiy promptga qaytish',
    '  /history — yozilgan buyruqlar tarixi (↑/↓ bilan ham ko\'rish mumkin)',
    '  /whoami — profilingiz (ism, rol, tanga, ball)',
    '  /student <ism> — talaba qidirish (faqat o\'qituvchi)',
    '  /theme [nom] — sotib olingan mavzularingiz, nom bersa yoqadi',
    '  /search <so\'z> — kurslar (va o\'qituvchi bo\'lsa talabalar) bo\'yicha umumiy qidiruv',
    '  /menu — yon menyuni ko\'rsatish/yashirish',
    '  /clear — ekranni tozalash',
    '  /logout — tizimdan chiqish',
    '  /help — shu ro\'yxat',
];

export default function TerminalOverlay() {
    const { equipped, terminalMenuHidden, toggleTerminalMenu, inventory, balance, lifetimePoints, refreshAll } = useStore();
    const { logout } = useAuth();
    const { request } = useHttp();
    const navigate = useNavigate();
    const [open, setOpen] = useState(false);
    const [input, setInput] = useState('');
    const [log, setLog] = useState([`Xush kelibsiz. Buyruq yozing (masalan /course). "/help" — yordam.`]);
    // Current "directory" — null means the root prompt. Set by `cd course`
    // so the shell stays "inside" it (like a real cd): after that, typing
    // a bare name with no leading /course or slash still searches courses,
    // exactly like being inside a folder and just typing filenames. "cd .."
    // (or "cd /") backs out to the root prompt.
    const [cwd, setCwd] = useState(null);
    const inputRef = useRef(null);
    const logRef = useRef(null);
    // Every submitted command, oldest first — a ref (not state) since
    // nothing needs to re-render when it changes; /history reads it at
    // print time and ArrowUp/ArrowDown read it at keypress time.
    const historyRef = useRef([]);
    // -1 = not currently browsing history (a fresh line). Set by
    // ArrowUp/ArrowDown, reset to -1 whenever a command actually runs.
    const historyIndexRef = useRef(-1);

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

    // Shared by "/course <name>" and "cd course [name]". No query -> lists
    // everything (up to 15). A query with exactly one title match navigates
    // straight there (the "cd" behavior the latter's named after); more
    // than one, or the plain "/course" form, lists clickable results
    // instead of guessing which the user meant.
    const searchCourses = useCallback((query, { autoNavigate } = {}) => {
        const loadingToken = `__loading_${Date.now()}__`;
        setLog(prev => [...prev, loadingToken]);
        const role = getCurrentUser()?.role === 'teacher' ? 'teacher' : 'student';
        const url = role === 'teacher'
            ? `${API_URL}v1/courses/my`
            : `${API_URL}v1/courses/?limit=100`;
        request(url, 'GET', null, headers())
            .then(rows => {
                const list = Array.isArray(rows) ? rows : (rows?.items || []);
                const needle = query.toLowerCase();
                const matches = query
                    ? list.filter(c => (c.title || '').toLowerCase().includes(needle))
                    : list;

                if (autoNavigate && query && matches.length === 1) {
                    setLog(prev => [
                        ...prev.filter(l => l !== loadingToken),
                        `→ ${matches[0].title}`,
                    ]);
                    navigate(`/${role}/courses/${matches[0].id}`);
                    setOpen(false);
                    return;
                }

                setLog(prev => {
                    const withoutLoading = prev.filter(l => l !== loadingToken);
                    if (matches.length === 0) {
                        return [...withoutLoading, query ? `"${query}" bo'yicha kurs topilmadi.` : 'Kurslar topilmadi.'];
                    }
                    return [
                        ...withoutLoading,
                        `${matches.length} ta kurs topildi:`,
                        ...matches.slice(0, 15).map(c => `__course__${c.id}__${c.title}`),
                    ];
                });
            })
            .catch(() => {
                setLog(prev => [...prev.filter(l => l !== loadingToken), 'Kurslarni yuklab bo\'lmadi.']);
            });
    }, [request, navigate]);

    // "/student <name>" — teacher-only, same result-list shape as
    // searchCourses but against the teacher's own roster
    // (GET /v1/teacher/students/?search=...), and always lists (no
    // auto-navigate) since two students can share a name where two
    // courses rarely do.
    const searchStudents = useCallback((query) => {
        const loadingToken = `__loading_${Date.now()}__`;
        setLog(prev => [...prev, loadingToken]);
        request(`${API_URL}v1/teacher/students/?search=${encodeURIComponent(query)}&limit=20`, 'GET', null, headers())
            .then(rows => {
                const list = Array.isArray(rows) ? rows : [];
                setLog(prev => {
                    const withoutLoading = prev.filter(l => l !== loadingToken);
                    if (list.length === 0) return [...withoutLoading, `"${query}" bo'yicha talaba topilmadi.`];
                    return [
                        ...withoutLoading,
                        `${list.length} ta talaba topildi:`,
                        ...list.slice(0, 15).map(s => `__student__${s.student_id}__${s.full_name || s.username}`),
                    ];
                });
            })
            .catch(() => {
                setLog(prev => [...prev.filter(l => l !== loadingToken), 'Talabalarni yuklab bo\'lmadi.']);
            });
    }, [request]);

    // Equips an already-owned theme (POST /v1/store/inventory/{id}/equip,
    // same endpoint Store.js's own "Yoqish" button calls) then refreshes
    // StoreContext so equipped.theme / the sidebar-hiding logic update
    // immediately, same as buying from the Do'kon page itself would.
    const equipTheme = useCallback((inventoryId, title) => {
        request(`${API_URL}v1/store/inventory/${inventoryId}/equip`, 'POST', JSON.stringify({}), headers())
            .then(() => {
                refreshAll();
                setLog(prev => [...prev, `✓ "${title}" yoqildi.`]);
            })
            .catch(() => setLog(prev => [...prev, 'Mavzuni yoqib bo\'lmadi.']));
    }, [request, refreshAll]);

    const run = useCallback((raw) => {
        const stripped = raw.trim().replace(/^\//, '');
        if (!stripped) return;
        // "/course html" -> cmd="course", arg="html". Every other command
        // ignores arg entirely, so this doesn't change their behavior.
        const [cmdWord, ...argWords] = stripped.split(/\s+/);
        const cmd = cmdWord.toLowerCase();
        const arg = argWords.join(' ');
        setLog(prev => [...prev, `> ${cwd ? `${cwd}/` : ''}${stripped}`]);
        historyRef.current = [...historyRef.current, stripped];
        historyIndexRef.current = -1;

        if (cmd === 'history') {
            if (historyRef.current.length === 0) {
                setLog(prev => [...prev, 'Tarix hali bo\'sh.']);
            } else {
                setLog(prev => [
                    ...prev,
                    ...historyRef.current.map((h, i) => `  ${i + 1}  ${h}`),
                ]);
            }
            return;
        }

        // Backing out of a directory: "cd .." or "cd /" from inside one.
        if (cwd && cmd === 'cd' && (arg === '..' || arg === '/' || !arg)) {
            setCwd(null);
            return;
        }

        // Already "inside" course/ (see cwd's declaration) — anything that
        // isn't itself a recognized top-level command is a bare filename,
        // i.e. a course-name query, exactly like typing inside a real
        // directory needs no path prefix for what's already local to it.
        if (cwd === 'course' && cmd !== 'cd' && !ALL_COMMANDS.includes(cmd)) {
            searchCourses(stripped, { autoNavigate: true });
            return;
        }

        if ((cmd === 'course' || cmd === 'courses') && arg) {
            searchCourses(arg);
            return;
        }

        // "cd course" lists every course AND stays inside it (cwd) so the
        // next thing typed can just be a name — "cd course html" (from the
        // root prompt) navigates straight there if that's an unambiguous
        // match instead, same idea as a shell's `cd` taking a path in one
        // go vs. listing a directory and moving into it first.
        if (cmd === 'cd') {
            const [target, ...nameWords] = argWords;
            const targetWord = (target || '').toLowerCase();
            if (targetWord === 'course' || targetWord === 'courses') {
                const name = nameWords.join(' ');
                if (!name) setCwd('course');
                searchCourses(name, { autoNavigate: true });
                return;
            }
            if (!target) {
                setLog(prev => [...prev, 'Foydalanish: /cd course [nom]']);
                return;
            }
            // Anything else behaves like typing the bare command — "cd
            // rankings" reaches the same place "/rankings" does.
            run(`/${target} ${nameWords.join(' ')}`.trim());
            return;
        }

        if (cmd === 'whoami') {
            const me = getCurrentUser();
            setLog(prev => [
                ...prev,
                me?.full_name || me?.username || '—',
                `Rol: ${me?.role === 'teacher' ? "O'qituvchi" : 'Talaba'}`,
                `Tanga: ${balance ?? '—'}`,
                `Jami yiqqan ball: ${lifetimePoints ?? '—'}`,
            ]);
            return;
        }

        if (cmd === 'student' && arg) {
            if (getCurrentUser()?.role !== 'teacher') {
                setLog(prev => [...prev, 'Bu buyruq faqat o\'qituvchilar uchun.']);
                return;
            }
            searchStudents(arg);
            return;
        }

        if (cmd === 'theme') {
            const themes = (inventory || []).filter(r => r.kind === 'theme');
            const needle = arg.toLowerCase();
            const matches = needle ? themes.filter(t => t.title.toLowerCase().includes(needle)) : themes;
            if (themes.length === 0) {
                setLog(prev => [...prev, 'Sizda hali mavzular yo\'q — Do\'kondan sotib oling (/store).']);
            } else if (arg && matches.length === 1) {
                equipTheme(matches[0].inventory_id, matches[0].title);
            } else if (arg && matches.length === 0) {
                setLog(prev => [...prev, `"${arg}" nomli mavzu topilmadi.`]);
            } else {
                setLog(prev => [
                    ...prev,
                    arg ? `${matches.length} ta mos mavzu:` : 'Sizdagi mavzular:',
                    ...matches.map(t => `__theme__${t.inventory_id}__${t.is_equipped ? '✓ ' : ''}${t.title}`),
                ]);
            }
            return;
        }

        if (cmd === 'search' && arg) {
            const role = getCurrentUser()?.role === 'teacher' ? 'teacher' : 'student';
            const loadingToken = `__loading_${Date.now()}__`;
            setLog(prev => [...prev, loadingToken]);
            const coursesUrl = role === 'teacher' ? `${API_URL}v1/courses/my` : `${API_URL}v1/courses/?limit=100`;
            const requests = [request(coursesUrl, 'GET', null, headers()).catch(() => [])];
            if (role === 'teacher') {
                requests.push(
                    request(`${API_URL}v1/teacher/students/?search=${encodeURIComponent(arg)}&limit=10`, 'GET', null, headers()).catch(() => [])
                );
            }
            Promise.all(requests).then(([courseRows, studentRows]) => {
                const needle2 = arg.toLowerCase();
                const courseList = Array.isArray(courseRows) ? courseRows : (courseRows?.items || []);
                const courseMatches = courseList.filter(c => (c.title || '').toLowerCase().includes(needle2));
                const studentMatches = Array.isArray(studentRows) ? studentRows : [];
                setLog(prev => {
                    const withoutLoading = prev.filter(l => l !== loadingToken);
                    const lines = [];
                    if (courseMatches.length) {
                        lines.push(`Kurslar (${courseMatches.length}):`);
                        lines.push(...courseMatches.slice(0, 8).map(c => `__course__${c.id}__${c.title}`));
                    }
                    if (studentMatches.length) {
                        lines.push(`Talabalar (${studentMatches.length}):`);
                        lines.push(...studentMatches.slice(0, 8).map(s => `__student__${s.student_id}__${s.full_name || s.username}`));
                    }
                    if (lines.length === 0) lines.push(`"${arg}" bo'yicha hech narsa topilmadi.`);
                    return [...withoutLoading, ...lines];
                });
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
    }, [navigate, toggleTerminalMenu, terminalMenuHidden, logout, request, searchCourses, cwd,
        searchStudents, equipTheme, inventory, balance, lifetimePoints]);

    const handleKeyDown = (e) => {
        // Tab or → (when the caret's already at the end, so it's not just
        // moving the cursor through existing text) accepts the ghost
        // suggestion instead of its usual behavior.
        const atEnd = e.currentTarget.selectionStart === input.length;
        if (topMatch && (e.key === 'Tab' || (e.key === 'ArrowRight' && atEnd))) {
            e.preventDefault();
            acceptGhost();
            return;
        }
        // ↑/↓ walk backward/forward through history, same as a real shell.
        // historyIndexRef, not state, since nothing else needs to
        // re-render off it — only this handler reads/writes it.
        if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
            const hist = historyRef.current;
            if (hist.length === 0) return;
            e.preventDefault();
            if (e.key === 'ArrowUp') {
                const next = historyIndexRef.current === -1 ? hist.length - 1 : Math.max(0, historyIndexRef.current - 1);
                historyIndexRef.current = next;
                setInput(hist[next]);
            } else {
                if (historyIndexRef.current === -1) return;
                const next = historyIndexRef.current + 1;
                if (next >= hist.length) {
                    historyIndexRef.current = -1;
                    setInput('');
                } else {
                    historyIndexRef.current = next;
                    setInput(hist[next]);
                }
            }
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
                        <span className="term-title">guest@student-platform:~{cwd ? `/${cwd}` : ''}$</span>
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
                            const studentMatch = line.match(/^__student__(\d+)__([\s\S]*)$/);
                            if (studentMatch) {
                                const [, studentId, name] = studentMatch;
                                return (
                                    <button
                                        key={i}
                                        type="button"
                                        className="term-line term-result"
                                        onClick={() => {
                                            navigate(`/teacher/students/${studentId}`);
                                            setOpen(false);
                                        }}
                                    >
                                        → {name}
                                    </button>
                                );
                            }
                            const themeMatch = line.match(/^__theme__(\d+)__([\s\S]*)$/);
                            if (themeMatch) {
                                const [, inventoryId, title] = themeMatch;
                                return (
                                    <button
                                        key={i}
                                        type="button"
                                        className="term-line term-result"
                                        onClick={() => equipTheme(inventoryId, title.replace(/^✓\s*/, ''))}
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
                            <span className="term-prompt">{cwd ? `${cwd}$` : '$'}</span>
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
                                    placeholder={cwd === 'course' ? 'html (yoki /cd ..)' : '/course'}
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
